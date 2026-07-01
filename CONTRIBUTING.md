# Contributing

Thanks for your interest in improving Vibe Coding Context Engineering.

## Development Setup

This repository intentionally has no runtime package dependency for its core checks. Python standard library is enough for the verification scripts and regression tests.

Run the full local gate before opening a pull request:

```bash
python3 scripts/vibe/verify_all.py --root . --profile full
```

If you use RTK:

```bash
rtk test python3 scripts/vibe/verify_all.py --root . --profile full
```

## Pull Request Expectations

- Keep changes scoped to one workflow, script, hook, or documentation concern.
- Update `docs/` for durable behavior changes.
- Update `.context/plan.md` and `.context/state.json` only when working inside this repository's Codex workflow.
- Add or update `tests/vibe/` when changing shared policy or verifier behavior.
- Do not commit local logs, chat exports, generated caches, or secret material.

## Verification Evidence

Local contributors may use `--record` while working:

```bash
python3 scripts/vibe/verify_all.py --root . --profile full --record
```

CI should not use `--record`; it should verify without mutating `.context/verification.jsonl`.

## Security

If you find a security issue in hook policy or secret scanning, do not include sensitive exploit data in a public issue. Open a minimal report first, or contact the maintainer through GitHub.
