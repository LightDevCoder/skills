# Changelog

[中文变更记录](CHANGELOG.zh-CN.md)

All notable changes are recorded here. A release entry must be tied to an actual version or tag and must not be created merely because a document was drafted.

## Unreleased

### Refactored — agent-config profile authority, execution configuration & companion runtime

- **Profile-authorized execution configurator:** Refactored `skills/agent-config` to map verified host capability evidence and user-confirmed profile tiers (`routine`, `standard`, `high`, `review`) to right-sized execution plans (`single-pass` or `decomposed` across `single-model` or `multi-model` topologies; Cases A, B, C, D). Returns canonical `AgentConfigResult` (`READY`, `NEED_INPUT`, `NEED_PROJECT_TICKETS`, `BLOCKED`, `UNSUPPORTED`).
- **Profile authority over model intelligence inference:** Eliminated heuristic model ranking (`routing_rank`) and guessing model capability from names. Tier assignments and reasoning requirements are authorized solely through user-confirmed profile configuration against evidenced host models.
- **Host-neutral reasoning & effort resolution:** Abstract reasoning policies resolve to authentic host-supported values (`supported_reasoning_efforts` or `reasoning_effort_hierarchy`), failing closed without inventing unsupported values.
- **Companion MCP runtime & native adapter coverage:** Integrated optional companion MCP runtime protocol (`protocol_version: 1`, 8 canonical MCP tools: `get_setup_status`, `inspect_host`, `get_profile`, `save_profile`, `preview_configuration`, `apply_configuration`, `validate_configuration`, `reset_profile`) with 9 native adapters (Codex, Claude Code, Antigravity / agy, DeepSeek Harness / DSH, OpenCode, ZCode, Cursor, Grok Build, Hermes) plus generic plan-only fallback (Pi deferred). Companion runtime is maintained in `LightDevCoder/agent-config`. Maintains full session-local plan-only execution without the companion.
- **Companion health & setup gate:** Added companion health probe semantics (`agent-config setup --check`, live MCP protocol version, canonical tool schema validation) and a non-blocking setup gate (`agent-config setup`, `NEED_INPUT` / `UNSUPPORTED`) supporting explicit host inspection and safe mutation preview before apply.
- **Skill ↔ Companion integration:** Downstream workflows consume normalized `AgentConfigResult`; `implement` offers optional agent-config without blocking execution; `ask-light` routes setup intent to `agent-config setup` while strictly keeping ready unblocked tickets routed to `implement` and complex decomposition routed to `project-tickets`.

## 0.2.0 — 2026-08-28

### Added — 33-package Light workflow architecture

- **Project Workflow (7):** `project-init` (refactored to minimum init), `project-clarify`, `project-spec`, `project-tickets`, `implement`, `project-review`, `release-workflow` (migrated from `LightDevCoder/release-workflow`).
- **Clarification & Research (7):** `socratic` (core engine, from Matt `grilling`), `clarify` (`grill-me`), `project-clarify` (`grill-with-docs`), `decision-map` (`wayfinder`), `research`, `prototype`, `to-questionnaire` — with `socratic` as the shared engine.
- **Planning (2):** `project-spec` (`to-spec`), `project-tickets` (`to-tickets`).
- **Execution (5):** `agent-config` (new, host-agnostic, Sol Advisor reference), `implement` (MatT `implement` → general-purpose executor), `tdd`, `diagnosing-bugs`, `resolving-merge-conflicts`.
- **Review (4):** `review-loop` refactored to lightweight engine + `generic-review` (new default) + `code-review` (adapted) + `project-review` (new, owns frozen baseline and final `PASS`/`FAIL`/`BLOCKED`; migrated from old `review-loop` final-acceptance logic).
- **Productivity & Communication (4):** `handoff`, `wizard`, `wait-what`, `writing-for-agents` (Matt PORTs).
- **Learning (3):** `eli5` (migrated from upstream `DreambigOu/ELI5` @ `a766623`, via temporary migration fork `LightDevCoder/ELI5`), `teach` (PORT), `language-learning` (preserved).
- **Router (1):** `ask-light` refactored last as the Light Workflow Router across 33 Skills.
- **Specialized Workflows (8):** `manuscript-ops`, `kb-init`, `learn-anything`, `language-learning`, `kanban-worker`, `recap`, `eli5`, `release-workflow` — verified standalone + composition with only minimal handoff patches.

Total **34** first-party Skills under `skills/` — the 33-package architecture below plus `humanizer` (see [CATALOG.md](CATALOG.md)).

Approved Matt PORTs (11) each carry `ATTRIBUTION.md` and have no upstream runtime dependency: `research`, `prototype`, `tdd`, `handoff`, `diagnosing-bugs`, `wizard`, `teach`, `wait-what`, `to-questionnaire`, `writing-for-agents`, `resolving-merge-conflicts`. Port preserves upstream behavior; Light changes are limited to runtime decoupling and handoff wiring.

