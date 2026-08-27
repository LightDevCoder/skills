---
name: socratic
description: Maintain a decision-owned clarification state and ask the current actionable frontier as a round of independent questions with choices and recommendations. Use as a model-invoked engine inside a clarification conversation; do not use it to research facts, perform experimental work, or write a formal specification.
---

# Socratic

`socratic` is a model-invoked Clarification Engine for user-owned decisions.
Use it when a clarification wrapper (`clarify`, `project-clarify`,
`decision-map`) needs to track a conversation.

## Core loop

1. Receive the latest answer as evidence.
2. Update `current understanding`.
3. Mark newly resolved decisions.
4. Recompute dependencies and the **frontier**: every meaningful user decision
   whose prerequisites are already settled.
5. Ask the complete actionable frontier as a round, not one question at a time.
6. Return internal state plus a conversational projection to the calling
   wrapper.

Each round normally contains multiple independent questions when multiple
frontier decisions exist. Number them (`Q1`, `Q2`, ...). Provide concrete
options when decisions can reasonably be discretized, and include a
recommendation when evidence supports one; the user owns the decision and may
always answer outside the listed choices. Accept a compact batch reply
(`1B, 2A, 3C`), mixed free text, or normal prose, and mark only the answered
questions resolved.

Facts are not user decisions: inspectable, researchable, or testable gaps are
dependencies, not choices for the user to invent.

## Internal state

Maintain these fields for the calling wrapper; do not dump them to the user by
default:

```text
Current understanding:
Newly resolved decisions:
Open decisions:
Dependencies and fact-finding gaps:
Current frontier:
Next step: ask-round | wait for decision | authorize fact work | synthesize
```

A blocked dependency keeps its downstream decision out of the frontier. An
empty frontier states whether the blocker is a missing fact, a missing
capability, or no remaining user decision; it never justifies inventing a
conclusion.

## Conversational projection

A normal user-facing turn contains a brief acknowledgement and the current
frontier round: numbered questions, meaningful options/tradeoffs, and a
recommendation for each question when evidence supports one. Expose the
detailed state only when it resolves ambiguity, the user asks for it, or
`decision-map` needs durable state.

When no decision or dependency remains, return a concise synthesis for shared-
understanding confirmation. `confirmed` means done; a correction updates state
and recomputes the frontier.

The machine-readable helper in [frontier.py](scripts/frontier.py) models
frontier computation, batch parsing, and next-step classification for tests
and deterministic checks.

## Unknown routing

Declare the next capability; the calling wrapper decides whether to pause for
authorization or continue the clarification session.

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
[EXAMPLES.md](references/EXAMPLES.md). The behavior fields used by executable
contract tests are in
[conversation-contract.json](references/conversation-contract.json).