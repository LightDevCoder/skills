# LightDevCoder/skills v0.1.3 发布回执

状态：`RELEASED` — tag、GitHub release、合并的 CI 与本地跨平台验证齐备。
工具链迁移版本：PowerShell 测试套件移植为 Python；CI 迁至 ubuntu-latest；
治理措辞不变。

## Identity

| 字段 | 值 |
| --- | --- |
| 仓库 | `LightDevCoder/skills`（公开） |
| 版本 | `v0.1.3` |
| 发布提交 | 本回执之后的 main |
| Release URL | https://github.com/LightDevCoder/skills/releases/tag/v0.1.3 |
| 范围 | 仅测试工具链迁移：21 个 PowerShell 测试文件替换为 18 个 Python 套件（collection、header assets、quick start、ask-light、project-init、recap、language-learning、review-loop ×5 profile） |

## 变更

- 移除 PowerShell 测试文件（`tests/*.ps1`、`skills/<name>/tests/*.ps1`、
  review-loop 协议 helpers）。
- Python 移植保留断言集（collection discovery 1064+ 断言，含组合的
  recap/language-learning 套件；各 profile 的 review-loop contract 与
  behavior 场景）。
- `ask-light` scanner behavior 套件仍通过 `pwsh` 执行真实的
  `scripts/ask-light.ps1`，pwsh 缺失时优雅跳过（CI 自带 pwsh 并运行）。
- CI：`ubuntu-latest`、bash + python；含 retired-boundary 与无 ps1 测试
  检查。
- 文档：仅更新文件名与手动 fallback 引用；治理措辞不变。

## 证据

- [测试摘要](TEST_SUMMARY.md)
- 历史版本 v0.1.1/v0.1.2 保留原证据。
