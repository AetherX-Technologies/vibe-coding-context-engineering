# Vibe Coding Workflow Project Instructions

## Working Contract

- Treat this repository as a Vibe Coding workflow workspace.
- Use `rtk` for normal shell commands. Use raw shell only when debugging hook behavior or when `rtk` would hide required details; state the reason.
- Keep durable project intent in `docs/`.
- Keep dynamic AI working state in `.context/`.
- Do not put long logs in chat. Write logs over 50 lines to `.context/scratchpads/` and create a paired `.summary.md`.

## Read Contract

Always inspect these before non-trivial implementation:

- `AGENTS.md`
- `docs/PRD.md`
- `docs/acceptance.md`
- `.context/plan.md`
- `.context/state.json`

Read these by task type:

- Architecture or policy change: `docs/architecture/INDEX.md` and relevant ADRs in `docs/decisions/`.
- Hook or Codex config change: `CODEX_HOOK_SKILL_GOVERNANCE_PLAN.md` and official Codex docs via `$openai-docs`.
- Security-sensitive change: use `ecc:security-review`.
- Completion or PR-ready work: use `ecc:verification-loop`.

Avoid reading full scratchpad logs unless the summary is insufficient.

## Planning And State

- Maintain `.context/plan.md` for multi-step work.
- Maintain `.context/state.json` for machine-readable recovery state.
- Update `.context/verification.jsonl` after verification commands.
- Use ADRs for decisions that affect workflow architecture, hook policy, security, or project structure.

## Verification Contract

For workflow scaffold work, minimum local verification is:

```bash
rtk test python3 scripts/vibe/verify_context_state.py --root .
rtk test python3 scripts/vibe/scan_secrets.py --root .
rtk test python3 scripts/vibe/check_verification_freshness.py --root .
```

Completion requires either passing verification evidence in `.context/verification.jsonl` or a concrete blocker explaining why verification cannot run.
