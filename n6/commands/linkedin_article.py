"""
`n6 linkedin-article` — generate a LinkedIn post from a piped article using Claude Sonnet.

Example:
  cat article.md | n6 linkedin-article
  curl -s https://example.com/post | n6 linkedin-article

Uses the Claude CLI backend with the Sonnet model.
"""

import sys
from pathlib import Path
import typer
from rich.console import Console
from n6.llm import claude

console = Console()

TONE_FILE = Path(__file__).parent.parent / "social_tone.md"

SYSTEM_PROMPT_TEMPLATE = """You write LinkedIn posts for software engineers and technical leaders.

Given an article, write a LinkedIn post that promotes it to a professional audience.

Length and structure:
- Total length: 1,300 to 1,600 characters (including spaces). This is the proven sweet spot for thought leadership engagement on LinkedIn.
- The first 140 characters are the hook — they appear in the feed before the "See More" cutoff. Make them count. No "I wrote an article..." opener.
- 3 to 5 short paragraphs. One idea per paragraph.
- End with a natural call to action — invite readers to check the article or share their take.
- Plain text only. No bullet points, no headers, no bold or italic markers.

Content:
- Lead with the core insight or argument of the article, not just its topic.
- Be specific. Concrete details are more compelling than general claims.
- Write in first person.

Tone and style rules:
{tone}"""


def _load_tone() -> str:
    if not TONE_FILE.exists():
        return ""
    return TONE_FILE.read_text()


def linkedin_article() -> None:
    """Generate a LinkedIn post from a piped article using Claude Sonnet."""
    if sys.stdin.isatty():
        console.print("[bold red]Error:[/bold red] No input detected. Pipe your article into this command.")
        console.print("  Example: [dim]cat article.md | n6 linkedin-article[/dim]")
        raise typer.Exit(1)

    article = sys.stdin.read().strip()
    if not article:
        console.print("[bold red]Error:[/bold red] Input is empty.")
        raise typer.Exit(1)

    system = SYSTEM_PROMPT_TEMPLATE.format(tone=_load_tone())

    try:
        for chunk in claude.stream(article, system=system, model="claude-sonnet-4-6"):
            print(chunk, end="", flush=True)
        print()
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
