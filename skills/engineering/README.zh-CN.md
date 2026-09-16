# 工程开发

[English](README.md)

处理执行配置、故障诊断、原型验证、测试驱动开发与合并冲突。

分类只用于浏览，不新增流程或批准要求。技能自身的 `SKILL.md` 是行为权威。

## Agent 或用户调用

- **[agent-config](agent-config/SKILL.md)** — Profile 驱动的跨 Harness 执行配置器：检查当前宿主真实执行能力，匹配用户确认的模型档位 Profile 与任务形态，精准配置执行拓扑、模型等级与 effort，支持可选 companion MCP（原生支持 primary coding-agent harnesses [10 native adapters + 1 generic fallback]）并提供单模型对等一等模式。
- **[diagnosing-bugs](diagnosing-bugs/SKILL.md)** — 针对难 bug 与性能回退的诊断环，需紧反馈信号。
- **[prototype](prototype/SKILL.md)** — 为设计问题构建一次性原型。
- **[resolving-merge-conflicts](resolving-merge-conflicts/SKILL.md)** — 解决进行中的 `git` merge/rebase 冲突。
- **[tdd](tdd/SKILL.md)** — 测试驱动开发—— red → green → refactor 真测试循环。

[全部分类](../README.zh-CN.md) · [完整目录](../../CATALOG.zh-CN.md)
