---
name: vibe-coding-3
description: Initialize or operate a Vibe Coding B+ software workspace with repo-local AGENTS.md guidance, Codex hooks, project-local verification scripts, filesystem context, scratchpad log masking, ADR capture, and context-budget discipline. Use when setting up or maintaining Codex project rules, AI coding workflow scaffolds, Vibe Coding B+ Phase 1/2 workflows, or reusable context-engineering conventions; do not use for one-off code edits that do not need persistent workflow state.
---

# Vibe Coding 3

Use this skill to initialize, inspect, or operate a Vibe Coding B+ workspace. Keep the runtime project-local: hooks call project `scripts/vibe/*`, while this skill provides reusable workflow guidance and installation helpers.

## Operating Flow

1. Inspect project instructions, requirements, acceptance criteria, and current plan/state files before non-trivial implementation.
2. Keep stable human intent in project docs; keep dynamic AI working state in the project context directory.
3. Use Codex hooks for lifecycle guardrails, but keep hard policy in project-local scripts.
4. Record verification evidence with a changed-files fingerprint.
5. Capture workflow-shaping decisions in ADRs under `docs/decisions/`.
6. Run project verification before reporting completion.

## Reference Routing

- For Codex hook event behavior, trust, matcher limits, and runtime boundaries, read `references/codex-hooks.md`.
- For gate sequencing and completion criteria, read `references/gates.md`.
- For always-read versus task-specific context, read `references/context-budget.md`.
- For project memory admission rules, read `references/memory-policy.md`.
- For scratchpad and summary handling, read `references/observation-masking.md`.
- For decision capture rules, read `references/adr-policy.md`.

## Script Routing

- Use `scripts/install_project_scripts.py` to install or refresh a project-local B+ scaffold in a target workspace.
- Use `scripts/generate_project_hooks.py` to print canonical `.codex/hooks.json` for a target workspace.
- Do not configure `.codex/hooks.json` to call skill scripts directly. Runtime hooks must call project-local `.codex/hooks/*.py` and `scripts/vibe/*.py`.

## Verification

After changing a B+ workspace, run:

```bash
rtk test python3 scripts/vibe/verify_context_state.py --root .
rtk test python3 scripts/vibe/scan_secrets.py --root .
rtk test python3 scripts/vibe/check_verification_freshness.py --root .
```

For this skill itself, also verify that `SKILL.md` has only `name` and `description` frontmatter, stays under 500 lines, and does not include project-specific context state.
