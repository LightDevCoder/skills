---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: multi-task)

A complete worker protocol that violates exactly one rule: it claims several
tasks in one run instead of at most one.

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

## Claiming new work (WRONG RULE)

Fetch the queue and claim the first two items, then process multiple tasks
in parallel to maximize throughput:

```http
GET /api/tasks?status=todo
POST /api/tasks/:id/claim
POST /api/tasks/:id/claim
```

## One task per run (WRONG RULE)

One invocation may work on several tasks at once and keeps going until every
claimed task is done.

## Human review boundary

The worker never archives, never accepts, never deletes, never recycles, and
never unblocks a task.

## No work available

If nothing to do: No task available — report and end the run.

## Complete the task

```http
POST /api/tasks/:id/complete
```
