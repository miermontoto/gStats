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
    def get_author_mapping(names: List[str], threshold: float = 0.8, manual_mappings: Dict[str, str] = None) -> Dict[str, str]:
        """Create a mapping from original names to their normalized versions."""
        if manual_mappings is None:
            manual_mappings = {}
        
        # Start with automatic similarity grouping
        groups = AuthorNormalizer.find_similar_names(names, threshold)
        mapping: Dict[str, str] = {}

        for canonical_name, similar_names in groups.items():
            for name in similar_names:
                mapping[name] = canonical_name

        # Apply manual mappings, which override automatic ones
        # Also ensure transitive merging (if A->B and C->B, then A and C both map to B)
        manual_groups = {}
        for original_name, target_name in manual_mappings.items():
            if original_name in names and target_name in names:
                # Find the canonical target (resolve chains)
                final_target = target_name
                visited = set()
                while final_target in manual_mappings and final_target not in visited:
                    visited.add(final_target)
                    final_target = manual_mappings[final_target]
                
                if final_target not in manual_groups:
                    manual_groups[final_target] = []
                manual_groups[final_target].append(original_name)
        
        # Apply manual groupings
        for target, sources in manual_groups.items():
            for source in sources:
                mapping[source] = target
            # Ensure the target maps to itself
            mapping[target] = target

        return mapping

    @staticmethod
    def get_combined_groups(names: List[str], threshold: float = 0.8, manual_mappings: Dict[str, str] = None) -> Dict[str, List[str]]:
        """Get author groups combining both automatic similarity and manual mappings."""
        if manual_mappings is None:
            manual_mappings = {}
        
        # Get the final mapping
        final_mapping = AuthorNormalizer.get_author_mapping(names, threshold, manual_mappings)
        
        # Build reverse mapping to show groups
        groups: Dict[str, List[str]] = {}
        for original_name, canonical_name in final_mapping.items():
            if canonical_name not in groups:
                groups[canonical_name] = []
            groups[canonical_name].append(original_name)
        
        # Remove single-item groups for display
        return {k: v for k, v in groups.items() if len(v) > 1}

    @staticmethod
    def get_merge_options(names: List[str], threshold: float = 0.8, manual_mappings: Dict[str, str] = None) -> tuple[List[str], List[str]]:
        """Get available merge options: (authors_that_can_be_merged, merge_targets)."""
        if manual_mappings is None:
            manual_mappings = {}
        
        # Get the final mapping to understand current state
        final_mapping = AuthorNormalizer.get_author_mapping(names, threshold, manual_mappings)
        
        # Find canonical authors (those who are the target of mappings)
        canonical_authors = set()
        mapped_authors = set()
        
        for original, canonical in final_mapping.items():
            canonical_authors.add(canonical)
            if original != canonical:
                mapped_authors.add(original)
        
        # Authors that can be merged: those not already merged into someone else
        authors_to_merge = [name for name in names if name not in mapped_authors]
        
        # Merge targets: canonical authors (group leaders) and standalone authors
        merge_targets = sorted(list(canonical_authors))
        
        return sorted(authors_to_merge), merge_targets
