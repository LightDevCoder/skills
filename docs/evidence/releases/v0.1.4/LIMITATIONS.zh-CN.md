# v0.1.4 限制

[English record](LIMITATIONS.md)

## 本 release 的已知限制

- `light-kanban-worker` 行为场景 A–F 在单台 localhost 机器上针对真实
  Light-Kanban 服务器运行。跨机器 LAN 可达性（其他主机可达看板）及对应的
  workspace 可达性区分在 Skill 契约中记录为 block 规则，未做活体测试。
- worker 的"绝不猜测 agent identity"规则是指令级约束：执行依赖运行 agent
  遵循 `SKILL.md`。
- 安装验证未声称 host refresh 与模型介导的运行时调用；CLI discovery 在
  fresh destination 上脱离 source checkout 运行。
- 包测试套件导入 collection 共享的 `tests/check_helpers.py` harness；对安装
  副本运行套件需要该 harness 在 `PYTHONPATH` 上（与 collection 其他包相同）。
- 原有五个包的独立 `review-loop agent-skill` acceptance 仍为 `BLOCKED`；这
  不影响正常安装与使用。
