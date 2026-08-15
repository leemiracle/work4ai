# 02 · SDK、ACP 与 Python 运行时

> 对应 `packages/sdk/`、`packages/acp/`、`python/`
> 行号钉版 `47f943859b`

## 1. TS SDK：进程外驱动的最小协议

stdio 上的换行分隔 JSON-RPC 2.0（`packages/sdk/protocol`）：

- 方法：`initialize`、`session/prompt`（→ 回执 `{messageId}`）、`shutdown`。
- 通知：`session.event`（会话事件流镜像）、`session.status`、`subagent.started/finished`。
- Server 插件（`packages/sdk/server/src/server.ts:53` `HarnessSdkJsonRpcServer`）：订阅 `session/event` 转发；**stdout 即协议——禁止任何 stdout 日志**；shutdown 先 flush 持久化再 dispose 根再 exit 0。
- Client（`packages/sdk/client`）：`DeepSeekHarness`（owned-run：spawn 子进程、`run()` 拥有"回执→idle"区间、返回 `RunResult{finalResponse, events, notifications}`）与 `HarnessClient`（低层；关闭梯 EOF→SIGTERM→SIGKILL）。

## 2. ACP：编辑器集成的 automation-only 通道

`packages/acp/acp`：Agent Client Protocol（Zed 等编辑器用的开放协议）服务器，JSON-RPC stdio。`initialize` / `session/new`（仅新鲜会话）/ `session/prompt`（纯文本、每会话一个 in-flight、等 idle、流式转发已提交的 `agent_message_chunk`）/ `session/cancel` / `session/request_permission`（一次性 allow/reject）。明确不做：回放、编辑器能力协商——**它自己也是 dsh 的 subagent-acp provider 的对端**。

## 3. Subagent providers：七种出身

`ctx.subagents`（注册表，多命名 provider 并存，`packages/subagent/subagent/src/index.ts:171`）：

| Provider | 出身 | 备注 |
|---|---|---|
| spawn-in-process | 全新进程内子 Agent | 空对话、继承父模型/工作区 |
| fork-in-process | 父会话已完成 turns 前缀 | 用 `sessions.fork` 种子 |
| in-process-driver | 共享驱动（非注册项） | 前两者的引擎 |
| acp | ACP 子进程 | 每次运行全新进程、零能力声明 |
| codex | `codex app-server --stdio` | 固定子进程、单临时线程、无人值守审批自动拒绝 |
| claude-code | 官方 Agent SDK `query()` | 经 `ctx.subprocess` 解析原生 CLI |
| dsh-sdk | **全量对等 harness 子进程** | stdio JSON-RPC 驱动；stop-reason 从子 `turn/end` 映射 |

Consumer：`tool-subagent`（一个插件实例绑一个 provider → 一个工具名，`backgroundMode: one-shot|continuable`）、`tool-subagent-control`（`send_message`/`interrupt_agent`/`list_agents`）、`tool-subagent-report`（子作用域 `report` 工具——子 agent 只能经它向父汇报）。

## 4. Python SDK 与单文件运行时

两个 wheel（`python/README.md`）：

- `deepseek-harness-sdk`（`deepseek_harness`）：镜像 TS 客户端——`DeepSeekHarness()` 高层 turns API + `HarnessClient` 低层。默认 launch 打包运行时并经 `DSH_CORDIS_CONFIG` 注入默认组合。
- `deepseek-harness-runtime-bin`：运行时载体 = **单文件 Node 可执行** `dsh-jsonrpc-agent-pkg-<platform>-<arch>`（linux/macos × x64/arm64；macOS 附 node-pty spawn-helper）。构建脚本 `scripts/build-exe-for-python-sdk.ts` 从 `python/sdk-runtime/package.json` 声明的依赖闭包打包——**目标机无需装 Node**。默认组合：JSON-RPC server + agent core + DeepSeek 适配器 + JSONL 持久化 + checkpoint 策略 + 本地 bash。

## 5. 设计要点提炼

1. **同一运行时四种宿主**——CLI、Web、SDK 子进程、Python 单文件可执行，全部是"组合不同 bundle 的同一插件树"。
2. **stdout 即协议**的纪律——把"日志与协议抢管道"这类事故从设计上消灭。
3. **subagent 是接缝不是功能**——七种出身（含竞争对手的产品）插在同一个工具名后面。
4. **Python 生态经"可执行文件"桥接**——不做 Python 重写，把整个 Node 运行时打包成一个 binary 分发。

## 6. 验证命令

```bash
$ rg -n "export class HarnessSdkJsonRpcServer" packages/sdk/server/src/server.ts
53:export class HarnessSdkJsonRpcServer {
$ ls python/     # README.md  sdk/  sdk-runtime/
$ rg -n "resolve_bundled_launch_args" python/sdk-runtime/src -l   # 运行时解析 API
```

→ 下一篇：[05-lessons](../05-lessons/01-设计决策与可借鉴.md)
