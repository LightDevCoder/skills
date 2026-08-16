---
name: light-kanban-worker
description: "Pick up and execute one task from a Light-Kanban board, then return it for human confirmation. Use when a scheduled agent wakes and must process queued Light-Kanban work — resume owned in-progress tasks and Request Changes feedback first, claim new To Do work with a stable agent identity, validate the workspace, execute, then complete or block with a meaningful reason."
---

# Light Kanban Worker

Process **at most one task** from a Light-Kanban board and end the run. This
Skill is the protocol an agent follows after an external scheduler (cron,
orchestrator, manual run) wakes it; the scheduler decides *when* the agent
runs, this Skill decides *what the agent does once awake*.

## Responsibility and boundaries

The worker only:

- resolves its stable agent identity on the board,
- resumes its own unfinished or returned work,
- claims new work when it holds none,
- validates the task workspace on this agent host,
- executes the task inside the project's own workflow, and
- reports the result back (`complete` or `block`).

It is not a multi-agent orchestrator, task planner, ticket system, project
manager, or review framework. It ships no runtime scripts, resident process,
or CLI; use the current agent's HTTP and shell tools. The board manages tasks
and the scheduler manages wake-ups — do not build either into this Skill.

## One task per run

Every invocation handles **at most one task**, then stops. Never take more
than one task in a run, never work on more than one project at once, and
never keep working after the outcome (complete or block) is reported.

## Configuration

| Variable | Meaning | Default |
| --- | --- | --- |
| `LIGHT_KANBAN_URL` | Light-Kanban base URL | `http://127.0.0.1:8641` |
| `LIGHT_KANBAN_AGENT_ID` | Stable agent id, e.g. `codex-main` | none — must be provided |
| `LIGHT_KANBAN_AGENT_NAME` | Display name for first registration, e.g. `Codex` | none — reuse the server's stored name |
| `LIGHT_KANBAN_AVATAR` / `LIGHT_KANBAN_AGENT_AVATAR` | http(s) image URL or a path to a local icon image | none — reuse the server's stored avatar |

Resolution order:

1. values explicitly given by the current invocation or scheduled task,
2. environment variables,
3. the URL default above.

The agent id comes only from those sources — the current invocation (or its
scheduled task instruction) or the `LIGHT_KANBAN_AGENT_ID` environment
variable. An id invented per run is a guessed identity and is not allowed.
Agent identity values are never guessed. If the agent id is unavailable, end
the run with a clear report and **do not change any task**.

## Agent identity

Every run uses one **stable agent id** (e.g. `codex-main`). Never generate a
fresh id per wake-up.

First, read the board's agent list:

```http
GET /api/agents
```

- If the agent id already exists, reuse the server's stored `name` and
  `avatar` for this run; do not require the scheduled task to repeat them.
- If the agent id does not exist, this is first registration: a legal `name`
  and `avatar` are required. The avatar may be an http(s) image URL, or a
  local icon image — upload a local image first:

  ```http
  POST /api/avatars
  Content-Type: multipart/form-data; field "file"
  ```

  and use the returned `/api/avatars/...` path. End the run without touching
  tasks when neither avatar form is available.

## Golden flow

```text
Wake
 ↓
Check Light-Kanban
 ↓
Resolve Agent identity
 ↓
Check owned In Progress tasks
 ↓
Found revision / unfinished work?
 ├─ Yes → continue it
 └─ No
      ↓
    Check To Do
      ↓
    Claim first FIFO task
      ↓
    Enter workspace
      ↓
    Read task + project instructions
      ↓
    Execute
      ↓
 ┌────┴─────┐
Done      Blocked
 ↓           ↓
complete    block + reason
 ↓           ↓
Stop        Stop
```

## Existing work before new work

This is the most important ordering rule. On every wake-up, **check owned
in-progress work before looking at new To Do work**:

```http
GET /api/tasks?status=in_progress
```

and keep only the tasks whose `claimedBy` equals this agent's id. If any
exist, continue one of them — do not fetch To Do first, and do not claim new
work while unfinished owned work exists.

## Review feedback first

When owned in-progress work exists, pick **one** task in this order:

1. a task returned with **Request Changes** — its `reviewFeedback` is set; the
   human rejected the previous delivery and this rework **outranks** everything
   else,
2. any other owned in-progress task,
3. new To Do work — only when no owned in-progress task exists at all.

