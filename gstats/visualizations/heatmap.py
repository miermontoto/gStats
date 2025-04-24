"""Commit heatmap visualization module."""

import calendar

import pandas as pd
import plotly.graph_objects as go

from gstats.visualizations.base import BaseVisualization


class CommitHeatmap(BaseVisualization):
    """Class for creating commit heatmap visualizations."""

    @staticmethod
    def create(df: pd.DataFrame) -> go.Figure:
        """Create a heatmap of commit activity."""
        # Create a pivot table for the heatmap
        df['weekday'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
        heatmap_data = df.pivot_table(
            index='weekday',
            columns='hour',
            values='hash',
            aggfunc='count',
            fill_value=0
        )

        # Reorder weekdays
        weekdays = list(calendar.day_name)
        heatmap_data = heatmap_data.reindex(weekdays)

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Viridis'
        ))

        fig.update_layout(
            title='Commit Activity Heatmap',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week'
        )

        return fig

    @staticmethod
    def create_individual_author_heatmaps(df: pd.DataFrame) -> list[go.Figure]:
        """Create heatmaps for each individual author."""
        figures = []
        authors = df['author'].unique()

        for author in authors:
            author_df = df[df['author'] == author].copy()

            # Create a pivot table for the heatmap
            author_df['weekday'] = author_df['date'].dt.day_name()
            author_df['hour'] = author_df['date'].dt.hour
            heatmap_data = author_df.pivot_table(
                index='weekday',
                columns='hour',
                values='hash',
                aggfunc='count',
                fill_value=0
            )

            # Reorder weekdays
            weekdays = list(calendar.day_name)
            heatmap_data = heatmap_data.reindex(weekdays)

            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Viridis',
                hovertemplate='<b>%{y}</b><br>Hour: %{x}<br>Commits: %{z}<extra></extra>'
            ))

            fig.update_layout(
                title=dict(
                    text=f'<b>{author}</b><br>Commit Activity Heatmap',
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top'
                ),
                xaxis_title='Hour of Day',
                yaxis_title='Day of Week',
                height=350,
                margin=dict(l=20, r=20, t=80, b=20)
            )

            figures.append(fig)

        return figures
