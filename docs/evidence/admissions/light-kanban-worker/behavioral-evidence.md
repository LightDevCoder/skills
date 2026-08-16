# `light-kanban-worker` behavioral evidence

[中文记录](behavioral-evidence.zh-CN.md)

Status: `PASS` — all six scenarios completed against a real Light-Kanban
server following the `SKILL.md` protocol (the worker's HTTP + shell steps,
executed by the running agent exactly as a scheduled agent would).

## Environment facts

| Fact | Value |
| --- | --- |
| Light-Kanban binary | `light-kanban` built from `LightDevCoder/light-kanban` main (v1.0.4+) via `make build`, commit `f49ace5` |
| Server command | `./dist/light-kanban -db /tmp/lk-worker-smoke/data/kanban.db -avatars /tmp/lk-worker-smoke/data/avatars -no-open -addr 127.0.0.1:8641` |
| Date | 2026-08-16 (UTC timestamps in the transcript) |
| Worker agents | `codex-main` (name `Codex`), `claude-code` (name `Claude Code`); 1×1 PNG icons uploaded via `POST /api/avatars` |
| Harness | Throwaway bash + curl + jq at `/tmp/lk-worker-smoke/run-scenarios.sh` (not shipped with the Skill); full transcript at `/tmp/lk-worker-smoke/transcript.txt` |

## Results

| Scenario | Expectation | Result |
| --- | --- | --- |
| A — Fresh task | todo → worker claims → executes → complete → awaiting_confirmation | `PASS` — task `1d2cfffb…` created `todo`; identity resolved (`GET /api/agents` → empty → first registration via avatar upload `/api/avatars/5efb83c4….png`); owned in-progress check ran first (empty); first FIFO todo claimed (`200`, `claimedBy=codex-main`, `in_progress`); workspace `/tmp/lk-worker-smoke/ws-a` accessible; fix applied; `POST complete` → `200` `awaiting_confirmation`. |
| B — Request Changes | awaiting_confirmation → human reject with feedback → in_progress → next run finds owned task first → reads feedback → fixes → complete | `PASS` — human `POST reject` with `{"feedback":"Add a regression test for the redirect fix."}` returned the task to `in_progress` with `reviewFeedback` set; next wake reused the existing agent identity (`GET /api/agents` → `codex-main`, stored name/avatar); the owned in-progress task with `reviewFeedback` was found before any todo check; regression test written in the workspace; `POST complete` → `awaiting_confirmation`; human `POST archive` → `archived` (the worker itself never archived). |
| C — Two workers | Two different agentIds claim the same To Do concurrently; exactly one claim succeeds | `PASS` — concurrent claims on the same todo: `claude-code` → `200` `in_progress`, `codex-main` → `409 conflict` ("task is not in the required status for claim"); `claimedBy=claude-code` exactly one winner; loser re-read `todo` (`[]`) and ended — bounded retry, no infinite loop. |
| D — Workspace missing | task workspacePath does not exist → claim → block with a meaningful reason | `PASS` — task claimed, `test -d /tmp/lk-worker-smoke/ws-missing` failed, `POST block` with `{"reason":"Workspace path is not accessible from this agent host."}` → `200` `blocked` with that exact `blockReason` visible on the card. |
| E — Empty queue | No owned in_progress and no todo → no mutation, clean exit | `PASS` — `GET in_progress` → `[]`, `GET todo` → `[]`; "No task available"; database SHA-1 identical before/after (`53ad3992…`), active task count 0 → 0, no task created, no waiting. |
| F — Light-Kanban offline | Server unreachable → no mutation, clear failure | `PASS` — health probe against `http://127.0.0.1:19999` → `000` (connection refused); worker reported the unreachable board and ended; database SHA-1 unchanged (`53ad3992…`). |

## Coverage notes

- Existing-work-first: exercised in B (owned in-progress work found before any
  todo claim) and by the protocol ordering in A (in-progress checked before
  todo).
- Identity: first registration with a local icon upload in A; server-identity
  reuse without re-uploading in B.
- Human review boundary: the worker never called `archive`/`reject`/
  `recycle`/`unblock`/`delete`; those calls were made by the human role in the
  harness (reject, archive, delete) and are recorded as such.
- Atomic claim: the board's single conditional `claim` transition produced
  exactly one `200` and one `409` under real concurrency.
- Limitation: this is a single-machine (localhost) integration smoke, not a
  cross-machine LAN test; network-reachability-vs-workspace-reachability on a
  remote host follows the same block rule (D) and is documented in `SKILL.md`.
