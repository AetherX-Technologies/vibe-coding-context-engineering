# Memory Policy Reference

Use `.context/memory.jsonl` only for concise cross-session project memory.

## Admit

- Workflow decisions that affect future sessions.
- Gotchas that are likely to recur.
- Tooling constraints that future agents must remember.
- Links to ADRs or runbooks.

## Reject

- Ordinary progress updates.
- Full command output.
- Large logs.
- Unverified model assertions.
- Data that belongs in `docs/`, `.context/plan.md`, or `.context/state.json`.

## Format

```json
{"date":"2026-07-01","type":"decision","tags":["#codex","#hooks"],"summary":"Runtime hooks call project-local scripts, not skill scripts.","files":["docs/decisions/0001-adopt-vibe-coding-b-plus.md"]}
```

Memory is a routing aid. ADRs and docs remain the source of truth for stable decisions.

