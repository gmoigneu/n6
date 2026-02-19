## ADDED Requirements

### Requirement: n6 serve launches a local Gradio app
The system SHALL provide an `n6 serve` command that starts a Gradio web server bound to `127.0.0.1` on a configurable port (default `7860`). The app SHALL open automatically in the default browser on launch.

#### Scenario: Server starts successfully
- **WHEN** the user runs `n6 serve`
- **THEN** a Gradio app is accessible at `http://127.0.0.1:7860` and the browser opens automatically

#### Scenario: Custom port via option
- **WHEN** the user runs `n6 serve --port 8080`
- **THEN** the Gradio app is bound to port 8080

### Requirement: Add Memory tab accepts text, file upload, and URL inputs
The Add Memory tab SHALL provide three mutually exclusive input methods:
- **Text input**: a multiline textbox for pasting or typing content
- **File upload**: accepts `.txt` and `.md` files; content is read and stored
- **URL fetch**: a URL textbox; the page is fetched, HTML stripped, and plain text stored

The tab SHALL also provide:
- A **Context** textbox (default `"global"`)
- A **Type** dropdown with options: `fact`, `note`, `article`, `meeting`, `social`
- A **Store** button that triggers storage

#### Scenario: Storing pasted text
- **WHEN** the user pastes text into the text input, selects type and context, and clicks Store
- **THEN** the text is stored in mem0 with the selected type and context metadata, and a success message is shown

#### Scenario: Storing an uploaded file
- **WHEN** the user uploads a `.txt` or `.md` file, selects type and context, and clicks Store
- **THEN** the file contents are read and stored in mem0 with the selected type and context, and a success message is shown

#### Scenario: Storing content from a URL
- **WHEN** the user enters a URL, selects type and context, and clicks Store
- **THEN** the page is fetched, HTML is stripped to plain text, and the text is stored in mem0 with the selected type, context, and `source` metadata set to the URL

#### Scenario: URL fetch fails
- **WHEN** the user enters an unreachable or invalid URL and clicks Store
- **THEN** an error message is shown and nothing is stored in mem0

#### Scenario: Article type uses two-pass storage
- **WHEN** the user selects type `article` and clicks Store
- **THEN** storage uses two passes: `infer=True` (fact extraction) and `infer=False` (verbatim), identical to the `n6 m article` CLI command

### Requirement: Chat tab provides conversational memory search
The Chat tab SHALL provide a `gr.ChatInterface` component backed by mem0 search + OpenAI synthesis. Responses SHALL stream token-by-token. The tab SHALL include a **Context** textbox (default `"global"`) that scopes the mem0 search.

#### Scenario: User asks a question in the chat
- **WHEN** the user types a question and submits
- **THEN** mem0 is searched with the question and context, results are synthesised by OpenAI `gpt-4o-mini`, and the answer streams into the chat

#### Scenario: No memories found
- **WHEN** the user asks a question but no relevant memories exist in the given context
- **THEN** the chat responds with a clear message indicating no relevant memories were found

#### Scenario: Streaming response
- **WHEN** the chat generates a response
- **THEN** tokens appear progressively in the chat window as they are generated (not all at once)

### Requirement: serve command dependencies are declared
The project SHALL declare `gradio>=4.0,<5` and `httpx` as runtime dependencies in `pyproject.toml`.

#### Scenario: Dependencies install cleanly
- **WHEN** `uv sync` is run after adding the dependencies
- **THEN** `gradio` and `httpx` are installed without conflict
