"""Number 6 — CLI entry point."""

import typer
from n6.commands.ask import ask
from n6.commands.summarize import summarize
from n6.commands.linkedin_article import linkedin_article
from n6.commands.yt_transcript import yt_transcript

app = typer.Typer(
    name="n6",
    help="Number 6 — your personal AI assistant.",
    no_args_is_help=True,
)

app.command()(ask)
app.command()(summarize)
app.command()(linkedin_article)
app.command()(yt_transcript)

if __name__ == "__main__":
    app()
