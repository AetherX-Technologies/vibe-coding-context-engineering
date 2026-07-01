"""Run the local Vibe Coding verification bundle."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from policy import append_jsonl, changed_files, fingerprint_files, now_iso, workspace_root

BASE_CHECKS = [
    ("context", [sys.executable, "scripts/vibe/verify_context_state.py", "--root", "{root}"]),
    ("secrets", [sys.executable, "scripts/vibe/scan_secrets.py", "--root", "{root}"]),
]

PHASE2_CHECK = ("skill-phase2", [sys.executable, "scripts/vibe/verify_skill_phase2.py", "--root", "{root}"])
PHASE3_CHECK = ("plugin-phase3", [sys.executable, "scripts/vibe/verify_plugin_phase3.py", "--root", "{root}"])
PLUGIN_INSTALL_CHECK = ("plugin-installation", [sys.executable, "scripts/vibe/check_plugin_installation.py", "--root", "{root}"])
REGRESSION_CHECK = ("regression-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests/vibe", "-p", "test_*.py"])
DEFAULT_PLUGIN_VALIDATOR = Path.home() / ".codex/skills/.system/plugin-creator/scripts/validate_plugin.py"

def command_for(raw: list[str], root: Path) -> list[str]:
    return [part.format(root=str(root)) for part in raw]

def run_check(name: str, command: list[str], cwd: Path) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    status = "PASS" if result.returncode == 0 else "FAIL"
    print(f"[{status}] {name}")
    if output:
        print(output)
    return result.returncode == 0, output

def record_bundle(root: Path, summary: str, session_id: str, turn_id: str, profile: str) -> str:
    files = changed_files(root)
    fingerprint = fingerprint_files(root, files)
    append_jsonl(
        root / ".context/verification.jsonl",
        {
            "time": now_iso(),
            "session_id": session_id,
            "turn_id": turn_id,
            "command": f"python3 scripts/vibe/verify_all.py --root . --profile {profile} --record",
            "status": "passed",
            "changed_files": files,
            "changed_files_fingerprint": fingerprint,
            "summary": summary,
        },
    )
    return fingerprint

def has_phase2(root: Path) -> bool:
    return (root / ".agents/skills/vibe-coding-3/SKILL.md").exists()

def has_phase3(root: Path) -> bool:
    return (root / "plugins/vibe-coding/.codex-plugin/plugin.json").exists()

def build_checks(root: Path, profile: str, plugin_validator: Path | None) -> list[tuple[str, list[str]]]:
    checks = list(BASE_CHECKS)
    if profile == "full" or (profile == "auto" and has_phase2(root)):
        checks.append(PHASE2_CHECK)
    if profile == "full" or (profile == "auto" and has_phase3(root)):
        checks.append(PHASE3_CHECK)
        checks.append(PLUGIN_INSTALL_CHECK)
        if plugin_validator is not None and plugin_validator.exists():
            checks.append(("plugin-creator", [sys.executable, str(plugin_validator), "plugins/vibe-coding"]))
        else:
            print("[SKIP] plugin-creator validator unavailable")
    if profile == "full" and (root / "tests").exists():
        checks.append(REGRESSION_CHECK)
    return checks

def main() -> int:
    parser = argparse.ArgumentParser(description="Run all local Vibe Coding verification checks")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument(
        "--profile",
        choices=["auto", "phase1", "full"],
        default="auto",
        help="Verification profile. auto runs checks for detected local capabilities.",
    )
    parser.add_argument("--record", action="store_true", help="Record a passed verification bundle")
    parser.add_argument("--session-id", default="codex", help="Verification record session id")
    parser.add_argument("--turn-id", default="verify-all", help="Verification record turn id")
    parser.add_argument("--plugin-validator", default=None, help="Optional plugin-creator validator path")
    args = parser.parse_args()

    root = workspace_root(args.root)
    plugin_validator = Path(args.plugin_validator).expanduser() if args.plugin_validator else DEFAULT_PLUGIN_VALIDATOR
    checks = build_checks(root, args.profile, plugin_validator)

    failures: list[str] = []
    for name, raw_command in checks:
        ok, _output = run_check(name, command_for(raw_command, root), root)
        if not ok:
            failures.append(name)

    if failures:
        print("Verification bundle failed: " + ", ".join(failures), file=sys.stderr)
        return 1

    if args.record:
        fingerprint = record_bundle(
            root,
            "Vibe Coding verification bundle passed.",
            args.session_id,
            args.turn_id,
            args.profile,
        )
        print(f"Recorded verification: {fingerprint}")

    print("Vibe Coding verification bundle passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
