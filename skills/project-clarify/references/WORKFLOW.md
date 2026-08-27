# Project-clarify workflow

Supporting detail for `project-clarify`. The normative contract is
[project-clarification-contract.md](project-clarification-contract.md);
this file summarizes the execution order and references the examples.

## Order

1. **Inspect** — read applicable project facts with paths and locations.
2. **Socratic** — call `socratic` to maintain the frontier; present the
   complete current frontier as a round with numbered questions, choices, and
   recommendations. Accept batch replies.
3. **Fact work (optional)** — `research`/`prototype` only when authorized;
   use `to-questionnaire` as the handoff branch when the missing information is
   held by another person.
4. **Handoff** — return the `Project clarification handoff` and stop.

## Composition

- `project-clarify → socratic` (required)
- optionally `research` / `prototype` per `socratic`'s Unknown routing
- optionally recommend `to-questionnaire` when another person holds the
  blocking information
- large effort may upgrade to `$decision-map`

See [project-clarification-contract.md](project-clarification-contract.md) for
the ledger shape and [EXAMPLES.md](EXAMPLES.md) for handoff examples that
`project-spec` can consume directly without re-inspection.

## Stopping

Return the handoff as an in-memory record. Write to a file only when the user
names a destination and confirms. Recommend the next explicit invocation
(`project-spec`, `decision-map`, or `none`) and stop; do not auto-chain.