### Added — humanizer skill (34th package)

- **humanizer skill:** New first-party model-invoked Skill that rewrites AI-sounding English or Chinese text so it reads naturally without changing what it says. Adapted from blader/humanizer `e2e92e7` (version 2.11.2) with the pattern book preserved verbatim; adds a Language routing section and a thin Chinese adaptation layer in `references/zh-adaptation.md` (rule overrides for dashes/title case/curly quotes/hyphenated pairs, Chinese pattern mappings and AI vocabulary, an anti-fabrication rule, and Chinese false-positive exemptions). Chinese vocabulary informed by the MIT-licensed op7418/Humanizer-zh (`91f3d39`). Admitted via full-path `review-loop agent-skill` acceptance — `PASS` in round 01 with one minor attribution-wording finding repaired; evidence at [docs/evidence/admissions/humanizer/](docs/evidence/admissions/humanizer/README.md).

### Changed — post-release hardening (agent-config / implement / ask-light)

- **Host-agnostic agent-config:** Refactored `agent-config` to distinguish current executable model availability from model selectability (`model_selection` / `per_agent_model_selection`). Harnesses with one executable model but without model selectors or subagents now safely select single-model multi-agent or single-model single-agent routes without returning `BOUNDARY`.
- **User-optional agent-config in implement:** Refactored `implement` so it never invokes `agent-config` automatically. When orchestration could materially help (role splitting, parallelism, reviewer isolation), `implement` offers `agent-config` as an explicit user choice; declining or running without model selection never blocks normal bounded execution. Simple solo tasks proceed directly without prompts.
- **ask-light model-led hybrid advisor refactor:** Refactored `ask-light` into a model-led workflow advisor following the five-stage architecture: (1) Request interpretation (MODEL), (2) Project/host evidence collection (CODE), (3) Candidate Skill understanding (MODEL + catalog metadata), (4) Final workflow judgment (MODEL), (5) Selection validation & transition (CODE + host capability).
- **Canonical project flow alignment:** Restored the canonical flow `project-clarify → project-spec → project-tickets → implement → project-review` across `ask-light`, recipes, maps, and documentation without inserting a SPEC-review gate before `project-tickets`.
- **Strict scope and validation safety:** Added strict scope vocabulary enforcement (`current-workflow`, `independent`, `standalone`), explicit `Skill: none` validation permitting terminal `none` only on genuinely accepted efforts, and durable scope preservation across explicit user approval with fail-closed behavior on missing or invalid scope.
- **Trusted host capability evidence:** Defined trusted host evidence policy requiring genuine host-owned capability channels for approved user-invoked transitions, rejecting model/context JSON string spoofing and unverified booleans, and defaulting safely to exact invocation rendering (`host-transition-required`).
- **Content-validated clarification readiness:** Tightened clarification readiness to require producer-contract identity and target (`readyFor: project-spec`).
- **ask_light.py evidence service:** The Python helper is now purely an evidence, catalog, recipe, and validation service (`ask-light-evidence/1`). Returns structured facts (projectContract, currentEffort, spec, tickets, review, artifactSignals) and scoped hard constraints without any deterministic Skill recommendation.
- **Workflow mode:** Refactored `recipes_result` (`--mode workflow`) to publish canonical recipes with step availability and handoffs without deterministic regex winner selection; the model selects and anchors the recipe at the current state.
- **Comprehensive regression test suite:** Full matrix regression coverage for review transaction coherence, source/implementation freshness, software three-field baseline validation, current-effort resolution, discovery/provenance checks, strict scope validation, and `agent-config`/`implement` relationship tests.

### Changed

