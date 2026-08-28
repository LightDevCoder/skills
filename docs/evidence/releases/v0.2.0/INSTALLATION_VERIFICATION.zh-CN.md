# v0.2.0 安装验证记录

[English record](INSTALLATION_VERIFICATION.md)

## 状态

`NOT TESTED` — 发布候选提交已就绪。在 Phase 2 人工批准发布后，将在 Phase 3 于独立临时隔离环境中执行针对已发布 tag 和 generic latest 的全新安装验证。

## 隔离与名称冲突策略

- 安装验证均在全新临时目录中运行，并使用隔离的临时 `HOME`、`XDG_CONFIG_HOME` 与 `XDG_DATA_HOME` 环境变量。
- 绝不修改真实的开发机用户主目录、全局 Skills 目录或活跃 Agent 工作区。
- 绝不覆盖任何现有 Matt Skills 或其他第三方安装。

## 计划验证矩阵

| 范围 | Generic `latest` 命令 | Pinned `#v0.2.0` 命令 | 状态 |
| --- | --- | --- | --- |
| 全集合（33 个包） | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `npx --yes skills add LightDevCoder/skills#v0.2.0 --yes --copy --agent '*'` | `NOT TESTED` |
| 33 个单独 Skill 矩阵 | `npx --yes skills add LightDevCoder/skills --skill <name> --yes --copy --agent '*'` | `npx --yes skills add LightDevCoder/skills#v0.2.0 --skill <name> --yes --copy --agent '*'` | `NOT TESTED` |

## 验证结果记录（Phase 3 执行后填充）

| 目标 | 形式 | 退出码 | 安装数量 | 发现验证（`skills list`） | Smoke / 完整性 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 全集合 | latest | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| 全集合 | #v0.2.0 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| 33 个单独 Skill | latest | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |
| 33 个单独 Skill | #v0.2.0 | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED | NOT TESTED |

## 局限性

- 待全新安装矩阵执行后记录。
