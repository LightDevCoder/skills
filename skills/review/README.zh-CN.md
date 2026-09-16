# 审阅验收

[English](README.md)

区分只读审阅、修复收敛和项目最终验收；选择与当前检查范围相符的技能。

分类只用于浏览，不新增流程或批准要求。技能自身的 `SKILL.md` 是行为权威。

## Agent 或用户调用

- **[code-review](code-review/SKILL.md)** — 针对有界 `git diff` 的只读 specialist 审查（Standards + Spec 双轴）。
- **[generic-review](generic-review/SKILL.md)** — 针对普通制品的只读默认 reviewer，找遗漏、错误、矛盾与可用性问题。
- **[review-loop](review-loop/SKILL.md)** — 轻量 review/repair 引擎——解析 reviewer、调用、收 findings、回 Producer、重跑。
- **[project-review](project-review/SKILL.md)** — 项目级最终验收——冻结 baseline、组合 reviewer、签发 `PASS`/`FAIL`/`BLOCKED`。

[全部分类](../README.zh-CN.md) · [完整目录](../../CATALOG.zh-CN.md)
