"""n6 s — search stored memories."""

import typer
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

from n6.config import get_config
from n6.memory import get_memory_client

console = Console()
err = Console(stderr=True)


def search(
    query: str = typer.Argument(..., help="Search query."),
    context: str = typer.Option(
        "global",
        "--context",
        "-c",
        help="Memory context to search (e.g. upsun, writing). Default: global.",
    ),
):
    """Search stored memories semantically."""
    cfg = get_config()
    client = get_memory_client()

    results = client.search(
        query=query,
        user_id=cfg.mem0_user_id,
        filters={"context": context},
        limit=10,
    )
    memories = results.get("results", []) if isinstance(results, dict) else []

    if not memories:
        console.print(f"No memories found. [dim](context: {context})[/dim]")
        return

    err.print(f"[dim]Found {len(memories)} memories — interpreting…[/dim]")

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
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a personal assistant synthesising memory search results. "
                    "Given a query and a list of relevant memories, produce a clear, "
                    "concise markdown response that directly answers the query using the "
                    "memories as source material. Group related information naturally. "
                    "Do not list the raw memories — interpret and synthesise them. "
                    "If the memories don't contain enough to answer, say so briefly."
                ),
            },
            {
                "role": "user",
                "content": f"Query: {query}{context_note}\n\nMemories:\n{memories_text}",
            },
        ],
    )

    answer = response.choices[0].message.content
    console.print(Markdown(answer))
