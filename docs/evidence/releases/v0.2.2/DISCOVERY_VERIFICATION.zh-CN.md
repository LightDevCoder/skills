# 发现验证记录 — v0.2.2

[English Record](DISCOVERY_VERIFICATION.md)

## 发现扫描

- 工具：`npx --yes skills list`
- 目标：从 release `v0.2.2` 安装的全新目录
- 发现 Skill 数量：36
- 结果：
  - 分布于七大分类目录下的全部 36 个 Skill 的 Frontmatter 名称与描述均正常解析。
  - `agent-config` 正常被识别为模型调用（model-invoked）执行配置器。
  - `ask-light` 正常被识别为用户调用（user-invoked）工作流顾问。
  - `project-init` 正常被识别为用户调用（user-invoked）项目初始化器。
  - 未检测到缺失依赖、无法解析的软链接或损坏的元数据。
