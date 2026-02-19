## Why

N6 has no persistent memory — information shared across sessions (personal preferences, notes, articles, meeting transcripts) is lost immediately. A searchable memory layer backed by a vector store will let N6 store and recall semantically relevant context on demand.

## What Changes

- Add `mem0` Python SDK + Qdrant as the vector store backend
- Add Qdrant to a new `docker-compose.yml` at the project root
- Add two top-level commands: `m` (store) and `s` (search)
  - `n6 m fact <text>` — store a short fact or preference
  - `n6 m note <text>` — store a free-form note
  - `n6 m meeting` — read a meeting transcript from stdin, extract and store structured memories
  - `n6 s <query>` — semantic search across all stored memories, print results
- Configure mem0 to use GLM (via Z.AI's OpenAI-compatible endpoint) as the LLM
- Add `QDRANT_HOST`, `QDRANT_PORT`, `MEM0_USER_ID` to config (env + `~/.n6.toml`)

## Capabilities

### New Capabilities

- `memory-store`: mem0 + Qdrant integration — client initialisation, config schema, Docker Compose service definition, GLM wiring
- `memory-commands`: `m` and `s` CLI commands — argument parsing, memory type tagging, stdin handling for meetings, Rich-formatted search results

### Modified Capabilities

- `config`: Add new config fields — `qdrant_host`, `qdrant_port`, `mem0_user_id` (no requirement changes, implementation only)

## Impact

- **New file:** `docker-compose.yml` — Qdrant service (port 6333/6334)
- **New files:** `n6/commands/memory.py`, `n6/commands/search.py`
- **New module:** `n6/memory.py` — mem0 client factory, shared config
- **Modified:** `n6/config.py` — three new fields
- **Modified:** `n6/main.py` — register `m` and `s` commands
- **New deps:** `mem0ai`, `qdrant-client`
- Z.AI OpenAI-compatible endpoint used for mem0 LLM (not the Anthropic-compatible one used by `glm.py`) — requires verifying the correct base URL and whether mem0's OpenAI provider accepts a custom `base_url`
