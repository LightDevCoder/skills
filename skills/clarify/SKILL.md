---
name: clarify
description: Run a lightweight standalone clarification session for an ambiguous idea, requirement, plan, or process. Use only when the user explicitly invokes $clarify to start; normal replies then continue until shared understanding is confirmed, without generating a formal specification or auto-chaining another workflow.
disable-model-invocation: true
---

# Clarify

`clarify` is a lightweight, user-invoked clarification entry. An explicit
`$clarify` starts one session in the current thread. While that session is
active, ordinary user replies continue it; another `$clarify` token is not
required. The session ends after confirmed shared understanding, an explicit
exit, or a switch to another workflow.

## Execution

1. Call the model-invoked `socratic` engine to maintain internal decision state.
2. Present only the engine's conversational projection: brief acknowledgement,
   one useful frontier decision with meaningful options, a recommendation when
   context supports one, and one question.
3. Treat the next normal user message as evidence, call `socratic` again, and
   continue until the completion gate.

If a fact-finding gap blocks the frontier, report the gap and the capability
that would resolve it (`research`, `prototype`, or `to-questionnaire`); do not
invent an answer or turn the gap into a user decision. If another user-invoked
Skill is the better next step, recommend its explicit invocation and stop.

## Completion gate

When no user-owned decision remains and no unresolved dependency blocks the
result, return a concise shared-understanding synthesis and ask the user to
confirm it. A correction reopens the session; confirmation completes it. Then
stop cleanly or recommend one separately invoked next Skill. Do not auto-chain.

## Composition

```text
clarify → socratic
```

`clarify` composes `socratic`; it does not copy the engine's state or unknown
routing contract. Session transitions are specified by
[session_state.py](scripts/session_state.py), full turn mechanics are in
[WORKFLOW.md](references/WORKFLOW.md), and examples are in
[EXAMPLES.md](references/EXAMPLES.md).
