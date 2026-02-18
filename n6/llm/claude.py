"""Claude client — delegates to the `claude` CLI (uses your Claude Code subscription)."""

import subprocess
from collections.abc import Iterator
from n6.config import get_config


def _build_cmd(system: str = "", model: str = "") -> list[str]:
    """Build the claude CLI command. Prompt is passed via stdin, not as an argument."""
    if not model:
        model = get_config().claude_default_model
    cmd = ["claude", "--print"]
    if system:
        cmd += ["--system-prompt", system]
    if model:
        cmd += ["--model", model]
    return cmd


def ask(prompt: str, system: str = "", model: str = "") -> str:
    """Single-turn, non-streaming call. Returns the response text."""
    result = subprocess.run(
        _build_cmd(system, model),
        input=prompt,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "claude CLI returned a non-zero exit code")
    return result.stdout


def stream(prompt: str, system: str = "", model: str = "") -> Iterator[str]:
    """Single-turn streaming call. Yields text chunks as they arrive."""
    proc = subprocess.Popen(
        _build_cmd(system, model),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.stdin is not None and proc.stdout is not None
    proc.stdin.write(prompt)
    proc.stdin.close()
    for chunk in proc.stdout:
        yield chunk
    proc.wait()
    if proc.returncode != 0:
        err = proc.stderr.read().strip() if proc.stderr else ""
        raise RuntimeError(err or "claude CLI returned a non-zero exit code")
