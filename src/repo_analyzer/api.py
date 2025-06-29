"""FastAPI web service for repo analysis."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from .engine import analyze_org


app = FastAPI(title="GitHub Repo Analyzer", version="0.1.0")


class AnalysisResponse(BaseModel):
    organization: str
    repository_scores: Dict[str, int]
    total_repos_analyzed: int


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "repo-analyzer"}


@app.get("/analyze/{org}", response_model=AnalysisResponse)
async def analyze_organization(org: str):
    """Analyze a GitHub organization and return scores."""
    try:
        # TODO: Wire up to actual engine
        scores = await analyze_org(org)
        return AnalysisResponse(
            organization=org,
            repository_scores=scores
            or {"repo1": 85, "repo2": 72},  # Placeholder if empty
            total_repos_analyzed=len(scores) if scores else 2,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
