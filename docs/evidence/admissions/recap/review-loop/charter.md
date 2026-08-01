# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-08-01T17:08:16+08:00

## Acceptance baseline
- Source: user request in the active Codex task plus `AGENTS.md`, `docs/SKILL_ADMISSION.md`, `docs/MAINTENANCE.md`, and `docs/REVIEW_POLICY.md`
- Source revision or identity: explicit request to reproduce Claude Code's recap as a manual-only Skill and prepare a mergeable `main` PR; Anthropic documentation checked 2026-08-01
- Approval state: approved
- Approval evidence: user explicitly requested manual-only behavior, repository admission, and a `main`-targeted mergeable change

## Review Profile
- Profile: agent-skill
- Selection reason: the target is an installable Agent Skill whose installation, discovery, invocation, and behavior must be accepted

## Original goal
Add a first-party `recap` Skill that reproduces Claude Code's on-demand one-line session recap while supporting manual invocation only, install it locally, and prepare a repository change that can merge into `main`.

## User-visible outcome
Explicit `$recap` returns exactly one concise line about the current Agent session; it never triggers implicitly, runs tools, changes files, compacts history, continues work, or invokes another Skill.

## In scope
- `skills/recap/` package contract, metadata, and tests
- first-party catalog, bilingual guides, installation boundary, workflow examples, discovery tests, CI, changelog, and admission evidence
- current-branch fresh-copy installation and independent review

## Out of scope
- Claude Code's automatic focus/idle recap trigger
- copying Anthropic source code or proprietary prompt text
- tagging or publishing a new release
- claiming a released pinned install command before a new tag exists

## Acceptance criteria
- AC-1: Package structure, metadata, links, and resources are valid and the package is independently authored first-party work.
- AC-2: Both Claude-facing and Codex-facing metadata prohibit implicit invocation.
- AC-3: Explicit invocation produces exactly one unlabeled line grounded in current session context without tool use or state changes.
- AC-4: Little-context and non-trigger scenarios preserve the declared boundary without invented progress or silent invocation.
- AC-5: A fresh-copy per-Skill installation discovers only `recap`, preserves the complete package, and works without a source checkout in the destination.
- AC-6: Catalog, bilingual documentation, maintenance baseline, workflow examples, collection tests, CI, and changelog agree on six packages on `main` versus five in stable v0.1.1.
- AC-7: No runtime executable dependency is introduced; package tests contain non-zero assertions and cover positive and negative output boundaries.
- AC-8: A fresh read-only Critic and a separate fresh read-only Evaluator assess the package under the `agent-skill` Profile, with no unresolved blocking finding.

## Required evidence
- approved source and official behavior references (`source`)
- package tree, metadata, hashes, links, and test results (`structural`)
- fresh-copy install and discovery (`installation`)
- explicit success, empty-session boundary, and non-trigger observations (`behavioral` and `invocation`)
- independent Critic and Evaluator records (`review`)

## Required validation scenarios
- VS-1: explicit `$recap` after completed work returns exactly one line with result and state
- VS-2: explicit `$recap` with no prior activity returns one safe line without invented progress
- VS-3: a request that does not explicitly invoke `$recap` does not trigger the Skill
- VS-4: multiline and labeled output are rejected by package tests
- VS-5: isolated local-source installation selects only `recap`, preserves hashes, and runs installed package tests
- VS-6: collection and package quality checks pass

## Constraints, assumptions, and risks
- The current candidate is unreleased; local-source fresh-copy evidence is admission evidence, not published-release proof.
- The Skill implements documented observable behavior independently and does not copy Anthropic code or prompt text.
- Maximum review rounds: 3.

## Approved exceptions
- None
