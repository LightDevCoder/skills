---
name: clarify
description: Start a lightweight standalone clarification for an ambiguous idea, requirement, plan, or process. Use only when the user explicitly invokes $clarify; it summarizes understanding and unresolved decisions without generating a formal specification or continuing into another workflow.
disable-model-invocation: true
---

# Clarify

`clarify` is a **user-invoked standalone entry** for lightweight
clarification. Run it only after an explicit `$clarify` request. It is useful
when an idea, requirement, brainstorm, plan, or process is still vague and no
formal project context or deliverable is required.

On that explicit request, use the model-invoked `socratic` engine to maintain
a decision-owned clarification state. This is an internal engine use, not a
second user entry point. See [WORKFLOW.md](references/WORKFLOW.md) and
[EXAMPLES.md](references/EXAMPLES.md).

## Composition

```text
clarify → socratic
```

Do not reimplement `socratic`, `research`, `prototype`, or
`to-questionnaire`. `clarify` asks only user-owned frontier decisions; it
leaves fact work as a reported gap. Details in
[ROUTING.md](references/ROUTING.md).

Do not start this Skill from a general vague request and do not automatically
invoke another user-invoked Skill.

## Scope and stopping boundary

Collect only the context needed to identify current understanding and the next
unblocked user decision. Preserve facts supplied by the user; do not ask the
user to decide a fact that can be inspected, researched, or tested. If a fact
is needed, show the fact-finding gap or separately authorized next step that
the engine reports.

After each explicit exchange, return a compact state summary:

```text
Current understanding:
Resolved decisions:
Still unresolved decisions:
Dependencies and fact-finding gaps:
Current question or next step:
```

Then stop for the user. The user may invoke `$clarify` again with an answer.
Do not silently continue a multi-stage workflow, launch research or a
prototype, modify project files, or turn the result into a formal SPEC.

When a different user-invoked Skill would be useful, recommend its explicit
invocation and stop; the user chooses whether to proceed.

## Clarification conduct

- Ask only a current frontier decision, not a fixed questionnaire.
- Keep the user's choices distinct from facts and clearly identify what is
  known, resolved, unknown, or blocked.
- Do not claim external investigation has run unless it actually has.
- Leave the decision with the user; a recommendation may explain a tradeoff
  but must not substitute for the user's choice.

This entry does not create a formal SPEC or claim that clarification is
complete merely because the current frontier is empty.
