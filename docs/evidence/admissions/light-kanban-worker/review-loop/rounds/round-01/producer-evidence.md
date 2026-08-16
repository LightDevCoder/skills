# Producer Evidence - Round 1

## Scope
- Charter revision: 1
- Profile: agent-skill
- In-scope work: `skills/light-kanban-worker/` package admission (structure, installation/discovery, invocation, behavior, tests)
- Out-of-scope check: Light-Kanban repo changes, v0.1.4 publication, and published-tag install verification were not touched by this evidence

This is Producer evidence, not final acceptance.

## Evidence

### E-001 - Package structure and metadata
- Evidence label: structural
- Run or observation: `python3 skills/light-kanban-worker/tests/test_light_kanban_worker_contract.py` and `test_light_kanban_worker_behavior.py` in `LightDevCoder/skills` (commit `bc09126`)
- Expected: both suites pass with non-zero assertions (Charter AC-1, AC-2, AC-11)
- Observed: contract suite OK (SKILL.md frontmatter name, required workflow sections incl. golden flow/identity/existing-work-first/review-feedback/claiming/no-work/workspace/complete/human-review/blocked/failures/network boundaries; openai.yaml display_name "Light Kanban Worker", short_description "Pick up and execute work from Light-Kanban", default_prompt "Use light-kanban-worker to process one Light-Kanban task.", allow_implicit_invocation true, no disable-model-invocation); behavior suite OK (golden-flow marker order, reviewFeedback priority list, one-task rule, human-only boundary incl. never archive/accept/delete/recycle/unblock, workspace block reason, no daemon/sleep/while-true/infinite-loop/polling-loop, "No task available", pre-claim no-mutation, post-claim block)
- Outcome: PASS
- Validates: AC-1, AC-2, AC-11 (partially)
- Environment and limitations: Python 3.9.6, macOS; static/contract class evidence, not runtime proof
- Artifact: skills/light-kanban-worker/tests/

### E-002 - Negative fixtures and mutations
- Evidence label: structural
- Run or observation: same suites; mutated positive content and four adversarial fixture files (`todo-first-variant.md`, `daemon-variant.md`, `archive-variant.md`, `multi-task-variant.md`) run through the same rule checkers
- Expected: every negative fixture and each mutation flips at least one checker (Charter AC-11)
- Observed: archive mutation rejected, multi-task mutation rejected, daemon mutation rejected, invocation-policy mutation rejected, claim-endpoint removal from api.md rejected; all four fixture files rejected by their target checker
- Outcome: PASS
- Validates: AC-11
- Environment and limitations: static adversarial fixtures, not runtime misuse
- Artifact: skills/light-kanban-worker/tests/fixtures/

### E-003 - Collection-level composition
- Evidence label: structural
- Run or observation: `python3 -m unittest discover -s tests -p "test_*.py"` in `LightDevCoder/skills` (commit `bc09126`, plus later doc commit), incl. LightKanbanWorkerContractCompositionTest and LightKanbanWorkerBehaviorCompositionTest; CI-shaped package file loop; compileall; retired-boundary grep
- Expected: 12 discovery/contract tests OK, all 19 package suites OK, compileall OK, no retired references (Charter AC-1, AC-11)
- Observed: 12 tests OK (COLLECTION_PYTHON_ASSERTIONS=90, LEARN_ANYTHING_HOOK_ASSERTIONS=7), all package suites PASS, compileall OK, retired boundary clean, no PowerShell test files
- Outcome: PASS
- Validates: AC-1, AC-11
- Environment and limitations: structural cross-reference check, not host runtime proof
- Artifact: tests/test_collection_discovery.py, tests/test_collection_contract.py, .github/workflows/quality.yml

### E-004 - Clean-copy installation and discovery
- Evidence label: installation
- Run or observation: `cp -R LightDevCoder/skills/skills/light-kanban-worker /tmp/lk-worker-fresh/codex/skills/light-kanban-worker`; enumerated the installed tree; SHA-256-compared all 10 files against the source; ran both suites against the installed copy with `PYTHONPATH` carrying the collection's shared test harness
- Expected: the clean copy contains exactly the declared package files, is byte-identical to source, and the installed suites pass without the source checkout (Charter AC-1, AC-11)
- Observed: 10/10 files SAME (SKILL.md, agents/openai.yaml, references/api.md, 2 test modules, shared checker, 4 fixtures); both suites OK against the installed copy; discovery reads SKILL.md + agents/openai.yaml from the installed location only
- Outcome: PASS
- Validates: AC-1, AC-11
- Environment and limitations: local-copy installation evidence (admission class), not a published-tag `npx skills add` verification (release gate); the suites import the repo-level `tests/check_helpers.py` harness, same convention as the other collection packages
- Artifact: /tmp/lk-worker-fresh/codex/skills/light-kanban-worker

