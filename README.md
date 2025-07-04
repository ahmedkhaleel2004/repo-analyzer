# GitHub Repo Analyzer

Analyzes GitHub organizations and scores repository health (0-100). Higher scores = better maintained repos.

## How We Select Repositories

The smart selection algorithm focuses on what matters:

1. **Filters out**: Forks, archived repos, empty repos, and private repos
2. **Ranks by importance**: `stars × 1.0 + forks × 0.5`
3. **Boosts recent activity**: ×1.2 multiplier if pushed in last 30 days
4. **Selects top repos**: Up to 30 repos that represent 80% of organization's total stars

This ensures we analyze the most important repositories while saving time and API calls.

## Health Score Calculation

| Metric            | Weight | How It's Measured               |
| ----------------- | ------ | ------------------------------- |
| Recent Activity   | 30%    | Days since last push            |
| Issue/PR Activity | 25%    | Total closed issues and PRs     |
| Recent Releases   | 15%    | Days since last release         |
| Community         | 10%    | Fork count (contributor proxy)  |
| Popularity Growth | 10%    | Stars per month since creation  |
| CI Activity       | 10%    | Recent pushes (CI health proxy) |

## 🚀 Try It Now (No Installation!)

```bash
# Analyze any GitHub organization
curl https://repo-analyzer-production-247d.up.railway.app/analyze/socketdev
```

Or visit the interactive docs: https://repo-analyzer-production-247d.up.railway.app/docs

## What It Does

This tool helps you quickly assess which repositories in a GitHub organization are actively maintained:

- **Fetches** all repos from an organization
- **Filters** out forks, archived, and unimportant repos
- **Scores** each repo's health (0-100) based on activity
- **Exports** results as JSON

## ✨ Features

- **🚀 Fast Analysis** - Completes in <10 seconds for most orgs (requirement: <5 minutes ✓)
- **🎯 Smart Selection** - Only analyzes important repos (max 30) to save time and API calls
- **📊 GraphQL API** - Fetches all data in 1-5 requests instead of hundreds
- **💾 SQLite Caching** - 1-hour cache reduces API calls
- **📈 Rate Limit Display** - Shows API usage after each run
- **🌐 REST API + CLI** - Use via web or command line
- **🐳 Docker Ready** - Deploy anywhere with one command

## 🛠️ Tech Stack & Architecture

### Why These Choices?

- **Python 3.12 + FastAPI** - Modern async framework for speed and auto-generated API docs
- **GraphQL over REST** - Get 50 repos of data in 1 request vs 50+ REST calls
- **SQLite Cache** - Zero-config database perfect for caching
- **Typer CLI** - Beautiful command-line interface with minimal code
- **Docker + Railway** - One-click deployment with automatic HTTPS

### Strategic Design Decisions

1. **Rate Limit Strategy**
   - GraphQL batching: 50 repos per request
   - SQLite caching: Avoid repeated API calls
   - Rate limit tracking: Display usage after each run
   - _Result:_ Can analyze 1000+ orgs per hour with one token

## Installation (Optional)

### Quick Start

```bash
# Clone and setup
git clone https://github.com/ahmedkhaleel2004/repo-analyzer.git
cd repo-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Add your GitHub token (for better rate limits)
cp .env.example .env
# Edit .env and add your token - it loads automatically!
```

### Run It

```bash
# Analyze an organization (no need to export variables!)
repo-analyzer vercel

# Skip cache for fresh data
repo-analyzer vercel --no-cache

# Clear cache before running
repo-analyzer vercel --clear-cache

# Results saved to: results/vercel.json
```

## API Usage

### REST Endpoints

```bash
# Check health
GET https://repo-analyzer-production-247d.up.railway.app/

# Analyze organization
GET https://repo-analyzer-production-247d.up.railway.app/analyze/{org}

# Get previous results
GET https://repo-analyzer-production-247d.up.railway.app/results/{org}
```

### Example Response

```json
{
  "organization": "vercel",
  "repository_scores": {
    "next.js": 100,
    "turborepo": 95,
    "swr": 90
  },
  "total_repos_analyzed": 12,
  "average_score": 85.3
}
```

## Rate Limits & Caching

- **With GitHub token**: 5,000 requests/hour
- **Without token**: 60 requests/hour
- **Cache**: Results cached for 1 hour (use `--no-cache` to skip)
- **API usage**: Shows rate limit info after each run
- **Token support**: Uses `GITHUB_TOKEN` or `GITHUB_PAT` environment variables

Example output:

```
📊 API Rate Limit: 64 used, 4936/5000 remaining, resets in 32m
```

## Testing & Validation

Successfully tested with:

- ✅ **SocketDev** (required): 43 repos → 21 analyzed in 5 seconds
- ✅ **Vercel**: 176 repos → 12 analyzed in 8 seconds

## Popular Organizations to Try

```bash
# Web frameworks
repo-analyzer vercel      # Next.js, SWR
repo-analyzer vuejs       # Vue.js ecosystem
repo-analyzer sveltejs    # Svelte framework

# Developer tools
repo-analyzer microsoft   # VS Code, TypeScript
repo-analyzer docker      # Container tools
repo-analyzer hashicorp   # Terraform, Vault

# Large organizations
repo-analyzer google      # 2000+ repos
repo-analyzer apache      # Open source projects
```

## Deploy Your Own

### Using Railway (Easiest)

1. Fork this repo
2. Connect to [Railway](https://railway.app)
3. Add env variable: `GITHUB_PAT=your_token`
4. Deploy!

### Using Docker

```bash
docker build -t repo-analyzer .
docker run -e GITHUB_PAT=your_token -p 8000:8000 repo-analyzer
```

## Development

```bash
# Run full CI pipeline (tests, linting, type checking)
make ci

# Start API locally
uvicorn repo_analyzer.api:app --reload

# Run specific tools
ruff check src/               # Linting
mypy src/                     # Type checking
pytest tests/ -v              # Run tests
```

### Project Structure

- **Modern Python packaging** with `pyproject.toml` (PEP 621)
- **Comprehensive test suite** with async support
- **Type hints** throughout the codebase
- **Auto code formatting** with Ruff
- **SQLite caching** with TTL support
- **GraphQL optimization** for minimal API calls

## Questions?

- **Why only 30 repos?** We analyze the most important ones to save time
- **Why is my score low?** Check if the repo has recent commits, releases, and closed issues
- **Can I analyze private repos?** Yes, with a token that has private repo access

---

Built for the Neo take-home assignment | [GitHub](https://github.com/ahmedkhaleel2004/repo-analyzer)
