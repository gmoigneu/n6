# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Number 6** — a personal AI-powered CLI tool named after Caprica Six from *Battlestar Galactica*. It is a mix of everyday utilities: some are pure code, others call an LLM. Licensed under Apache V2.

## Architecture Intent

- Each command/subcommand should be self-contained and independently runnable.
- LLM-backed commands should be clearly separated from pure-code utilities so the tool remains usable offline for the latter.
- Configuration (API keys, user preferences) should live in a single config file, not scattered across commands.

## Tech Stack

Not yet decided — update this section when the stack is chosen. Likely candidates: Python (Typer/Click), TypeScript (commander), or Go.

## Commands

> Fill in once the project has a build system and entry point.

- **Build:** TBD
- **Run:** TBD
- **Test:** TBD
- **Lint:** TBD

## Key Conventions

- The project owner is the primary user — optimize for personal productivity, not generality.
- New commands go in their own module/file under a `commands/` (or equivalent) directory.
- If a command depends on an external API or LLM, document the required env vars at the top of that file.
