# Architecture Index

## Vibe Coding Workflow Runtime

The runtime is project-local:

- `AGENTS.md` provides durable project instructions.
- `.codex/hooks.json` binds Codex lifecycle events to project hook scripts.
- `.codex/hooks/*.py` parses hook stdin JSON and enforces local policy.
- `scripts/vibe/*.py` contains deterministic checks shared by hooks and manual verification.
- `.context/` stores dynamic working memory and verification evidence.
- `docs/` stores stable intent, acceptance criteria, ADRs, runbooks, and gotchas.

## Boundary

Hooks do not provide a complete security boundary. They are guardrails around supported Codex lifecycle events. Critical checks should also exist as scripts and, later, CI/git hooks when this workspace becomes a git repository.

## Decisions

- [ADR-0001: Adopt a Project-Local Workflow Scaffold Before Plugin Packaging](../decisions/0001-adopt-vibe-coding-b-plus.md)
- [ADR-0002: Refresh Project-Local Hook Runtime Behavior](../decisions/0002-refresh-project-local-hook-runtime.md)

## References

- [CODEX_HOOK_SKILL_GOVERNANCE_PLAN.md](../../CODEX_HOOK_SKILL_GOVERNANCE_PLAN.md)
- [AGENTS.md](../../AGENTS.md)
