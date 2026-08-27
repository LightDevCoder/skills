# Light Skills Core Flow Repair — Final Audit Results

Status: LOCAL COMMIT CREATED — see `git log -1` for the local repair commit SHA.

## Final narrow repair: current-effort isolation and acceptance semantics

This pass did not restart architecture or the Lean refactor. It closed the
remaining `ask-light` multi-effort contamination and acceptance vocabulary gaps.

### Current-effort resolution

- `ask-light` now resolves the current/active `.scratch/<effort>` before reading
  effort-owned SPEC, tickets, or acceptance/review evidence.
- Resolution prefers an explicit project-level pointer (`Current effort:`,
  concrete `.scratch/<actual-effort>/...` in `docs/agents/light-project.md` or
  `docs/agents/issue-tracker.md`), then a single active SPEC effort, then a
  single non-historical effort with evidence.
- Multiple active efforts fail closed with `ProjectStage:
  ambiguous-current-effort` and `NEED-INPUT`; no directory-order guessing.
- Historical efforts with no reliable pointer also fail closed instead of being
  selected as current.

### Ticket and acceptance scoping

- Tickets are read only from `.scratch/<current-effort>/issues/`.
- Acceptance/review evidence is read only from project-level verdict paths and
  `.scratch/<current-effort>/` handoff/verdict paths.
- Historical open tickets no longer pollute a resolved current effort.
- Historical PASS/FAIL acceptance no longer overrides the current effort.

### Acceptance success semantics

- `ACCEPTANCE_PASS_STATES` is tightened to explicit `pass`/`passed` only.
- Generic lifecycle values (`complete`, `completed`, `done`) are no longer
  treated as acceptance success.
- `Status: complete` without an explicit PASS verdict returns
  `acceptance-unknown` / not accepted.

### New regression tests

Added focused temporary-repository tests for the requested scenarios:

- A: historical unresolved ticket ignored → `project-review`
- B: historical resolved tickets do not hide current open work → `implement`
- C: current PASS + historical FAIL → `accepted`
- D: current FAIL + historical PASS → not accepted
- E: two active efforts → `ambiguous-current-effort`
- F: superseded effort ignored over active effort → `project-review`
- G: no reliable current effort → fail closed
- H: `Status: complete` without PASS → not accepted
- I: `Verdict: PASS` → `accepted`
- J: explicit `Verdict: PASS` is not downgraded by `Status: complete`

### Validation actually performed

```text
python3 -m pytest -q
→ 219 passed

python3 -m unittest discover -s tests
→ Ran 27 tests; OK

python3 -m compileall -q skills tests
→ OK

Skill-local suites:
  skills/ask-light/tests .......... 56 passed
  skills/socratic/tests ........... 21 passed
  skills/clarify/tests ............  5 passed
  skills/project-clarify/tests .... 11 passed
  skills/project-init/tests ....... 32 passed
  skills/review-loop/tests ........ 19 passed
```

Manual smoke with real temporary repositories and the actual first-party skill
root confirmed the scenarios in section 15 of the repair prompt. No Codex host
smoke was fabricated; the existing live-host limitation remains.

## What changed in this final pass

This was a narrow final repair pass after the latest human audit. It did not
reopen architecture, the Lean refactor, or the Skill hierarchy. It closed six
concrete gaps:

1. **Natural project-state intent**: `ask-light` now treats small interrogative
   project-state phrases (`What's next for this project?`, `What stage are we
   at?`, `What's missing?`, etc.) as evidence-driven requests when a project
   root is available, without an oversized keyword list.
2. **Fail-closed ticket completion**: missing ticket `Status` fields and
   unknown statuses no longer imply `tickets resolved`. Unknown ticket state
   returns an honest `NEED-INPUT` result.
3. **Active SPEC detection**: superseded/obsolete/archived specs are excluded
   from project evidence (via status markers and obvious archive/old path
   segments).
4. **Acceptance verdict handling**: only explicit PASS counts as accepted;
   FAIL/BLOCKED/pending/unknown verdicts do not. A fully accepted project
   returns a valid terminal result (`ProjectStage: accepted`, no next Skill).
5. **Socratic recommendation reasoning**: every question exposes a recommended
   option plus a non-empty recommendation reason; contract/executable tests
   now guarantee both.
6. **Batch parser/documentation parity**: semicolon-separated batch replies are
   parsed cleanly (`1B; 2A, but only locally; 3C`) and stray separators such
   as `B, ;` are removed without losing free-text qualifiers.

Preserved behavior: ask-light family navigation, standalone routing, root
discovery, first-party provenance, availability distinction, honest
approval-to-execution behavior, clarify/project-clarify continuous sessions,
dependency gating, and shared-understanding confirmation.

