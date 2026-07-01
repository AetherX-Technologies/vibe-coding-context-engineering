# Runbook: Vibe Verification

## Manual Verification

Run from workspace root:

```bash
rtk test python3 scripts/vibe/verify_context_state.py --root .
rtk test python3 scripts/vibe/scan_secrets.py --root .
rtk test python3 scripts/vibe/check_verification_freshness.py --root .
```

## If Verification Fails

1. Read the error message.
2. Fix missing scaffold, secret findings, or stale verification evidence.
3. Rerun only the failing command.
4. Append the passed verification record with `scripts/vibe/record_verification.py`.

