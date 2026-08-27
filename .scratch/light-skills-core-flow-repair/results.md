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

---

# Final closure pass 2 — review freshness and Charter field consistency

Status: LOCAL COMMIT PENDING (`fix: invalidate stale project-review verdicts`);
nothing pushed, tagged, or released. Returned for human final audit.

## Producer contract reconfirmed from the repository

- `skills/project-review/references/acceptance-charter.md` freezes the
  acceptance baseline with BOTH `- Source:` (location) and
  `- Source revision or identity:` (commit / version / timestamp / identity).
- `references/WORKFLOW.md` step 4: freeze the baseline with the source
  location **and** revision or immutable identity; the Charter never silently
  edits it afterward.
- Real generated charters under `docs/evidence/**` encode both fields
  (historical evidence — left untouched).

## Bug reproduced before fixing (red first)

`ReviewFreshnessRegressionTest` was written BEFORE the implementation and run
against commit fba2c82 code:

```text
committed change after PASS       → PRE-FIX: accepted        (7 red cases)
dirty working tree after PASS     → PRE-FIX: accepted
stale FAIL/BLOCKED after change   → PRE-FIX: old verdict kept authoritative
unverifiable revision + PASS      → PRE-FIX: accepted
blank/missing revision + PASS     → PRE-FIX: accepted
```

## Freshness repair (`ask_light.py`, consumer-side only)

- `_classify_review_freshness` resolves the Charter's
  `Source revision or identity:` to a local Git commit (`rev-parse --verify`)
  and compares every `.scratch` path cited by `Source:` against it
  (`cat-file -e <rev>:<path>`, then `git diff --quiet <rev> -- <path>`).
  Because that diff targets the working tree, uncommitted post-review edits
  invalidate exactly like committed ones.
- Verdict freshness gates ALL verdict interpretation: ownership proven →
  freshness decided → only then PASS/FAIL/BLOCKED parsing.
- Verified change since the recorded revision → stage `review-stale`,
  `Skill: project-review`, RECOMMEND routing back for a fresh review;
  applies to stale PASS, FAIL, and BLOCKED alike (a verdict binds to its
  baseline). Not downgraded to generic NEED-INPUT.
- Unrelated repository changes never invalidate: comparison scope is exactly
  the reviewed source paths the Charter cites (producer semantics; no invented
  broader/narrower baseline).
- Fail closed (`review-freshness-unknown`, NEED-INPUT terminal, never
  accepted): blank/missing identity; identity not resolvable to a local Git
  commit (timestamps/version strings/free-form labels); project root not a git
  work tree; cited path absent at the recorded revision; git failure during
  comparison. Each gap names what could not be verified.
- Preserved unchanged: current-effort ownership classification, historical
  review isolation, legacy root acceptance non-authority, `.review-loop/`
  fallback, owned-charter-without-verdict resume flow,
  explicit-PASS-vs-lifecycle-status semantics.

## Producer fixture normalization (contract drift)

- Canonical Charter field is `Source:`; four executable profile fixtures in
  `skills/project-review/tests/` still wrote a synthetic
  `- Acceptance source:` line. All four now use canonical `- Source:` plus a
  profile-appropriate `- Source revision or identity:`.
- Repo-wide drift search confirms zero remaining `Acceptance source:` fields
  in runtime/tests/docs-contract surfaces; historical evidence records under
  `docs/evidence/` were classified historical and NOT rewritten.
- One ask-light test fixture (`test_acceptance_verdicts_are_fail_closed`) had
  encoded ownership by citing a `.scratch/<effort>/spec.md` that never existed
  on disk; it now creates and commits the cited SPEC before the review
  freezes its baseline (fixtures follow the real producer layout instead of
  weakening runtime logic).

## Tests added

`ReviewFreshnessRegressionTest` (temporary real-git repositories):

A fresh PASS on unchanged baseline accepted (incl. new-untracked-noise) ·
B committed change after PASS → `review-stale`/project-review · C dirty
working-tree change → `review-stale` · D unrelated file change keeps
acceptance · E stale FAIL/BLOCKED require fresh review instead of keeping the
old conclusion · F nonsense revision identity fails closed · G blank value and
omitted field fail closed · H full canonical template charter parses end-to-end.

## Validation (this pass, run fresh)

```text
python3 -m pytest -q            → 239 passed
python3 -m unittest discover -s tests → OK
python3 -m compileall -q skills tests → OK
git status --short              → only in-scope files modified

Skill-local suites (run per file):
  skills/ask-light/tests .......... 76 tests OK
  skills/project-review/tests ..... 10 tests OK
  skills/socratic/tests ........... 21 tests OK
  skills/clarify/tests ............ 5 tests OK
  skills/project-clarify/tests .... 11 tests OK
  skills/project-init/tests ....... 32 tests OK
  skills/review-loop/tests ........ 19 tests OK
```

