# Project Spec — logic reconstruction

**Real job:** Turn already-clarified material (project-clarify handoff or decision-map map + answers) into a formal bounded SPEC for `project-tickets`.

**Entry:** User explicitly invokes `$project-spec` with a handoff path or feature slug.

**Core loop:** Gather/validate clarification material → decide if a SPEC can be written (blocking user decision?) → synthesize bounded SPEC using output format → publish to `.scratch/<feature>/spec.md` → recommend `$project-tickets`.

**Produces:** One SPEC file at the canonical tracker location.

**Completion/stop:** After publish and recommending explicit `$project-tickets`; does not auto-chain or create tickets.

**Every-invocation knowledge:** Consume handoff, don't reopen decisions, output path, handoff to project-tickets.

**Conditional knowledge:** Output format, workflow, examples in references.

**Duplicates:** Delegates to `project-clarify`/`decision-map` for unresolved decisions and to `project-tickets` for slicing.

**Negative constraints:** Do not reopen settled decisions, do not auto-chain, do not launch research/prototype are real boundaries.