- **Governance:** `AGENTS.md` now states the authoritative references (Matt Pocock Skills for Skill-writing; Sol Advisor for `agent-config`) and the 14 maintenance rules (inspect upstream, no rewrite of mature Skills, no redesign of PORTs, concise `SKILL.md`, supporting-files disclosure, no single package shape, composition over duplication, no architecture duplication, etc.), without bloating into SPEC.
- **Admission:** `docs/SKILL_ADMISSION.md` now allows SPEC-authorized Ports with attribution, Light integration, and no upstream runtime dependency (`Port ≠ arbitrary copying`).
- **Review:** `docs/REVIEW_POLICY.md` now distinguishes `reviewer` (`generic-review`/`code-review`/domain → findings) vs `review-loop` (engine) vs `project-review` (final acceptance), in sync with [Reviewer contract](docs/REVIEWER_CONTRACT.md); final-acceptance logic migrated from `review-loop` to `project-review`.
- **Maintenance:** `docs/MAINTENANCE.md` updated to the real flow (add/update/rename/remove/port/adapt + docs/catalog/tests/attribution sync + release handoff).
- **Installation:** `docs/INSTALLATION.md` synced for 33 packages (current branch 33, last stable `v0.1.6` 9) and clarified that Light main workflow requires neither `mattpocock/skills` nor `sol-advisor` at runtime.
- **Workflows:** `docs/workflows/` now owns repository-level composition (`project-workflow.md`, `clarification-system.md`, `execution.md`, `review-system.md`, `specialized-workflows.md` — each explains `entry → handoff → stop → optional`, not internal Skill workflows).
- **Hero:** `README.md` / `README.zh-CN.md` now use `Assets/header.png` (first line) as the repository hero; legacy editable header remains at `skills/docs/assets/skills-header.svg` / `.png` with manifest.
- **Tests:** Preserved effective behavior tests; updated architecture-locked tests to 33 packages, composition handoffs, and hero/bilingual checks.

### Changed — Lean architecture refactor

- **SKILL.md as minimal executable interface:** Full-refactor Skills (`agent-config`, `ask-light`, `clarify`, `code-review`, `decision-map`, `generic-review`, `implement`, `project-clarify`, `project-init`, `project-review`, `project-spec`, `project-tickets`, `review-loop`, `socratic`) now expose their core execution behavior directly and keep conditional formats/examples/specialized guidance in Skill-owned supporting files.
- **Composition over duplication:** `review-loop` is the lightweight review engine; `project-review` owns final `PASS`/`FAIL`/`BLOCKED`; callers name Skills instead of re-documenting their runbooks.
- **Tests:** prose-only assertions were loosened where literal wording is not a contract; root discovery/composition tests updated for the `project-review` final-acceptance command.
- **Planning state:** the previous `.scratch/light-skills-refactor/` is archived/superseded; `.scratch/light-skills-lean-refactor/` is now the active planning set with reconstruction analysis and implementation tickets.
- **Frozen integrity:** five Frozen Skills (`eli5`, `language-learning`, `kb-init`, `kanban-worker`, `learn-anything`) remain byte-for-byte unchanged and hash-verified. On 2026-08-27 the user explicitly amended the active scope for `recap`, replacing its explanatory body with one manual execution sentence.

### Changed — Functional closure

- **ask-light:** added a Light-owned 33-Skill semantic map, separated logical routing from host availability, treated UI metadata as optional, rejected generic-root provenance, added Codex/Claude/generic invocation rendering, and made the Python router the tested implementation with a PowerShell compatibility launcher.
- **Project bootstrap:** `project-init` now writes idempotent `docs/agents/light-project.md` and issue-tracker contracts; downstream Project Skills consume only their relevant fields. Ambiguous presets require a concise comparison and recommended choice.
- **Clarification:** one `$clarify` invocation now continues across normal replies; Socratic state is internal by default, recommendations are conversational, and completion requires shared-understanding confirmation. `socratic` is the sole unknown-routing owner.
- **Review ownership:** `review-loop` is the sole owner of the lightweight reviewer packet; `project-review` keeps the acceptance registry and verdict. Migration references are explicitly historical.
- **Tests:** added representative top-routing, empty-repository bootstrap/rerun, clarification lifecycle, local-pointer, ownership, and historical-runtime-boundary tests; removed repaired prose coupling instead of restoring old wording.
- **recap:** by explicit user amendment, its `SKILL.md` now keeps only required frontmatter plus one manual `$recap` execution sentence; it shows one concise line about the current session without replacing or compacting conversation history.

### Changed — Core workflow & Socratic repair

- **ask-light workflow advisor:** `ask-light` now inspects project/workflow evidence, explains the current stage, recommends the next Skill with reasoning, supports collection navigation, discovers Light roots without requiring caller-injected roots, distinguishes first-party provenance from colocated third-party packages, and transitions safely after user approval (direct execution on Codex was an intermediate state; final Unreleased behavior is defined by the current Host transition policy above).
- **Socratic frontier rounds:** `socratic` now asks the complete actionable frontier as a round of numbered independent questions with choices and recommendations, and accepts batch replies like `1B, 2A, 3C`; `clarify` and `project-clarify` use the same round interaction.
- **project-init availability:** bootstrap now classifies declared relevant capabilities as `available`, `unavailable`, or `unknown` and never silently promotes `unknown` to `available`.
- **Reviewer ownership:** `review-loop/references/reviewer-contract.md` is the single canonical runtime contract; `docs/REVIEWER_CONTRACT.md` (and zh-CN) are now human-facing summaries/pointers.
- **Header:** README hero remains `Assets/header.png` as the new repository header image.

### Changed — Review baseline integrity