## Manual smoke (real CLI, live temporary git repositories)

| Scenario | Result |
| --- | --- |
| fresh PASS | `accepted`, skill none |
| PASS then committed source change | `review-stale` → `project-review` |
| PASS then dirty working-tree edit | `review-stale` → `project-review` |
| unrelated README change after PASS | `accepted` (not invalidated) |
| FAIL then baseline change | `review-stale` (old FAIL no longer authoritative) |
| unverifiable revision identity + PASS | `review-freshness-unknown`, NEED-INPUT |
| canonical template Charter, fresh | `accepted` |

## Files changed in this pass

```text
skills/ask-light/scripts/ask_light.py
skills/ask-light/references/discovery-contract.md
skills/ask-light/tests/test_ask_light_behavior.py
skills/project-review/tests/test_agent_skill_profile_behavior.py
skills/project-review/tests/test_manuscript_profile_behavior.py
skills/project-review/tests/test_software_profile_behavior.py
skills/project-review/tests/test_specification_profile_behavior.py
.scratch/light-skills-core-flow-repair/results.md
```

## Ownership boundary preserved

`project-review` still owns the durable review contract; `ask-light` consumes
it and `discovery-contract.md` documents consumption rules without redefining
the Charter format. Socratic, clarify, project-clarify, project-init,
review-loop, project-workflow exclusion, and all frozen ask-light behaviors are
unchanged. Live Codex host-transition remains unobserved (unchanged limitation);
nothing was fabricated.

## Known freshness boundary (documented, accepted)

- Detection covers modification and deletion of the exact reviewed source
  paths after the recorded revision. A brand-new file added under a
  directory-cited baseline (e.g. `Source: .scratch/current`) is not part of a
  git diff against that revision; such additions do not stale the verdict by
  themselves. Effort-level activity (e.g. reopening/adding tickets) still
  routes to `implement` through normal ticket-state evidence.
- Projects without a Git work tree cannot prove freshness at all and fail
  closed (`review-freshness-unknown`); this is the intended enforcement of the
  producer's freeze-the-revision contract for repository sources.

## Review baseline integrity repair — 2026-08-27 (final repair: software fixed point + directory baseline)

Closes the two documented gaps in "Known freshness boundary" above, per the
pasted SPEC (Software Fixed-Point Freshness & Directory Baseline Integrity,
base commit `0fa6304`). Reproduced both bugs in real temporary Git repositories
before fixing; ask-light returned `accepted` for software-PASS-after-code-change
and for directory-baseline-with-new-untracked-child pre-fix.

### Software review contract (producer semantics, confirmed)

- Approved source baseline: Charter `Source:` + `Source revision or identity:`
  (unchanged previous layer).
- Implementation fixed point: Charter `- Fixed point:` field, now documented by
  the producer (`skills/project-review/references/profiles/software.md` —
  "Durable fixed-point record"), added to the Charter template
  (`acceptance-charter.md`) and frozen at `init` (`references/WORKFLOW.md` step 4).
- Fixed-point identity source: the produced identity only; ask-light creates no
  parallel format. Two values `<base> <candidate>` delimit the reviewed window;
  one value means the candidate's own change set vs its parent.
- Verification semantics: `git diff --quiet <candidate> -- <path>` per window
  path (covers committed AND uncommitted drift); repository-first commits cannot
  delimit a window and fail closed; empty windows fail closed.

### Software freshness results

- fresh PASS → `accepted`; dirty implementation change → `review-stale`;
  committed implementation change → `review-stale`; unrelated change (README /
  side files outside window) → still `accepted`; stale FAIL/BLOCKED after
  implementation change → `review-stale` (old failure not carried to a new
  baseline); missing fixed point → fail closed (`review-freshness-unknown`,
  NEED-INPUT, no-execution); unverifiable/unresolvable fixed point → same
  fail-closed class.

### Directory baseline results

- tracked child modification / deletion → `review-stale`; brand-new untracked
  child inside the cited directory → `review-stale` (new: scoped
  `git status --porcelain -- <dir>`); untracked file outside the directory →
  irrelevant; file-only Source ignores untracked siblings in its directory.

### Tests added

