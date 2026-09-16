# Historical migration — review-loop → project-review

This provenance record is not required for current `project-review` execution.

This file records the provenance and mapping for the `review-loop` →
`project-review` split (SPEC §9 / §15 / §25 Phase 7, Ticket 11).

## Provenance

- **Source package:** `skills/review-loop` at baseline commit `26110c9`
  (LightDevCoder/skills, main) and its heavy final-acceptance semantics
  (`init`/`review`/`resume`, frozen baseline/Charter, evidence protocol,
  finding registry, `PASS`/`FAIL`/`BLOCKED`, scope-change boundary, Profile
  selection, durable `.review-loop/` state, `code-review` specialist
  boundary).
- **Target package:** `skills/project-review` — new Light capability
  (`NEW / MIGRATE LOGIC` per SPEC §16).
- **Retained package:** `skills/review-loop` — refactored to lightweight
  Review Engine (`REFACTOR + SPLIT` per SPEC §16).
- **Reviewer contract:** `docs/REVIEWER_CONTRACT.md` introduced in
  Ticket 10 (baseline-check) as the lightweight packet/normalized-finding
  contract for all reviewers. It is a documentation surface, not a runtime
  dependency of `generic-review` or `code-review`.

## Decision

Do not delete already-validated final-acceptance capability and rewrite from
scratch. Migrate the mature `review-loop` acceptance logic to
`project-review` verbatim where it remains correct, then rewire its reviewer
invocation to use the new lightweight `review-loop` engine and the shared
`REVIEWER_CONTRACT`.

```
Light review-loop (heavy, final-acceptance + loop)
  ──► project-review (frozen baseline, PASS/FAIL/BLOCKED, scope gate — migrated)
  ──► review-loop (lightweight engine: resolve→invoke→receive→return repair→re-run)
  ──► generic-review (default reviewer, 5 checks, read-only)
  ──► code-review (specialist, still read-only, invoked via review-loop)
```

## Mapping

| Concern | Former location (`review-loop`) | New location | Change scope |
| --- | --- | --- | --- |
| Final-acceptance ownership | `SKILL.md` owned `PASS`/`FAIL`/`BLOCKED` | `project-review/SKILL.md` owns `PASS`/`FAIL`/`BLOCKED` | Move ownership; `review-loop` now owns only `Findings: []` / `REVIEW-ERROR` convergence and handoff |
| Frozen baseline / Charter | `SKILL.md#init`, `references/acceptance-charter.md`, `state.md#charter` | `project-review/SKILL.md#init`, `references/acceptance-charter.md` | Identical content, new canonical directory `.project-review/` (fallback `.review-loop/` for compatibility) |
| Evidence labels & records | `references/evidence-protocol.md` | `references/evidence-protocol.md` | Identical |
| Finding identity & registry | `references/finding-schema.md` | `references/finding-schema.md` | Identical; lightweight `F-###` contract in `REVIEWER_CONTRACT.md` is compatible, not a replacement |
| Stopping rules, verdicts, 3-round limit, scope-expansion stop | `references/stopping-rules.md`, `SKILL.md#Verdicts and limits` | `references/stopping-rules.md`, `SKILL.md#Verdicts and limits` | Identical |
| Critic/Evaluator read-only, independence | `references/subagent-protocol.md` | `references/subagent-protocol.md` | Identical; reviewers now also conform to `REVIEWER_CONTRACT.md` |
| Review rubric, severity | `references/review-rubric.md` | `references/review-rubric.md` | Identical |
| Profiles (generic, software, manuscript, agent-skill, specification) | `references/profiles/*` | `references/profiles/*` | Identical |
| Mission Center compatibility | `references/mission-center-compatibility.md` | `references/mission-center-compatibility.md` | Identical |
| Code-review specialist boundary | `SKILL.md#Software specialist boundary` (direct invoke) | `SKILL.md` via `review-loop` engine → `code-review` | Indirection added; `code-review` remains read-only, no loop, no final verdict — boundary verifiable |
| Generic reviewer | (none — ad-hoc Critic) | `skills/generic-review/` (default, 5 checks) | New; `code-review` was already read-only, generic path was implicit |
| Convergence loop | Embedded in `review` workflow steps 2–7 | Delegated to `review-loop` engine: `resolve reviewer` → `invoke` → `receive findings` → `return repair` → `re-run` → `stop at limit` | Split responsibilities; `project-review` provides Charter & validation, `review-loop` provides convergence |

## Content fidelity

All reference files under `skills/project-review/references/` were copied
verbatim from `skills/review-loop/references/` at `26110c9` (or the
equivalent baseline-check snapshot). No rule was rewritten; only the owning
Skill path and composition wiring changed. `skills/review-loop` was then
refactored to its lightweight engine contract (see `skills/review-loop/SKILL.md`
legacy note). `skills/generic-review` was introduced as the default reviewer
(see `skills/generic-review/references/output-schema.md`).

## Verification

- `skills/project-review/SKILL.md` frontmatter `name: project-review` resolves.
- `skills/project-review/agents/openai.yaml` permits `allow_implicit_invocation: true`.
- Every reference linked in `project-review/SKILL.md` resolves under
  `skills/project-review/references/` or via `../../docs/REVIEWER_CONTRACT.md`.
- `skills/generic-review/references/output-schema.md` defines `Findings: []`,
  `REVIEW-ERROR`, and the required finding fields (`id`, `severity`,
  `location`, `problem`, `reason`, `suggestion`, states `new`/`persists`/
  `fixed`/`duplicate`).
- `skills/review-loop/SKILL.md` no longer claims `PASS`/`FAIL`/`BLOCKED` as
  its own verdict; it references `project-review` for final acceptance and
  links to `REVIEWER_CONTRACT.md` + `generic-review/output-schema.md`.
- `skills/code-review/SKILL.md` still contains the read-only, no-loop,
  no-final-verdict boundary and is invoked via `review-loop`/`project-review`
  (see its Composition and Stopping boundary sections).
- `docs/REVIEWER_CONTRACT.md` exists and defines the 4-field input packet
  and normalized finding shape used by both `review-loop` and
  `project-review`.

Retained evidence: old `review-loop` tests that validate the final-acceptance
protocol remain applicable to `project-review`; lightweight engine tests (if
any) validate `review-loop`'s 5-step convergence and handoff.

## Software baseline contract break (this release train)

The earliest `project-review` software records froze the Charter fixed point
as two commits (`Fixed point: <base> <candidate>`) and derived consumer
freshness from exactly the paths that window touched. Human audit proved this
fail-open: pre-existing or future files inside the accepted component evaded
freshness, and malformed identities were partially salvaged (invalid tokens
dropped, duplicates deduplicated).

This is an intentional compatibility break for an unreleased unsafe acceptance
record format. The software contract now requires three fields
([profiles/software.md](profiles/software.md)):

- Charter `- Fixed point:` — one full commit SHA, the immutable review base;
- Charter `- Implementation scope:` — the reviewed software target as
  repository-relative literal paths;
- verdict `- Reviewed implementation revision:` — one full commit SHA, the
  final evaluated candidate.

Records in the old shape, and any record missing these fields, fail closed as
`review-freshness-unknown`; they are never silently migrated at read time.
Run a fresh `project-review` under the corrected contract to produce a safe,
consumable verdict. There is no fallback to touched-window paths.
