---
title: Claude Code 源码拆解 01：启动链路与整体架构，51 万行源码怎么组织
date: "2026-04-02 22:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 01/20 篇 · 对应主题：总览

# 启动链路与整体架构

这份泄露的 Claude Code 源码树共 1884 个 `.ts`/`.tsx` 文件、512,664 行（`find src -name "*.ts" -o -name "*.tsx" | xargs wc -l`）。体量虽大，但启动路径收束得非常窄：进程从 `src/entrypoints/cli.tsx` 进入，绝大多数子命令在动态 import 分发层就被截获，只有"默认交互/打印会话"一条路会真正加载 4683 行的 `src/main.tsx`。本篇沿这条主链路走一遍：cli.tsx 的快速引导 → main.tsx 的 commander 体系与预取编排 → init.ts 的完整初始化 → bootstrap/state.ts 的全局状态 → tools.ts / commands.ts / setup.ts 的装配层，最后给出顶层目录全景和"哪些文件是 React Compiler 产物"的辨别方法。

## cli.tsx：环境修复与快速路径分发

`src/entrypoints/cli.tsx` 只有 302 行代码（末尾另挂一行 base64 内联 sourcemap），是二进制的真正入口。它做的第一件事不是解析参数，而是修环境。文件顶部直接置 `process.env.COREPACK_ENABLE_AUTO_PIN = '0'`，修掉 corepack 自动往用户 package.json 里钉 yarnpkg 的问题（src/entrypoints/cli.tsx:5）；当 `CLAUDE_CODE_REMOTE === 'true'` 时往 `NODE_OPTIONS` 追加 `--max-old-space-size=8192`，因为 CCR 容器有 16GB 内存而默认堆上限不够用（src/entrypoints/cli.tsx:9-14）。

紧接着是一个对研究很有价值的开关，ABLATION_BASELINE 消融模式：

```typescript
if (feature('ABLATION_BASELINE') && process.env.CLAUDE_CODE_ABLATION_BASELINE) {
  for (const k of ['CLAUDE_CODE_SIMPLE', 'CLAUDE_CODE_DISABLE_THINKING', 'DISABLE_INTERLEAVED_THINKING', 'DISABLE_COMPACT', 'DISABLE_AUTO_COMPACT', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY', 'CLAUDE_CODE_DISABLE_BACKGROUND_TASKS']) {
    process.env[k] ??= '1';
  }
}
```

（src/entrypoints/cli.tsx:21-26）。注释说明这是 "Harness-science L0 ablation baseline"，用于评估实验：一键关掉 thinking、交错 thinking、compact、自动记忆、后台任务，得到一个裸 harness 基线。它必须内联在 cli.tsx 而不是 init.ts，因为 BashTool/AgentTool/PowerShellTool 在模块求值时就把 `DISABLE_BACKGROUND_TASKS` 捕获进了模块级常量，init() 跑得太晚。`feature()` 门来自 `bun:bundle`，构建期做死代码消除，外部发行版里这段整块消失。

`main()` 函数的全部职责是"在加载完整 CLI 之前截获特殊 flag"，文件注释明确写了设计原则："All imports are dynamic to minimize module evaluation for fast paths"（src/entrypoints/cli.tsx:28-32）。最极端的快路径是 `--version`：零额外 import，直接打印构建期内联的 `MACRO.VERSION` 就返回（src/entrypoints/cli.tsx:37-42）。其余快路径包括 `--dump-system-prompt`（给 prompt 敏感性评测用，53-71）、`--claude-in-chrome-mcp` / `--chrome-native-host` / `--computer-use-mcp` 三个 MCP 服务（72-93）、`--daemon-worker`（100-106）、`remote-control` 桥接模式（112-162）、`daemon`（165-180）、`ps|logs|attach|kill|--bg` 后台会话管理（185-209）、模板任务 `new|list|reply`（212-222）、两个 headless runner（226-245）、以及 `--worktree --tmux` 直接 exec 进 tmux（248-274）。

