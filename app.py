"""Main application module."""

from pathlib import Path

import streamlit as st

from gstats.analyzer import RepositoryAnalyzer
from gstats.visualizations import GitVisualizer

st.set_page_config(
    page_title="gStats",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for success message
if 'show_success' not in st.session_state:
    st.session_state.show_success = False


def main():
    """Main application function."""
    # Sidebar layout
    with st.sidebar:
        st.title("📊 gStats")
        st.sidebar.title("Repository Settings")

        # Repository path input
        repo_path = st.text_input(
            "Enter repository path",
            value=str(Path.home())
        )

    if st.sidebar.button("Analyze"):
        with st.spinner("Analyzing repository..."):
            try:
                analyzer = RepositoryAnalyzer(repo_path)
                df = analyzer.get_commit_stats()
                repo_info = analyzer.get_repository_info()

                # Set success message to show
                st.session_state.show_success = True

                # Display repository title in main container
                repo_name = Path(repo_info['path']).name
                st.markdown(f"# {repo_name}")

                # Display repository information in sidebar
                st.sidebar.subheader("Repository Information")
                st.sidebar.write(f"**Path:** {repo_info['path']}")
                st.sidebar.write(f"**Active Branch:** {repo_info['active_branch']}")

                if repo_info['untracked_files']:
                    st.sidebar.warning(f"**Untracked Files:** {len(repo_info['untracked_files'])}")
                    with st.sidebar.expander("Show untracked files"):
                        for file in repo_info['untracked_files']:
                            st.code(file)

                # Get date range for the entire project
                min_date = df['date'].min()
                max_date = df['date'].max()

                # Display date range info
                st.sidebar.info(f"**Project lifespan:** {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")

                # Display basic stats
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric("Commits", len(df))

                with col2:
                    st.metric("Authors", df['author'].nunique())

                # TODO: mostrar inserciones y borrados por separado, con colorines
                with col3:
                    insertions = df['insertions'].sum()
                    deletions = df['deletions'].sum()
                    # delta = f"+{insertions:,} 📈 / -{deletions:,} 📉"
                    st.metric(
                        "Lines changed",
                        f"{insertions + deletions:,}",
                        # delta=delta,
                        # delta_color="normal"
                    )

                with col4:
                    st.metric("Files changed", df['files_changed'].sum())

                with col5:
                    st.metric("Branches", repo_info['branch_count'])

                # Tabs for different visualizations
                tab1, tab2, tab3, tab4 = st.tabs([
                    "Commit Activity", "Author Stats", "Code Churn", "Branch Info"
                ])

                with tab1:
                    # Commit timeline
                    st.subheader("Commit Timeline")
                    fig = GitVisualizer.create_commit_timeline(df)
                    st.plotly_chart(fig, use_container_width=True)

                    # Commit heatmap
                    st.subheader("Commit Activity Heatmap")
                    heatmap_fig = GitVisualizer.create_commit_heatmap(df)
                    st.plotly_chart(heatmap_fig, use_container_width=True)

                with tab2:
                    # Author contributions overview
                    st.subheader("Author Contributions Overview")
                    author_fig = GitVisualizer.create_author_stats(df)
                    st.plotly_chart(author_fig, use_container_width=True)

                    # Individual author contributions
                    st.subheader("Individual Author Contributions")
                    author_figs = GitVisualizer.create_individual_author_contributions(df)

                    # Display author contribution graphs in a grid
                    cols = st.columns(2)  # Create 2 columns
                    for i, fig in enumerate(author_figs):
                        with cols[i % 2]:  # Alternate between columns
                            st.plotly_chart(fig, use_container_width=True)

                    # Individual author heatmaps
                    st.subheader("Individual Author Commit Patterns")
                    author_heatmaps = GitVisualizer.create_individual_author_heatmaps(df)

                    # Display author heatmaps in a grid
                    cols = st.columns(2)  # Create 2 columns
                    for i, heatmap in enumerate(author_heatmaps):
                        with cols[i % 2]:  # Alternate between columns
                            st.plotly_chart(heatmap, use_container_width=True)

                with tab3:
                    # Code churn timeline
                    st.subheader("Code Churn Timeline")
                    churn_fig = GitVisualizer.create_code_churn_timeline(df)
                    st.plotly_chart(churn_fig, use_container_width=True)

                with tab4:
                    # Branch information
                    st.subheader("Branch Statistics")
                    branch_fig = GitVisualizer.create_branch_stats(df)
                    st.plotly_chart(branch_fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error analyzing repository: {str(e)}")

                # print trace in console
                import traceback
                traceback.print_exc()

    # Display success message if it exists and handle dismissal
    if st.session_state.show_success:
        success_container = st.empty()
        with success_container:
            success = st.success("Repository analyzed successfully!")
            if st.button("Dismiss", key="dismiss_success"):
                st.session_state.show_success = False
                success_container.empty()


if __name__ == "__main__":
    main()
