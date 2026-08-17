# 变更记录

[English changelog](CHANGELOG.md)

所有变更都必须记录在实际版本/tag 对应的条目中，不能因为文档已起草就提前宣称 release。

## 0.1.4 — 2026-08-16

### 新增

- 新的第一方 model-invoked Skill `light-kanban-worker`：每次 scheduled
  agent 运行最多处理一张 Light-Kanban 任务——稳定 agent identity、先检查
  自己持有的 in-progress 任务与 `reviewFeedback` 再领取新任务、原子 claim
  带有限次冲突重试、workspace 校验（不可访问的 workspace 变成 `block` 并带
  具体原因）、`complete` 交回人工验收。worker 绝不 archive、accept、delete、
  recycle、unblock，也绝不循环或常驻进程。因其涉及网络/文件系统/看板状态
  副作用，走完整准入路径（`review-loop agent-skill`），不走纯提示型快速通道。
- worker 包的 contract 与 behavior 测试套件，包含 positive fixtures 与
  negative fixtures（对抗性单规则 fixture 文件）及 frontmatter YAML 安全门。
- ask-light behavior 套件新增 outside-readable-path negative 场景。

### 变更

- 版本文档同步：v0.1.4 为当前稳定 release，v0.1.3 及更早版本保持历史
  记录。README、目录、安装指南、维护基线、discovery 测试与 CI 更新为八包集合。
- 修复 ask-light scanner 的 `Test-PathUnder` 路径比较（硬编码 Windows
  分隔符），该问题使 collection-quality workflow 自 v0.1.3 Python 移植起在
  ubuntu-latest 上失败。

### Release 证据

- Release tag：`v0.1.4`，commit `a9cc8aa029c926fc80f6ddc0022793f79dfd85bd`。
- GitHub Actions `collection-quality`：release commit 上 `PASS`（run
  `31962459531`）。
- 整集合与单 Skill fresh installs：`PASS`（CLI `1.5.22`，通用 `latest` 与
  pinned `#v0.1.4` 形式）。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.4
- 整集合与单 Skill fresh-install 证据：
  [INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.4/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包级证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.4/TEST_SUMMARY.zh-CN.md)。
- 准入：[light-kanban-worker 证据](docs/evidence/admissions/light-kanban-worker/README.zh-CN.md)。
- scanner code-review：[CODE_REVIEW.zh-CN.md](docs/evidence/releases/v0.1.4/CODE_REVIEW.zh-CN.md)。
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；见
  [发布收据](docs/evidence/releases/)。

## 0.1.3 — 2026-08-10

### 变更

- 测试工具链从 Windows PowerShell 迁移为跨平台 Python：21 个 PowerShell
  测试文件替换为 18 个 Python 套件（collection discovery、header assets、
  quick start、ask-light contract、project-init contract 与 behavior、
  recap 两个 contract、language-learning contract、review-loop 五个
  profile 的 contract 与 behavior 套件及协议 helpers），保留断言集。
- ask-light scanner behavior 套件仍通过 `pwsh` 执行真实的
  `scripts/ask-light.ps1`，pwsh 缺失时优雅跳过；CI（ubuntu-latest）自带
  pwsh 并运行。
- CI 迁至 `ubuntu-latest`（bash + python）；新增 retired-boundary 与
  无 PowerShell 测试检查。
- 文档更新为新测试文件名与跨平台手动 fallback 片段；治理措辞不变。

### 证据

- [docs/evidence/releases/v0.1.3/](docs/evidence/releases/v0.1.3/)

## 0.1.2 — 2026-08-10

### 新增

- 为 v0.1.2 准备第一方、仅 user-invoked 的 `recap` Skill。用户显式调用 `$recap`
  后只返回一行当前 session 总结；不会运行工具、继续任务、修改文件、压缩历史或调用其他 Skill。
- 为 v0.1.2 准备第一方、仅 user-invoked 的 `language-learning` Skill。它通过六种
  学习模式辅导任意目标语言——每日课程、即时卡片、对话练习、语法解码、
  进度测验与沉浸翻译——并在多次调用之间复用会话上下文与已学词汇，而不是
  每次都重新询问。
