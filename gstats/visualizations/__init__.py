"""Visualization module for git statistics."""

from gstats.visualizations.author_stats import AuthorStats
from gstats.visualizations.branch_stats import BranchStats
from gstats.visualizations.churn import CodeChurn
from gstats.visualizations.heatmap import CommitHeatmap
from gstats.visualizations.individual_author import IndividualAuthor
from gstats.visualizations.timeline import CommitTimeline


class GitVisualizer:
    """Class for creating git statistics visualizations."""

    @staticmethod
    def create_commit_heatmap(df):
        """Create a heatmap of commit activity."""
        return CommitHeatmap.create(df)

    @staticmethod
    def create_code_churn_timeline(df):
        """Create a timeline of code churn."""
        return CodeChurn.create(df)

    @staticmethod
    def create_commit_timeline(df):
        """Create a timeline of commits."""
        return CommitTimeline.create(df)

    @staticmethod
    def create_author_stats(df):
        """Create author contribution statistics."""
        return AuthorStats.create(df)

    @staticmethod
    def create_individual_author_contributions(df):
        """Create individual contribution visualizations for each author."""
        return IndividualAuthor.create(df)

    @staticmethod
    def create_individual_author_heatmaps(df):
        """Create individual author heatmaps."""
        return CommitHeatmap.create_individual_author_heatmaps(df)

    @staticmethod
    def create_branch_stats(df):
        """Create branch statistics visualization."""
        return BranchStats.create(df)
