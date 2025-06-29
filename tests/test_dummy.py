from repo_analyzer.engine import analyze_org
import asyncio


def test_stub():
    assert asyncio.run(analyze_org("octocat")) is None
