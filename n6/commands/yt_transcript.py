"""
`n6 yt-transcript` — fetch a YouTube video transcript and reformat it for readability.

Example:
  n6 yt-transcript https://www.youtube.com/watch?v=dQw4w9WgXcQ
  n6 yt-transcript https://youtu.be/dQw4w9WgXcQ

Uses the Claude CLI backend to clean up and reformat the raw transcript.
"""

from typing import Annotated
from urllib.parse import urlparse, parse_qs
import typer
from rich.console import Console
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    VideoUnavailable,
    NoTranscriptFound,
)
from n6.llm import claude
from n6.llm.skills import load_humanizer

console = Console()
err_console = Console(stderr=True)

SYSTEM_PROMPT = """You are given a raw YouTube transcript — a flat stream of automatically timed caption snippets with no punctuation, no paragraph breaks, and occasional transcription errors.

Your job is to reformat it into clean, readable prose:
- Group related sentences into short paragraphs (3 to 5 sentences each).
- Add proper punctuation and capitalisation.
- Fix obvious transcription errors (wrong homophones, missing apostrophes, etc.).
- Remove filler words (um, uh, you know, like) and false starts.
- Do not summarize. Do not remove content. Preserve the full meaning and all details.
- Plain text output only. No markdown."""


def _extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    if parsed.netloc in ("youtu.be",):
        return parsed.path.lstrip("/")

    if parsed.path == "/watch":
        params = parse_qs(parsed.query)
        if "v" in params:
            return params["v"][0]

    if parsed.path.startswith(("/embed/", "/v/")):
        return parsed.path.split("/")[2]

    # Treat bare input as a video ID
    if url.isalnum() or (len(url) == 11 and "-" in url or "_" in url):
        return url

    raise ValueError(f"Cannot extract video ID from: {url}")


def yt_transcript(
    url: Annotated[str, typer.Argument(help="YouTube video URL or video ID")],
    lang: Annotated[
        str, typer.Option("--lang", "-l", help="Preferred language code (default: en)")
    ] = "en",
    raw: Annotated[
        bool, typer.Option("--raw", help="Print raw transcript without reformatting")
    ] = False,
) -> None:
    """Fetch a YouTube transcript and reformat it into readable prose using Claude."""
    try:
        video_id = _extract_video_id(url)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    err_console.print(f"[dim]Fetching transcript for video ID: {video_id}...[/dim]")

    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=[lang, f"{lang}-US", f"{lang}-GB"])
    except VideoUnavailable:
        console.print("[bold red]Error:[/bold red] Video is unavailable or private.")
        raise typer.Exit(1)
    except TranscriptsDisabled:
        console.print("[bold red]Error:[/bold red] Transcripts are disabled for this video.")
        raise typer.Exit(1)
    except NoTranscriptFound:
        console.print(f"[bold red]Error:[/bold red] No transcript found for language '{lang}'.")
        err_console.print("[dim]Tip: try --lang with a different language code.[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    raw_text = " ".join(snippet.text for snippet in transcript)

    if raw:
        print(raw_text)
        return

    err_console.print("[dim]Reformatting with Claude...[/dim]")
    system = SYSTEM_PROMPT + "\n\n---\n\n" + load_humanizer()

    try:
        for chunk in claude.stream(raw_text, system=system):
            print(chunk, end="", flush=True)
        print()
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
