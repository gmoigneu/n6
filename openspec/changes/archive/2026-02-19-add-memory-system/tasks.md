## 1. Infrastructure

- [x] 1.1 Create `docker-compose.yml` at project root with `qdrant` service (`qdrant/qdrant` image, ports 6333/6334, named volume `qdrant_data`)
- [x] 1.2 Verify `mem0ai` and `qdrant-client` are listed as dependencies in `pyproject.toml` (already added via `uv add`)

## 2. Config

- [x] 2.1 Add `qdrant_host` (default `"localhost"`), `qdrant_port` (default `6333`), `mem0_user_id` (default `"default"`), and `zai_openai_base_url` (default `"https://api.z.ai/v1"`) fields to `Config` dataclass in `n6/config.py`
- [x] 2.2 Wire the four new fields through `get_config()` (env vars: `QDRANT_HOST`, `QDRANT_PORT`, `MEM0_USER_ID`, `ZAI_OPENAI_BASE_URL`)
- [x] 2.3 Update `CLAUDE.md` config table with the four new env vars

## 3. Memory Client

- [x] 3.1 Create `n6/memory.py` with `get_memory_client()` — set `os.environ["ANTHROPIC_BASE_URL"] = cfg.zai_base_url` before constructing mem0, builds `mem0.Memory` config dict (LLM: anthropic provider + `glm-4.6` + `zai_api_key`, embedder: openai + `embedding-3` + `zai_openai_base_url`, vector store: qdrant + host/port from config)
- [x] 3.2 Decorate `get_memory_client()` with `@lru_cache` for singleton behaviour
- [x] 3.3 Wrap the Qdrant connection attempt in a try/except and raise `RuntimeError` with a `docker compose up -d qdrant` hint on connection failure
- [x] 3.4 Verify end-to-end: start Qdrant, run a scratch script to call `get_memory_client().add(...)` and confirm a memory is stored

## 4. `m` Commands

- [x] 4.1 Create `n6/commands/memory.py` — define a Typer sub-app `app` with commands `fact`, `note`, and `meeting`
- [x] 4.2 Implement `fact(text: str)` — calls `client.add([{"role": "user", "content": text}], user_id=..., metadata={"type": "fact"})`, prints confirmation to stderr
- [x] 4.3 Implement `note(text: str)` — same pattern as `fact` with `metadata={"type": "note"}`
- [x] 4.4 Implement `meeting()` — reads from `sys.stdin`, errors if stdin is empty/a TTY, calls `client.add([{"role": "user", "content": transcript}], ..., metadata={"type": "meeting"})`, prints count of stored memories to stderr
- [x] 4.5 Register the `memory.app` sub-app on the main Typer app in `n6/main.py` under the name `m`

## 5. `s` Command

- [x] 5.1 Create `n6/commands/search.py` — define `search(query: str)` function
- [x] 5.2 Call `client.search(query=query, user_id=..., limit=10)` and handle empty results with a "No memories found." message
- [x] 5.3 Render results as a Rich table (columns: `#`, `score`, `memory`, `type`) printed to stdout
- [x] 5.4 Register `search` as command `s` on the main Typer app in `n6/main.py`

## 6. Verification

- [x] 6.1 Confirm Z.AI Anthropic endpoint (`zai_base_url`) accepts `glm-4.6` requests via mem0's Anthropic provider (smoke test: run `get_memory_client()` and call `.add()` once)
- [x] 6.2 Confirm `embedding-3` model is available at the Z.AI endpoint and returns vectors of the expected dimension
- [x] 6.3 Run `n6 m fact "test"`, `n6 m note "test note"`, pipe a short transcript to `n6 m meeting`, then run `n6 s "test"` and confirm results appear
- [x] 6.4 Run `uv run ruff check n6/ && uv run ruff format n6/`
