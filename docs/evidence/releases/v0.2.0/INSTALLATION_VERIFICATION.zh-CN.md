# v0.2.0 安装验证记录

[English record](INSTALLATION_VERIFICATION.md)

## 状态

`PASS` — 基于 Skills CLI `1.5.23` 针对打标的公开仓库验证通过。全集合与全部 33 个单独 Skill 均在全新隔离环境中完成了 generic `latest` 与 pinned `#v0.2.0` 的安装与发现验证。

## 隔离与名称冲突策略

- 安装验证均在独立的临时工程根目录下运行，并使用隔离的临时 `HOME`、`XDG_CONFIG_HOME` 与 `XDG_DATA_HOME` 环境变量。
- 绝不修改开发机真实的用户主目录、全局 Skills 目录或活跃 Agent 工作区。
- 绝不覆盖任何现有 Matt Skills 或其他第三方包。

## 验证矩阵结果

| 范围 | 形式 | 命令 | CLI 版本 | 退出码 | 安装数量 | 发现验证（`skills list`） | 完整性检查 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 全集合 | `latest` | `npx --yes skills add LightDevCoder/skills --yes --copy --agent '*'` | `1.5.23` | `0` | 33 个包 | `PASS`（全部 33 个正常列出） | 完整 33 包安装成功 | `PASS` |
| 全集合 | `#v0.2.0` | `npx --yes skills add LightDevCoder/skills#v0.2.0 --yes --copy --agent '*'` | `1.5.23` | `0` | 33 个包 | `PASS`（全部 33 个正常列出） | 与打标源码 100% 逐字节一致 | `PASS` |
| 33 个单独 Skill | `latest` | `npx --yes skills add LightDevCoder/skills --skill <name> --yes --copy --agent '*'` | `1.5.23` | `0`（33/33） | 各 1 个包 | `PASS` | 恰好安装所请求的单个包 | `PASS` |
| 33 个单独 Skill | `#v0.2.0` | `npx --yes skills add LightDevCoder/skills#v0.2.0 --skill <name> --yes --copy --agent '*'` | `1.5.23` | `0`（33/33） | 各 1 个包 | `PASS` | 恰好安装所请求的单个包 | `PASS` |

## 重复安装行为

- 在已安装目录上再次执行 pinned 全集合安装命令，退出码为 `0`（干净的 no-op overwrite）。

## 局限性

- `.agents/skills/` 下的安装副本经由 CLI 发现机制（`skills list`）完成结构与发现验证。不同 Agent 宿主的实时刷新与模型运行时调用属于 host 自行行为。