- **ask-light software fixed point:** a `software`-Profile verdict is now consumable only while the current tree still matches the Charter's produced `- Fixed point:` identity on exactly the paths the recorded implementation window touched; dirty or committed drift inside that window stales any old verdict into `review-stale → project-review`, changes outside it never invalidate, and a missing, unresolvable, or undelimitable (repository-first) fixed point fails closed (`review-freshness-unknown`).
- **ask-light directory baselines:** when the Charter cites a directory source, the whole directory is the reviewed baseline — files appearing inside it after the recorded revision, including untracked ones, now stale the verdict; untracked files outside the cited directory and siblings of file-only sources stay unrelated.
- **project-review producer contract:** `references/profiles/software.md` documents the durable two-baseline record; the Charter template (`acceptance-charter.md`) gains the software-only `- Fixed point:` line and the `init` workflow freezes it with the baseline.
- **Tests:** 11 new Git-backed regression tests (17 cases) covering the §13/§14 matrix: fresh PASS, dirty/committed implementation change, unrelated-change isolation, stale FAIL/BLOCKED, missing/unresolvable/unverifiable fixed points, directory tracked modification/deletion, new untracked child, outside-directory noise, and file-source sibling isolation.

> History note: the fixed-point rule stated in this section was audited as
> fail-open (changed-file-set monitoring plus salvageable identities) and is
> **superseded before any release** by "Software review baseline contract"
> below. It is preserved verbatim because the audit trail must show what the
> earlier rule claimed, not relabel it.

### Changed — Software review baseline contract (supersedes the two-value fixed-point rule above before any release)

Human audit reproduced false `accepted` verdicts behind the earlier unreleased
rule: pre-existing in-scope files untouched by the review diff, and files
created inside the component after PASS, evaded freshness because the monitored
set was derived from the window's changed paths; malformed fixed points were
partially salvaged (invalid tokens dropped, duplicates deduplicated); and
freezing the candidate in the immutable Charter contradicted the authorized
review → bounded repair → re-review lifecycle. Fixed as a producer+consumer
contract, fail-closed throughout:

- **Three-field software baseline (producer `project-review`):** the Charter
  freezes `- Fixed point:` (exactly one full commit SHA — the immutable
  code-review base; freeze the effective delimiting commit, never a mutable
  branch name) and `- Implementation scope:` (`';'`-separated repository-
  relative literal paths — the machine projection of the approved software
  `In scope`; stable component roots, never inferred from changed paths,
  extensions, or common directories; unverifiable targets are `BLOCKED`, one
  invalid entry rejects the whole field). The final candidate is not frozen at
  `init`: every durable `PASS`/`FAIL`/`BLOCKED` records
  `- Reviewed implementation revision:` on `verdict.md`, so a legitimate C1→C2
  repair re-binds acceptance without mutating the Charter.
- **Consumer freshness invariant (`ask-light`):** a software verdict is only
  consumable when all three identities parse strictly (no salvage/dedupe),
  the base differs from and delimits the final revision with non-empty
  in-scope change, and — inside the frozen scope — tracked, staged, committed,
  and untracked additions alike still match the reviewed revision. In-scope
  drift stales ANY old verdict (`review-stale`); out-of-scope changes stay
  unrelated; whole-repo scope `.` deliberately stales on README changes (no
  hidden exceptions); old-shape records never accept (`review-freshness-unknown`)
  and require a fresh `project-review`.
- **Tests:** Git-backed matrix rewritten to ~45 cases across 22 methods:
  §10–§14 freshness matrix (changed/pre-existing/new/deleted in-scope,
  out-of-scope isolation, exact-file scope, whole-repo scope), strict
  fixed-point and final-revision grammars, scope validation incl. mixed
  valid/invalid, base/final relationship checks, FAIL/BLOCKED binding,
  legacy-record break, §16 self-staling guard, and the mandatory
  review→repair→PASS lifecycle binding to C2.
- **Docs:** `project-review` references (software profile, Charter template,
  workflow, evidence protocol, migration note) define the contract;
  `ask-light` discovery-contract carries only the concise consumer summary.

### Changed — Durable baseline hardening (singleton fields, unambiguous identities, ignored-file completeness)

Human audit reproduced three false-`accepted` classes at `52d8638`: duplicate
canonical durable fields were consumed first-match-wins (duplicate/missing
`Profile` silently skipped software freshness); multi-candidate
`Source revision or identity` values were salvaged to the first resolvable SHA;
and files hidden from `git status` by `.gitignore` / `.git/info/exclude` evaded
directory-Source and implementation-scope freshness. Closed fail-closed:

