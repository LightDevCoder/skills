# v0.1.2 发布说明（中文）

[English release notes](RELEASE_RECEIPT.md)

## 本次更新

- 新增第一方、仅 user-invoked 的 `recap` Skill：显式 `$recap` 只返回一行当前 session 总结，不运行工具、不修改历史、不调用其他 Skill。
- 新增第一方、仅 user-invoked 的 `language-learning` Skill：通过六种学习模式辅导任意目标语言，并在多次调用间复用上下文与已学词汇。
- 新增低风险纯提示型准入快速通道，`recap` 与 `language-learning` 均由此 `PASS` 准入。
- 发布通用 `latest` 安装命令，并保留 pinned `#v0.1.2` 形式用于可复现安装。
