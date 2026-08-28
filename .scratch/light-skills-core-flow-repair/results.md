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

---

# Final hardening pass — durable review state edge cases (baseline `52d8638`)

Human audit baseline: `52d8638` (`fix: finalize software review baseline contract`),
verdict NEEDS REPAIR. Narrow repair only: the accepted baseline architecture
(Charter fixed point / implementation scope / verdict reviewed implementation
revision, and the review→repair→re-review lifecycle) was frozen and untouched.
Reproductions and smokes live in
`.scratch/light-skills-core-flow-repair/smoke/` (`repro-prefix-52d8638.*`,
`manual-matrix-hardening.*`).

## Pre-fix reproductions (§19, real temp Git repos, real route() path)

Script `smoke/repro-prefix-52d8638.py`; captured output
`smoke/repro-prefix-52d8638.out` (pre-fix section). All 15 rows reproduced
false `accepted` against `52d8638`:

```text
A  duplicate Profile (generic first) + committed in-scope drift  -> accepted  BUG
B  missing Profile + committed in-scope drift                    -> accepted  BUG
C1 duplicate identical Fixed point        C2 duplicate conflicting Fixed point -> accepted  BUG
D1 duplicate identical Implementation scope D2 conflicting                    -> accepted  BUG
E1 duplicate identical Reviewed implementation revision E2 conflicting        -> accepted  BUG
F  duplicate Source (current effort cited first)                 -> accepted  BUG
G1 Source revision '<invalid-40hex> <valid-sha>'                 -> accepted  BUG
G2 Source revision '<valid-sha-A> <valid-sha-B>'                 -> accepted  BUG
H1/H2 ignored in-scope src/new_hidden.py (.gitignore / .git/info/exclude)     -> accepted  BUG
I1/I2 ignored .scratch/current/hidden.md child (both mechanisms)              -> accepted  BUG
```

Root causes:

1. **First-match canonical field parsing** — `_raw_field_line(.search)` and
   `_reviewed_profile(.values[0])` read "first value wins" from authoritative
   fields, so duplicate (or missing) Profile silently skipped software
   freshness and duplicate baseline fields preserved `accepted`.
2. **Permissive Source revision salvage** — `_resolve_recorded_revision`
   extracted all commit-like tokens and returned the first resolvable one,
   selecting one SHA out of an ambiguous value (the removed failure mode of
   the old two-value Fixed point, still alive in `Source revision or identity`).
3. **Ignored files hidden from `git status`** — both directory-Source and
   implementation-scope new-file detection scanned
   `git status --porcelain -uall`, which never reports files hidden by
   `.gitignore` / `.git/info/exclude` / global excludes files.

## Singleton-field contract (§3–§5, §8, §26)

Canonical producer-owned fields are singleton fields; cardinality is part of
validity. New `_raw_field_occurrences` (same canonical field-line regex as
before, `finditer`) + `_singleton_field_value` enforce:

```text
exactly 1 occurrence -> parse and validate (existing wrapper trimming kept)
0 occurrences        -> missing  -> fail closed (unknown / ownership unknown)
>1 occurrences       -> ambiguous -> fail closed — even identical values,
                        in any field order; never "first wins"
```

Enforced for `Source:`, `Source revision or identity:`, `Profile:` (Charter),
`Fixed point:`, `Implementation scope:` (Charter), `Reviewed implementation
revision:` (verdict). A missing or duplicated `Profile:` fails closed as
`review-freshness-unknown` (NEED-INPUT, no-execution) — it never falls back to
generic behavior; `not-applicable` is reachable only when exactly one Profile
value parses and is not `software`. Duplicate `Source:` fails ownership
closed (`review-ownership-unknown`) even when one occurrence matches the
current effort. `_parse_exact_commit_field` gained the `ambiguous` failure for
`Fixed point` / `Reviewed implementation revision`.

## Source identity parsing behavior (§9–§11)

`_resolve_recorded_revision` no longer salvages: the value is usable only when
it carries exactly ONE commit-like token that resolves locally. invalid+valid,
valid+valid, duplicated SHAs (incl. mixed case), short-prefix+full-SHA of the
same commit → `ambiguous` → unknown. 0 usable tokens (free-form labels,
timestamps, version strings) → `unresolvable` → unknown. Non-Git immutable
identities remain unsupported by the consumer (no verifier exists → unknown;
unchanged, do not guess). The strict exactly-one-full-40-hex grammar is
unchanged for `Fixed point` / `Reviewed implementation revision`.