## Files changed in this final pass

```text
skills/ask-light/SKILL.md
skills/ask-light/references/discovery-contract.md
skills/ask-light/scripts/ask_light.py
skills/ask-light/tests/test_ask_light_behavior.py
skills/socratic/SKILL.md
skills/socratic/references/conversation-contract.json
skills/socratic/references/WORKFLOW.md
skills/socratic/scripts/frontier.py
skills/socratic/tests/test_socratic_behavior.py
skills/clarify/SKILL.md
skills/clarify/references/WORKFLOW.md
skills/clarify/tests/test_clarify_contract.py
skills/project-clarify/SKILL.md
skills/project-clarify/references/WORKFLOW.md
.scratch/light-skills-core-flow-repair/results.md
```

## Validation actually performed

```text
python3 -m pytest -q
→ 209 passed

python3 -m unittest discover -s tests -q
→ Ran 27 tests; OK

python3 -m compileall -q skills tests
→ OK

Skill-local suites:
  skills/ask-light/tests .......... 46 passed
  skills/socratic/tests ........... 21 passed
  skills/clarify/tests ............  5 passed
  skills/project-clarify/tests .... 11 passed
  skills/project-init/tests ....... 32 passed
  skills/review-loop/tests ........ 19 passed
```

## Project-state scenarios manually exercised

| Scenario | Result |
| --- | --- |
| Initialized project, no SPEC | `project-spec` |
| Stable active SPEC, no tickets | `project-tickets` |
| Tickets exist, explicitly unresolved | `implement` |
| Tickets exist, unknown status | `NEED-INPUT` (`tickets-unknown`), not `project-review` |
| All tickets explicitly resolved, no acceptance PASS | `project-review` |
| Acceptance FAIL/BLOCKED | `NEED-INPUT` (`acceptance-not-passed`), not accepted |
| Acceptance PASS | `accepted`, no next Skill |

Natural-language project-state phrases were tested with real temporary
repositories where the prompt itself did not encode the expected conclusion.

## Approval-to-execution status

No live Codex proof was fabricated. The previous Codex smoke attempt is still
the only recorded host interaction and it ended at the account usage limit.
The deterministic helper continues to report `host-transition-required` for
user-invoked targets and `beginning-<skill>` only for model-invoked targets,
per repository policy. A prose claim or unit test is not host proof.

## Remaining limitations

- Live Codex smoke remains unavailable in this environment because of the
  account usage limit; direct host transition behavior for model-invoked
  targets is still not observed end-to-end.
- Acceptance/ticket state parsing is deliberately bounded to the repository's
  conventional markdown fields (`Status`, `State`, `Verdict`, `Result`,
  `Outcome`). Exotic custom lifecycle formats are not inferred.

## Stop status

One local commit is created for this final repair pass. Nothing was pushed,
tagged, or released. The repository is returned for human final audit.
---

# Final closure pass — ask-light consumes real project-review durable state

Status: LOCAL COMMIT CREATED (`fix: align ask-light with project-review state`);
nothing pushed, tagged, or released. Returned for human review.

## Producer contract verified from the repository itself

- Durable state tree (`skills/project-review/references/WORKFLOW.md`):
  `.project-review/{charter,state,findings,verdict}.md` plus `rounds/`;
  `.review-loop/` is an accepted backwards-compatibility location when no
  `.project-review/` exists.
- Charter ownership fields (`references/acceptance-charter.md`): `Source:` /
  `Source revision or identity:` identify what was reviewed.
- Real produced records were inspected under `docs/evidence/admissions/kb-init/review-loop/`
  and `docs/evidence/releases/v0.1.5/review-loop/`: verdict files write the
  conclusion as `- Verdict: **PASS**` (markdown-emphasis value); state files
  record `- Status:` from INIT/READY/CRITIC/REPAIR/EVALUATE/PASS/FAIL/BLOCKED.
- No runtime producer writes `docs/agents/acceptance.md`,
  `docs/agents/review-verdict.md`, or effort-level `acceptance*.md`; those were
  speculative fallback paths inside `ask-light` only.

## Bug reproduced before fixing

Real-layout fixtures (temporary repositories mirroring the producer output):

```text
current effort + all tickets resolved + .project-review PASS owned by current effort
→ PRE-FIX: ProjectStage: implementation-complete, Skill: project-review (bug)

current valid PASS + docs/agents/acceptance.md FAIL
→ PRE-FIX: acceptance-not-passed (stale file contaminated current state)

pointer → superseded effort while another effort SPEC is active
→ PRE-FIX: silently selected the superseded effort
```

