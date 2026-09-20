# LightDevCoder/skills v0.2.2 发布收据

[English Receipt](RELEASE_RECEIPT.md)

状态：`CANDIDATE` —— 发布候选（Release candidate）已在本地准备就绪；Tag 创建、远端发布推送及远端验证正等待 Phase 2 发布门禁与人类确认。

## 标识信息

| 字段 | 属性值 |
| --- | --- |
| 仓库 | `LightDevCoder/skills` (公开) |
| 发布版本 | `v0.2.2` |
| 发布 commit | 候选 commit（将被 tag 为 `v0.2.2`） |
| 发布 tag | `v0.2.2` |
| 发布 URL | https://github.com/LightDevCoder/skills/releases/tag/v0.2.2 |
| 范围 | 涵盖 7 大按职责分类目录下的全部 36 个第一方 Skill；收敛并稳定化 `ask-light`、`agent-config` 和 `project-init` 的 TypeSafe Jev System One 语义加速能力；官方 Skills CLI 规范映射与作用域；临时非对称降级防御策略；建立不可变 Release 边界。 |
| 集合包数量 | 36 个已准入包 |
| 工作区状态 | `CLEAN` |
| 策略状态 | `PROVISIONAL`（暂定） |
| Tag 不可变性 | 发布后永久不可变（Permanently immutable） |

## 变更内容

- **Release 边界与 Tag 不可变性：** 建立不可变发布快照。已发布的 Tag 永久不可变：绝不强制移动（force-move）、绝不重指向（retarget）、绝不重写代码边界。发布后的元数据维护仅限通过不移动 Tag 的显式文档修正或递增 Patch 版本进行。
- **发布完整性守卫与复盘技能演化：** 增加自动化前置检查 `scripts/verify_release_integrity.py`，确定性校验 Tag 不可变性（同 Target 幂等放行，异 Target 强行阻断）、双语发布收据与 Git 工作区干净度。将 `project-retro` 升级为具备工作流感知、三态去重（`CLOSED` / `PARTIAL` / `OPEN`）与价值判断矩阵的完整复盘 Skill。固化官方 Skills CLI 规范映射参考文档 `skills_cli_conventions.md`，建立 Companion 双层测试架构（封闭 Schema 快照 + 跨仓漂移监控），并精简全局动态寻路指针。
- **`ask-light` 语义路由与查询规划：** 最终收敛的架构由 Python 证据引擎独占工作流权威；Jev 查询仅在存在活跃消费者时触发（多候选时调用 Choice；关键歧义与深度推理升级调用 Noul）。Jev 绝不赋予工作流流转授权；执行意图相关查询已被完全移除。零价值查询自动跳过。
- **`project-init` 官方 Skills CLI 集成：** 严格遵循 `vercel-labs/skills` v1.7.0 CLI 映射（`pi`, `claude-code`, `cursor`, `codex`, `antigravity`, `grok`, `hermes-agent`）及规范项目作用域（`.agents/skills` 适用于 Cursor、Codex 与 Antigravity）。不支持环境（如 DSH）严格确定性 Fail-Closed。提供可选 TypeSafe Jev 生态接入（`--jev` / `--no-jev`）、安全凭据解析（优先 `os.environ` 其次 `.env`）、写入前强制 `.gitignore` 保护，以及全局 Skill 复用。
- **`agent-config` 抽象任务分析与非对称降级防御：** 实现跨厂商解耦的抽象任务画像（routine, standard, high）与推理需求（low, medium, high）。无标签泄露的干净评测，权威输入完全由代码独占。执行临时非对称降级防御策略（置信度 `>= 0.75` 且边界裕度 `>= 0.15`，策略状态：`PROVISIONAL`）。
- **真实评测实证（AC-02）：** 提议将基线 `standard` 降级为 `routine` 的请求因置信度不足（0.59 < 0.75）且临近分档边界（分值 0.41）被安全拦截，正确保留基线 `standard` 档位（`claude-3-5-sonnet`）。
- **分类目录结构重组：** 将全部 36 个第一方 Skill 归入 `skills/` 下的七大分类目录（`project`, `thinking`, `engineering`, `review`, `knowledge`, `writing`, `productivity`），同时完全保留宿主端平铺安装与官方 CLI 选装兼容性。

## 验证检查表

| 门禁 | 状态 | 证据 |
| --- | --- | --- |
| 本地测试套件 | `PASS` | 409 passed（独立无外部 companion 仓库环境：408 passed, 1 skip: `test_layer1_deterministic_schemas_via_companion_ajv`）；39 unittest（271 断言）；compileall clean；git diff --check clean |
| Jev 评测实证 | `PASS` | AC-02 分值：0.41，置信度：0.59，最终档位：standard（`Policy status: PROVISIONAL`） |
| Phase 2 人类审批门禁 | `PENDING` | 当前仅本地提交；等待人类确认后方可进行远端推送与发布 |
| GitHub Actions CI (`collection-quality`) | `PENDING` | 等待推送到 main 后触发 |
| 锁定版本全量全新安装 | `PENDING` | `npx skills add LightDevCoder/skills#v0.2.2 -y` |
| 默认最新全量全新安装 | `PENDING` | `npx skills add LightDevCoder/skills -y` |
| 发现校验 | `PASS` | 36 个包的 Frontmatter 与契约全部正常发现 |

## 发布溯源说明（Provenance Note）

Release `v0.2.1` 最初于 2026-09-16 在 commit `70a48ef`（发布收据中记录为 `cb17b17c8227b7d7211e4bf5b72223703d987d60`）发布。在随后的 Jev 集成加固迭代周期中，其 Tag 曾被移动（先至 `6f9d173`，后至 `27f16e4`）。Release `v0.2.2` 正式确立全新的不可变发布边界。
