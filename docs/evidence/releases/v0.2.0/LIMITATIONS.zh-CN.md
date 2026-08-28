# v0.2.0 局限性

[English record](LIMITATIONS.md)

- `evals.json` 是语义回归 fixture，并非实际执行的模型评估套件；作为规范覆盖率接受审阅。
- 全新安装验证在干净、隔离的环境中验证 CLI 发现与结构完整性；特定专属 Agent host 的 live host refresh 与模型运行时调用属于 host 自行行为，除 CLI 发现外不额外宣称。
- 名称冲突：Light 经批准的 Port 是完全自包含的，不依赖 `mattpocock/skills`。但在未做命名空间隔离的情况下，将两个集合同时安装到同一个物理目录可能会根据 host 优先级发生文件冲突。建议在同时使用多个集合时采用项目作用域安装。
