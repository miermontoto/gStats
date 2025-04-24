"""Individual author contributions visualization module."""

import pandas as pd
import plotly.graph_objects as go

from gstats.visualizations.base import BaseVisualization


class IndividualAuthor(BaseVisualization):
    """Class for creating individual author contribution visualizations."""

    @staticmethod
    def create(df: pd.DataFrame) -> list[go.Figure]:
        """Create individual contribution visualizations for each author."""
        # Calculate total changes for the entire dataset first
        df['total_changes'] = df['insertions'] + df['deletions']

        # Calculate total changes per author and sort authors
        author_totals = df.groupby('author')['total_changes'].sum().sort_values(ascending=False)
        authors = author_totals.index.tolist()

        figures = []

        # Calculate global min and max dates for consistent time periods
        min_date = df['date'].min()
        max_date = df['date'].max()

        # Calculate global max values for consistent scales
        max_changes = df.groupby('author')['total_changes'].sum().max()
        max_cumulative = df.groupby('author')['total_changes'].sum().max()

        # Get current month for comparison
        current_month = pd.Timestamp.now().normalize().replace(day=1)

        for author in authors:
            author_df = df[df['author'] == author].copy()

            # Calculate author statistics
            total_commits = len(author_df)
            total_changes = author_df['total_changes'].sum()
            avg_changes = total_changes / total_commits
            first_commit = author_df['date'].min()
            last_commit = author_df['date'].max()

            # Resample to monthly periods
            period_df = author_df.set_index('date').resample('ME')['total_changes'].sum().reset_index()
            period_df['cumulative_total'] = period_df['total_changes'].cumsum()

            # Create figure
            fig = go.Figure()

            # Add bars for period changes
            fig.add_trace(go.Bar(
                x=period_df['date'],
                y=period_df['total_changes'],
                name='Changes per Month',
                marker_color='rgba(100, 181, 246, 0.7)',  # Light blue
                opacity=0.7,
                hovertemplate='<b>%{x|%B %Y}</b><br>Changes: %{y:,}<extra></extra>'
            ))

            # Add line for cumulative total
            fig.add_trace(go.Scatter(
                x=period_df['date'],
                y=period_df['cumulative_total'],
                name='Cumulative Total',
                line=dict(color='#FF8A65', width=2),  # Light orange
                yaxis='y2',
                hovertemplate='<b>%{x|%B %Y}</b><br>Cumulative: %{y:,}<extra></extra>'
            ))

            # Update layout with consistent scales
            fig.update_layout(
                title=dict(
                    text=f'<b>{author}</b><br>'
                         f'<span style="font-size: 12px; color: #9e9e9e">'
                         f'{total_changes:,} lines | {total_commits:,} commits | '
                         f'avg: {avg_changes:.0f} lines/commit</span>',
                    x=0.5,
                    y=0.95,
                    xanchor='center',
                    yanchor='top'
                ),
                xaxis=dict(
                    range=[min_date, max_date],
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    color='#9e9e9e',
                    showticklabels=True,
                    showline=False,
                    zeroline=False
                ),
                yaxis=dict(
                    range=[0, max_changes * 1.1],
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    color='#9e9e9e',
                    showticklabels=True,
                    showline=False,
                    zeroline=False
                ),
                yaxis2=dict(
                    range=[0, max_cumulative * 1.1],
                    overlaying='y',
                    side='right',
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    color='#9e9e9e',
                    showticklabels=True,
                    showline=False,
                    zeroline=False
                ),
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    font=dict(color='#9e9e9e')
                ),
                height=350,
                margin=dict(l=20, r=20, t=80, b=20),
                barmode='group'
            )

            figures.append(fig)

        return figures
