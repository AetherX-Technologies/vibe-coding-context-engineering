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
- [ ] Run verification and security checks.
- [ ] Initialize git and create the public GitHub repository.
- [ ] Push `main` and confirm the GitHub URL.

## Current Task

Running verification and preparing GitHub publication.

## Blockers

None.

## Technical Decisions

- Use MIT license to match the plugin manifest.
- Keep the root README in English and place the Chinese page under `docs/README.zh-CN.md`.
- Keep `.context` as a minimal recoverable state, but ignore scratchpad and checkpoint contents.
- Exclude local chat exports and local code index state from git.

## Verification Commands

```bash
rtk test python3 scripts/vibe/verify_all.py --root . --profile full --record --session-id codex --turn-id open-source-release
rtk test python3 scripts/vibe/check_verification_freshness.py --root .
```

## Outcome

Pending.

## Next Action

Run verification and publish to GitHub after packaging files are in place.
