# 技能分类

[English](README.md)

36 个技能按用途分成七类。每个分类说明集合的用途，并区分用户显式调用与 Agent 可调用的技能。

| 分类 | 数量 | 用途 |
| --- | ---: | --- |
| [项目执行](project/README.zh-CN.md) | 8 | 从项目初始化、需求确认和任务拆分，到执行、发布与复盘。分类不改变各阶段的授权或交接边界。 |
| [工程开发](engineering/README.zh-CN.md) | 5 | 处理执行配置、故障诊断、原型验证、测试驱动开发与合并冲突。 |
| [审阅验收](review/README.zh-CN.md) | 4 | 区分只读审阅、修复收敛和项目最终验收；选择与当前检查范围相符的技能。 |
| [澄清研究](thinking/README.zh-CN.md) | 5 | 澄清想法与决策，研究外部事实，或为掌握信息的人准备问题。 |
| [学习知识](knowledge/README.zh-CN.md) | 5 | 用于学习、分层解释、语言练习、来源方法提炼和知识库初始化。 |
| [写作编辑](writing/README.zh-CN.md) | 3 | 组织稿件生产、改写生硬文案，以及编写清晰的 Agent 指令。 |
| [日常工具](productivity/README.zh-CN.md) | 6 | 查找合适技能、交接任务、简短回顾会话、指导手动步骤，以及制作旅行页面。 |

源码路径为 `skills/<category>/<name>/`。技能名称、调用方式和安装后的 `<skills-root>/<name>/` 路径不变。
