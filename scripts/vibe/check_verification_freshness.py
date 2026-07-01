#!/usr/bin/env python3
"""Check whether current changed files have a matching passed verification record."""

from __future__ import annotations

import sys

from policy import (
    build_arg_parser,
    changed_files,
    fingerprint_files,
    latest_passed_verification,
    workspace_root,
)


def main() -> int:
    parser = build_arg_parser("Check verification freshness")
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Return success when no matching verification exists; useful before the first record is created.",
    )
    args = parser.parse_args()
    root = workspace_root(args.root)
    files = changed_files(root)
    fingerprint = fingerprint_files(root, files)
    record = latest_passed_verification(root, fingerprint)

    if record:
        print(f"Fresh verification found: {record.get('command', '<unknown command>')}")
        return 0

    message = (
        "No passed verification record matches the current changed-files fingerprint.\n"
        f"changed_files={len(files)}\n"
        f"changed_files_fingerprint={fingerprint}"
    )
    if args.allow_missing:
        print(message)
        return 0
    print(message, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

