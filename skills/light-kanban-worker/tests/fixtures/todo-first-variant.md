---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: todo first)

A complete worker protocol that violates exactly one rule: it checks To Do
before owned In Progress work, which can orphan a Request Changes rework loop.

## Agent identity

Use a stable agent id from the invocation or the environment:

```http
GET /api/agents
```

## Claiming new work (WRONG ORDER)

Start by listing new work:

```http
GET /api/tasks?status=todo
```

Then claim the first FIFO item:

```http
POST /api/tasks/:id/claim
```

## Existing work before new work

Only afterwards check whether you already hold work:

```http
GET /api/tasks?status=in_progress
```

## Review feedback first

reviewFeedback has top priority: a task returned with Request Changes
outranks other work.

## One task per run

Every invocation handles at most one task, then stops.

## Human review boundary

The worker never archives, never accepts, never deletes, never recycles, and
never unblocks a task.

## No work available

If nothing to do: No task available — report and end the run.

## Complete the task

```http
POST /api/tasks/:id/complete
```
