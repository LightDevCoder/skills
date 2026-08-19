# Scenario G — Same Agent Concurrent Wake (scheduler guard fixture)

Deterministic contract fixture for the same-agent overlap boundary. This is
not a live two-worker race against a Light-Kanban server, and Light-Kanban
provides no run lease: the guard below is the scheduler's concurrency
control, which is exactly where the worker contract places it.

## Setup

- Board reachable at `http://127.0.0.1:8641`.
- Agent id `codex-main`; scheduler interval 15 min; task runtime about 40 min.
- Scheduler configured with `max concurrent runs = 1` for `codex-main`.

## Sequence

1. `08:00` — the scheduler starts run #1 with agentId `codex-main`. Run #1 is
   active: it has resolved its identity and is processing its task.
2. `08:15` — the scheduled wake for `codex-main` fires while run #1 is still
   active. The scheduler guard detects the active run.
3. Run #2 must not start processing work: no second identity resolution, no
   second claim, no workspace entry, no task mutation.
4. `08:40` — run #1 finishes (complete or block) and ends.
5. `08:45` — the next scheduler occurrence is allowed to start run #3.

## Verification boundary

This fixture verifies the scheduler / Worker contract only: the worker must
skip when a previous run with the same agent id is still active. It does not
simulate a Light-Kanban server lease and does not exercise two agents
mutating one workspace at the same time.
