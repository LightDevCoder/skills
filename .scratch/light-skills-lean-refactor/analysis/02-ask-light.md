# Ask Light — logic reconstruction

**Real job:** Be the read-only Light Workflow Router: recommend one next first-party Skill or one bounded workflow recipe from current context.

**Entry:** User explicitly invokes `$ask-light` or `$ask-light workflow`.

**Core decision path:** Gather context fields → enumerate real first-party Skills visible on host → read metadata first, shortlist → read only shortlist bodies/references → score against goal/project type/task kind/availability/invocation control → return a single recommendation record.

**Produces:** `RECOMMEND` / `NEED-INPUT` / `BLOCKED` result record; never executes/installs/orchestrates.

**Completion/stop:** After printing the recommendation or boundary result; never auto-chains.

**Every-invocation knowledge:** Invocation boundary, routing map, result contract, where the scanner/contract live.

**Conditional knowledge:** Discovery procedure details, recipe step schemas, and host-install fallback details live in `references/discovery-contract.md` and the PowerShell scanner.

**Duplicates with siblings:** Must not reimplement `clarify`, `project-clarify`, `implement`, `review-loop`, etc.; it only names them when their entry condition fits.

**Negative constraints:** The no-execution boundary is a real product contract (user-invoked read-only router) and stays explicit; other "do not" phrasing around metadata/host validation was condensed into positive rules.
