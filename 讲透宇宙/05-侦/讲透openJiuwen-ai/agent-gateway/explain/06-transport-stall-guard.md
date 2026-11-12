# 06 · transport_stall_guard.py：1888 个 CLOSE-WAIT 的生产事故全解

> 锚定 commit `7af202253`。行号指 `agent_gateway/channel_manager/web/transport_stall_guard.py`，另注者除外。

## 一、角色定位

这是全仓最小的"英雄文件"之一——134 行，却完整处置了一次真实生产事故：**WebChannel 端口上堆积 1888 个 CLOSE-WAIT 连接**（issue #4946，docstring `transport_stall_guard.py:11` 原文记载）。它的角色是 asyncio transport 层的**写停滞看门狗**：客户端触发服务端响应后停止读取，写缓冲被填满，而 TCP 会一直带着零窗口（zero window）ACK——socket 永远不报错，`transport.close()` 永远等不到缓冲排空。文件名即使命：Abort server transports whose peer stopped reading（transport_stall_guard.py:2）。

它以 Mixin 形式存在（`TransportStallGuardMixin`，transport_stall_guard.py:36），被两个工厂函数（transport_stall_guard.py:110-133）动态混入 uvicorn 的 HTTP/WebSocket 协议类，在 `web_connect.py:734-735` 注入 uvicorn.Config——所以它保护的是**进程内所有 uvicorn 承载的连接**（WebChannel 的 HTTP+WS 同端口），不只 WebSocket。与 03/04 篇的 per-ws writer 512 帧队列（`routing/base_ws_channel.py:29`，注释同样引用 issue #4946）构成双层防线：writer 队列挡 Gateway 自己往坏连接堆帧，stall guard 挡 uvicorn transport 层的缓冲滞留。

## 二、内部结构

**事故解剖（docstring transport_stall_guard.py:4-22，本文件的知识密度高峰）**分三层递进：

1. **uvicorn 层**：HTTP 协议实现里没有任何东西会中止这类连接——socket 以 CLOSE-WAIT 状态活过整个进程生命周期，占着一个 fd 加**每一字节缓冲**（1888 个实测就在 WebChannel 端口上），且停滞的 transport 还会**钉死 uvicorn 的优雅关闭**（graceful shutdown 等它排空，transport_stall_guard.py:12-13）。
2. **websockets 层**：其实现只在收到 FIN 后约 30 秒才 abort；更要命的是 keepalive 在写停滞时**根本无法触发**——`await self.ping()` 阻塞在同一条未排空的缓冲上（transport_stall_guard.py:13-15）。ping/pong 保活机制的前提是"写路径可用"，写路径本身堵死时保活形同虚设。
3. **解法层**：`pause_writing` 在写缓冲越过高水位线时触发、`resume_writing` 在排空到低水位线以下时触发（asyncio 流控的标准回调，transport_stall_guard.py:17-18）——把"持续 paused 超过 60 秒"作为停滞判据；对端 EOF 后再挂一条独立的关闭截止线，覆盖"从未越过高水位"或"恢复后仍残留少量未排字节"的缓冲（transport_stall_guard.py:19-21）；`connection_lost` 在 socket 真正关闭后解除两条截止线（transport_stall_guard.py:21-22）。

**Mixin 的四个覆写**（transport_stall_guard.py:48-72）就是上述设计的直译：

- `pause_writing`（transport_stall_guard.py:48-53）：先 `super()` 保持原语义，再在无既有定时器时 `loop.call_later(60.0, self._abort_stalled_transport)` 布防——幂等，重复 pause（水位上下震荡）不叠加定时器。
- `resume_writing`（transport_stall_guard.py:55-57）：**先取消定时器再 super()**——排空即解除武装。
- `eof_received`（transport_stall_guard.py:59-67）：super() 返回 false/None 时 asyncio 会关闭 transport，但注释点破：`close()` 即便在流控上限之下也仍会等待 pending writes（transport_stall_guard.py:61-62）——所以对端 EOF 也要挂 60s 截止线。
- `connection_lost`（transport_stall_guard.py:69-72）：两个 handle 全部取消后交还 super()，这是唯一合法的"解除布防"出口。

