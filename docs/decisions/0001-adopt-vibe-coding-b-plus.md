# ADR-0001: Adopt a Project-Local Workflow Scaffold Before Plugin Packaging

Note: "B+" was the internal planning label for the project-local workflow scaffold: repo instructions, Codex hooks, deterministic verification scripts, and filesystem working state before broad plugin distribution.

**Date**: 2026-07-01  
**Status**: accepted  
**Deciders**: project owner, Codex

## Context

The workspace needs Codex hooks, project instructions, deterministic verification, and filesystem context before it can be packaged for reuse. A pure skill would be too soft to enforce safety and verification. A full plugin would freeze rules before the local workflow has proven stable.

## Decision

Adopt the project-local Vibe Coding workflow scaffold as the first implementation target: repo-local `AGENTS.md`, `.codex/hooks.json`, hook scripts, `scripts/vibe` verification tools, `.context`, and `docs`.

## Alternatives Considered

### Pure Skill

- **Pros**: Easy to reuse across projects.
- **Cons**: Cannot provide hard runtime gates by itself.
- **Why not**: The goal requires Codex hooks and local verification evidence.

### Immediate Plugin

- **Pros**: Best eventual distribution unit.
- **Cons**: Premature packaging and hook trust complexity.
- **Why not**: Phase 1 rules need local validation first.

## Consequences

### Positive

- Fast local feedback.
- Clear separation between project state and reusable method.
- Plugin remains available as Phase 3 after the workflow stabilizes.

### Negative

- Some files will need later extraction into a reusable skill/plugin.
- Local hooks must be trusted in Codex before they run.

### Risks

- Hook coverage is incomplete; mitigate with deterministic scripts and later CI/git hooks.
