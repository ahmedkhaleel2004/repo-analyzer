from repo_analyzer.engine import analyze_org
import asyncio


def test_stub():
    result = asyncio.run(analyze_org("octocat"))
    assert isinstance(result, dict)
    assert result == {}  # Empty since fetcher returns empty list for now
