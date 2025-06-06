"""Repository analysis module."""

from pathlib import Path
from zoneinfo import ZoneInfo

import git
import pandas as pd

from gstats.author_normalizer import AuthorNormalizer


class RepositoryAnalyzer:
    """Class for analyzing git repositories."""

    def __init__(self, repo_path: str | Path, author_similarity_threshold: float = 0.7):
        """Initialize the analyzer with a repository path."""
        self.repo_path = Path(repo_path)
        self.repo = None
        self.author_similarity_threshold = author_similarity_threshold
        self._load_repository()

    def _load_repository(self) -> None:
        """Load the git repository."""
        try:
            self.repo = git.Repo(self.repo_path)
        except git.InvalidGitRepositoryError:
            raise ValueError("Invalid git repository path")
        except Exception as e:
            raise RuntimeError(f"Error loading repository: {str(e)}")

    def get_commit_stats(self) -> pd.DataFrame:
        """Get commit statistics from the repository."""
        commits = []
        original_authors = set()

        # First pass: collect all commits and unique author names
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

        # Create DataFrame
        df = pd.DataFrame(commits)

        # Normalize author names
        if not df.empty:
            # Get author mapping
            author_mapping = AuthorNormalizer.get_author_mapping(
                list(original_authors),
                self.author_similarity_threshold
            )

            # Apply mapping to DataFrame
            df['author'] = df['author'].map(author_mapping)

        return df

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
