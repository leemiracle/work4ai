---
title: Claude Code 源码拆解 12：沙箱与容器出口代理
date: "2026-04-11 09:30"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---

> 系列第 12/20 篇 · 对应主题：隔离执行环境

# Claude Code 源码拆解 12：沙箱与容器出口代理

Claude Code 里有两套互相独立、目标不同的隔离机制。第一套面向本地 CLI：把 Bash 工具执行的命令包进操作系统级沙箱（macOS seatbelt / Linux bubblewrap），由 `src/utils/sandbox/sandbox-adapter.ts` 桥接外部包 `@anthropic-ai/sandbox-runtime`。第二套面向 CCR（Claude Code Remote）云端容器：容器出站被网关封死，所有 HTTPS 流量必须经过 `src/upstreamproxy/` 里的本地 CONNECT→WebSocket 中继，由服务端 MITM 并注入组织凭据。前者防"模型生成的命令伤害宿主机"，后者防"容器里的命令绕过组织审计与凭据管控"。本篇按源码把两条链路分别拆开。

## sandbox-adapter：settings → SandboxRuntimeConfig 的转换层

`sandbox-adapter.ts` 的自我定位写在文件头注释里：它是 sandbox-runtime 与 Claude CLI 的设置系统、工具集成之间的桥（src/utils/sandbox/sandbox-adapter.ts:1-5）。对外它导出单例 `SandboxManager`（src/utils/sandbox/sandbox-adapter.ts:927），其中一小半方法是自实现，一大半直接转发给 `BaseSandboxManager`，例如 `getFsReadConfig`、`getProxyPort`、`getSandboxViolationStore` 等（src/utils/sandbox/sandbox-adapter.ts:946-960）。

主要工作是 `convertToSandboxRuntimeConfig()`（src/utils/sandbox/sandbox-adapter.ts:172），把 Claude Code 的 settings/permissions 体系翻译成 sandbox-runtime 的 `SandboxRuntimeConfig`。翻译规则分几路：

- 网络侧：从 `sandbox.network.allowedDomains` 和 `WebFetch(domain:...)` allow 规则提取 `allowedDomains`，从 deny 规则提取 `deniedDomains`（src/utils/sandbox/sandbox-adapter.ts:198-220）。当 policySettings 里设了 `allowManagedDomainsOnly` 时，只采纳托管来源的域名，用户级配置被忽略（src/utils/sandbox/sandbox-adapter.ts:182-196）。
- 文件系统写侧：`allowWrite` 默认包含 `'.'` 和 Claude 临时目录（src/utils/sandbox/sandbox-adapter.ts:225），再加上 worktree 主仓库路径（src/utils/sandbox/sandbox-adapter.ts:286-288）和 `--add-dir` 添加的目录（src/utils/sandbox/sandbox-adapter.ts:295-299）。
- 文件系统规则抽取：遍历所有 settings 来源，把 `Edit(...)` allow 规则变成 `allowWrite`、`Edit(...)`/`Read(...)` deny 规则变成 `denyWrite`/`denyRead`（src/utils/sandbox/sandbox-adapter.ts:304-327）。

路径解析有两套语义，容易弄混。权限规则里的 `/foo` 是"相对于 settings 文件所在目录"，由 `resolvePathPatternForSandbox` 处理；而 `sandbox.filesystem.allowWrite` 里的 `/foo` 按标准语义是绝对路径，由 `resolveSandboxFilesystemPath` 处理。注释里明确记录了这是 issue #30067 的修复：用户合理地期望绝对路径按原样生效（src/utils/sandbox/sandbox-adapter.ts:130-146）。

