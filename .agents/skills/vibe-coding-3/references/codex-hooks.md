# Codex Hooks Reference

Use Codex hooks as lifecycle guardrails, not as the only security boundary.

## Locations

Project-local hooks live in:

- `.codex/hooks.json`
- or inline `[hooks]` in `.codex/config.toml`

Prefer `.codex/hooks.json` for this workflow. If both exist in the same layer, Codex merges them and warns.

## Required Events

| Event | Use |
|---|---|
| `UserPromptSubmit` | Add Vibe routing context for implementation, hook, release, or security prompts |
| `PreToolUse` | Deny destructive Bash and high-signal secrets in `apply_patch` |
| `PostToolUse` | Record verification outcomes and feed failures back to the model |
| `PreCompact` | Ensure state and checkpoint evidence exists before compaction |
| `Stop` | Continue the turn when current changes lack fresh passed verification |

## Runtime Rules

- Hook scripts receive one JSON object on stdin.
- Unknown or unsupported events should fail open with diagnostic output, not break normal Codex work.
- `PreToolUse` can deny supported tool calls using `hookSpecificOutput.permissionDecision = "deny"`.
- `PostToolUse` cannot undo side effects; it can only replace feedback to the model.
- `Stop` with `decision: "block"` continues Codex with a new prompt; it does not reject the answer.
- `Stop` must check `stop_hook_active` to avoid continuation loops.
- Hooks can run concurrently, so do not rely on hook ordering.
- Project-local hooks require trust review through `/hooks` before Codex runs them.

## Path Rule

Resolve project hook scripts with git-root fallback:

```bash
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
/usr/bin/python3 "$ROOT/.codex/hooks/pre_tool_use_policy.py"
```

Runtime `.codex/hooks.json` must call project-local scripts, not skill scripts.