- 新增低风险纯提示型准入快速通道：仅适用于 owner-authored、manual-only、
  只输出文本、无工具/副作用/runtime executable/外部依赖的 Skill；只需一个
  fresh Evaluator，不再要求额外 Critic 或 Standards/Spec review。
- 发布通用 `latest` 安装命令（`npx skills add LightDevCoder/skills --yes --copy
  --agent '*'`）作为标准安装路径，并保留 pinned `#v0.1.2` 形式用于可复现
  安装。`recap` 与 `language-learning` 均由 fresh independent prompt-only
  fast-track Evaluator `PASS` 准入，见各自[准入证据](docs/evidence/admissions/)。

### Release 证据

- Release tag：`v0.1.2`，commit `8de5ec1a453b0e93f71dcda160e17ea7b42c3997`。
- 合并后的 release commit 上 GitHub Actions `collection-quality`：`PASS`。
- 整仓和单 Skill fresh install：使用 CLI `1.5.22`，通用 `latest` 与 pinned
  `#v0.1.2` 两种形式均为 `PASS`。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.2
- 整仓与单 Skill fresh-install 证据：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.2/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包测试证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.2/TEST_SUMMARY.zh-CN.md)。
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；见
  [发布收据](docs/evidence/releases/v0.1.2/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.1 — 2026-07-26

### 新增

- 五个第一方 Skill 的双语用户指南、已验证的 workflow recipes 和可运行大小的 Quick Start 示例。
- `docs/evidence/releases/v0.1.1/` release 证据目录，以及覆盖结构、metadata、链接、双语配对、包测试、退休引用和头图的 CI 检查。
- 显式 `$ask-light next` 与 `$ask-light workflow` 模式，包含 bounded recipe、availability gap、handoff 字段和不执行测试。
- 可编辑 SVG 与 1600 × 480 PNG 头图：平面叠层的 `LightDevCoder` / `/skills` wordmark 和 serif slogan。

### 修复

- 为 user-invoked 的 `learn-anything`、`ask-light`、`project-init` 补齐 `policy.allow_implicit_invocation: false` 及对应 frontmatter。
- 修正安装语义：无 fragment 的仓库来源遵循 CLI 默认 revision，发布后 `#v0.1.1` 才是固定 target tag。

### Release 证据

- Release tag：`v0.1.1`，commit `c50f1ef403a5f0bfe02e75d1aeff2c237556db63`。
- 合并后的 release commit 上 GitHub Actions `collection-quality`：`PASS`。
- 整仓和单 Skill fresh install：使用 CLI `1.5.20`，均为 `PASS`。
- GitHub release：https://github.com/LightDevCoder/skills/releases/tag/v0.1.1
- 整仓与单 Skill fresh-install 目标记录：[INSTALLATION_VERIFICATION.zh-CN.md](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md)。
- 结构与包测试证据：[TEST_SUMMARY.zh-CN.md](docs/evidence/releases/v0.1.1/TEST_SUMMARY.zh-CN.md)。
- 五个包组成的集合仍可安装，`collection-quality` 检查已通过。`review-loop
  agent-skill` acceptance gate 的独立 evaluator 证据仍为 `BLOCKED`；这不影响
  一般安装或使用。准确证据边界见[发布收据](docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.zh-CN.md)。

## 0.1.0 — 2026-07-23

- 建立第一方治理基础并准入五个第一方 Skill。
- 已发布于 https://github.com/LightDevCoder/skills。
- 稳定 tag：v0.1.0。
- v0.1.0 的整集合与单 Skill 安装命令曾针对 fresh destination 和已发布包内容完成验证；这份历史证据与 v0.1.1 release 证据一并保留。
- 历史命令：`npx skills add LightDevCoder/skills` 和
  `npx skills add LightDevCoder/skills --skill review-loop`。
- 历史安装明细：[v0.1.0 摘要](docs/evidence/releases/v0.1.1/INSTALLATION_VERIFICATION.zh-CN.md#历史-v0.1.0-摘要)。