配置的形态由 `src/entrypoints/sandboxTypes.ts` 定义，文件头声明它是 SDK 与 settings 校验共用的单一事实来源（src/entrypoints/sandboxTypes.ts:1-6）。schema 里有几个值得单独看的字段：`allowManagedDomainsOnly` 置真时，用户级、项目级、本地、flag 来源的域名全部失效，只认托管设置，但 deniedDomains 仍从所有来源生效：收紧只针对放行面，不针对封禁面（src/entrypoints/sandboxTypes.ts:18-24）。`allowUnixSockets` 标注为 macOS only，因为 Linux 的 seccomp 无法按路径过滤（src/entrypoints/sandboxTypes.ts:25-30）。`enableWeakerNetworkIsolation` 的 describe 直白写明 "Reduces security"：它放行 `com.apple.trustd.agent`，让 Go 系 CLI（gh、gcloud、terraform）在 MITM 代理加自定义 CA 的场景下能验证 TLS，代价是打开一条经 trustd 服务的数据外泄通道（src/entrypoints/sandboxTypes.ts:125-133）。这些"weaker"开关的存在说明沙箱默认姿态偏严，松动需要逐项显式授权。

### 防沙箱逃逸：denyWrite 清单

转换器里有一段防御逻辑：阻止沙箱内进程修改"能影响沙箱决策"的文件：

```typescript
const settingsPaths = SETTING_SOURCES.map(source =>
  getSettingsFilePathForSource(source),
).filter((p): p is string => p !== undefined)
denyWrite.push(...settingsPaths)
denyWrite.push(getManagedSettingsDropInDir())
// ...
denyWrite.push(resolve(originalCwd, '.claude', 'skills'))
```

（src/utils/sandbox/sandbox-adapter.ts:232-252）。所有来源的 settings.json、托管配置 drop-in 目录、`.claude/skills` 都被 denyWrite。skills 与 commands/agents 同级，会被自动发现自动加载，拥有完整 Claude 能力，因此需要同等的 OS 级保护；sandbox-runtime 自带的危险目录表只覆盖前两者，skills 由适配层补上（src/utils/sandbox/sandbox-adapter.ts:247-251）。

另一处防护针对 bare git repo。Git 的 `is_git_directory()` 只要看到 cwd 下有 `HEAD` + `objects/` + `refs/` 就把它当裸仓库；攻击者（通过沙箱内命令）在 cwd 种下这几个文件加一个带 `core.fsmonitor` 的 config，就能在 Claude 后续执行未沙箱化的 git 命令时逃逸。处理方式是分情况：文件已存在就 denyWrite（只读绑定，不留桩）；文件不存在就记入 `bareGitRepoScrubPaths`，命令结束后由 `scrubBareGitRepoFiles()` 用 `rmSync` 清掉（src/utils/sandbox/sandbox-adapter.ts:257-280, 404-414）。不直接 denyWrite 不存在文件的原因也写在注释里：那会让 sandbox-runtime 在这些路径挂载 /dev/null，留下 0 字节 HEAD 桩并搞坏沙箱内的 `git log HEAD`（src/utils/sandbox/sandbox-adapter.ts:261-266）。清理挂在 `cleanupAfterCommand` 上（src/utils/sandbox/sandbox-adapter.ts:963-966）。

### 启用判定与初始化

`isSandboxingEnabled()` 串了四道闸门：平台支持（macOS/Linux/WSL2，WSL1 排除）、依赖检查（ripgrep 等）、未文档化的 `enabledPlatforms` 企业限制、`sandbox.enabled` 设置项（src/utils/sandbox/sandbox-adapter.ts:532-547）。`enabledPlatforms` 的注释交代了来历：NVIDIA 企业部署想只在 macOS 上开 `autoAllowBashIfSandboxed`，等 Linux/WSL 沙箱更成熟再放开（src/utils/sandbox/sandbox-adapter.ts:501-504）。

`initialize()` 用模块级 `initializationPromise` 防重入，promise 在任何 await 之前同步创建，避免 `wrapWithSandbox()` 抢在赋值前调用产生竞态（src/utils/sandbox/sandbox-adapter.ts:757-759）。`wrapWithSandbox()` 本身在沙箱启用时会先 await 这个 promise，未初始化则直接抛错（src/utils/sandbox/sandbox-adapter.ts:704-717）。初始化成功后订阅 settings 变更，动态调用 `BaseSandboxManager.updateConfig` 热更新配置（src/utils/sandbox/sandbox-adapter.ts:776-781）；权限变更后另有同步的 `refreshConfig()` 立即重建配置，注释说明 refreshConfig 必须是同步的，否则排队中的请求会带着旧配置漏过去（src/utils/sandbox/sandbox-adapter.ts:798-803, 762-764）。失败路径只记日志不抛错（src/utils/sandbox/sandbox-adapter.ts:782-788）。配套的 `getSandboxUnavailableReason()` 解决另一个问题（issue #34044）：用户显式开了 sandbox 但依赖缺失时，之前会静默退回非沙箱执行，用户配了 `allowedDomains` 却毫无强制力；现在启动时给出具体原因和修复提示（src/utils/sandbox/sandbox-adapter.ts:550-592）。

