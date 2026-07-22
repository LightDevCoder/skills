# Evidence Protocol

Evidence must let a later session reopen the verdict without relying on a
Producer narrative. Preserve exact commands or observations, redact secrets,
and retain the original label across every round.

## Evidence labels

Use exactly one primary label for each evidence item:

- `source`: an approved acceptance source or baseline identity.
- `structural`: package, document, path, format, or schema inspection.
- `behavioral`: an executed success, boundary, or failure interaction.
- `installation`: a fresh-install or discovery observation.
- `invocation`: an observed invocation-boundary result.
- `runtime`: an executed representative-environment scenario.
- `manual`: a reproducible human observation that cannot be automated.
- `review`: a Critic, Evaluator, or specialist judgment.

An item may link supporting evidence of another class, but its primary label
must match what was actually observed. A structural or simulated fixture check
does not become behavioral or runtime evidence by relabeling it.

## Producer evidence

Write `producer-evidence.md` with:

```markdown
# Producer Evidence - Round <n>

## Scope
- Charter revision: <n>
- Profile: <name>
- In-scope work: <bounded summary>
- Out-of-scope check: <result>

## Evidence
### E-001 - <short name>
- Evidence label: structural | behavioral | installation | invocation | runtime | manual | review | source
- Run or observation: <exact command or reproducible action>
- Expected: <Charter-backed result>
- Observed: <actual result>
- Outcome: PASS | FAIL | BLOCKED
- Validates: AC-<n> or <none with reason>
- Environment and limitations: <facts>
- Artifact: <path, output, screenshot, or log>
```

State that this is Producer evidence, not final acceptance. Missing evidence is
missing; do not infer a pass.

## Repair evidence

Write `repair-evidence.md` with the confirmed Finding IDs, bounded files or
artifacts changed, focused checks or observations, validation-scenario results,
evidence labels, and remaining limitations. Do not replace the original
candidate, disposition, or Producer evidence.

## Evaluator evidence

Write `evaluator-verdict.md` with:

- context identity and declared independence;
- Charter revision and Profile reviewed;
- criterion-by-criterion judgment with evidence links and labels;
- open findings and approved exceptions;
- `PASS`, `FAIL`, or `BLOCKED`, with concise reason and next action.

Review evidence informs the Core; it is not the frozen acceptance baseline.

## Resume and closeout views

Keep a compact resume snapshot in `state.md`: captured time, goal, Charter
revision, Profile, current round, status, independence, blockers, recent
decisions, open questions, and next action. Keep closeout in `verdict.md` with
the conclusion, completed and unfinished work, risks, linked evidence, and
reopen note. These remain views over the Charter and round records.
