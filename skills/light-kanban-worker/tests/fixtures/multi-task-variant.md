---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: multi-task)

This fixture violates the one-task-per-run rule: it claims every available
task in a single invocation and works them in parallel.

## Claiming new work

Fetch the queue and claim every item at once:

```http
GET /api/tasks?status=in_progress
GET /api/tasks?status=todo
```

For each todo task, process all tasks in the list — claim several at the same
time and execute them concurrently to maximize throughput.

## Complete the task

```http
POST /api/tasks/:id/complete
```
