"""Main application module."""

from pathlib import Path

import streamlit as st

from gstats.analyzer import RepositoryAnalyzer
from gstats.author_normalizer import AuthorNormalizer
from gstats.visualizations import GitVisualizer

st.set_page_config(
    page_title="gStats",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for success message and settings
if 'show_success' not in st.session_state:
    st.session_state.show_success = False
if 'similarity_threshold' not in st.session_state:
    st.session_state.similarity_threshold = 0.7
if 'max_lines_per_commit' not in st.session_state:
    st.session_state.max_lines_per_commit = 250000
if 'repo_path' not in st.session_state:
    st.session_state.repo_path = str(Path.home())
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'repo_info' not in st.session_state:
    st.session_state.repo_info = None
if 'manual_author_mappings' not in st.session_state:
    st.session_state.manual_author_mappings = {}
if 'raw_commit_data' not in st.session_state:
    st.session_state.raw_commit_data = None
if 'original_authors' not in st.session_state:
    st.session_state.original_authors = None


def analyze_repository():
    """Analyze the repository with current settings."""
    try:
        st.session_state.analyzer = RepositoryAnalyzer(
            st.session_state.repo_path,
            st.session_state.similarity_threshold,
            st.session_state.manual_author_mappings
        )
        
        # Only extract raw data if we don't have it cached
        if st.session_state.raw_commit_data is None:
            st.session_state.raw_commit_data, st.session_state.original_authors = st.session_state.analyzer.get_raw_commit_data()
        
        # Apply author normalization to cached data
        df = st.session_state.analyzer.apply_author_normalization(
            st.session_state.raw_commit_data, 
            st.session_state.original_authors
        )

        # Filter out large commits
        if st.session_state.max_lines_per_commit > 0:
            df = df[df['insertions'] + df['deletions'] <= st.session_state.max_lines_per_commit]

        st.session_state.df = df
        st.session_state.repo_info = st.session_state.analyzer.get_repository_info()
        st.session_state.show_success = True
    except Exception as e:
        st.error(f"Error analyzing repository: {str(e)}")
        import traceback
        traceback.print_exc()


def reapply_author_mappings():
    """Fast re-application of author mappings without re-reading git data."""
    if st.session_state.analyzer and st.session_state.raw_commit_data is not None:
        # Update analyzer settings
        st.session_state.analyzer.manual_author_mappings = st.session_state.manual_author_mappings
        st.session_state.analyzer.author_similarity_threshold = st.session_state.similarity_threshold
        
        # Apply author normalization to cached data
        df = st.session_state.analyzer.apply_author_normalization(
            st.session_state.raw_commit_data, 
            st.session_state.original_authors
        )

        # Filter out large commits
        if st.session_state.max_lines_per_commit > 0:
            df = df[df['insertions'] + df['deletions'] <= st.session_state.max_lines_per_commit]

        st.session_state.df = df


def main():
    """Main application function."""
    # Sidebar layout
    with st.sidebar:
        st.title("📊 gStats")

        # Create a form for repository path input
        with st.form("repo_form"):
            repo_path = st.text_input(
                "Enter repository path",
                value=st.session_state.repo_path
            )

            # Form submit button
            submitted = st.form_submit_button("Analyze")

            if submitted:
                st.session_state.repo_path = repo_path
                # Clear cached data when changing repository
                st.session_state.raw_commit_data = None
                st.session_state.original_authors = None
                analyze_repository()

    if st.session_state.df is not None and st.session_state.repo_info is not None:
        # Display repository title in main container
        repo_name = Path(st.session_state.repo_info['path']).name
        st.markdown(f"# {repo_name}")

        # Display repository information in sidebar
        st.sidebar.subheader("Repository Information")
        st.sidebar.write(f"**Path:** {st.session_state.repo_info['path']}")
        st.sidebar.write(f"**Active Branch:** {st.session_state.repo_info['active_branch']}")

        if st.session_state.repo_info['untracked_files']:
            st.sidebar.warning(f"**Untracked Files:** {len(st.session_state.repo_info['untracked_files'])}")
            with st.sidebar.expander("Show untracked files"):
                for file in st.session_state.repo_info['untracked_files']:
                    st.code(file)

        # Get date range for the entire project
        min_date = st.session_state.df['date'].min()
        max_date = st.session_state.df['date'].max()

        # Display date range info
        st.sidebar.info(f"**Project lifespan:** {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")

        # Display basic stats
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Commits", len(st.session_state.df))

        with col2:
            st.metric("Authors", st.session_state.df['author'].nunique())

        with col3:
            insertions = st.session_state.df['insertions'].sum()
            deletions = st.session_state.df['deletions'].sum()
            st.metric(
                "Lines changed",
                f"{insertions + deletions:,}",
            )

        with col4:
            st.metric("Files changed", st.session_state.df['files_changed'].sum())

        with col5:
            st.metric("Branches", st.session_state.repo_info['branch_count'])

        # Tabs for different visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", "Authors", "Churn", "Branches", "Settings"
        ])

        with tab1:
            # Commit timeline
            st.subheader("Commit Timeline")
            fig = GitVisualizer.create_commit_timeline(st.session_state.df)
            st.plotly_chart(fig, use_container_width=True)

            # Commit heatmap
            st.subheader("Commit Activity Heatmap")
            heatmap_fig = GitVisualizer.create_commit_heatmap(st.session_state.df)
            st.plotly_chart(heatmap_fig, use_container_width=True)

        with tab2:
            # Author contributions overview
            st.subheader("Author Contributions Overview")
            author_fig = GitVisualizer.create_author_stats(st.session_state.df)
            st.plotly_chart(author_fig, use_container_width=True)

            # Individual author contributions
            st.subheader("Individual Author Contributions")
            author_figs = GitVisualizer.create_individual_author_contributions(st.session_state.df)

            # Display author contribution graphs in a grid
            cols = st.columns(2)  # Create 2 columns
            for i, fig in enumerate(author_figs):
                with cols[i % 2]:  # Alternate between columns
                    st.plotly_chart(fig, use_container_width=True)

            # Individual author heatmaps
            st.subheader("Individual Author Commit Patterns")
            author_heatmaps = GitVisualizer.create_individual_author_heatmaps(st.session_state.df)

            # Display author heatmaps in a grid
            cols = st.columns(2)  # Create 2 columns
            for i, heatmap in enumerate(author_heatmaps):
                with cols[i % 2]:  # Alternate between columns
                    st.plotly_chart(heatmap, use_container_width=True)

        with tab3:
            # Code churn timeline
            st.subheader("Code Churn Timeline")
            churn_fig = GitVisualizer.create_code_churn_timeline(st.session_state.df)
            st.plotly_chart(churn_fig, use_container_width=True)

        with tab4:
            # Branch information
            st.subheader("Branch Statistics")
            branch_fig = GitVisualizer.create_branch_stats(st.session_state.df)
            st.plotly_chart(branch_fig, use_container_width=True)

        with tab5:
            st.header("⚙️ Settings & Author Management")
            
            # Use cached original authors
            original_authors = st.session_state.original_authors
            
            # Settings in a clean layout
            st.subheader("📊 Analysis Settings")
            
            settings_col1, settings_col2 = st.columns(2)
            
            with settings_col1:
                new_threshold = st.slider(
                    "🎯 Author similarity threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.similarity_threshold,
                    step=0.05,
                    help="Higher values require more exact matches between author names"
                )
                
            with settings_col2:
                new_max_lines = st.number_input(
                    "📏 Max lines per commit",
                    min_value=0,
                    max_value=1000000,
                    value=st.session_state.max_lines_per_commit,
                    step=10000,
                    help="Commits with more lines than this will be ignored. Set to 0 to disable."
                )

            # Apply settings changes
            if (new_threshold != st.session_state.similarity_threshold or
                    new_max_lines != st.session_state.max_lines_per_commit):
                st.session_state.similarity_threshold = new_threshold
                st.session_state.max_lines_per_commit = new_max_lines
                reapply_author_mappings()
                st.rerun()

            st.divider()

            # Author Management Section
            st.subheader("👥 Author Management")
            
            # Get current groupings and mappings
            groups = AuthorNormalizer.get_combined_groups(
                list(original_authors),
                st.session_state.similarity_threshold,
                st.session_state.manual_author_mappings
            )
            
            # Find standalone authors (those not in any group)
            standalone_authors = []
            for author in original_authors:
                is_in_group = any(author in members for members in groups.values())
                if not is_in_group:
                    standalone_authors.append(author)
            
            # Show stats
            total_authors = len(original_authors)
            unique_after_merge = st.session_state.df['author'].nunique() if st.session_state.df is not None else total_authors
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Original Authors", total_authors)
            with col_stat2:
                st.metric("After Merging", unique_after_merge)
            with col_stat3:
                st.metric("Groups", len(groups))
            
            # Create tabs for different author management views
            author_tab1, author_tab2, author_tab3 = st.tabs([
                "🔗 Merge Authors", "📋 Current Groups", "🗂️ All Authors"
            ])
            
            with author_tab1:
                st.markdown("**Merge two authors into one**")
                
                # Get smart merge options
                authors_to_merge, merge_targets = AuthorNormalizer.get_merge_options(
                    list(original_authors),
                    st.session_state.similarity_threshold,
                    st.session_state.manual_author_mappings
                )
                
                if not authors_to_merge:
                    st.info("ℹ️ All authors are already part of groups or merged. No additional merging is possible.")
                else:
                    merge_col1, merge_col2, merge_col3 = st.columns([2, 2, 1])
                    
                    with merge_col1:
                        author_to_merge = st.selectbox(
                            "Author to merge",
                            options=[""] + authors_to_merge,
                            key="merge_from",
                            help="Select an unmerged author to merge into a group or another author"
                        )
                        
                    with merge_col2:
                        # Filter out the selected author from merge targets to prevent self-merge
                        available_targets = [t for t in merge_targets if t != author_to_merge]
                        merge_target = st.selectbox(
                            "Merge into",
                            options=[""] + available_targets,
                            key="merge_into",
                            help="Select an existing author or group leader to merge into"
                        )
                        
                    with merge_col3:
                        st.write("")  # Spacing
                        st.write("")  # Spacing
                        if st.button("🔗 Merge", disabled=not (author_to_merge and merge_target), use_container_width=True):
                            st.session_state.manual_author_mappings[author_to_merge] = merge_target
                            reapply_author_mappings()
                            st.rerun()
                    
                    # Show preview
                    if author_to_merge and merge_target:
                        # Check if target is already a group leader
                        current_groups = AuthorNormalizer.get_combined_groups(
                            list(original_authors),
                            st.session_state.similarity_threshold,
                            st.session_state.manual_author_mappings
                        )
                        
                        target_group_size = 0
                        for canonical, members in current_groups.items():
                            if canonical == merge_target:
                                target_group_size = len(members)
                                break
                        
                        if target_group_size > 1:
                            st.info(f"Preview: **{author_to_merge}** will be added to the **{merge_target}** group ({target_group_size} members)")
                        else:
                            st.info(f"Preview: **{author_to_merge}** will be merged into **{merge_target}**")
                    
                    # Show available merge statistics
                    st.caption(f"📊 {len(authors_to_merge)} authors available to merge • {len(merge_targets)} possible targets")
            
            with author_tab2:
                st.markdown("**Current author groups** (showing merged authors)")
                
                if groups:
                    for i, (canonical_name, similar_names) in enumerate(groups.items()):
                        with st.container():
                            col_group, col_actions = st.columns([4, 1])
                            
                            with col_group:
                                st.markdown(f"**🎯 {canonical_name}**")
                                for name in similar_names:
                                    if name != canonical_name:
                                        is_manual = name in st.session_state.manual_author_mappings
                                        indicator = " (manual)" if is_manual else " (auto)"
                                        st.markdown(f"- {name}{indicator}")
                            
                            with col_actions:
                                # Option to unmerge manual mappings
                                manual_mappings_in_group = [
                                    name for name in similar_names 
                                    if name in st.session_state.manual_author_mappings
                                ]
                                if manual_mappings_in_group:
                                    if st.button("🔓 Unmerge", key=f"unmerge_group_{i}"):
                                        for name in manual_mappings_in_group:
                                            if name in st.session_state.manual_author_mappings:
                                                del st.session_state.manual_author_mappings[name]
                                        reapply_author_mappings()
                                        st.rerun()
                            
                        st.divider()
                else:
                    st.info("No author groups found. Authors are either unique or similarity threshold is too high.")
            
            with author_tab3:
                st.markdown("**All authors in repository**")
                
                # Show stats
                total_authors = len(original_authors)
                unique_after_merge = st.session_state.df['author'].nunique() if st.session_state.df is not None else total_authors
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Original Authors", total_authors)
                with col_stat2:
                    st.metric("After Merging", unique_after_merge)
                with col_stat3:
                    merged_count = total_authors - unique_after_merge
                    st.metric("Authors Merged", merged_count)
                
                # List all authors with their status
                st.markdown("**Author list:**")
                for author in sorted(original_authors):
                    status_icon = "🔗" if author in st.session_state.manual_author_mappings else "👤"
                    if author in st.session_state.manual_author_mappings:
                        target = st.session_state.manual_author_mappings[author]
                        st.markdown(f"{status_icon} {author} → {target}")
                    else:
                        st.markdown(f"{status_icon} {author}")

            # Manual mappings management section
            if st.session_state.manual_author_mappings:
                st.divider()
                st.subheader("🗑️ Manual Mappings")
                
                for orig, target in list(st.session_state.manual_author_mappings.items()):
                    map_col, del_col = st.columns([5, 1])
                    with map_col:
                        st.markdown(f"🔗 **{orig}** → **{target}**")
                    with del_col:
                        if st.button("🗑️", key=f"delete_mapping_{orig}"):
                            del st.session_state.manual_author_mappings[orig]
                            reapply_author_mappings()
                            st.rerun()


if __name__ == "__main__":
    main()
