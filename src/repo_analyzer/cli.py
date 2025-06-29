"""CLI interface for the repo analyzer."""

import asyncio
import typer

from .engine import analyze_org

app = typer.Typer()


@app.command()
def main(
    org: str,
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable cache"),
    clear_cache: bool = typer.Option(
        False, "--clear-cache", help="Clear cache before running"
    ),
):
    """Analyze a GitHub organisation and dump JSON."""
    asyncio.run(analyze_org(org, use_cache=not no_cache, clear_cache=clear_cache))


if __name__ == "__main__":
    app()
