"""OpenAI client wrapper."""

from collections.abc import Iterator
import openai as _openai
from n6.config import get_config

_DEFAULT_MODEL = "gpt-4.1-nano"


def get_client() -> _openai.OpenAI:
    cfg = get_config()
    if not cfg.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set (or missing from ~/.n6.toml)")
    return _openai.OpenAI(api_key=cfg.openai_api_key)


def ask(prompt: str, system: str = "", model: str = "") -> str:
    """Single-turn, non-streaming call. Returns the response text."""
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        response = client.chat.completions.create(
            model=model or _DEFAULT_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content or ""
    except _openai.APIError as e:
        raise RuntimeError(str(e)) from e


def stream(prompt: str, system: str = "", model: str = "") -> Iterator[str]:
    """Single-turn streaming call. Yields text chunks."""
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        stream = client.chat.completions.create(
            model=model or _DEFAULT_MODEL,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except _openai.APIError as e:
        raise RuntimeError(str(e)) from e
