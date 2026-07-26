# Workflow recipes

[中文 recipes](../zh-CN/workflows/recipes.md)

These recipes are bounded documentation and validation assets. They describe
explicit handoffs; they do not create a canonical pipeline, permanent state
machine, or automatic multi-Skill orchestrator. `SKILL.md` remains the behavior
authority for every package.

## Source legend and common rule

- **First-party:** `review-loop`, `project-init`, `ask-light`,
  `learn-anything`, and `manuscript-ops` in this repository.
- **Matt upstream:** `to-spec`, `to-tickets`, `implement`, `code-review`,
  `handoff`, `diagnosing-bugs`, `grill-me`, `wayfinder`, and
  `writing-great-skills` from `mattpocock/skills` or a separately visible
  pinned third-party package.
- **Private modified third-party:** a package in `skills-3rdParty`; an absent
  private root is an availability gap, not an invitation to invent a fallback.

Each row declares the handoff artifact and stop condition. `user-invoked` means
the user must explicitly select the Skill; `model-invoked` means the host may
call it under its package policy. Findings from a specialist never become the
final verdict; `review-loop` owns final `PASS`, `FAIL`, or `BLOCKED` whenever a
recipe reaches acceptance.

## 1. Software feature

**Entry condition:** a software feature or implementation goal has a defined
outcome, constraints, and acceptance direction.

| Order | Skill / source | Invocation | Input → output | Handoff / stop |
| --- | --- | --- | --- | --- |
| 1 | `to-spec` / Matt upstream | user-invoked | goal and constraints → traceable specification | Specification artifact; stop for user approval. |
| 2 | `review-loop` / first-party | model-invoked | frozen specification + acceptance source → specification findings/verdict | Review evidence; stop at the review result. |
| 3 | `to-tickets` / Matt upstream | user-invoked | approved specification → dependency-ordered tracer tickets | Ticket graph; do not auto-start implementation. |
| 4 | `implement` / Matt upstream | user-invoked | one unblocked ticket → bounded diff and tests | Commit/implementation evidence; stop at ticket scope. |
| 5 | `code-review` / Matt upstream | model-invoked | fixed diff → Standards/Spec findings | Specialist review; it does not accept the change. |
| 6 | `review-loop` / first-party | model-invoked | implementation, tests, findings → final verdict | Durable verdict; stop at `PASS`, `FAIL`, or `BLOCKED`. |
| 7 | `handoff` / Matt upstream | user-invoked | accepted result or blocker → closeout/resume record | Closeout artifact; user decides whether to resume. |

**Blocked conditions:** missing acceptance authority, unavailable upstream
package, unapproved tickets, unresolved implementation dependencies, or absent
independent evaluator. **Evidence:** specification, ticket graph, commit,
focused tests, specialist findings, review-loop state/verdict, and handoff.

## 2. New project initialization

**Entry condition:** a project needs a minimal confirmed starting point and has
not yet selected a full delivery route.

| Order | Skill / source | Invocation | Input → output | Handoff / stop |
| --- | --- | --- | --- | --- |
| 1 | `ask-light` / first-party | user-invoked | goal, project type, task kind, artifacts, blockers, availability, invocation control → one next Skill or recipe | Recommendation record; stop and wait for user selection. |
| 2 | `project-init` / first-party | user-invoked | confirmed preset + target root → minimal instruction update and validation | Initialization report; stop before discovery/specification/implementation/review. |
| 3 | User-selected next capability | per package policy | confirmed initialized root → next explicit artifact | The user chooses `to-spec`, `manuscript-ops`, `learn-anything`, or `review-loop`; no implicit chain. |

**Blocked conditions:** missing root, ambiguous preset, unconfirmed fallback,
instruction conflict, or unavailable declared capability. **Final authority:**
the user chooses the next Skill; any later acceptance belongs to
`review-loop`.

## 3. Manuscript project

**Entry condition:** a manuscript/manual/book/multilingual project has source,
format, batch, review, or production risk.