**执行器 `_abort_transport`**（transport_stall_guard.py:90-103）：先取消两个定时器（防 abort 后再触发）、取 `self.transport`（可能已 None，transport_stall_guard.py:93-95）、拼对端标识（uvicorn 协议的 `self.client` 回退 `remote_address`，transport_stall_guard.py:96）、打 warning 日志（含原因 + 60s + peer 三要素）、最后 `transport.abort()`（transport_stall_guard.py:103）。abort 与 close 的区别正是本文件存在的理由：abort 立即丢弃缓冲与连接（RST），close 优雅排空——后者在零窗口对端面前等于永不返回。

**工厂与记忆化**（transport_stall_guard.py:106-133）：`guarded_http_protocol()` 混入 `uvicorn.protocols.http.auto.AutoHTTPProtocol`，`guarded_websockets_protocol()` 混入 `uvicorn.protocols.websockets.websockets_impl.WebSocketProtocol`，各自模块级 `_guarded_*_class` 缓存——多次调用返回同一个类，避免重复造类导致 isinstance 分裂。

## 三、外部连接

- **接线点 `web_connect.py:710-755`**：`_start_uvicorn_server` 的 `uvicorn.Config` 一次配齐五件套——`ws_max_size=WEB_WS_MAX_MESSAGE_BYTES`（150 MiB，`common/ws_limits.py:11`，注释解释 100 MiB 文档 base64 后约 133 MiB）、`ws_ping_interval=20.0`、`ws_ping_timeout=60.0`（web_connect.py:728-730）、`http=guarded_http_protocol()`、`ws=guarded_websockets_protocol()`（web_connect.py:734-735）。web_connect.py:731-733 的中文注释把因果链复述一遍："停止读取的客户端会让 transport 写缓冲滞留，close() 永远等不到排空，socket 永久卡在 CLOSE-WAIT（issue #4946）；带看门狗的协议类在写停滞超时后直接 abort，释放 fd 与缓冲。"
- **同文件的 `EmbeddedUvicornServer`**（web_connect.py:738-745）：覆写 `capture_signals` 为空 contextmanager——Gateway 进程自持信号并统筹所有组件的关闭序，内嵌 uvicorn 若重抛捕获的 SIGINT 会打断这套清理、留下未观测的 KeyboardInterrupt。stall guard 与它是同一条关闭正确性线上的两颗钉子。
- **上游防线 `routing/base_ws_channel.py`**：`_SEND_QUEUE_MAX_FRAMES = 512`（base_ws_channel.py:29，注释"停滞 transport 由写停滞看门狗回收，issue #4946"）+ writer 单帧 10s 超时只丢帧不杀 writer（base_ws_channel.py:305-315）。三层递进：writer 队列（Gateway 应用层）→ 512 帧硬顶丢弃（队列层）→ stall guard 60s abort（transport 层）。
- **兄弟链路限额**：`AGENT_WS_MAX_MESSAGE_BYTES = 8 MiB`（ws_limits.py:6）与 `AGENT_WS_SEND_BUDGET_BYTES = 6 MiB`（ws_limits.py:8）——Gateway↔AgentServer 内部链路禁止大 base64（channel_manager.py:206-210 注释：PayloadTooBig 会击穿整条连接），与浏览器侧 150 MiB 的宽限形成鲜明对照。
- **`ws_connection_adapter.py`**（Starlette WebSocket → websockets 风格适配，ws_connection_adapter.py:17-20）让 WebChannel 处理器无感地跑在 uvicorn 原生 WS 上——stall guard 保护的正是在这层适配之下默默滞留的 transport。

## 四、数据流

**事故时间线（无 guard 时）**：客户端发大请求 → 服务端开始流式响应 → 客户端停止 read（标签页挂起/网络半死）→ uvicorn 协议层不断 `transport.write` → 缓冲越过高水位、TCP 通告零窗口 → 对端持续零窗口 ACK（TCP 层无错）→ websockets keepalive `await ping()` 挂在同一缓冲 → 60s ping_timeout 也无法触发 → 客户端 FIN 后 30s 才有 abort，但缓冲未越线的连接连这条路都走不到 → `close()` 永等 → CLOSE-WAIT 堆积 → fd 与内存泄漏 + 优雅关闭被钉死 → 进程只能硬杀。

**guard 后的同一条线**：`pause_writing` 首次触发即布防 60s 定时器 → 若客户端恢复读取，`resume_writing` 到来、定时器取消、连接继续（误杀窗口 = 60s 内不能完成一次越过高低水位的排空，正常慢客户端足够安全）→ 若 60s 仍 paused，`_abort_stalled_transport`（transport_stall_guard.py:79-80）→ `transport.abort()` 强制 RST → `connection_lost` 清理状态 → fd 与缓冲立即释放。EOF 分支独立计时：对端已 FIN 但缓冲残留的，60s 后 `_abort_after_eof`（transport_stall_guard.py:87-88）同样 abort。

