---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: same-agent overlap allowed)

A complete worker protocol that violates exactly one rule: it lets a second
scheduled run with the same agent id start while the first run is still
active.

## Agent identity

Use a stable agent id from the invocation or the environment:

```http
GET /api/agents
```

## Existing work before new work

Check owned in-progress work before new work:

```http
GET /api/tasks?status=in_progress
```

## Review feedback first

reviewFeedback has top priority: a task returned with Request Changes
outranks other work.

## Overlapping runs (WRONG RULE)

If another worker with the same agentId is running, continue the same task
concurrently. Two active runs of one agent id simply divide the work between
them and finish faster.

## One task per run

Process at most one task per invocation.

## Claiming new work

```http
GET /api/tasks?status=todo
POST /api/tasks/:id/claim
```

## Human review boundary

The worker never archives, never accepts, never deletes, never recycles, and
never unblocks a task.

## No work available

If nothing to do: No task available — report and end the run.

## Complete the task

```http
POST /api/tasks/:id/complete
```
