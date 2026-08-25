---
name: project-spec
description: Turn already-clarified outputs from project-clarify or decision-map into a formal project SPEC without reopening an interview. Use only when the user explicitly invokes $project-spec; it returns to project-clarify when a blocking user decision remains and hands off to project-tickets when ready.
disable-model-invocation: true
---

# Project Spec

`project-spec` is an **explicit, user-invoked planning stage**. Run it only
after an explicit `$project-spec` request. It turns material that clarification
already settled into a formal, bounded SPEC that `project-tickets` can slice.

Read [WORKFLOW.md](references/WORKFLOW.md) before starting a run.
The SPEC shape is in [OUTPUT-FORMAT.md](references/OUTPUT-FORMAT.md);
examples are in [EXAMPLES.md](references/EXAMPLES.md).

Reference baseline: Matt `to-spec` per [ATTRIBUTION.md](ATTRIBUTION.md).
This package adapts that baseline to Light's local tracker and general-purpose
project types (SPEC §7, §15 ADAPT).

## When to use

- A `project-clarify` handoff (`Project clarification handoff`) or a
  `decision-map` map plus resolved ticket answers exists and the way is ready
  for a SPEC.
- The user has explicitly invoked `$project-spec` (with an optional feature
  slug or handoff path).

Do not start this Skill from a general vague request or as an automatic
follow-on to a clarification turn.

## What it consumes — not what it re-asks

- The clarification handoff: `Target and inspected project facts`,
  `Evidence not found`, `Current goal and constraints`, `Resolved user
  decisions`, `Open decisions and dependencies`, `Capability call records`,
  `Current frontier / blocker`, and the recommended invocation.
- For a mapped effort: `.scratch/<effort>/map.md` (`Destination`, `Notes`,
  `Decisions so far`, `Not yet specified`, `Out of scope`) plus the linked
  ticket `## Answer` records.
- The current conversation context as supplemental signal only.

Do not reopen a settled decision as a new interview question. An inspected
fact stays a fact; a user decision already recorded stays recorded.

## Core behavior

1. **Gather and validate** the above material plus a light repo inspection
   (domain glossary, ADRs, existing seams) to ground decisions in real source
   locations — no fabrication when evidence is missing.
2. **Decide whether a SPEC can be written.** If any truly blocking,
   user-owned decision remains without which the SPEC would be speculative,
   stop spec work and return to `project-clarify` with the exact blocker and
   its context pointer — do not invent the answer.
3. **Synthesize a bounded SPEC** using [OUTPUT-FORMAT.md](references/OUTPUT-FORMAT.md):
   sketch the highest feasible seams first (prefer existing seams), then write
   the SPEC, then publish it to the issue tracker's canonical location per
   [docs/agents/issue-tracker.md](../../docs/agents/issue-tracker.md):

   ```text
   .scratch/<feature>/spec.md
   ```

   Confirm the publish with the user when seams affect scoping; see
   [WORKFLOW.md](references/WORKFLOW.md) for the seam-check gate.
4. **Stop and recommend the next explicit invocation.** On success:

   ```text
   project-spec → project-tickets
   ```

   Do not auto-chain. This ticket (08 — Planning) is itself the dog-food
   example of that handoff: the SPEC for `project-spec`/`project-tickets`
   is the input this Skill's successor slices.

## Composition

- `project-spec` does not reimplement `socratic`, `research`, `prototype`, or
  `to-questionnaire`. If it encounters a blocking unknown of those kinds, it
  reports the return to `project-clarify`; `project-clarify` owns the
  capability-call ledger and the decision-map upgrade path.
- `project-spec → project-tickets` is a handoff of the verified SPEC path,
  not an automatic invocation. The hand-off is verifiable: the published
  `spec.md` exists at the stated path and satisfies the template in
  [OUTPUT-FORMAT.md](references/OUTPUT-FORMAT.md).

## Scope and stopping boundary

- Produces one SPEC file and an optional seam note; it does not create
  tickets, execute work, mutate business artifacts, or run a review loop.
- Does not launch research, a prototype, or a questionnaire on its own;
  those belong to the clarification stages it returns to when needed.
- If the handoff recommends `decision-map` (fog beyond a single SPEC),
  recommend explicit `$decision-map` and stop.

See [WORKFLOW.md](references/WORKFLOW.md) for the full step sequence and
[EXAMPLES.md](references/EXAMPLES.md) for dog-food and boundary examples.
