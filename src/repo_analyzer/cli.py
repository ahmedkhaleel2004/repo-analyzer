import typer
import asyncio
from .engine import analyze_org

app = typer.Typer()

@app.command()
def main(org: str):
    """Analyze a GitHub organisation and dump JSON."""
    asyncio.run(analyze_org(org))

if __name__ == "__main__":
    app()
