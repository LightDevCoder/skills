# v0.1.1 Discovery 验证

[English record](DISCOVERY_VERIFICATION.md)

## 状态

本地 collection test 已返回 683 条断言并输出 `COLLECTION_DISCOVERY=PASS`；tagged
artifact 已安装到 fresh destination，并在没有 source checkout 的情况下成功
列出，结论为 `PASS`。

## 必须观察

- 恰好五个第一方包名存在。
- 每个包都有 `SKILL.md`、完整 frontmatter 和带 invocation policy 的 `agents/openai.yaml`。
- 引用资源完整，且脱离 source checkout 后仍可发现。
- `ask-light next/workflow` 保留 source、invocation、availability gap、expected input/output 和 stop condition。
- user-invoked 包不会被静默当作 model-invoked。
- `project-workflow` 与 `to-manuscript-spec` 仍在准入树外。

## Fresh artifact 命令

```text
npx --yes skills add LightDevCoder/skills#v0.1.1 --yes --copy --agent codex
npx --yes skills list
npx --yes skills add LightDevCoder/skills#v0.1.1 --skill review-loop --yes --copy --agent codex
npx --yes skills list
```

观察结果：整仓 destination 恰好列出 5 个包，单 Skill destination 恰好列出
`review-loop`；两个 destination 都不存在 `skills/` source checkout。已安装的
`review-loop` contract tests 通过，整仓安装后的 `ask-light` behavior suite
返回 52 assertions/PASS。

结构命令为 `powershell -File tests/collection-discovery-tests.ps1`。
观察结果：`COLLECTION_DISCOVERY_ASSERTIONS=683`、`COLLECTION_DISCOVERY=PASS`。
这同时包含 structural/discovery evidence 和 fresh artifact discovery evidence；
不等于 host refresh 或模型介导的 runtime proof。
