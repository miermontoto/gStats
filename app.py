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


def analyze_repository():
    """Analyze the repository with current settings."""
    try:
        st.session_state.analyzer = RepositoryAnalyzer(
            st.session_state.repo_path,
            st.session_state.similarity_threshold
        )
        df = st.session_state.analyzer.get_commit_stats()

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
            # Settings and author mappings
            st.subheader("Settings")

            # Author similarity threshold slider
            new_threshold = st.slider(
                "Author name similarity threshold",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.similarity_threshold,
                step=0.1,
                help="Higher values require more exact matches between author names"
            )

            # Max lines per commit setting
            new_max_lines = st.number_input(
                "Maximum lines per commit",
                min_value=0,
                max_value=1000000,
                value=st.session_state.max_lines_per_commit,
                step=10000,
                help="Commits with more lines than this will be ignored. Set to 0 to disable."
            )

            # If any setting changed, update and re-analyze
            if (new_threshold != st.session_state.similarity_threshold or
                    new_max_lines != st.session_state.max_lines_per_commit):
                st.session_state.similarity_threshold = new_threshold
                st.session_state.max_lines_per_commit = new_max_lines
                analyze_repository()
                st.rerun()

            # Get the original author names from the repository
            original_authors = set()
            for commit in st.session_state.analyzer.repo.iter_commits():
                original_authors.add(commit.author.name)

            # Display author mappings in an expandable section
            with st.expander("Show Author Mappings", expanded=True):
                st.write("The following author names have been merged:")
                groups = AuthorNormalizer.find_similar_names(
                    list(original_authors),
                    st.session_state.similarity_threshold
                )

                if not any(len(names) > 1 for names in groups.values()):
                    st.info("No author names were merged with the current similarity threshold.")
                else:
                    for canonical_name, similar_names in groups.items():
                        if len(similar_names) > 1:
                            st.markdown(f"**{canonical_name}**")
                            for name in similar_names:
                                if name != canonical_name:
                                    st.markdown(f"- {name}")
                            st.markdown("---")


if __name__ == "__main__":
    main()
