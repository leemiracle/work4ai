# 01 · 启动装配与 Web 架构

> 对应 `apps/cli/`、`packages/boot/app-boot/`、`packages/bundle/`、`packages/host/`、`packages/client/`、`packages/api/`、`packages/typert/`
> 行号钉版 `47f943859b`

## 1. Boot 流：从命令行到插件树

```text
dsh web
 → apps/cli/src/bin.ts:27   parseDshArgs（'web' = --profile web 的硬编码别名）
 → apps/cli/src/profile-boot.ts:142  composeProfile：在空根上按序叠层
      ① profile 列出的 bundles（按序）
      ② profile 自己的 cordis.patch.yml
      ③ $DSH_HOME/cordis.patch.yml
      ④ --patch 覆盖层
 → runProfile (:207) → app-boot/src/index.ts:757  boot()
      建 root Context → 装 vendored Loader → mountRootInclude(组合后的 patch 栈)
      → 等 Loader 沉降 → assertEntriesActivated 激活审计
      （失败：dispose 部分上下文并带标签 rethrow）
 → 此后用户 patch 层 watch 生效（配置级 HMR，无需重启换插件组合）
```

- **profile** = `$DSH_HOME/profiles/<name>` 目录（package.json 里 `dsh.profile` 列 bundle 顺序 + 用户 cordis.patch.yml）。
- **bundle** = npm 包声明 `"dsh": {"bundle": {"patch": "./cordis.patch.yml"}}`。内置：`dsh-base`（所有核心行）/ `dsh-web-app` / `dsh-headless`。
- patch 按 id 命中行**整体替换**其 config 或插入新行——任何内置行为都可被上层替换。
- CLI 只解析自己的 flag，其余原样交给插件树（`ctx.cmdlineArgs`）——launcher 与产品解耦。

## 2. Web：host / client 双半

**Host 半**（Node）：

| 包 | 职责 |
|---|---|
| `host/webserver` | 原生 node:http 载体，`ctx.webServer`：命名路由 + upgrade + 一个 SPA fallback 座（`src/index.ts:170` createServer、`:218` listen；默认 `127.0.0.1:3080`） |
| `host/apiproxy` | 遗留共享 API 网关（四象限 wire union） |
| `api/gateway` + `api/remotes` | 新栈：Typert RPC 双端点 + BFF（live agent 复用、冷会话恢复、并发恢复去重、转发事件白名单） |
| `host/frontend-static` | SPA dist 静态服务 |

**Client 半**（浏览器）：

- 入口 `apps/web/src/main.ts` → `AppWebEntry`（`client/web`）——**外壳内核零组合决策**。
- 两阶段引导：① 模块面——host 推送入口图 `window.__DSH_BOOT__`，`client/modules` 预取分层包；② 插件面——每个图行一个 Loader 条目挂载，模块系统经 `internal` 契约注入。
- `client/connection` 拥有传输两端：fetch RPC + 两条**只下行** WebSocket（`events.mux`/`events.host`）；Node 半持有唯一 `/api` 路由及信任栅栏（见 trust 笔记 §5）。
- `client/runtime`（React-free 对象层）：`SessionRuntime`/`WorkspaceRuntime`、slot 注册表、**ConversationNodeAssembler**——插件注册 `ConversationNodeDefinition` 把会话事件折叠为稳定会话节点（按 log seq 可重放）。
- 30+ `ui-*` 插件：声明合并 `ChatNodeDataMap` + keyed renderer 渲染聊天行，**无中央 switch**；Slots（`ui-slots`）一次 `register({name, children, store, inject}, Component)` 同时贡献组件+子声明+store 座+业务面。

**UI 渲染流**：durable 会话事件流 → mux socket → runtime 扇分 → 域插件经 `ctx.remote.$on` 失效缓存 → assembler 折叠成会话节点 → React 组件经 `useProjection`/slot hooks 消费。**UI 是会话日志的又一个投影**——与模型输入同源。

## 3. Typert：类型化 RPC 管线

解决的问题：浏览器↔host RPC 不手写 wire 类型。四包分工：

| 包 | 阶段 | 职责 |
|---|---|---|
| `typert/generator` | 构建期 | WorkspaceAnalyzer 从 TS 源产 `FaceModel`/TypeGraph → 发射带 Zod schema 的可执行 JS（host/client 双面制品） |
| `typert/registry` | 运行时 | `ctx.typert`：`<package>#<face>` 反射 + `<package>#<name>` 活 schema 存储 |
| `typert/loader` | 启动期 | 扫描 Loader 条目、import 各包 `./typert` 导出、校验 manifest、注册 |
| `typert/protocol` | 声明层 | `@Remote`/`@RemoteScope` 装饰器、可合并 `TypertRemoteMap` |

调度：Host `ctx.typertGateway.invoke()` 解析 descriptor + Cordis Service → **校验精确命名参数** → 调用 → 校验返回；Client `ctx.remote.$mount()` 装出类型化方法。

## 4. 验证命令

```bash
$ rg -n "export async function boot\(" packages/boot/app-boot/src/index.ts
757:export async function boot(
$ rg -n "function composeProfile|export async function runProfile" apps/cli/src/profile-boot.ts
142:function composeProfile(
207:export async function runProfile(...
$ rg -n "this.server = createServer|this.server.listen" packages/host/webserver/src/index.ts
170:      this.server = createServer((req, res) => {
218:      this.server.listen(this.config.port, this.config.host, () => {
```

## 5. 设计要点提炼

1. **组合即数据**——整个运行形态是 profile/bundle/patch 的有序叠加，`--dump-config` 可完整打印、逐行替换。
2. **宿主与浏览器共享一套插件协议**——`ui-*` 也是插件，聊天行渲染无中央 switch。
3. **RPC 的 schema 是生成物不是手写物**——wire 契约随源码类型漂移而再生成。
4. **UI=日志投影**——与"model-visible⟺logged"构成闭环：模型、审计、渲染三个消费者读同一事实源。

→ 下一篇：[02-SDK-ACP-Python](02-SDK-ACP-Python.md)
