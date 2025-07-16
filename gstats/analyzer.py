"""Repository analysis module."""

from pathlib import Path
from zoneinfo import ZoneInfo

import git
import pandas as pd

from gstats.author_normalizer import AuthorNormalizer


class RepositoryAnalyzer:
    """Class for analyzing git repositories."""

    def __init__(self, repo_path: str | Path, author_similarity_threshold: float = 0.7, manual_author_mappings: dict = None):
        """Initialize the analyzer with a repository path."""
        self.repo_path = Path(repo_path)
        self.repo = None
        self.author_similarity_threshold = author_similarity_threshold
        self.manual_author_mappings = manual_author_mappings or {}
        self._load_repository()

    def _load_repository(self) -> None:
        """Load the git repository."""
        try:
            self.repo = git.Repo(self.repo_path)
        except git.InvalidGitRepositoryError:
            raise ValueError("Invalid git repository path")
        except Exception as e:
            raise RuntimeError(f"Error loading repository: {str(e)}")

    def get_raw_commit_data(self) -> tuple[pd.DataFrame, set[str]]:
        """Get raw commit data without author normalization."""
        commits = []
        original_authors = set()

        # Collect all commits and unique author names
        for commit in self.repo.iter_commits():
            try:
                stats = commit.stats.total
                commit_date = commit.committed_datetime
                author_name = commit.author.name

                # Handle timezone-aware datetime
                if commit_date.tzinfo is not None:
                    commit_date = commit_date.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)

                commits.append({
                    'hash': commit.hexsha,
                    'author': author_name,
                    'date': commit_date,
                    'message': commit.message.strip(),
                    'insertions': stats.get('insertions', 0),
                    'deletions': stats.get('deletions', 0),
                    'files_changed': stats.get('files', 0),
                    'branch': commit.name_rev.split(' ')[1].split('~')[0]
                })

                original_authors.add(author_name)
            except Exception as e:
                print(f"Warning: Skipping commit due to error: {str(e)}")
                continue

        return pd.DataFrame(commits), original_authors

    def get_commit_stats(self) -> pd.DataFrame:
        """Get commit statistics from the repository with author normalization."""
        # Get raw data
        df, original_authors = self.get_raw_commit_data()
        
        # Apply author normalization
        return self.apply_author_normalization(df, original_authors)

    def apply_author_normalization(self, df: pd.DataFrame, original_authors: set[str]) -> pd.DataFrame:
        """Apply author normalization to a DataFrame without re-reading git data."""
        if df.empty:
            return df
        
        # Create a copy to avoid modifying the original
        normalized_df = df.copy()
        
        # Get author mapping with manual mappings
        author_mapping = AuthorNormalizer.get_author_mapping(
            list(original_authors),
            self.author_similarity_threshold,
            self.manual_author_mappings
        )

        # Apply mapping to DataFrame
        normalized_df['author'] = normalized_df['author'].map(author_mapping)
        
        return normalized_df

    def get_repository_info(self) -> dict:
        """Get basic repository information."""
        if not self.repo:
            raise RuntimeError("Repository not loaded")

        return {
            'path': str(self.repo_path),
            'active_branch': self.repo.active_branch.name,
            'is_dirty': self.repo.is_dirty(),
            'untracked_files': self.repo.untracked_files,
            'branch_count': len(self.repo.branches)
        }
