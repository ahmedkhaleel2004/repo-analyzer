# GitHub Repo Analyzer

A service that analyzes GitHub organizations and calculates health scores (0-100) for their most important repositories.

## Features

- CLI tool for analyzing GitHub organizations
- FastAPI web service for HTTP access
- Smart repository selection (filters out forks, archived repos, etc.)
- Health scoring based on multiple metrics
- JSON export of results
- Rate limit handling and caching
- Docker support for easy deployment

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
```

### Docker

```bash
docker build -t repo-analyzer .
docker run -e GITHUB_TOKEN=your_token repo-analyzer
```

## Usage

### CLI

```bash
# Set your GitHub token (optional but recommended for higher rate limits)
export GITHUB_TOKEN=ghp_your_token_here

# Analyze an organization
repo-analyzer SocketDev

# Results will be saved to results/SocketDev.json
```

### Web API

```bash
# Start the FastAPI server
uvicorn repo_analyzer.api:app --reload

# Visit http://localhost:8000/docs for API documentation
# Analyze an org: GET http://localhost:8000/analyze/SocketDev
```

## Health Score Algorithm

The health score (0-100) is calculated based on:

| Metric           | Weight | Description                        |
| ---------------- | ------ | ---------------------------------- |
| Commit Frequency | 30%    | Median commits/week (last 90 days) |
| Responsiveness   | 25%    | Mean time to close issues/PRs      |
| Release Cadence  | 15%    | Days since last release/tag        |
| Contributors     | 10%    | Unique contributors (90 days)      |
| Star Growth      | 10%    | Star growth rate (12 months)       |
| CI Health        | 10%    | CI pass rate (last 20 runs)        |

## Repository Selection

Not all repositories in an organization are analyzed. The selector:

1. **Filters out:**

   - Archived repositories
   - Forks
   - Empty repositories (size = 0)

2. **Ranks by:** Stars + Forks count

3. **Analyzes:** Top N repos (max 30) that represent ≥80% of org's total stars

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
├── fetcher.py       # GitHub API client
├── selector.py      # Repository filtering/ranking
├── scorer.py        # Health score calculation
├── exporter.py      # JSON export functionality
└── api.py           # FastAPI web service
```

## Configuration

Set these environment variables:

- `GITHUB_TOKEN`: Personal access token for GitHub API (required for private repos, recommended for rate limits)
- `CACHE_DB`: SQLite database path for caching (default: `cache.db`)

## Deployment

### Railway

```bash
railway init
railway secrets set GITHUB_TOKEN=ghp_your_token
railway up
```

### Manual Docker Deployment

```bash
docker build -t repo-analyzer .
docker run -d \
  -e GITHUB_TOKEN=ghp_your_token \
  -p 8000:8000 \
  repo-analyzer
```

## TODO

- [ ] Implement GitHub GraphQL queries in fetcher.py
- [ ] Add proper rate limit handling with backoff
- [ ] Implement caching with SQLite
- [ ] Calculate actual health metrics
- [ ] Add more comprehensive tests
- [ ] Support authentication for private repos
- [ ] Add progress bars for CLI
- [ ] Implement webhook support for real-time updates

## License

MIT
