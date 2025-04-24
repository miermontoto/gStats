"""Base visualization module."""

import plotly.graph_objects as go


class BaseVisualization:
    """Base class for all visualizations."""

    @staticmethod
    def create_figure() -> go.Figure:
        """Create a base figure with common settings."""
        fig = go.Figure()
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Arial',
                size=12,
                color='#e0e0e0'
            )
        )
        return fig
