# ADR-0002: Refresh Project-Local Hook Runtime Behavior

**Date**: 2026-07-09  
**Status**: accepted  
**Deciders**: project owner, Codex

## Context

The Vibe Coding plugin distributes project-local hooks and verification scripts
into target repositories. Two operational issues showed up in non-git or
already-scaffolded target projects:

- Verification fingerprints included top-level runtime artifacts such as
  `exports/` and cache directories, causing Stop hooks to request fresh
  verification after routine report generation.
- `PreCompact` only checked for any checkpoint, so an old checkpoint could
  remain while `.context/state.json` had moved on.

Existing scaffold files also live inside target projects after installation.
Reinstalling the plugin updates Codex's plugin cache, but it does not mutate
previously copied target-project hook files.

## Decision

Update the plugin scaffold and project-local runtime so that:

- Non-git fallback fingerprints ignore only top-level runtime/cache directories:
  `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `data/`, `exports/`, and
  `htmlcov/`.
- Source paths with the same names, such as `src/**/exports/`, remain tracked.
- `.env` and `.env.*` files are ignored except `.env.example`.
- `PreCompact` blocks only when base state files are missing.
- When base state exists, `PreCompact` writes a fresh minimal auto checkpoint
  derived from `.context/state.json` and the latest verification record.
- The installation docs explicitly distinguish plugin cache refresh from
  updating an existing target project's copied scaffold.

## Alternatives Considered

### Keep Runtime Artifacts In Fingerprints

- **Pros**: Every generated report change can force verification.
- **Cons**: Non-git projects become noisy and Stop hooks block after routine
  local output generation.
- **Rejected**: Runtime artifacts should be verified by explicit commands, not
  treated as durable source changes in non-git fallback fingerprints.

### Ignore Any Directory Named `exports`

- **Pros**: Simpler implementation.
- **Cons**: Would accidentally ignore source packages such as
  `src/promo_monitor/exports/`.
- **Rejected**: Ignore only top-level runtime directories.

### Require Manual Checkpoints Only

- **Pros**: Human-authored checkpoints can be richer.
- **Cons**: Existing checkpoint presence can mask stale recovery state.
- **Rejected**: The hook can safely write a small mechanically derived
  checkpoint without treating the transcript as a source of truth.

## Consequences

### Positive

- Existing non-git target projects get less Stop-hook noise.
- Compact/resume recovery has a fresher minimal checkpoint.
- Plugin update instructions are clearer for already-scaffolded projects.

### Negative

- Runtime artifacts under top-level `exports/` no longer affect the fallback
  changed-files fingerprint.
- Existing target projects still need an explicit scaffold runtime update if
  they copied older hook files.

### Follow-Up

If this plugin is later versioned beyond `0.1.1`, add a migration helper that
updates only project-local hook/runtime files and preserves target-specific
docs and context.
