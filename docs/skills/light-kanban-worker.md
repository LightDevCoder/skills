# `light-kanban-worker` user guide

[中文指南](../zh-CN/skills/light-kanban-worker.md)

The package contract at [skills/light-kanban-worker/SKILL.md](../../skills/light-kanban-worker/SKILL.md)
is authoritative. This guide explains how to enter it without duplicating the
contract.

## What it solves

`light-kanban-worker` turns a scheduled agent wake-up into exactly one handled
Light-Kanban task: resolve the stable agent identity, continue owned
in-progress work (with `reviewFeedback` first), claim new To Do work when the
agent holds none, validate the workspace on the agent host, execute, and
return the outcome — `complete` for review, or `block` with a meaningful
reason.

> **First run**
>
> First registration needs **ID + Name + Avatar**. Later runs reuse the
> saved identity; only the stable Agent ID is required after that.

> **Scheduling**
>
> Do not allow two scheduled runs using the same agentId to overlap.
> Configure scheduler concurrency to 1.

## When to use it

Use it when an external scheduler (cron, orchestrator, or a manual one-shot
run) wakes the agent and the task instruction asks the agent to process
Light-Kanban work. A scheduler prompt that can also perform the first
registration:

```text
Use light-kanban-worker to process at most one Light-Kanban task.

Light-Kanban URL:
http://127.0.0.1:8641

Agent ID:
codex-main

Agent Name:
Codex

Agent Avatar:
/path/to/codex-icon.png

Run only when no other codex-main worker invocation is still active.
```

Agent Avatar is only needed for first registration.

The Skill is `model-invoked` (it is not a user-invoked-only package), and an
explicit manual run is also valid:

```text
Use light-kanban-worker to process one task from
http://127.0.0.1:8641.

Agent ID: codex-main
Agent Name: Codex
Agent Avatar: /path/to/codex-icon.png
```

If `codex-main` is already registered, only the stable Agent ID is required.

Do not use it as a multi-agent orchestrator, a project manager, or a review
framework; it is the protocol for one agent handling one board task per run.

## Scheduling boundary

Different agent ids may run concurrently — they hold different identities and
compete for new tasks through atomic claim. Two runs of the **same** agent id
must not overlap: configure the scheduler with `max concurrent runs = 1`
(or the equivalent skip-while-active setting) per agent id. The worker adds
no lock process, heartbeat, or lease service; concurrency control stays with
the scheduler / agent runtime. If the scheduler cannot guarantee that, do not
schedule overlapping runs with the same agentId — lower the frequency, use an
external scheduler lock, or switch schedulers.

## Configuration

`LIGHT_KANBAN_URL` defaults to `http://127.0.0.1:8641`. The agent id
(`LIGHT_KANBAN_AGENT_ID`) must be stable and must come from the invocation or
the environment — it is never guessed. Name and avatar are reused from the
board's existing agent record when present; first registration requires a
real name and an http(s) or uploaded avatar. A new agent id without a name or
avatar is an identity-configuration failure: report it, do not claim or
mutate any task, and end the run.

## Golden flow

Resolve identity → check owned in-progress work → review feedback first →
otherwise claim the first FIFO To Do task (at most 2 claim attempts) →
validate `workspacePath` on this host → read task context and project
instructions → execute → `complete` (Awaiting Confirmation) or `block` with a
reason → stop. An empty board means "No task available": report and end; the
worker never waits or loops.

## Workspace and blocking

An unreachable `workspacePath` becomes
`block` with "Workspace path is not accessible from this agent host." Never
leave a claimed task silently stuck in `in_progress`: post-claim failures
must block with a concrete reason. The worker never unblocks a `blocked`
task — the human or an explicit process does.

## Human review boundary

After `complete`, the task sits in Awaiting Confirmation. The human Accepts
or Requests Changes; the worker never archives, accepts, deletes, or
recycles. A Request Changes rejection sets `reviewFeedback` and returns the
task to In Progress, where the same agent's next run finds it first and
fixes it — rework does not create a new task.

## Admission and tests

`light-kanban-worker` accesses the network, reads workspace files, and
mutates board state, so it follows the full admission path: contract and
behavior tests under [skills/light-kanban-worker/tests/](../../skills/light-kanban-worker/tests/)
plus `review-loop agent-skill` acceptance; a `BLOCKED` verdict would keep it
outside the catalog. See the [admission evidence](../evidence/admissions/light-kanban-worker/README.md).
The v0.1.5 contract change (non-overlapping same-agent runs and the
first-registration avatar requirement) carries its own `review-loop
agent-skill` `PASS`; see the [v0.1.5 release evidence](../evidence/releases/v0.1.5/README.md).

## Installation and discovery

Install the package with:

```text
npx skills add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy --agent '*'
```

The pinned `#v0.1.5` command is verified against fresh destinations (Skills
CLI `1.5.22`, installed copy byte-identical to the tag, package suites run
standalone); see the
[v0.1.5 installation record](../evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.md).
Refresh the agent host and confirm the Skill is discovered without relying
on the source checkout. It is compatible with Light-Kanban v1.0.4+; the
recommended integration version is Light-Kanban v1.0.6, which vendors this
v0.1.5 snapshot.
