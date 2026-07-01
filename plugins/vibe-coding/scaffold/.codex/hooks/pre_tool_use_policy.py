#!/usr/bin/env python3
"""Codex PreToolUse policy for Vibe Coding B+."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/vibe"))

from policy import (
    bash_policy,
    command_from_event,
    context_for,
    deny_pre_tool,
    load_hook_event,
    scan_text_for_secrets,
)


def main() -> int:
    event = load_hook_event()
    if event.get("hook_event_name") not in (None, "PreToolUse"):
        return 0

    tool_name = str(event.get("tool_name", ""))
    command = command_from_event(event)

    if tool_name == "Bash":
        decision, reason = bash_policy(command)
        if decision == "deny":
            deny_pre_tool(reason)
        elif decision == "warn":
            context_for("PreToolUse", reason)
        return 0

    if tool_name == "apply_patch":
        findings = scan_text_for_secrets("<apply_patch>", command)
        if findings:
            first = findings[0]
            deny_pre_tool(f"Potential secret blocked in patch ({first.name}) at line {first.line}.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

