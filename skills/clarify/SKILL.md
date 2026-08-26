---
name: clarify
description: Start a lightweight standalone clarification for an ambiguous idea, requirement, plan, or process. Use only when the user explicitly invokes $clarify; it summarizes understanding and unresolved decisions without generating a formal specification or continuing into another workflow.
disable-model-invocation: true
---

# Clarify

`clarify` is a lightweight, user-invoked clarification entry. Run it only
after an explicit `$clarify` request.

## Execution

1. Call the model-invoked `socratic` engine to maintain a decision-owned
   clarification state.
2. Return the compact state summary below.
3. Stop for the user.

If a fact-finding gap blocks the frontier, report the gap and the capability
that would resolve it (`research`, `prototype`, or `to-questionnaire`); do not
invent an answer or turn the gap into a user decision. If another user-invoked
Skill is the better next step, recommend its explicit invocation and stop.

## State summary

```text
Current understanding:
Resolved decisions:
Still unresolved decisions:
Dependencies and fact-finding gaps:
Current question or next step:
```

## Composition

```text
clarify → socratic
```

`clarify` composes `socratic`; it does not reimplement it. Full turn mechanics
are in [WORKFLOW.md](references/WORKFLOW.md); unknown routing is in
[ROUTING.md](references/ROUTING.md); examples are in
[EXAMPLES.md](references/EXAMPLES.md).