# Acceptance Criteria

## Phase 1 Required Artifacts

- `AGENTS.md`
- `.codex/hooks.json`
- `.codex/hooks/*.py`
- `scripts/vibe/*.py`
- `.context/plan.md`
- `.context/state.json`
- `.context/verification.jsonl`
- `.context/scratchpads/`
- `.context/checkpoints/`
- `docs/PRD.md`
- `docs/acceptance.md`
- `docs/architecture/INDEX.md`
- `docs/decisions/`
- `docs/runbooks/`

## Hook Behavior

- `PreToolUse` for Bash denies destructive commands.
- `PreToolUse` for Bash warns or denies ordinary project commands that omit `rtk`, within the boundary defined in `AGENTS.md`.
- `PreToolUse` for `apply_patch` denies high-signal secrets.
- `PostToolUse` records failed verification summaries when possible.
- `PreCompact` blocks when base state is missing and writes a fresh auto
  checkpoint when base state exists.
- `Stop` prevents finalization when changed files lack a matching passed verification fingerprint.

## Verification Behavior

- Verification scripts run without assuming git.
- Verification scripts fail with actionable messages.
- Verification records include `session_id`, `turn_id`, `changed_files`, and `changed_files_fingerprint`.
- Long command output has a `.summary.md` sidecar.
