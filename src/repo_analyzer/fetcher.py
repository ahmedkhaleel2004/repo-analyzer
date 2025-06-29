"""GitHub API fetcher with rate limiting and GraphQL support."""

import httpx
from typing import Any, Dict, List
import os
from datetime import datetime
import asyncio


class GitHubFetcher:
    """Handles GitHub API calls with rate limiting."""

    def __init__(self, token: str | None = None):
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

    async def fetch_org_repos(self, org: str) -> List[Dict[str, Any]]:
        """Fetch all repositories for an organization using GraphQL."""
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
                        )
                    elif e.response.status_code == 404:
                        raise Exception(f"Organization '{org}' not found")
                    else:
                        raise Exception(
                            f"GitHub API error: {e.response.status_code} - {e.response.text}"
                        )

        print(f"Fetched {len(all_repos)} repositories from {org}")
        return all_repos

    async def fetch_additional_metrics(self, repo_name: str) -> Dict[str, Any]:
        """Fetch additional metrics that aren't available in GraphQL."""
        # This could fetch commit activity, contributor stats, etc.
        # For now, returning empty dict as these would require many REST calls
        return {}
