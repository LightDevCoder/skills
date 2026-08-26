# Review Loop — logic reconstruction

**Real job:** Drive the lightweight `review → findings → repair → re-review` engine to convergence; it is not the final acceptance owner.

**Entry:** Model-invoked (or manual) when a caller has a bounded packet and a concrete repair path.

**Core loop:** Resolve reviewer (`generic-review` default, `code-review` for software diff, accepted domain reviewer) → invoke with four-field packet → collect normalized findings → return confirmed in-scope findings to Producer → re-run with same reviewer until `Findings: []` or configured limit (default 3).

**Produces:** Clean findings handoff or outstanding findings at limit; never `PASS`/`FAIL`/`BLOCKED`.

**Completion/stop:** Clean or limit; then hand to caller; if final acceptance needed recommend `project-review`.

**Every-invocation knowledge:** Loop shape, reviewer resolution, four-field packet, no-verdict boundary.

**Conditional knowledge:** Reviewer contract and finding schema in references.

**Duplicates:** Does not re-document `generic-review`/`code-review` methods or `project-review` verdict ownership.
