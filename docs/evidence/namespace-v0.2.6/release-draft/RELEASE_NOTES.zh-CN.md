# v0.2.6：Skill 名称与迁移

[英文候选说明](RELEASE_NOTES.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md)

**候选状态：BLOCKED。** 本地名称迁移候选尚未发布。远端 v0.2.6 已被旅行手册发布占用；v0.2.5 是本 checkout 的已验证发布基线。标题保留用户指定的草稿标题，不能用作现有 Release 的描述。D7 禁止覆盖标签或自行改号；见[发布阻断记录](../publication-blocker.md)。

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

其他 24 个名称、分类、职责和调用权限保留。`ask-light` 与 `light-travelpage` 保留名称。软件工作使用 `light-implement`，适用时组合 `light-tdd`；`review-loop` 组合 `light-code-review`。`project-review` 仍拥有最终验收。Light 依赖缺失时明确报告缺口。

## 升级说明

更新 Light 的旧 `--skill` 参数和显式调用，例如 `$implement` 改为 `$light-implement`。检查项目提示、能力声明、自动化与源码软链接。处理旧名包前，确认其实际来源或链接目标，并保存副本或链接目标。重新安装不代表旧名已经清理。本版不提供旧名 alias，也不会自动迁移真实全局安装。

需要恢复时，恢复保存的 Light 副本或软链接目标，恢复相关引用；必要时重装 `#v0.2.5`。先确认恢复旧名不会覆盖其他来源的包。详见[完整迁移说明](../../../MIGRATION-v0.2.6.zh-CN.md)。

## 其他变化

候选也包含 v0.2.5 标签之后已经进入仓库的变化：

- `light-travelpage` 为 PDF 票据构建受鉴权保护的首页 PNG 预览，在共用弹窗中提供缩放与原始 PDF 链接。Google 与 Apple 导航优先使用可读的当地名称和地址；补充移动端交互、地图回退和 PDF 构建 fixture 覆盖。
- 稳定版检查从目录读取目标版本，使检查与声明的稳定版本一致。
- v0.2.5 标签之后完成了发布证明与双语文档同步。英文发布页与独立中文页相互链接；历史标签快照保持原样。

## 安装

**BLOCKED 模板，不可执行。** 现有 `#v0.2.6` 指向旅行手册快照，不含新名称，不能安装本地名称迁移候选。

```bash
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6 --skill light-implement
# BLOCKED — do not execute: npx skills add LightDevCoder/skills#v0.2.6 --global --agent codex
```

不带版本的命令跟随实际 `main`，包括该分支的已准入变化，不会自动选择稳定标签：

```bash
npx skills add LightDevCoder/skills
```

## 验证记录

本地候选检查、独立审阅、候选最终验收、准确候选 CI、固定版本与默认分支新鲜安装、真实 Host 发现和调用证据尚待完成。[发布清单](RELEASE_MANIFEST.zh-CN.md)记录发布前状态。发布后验证事实只能在发布完成后于 `main` 首次创建收据。目录扫描和 Producer 自检不能代表运行时或独立验收。
