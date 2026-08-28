# v0.2.0 测试汇总

[English record](TEST_SUMMARY.md)

状态：`CANDIDATE` — 本地候选测试门禁全部通过；CI 与安装后回归验证待发布后执行。

## 本地候选验证结果

| 套件 / 门禁 | 命令 | 状态 | 结果 / 断言数 |
| --- | --- | --- | --- |
| Pytest 套件 | `python3 -m pytest -q` | `PASS` | 309 passed |
| Unittest 套件 | `python3 -m unittest discover -s tests` | `PASS` | 27 tests（245 条 collection 断言 + 7 条 hook 断言） |
| Python compileall | `python3 -m compileall -q skills tests` | `PASS` | 零错误 |
| Git diff 检查 | `git diff --check` | `PASS` | 干净（无空白/diff 错误） |
| 局部包测试：ask-light contract | `python3 skills/ask-light/tests/test_ask_light_contract.py` | `PASS` | 通过 |
| 局部包测试：ask-light behavior | `python3 skills/ask-light/tests/test_ask_light_behavior.py` | `PASS` | 通过 |
| 局部包测试：kb-init | `python3 skills/kb-init/tests/test_kb_init_contract.py` | `PASS` | 通过 |
| 局部包测试：kanban-worker contract | `python3 skills/kanban-worker/tests/test_kanban_worker_contract.py` | `PASS` | 通过 |
| 局部包测试：kanban-worker behavior | `python3 skills/kanban-worker/tests/test_kanban_worker_behavior.py` | `PASS` | 通过 |
| 局部包测试：language-learning | `python3 skills/language-learning/tests/test_language_learning_contract.py` | `PASS` | 通过 |
| 局部包测试：project-init | `python3 skills/project-init/tests/test_project_init_contract.py` | `PASS` | 通过 |
| 局部包测试：project-review profiles | `python3 -m unittest discover -s skills/project-review/tests` | `PASS` | 通过 |

## CI 与发布后门禁

| 门禁 | 状态 | 观测结果 |
| --- | --- | --- |
| GitHub Actions `collection-quality` | `NOT TESTED` | 待推送 main |
| 安装后源码树无污染回归 | `NOT TESTED` | 待全新安装矩阵完成后验证 |