| Order | Skill / source | Invocation | Input → output | Handoff / stop |
| --- | --- | --- | --- | --- |
| 1 | `manuscript-ops` / first-party | model-invoked or manual entry | root, six routing dimensions, sources → route and RoutingSnapshot | On Project route, choose one discovery handoff and stop. |
| 2 | `grill-me` or `wayfinder` / Matt upstream | user-invoked | unresolved decisions or multi-session uncertainty → confirmed decisions/map | Return to `manuscript-ops` only after explicit resume. |
| 3 | `project-init` / first-party | user-invoked | approved manuscript brief → mapped minimal project state | Initialization evidence; stop and wait for the next explicit handoff. |
| 4 | `review-loop init` / first-party | model-invoked or manual entry | approved brief + acceptance source → frozen manuscript Charter | Charter/state; no production before approval. |
| 5 | `manuscript-ops resume` / first-party | model-invoked or manual entry | approved Charter + project state → batches, locked source, formats, QA | User-controlled lock/resume boundary. |
| 6 | `review-loop` manuscript Profile / first-party | model-invoked | frozen candidate/final + format QA → final verdict | Stop at `PASS`, `FAIL`, or `BLOCKED`. |

**Blocked conditions:** root/dependency/capability/brief/Charter/rendering or
round-trip evidence missing. **Evidence:** RoutingSnapshot, brief, profile,
source/batch/format records, QA, lock receipt, review-loop state and verdict.

## 4. Source to reusable Skill

**Entry condition:** source material may contain a repeated, evidence-backed
method rather than a one-off event.

| Order | Skill / source | Invocation | Input → output | Handoff / stop |
| --- | --- | --- | --- | --- |
| 1 | `learn-anything` / first-party | user-invoked | source + provenance → internal Method Contract or precise gaps | Stop at `method_contract`, `not_promoted`, or `BLOCKED`. |
| 2 | deterministic package builder / first-party resource | explicit build step after contract | Method Contract → created/updated/no-op/duplicate/blocked package result | Stop on the exact builder state; do not hide duplicate ownership. |
| 3 | `writing-great-skills` / Matt upstream | optional model-invoked knowledge | approved contract → authoring notes | Knowledge only; never a runtime dependency of `learn-anything`. |
| 4 | `review-loop` `agent-skill` Profile / first-party | model-invoked | complete package + admission source → acceptance verdict | Stop at the verdict before admission. |
| 5 | Admission and collection sync / repository governance | explicit maintainer action | accepted package → catalog, tests, release evidence | Stop after fresh install and release gate. |

**Blocked conditions:** missing method fields, unresolved placeholders,
contradictory invocation evidence, unowned duplicate package, missing resource,
or unavailable reviewer. **Final authority:** `review-loop` for package
acceptance; admission governance for collection entry.

## 5. Skill maintenance and release

**Entry condition:** a change request affects a package, script, metadata,
documentation, ownership boundary, or release surface.

| Order | Capability / source | Invocation | Input → output | Handoff / stop |
| --- | --- | --- | --- | --- |
| 1 | Ownership/reuse gate / first-party governance | maintainer decision | request + current package/source → ownership decision | Stop if direct upstream use or `skills-3rdParty` is the correct home. |
| 2 | Bounded implementation / appropriate Skill | explicit by package policy | approved scope → patch, tests, and change record | Stop at the requested scope. |
| 3 | package tests and mutation/negative fixtures | explicit maintainer action | patch → structural/behavioral/invocation evidence | Stop if a required assertion or failure path is absent. |
| 4 | `code-review` / Matt upstream when scripts changed | model-invoked | fixed diff → specialist findings | Findings only; hand to acceptance. |
| 5 | `review-loop` `agent-skill` Profile / first-party | model-invoked | package + acceptance source → verdict | Stop at final verdict. |
| 6 | Collection sync and bilingual documentation | maintainer action | accepted change → catalog/docs/changelog/evidence | Stop when all synchronization records agree. |
| 7 | Fresh whole/per-Skill install and discovery | explicit validation | released tag → install/discovery/smoke evidence | Stop on evidence or `NOT TESTED`; do not overclaim. |
| 8 | Release/tag/closeout | explicit release action | verified evidence → release record and migration state | Final authority is the applicable acceptance gate. |

**Blocked conditions:** ownership ambiguity, failing tests, missing independent
review, unverified install, private dependency not visible, release credential
failure, or stale bilingual/catalog records. Structural tests are not runtime
proof; a source-checkout scan is not fresh-install proof.

## 6. Bug diagnosis and final review

`ask-light workflow` also has bounded recipes for a reproducible bug and a
final acceptance review. The bug route is `diagnosing-bugs` → `implement` →
`code-review` → `review-loop`; the final-review route is a single
`review-loop` step. Both stop at missing reproduction/acceptance authority or
the final `PASS`/`FAIL`/`BLOCKED` verdict and never auto-invoke a user Skill.
