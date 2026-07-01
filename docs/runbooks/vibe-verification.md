# Runbook: Vibe Verification

## Manual Verification

Run from workspace root:

```bash
rtk test python3 scripts/vibe/verify_all.py --root . --profile auto
```

For this repository, use the full profile before reporting plugin-ready work or changes to hooks, verifiers, skills, or plugin packaging. It includes repo skill checks, plugin checks, secret scanning, and regression tests:

```bash
rtk test python3 scripts/vibe/verify_all.py --root . --profile full
```

For local completion evidence, record the current changed-files fingerprint:

```bash
rtk test python3 scripts/vibe/verify_all.py --root . --profile full --record
rtk test python3 scripts/vibe/check_verification_freshness.py --root .
```

For a newly scaffolded project that does not yet include repo skills or plugin packaging:

```bash
rtk test python3 scripts/vibe/verify_all.py --root . --profile phase1
```

The legacy individual checks remain useful for isolating failures:

```bash
rtk test python3 scripts/vibe/verify_context_state.py --root .
rtk test python3 scripts/vibe/scan_secrets.py --root .
rtk test python3 scripts/vibe/check_verification_freshness.py --root .
```

## CI Verification

GitHub Actions runs the same full verification bundle in `.github/workflows/vibe-verify.yml`:

```bash
python3 scripts/vibe/verify_all.py --root . --profile full
```

CI must not use `--record`; `.context/verification.jsonl` is local workspace evidence and should only be updated intentionally during a Codex or manual local session.

The repository-local Phase 3 verifier checks the plugin manifest contract that CI needs. A local `plugin-creator` validator may run when available, but CI correctness must not depend on a user-specific skill path.

For local plugin install and update testing, see `docs/runbooks/vibe-plugin-installation.md`.

## If Verification Fails

1. Read the error message.
2. Fix missing scaffold, secret findings, or stale verification evidence.
3. Rerun only the failing command.
4. Append the passed verification record with `scripts/vibe/record_verification.py` or rerun `verify_all.py --record`.
