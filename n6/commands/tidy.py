"""
`n6 tidy` — organize loose files in the current directory into subfolders using Claude.

Scans the CWD for loose files (skipping dotfiles), asks Claude Opus to
categorize them, then moves each file into a target subfolder. Files that
look like junk go to "To delete". Nothing is ever deleted.

Example:
  n6 tidy              # interactive — shows plan, asks before moving
  n6 tidy --dry-run    # preview only
  n6 tidy --yes        # skip confirmation
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from n6.llm import claude

err = Console(stderr=True)

SYSTEM_PROMPT = """\
You are a file organizer. Given a list of loose files and existing subdirectories
in a directory, decide where each file should go.

Return a JSON array of objects: [{"file": "<name>", "target": "<folder>"}]

Rules:
- "target" is a short lowercase folder name (e.g. "documents", "images", "scripts").
- Use "." to leave a file in place (config files, READMEs, etc.).
- Use "To delete" for junk, temp files, thumbs.db, .DS_Store-like detritus, etc.
- Reuse existing subdirectory names when they fit.
- Folder names must be single depth — no slashes, no nesting.
- Every file from the input list must appear exactly once in the output.
- Do not invent files that aren't in the input.
- Return ONLY the JSON array. No markdown fences, no commentary.
"""


def _scan_cwd() -> tuple[list[str], list[str]]:
    """Return (loose_files, existing_subdirs) in CWD, skipping dotfiles/dotdirs."""
    cwd = Path.cwd()
    files: list[str] = []
    dirs: list[str] = []
    for entry in sorted(cwd.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            dirs.append(entry.name)
        elif entry.is_file():
            files.append(entry.name)
    return files, dirs


def _build_prompt(files: list[str], dirs: list[str]) -> str:
    prompt = "Loose files:\n"
    for f in files:
        prompt += f"- {f}\n"
    if dirs:
        prompt += "\nExisting subdirectories:\n"
        for d in dirs:
            prompt += f"- {d}/\n"
    return prompt


def _parse_response(raw: str, files: list[str]) -> list[dict[str, str]]:
    """Parse and validate the JSON response from Claude."""
    # Strip markdown fences if present
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    plan = json.loads(text)

    if not isinstance(plan, list):
        raise ValueError("Response is not a JSON array")

    file_set = set(files)
    seen: set[str] = set()

    for item in plan:
        if not isinstance(item, dict) or "file" not in item or "target" not in item:
            raise ValueError(f"Invalid item: {item}")
        name = item["file"]
        target = item["target"]

        if name in seen:
            raise ValueError(f"Duplicate file in response: {name}")
        seen.add(name)

        if name not in file_set:
            raise ValueError(f"Unknown file in response: {name}")

        if target != "." and target != "To delete":
            if "/" in target or "\\" in target:
                raise ValueError(f"Nested path not allowed: {target}")

    missing = file_set - seen
    if missing:
        raise ValueError(f"Files missing from response: {', '.join(sorted(missing))}")

    return plan


def _safe_destination(cwd: Path, target: str, filename: str) -> Path:
    """Resolve destination path, ensuring it stays within CWD. Auto-renames on collision."""
    dest_dir = (cwd / target).resolve()
    if not str(dest_dir).startswith(str(cwd.resolve())):
        raise ValueError(f"Target escapes CWD: {target}")

    dest = dest_dir / filename
    if not dest.exists():
        return dest

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem}({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _display_plan(plan: list[dict[str, str]]) -> int:
    """Show a Rich table grouped by target folder. Returns count of files to move."""
    groups: dict[str, list[str]] = {}
    for item in plan:
        groups.setdefault(item["target"], []).append(item["file"])

    table = Table(title="Tidy plan", show_lines=False)
    table.add_column("Folder", style="bold")
    table.add_column("Files")

    move_count = 0
    staying = 0

    for target in sorted(groups.keys()):
        files = sorted(groups[target])
        if target == ".":
            staying = len(files)
            continue
        style = "red" if target == "To delete" else ""
        table.add_row(
            f"[{style}]{target}[/{style}]" if style else target,
            ", ".join(f"[{style}]{f}[/{style}]" if style else f for f in files),
        )
        move_count += len(files)

    err.print(table)
    err.print(f"\n{move_count} file(s) to move, {staying} staying in place.")
    return move_count


def _execute_plan(plan: list[dict[str, str]]) -> None:
    """Create folders and move files."""
    cwd = Path.cwd()
    for item in plan:
        target = item["target"]
        if target == ".":
            continue
        filename = item["file"]
        src = cwd / filename
        dest_dir = cwd / target
        dest_dir.mkdir(exist_ok=True)
        dest = _safe_destination(cwd, target, filename)
        shutil.move(str(src), str(dest))
        err.print(f"  [dim]{filename}[/dim] → [bold]{dest.relative_to(cwd)}[/bold]")


def tidy(
    dry_run: Annotated[
        bool, typer.Option("--dry-run", "-n", help="Show plan without executing")
    ] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation prompt")] = False,
) -> None:
    """Organize loose files in the current directory into subfolders using Claude."""
    files, dirs = _scan_cwd()

    if not files:
        err.print("[yellow]No loose files found in the current directory.[/yellow]")
        raise typer.Exit(0)

    err.print(f"[dim]Found {len(files)} file(s) to categorize…[/dim]")

    prompt = _build_prompt(files, dirs)

    try:
        raw = claude.ask(prompt, system=SYSTEM_PROMPT, model="claude-opus-4-6")
    except RuntimeError as e:
        err.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    try:
        plan = _parse_response(raw, files)
    except (json.JSONDecodeError, ValueError) as e:
        err.print(f"[bold red]Error parsing LLM response:[/bold red] {e}")
        err.print(f"[dim]Raw response:[/dim]\n{raw}")
        raise typer.Exit(1)

    move_count = _display_plan(plan)

    if move_count == 0:
        err.print("[green]Nothing to move.[/green]")
        raise typer.Exit(0)

    if dry_run:
        raise typer.Exit(0)

    if not yes:
        confirm = typer.confirm("Proceed?")
        if not confirm:
            err.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    _execute_plan(plan)
    err.print("[green]Done.[/green]")
