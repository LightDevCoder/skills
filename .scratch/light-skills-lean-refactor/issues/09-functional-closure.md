# 09 — Functional closure pass

Status: in-progress
Authority: `../spec.md` plus the user-supplied Functional Closure Pass

## Scope

- Prove full-package capability coverage before simplifying references.
- Separate `ask-light` logical routing from host availability and provenance.
- Make `project-init` produce an idempotent Light project contract consumed by downstream Project Skills.
- Make one `$clarify` invocation continue across normal replies with concise, recommendation-bearing Socratic turns and a confirmation synthesis.
- Replace repaired prose assertions with functional boundary tests.
- Preserve Frozen packages byte-for-byte and Integration-only behavior, except
  for the user-approved 2026-08-27 manual-only `recap/SKILL.md` amendment.
- Keep the unamended package-local `recap/tests` files frozen as historical
  records; validate the amended contract in the active repository-level suite.

## Acceptance

- [x] Capability ownership audit is complete.
- [x] Representative intent phrases route to the correct top Light Skill.
- [x] Empty-repository bootstrap and rerun tests pass.
- [x] Clarification sequence contract covers entry, continuation, recommendation, synthesis, and confirmed stop.
- [x] Local pointers resolve and repaired sibling ownership has one runtime source.
- [x] Canonical active suites, amended Frozen hashes, and Integration-only diff checks pass.
- [ ] Fresh independent review accepts the accumulated diff.
- [x] Work is committed locally and not pushed.

## Review boundary — 2026-08-27

The accumulated diff is ready for human review in local commits
`b671a90ac10b5777a50ca897a03242cc51949478` and `b6e0515`. A fresh independent
Sol review was requested against `28ce785..HEAD`, but the reviewer thread was
blocked by the Codex usage limit. The direct `codex review --base 28ce785`
attempt was blocked by the same limit before inspecting the diff. These are
availability blockers, not review verdicts; the acceptance checkbox remains
open and this issue stays `in-progress` until a fresh independent review can
run or the owner completes the human review.
