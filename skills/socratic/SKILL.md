---
name: socratic
description: Maintain a decision-owned clarification state and ask only the currently unblocked user decisions. Use as a model-invoked engine inside a clarification conversation; do not use it to research facts, perform experimental work, or write a formal specification.
---

# Socratic

`socratic` is a **model-invoked Clarification Engine**. It turns an ambiguous
idea, requirement, plan, or process into a small, inspectable decision state.
It is not a user entry point, a fixed questionnaire, an execution workflow, or
a formal SPEC generator.

Use it only when a clarification wrapper (`clarify`, `project-clarify`,
`decision-map`) needs to track user-owned choices. See
[WORKFLOW.md](references/WORKFLOW.md) for the detailed state and turn
procedure and [EXAMPLES.md](references/EXAMPLES.md) for examples.

## Core behavior

- Ask with **dynamic follow-up**: expand along the user's last answer instead
  of stepping through a prewritten questionnaire.
- **Distinguish fact from decision**: user owns outcomes, priorities,
  tradeoffs, and acceptable risk; facts belong to the agent (inspection,
  research, prototype) and are never phrased as a user choice.
- **Continuously converge**: treat each answer as evidence, update
  `current understanding`, mark newly resolved decisions, recompute
  dependencies and the `frontier`, and ask only the currently unblocked
  frontier.

Read [ROUTING.md](references/ROUTING.md) for the Unknown routing contract.

## State to maintain

At each turn, update and return:

- **current understanding** — known goals, constraints, and facts with source
  or uncertainty marker;
- **open decisions** — user-owned choices not yet settled;
- **dependencies** — facts, experiments, or prior choices required before a
  decision can be asked;
- **frontier** — the unblocked open decisions that may be asked now;
- **newly resolved decisions** — choices settled by the latest answer.

Do not repeat a resolved fact or decision. A blocked dependency stays open
and its downstream decision is not part of the frontier.

## Unknown routing

Do not reimplement `research`, `prototype`, or `to-questionnaire`. Declare the
next step and stop:

```text
Unknown
  ├─ user must decide        → socratic (keep in frontier)
  ├─ external fact           → research
  ├─ needs experiment        → prototype
  └─ held by another person  → to-questionnaire
```

If the required capability is not callable, retain the fact as unresolved
and report the missing capability. Do not invent work or convert the
dependency into a user decision. Details in [ROUTING.md](references/ROUTING.md).

## Composition boundary

The engine does not automatically invoke another user-invoked Skill, launch
research/prototype, modify project files, or advance into a formal SPEC.
A calling workflow decides whether to authorize a separate fact-work step.

## Output shape

Return a compact update that keeps the user as final authority:

```text
Current understanding:
Newly resolved decisions:
Open decisions:
Dependencies and fact-finding gaps:
Current frontier:
Question(s) for the user:
Next step: wait for decision | authorize fact work | done
```

An empty frontier is not permission to invent a conclusion. State whether the
blocker is a missing fact, missing capability, or no remaining user decision.
See [WORKFLOW.md](references/WORKFLOW.md) for the full turn procedure.
