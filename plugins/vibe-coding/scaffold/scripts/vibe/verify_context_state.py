#!/usr/bin/env python3
"""Verify the Vibe Coding B+ scaffold is present and parseable."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from policy import build_arg_parser, require_paths, workspace_root


def main() -> int:
    parser = build_arg_parser("Verify Vibe Coding B+ scaffold")
    args = parser.parse_args()
    root = workspace_root(args.root)

    missing = require_paths(root)
    errors: list[str] = []
    if missing:
        errors.append("Missing required paths:\n" + "\n".join(f"- {item}" for item in missing))

    for rel in [".context/state.json", ".codex/hooks.json"]:
        path = root / rel
        if path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{rel} is invalid JSON: {exc}")

    hooks_dir = root / ".codex/hooks"
    if hooks_dir.exists():
        for script in hooks_dir.glob("*.py"):
            if not script.read_text(encoding="utf-8", errors="replace").startswith("#!/usr/bin/env python3"):
                errors.append(f"{script.relative_to(root)} must start with python3 shebang")

    if errors:
        print("\n\n".join(errors), file=sys.stderr)
        return 1

    print("Vibe context scaffold verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

