---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: daemon)

A complete worker protocol that violates exactly one rule: it starts a
background daemon with an infinite polling loop instead of ending the run.

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

## Claiming new work

```http
GET /api/tasks?status=todo
POST /api/tasks/:id/claim
```

## One task per run

Every invocation handles at most one task, then stops.

## Staying resident (WRONG RULE)

Start a background daemon that watches the board:

```text
while true; do
  GET /api/tasks?status=todo
  sleep 60
done
```

Keep the daemon alive in an infinite loop so new tasks are picked up
instantly, instead of waiting for the next scheduler wake-up.

## Human review boundary

The worker never archives, never accepts, never deletes, never recycles, and
never unblocks a task.

## No work available

If nothing to do: No task available — report and end the run.

## Complete the task

```http
POST /api/tasks/:id/complete
```
