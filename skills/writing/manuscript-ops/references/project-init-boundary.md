# Project-init boundary

`manuscript-ops` does not perform generic project bootstrap or invoke another
user-invoked Skill. It hands missing generic bootstrap to `project-init`, then
creates its own manuscript-specific state after the approved Brief.

## Missing initialization

Before a Project route can proceed, verify the exact root has:

- the root mapping and applicable project rules;
- generic `project-init` outputs (`docs/agents/light-project.md`, issue tracker,
  and instruction pointer).

If any required result is missing, report `BLOCKED` at the exact root. State the
missing result and the required initialization outcome, then recommend that the
user explicitly activate `project-init` for that root. Stop. Do not invoke it
automatically or simulate its result. Missing manuscript Profile/state alone
is not a reason to repeat `project-init`.

## Dependency branches

When `project-init` is available, provide the exact user invocation and wait for
its reported initialization outcome before resuming `manuscript-ops`.

When `project-init` is unavailable, keep the manuscript evidence unchanged,
report `BLOCKED`, provide the approved installation method for the dependency,
and state the exact `manuscript-ops resume` point. Do not fall back to
an obsolete repository workflow, a private initializer, or another user-invoked
Skill.

## Resume condition

Resume only after `project-init` reports the exact root mapping and applicable
generic project rules. Re-check those outputs, then, with an approved Brief and
the fixed initialization gate, create or map the manuscript Project Profile,
resumable state, and capability record within `manuscript-ops`.
