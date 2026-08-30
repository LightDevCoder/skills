# v0.2.0 安装验证补充记录 — 重指后的 tag（34 个包）

[English record](INSTALLATION_VERIFICATION_ADDENDUM.md)

Status: `VERIFIED` — 2026-08-30，发布后记录。

## 发布标识

- Tag：`v0.2.0`，由原始发布点（commit `9c2572b`，tag 对象 `29bfd22`）强推
  重指到扩展发布 commit **`e063753d880afec760f1c7b7a64b3ac601073ff9`**。
  发布线现承载 34 个第一方包：原始 33 包架构加上 `humanizer` 准入，
  并入发布后对 `agent-config` / `implement` / `ask-light` 的加固。
- 缘由：集合所有者决定不发布新版本；扩展与 `humanizer` 准入记录在正式
  `v0.2.0` 发布线上（CHANGELOG `## 0.2.0`）。
- CI：`collection-quality` 在发布 commit 上 **PASS**（`e063753`，
  run `33292549793`）。

## 对已发布仓库的全新安装验证（PASS）

环境：macOS 上的隔离临时目录；Skills CLI **`1.5.23`**（`npx --yes
skills@latest`）；来源为实际已发布仓库 tag（`LightDevCoder/skills#v0.2.0`）；
`--copy` 模式；不依赖任何本地源码检出。

| 范围 | 命令 | 结果 |
| --- | --- | --- |
| 单包 | `npx --yes skills add LightDevCoder/skills#v0.2.0 --skill humanizer --yes --copy` | `PASS` —— 安装进检测到的 agent scope（`.agents/skills/`、`.zcode/skills/`）；4 个包文件与 tag 逐字节一致；对安装副本的发现扫描通过（`name: humanizer`、model-invoked policy、`references/zh-adaptation.md` 可解析、`ATTRIBUTION.md` 存在）。 |
| 整集合 | `npx --yes skills add LightDevCoder/skills#v0.2.0 --yes --copy` | `PASS` —— 安装 34 个包；257 个包文件与 `git show v0.2.0:` 内容逐一比对，0 缺失、0 差异（`skills/docs/` 为集合资产，不属于安装的包内容）。 |

## 边界

- 本补充记录覆盖重指 tag 的已发布仓库安装验证；所有者个人主机上的
  host 级发现记录见 [humanizer 准入记录](../../admissions/humanizer/README.zh-CN.md)。
- 原始 v0.2.0 验证记录
  （[INSTALLATION_VERIFICATION.md](INSTALLATION_VERIFICATION.md)、
  [RELEASE_RECEIPT.md](RELEASE_RECEIPT.md)）保持不变，仍描述原始 33 包
  发布；本补充记录描述扩展。
- 通用 `latest` 安装命令跟随仓库默认 revision，从 `main` 安装同样的
  34 包树。
