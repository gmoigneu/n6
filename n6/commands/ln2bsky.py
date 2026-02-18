"""
`n6 ln2bsky` — convert a LinkedIn post to a Bluesky thread.

Each post in the thread is capped at 300 characters (Bluesky's limit),
numbered as 1/N, 2/N, etc.

Example:
  cat linkedin-post.txt | n6 ln2bsky
  pbpaste | n6 ln2bsky

Uses the Claude CLI backend with the Sonnet model.
"""

import sys
from pathlib import Path
import typer
from rich.console import Console
from n6.llm import claude

console = Console(stderr=True)

CHAR_LIMIT = 300

SYSTEM_PROMPT = f"""You convert LinkedIn posts into Bluesky threads.

Each Bluesky post is capped at {CHAR_LIMIT} characters, including the post number label (e.g. "1/4 "). Count carefully — stay under the limit on every post.

Rules:
- Split at natural thought or sentence boundaries. Never cut mid-sentence.
- Number each post at the start: "1/N ", "2/N ", etc. (note the trailing space). This counts toward the character limit.
- The first post is the hook. It must stand alone and pull the reader in.
- Adapt the tone: Bluesky is more conversational and direct than LinkedIn. Drop the professional polish. Keep the insight.
- No emojis. Plain text.
- No filler transitions like "Thread:" or "Continued...". The numbers do that job.
- Each post should make sense on its own.
- Add 3 to 5 relevant hashtags at the end of the last post, on their own line. Pick hashtags that are specific and actually used (e.g. #softwareengineering, #devops, #opensource). No generic filler like #tech or #innovation. Hashtags count toward the 300-character limit on that post — if they don't fit, put them as a final standalone post.

Output format: each post as its own block, separated by a blank line. Nothing else — no explanation, no meta-commentary, no character counts."""


def ln2bsky() -> None:
    """Convert a piped LinkedIn post into a Bluesky thread (300 chars per post)."""
    if sys.stdin.isatty():
        console.print("[bold red]Error:[/bold red] No input detected. Pipe your LinkedIn post into this command.")
        console.print("  Example: [dim]cat post.txt | n6 ln2bsky[/dim]")
        raise typer.Exit(1)

    post = sys.stdin.read().strip()
    if not post:
        console.print("[bold red]Error:[/bold red] Input is empty.")
        raise typer.Exit(1)

    try:
        for chunk in claude.stream(post, system=SYSTEM_PROMPT, model="claude-sonnet-4-6"):
            print(chunk, end="", flush=True)
        print()
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
