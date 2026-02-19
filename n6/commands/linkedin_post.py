"""
`n6 linkedin-post` — write a LinkedIn post from a prompt, opinion, or idea.

Examples:
  n6 linkedin-post "My take on why most teams shouldn't use microservices"
  n6 linkedin-post "Highlight this project" < README.md
  cat README.md | n6 linkedin-post "Highlight this project"

The prompt is the core idea. Any piped content is appended as supporting material.
Uses the Claude CLI backend with the Sonnet model.
System prompt is loaded from .claude/skills/linkedin-write/SKILL.md.
"""

import sys
from pathlib import Path
from typing import Annotated
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


def linkedin_post(
    prompt: Annotated[
        str, typer.Argument(help="The idea, opinion, or topic to write a LinkedIn post about")
    ],
) -> None:
    """Write a LinkedIn post from a prompt, opinion, or idea."""
    user_message = prompt

    if not sys.stdin.isatty():
        piped = sys.stdin.read().strip()
        if piped:
            user_message = f"{prompt}\n\n{piped}"

    try:
        system = _load_skill()
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    try:
        for chunk in claude.stream(user_message, system=system, model="claude-sonnet-4-6"):
            print(chunk, end="", flush=True)
        print()
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
