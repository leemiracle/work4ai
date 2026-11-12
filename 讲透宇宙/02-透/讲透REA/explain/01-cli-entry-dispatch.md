<!-- source: knowledge-graph tour step | files: scripts/rea.mjs, src/main.ts, src/cli.ts, src/cliCommandNames.ts -->

# 第 1 篇：进程入口与 CLI 命令分派

`package.json` 把 `rea`/`rea-agents` 两个 bin 都指向 `scripts/rea.mjs`（154 行），它是唯一可执行边界；真正入口有两个：长驻 MCP 进程 `src/main.ts`（118 行，编译产物迁 `dist/mcp/main.js`）与一次性 CLI 组装器 `src/cli.ts`（140 行），`src/cliCommandNames.ts` 用一份冻结清单保证两入口能力面一致。

### 1. 角色定位

在 14 层分层的最顶端是"进程边界层"。`scripts/rea.mjs` 在加载任何重模块之前先做模式判定：单参数 `--mcp` 或 `mcp` 即 MCP 模式（scripts/rea.mjs:14-15），`mcp doctor` 走诊断（:16），其余全进 CLI。判定收益是分产物懒加载：三种模式各有一套 `runtimeFiles` 清单（scripts/rea.mjs:43-51），MCP 模式只 import `dist/mcp/main.js`（:59）。`src/main.ts:116` 还有 direct-execution 守卫：`isDirectEntrypoint` 用 `realpathSync(argv)` 对比 `import.meta.url`（src/main.ts:104-114），防止被别的脚本引入时误启动。

分工：`src/main.ts` 是 MCP 适配器装配序列；`src/cli.ts` 是纯注册工厂，构建 CLI 实例不碰分析引擎；`src/cliCommandNames.ts` 是 CLI、MCP 目录、catalog 指纹三方消费的命令名单单一事实源。

### 2. 内部结构

**src/main.ts** 导出两个函数。`runtimeDependencies()`（src/main.ts:26-34）把进程副作用（serve/writeStderr/setExitCode/registerShutdown）收进一个对象，信号注册拆在 `registerProcessShutdown`（src/main/processShutdown.ts:24-38）。`run()`（src/main.ts:41-82）按序装配：`snapshotEnvironment` 快照环境（:44）后 `parseConfig`，失败投影写 stderr 返回 1（:45-49）；随后 `createLogger`、`createBinarySession(config, logger, environment)`（:52，第三参环境是 v6.5 新签名）、`openInitialTarget`（:53-59）、`startMcpTransport`——带两件新货：`delivery`（:64）与可选观测 provider 工厂（:65-70）；最后 `createShutdown`（:73-80）。`runEntrypoint()` 是 catch-all：启动异常被 `void cause` 吞掉（src/main.ts:97），只输出固定文案 `SERVER_START_FAILED`（src/main/messages.ts:8）。

**main/ 六个子模块**各管一段（v6.1 的 reload.ts/SIGHUP 热重载已整体删除）：`startup.ts` 在 `hopperTargetPath` 未设时放行，失败先 `session.close()` 再把打开与清理错误都写 stderr（src/main/startup.ts:14-32）。`transport.ts` 加载可选观测 provider，单个失败只 warn 不阻断（src/main/transport.ts:40-57）；`serve` 工厂每次被 SDK 调用都新建 Android provider（:87-89），注释明说"SDK 可能丢弃 discovery probe 并重建 server"（:86）。`shutdown.ts` 幂等（:47-48），并行关 transport/Android/可选 provider/session，session 关闭带 `retainProviderDocuments: true`（:39），失败降级 debug 日志（:78-88）。

**src/cli.ts** 的 `createCli` 接受 environment、可选 `resultOutput` 与可选 `fridaInstrumentation`（src/cli.ts:70-76）。logger 默认 `silent`，显式设 `REA_LOG_LEVEL` 才解析（:80-87）。`Cli.create(PRODUCT_IDENTITY.cliBinary, ...)` 带 `npxRegistrationCommand().join(" ")`（:92）与 `sync: false`（:96）。随后是 **38 个** register 调用（src/cli.ts:99-136，v6.1 是 23 个），新增 cutter/frida/gdb/rizin 直通族与 adb/apktool/pcap/flutter/jeb/go/rust/sqlite/wasm 等十余个命令族。

**src/cliCommandNames.ts** 五个导出：`CLI_COMMANDS` 是 153 条冻结的属性名→kebab-case 命令名映射（src/cliCommandNames.ts:2-157，v6.1 是 94 条）；`CLI_COMMAND_NAMES` 取 `Object.values`（:160）；`CLI_COMMAND_ALIASES` 仅 `compare-bundles`（:163）；`CLI_COMMAND_TOOL_ALIASES` 记 19 组/20 条 CLI 名到 MCP 工具名映射（:166-186，含 cutter/objdump/rizin/gdb/frida 直通族）；`MCP_TOOLS_WITHOUT_DEDICATED_CLI` 列 65 个有意不做 CLI 的 MCP 工具（:189-255）。

