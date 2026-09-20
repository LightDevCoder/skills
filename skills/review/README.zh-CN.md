# 审阅验收

[English](README.md)

区分只读检查、迭代修复循环与项目最终验收，确保审查职责清晰。

分类仅用于组织浏览，不设强制流水线。每个技能的具体行为以其 `SKILL.md` 为准。

## Agent 或用户调用

- **[code-review](code-review/SKILL.md)** — 代码审查专员：对比变更代码（`git diff`），从规范标准与业务规格两个维度检查潜在问题，仅输出问题清单而不直接修改代码。
- **[generic-review](generic-review/SKILL.md)** — 通用文档与制品审阅：检查非代码产物（文档、配置、计划）中的遗漏、事实矛盾、格式错误或体验缺陷。
- **[review-loop](review-loop/SKILL.md)** — 审查与修复循环引擎：将产物提交给对应的审查技能，收集发现的问题并指导修复，直到通过或达到轮次上限。
- **[project-review](project-review/SKILL.md)** — 项目最终验收：基于已确认的验收基准，组合各项审查结果，给出最终的验收判定（`PASS` / `FAIL` / `BLOCKED`）。

[全部分类](../README.zh-CN.md) · [完整目录](../../CATALOG.zh-CN.md)
