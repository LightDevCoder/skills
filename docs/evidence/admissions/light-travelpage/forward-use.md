# 独立安装后正向使用观察

本报告仅记录行为观察，不给出最终准入结论。使用入口为 `.scratch/install-final-package/.agents/skills/light-travelpage/SKILL.md`，并读取其四份 references、安装包 `agents/openai.yaml` 及生成项目的数据模板和 validator。未读取候选修复内容或既往评审报告；未读取或使用根项目、演示项目或宿主的部署凭据。

## Success：生成、构建、更新

场景为明确标注的虚构杭州行程：2026-10-01 至 2026-10-02；第一天西湖步行，第二天自由活动待确认；无已确认坐标、预订或票据；需要共享记账和任务。生成项目在 `.scratch/forward-use/hangzhou`。

从仓库根执行：

```sh
node .scratch/install-final-package/.agents/skills/light-travelpage/scripts/create.mjs .scratch/forward-use/hangzhou
```

退出 0，创建成功。按数据合同填写完整 JSON，tripId 为 `hangzhou-fictional-20261001`；启用 itinerary、todo、ledger。overview 因坐标未确认关闭；flights、driving 关闭。空票据、预订、行前任务容器保留，没有虚构材料或具体任务。日期、安排、地图不可用原因在数据中保留，私有来源索引位于 `.scratch/forward-use/private/source-index.md`，没有加入站点。

在生成项目执行：

```sh
node --version
npm ci
npm run build
npm test
npm run validate
npx wrangler --version
```

实际 Node 为 `v26.7.0`，Wrangler 为 `4.131.1`。`npm ci` 退出 0，新增 44 包、audit 45 包、0 vulnerabilities。npm 对 esbuild、fsevents、workerd 给出 allowScripts 未覆盖警告；未修改 npm 全局设置。build 退出 0，报告因地图模块关闭而跳过地图，并生成 protected site 的 dist。tests 为 23/23 通过、0 failed、0 skipped，日志在 `.scratch/forward-use/initial-tests.log`。validate 为 `ok: true`、空 errors/warnings。

对第二天标题和说明进行保留“待确认”语义的文案更新，完整 next JSON 在 `.scratch/forward-use/next-trip.json`。执行：

```sh
node .scratch/install-final-package/.agents/skills/light-travelpage/scripts/update.mjs .scratch/forward-use/hangzhou .scratch/forward-use/next-trip.json
npm run build --prefix .scratch/forward-use/hangzhou
```

均退出 0。更新工具生成 `.trip-backups/1789237115472-6806347b-b16b-44a6-8ceb-ea2c2b6d0c2b.json`，报告 cloud runtime data was not changed。程序比较确认 tripId 相同，且将第二天恢复为旧内容后，完整对象与更新前相等：所有无关字段和稳定记录 ID 保持。

## Failure：无效日期拒绝且保留旧数据

将第二天日期改成不存在的 `2026-02-30`，其他字段不变，执行：

```sh
node .scratch/install-final-package/.agents/skills/light-travelpage/scripts/update.mjs .scratch/forward-use/hangzhou .scratch/forward-use/invalid-trip.json
```

退出 1，明确报错 `Day 2 has invalid date` 和 `Day 2 date does not match trip`。失败前后 trip-data.json 的 SHA-256 完全相同：`0b990725ff8cce2ead601428f7648a65bfedbb3ec240898e364dafcfa48e06de`。程序化结果在 `.scratch/forward-use/update-results.json`。没有放宽校验器。

## Boundary：部署及运行证据

本隔离场景未提供 GitHub/Cloudflare 凭据或已选远端资源，故没有创建代码仓库、远端 D1/Pages、设置远端 secrets 或发布。没有 live URL、远端 Functions 编译证明、远端鉴权或双会话同步证据；本地 build/tests 不代表这些证据。

为按文档尝试本地 D1，创建了只用于隔离本地运行的 wrangler.jsonc（全零 database_id 是本地占位符，不能当作真实远端资源）和 mode 0600 的随机合成 `.dev.vars`；访问码只写入隔离私有目录。第一次误在根 cwd 执行：

```sh
XDG_CONFIG_HOME="$PWD/.isolated-config" WRANGLER_SEND_METRICS=false npx wrangler d1 migrations apply hangzhou-forward-use-local --local
```

退出 1：`No configuration file found`。其隔离日志目录已用 `trash .isolated-config` 清理。改为生成项目 cwd 后尝试：

```sh
XDG_CONFIG_HOME="$PWD/../isolated-config" WRANGLER_SEND_METRICS=false npx wrangler d1 migrations apply hangzhou-forward-use-local --local && XDG_CONFIG_HOME="$PWD/../isolated-config" WRANGLER_SEND_METRICS=false npm run preview -- --port 8899
```

工具仅捕获 Wrangler 的 `Resource location: local`，随后收尾时会话 ID 已不存在，未获得最终迁移结果或实际 loopback URL。因此本报告不认定本地 D1 迁移或预览通过，未补充新的运行测试。未做独立移动浏览器观察、PDF 打开测试（输入无 PDF）或远端双会话测试。

下一步须在用户授权的目标账户下确认登录和 GitHub/Pages/D1 目标，替换本地占位资源配置，完成远端 migration、secrets、带 Functions 的部署，再取得实际 URL 上的受保护资源与同步证据。地图继续等待确认坐标，不能用估算坐标填空。

## Invocation：调用方向与负向问题

安装包 SKILL frontmatter 的 description 明确将用途限定为 travel webpage creation or maintenance，并排除 ordinary travel questions / booking purchases；正文声明 model-invoked。`agents/openai.yaml` 设置 `policy.allow_implicit_invocation: true`，default_prompt 指向生成多人共享网页及 GitHub/Cloudflare 部署。因此它允许模型按语义隐式选择，也支持显式 `$light-travelpage`，不是只能显式触发。

普通问题 “What should I pack for Hangzhou?” 不应触发本 Skill：没有网页创建或维护意图，只是旅行咨询。若明确要求把已给定物品添加到现有共享旅行页面，则属于维护页面，才匹配该用途。
