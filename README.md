# Vibe Coding Context Engineering

[中文说明](docs/README.zh-CN.md)

Vibe Coding Context Engineering is a Codex workflow package for building recoverable, verifiable AI-assisted software workspaces. It packages a project-local Vibe Coding workflow as Codex rules, hooks, deterministic verification scripts, a reusable skill, and an installable local plugin.

The goal is simple: keep AI coding fast without losing the engineering controls that make long-running work trustworthy.

## What It Includes

- Project-local `AGENTS.md` guidance for durable workspace rules.
- Codex hooks under `.codex/hooks/` for command policy, stop-time verification, checkpointing, and context routing.
- Verification scripts under `scripts/vibe/` for scaffold checks, secret scanning, plugin checks, freshness checks, and full verification bundles.
- A reusable skill at `.agents/skills/vibe-coding-3/`.
- An installable Codex plugin at `plugins/vibe-coding/`.
- A scaffold template for bootstrapping other projects into the same workflow.
- CI verification through `.github/workflows/vibe-verify.yml`.

## Core Model

The Vibe Coding workflow separates durable project intent from dynamic AI working state:

```text
docs/       stable human-facing design context
.context/   dynamic AI working memory and verification evidence
.codex/     lifecycle hooks and Codex project integration
.agents/    reusable project-local skills and marketplace metadata
plugins/    installable Codex plugin packages
```

The workflow is intentionally layered:

1. Start with project-local rules, hooks, and verification.
2. Extract repeatable behavior into a repo skill.
3. Package the stable pieces as a Codex plugin.

## Quick Start

Clone the repository:

```bash
git clone https://github.com/AetherX-Technologies/vibe-coding-context-engineering.git
cd vibe-coding-context-engineering
```

Run the full local verification bundle:

```bash
python3 scripts/vibe/verify_all.py --root . --profile full
```

If you use RTK in your Codex workspace, the equivalent command is:

```bash
rtk test python3 scripts/vibe/verify_all.py --root . --profile full
```

## Install The Local Codex Plugin

Add this repository as a local Codex plugin marketplace:

```bash
codex plugin marketplace add /absolute/path/to/vibe-coding-context-engineering
```

Install the plugin:

```bash
codex plugin add vibe-coding@local-vibe-coding
```

Refresh an already-installed local copy after changing plugin files:

```bash
codex plugin remove vibe-coding@local-vibe-coding
codex plugin add vibe-coding@local-vibe-coding
```

Start a new Codex thread and invoke the skill:

```text
Use $vibe-coding-3 to initialize or operate this Vibe Coding workflow workspace.
```

See [docs/runbooks/vibe-plugin-installation.md](docs/runbooks/vibe-plugin-installation.md) for reinstall, update, hook review, and smoke-test details.

## Bootstrap Another Project

After installing or cloning this repository, use the skill scaffold installer:

```bash
python3 plugins/vibe-coding/skills/vibe-coding-3/scripts/install_project_scripts.py --target /path/to/target-project
```

Then verify the target project:

```bash
python3 /path/to/target-project/scripts/vibe/verify_all.py --root /path/to/target-project --profile phase1
```

For a target project that already has an older scaffold, update only the
project-local runtime files:

```bash
TARGET=/path/to/target-project
PLUGIN=/Users/blueice/.codex/plugins/cache/local-vibe-coding/vibe-coding/0.1.1/scaffold

mkdir -p "$TARGET/.codex/hooks" "$TARGET/scripts/vibe"
cp "$PLUGIN/.codex/hooks.json" "$TARGET/.codex/hooks.json"
cp "$PLUGIN/.codex/hooks/"*.py "$TARGET/.codex/hooks/"
cp "$PLUGIN/scripts/vibe/"*.py "$TARGET/scripts/vibe/"
```

This does not overwrite the target project's `AGENTS.md`, `docs/`, or
`.context/plan.md`.

## Verification

The main local gate is:

```bash
python3 scripts/vibe/verify_all.py --root . --profile full
```

To record fresh local evidence in `.context/verification.jsonl`:

```bash
python3 scripts/vibe/verify_all.py --root . --profile full --record
python3 scripts/vibe/check_verification_freshness.py --root .
```

CI runs the same verification profile without `--record`.

## Repository Layout

```text
.agents/                  repo-local skills and local marketplace metadata
.codex/                   project-local Codex hook configuration and scripts
.context/                 dynamic AI working state and verification evidence
.github/workflows/        CI verification
docs/                     product, architecture, decision, and runbook docs
plugins/vibe-coding/      installable Codex plugin package
scripts/vibe/             deterministic local verification and policy scripts
tests/vibe/               stdlib regression tests
```

## Status

This project is an early open-source release of a local Codex workflow system. The scripts are intentionally dependency-light and use Python standard library tests. Treat hooks as enforcement aids, not as a replacement for code review and project-specific judgment.

Current scaffold behavior:

- Project hooks resolve scripts with a git-root fallback and skip missing
  project-local hook files instead of failing across unrelated directories.
- Non-git verification fingerprints ignore top-level runtime artifacts such as
  `exports/`, `data/`, `.pytest_cache/`, and `.ruff_cache/`, while keeping
  source paths such as `src/**/exports/`.
- `PreCompact` writes a fresh minimal auto checkpoint from `.context/state.json`
  and latest verification evidence whenever base state exists.

## License

MIT. See [LICENSE](LICENSE).
