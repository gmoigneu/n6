"""Utilities for loading skill files from .claude/skills/."""

from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / ".claude" / "skills"


def load_humanizer() -> str:
    """Load the humanizer skill content."""
    skill_file = SKILLS_DIR / "humanizer" / "SKILL.md"
    if not skill_file.exists():
        raise FileNotFoundError(f"Humanizer skill not found: {skill_file}")
    return skill_file.read_text()
