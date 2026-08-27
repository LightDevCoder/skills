# Workflow recipes

[中文 recipes](../../docs/zh-CN/workflows/recipes.md)

These recipes are bounded documentation and validation assets. They describe explicit handoffs; they do not create a canonical pipeline, permanent state machine, or automatic multi-Skill orchestrator. `SKILL.md` remains the behavior authority for every package.

## Source legend and common rule

- **First-party (33):** all Skills in this repository — `project-init`, `project-clarify`, `project-spec`, `project-tickets`, `implement`, `project-review`, `release-workflow`, `socratic`, `clarify`, `decision-map`, `research`, `prototype`, `to-questionnaire`, `agent-config`, `tdd`, `diagnosing-bugs`, `resolving-merge-conflicts`, `review-loop`, `generic-review`, `code-review`, `handoff`, `wizard`, `wait-what`, `writing-for-agents`, `teach`, `eli5`, `language-learning`, `recap`, `learn-anything`, `manuscript-ops`, `kb-init`, `kanban-worker`, `ask-light` — installed via `LightDevCoder/skills` (see [CATALOG.md](../../CATALOG.md)).
- **Approved PORTs:** `research`, `prototype`, `tdd`, `handoff`, `diagnosing-bugs`, `wizard`, `teach`, `wait-what`, `to-questionnaire`, `writing-for-agents`, `resolving-merge-conflicts` are self-contained first-party packages with `ATTRIBUTION.md` and no upstream runtime dependency (Port preserves Matt behavior; Light changes are handoff/decoupling only).
- **Historical Matt names:** `grill-me` → `clarify`, `grilling` → `socratic`, `grill-with-docs` → `project-clarify`, `wayfinder` → `decision-map`, `to-spec` → `project-spec`, `to-tickets` → `project-tickets` — used only for attribution; the Light names above are the canonical workflow steps.
- **Private modified third-party:** a package in `skills-3rdParty`; an absent private root is an availability gap, not an invitation to invent a fallback.

`socratic` is the model-invoked engine; `clarify` is the user-facing lightweight entry, `project-clarify` the project-aware entry, and `decision-map` the large-effort map. Treat `clarify → socratic`, `project-clarify → socratic`, `decision-map → socratic` as composition, not separate steps.

Each row declares the handoff artifact and stop condition. `user-invoked` means the user must explicitly select the Skill; `model-invoked` means the host may call it under its package policy. Findings from a specialist never become the final verdict; `project-review` (via `review-loop`) owns final `PASS`, `FAIL`, or `BLOCKED` whenever a recipe reaches acceptance.

## 1. Software feature

**Entry condition:** a software feature or implementation goal has a defined outcome, constraints, and acceptance direction.

| Order | Skill | Invocation | Input → output | Handoff / stop |
| --- | --- | --- | --- | --- |
| 1 | `project-spec` | user-invoked | goal, constraints + clarified decisions → traceable SPEC | SPEC artifact; stop for user approval. |
| 2 | `project-review` (spec) | model-invoked via `review-loop` + `generic-review` | frozen SPEC + acceptance source → findings / verdict | Review evidence; stop at result. |
| 3 | `project-tickets` | user-invoked | approved SPEC → dependency-ordered tracer tickets | Ticket graph; do not auto-start `implement`. |
| 4 | `implement` | user-invoked | one unblocked ticket → bounded diff + tests | Commit evidence; stop at ticket scope. |
| 5 | `code-review` | model-invoked | fixed diff → Standards/Spec findings | Specialist review; it does not accept the change. |
| 6 | `project-review` | model-invoked via `review-loop` + `code-review`/`generic-review` | implementation + tests + findings → final verdict | Durable `PASS`/`FAIL`/`BLOCKED`; stop. |
| 7 | `handoff` | user-invoked | accepted result or blocker → closeout/resume record | Closeout artifact; user decides whether to resume. |

**Blocked conditions:** missing acceptance authority, unapproved tickets, unresolved dependencies, or absent independent evaluator. **Evidence:** SPEC, ticket graph, commit, focused tests, specialist findings, `project-review`/`review-loop` state/verdict, and `handoff`.

## 2. New project initialization

**Entry condition:** a project needs a minimal confirmed starting point and has not yet selected a full delivery route.

