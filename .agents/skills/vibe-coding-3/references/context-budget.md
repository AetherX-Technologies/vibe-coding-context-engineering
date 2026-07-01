# Context Budget Reference

Keep prompt context focused on active work.

## Always Read

For non-trivial implementation:

- `AGENTS.md`
- `docs/PRD.md`
- `docs/acceptance.md`
- `.context/plan.md`
- `.context/state.json`

## Read By Task

- Hook/config work: `CODEX_HOOK_SKILL_GOVERNANCE_PLAN.md`, `.codex/hooks.json`, affected hook scripts, and official Codex docs.
- Security-sensitive work: relevant scripts plus `ecc:security-review`.
- Architecture/process changes: `docs/architecture/INDEX.md` and relevant ADRs.
- Verification work: `docs/runbooks/vibe-verification.md`, `.context/verification.jsonl`, and relevant scratchpad summaries.

## Avoid By Default

- Full scratchpad logs.
- Whole chat exports.
- Generated caches.
- Skill references unrelated to the task.

## Skill Size Rule

Keep `SKILL.md` under 500 lines and move details into one-level `references/` files. Do not duplicate long policy text in both `AGENTS.md` and `SKILL.md`.