平台差异还有一处显式处理：Linux/WSL 上 bubblewrap 不支持 glob，`getLinuxGlobPatternWarnings()` 会扫描 Edit/Read 权限规则里除尾部 `/**` 外仍含 `*?[]` 的模式，逐条返回警告，让用户知道哪些规则在 Linux 下不会完整生效（src/utils/sandbox/sandbox-adapter.ts:597-642）。

## shouldUseSandbox：每条命令的裁决

每条 Bash 命令执行前由 `shouldUseSandbox()` 裁决（src/tools/BashTool/shouldUseSandbox.ts:130），BashTool 和 PowerShellTool 都调用它（src/tools/BashTool/BashTool.tsx:896, src/tools/PowerShellTool/PowerShellTool.tsx:746）。逻辑只有四层：

1. 沙箱未启用 → false；
2. 模型传了 `dangerouslyDisableSandbox` 且 `allowUnsandboxedCommands` 策略允许 → false；
3. 无 command → false；
4. 命中 `excludedCommands` → false。

`containsExcludedCommand` 的体量远大于裁决函数本身，因为它在做模式匹配的鲁棒性工程。先把复合命令按 `&&`/`;` 等切成子命令分别检查，防止 `bazel run x && curl evil.com` 因子命令命中排除而整体逃出沙箱（src/tools/BashTool/shouldUseSandbox.ts:60-69）。然后对每个子命令做不动点迭代：反复剥掉前导环境变量（`FOO=bar`）和安全包装命令（`timeout 30`）直到不再产生新候选，使 `timeout 300 FOO=bar bazel run` 也能匹配 `bazel:*`（src/tools/BashTool/shouldUseSandbox.ts:82-101）。最后用 prefix/exact/wildcard 三种规则类型匹配（src/tools/BashTool/shouldUseSandbox.ts:103-124）。

文件头的 NOTE 明确了设计边界：`excludedCommands` 是便利性特性而非安全边界，能绕过它不算安全漏洞，安全边界由会向用户提问的沙箱权限系统承担（src/tools/BashTool/shouldUseSandbox.ts:18-20）。另外 Anthropic 内部用户（`USER_TYPE === 'ant'`）还叠加了一层 GrowthBook 动态下发的禁用命令/子串表 `tengu_sandbox_disabled_commands`（src/tools/BashTool/shouldUseSandbox.ts:23-50）。PowerShellTool 在 Windows 原生环境下直接跳过裁决返回 false，因为 Windows 不在支持平台列表内（src/tools/PowerShellTool/PowerShellTool.tsx:743-746）。

裁决之外还有一道兜底在初始化侧：`initialize()` 会包装调用方传入的 `sandboxAskCallback`，当 `allowManagedDomainsOnly` 策略生效时，对任何网络放行请求直接返回 false 并记日志，保证 REPL 和 print/SDK 两条代码路径都被策略覆盖（src/utils/sandbox/sandbox-adapter.ts:743-755）。这样即使模型在沙箱内触发了交互式域名放行询问，托管策略也会在回调层直接拒绝。

## 违规存储与 UI

