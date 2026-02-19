"""
`n6 blog` — generate article.md from content files in the current directory.

Recursively scans the working directory for .md and .txt files, assembles
them as research material, and writes article.md using the blog-write skill.

Example:
  cd ~/research/my-topic/
  n6 blog

Uses the Claude CLI backend with the Sonnet model.
"""

from pathlib import Path
import typer
from rich.console import Console
from n6.llm import claude
from n6.llm.skills import load_humanizer

console = Console(stderr=True)

SKILL_DIR = Path(__file__).parent.parent.parent / ".claude" / "skills" / "blog-write"
SKILL_FILE = SKILL_DIR / "SKILL.md"
STYLE_GUIDE_FILE = SKILL_DIR / "references" / "style-guide.md"

INCLUDE_EXTENSIONS = {".md", ".txt"}
EXCLUDE_DIRS = {".git", ".claude", "__pycache__", "node_modules", ".venv", "venv"}
MAX_FILE_BYTES = 100_000  # 100 KB per file — keeps individual files from dominating


def _load_system() -> str:
    if not SKILL_FILE.exists():
        raise FileNotFoundError(f"Skill file not found: {SKILL_FILE}")
    system = SKILL_FILE.read_text()
    if STYLE_GUIDE_FILE.exists():
        system += "\n\n---\n\n" + STYLE_GUIDE_FILE.read_text()
    system += "\n\n---\n\n" + load_humanizer()
    return system


def _collect_files(cwd: Path, output_file: Path) -> list[Path]:
    files = []
    for path in sorted(cwd.rglob("*")):
        if not path.is_file():
            continue
        if path == output_file:
            continue
        # Skip hidden dirs and known noise directories anywhere in the path
        rel_parts = path.relative_to(cwd).parts
        if any(p.startswith(".") or p in EXCLUDE_DIRS for p in rel_parts[:-1]):
            continue
        if path.suffix.lower() in INCLUDE_EXTENSIONS:
            files.append(path)
    return files


def blog() -> None:
    """Generate article.md by synthesizing content files in the current directory."""
    cwd = Path.cwd()
    output_file = cwd / "article.md"

    try:
        system = _load_system()
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    files = _collect_files(cwd, output_file)
    if not files:
        console.print(f"[yellow]No .md or .txt files found in {cwd}[/yellow]")
        raise typer.Exit(1)

    console.print(f"Found {len(files)} file(s):")
    sections = []
    for path in files:
        rel = path.relative_to(cwd)
        try:
            raw = path.read_bytes()
        except OSError as e:
            console.print(f"  [yellow]Skipping {rel}: {e}[/yellow]")
            continue

        if len(raw) > MAX_FILE_BYTES:
            content = raw[:MAX_FILE_BYTES].decode(errors="replace").strip()
            console.print(f"  [dim]{rel} (truncated to 100KB)[/dim]")
        else:
            content = raw.decode(errors="replace").strip()
            console.print(f"  [dim]{rel}[/dim]")

        if content:
            sections.append(f"### {rel}\n\n{content}")

    if not sections:
        console.print("[yellow]All files were empty or unreadable.[/yellow]")
        raise typer.Exit(1)

    assembled = "\n\n---\n\n".join(sections)
    user_message = (
        "Write a blog article based on the following research material. "
        "Synthesize it into a single cohesive article — not a summary of each file, "
        "but one unified piece with a clear argument or narrative.\n\n" + assembled
    )

    console.print("\nGenerating article...")
    try:
        result = claude.ask(user_message, system=system, model="claude-sonnet-4-6")
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    output_file.write_text(result)
    console.print(f"\n[green]Written:[/green] {output_file}")
