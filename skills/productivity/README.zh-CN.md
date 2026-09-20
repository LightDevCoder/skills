# 日常工具

[English](README.md)

寻找合适技能、交接会话上下文、一句话总结进展、引导手动操作，以及生成旅行计划页面。

分类仅用于组织浏览，不设强制流水线。每个技能的具体行为以其 `SKILL.md` 为准。

## 用户显式调用

- **[ask-light](ask-light/SKILL.md)** — 工作流顾问与导航助手：根据当前项目与对话状态，推荐最合适的下一步技能并说明理由。
- **[handoff](handoff/SKILL.md)** — 将当前会话的核心背景与进展浓缩为交接文档，方便下一位 Agent 接力。
- **[recap](recap/SKILL.md)** — 输出当前会话的一句话进展摘要，不改动也不压缩原有对话历史。
- **[wait-what](wait-what/SKILL.md)** — 当上一条回复不够清晰或理解有偏差时，换一个通俗视角重新解释。

## Agent 或用户调用

- **[wizard](wizard/SKILL.md)** — 生成交互式终端向导，引导人类完成只有人才能操作的步骤（如云控制台配置、密钥填写、生产环境割接）。
- **[light-travelpage](light-travelpage/SKILL.md)** — 将旅行行程与预订资料生成为中英双语手机网页，支持航班住宿卡片、地图导航、费用记账与待办清单。

[全部分类](../README.zh-CN.md) · [完整目录](../../CATALOG.zh-CN.md)
