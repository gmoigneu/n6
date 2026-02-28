"""
`n6 yt-transcript` — fetch a YouTube video transcript and reformat it for readability.

Example:
  n6 yt-transcript https://www.youtube.com/watch?v=dQw4w9WgXcQ
  n6 yt-transcript https://youtu.be/dQw4w9WgXcQ

Uses the OpenAI backend to clean up and reformat the raw transcript.
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
from n6.llm import openai as llm
from n6.llm.skills import load_humanizer

console = Console()
err_console = Console(stderr=True)

SYSTEM_PROMPT = """You are given a raw YouTube transcript — a flat stream of automatically timed caption snippets with no punctuation, no paragraph breaks, and occasional transcription errors.

Your job is to produce a clean, readable document in two parts:

PART 1 — KEY TAKEAWAYS
Write a concise bullet-point summary (5 to 10 bullets) of the most important points. Place this at the very top under the heading "Key Takeaways".

PART 2 — FULL TRANSCRIPT
Reformat the ENTIRE transcript into clean, readable prose. This is a formatting job, not a summarising job.

CRITICAL RULES — failure to follow these means you have failed the task:
- Your output for the transcript must be approximately the same length as the input. If your output is significantly shorter, you have summarised instead of reformatted. Do not do this.
- Keep the speaker's own words and phrasing wherever possible. Do not paraphrase, compress, or rephrase into your own words.
- Every example, analogy, story, anecdote, aside, tangent, and digression must be included in full, exactly as the speaker told it.
- Every rhetorical question, repetition for emphasis, and conversational aside must be kept.
- Group sentences into short paragraphs (3 to 5 sentences) by topic to aid readability.
- Add proper punctuation and capitalisation.
- Fix obvious transcription errors (wrong homophones, missing apostrophes, etc.).
- Remove only pure noise: unintelligible stutters and exact duplicate false starts (e.g. "I I I was" → "I was"). Do not remove filler words that carry the speaker's voice or rhythm.
- Plain text output only. No markdown except for the "Key Takeaways" heading and bullet points."""


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
    """Fetch a YouTube transcript and reformat it into readable prose using OpenAI."""
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

    err_console.print("[dim]Reformatting with OpenAI...[/dim]")
    system = SYSTEM_PROMPT + "\n\n---\n\n" + load_humanizer()

    try:
        for chunk in llm.stream(raw_text, system=system, model="gpt-5"):
            print(chunk, end="", flush=True)
        print()
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
