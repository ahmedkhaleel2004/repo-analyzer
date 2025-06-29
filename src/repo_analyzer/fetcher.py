"""GitHub API fetcher with rate limiting and GraphQL support."""

import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from .cache import Cache

# Try to load .env file if it exists
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value.strip()


class GitHubFetcher:
    """Handles GitHub API calls with rate limiting."""

    def __init__(self, token: str | None = None, use_cache: bool = True):
        self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
        if not self.token:
            print(
                "Warning: No GitHub token found. API rate limits will be very restrictive."
            )

        self.headers = {
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "Accept": "application/vnd.github.v3+json",
        }
        self.graphql_url = "https://api.github.com/graphql"
        self.rest_url = "https://api.github.com"
        self.cache = Cache() if use_cache else None
        self.rate_limit_info: dict[str, int] = {}

    def _update_rate_limit_info(self, headers: dict) -> None:
        """Extract and store rate limit information from response headers."""
        # Try both REST and GraphQL rate limit headers
        if "x-ratelimit-limit" in headers or "X-RateLimit-Limit" in headers:
            # Headers might be lowercase
            limit_key = (
                "x-ratelimit-limit"
                if "x-ratelimit-limit" in headers
                else "X-RateLimit-Limit"
            )
            remaining_key = (
                "x-ratelimit-remaining"
                if "x-ratelimit-remaining" in headers
                else "X-RateLimit-Remaining"
            )
            used_key = (
                "x-ratelimit-used"
                if "x-ratelimit-used" in headers
                else "X-RateLimit-Used"
            )
            reset_key = (
                "x-ratelimit-reset"
                if "x-ratelimit-reset" in headers
                else "X-RateLimit-Reset"
            )

            self.rate_limit_info = {
                "limit": int(headers.get(limit_key, 0)),
                "remaining": int(headers.get(remaining_key, 0)),
                "used": int(headers.get(used_key, 0)),
                "reset": int(headers.get(reset_key, 0)),
            }

    def get_rate_limit_status(self) -> str | None:
        """Get formatted rate limit status."""
        if not self.rate_limit_info:
            return None

        reset_time = datetime.fromtimestamp(self.rate_limit_info["reset"], tz=UTC)
        now = datetime.now(UTC)
        time_until_reset = reset_time - now

        # Format time until reset
        minutes = int(time_until_reset.total_seconds() / 60)
        hours = minutes // 60
        minutes = minutes % 60

        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        return (
            f"📊 API Rate Limit: {self.rate_limit_info['used']} used, "
            f"{self.rate_limit_info['remaining']}/{self.rate_limit_info['limit']} remaining, "
            f"resets in {time_str}"
        )

    async def fetch_org_repos(self, org: str) -> list[dict[str, Any]]:
        """Fetch all repositories for an organization using GraphQL."""
        # Check cache first
        if self.cache:
            cached_data = await self.cache.get("org_repos", org)
            if cached_data:
                print(f"📦 Using cached data for {org} (expires in 1 hour)")
                return list(cached_data)

        query = """
        query($org: String!, $cursor: String) {
            organization(login: $org) {
                repositories(first: 50, after: $cursor, orderBy: {field: STARGAZERS, direction: DESC}) {
                    nodes {
                        name
                        nameWithOwner
                        description
                        url
                        isArchived
                        isFork
                        isEmpty
                        isPrivate
                        stargazerCount
                        forkCount
                        createdAt
                        updatedAt
                        pushedAt

                        # For commit frequency
                        defaultBranchRef {
                            target {
                                ... on Commit {
                                    history(first: 1) {
                                        totalCount
                                    }
                                }
                            }
                        }

                        # For issues/PR metrics
                        issues(states: CLOSED, first: 1) {
                            totalCount
                        }
                        pullRequests(states: CLOSED, first: 1) {
                            totalCount
                        }

                        # For release info
                        releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
                            nodes {
                                createdAt
                            }
                        }

                        # For language info
                        primaryLanguage {
                            name
                        }

                        # For topics
                        repositoryTopics(first: 10) {
                            nodes {
                                topic {
                                    name
                                }
                            }
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    totalCount
                }
            }
        }
        """

        all_repos = []
        cursor = None
        api_calls = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                variables = {"org": org, "cursor": cursor}

                try:
                    response = await client.post(
                        self.graphql_url,
                        json={"query": query, "variables": variables},
                        headers=self.headers,
                    )
                    response.raise_for_status()
                    api_calls += 1

                    # Update rate limit info
                    self._update_rate_limit_info(dict(response.headers))

                    # Check rate limits
                    if "X-RateLimit-Remaining" in response.headers:
                        remaining = int(response.headers["X-RateLimit-Remaining"])
                        if remaining < 10:
                            reset_time = int(response.headers["X-RateLimit-Reset"])
                            sleep_time = (
                                reset_time - int(datetime.now().timestamp()) + 1
                            )
                            if sleep_time > 0:
                                print(
                                    f"Rate limit low ({remaining} remaining). Sleeping for {sleep_time}s..."
                                )
                                await asyncio.sleep(sleep_time)

                    data = response.json()

                    if "errors" in data:
                        print(f"GraphQL errors: {data['errors']}")
                        raise Exception(f"GraphQL query failed: {data['errors']}")

                    org_data = data.get("data", {}).get("organization")
                    if not org_data:
                        raise Exception(f"Organization '{org}' not found")

                    repos = org_data["repositories"]["nodes"]
                    all_repos.extend(repos)

                    page_info = org_data["repositories"]["pageInfo"]
                    if not page_info["hasNextPage"]:
                        break

                    cursor = page_info["endCursor"]

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 401:
                        raise Exception(
                            "Invalid GitHub token. Please check your GITHUB_TOKEN."
                        ) from None
                    elif e.response.status_code == 404:
                        raise Exception(f"Organization '{org}' not found") from None
                    else:
                        if e.response.status_code == 502:
                            raise Exception(
                                "GitHub servers are temporarily unavailable (502). Try again in a few moments or try a smaller organization."
                            ) from None
                        raise Exception(
                            f"GitHub API error: {e.response.status_code} - {e.response.text}"
                        ) from None

        print(
            f"Fetched {len(all_repos)} repositories from {org} (used {api_calls} API calls)"
        )

        # Cache the results
        if self.cache:
            await self.cache.set("org_repos", org, all_repos)

        return all_repos

    async def fetch_additional_metrics(self, repo_name: str) -> dict[str, Any]:
        """Fetch additional metrics that aren't available in GraphQL."""
        # This could fetch commit activity, contributor stats, etc.
        # For now, returning empty dict as these would require many REST calls
        return {}
