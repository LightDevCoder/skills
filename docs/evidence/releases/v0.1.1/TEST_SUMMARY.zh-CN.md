# v0.1.1 测试摘要

[English summary](TEST_SUMMARY.md)

本页只记录真实命令和断言数量；未运行的命令标为 `NOT TESTED`，零断言或只扫描 source 的检查不能算通过。

| 范围 | 命令 | 结果 |
| --- | --- | --- |
| ask-light contract | `powershell -File skills/ask-light/tests/ask-light-contract-tests.ps1` | `PASS`；脚本只输出通过标记，不输出数字断言数。 |
| ask-light behavior | `powershell -File skills/ask-light/tests/ask-light-behavior-tests.ps1` | `PASS`；本地分支运行 52 条断言，包含重复 source category、完整 workflow context、非法 availability/invocation-control context 和 workflow read-count fixtures。 |
| project-init | package contract/behavior scripts | `PASS`；contract 和 behavior 均通过，脚本不输出数字断言数。 |
| review-loop Profiles | `skills/review-loop/tests/` 全部 contract/behavior | `PASS`；5 个 contract 套件、5 个 behavior 套件，共 105 条 behavior 断言。 |
| learn-anything hooks | `python -m unittest discover -s tests -p "test*.py"` | `PASS`；4 个测试，collection 54 条断言、learn-anything hook 7 条断言。 |
| manuscript-ops | 三个 Python CLI 的 `--help` | `PASS`；三个只读 CLI help 检查均成功。 |
| collection discovery | `powershell -File tests/collection-discovery-tests.ps1` | `PASS`；683 条断言，包含 Skill guide、workflow、release evidence 和双语 semantic-pair parity。 |
| header asset | `powershell -File tests/header-asset-tests.ps1` | `PASS`；11 条断言，覆盖 SVG/PNG 尺寸、同步资产 manifest 和叠层字标标记。 |
| Quick Start | `powershell -File tests/quick-start-smoke-tests.ps1` | `PASS`；8 条断言。 |
| Python 语法 | 只读 `ast.parse` 检查 | `PASS`；12 个 Python 文件解析通过且不写入字节码。 |
| Python `compileall` | `python -m compileall -q skills tests` | 本地 `NOT PASSED`；沙箱拒绝写入现有受保护的 `__pycache__`，但合并 release commit `c50f1ef` 上的 GitHub Actions 同命令已通过。 |
| Tagged fresh install | `npx skills add LightDevCoder/skills#v0.1.1 ...` 加 `npx skills list` | `PASS`；CLI `1.5.20`，整仓 destination 列出 5 个包，单 Skill destination 列出 `review-loop`，且两个 source checkout 都不存在。见[安装证据](INSTALLATION_VERIFICATION.md)。 |
| Release-commit CI | GitHub Actions `collection-quality` | `PASS`；run `30189210521` 对应 `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`。 |

包测试只证明覆盖到的 contract 场景；collection discovery 只证明 cross-reference 和 metadata 一致。tagged installation 证据另有记录；这些证据都不能证明 independent acceptance 或模型介导的 runtime 行为。
