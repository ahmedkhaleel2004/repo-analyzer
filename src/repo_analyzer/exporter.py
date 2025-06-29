"""Export analysis results to JSON format."""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone


class ResultExporter:
    """Exports analysis results to JSON files."""

    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_results(
        self, org: str, repo_scores: List[Dict[str, Any]], total_repos_found: int
    ) -> Path:
        """
        Export repository scores to JSON file.

        Args:
            org: Organization name
            repo_scores: List of dicts with repo data and scores
            total_repos_found: Total repositories found before filtering
        """
        output_file = self.output_dir / f"{org}.json"

        # Sort repos by score (descending)
        sorted_repos = sorted(
            repo_scores, key=lambda r: r["health_score"], reverse=True
        )

        # Create summary statistics
        scores = [r["health_score"] for r in sorted_repos]

        data = {
            "organization": org,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_repos_in_org": total_repos_found,
                "repos_analyzed": len(sorted_repos),
                "average_health_score": (
                    round(sum(scores) / len(scores), 1) if scores else 0
                ),
                "median_health_score": (
                    sorted(scores)[len(scores) // 2] if scores else 0
                ),
                "top_score": max(scores) if scores else 0,
                "bottom_score": min(scores) if scores else 0,
            },
            "repositories": [
                {
                    "name": repo["name"],
                    "url": repo["url"],
                    "description": repo.get("description", ""),
                    "health_score": repo["health_score"],
                    "stars": repo["stargazerCount"],
                    "forks": repo["forkCount"],
                    "primary_language": (
                        repo.get("primaryLanguage", {}).get("name")
                        if repo.get("primaryLanguage")
                        else None
                    ),
                    "last_pushed": repo.get("pushedAt", ""),
                    "topics": [
                        node["topic"]["name"]
                        for node in repo.get("repositoryTopics", {}).get("nodes", [])
                    ],
                }
                for repo in sorted_repos
            ],
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        return output_file
