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

    Returns:
        Dict mapping repo names to their health scores
    """
    print(f"\n🔍 Analyzing {org}...")

    # Initialize components
    fetcher = GitHubFetcher()
    selector = RepoSelector()
    scorer = HealthScorer()
    exporter = ResultExporter()

    try:
        # Fetch all repos
        print("📥 Fetching repositories from GitHub...")
        repos = await fetcher.fetch_org_repos(org)
        total_repos = len(repos)

        if not repos:
            print(f"❌ No repositories found for organization '{org}'")
            return {}

        # Select important ones
        print("🎯 Selecting important repositories...")
        important_repos = selector.select_important_repos(repos)

        if not important_repos:
            print("❌ No repositories met the selection criteria")
            return {}

        # Calculate scores
        print("📊 Calculating health scores...")
        repo_scores = []
        scores_dict = {}

        for i, repo in enumerate(important_repos, 1):
            repo_name = repo.get("name", "unknown")
            print(f"  [{i}/{len(important_repos)}] Scoring {repo_name}...", end="\r")

            score = scorer.calculate_score(repo)

            # Add score to repo data for export
            repo["health_score"] = score
            repo_scores.append(repo)

            # Also keep simple dict for return value
            scores_dict[repo_name] = score

        print()  # New line after progress

        # Export results
        print("💾 Exporting results...")
        output_file = exporter.export_results(org, repo_scores, total_repos)
        print(f"✅ Results saved to {output_file}")

        # Print summary
        avg_score = sum(scores_dict.values()) / len(scores_dict) if scores_dict else 0
        print(f"\n📈 Summary for {org}:")
        print(f"   - Total repositories: {total_repos}")
        print(f"   - Repositories analyzed: {len(important_repos)}")
        print(f"   - Average health score: {avg_score:.1f}/100")

        # Show top 5 repos
        top_repos = sorted(repo_scores, key=lambda r: r["health_score"], reverse=True)[
            :5
        ]
        if top_repos:
            print("\n🏆 Top 5 repositories:")
            for i, repo in enumerate(top_repos, 1):
                print(
                    f"   {i}. {repo['name']}: {repo['health_score']}/100 ⭐ {repo['stargazerCount']}"
                )

        return scores_dict

    except Exception as e:
        print(f"\n❌ Error analyzing {org}: {str(e)}")
        raise
