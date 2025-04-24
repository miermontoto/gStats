"""Code churn visualization module."""

import pandas as pd
import plotly.graph_objects as go

from gstats.visualizations.base import BaseVisualization


class CodeChurn(BaseVisualization):
    """Class for creating code churn visualizations."""

    @staticmethod
    def create(df: pd.DataFrame) -> go.Figure:
        """Create a timeline of code churn."""
        df['net_changes'] = df['insertions'] - df['deletions']
        df['total_changes'] = df['insertions'] + df['deletions']

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['net_changes'].cumsum(),
            name='Net Changes',
            line=dict(color='green')
        ))

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['total_changes'].cumsum(),
            name='Total Changes',
            line=dict(color='blue')
        ))

        fig.update_layout(
            title='Code Churn Timeline',
            xaxis_title='Date',
            yaxis_title='Lines of Code',
            hovermode='x unified'
        )

        return fig
