## Context

N6 currently has no persistent memory. Information — preferences, notes, articles, meeting transcripts — lives only within a single session. The mem0 Python SDK provides a high-level memory abstraction (add/search) backed by a vector store, and handles memory extraction from raw text using an LLM. Qdrant is the chosen vector store, run locally via Docker. GLM (via Z.AI) is used for both the LLM extraction step and embeddings, keeping all inference on the existing Z.AI account.

## Goals / Non-Goals

**Goals:**
- Persist memories across sessions via mem0 + Qdrant
- Three memory input types: `fact` (one-liner), `note` (free-form text), `meeting` (transcript → extracted memories via LLM)
- Semantic search across all stored memories (`n6 s <query>`)
- All inference on Z.AI (LLM + embeddings)
- Qdrant runs in Docker with a named volume for persistence

**Non-Goals:**
- Memory editing or deletion (out of scope for v1)
- Per-type search filtering (all types searched together)
- Remote/cloud Qdrant deployment
- Auth or multi-user isolation (single `user_id`, configurable)

## Decisions

### 1. mem0 LLM provider: `anthropic` via Z.AI Anthropic-compatible endpoint

mem0's `anthropic` provider is used for the LLM. `AnthropicConfig` exposes `anthropic_base_url` but the `AnthropicLLM` implementation does not pass it to the client — it creates `anthropic.Anthropic(api_key=api_key)` without `base_url`. However, the Anthropic SDK respects the `ANTHROPIC_BASE_URL` environment variable when no explicit `base_url` is set.

The workaround: in `n6/memory.py`, before constructing the `mem0.Memory` instance, set `os.environ["ANTHROPIC_BASE_URL"]` to `cfg.zai_base_url`. This reuses the existing `zai_base_url` config value (`https://api.z.ai/api/anthropic`) — the same endpoint that `n6/llm/glm.py` uses — so no new config field is needed for the LLM.

**Config shape:**
```python
# Before constructing mem0.Memory:
os.environ["ANTHROPIC_BASE_URL"] = cfg.zai_base_url  # https://api.z.ai/api/anthropic

"llm": {
    "provider": "anthropic",
    "config": {
        "model": "glm-4.6",
        "api_key": cfg.zai_api_key,
        "temperature": 0.1,
    }
}
```

**Alternative considered:** mem0's `openai` provider with Z.AI's OpenAI-compatible endpoint. Rejected in favour of Anthropic provider since Z.AI's primary supported API shape in N6 is the Anthropic-compatible one, keeping the LLM path consistent with `glm.py`.

### 2. Embedder: `openai` provider with Z.AI, model `embedding-3`

GLM / Zhipu AI ships an `embedding-3` model accessible via the same OpenAI-compatible endpoint. Using it keeps all inference on Z.AI with no additional API keys. The embedder config supports `openai_base_url` identically to the LLM config.

**Config shape:**
```python
"embedder": {
    "provider": "openai",
    "config": {
        "model": "embedding-3",
        "api_key": "<ZAI_API_KEY>",
        "openai_base_url": "<ZAI_OPENAI_BASE_URL>",
        "embedding_dims": 2048,
    }
}
```

`embedding_dims` must match what the model actually returns; `2048` is the documented dimension for `embedding-3`. The Qdrant collection is created with this dimension.

**Alternative considered:** `huggingface` sentence-transformers (local, offline). Rejected because it adds a large dependency and slower first-run; keeping inference on Z.AI is consistent with the rest of N6.

### 3. Memory client: singleton factory in `n6/memory.py`

A single `get_memory_client()` function decorated with `@lru_cache` constructs and returns a `mem0.Memory` instance. Commands import this and call `.add()` / `.search()`. This mirrors the pattern of `n6/llm/glm.py`.

### 4. Memory type tagging via `metadata`

mem0 accepts a `metadata` dict on `.add()`. We store `{"type": "fact" | "note" | "meeting"}` per entry. This enables future filtering without schema changes.

For `meeting`, the transcript is passed as a `user`-role message. mem0 will run its LLM extraction pipeline to distil discrete memories from the transcript rather than storing the raw text verbatim.

### 5. Command structure

- `m` is a Typer command group (not a subapp) registered on the main app. Sub-commands: `fact`, `note`, `meeting`.
- `s` is a standalone command (not in the group) for ergonomics: `n6 s "query"`.
- `m fact` and `m note` accept the text as a positional CLI argument.
- `m meeting` reads from **stdin** (transcript can be large).
- `s` prints results as a Rich table: rank, score, memory text, type tag.

### 6. Docker Compose

A `docker-compose.yml` at the project root defines a single `qdrant` service using the official `qdrant/qdrant` image. Data is persisted in a named Docker volume `qdrant_data`.

## Risks / Trade-offs

- **`ANTHROPIC_BASE_URL` env var side-effect** → Setting it globally in the process will affect any other Anthropic SDK usage in the same process. In practice N6 commands are short-lived CLI processes, so this is acceptable. If N6 ever runs as a long-lived server, this should be revisited in favour of passing `base_url` directly to the client.
- **Z.AI OpenAI-compatible endpoint for embeddings is unverified** → Before implementing, confirm the base URL and that `embedding-3` is accessible via it. If embedding-3 is unavailable, fall back to huggingface sentence-transformers.
- **`embedding_dims` mismatch** → If the actual dims differ from `2048`, Qdrant collection creation fails with a dimension error. Verify by calling the embedding endpoint in a scratch script.
- **mem0 extraction quality on meetings** → mem0 runs its own extraction prompt on the transcript. For long transcripts this may produce noisy or duplicate memories. Mitigation: no action in v1; observe in practice.
- **Qdrant not running** → Commands fail loudly with a connection error. Mitigation: wrap in a friendly error message pointing the user to `docker compose up -d qdrant`.

## Open Questions

1. What is the exact Z.AI OpenAI-compatible base URL for embeddings? (Likely `https://api.z.ai/v1` — needs confirmation)
2. Does the Z.AI plan include `embedding-3`, or is a separate model needed?
3. Should `m meeting` print a summary of extracted memories after storing, or stay silent?
