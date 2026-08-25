# Project-spec output format

The SPEC `project-spec` publishes is a bounded, verifiable artifact that
`project-tickets` consumes directly. Adapt the upstream `to-spec` template to
Light's tracker location and general-purpose project types.

## Publish location

```text
.scratch/<feature>/spec.md
```

`<feature>` is the confirmed feature slug (from the invoke argument, the map's
`<effort>`, or the goal-derived slug). The file is the canonical handoff to
`project-tickets`; do not write the SPEC elsewhere to satisfy this Skill.

## Required sections

Use these headings in order. Keep each section bounded prose, not a code
dump. Use the project's domain glossary and respect ADRs; note the ADR path
when a decision follows or deliberately departs from one.

```markdown
# SPEC — <Feature title>

## Problem Statement

The problem from the user's perspective — who is affected, what is currently
costly or impossible, and why the current workaround is insufficient. Ground
in the inspected project facts when they exist; cite the fact locator rather
than restating a claim without evidence.

## Solution

The solution from the user's perspective — what becomes possible after this
feature lands, described as observable capability. Keep this free of
implementation layer ordering; the layering belongs below.

## User Stories

An extensive, numbered list. Each story is:

1. As a <actor>, I want <capability> so that <benefit>

Cover the feature broadly: happy path, important boundaries, and failure
behaviour worth guaranteeing. For a non-product deliverable (Skill, document
set, configuration), the "actor" may be the agent host, the operator, or the
reviewer — keep the actor/benefit shape.

## Implementation Decisions

The settled architectural and interface choices. Include only decisions the
clarification material actually settled, plus the seam sketch from WORKFLOW
step 3. Typical entries:

- modules or contexts to build or modify;
- interfaces or contracts to add, change, or leave intact;
- technical clarifications and ADR references with path;
- schema/API/contract changes;
- interaction and ownership boundaries between capabilities.

Do not list specific file paths or code snippets — they go stale. Exception:
when a prototype snippet encodes a decision more precisely than prose can
(state machine, reducer, schema, type shape), inline the trimmed,
decision-rich fragment and note that it came from a prototype.

## Testing / Verification Decisions

What makes verification credible for this SPEC:

- what counts as a good test for this feature (observe external behaviour,
  not implementation prose);
- which modules, seams, or verification boundaries are exercised;
- prior art in the repo that the tests or checks should follow;
- for non-code deliverables, the manual or automated verification that will
  be run (template renders, script checks, composition probes, review packets).

## Out of Scope

In-scope-looking items explicitly deferred, with the reason for deferral
(risk, ordering, separate feature, requires new research/prototype).

## Further Notes

Any residual notes, evidence gaps, or non-blocking dependencies worth
preserving. If a fact remains unresolved but does not block the SPEC, note it
here with the evidence gap and the next fact-work step (`research` /
`prototype`) without converting it into a user question.
```

## Vocabulary and evidence rules

- Use domain-glossary terms consistently; when the glossary defines a term,
  use that term.
- Every non-trivial claim about prior project state should carry its
  locator (`README.md#Heading`, `docs/adr/NNN.md`, `spec.md` path, ticket
  `## Answer` link). An absent locator is an evidence gap, not an implicit
  truth.
- Do not reintroduce a question the clarification material already settled;
  if the material left a decision open, that openness is preserved in
  `Further Notes` or `Out of Scope`, not resolved by invention.
- Keep the SPEC readable by a reviewer who has not seen the full
  clarification thread; the thread supplied it, but the SPEC restates what
  the reviewer needs.

## Seam note

The seam sketch is part of `Implementation Decisions` and may also be
summarized in a short preamble when the seam implies a scope choice. One
high seam is ideal; more seams are justified only when they isolate distinct
verification boundaries.

## Verifiable handoff to project-tickets

The published `spec.md` satisfying this template at the stated path is the
verifiable handoff token for `project-tickets`. `project-tickets` validates
that token by reading the file at that path; a missing or malformed SPEC is
treated as a handoff gap, not a prompt to fabricate tickets.
