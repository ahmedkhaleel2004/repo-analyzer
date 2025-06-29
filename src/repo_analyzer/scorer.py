"""Repository health score calculator."""

from datetime import UTC, datetime
from typing import Any


class HealthScorer:
    """Calculates health scores for repositories."""

    def __init__(self):
        # Weights for each metric (must sum to 1.0)
        self.weights = {
            "commit_frequency": 0.30,
            "responsiveness": 0.25,
            "release_cadence": 0.15,
            "contributors": 0.10,
            "star_growth": 0.10,
            "ci_health": 0.10,
        }

    def calculate_score(self, repo_data: dict[str, Any]) -> int:
        """
        Calculate health score (0-100) based on various metrics.

        Metrics considered:
        - Commit frequency (30%): Median commits/week (last 90 days)
        - Responsiveness (25%): Mean time to close issues/PRs
        - Release cadence (15%): Days since last release/tag
        - Contributors (10%): Unique contributors (90 days)
        - Star growth (10%): Star growth rate (12 months)
        - CI health (10%): CI pass rate (last 20 runs)
        """
        scores = {}

        # 1. Commit Frequency Score (30%)
        scores["commit_frequency"] = self._score_commit_frequency(repo_data)

        # 2. Responsiveness Score (25%)
        scores["responsiveness"] = self._score_responsiveness(repo_data)

        # 3. Release Cadence Score (15%)
        scores["release_cadence"] = self._score_release_cadence(repo_data)

        # 4. Contributors Score (10%)
        scores["contributors"] = self._score_contributors(repo_data)

        # 5. Star Growth Score (10%)
        scores["star_growth"] = self._score_star_growth(repo_data)

        # 6. CI Health Score (10%)
        scores["ci_health"] = self._score_ci_health(repo_data)

        # Calculate weighted sum
        total_score = sum(
            scores[metric] * self.weights[metric] for metric in self.weights
        )

        # Round to integer 0-100
        return max(0, min(100, round(total_score)))

    def _score_commit_frequency(self, repo: dict[str, Any]) -> float:
        """Score based on commit frequency in the last 90 days."""
        # For now, use pushedAt as a proxy (since getting commit history is expensive)
        pushed_at = repo.get("pushedAt")
        if not pushed_at:
            return 0

        pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        days_since_push = (datetime.now(UTC) - pushed_date).days

        # Score based on recency of push
        if days_since_push <= 7:
            return 100
        elif days_since_push <= 30:
            return 80
        elif days_since_push <= 90:
            return 60
        elif days_since_push <= 180:
            return 40
        elif days_since_push <= 365:
            return 20
        else:
            return 0

    def _score_responsiveness(self, repo: dict[str, Any]) -> float:
        """Score based on issue/PR closure rates."""
        # We have total closed issues and PRs from GraphQL
        closed_issues = repo.get("issues", {}).get("totalCount", 0)
        closed_prs = repo.get("pullRequests", {}).get("totalCount", 0)

        # Without open counts, we'll use total closed as a proxy for activity
        total_closed = closed_issues + closed_prs

        # More closed items = more responsive (simplified)
        if total_closed >= 100:
            return 100
        elif total_closed >= 50:
            return 80
        elif total_closed >= 20:
            return 60
        elif total_closed >= 10:
            return 40
        elif total_closed >= 5:
            return 20
        else:
            return 10  # Give some points for existing

    def _score_release_cadence(self, repo: dict[str, Any]) -> float:
        """Score based on days since last release."""
        releases = repo.get("releases", {}).get("nodes", [])

        if not releases:
            # No releases, check if it's a new repo
            created_at = repo.get("createdAt")
            if created_at:
                created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                repo_age_days = (datetime.now(UTC) - created_date).days

                # If repo is less than 30 days old, don't penalize
                if repo_age_days < 30:
                    return 50
            return 0

        last_release = releases[0]
        release_date = datetime.fromisoformat(
            last_release["createdAt"].replace("Z", "+00:00")
        )
        days_since_release = (datetime.now(UTC) - release_date).days

        # Score based on recency
        if days_since_release <= 30:
            return 100
        elif days_since_release <= 90:
            return 80
        elif days_since_release <= 180:
            return 60
        elif days_since_release <= 365:
            return 40
        else:
            return 20

    def _score_contributors(self, repo: dict[str, Any]) -> float:
        """Score based on contributor diversity."""
        # Without expensive API calls, use forks as proxy for community
        forks = repo.get("forkCount", 0)

        # Forks indicate potential contributors
        if forks >= 50:
            return 100
        elif forks >= 20:
            return 80
        elif forks >= 10:
            return 60
        elif forks >= 5:
            return 40
        elif forks >= 2:
            return 20
        else:
            return 10

    def _score_star_growth(self, repo: dict[str, Any]) -> float:
        """Score based on star growth rate."""
        stars = repo.get("stargazerCount", 0)
        created_at = repo.get("createdAt")

        if not created_at or stars == 0:
            return 0

        # Calculate stars per month
        created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        repo_age_days = max(1, (datetime.now(UTC) - created_date).days)
        repo_age_months = max(1, repo_age_days / 30)

        stars_per_month = stars / repo_age_months

        # Score based on growth rate
        if stars_per_month >= 100:
            return 100
        elif stars_per_month >= 50:
            return 90
        elif stars_per_month >= 20:
            return 80
        elif stars_per_month >= 10:
            return 70
        elif stars_per_month >= 5:
            return 60
        elif stars_per_month >= 2:
            return 50
        elif stars_per_month >= 1:
            return 40
        elif stars_per_month >= 0.5:
            return 30
        else:
            return 20

    def _score_ci_health(self, repo: dict[str, Any]) -> float:
        """Score based on CI health (using push recency as proxy)."""
        # Without access to CI data, use recent push as proxy for active development
        pushed_at = repo.get("pushedAt")
        if not pushed_at:
            return 50  # Neutral score if no data

        pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        days_since_push = (datetime.now(UTC) - pushed_date).days

        # Recent pushes suggest active CI
        if days_since_push <= 1:
            return 100
        elif days_since_push <= 7:
            return 90
        elif days_since_push <= 14:
            return 80
        elif days_since_push <= 30:
            return 70
        else:
            return 50  # Don't heavily penalize
