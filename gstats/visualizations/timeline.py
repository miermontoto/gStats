"""Commit timeline visualization module."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from gstats.visualizations.base import BaseVisualization


class CommitTimeline(BaseVisualization):
    """Class for creating commit timeline visualizations."""

    @staticmethod
    def create(df: pd.DataFrame) -> go.Figure:
        """Create a timeline of commits."""
        fig = px.scatter(
            df,
            x='date',
            y='author',
            size='files_changed',
            color='branch',
            title='Commit Timeline by Author',
            labels={'date': 'Date', 'author': 'Author'}
        )
        return fig