- **Singleton durable fields:** canonical producer-owned fields (`Source:`,
  `Source revision or identity:`, `Profile:` in the Charter; `Fixed point:`,
  `Implementation scope:` in the Charter; `Reviewed implementation revision:`
  on the verdict) are singleton fields — cardinality is part of validity.
  Exactly one occurrence parses; zero or more than one (even identically
  duplicated) fails closed as `review-freshness-unknown` /
  `review-ownership-unknown`, in any field order. `ask-light` never reads
  "first value wins" from an authoritative field.
- **Unambiguous Source identities:** `Source revision or identity` is usable
  only when it carries exactly one unambiguous locally resolvable Git commit;
  invalid+valid, valid+valid, duplicated, or duplicate-field values all fail
  closed with no partial salvage. Non-Git identities remain unsupported by the
  consumer (fail closed, unchanged).
- **Ignored-file completeness:** directory-Source and implementation-scope
  new-file detection now uses `git ls-files --others` (literal pathspecs,
  without `--exclude-standard`), so ignored in-scope files stale the verdict
  like any other addition. Git ignore controls status presentation, not scope
  membership; exact-file scopes, file-only Sources, and out-of-scope paths
  keep their narrow semantics.
- **Producer docs:** `project-review` references (Charter template, software
  profile, workflow) state the singleton rule and that reviewed scope
  completeness includes Git-ignored files; `ask-light` discovery-contract
  carries the consumer summary.
- **Tests:** 19 new Git-backed regression methods (122 total in the ask-light
  suite): singleton cardinality matrix incl. order independence and durable-
  record tamper through the real route path, Source-revision ambiguity matrix,
  ignored-file matrix (in-scope/out-of-scope, exact-file, whole-repo,
  directory-Source children), and valid-baseline positive controls.

### Changed — Durable review transaction coherence (charter.md + state.md + verdict.md)

Human audit reproduced false-`accepted` verdicts at `38f4f9b` when `state.md` was
active/non-terminal (READY, CRITIC, REPAIR, EVALUATE), missing, or updated to a
new Charter revision while leaving a previous PASS verdict in place. `ask-light`
now evaluates `charter.md` + `state.md` + `verdict.md` as one coherent review
transaction:

- **State file required:** `state.md` must exist and establish canonical
  singleton fields (`Status:`, `Charter revision:`, `Profile:`). Missing or
  duplicate fields fail closed as `review-state-unknown`.
- **Active state overrides old verdict:** active review states (`INIT`, `READY`,
  `CRITIC`, `REPAIR`, `EVALUATE`) immediately route to `project-review` (stage
  `project-review`); any previous `verdict.md` is non-authoritative and never
  accepted.
- **Terminal State/Verdict agreement:** terminal review states (`PASS`, `FAIL`,
  `BLOCKED`) require an agreeing `verdict.md`; conflicts fail closed as
  `acceptance-unknown`.
- **Charter revision & Profile coherence:** `state.md` must match `charter.md`
  on both `Charter revision` and `Profile`; mismatches fail closed as
  `review-state-unknown`.
- **Tests & smoke:** 15 new test methods (300 total tests in pytest suite, 137
  in ask-light suite) covering the full transaction matrix, reopen lifecycle,
  Charter update lifecycle, C1→repair→C2 lifecycle, and 24 manual smoke
  scenarios on real durable state.

### Changed — Terminal review transaction identity binding (State & Verdict Round, mandatory Verdict identity, unique conclusion)

Fixed a false-`accepted` defect at `d414a3b` where a terminal State (e.g. Round 2 PASS) could accept an old-round PASS verdict (Round 1) because `Round` was not bound, and Verdict-side Charter revision and Profile were optional. Finished the durable review transaction contract:

- **Round binding (`state.md` + `verdict.md`):** `Round` is a mandatory canonical singleton field in `state.md` (`review-state-unknown` if missing/duplicate/malformed) and terminal `verdict.md` (`acceptance-unknown` if missing/duplicate/malformed/mismatched). Canonical producer syntax (`1`, `2`, `round-01`, `round-01 (final)`) is parsed into a normalized review round identity.
- **Mandatory Verdict identity:** `Charter revision:` and `Profile:` are mandatory singleton fields on terminal `verdict.md`; missing, duplicate, or mismatched values fail closed as `acceptance-unknown`.
- **Unique terminal verdict semantics:** terminal conclusion set (`PASS`, `FAIL`, `BLOCKED`) must resolve to exactly one unambiguous conclusion; multiple or conflicting conclusions (`PASS+FAIL`, `PASS+BLOCKED`, `FAIL+BLOCKED`, `PASS+FAIL+BLOCKED`) fail closed as `acceptance-unknown`.
- **Safe closeout ordering:** producer documentation (`WORKFLOW.md`) explicitly specifies the fail-safe closeout sequence (`write current-round verdict → verify durable fields → set state terminal`) ensuring intermediate states fail closed.
- **Tests & smoke:** 6 new test methods (306 total tests in pytest suite, 143 in ask-light suite) covering the complete transaction identity matrix, Round mismatch, Verdict identity requirements, terminal conclusion uniqueness, SPEC §14 reopen round lifecycle, and 24 manual smoke scenarios.

