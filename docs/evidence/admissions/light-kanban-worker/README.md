# `light-kanban-worker` admission evidence

[中文记录](README.zh-CN.md)

## Scope and status

- Package: `skills/light-kanban-worker/`
- Invocation type: model-invoked, with a supported manual entry point
- Profile: `review-loop` `agent-skill`
- Stable-release boundary: v0.1.3 contains seven packages and does not contain `light-kanban-worker`
- Admission status: `PASS` — full admission path (2026-08-16); the prompt-only fast track does not apply because the Skill accesses the network, reads workspace files, and mutates Light-Kanban task state

## Evidence summary

| Area | Result | Evidence boundary |
| --- | --- | --- |
| Structure | PASS | Package contract and behavior suites (metadata, required workflow sections, golden-flow order, rule checkers) plus collection discovery/contract composition; 90 collection assertions + all 19 package suites green. |
| Installation and discovery | PASS | Clean-copy install to `/tmp/lk-worker-fresh/codex/skills/light-kanban-worker`: 10/10 files SHA-256 identical, tree contains only the declared package, both suites green against the installed copy (shared collection test harness on PYTHONPATH). Published-tag `npx skills add` verification is the v0.1.4 release gate. |
| Behavioral | PASS | Scenarios A–F against a real Light-Kanban server (binary built from `LightDevCoder/light-kanban` main, commit `f49ace5`): fresh task, Request Changes rework, two-worker atomic claim (exactly one 200 / one 409), workspace missing → block, empty queue no-mutation, offline no-mutation. Full transcript recorded. |
| Invocation | PASS | Fresh read-only probes: the scheduled-task prompt loads the skill with the correct first protocol actions; an unrelated instruction does not trigger it; the skill invokes no other user-invoked skill. |
| Review | PASS | `review-loop` `agent-skill` Profile, Charter revision 1: Critic candidates F-001/F-002/F-003 resolved with verified repairs, F-004 rejected; fresh independent Evaluator returned `PASS` criterion-by-criterion. |
| Attribution | PASS | Owner-authored first-party; no third-party content or code, so no `ATTRIBUTION.md` is required. |

Behavioral evidence: [behavioral-evidence.md](behavioral-evidence.md).
Final acceptance record: [review-loop/](review-loop/) (charter, findings,
round-01 records, verdict).

Admission does not waive release, installation-command verification, or
Program-level acceptance gates; those are recorded under
[docs/evidence/releases/v0.1.4/](../../releases/v0.1.4/).
