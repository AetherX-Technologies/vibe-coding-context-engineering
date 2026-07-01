#!/usr/bin/env python3
"""Shared policy helpers for Vibe Coding workflow hooks and verifiers."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


IGNORED_DIRS = {
    ".git",
    ".cocoindex_code",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
}

IGNORED_FILE_PATTERNS = [
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.pdf",
    "*.zip",
    "*.gz",
    "*.tar",
    "*.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
]

FINGERPRINT_IGNORED_PREFIXES = (
    ".context/verification.jsonl",
    ".context/scratchpads/",
    ".context/checkpoints/",
)

REQUIRED_PATHS = [
    "AGENTS.md",
    ".codex/hooks.json",
    ".codex/hooks/pre_tool_use_policy.py",
    ".codex/hooks/post_tool_use_review.py",
    ".codex/hooks/pre_compact_checkpoint.py",
    ".codex/hooks/stop_verification_gate.py",
    "scripts/vibe/policy.py",
    "scripts/vibe/verify_context_state.py",
    "scripts/vibe/scan_secrets.py",
    "scripts/vibe/check_verification_freshness.py",
    "scripts/vibe/check_plugin_installation.py",
    "scripts/vibe/record_verification.py",
    "scripts/vibe/verify_all.py",
    ".context/plan.md",
    ".context/state.json",
    ".context/verification.jsonl",
    ".context/scratchpads",
    ".context/checkpoints",
    "docs/PRD.md",
    "docs/acceptance.md",
    "docs/architecture/INDEX.md",
    "docs/decisions",
    "docs/runbooks",
]

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("OpenAI key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("GitHub classic token", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("GitHub fine-grained token", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key block", re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|PRIVATE) KEY-----")),
    (
        "generic credential assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|secret|password|token)\b\s*[:=]\s*['\"][^'\"]{12,}['\"]"
        ),
    ),
]

DESTRUCTIVE_COMMAND_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("remove root", re.compile(r"\brm\s+-[^\n;]*r[^\n;]*f[^\n;]*(?:/|\$HOME|~)(?:\s|$)")),
    ("git hard reset", re.compile(r"\bgit\s+reset\s+--hard\b")),
    ("git checkout all", re.compile(r"\bgit\s+checkout\s+--\s+\.")),
    ("world-writable chmod", re.compile(r"\bchmod\s+(?:-R\s+)?777\b")),
    ("pipe to shell", re.compile(r"\b(?:curl|wget)\b[^\n|;]*\|\s*(?:sh|bash|zsh)\b")),
    ("disk formatting", re.compile(r"\b(?:mkfs|dd\s+if=)\b")),
]


@dataclass(frozen=True)
class Finding:
    name: str
    path: str
    line: int
    text: str


def workspace_root(value: str | None = None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            text=True,
            capture_output=True,
        )
        return Path(result.stdout.strip()).resolve()
    except Exception:
        return Path.cwd().resolve()


def load_hook_event() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        event = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid hook JSON on stdin: {exc}") from exc
    if not isinstance(event, dict):
        raise SystemExit("Hook stdin JSON must be an object")
    return event


def emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def deny_pre_tool(reason: str) -> None:
    emit_json(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )


def context_for(event_name: str, message: str) -> None:
    emit_json(
        {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": message,
            }
        }
    )


def stop_continue(reason: str) -> None:
    emit_json({"decision": "block", "reason": reason})


def common_success(message: str | None = None) -> None:
    if message:
        emit_json({"systemMessage": message})


def command_from_event(event: dict[str, Any]) -> str:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command")
    return command if isinstance(command, str) else ""


def normalize_wrapped_command(command: str) -> str:
    match = re.match(r"^\s*(?:sh|bash|zsh)\s+-lc\s+(['\"])(.*)\1\s*$", command, re.DOTALL)
    if match:
        return match.group(2)
    return command


def bash_policy(command: str) -> tuple[str, str]:
    normalized = normalize_wrapped_command(command)
    for name, pattern in DESTRUCTIVE_COMMAND_PATTERNS:
        if pattern.search(normalized):
            return "deny", f"Destructive command blocked ({name}): {command}"

    stripped = normalized.strip()
    if not stripped:
        return "allow", ""

    allowed_prefixes = (
        "rtk ",
        "python3 .codex/hooks/",
        "python3 scripts/vibe/",
        "/usr/bin/python3 ",
        "mkdir ",
    )
    if stripped.startswith(allowed_prefixes):
        return "allow", ""

    if stripped.startswith(("git ", "ls", "pwd", "cat ", "sed ", "rg ", "find ")):
        return "warn", "Normal project shell commands should use the `rtk` prefix in this workspace."

    return "warn", "Consider using `rtk` for normal shell commands in this workspace."


def is_ignored_path(path: Path) -> bool:
    parts = set(path.parts)
    if parts & IGNORED_DIRS:
        return True
    name = path.name
    return any(fnmatch.fnmatch(name, pattern) for pattern in IGNORED_FILE_PATTERNS)


def is_probably_text(path: Path) -> bool:
    try:
        data = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\x00" not in data


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if is_ignored_path(rel):
            continue
        if is_probably_text(path):
            yield path


def allowlisted_secret(path: Path, line_text: str) -> bool:
    normalized = path.as_posix()
    if "# vibe-allow-secret-example" in line_text:
        return True
    if normalized.startswith(("tests/fixtures/", "docs/examples/")):
        return "example" in line_text.lower() or "fake" in line_text.lower()
    return False


def scan_text_for_secrets(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    rel_path = Path(path)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if allowlisted_secret(rel_path, line):
            continue
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(name, path, line_no, line.strip()[:220]))
    return findings


def scan_workspace_for_secrets(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        findings.extend(scan_text_for_secrets(rel, text))
    return findings


def changed_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            check=True,
            text=True,
            capture_output=True,
        )
        files: list[str] = []
        for line in result.stdout.splitlines():
            if len(line) < 4:
                continue
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path and not is_ignored_path(Path(path)) and not fingerprint_ignored(path):
                files.append(path)
        return sorted(set(files))
    except Exception:
        files = []
        for path in iter_text_files(root):
            rel = path.relative_to(root).as_posix()
            if fingerprint_ignored(rel):
                continue
            files.append(rel)
        return sorted(files)


def fingerprint_ignored(rel: str) -> bool:
    return any(rel == prefix or rel.startswith(prefix) for prefix in FINGERPRINT_IGNORED_PREFIXES)


def fingerprint_files(root: Path, files: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for rel in sorted(set(files)):
        path = root / rel
        digest.update(rel.encode("utf-8"))
        if path.exists() and path.is_file():
            digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii"))
            try:
                digest.update(str(path.stat().st_mtime_ns).encode("ascii"))
            except OSError:
                pass
        else:
            digest.update(b"<missing>")
    return "sha256:" + digest.hexdigest()


def verification_records(root: Path) -> list[dict[str, Any]]:
    path = root / ".context/verification.jsonl"
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            records.append(item)
    return records


def latest_passed_verification(root: Path, fingerprint: str) -> dict[str, Any] | None:
    for record in reversed(verification_records(root)):
        if record.get("status") == "passed" and record.get("changed_files_fingerprint") == fingerprint:
            return record
    return None


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def write_summary(root: Path, name: str, lines: list[str]) -> str:
    scratch = root / ".context/scratchpads"
    scratch.mkdir(parents=True, exist_ok=True)
    path = scratch / name
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path.relative_to(root).as_posix()


def require_paths(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def executable_script(path: Path) -> bool:
    return path.exists() and path.is_file()


def build_arg_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--root", default=".", help="Workspace root")
    return parser