### No redesign verification

18 `NO REWRITE/PORT` Skills were `git diff` checked (SPEC §26): `manuscript-ops`, `kb-init`, `learn-anything`, `language-learning`, `kanban-worker`, `eli5`, `release-workflow`, `research`, `prototype`, `tdd`, `handoff`, `diagnosing-bugs`, `wizard`, `teach`, `wait-what`, `to-questionnaire`, `writing-for-agents`, `resolving-merge-conflicts` — only minimal handoff/attribution wiring where a real integration need existed. `recap` is the separately recorded user-approved exception above.

### Release evidence

- No version, tag, or GitHub Release created for this refactor.
- The `humanizer` admission and the post-release hardening above extend the `v0.2.0` release line; the tag was re-pointed to commit `e063753` and fresh released-repository installation verification passed (CLI `1.5.23`; whole collection — 34 packages, 257 files byte-identical — and per-Skill `humanizer`) — see [INSTALLATION_VERIFICATION_ADDENDUM.md](docs/evidence/releases/v0.2.0/INSTALLATION_VERIFICATION_ADDENDUM.md).
- Discovery/composition/link/hero/bilingual and package-contract checks: see `tests/` and `python -m unittest discover`.

## 0.1.6 — 2026-08-19

### Added

- First-party `kb-init` Skill: the formal knowledge-base initialization package replaces the earlier unreleased draft. It adds expanded core principles (decision provenance, open-decision surfacing, depth before settlement), readiness checks, human-navigation design, a research contract, connection setup/validation, backup/recovery semantics, and 38 regression eval cases. It remains user-invoked only per owner decision.
- Contract tests and bilingual user guides updated for the formal kb-init package.
- v0.1.6 publishes the nine-package collection: v0.1.1's five, `recap` and `language-learning` (v0.1.2), `kanban-worker` (renamed from `light-kanban-worker` in v0.1.6; first released in v0.1.4), and `kb-init`.

### Changed

- `light-kanban-worker` was renamed to `kanban-worker`. The package directory, `SKILL.md` name/frontmatter, `agents/openai.yaml`, tests, guides, catalog, README, and installation surfaces now use `kanban-worker`. Historical v0.1.4 and v0.1.5 records retain the old name with a migration note.
- `kb-init` stays explicit-only: `disable-model-invocation: true` in `SKILL.md` and `allow_implicit_invocation: false` in `agents/openai.yaml`.
- README, catalog, installation guide, maintenance baseline, discovery tests, and bilingual guides updated from the v0.1.5 eight-package release boundary to the v0.1.6 nine-package release.

### Release evidence

- Release tag: `v0.1.6`, commit `e8c3589031bbc1cb76d7f928761ce3f60ebea3e1`.
- GitHub Actions `collection-quality`: PASS on the release commit (run `32232850422`).
- Fresh whole-collection and per-Skill installs: PASS with the documented CLI for both generic `latest` and pinned `#v0.1.6` forms; see [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.6/INSTALLATION_VERIFICATION.md).
- Host discovery: [DISCOVERY_VERIFICATION.md](docs/evidence/releases/v0.1.6/DISCOVERY_VERIFICATION.md).
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.6
- Final receipt: [RELEASE_RECEIPT.md](docs/evidence/releases/v0.1.6/RELEASE_RECEIPT.md).

## 0.1.5 — 2026-08-17

### Changed

- `light-kanban-worker` now explicitly forbids overlapping scheduled runs with the same `LIGHT_KANBAN_AGENT_ID`: at most one invocation per agent id may be active, a wake that fires while the previous run is still active must skip, and different agent ids may still run concurrently. The atomic claim boundary is documented accurately — atomic claim protects two different workers claiming the same To Do task and is not a concurrency lock for multiple invocations using the same agent identity; concurrency control stays with the scheduler / agent runtime (`max concurrent runs = 1` or an equivalent skip-while-active setting), and the worker adds no lock process, heartbeat, or lease service.
- First registration now clearly requires ID + name + avatar. A local image is uploaded through `POST /api/avatars` and the returned `/api/avatars/...` path is used for the claim; an existing agent id reuses the server's stored name/avatar, so later wakes do not repeat the avatar. A new agent id without a name or avatar reports identity configuration missing, claims nothing, and mutates nothing.
- `agents/openai.yaml` default prompt updated to the first-run-capable one-shot form (Agent ID / Name / Avatar) so a fresh board can register a new agent identity.

