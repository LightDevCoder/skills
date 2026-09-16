# Finding Schema

`review-loop` collects one normalized report per reviewer invocation. This file
is the local shape; it does not replace any richer registry kept by
`project-review`.

## Required fields

Each finding has:

```yaml
id: F-001
state: new | persists | fixed | duplicate
severity: critical | high | medium | low
location: path, section, stable anchor, or "whole target"
problem: concise observable gap
reason: requirement or evidence that makes it a gap
suggestion: optional minimal direction; never an implementation order
```

`id`, `severity`, `location`, `problem`, and `reason` are required; `suggestion`
is optional.

## Identity rules

- Allocate the next unused `F-###` from `Previous findings`; never reuse an ID.
- Reuse an ID when the same gap `persists` after repair.
- Mark `fixed` only when the original gap is absent in the rechecked target.
- Mark `duplicate` and link `duplicate_of: F-###` when a candidate repeats an
  existing canonical concern.

## Clean and error reports

- A clean review writes `Findings: []`.
- A review must not write `PASS`, `FAIL`, or `BLOCKED`; those are final
  acceptance verdicts owned by `project-review`.
- A malformed or mutating report is rejected as `REVIEW-ERROR`. The engine
  stops without a repair.