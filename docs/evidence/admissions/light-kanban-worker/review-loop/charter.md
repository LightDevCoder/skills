# Acceptance Charter

## Revision
- Charter revision: 1
- Supersedes: none
- Created at: 2026-08-16 (session start of the Light-Kanban v1.0.5 / Skills v0.1.4 release work)

## Acceptance baseline
- Source: direct user-provided SPEC — "Light-Kanban v1.0.5 — Agent Worker Integration SPEC" (this session's request message)
- Source revision or identity: the SPEC as received at session start; worker-skill sections 4–35, 57–58, and Definition-of-Done section 69
- Approval state: approved
- Approval evidence: the SPEC is the user's direct instruction for this work

## Review Profile
- Profile: agent-skill
- Selection reason: the target is an installable Agent Skill package whose installation, discovery, invocation, behavior, and interaction boundaries must be accepted (Skills-repo admission contract, docs/SKILL_ADMISSION.md full path)

## Original goal
Admit the first-party, model-invoked `light-kanban-worker` Skill into the LightDevCoder/skills collection so a scheduled agent can periodically pick up, execute, and return one Light-Kanban task for human confirmation.

## User-visible outcome
A scheduled agent run that invokes `light-kanban-worker` handles at most one Light-Kanban task: resumes owned work (review feedback first), claims new FIFO work atomically, validates the workspace, executes, then completes for human review or blocks with a meaningful reason — without daemons, polling loops, or auto-archiving.

## In scope
- `skills/light-kanban-worker/` package: `SKILL.md`, `agents/openai.yaml`, `references/api.md`, `tests/` (contract, behavior, fixtures, shared checkers)
- Package admission into the first-party collection (full admission path, not the prompt-only fast track)
- Collection synchronization required by the admission: catalog, README, installation guide, maintenance baseline, discovery/contract tests, bilingual guides, changelog (unreleased v0.1.4 candidate)

## Out of scope
- Light-Kanban repository changes (README rewrite, Use Cases, v1.0.5 release) — separate acceptance under the same SPEC
- Publishing the v0.1.4 tag and the published-tag fresh-install verification — release gate, recorded in docs/evidence/releases/v0.1.4/
- Light-Kanban UI changes, new task states, daemons, WebSockets, auth, scheduler (explicitly not required by the SPEC)

## Acceptance criteria
- AC-1: package structure and metadata are valid (SKILL.md frontmatter name, description, required workflow sections; agents/openai.yaml display_name/short_description/default_prompt/allow_implicit_invocation) — SPEC §4, §6, §33
- AC-2: invocation type is model-invoked and permits explicit manual use; no `disable-model-invocation: true`; scheduled invocation supported — SPEC §6–7
- AC-3: stable agent identity; existing agent identity reused from the board; first registration requires a legal name and avatar (upload or http(s) URL); no guessed identity — SPEC §8–11
- AC-4: existing owned work is checked before new work; reviewFeedback work has priority; at most ONE task per run — SPEC §12–16
- AC-5: atomic claim conflicts are handled with bounded retry (max 2 attempts), no infinite loop — SPEC §17
- AC-6: no work → "No task available", clean exit, no task creation, no waiting — SPEC §18
- AC-7: workspace validated on the agent host; inaccessible workspace → block with "Workspace path is not accessible from this agent host." — SPEC §19, §21
- AC-8: success → POST complete → awaiting_confirmation → stop; the worker never archives/accepts/deletes/recycles/unblocks; post-claim failure blocks with a meaningful reason; pre-claim failure mutates nothing — SPEC §24–30
- AC-9: no daemon, background service, polling loop, sleep, or runtime scripts shipped — SPEC §18, §32
- AC-10: API reference covers GET /api/agents, GET /api/tasks?status=in_progress, GET /api/tasks?status=todo, POST claim/block/complete, POST /api/avatars, and explains reviewFeedback, claimedBy, workspacePath, blockReason — SPEC §31
- AC-11: package tests verify metadata, invocation type, workflow sections, existing-work-first, reviewFeedback priority, one-task-per-run, human-only archive boundary, block-on-workspace-failure, no-daemon rule, API links, openai.yaml consistency, with positive fixtures, negative fixtures, and non-zero assertions — SPEC §33
- AC-12: behavioral scenarios A–F pass against a real Light-Kanban server — SPEC §34
- AC-13: final acceptance comes from `review-loop` with the `agent-skill` Profile; only PASS admits — SPEC §35
- AC-14: compatible with Light-Kanban v1.0.4+; v1.0.5 recommended; no new REST API added — SPEC §57–58

## Required evidence
- structural: package contract and behavior suites, collection discovery/contract composition (commands + outputs)
- installation: clean-copy install and discovery observation without the source checkout
- behavioral: scenarios A–F transcripts against a real server (success, boundary, failure paths)
- invocation: positive trigger and non-trigger observations from fresh contexts
- review: read-only Critic candidate findings + fresh read-only Evaluator judgment

## Required validation scenarios
- VS-1 (A): fresh task → claim → execute → complete → awaiting_confirmation
- VS-2 (B): reject with feedback → in_progress → next run finds owned task first → fix → complete
- VS-3 (C): two agents claim the same todo concurrently → exactly one 200, one 409
- VS-4 (D): workspace missing → claim → block with meaningful reason
- VS-5 (E): empty queue → no mutation, clean exit
- VS-6 (F): board offline → no mutation, clear failure

## Constraints, assumptions, and risks
- Behavioral smoke ran on one localhost machine; LAN cross-machine reachability is covered by the documented block rule, not a live remote test (recorded limitation)
- The package test suites import the collection's shared `tests/check_helpers.py` harness; running them against an installed copy requires the harness on PYTHONPATH (same convention as the other collection packages)
- `npx skills add` verification against the published tag is a release gate, not an admission gate

## Approved exceptions
- None
