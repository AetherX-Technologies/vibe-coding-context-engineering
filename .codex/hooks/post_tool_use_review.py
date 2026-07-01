#!/usr/bin/env python3
"""Codex PostToolUse review for Bash verification output."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/vibe"))

from policy import append_jsonl, changed_files, command_from_event, fingerprint_files, load_hook_event, now_iso


def main() -> int:
    event = load_hook_event()
    if event.get("hook_event_name") not in (None, "PostToolUse"):
        return 0
    if event.get("tool_name") != "Bash":
        return 0

    response = event.get("tool_response")
    if not isinstance(response, dict):
        return 0
    exit_code = response.get("exit_code")
    status = "passed" if exit_code in (0, None) else "failed"
    command = command_from_event(event)
    if not any(token in command for token in ["test", "lint", "typecheck", "build", "verify", "scan_secrets"]):
        return 0

    files = changed_files(ROOT)
    record = {
        "time": now_iso(),
        "session_id": event.get("session_id", "unknown"),
        "turn_id": event.get("turn_id", "unknown"),
        "command": command,
        "status": status,
        "changed_files": files,
        "changed_files_fingerprint": fingerprint_files(ROOT, files),
        "summary": f"Bash verification command {status}",
    }
    append_jsonl(ROOT / ".context/verification.jsonl", record)
    if status == "failed":
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": "Verification command failed. Fix the failure before continuing.",
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": "A failed verification record was appended to .context/verification.jsonl.",
                    },
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

