## Context

N6 already has a working memory system (`n6 m` / `n6 s`) backed by mem0 + Qdrant + OpenAI. All interaction is CLI-only. Adding longer content (articles, meeting transcripts) is cumbersome from the terminal — you need to pipe files or paste into a terminal. Searching is one-shot; there's no conversational follow-up. A local web interface removes both friction points without requiring any new backend infrastructure.

The existing `n6.memory` module provides the mem0 client singleton. The `n6/commands/search.py` pattern (mem0 search → OpenAI synthesis) is the model for the chat backend. The serve command wraps both in a Gradio app.

## Goals / Non-Goals

**Goals:**
- `n6 serve` launches a local Gradio app that opens in the browser
- Add Memory tab: three input methods (paste/type, file upload, URL fetch), context selector, type selector
- Chat tab: streaming conversational interface that queries mem0 and synthesises answers via OpenAI
- URL fetching: fetch page content, strip HTML, store as article
- Reuse existing `n6.memory` and search patterns — no new backend infrastructure

**Non-Goals:**
- Remote/public deployment — local only
- Authentication or user accounts
- Persistent chat history across server restarts
- PDF parsing (files limited to `.txt` and `.md` for now)
- Any UI beyond the two core tabs

## Decisions

### Gradio over Flask/FastAPI + custom frontend
Gradio provides built-in chat interface with streaming, file upload widget, tab layout, and a textbox — all with zero frontend code. A Flask/FastAPI approach would require writing HTML/JS. Given this is a personal local tool, Gradio's opinionated UI is the right trade-off. The `gr.ChatInterface` component handles streaming generator functions natively.

**Alternatives considered:**
- **FastAPI + HTMX**: More control but requires maintaining HTML templates
- **Streamlit**: Similar to Gradio, but `st.chat_message` has less ergonomic streaming support and Streamlit's execution model (reruns on interaction) is harder to reason about for chat

### httpx for URL fetching
`httpx` is already a transitive dependency in the Python ecosystem (used by several packages in the stack). It supports both sync and async usage, and handles redirects and timeouts cleanly. `requests` would also work but `httpx` is preferred for new code.

**Alternative considered:** `urllib` — no external dependency but verbose for stripping HTML.

We use `httpx` + a simple regex/BeautifulSoup-lite approach to strip script/style tags and extract readable text. Full `beautifulsoup4` is heavier than needed for this use case; we'll use stdlib `html.parser` via `html` module to unescape, and a regex to strip tags.

### Store URL content as article type
Fetched URL content is stored with `type=article` and `storage=facts` (infer=True) + `storage=verbatim` (infer=False), identical to `n6 m article`. The URL is added to metadata as `source`. This mirrors the existing two-pass approach.

### Streaming in Chat tab
Gradio `gr.ChatInterface` accepts a generator function — `yield` each token chunk. We use `openai.chat.completions.create(..., stream=True)` and yield chunks as they arrive, identical to how `n6/llm/claude.py` streams via subprocess. Context window is capped at 10 mem0 results (same as `n6 s`).

### Context selector implementation
Both tabs expose a free-text input for context (defaulting to `"global"`). A dropdown is avoided because contexts are user-defined and not enumerable from the config — a textbox is simpler and more flexible.

## Risks / Trade-offs

- **Gradio version churn**: Gradio's API has changed significantly between major versions. Pin to a known-good version (4.x) to avoid surprises. → Mitigation: pin `gradio>=4.0,<5` in pyproject.toml.
- **HTML stripping quality**: Regex-based HTML stripping misses some content (JS-rendered pages, paywalled content). → Mitigation: acceptable for personal use; log a warning if fetched content is very short.
- **No chat history persistence**: Chat history lives only in Gradio session state; restarting `n6 serve` clears it. → Accepted trade-off; persistence can be added later via mem0's conversation storage if needed.
- **Blocking on Gradio launch**: `gr.launch()` blocks the process by default. → Use `server_name="127.0.0.1"` to ensure local-only and pass `inbrowser=True` to auto-open the browser.

## Open Questions

- None — scope is well-defined and local-only deployment eliminates auth/security questions.
