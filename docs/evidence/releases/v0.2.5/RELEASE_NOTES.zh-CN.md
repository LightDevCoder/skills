# v0.2.5：路由、工单编号与发布检查

[English GitHub Release](https://github.com/LightDevCoder/skills/releases/tag/v0.2.5) · [发布清单](RELEASE_MANIFEST.zh-CN.md) · [验证收据](RELEASE_RECEIPT.zh-CN.md)

这版修复了证据缺失或过期时，工作流仍可能给出“可以执行”建议的问题。集合仍是 36 个 Skill。

---

## 主要变化

### 1. 不确定的状态会阻断路由

`agent-config` 需要当前 Host 记录和匹配的已确认 Profile，才会建议执行。`ask-light --mode semantic` 与主路由使用相同的项目约束，并校验最终建议。已领取工单、无法确认新鲜度的审阅证据不会再被当作可执行状态。

### 2. 工单共用一条编号序列

`decision-map`、`project-spec` 和 `project-tickets` 从现有最大编号之后创建新工单。旧项目若有重复编号，路由会停止并给出迁移指引，不会擅自改写旧工单。

### 3. 跨 Skill 交接使用当前契约

`project-init` 负责通用初始化，`manuscript-ops` 随后建立手稿专属状态。手稿依赖按当前运行时接口检查。`code-review` 仍分别检查 Standards 和 Spec，并输出 `review-loop` 可直接使用的 Findings。

### 4. 验证覆盖实际生成结果

旅行页生成和首次同步遵守同一套待办规则。CI 运行完整 Python 测试、Node 测试，以及临时生成旅程的校验和构建。远端标签或 GitHub Release 无法核实时，发布检查会停止。

---

## 升级说明

已有重复工单编号的项目需要先明确迁移，路由才会恢复。Host 或 Profile 证据缺失、过期时，应先补充并确认，再请求执行方案。本次没有新增或移除 Skill。

## 安装

固定版本快照：

```bash
npx skills add LightDevCoder/skills#v0.2.5
```

不带版本的命令跟随当前 `main`：

```bash
npx skills add LightDevCoder/skills
```

## 验证记录

注释标签指向 [`ecafc2f`](https://github.com/LightDevCoder/skills/commit/ecafc2f3da3ab25a62e7a31285658fac5a50b47f)，[候选提交 CI](https://github.com/LightDevCoder/skills/actions/runs/35858468222) 在同一提交上通过。锁定版本与最新主线的两次全新安装均发现 36 个 Skill；367 个包内文件逐字节匹配发布快照。具体命令和发布身份见[验证收据](RELEASE_RECEIPT.zh-CN.md)。同级 `agent-config` MCP 只用于契约验证，不在本次发布范围内。
