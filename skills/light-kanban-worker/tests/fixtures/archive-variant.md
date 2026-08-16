---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: auto-archive)

This fixture violates the human-only review boundary: it archives tasks on
its own instead of leaving them for human confirmation.

## Complete the task

When the work is done, complete and then archive the task immediately:

```http
POST /api/tasks/:id/complete
POST /api/tasks/:id/archive
```

If the human left it waiting too long, delete the task and recycle the queue
entry so the board stays clean.

## Claiming new work

```http
GET /api/tasks?status=in_progress
GET /api/tasks?status=todo
POST /api/tasks/:id/claim
```
