"""FastAPI web service for repo analysis."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .engine import analyze_org

app = FastAPI(
    title="GitHub Repo Analyzer",
    version="0.1.0",
    description="Analyze GitHub organizations and calculate repository health scores",
)


class AnalysisResponse(BaseModel):
    organization: str
    repository_scores: dict[str, int]
    total_repos_analyzed: int
    average_score: float
    results_file: str


class HealthResponse(BaseModel):
    status: str
    service: str
    github_token_configured: bool


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="repo-analyzer",
        github_token_configured=bool(
            os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
        ),
    )


@app.get("/analyze/{org}", response_model=AnalysisResponse)
async def analyze_organization(org: str):
    """
    Analyze a GitHub organization and return scores.

    This endpoint will fetch all repositories from the organization,
    select the most important ones, calculate health scores, and
    save the results to a JSON file.
    """
    try:
        # Run the analysis
        scores = await analyze_org(org)

        if not scores:
            raise HTTPException(
                status_code=404,
                detail=f"No repositories found or analyzed for organization '{org}'",
            )

        # Calculate average
        avg_score = sum(scores.values()) / len(scores) if scores else 0

        # Path to results file
        results_file = f"results/{org}.json"

        return AnalysisResponse(
            organization=org,
            repository_scores=scores,
            total_repos_analyzed=len(scores),
            average_score=round(avg_score, 1),
            results_file=results_file,
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in API: {str(e)}")

        # Return appropriate HTTP error
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e)) from None
        elif "token" in str(e).lower():
            raise HTTPException(status_code=401, detail=str(e)) from None
        elif "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail=str(e)) from None
        else:
            raise HTTPException(
                status_code=500, detail=f"Analysis failed: {str(e)}"
            ) from None


@app.get("/results/{org}")
async def get_results(org: str):
    """
    Get the analysis results for an organization.

    Returns the JSON file if it exists.
    """
    results_path = Path(f"results/{org}.json")

    if not results_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No results found for organization '{org}'. Run /analyze/{org} first.",
        )

    return FileResponse(
        path=results_path,
        media_type="application/json",
        filename=f"{org}_analysis.json",
    )
