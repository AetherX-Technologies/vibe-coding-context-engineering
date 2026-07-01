# Runbook: Vibe Plugin Installation

## Purpose

Use this runbook to install or refresh the local `vibe-coding` Codex plugin from this repository.

## Local Marketplace

This repository exposes the plugin through:

```text
.agents/plugins/marketplace.json
```

The marketplace name is:

```text
local-vibe-coding
```

The marketplace entry points to:

```text
./plugins/vibe-coding
```

Codex resolves `source.path` relative to the marketplace root. For this repo-scoped marketplace, the plugin source is `plugins/vibe-coding`.

## Preflight

Run from the repository root:

```bash
rtk test python3 scripts/vibe/check_plugin_installation.py --root .
rtk test python3 scripts/vibe/verify_all.py --root . --profile full
```

The check prints the expected install command when marketplace wiring is valid.

## Install Or Reinstall

From a shell where `codex` is available:

```bash
codex plugin add vibe-coding@local-vibe-coding
```

Then restart Codex or start a new thread before testing the plugin. New threads are the safe boundary for loading updated plugin skills and lifecycle configuration.

## Use After Install

In a new Codex thread, invoke the skill explicitly:

```text
Use $vibe-coding-3 to initialize or operate this Vibe Coding B+ workspace.
```

If hooks are shown for review, inspect and trust them through Codex's hook review UI before relying on lifecycle enforcement.

## Update Loop

When plugin files change locally:

1. Run local verification:

   ```bash
   rtk test python3 scripts/vibe/verify_all.py --root . --profile full
   ```

2. Reinstall the plugin from the repo marketplace:

   ```bash
   codex plugin add vibe-coding@local-vibe-coding
   ```

3. Start a new Codex thread for testing.

4. If hook definitions changed, review and trust the updated hooks before relying on them.

## Scaffold Smoke Test

To verify the plugin can install a project-local B+ scaffold:

```bash
rtk proxy rm -rf /tmp/vibe-plugin-scaffold-test
rtk proxy python3 plugins/vibe-coding/skills/vibe-coding-3/scripts/install_project_scripts.py --target /tmp/vibe-plugin-scaffold-test
rtk test python3 /tmp/vibe-plugin-scaffold-test/scripts/vibe/verify_all.py --root /tmp/vibe-plugin-scaffold-test --profile phase1
```

The scaffold check should pass without requiring the repo skill or plugin package in the target project.

## Notes

- Do not use `--record` in CI or plugin installation checks.
- Use `--record` only when intentionally updating local `.context/verification.jsonl` evidence.
- Do not hand-edit marketplace entries during normal update loops; keep marketplace wiring stable and reinstall the plugin from the existing marketplace name.
