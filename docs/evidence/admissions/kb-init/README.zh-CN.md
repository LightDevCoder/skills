# `kb-init` 准入证据

[English record](README.md)

## 范围与状态

- 包：`skills/kb-init/`
- 调用类型：仅 user-invoked
- Profile：`review-loop` `agent-skill`
- 稳定版本边界：v0.1.6 包含 `kb-init` v1.0.0，作为第九个包
- 准入状态：完整准入路径 `PASS`；以 v1.0.0 包随 v0.1.6 发布

## 证据摘要

| 领域 | 结果 | 证据边界 |
| --- | --- | --- |
| 来源 | PASS | 原创第一方设计；未复制第三方代码或资源；不需要 `ATTRIBUTION.md`。 |
| 结构 | PASS | `SKILL.md`、`agents/openai.yaml`、八份参考文档、`evals/evals.json` 与 contract 测试均存在且非空；contract 测试运行 `OK`。 |
| 调用 | PASS | `SKILL.md` 含 `disable-model-invocation: true`；`agents/openai.yaml` 含 `allow_implicit_invocation: false`；显式-only 章节禁止自触发和调用另一个 user-invoked Skill。 |
| 快速通道分类 | PASS | 纯提示型快速通道不适用，因为访谈/实施可使用工具、调用 model-invoked `research` 能力，并可能创建文件或状态。 |
| 文档同步 | PASS | README、目录、安装指南、维护基线、changelog 与双语指南一致描述当前分支九个包、已发布 v0.1.5 八个包；所有相对链接可解析。 |
| 独立审查 | PASS | 新的只读 Evaluator 确认 eligibility、包结构、调用边界、文档同步与 contract 测试结果；最终 verdict `PASS`。 |

完整记录见 [review-loop/](review-loop/)。

本地源码与结构证据属于准入证据。v0.1.6 已发布 tag 的安装验证记录在 docs/evidence/releases/v0.1.6/ 下。
