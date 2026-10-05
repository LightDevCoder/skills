# Light Skills v0.2.6 名称迁移

[English](MIGRATION-v0.2.6.md) · [候选发布说明](evidence/namespace-v0.2.6/release-draft/RELEASE_NOTES.zh-CN.md)

**状态：** 本地名称迁移候选尚未发布；远端 v0.2.6 已被旅行手册发布占用。v0.2.5 是本 checkout 的已验证发布基线，并非最新远端稳定版。新名称模板为 **BLOCKED，不可执行**；D7 禁止覆盖标签或自行改号。见[发布阻断记录](evidence/namespace-v0.2.6/publication-blocker.md)。

12 个 Light 包增加 `light-` 前缀。其他 24 个名称、七个分类、36 个包总数、职责和调用权限保持不变。旧名不提供可安装 alias 或 wrapper。`ask-light` 与 `light-travelpage` 保留名称。安装路径变为 `<skills-root>/<新名>/`；源码路径仍为 `skills/<category>/<新名>/`。

| 原 Light 名称 | 新名称 | 分类 | 调用方式 |
| --- | --- | --- | --- |
| `implement` | `light-implement` | project | user-invoked |
| `code-review` | `light-code-review` | review | model-invoked |
| `research` | `light-research` | thinking | model-invoked |
| `prototype` | `light-prototype` | engineering | model-invoked |
| `tdd` | `light-tdd` | engineering | model-invoked |
| `diagnosing-bugs` | `light-diagnosing-bugs` | engineering | model-invoked |
| `wizard` | `light-wizard` | productivity | model-invoked |
| `handoff` | `light-handoff` | productivity | user-invoked |
| `teach` | `light-teach` | knowledge | user-invoked |
| `to-questionnaire` | `light-to-questionnaire` | thinking | user-invoked |
| `wait-what` | `light-wait-what` | productivity | user-invoked |
| `writing-for-agents` | `light-writing-for-agents` | writing | model-invoked |

## 升级前

记录目标 Host 及其识别的 Skill 根目录。逐项记录旧名包的来源仓库、revision、实际路径和安装模式。软链接需要检查目标路径及目标内容；复制安装需要检查 `SKILL.md`、`ATTRIBUTION.md` 和安装器来源元数据，并与安装源码核对。只看目录名不能判断归属。处理旧包前，备份已确认属于 Light 的副本，或记录其软链接目标。

检查项目提示、`AGENTS.md`、能力可用性声明、脚本、自动化和安装命令的旧 `--skill` 参数。只改能力引用。项目类型 `research`、ticket 类型 `research` 或 `prototype`、研究产物目录和普通 handoff 语义保留。已有项目状态不会自动重写。

## 升级步骤

1. 决策所有者处理版本冲突，且名称迁移发布通过门禁后，把已确认的固定标签安装到所需 Host 范围。只选择实际使用的 Skill 与 Host；下列命令不强制复制，也不写入所有 Host。
2. 确认旧名安装属于 Light，且已保存副本或软链接目标后，再移除或归档。重新安装可能留下旧目录。其他来源的包保留原样。
3. 按完整映射表更新 Light 的旧 `--skill` 参数和显式调用，例如 `$implement` 改为 `$light-implement`。逐项更新项目能力声明、提示、自动化与源码链接；每个目标的写入需要对应授权。
4. 软链接安装需确认 canonical 源码已升级，链接解析到新目录。复制安装需核对每个 Host 的完整包内容，再按 Host 的界面刷新发现。
5. 检查 Host 选择器或发现列表。安装全集时记录全部 36 个 Light 包身份、12 个新界面标签（`Light · …`）、实际路径、来源和选中的调用。ready-ticket 场景应推荐 `light-implement`，软件审阅应解析到 `light-code-review`。Light 依赖缺失时应报告不可用，不应改用旧同名能力。

```bash
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6 --skill light-implement
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6 --global --agent codex
```

不带版本的 `npx skills add LightDevCoder/skills` 跟随实际默认分支 `main`，不会自动跟随最新稳定标签。v0.2.5 不包含候选新名称。静态文件扫描只能证明结构，不能证明 Host 实际调用。能力发现与显式选择来源不会锁定所有 model-invoked 调用。

## 恢复

迁移失败时保留诊断，在依赖恢复前停止使用新入口。恢复保存的 Light 副本或软链接目标，恢复对应项目和自动化引用；必要时重新安装固定 `#v0.2.5`。恢复旧名目录前，确认不会覆盖其他来源的包。刷新 Host，核对恢复后的来源和入口。历史标签与证据保留原样。

本次仓库任务只准备候选与隔离验证证据，不修改真实用户的全局 Skills、Host 配置、其他项目或自动化。此类写入属于另行授权的迁移阶段；需记录实际发现、安装模式、来源和恢复结果，不能从仓库改名推断迁移已经完成。
