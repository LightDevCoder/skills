# Independent Reviewer Protocol

Use a real independent subagent or fresh isolated context when the platform
supports it. The Core validates findings and records state. The Producer is the
only role permitted to modify the target during a repair.

## Role boundary

- The Critic is read-only. It returns candidate findings and never changes the
  target, the Charter, state, or evidence.
- The Evaluator is read-only. It evaluates the frozen baseline and admissible
  evidence, and never changes the target, the Charter, state, or evidence.
- The Producer supplies evidence and performs only Core-authorized repairs. It
  never issues its own final acceptance verdict.

## Critic packet

Provide only:

- the frozen Charter and selected Profile;
- a bounded view of the target;
- admissible Producer evidence and test or observation entry points where they
  exist;
- requested review dimensions and the finding schema.

Do not include a Producer defense, intended verdict, suspected bug list, or
completion conclusion. Ask for candidate findings without edits.

## Evaluator packet

Provide a different fresh context with:

- the same original Charter and Profile;
- the current bounded target view;
- candidate findings and dispositions;
- repair evidence and current observations;
- the verdict format and relevant acceptance criteria.

Ask the Evaluator to reassess the whole target. It may identify a new gap even
when every Critic candidate was closed.

## Independence declaration

Record one of:

- `independence: full`: Critic and Evaluator ran in separate read-only-capable
  contexts and neither modified the target.
- `independence: degraded`: separate fresh contexts existed but isolation or
  read-only enforcement could not be guaranteed; disclose the limitation.
- `independence: unavailable`: no distinct context was possible. If independent
  evidence is required, return `BLOCKED`; do not role-play an independent
  review in the same context.

Never treat reviewer silence as evidence that a frozen criterion is satisfied.
