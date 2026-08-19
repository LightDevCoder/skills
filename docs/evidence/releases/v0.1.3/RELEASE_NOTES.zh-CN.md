# v0.1.3 发布说明（中文）

[English release notes](RELEASE_RECEIPT.md)

## 本次更新

- 测试工具链从 Windows PowerShell 迁移为跨平台 Python：21 个 PowerShell 测试文件替换为 18 个 Python 套件，保留断言集。
- CI 迁至 `ubuntu-latest`（bash + python）；新增 retired-boundary 与无 PowerShell 测试检查。
- 文档更新为新测试文件名与跨平台手动 fallback 片段。
