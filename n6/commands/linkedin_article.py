"""
`n6 linkedin-article` — generate a LinkedIn post from a piped article using Claude Sonnet.

Example:
  cat article.md | n6 linkedin-article
  curl -s https://example.com/post | n6 linkedin-article

Uses the Claude CLI backend with the Sonnet model.
System prompt is loaded from .claude/skills/linkedin-write/SKILL.md.
"""

import sys
from pathlib import Path
import typer
from rich.console import Console
from n6.llm import claude
from n6.llm.skills import load_humanizer

console = Console()

SKILL_FILE = (
    Path(__file__).parent.parent.parent / ".claude" / "skills" / "linkedin-write" / "SKILL.md"
)


def _load_skill() -> str:
    if not SKILL_FILE.exists():
        raise FileNotFoundError(f"Skill file not found: {SKILL_FILE}")
    return SKILL_FILE.read_text() + "\n\n---\n\n" + load_humanizer()


def linkedin_article() -> None:
    """Generate a LinkedIn post from a piped article using Claude Sonnet."""
    if sys.stdin.isatty():
        console.print(
            "[bold red]Error:[/bold red] No input detected. Pipe your article into this command."
        )
        console.print("  Example: [dim]cat article.md | n6 linkedin-article[/dim]")
        raise typer.Exit(1)

    article = sys.stdin.read().strip()
    if not article:
        console.print("[bold red]Error:[/bold red] Input is empty.")
        raise typer.Exit(1)

    try:
        system = _load_skill()
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    try:
        for chunk in claude.stream(article, system=system, model="claude-sonnet-4-6"):
            print(chunk, end="", flush=True)
        print()
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