If several owned tasks carry `reviewFeedback`, take the one waiting longest
(oldest `updatedAt`). With no feedback, take the earliest unfinished owned
task (oldest `updatedAt`). The in-progress list is ordered most-recently
updated first, so the oldest entry is the last match. This keeps the rework
chain alive: `complete` → human review → Request Changes → the same agent
finds the returned task on its next wake-up and fixes it — the loop never
breaks because the task left To Do.

## Claiming new work

Only when no owned in-progress task needs continuing:

```http
GET /api/tasks?status=todo
```

The board returns To Do as a FIFO queue (oldest first). Take the first item
and claim it:

```http
POST /api/tasks/:id/claim
Content-Type: application/json

{"agentId":"<stable-agent-id>","name":"<agent-name>","avatar":"<avatar-path-or-url>"}
```

Claiming is atomic: if several agents check the board at the same time,
exactly one claim succeeds. On a `409 conflict` the task was taken by another
agent — re-read To Do and try the next first item, at most **2 claim attempts
per run**, then end. Never loop indefinitely.

## No work available

If there is no owned in-progress task and To Do is empty: **No task
available**. Report it and end the invocation. Do not create tasks, wait,
retry forever, or start any resident process — the next scheduler wake-up
handles the next opportunity.

## Workspace validation

After claiming or resuming, read `workspacePath` and confirm the path is
accessible **from this agent host** (use the host's file check, e.g.
`test -d` / `Test-Path`). Network reachability of the API is not workspace
reachability: a remote agent can reach the board while the workspace exists
only on another machine. If the workspace is missing or inaccessible, do not
pretend to work:

```http
POST /api/tasks/:id/block
Content-Type: application/json

{"reason":"Workspace path is not accessible from this agent host."}
```

then end the run.

## Read the task context

Before executing, read at least `title`, `description`, `workspacePath`,
`tags`, and `reviewFeedback` from the task, then enter the workspace and read
the project's own instructions where they exist (`AGENTS.md`, `CLAUDE.md`,
`README`, spec or task documents). Follow the host and project's existing
instruction priority — do not invent a second project workflow.

## Execute

Do the task with the current agent's normal capabilities, inside the
project's own workflow and tooling. Stop when the task requirements are met
or when a real blocker appears.

## Complete the task

When the work genuinely satisfies the task requirements:

```http
POST /api/tasks/:id/complete
```

The task moves In Progress → Awaiting Confirmation. Then **Stop** — end the
invocation.

## Human review boundary

The human reviews Awaiting Confirmation: **Accept** (archive) or **Request
Changes**. The worker never archives, never accepts, never deletes, never
recycles, and never unblocks a task — those are human actions (or, for
unblock, an explicit human-orchestrated process). The worker's only job after
`complete` is to stop.

When the human chooses Request Changes, the task returns to In Progress with
`reviewFeedback` set. The next worker run finds that owned task first (see
Review feedback first), reads the feedback, fixes the work, and calls
`/complete` again — no new task is created for rework.

## Blocked work

When the task cannot proceed without something the agent cannot provide:

```http
POST /api/tasks/:id/block
Content-Type: application/json

{"reason":"<concrete, specific reason>"}
```

Use meaningful reasons, e.g.:

```text
Required API credential is unavailable.
Workspace path cannot be accessed.
Build dependency is missing.
Required user decision is needed.
```

Never write vague reasons like "Something failed." or "Cannot continue." A
blocked task stays blocked until the human or an explicit process removes the
obstacle and unblocks it; the worker never unblocks a blocked task itself,
and resumes it only after it returns to in_progress through that outside
process.

## Failures before and after claim

Before claim (board unreachable, identity unavailable, invalid
configuration): **do not change any task** — report the failure clearly and
end the run.

After claim, if the task turns out to be impossible to execute, block it with
a meaningful reason (see Blocked work) — never leave a claimed task silently
stuck in In Progress.

## Network boundary

Light-Kanban binds `127.0.0.1:8641` by default and only the same machine can
reach it. If this agent runs on another machine, the human must have started
the board with `-addr :8641` (or `0.0.0.0:8641`). The worker never changes
the server's network binding — if the board is unreachable, report it and
stop (see Failures before and after claim).

## API reference

The exact endpoints, fields, and error semantics this worker uses are in
[references/api.md](references/api.md). Compatible with Light-Kanban v1.0.4+;
v1.0.5 is the recommended integration version.
