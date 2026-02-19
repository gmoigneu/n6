"""mem0 client factory for N6's memory system.

Uses Qdrant as the vector store, and OpenAI for both the LLM (gpt-4o-mini)
and embeddings (text-embedding-3-small).
"""

from functools import lru_cache

from mem0 import Memory

from n6.config import get_config

# Replaces mem0's default personal-facts-only extraction prompt with one that
# works across all content types (articles, meetings, notes, social posts,
# personal facts). Intentionally loose — err on the side of extracting more.
_EXTRACTION_PROMPT = """\
You are a knowledge extraction specialist. Extract every meaningful, retrievable \
piece of information from the input text.

Be broad and inclusive. Extract:
- Personal facts, preferences, opinions, and plans
- Key claims, arguments, findings, and recommendations from articles or documents
- Decisions, action items, topics, and participants from meetings
- Opinions, positions, and key claims from social media posts
- Ideas, todos, references, and observations from notes
- Any technical facts, best practices, statistics, or named concepts worth remembering

Each extracted fact must be:
- Self-contained (meaningful when read in isolation)
- Concise (one idea per fact)
- Specific (not vague or generic)

Return ONLY a JSON object in exactly this format:
{"facts": ["fact 1", "fact 2", ...]}

Return {"facts": []} only if the input contains no meaningful information at all \
(e.g. greetings, filler, empty content).

Examples:
Input: "user: I prefer tabs over spaces in Python."
Output: {"facts": ["Prefers tabs over spaces in Python"]}

Input: "user: According to the Imperva Bad Bot Report 2025, 51% of web traffic \
is now automated."
Output: {"facts": ["51% of web traffic is automated according to Imperva Bad Bot Report 2025"]}

Input: "user: Meeting notes — decided to migrate to Upsun by Q2. Alice owns the \
migration plan. Budget is 20k."
Output: {"facts": ["Team decided to migrate to Upsun by Q2", "Alice owns the migration plan", "Migration budget is 20k"]}

Input: "user: Hi there!"
Output: {"facts": []}

Now extract facts from the following:
"""


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
        "custom_fact_extraction_prompt": _EXTRACTION_PROMPT,
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
