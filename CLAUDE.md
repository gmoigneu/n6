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
  memory.py               # mem0 client factory (singleton); OpenAI LLM + embeddings + Qdrant
  llm/
    claude.py             # Shells out to the `claude` CLI: ask() and stream()
    glm.py                # Anthropic SDK → Z.AI endpoint: ask() and stream()
  commands/
    ask.py                # n6 ask — one-shot prompt, selects backend via --backend
    summarize.py          # n6 summarize — pipe content in, GLM returns ~200-word summary
    yt_transcript.py      # n6 yt-transcript — fetch YouTube transcript, reformat with Claude
    blog.py               # n6 blog — scan cwd for .md/.txt files, write article.md
    linkedin_article.py   # n6 linkedin-article — pipe article in, Claude writes LinkedIn post
    linkedin_post.py      # n6 linkedin-post — prompt + optional piped content → LinkedIn post
    ln2bsky.py            # n6 ln2bsky — pipe LinkedIn post in, get Bluesky thread out
    tidy.py               # n6 tidy — organize loose files in cwd into subfolders via Claude
    image.py              # n6 image — pipe prompt in, generate image via Gemini
    memory.py             # n6 m — store memories: fact, note, article, meeting, social (--context)
    search.py             # n6 s — semantic search with LLM-synthesised markdown output (--context)

.claude/skills/
  blog-write/
    SKILL.md              # Voice + style rules for blog/article writing
    references/
      style-guide.md      # Detailed style patterns (inlined at runtime by blog.py)
  linkedin-write/
    SKILL.md              # Voice + LinkedIn formatting rules (loaded as system prompt)
```

**Adding a new command:** create `n6/commands/<name>.py` with a function, then register it in `main.py` with `app.command()(<function>)`. Typer converts underscores to hyphens in command names automatically.

**Adding a new LLM backend:** add a module to `n6/llm/` exposing `ask()` and `stream()`, then wire it into whichever command needs it.

**Skills as system prompts:** commands that need rich writing instructions load their system prompt from `.claude/skills/<name>/SKILL.md` at runtime. This keeps prompts editable without touching Python code, and makes the same rules available to Claude Code when the skill is invoked interactively. See `linkedin_article.py` for the pattern.

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
| `GEMINI_API_KEY` | API key for Gemini (image command) |
| `GEMINI_PROJECT` | GCP project for Vertex AI auth (falls back to `GOOGLE_CLOUD_PROJECT`) |
| `GEMINI_LOCATION` | Vertex AI location (falls back to `GOOGLE_CLOUD_LOCATION`, default: `us-central1`) |
| `OPENAI_API_KEY` | Required for mem0 LLM (`gpt-4o-mini`) and embeddings (`text-embedding-3-small`) |
| `QDRANT_HOST` | Qdrant host for memory storage (default: `localhost`) |
| `QDRANT_PORT` | Qdrant port (default: `6333`) |
| `MEM0_USER_ID` | mem0 user ID for memory isolation (default: `default`) |

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