每条快路径都有一个共同点：用到什么模块才 `await import()` 什么，且每条路径都先打 `profileCheckpoint('cli_xxx_path')` 桩点。桥接模式是其中校验链最完整的：先查 OAuth token，再查 GrowthBook 运行时门（`getBridgeDisabledReason`），再查最低版本，最后查组织策略 `isPolicyAllowed('allow_remote_control')`（src/entrypoints/cli.tsx:136-159）。注释专门解释了为什么 auth 检查必须排在 GrowthBook 门之前：没有 auth，GrowthBook 没有用户上下文，只会返回陈旧的默认 false。

所有快路径都不命中时，才启动早期输入捕获（`startCapturingEarlyInput`，避免启动期间丢键盘输入），然后 `await import('../main.js')` 并调用 `cliMain()`（src/entrypoints/cli.tsx:288-298）。整个文件还用 `profileCheckpoint` 串起了一条启动观测链：`cli_entry` → 各快路径桩点 → `cli_before_main_import` → `cli_after_main_import` → `cli_after_main_complete`（48、292-298），与 main.tsx、init.ts 里的桩点衔接成完整的冷启动时间线，哪个阶段耗时可疑一眼可辨。另外有两个小 rewrite：`--update`/`--upgrade` 被改写成 `update` 子命令（277-279），`--bare` 提前置 `CLAUDE_CODE_SIMPLE=1`，让 SIMPLE 门在模块求值和 commander option 构建阶段就生效，而不是等到 action handler 里（283-285）。

## main.tsx：4683 行的 commander 体系与预取编排

`src/main.tsx` 是全仓库最大的单文件。它的前 20 行是一段"竞速"代码：

```typescript
import { profileCheckpoint, profileReport } from './utils/startupProfiler.js';
profileCheckpoint('main_tsx_entry');
import { startMdmRawRead } from './utils/settings/mdm/rawRead.js';
startMdmRawRead();
import { ensureKeychainPrefetchCompleted, startKeychainPrefetch } from './utils/secureStorage/keychainPrefetch.js';
startKeychainPrefetch();
```

（src/main.tsx:9-20）。利用 ESM 模块求值的顺序性，在剩下约 135ms 的 import 瀑布开始之前，先异步点火两类慢子进程：macOS 的 MDM 读取（plutil/reg query）和两次 keychain 读取（OAuth + 遗留 API key）。文件头注释算了这笔账：不预取的话，`isRemoteManagedSettingsEligible()` 会在 `applySafeConfigEnvironmentVariables()` 里以同步 spawn 方式串行读 keychain，每次 macOS 启动白耗约 65ms（src/main.tsx:1-8）。这就是为什么仓库里有自定义 lint 规则 `no-top-level-side-effects`：每个顶层副作用都要显式写 eslint-disable 并注释理由。

`main()` 函数本体（src/main.tsx:585）先做安全加固：置 `NoDefaultCurrentDirectoryInExePath=1` 防 Windows 当前目录 PATH 劫持（591），注册 warning handler 和 SIGINT 处理（594-606）。然后是一串 argv 重写：`cc://` 直连 URL（612-642）、deep link URI（647-677）、`claude assistant`（685-700）、`claude ssh` 的参数剥离与暂存（706-795）。接着判定会话形态：`-p/--print`、`--init-only`、`--sdk-url` 或 stdout 非 TTY 都算非交互（799-803），并从 `CLAUDE_CODE_ENTRYPOINT` 等环境变量推出 `clientType`（`github-action`/`sdk-typescript`/`claude-vscode`/`remote`/`cli` 等，818-833），写入全局状态。

