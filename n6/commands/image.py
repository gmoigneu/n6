"""
`n6 image` — generate an image from a piped prompt using Gemini.

Example:
  echo "A cat wearing a top hat" | n6 image cat.png
  echo "A mountain at sunset" | n6 image mountain.png --pro

Authenticates with either GEMINI_API_KEY or Vertex AI (gcloud ADC + GEMINI_PROJECT).
"""

import sys
from pathlib import Path

import typer
from rich.console import Console

from n6.config import get_config

err = Console(stderr=True)

MODEL_FLASH = "gemini-2.5-flash-image"
MODEL_PRO = "gemini-3-pro-image-preview"


def image(
    filename: str = typer.Argument(help="Output filename for the generated image"),
    pro: bool = typer.Option(False, "--pro", help="Use Gemini 3 Pro for higher fidelity"),
) -> None:
    """Generate an image from a piped prompt using Gemini."""
    if sys.stdin.isatty():
        err.print(
            "[bold red]Error:[/bold red] No input detected. Pipe your prompt into this command."
        )
        err.print("  Example: [dim]echo 'A cat in space' | n6 image cat.png[/dim]")
        raise typer.Exit(1)

    prompt = sys.stdin.read().strip()
    if not prompt:
        err.print("[bold red]Error:[/bold red] Input is empty.")
        raise typer.Exit(1)

    cfg = get_config()
    model_name = MODEL_PRO if pro else MODEL_FLASH

    from google import genai
    from google.genai import types

    # Build client: API key or Vertex AI
    if cfg.gemini_api_key:
        client = genai.Client(api_key=cfg.gemini_api_key)
    elif cfg.gemini_project:
        client = genai.Client(
            vertexai=True, project=cfg.gemini_project, location=cfg.gemini_location
        )
    else:
        err.print("[bold red]Error:[/bold red] No Gemini auth configured.")
        err.print("Set GEMINI_API_KEY or GEMINI_PROJECT (for Vertex AI with gcloud ADC).")
        raise typer.Exit(1)

    err.print(f"[dim]Generating image with {model_name}…[/dim]")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
    except Exception as e:
        err.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    # Extract image data from response
    if not response.candidates or not response.candidates[0].content.parts:
        err.print("[bold red]Error:[/bold red] No image returned by the model.")
        raise typer.Exit(1)

    image_part = None
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            image_part = part
            break

    if not image_part:
        err.print("[bold red]Error:[/bold red] Response contained no image data.")
        raise typer.Exit(1)

    image_bytes = image_part.inline_data.data
    Path(filename).write_bytes(image_bytes)
    err.print(f"[green]Saved to {filename}[/green]")
