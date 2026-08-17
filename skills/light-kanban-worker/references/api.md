# Light-Kanban API Reference for light-kanban-worker

The minimal API surface the worker actually uses. Compatible with
Light-Kanban v1.0.4+; v0.1.5 adds no REST API requirement. The recommended
integration version is Light-Kanban v1.0.6, which vendors the v0.1.5
snapshot. The
authoritative product contract is the Light-Kanban repository spec
(`.scratch/task-board/spec.md` in `LightDevCoder/light-kanban`); this file
records only the worker-facing subset.

Base URL: `LIGHT_KANBAN_URL`, default `http://127.0.0.1:8641`. All requests
and responses are JSON (except the avatar upload, which is multipart).

## Status tokens

`todo` / `in_progress` / `blocked` / `awaiting_confirmation` / `archived`.

## Task object (relevant fields)

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Task id, used in transition URLs. |
| `title` | string | Task title. |
| `workspacePath` | string | Workspace folder the task points at; must be readable from the agent host. |
| `description` | string \| null | Task description. |
| `status` | string | One of the status tokens. |
| `claimedBy` | string \| null | Agent id that currently holds the task (set on claim, cleared on recycle / manual To Do correction). |
| `tags` | string[] | Task tags. |
| `createdAt` / `updatedAt` | RFC3339 string | Creation / last activity timestamps. |
| `blockReason` | string \| null | Set when an agent blocks; shown on the card; cleared on unblock. |
| `reviewFeedback` | string \| null | Set when the human does Request Changes; the agent must read and apply it; cleared on `complete`. |

## Endpoints

### GET /api/agents

Lists registered agents:

```json
[{"id":"codex-main","name":"Codex","avatar":"/api/avatars/ab12….png"}]
```

Used for identity resolution: reuse the existing agent's `name`/`avatar`;
register a new identity only when the agent id is absent.

### GET /api/tasks?status=in_progress

Returns all in-progress tasks, most recently updated first. The worker keeps
the entries with `claimedBy == <own agent id>` and continues one of them —
before ever looking at To Do.

### GET /api/tasks?status=todo

Returns the To Do queue, FIFO (oldest `createdAt` first). The worker claims
the first entry. Other filters (`active`, `blocked`,
`awaiting_confirmation`, `archived`) exist but are not part of the worker's
golden flow.

### POST /api/tasks/:id/claim

Body:

```json
{"agentId":"codex-main","name":"Codex","avatar":"/api/avatars/ab12….png"}
```

`avatar` must be an http(s) image URL or a previously uploaded
`/api/avatars/...` path; `name` must be non-empty.

Semantics: atomic `todo → in_progress` transition; the agent is
self-registered or refreshed. Errors:

- `409 conflict` — another agent claimed it first (task no longer in `todo`).
  Re-read To Do and try the next first item; at most 2 claim attempts per run.
- `404` — unknown task id.
- `422` — missing/empty `agentId` or `name`, or an invalid `avatar`
  reference.

### POST /api/avatars

Multipart upload, field name `file` (PNG / JPEG / GIF / WebP, ≤ 2 MiB).
Response: `{"path":"/api/avatars/<name>.png"}`. Use the returned path as the
`avatar` for a first claim. Needed only for first registration with a local
icon; http(s) URLs and previously stored avatars skip this step.

### POST /api/tasks/:id/block

Body optional: `{"reason":"…"}`. Moves `in_progress → blocked` and stores
`blockReason`. Meaningful reasons only. `409` when the task is not in
`in_progress`.

### POST /api/tasks/:id/complete

No body. Moves `in_progress → awaiting_confirmation` and clears any previous
`reviewFeedback`. After success the worker stops — review is the human's.

## Transitions the worker never calls

`POST /api/tasks/:id/archive`, `/reject`, `/recycle`, `/unblock`,
`DELETE /api/tasks/:id`, and `PATCH /api/tasks/:id` are human (or
human-orchestrated) actions. The worker must not call them.

## Ordering notes

- To Do is a FIFO queue — the first entry is the next work item.
- In Progress lists the most recent activity first, so the oldest owned entry
  is the last match — the "earliest unfinished" or "longest-waiting rework"
  selection scans from the end.
- Awaiting Confirmation lists the longest-waiting review first; the worker
  does not act on it (human review boundary).

## Failure semantics

- Board unreachable / identity unavailable / invalid configuration → fail
  before touching any task; no mutation.
- Claimed task with inaccessible `workspacePath` → `POST /:id/block` with
  `{"reason":"Workspace path is not accessible from this agent host."}`.
- Post-claim execution failure → `POST /:id/block` with a concrete reason;
  never leave a task silently in `in_progress`.
