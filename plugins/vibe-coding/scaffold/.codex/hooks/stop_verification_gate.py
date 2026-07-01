#!/usr/bin/env python3
"""Stop-phase verification gate for Vibe Coding B+."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/vibe"))

from policy import changed_files, fingerprint_files, latest_passed_verification, load_hook_event, stop_continue


def main() -> int:
    event = load_hook_event()
    if event.get("hook_event_name") not in (None, "Stop"):
        return 0
    if event.get("stop_hook_active"):
        return 0

    files = changed_files(ROOT)
    if not files:
        return 0
    fingerprint = fingerprint_files(ROOT, files)
    if latest_passed_verification(ROOT, fingerprint):
        return 0

    stop_continue(
        "Run the Vibe verification gate before finalizing. "
        f"No passed verification record matches changed_files_fingerprint={fingerprint}. "
        "If verification cannot run, report the concrete blocker."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

