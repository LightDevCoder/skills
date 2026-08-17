---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: avatar-optional first registration)

A complete worker protocol that violates exactly one rule: it lets a brand
new agent identity register and start claiming work without an avatar.

## Agent identity

Use a stable agent id from the invocation or the environment:

```http
GET /api/agents
```

If the agent id does not exist yet, the worker may claim a new identity
without avatar: a missing avatar value is not an error, and the board shows
a generated placeholder instead.

## Existing work before new work

Check owned in-progress work before new work:

```http
GET /api/tasks?status=in_progress
```

## Review feedback first

reviewFeedback has top priority: a task returned with Request Changes
outranks other work.

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
