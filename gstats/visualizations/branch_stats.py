"""Branch statistics visualization module."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from gstats.visualizations.base import BaseVisualization


class BranchStats(BaseVisualization):
    """Class for creating branch statistics visualizations."""

    @staticmethod
    def create(df: pd.DataFrame) -> go.Figure:
        """Create branch statistics visualization."""
        branch_stats = df.groupby('branch').agg({
            'hash': 'count',
            'insertions': 'sum',
            'deletions': 'sum'
        }).reset_index()

        branch_stats.columns = ['Branch', 'Commits', 'Insertions', 'Deletions']

        fig = px.treemap(
            branch_stats,
            path=['Branch'],
            values='Commits',
            color='Insertions',
            title='Branch Activity'
        )
        return fig
