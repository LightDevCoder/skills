# Light Skills Core Flow Repair — Results

Status: LOCAL COMMIT PENDING (final targeted repair complete; awaiting human review)

## What changed

This repair did not reopen architecture work. It targeted the remaining gaps
found in human review.

### Files changed

```text
docs/skills/ask-light.md
docs/workflows/first-party-composition.md
docs/workflows/recipes.md
docs/zh-CN/skills/ask-light.md
docs/zh-CN/workflows/first-party-composition.md
docs/zh-CN/workflows/recipes.md
skills/ask-light/SKILL.md
skills/ask-light/references/discovery-contract.md
skills/ask-light/scripts/ask_light.py
skills/ask-light/tests/test_ask_light_behavior.py
skills/project-clarify/SKILL.md
skills/project-clarify/references/WORKFLOW.md
skills/project-clarify/references/project-clarification-contract.md
skills/project-clarify/scripts/session_state.py
skills/project-clarify/tests/test_project_clarify_behavior.py
skills/socratic/scripts/frontier.py
skills/socratic/tests/test_socratic_behavior.py
.scratch/light-skills-core-flow-repair/smoke/codex-smoke-attempt.md
.scratch/light-skills-core-flow-repair/results.md
```

The duplicate `skills/SPEC-light-skills-core-workflow-socratic-repair.md` was
already absent from the working tree; no duplicate remains.

## Validation results

Commands actually executed in this working copy:

```text
python3 -m pytest -q
→ 202 passed

python3 -m unittest discover -s tests
→ Ran 27 tests; OK

python3 -m compileall -q skills tests
→ OK

Skill-local unittest suites:
  skills/ask-light/tests .......... 42 tests, OK
  skills/socratic/tests ........... 18 tests, OK
  skills/clarify/tests ............  5 tests, OK
  skills/project-clarify/tests .... 11 tests, OK
  skills/project-init/tests ....... 32 tests, OK
  skills/review-loop/tests ........ 19 tests, OK
```

## Project-state detection scenarios tested

Executable tests use real temporary repositories with evidence files, not
conclusion-bearing input text:

| Scenario | Evidence | Recommended Skill |
| --- | --- | --- |
| Initialized project, no SPEC, clear goal | `docs/agents/light-project.md` with Goal/Outputs | `project-spec` |
| Initialized project, no SPEC, unclear goal | `docs/agents/light-project.md` with `Goal: ?` | `project-clarify` |
| Stable SPEC, no tickets | `docs/SPEC.md`, no `.scratch/*/issues/*.md` | `project-tickets` |
| Tickets exist, work incomplete | `.scratch/*/issues/*.md` with `Status: open` | `implement` |
| Tickets resolved, acceptance missing | `.scratch/*/issues/*.md` with `Status: resolved`, no acceptance evidence | `project-review` |

## Natural-language family navigation tested

Exact phrases from the task are covered by behavior tests:

- `What project skills do I have?` → project family only
- `Show me the review skills` → review family only
- `Which skills are for learning?` → learning family only
- `What can I use for bugs?` → `diagnosing-bugs`
- `What's the difference between clarify and project-clarify?` → comparison, no broad search noise

## Socratic parser formats tested

- `1B, 2A, 3C`
- `1: B` / `2: A` / `3: C` (newline-separated)
- `Q1: B` / `Q2: A` / `Q3: C`
- Qualified answers: `Q2: B, but only locally`
- Partial answers: `1B, 3C` (unanswered decisions remain open)

Dependency gating and multi-question frontier tests remain in place; no hard
global small-question limit was reintroduced.

## project-clarify continuous session

Added `skills/project-clarify/scripts/session_state.py` and a behavior test
proving one explicit `$project-clarify` invocation → repeated normal replies
→ confirmation → handoff/done. The `SKILL.md` and contract now state that
ordinary replies continue the session and the user does not repeat the
invocation.

## Codex smoke result

A real Codex attempt was made:

- Prepared a temp project with stable SPEC and no tickets (expected next:
  `project-tickets`).
- Used isolated `CODEX_HOME` with auth/config symlinks and all repository
  Skill packages symlinked into `$CODEX_HOME/skills/`.
- Invoked `codex exec` with `$ask-light`.
- The CLI started but terminated before model interaction:

```text
ERROR: You've hit your usage limit. Upgrade to Pro ... or try again at Sep 1st, 2026 11:48 PM.
```

Evidence: `.scratch/light-skills-core-flow-repair/smoke/codex-smoke-attempt.md`.

## Approval-to-execution: honest status

**Not truly supported for user-invoked targets in this repository.** The
repository invocation policy says a user-invoked Skill must not auto-invoke
another user-invoked Skill. `ask-light` is user-invoked, and the normal
project-stage recommendations (`project-clarify`, `project-spec`,
`project-tickets`, `implement`, etc.) are user-invoked. Therefore after
approval `ask-light`:

- may begin a **model-invoked** accepted Skill where the host supports that
  (e.g. `project-review`);
- for a **user-invoked** accepted Skill renders the exact invocation
  (`$<skill>` on Codex, `/<skill>` on Claude Code) and asks the user to start
  it.

The deterministic helper now exposes this as `Next:
host-transition-required` vs `Next: beginning-<skill>`. The contract, docs,
and tests were updated to stop claiming a direct Codex transition without
evidence. The real Codex smoke could not complete because of the account usage
limit, so even the model-invoked direct-start path remains **unverified on
Codex**.

## Known limitations

- Real Codex interaction smoke could not be completed: Codex CLI is present
  but the account is at its usage limit. No transcript exists.
- Direct approval-to-execution for user-invoked targets is prohibited by
  repository policy, not merely unverified.
- The model-invoked `beginning-<skill>` path is deterministic in the helper
  but has not been observed in a live Codex run.

## Stop status

Repository is ready for human review after the local commit. Nothing pushed,
tagged, or released. No untracked artifacts will remain after commit.