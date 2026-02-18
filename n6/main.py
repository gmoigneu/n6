"""Number 6 — CLI entry point."""

import typer
from n6.commands.ask import ask
from n6.commands.summarize import summarize
from n6.commands.linkedin_article import linkedin_article
from n6.commands.linkedin_post import linkedin_post
from n6.commands.ln2bsky import ln2bsky
from n6.commands.blog import blog
from n6.commands.yt_transcript import yt_transcript
from n6.commands.tidy import tidy
from n6.commands.image import image

app = typer.Typer(
    name="n6",
    help="Number 6 — your personal AI assistant.",
    no_args_is_help=True,
)

app.command()(ask)
app.command()(summarize)
app.command()(linkedin_article)
app.command()(linkedin_post)
app.command()(ln2bsky)
app.command()(blog)
app.command()(yt_transcript)
app.command()(tidy)
app.command()(image)

if __name__ == "__main__":
    app()
