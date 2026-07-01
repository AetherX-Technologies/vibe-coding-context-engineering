# PRD: Vibe Coding B+ Phase 1

## Goal

Implement the Phase 1 Vibe Coding B+ minimum loop for this workspace:

- project instructions
- Codex hook configuration
- hook scripts
- deterministic verification scripts
- `.context/` working memory
- `docs/` scaffold
- local verification evidence

## Non-goals

- Do not create a full plugin package in Phase 1.
- Do not create the reusable repo skill in Phase 1.
- Do not assume the workspace is a git repository.

## Users

- A Codex operator using this workspace for long-running AI-assisted development.
- Future agents that need recoverable context, verification gates, and hook-enforced safety.

## Success

- Codex can discover project instructions and hook config.
- Hook scripts parse Codex hook stdin JSON and fail open for unknown events.
- Dangerous Bash commands are denied by `PreToolUse`.
- Secret-like additions are denied for `apply_patch`.
- Stop-phase verification requires current changed-files evidence.
- Local verification scripts pass and append verification evidence.

