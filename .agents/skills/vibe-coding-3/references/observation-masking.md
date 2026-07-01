# Observation Masking Reference

Keep long observations out of the main conversation.

## Rule

If command output exceeds 50 lines, write the full output to `.context/scratchpads/` and create a paired `.summary.md`.

## Naming

```text
test-YYYY-MM-DD-HHMM-topic.log
test-YYYY-MM-DD-HHMM-topic.summary.md
```

## Summary Contents

- Command
- Status
- Key failures
- Suspected cause
- Next action
- Path to full output

The conversation should use the summary, not the full log, unless debugging requires exact output.

