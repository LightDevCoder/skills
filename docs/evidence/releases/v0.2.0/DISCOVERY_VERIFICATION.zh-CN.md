# v0.2.0 host 发现机制验证

[English record](DISCOVERY_VERIFICATION.md)

状态：`PASS`（Skills CLI `1.5.23`）

在无源码检出的全新隔离环境中完成安装后：
- 全集合安装：`npx --yes skills list` 正常退出（退出码 `0`），成功发现全部 33 个已安装包。
- 单个 Skill 安装：`npx --yes skills list` 正常退出（退出码 `0`），各包均恰好发现所安装的单个包。

详细的各命令执行结果与路径记录在 [INSTALLATION_VERIFICATION.zh-CN.md](INSTALLATION_VERIFICATION.zh-CN.md)。