### E-005 - Behavioral scenarios A-F against a real server
- Evidence label: behavioral
- Run or observation: real Light-Kanban binary (`make build` from LightDevCoder/light-kanban main, commit `f49ace5`) started with `-db /tmp/lk-worker-smoke/data/kanban.db -avatars /tmp/lk-worker-smoke/data/avatars -no-open -addr 127.0.0.1:8641`; the SKILL.md protocol executed with curl/jq per scenario (harness `/tmp/lk-worker-smoke/run-scenarios.sh`, transcript `/tmp/lk-worker-smoke/transcript.txt`)
- Expected: VS-1…VS-6 outcomes per the Charter (AC-4…AC-9, AC-12)
- Observed: A fresh task → claim 200 (`claimedBy=codex-main`) → complete → awaiting_confirmation; B reject with feedback → in_progress + reviewFeedback → next wake reused stored identity, found the owned reviewFeedback task before todo, fixed, complete, human archive (worker never archived); C concurrent claims → exactly one 200 (claude-code) and one 409 (codex-main), loser re-read empty todo and ended; D missing workspace → claim → block with exact reason "Workspace path is not accessible from this agent host." → blocked; E empty queue → in_progress [] and todo [] → "No task available" → db SHA-1 `53ad3992…` unchanged, 0→0 active tasks; F unreachable board → health probe 000 → clear failure → db SHA-1 unchanged
- Outcome: PASS
- Validates: AC-3 (identity register/reuse), AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-12
- Environment and limitations: localhost single-machine smoke; LAN cross-machine reachability is documented as a block rule rather than live-tested
- Artifact: docs/evidence/admissions/light-kanban-worker/behavioral-evidence.md (+ .zh-CN.md), /tmp/lk-worker-smoke/transcript.txt

### E-006 - Invocation trigger and non-trigger
- Evidence label: invocation
- Run or observation: two fresh read-only subagent contexts, each given only the installed package at /tmp/lk-worker-fresh and one instruction — trigger: the scheduled-task prompt "Use light-kanban-worker to process at most one Light-Kanban task…" (URL, agent id, name); non-trigger: "Read /tmp/lk-worker-smoke/ws-a/README.md and tell me in one sentence what changed"
- Expected: the trigger instruction loads the skill with correct first protocol actions; the unrelated instruction does not trigger it; the skill invokes no other user-invoked skill (AC-2, AC-6, AC-13)
- Observed: trigger probe loaded light-kanban-worker, listed GET /api/agents → GET in_progress → reviewFeedback ordering → GET todo → POST claim with bounded 409 retry as the first five actions; non-trigger probe reported no reasonable implicit trigger and quoted the manual entry line; both reported the skill invokes no other user-invoked skill
- Outcome: PASS
- Validates: AC-2, AC-13
- Environment and limitations: fresh subagent observations, read-only; not a host product integration test
- Artifact: probe reports recorded in the admission session and summarized in the Evaluator packet

### E-007 - API surface and compatibility
- Evidence label: source
- Run or observation: read `internal/api/api.go` and `internal/store/store.go` of LightDevCoder/light-kanban (commit `f49ace5`, v1.0.4 tag lineage) and compared with references/api.md
- Expected: the seven documented endpoints exist with the documented semantics; no new API is required (AC-10, AC-14)
- Observed: GET /api/agents, GET /api/tasks with status filters (todo FIFO oldest-first, in_progress most-recent-first), POST /api/tasks/:id/claim (atomic conditional update, 409 on conflict, 422 identity validation), POST /:id/block with optional reason, POST /:id/complete clearing reviewFeedback, POST /api/avatars multipart → /api/avatars/<name>; fields id/title/workspacePath/description/status/claimedBy/tags/blockReason/reviewFeedback match; no endpoint added or modified for this work
- Outcome: PASS
- Validates: AC-10, AC-14
- Environment and limitations: source inspection, cross-checked by the live behavioral runs (E-005)
- Artifact: skills/light-kanban-worker/references/api.md
