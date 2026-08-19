# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-08-18

## Acceptance baseline
- Source: user request to add `/Users/light/Downloads/kb-init` into the first-party skills library without cutting a new release
- Source revision or identity: the kb-init package in `Downloads/kb-init` plus the repository governance docs (`AGENTS.md`, `docs/SKILL_ADMISSION.md`, `docs/MAINTENANCE.md`, `docs/REVIEW_POLICY.md`)
- Approval state: approved
- Approval evidence: user explicitly requested the admission and specified no new release tag

## Review Profile
- Profile: agent-skill
- Selection reason: the target is an installable Agent Skill package whose installation, discovery, invocation, behavior, and interaction boundaries must be accepted (Skills-repo admission contract full path; the prompt-only fast track does not apply because kb-init can use tools, call the model-invoked `research` capability, and create files/state)

## Original goal
Admit the first-party, user-invoked `kb-init` Skill into the LightDevCoder/skills collection as the ninth package and release it in v0.1.6.

## User-visible outcome
Explicit `kb-init` runs a knowledge-base-specific interview, performs Base Discovery when a base is selected, produces an implementation SPEC, and only after explicit user approval implements, validates, and hands off the knowledge base.

## In scope
- `skills/kb-init/` package: `SKILL.md`, `agents/openai.yaml`, `references/`, `evals/`, `tests/`
- Package admission into the first-party collection (full admission path)
- Collection synchronization: catalog, README, installation guide, maintenance baseline, discovery/contract tests, bilingual guides, changelog (Unreleased)

## Out of scope
- Creating a new GitHub release/tag for `kb-init`
- Published-tag fresh-install verification for `kb-init`
- Changing the stable v0.1.5 release record

## Acceptance criteria
- AC-1: package structure and metadata are valid (`SKILL.md` name/description/`disable-model-invocation: true`; `agents/openai.yaml` has display_name/short_description/default_prompt/allow_implicit_invocation: false)
- AC-2: invocation type is user-invoked only and forbids implicit trigger and chaining another user-invoked Skill
- AC-3: fast-track classification is correct: full path applies because tools/research/file state are possible
- AC-4: references cover interview contract, design guide, base discovery, and SPEC guide with the required design areas
- AC-5: contract test passes with non-zero assertions, including positive and negative mutation checks
- AC-6: documentation synchronization is complete for the nine-package current branch while v0.1.5 stays the eight-package stable release
- AC-7: the admission record does not claim release verification; v0.1.6 released-tag fresh-install verification is recorded separately under docs/evidence/releases/v0.1.6/
- AC-8: fresh independent Evaluator returns `PASS`

## Required evidence
- structural: package tree, metadata, reference files, evals, contract test run
- invocation: frontmatter + openai.yaml explicit-only declarations and invocation-direction rules in SKILL.md
- review: fresh read-only Evaluator judgment
- documentation synchronization: README/catalog/installation/maintenance/changelog/guides/tests conformance

## Required validation scenarios
- VS-1: `python3 skills/kb-init/tests/test_kb_init_contract.py` passes
- VS-2: `python3 -m unittest discover -s tests -p "test_*.py"` passes after admission evidence exists
- VS-3: all relative links in updated Markdown resolve
- VS-4: evals/evals.json cases cover automatic interview start, user-question handling, no auto-SPEC, research detour, explicit end, and approval gate

## Constraints, assumptions, and risks
- The candidate is released in v0.1.6; local-source/structural evidence is admission evidence, and released-tag fresh-install verification is a separate release gate.
- `evals.json` is a semantic regression fixture, not an executed model-evaluation harness; it is reviewed as spec coverage.
- Maximum review rounds: 3.

## Approved exceptions
- None
