# v0.1.4 ask-light scanner code-review 证据

[English record](CODE_REVIEW.md)

运行时脚本变更：`skills/ask-light/scripts/ask-light.ps1`（`Test-PathUnder`
跨平台分隔符修复）及 `skills/ask-light/tests/test_ask_light_behavior.py`
新增的跨平台 negative 场景。仓库政策要求运行时脚本变更有 `code-review` 证据。

## 审查范围

- Fixed point：commit `f8a9fcf`（准入后状态）
- 文件：`skills/ask-light/scripts/ask-light.ps1`、
  `skills/ask-light/tests/test_ask_light_behavior.py`
- 专家：全新只读 code-review subagent（Standards + Spec 两轴）

## Findings 与处置

| ID | 轴 | 严重度 | Finding | 处置 |
| --- | --- | --- | --- | --- |
| STD-1 | Standards | Low | `Test-PathUnder` 使用 `OrdinalIgnoreCase` 比较路径；在大小写敏感的 Linux 文件系统上可能把 `/tmp/MySkill` 判为 `/tmp/myskill` 的子路径（历史既有行为，本次修复后对 Linux 有意义）。 | 接受并记录理由：大小写不敏感比较保留了 Windows 与 macOS（默认大小写不敏感）的历史行为；Linux 上比较双方都来自 host 上报的路径、大小写一致；PowerShell 没有可移植的按文件系统探测大小写敏感性的方法。行为测试不覆盖大小写不同路径；negative 场景在大小写一致的前提下钉住外部路径拒绝。 |

无 Spec findings：变更精确匹配原始需求——硬编码 `'\'` 使 Linux/macOS pwsh
下所有候选都被判为"outside host readable paths"；修复改用平台分隔符，
Windows 行为逐字节不变；新增 negative 场景是真正的 negative（skill 位于
已发现 root 下但在 `readablePaths` 之外）。

## 变更的测试证据

- `skills/ask-light/tests/test_ask_light_behavior.py` 通过 pwsh（PowerShell
  7.4.6）对一次性 fixture 目录运行真实 scanner：host-filter positive（兼容
  Skill 可选）、新增 outside-readable-path negative（unavailable + 可操作
  gap）、block-list 与 host 声明场景。结果：macOS 本地 OK；同一套件此前在
  ubuntu CI 失败，本变更修复该失败。