## Ignored-file detection behavior (§12–§18, §26)

Both new-file checks now use
`git --literal-pathspecs ls-files --others -- <scope>` WITHOUT
`--exclude-standard`, so ignored files count as post-review additions; Git
ignore controls status presentation, not scope membership. Preserved:

- tracked / staged / committed drift still detected by
  `git diff <rev> -- <scope>` (checked first; deletions and committed
  additions included) — no regression to `Reviewed implementation revision`
  or Source revision comparison;
- directory Source `.scratch/current`: any new child anywhere under it
  (ordinary, `.gitignore`, info/exclude, nested) stales; files outside the
  directory stay irrelevant;
- exact-file Source / exact-file scope: siblings never widen the baseline;
- whole-repo scope `.`: ignored files anywhere in scope count;
- out-of-scope caches/build artifacts stay irrelevant (no repo-wide scan);
- entries are filtered by emptiness only — a whitespace-only filename is a
  real entry (Reviewer-B defect repair below).

## Tests added (§20–§21)

`skills/ask-light/tests/test_ask_light_behavior.py`: 103 → 122 methods.
Singleton cardinality matrix through the REAL route path (duplicate identical
/ conflicting / order-reversed Profile, Source, Source revision or identity,
Fixed point, Implementation scope, Reviewed implementation revision; missing
Profile with drift; missing/duplicate generic Profile); Source-revision
ambiguity matrix (single valid control; invalid-only; invalid+valid;
valid+invalid; valid A+B; same SHA twice; duplicate fields); ignored-file
matrix (in-scope `.gitignore` / info/exclude / nested ignored; out-of-scope
ignored root+docs; exact-file scope sibling; whole-repo scope incl.
whitespace-filename adversarial case; directory-Source children both
mechanisms + nested; outside-directory ignored file; file-only Source ignored
sibling). Tamper tests mutate otherwise-valid accepted records via
`append_durable_field` / `set_*_field_lines` helpers and call `route()`.
`skills/project-review/tests/test_software_profile_contract.py`: TC-SW-008
re-aligned to the ignored-files wording + TC-SW-006 singleton-fields check.

## Manual smoke matrix (§22) — real CLI, real Git: 20/20 OK

`smoke/manual-matrix-hardening.py` → `manual-matrix-hardening.out` (observed
output per row): fresh software PASS accepted; duplicate Profile + drift,
missing Profile + drift, duplicate Source/Fixed point/Implementation scope/
Reviewed implementation revision, Source revision invalid+valid and validA+
validB → not accepted (`review-freshness-unknown` / `review-ownership-
unknown`); ignored in-scope file via .gitignore and info/exclude, ignored
directory-Source child, whole-repo scope ignored file, post-C2 in-scope
tracked drift → `review-stale`; ignored out-of-scope file, ignored file
outside directory Source, file-only Source + ignored sibling, exact-file scope
+ ignored sibling, unrelated README → `accepted`; C1→repair→C2 lifecycle →
accepted at C2.

## Specialist review findings and dispositions (§27)

Reviewer A (durable-state parsing): Q1–Q4 all PASS with live adversarial
probes (identical/conflicting/cross-section duplicates for all six fields;
missing Profile with drift; token soup incl. prefix-of-same-commit,
mixed-case, glued 41+-hex runs; full order-flip battery; 16 line-format
variants × 6 fields regex-delta check; CRLF). No valid defects. Dispositions:
advisory "identical duplicate `Verdict: PASS` still accepted" — NOT repaired:
verdict parsing is aggregate-unanimous (any conflicting value already fails
closed; identical duplication is interpretation-invariant), recorded as a
known limitation; advisory `_spec_status` first-value-wins — out of scope
(SPEC-status routing frozen by §1); advisory per-document singleton ownership,
fenced-code-block occurrences, 7–40 token latitude — intended/accepted;
advisory cosmetic ambiguous-Source gap text — REPAIRED.

Reviewer B (Git scope completeness): Q1–Q5 all PASS with 30+ live repos
(.gitignore, info/exclude, GLOBAL core.excludesFile proven active in-process,
negated patterns, ignored directories, nested/deep/unicode/space names,
anchored and `**` exclude forms; scope containment incl. shared-prefix
siblings; exact-file non-widening; directory-Source regression battery;
drift-before-others interplay, four drift categories covered exactly once).
One VALID defect found and REPAIRED: a whitespace-only filename at repo root
evaded the scope-others check under scope `.` because the blank-line filter
used `line.strip()` — replaced with emptiness-only filtering in both checks +
regression test. Advisories (pre-existing, unchanged): empty untracked
directories invisible to git (both channels); C-quoted unicode names in gap
messages (cosmetic); embedded repos listed collapsed → stale (fail-closed);
assume-unchanged/skip-worktree can hide tracked modifications from
`git diff` (git-domain limit).

