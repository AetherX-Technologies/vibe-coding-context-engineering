#!/usr/bin/env python3
"""Verify the Vibe Coding 3 repo skill satisfies Phase 2 constraints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_REFERENCES = [
    "codex-hooks.md",
    "gates.md",
    "context-budget.md",
    "memory-policy.md",
    "observation-masking.md",
    "adr-policy.md",
]

REQUIRED_SKILL_SCRIPTS = [
    "generate_project_hooks.py",
    "install_project_scripts.py",
]


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter must end with ---")
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, body


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Vibe Coding 3 repo skill")
    parser.add_argument("--root", default=".", help="Workspace root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    skill = root / ".agents/skills/vibe-coding-3"
    errors: list[str] = []

    skill_md = skill / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing .agents/skills/vibe-coding-3/SKILL.md")
    else:
        text = skill_md.read_text(encoding="utf-8")
        try:
            frontmatter, _body = parse_frontmatter(text)
        except ValueError as exc:
            errors.append(str(exc))
            frontmatter = {}
        keys = set(frontmatter)
        if keys != {"name", "description"}:
            errors.append(f"SKILL.md frontmatter must contain only name and description, got {sorted(keys)}")
        if frontmatter.get("name") != "vibe-coding-3":
            errors.append("SKILL.md name must be vibe-coding-3")
        description = frontmatter.get("description", "")
        if "$vibe-coding-3" in description:
            errors.append("Description should describe trigger behavior, not include invocation syntax")
        if not all(term in description.lower() for term in ["vibe coding", "codex", "hooks"]):
            errors.append("Description must clearly trigger for Vibe Coding Codex hooks workflows")
        line_count = len(text.splitlines())
        if line_count > 500:
            errors.append(f"SKILL.md must stay under 500 lines, got {line_count}")
        if ".context/state.json" in text or ".context/verification.jsonl" in text:
            errors.append("SKILL.md should not embed project .context state details")

    references_dir = skill / "references"
    for name in REQUIRED_REFERENCES:
        path = references_dir / name
        if not path.exists():
            errors.append(f"Missing reference: {name}")
        elif len(path.read_text(encoding="utf-8").splitlines()) > 160:
            errors.append(f"Reference is too large for focused loading: {name}")

    scripts_dir = skill / "scripts"
    for name in REQUIRED_SKILL_SCRIPTS:
        path = scripts_dir / name
        if not path.exists():
            errors.append(f"Missing skill script: {name}")
        elif not path.read_text(encoding="utf-8", errors="replace").startswith("#!/usr/bin/env python3"):
            errors.append(f"Skill script must start with python3 shebang: {name}")

    hooks_json = root / ".codex/hooks.json"
    if hooks_json.exists():
        try:
            hooks = json.loads(hooks_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f".codex/hooks.json invalid JSON: {exc}")
            hooks = {}
        hooks_text = json.dumps(hooks)
        if ".agents/skills/vibe-coding-3/scripts" in hooks_text:
            errors.append(".codex/hooks.json must not call skill scripts directly")

    for path in skill.rglob("*"):
        rel = path.relative_to(skill).as_posix()
        if rel.startswith(".context/"):
            errors.append("Skill must not contain project .context state")
            break

    if errors:
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1

    print("Vibe Coding 3 repo skill verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