sandbox-runtime 的 `SandboxViolationStore` 由适配层再导出（src/utils/sandbox/sandbox-adapter.ts:985）。UI 侧 `SandboxViolationExpandedView` 订阅这个 store，取最近 10 条违规展示，总数为 0 时不渲染；Linux 平台直接不渲染（src/components/SandboxViolationExpandedView.tsx:35-55）。stderr 里由 sandbox-runtime 注入的 `<sandbox_violations>` 标签在展示前由 `removeSandboxViolationTags` 剥掉（src/utils/sandbox/sandbox-ui-utils.ts:10-12）。命令结束后 BashTool 还会用 `annotateStderrWithSandboxFailures` 把沙箱失败标注进输出（src/tools/BashTool/BashTool.tsx:710）。

`/sandbox` 命令（内部目录名 sandbox-toggle）是配置入口：无参数时渲染 `SandboxSettings` 交互面板，`/sandbox exclude "pattern"` 子命令把模式写入 localSettings 的 `excludedCommands`（src/commands/sandbox-toggle/sandbox-toggle.tsx:43-71）。命令描述动态生成，汇总启用状态、auto-allow、fallback 是否允许、依赖是否缺失、是否被策略锁定（src/commands/sandbox-toggle/index.ts:7-37）。面板有三个模式（auto-allow、regular、disabled），选择即调用 `SandboxManager.setSandboxSettings` 落盘（src/components/sandbox/SandboxSettings.tsx:112-139）。依赖缺失时面板只显示 Dependencies 标签页，逐项列出 seatbelt（macOS 内建）、ripgrep、bubblewrap、socat、seccomp 的安装状态（src/components/sandbox/SandboxDependenciesTab.tsx:57-93）。被 flagSettings/policySettings 锁定时整个配置入口直接报错退出（src/commands/sandbox-toggle/sandbox-toggle.tsx:33-37）。

## upstreamproxy：容器侧的出口代理

切换到 CCR 容器场景。`upstreamproxy.ts` 的文件头注释完整列出了启动序列（src/upstreamproxy/upstreamproxy.ts:1-20）：

1. 从 `/run/ccr/session_token` 读会话令牌；
2. `prctl(PR_SET_DUMPABLE, 0)` 反调试；
3. 下载上游代理 CA 证书并与系统 CA bundle 拼接；
4. 启动本地 CONNECT→WebSocket 中继；
5. 中继确认起来之后才 unlink 令牌文件；
6. 向所有 agent 子进程暴露 `HTTPS_PROXY`/`SSL_CERT_FILE`。

每一步都 fail open，注释原文："Every step fails open: any error logs a warning and disables the proxy. A broken proxy setup must never break an otherwise-working session."（src/upstreamproxy/upstreamproxy.ts:16-17）。

启用条件是两道环境变量闸门：`CLAUDE_CODE_REMOTE` 和 `CCR_UPSTREAM_PROXY_ENABLED`。后者由 CCR 服务端评估 GrowthBook 后注入，因为容器是全新的、客户端 GB 缓存永远是默认值（src/upstreamproxy/upstreamproxy.ts:85-94）。

反调试这步通过 Bun FFI 直接调 libc：

```typescript
const ffi = require('bun:ffi') as typeof import('bun:ffi')
const lib = ffi.dlopen('libc.so.6', {
  prctl: { args: ['int', 'u64', 'u64', 'u64', 'u64'], returns: 'int' },
} as const)
const PR_SET_DUMPABLE = 4
const rc = lib.symbols.prctl(PR_SET_DUMPABLE, 0n, 0n, 0n, 0n)
```

（src/upstreamproxy/upstreamproxy.ts:228-237）。目的是阻止同 UID 进程 ptrace 本进程堆内存，防止提示词注入后模型执行 `gdb -p $PPID` 把 session token 从堆里刮出来（src/upstreamproxy/upstreamproxy.ts:220-224）。仅 Linux 生效，其他平台静默跳过。

令牌生命周期管理有一个顺序细节：`unlink(tokenPath)` 放在 relay 监听确认成功之后，而不是读完就删。这样 CA 下载或 `listen()` 失败时，supervisor 重启还能用磁盘上的令牌重试；一旦中继起来，令牌就只存在于堆内存（src/upstreamproxy/upstreamproxy.ts:138-144）。