## Full validation (§28, run fresh after all fixes)

```text
python3 -m pytest -q             → 285 passed
python3 -m unittest discover -s tests → OK (COLLECTION 245 + HOOKS 7 assertions)
python3 -m compileall -q skills tests → OK
git diff --check                 → OK
git status --short               → only intended changes

Skill-local suites: ask-light 122 · project-review 10 · socratic 21 ·
clarify 5 · project-clarify 11 · project-init 32 · review-loop 19 — all OK
```

## Final self-audit (§30, from the tests above)

Duplicate Profile → freshness skipped? NO (repro A, matrix 02, tamper tests).
Missing Profile → skipped? NO (repro B, matrix 03). Duplicate Source resolves
ownership? NO (matrix 04). Duplicate Fixed point / Implementation scope /
Reviewed implementation revision select one value? NO (matrices 05–07).
Source revision salvage from ambiguous input? NO (matrices 08–09, Reviewer A
Q3). .gitignore / info/exclude hide in-scope new implementation files? NO
(matrices 10–11, Reviewer B Q1–Q2 incl. global excludes). Ignored Source
children evade directory freshness? NO (matrix 13). Ignored-file fix
incorrectly invalidates exact-file or out-of-scope paths? NO (matrices
12/14/15/16, Reviewer B Q3–Q4). C1→C2 lifecycle works? YES (matrix 18–20,
lifecycle test). All answers from executed tests; none unknown/untested.

## Files changed

```text
CHANGELOG.md
skills/ask-light/scripts/ask_light.py
skills/ask-light/references/discovery-contract.md
skills/ask-light/tests/test_ask_light_behavior.py
skills/project-review/references/WORKFLOW.md
skills/project-review/references/acceptance-charter.md
skills/project-review/references/profiles/software.md
skills/project-review/tests/test_software_profile_contract.py
.scratch/light-skills-core-flow-repair/results.md
.scratch/light-skills-core-flow-repair/smoke/repro-prefix-52d8638.{py,out}
.scratch/light-skills-core-flow-repair/smoke/manual-matrix-hardening.{py,out}
```

## Remaining limitations

- Carried forward unchanged: committed symlink content beyond the link value
  is unverifiable by Git; truncated (>64 KB) records fail closed; scope-choice
  soundness remains a producer duty; live Codex host transition unobserved.
	- This round, by design: identical duplicate `Verdict: PASS` values are
	  interpretation-invariant and still accepted (any conflicting verdict value
	  fails closed); SPEC `Status:` duplication is outside the durable review
	  contract (frozen routing); field-shaped lines inside fenced code blocks
	  count as occurrences (over-strict, fail-closed); a single 7–40-hex token
	  remains a valid free-form `Source revision or identity` (field name allows
	  identity forms; strict 40-hex only for the software identities).

---

# Final Repair Results — Durable Review Transaction Coherence

## Human audit baseline

`38f4f9b867777a95c818ef7d3845e2bb42c679b0` (`fix: harden project-review durable baseline`)

## Pre-fix state.md reproductions (§28)

Against baseline `38f4f9b`, `ask-light` evaluated `charter.md` and `verdict.md` while completely ignoring `.project-review/state.md`. Executed with real project-review durable state (`.scratch/light-skills-core-flow-repair/smoke/repro-prefix-38f4f9b.{py,out}`):

- **A (State READY + old Verdict PASS):** returned `accepted` ❌ (false positive; active review bypassed).
- **B (State CRITIC + old Verdict PASS):** returned `accepted` ❌ (false positive; active review bypassed).
- **C (State REPAIR + old Verdict PASS):** returned `accepted` ❌ (false positive; active review bypassed).
- **D (State EVALUATE + old Verdict PASS):** returned `accepted` ❌ (false positive; active review bypassed).
- **E (missing state.md + Verdict PASS):** returned `accepted` ❌ (false positive; missing lifecycle state ignored).
- **F (Charter rev 2, State/Verdict rev 1):** returned `accepted` ❌ (false positive; revision mismatch bypassed).
- **G (State Profile != Charter Profile):** returned `accepted` ❌ (false positive; profile mismatch bypassed).
- **H (State FAIL + Verdict PASS):** returned `accepted` ❌ (false positive; record conflict bypassed).

