# Unknown routing

`socratic` does not execute fact work. It only declares the routing and
preserves the blocking relationship.

## Routing table

```text
Unknown
  ├─ user must decide        → socratic
  │     The choice requires judgment about outcome, priority, tradeoff, or risk.
  │     Keep it in open decisions and, when unblocked, in the frontier.
  │
  ├─ external fact           → research
  │     Primary-source knowledge outside the current working root: official
  │     docs, specs, APIs, papers. Fact-finding step, not a user question.
  │
  ├─ needs experiment        → prototype
  │     A cheap, throwaway experiment distinguishes the alternatives (state
  │     model, behavior, UI variation). Non-production, discarded after learning.
  │
  └─ held by another person  → to-questionnaire
        │  Knowledge the current user does not hold and cannot decide alone.
        │  Capture as a questionnaire for the holder to fill in.
```

## Rules

- Do not reimplement any of `research`/`prototype`/`to-questionnaire`.
- Record the blocked decision, the question, and the chosen capability.
- If the capability is not callable or not authorized, retain the fact as
  `unresolved` and report `missing capability: <name>`; do not invent an
  answer or convert the dependency into a user decision.
- A missing fact-finding capability keeps its downstream decision out of the
  frontier.
- Do not claim a call has `started` or `completed` unless it actually has.

Cross-reference: `clarify`, `project-clarify`, and `decision-map` all call
`socratic` for user-owned decisions and optionally invoke `research`/
`prototype`/`to-questionnaire` per this table.