commander 体系在 `run()` 里搭建（src/main.tsx:884）。`program` 配了按长选项名排序的 help（890-902）。`preAction` 钩子（907）让初始化逻辑只在真正执行命令时跑，显示 help 时不跑。钩子里做的第一件事就是回收模块求值期点火的两个预取 promise：`await Promise.all([ensureMdmSettingsLoaded(), ensureKeychainPrefetchCompleted()])`（914），然后才 `await init()`（916）、挂日志 sink（931-934）、接线 `--plugin-dir`（945-949）、跑 migrations（950）、非阻塞加载远程托管设置和 policy limits（957-958），并在 `UPLOAD_USER_SETTINGS` 门下后台上传本地设置做同步（963-965）。LSP 插件管理器的初始化则刻意不放在钩子里，而是延后到默认 action 中 trust 建立之后执行，注释说明必须排在 inline plugins 设置之后，这样 `--plugin-dir` 带来的 LSP server 才会被纳入（src/main.tsx:2317-2321）。这个钩子的存在使 `claude --help` 这类纯展示路径完全不触发 init() 的配置读取与网络预热，是 commander 用法里值得借鉴的隔离手法。

主命令的 option 链从 968 行一直排到 1006 行，四十多个选项覆盖：debug 三件套、`-p/--print` 与 stream-json 输入输出格式、`--dangerously-skip-permissions`、`--allowedTools/--disallowedTools`、`--mcp-config`、system prompt 四件套、`-c/--continue` 与 `-r/--resume`、`--model/--effort/--fallback-model`、`--agents`、`--setting-sources`、`--plugin-dir`、`--chrome/--no-chrome` 等（src/main.tsx:968-1006）。3811 行之后还有一批 feature-gated 的隐藏选项（`--advisor`、`--proactive`、`--channels`、`--teammate-mode` 等），再往后是 `mcp`、`server`、`ssh`、`auth`、`plugin marketplace`、`setup-token`、`doctor` 等子命令树（3894 起）。

默认 action 的装配顺序体现了启动性能上的主要取舍：能并行的绝不串行。

```typescript
const setupPromise = setup(preSetupCwd, permissionMode, ...);
const commandsPromise = worktreeEnabled ? null : getCommands(preSetupCwd);
const agentDefsPromise = worktreeEnabled ? null : getAgentDefinitionsWithOverrides(preSetupCwd);
commandsPromise?.catch(() => {});
agentDefsPromise?.catch(() => {});
await setupPromise;
```

（src/main.tsx:1928-1935）。注释给出数字：setup() 约 28ms，大头是 `startUdsMessaging` 的 socket bind（约 20ms），不吃磁盘，所以可以和吃磁盘的 getCommands 并行；唯一的例外是 `--worktree`，因为 setup 会 `process.chdir()`，commands/agents 必须用 chdir 之后的 cwd（1914-1918 注释）。工具集则在 action 更早的位置同步装配：`maybeActivateProactive(options)` 必须先于 `getTools(toolPermissionContext)` 调用，因为 `SleepTool.isEnabled()` 依赖 proactive 状态（src/main.tsx:1864-1868）。

首条 API 请求之前的网络预热集中在 2339-2378 行：`checkQuotaStatus()`、`fetchBootstrapData()`（一次请求刷所有缓存值）、`prefetchPassesEligibility()` 全部 fire-and-forget 并发发出；`prefetchFastModeStatus()` 也 fire-and-forget，但受 `tengu_miraculo_the_bard` kill switch 控制，命中时改为从缓存解析 org 状态。整组预热受 `tengu_cicada_nap_ms` 节流：距上次预取不足阈值就整组跳过，`--bare` 模式下也整组跳过（src/main.tsx:2345-2356）。

## init.ts：完整初始化序列

`src/entrypoints/init.ts` 的 `init` 被 `memoize` 包裹保证只跑一次（src/entrypoints/init.ts:57），整个函数包在 try 里以便把 `ConfigParseError` 转成交互式对话框（非交互会话则直接写 stderr 退出，216-231）。初始化顺序有明确的先后约束：

