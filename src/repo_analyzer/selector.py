"""Repository selector - filters and ranks repos by importance."""

from typing import List, Dict, Any


class RepoSelector:
    """Selects important repositories to analyze."""

    def select_important_repos(
        self, repos: List[Dict[str, Any]], max_repos: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Filter out unimportant repos and return top N by stars/forks.

        Filters out:
        - Archived repos
        - Forks
        - Empty repos
        """
        # TODO: Implement filtering and ranking logic
        filtered = [r for r in repos if not r.get("archived", False)]
        return filtered[:max_repos]
