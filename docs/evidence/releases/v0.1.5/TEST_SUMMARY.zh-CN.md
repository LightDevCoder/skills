# v0.1.5 测试摘要

[English record](TEST_SUMMARY.md)

## 状态

`PASS` — v0.1.5 candidate commit 上 main 的本地跨平台 Python 套件。属于
pre-release gate 证据；post-release CI 在 tag 发布后记录于 main。

## 套件与计数

| 套件 | 结果 |
| --- | --- |
| `python3 -m unittest discover -s tests -p "test_*.py"` | 12 个测试 OK |
| `light-kanban-worker` contract 套件 | PASS — 100 条断言 |
| `light-kanban-worker` behavior 套件 | PASS — 23 条断言 |
| 集合 discovery 套件 | PASS — 1309 条断言 |
| 包级套件（ask-light contract；project-init contract + behavior；recap contract + output；language-learning contract；review-loop 五 profile contract + behavior；协议 helpers） | PASS |
| `python3 -m compileall -q skills/learn-anything skills/manuscript-ops skills/light-kanban-worker/tests tests/test_collection_contract.py` | OK |
| 退休包边界（project-workflow / to-manuscript-spec） | clean |
| 无 PowerShell 测试文件残留 | clean |
| ask-light scanner behavior（pwsh） | 本地跳过（无 pwsh；CI 会运行） |

## 新增 worker 覆盖（v0.1.5）

- 契约规则：same-agent 不得重叠（`must not overlap` / `must skip`）、不同
  agent 并发允许、atomic claim 不是并发锁的边界、scheduler 拥有并发控制
  （`max concurrent runs = 1`）、无常驻 lock/heartbeat/lease service、首次
  注册需要 ID + name + avatar、已有 agent 身份复用、缺身份不得改动任务、
  本地 avatar 上传路径。
- negative fixtures：`overlap-allowed-variant.md`（仅违反不得重叠规则）与
  `avatar-optional-first-registration.md`（仅违反首次注册 avatar 规则）。
  每个都必须让目标 checker 失败并通过其余五个规则 checker；mutation
  negative 覆盖真实 `SKILL.md` 上的两条新规则。
- 行为场景：
  - 场景 G — 同 agent 并发唤醒，经 scheduler-guard fixture
    `scenario-g-scheduler-guard.md` 验证：run #1 活跃 → run #2 被调度 →
    不得开始。fixture 记录了验证边界：Light-Kanban 自身不提供 run lease。
  - 场景 H — 无 avatar 的新身份，经
    `scenario-h-fresh-identity-no-avatar.md` 验证：缺 avatar → identity
    configuration missing → 不 claim、不改动；提供合法 avatar → 注册 →
    claim 成功。
  - 场景 A–F 保持不变并继续通过；真实服务器证据在
    [behavioral-evidence.zh-CN.md](../../admissions/light-kanban-worker/behavioral-evidence.zh-CN.md)。