## Root cause

`ask-light`'s `inspect_project_state` read `charter.md` for ownership/freshness and `verdict.md` for conclusion without checking `state.md`. Consequently, whenever review was active/reopened (`READY`, `CRITIC`, `REPAIR`, `EVALUATE`), `state.md` was missing, or the Charter was updated to a new revision, any pre-existing `verdict.md` with `PASS` survived as authoritative acceptance.

## Final durable transaction contract (§4–§16)

`charter.md` + `state.md` + `verdict.md` are evaluated as one indivisible durable review transaction:
1. **Charter (`charter.md`):** defines what is being reviewed (Charter revision, Profile, Source baseline, Fixed point, Implementation scope).
2. **State (`state.md`):** defines where the review currently is in its lifecycle (`Status:`, `Charter revision:`, `Profile:`, `Round:`).
3. **Verdict (`verdict.md`):** records the terminal closeout conclusion for that exact review.

A verdict is authoritative if and only if all three parts are mutually coherent.

## Canonical State fields (§6, §7)

`state.md` is mandatory and must establish:
- `- Status:` (exact token from canonical state machine)
- `- Charter revision:` (exact revision identifier)
- `- Profile:` (normalized lowercase profile token)

All State fields are authoritative singletons: exactly 1 occurrence parses; 0 or >1 occurrences (even identical duplicates) fail closed as `review-state-unknown`.

## State status semantics (§8, §9, §26)

- **Active / Non-Terminal States (`INIT`, `READY`, `CRITIC`, `REPAIR`, `EVALUATE`):** review is in progress. Routes immediately to `project-review` (stage `project-review`, skill `project-review`). Any previous `verdict.md` is non-authoritative and never accepted.
- **Terminal States (`PASS`, `FAIL`, `BLOCKED`):** review is complete; requires an agreeing `verdict.md`.
- **Unknown Status:** any non-canonical status (`UNKNOWN`, `NOT-PASS`, `PASSING`, `READY FOR PASS`) fails closed as `review-state-unknown`. Exact token matching only (no substring matching).

## Charter revision coherence (§13)

`state.md`'s `Charter revision` must match `charter.md`'s `Charter revision` exactly. If `verdict.md` records `Charter revision`, it must also match. Any mismatch fails closed as `review-state-unknown`.

## Profile coherence (§14)

