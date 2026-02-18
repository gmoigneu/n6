"""Z.AI GLM client wrapper.

Uses the Anthropic-compatible endpoint provided by the Z.AI coding plan.
Base URL: https://api.z.ai/api/anthropic
Auth:     ZAI_API_KEY used as the Anthropic auth token.
"""

from collections.abc import Iterator
import anthropic
from n6.config import get_config


def get_client() -> anthropic.Anthropic:
    cfg = get_config()
    if not cfg.zai_api_key:
        raise RuntimeError("ZAI_API_KEY is not set (or missing from ~/.n6.toml)")
    return anthropic.Anthropic(
        api_key=cfg.zai_api_key,
        base_url=cfg.zai_base_url,
    )


def ask(prompt: str, system: str = "", model: str = "") -> str:
    """Single-turn, non-streaming call. Returns the response text."""
    cfg = get_config()
    client = get_client()
    try:
        response = client.messages.create(
            model=model or cfg.zai_default_model,
            max_tokens=4096,
            system=system or anthropic.NOT_GIVEN,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        raise RuntimeError(str(e)) from e


def stream(prompt: str, system: str = "", model: str = "") -> Iterator[str]:
    """Single-turn streaming call. Yields text chunks."""
    cfg = get_config()
    client = get_client()
    try:
        with client.messages.stream(
            model=model or cfg.zai_default_model,
            max_tokens=4096,
            system=system or anthropic.NOT_GIVEN,
            messages=[{"role": "user", "content": prompt}],
        ) as s:
            yield from s.text_stream
    except anthropic.APIError as e:
        raise RuntimeError(str(e)) from e
