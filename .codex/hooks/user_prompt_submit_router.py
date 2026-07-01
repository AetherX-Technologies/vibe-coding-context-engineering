#!/usr/bin/env python3
"""Add Vibe context routing hints for incoming prompts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/vibe"))

from policy import context_for, load_hook_event


def main() -> int:
    event = load_hook_event()
    if event.get("hook_event_name") not in (None, "UserPromptSubmit"):
        return 0
    prompt = str(event.get("prompt", "")).lower()
    hints: list[str] = []
    if any(word in prompt for word in ["实现", "修", "bug", "改代码", "develop", "implement", "fix"]):
        hints.append("For Vibe B+ implementation work, read AGENTS.md, docs/PRD.md, docs/acceptance.md, .context/plan.md, and .context/state.json before editing.")
        hints.append("Create or update verification evidence in .context/verification.jsonl before finalizing.")
    if any(word in prompt for word in ["hook", "codex", "skill", "plugin"]):
        hints.append("Use $openai-docs for Codex hook/config/skill/plugin semantics before changing lifecycle behavior.")
    if any(word in prompt for word in ["上线", "提交", "pr", "ship", "release"]):
        hints.append("Use ecc:verification-loop and ecc:security-review before reporting ready status.")
    if hints:
        context_for("UserPromptSubmit", "\n".join(hints))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

