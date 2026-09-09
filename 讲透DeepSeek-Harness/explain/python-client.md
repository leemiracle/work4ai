# python/sdk client.py — HarnessClient：Python 侧的传输核心

> 原文件：[`python/sdk/src/deepseek_harness/client.py`](../../../explore/deepseek-ai/deepseek-harness/python/sdk/src/deepseek_harness/client.py)（589 行）

## 角色定位

`HarnessClient` 是 Python SDK 的传输核心：它在子进程里启动一个本地 dsh 运行时（默认 `--profile sdk`），然后在两者之间用**换行分隔的 JSON-RPC over stdio** 驱动一切——请求写 stdin，响应与通知从 stdout 读回。文件自带 reader 与 stderr 双守护线程、按 id 路由的请求等待器、通知订阅队列，以及子代理会话树过滤。

它是 TypeScript 侧远程协议（Typert/JSON-RPC）在 Python 世界的对等入口：session-controller 那一侧暴露的远程面，最终就是被这个类（或其上层门面）消费的。仓库规则"两个 SDK 都投影循环"意味着：agent-loop、会话生命周期、`SessionEventMap` 的任何变化，都会同时波及这里的事件模型——Python 侧不是二等公民。

## 内部结构

**配置**：`HarnessConfig` 数据类声明全部部署事实——`dsh_bin`（dsh 可执行路径）、`profile`（默认 `'sdk'`）、`patches`、`dsh_home`、`cwd`、`env`、以及三段独立超时：`initialize_timeout_seconds` / `request_timeout_seconds` / `shutdown_timeout_seconds`。三段超时各管生命周期一段，互不挤占。

**进程与线程模型**：`Popen` 启动子进程；reader 守护线程持续从 stdout 逐行读 JSON-RPC 消息，按 id 分发到对应等待队列，无 id 的进通知队列；stderr 守护线程单独排水防止子进程 stderr 缓冲区写满造成卡死。

**并发结构**：双锁分工——`_lock` 串行化公开方法调用（生命周期与状态转换），`_write_lock` 只串行化 stdin 写入（长的读处理不阻塞别的写）。`_responses` 是 `dict[request_id → queue]`：每个在途请求一个专属队列，支持多请求并发在途，完成或失败后队列清理。

**错误面**（`errors.py`）：`JsonRpcError`（服务器返回的结构化错误）与 `TransportClosedError`（传输已关——进程退出/管道断开后再发请求得到的显式异常，而非挂死）。

**消息模型**（`models.py`）：`IncomingRequest`（服务器→客户端请求）、`InitializeResponse`、`Notification` 等数据类，把线格式钉在类型上。

**会话树过滤**：客户端层面可按子代理会话树过滤事件——只想跟随某个子代理的事件流时不必在应用层自己筛。

子代理过滤值得多说一句：远程面的事件流里混着父会话与各级子代理的事件，客户端侧的树过滤让你以"某个会话及其后代"为窗口订阅——在 Python 侧跟踪一次委派的全过程因此不必拉全量流。`HarnessConfig` 的 `env` 与 `cwd` 让同一个 `dsh_bin` 能以不同环境形态反复拉起，配合 `patches` 甚至能给运行时叠不同的插件层，测试与多环境部署共用一个类。

## 外部连接

包内：import `errors.py` 与 `models.py`；被 `__init__.py` 与 `api.py` 消费——`api.py` 的 `DeepSeekHarness` 是懒启动、可复用的高层门面（`run` / `start_session`；`Session` 驱动单轮对话并收集事件流，附 `normalize_input`、`final_response`、`finish_reason` 等后处理工具）。对端：dsh 运行时的 sdk profile——也就是 TypeScript 侧 gateway/session-controller 暴露的同一套 JSON-RPC 面。图谱确认：`api.py` 反向依赖本文件，`__init__.py` 汇出两者。

## 数据流

启动：构造 → `Popen` 拉起 `dsh --profile sdk`（附 patches/env/cwd）→ 双守护线程就位 → initialize 握手（超时受 `initialize_timeout_seconds` 约束）→ 运行时就绪。调用：公开方法 → 分配请求 id →（持 `_lock` 检查状态）→ 持 `_write_lock` 把 JSON-RPC 行写 stdin → 释放写锁 → 调用方在自己的 `_responses[id]` 队列上等待 → reader 线程读到该 id 的响应/错误 → 入队 → 调用方取回，队列删除。通知与服务器请求：reader 发现无 id 消息 → 进 `_notifications` 队列 → 订阅方按需消费；`IncomingRequest`（服务器主动发起）同样有应答通道。关闭：shutdown（带专属超时）→ 子进程收尾 → 传输标记关闭，后续调用得到 `TransportClosedError`。

## 设计决策

**同步优先**：SDK 的默认用户面是同步的——简单、易调试、与脚本场景匹配；并发能力不靠 async 事件循环，而靠"每请求一个等待队列"的朴素结构支撑，多线程调用天然安全（双锁划定边界）。

**per-request 队列而非单等待点**：多请求并发在途时互不干扰，慢响应不阻塞快响应的返回路径。

**stderr 独立排水线程**：最容易被忽略的一类死锁（子进程 stderr 写满阻塞→整个进程停摆）用一个专职线程消灭在萌芽。

**传输关闭显式化**：`TransportClosedError` 把"对端没了"变成可捕获的异常类型——调用方能区分"请求失败"与"再也不会有响应"。

**三段超时**：初始化（冷启动可能慢）、常规请求、关闭（排空可能慢）各有节奏，一个全局超时必然顾此失彼。

**配置即数据类**：全部部署事实集中在 `HarnessConfig`，显式传入而非环境变量散落——与 TS 侧"misconfiguration fails loud"的立场同构。

## 新人提示

生命周期三拍子：initialize → 使用 → shutdown，忘了第三拍会留下孤儿 dsh 进程（`ps` 里搜 `--profile sdk` 能找到它们）。不要跨进程共享一个 client——它绑着真实的子进程与线程，序列化不了。写高层封装前先看 `api.py`：懒启动、复用、事件流后处理这些常见需求那里都有现成答案。调试协议问题的最快路径是把 reader 线程收到的原始消息打出来对着 JSON-RPC 面看；stderr 线程的输出则直接反映 dsh 侧的启动失败。遇到 `TransportClosedError` 先查子进程退出原因（dsh_home 下的日志或 stderr 缓冲），而不是重试——对端已死，重试只是制造新的异常。最后，升级 SDK 时记住"两边 SDK 同 PR 投影"的仓库规则：这里的事件模型与 TS 侧快照是同步演进的，单边升级必然出现事件对不上。日常使用还有一个细节：请求超时只结束等待，不杀子进程——运行时仍在跑，后续通知仍会进队列；要把"放弃等待"变成"放弃运行时"，得显式走 shutdown。
