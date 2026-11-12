# src/main.ts 与 CLI 命令分派：一个包，两条启动链

## 角色定位

先厘清易混点：`src/main.ts` 不是全部分派中心，而是 **MCP 服务器进程的入口**。命令分派分两层——裸 `mcp`/`--mcp` 在 scripts/rea.mjs:14-16 被截走直达本文件；`rea setup`、`rea doctor` 等一次性命令走 `dist/cli.js`（src/cli.ts），其注释明说 "bare `mcp` and `--mcp` are intercepted by the executable dispatcher before this module loads"（src/cli.ts:33-35）。main.ts 图谱 fan-out=18，是长驻进程的生命线。

## 内部结构

main.ts 两个导出加一段守卫：

- `runtimeDependencies()` 装配进程级依赖：`serve=serveStdio`（MCP SDK stdio transport）、`writeStderr`、`setExitCode`、`registerShutdown`——挂 SIGINT/SIGTERM 与 stdin end/close 并返回注销函数（src/main.ts:21-44）；`registerReload` 挂 SIGHUP 供热重载（src/main.ts:40-43）。
- `run()` 主流程：`parseConfig` 失败即返回 1（src/main.ts:54-58）；成功后 `createLogger` → `createBinarySession`（src/main.ts:59-61）→ `openInitialTarget`（src/main.ts:62-68）→ `startMcpTransport`（src/main.ts:70-76）→ reload 与 shutdown 收尾（src/main.ts:77-89）。
- `runEntrypoint()` 捕获一切异常后**刻意吞掉原因**，只输出固定 `SERVER_START_FAILED`（src/main.ts:103-108）——意外故障不得泄漏内部细节。末尾守卫比较 `realpath(argv[1])` 与 `import.meta.url`，仅直接运行才自启（src/main.ts:112-118）。

CLI 侧分派在 src/cli.ts：`createCli` 用 `Cli.create`（Incur 框架）建实例并注入 MCP 注册指引（src/cli.ts:47-56），按序调 23 个 `register*Commands`（src/cli.ts:58-80）；规范名集中在 `CLI_COMMANDS` 常量表（src/cliCommandNames.ts:1-2），setup/doctor/uninstall/update 统一注册于 src/cli/setupCommands.ts:38-96。

## 外部连接

main.ts 下游是 `src/main/` 七件套：types.ts 留 `createServer`/`loadOptionalProviders` 注入缝（src/main/types.ts:8-11）；transport.ts 加载五个可选观测 provider，单个失败仅告警不阻断（src/main/transport.ts:38-55），并为每个 discovery probe 新建 server（src/main/transport.ts:66-76）；startup.ts 失败先 `session.close()` 再退出（src/main/startup.ts:15-25）；messages.ts 存固定用户文案（src/main/messages.ts:1-8）。CLI 侧下游是 src/cli/ 下 30 个命令模块。

## 数据流

MCP 链：环境变量 → `parseConfig` 得 `Result<AppConfig, ConfigurationError>` → session 持 config → transport 每 connection 建 `createServer(session, session, {...})`（src/main/transport.ts:71-75，session 兼任分析端口）→ stdio 上双向 JSON-RPC。CLI 链：argv → rea.mjs 校验输出参数 → `createCli(...).serve(args, callbacks)`（scripts/rea.mjs:57-68）→ 命令自建自毁 session（"Analysis commands acquire and close their own sessions"，src/cli.ts:32-36）。两条链共享同一组合根，行为一致。

## 设计决策

- **依赖全走参数注入**：`run(dependencies)` 可整体替换（src/main.ts:51-53），进程副作用压到一个函数，测试可用假 serve/writeStderr 驱动全流程。
- **错误文案集中且不自曝**：启动失败只说"运行 `rea doctor` 再重启"（src/main/messages.ts:7-8），技术细节进 logger 而非 stderr。
- **分派前置到 .mjs** 是加载隔离：MCP 进程内存里干脆没有 CLI 代码。
- **命令名常量表**让 30 个注册模块与拼写解耦，重命名只改一处。

## 新人提示

加功能先问"这属于进程生命线吗"：信号、transport、reload 归这里；新分析能力不该碰它。`runEntrypoint` 吞异常是安全设计（src/main.ts:104-107），调试用 `REA_LOG_LEVEL` 开日志。新增 `mcp` 子命令必须同步改 scripts/rea.mjs:16-22 的判定与 runtimeFiles，否则分发器到不了你的代码。
