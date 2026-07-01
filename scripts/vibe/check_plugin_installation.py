"""Check local Codex plugin marketplace wiring for Vibe Coding."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLUGIN_NAME = "vibe-coding"
EXPECTED_PLUGIN_PATH = "./plugins/vibe-coding"

def load_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path} is not valid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path} must contain a JSON object")
        return {}
    return value

def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())

def main() -> int:
    parser = argparse.ArgumentParser(description="Check Vibe Coding local plugin installation wiring")
    parser.add_argument("--root", default=".", help="Workspace root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []

    marketplace_path = root / ".agents/plugins/marketplace.json"
    marketplace = load_json(marketplace_path, errors) if marketplace_path.exists() else {}
    if not marketplace_path.exists():
        errors.append("Missing .agents/plugins/marketplace.json")

    marketplace_name = marketplace.get("name")
    if not non_empty_string(marketplace_name):
        errors.append("marketplace name must be a non-empty string")

    plugins = marketplace.get("plugins")
    entry = None
    if not isinstance(plugins, list):
        errors.append("marketplace plugins must be a list")
    else:
        matches = [item for item in plugins if isinstance(item, dict) and item.get("name") == PLUGIN_NAME]
        if len(matches) != 1:
            errors.append("marketplace must contain exactly one vibe-coding plugin entry")
        else:
            entry = matches[0]

    if entry is not None:
        source = entry.get("source")
        if not isinstance(source, dict):
            errors.append("vibe-coding marketplace source must be an object")
        else:
            if source.get("source") != "local":
                errors.append("vibe-coding marketplace source.source must be local")
            if source.get("path") != EXPECTED_PLUGIN_PATH:
                errors.append(f"vibe-coding marketplace source.path must be {EXPECTED_PLUGIN_PATH}")
        policy = entry.get("policy")
        if not isinstance(policy, dict):
            errors.append("vibe-coding marketplace policy must be an object")
        else:
            if policy.get("installation") != "AVAILABLE":
                errors.append("vibe-coding marketplace policy.installation must be AVAILABLE")
            if policy.get("authentication") != "ON_INSTALL":
                errors.append("vibe-coding marketplace policy.authentication must be ON_INSTALL")
        if entry.get("category") != "Productivity":
            errors.append("vibe-coding marketplace category must be Productivity")

    plugin_root = root / "plugins/vibe-coding"
    manifest_path = plugin_root / ".codex-plugin/plugin.json"
    manifest = load_json(manifest_path, errors) if manifest_path.exists() else {}
    if not manifest_path.exists():
        errors.append("Missing plugins/vibe-coding/.codex-plugin/plugin.json")
    if manifest.get("name") != PLUGIN_NAME:
        errors.append("plugin manifest name must be vibe-coding")

    required_paths = [
        plugin_root / "skills/vibe-coding-3/SKILL.md",
        plugin_root / "hooks/hooks.json",
        plugin_root / "scaffold/AGENTS.md",
        plugin_root / "scaffold/scripts/vibe/verify_all.py",
    ]
    for path in required_paths:
        if not path.exists():
            errors.append(f"Missing plugin artifact: {path.relative_to(root)}")

    if errors:
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1

    print("Vibe Coding plugin marketplace wiring verified.")
    print(f"Install command: codex plugin add {PLUGIN_NAME}@{marketplace_name}")
    print("After reinstall, start a new Codex thread to load updated plugin skills and hooks.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
