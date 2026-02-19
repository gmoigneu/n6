## 1. Dependencies

- [x] 1.1 Add `gradio>=4.0,<5` and `httpx` to `pyproject.toml` via `uv add gradio "httpx"`
- [x] 1.2 Run `uv sync` to verify dependencies install cleanly

## 2. URL Fetching Utility

- [x] 2.1 Create `n6/serve_utils.py` with a `fetch_url(url: str) -> str` function that uses `httpx` to GET the URL (follow redirects, 10s timeout), strips `<script>`, `<style>`, and all other HTML tags using regex, unescapes HTML entities, collapses whitespace, and raises `ValueError` if the result is fewer than 50 characters

## 3. Core Serve Command

- [x] 3.1 Create `n6/commands/serve.py` with the `serve()` Typer command accepting `--port` (default `7860`)
- [x] 3.2 Implement `store_memory(text, input_type, context)` helper that dispatches to mem0 `client.add()` using the correct two-pass logic for `article` type and single-pass for all others
- [x] 3.3 Implement `build_add_tab()` that returns a `gr.Tab` with: text input, file upload (`.txt`/`.md`), URL textbox, context textbox (default `"global"`), type dropdown (`fact`, `note`, `article`, `meeting`, `social`), Store button, and status output
- [x] 3.4 Wire the Store button click handler: read whichever of text/file/URL is non-empty (in that priority order), call `store_memory()` or `fetch_url()` + `store_memory()`, return success/error string
- [x] 3.5 Implement `build_chat_tab()` that returns a `gr.Tab` with a `gr.ChatInterface` backed by a streaming generator function and a context textbox (default `"global"`)
- [x] 3.6 Implement the chat generator: call `client.search(query, user_id, filters={"context": context}, limit=10)`, format results, call `openai.chat.completions.create(..., stream=True)` with the same system prompt as `n6 s`, and `yield` each chunk
- [x] 3.7 Assemble the Gradio app with `gr.TabbedInterface` (or `gr.Blocks` with tabs), call `app.launch(server_name="127.0.0.1", server_port=port, inbrowser=True)`

## 4. Registration

- [x] 4.1 Import and register `serve` in `n6/main.py` with `app.command()(serve)`

## 5. README Update

- [x] 5.1 Add `n6 serve` entry to the commands table in `README.md`
- [x] 5.2 Add a `### n6 serve` section with usage example and `--port` option table
