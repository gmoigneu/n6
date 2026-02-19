"""n6 serve — local Gradio web interface for the memory system."""

from typing import Generator

import typer
from openai import OpenAI
from rich.console import Console

from n6.config import get_config
from n6.memory import get_memory_client
from n6.serve_utils import fetch_url

err = Console(stderr=True)

_CHAT_SYSTEM_PROMPT = (
    "You are a personal assistant synthesising memory search results. "
    "Given a query and a list of relevant memories, produce a clear, "
    "concise markdown response that directly answers the query using the "
    "memories as source material. Group related information naturally. "
    "Do not list the raw memories — interpret and synthesise them. "
    "If the memories don't contain enough to answer, say so briefly."
)


def _store_memory(text: str, input_type: str, context: str) -> str:
    """Store text in mem0. Returns a status message."""
    cfg = get_config()
    client = get_memory_client()
    base_metadata = {"type": input_type, "context": context}

    if input_type == "article":
        # Two-pass: extract facts + verbatim
        result = client.add(
            [{"role": "user", "content": text}],
            user_id=cfg.mem0_user_id,
            metadata={**base_metadata, "storage": "facts"},
            infer=True,
        )
        facts_count = len(result) if isinstance(result, list) else len(result.get("results", [])) if isinstance(result, dict) else 0
        client.add(
            [{"role": "user", "content": text}],
            user_id=cfg.mem0_user_id,
            metadata={**base_metadata, "storage": "verbatim"},
            infer=False,
        )
        return f"✓ Article stored — {facts_count} facts extracted + verbatim. (context: {context})"
    else:
        client.add(
            [{"role": "user", "content": text}],
            user_id=cfg.mem0_user_id,
            metadata=base_metadata,
        )
        return f"✓ {input_type.capitalize()} stored. (context: {context})"


def _handle_store(
    text_input: str,
    file_obj,
    url_input: str,
    context: str,
    input_type: str,
) -> str:
    """Store button handler. Prioritises text > file > URL."""
    context = (context or "global").strip()
    input_type = (input_type or "note").strip()

    content = None
    source = None

    if text_input and text_input.strip():
        content = text_input.strip()
        source = "text"
    elif file_obj is not None:
        try:
            with open(file_obj, "r", encoding="utf-8") as f:
                content = f.read().strip()
            source = "file"
        except Exception as e:
            return f"✗ Could not read file: {e}"
    elif url_input and url_input.strip():
        try:
            content = fetch_url(url_input.strip())
            source = "url"
            # Override type to article for URL fetches, and tag source
        except Exception as e:
            return f"✗ URL fetch failed: {e}"

    if not content:
        return "✗ No content provided. Paste text, upload a file, or enter a URL."

    # For URL input, always store as article with source metadata
    if source == "url":
        cfg = get_config()
        client = get_memory_client()
        base_metadata = {"type": "article", "context": context, "source": url_input.strip()}
        result = client.add(
            [{"role": "user", "content": content}],
            user_id=cfg.mem0_user_id,
            metadata={**base_metadata, "storage": "facts"},
            infer=True,
        )
        facts_count = len(result) if isinstance(result, list) else len(result.get("results", [])) if isinstance(result, dict) else 0
        client.add(
            [{"role": "user", "content": content}],
            user_id=cfg.mem0_user_id,
            metadata={**base_metadata, "storage": "verbatim"},
            infer=False,
        )
        return (
            f"✓ URL content stored — {facts_count} facts extracted + verbatim. (context: {context})"
        )

    try:
        return _store_memory(content, input_type, context)
    except Exception as e:
        return f"✗ Error storing memory: {e}"


def _chat_fn(
    message: str,
    history: list,
    context: str,
) -> Generator[str, None, None]:
    """Streaming chat generator for the Chat tab."""
    context = (context or "global").strip()
    cfg = get_config()
    client = get_memory_client()

    results = client.search(
        query=message,
        user_id=cfg.mem0_user_id,
        filters={"context": context},
        limit=10,
    )
    memories = results.get("results", []) if isinstance(results, dict) else []

    if not memories:
        yield f"No memories found for your query in context **{context!r}**."
        return

    memories_text = "\n".join(
        "- [{type}]{platform} {memory}".format(
            type=item.get("metadata", {}).get("type", "unknown"),
            platform=(
                f"[{item['metadata']['platform']}]"
                if item.get("metadata", {}).get("platform")
                else ""
            ),
            memory=item.get("memory", ""),
        )
        for item in memories
    )

    context_note = f" in the '{context}' context" if context != "global" else ""
    openai_client = OpenAI(api_key=cfg.openai_api_key)

    stream = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        stream=True,
        messages=[
            {"role": "system", "content": _CHAT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Query: {message}{context_note}\n\nMemories:\n{memories_text}",
            },
        ],
    )

    accumulated = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            accumulated += delta
            yield accumulated


def serve(
    port: int = typer.Option(7860, "--port", "-p", help="Port to bind the local server to."),
):
    """Launch a local Gradio web interface for adding and querying memories."""
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"websockets.*")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"uvicorn.*")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"gradio.*")
    warnings.filterwarnings("ignore", message=r".*no_silent_downcasting.*")
    warnings.filterwarnings("ignore", message=r".*copy keyword is deprecated.*")

    import gradio as gr

    # --- Add Memory Tab ---
    with gr.Blocks(title="N6 Memory") as app:
        gr.Markdown("# N6 Memory Interface")

        with gr.Tab("Add Memory"):
            gr.Markdown("Store text, a file, or a web page into memory.")
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(
                        label="Paste or type text",
                        lines=8,
                        placeholder="Paste content here…",
                    )
                    file_input = gr.File(
                        label="Upload file (.txt or .md)",
                        file_types=[".txt", ".md"],
                    )
                    url_input = gr.Textbox(
                        label="Fetch from URL",
                        placeholder="https://example.com/article",
                    )
                with gr.Column():
                    add_context = gr.Textbox(
                        label="Context",
                        value="global",
                        placeholder="e.g. upsun, writing, personal",
                    )
                    input_type = gr.Dropdown(
                        label="Type",
                        choices=["fact", "note", "article", "meeting", "social"],
                        value="note",
                    )
                    store_btn = gr.Button("Store", variant="primary")
                    status_output = gr.Textbox(label="Status", interactive=False)

            store_btn.click(
                fn=_handle_store,
                inputs=[text_input, file_input, url_input, add_context, input_type],
                outputs=status_output,
            )

        # --- Chat Tab ---
        with gr.Tab("Chat"):
            gr.Markdown("Ask questions about your stored memories.")
            chat_context = gr.Textbox(
                label="Context",
                value="global",
                placeholder="e.g. upsun, writing, personal",
                scale=1,
            )
            gr.ChatInterface(
                fn=_chat_fn,
                additional_inputs=[chat_context],
                fill_height=True,
            )

    err.print(f"[green]Starting N6 web interface at http://127.0.0.1:{port}[/green]")
    app.launch(server_name="127.0.0.1", server_port=port, inbrowser=True)
