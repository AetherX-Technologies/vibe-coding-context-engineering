# PRD: Vibe Coding Workflow Scaffold

## Goal

Implement the minimum Vibe Coding workflow loop for this workspace:

- project instructions
- Codex hook configuration
- hook scripts
- deterministic verification scripts
- `.context/` working memory
- `docs/` scaffold
- local verification evidence

## Non-goals

- Do not require a full plugin package before the project-local workflow works.
- Do not require the reusable repo skill before the project-local workflow works.
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
