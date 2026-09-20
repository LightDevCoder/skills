# 项目执行

[English](README.md)

涵盖项目初始化、需求澄清、任务拆解、功能实现、版本发布到会话复盘的完整过程。

分类仅用于组织浏览，不设强制流水线。每个技能的具体行为以其 `SKILL.md` 为准。

## 用户显式调用

- **[project-init](project-init/SKILL.md)** — 为新项目或已有项目建立基础结构与任务跟踪配置，让后续澄清、拆任务和执行可以直接接上。
- **[project-clarify](project-clarify/SKILL.md)** — 读取已有代码和文档资料，只追问尚未确定的关键决策，并将确认结果交给技术规格编写。
- **[project-spec](project-spec/SKILL.md)** — 把已澄清的需求与决策整理成正式的开发规格（SPEC），避免在编写阶段重新提问。
- **[project-tickets](project-tickets/SKILL.md)** — 把已确认的技术规格拆解为有先后依赖关系的任务清单，方便逐步独立执行。
- **[implement](implement/SKILL.md)** — 执行单个已确认的任务（代码、文档或配置），完成本地验证并提交审查。

## Agent 或用户调用

- **[kanban-worker](kanban-worker/SKILL.md)** — 在定时运行中认领并执行一张看板任务，优先处理已有修改意见或进行中的工作。
- **[release-workflow](release-workflow/SKILL.md)** — 负责项目的受控发布，涵盖文档同步、质量检查、标签打标和正式发布。
- **[project-retro](project-retro/SKILL.md)** — 在项目或长会话结束后进行复盘，分析环境阻力、自动化检查、导航效率与命令开销，提出具体改进建议。

[全部分类](../README.zh-CN.md) · [完整目录](../../CATALOG.zh-CN.md)
