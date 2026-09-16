# 项目执行

[English](README.md)

从项目初始化、需求确认和任务拆分，到执行、发布与复盘。分类不改变各阶段的授权或交接边界。

分类只用于浏览，不新增流程或批准要求。技能自身的 `SKILL.md` 是行为权威。

## 用户显式调用

- **[project-init](project-init/SKILL.md)** — 幂等建立下游 Project Skills 消费的稳定 Light 项目与 tracker 契约。
- **[project-clarify](project-clarify/SKILL.md)** — 基于已检查的项目事实澄清真实未决决策，输出给 `project-spec` 的有界 handoff。采用与 `clarify` 相同的 frontier-round 交互，并注入项目证据。
- **[project-spec](project-spec/SKILL.md)** — 将已澄清的输出整理为正式 SPEC，不再重做访谈。
- **[project-tickets](project-tickets/SKILL.md)** — 将已批准 SPEC 转为按依赖排序的 tracer-bullet ticket 图。
- **[implement](implement/SKILL.md)** — 执行一个已决策、有边界的工作项（代码、文档、配置、Skill）。

## Agent 或用户调用

- **[kanban-worker](kanban-worker/SKILL.md)** — 每次定时运行领取并执行一张 Light-Kanban 任务；先继续持有任务与 `reviewFeedback`。
- **[release-workflow](release-workflow/SKILL.md)** — 发布已完成项目——同步文档、执行质量门、打 tag、发布。
- **[project-retro](project-retro/SKILL.md)** — 对已完成的项目或编码会话进行复盘，识别环境、守护线、导航、工具经济性与工作流改进点。

[全部分类](../README.zh-CN.md) · [完整目录](../../CATALOG.zh-CN.md)
