"""mem0 client factory for N6's memory system.

Uses Qdrant as the vector store, and OpenAI for both the LLM (gpt-4o-mini)
and embeddings (text-embedding-3-small).
"""

from functools import lru_cache

from mem0 import Memory

from n6.config import get_config


@lru_cache(maxsize=1)
def get_memory_client() -> Memory:
    """Return a singleton mem0 Memory instance configured for N6."""
    cfg = get_config()

    if not cfg.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set (or missing from ~/.n6.toml)")

    mem0_config = {
        "llm": {
            "provider": "openai",
            "config": {
                "model": "gpt-4o-mini",
                "api_key": cfg.openai_api_key,
                "temperature": 0.1,
                "max_tokens": 2000,
            },
        },
        "embedder": {
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small",
                "api_key": cfg.openai_api_key,
                "embedding_dims": 1536,
            },
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "n6_memories",
                "host": cfg.qdrant_host,
                "port": cfg.qdrant_port,
            },
        },
    }

    try:
        return Memory.from_config(mem0_config)
    except Exception as e:
        msg = str(e).lower()
        if "connection" in msg or "refused" in msg or "qdrant" in msg:
            raise RuntimeError(
                f"Cannot connect to Qdrant at {cfg.qdrant_host}:{cfg.qdrant_port}. "
                "Start it with: docker compose up -d qdrant"
            ) from e
        raise
