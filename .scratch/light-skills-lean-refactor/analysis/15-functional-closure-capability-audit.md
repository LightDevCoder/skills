# Functional closure capability audit

Audit date: 2026-08-26
Active authority: `../spec.md`
Matt design reference: `mattpocock/skills` at `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`

The unit of review is the complete package: entrypoint, local references,
scripts, metadata, owned contracts, tests, and composition targets. Reference
length or repeated filenames are not findings by themselves.

| Skill | Original intended capability | Current owner and reachability | Result before repair |
| --- | --- | --- | --- |
| `agent-config` | Inspect host evidence and return a safe routing plan | `SKILL.md` → host evidence and plan schemas; behavior fixtures exercise false and multi-model inventories | covered |
| `ask-light` | Navigate from intent to one Light Skill or bounded recipe | `SKILL.md` → discovery contract → PowerShell lexical scanner | **missing:** no Light-owned semantic map; optional UI metadata can hide Frozen Skills; provenance is inferred from a generic root |
| `clarify` | Lightweight standalone entry to the decision engine | `SKILL.md` → `socratic`; local workflow/routing/examples | **duplicated/missing:** local routing deep-links into Socratic internals; continuation requires another `$clarify`; default output exposes engine state |
| `code-review` | Read-only Standards + Spec review of a fixed diff | `SKILL.md` → workflow, examples, smell baseline; composed by `review-loop` | covered |
| `decision-map` | Durable multi-session decision graph | `SKILL.md` → map contract/workflow/examples → owning capabilities per ticket type | covered; must consume bootstrap tracker locator when present |
| `generic-review` | Read-only general findings with stable IDs | `SKILL.md` → output schema; behavior tests reject mutation/verdict output | covered |
| `implement` | Execute one bounded item, verify, and hand to review | `SKILL.md` → workflow/examples → `tdd`, reviewers, `review-loop` | covered; must consume bootstrap paths/profile when present |
| `project-clarify` | Inspect a real project, resolve user decisions, return handoff | `SKILL.md` → clarification contract/workflow/examples → `socratic` | covered; must inspect bootstrap contract first when present |
| `project-init` | Initialize a project for later Light workflows | `SKILL.md` → presets and initialization contract | **missing:** only writes an instruction block; no stable downstream configuration, issue-tracker contract, or executable idempotence boundary |
| `project-review` | Freeze acceptance and own final PASS/FAIL/BLOCKED | `SKILL.md` → acceptance/profile/evidence contracts → `review-loop` and reviewers | covered; local reviewer contract duplicates the engine-owned runtime packet; migration docs are historical but not labeled as runtime-optional at the entry |
| `project-spec` | Publish a formal SPEC from settled decisions | `SKILL.md` → workflow/output format/examples | covered; must consume bootstrap tracker/context locators when present |
| `project-tickets` | Slice a SPEC into tracker-native vertical tickets | `SKILL.md` → workflow/ticket contract/examples | covered; currently assumes the development repo's local tracker document exists |
| `review-loop` | Drive findings → repair → re-review convergence | `SKILL.md` → lightweight reviewer/finding contracts | covered; should remain canonical owner of the lightweight reviewer packet |
| `socratic` | Maintain decision state and frontier across a conversation | `SKILL.md` → workflow/routing/examples | engine logic covered; **missing presentation contract:** concise normal turn, recommendation, confirmation synthesis, and session continuation signal |

## Ownership decisions

- `socratic` owns unknown routing and internal decision state. `clarify` calls it
  and presents the returned conversation; it does not deep-link into or copy
  `socratic/references/ROUTING.md`.
- `review-loop` owns the lightweight reviewer input/output packet.
  `project-review` owns the richer acceptance registry and final verdict; its
  historical migration record remains available but is not runtime knowledge.
- `project-init` owns the stable per-repository Light configuration contract.
  Downstream Project Skills read only the fields they need and retain their own
  artifact contracts.
- `ask-light` owns routing knowledge only. Installed packages and host evidence
  determine availability separately; an arbitrary package beside Light Skills
  is not first-party provenance.

## Matt concepts accepted or rejected

- Accepted from `ask-matt`: explicit repository-owned capability map and phase
  distinctions. Rejected: copying Matt's flow or vocabulary as Light routing.
- Accepted from `setup-matt-pocock-skills`: one-time repository configuration,
  inspect-before-write, concise recommendations for ambiguous choices, and
  consumer-driven files. Rejected: triage labels because Light has no admitted
  triage consumer.
- Accepted from `grilling`: continuous conversation, a recommended option when
  evidence supports judgment, and shared-understanding confirmation. Preserved:
  Light's dependency/frontier engine and user decision ownership.
- Accepted from `domain-modeling`: stable locators for domain context. Rejected:
  forcing `CONTEXT.md` or ADR creation when the project does not need them.

No reference was removed before this coverage and ownership decision was
recorded.

## Closure status after repair

- `ask-light`: covered by the Light-owned 33-package semantic map, explicit
  task-kind routes, package-aligned invocation types, host availability and
  provenance checks, portable Python runtime, and isolated-copy evidence.
- `project-init`: covered by stable project/tracker contracts, downstream field
  consumption, bounded local tracker paths, case-insensitive instruction
  precedence, marker-aware preservation, atomic preflight, and rerun evidence.
- `clarify` / `socratic`: covered by one-invocation session state, lightweight
  recommendation-bearing projection, synthesis confirmation, correction
  reopen, single routing ownership, and a real three-turn Codex invocation.
- `review-loop` / `project-review`: the lightweight reviewer packet has one
  runtime owner; migration notes remain explicit historical provenance.

The exact commands, limitations, and repair rounds are recorded in
`../evidence/functional-closure-runtime.md`.
