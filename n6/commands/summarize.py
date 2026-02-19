"""
`n6 summarize` — pipe content in, get a ~200-word organized summary out.

Example:
  cat article.txt | n6 summarize
  curl -s https://example.com | n6 summarize

Uses the GLM backend (ZAI_API_KEY required).
"""

import re
import sys
import typer
from rich.console import Console
from n6.llm import glm
from n6.llm.skills import load_humanizer

console = Console()

SYSTEM_PROMPT = (
    "You are a precise summarizer. Given any content, produce a clear, organized summary "
    "of approximately 200 words. Use short paragraphs or bullet points as appropriate for "
    "the content type. Do not include preamble like 'Here is a summary' — just the summary itself."
)


def _strip_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def summarize() -> None:
    """Summarize piped content using GLM."""
    if sys.stdin.isatty():
        console.print("[bold red]Error:[/bold red] No input detected. Pipe content into this command.")
        console.print("  Example: [dim]cat file.txt | n6 summarize[/dim]")
        raise typer.Exit(1)

    content = sys.stdin.read().strip()
    if not content:
        console.print("[bold red]Error:[/bold red] Input is empty.")
        raise typer.Exit(1)

    # Strip HTML if the input looks like a web page
    if "<html" in content[:1000].lower() or "<!doctype" in content[:100].lower():
        content = _strip_html(content)

    system = SYSTEM_PROMPT + "\n\n---\n\n" + load_humanizer()

    try:
        for chunk in glm.stream(content, system=system):
            console.print(chunk, end="")
        console.print()
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
