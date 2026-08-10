# v0.1.2 discovery 验证

[English record](DISCOVERY_VERIFICATION.md)

## 状态

`NOT TESTED — 将 tagged artifact 安装到 fresh destinations 并在无 source
checkout 的条件下列出后填写。`

本分支当前的本地集合测试返回 951 assertions 与 `COLLECTION_DISCOVERY=PASS`，
这是已准入树的 structural/discovery 证据，不是 fresh host installation proof。

## 必需观察

- 恰好七个第一方包名存在。
- 每个包都有 `SKILL.md`、完整 frontmatter 和带 interface 与 invocation policy
  的 `agents/openai.yaml`。
- 引用资源存在，且脱离 source checkout 后仍可发现包。
- `ask-light` next/workflow 输出保留 source category、invocation type、
  availability gap、expected input/output 与 stop condition。
- user-invoked 包不会被静默 model-invoked。
- `project-workflow` 与 `to-manuscript-spec` 仍在准入树之外。

## Fresh artifact 命令

```text
npx --yes skills add LightDevCoder/skills#v0.1.2 --yes --copy --agent '*'
npx --yes skills list
npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'
npx --yes skills list
npx --yes skills add LightDevCoder/skills#v0.1.2 --skill review-loop --yes --copy --agent '*'
npx --yes skills list
```

观察结果：`NOT TESTED — 创建 release tag 后填写`。

## 结构命令

```text
powershell -File tests/collection-discovery-tests.ps1
```

本地观察结果：`COLLECTION_DISCOVERY_ASSERTIONS=951`、`COLLECTION_DISCOVERY=PASS`。
这只是 structural/discovery 证据。
