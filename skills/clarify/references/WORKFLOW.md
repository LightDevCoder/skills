# Clarify workflow

Supporting detail for `clarify`. `SKILL.md` is the entry; this file holds the
full step description.

## Entry condition

- User explicitly invokes `$clarify` with an idea, requirement, brainstorm
  topic, plan, or vague request.
- No project context is required. The thread is standalone.

Do not start `clarify` from a general vague prompt — wait for the explicit
`$clarify` token.

## Steps

1. Collect the minimal context the user supplied (goal, constraints, initial
   vague request).
2. Call `socratic` (model-invoked) with that context. Let it separate known
   facts, user-owned open decisions, dependencies, and the current frontier.
3. Present the conversational projection from `socratic`: acknowledge what the
   latest answer settled, show one frontier decision and its real tradeoffs,
   include a recommendation when evidence supports judgment, then ask one
   question.
4. Keep the session active. Feed the next ordinary user reply back to
   `socratic`, recompute the frontier, and present the next useful turn.
5. When the engine reports no open decision or dependency, synthesize the
   shared understanding and ask for confirmation. Confirmation ends the
   session; a correction updates state and continues.

## Boundaries

- No formal SPEC or tickets are produced.
- No project files are written.
- No automatic chaining to another user-invoked Skill. If `project-clarify`,
  `research`, `prototype`, or `to-questionnaire` would be useful, recommend
  the explicit invocation and stop.
- Fact work is reported using `socratic`'s routing result and is not executed
  unless the user separately authorizes it.

## Handoff options

- If the clarified thread now has enough context to become a project stage,
  recommend `$project-clarify` and stop.
- If the user wants a questionnaire for another person, recommend
  `$to-questionnaire` and stop.
- Otherwise the user replies normally until the synthesis is confirmed or the
  frontier is blocked.
