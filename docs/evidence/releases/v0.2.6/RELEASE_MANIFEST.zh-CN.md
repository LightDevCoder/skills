# LightDevCoder/skills v0.2.6 发布清单

[English manifest](RELEASE_MANIFEST.md) · [中文发布说明](RELEASE_NOTES.zh-CN.md)

本清单记录发布前的候选规范。发布后才在 `main` 创建收据，候选提交与标签中均不包含收据。

| 字段 | 值 |
| --- | --- |
| **发布版本** | `v0.2.6`（拟定，仍须核对远端是否可用） |
| **预期标签** | `refs/tags/v0.2.6` |
| **发布身份** | `refs/tags/v0.2.6^{commit}` |
| **发布范围** | `light-travelpage` 手册 UI、可见每日路线、地点选择、空日期初始化、次级界面统一、可选服务端 AI、草稿及重试恢复；相关双语集合和发布说明。 |
| **集合包数量** | 36 admitted packages，已准入包数量不变 |
| **策略状态** | `PROVISIONAL`，Jev 策略未改变 |
| **标签不可变性** | 发布后 annotated tag 永久不可修改 |
| **兼容基线** | 保留旅程与记录 ID、原件、资料事实、共享变更校验及指定范围鉴权；AI 默认关闭。 |

## 候选证据

- 运行代码基于本地旅行候选 `ae77154`，随后补齐范围内的凭据过滤与鼠标日期条修复；生成说明和 AI 示例同步采用每天一页及 to-do。
- 生产者验证：80 项模板测试、4 项生成器测试及 AI 关闭、开启和空日期北海道构建通过。实际桌面与 390px 浏览器检查覆盖日期切换、整组地点展开、材料直达、内容数量及合成 AI 只读请求。
- 集合完整检查：`python3 -m pytest -q -p no:cacheprovider` 528 项通过；`python3 -m unittest discover -s tests` 156 项通过。Compileall、公开文档检查、GitHub 发布正文链接校验与 `git diff --check` 通过。编译缓存写入临时目录，候选版本识别测试改用独立版本目录。
- 源码验收：Core 对 `d0a4b0700cc645aa9ca45bff0106a2c7badb52de` 记录 `PASS`，charter 为 `itinerary-visible-maps-2026-10-05-v2`，Profile 为 `agent-skill`，用户授权第 4/4 轮。独立 Standards/Spec 与另一全新 Evaluator 覆盖完整冻结基线；独立性为 `FULL`，无例外或未关闭阻断项。空日期完整初始化、凭据拒绝和日期条拖动均独立复核；Evaluator 重跑 80 项模板、4 项生成器检查，并核对 75 文件安装副本和实际本地发现。此前各轮保留为历史记录。
- 准备阶段已核对远端 main、版本可用性和已启用的不可变标签保护。指定提交 CI、标签及最新主干的全新安装和发布属于后续 release-workflow 门禁，须针对最终候选再次核验。本地验收不代表远端发布。

发布后才在 `main` 创建 `RELEASE_RECEIPT.zh-CN.md`，记录已核实的发布事实。
