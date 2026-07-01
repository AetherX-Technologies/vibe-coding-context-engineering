#!/usr/bin/env python3
"""Scan workspace text files for high-signal secrets."""

from __future__ import annotations

import sys

from policy import build_arg_parser, scan_workspace_for_secrets, workspace_root


def main() -> int:
    parser = build_arg_parser("Scan workspace for high-signal secrets")
    args = parser.parse_args()
    root = workspace_root(args.root)
    findings = scan_workspace_for_secrets(root)
    if findings:
        for finding in findings:
            print(
                f"{finding.path}:{finding.line}: {finding.name}: {finding.text}",
                file=sys.stderr,
            )
        return 1
    print("No high-signal secrets found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

