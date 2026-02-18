# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Number 6** — a personal AI-powered CLI tool named after Caprica Six from *Battlestar Galactica*. Mix of everyday utilities: some pure code, some LLM-backed. Licensed under Apache V2.

## Stack

- **Language:** Python 3.11+
- **CLI framework:** [Typer](https://typer.tiangolo.com/) + Rich
- **LLM backends:** `claude` CLI subprocess (Claude, uses Claude Code subscription) and `anthropic` SDK pointed at Z.AI's Anthropic-compatible endpoint (GLM via Z.AI coding plan)
- **Build/packaging:** Hatch (`pyproject.toml`)

## Commands

```bash
# Install / sync dependencies (do this once, and after adding new deps)
uv sync

# Install as a global tool (editable — changes are reflected immediately)
uv tool install --editable .

# Run the CLI
uv run n6 --help

# Add a dependency
uv add <package>

# Lint
uv run ruff check n6/
uv run ruff format n6/
```

## Architecture

```
n6/
  main.py                 # Typer app; registers all commands
  config.py               # Config via env vars + ~/.n6.toml (TOML)
  social_tone.md          # Shared tone/style rules for social media commands
  llm/
    claude.py             # Shells out to the `claude` CLI: ask() and stream()
    glm.py                # Anthropic SDK → Z.AI endpoint: ask() and stream()
  commands/
    ask.py                # n6 ask — one-shot prompt, selects backend via --backend
    summarize.py          # n6 summarize — pipe content in, GLM returns ~200-word summary
    linkedin_article.py   # n6 linkedin-article — pipe article in, Claude Sonnet writes LinkedIn post
    yt_transcript.py      # n6 yt-transcript — fetch YouTube transcript, reformat with Claude
```

**Adding a new command:** create `n6/commands/<name>.py` with a function, then register it in `main.py` with `app.command()(<function>)`. Typer converts underscores to hyphens in command names automatically.

**Adding a new LLM backend:** add a module to `n6/llm/` exposing `ask()` and `stream()`, then wire it into whichever command needs it.

**Social media commands** should load `n6/social_tone.md` at runtime and inject it into the system prompt. See `linkedin_article.py` for the pattern.

## LLM Backends

### Claude (`n6/llm/claude.py`)
Shells out to the `claude` CLI. No API key needed — uses the Claude Code subscription. Prompt is passed via **stdin** (not as a CLI argument) to avoid `E2BIG` errors on large inputs.

> **Dev note:** The `claude` CLI cannot be run inside an active Claude Code session (`CLAUDECODE` env var blocks it). Use `env -u CLAUDECODE uv run n6 <command>` to test locally, or test from a regular terminal.

### GLM via Z.AI (`n6/llm/glm.py`)
Uses the `anthropic` SDK pointed at Z.AI's Anthropic-compatible endpoint (`https://api.z.ai/api/anthropic`). Requires the **Z.AI coding plan** — not a standard pay-per-token account. The coding plan endpoint is different from Z.AI's OpenAI-compatible API.

## Configuration

Keys are read from env vars first, then `~/.n6.toml`:

| Env var | Purpose |
|---|---|
| `ZAI_API_KEY` | Required for GLM backend |
| `CLAUDE_DEFAULT_MODEL` | Override model passed to `claude --model` |
| `ZAI_DEFAULT_MODEL` | Override GLM model (default: `glm-4.6`) |
| `ZAI_BASE_URL` | Override Z.AI base URL (default: `https://api.z.ai/api/anthropic`) |

Example `~/.n6.toml`:
```toml
zai_api_key = "..."
```

## Output and piping

Commands that produce content write to **stdout**; status/progress messages write to **stderr**. This keeps output clean for piping:

```bash
n6 yt-transcript <id> > transcript.txt        # status visible, content to file
n6 yt-transcript <id> | n6 summarize          # chain commands
n6 yt-transcript <id> 2>/dev/null             # suppress status messages
```