### 3. 外部连接

`src/main.ts` 向下依赖 `composition/binary.ts` 的 `createBinarySession`（CLI 与 MCP 适配器共享的唯一生产装配点）、`config/parseConfig.js`（:10）与 `server/createServer.js`（经 transport.ts:91）。`RuntimeDependencies` 里 `createServer`、`loadOptionalProviders` 均为可选注入（src/main/types.ts:9-10）——测试接缝。

`src/cli.ts` 的 38 个 register 模块平铺在 `src/cli/`（50 个文件，无 commands/ 子目录）与 `src/cli*.ts`。注册器统一从 `CLI_COMMANDS` 取规范名（如 src/cli/setupCommands.ts:50），**没有一处硬编码命令字符串**。

`cliCommandNames.ts` 最有分量的下游是 `src/catalogIdentity.ts`：`CLI_COMMAND_NAMES` 直接进入 `combined_sha256` 指纹（src/catalogIdentity.ts:97-101），命令数进 `counts.cli_commands`（:124），即**改一个命令名会改变产品 catalog 身份**；默认摘要构建期预录 `RECORDED_CATALOG_DIGESTS` 免启动期全量 canonicalize（:117-120）。守门测试把每个 MCP 工具名（`-`换`_`）与 CLI 名单求差集，两边都不在的一律 fail，并反向校验豁免清单的名字都真实存在于 `TOOL_CONTRACTS`（tests/boundary/cli/cliToolCoverage.test.ts:23-41）。

### 4. 数据流

以 `npx rea-agents mcp` 为例。Node 启动 `scripts/rea.mjs`，先把 package.json 的 version 写进 `REA_PACKAGE_VERSION`（scripts/rea.mjs:13）；识别 MCP 模式后检查 `dist/mcp/main.js` 存在，动态 import 并 `await runEntrypoint()`（:53-60）。`run()` 里 `parseConfig` 读 `HOPPER_TARGET_PATH` 等变量，设了目标则 `openInitialTarget` 打开二进制，失败投影进 stderr、退出码 1。成功后 `startMcpTransport` 把工厂交给 SDK，数据流反转——**MCP client 的 JSON-RPC 请求从 stdin 进来**，工具调用沿 BinarySession 走到 Hopper/Ghidra/IDA/Kuna provider，应答写回 stdout。

CLI 侧 `rea analyze foo`：rea.mjs 先装 SIGPIPE 守卫 `guardClosedStdout`（scripts/rea.mjs:82,119-129），再 `validateCliOutputArguments` 校验输出过滤参数（:84）、`cliConfigurationError` 预检非法 `REA_LOG_LEVEL`（:85），然后 `createCli(...).serve(args, {stdout, exit})`（:95-107）。读者提前关管道（`| head`）不报失败，按 SIGPIPE 惯例退出 141（:18,106-108）。分析命令自建自关 session，进程随即退出——"一次性"。

### 5. 设计决策

**为什么分发层用动态 import+产物预检？** 三种模式各查各的编译产物（scripts/rea.mjs:43-51）：CLI 只加载 `dist/cli-runtime/` 三件套，MCP 模式不付 CLI 框架启动成本；编译产物缺失在 import 前给出可操作修复提示 `npm ci && npm run build:cached`（scripts/rea.mjs:54-56）。

**为什么 main.ts 全依赖注入？** 信号注册、stdio、退出码参数化后，`run` 的每个失败分支都能在 vitest 里无进程副作用地复现；`void cause`（src/main.ts:97）是安全取舍：启动期意外可能含路径/凭据细节，宁用固定文案（src/main/messages.ts:1-8）换信息量。

**为什么命令名单单独成文件？** 注册器要规范名、coverage 测试要全量清单、catalog 指纹要稳定序——单一冻结来源让"CLI 有而 MCP 无对应工具"的漂移在 CI 即被拦截。

**为什么 CLI logger 落 stderr？** `createLogger` 用 `pino.destination({dest: 2, sync: false})`（src/logger.ts:38）——stdout 全程留给 MCP 协议或 CLI JSON 结果。

### 6. 新人提示

上手顺序：先读 scripts/rea.mjs 看三模式分发，再读 src/main.ts 的 `run` 主序列，最后用 38 个 register 当目录索引下钻。易错点：①`mcp` 是被 rea.mjs 拦截的保留字，别在 Incur 里注册它；②新增 MCP 工具若不做 CLI 命令，**必须**同步补进 `MCP_TOOLS_WITHOUT_DEDICATED_CLI`，否则 coverage 测试红；③新增 CLI 命令名只能改 `CLI_COMMANDS`，动它就会变 catalog `combined_sha256`；④SIGHUP 热重载已删，改配置只能重启进程；⑤shutdown 幂等，`retainProviderDocuments: true` 让 provider 文档在会话关闭后仍可用。测试入口：`tests/boundary/cli/dispatcher.test.ts`、`cliToolCoverage.test.ts`、`tests/boundary/mcp/` 的 mainErrors/shutdown 两件套（mainReload 随 reload 删除）。
