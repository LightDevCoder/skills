# `kanban-worker` 使用指南

[English guide](../../skills/kanban-worker.md)

行为权威是 [skills/kanban-worker/SKILL.md](../../../skills/kanban-worker/SKILL.md)；本页只说明如何调用，不复制第二份契约。

> **改名说明：** 本 Skill 在 v0.1.4 首次发布时名为 `light-kanban-worker`，v0.1.6 改名为 `kanban-worker`。v0.1.4/v0.1.5 证据与 pinned `--skill light-kanban-worker` 命令保留旧名。

## 作用

`kanban-worker` 把一次 scheduled agent 唤醒变成恰好处理一个 Light-Kanban 任务：解析稳定的 agent identity、继续自己持有的 in-progress 任务（`reviewFeedback` 优先）、没有遗留工作时领取新的 To Do、在当前 agent host 上校验 workspace、执行、交回结果——`complete` 进入人工验收，或 `block` 并给出具体原因。

> **首次运行**
>
> 首次注册需要 **ID + Name + Avatar**。之后的运行复用已保存的身份，只需稳定的 Agent ID。

> **调度**
>
> 同一 agentId 的两个 scheduled run 不得重叠；把调度并发配置为 1。

## 何时使用

当外部 scheduler（cron、orchestrator 或手动单次 run）唤醒 agent，且任务指令要求处理 Light-Kanban 工作时使用。可同时完成首次注册的调度 prompt：

```text
Use kanban-worker to process at most one Light-Kanban task.

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

Agent Avatar 只在首次注册时需要。

本 Skill 是 `model-invoked`（不是仅 user-invoked 的包），也支持显式手动运行：

```text
Use kanban-worker to process one task from
http://127.0.0.1:8641.

Agent ID: codex-main
Agent Name: Codex
Agent Avatar: /path/to/codex-icon.png
```

`codex-main` 已注册后只需要稳定 Agent ID。

不要把它当作多 agent 编排器、项目经理或 review 框架；它只是“一个 agent 每次处理一张看板任务”的协议。

## 调度边界

不同 agent id 可并发——它们身份不同，通过 atomic claim 竞争新任务。**同一** agent id 的两个 run 不得重叠：把 scheduler 配置为每个 agent id `max concurrent runs = 1`（或等效 skip-while-active）。worker 不新增 lock process、heartbeat 或 lease service；并发控制属于 scheduler / agent runtime。若 scheduler 无法保证，则降低频率、使用外部 scheduler lock 或换 scheduler。

## 配置

`LIGHT_KANBAN_URL` 默认 `http://127.0.0.1:8641`。agent id（`LIGHT_KANBAN_AGENT_ID`）必须稳定，来自当前 invocation 或环境变量，绝不凭空猜测；name 与 avatar 优先复用看板已有 agent 记录；首次注册必须有真实 name 和合法 avatar。新 agent id 缺 name/avatar 属于身份配置失败：报告、不 claim、不改动任何任务，然后结束运行。

## Golden flow

解析身份 → 检查自己持有的 in-progress 任务 → `reviewFeedback` 优先 → 否则领取第一张 FIFO To Do（最多 2 次 claim 尝试）→ 在本 host 校验 `workspacePath` → 读取任务上下文与项目指令 → 执行 → `complete`（Awaiting Confirmation）或带原因 `block` → 停止。空看板时报告 “No task available” 并结束；worker 永不等待或循环。

## Workspace 与阻塞

不可达的 `workspacePath` 变成 `block`，原因是 “Workspace path is not accessible from this agent host.”。绝不让已领取的任务静默卡在 `in_progress`：claim 后失败必须带具体原因 block。worker 不会 unblock 已 `blocked` 的任务——由人工或显式流程处理。

## 人工验收边界

`complete` 后任务进入 Awaiting Confirmation。由人工 Accept 或 Requests Changes；worker 永不 archive、accept、delete 或 recycle。Request Changes 会写入 `reviewFeedback` 并把任务退回 In Progress，同一 agent 的下一次运行会先找到并修复它——返工不产生新任务。

## 准入与测试

`kanban-worker` 会访问网络、读取 workspace 文件、改变看板状态，因此走完整准入路径：`skills/kanban-worker/tests/` 下 contract 与 behavior 测试，加上 `review-loop agent-skill` 验收；`BLOCKED` 结论会把它留在目录外。证据见[准入记录](../../evidence/admissions/light-kanban-worker/README.zh-CN.md)（记录仍用原名 `light-kanban-worker`）。v0.1.5 契约变更（同 agent run 不得重叠、首次注册 avatar 要求）带有独立的 `review-loop agent-skill` `PASS`；见 [v0.1.5 release 证据](../../evidence/releases/v0.1.5/README.zh-CN.md)。

## 安装与发现

从当前版本安装：

```text
npx skills add LightDevCoder/skills --skill kanban-worker --yes --copy --agent '*'
npx skills add LightDevCoder/skills#v0.1.6 --skill kanban-worker --yes --copy --agent '*'
```

v0.1.5 的 pinned `#v0.1.5 --skill light-kanban-worker` 命令安装在旧名下，保留在 v0.1.5 安装记录中。刷新 host 并在脱离 source checkout 的情况下确认 discovery。兼容 Light-Kanban v1.0.4+。
