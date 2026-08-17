# v0.1.5 发现验证

[English record](DISCOVERY_VERIFICATION.md)

## 状态

`PASS` — 针对已发布的 `v0.1.5` tag 验证发现：`npx skills add
LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy
--agent '*'` 安装到 fresh destination 后，在该 destination 运行
`npx --yes skills list`（路径上不存在任何 source checkout）。

| 字段 | 值 |
| --- | --- |
| 命令 | `npx skills add LightDevCoder/skills#v0.1.5 --skill light-kanban-worker --yes --copy --agent '*'` |
| Installer 版本 | `1.5.22` |
| Host / destination | 一次性空临时目录 |
| Discovery 结果（`npx --yes skills list`） | exit 0；列出 `light-kanban-worker ./.agents/skills/light-kanban-worker`，带 `Agents: …` 与 `Source: LightDevCoder/skills` |
| 包完整性 | 14 个文件：SKILL.md、agents/openai.yaml、references/api.md、tests/（2 个套件 + helpers + 8 个 fixtures）——与 tag checkout 逐字节一致 |
| Metadata | frontmatter `name: light-kanban-worker`；display_name / short_description / `allow_implicit_invocation: true` 均存在 |
| 安装副本上的 contract 测试 | PASS — 100 断言，从安装包独立运行 |
| 安装副本上的 behavior 测试 | PASS — 23 断言，从安装包独立运行 |

已知 CLI 显示怪癖（非包缺陷）：CLI 在 `agent/skills/` 下的各 host 副本会去掉
`name` frontmatter 字段，因此 `skills list` 对每个包打印统一的 "missing
required frontmatter field(s): name" 警告；`.agents/skills/` 下的副本与 tag
逐字节一致。
