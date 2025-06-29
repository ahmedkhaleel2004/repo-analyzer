# GitHub Repo Analyzer

A service that analyzes GitHub organizations and calculates health scores (0-100) for their most important repositories.

## 🚀 Live API

Try it now without installation:

```bash
# Analyze any GitHub organization
curl https://your-app-production.up.railway.app/analyze/vercel

# View API documentation
https://your-app-production.up.railway.app/docs
```

> Note: Replace `your-app-production` with your actual Railway subdomain

## Features

- ✅ **GraphQL API Integration** - Efficient data fetching with minimal API calls
- ✅ **Smart Repository Selection** - Analyzes top 30 most important repos
- ✅ **Comprehensive Health Scoring** - 6 weighted metrics for accurate assessment
- ✅ **SQLite Caching** - 1-hour cache to reduce API calls and improve speed
- ✅ **CLI & Web API** - Use via command line or REST API
- ✅ **Rate Limit Handling** - Automatic backoff when approaching limits
- ✅ **Docker Support** - Easy deployment anywhere

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/ahmedkhaleel2004/repo-analyzer.git
cd repo-analyzer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e '.[dev]'

# Copy environment variables
cp .env.example .env
# Edit .env and add your GitHub PAT token
```

### Docker

```bash
docker build -t repo-analyzer .
docker run -e GITHUB_PAT=your_token -p 8000:8000 repo-analyzer
```

## Usage

### CLI

```bash
# Basic usage
repo-analyzer SocketDev

# Bypass cache for fresh data
repo-analyzer SocketDev --no-cache

# Clear cache before running
repo-analyzer SocketDev --clear-cache

# Results saved to results/SocketDev.json
```

### Web API

```bash
# Start the FastAPI server
uvicorn repo_analyzer.api:app --reload

# Endpoints:
GET /                    # Health check
GET /analyze/{org}       # Analyze organization
GET /results/{org}       # Get cached results
GET /docs               # Interactive API documentation
```

### Example API Response

```json
{
  "organization": "vercel",
  "repository_scores": {
    "next.js": 100,
    "turborepo": 100,
    "ai": 100,
    "vercel": 100,
    "swr": 94
  },
  "total_repos_analyzed": 12,
  "average_score": 83.5,
  "results_file": "results/vercel.json"
}
```

## Health Score Algorithm

The health score (0-100) is calculated based on:

| Metric           | Weight | Description                                  |
| ---------------- | ------ | -------------------------------------------- |
| Commit Frequency | 30%    | Recent push activity (proxy for commits)     |
| Responsiveness   | 25%    | Closed issues/PRs count (activity indicator) |
| Release Cadence  | 15%    | Days since last release                      |
| Contributors     | 10%    | Fork count (proxy for contributors)          |
| Star Growth      | 10%    | Stars per month since creation               |
| CI Health        | 10%    | Recent push frequency (proxy for CI)         |

## Repository Selection

The analyzer intelligently selects repositories:

1. **Filters out:**

   - Archived repositories
   - Forks
   - Empty repositories
   - Private repositories

2. **Ranks by:** `stars × 1.0 + forks × 0.5` (with recency boost)

3. **Selects:** Top N repos (max 30) that represent ≥80% of org's total stars

## Caching

- API responses cached for 1 hour in SQLite database
- Reduces API calls and improves response time
- Cache location: `cache.db` (configurable via `CACHE_DB` env var)
- Use `--no-cache` flag to bypass cache
- Use `--clear-cache` flag to clear cache

## Configuration

Environment variables (see `.env.example`):

- `GITHUB_PAT` or `GITHUB_TOKEN`: GitHub Personal Access Token (required)
- `CACHE_DB`: SQLite database path (default: `cache.db`)
- `CACHE_TTL_HOURS`: Cache expiration in hours (default: 1)

## Development

### Running Tests Locally

```bash
# Run all CI checks (lint, type check, tests)
make ci

# Or run individually:
ruff check .
mypy src/
pytest -q
```

### Project Structure

```
src/repo_analyzer/
├── __init__.py      # Package initialization
├── cli.py           # CLI entry point (Typer)
├── engine.py        # Main orchestration logic
├── fetcher.py       # GitHub GraphQL API client
├── selector.py      # Repository filtering/ranking
├── scorer.py        # Health score calculation
├── exporter.py      # JSON export functionality
├── cache.py         # SQLite caching layer
└── api.py           # FastAPI web service
```

## Deployment

### Railway (Recommended)

The service is already deployed! To deploy your own:

1. Push to GitHub
2. Connect repo on [railway.app](https://railway.app)
3. Add environment variable: `GITHUB_PAT=your_token`
4. Railway auto-detects Dockerfile and deploys
5. Generate a public domain in settings

### Other Platforms

```bash
# Fly.io
fly launch
fly secrets set GITHUB_PAT=your_token
fly deploy

# Google Cloud Run
gcloud run deploy repo-analyzer \
  --source . \
  --set-env-vars GITHUB_PAT=your_token \
  --region us-central1

# Heroku
heroku create your-app-name
heroku config:set GITHUB_PAT=your_token
git push heroku main
```

## API Rate Limits

- With token: 5,000 requests/hour
- Without token: 60 requests/hour
- Our GraphQL queries are efficient (~2-3 requests per org)
- Caching further reduces API calls

## Examples

### Analyze Popular Organizations

```bash
# Large orgs
repo-analyzer microsoft
repo-analyzer google
repo-analyzer facebook

# Web frameworks
repo-analyzer vercel
repo-analyzer vuejs
repo-analyzer sveltejs

# Tools & platforms
repo-analyzer hashicorp
repo-analyzer docker
repo-analyzer kubernetes
```

## Performance

- SocketDev (43 repos): ~5 seconds
- Vercel (176 repos): ~8 seconds
- Microsoft (3000+ repos): ~45 seconds

With caching, subsequent requests return instantly.

## License

MIT
