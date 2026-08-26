---
name: socratic
description: Maintain a decision-owned clarification state and ask only the currently unblocked user decisions. Use as a model-invoked engine inside a clarification conversation; do not use it to research facts, perform experimental work, or write a formal specification.
---

# Socratic

`socratic` is a model-invoked Clarification Engine for user-owned decisions.
Use it when a clarification wrapper (`clarify`, `project-clarify`,
`decision-map`) needs to track a conversation.

## Core loop

1. Receive the latest answer as evidence.
2. Update `current understanding`.
3. Mark newly resolved decisions.
4. Recompute dependencies and the frontier.
5. Ask only the currently unblocked frontier decisions.
6. Return the state update and stop.

Ask with dynamic follow-up, never a fixed questionnaire. Facts are not user
decisions: inspectable, researchable, or testable gaps are dependencies, not
choices for the user to invent.

## State fields

Return after every turn:

```text
Current understanding:
Newly resolved decisions:
Open decisions:
Dependencies and fact-finding gaps:
Current frontier:
Question(s) for the user:
Next step: wait for decision | authorize fact work | done
```

A blocked dependency keeps its downstream decision out of the frontier. An
empty frontier states whether the blocker is a missing fact, a missing
capability, or no remaining user decision; it never justifies inventing a
conclusion.

## Unknown routing

Declare the next capability and stop; the calling wrapper authorizes execution.

```text
user must decide       → socratic (keep in frontier)
external fact          → research
needs experiment       → prototype
held by another person → to-questionnaire
```

If the required capability is not callable, retain the fact as unresolved and
report the missing capability. Full turn procedure and routing details are in
[WORKFLOW.md](references/WORKFLOW.md) and
[ROUTING.md](references/ROUTING.md); examples are in
[EXAMPLES.md](references/EXAMPLES.md).