1. `enableConfigs()` 启用配置系统（65）；
2. `applySafeConfigEnvironmentVariables()` 只应用"安全"环境变量，完整的环境变量要等 trust dialog 通过后才应用（71-74）；
3. `applyExtraCACertsFromConfig()` 把 settings.json 里的 `NODE_EXTRA_CA_CERTS` 灌进 process.env，必须在任何 TLS 连接之前，因为 Bun 在启动时就通过 BoringSSL 缓存了证书库（76-79）；
4. `setupGracefulShutdown()` 注册优雅退出，保证退出时遥测能 flush（87）；
5. 动态 import 1P 事件日志与 GrowthBook，并注册配置变更时的 logger provider 重建（94-105）；
6. 按需点火 `initializeRemoteManagedSettingsLoadingPromise()` 和 `initializePolicyLimitsLoadingPromise()`，只初始化 promise，让 plugin hooks 等系统可以 await 它，promise 自带超时防死锁（120-128）；
7. `configureGlobalMTLS()`（137）和 `configureGlobalAgents()`（146）配 mTLS 与代理；
8. `preconnectAnthropicApi()` 预热 TCP+TLS 握手，把约 100-200ms 的握手与 action handler 的约 100ms 工作重叠（153-159）；
9. CCR 环境下懒加载 upstreamproxy，起本地 CONNECT relay 给子进程注入带凭据的上游代理，任何错误 fail-open（167-183）；
10. 注册清理钩子：LSP manager 关闭（189）、会话内创建的 teams 清理（195-200，gh-32730 修子代理创建的团队永久残留磁盘的问题）。

遥测的初始化刻意拆成两阶段。`init()` 里只埋点；真正的 `initializeTelemetryAfterTrust()` 要等 trust dialog 通过之后调用（src/entrypoints/init.ts:247）。对 eligible 用户先等远程托管设置加载、重新应用环境变量再初始化（263-271）；`doInitializeTelemetry` 用 `telemetryInitialized` 标志防双初始化且失败可重试（288-303）。`setMeterState()` 里还有一层懒加载：`initializeTelemetry` 动态 import，把约 400KB 的 OpenTelemetry + protobuf 推迟到遥测真正启用时；gRPC exporter 的约 700KB 在 instrumentation.ts 里再推迟一层（44-46、305-311）。

## bootstrap/state.ts：全局可变会话状态

`src/bootstrap/state.ts` 是全仓库唯一被允许持有全局可变状态的模块，文件头第 31 行就钉了警告："DO NOT ADD MORE STATE HERE - BE JUDICIOUS WITH GLOBAL STATE"（src/bootstrap/state.ts:31），在 428 行单例定义上方又补了一句 "AND ESPECIALLY HERE"。

结构上它是一个约 200 字段的 `State` 接口（45 起）加 `getInitialState()`（260）加模块级单例 `const STATE: State = getInitialState()`（429），外部只能通过成对的 getter/setter 访问。字段大致分几类：路径与身份（`originalCwd`、`projectRoot`、`sessionId`、`parentSessionId`）、成本与计时（`totalCostUSD`、`totalAPIDuration`、各类 turn 计数）、遥测 provider（`meter`、`loggerProvider`、`tracerProvider` 及八个 AttributedCounter）、会话级一次性标志（`sessionTrustAccepted`、`hasExitedPlanMode`、`lspRecommendationShownThisSession`）、以及一组为 prompt cache 稳定性设计的 sticky latch：`afkModeHeaderLatched`、`fastModeHeaderLatched`、`cacheEditingHeaderLatched`、`thinkingClearLatched`，一旦某个 beta header 首次发出就锁存，防止会话中段的开关翻转打爆服务端 prompt cache（226-242 的注释逐个解释了机制）。

访问模式上，state.ts 不导出 STATE 本体，只导出成对的存取函数。以会话 ID 为例：`getSessionId()` 直接读单例（src/bootstrap/state.ts:431-433），`regenerateSessionId({ setCurrentAsParent })` 在重生成前可先把当前 ID 存入 `parentSessionId`，用于 plan mode → implementation 这类会话血缘追踪（435-439 起）。全文件 1758 行里绝大部分都是这样的薄存取器，这也解释了为什么它能作为 import DAG 的叶子被任意模块安全引用：它几乎不 import 任何业务模块，文件头的注释明确说"不 import cronTasks.ts 是为了让 bootstrap 保持 import DAG 叶子"（139-142）。

