#!/usr/bin/env python3
"""Warn before compaction when Vibe state is missing."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/vibe"))

from policy import load_hook_event


def main() -> int:
    event = load_hook_event()
    if event.get("hook_event_name") not in (None, "PreCompact"):
        return 0
    missing = []
    for rel in [".context/state.json", ".context/plan.md"]:
        if not (ROOT / rel).exists():
            missing.append(rel)
    has_checkpoint = any((ROOT / ".context/checkpoints").glob("*.md"))
    if not has_checkpoint:
        missing.append(".context/checkpoints/*.md")
    if missing:
        print(
            json.dumps(
                {
                    "continue": False,
                    "stopReason": "Missing Vibe checkpoint state before compaction.",
                    "systemMessage": "Write or update Vibe checkpoint state before compaction: "
                    + ", ".join(missing),
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

