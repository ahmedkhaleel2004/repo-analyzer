"""Main analysis engine that orchestrates the workflow."""

from typing import Dict
from .fetcher import GitHubFetcher
from .selector import RepoSelector
from .scorer import HealthScorer
from .exporter import ResultExporter


async def analyze_org(org: str) -> Dict[str, int]:
    """
    Analyze a GitHub organization and return health scores.

    Workflow:
    1. Fetch repos from GitHub
    2. Select important repos
    3. Calculate health scores
    4. Export results
    """
    print(f"Analyzing {org}...")

    # Initialize components
    fetcher = GitHubFetcher()
    selector = RepoSelector()
    scorer = HealthScorer()
    exporter = ResultExporter()

    # Fetch all repos
    repos = await fetcher.fetch_org_repos(org)

    # Select important ones
    important_repos = selector.select_important_repos(repos)

    # Calculate scores
    scores = {}
    for repo in important_repos:
        repo_name = repo.get("name", "unknown")
        score = scorer.calculate_score(repo)
        scores[repo_name] = score

    # Export results
    output_file = exporter.export_results(org, scores)
    print(f"Results saved to {output_file}")

    return scores
