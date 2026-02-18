"""
`n6 ask` — send a one-shot prompt to an LLM and print the response.

Backend is selected with --backend (claude | glm). Streams by default.

Required env vars:
  ANTHROPIC_API_KEY  (for --backend claude)
  ZAI_API_KEY        (for --backend glm)
"""

from typing import Annotated
import typer
from rich.console import Console
from n6.llm import claude, glm

console = Console()

Backend = typer.Argument


def ask(
    prompt: Annotated[str, typer.Argument(help="The prompt to send")],
    backend: Annotated[str, typer.Option("--backend", "-b", help="claude | glm")] = "claude",
    system: Annotated[str, typer.Option("--system", "-s", help="System prompt")] = "",
    model: Annotated[str, typer.Option("--model", "-m", help="Override model name")] = "",
    no_stream: Annotated[bool, typer.Option("--no-stream", help="Disable streaming")] = False,
) -> None:
    """Send a prompt to Claude or GLM-5 and print the response."""
    try:
        if no_stream:
            if backend == "glm":
                result = glm.ask(prompt, system=system, model=model)
            else:
                result = claude.ask(prompt, system=system, model=model)
            console.print(result)
        else:
            stream_fn = glm.stream if backend == "glm" else claude.stream
            for chunk in stream_fn(prompt, system=system, model=model):
                console.print(chunk, end="")
            console.print()  # newline at end
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
