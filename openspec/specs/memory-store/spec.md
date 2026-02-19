## ADDED Requirements

### Requirement: mem0 client is initialised with Qdrant and OpenAI
The system SHALL provide a `get_memory_client()` factory in `n6/memory.py` that returns a configured `mem0.Memory` instance using:
- **Vector store:** Qdrant (local Docker)
- **LLM:** OpenAI `gpt-4o-mini` (used by mem0 for memory extraction)
- **Embedder:** OpenAI `text-embedding-3-small` (1536 dims)

The client SHALL be a singleton (constructed once per process via `@lru_cache`).

#### Scenario: Client initialises successfully when Qdrant is running
- **WHEN** `get_memory_client()` is called and Qdrant is reachable at the configured host/port
- **THEN** a `mem0.Memory` instance is returned without error

#### Scenario: Client raises a clear error when Qdrant is unreachable
- **WHEN** `get_memory_client()` is called and Qdrant is not running
- **THEN** the function raises a `RuntimeError` with a message directing the user to run `docker compose up -d qdrant`

#### Scenario: Client uses config values from environment and ~/.n6.toml
- **WHEN** `OPENAI_API_KEY`, `QDRANT_HOST`, and `QDRANT_PORT` are set
- **THEN** the mem0 client is constructed using those values

### Requirement: Memories are stored with type metadata
The system SHALL tag every stored memory with `metadata={"type": "<type>"}` where type is one of `fact`, `note`, or `meeting`. The `user_id` SHALL be read from config (`MEM0_USER_ID`, default `"default"`).

#### Scenario: Storing a fact includes type metadata
- **WHEN** a fact is stored via `client.add()`
- **THEN** the metadata dict contains `{"type": "fact"}`

#### Scenario: Storing a meeting transcript includes type metadata
- **WHEN** a meeting transcript is stored via `client.add()`
- **THEN** the metadata dict contains `{"type": "meeting"}`

### Requirement: Docker Compose defines the Qdrant service
The project root SHALL contain a `docker-compose.yml` that defines a `qdrant` service using the `qdrant/qdrant` image, exposing ports `6333` (HTTP/REST) and `6334` (gRPC), and persisting data in a named Docker volume `qdrant_data`.

#### Scenario: Qdrant starts with persistent storage
- **WHEN** `docker compose up -d qdrant` is run
- **THEN** the Qdrant service starts and data is stored in the `qdrant_data` volume, surviving container restarts

### Requirement: Dependencies are declared in pyproject.toml
The project SHALL declare `mem0ai` and `qdrant-client` as runtime dependencies in `pyproject.toml`.

#### Scenario: Dependencies install cleanly
- **WHEN** `uv sync` is run
- **THEN** `mem0ai` and `qdrant-client` are installed without conflict
