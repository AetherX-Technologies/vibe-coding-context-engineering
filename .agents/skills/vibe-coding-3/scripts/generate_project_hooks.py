#!/usr/bin/env python3
"""Generate canonical Vibe Coding B+ .codex/hooks.json content."""

from __future__ import annotations

import json


def hook_command(script_name: str) -> str:
    return (
        "sh -lc 'ROOT=\"$(git rev-parse --show-toplevel 2>/dev/null || pwd)\"; "
        f"/usr/bin/python3 \"$ROOT/.codex/hooks/{script_name}\"'"
    )


def build_hooks() -> dict:
    return {
        "hooks": {
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": hook_command("user_prompt_submit_router.py"),
                            "timeout": 30,
                            "statusMessage": "Routing Vibe context",
                        }
                    ]
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Bash|apply_patch|Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": hook_command("pre_tool_use_policy.py"),
                            "timeout": 30,
                            "statusMessage": "Checking Vibe tool policy",
                        }
                    ],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": hook_command("post_tool_use_review.py"),
                            "timeout": 30,
                            "statusMessage": "Reviewing Vibe command output",
                        }
                    ],
                }
            ],
            "PreCompact": [
                {
                    "matcher": "manual|auto",
                    "hooks": [
                        {
                            "type": "command",
                            "command": hook_command("pre_compact_checkpoint.py"),
                            "timeout": 30,
                            "statusMessage": "Checking Vibe checkpoint",
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": hook_command("stop_verification_gate.py"),
                            "timeout": 30,
                            "statusMessage": "Checking Vibe verification gate",
                        }
                    ]
                }
            ],
        }
    }


def main() -> int:
    print(json.dumps(build_hooks(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

