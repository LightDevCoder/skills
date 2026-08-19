# v0.1.6 安装验证

[English record](INSTALLATION_VERIFICATION.md)

状态：`PASS`，针对已发布 tag 使用 Skills CLI `1.5.23` 在 fresh destination 验证通用 `latest` 与 pinned `#v0.1.6` 两种形式。Host refresh 不在此声明；discovery 在 fresh destination 中运行且没有 source checkout。

| 字段 | 整集合 | 单 Skill（`kb-init`） |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.6 --yes --copy --agent '*'`（tag） | `npx skills add LightDevCoder/skills --skill kb-init --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.6 --skill kb-init --yes --copy --agent '*'`（tag） |
| CLI 版本 | `1.5.23` | `1.5.23` |
| 发布 commit | `41b6e7169a1c68bb017f9ff6c464b220185b02ff`（`v0.1.6` tag） | 相同 |
| Fresh destination | 新空临时目录；发现/安装 9 个 skills | 新空临时目录；恰好 1 个包（`kb-init`） |
| 安装结果 | PASS | PASS |
| 脱离 source checkout 的 discovery | `npx --yes skills list` exit 0；包含 `kb-init`；无 source checkout | `npx --yes skills list` exit 0；恰好 `kb-init`；无 source checkout |
| 安装包 smoke | — | 安装的 `kb-init` 与 tag 源码逐字节一致且 contract 测试 OK |
| 重复安装 | 同命令 exit 0；no-op overwrite | 同命令 exit 0；no-op overwrite |

## 限制

- CLI 的 `agent/skills/` 逐 agent 副本会去掉 `name` frontmatter 字段，因此 `skills list` 会对每个复制包打印 "missing required frontmatter field(s): name" 警告。这是 CLI 复制行为，不是包缺陷；`.agents/skills/` 安装与 tag 逐字节一致（与 tag 源码 `diff -r` 干净），并在共享测试 harness 的 `PYTHONPATH` 下 contract 测试通过。
- 只验证了本文件记录的安装范围；不声明 host refresh 与 model-runtime invocation。