12 Git-backed regression methods (17 cases incl. subTests) in
`skills/ask-light/tests/test_ask_light_behavior.py`:
`SoftwareReviewFreshnessTest` (§13 A–G incl. G2 repository-first) and
`DirectorySourceBaselineTest` (§14 H–L). Existing 72-method behavior suite and
all fixture helpers extended, not rewritten (`profile=`/`fixed_point=` kwargs).

### Manual smoke (real CLI, live temporary git repositories) — 11/11 OK

fresh software PASS; repository-first fixed point fail-closed; dirty code after
PASS; committed code after PASS; unrelated README change after PASS; stale FAIL;
directory untracked addition; outside-directory untracked; file-only source
sibling; normal flow resolved-tickets→project-review→accepted (pre-review stage
`implementation-complete`, post-review `accepted`).

### Validation (fresh, post-review-repair)

```text
python3 -m pytest -q            → 251 passed
python3 -m unittest discover -s tests → 27 tests OK (245+7 assertions)
python3 -m compileall -q skills tests → OK
git status --short              → only in-scope tracked files modified

Skill-local suites:
ask-light 88 · project-review · socratic · clarify · project-clarify ·
project-init · review-loop → all OK
```

### Specialist review evidence

Two-axis independent review ran on the working-tree diff vs fixed point
`0fa6304` (Standards + Spec sub-agents). Findings applied before commit:
unreleased CHANGELOG entry added under "Changed — Review baseline integrity";
Charter template + init workflow now carry the `- Fixed point:` field so the
producer template matches the consumer contract; root-commit whole-tree window
fallback removed in favor of fail-closed (spec §9 anti-too-broad);
Profile matching tightened to exact token; revision-resolution helper deduped.
Own regression test caught a peel-suffix bug introduced during that dedupe
(parent probe) and was fixed before validation. Non-applied judgement calls,
recorded intentionally: discovery-contract keeps a short consumer summary of the
producer rule (explicitly labelled as producer-owned definition), and failure-
message ladders stay structurally similar across classifiers.

### Files changed

```text
CHANGELOG.md
skills/ask-light/scripts/ask_light.py
skills/ask-light/references/discovery-contract.md
skills/ask-light/tests/test_ask_light_behavior.py
skills/project-review/references/profiles/software.md
skills/project-review/references/acceptance-charter.md
skills/project-review/references/WORKFLOW.md
```

Live Codex host-transition remains unobserved; nothing fabricated. Remaining
limitation (documented): single-value fixed points protect only the candidate's
own change set; multi-commit implementation spans must freeze two endpoints per
the producer reference.

# Final closure — software review baseline contract (supersedes d00b221 two-value grammar)

Human audit baseline: `d00b221` (`fix: validate complete project-review baseline`),
verdict NEEDS REPAIR. This round closes the remaining false-accept class as a
contract (producer + consumer together), per the final repair prompt. Reproductions
and smokes live in `.scratch/light-skills-core-flow-repair/smoke/`.

## Pre-fix reproductions (run against d00b221 working tree, real temp Git repos)

Script: `smoke/repro-prefix-d00b221.py`; captured output: `smoke/repro-prefix-d00b221.out`.

```text
A/A1 dirty:    modify pre-existing in-scope src/common.py (untouched by B..C diff) -> accepted   BUG  (required: review-stale)
A/A2 committed: same, committed                                                                    -> accepted   BUG
B/B1 untracked: new src/new_feature.py after PASS                                                  -> accepted   BUG  (required: review-stale)
B/B2 committed: new src/new_feature.py after PASS, committed                                       -> accepted   BUG
C: Fixed point '<unresolvable-40hex> <valid-candidate>'        -> accepted                         PARTIAL-SALVAGE BUG (required: review-freshness-unknown)
D: Fixed point '<candidate> <candidate>' (deduped to one entry) -> accepted                        DEDUPE BUG          (required: review-freshness-unknown)
```

Root causes confirmed live:

1. `_classify_implementation_fixed_point` derived the monitored set from
   `git diff --name-only <window>` — i.e. changed-file-set != complete
   implementation scope; pre-existing and future in-scope files evaded freshness.
2. `_resolve_revision_chain` salvaged revision chains (extract → resolve → drop
   failures → dedupe → reinterpret by count), so malformed identities were
   silently reduced into a valid-looking one-value form.
3. Freezing the candidate inside the immutable Charter at `init` contradicts the
   authorized review→repair→re-review lifecycle (C1 repaired to C2 would either
   instantly stale against C1 or force a Charter mutation).

## Final producer contract (this round)

Three distinct concepts, never conflated:

