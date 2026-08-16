---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: todo first)

This fixture violates the existing-work-first rule: it checks To Do before
owned In Progress work, which can orphan a Request Changes rework loop.

## Claiming new work

Start by listing new work:

```http
GET /api/tasks?status=todo
```

Then claim the first item:

```http
POST /api/tasks/:id/claim
```

Only afterwards check whether you already hold work:

```http
GET /api/tasks?status=in_progress
```

## Complete the task

```http
POST /api/tasks/:id/complete
```
