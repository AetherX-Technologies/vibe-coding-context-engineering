# Gates Reference

Use gates to keep agentic development recoverable and auditable.

## Gate Order

| Gate | Required Evidence |
|---|---|
| Pre-flight | Required docs and `.context` files exist; verification commands are known |
| Plan | `.context/plan.md` has goal, acceptance criteria, tasks, and verification commands |
| Implementation | Scope is limited to relevant files; tests or checks are planned |
| Verification | Commands pass or blocker is recorded; `.context/verification.jsonl` is updated |
| Review | Security and quality risks checked when hooks, scripts, or workflow policy changes |
| Commit/Completion | Diff reviewed, ADR updated if needed, no stale verification fingerprint |

## Verification Record

Every passed verification record should include:

```json
{
  "time": "2026-07-01T16:40:00+08:00",
  "session_id": "manual-or-codex-session",
  "turn_id": "manual-or-codex-turn",
  "command": "python3 scripts/vibe/scan_secrets.py --root .",
  "status": "passed",
  "changed_files": ["AGENTS.md"],
  "changed_files_fingerprint": "sha256:...",
  "summary": "No high-signal secrets found"
}
```

Stop-phase gates should accept only passed records that match the current changed-files fingerprint.

