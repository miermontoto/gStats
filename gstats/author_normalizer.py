"""Author name normalization module."""

import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple


class AuthorNormalizer:
    """Class for normalizing author names."""

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize a name by removing special characters and converting to lowercase."""
        # Remove special characters and convert to lowercase
        normalized = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        return normalized

    @staticmethod
    def similar(a: str, b: str, threshold: float = 0.8) -> bool:
        """Check if two strings are similar based on a threshold."""
        return SequenceMatcher(None, a, b).ratio() > threshold

    @staticmethod
    def find_similar_names(names: List[str], threshold: float = 0.8) -> Dict[str, List[str]]:
        """Find similar names in a list and group them together."""
        normalized_names = {name: AuthorNormalizer.normalize_name(name) for name in names}
        groups: Dict[str, List[str]] = {}

        for name, normalized in normalized_names.items():
            found_group = False
            for group_name in list(groups.keys()):
                if AuthorNormalizer.similar(normalized, AuthorNormalizer.normalize_name(group_name), threshold):
                    groups[group_name].append(name)
                    found_group = True
                    break
            if not found_group:
                groups[name] = [name]

        return groups

    @staticmethod
    def get_author_mapping(names: List[str], threshold: float = 0.8) -> Dict[str, str]:
        """Create a mapping from original names to their normalized versions."""
        groups = AuthorNormalizer.find_similar_names(names, threshold)
        mapping: Dict[str, str] = {}

        for canonical_name, similar_names in groups.items():
            for name in similar_names:
                mapping[name] = canonical_name

        return mapping
