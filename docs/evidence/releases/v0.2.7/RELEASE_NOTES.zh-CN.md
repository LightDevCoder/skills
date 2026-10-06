# v0.2.7：Skill 名称与迁移

[English GitHub Release](https://github.com/LightDevCoder/skills/releases/tag/v0.2.7) · [英文发布说明](RELEASE_NOTES.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md)

本次为 12 个 Skill 增加 `light-` 前缀，便于在全局安装中识别来源。内部引用、`ask-light` 路由与界面名称使用新名称。集合仍有 36 个 Skill。

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

其他 24 个名称、分类、职责和调用权限保留。`ask-light` 与 `light-travelpage` 保留名称。软件工作使用 `light-implement`，适用时组合 `light-tdd`；`review-loop` 组合 `light-code-review`。`project-review` 仍拥有最终验收。Light 依赖缺失时明确报告缺口。相对 v0.2.6，本版的变化仅为名称迁移及其引用、路由、文档、归属记录与验证。已发布的旅行手册和可选 AI 保持完整。

## 升级说明

更新 Light 的旧 `--skill` 参数和显式调用，例如 `$implement` 改为 `$light-implement`。检查项目提示、能力声明、自动化与源码软链接。处理旧名包前，确认其实际来源或链接目标，并保存副本或链接目标。重新安装不代表旧名已经清理。本版不提供旧名 alias，也不会自动迁移真实全局安装。

需要恢复时，恢复保存的 Light 副本或软链接目标，恢复相关引用；必要时重装 `#v0.2.6`。先确认恢复旧名不会覆盖其他来源的包。详见[完整迁移说明](https://github.com/LightDevCoder/skills/blob/main/docs/MIGRATION-v0.2.7.zh-CN.md)。

## 安装

v0.2.7 的实际发布源已在新鲜环境通过安装验证。可用固定标签安装所需 Skill：

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

候选源码通过 543 项 pytest、167 项 unittest、编译和公开文档检查。本地安装验证覆盖两种来源顺序和两种模式，完整包内容保留。真实 Codex 0.160.1 显示全部 12 个 Light 来源标签，并在成功的有界任务中解析 Light 入口和其依赖；另一显式入口解析到其对应安装来源。原生选择器使用已披露的临时传输适配器，Host Skill 响应保持原字节。

独立源码验收通过，准确候选 CI 和受保护 annotated tag 的远端身份已核对。新鲜托管 Linux 用户中的实际发布源安装通过：Codex、Claude Code 的固定标签及默认分支全集均为 36 个包、386 个文件，逐项匹配各自来源；原生 Codex 全局安装和 `light-implement`、`light-tdd`、`light-research` 单包也通过。HOME/CODEX_HOME 未重设。首轮验证因检查错误的全局目录失败，修正后重新验证通过；标签和包内容保持不变。

发布清单保留标签中的发布前快照，发布事实由 main 上的发布后收据证明。见[源码与运行证据](https://github.com/LightDevCoder/skills/blob/main/docs/evidence/namespace-v0.2.7/producer-evidence.md)。
