"""Utilities for the n6 serve command (URL fetching and HTML stripping)."""

import html
import re

import httpx


def fetch_url(url: str) -> str:
    """Fetch a URL and return its content as plain text.

    Strips script/style blocks and all HTML tags, unescapes entities,
    and collapses whitespace. Raises ValueError if the result is too short.
    """
    response = httpx.get(url, follow_redirects=True, timeout=10.0)
    response.raise_for_status()

    raw = response.text

    # Remove script and style blocks (including their content)
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.DOTALL | re.IGNORECASE)

    # Strip all remaining HTML tags
    raw = re.sub(r"<[^>]+>", " ", raw)

    # Unescape HTML entities (&amp; &lt; etc.)
    raw = html.unescape(raw)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", raw).strip()

    if len(text) < 50:
        raise ValueError(
            f"Fetched content from {url!r} is too short ({len(text)} chars) — the page may be empty, JS-rendered, or paywalled."
        )

    return text
