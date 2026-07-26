# v0.1.1 Discovery 验证

[English record](DISCOVERY_VERIFICATION.md)

## 状态

本地 collection test 已返回 668 条断言并输出 `COLLECTION_DISCOVERY=PASS`，属于
`STRUCTURAL PASS`。从 fresh destination 检查最终 release artifact 仍为
`NOT TESTED`。

## 必须观察

- 恰好五个第一方包名存在。
- 每个包都有 `SKILL.md`、完整 frontmatter 和带 invocation policy 的 `agents/openai.yaml`。
- 引用资源完整，且脱离 source checkout 后仍可发现。
- `ask-light next/workflow` 保留 source、invocation、availability gap、expected input/output 和 stop condition。
- user-invoked 包不会被静默当作 model-invoked。
- `project-workflow` 与 `to-manuscript-spec` 仍在准入树外。

结构命令为 `powershell -File tests/collection-discovery-tests.ps1`。
观察结果：`COLLECTION_DISCOVERY_ASSERTIONS=668`、`COLLECTION_DISCOVERY=PASS`。
这只属于 structural/discovery evidence。
