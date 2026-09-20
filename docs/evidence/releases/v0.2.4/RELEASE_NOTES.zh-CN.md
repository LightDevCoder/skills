# v0.2.4 — 发布完整性加固与 Git 对象严格绑定

[English Release Notes](RELEASE_NOTES.md) · [发布清单](RELEASE_MANIFEST.zh-CN.md)

Light Skills v0.2.4 全面加固了发布完整性防护栏：将发布证据校验直接绑定至不可变的 Git tree 对象、对发布后事实收据执行快照隔离与防漂移保护、强制执行 Fail-Closed 单向 Tag Preflight 门禁与 Annotated Tag 校验，并在公开文档表面建立了高质量的双语术语一致性门禁。发布后事实证明将在公开发布后于 main 分支的 RELEASE_RECEIPT.zh-CN.md 中完成收据记录。

---

## v0.2.4 主要更新

### 1. Git 对象发布证据绑定
- `RELEASE_MANIFEST.md` 与 `RELEASE_NOTES.md` 的校验严格源自候选提交 tree 对象与 Tag 快照（`refs/tags/v0.2.4^{commit}`），彻底杜绝工作区未提交或未跟踪文件穿透发布门禁。
- Tag Preflight 自动检测并拒绝目标发布路径 `docs/evidence/releases/vX.Y.Z/` 下的未跟踪证据。

### 2. 发布后收据快照严格隔离
- 在 `ATTESTED` 阶段，集合包总数校验强制绑定至发布时的不可变候选快照（`release_revision`），防止后续 `main` 分支包增减漂移破坏已发布版本的事实证明。
- 重新对 `TAGGED` 阶段进行审计时，严格仅检查 Tag 快照，杜绝工作区中已生成的收据产生假阳性干扰。

### 3. Fail-Closed 单向 Tag Preflight 与 Tag 保护
- 远端 Tag 预检默认检查 `origin`，远端查询或网络异常严格判定为 `BLOCKED`（Fail-Closed）。
- 执行单向 Tag 创建保护：本地或远端已存在同名 Tag 时严格阻断，杜绝误覆盖。
- 强制校验 GitHub Ruleset 的 active 状态、删除与更新限制、零 bypass actors 与 `current_user_can_bypass='never'`。

### 4. 强制 Annotated Tag 校验
- 严格强制发布 Tag 必须为 Annotated Tag（`git cat-file -t` 返回 `tag`），全生命周期拒绝 lightweight tag。

### 5. 零 Traceback 结构化失败机制
- 所有错误分支均规范化采用相对逻辑路径，无论在 revision 模式还是文件系统模式下，均保证零 Python 未定义变量 traceback，稳定返回结构化 `VerificationResult`。

### 6. 公开文档质量门禁
- 自动化检查统一 `README.md`、`CATALOG.md`、`INSTALLATION.md` 中英文术语，彻底消除内部实现防模式黑话，保证中英文目录语义对称。

---

## 安装方式

### 稳定版本固定安装（v0.2.4）
安装不可变且完全可复现的 v0.2.4 发布快照：

```bash
# 全量 36 个 Skill 集合：
npx skills add LightDevCoder/skills#v0.2.4 -y

# 单个 Skill 选装：
npx skills add LightDevCoder/skills#v0.2.4 --skill agent-config -y
npx skills add LightDevCoder/skills#v0.2.4 --skill project-review -y
```

### 通用最新版本安装
安装当前最新版本：

```bash
npx skills add LightDevCoder/skills -y
```
