# Vibe Coding Context Engineering Release Plan

## Current Goal

Prepare and publish the repository as an open-source GitHub project with an English homepage and a Chinese documentation page.

## Acceptance Criteria

- `README.md` is the English GitHub homepage.
- `docs/README.zh-CN.md` provides a Chinese explanation and quick start.
- Open-source packaging files are present: `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `.gitignore`, and issue templates.
- Local-only exports, caches, scratchpads, and generated files are excluded from git.
- Full local verification and secret scan pass before publishing.
- The repository is initialized, committed, created publicly on GitHub, and pushed to `main`.

## Task List

- [x] Add open-source documentation and packaging files.
- [x] Sanitize public dynamic state and ignore local-only files.
- [x] Run verification and security checks.
- [x] Initialize git and create the public GitHub repository.
- [x] Push `main` and confirm the GitHub URL.

## Current Task

Open-source publication completed.

## Blockers

None.

## Technical Decisions

- Use MIT license to match the plugin manifest.
- Keep the root README in English and place the Chinese page under `docs/README.zh-CN.md`.
- Keep `.context` as a minimal recoverable state, but ignore scratchpad and checkpoint contents.
- Exclude local chat exports and local code index state from git.

## Verification Commands

```bash
rtk test python3 scripts/vibe/verify_all.py --root . --profile full --record --session-id codex --turn-id open-source-release-final
rtk test python3 scripts/vibe/check_verification_freshness.py --root .
```

## Outcome

Published as a public GitHub repository:

```text
https://github.com/AetherX-Technologies/vibe-coding-context-engineering
```

GitHub Actions `Vibe Verify` passed on `main`.

## Next Action

Use issues and pull requests for follow-up changes.

## Follow-Up: Plugin Hook Runtime Update

Goal: publish the updated Vibe Coding plugin hook runtime to GitHub.

Scope:

- Refresh plugin scaffold `PreCompact` behavior to write a fresh minimal auto
  checkpoint whenever base state exists.
- Ignore top-level runtime/cache directories in non-git fallback fingerprints
  while preserving source paths such as `src/**/exports/`.
- Document plugin cache refresh, existing target-project scaffold updates, and
  the current runtime expectations in English and Chinese docs.
- Record ADR-0002 for the hook runtime behavior decision.

Verification:

```bash
rtk ruff check scripts/vibe/policy.py plugins/vibe-coding/scaffold/scripts/vibe/policy.py
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 scripts/vibe/verify_context_state.py --root .
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 scripts/vibe/scan_secrets.py --root .
rtk proxy npx --yes markdown-link-check README.md
rtk proxy npx --yes markdown-link-check docs/README.zh-CN.md
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 scripts/vibe/verify_all.py --root . --profile auto --record --turn-id publish-plugin-hook-runtime-update
rtk test env PYTHONDONTWRITEBYTECODE=1 python3 scripts/vibe/check_verification_freshness.py --root .
```
