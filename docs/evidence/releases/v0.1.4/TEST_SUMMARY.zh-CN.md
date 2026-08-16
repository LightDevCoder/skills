# v0.1.4 测试摘要

[English record](TEST_SUMMARY.md)

## 状态

`PASS` — 发布 commit 上 main 的本地跨平台 Python 套件。

## 套件与数量

| 套件 | 结果 |
| --- | --- |
| `python3 -m unittest discover -s tests -p "test_*.py"` | 12 个测试 OK；`COLLECTION_PYTHON_ASSERTIONS=90`；`LEARN_ANYTHING_HOOK_ASSERTIONS=7` |
| 包套件（ask-light contract；project-init contract + behavior；recap contract + output；language-learning contract；light-kanban-worker contract + behavior；review-loop 五个 profile 的 contract + behavior；协议 helpers） | 19 个套件 PASS |
| `python3 -m compileall -q skills/learn-anything skills/manuscript-ops skills/light-kanban-worker/tests tests/test_collection_contract.py` | OK |
| 退休包边界（project-workflow / to-manuscript-spec） | 干净 |
| 无 PowerShell 测试文件残留 | 干净 |
| ask-light scanner behavior（pwsh） | 本地以 PowerShell 7.4.6 PASS — 包含跨平台 `Test-PathUnder` 分隔符修复与新增 outside-readable-path negative 场景（见 [CODE_REVIEW.zh-CN.md](CODE_REVIEW.zh-CN.md)） |

## 包级证据

- `light-kanban-worker` contract 套件：metadata、调用类型、必需 workflow
  章节、规则 checker、变异 negative 与四个对抗性单规则 fixture 文件。
- `light-kanban-worker` behavior 套件：golden-flow 顺序、review-feedback
  优先级、单任务规则、人工验收边界、workspace block、无 daemon、失败语义、
  API 参考细节。
- 准入：`review-loop agent-skill` `PASS`（见
  [准入证据](../../admissions/light-kanban-worker/README.zh-CN.md)）。
- 针对真实 Light-Kanban 服务器的行为场景 A–F：全部 `PASS`（见
  [行为证据](../../admissions/light-kanban-worker/behavioral-evidence.zh-CN.md)）。