### Tests

- Worker contract suite extended with the scheduling-boundary rules: same-agent non-overlap, different-agent concurrency, atomic-claim boundary, scheduler ownership of concurrency, no resident lock service, first-registration identity, identity reuse, missing-identity no-mutation, and the local avatar upload path.
- New adversarial negative fixtures `overlap-allowed-variant.md` and `avatar-optional-first-registration.md`; each violates exactly one rule and must be rejected.
- Behavior suite adds Scenario G (same-agent concurrent wake: the second run must not start while run #1 is active, verified through a scheduler-guard fixture — Light-Kanban itself provides no run lease) and Scenario H (fresh identity without avatar: no claim, no mutation, clear configuration failure; a legal avatar then makes registration and claim succeed). Scenarios A–F remain unchanged and passing.
- Release evidence workflow clarified: the receipt now separates the pre-release gate (candidate tests, admission, catalog sync — `READY FOR RELEASE`) from post-release verification (published tag identity, fresh install, host discovery, release CI), so a published tag no longer shows unexplained `PENDING` markers.

### Evidence

- Release tag: `v0.1.5`, commit `a56aa9d98de0b941ee2282144bc7e756ef5e48bd`.
- GitHub Actions `collection-quality`: `PASS` on the release commit (run `31985455493`).
- `review-loop agent-skill` acceptance for the contract change: PASS with full independence (findings F-001/F-002/F-003/G-001 repaired) — [AGENT_SKILL_REVIEW.md](docs/evidence/releases/v0.1.5/AGENT_SKILL_REVIEW.md).
- Fresh installs: whole-collection and per-Skill, generic `latest` and pinned `#v0.1.5` forms, CLI `1.5.22` — PASS; installed package byte-identical to the tag and its suites run standalone. See [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.md).
- Host discovery: [DISCOVERY_VERIFICATION.md](docs/evidence/releases/v0.1.5/DISCOVERY_VERIFICATION.md).
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.5
- Final receipt (pre-release gate + post-release verification): [RELEASE_RECEIPT.md](docs/evidence/releases/v0.1.5/RELEASE_RECEIPT.md).

## 0.1.4 — 2026-08-16

### Added

- New first-party, model-invoked `light-kanban-worker` Skill: each scheduled agent run processes at most one Light-Kanban task — stable agent identity, owned in-progress work and `reviewFeedback` checked before new claims, atomic claim with bounded conflict retry, workspace validation (an inaccessible workspace becomes `block` with a meaningful reason), and `complete` back to human confirmation. The worker never archives, accepts, deletes, recycles, or unblocks tasks, and never loops or starts a resident process. Network/filesystem/state side effects place it on the full admission path (`review-loop agent-skill`), not the prompt-only fast track.
- Contract and behavior test suites for the worker package with positive and negative fixtures (adversarial single-rule fixture files) and a frontmatter YAML-safety gate.
- A negative outside-readable-path scenario in the ask-light behavior suite.

### Changed

- Version documentation synchronized: v0.1.4 is the current stable release, v0.1.3 and earlier remain historical records. README, catalog, installation guide, maintenance baseline, discovery tests, and CI updated for the eight-package collection.
- Fixed the ask-light scanner's `Test-PathUnder` path comparison, which hardcoded Windows separators and made the collection-quality workflow fail on ubuntu-latest since the v0.1.3 Python port.

### Release evidence

- Release tag: `v0.1.4`, commit `a9cc8aa029c926fc80f6ddc0022793f79dfd85bd`.
- GitHub Actions `collection-quality`: `PASS` on the release commit (run `31962459531`).
- Fresh whole-collection and per-Skill installs: `PASS` with CLI `1.5.22` for both the generic `latest` and pinned `#v0.1.4` forms.
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.4
- Whole-collection and per-Skill fresh-install evidence: [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.4/INSTALLATION_VERIFICATION.md).
- Structural and package evidence: [TEST_SUMMARY.md](docs/evidence/releases/v0.1.4/TEST_SUMMARY.md).
- Admission: [light-kanban-worker evidence](docs/evidence/admissions/light-kanban-worker/README.md).
- Scanner code-review: [CODE_REVIEW.md](docs/evidence/releases/v0.1.4/CODE_REVIEW.md).
- Independent `review-loop agent-skill` acceptance for the original five packages remains `BLOCKED`; see the [release receipts](docs/evidence/releases/).

## 0.1.3 — 2026-08-10

### Changed

- Test toolchain migrated from Windows PowerShell to cross-platform Python: 21 PowerShell test files replaced by 18 Python suites (collection discovery, header assets, quick start, ask-light contract, project-init contract and behavior, recap contracts, language-learning contract, and review-loop five-profile contract and behavior suites plus protocol helpers), preserving the assertion sets.
- The ask-light behavior suite executes the portable Python router on every host; `scripts/ask-light.ps1` remains a thin compatibility launcher.
- CI moved to `ubuntu-latest` (bash + python); retired-boundary and no-PowerShell-test checks added.
- Documentation updated for the new test file names and the cross-platform manual-fallback snippet; governance wording unchanged.

### Evidence

- [docs/evidence/releases/v0.1.3/](docs/evidence/releases/v0.1.3/)

## 0.1.2 — 2026-08-10

### Added

- Prepared the first-party, user-invoked `recap` Skill for v0.1.2. Explicit `$recap` invocation returns exactly one line about the current session, never runs tools, continues work, changes files, compacts history, or invokes another Skill.
- Prepared the first-party, user-invoked `language-learning` Skill for v0.1.2. It tutors any target language through six study modes — daily lessons, flashcards, conversation practice, grammar decoding, progress quizzes, and immersion translation — reusing session context and previously learned vocabulary across invocations instead of re-asking.
- Added a low-risk prompt-only admission fast track for owner-authored, manual-only, text-output Skills with no tools, side effects, runtime executables, or external dependencies. It uses one fresh Evaluator and does not require separate Critic or Standards/Spec review.
- Published the generic `latest` install command (`npx skills add LightDevCoder/skills --yes --copy --agent '*'`) as the standard install path, with the pinned `#v0.1.2` form retained for reproducible installs. `recap` and `language-learning` were both admitted by a fresh independent prompt-only fast-track Evaluator `PASS`; see their [admission evidence](docs/evidence/admissions/).

### Release evidence

- Release tag: `v0.1.2`, commit `8de5ec1a453b0e93f71dcda160e17ea7b42c3997`.
- GitHub Actions `collection-quality`: `PASS` on the merged release commit.
- Fresh whole-collection and per-Skill installs: `PASS` with CLI `1.5.22` for both the generic `latest` and pinned `#v0.1.2` forms.
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.2
- Whole-collection and per-Skill fresh-install evidence: [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.md).
- Structural and package evidence: [TEST_SUMMARY.md](docs/evidence/releases/v0.1.2/TEST_SUMMARY.md).
- Independent `review-loop agent-skill` acceptance for the original five packages remains `BLOCKED`; see the [release receipt](docs/evidence/releases/v0.1.2/RELEASE_RECEIPT.md).

## 0.1.1 — 2026-07-26

### Added

- Bilingual user guides for all five first-party Skills, validated workflow recipes, and a runnable-sized Quick Start example.
- A release evidence tree under `docs/evidence/releases/v0.1.1/` and CI checks for structure, metadata, links, bilingual pairs, package tests, retired references, and header assets.
- Explicit `$ask-light next` and `$ask-light workflow` modes with bounded recipe output, availability gaps, handoff fields, and non-execution tests.
- A redesigned editable SVG and 1600 × 480 PNG header with a flat layered `LightDevCoder` / `/skills` wordmark and serif slogan.

### Fixed

- Added `policy.allow_implicit_invocation: false` and matching frontmatter to the user-invoked `learn-anything`, `ask-light`, and `project-init` packages.
- Corrected installation language: an unqualified repository source follows the CLI's default revision, while `#v0.1.1` will pin the target tag once published.

### Release evidence

- Release tag: `v0.1.1`, commit `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`.
- GitHub Actions `collection-quality`: `PASS` on the merged release commit.
- Fresh whole-collection and per-Skill installs: `PASS` with CLI `1.5.20`.
- GitHub release: https://github.com/LightDevCoder/skills/releases/tag/v0.1.1
- Whole-collection and per-Skill fresh-install target evidence: [INSTALLATION_VERIFICATION.md](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md).
- Structural and package evidence: [TEST_SUMMARY.md](docs/evidence/releases/v0.1.1/TEST_SUMMARY.md).
- The five-package collection remains installable and its collection-quality checks passed. Independent evaluator evidence for the `review-loop agent-skill` acceptance gate remains `BLOCKED`; this does not block ordinary installation or use. See the [release receipt](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.md) for the exact evidence boundary.

## 0.1.0 — 2026-07-23

- Established the first-party governance foundation and admitted the five first-party Skills.
- Published at https://github.com/LightDevCoder/skills.
- Stable tag: v0.1.0.
- The v0.1.0 whole-collection and per-Skill installer commands were verified against a fresh destination and the published package content; this historical evidence is retained alongside the v0.1.1 release.
- Historical commands: `npx skills add LightDevCoder/skills` and `npx skills add LightDevCoder/skills --skill review-loop`.
- Historical installation details: [v0.1.0 summary](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.md#historical-v0.1.0-summary).