两个初始化细节值得记录：cwd 会过 `realpathSync` 解符号链接并做 NFC 归一化，CloudStorage 挂载点 EPERM 时回退原始路径（263-275）；`USER_TYPE === 'ant'` 时会额外注入 `replBridgeActive` 字段，内部版和外部版的状态形状本就不同（391-395）。测试卫生靠 `resetStateForTests()` 保证，且该函数在非测试环境直接抛错（919-921）。

## 装配层：tools.ts / commands.ts / setup.ts

工具装配在 `src/tools.ts`。`getAllBaseTools()` 返回全量内置工具数组，但它不是一个静态列表，而是 feature 门与环境变量的求值现场：`USER_TYPE === 'ant'` 时才 require REPLTool/SuggestBackgroundPRTool（src/tools.ts:16-24），`feature('AGENT_TRIGGERS')` 时才挂三个 cron 工具（29-35），TeamCreate/TeamDelete/SendMessage 用 lazy require 打破循环依赖（61-72），嵌入 bfs/ugrep 的构建里 Glob/Grep 工具直接不注册（193-200 的注释说明 ARGV0 trick）。`getTools()` 是过滤入口：SIMPLE 模式只留 Bash/Read/Edit（src/tools.ts:271-296），其余情况过滤 deny 规则、REPL 模式下隐藏原语工具、再按 `isEnabled()` 筛（300-327）。`assembleToolPool()` 合并内置与 MCP 工具时有一段专门为 prompt cache 设计的排序逻辑：内置工具按名排序构成连续前缀，MCP 工具各自排序后追加，因为服务端的 cache breakpoint 打在最后一个前缀匹配的内置工具之后，交叉排序会让下游所有 cache key 失效（345-367）。

命令装配在 `src/commands.ts`。`loadAllCommands` 用 lodash memoize 按 cwd 缓存，并行加载 skills、plugin commands、workflow commands，再与内置 `COMMANDS()` 拼接（src/commands.ts:449-469）；`getCommands()` 在 memoized 结果之上每次现算可用性（auth 变化如 /login 立即生效），并把文件操作期间动态发现的 skills 插到 plugin skills 之后、内置命令之前（476-517）。

`setup.ts` 承担"会话落盘前的最后一步"：Node >= 18 检查（src/setup.ts:70-79）、`--session-id` 切换（82-84）、UDS 消息服务器启动（socket 要先绑定并导出 `$CLAUDE_CODE_MESSAGING_SOCKET`，SessionStart hook 才能拿到，89-102）、swarm 快照、终端备份恢复等。它由 main.tsx 动态 import 并与 getCommands 并行执行，上文已述。

装配完成后，控制权按会话形态分流：交互模式走 `launchRepl()`（import 自 `./replLauncher.js`，src/main.tsx:35），非交互的 print 模式走 print.ts 的独立 SIGINT 与 gracefulShutdown 路径（src/main.tsx:598-606 的注释点出了这条分流）。main.tsx 自身不实现 agent loop，loop 在根级 `query.ts`/`QueryEngine.ts` 与 `src/query/` 目录里，那是下一篇的主题。

## 顶层目录全景

`src/` 下一级目录的职责划分（按本仓实际内容归纳）：

- `entrypoints/`：进程入口层，cli.tsx 快速分发、init.ts 完整初始化、agentSdkTypes 等
- `bootstrap/`：全局状态单例 state.ts，被设计成 import DAG 的叶子
- `query/` + 根级 `query.ts` / `QueryEngine.ts`：主 agent loop，请求编排、token 预算、stop hooks
- `tools/`（42 个子目录）与根级 `tools.ts` / `Tool.ts`：每个工具一个目录，统一 `Tool` 接口
- `commands/` 与根级 `commands.ts`：斜杠命令与 skill 的加载、过滤、可用性
- `services/`：横切服务，analytics（GrowthBook/1P 事件）、api、mcp、oauth、policyLimits、remoteManagedSettings、compact、SessionMemory、lsp 等
- `components/`（389 个 .ts/.tsx 文件）：Ink TUI 的全部 React 组件
- `ink/`：vendored 并改造过的 Ink 渲染器，含 dom、frame、focus、termio
- `hooks/`：百余个 React hooks（注意：这是 UI hooks；agent 的 hooks 系统在 `utils/hooks*` 与 `types/hooks.ts`）
- `bridge/`：remote-control 桥接，把本机变成 claude.ai/code 的远端环境
- `utils/`：最大的杂项层（300+ 文件），settings、permissions、git、telemetry、worktree、swarm 都在此
- `keybindings/`、`vim/`、`voice/`、`skills/`、`plugins/`、`migrations/`、`server/`、`remote/`、`coordinator/`、`assistant/`、`buddy/`、`tasks/`、`memdir/`、`outputStyles/`、`screens/`：各垂直特性

