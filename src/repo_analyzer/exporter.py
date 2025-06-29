"""Export analysis results to JSON format."""

import json
from pathlib import Path
from typing import Dict


class ResultExporter:
    """Exports analysis results to JSON files."""

    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_results(self, org: str, scores: Dict[str, int]) -> Path:
        """Export repository scores to JSON file."""
        output_file = self.output_dir / f"{org}.json"

        data = {
            "organization": org,
            "repository_scores": scores,
            "analyzed_at": "2024-01-01T00:00:00Z",  # TODO: Use actual timestamp
            "total_repos_analyzed": len(scores),
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        return output_file
