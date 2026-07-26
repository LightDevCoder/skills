# v0.1.1 限制

[English limitations](LIMITATIONS.md)

- `NOT TESTED`：整仓和单 Skill fresh public install 必须针对真实 remote tag 运行。
- `BLOCKED`：尚无独立 `review-loop agent-skill` Evaluator 记录；同一上下文检查不能标为 independent。
- `NOT TESTED`：GitHub Actions 状态要等公开 release commit 的 runner 执行。
- 不同 host 的 Skills destination 和 refresh/discovery 行为不同；公开记录不能包含私人路径或凭据。
- Direct upstream 和 private third-party 包依赖可见性；本第一方仓库不复制或代售它们。