## 辨别 React Compiler 产物

这份源码不是原始仓库形态，而是带构建痕迹的泄露源，最明显的痕迹是 React Compiler 的输出。全仓 395 个文件含有 `import { c as _c } from "react/compiler-runtime"`，按目录分布：components 294、commands 39、hooks 17、ink 12、tools 11，其余零星。形态特征以 `src/components/Spinner.tsx` 为例：

```typescript
import { c as _c } from "react/compiler-runtime";
...
function BriefSpinner(t0) {
  const $ = _c(31);
  const {
    mode,
    overrideMessage
  } = t0;
  ...
  let t1;
  let t2;
  if ($[0] !== mode) {
    t1 = () => {
```

（src/components/Spinner.tsx:1、316-330）。辨别要点：函数参数被压成 `t0` 再解构；`const $ = _c(N)` 申请定长 memo 槽位数组（N 即槽位数，由编译器静态算出）；后续用 `if ($[0] !== mode)` 这类槽位比较代替手写的 useMemo/useCallback 依赖数组，未命中时才重建值并写回槽位；临时变量名是 `t1`、`t2`、`_temp4`；参数无类型注解（类型在编译时被擦除，且这不是手写风格）。与之对照，同仓的手写源码（如 main.tsx、tools.ts）有完整 JSDoc、类型注解和单引号风格。另一个泄露源形态证据是 cli.tsx 末尾挂着整条 base64 内联 sourcemap（src/entrypoints/cli.tsx:303），`sourcesContent` 里带着原始源码，说明发布物是转译产物，而本仓部分文件保留了编译后形态、部分被还原成了源码形态。一个实用的读码推论：`.tsx` 且 import 了 `react/compiler-runtime` 的文件，其逻辑是真实的，但变量命名与控制流已被编译器改写，引用其行内"变量名"时需注明这是编译产物；而 cli.tsx、init.ts、state.ts 这类基础设施文件形态干净，可以直接按源码读。

整条启动链路串起来是：cli.tsx 修环境并分发快路径 → main.tsx 顶层点火 keychain/MDM 预取 → preAction 钩子里 init() 完成配置/mTLS/代理/优雅退出 → action 里并行 setup() 与 getCommands()、同步 getTools() → 后台预取 bootstrap 数据 → REPL 或 print 模式接管。后续篇章将沿这条链路逐个深入。

## 本篇涉及的源码文件

- `src/entrypoints/cli.tsx`：进程入口，环境修复、ABLATION_BASELINE、动态 import 快路径分发
- `src/main.tsx`：4683 行主 CLI，commander 参数体系、keychain/MDM 预取编排、setup/commands 并行装配
- `src/entrypoints/init.ts`：memoized 完整初始化，配置、mTLS、代理、优雅退出、两阶段遥测
- `src/bootstrap/state.ts`：全局可变会话状态单例，getter/setter 访问，含 prompt cache sticky latch
- `src/tools.ts`：内置工具注册表与 feature 门求值，getTools 过滤与 assembleToolPool 的 cache 友好排序
- `src/commands.ts`：斜杠命令/skills 的 memoized 加载与可用性过滤
- `src/setup.ts`：会话级 setup，Node 版本检查、UDS 消息服务器、worktree 与终端恢复
- `src/components/Spinner.tsx`：React Compiler 产物样本，`_c(N)` memo cache 形态
