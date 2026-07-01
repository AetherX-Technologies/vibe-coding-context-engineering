# Security Policy

This project contains Codex hook policies and verification scripts. Treat hook behavior as a local engineering control, not as a complete sandbox or security boundary.

## Reporting

Please report security-sensitive issues privately through GitHub when available, or open a minimal public issue that does not include secrets, tokens, private paths, or exploit payloads.

## Scope

In scope:

- Hook policy bypasses that allow clearly destructive commands.
- Secret scanning false negatives for common high-signal token formats.
- Plugin packaging behavior that could cause unexpected execution from the plugin cache.
- Documentation that instructs users to run unsafe commands.

Out of scope:

- General Codex product security issues.
- Issues requiring a compromised local machine.
- False positives in intentionally fake examples.
