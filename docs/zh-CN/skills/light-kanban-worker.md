# `light-kanban-worker` 使用指南

[英文指南](../../skills/light-kanban-worker.md)

行为权威仍是 [skills/light-kanban-worker/SKILL.md](../../../skills/light-kanban-worker/SKILL.md)；本页只说明如何使用，不复制第二份契约。

## 解决什么问题

`light-kanban-worker` 把一次 scheduled agent 唤醒变成恰好处理一个 Light-Kanban 任务：解析稳定的 agent identity、继续自己持有的 in-progress 任务（`reviewFeedback` 优先）、没有遗留工作时领取新的 To Do、在当前 agent host 上校验 workspace、执行、交回结果——`complete` 进入人工验收，或 `block` 并给出具体原因。

> **首次运行**
>
> 首次注册需要 **ID + Name + Avatar**。之后的运行复用已保存的身份；此后只需要稳定的 Agent ID。

> **调度**
>
> 不允许同一个 agentId 的两个 scheduled run 重叠执行。把 scheduler 并发度配置为 1。

## 何时使用 / 不使用

当外部 scheduler（cron、编排器或手动一次性运行）唤醒 agent，且任务指令要求处理 Light-Kanban 工作时使用。一个同时能完成首次注册的 scheduler prompt：

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

Agent Avatar 只在首次注册时需要。

它是 `model-invoked`（不是 user-invoked-only 包），也支持手动入口：

```text
Use light-kanban-worker to process one task from
http://127.0.0.1:8641.

Agent ID: codex-main
Agent Name: Codex
Agent Avatar: /path/to/codex-icon.png
```

如果 `codex-main` 已经注册过，只需要稳定的 Agent ID。

不要把它当成 multi-agent orchestrator、项目管理器或 review framework；它是"一个 agent 每次运行处理一张卡"的协议。

## 调度边界

不同 agent id 可以并发运行——它们身份不同，通过 atomic claim 竞争新任务。同一个 agent id 的两个 run 不得重叠：为每个 agent id 配置 scheduler 的 `max concurrent runs = 1`（或等价的"上一 run 仍活跃则跳过"设置）。worker 不新增任何 lock process、heartbeat 或 lease service；并发控制属于 scheduler / agent runtime。如果 scheduler 无法保证这一点，就不要给同一个 agentId 排重叠的 run——降低运行频率、使用外部 scheduler lock，或更换 scheduler。

## 配置

`LIGHT_KANBAN_URL` 默认 `http://127.0.0.1:8641`。agent id（`LIGHT_KANBAN_AGENT_ID`）必须稳定，来自当前 invocation 或环境变量，绝不凭空猜测。name 与 avatar 优先复用看板上已有 agent 记录；首次注册必须有真实 name 和 http(s) 或已上传的 avatar。新的 agent id 缺 name 或 avatar 属于身份配置失败：报告、不 claim、不改动任何任务，然后结束运行。

## 主流程（Golden flow）

解析 identity → 检查自己持有的 in-progress 任务 → review feedback 优先 → 否则领取 FIFO 第一张 To Do（至多 2 次 claim 尝试）→ 在本机校验 `workspacePath` → 阅读任务上下文与项目指令 → 执行 → `complete`（等你确认）或 `block` 带原因 → 停止。看板为空就是 "No task available"：报告后结束；worker 绝不等待或循环。

## Workspace 与 block

`workspacePath` 不可访问时执行 `block`，原因是 "Workspace path is not accessible from this agent host."。claim 之后发现无法执行，必须 block 并给出具体原因，不能让任务无声停在 `in_progress`。worker 绝不自行解除 `blocked` 状态——那由人类或明确流程完成。

## 人工验收边界

`complete` 之后任务进入 Awaiting Confirmation。人类选择验收通过或退回修改；worker 绝不 archive、accept、delete、recycle。退回修改会写入 `reviewFeedback` 并把任务放回处理中，同一 agent 下次运行优先发现并修复——返工不需要新建任务。

## 准入与测试

`light-kanban-worker` 会访问网络、读取 workspace 文件、改变看板状态，因此走完整准入路径：[skills/light-kanban-worker/tests/](../../../skills/light-kanban-worker/tests/) 的 contract 与 behavior 测试，加上 `review-loop agent-skill` 验收；`BLOCKED` 结论会让它留在 catalog 之外。证据见[准入记录](../../evidence/admissions/light-kanban-worker/README.md)。v0.1.5 的契约变更（同 agent run 不得重叠、首次注册 avatar 要求）带有独立的 `review-loop agent-skill` `PASS`；见 [v0.1.5 release 证据](../../evidence/releases/v0.1.5/README.md)。

## 安装与发现验证

安装该包：

```text
npx skills add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy --agent '*'
```

pinned `#v0.1.5` 命令在 v0.1.5 tag 发布后针对 fresh destination 验证；见
[v0.1.5 安装记录](../../evidence/releases/v0.1.5/INSTALLATION_VERIFICATION.zh-CN.md)。
刷新 agent host，确认脱离 source checkout 仍能发现该 Skill。兼容
Light-Kanban v1.0.4+；推荐集成版本是 Light-Kanban v1.0.6（其内置的正是本
v0.1.5 snapshot）。
