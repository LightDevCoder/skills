# v0.1.2 测试摘要

[English summary](TEST_SUMMARY.md)

本文件记录真实命令与断言数。未运行的命令标记为 `NOT TESTED`；零断言或仅
source scan 不算通过。

## 当前结果

| 区域 | 命令 | 结果 |
| --- | --- | --- |
| ask-light contract | `powershell -File skills/ask-light/tests/ask-light-contract-tests.ps1` | `PASS` — 零失败；该脚本只报告 pass marker，不输出数字计数。 |
| ask-light behavior | `powershell -File skills/ask-light/tests/ask-light-behavior-tests.ps1` | `PASS` — 本地分支运行 52 assertions，含重复 source-category、完整 workflow context、invalid availability/invocation-control context 与 workflow read-count fixtures。 |
| project-init | 包 contract 与 behavior 脚本 | `PASS` — contract 与 behavior 套件通过；脚本不输出数字计数。 |
| review-loop Profiles | `skills/review-loop/tests/` 下所有 contract/behavior 脚本 | `PASS` — Agent-Skill、generic、manuscript、software、specification 五个 profile 共 5 套 contract 与 105 个 behavior assertions。 |
| language-learning | `powershell -File skills/language-learning/tests/language-learning-contract-tests.ps1` | `PASS` — 33 assertions。 |
| recap | `powershell -File skills/recap/tests/recap-output-contract-tests.ps1` | `PASS` — 8 assertions。 |
| learn-anything hooks | `python -m unittest discover -s tests -p "test*.py"` | `PASS` — 4 tests；80 个集合 assertions 与 7 个 learn-anything hook assertions。 |
| manuscript-ops | `python skills/manuscript-ops/scripts/{assess_project,check_dependencies,validate_state}.py --help` | `PASS` — 三个只读 CLI help 检查全部成功。 |
| collection discovery | `powershell -File tests/collection-discovery-tests.ps1` | `PASS` — 951 assertions，含 Skill-guide、workflow、release-evidence 与双语语义配对 parity。 |
| header asset | `powershell -File tests/header-asset-tests.ps1` | `PASS` — 11 assertions；SVG/PNG 尺寸、同步 asset manifest 与 layered wordmark markers。 |
| Quick Start | `powershell -File tests/quick-start-smoke-tests.ps1` | `PASS` — 8 assertions。 |
| Python syntax | `python -B -c "...ast.parse..."` | `PASS` — Python 文件解析通过，未写 bytecode。 |
| Tagged fresh install | `npx skills add LightDevCoder/skills#v0.1.2 ...` 加 `npx skills list` | 在 release tag 存在前为 `NOT TESTED`；见 [installation evidence](INSTALLATION_VERIFICATION.zh-CN.md)。 |
| 通用 `latest` fresh install | `npx skills add LightDevCoder/skills ...` 加 `npx skills list` | 在 release tag 存在前为 `NOT TESTED`；见 [installation evidence](INSTALLATION_VERIFICATION.zh-CN.md)。 |
| Release-commit CI | GitHub Actions `collection-quality` | 在 release commit 上运行前为 `NOT TESTED`。 |

## Evidence class

包测试演示已演练的 contract 场景。Collection discovery 演示 cross-reference
与 metadata 一致性。Fresh tagged installation evidence 单独记录；本地包测试
与 CLI discovery 都不能证明独立验收或 model-mediated runtime 行为。
