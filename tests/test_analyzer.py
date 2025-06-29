"""Tests for the repo analyzer components."""

from repo_analyzer.scorer import HealthScorer
from repo_analyzer.selector import RepoSelector
from datetime import datetime, timezone, timedelta


class TestHealthScorer:
    """Test the health scoring logic."""

    def test_perfect_score(self):
        """Test a repository that should get a perfect score."""
        scorer = HealthScorer()

        # Mock repo data with perfect metrics
        repo_data = {
            "name": "perfect-repo",
            "stargazerCount": 10000,
            "forkCount": 500,
            "pushedAt": datetime.now(timezone.utc).isoformat(),
            "createdAt": (datetime.now(timezone.utc) - timedelta(days=365)).isoformat(),
            "issues": {"totalCount": 1000},
            "pullRequests": {"totalCount": 500},
            "releases": {
                "nodes": [{"createdAt": datetime.now(timezone.utc).isoformat()}]
            },
        }

        score = scorer.calculate_score(repo_data)
        assert score >= 90  # Should be very high

    def test_abandoned_repo(self):
        """Test a repository that appears abandoned."""
        scorer = HealthScorer()

        # Mock repo data for abandoned project
        repo_data = {
            "name": "abandoned-repo",
            "stargazerCount": 100,
            "forkCount": 5,
            "pushedAt": (datetime.now(timezone.utc) - timedelta(days=730)).isoformat(),
            "createdAt": (
                datetime.now(timezone.utc) - timedelta(days=1000)
            ).isoformat(),
            "issues": {"totalCount": 10},
            "pullRequests": {"totalCount": 2},
            "releases": {"nodes": []},
        }

        score = scorer.calculate_score(repo_data)
        assert score < 30  # Should be very low

    def test_score_range(self):
        """Test that scores are always in valid range."""
        scorer = HealthScorer()

        # Test with minimal data
        repo_data = {"name": "test"}
        score = scorer.calculate_score(repo_data)

        assert 0 <= score <= 100


class TestRepoSelector:
    """Test the repository selection logic."""

    def test_filters_archived(self):
        """Test that archived repos are filtered out."""
        selector = RepoSelector()

        repos = [
            {"name": "active", "isArchived": False, "stargazerCount": 100},
            {"name": "archived", "isArchived": True, "stargazerCount": 200},
        ]

        selected = selector.select_important_repos(repos)
        assert len(selected) == 1
        assert selected[0]["name"] == "active"

    def test_filters_forks(self):
        """Test that forks are filtered out."""
        selector = RepoSelector()

        repos = [
            {"name": "original", "isFork": False, "stargazerCount": 100},
            {"name": "fork", "isFork": True, "stargazerCount": 200},
        ]

        selected = selector.select_important_repos(repos)
        assert len(selected) == 1
        assert selected[0]["name"] == "original"

    def test_sorts_by_importance(self):
        """Test that repos are sorted by importance."""
        selector = RepoSelector()

        repos = [
            {"name": "small", "stargazerCount": 10, "forkCount": 1},
            {"name": "medium", "stargazerCount": 100, "forkCount": 10},
            {"name": "large", "stargazerCount": 1000, "forkCount": 100},
        ]

        selected = selector.select_important_repos(repos)
        assert selected[0]["name"] == "large"
        assert selected[1]["name"] == "medium"
        assert selected[2]["name"] == "small"

    def test_respects_max_repos(self):
        """Test that max_repos limit is respected."""
        selector = RepoSelector()

        # Create 50 repos
        repos = [{"name": f"repo{i}", "stargazerCount": i} for i in range(50)]

        selected = selector.select_important_repos(repos, max_repos=10)
        assert len(selected) == 10
