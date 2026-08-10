# v0.1.2 discovery 验证

[English record](DISCOVERY_VERIFICATION.md)

## 状态

`PASS — 从已发布的 v0.1.2 tag 与通用 latest 命令将 fresh destinations 安装完成，
并在无 source checkout 的条件下列出。`

本分支当前的本地集合测试返回 1064 assertions 与 `COLLECTION_DISCOVERY=PASS`，
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

观察结果：CLI `1.5.22` 下四个命令均为 `PASS`。pinned `#v0.1.2` 整仓安装列出
恰好七个包；pinned per-Skill 安装恰好列出 `review-loop`；通用 `latest` 整仓
安装列出恰好七个包；通用 `latest` per-Skill 安装恰好列出 `review-loop`。
任何 fresh destination 中均无 source checkout。

## 结构命令

```text
powershell -File tests/collection-discovery-tests.ps1
```

本地观察结果：`COLLECTION_DISCOVERY_ASSERTIONS=1064`、`COLLECTION_DISCOVERY=PASS`。
这只是 structural/discovery 证据。