CA 安装是 MITM 能工作的前提：从 `${baseUrl}/v1/code/upstreamproxy/ca-cert` 拉代理 CA（5 秒超时，防 Bun fetch 无默认超时挂死启动），与系统 bundle 拼接写到 `~/.ccr/ca-bundle.crt`（src/upstreamproxy/upstreamproxy.ts:254-277）。随后 `getUpstreamProxyEnv()` 给所有子进程注入一组环境变量：`HTTPS_PROXY` 指向 `http://127.0.0.1:<port>`，`SSL_CERT_FILE`/`NODE_EXTRA_CA_CERTS`/`REQUESTS_CA_BUNDLE`/`CURL_CA_BUNDLE` 四个变量覆盖 Node、Python requests、curl 各自的 CA 查找路径（src/upstreamproxy/upstreamproxy.ts:185-198）。只设 HTTPS 不设 HTTP 的原因：relay 只处理 CONNECT，纯 HTTP 没有凭据可注入，走代理只会吃到 405（src/upstreamproxy/upstreamproxy.ts:186-188）。

这个函数还处理了一个进程树问题：子 CLI 进程无法重新初始化 relay（令牌文件已被父进程 unlink），但父进程的 relay 还在监听。因此当模块状态为 disabled 但环境变量里已继承 `HTTPS_PROXY` + `SSL_CERT_FILE` 时，把这八个代理相关变量原样透传给下游子进程，让整条进程树都走父进程的 relay（src/upstreamproxy/upstreamproxy.ts:160-184）。该函数由 `subprocessEnv()` 调用，Bash/MCP/LSP/hooks 子进程拿到同一份配置（src/upstreamproxy/upstreamproxy.ts:155-159）。

`NO_PROXY_LIST` 覆盖 loopback、RFC1918、IMDS 网段，以及 Anthropic API、GitHub 和各语言包注册表。Anthropic 域名给了三种写法（`anthropic.com`/`.anthropic.com`/`*.anthropic.com`），因为不同运行时对 NO_PROXY 的解析不同：Bun/curl/Go 用 glob，Python urllib/httpx 用后缀匹配（src/upstreamproxy/upstreamproxy.ts:37-63）。Anthropic API 必须绕开 MITM 的另一个原因写在注释里：伪造 CA 会破坏非 Bun 运行时：Python httpx/certifi 不信任它（src/upstreamproxy/upstreamproxy.ts:45-50）。包注册表直连则是容器既有行为，代理只接管需要注入组织凭据的那部分流量。

## relay.ts：localhost CONNECT → WebSocket 隧道

`relay.ts` 在 127.0.0.1 上起一个 TCP 服务，接受 curl/gh/kubectl 发来的 HTTP CONNECT，把字节流通过 WebSocket 隧道转发到 CCR 服务端；服务端终结隧道、MITM TLS、注入组织配置的凭据（如 DD-API-KEY），再转发到真实上游（src/upstreamproxy/relay.ts:2-9）。为什么用 WebSocket 而不是裸 CONNECT：CCR 入口是 GKE L7 负载均衡，只有路径前缀路由，没有 connect_matcher（src/upstreamproxy/relay.ts:11-13）。

隧道帧是手工编码的 protobuf：`UpstreamProxyChunk { bytes data = 1; }` 单字段消息，tag 0x0a + varint 长度 + 字节，十行代码避免在热路径引入 protobufjs（src/upstreamproxy/relay.ts:57-81）。

鉴权分两层。WebSocket upgrade 请求带 `Authorization: Bearer <token>`，因为 upgrade 本身由网关按 PRIVATE_API 鉴权；隧道内第一个 chunk 携带 CONNECT 行加 `Proxy-Authorization: Basic base64(sessionId:token)`，供服务端认证隧道并得知目标 host:port（src/upstreamproxy/relay.ts:160-165, 378-384）。

