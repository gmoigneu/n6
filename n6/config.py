"""
Configuration management for Number 6.
Reads from environment variables, with an optional ~/.n6.toml for defaults.
"""

import os
import tomllib
from pathlib import Path
from functools import lru_cache
from dataclasses import dataclass


CONFIG_PATH = Path.home() / ".n6.toml"


@dataclass
class Config:
    # Claude — no API key needed, delegates to the `claude` CLI
    claude_default_model: str = ""

    # Z.AI (GLM-5, OpenAI-compatible)
    zai_api_key: str = ""
    zai_default_model: str = "glm-4.6"
    zai_base_url: str = "https://api.z.ai/api/anthropic"

    # Gemini — API key or Vertex AI (gcloud ADC)
    gemini_api_key: str = ""
    gemini_project: str = ""
    gemini_location: str = "us-central1"


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Load config from ~/.n6.toml then override with env vars."""
    file_cfg: dict = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "rb") as f:
            file_cfg = tomllib.load(f)

    return Config(
        claude_default_model=os.getenv(
            "CLAUDE_DEFAULT_MODEL", file_cfg.get("claude_default_model", "")
        ),
        zai_api_key=os.getenv("ZAI_API_KEY", file_cfg.get("zai_api_key", "")),
        zai_default_model=os.getenv(
            "ZAI_DEFAULT_MODEL", file_cfg.get("zai_default_model", "glm-5")
        ),
        zai_base_url=os.getenv(
            "ZAI_BASE_URL",
            file_cfg.get("zai_base_url", "https://api.z.ai/api/anthropic"),
        ),
        gemini_api_key=os.getenv("GEMINI_API_KEY", file_cfg.get("gemini_api_key", "")),
        gemini_project=os.getenv(
            "GEMINI_PROJECT",
            os.getenv("GOOGLE_CLOUD_PROJECT", file_cfg.get("gemini_project", "")),
        ),
        gemini_location=os.getenv(
            "GEMINI_LOCATION",
            os.getenv("GOOGLE_CLOUD_LOCATION", file_cfg.get("gemini_location", "us-central1")),
        ),
    )
