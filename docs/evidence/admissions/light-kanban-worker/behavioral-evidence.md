# `light-kanban-worker` behavioral evidence

[中文记录](behavioral-evidence.zh-CN.md)

Status: `IN PROGRESS` — each scenario is filled with its exact commands,
environment facts, inputs, outputs, and result as it completes against a real
Light-Kanban server. A scenario marked `PENDING` has not run yet.

| Scenario | Expectation | Result |
| --- | --- | --- |
| A — Fresh task | todo → worker claims → executes → complete → awaiting_confirmation | PENDING |
| B — Request Changes | awaiting_confirmation → human reject with feedback → in_progress → next run finds owned task first → reads feedback → fixes → complete | PENDING |
| C — Two workers | Two different agentIds claim the same To Do concurrently; exactly one claim succeeds | PENDING |
| D — Workspace missing | task workspacePath does not exist → claim → block with a meaningful reason | PENDING |
| E — Empty queue | No owned in_progress and no todo → no mutation, clean exit | PENDING |
| F — Light-Kanban offline | Server unreachable → no mutation, clear failure | PENDING |
