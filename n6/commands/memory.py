"""n6 m — store memories (fact, note, article, meeting, social)."""

import sys
from typing import Optional

import typer
from rich.console import Console

from n6.config import get_config
from n6.memory import get_memory_client

app = typer.Typer(name="m", help="Store a memory (fact, note, article, meeting, social).")
err = Console(stderr=True)

_CONTEXT_OPTION = typer.Option(
    "global",
    "--context",
    "-c",
    help="Memory context (e.g. upsun, writing, personal). Default: global.",
)


@app.command()
def fact(
    text: str = typer.Argument(..., help="Short fact or preference to remember."),
    context: str = _CONTEXT_OPTION,
):
    """Store a short fact or preference."""
    cfg = get_config()
    client = get_memory_client()
    client.add(
        [{"role": "user", "content": text}],
        user_id=cfg.mem0_user_id,
        metadata={"type": "fact", "context": context},
    )
    err.print(f"[green]✓[/green] Fact stored. [dim](context: {context})[/dim]")


@app.command()
def note(
    text: str = typer.Argument(..., help="Free-form note to remember."),
    context: str = _CONTEXT_OPTION,
):
    """Store a free-form note."""
    cfg = get_config()
    client = get_memory_client()
    client.add(
        [{"role": "user", "content": text}],
        user_id=cfg.mem0_user_id,
        metadata={"type": "note", "context": context},
    )
    err.print(f"[green]✓[/green] Note stored. [dim](context: {context})[/dim]")


@app.command()
def article(
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Article title."),
    context: str = _CONTEXT_OPTION,
):
    """Store an article (read from stdin). Extracts key facts AND stores verbatim."""
    if sys.stdin.isatty():
        err.print(
            "[red]Error:[/red] No input detected. Pipe an article: cat article.md | n6 m article"
        )
        raise typer.Exit(1)

    text = sys.stdin.read().strip()
    if not text:
        err.print("[red]Error:[/red] Empty input.")
        raise typer.Exit(1)

    cfg = get_config()
    client = get_memory_client()
    base_metadata = {"type": "article", "context": context}
    if title:
        base_metadata["title"] = title

    # Pass 1: extract key facts and insights
    result = client.add(
        [{"role": "user", "content": text}],
        user_id=cfg.mem0_user_id,
        metadata={**base_metadata, "storage": "facts"},
        infer=True,
    )
    facts_count = len(result.get("results", [])) if isinstance(result, dict) else 0

    # Pass 2: store verbatim
    client.add(
        [{"role": "user", "content": text}],
        user_id=cfg.mem0_user_id,
        metadata={**base_metadata, "storage": "verbatim"},
        infer=False,
    )

    label = f'"{title}"' if title else "article"
    err.print(
        f"[green]✓[/green] {label} stored — "
        f"{facts_count} facts extracted + verbatim. [dim](context: {context})[/dim]"
    )


@app.command()
def meeting(
    context: str = _CONTEXT_OPTION,
):
    """Store a meeting transcript (read from stdin)."""
    if sys.stdin.isatty():
        err.print(
            "[red]Error:[/red] No input detected. Pipe a transcript: cat meeting.txt | n6 m meeting"
        )
        raise typer.Exit(1)

    transcript = sys.stdin.read().strip()
    if not transcript:
        err.print("[red]Error:[/red] Empty input.")
        raise typer.Exit(1)

    cfg = get_config()
    client = get_memory_client()
    result = client.add(
        [{"role": "user", "content": transcript}],
        user_id=cfg.mem0_user_id,
        metadata={"type": "meeting", "context": context},
    )

    count = len(result.get("results", [])) if isinstance(result, dict) else 0
    err.print(
        f"[green]✓[/green] Meeting stored ({count} memories extracted). "
        f"[dim](context: {context})[/dim]"
    )


@app.command()
def social(
    text: Optional[str] = typer.Argument(None, help="Post text. Omit to read from stdin."),
    platform: Optional[str] = typer.Option(
        None, "--platform", "-p", help="Platform (linkedin, bluesky, twitter, …)."
    ),
    context: str = _CONTEXT_OPTION,
):
    """Store a social media post (argument or stdin)."""
    if text is None:
        if sys.stdin.isatty():
            err.print(
                "[red]Error:[/red] Provide text as argument or pipe it: cat post.txt | n6 m social"
            )
            raise typer.Exit(1)
        text = sys.stdin.read().strip()

    if not text:
        err.print("[red]Error:[/red] Empty input.")
        raise typer.Exit(1)

    cfg = get_config()
    client = get_memory_client()
    metadata: dict = {"type": "social", "context": context}
    if platform:
        metadata["platform"] = platform

    client.add(
        [{"role": "user", "content": text}],
        user_id=cfg.mem0_user_id,
        metadata=metadata,
    )

    label = (
        f"[dim](platform: {platform}, context: {context})[/dim]"
        if platform
        else f"[dim](context: {context})[/dim]"
    )
    err.print(f"[green]✓[/green] Social post stored. {label}")
