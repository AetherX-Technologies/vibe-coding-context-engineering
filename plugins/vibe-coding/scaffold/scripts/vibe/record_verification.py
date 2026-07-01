#!/usr/bin/env python3
"""Append a Vibe verification record for the current workspace fingerprint."""

from __future__ import annotations

import argparse

from policy import append_jsonl, changed_files, fingerprint_files, now_iso, workspace_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a Vibe verification result")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument("--command", required=True, help="Verification command")
    parser.add_argument("--status", choices=["passed", "failed", "blocked"], required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--details", default=None)
    parser.add_argument("--session-id", default="manual")
    parser.add_argument("--turn-id", default="manual")
    args = parser.parse_args()

    root = workspace_root(args.root)
    files = changed_files(root)
    payload = {
        "time": now_iso(),
        "session_id": args.session_id,
        "turn_id": args.turn_id,
        "command": args.command,
        "status": args.status,
        "changed_files": files,
        "changed_files_fingerprint": fingerprint_files(root, files),
        "summary": args.summary,
    }
    if args.details:
        payload["details"] = args.details
    append_jsonl(root / ".context/verification.jsonl", payload)
    print("Recorded verification:", payload["changed_files_fingerprint"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