| Order | Skill | Invocation | Input → output | Handoff / stop |
| --- | --- | --- | --- | --- |
| 1 | `ask-light` | user-invoked | goal, project type, task kind, artifacts, blockers, availability, invocation control → one next Skill or recipe | Recommendation; wait for user approval, then honor invocation policy (model-invoked may begin; user-invoked target is rendered as the next explicit invocation). |
| 2 | `project-init` | user-invoked | confirmed preset + target root → minimal instruction update and validation | Initialization report; stop before clarification/spec/implementation/review. |
| 3 | User-selected next capability | per package policy | confirmed initialized root → next explicit artifact | The user chooses `project-clarify`, `project-spec`, `manuscript-ops`, `learn-anything`, or `project-review`; no implicit chain. |

**Blocked conditions:** missing root, ambiguous preset, unconfirmed fallback, instruction conflict, or unavailable capability. **Final authority:** the user chooses the next Skill; later acceptance belongs to `project-review`.

## 3. Manuscript project

**Entry condition:** a manuscript/manual/book/multilingual project has source, format, batch, review, or production risk.

| Order | Skill | Invocation | Input → output | Handoff / stop |
| --- | --- | --- | --- | --- |
| 1 | `manuscript-ops` | model-invoked or manual entry | root, six routing dimensions, sources → route and RoutingSnapshot | On Project route, choose one discovery handoff and stop. |
| 2 | `socratic` engine via `clarify` or `decision-map` | user-invoked entries | unresolved decisions or multi-session uncertainty → confirmed decisions/map | Return to `manuscript-ops` only after explicit resume. |
| 3 | `project-init` | user-invoked | approved manuscript brief → mapped minimal project state | Initialization evidence; stop and wait. |
| 4 | `project-review init` | model-invoked or manual entry | approved brief + acceptance source → frozen Charter | Charter/state; no production before approval. |
| 5 | `manuscript-ops resume` | model-invoked or manual entry | approved Charter + project state → batches, locked source, formats, QA | User-controlled lock/resume boundary. |
| 6 | `project-review` (manuscript Profile) | model-invoked via `review-loop` | frozen candidate/final + format QA → final verdict | Stop at `PASS`/`FAIL`/`BLOCKED`. |

**Blocked conditions:** root/dependency/capability/brief/Charter/rendering or round-trip evidence missing. **Evidence:** RoutingSnapshot, brief, profile, source/batch/format records, QA, lock receipt, `project-review`/`review-loop` state and verdict.

## 4. Source to reusable Skill

**Entry condition:** source material may contain a repeated, evidence-backed method rather than a one-off event.

| Order | Skill | Invocation | Input → output | Handoff / stop |
| --- | --- | --- | --- | --- |
| 1 | `learn-anything` | user-invoked | source + provenance → internal Method Contract or precise gaps | Stop at `method_contract`, `not_promoted`, or `BLOCKED`. |
| 2 | deterministic package builder | explicit build step after contract | Method Contract → created/updated/no-op/duplicate/blocked | Stop on exact builder state; do not hide duplicate ownership. |
| 3 | `writing-for-agents` | optional model-invoked knowledge | approved contract → authoring notes | Knowledge only; never a runtime dependency. |
| 4 | `project-review` (via `review-loop`) | model-invoked | complete package + admission source → acceptance verdict | Stop at verdict before admission. |
| 5 | Admission and collection sync | explicit maintainer action | accepted package → catalog, tests, release evidence | Stop after fresh install and release gate. |

**Blocked conditions:** missing method fields, unresolved placeholders, contradictory invocation evidence, unowned duplicate package, missing resource, or unavailable reviewer. **Final authority:** `project-review` for package acceptance; admission governance for collection entry.

## 5. Skill maintenance and release

See [docs/MAINTENANCE.md](../../docs/MAINTENANCE.md) and [docs/REVIEW_POLICY.md](../../docs/REVIEW_POLICY.md): ownership/reuse gate → bounded implementation → tests + adversarial fixtures → `code-review` when scripts changed → `project-review` verdict → collection sync → fresh install/discovery → release/tag/closeout.

## 6. Bug diagnosis and final review

`ask-light workflow` also has bounded recipes for a reproducible bug and a final acceptance review. The bug route is `diagnosing-bugs` → `implement` → `code-review` → `project-review` (via `review-loop`); the final-review route is a single `project-review` step. Both stop at missing reproduction/acceptance authority or the final `PASS`/`FAIL`/`BLOCKED` and never auto-invoke a user Skill.

## 7. Standalone session recap

`recap` is a one-step, user-invoked stopping boundary. The user explicitly selects `$recap`; it consumes only current session context, emits exactly one line, invokes nothing else, and stops. It does not create a handoff, compact history, continue execution, or issue a review verdict.