连接状态机分两阶段。Phase 1 累积到 `\r\n\r\n` 为止解析 CONNECT 头，超过 8192 字节没见到结束符就回 400；非 CONNECT 方法回 405（src/upstreamproxy/relay.ts:306-324）。Phase 2 在 WS 未 OPEN 前把字节塞进 `pending` 缓冲：TCP 可能把 CONNECT 头和 TLS ClientHello 合并成一个包，`onopen` 时再统一 flush（src/upstreamproxy/relay.ts:325-341, 385-392）。每 30 秒发一个空 chunk 做应用层 keepalive，对齐 sidecar 50 秒空闲超时（src/upstreamproxy/relay.ts:53-54, 395）。出站按 512KB 分块，对齐 Envoy 每请求缓冲上限（src/upstreamproxy/relay.ts:49-51, 436-442）。

错误处理里有一个细节：`established` 标志记录服务端 "200 Connection Established" 是否已转发。隧道已进入 TLS 阶段后再写明文 502 会污染客户端 TLS 流，所以 WS 出错时只有未 established 才回 502，否则直接断连（src/upstreamproxy/relay.ts:121-123, 410-420）。Bun 与 Node 双实现：Bun 的 `sock.write()` 部分写入会静默丢尾，需要显式尾队列加 drain 回调；Node 的 `net.Socket` 无条件缓冲，不需要这个处理（src/upstreamproxy/relay.ts:130-134, 176-241）。

## fail open 的取舍

两套机制在"失败时怎么办"上立场一致但手段不同。

本地沙箱：初始化失败只记 debug 日志，命令退回非沙箱执行（src/utils/sandbox/sandbox-adapter.ts:786-787）。想改成硬门需要显式配置 `failIfUnavailable`：启动时沙箱不可用就直接报错退出，该选项的 schema 注释说明它面向"要求沙箱作为硬性门槛"的托管部署（src/entrypoints/sandboxTypes.ts:95-103）。作为补偿，`getSandboxUnavailableReason()` 保证显式开启了沙箱却跑不起来时用户一定能看到原因（src/utils/sandbox/sandbox-adapter.ts:562-592）。

容器代理：六个启动步骤任何一步失败都只是 warn + 禁用代理，绝不让坏掉的代理配置毁掉一个本来能工作的会话（src/upstreamproxy/upstreamproxy.ts:16-17, 145-150）。

两处取舍的逻辑相同：隔离层是增强控制，不是业务功能本身；它自己的故障不应成为可用性故障源。代价是安全姿态静默降级，所以两边都配了观测手段：本地侧是启动警告与 `/sandbox` 面板的依赖检查，容器侧是 debug 日志链路与"代理禁用"状态。降级发生时用户能从这些渠道看到原因，而不是毫无察觉。

## 本篇涉及的源码文件

- `src/utils/sandbox/sandbox-adapter.ts`：桥接 @anthropic-ai/sandbox-runtime，完成 settings→SandboxRuntimeConfig 转换、逃逸防护 denyWrite 清单、启用判定与生命周期管理
- `src/tools/BashTool/shouldUseSandbox.ts`：每条 Bash 命令的沙箱裁决与 excludedCommands 匹配
- `src/entrypoints/sandboxTypes.ts`：SDK 与 settings 校验共用的沙箱配置 zod schema
- `src/upstreamproxy/upstreamproxy.ts`：CCR 容器侧代理初始化：令牌读取、PR_SET_DUMPABLE 反调试、MITM CA 安装、代理环境变量注入
- `src/upstreamproxy/relay.ts`：localhost CONNECT→WebSocket 隧道中继与凭据注入
- `src/components/sandbox/SandboxSettings.tsx`：/sandbox 交互面板的三模式切换
- `src/components/sandbox/SandboxDependenciesTab.tsx`：沙箱依赖（seatbelt/rg/bwrap/socat/seccomp）状态展示
- `src/components/sandbox/SandboxOverridesTab.tsx`：unsandboxed fallback 开关的 Overrides 标签页
- `src/components/SandboxViolationExpandedView.tsx`：沙箱违规事件的订阅与展示
- `src/utils/sandbox/sandbox-ui-utils.ts`：剥除 stderr 中 sandbox_violations 标签的工具函数
- `src/commands/sandbox-toggle/index.ts`：/sandbox 命令定义与动态状态描述
- `src/commands/sandbox-toggle/sandbox-toggle.tsx`：/sandbox 命令入口与 exclude 子命令处理
