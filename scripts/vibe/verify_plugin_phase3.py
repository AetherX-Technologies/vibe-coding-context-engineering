#!/usr/bin/env python3
"""Verify the local Vibe Coding plugin package satisfies Phase 3 constraints."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


REQUIRED_PLUGIN_FILES = [
    "plugins/vibe-coding/.codex-plugin/plugin.json",
    "plugins/vibe-coding/skills/vibe-coding-3/SKILL.md",
    "plugins/vibe-coding/hooks/hooks.json",
    "plugins/vibe-coding/scaffold/AGENTS.md",
    "plugins/vibe-coding/scaffold/.codex/hooks.json",
    "plugins/vibe-coding/scaffold/.codex/hooks/pre_tool_use_policy.py",
    "plugins/vibe-coding/scaffold/scripts/vibe/policy.py",
    "plugins/vibe-coding/scaffold/scripts/vibe/check_plugin_installation.py",
    "plugins/vibe-coding/scaffold/scripts/vibe/verify_context_state.py",
    "plugins/vibe-coding/scaffold/scripts/vibe/verify_all.py",
    "plugins/vibe-coding/scaffold/docs/PRD.md",
    "plugins/vibe-coding/scaffold/docs/acceptance.md",
    ".agents/plugins/marketplace.json",
]

FORBIDDEN_PLUGIN_PARTS = {
    ".context",
    "__pycache__",
}

INSTALL_SMOKE_REQUIRED_FILES = [
    "AGENTS.md",
    ".codex/hooks.json",
    ".codex/hooks/pre_tool_use_policy.py",
    "scripts/vibe/policy.py",
    "scripts/vibe/check_plugin_installation.py",
    "scripts/vibe/verify_context_state.py",
    "scripts/vibe/verify_all.py",
    "docs/PRD.md",
    ".context/plan.md",
    ".context/state.json",
]

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")

REQUIRED_INTERFACE_STRINGS = [
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
]


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

def verify_install_smoke(plugin_root: Path, errors: list[str]) -> None:
    install_script = plugin_root / "skills/vibe-coding-3/scripts/install_project_scripts.py"
    if not install_script.exists():
        errors.append("Plugin install_project_scripts.py is missing")
        return

    with tempfile.TemporaryDirectory(prefix="vibe-plugin-install-") as tmp:
        target = Path(tmp) / "target"
        result = subprocess.run(
            [sys.executable, str(install_script), "--target", str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append(f"Plugin install smoke failed with exit {result.returncode}: {result.stderr.strip()}")
            return
        if "missing-source" in result.stdout:
            missing = [line for line in result.stdout.splitlines() if line.startswith("missing-source")]
            errors.append("Plugin install smoke reported missing sources: " + ", ".join(missing))
        for rel in INSTALL_SMOKE_REQUIRED_FILES:
            if not (target / rel).exists():
                errors.append(f"Plugin install smoke did not create required file: {rel}")

def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())

def verify_manifest_contract(manifest: dict, errors: list[str]) -> None:
    for field in ["name", "version", "description"]:
        if not non_empty_string(manifest.get(field)):
            errors.append(f"plugin.json {field} must be a non-empty string")
    version = manifest.get("version")
    if isinstance(version, str) and SEMVER_RE.fullmatch(version) is None:
        errors.append("plugin.json version must be strict major.minor.patch semver")

    author = manifest.get("author")
    if not isinstance(author, dict) or not non_empty_string(author.get("name")):
        errors.append("plugin.json author.name must be a non-empty string")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin.json interface must be an object")
        return
    for field in REQUIRED_INTERFACE_STRINGS:
        if not non_empty_string(interface.get(field)):
            errors.append(f"plugin.json interface.{field} must be a non-empty string")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(non_empty_string(value) for value in capabilities):
        errors.append("plugin.json interface.capabilities must be an array of non-empty strings")
    default_prompt = interface.get("defaultPrompt", interface.get("default_prompt"))
    if not isinstance(default_prompt, list) or not all(non_empty_string(value) for value in default_prompt):
        errors.append("plugin.json interface.defaultPrompt must be an array of non-empty strings")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Vibe Coding plugin package")
    parser.add_argument("--root", default=".", help="Workspace root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []

    for rel in REQUIRED_PLUGIN_FILES:
        if not (root / rel).exists():
            errors.append(f"Missing required plugin file: {rel}")

    plugin_root = root / "plugins/vibe-coding"
    manifest_path = plugin_root / ".codex-plugin/plugin.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path, errors)
        if manifest.get("name") != "vibe-coding":
            errors.append("plugin.json name must be vibe-coding")
        verify_manifest_contract(manifest, errors)
        if manifest.get("skills") != "./skills/":
            errors.append("plugin.json skills must point to ./skills/")
        if "hooks" in manifest:
            errors.append("plugin.json must not contain hooks field; use hooks/hooks.json default")
        for forbidden in ["mcpServers", "apps"]:
            if forbidden in manifest:
                errors.append(f"plugin.json must not contain {forbidden} without companion files")

    marketplace_path = root / ".agents/plugins/marketplace.json"
    if marketplace_path.exists():
        marketplace = load_json(marketplace_path, errors)
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list):
            errors.append("marketplace plugins must be a list")
        else:
            match = [item for item in plugins if isinstance(item, dict) and item.get("name") == "vibe-coding"]
            if not match:
                errors.append("marketplace must include vibe-coding entry")
            else:
                entry = match[0]
                source = entry.get("source", {})
                if source.get("path") != "./plugins/vibe-coding":
                    errors.append("marketplace vibe-coding source.path must be ./plugins/vibe-coding")
                policy = entry.get("policy", {})
                if policy.get("installation") != "AVAILABLE" or policy.get("authentication") != "ON_INSTALL":
                    errors.append("marketplace vibe-coding policy must be AVAILABLE / ON_INSTALL")

    hooks_path = plugin_root / "hooks/hooks.json"
    if hooks_path.exists():
        hooks = load_json(hooks_path, errors)
        hooks_text = json.dumps(hooks)
        if ".agents/skills" in hooks_text:
            errors.append("plugin hooks must not call repo skill scripts directly")
        if "plugins/vibe-coding" in hooks_text:
            errors.append("plugin hooks must not hardcode this development plugin path")

    for path in plugin_root.rglob("*"):
        parts = set(path.relative_to(plugin_root).parts)
        if parts & FORBIDDEN_PLUGIN_PARTS:
            errors.append(f"Forbidden generated or dynamic content in plugin: {path.relative_to(root)}")

    skill_md = plugin_root / "skills/vibe-coding-3/SKILL.md"
    if skill_md.exists() and len(skill_md.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append("Plugin SKILL.md must stay under 500 lines")

    if plugin_root.exists():
        verify_install_smoke(plugin_root, errors)

    if errors:
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1

    print("Vibe Coding plugin package verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