`state.md`'s `Profile` must match `charter.md`'s `Profile` (and `verdict.md`'s `Profile` if recorded). Any mismatch fails closed as `review-state-unknown`.

## Terminal State / Verdict agreement (§10)

For terminal review states:
- `State PASS` + `Verdict PASS` → coherent terminal PASS (evaluates freshness).
- `State FAIL` + `Verdict FAIL` → coherent terminal FAIL (`acceptance-not-passed` when fresh).
- `State BLOCKED` + `Verdict BLOCKED` → coherent terminal BLOCKED (`acceptance-not-passed` when fresh).
- Conflicts (`PASS`+`FAIL`, `PASS`+`BLOCKED`, `FAIL`+`PASS`, `FAIL`+`BLOCKED`, `BLOCKED`+`PASS`, `BLOCKED`+`FAIL`) fail closed as `acceptance-unknown`.

## Reopen lifecycle (§17)

1. Initial round: `State PASS` + `Verdict PASS` → `accepted`.
2. Review reopened: `State READY` (with previous `Verdict PASS`) → `project-review` (not accepted).
3. Review progresses: `CRITIC` → `REPAIR` → `EVALUATE` → `project-review` (not accepted).
4. Fresh evaluation completes: `State PASS` + fresh `Verdict PASS` → `accepted`.

## Charter revision update lifecycle (§18)

1. `Charter rev 1` + `State PASS rev 1` + `Verdict PASS rev 1` → `accepted`.
2. Charter updated to `Charter rev 2` (state still rev 1) → `review-state-unknown` (not accepted).
3. New review started: `State READY rev 2` → `project-review`.
4. Review completes: `State PASS rev 2` + `Verdict PASS rev 2` → `accepted`.

## Regression tests (§29–§32)

Added `ReviewTransactionCoherenceTest` (15 methods) in `skills/ask-light/tests/test_ask_light_behavior.py`:
- `test_coherent_pass_software_and_generic_accepted` (generic & software profiles)
- `test_active_review_states_override_old_pass_verdict` (`INIT`, `READY`, `CRITIC`, `REPAIR`, `EVALUATE`)
- `test_missing_state_file_fails_closed`
- `test_empty_or_whitespace_state_file_fails_closed`
- `test_missing_canonical_state_fields_fail_closed` (`Status`, `Charter revision`, `Profile`)
- `test_duplicate_canonical_state_fields_fail_closed` (identical & conflicting duplicates)
- `test_unknown_and_non_canonical_status_fail_closed`
- `test_terminal_state_and_verdict_agreement` (`PASS`, `FAIL`, `BLOCKED`)
- `test_terminal_state_and_verdict_conflicts_fail_closed` (6 conflict combinations)
- `test_missing_or_empty_verdict_for_terminal_state_fails_closed`
- `test_charter_revision_mismatch_fails_closed`
- `test_profile_mismatch_fails_closed`
- `test_reopen_lifecycle_full_sequence`
- `test_charter_revision_update_lifecycle`
- `test_c1_repair_c2_with_reopen_lifecycle`

All 285 pre-existing tests + 15 new test methods (300 total) pass cleanly.

## Manual smoke results (§36)

Ran full 24-scenario smoke matrix against real durable state on disk (`.scratch/light-skills-core-flow-repair/smoke/manual-matrix-state-coherence.{py,out}`):

```text
Scenario                                      | ProjectStage           | Skill           | Verdict
-----------------------------------------------------------------------------------------------
1. coherent PASS transaction                  | accepted               |                 | [PASS]
2. READY + old PASS                           | project-review         | project-review  | [PASS]
3. CRITIC + old PASS                          | project-review         | project-review  | [PASS]
4. REPAIR + old PASS                          | project-review         | project-review  | [PASS]
5. EVALUATE + old PASS                        | project-review         | project-review  | [PASS]
6. missing state.md                           | review-state-unknown   |                 | [PASS]
7. missing Status                             | review-state-unknown   |                 | [PASS]
8. duplicate Status                           | review-state-unknown   |                 | [PASS]
9. unknown Status                             | review-state-unknown   |                 | [PASS]
10. State FAIL + Verdict PASS                 | acceptance-unknown     |                 | [PASS]
11. State PASS + Verdict FAIL                 | acceptance-unknown     |                 | [PASS]
12. State BLOCKED + Verdict PASS              | acceptance-unknown     |                 | [PASS]
13. Charter revision mismatch                 | review-state-unknown   |                 | [PASS]
14. Profile mismatch                          | review-state-unknown   |                 | [PASS]
15. rev1 PASS                                 | accepted               |                 | [PASS]
16. Charter changes to rev2                   | review-state-unknown   |                 | [PASS]
17. READY rev2                                | project-review         | project-review  | [PASS]
18. PASS rev2 + fresh PASS                    | accepted               |                 | [PASS]
19. C1->repair->C2 PASS                       | accepted               |                 | [PASS]
20. reopen C2 review                          | project-review         | project-review  | [PASS]
21. post-C2 in-scope drift                    | review-stale           | project-review  | [PASS]
22. out-of-scope README                       | accepted               |                 | [PASS]
23. ignored in-scope implementation file      | review-stale           | project-review  | [PASS]
24. ignored directory Source child            | review-stale           | project-review  | [PASS]
-----------------------------------------------------------------------------------------------
ALL 24 SCENARIOS PASSED: True
```

## Specialist review findings (§35)

- **Reviewer A (Producer state machine coherence):** Q1–Q4 all verified with test coverage and manual smoke. Active states never trust old verdicts; Charter revision changes invalidate old state; Profile mismatches fail closed; reopen lifecycle transitions cleanly without dead ends.
- **Reviewer B (Consumer fail-closed behavior):** Q1–Q4 all verified with test coverage and manual smoke. Missing/empty `state.md` and missing/duplicate canonical fields fail closed; singleton parsing enforces cardinality; old verdicts cannot bypass State; terminal conflicts fail closed without precedence assumptions.

## Full validation (§37)

```text
python3 -m pytest -q                        → 300 passed
python3 -m unittest discover -s tests       → OK (COLLECTION 245 + HOOKS 7 assertions)
python3 -m compileall -q skills tests       → OK
git diff --check                            → OK
git status --short                          → only intended changes

Local skill suites:
- ask-light (137 tests)                     → OK
- project-review (10 tests)                 → OK
- socratic (21 tests)                       → OK
- clarify (5 tests)                         → OK
- project-clarify (11 tests)                → OK
- project-init (32 tests)                   → OK
- review-loop (19 tests)                    → OK
```

## Files changed

```text
CHANGELOG.md
skills/ask-light/scripts/ask_light.py
skills/ask-light/references/discovery-contract.md
skills/ask-light/tests/test_ask_light_behavior.py
skills/project-review/references/WORKFLOW.md
skills/project-review/references/acceptance-charter.md
skills/project-review/references/evidence-protocol.md
.scratch/light-skills-core-flow-repair/results.md
.scratch/light-skills-core-flow-repair/smoke/repro-prefix-38f4f9b.{py,out}
.scratch/light-skills-core-flow-repair/smoke/manual-matrix-state-coherence.{py,out}
```

## Remaining accepted limitations

- Symlink target contents outside Git's tracked representation remain unverifiable by Git (carried forward unchanged).

---

# Terminal Transaction Identity Repair (SPEC: Final Terminal Transaction Identity Repair)

## Baseline

`d414a3b` (`fix: enforce project-review state coherence`)

## Pre-fix reproductions (§12)

Executed with real durable state on disk (`.scratch/light-skills-core-flow-repair/smoke/repro-prefix-d414a3b.{py,out}`):

- **A (Round mismatch):** `State PASS Round 2` + `Verdict PASS Round 1` → returned `accepted` ❌ (false positive; round mismatch bypassed). Expected post-fix: `acceptance-unknown`.
- **B (missing State Round):** `State PASS (no Round)` + `Verdict PASS Round 1` → returned `accepted` ❌ (false positive; missing State Round bypassed). Expected post-fix: `review-state-unknown`.
- **C (duplicate State Round):** `State PASS (Round: 1, Round: 2)` + `Verdict PASS Round 1` → returned `accepted` ❌ (false positive; duplicate State Round bypassed). Expected post-fix: `review-state-unknown`.
- **D (missing Verdict Round):** `State PASS Round 2` + `Verdict PASS (no Round)` → returned `accepted` ❌ (false positive; missing Verdict Round bypassed). Expected post-fix: `acceptance-unknown`.
- **E (missing Verdict Charter revision):** `State PASS Round 1` + `Verdict PASS (no Charter revision)` → returned `accepted` ❌ (false positive; missing Verdict Charter revision bypassed). Expected post-fix: `acceptance-unknown`.
- **F (missing Verdict Profile):** `State PASS Round 1` + `Verdict PASS (no Profile)` → returned `accepted` ❌ (false positive; missing Verdict Profile bypassed). Expected post-fix: `acceptance-unknown`.
- **G1 (FAIL State, Verdict FAIL+BLOCKED):** returned `acceptance-not-passed` ❌ (incorrect non-conflict interpretation; multiple conflicting terminal conclusions were not treated as ambiguous). Expected post-fix: `acceptance-unknown`.
- **G2 (BLOCKED State, Verdict BLOCKED+FAIL):** returned `acceptance-not-passed` ❌ (incorrect non-conflict interpretation). Expected post-fix: `acceptance-unknown`.

## Root cause

In `d414a3b`, while `state.md` was made authoritative for the review lifecycle, terminal `verdict.md` was not bound to the exact review identity dimensions:
1. `Round` was not extracted or compared between `state.md` and `verdict.md`, allowing old-round verdicts to survive across reopened review rounds once State reached terminal status again.
2. `Charter revision` and `Profile` were optional on `verdict.md` (checked only if present).
3. Multiple terminal conclusion fields in `verdict.md` (e.g. `FAIL` + `BLOCKED`) were not enforced as unique, leading to invalid non-conflict classification.

## State Round contract (§4)

`state.md` now requires exactly 1 canonical `Round:` field line:
- Missing Round → `review-state-unknown`.
- Ambiguous / duplicate Round → `review-state-unknown`.
- Malformed Round → `review-state-unknown`.
- Never defaults to Round 1; never infers from files, timestamps, or Verdict.

## Verdict identity contract (§5, §6, §7)

A terminal `verdict.md` requires:
- Exactly 1 `Verdict:` conclusion line.
- Exactly 1 `Charter revision:` field matching `charter.md` and `state.md`.
- Exactly 1 `Profile:` field matching `charter.md` and `state.md`.
- Exactly 1 `Round:` field matching `state.md`.
- For `software` Profile, exactly 1 `Reviewed implementation revision: <full 40-char commit SHA>`.

Missing, duplicate, malformed, or mismatched Verdict identity fields fail closed as `acceptance-unknown`.

## Round normalization and grammar (§3)

Canonical producer grammar:
- Non-negative integer (e.g. `1`, `2`, `01`, `02`) or standard round prefix/suffix formatting (`round-01`, `round-1`, `round-01 (final)`, `round-01 (closed)`).
- Canonical integer value is extracted and compared between State and Verdict.
- Arbitrary prose, non-numeric strings, or multi-field formats fail closed as malformed.

## Terminal semantic uniqueness (§8)

The terminal conclusion set `{PASS, FAIL, BLOCKED}` must resolve to exactly one unique meaning:
- `PASS` only → `PASS`
- `FAIL` only → `FAIL`
- `BLOCKED` only → `BLOCKED`
- Multiple / conflicting conclusions (`PASS+FAIL`, `PASS+BLOCKED`, `FAIL+BLOCKED`, `PASS+FAIL+BLOCKED`) → `acceptance-unknown`.

## Reopen Round lifecycle (§14)

1. Round 1: `State PASS` + `Verdict PASS (round 1)` → `accepted`.
2. Reopen: `State READY (round 2)` + old `Verdict PASS (round 1)` → `project-review`.
3. Progression: `CRITIC` → `REPAIR` → `EVALUATE` → `project-review`.
4. Transition: `State PASS (round 2)` + old `Verdict PASS (round 1)` → `acceptance-unknown` (fails closed).
5. Fresh evaluation: `State PASS (round 2)` + fresh `Verdict PASS (round 2)` → `accepted`.

## Safe closeout behavior (§18)

Producer documentation (`WORKFLOW.md`) explicitly specifies the fail-safe closeout sequence:
1. Write current-round `verdict.md` with complete transaction identity (`Verdict`, `Charter revision`, `Profile`, `Round`, and software `Reviewed implementation revision`).
2. Verify durable fields against active Charter and evaluated round.
3. Transition `state.md` to terminal status (`PASS`, `FAIL`, `BLOCKED`) for the exact same `Round`.

## Regression tests (§13, §14, §15, §16)

Updated and extended `ReviewTransactionCoherenceTest` in `skills/ask-light/tests/test_ask_light_behavior.py`:
- `test_missing_canonical_state_fields_fail_closed` (`Status`, `Charter revision`, `Profile`, `Round`)
- `test_duplicate_canonical_state_fields_fail_closed` (`Status`, `Charter revision`, `Profile`, `Round`)
- `test_state_round_malformed_fails_closed`
- `test_verdict_round_missing_or_duplicate_or_malformed_fails_closed`
- `test_round_mismatch_fails_closed` (`PASS`, `FAIL`, `BLOCKED`)
- `test_verdict_charter_revision_missing_duplicate_mismatch_fails_closed`
- `test_verdict_profile_missing_duplicate_mismatch_fails_closed`
- `test_terminal_verdict_semantic_uniqueness` (all singletons and all 4 conflict combinations)
- `test_reopen_lifecycle_full_sequence` (including intermediate closeout state)
- `test_charter_revision_update_lifecycle`
- `test_c1_repair_c2_with_reopen_lifecycle`

All 306 tests across test suites pass cleanly.

## Manual smoke results (§21)

Executed full 24-scenario smoke matrix against real durable state on disk (`.scratch/light-skills-core-flow-repair/smoke/manual-matrix-terminal-identity.{py,out}`):

```text
#   | Scenario                                       | Observed Stage         | Expected Stage         | Match
---------------------------------------------------------------------------------------------------------
1   | coherent PASS same round                       | accepted               | accepted               | PASS
2   | PASS State round2 + PASS Verdict round1        | acceptance-unknown     | acceptance-unknown     | PASS
3   | FAIL State round2 + FAIL Verdict round1        | acceptance-unknown     | acceptance-unknown     | PASS
4   | BLOCKED State round2 + BLOCKED Verdict round1  | acceptance-unknown     | acceptance-unknown     | PASS
5   | missing State Round                            | review-state-unknown   | review-state-unknown   | PASS
6   | duplicate State Round                          | review-state-unknown   | review-state-unknown   | PASS
7   | missing Verdict Round                          | acceptance-unknown     | acceptance-unknown     | PASS
8   | duplicate Verdict Round                        | acceptance-unknown     | acceptance-unknown     | PASS
9   | missing Verdict Charter revision               | acceptance-unknown     | acceptance-unknown     | PASS
10  | missing Verdict Profile                        | acceptance-unknown     | acceptance-unknown     | PASS
11  | Verdict revision mismatch                      | acceptance-unknown     | acceptance-unknown     | PASS
12  | Verdict profile mismatch                       | acceptance-unknown     | acceptance-unknown     | PASS
13  | State FAIL + Verdict FAIL/BLOCKED              | acceptance-unknown     | acceptance-unknown     | PASS
14  | State BLOCKED + Verdict BLOCKED/FAIL           | acceptance-unknown     | acceptance-unknown     | PASS
15  | Round1 PASS                                    | accepted               | accepted               | PASS
16  | reopen Round2 READY + old PASS                 | project-review         | project-review         | PASS
17  | Round2 EVALUATE + old PASS                     | project-review         | project-review         | PASS
18  | Round2 PASS + old Round1 PASS                  | acceptance-unknown     | acceptance-unknown     | PASS
19  | fresh Round2 PASS Verdict                      | accepted               | accepted               | PASS
20  | C1->C2 current-round PASS                      | accepted               | accepted               | PASS
21  | post-C2 in-scope drift                         | review-stale           | review-stale           | PASS
22  | out-of-scope README                            | accepted               | accepted               | PASS
23  | ignored in-scope file                          | review-stale           | review-stale           | PASS
24  | ignored Source child                           | review-stale           | review-stale           | PASS
---------------------------------------------------------------------------------------------------------
Overall Result: ALL 24 PASSED
```

## Specialist review findings (§20)

- **Reviewer A (Transaction Identity):** Verified Charter revision, Profile, Round binding, and terminal conclusion uniqueness. Old-round verdicts can never become authoritative in a new round; all required Verdict identity fields must be present as singletons; duplicates fail closed; conflicting conclusions fail closed as `acceptance-unknown`.
- **Reviewer B (Lifecycle Preservation):** Verified active review routing, reopen lifecycle, terminal closeout, C1→C2 software repairs, and Source/software freshness. Active states route to `project-review`; intermediate closeout states fail closed; fresh current-round PASS reaches `accepted`; all existing freshness guarantees remain green.

## Full validation (§22)

```text
python3 -m pytest -q                        → 306 passed in 41.14s
python3 -m unittest discover -s tests       → OK (COLLECTION 245 + HOOKS 7 assertions)
python3 -m compileall -q skills tests       → OK
git diff --check                            → OK (no whitespace or formatting issues)
git status --short                          → only intended changes

Local skill suites:
- ask-light (143 tests)                     → OK
- project-review (10 tests)                 → OK
- socratic (21 tests)                       → OK
- clarify (5 tests)                         → OK
- project-clarify (11 tests)                → OK
- project-init (32 tests)                   → OK
- review-loop (19 tests)                    → OK
```

## Files changed

- `skills/ask-light/scripts/ask_light.py`
- `skills/ask-light/tests/test_ask_light_behavior.py`
- `skills/project-review/references/WORKFLOW.md`
- `skills/project-review/references/acceptance-charter.md`
- `skills/project-review/references/evidence-protocol.md`
- `.scratch/light-skills-core-flow-repair/results.md`
- `.scratch/light-skills-core-flow-repair/smoke/manual-matrix-terminal-identity.py`
- `.scratch/light-skills-core-flow-repair/smoke/manual-matrix-terminal-identity.out`
- `.scratch/light-skills-core-flow-repair/smoke/repro-prefix-d414a3b.py`
- `.scratch/light-skills-core-flow-repair/smoke/repro-prefix-d414a3b.out`

## Remaining limitations

None within the scope of review transaction identity. The durable 3-part transaction contract (`charter.md` + `state.md` + `verdict.md`) is now fully bound across revision, profile, round, and unique verdict conclusion.

- >64 KB durable-record truncation fails closed (carried forward unchanged).
- Scope-choice quality remains a producer responsibility (carried forward unchanged).
- Git assume-unchanged / skip-worktree can hide tracked modifications from `git diff` (git-domain limit, carried forward unchanged).
- Live Codex host-transition evidence is unavailable in this environment (carried forward unchanged).
- Identical duplicate `Verdict: PASS` lines are interpretation-invariant and still accepted when State is PASS (conflicting verdict values fail closed as `acceptance-unknown`).