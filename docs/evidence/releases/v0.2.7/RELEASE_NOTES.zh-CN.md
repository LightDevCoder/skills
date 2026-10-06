# v0.2.7：Skill 名称与迁移

[English GitHub Release](https://github.com/LightDevCoder/skills/releases/tag/v0.2.7)（发布后可用） · [英文候选说明](RELEASE_NOTES.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md)

**候选状态：** v0.2.7 尚未发布，当前稳定版为 v0.2.6。候选 CI、真实 Host 验证与实际发布源安装尚待完成。本草稿不是已发布结果。

本候选为 12 个 Skill 增加 `light-` 前缀，便于在全局安装中识别来源。内部引用、`ask-light` 路由与界面名称使用新名称。集合仍有 36 个 Skill。

## 主要变化

| 原 Light 名称 | 新名称 |
| --- | --- |
| `implement` | `light-implement` |
| `code-review` | `light-code-review` |
| `research` | `light-research` |
| `prototype` | `light-prototype` |
| `tdd` | `light-tdd` |
| `diagnosing-bugs` | `light-diagnosing-bugs` |
| `wizard` | `light-wizard` |
| `handoff` | `light-handoff` |
| `teach` | `light-teach` |
| `to-questionnaire` | `light-to-questionnaire` |
| `wait-what` | `light-wait-what` |
| `writing-for-agents` | `light-writing-for-agents` |

其他 24 个名称、分类、职责和调用权限保留。`ask-light` 与 `light-travelpage` 保留名称。软件工作使用 `light-implement`，适用时组合 `light-tdd`；`review-loop` 组合 `light-code-review`。`project-review` 仍拥有最终验收。Light 依赖缺失时明确报告缺口。相对 v0.2.6，本候选的变化仅为名称迁移及其引用、路由、文档、归属记录与验证。已发布的旅行手册和可选 AI 保持完整。

## 升级说明

更新 Light 的旧 `--skill` 参数和显式调用，例如 `$implement` 改为 `$light-implement`。检查项目提示、能力声明、自动化与源码软链接。处理旧名包前，确认其实际来源或链接目标，并保存副本或链接目标。重新安装不代表旧名已经清理。本版不提供旧名 alias，也不会自动迁移真实全局安装。

需要恢复时，恢复保存的 Light 副本或软链接目标，恢复相关引用；必要时重装 `#v0.2.6`。先确认恢复旧名不会覆盖其他来源的包。详见[完整迁移说明](https://github.com/LightDevCoder/skills/blob/main/docs/MIGRATION-v0.2.7.zh-CN.md)。

## 安装

下列命令仅为候选模板。实际 v0.2.7 发布源通过新鲜安装验证后，才能标为已验证用法。

```bash
npx skills add LightDevCoder/skills#v0.2.7
npx skills add LightDevCoder/skills#v0.2.7 --skill light-implement
npx skills add LightDevCoder/skills#v0.2.7 --global --agent codex
```

不带版本的命令跟随实际 `main`，包括该分支的已准入变化，不会自动选择稳定标签：

```bash
npx skills add LightDevCoder/skills
```

## 验证记录

合并候选通过 128 项名称迁移、合同、冻结历史与发布保护检查，以及 80 项未改动旅行模板测试和 4 项生成器测试。旅行包与已发布历史的 224 个基线文件保持原字节。这些是本地行为与源码观察。

合集完整检查通过 534 项 pytest、158 项 unittest、编译和公开文档检查。准确候选的本地 CLI 安装通过四种顺序与模式组合，8 个目标均保留完整来源。独立 Standards/Spec 审阅未发现新的源码缺陷；Spec 审阅记录了必须补足的 Host 证据缺口。新的独立最终评估已完成，候选因必需的 Host 观察缺失而被判为 BLOCKED。真实 Codex 选择器、调用及依赖读取仍须验证；此前运行在读取 Skill 前初始化失败。不声称候选远端 CI、v0.2.7 标签安装或正式发布已经完成。见[候选证据](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/namespace-v0.2.7/producer-evidence.md)。
