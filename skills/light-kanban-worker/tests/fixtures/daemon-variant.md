---
name: light-kanban-worker
description: Pick up and execute work from a Light-Kanban board.
---

# Light Kanban Worker (negative fixture: daemon)

This fixture violates the no-daemon rule: it keeps a background service and
an infinite polling loop running instead of ending the invocation.

## Staying resident

Start a background daemon that watches the board:

```text
while true; do
  GET /api/tasks?status=todo
  sleep 60
done
```

Keep the daemon alive forever so tasks are picked up instantly. If the queue
is empty, wait in an infinite loop until work arrives.

## Complete the task

```http
POST /api/tasks/:id/complete
```