```text
Fixed point                      (Charter, immutable, frozen at init)
  - Fixed point: <one full 40-hex commit SHA>
  = the immutable code-review REVIEW BASE. The effective delimiting commit is
    frozen, never a mutable branch name. Not the final candidate.

Implementation scope             (Charter, immutable, frozen at init)
  - Implementation scope: <repo-relative literal path>; <repo-relative literal path>; ...
  = machine projection of the Charter's approved software `In scope`: the
    complete component whose state must equal the accepted implementation.
    Stable component roots (`src/`, `src/; tests/; pyproject.toml`, or `.`
    only when the whole repo is the target). NEVER derived from changed
    paths / common dirs / extensions; unverifiable target => BLOCKED;
    one invalid entry rejects the WHOLE field; no README exception — the
    scope decides.

Reviewed implementation revision (verdict.md, per verdict)
  - Reviewed implementation revision: <one full 40-hex commit SHA>
  = the exact committed candidate the final fresh Evaluator judged. Lives on
    the verdict, NOT the Charter, because authorized bounded repairs legally
    move C1 -> C2; the verdict re-binds the immutable requirements without
    mutating the Charter.
```

Freshness algorithm (consumer, `ask_light.py::_classify_software_implementation_freshness`):

```text
profile gate == software (else not-applicable, Source layer governs)
1. strict-parse Fixed point      (exactly one full SHA, resolves AS that commit; else unknown)
2. strict-parse Implementation scope (literal grammar, whole-field; else unknown)
3. strict-parse final revision from verdict.md (same grammar; else unknown)
4. B != C; merge-base --is-ancestor B C   (else unknown)
5. git --literal-pathspecs diff --name-only B C -- <scope> non-empty (else unknown; never broaden)
6. git --literal-pathspecs diff --name-status C -- <scope> must be empty
   (covers tracked/staged/unstaged/committed drift + deletions; else stale)
7. git --literal-pathspecs status --porcelain -uall -- <scope> must have no "??"
   (untracked additions; else stale)
current IFF 1-7 hold. FAIL/BLOCKED bind equally (drift -> review-stale).
Source freshness (§22) unchanged and AND-ed with implementation freshness.
Review metadata (.project-review/, .review-loop/, .scratch/) stays out of
scope unless genuinely the artifact (§16; producer guidance added).
```

Scope grammar: repo-relative POSIX literal paths, `;` separator; rejects
empty entries, absolute, `..`, pathspec magic (leading `:`), wildcard/glob
chars (incl. `[ ] { }` brackets added from Reviewer B advisory), backslash,
quoting wrappers; extraction skips markdown wrapper-stripping so `src/*`
cannot be silently rewritten to `src/` (real bug found by the new tests).

Legacy `d00b221` behavior: old two-value records and any record missing
`Implementation scope` / `Reviewed implementation revision` never reach
`accepted` — `review-freshness-unknown` / NEED-INPUT; no read-time migration
(documented in project-review `references/migration.md` and CHANGELOG).

## Tests added / changed this round

`skills/ask-light/tests/test_ask_light_behavior.py`:
- `SoftwareReviewFreshnessTest` rewritten as `SoftwareBaselineFreshnessTest`
  (22 methods / ~50 cases incl. subTests): §20 valid baseline, changed-path
  dirty/committed, §11 pre-existing-outside-diff dirty/committed, §12 new
  file untracked/staged/committed, in-scope deletion, out-of-scope isolation,
  exact-file scope sibling isolation, whole-repo `.` README staleness, missing/
  invalid/mixed scope (whole-field, no salvage), missing/invalid final revision
  (short/prose/two/unresolvable), strict fixed-point matrix (8 forms incl.
  legacy two-value + unresolvable single), base==final, non-ancestor base,
  empty in-scope window, FAIL/BLOCKED staleness, legacy d00b221 fixture,
  §21 review→repair→PASS binding to C2 (+ post-C2 in/out-of-scope variants),
  §16 metadata-commit self-staling guard.
- `write_project_review_state` gained `implementation_scope` / `final_revision`.

`skills/project-review/tests/test_software_profile_contract.py`: TC-SW-006..009
structural contract checks (baseline record section, fixed-point grammar +
review-base semantics, two-value/window rule forbidden via require_no_match,
scope grammar + never-inferred + BLOCKED + whole-field + no-README-exception,
verdict revision ownership, clean-in-scope-tree PASS rule, lifecycle rules,
init freeze wording, closeout binding, §16 metadata guidance).

## Review→repair→PASS lifecycle result (§21, real git)

