#!/usr/bin/env python3
"""Install the project-local Vibe Coding workflow scaffold into a target workspace."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]

def resolve_source_root() -> Path:
    candidates = [
        SKILL_ROOT.parents[1] / "scaffold",
        SKILL_ROOT.parents[2] / "scaffold",
        SKILL_ROOT.parents[2],
    ]
    for candidate in candidates:
        if (candidate / "AGENTS.md").exists() and (candidate / ".codex/hooks.json").exists():
            return candidate
    return SKILL_ROOT.parents[2]

SOURCE_ROOT = resolve_source_root()

FILES_TO_COPY = [
    "AGENTS.md",
    ".codex/hooks.json",
    ".codex/hooks/user_prompt_submit_router.py",
    ".codex/hooks/pre_tool_use_policy.py",
    ".codex/hooks/post_tool_use_review.py",
    ".codex/hooks/pre_compact_checkpoint.py",
    ".codex/hooks/stop_verification_gate.py",
    "scripts/vibe/__init__.py",
    "scripts/vibe/policy.py",
    "scripts/vibe/verify_context_state.py",
    "scripts/vibe/scan_secrets.py",
    "scripts/vibe/check_verification_freshness.py",
    "scripts/vibe/check_plugin_installation.py",
    "scripts/vibe/record_verification.py",
    "scripts/vibe/verify_all.py",
    "docs/PRD.md",
    "docs/acceptance.md",
    "docs/architecture/INDEX.md",
    "docs/runbooks/vibe-verification.md",
]

DIRS_TO_CREATE = [
    ".context/scratchpads",
    ".context/checkpoints",
    ".context/agents/handoffs",
    "docs/decisions",
    "docs/runbooks",
]

SEED_FILES = {
    ".context/plan.md": "# Vibe Coding Workflow Plan\n\n## Current Goal\n\nTBD\n",
    ".context/state.json": (
        "{\n"
        '  "current_goal": "TBD",\n'
        '  "phase": "bootstrap",\n'
        '  "active_task": "initialize-vibe-b-plus",\n'
        '  "blocked": false,\n'
        '  "last_green_command": null,\n'
        '  "next_action": "Fill project PRD and acceptance criteria"\n'
        "}\n"
    ),
    ".context/verification.jsonl": "",
    ".context/memory.jsonl": "",
}


def copy_file(rel: str, target_root: Path, force: bool) -> str:
    source = SOURCE_ROOT / rel
    target = target_root / rel
    if not source.exists():
        return f"missing-source {rel}"
    if target.exists() and not force:
        return f"kept-existing {rel}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return f"installed {rel}"


def write_seed(rel: str, content: str, target_root: Path, force: bool) -> str:
    target = target_root / rel
    if target.exists() and not force:
        return f"kept-existing {rel}"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"installed {rel}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Vibe Coding workflow project scaffold")
    parser.add_argument("--target", required=True, help="Target workspace root")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    target_root = Path(args.target).expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    results: list[str] = []
    for rel in DIRS_TO_CREATE:
        (target_root / rel).mkdir(parents=True, exist_ok=True)
        results.append(f"ensured-dir {rel}")
    for rel in FILES_TO_COPY:
        results.append(copy_file(rel, target_root, args.force))
    for rel, content in SEED_FILES.items():
        results.append(write_seed(rel, content, target_root, args.force))

    print("\n".join(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
