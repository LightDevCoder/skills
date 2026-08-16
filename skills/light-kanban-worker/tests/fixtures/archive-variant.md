---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: auto-archive)

A complete worker protocol that violates exactly one rule: the worker takes
over the human review boundary and archives / accepts / deletes / recycles /
unblocks tasks by itself.

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

## Human review boundary (WRONG RULE)

The worker owns the review flow: after completing, it archives the task; it
accepts stale deliveries, deletes unwanted tasks, recycles stuck ones, and
unblocks blocked tasks without waiting for the human.

```http
POST /api/tasks/:id/complete
POST /api/tasks/:id/archive
```

## No work available

If nothing to do: No task available — report and end the run.