```text
B frozen; C1 = initial impl commit -> confirmed finding -> bounded in-scope
repair committed as C2 -> fresh evaluator verdict records C2 -> ask-light:
accepted (compares against C2, NOT C1). Post-C2 in-scope change -> review-stale.
Post-C2 out-of-scope committed change -> still accepted.
Smoke lines 21/22/22b in smoke/manual-matrix-final.out; regression test
test_review_repair_lifecycle_binds_to_evaluated_revision_c2.
```

## Manual smoke matrix (§26) — smoke/manual-matrix-final.py, real CLI git

27/27 rows OK (25 required scenarios + staged-file extra + out-of-scope-after-C2
extra). Full observed outputs: `smoke/manual-matrix-final.out`. Highlights:
pre-existing in-scope dirty/committed -> review-stale (04/05); new in-scope
untracked/staged/committed -> review-stale (06/06b/07); whole-repo scope README
-> review-stale (11); exact-file scope sibling -> accepted (12); missing scope
(13), mixed-invalid scope (14), legacy two-SHA (15), invalid+valid SHA (16),
missing/unresolvable final revision (17/18) -> review-freshness-unknown;
FAIL/BLOCKED drift (19/20) -> review-stale; directory-Source layers (23-25)
unchanged and green.

## Specialist findings and dispositions (§27)

- Reviewer B (consumer/adversarial, ~60 live probes incl. argv-spy on git):
  B1-B12 all NO (no salvage, no evasion, no false stale, no legacy accept).
  ADVISORY applied: `[]{}` added to forbidden scope characters (glob
  metachars) + regression cases. ADVISORY noted, no change: Profile-token
  leniency arms fail-safe (gate-armed = stricter); committed symlink content
  inherently unverifiable (git domain limit).
- Reviewer A (producer/lifecycle): Q1/Q2/Q4 NO (contract holds), Q3 YES only
  for whole-repo scope `.` (closeout writes born-stale the PASS — fails safe).
  ADVISORY applied: explicit producer guidance added to
  `profiles/software.md` lifecycle rules (keep `.project-review/`,
  `.review-loop/`, `.scratch/` records out of the frozen target) + structural
  contract tests TC-SW-009. ADVISORY applied: CHANGELOG superseded section
  now carries an explicit history note (not relabeled, superseded-before-release).

## Validation (fresh, after specialist-review fixes)

```text
python3 -m pytest -q             -> 266 passed
python3 -m unittest discover -s tests -> OK (COLLECTION 245 + HOOKS 7 assertions)
python3 -m compileall -q skills tests -> OK
git diff --check                 -> OK

Skill-local suites: ask-light 103 · project-review 10 · socratic 21 ·
clarify 5 · project-clarify 11 · project-init 32 · review-loop 19 — all OK
```

## Self-audit answers (§30, from code/tests)

All seven audit questions: **NO** — pre-existing in-scope files cannot
survive (scope-wide diff, tests+smoke 04/05); new in-scope files cannot
(untracked/staged/committed arms, smoke 06/06b/07); malformed fixed points
cannot be reduced to a valid grammar (fullmatch single-token, 8-form matrix);
scope cannot be partially accepted (whole-field rejection); a verdict cannot
reference C1 after C2 was evaluated (verdict-bound revision, lifecycle smoke);
out-of-scope changes cannot falsely stale (scope-limited checks, smoke 09/10/
12/22b/24/25); legacy records cannot reach accepted (smoke 15 + fixture test).

## Files changed

```text
CHANGELOG.md
skills/ask-light/scripts/ask_light.py
skills/ask-light/references/discovery-contract.md
skills/ask-light/tests/test_ask_light_behavior.py
skills/project-review/references/WORKFLOW.md
skills/project-review/references/acceptance-charter.md
skills/project-review/references/evidence-protocol.md
skills/project-review/references/migration.md
skills/project-review/references/profiles/software.md
skills/project-review/tests/test_software_profile_contract.py
.scratch/light-skills-core-flow-repair/results.md
.scratch/light-skills-core-flow-repair/smoke/repro-prefix-d00b221.{py,out}
.scratch/light-skills-core-flow-repair/smoke/manual-matrix-final.{py,out}
```

## Remaining limitations

- Committed symlink CONTENT inside a frozen scope is not verifiable by Git
  content comparison (inherent git limit; noted by Reviewer B).
- Truncated (>64KB) charter/verdict files may hide baseline fields; failure
  direction is fail-closed (unknown), never a false accept.
- The consumer trusts the producer-frozen scope's derivation quality only
  structurally; scope-choice soundness remains a producer-side duty enforced
  by documentation + contract tests, not by ask-light semantics.
