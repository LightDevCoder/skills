# `language-learning` 准入证据

[English record](README.md)

## 范围与状态

- 包：`skills/language-learning/`
- 调用类型：仅 user-invoked
- 准入状态：已为低风险纯提示型快速通道准备好证据；尚无最终 verdict
- 稳定版本边界：v0.1.1 包含五个包，不含 `language-learning`

## 已准备的证据

| 领域 | 结果 | 证据边界 |
| --- | --- | --- |
| 来源 | PASS | 原创第一方设计；无复制的第三方代码、脚本或资源。 |
| 结构 | PENDING | 包树、`SKILL.md` metadata 与内部链接将在 collection discovery 检查中验证。 |
| 契约 | PENDING | 33 条本地通过的契约断言覆盖上下文复用、教学行为、选择性纠错、时间比例指导值、常用义优先卡片、易混结构对照、评估与沉浸分级，包含正反 fixtures。 |
| 调用 | PASS | Claude `disable-model-invocation: true` 与 Codex `allow_implicit_invocation: false`；包声明仅 user-invoked。 |
| Fresh-copy 安装 | PENDING | 需要 fresh host；pinned 命令还需要未来发布的 release tag，目前尚无。 |
| 行为 | PENDING | 需要 fresh Agent 对成功、边界与失败场景的观察。 |
| 独立评审 | PENDING | 最终 `PASS`、`FAIL` 或 `BLOCKED` 之前需要一个 fresh 独立快速通道 Evaluator。 |
| 集合质量 | PENDING | 准入编辑定稿后记录完整本地套件结果。 |

## 最终 verdict 之前的待办

1. 本地运行 collection discovery、header-asset 与 quick-start 套件并记录结果。
2. 为纯提示型快速通道取得一个 fresh 独立 Evaluator verdict。
3. 在 fresh host 上完成 fresh-copy 安装与 discovery 检查。
4. 记录 fresh Agent 的成功、边界与非触发行为观察。

在这些完成之前，该包只是提议，尚未准入，也不得发布任何 pinned 安装命令。

## 行为来源

原创第一方设计。本包未复制任何上游 Skill 代码或 prompt 文本。
