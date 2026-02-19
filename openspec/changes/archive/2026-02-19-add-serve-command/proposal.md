## Why

The memory system is CLI-only, which creates friction when adding longer content (articles, notes, meeting transcripts) or when exploring stored memories conversationally. A local web interface removes that friction — paste, upload, or fetch by URL to store; chat naturally to query.

## What Changes

- New `n6 serve` command that launches a local Gradio app in the browser
- Two-tab interface: **Add Memory** tab and **Chat** tab
- Add Memory tab: accepts text input (paste/type), file upload (`.txt`, `.md`, `.pdf`), or URL fetch; context selector; memory type selector (fact, note, article, meeting, social)
- Chat tab: conversational interface backed by mem0 search + OpenAI, with streaming responses
- URL fetching for article ingestion (new input method not in the CLI)
- No new backend logic — reuses `n6.memory` and `n6.commands.search` patterns

## Capabilities

### New Capabilities

- `serve-command`: Gradio-based local web UI with Add Memory and Chat tabs

### Modified Capabilities

- `memory-store`: URL ingestion is a new input method (fetch page content, then store as article)

## Impact

- New file: `n6/commands/serve.py`
- New dependency: `gradio` (local server + UI), `httpx` (URL fetching)
- `n6/main.py`: register `serve` command
- No breaking changes to existing CLI commands
- Local-only; no auth, no public exposure
