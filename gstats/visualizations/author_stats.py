"""Author statistics visualization module."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from gstats.visualizations.base import BaseVisualization


class AuthorStats(BaseVisualization):
    """Class for creating author statistics visualizations."""

    @staticmethod
    def create(df: pd.DataFrame) -> go.Figure:
        """Create author contribution statistics."""
        # Calculate total changes
        df['total_changes'] = df['insertions'] + df['deletions']

        author_stats = df.groupby('author').agg({
            'hash': 'count',
            'total_changes': 'sum',
            'files_changed': 'sum'
        }).reset_index()

        author_stats.columns = ['Author', 'Commits', 'Total Changes', 'Files Changed']

        # Sort by total changes
        author_stats = author_stats.sort_values('Total Changes', ascending=False)

        fig = px.bar(
            author_stats,
            x='Author',
            y='Total Changes',
            title='Total Changes by Author',
            color='Total Changes',
            color_continuous_scale='Blues'
        )

        fig.update_layout(
            xaxis_title='Author',
            yaxis_title='Lines Changed',
            showlegend=False
        )

        return fig
