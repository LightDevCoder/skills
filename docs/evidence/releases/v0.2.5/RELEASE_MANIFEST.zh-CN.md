# LightDevCoder/skills v0.2.5 发布清单

[English manifest](RELEASE_MANIFEST.md) · [发布说明](RELEASE_NOTES.zh-CN.md)

这是固化在候选提交中的发布规格。发布后的事实收据只在完成公开发布后写入 `main`，不进入本标签快照。

| 字段 | 值 |
| --- | --- |
| **发布版本** | `v0.2.5` |
| **预期 Tag** | `refs/tags/v0.2.5` |
| **发布身份** | `refs/tags/v0.2.5^{commit}` |
| **发布范围** | Host/Profile 与工作流路由失败关闭；工单共用编号；手稿初始化与依赖契约修复；规范审阅 Findings；旅行页待办契约；CI 与远端发布验证加固；中英文文档同步。 |
| **集合包数量** | 36 admitted packages（36 个已准入包） |
| **政策状态 / Policy Status** | `PROVISIONAL`（Jev 策略未变） |
| **Tag 不可变性** | 公开发布后的注释标签永久不可变 |

## 本地候选证据

- Python：`python3 -m pytest -q -p no:cacheprovider` — 515 项通过；`unittest discover` — 156 项通过。
- 旅行页：35 项 Node 测试、生成旅程校验和构建通过。
- 当前同级 MCP `3c97180219ed1dfef8f80a9fd4be05f8f4f32077`：契约集成通过。
- 公开文档门禁与 `git diff --check`：通过。
- 远端 CI、标签身份、全新安装和 GitHub Release 将在对应阶段验证，不在此预先宣称完成。
