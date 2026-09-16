# Project-init boundary

`manuscript-ops` does not initialize a project and does not invoke another
user-invoked Skill. It detects the initialization precondition and hands the
user to `project-init`.

## Missing initialization

Before a Project route can proceed, verify the exact root has:

- the root mapping and applicable project rules;
- a Project Profile with explicit value origins; and
- resumable manuscript state, including the required paths and capabilities.

If any required result is missing, report `BLOCKED` at the exact root. State the
missing result and the required initialization outcome, then recommend that the
user explicitly activate `project-init` for that root. Stop. Do not invoke it
automatically, write the initialization, or simulate its result.

## Dependency branches

When `project-init` is available, provide the exact user invocation and wait for
its reported initialization outcome before resuming `manuscript-ops`.

When `project-init` is unavailable, keep the manuscript evidence unchanged,
report `BLOCKED`, provide the approved installation method for the dependency,
and state the exact `manuscript-ops resume` point. Do not fall back to
an obsolete repository workflow, a private initializer, or another user-invoked
Skill.

## Resume condition

Resume only after the user has activated `project-init` and it has reported the
exact root mapping, applicable project rules, Project Profile, resumable
manuscript state, and capability-availability result. Re-check those outputs,
then continue at the fixed initialization gate.