## Integration repair

- `ask_light.py` now locates `.project-review/` (falling back to `.review-loop/`
  only when absent) and classifies its ownership by matching the Charter
  `Source:` citation against the resolved current effort:
  - cites exactly the current effort → verdict applies;
    `verdict.md` PASS/passed → `accepted` (emphasis-wrapped values parse);
    FAIL/BLOCKED/rejected/pending → `acceptance-not-passed`.
  - cites exactly another named `.scratch` target → historical; ignored for
    current acceptance (routes to `project-review`, cases C/D).
  - no Charter, no resolvable citation, mixed citations → fail closed,
    `review-ownership-unknown` (NEED-INPUT); never inferred PASS.
  - owned record without a written `verdict.md` → no acceptance claim;
    routes to `project-review` (its resume mode owns recorded state).
- Removed authoritative use of legacy root verdict paths and effort-level
  synthetic globs (`acceptance*.md`, `review*/verdict*.md`,
  `project-review*.md`); effort identity now uses only Light planning
  artifacts (spec/map/issues).
- Field extraction hardened twice: values strip markdown emphasis
  (`**PASS**`), and field grammar can no longer bridge newlines (a `# Verdict`
  heading followed by `- Charter revision: 1` previously fabricated a bogus
  second verdict token).
- Explicit-PASS semantics preserved: `complete/done` remain non-verdicts;
  explicit `Verdict: **PASS**` is not downgraded by a same-file
  `Status: complete`.
- Contradictory current-effort evidence fails closed:
  pointer → historical/inactive effort while another effort's SPEC is active →
  `contradictory-current-effort` (NEED-INPUT). Pointer → active effort wins
  over a superseded neighbor. Pointer → missing effort stays
  `ambiguous-current-effort` and is not re-resolved.

## Tests

New real-layout integration regressions (`test_ask_light_behavior.py`, helper
`write_project_review_state` mirrors WORKFLOW.md/acceptance-charter.md):

A current PASS accepted · B current FAIL not accepted · BLOCKED not accepted ·
C historical PASS does not accept current · D historical FAIL ignored ·
E1/E2 unresolvable ownership fails closed · F stale root FAIL cannot
contaminate current PASS · legacy-root PASS alone proves nothing ·
`.review-loop/` fallback consumed · owned charter without conclusion routes to
`project-review` resume · pointer contradictions §11-A/B/C · archive-path
citation counts as historical.

Legacy fixtures that encoded behavior through files no runtime contract
produces were migrated onto the real layout (assertions unchanged) or replaced
by the richer C/D cases; no fail-closed assertion was weakened.

## Validation (this pass, run fresh)

```text
python3 -m pytest -q            → 231 passed
python3 -m unittest discover -s tests → Ran 27 tests; OK
python3 -m compileall -q skills tests → OK

Skill-local suites:
  skills/ask-light/tests .......... 68 passed
  skills/project-review/tests ..... 10 passed
  skills/socratic/tests ........... 21 passed
  skills/clarify/tests ............ 5 passed
  skills/project-clarify/tests .... 11 passed
  skills/project-init/tests ....... 32 passed
  skills/review-loop/tests ........ 19 passed
```

## Manual smoke scenarios (live temporary repositories, post-fix)

| Scenario | Result |
| --- | --- |
| current-effort `.project-review` PASS | `accepted`, skill none |
| current-effort `.project-review` FAIL | `acceptance-not-passed` |
| historical effort A PASS vs current B | B not accepted; `project-review` |
| stale `docs/agents/acceptance.md` FAIL + current PASS | `accepted` (no contamination) |
| verdict with unprovable ownership | `review-ownership-unknown` (fail closed) |
| pointer → superseded effort + other active SPEC | `contradictory-current-effort` |
| normal single-effort open ticket | `work-in-progress` → `implement` (unchanged) |

## Files changed in this pass

```text
skills/ask-light/SKILL.md
skills/ask-light/references/discovery-contract.md
skills/ask-light/scripts/ask_light.py
skills/ask-light/tests/test_ask_light_behavior.py
.scratch/light-skills-core-flow-repair/results.md
```

## Ownership boundary preserved

No second reviewer contract was created and no `project-review` durable-state
definition was duplicated into `ask-light`; `discovery-contract.md` states what
`ask-light` reads and points at the producer package for definitions. Socratic,
clarify/project-clarify, and project-init were untouched. Host-transition
behavior is unchanged: user-invoked targets still report
`host-transition-required`, model-invoked targets `beginning-<skill>`. As
before, live Codex host transition remains unobserved in this environment
(previous attempt ended at the account usage limit); nothing was fabricated.
