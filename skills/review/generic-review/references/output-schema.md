# Generic Review Output Schema

Return exactly one Markdown report. It is a candidate-finding report, never a
final verdict.

```markdown
# Generic Review Report

- Target: <immutable identity>
- Reviewed requirements: <approved source or criterion IDs>
- Read-only: true
- Result: findings | no-findings | review-error

## Findings
- id: F-001
  state: new | persists | fixed | duplicate
  severity: critical | high | medium | low
  location: <path, section, stable anchor, or whole target>
  problem: <concise observable gap>
  reason: <requirement or evidence>
  suggestion: <optional narrow direction>
  duplicate_of: <F-###; required only for duplicate>
```

For a complete first review with no candidates, write `Findings: []` instead
of the Findings list. For a recheck, retain a row for every checked prior ID so
`fixed`, `persists`, and `duplicate` are visible. A `fixed` row repeats the
original problem and reason so the recheck remains auditable.

## Field rules

- `id`, `state`, `severity`, `location`, `problem`, and `reason` are required
  in each finding. `suggestion` is optional.
- `id` is `F-###`. Reuse a supplied ID for the same concern. For a new concern,
  assign the next unused number after all supplied previous IDs; never recycle
  a retired ID.
- `location` must identify a reviewable part of the target or say `whole
  target`; it cannot point to the Producer or an imagined file.
- `problem` states the observed gap. `reason` identifies the supplied
  requirement or evidence, not an unstated rule.
- `duplicate_of` is required and must name a different supplied canonical ID
  when `state: duplicate`; a duplicate creates no separate repair path.

## Invalid result

If the packet is incomplete, the target is unreadable, or the proposed output
would write or direct a change, return:

```markdown
# Generic Review Report

- Read-only: true
- Result: review-error
- Error: <missing input, malformed field, or prohibited mutation>
```

Do not include `PASS`, `FAIL`, `BLOCKED`, target edits, repair instructions, or
an ungrounded finding in an invalid result.