**与 writer 队列的协同**：guard abort transport → ws 对象 closed → BaseWsChannel 的 `_enqueue_send` 看见 `closed` 静默丢弃（base_ws_channel.py:256-257）、writer 的 ws.send 快速失败退出（base_ws_channel.py:316-327）→ `unregister_ws` 走 `_drain_and_cleanup_writer` 清队列（base_ws_channel.py:337-368）。应用层不用感知 transport 被谁杀的——对它来说就是一次普通断连。

## 五、设计决策与权衡

1. **Mixin + 工厂而非 fork uvicorn**：三个 super() 调用点（transport_stall_guard.py:49/57/60/72）保证原协议语义完整保留，guard 只是"叠加观察者"；缺点是依赖 uvicorn 内部类路径（`uvicorn.protocols.websockets.websockets_impl.WebSocketProtocol`）——升级 uvicorn 改动这些类时 mixin 静默失效（不会报错），需要版本升级时盯 `_guarded_*_class` 的导入点。
2. **60 秒的取值**：`ws_ping_timeout=60.0`（web_connect.py:730）与 `_STALL_ABORT_SECONDS = 60.0` 对齐——停滞判据不短于正常 ping 超时，避免"慢但健康"的连接被误杀；同时远小于 CLOSE-WAIT 的无限滞留，泄漏窗口有上界。
3. **双截止线（写停滞 + EOF 后不关闭）**：单独任一条都不完备——零窗口连接可能从未 EOF（还挂在半开状态），EOF 连接可能缓冲从未越线。两条线在 `connection_lost` 处统一解除，`_abort_transport` 再互防一次（transport_stall_guard.py:91-92），状态机无悬挂分支。
4. **abort 优于无限等待，但只在 60s 后**：abort 丢弃未送达字节对客户端是数据丢失，因此阈值给了正常排空充分机会；相比之下 512 帧队列丢弃（04 篇）发生在更早的队列层、代价更小——越靠近 transport，动作越重、阈值越长，层间梯度设计合理。
5. **进程信号自持**（EmbeddedUvicornServer）：内嵌服务器放弃信号捕获权，让 app_gateway 的统一关闭序（01 篇 finally 块）不被打断——组件化部署里"谁拥有信号"必须唯一。

## 六、新人提示与坑

- **读这文件先读 docstring（transport_stall_guard.py:2-23）**：22 行把 TCP 零窗口、websockets keepalive 失效机理、uvicorn 缺口、两层截止线全部讲透，是全仓最好的"事故复盘即文档"范本；排查类似 CLOSE-WAIT/写堆积问题先按这个因果链逐层验证。
- **别在 guard 布防期间调 `transport.close()` 代替 abort**：close 等排空正是事故根因；处理停滞 transport 的合法出口只有 `abort()`。
- **日志锚**：`[stall-guard] ... aborting transport peer=`（transport_stall_guard.py:97-102）出现即说明 guard 在干活；若生产再现 CLOSE-WAIT 而无此日志，优先怀疑 mixin 未生效（uvicorn 版本变动 / Config 未走 `guarded_*` 工厂——比如有人在别处新建 uvicorn server 忘了注入）。
- **`pause_writing`/`resume_writing` 是 asyncio Protocol 层回调**，不是 websockets 层概念——调试时要区分应用层 `ws.send`（BaseWsChannel writer）、协议层 `transport.write`（uvicorn）与内核缓冲（TCP 窗口）三层，日志里三层混看是排查此类问题的最大误区。
- **新增独立 uvicorn/HTTP 监听必须带上 guard**：`ws_connection_adapter.py` 的注释（ws_connection_adapter.py:13）提醒"Future HTTP routes on the same uvicorn app do not go through this adapter"——同 app 的新路由受 guard 保护，但**另起的 server**（如 mcp_oauth_http、diagnosis_http 若自建监听）需要各自确认协议类来源。
- **150 MiB 的 `WEB_WS_MAX_MESSAGE_BYTES` 是浏览器侧特例**：不要"顺手统一"到内部链路的 8 MiB——document.persist 的 base64 大文档依赖这个宽限；反过来内部链路也绝不能放宽（击穿连接的教训见 channel_manager.py:206-210）。
