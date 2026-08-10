# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-08-10T12:40:00+08:00

## Acceptance baseline
- Source: repository governance (`AGENTS.md`, `docs/SKILL_ADMISSION.md`, `docs/MAINTENANCE.md`) and the user's explicit request to improve and admit a language-learning Skill, then run the review-loop fast-track admission
- Source revision or identity: `skills/language-learning/` at commit `215c65ccbfd323c3f43265c45ddcbae5962b7818` (`main`, 2026-08-10); promotion route is the low-risk prompt-only fast track in `docs/SKILL_ADMISSION.md`
- Approval state: approved
- Approval evidence: user requested the improvement and the fast-track admission run; prompt-only fast-track policy is already adopted in this repository

## Review Profile
- Profile: agent-skill
- Selection reason: the target is an installable Agent Skill package whose installation, discovery, invocation, behavior, and interaction boundaries must be accepted

## Original goal
Admit a first-party, user-invoked `language-learning` Skill that tutors any target language through six study modes, reuses session context instead of re-asking, corrects selectively, and evaluates progress, so that the collection grows from six to seven packages on this branch.

## User-visible outcome
`$language-learning` runs as a user-invoked-only tutor: it inherits the target language, learner level, native language, and recent vocabulary from the conversation, defaults to beginner when the level is unknown, and routes to daily lessons, flashcards, conversation, grammar decoding, progress quizzes, or immersion without invoking another user-invoked Skill.

## In scope
- `skills/language-learning/` package contract, metadata, references, and tests
- first-party catalog, bilingual guides, installation boundary, discovery tests, CI, changelog, maintenance baseline, and admission evidence
- current-branch fresh-copy installation, fresh Agent behavior and invocation observations, and independent fast-track review

## Out of scope
- adding new study modes beyond the existing six
- adding runtime executable scripts, hooks, installers, external services, or dependencies
- tagging or publishing a new release
- claiming a released pinned install command before a new tag exists

## Acceptance criteria
- AC-1: Package structure, metadata, links, and resources are valid and the package is independently authored first-party work.
- AC-2: Both Claude-facing and Codex-facing metadata prohibit implicit invocation; the package is user-invoked only.
- AC-3: Explicit invocation routes to a declared study mode and produces the mode's contract output (lesson, cards, conversation, rule decode, quiz with evaluation, or immersion follow-up).
- AC-4: The Start and Teaching Behavior contract reuses session context and does not re-ask for language, level, or mode on every invocation.
- AC-5: A fresh-copy per-Skill installation discovers only `language-learning`, preserves the complete package, and works without a source checkout in the destination.
- AC-6: Catalog, bilingual documentation, maintenance baseline, collection tests, CI, and changelog agree on seven packages on `main` versus five in stable v0.1.1.
- AC-7: No runtime executable dependency is introduced; package contract tests contain non-zero assertions and cover positive and negative boundaries.
- AC-8: The package never invokes another user-invoked Skill; hand-offs to other first-party capabilities are recommendations only.
- AC-9: A fresh read-only independent Evaluator assesses the package under the `agent-skill` Profile with no unresolved blocking finding.

## Required evidence
- approved governance source and package revision identity (`source`)
- package tree, metadata, hashes, links, and test results (`structural`)
- fresh-copy install and discovery (`installation`)
- explicit-use success, boundary, and non-trigger observations (`behavioral` and `invocation`)
- independent Evaluator record (`review`)

## Required validation scenarios
- VS-1: explicit `$language-learning` with an established level and target language produces a routed mode output without re-asking for language, level, or mode
- VS-2: explicit `$language-learning` with an unknown level defaults to beginner
- VS-3: a request that does not explicitly invoke `$language-learning` does not trigger the Skill
- VS-4: contract tests reject an opposite-polarity mutation of the selective-correction and context-reuse rules
- VS-5: isolated fresh-copy installation selects only `language-learning`, preserves hashes, and runs the installed contract tests
- VS-6: collection and package quality checks pass with seven packages

## Constraints, assumptions, and risks
- The current candidate is unreleased; fresh-copy and host-install evidence is admission evidence, not published-release proof.
- The Skill is an original first-party design and does not copy upstream Skill code or prompt text.
- Maximum review rounds: 3.

## Approved exceptions
- None
