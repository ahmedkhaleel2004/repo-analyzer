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
        - Private repos (if included)
        """
        # First, filter out repos we don't want to analyze
        filtered_repos = []
        for repo in repos:
            # Skip archived repos
            if repo.get("isArchived", False):
                continue

            # Skip forks
            if repo.get("isFork", False):
                continue

            # Skip empty repos
            if repo.get("isEmpty", False):
                continue

            # Skip private repos (in case they're included)
            if repo.get("isPrivate", False):
                continue

            filtered_repos.append(repo)

        # Calculate importance score for ranking
        def importance_score(repo: Dict[str, Any]) -> float:
            stars = repo.get("stargazerCount", 0)
            forks = repo.get("forkCount", 0)

            # Weight stars more heavily than forks
            score = (stars * 1.0) + (forks * 0.5)

            # Boost score for repos with recent activity
            pushed_at = repo.get("pushedAt")
            if pushed_at:
                from datetime import datetime, timezone

                pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
                days_since_push = (datetime.now(timezone.utc) - pushed_date).days

                # Boost repos pushed in last 30 days
                if days_since_push < 30:
                    score *= 1.2
                # Penalize repos not pushed in over a year
                elif days_since_push > 365:
                    score *= 0.8

            return score

        # Sort by importance score
        filtered_repos.sort(key=importance_score, reverse=True)

        # Select top repos that represent significant portion of org's activity
        if len(filtered_repos) <= max_repos:
            selected = filtered_repos
        else:
            # Calculate total stars in org
            total_stars = sum(r.get("stargazerCount", 0) for r in filtered_repos)

            # Select repos until we have 80% of total stars or max_repos
            selected = []
            accumulated_stars = 0

            for repo in filtered_repos:
                selected.append(repo)
                accumulated_stars += repo.get("stargazerCount", 0)

                # Stop if we've reached max repos
                if len(selected) >= max_repos:
                    break

                # Stop if we've covered 80% of total stars (but take at least 5)
                if len(selected) >= 5 and accumulated_stars >= total_stars * 0.8:
                    break

        print(
            f"Selected {len(selected)} repos out of {len(repos)} total "
            f"({len(filtered_repos)} after filtering)"
        )

        return selected
