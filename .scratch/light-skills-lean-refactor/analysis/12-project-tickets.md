# Project Tickets — logic reconstruction

**Real job:** Turn a formal SPEC into tracer-bullet vertical slices with blocking edges and publish them as numbered local-markdown tickets.

**Entry:** User explicitly invokes `$project-tickets` against a SPEC path.

**Core loop:** Verify SPEC handoff → draft vertical slices → quiz user on granularity/blocking → publish one file per ticket under `.scratch/<feature>/issues/` → describe frontier and recommend explicit `$implement`.

**Produces:** Numbered ticket files with `Status`/`Blocked by` ready for the tracker frontier scan.

**Completion/stop:** After publishing ticket set and recommending explicit `$implement`; does not execute tickets.

**Every-invocation knowledge:** SPEC readability bar, vertical-slice sizing, user quiz gate, tracker-native publishing shape.

**Conditional knowledge:** Ticket contract, workflow, examples in references.

**Duplicates:** Delegates execution/review to `implement`, `tdd`, `agent-config`, review family.

**Negative constraints:** Do not fabricate tickets from malformed SPEC and do not auto-invoke implementations are real boundaries.
