# v0.1.6 安装验证

[English record](INSTALLATION_VERIFICATION.md)

状态：`PASS`，针对已发布 tag 使用 Skills CLI 在 fresh destination 验证通用 `latest` 与 pinned `#v0.1.6` 两种形式。Host refresh 不在此声明；discovery 在 fresh destination 中运行且没有 source checkout。

| 字段 | 整集合 | 单 Skill（`kb-init`） |
| --- | --- | --- |
| 命令 | `npx skills add LightDevCoder/skills --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.6 --yes --copy --agent '*'`（tag） | `npx skills add LightDevCoder/skills --skill kb-init --yes --copy --agent '*'`（latest）与 `npx skills add LightDevCoder/skills#v0.1.6 --skill kb-init --yes --copy --agent '*'`（tag） |
| CLI 版本 | `<cli-version>` | `<cli-version>` |
| 发布 commit | `<release-commit>`（`v0.1.6` tag） | 相同 |
| Fresh destination | 新空临时目录；发现/安装 9 个 skills | 新空临时目录；恰好 1 个包（`kb-init`） |
| 安装结果 | PASS | PASS |
| 脱离 source checkout 的 discovery | `npx --yes skills list` exit 0；包含 `kb-init`；无 source checkout | `npx --yes skills list` exit 0；恰好 `kb-init`；无 source checkout |
| 安装包 smoke | — | 安装的 `kb-init` 与 tag 源码逐字节一致且 contract 测试 OK |
| 重复安装 | 同命令 exit 0；no-op overwrite | 同命令 exit 0；no-op overwrite |
