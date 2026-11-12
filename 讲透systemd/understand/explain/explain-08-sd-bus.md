# explain-08 · src/libsystemd/sd-bus/sd-bus.c — sd-bus：D-Bus 连接状态机与消息泵

## 一、角色定位

sd-bus.c（4511 行）是 libsystemd 公共 API `sd_bus_*` 的主体实现——systemd 自研的 D-Bus 客户端/服务端双用库，也是整个 systemd 生态的进程间通信地基（PID 1 管服务、loginctl 管会话、timedatectl 调 hostnamed，全走它；对外还替代 libdbus 成为推荐实现）。这个文件管"连接的生命周期与消息泵"，不管序列化（sd-bus-message.c）与对象注册（bus-objects.c）：地址解析与连接建立（含 system/user/ssh 远程/machine 容器/exec 五种 transport）、SASL 认证、Hello 握手、八态状态机、读写双队列、超时 prioq、以及把这一切嫁接到 sd-event 事件循环。它同时是稳定 API 承诺（sd-bus.h 带 stability pledge）的载体——函数签名只增不改。

## 二、内部结构

连接建立是重入的"地址游标"模式：地址串可能列出多个端点（`unix:path=/run/dbus/system_bus_socket;tcp:...`），`bus_parse_next_address()`（sd-bus.c:1067）逐段解析（unix:740 / tcp:833 / unixexec:903 / 容器内:995），`bus_start_address()`（1141）按当前游标尝试连接，失败则 `bus_next_address()`（1189）轮转到下一个并重试——多地址故障转移内建于连接层。状态机八态（`bus_set_state` 的表，sd-bus.c:539-548）：UNSET → WATCH_BIND（等 socket 出现，dbus-daemon 未起时 inotify 监视）/OPENING（connect 进行中）→ AUTHENTICATING（SASL EXTERNAL）→ HELLO（等 Hello() 应答拿 unique name）→ RUNNING → CLOSING/CLOSED。每态都有对应的 process 分支（bus_process_internal 的 switch，sd-bus.c:3310-3350）。读写各一条队列（wqueue/rqueue，dispatch_wqueue:2082 / dispatch_rqueue:2146），方法调用的超时挂在 prioq 上（timeout_compare:2303），应答回调按 cookie 配对（process_reply:2785，cookie 由 `next_cookie` 1952 递增）。

## 三、外部连接

对上是所有 daemon 与 CLI：sd_bus_call（sd-bus.c:2417，同步阻塞）与 sd_bus_call_async（2315，回调式）；bus-objects.c 的 vtable 服务端注册、bus-match.c 的信号订阅（bus_add_match_full:3586）都把回调插进本文件的消息分派链。对下是 bus-socket.c（真实 fd 读写与 SASL）、bus-message.c（wire 格式 marshalling，`bus_remarshal_message` 2014 处理 gdbus/libdbus 兼容差异）、bus-internal.h（sd_bus 结构体与 BusState）。事件循环集成：sd_bus_attach_event（3874）把 io/时间/defer 三种源挂进 sd-event，`sd_bus_process`（3353）+`sd_bus_wait`（3426）则是裸轮询模式的双件套（bus_process_internal 头注释 3288-3291 规定了"0=没事做该去 wait"的协议）。默认连接单例经 thread-local 缓存（bus_default:3976）。

## 四、数据流

一次典型调用（异步）：应用构 message → sd_bus_call_async 盖 cookie/超时入 prioq → seal（bus_seal_message:1981）→ 进 wqueue → 事件循环可写时 dispatch_wqueue 逐条写出 → 对端应答到达 → dispatch_rqueue 读出 → `process_running`（3067）按固定序排空内部工作：process_timeout（超时先决，3074）→ wqueue → track 队列（3082，名主跟踪回调）→ 读消息 → `process_message`（3011）。后者是七级瀑布，顺序即语义（3026-3050）：hello → reply（method 应答配对）→ fd_check（peer 凭证过滤）→ filter（sd_bus_add_filter 全局回调）→ match（信号匹配）→ builtin（本地应答 Introspect/AddMatch 等）→ **object（用户的 vtable 方法）**——每级返回非 0 即截断，object 永远最后，框架级处理永远优先于应用代码。连接失败/断开统一走 `bus_enter_closing`（1828），发 SyntheticDisconnected 通知（synthesize_connected_signal:494 是对应的 Connected 合成信号——把连接事件也建模成信号，回调模型归一）。Hello 握手成功才拿 unique name 并切 RUNNING（hello_callback:561-596，581 行校验名字必须 ':' 开头）。

## 五、设计决策

1. **状态机驱动而非回调地狱**：所有 I/O 都"推进状态机一步"（bus_process_internal 按态分派），同一个 sd_bus_process 在任何状态调用都安全——调用方无需知道连接进展到哪。
2. **多地址故障转移内建**（1141/1189）：连接串本身就是故障转移列表，配合 WATCH_BIND 态（dbus-daemon 后启动也能自动连上）实现"连接永远自愈"。
3. **七级分派瀑布**（3026-3050）：框架语义（配对应答、过滤、匹配、内置方法）与应用回调严格分层，应用代码不可能截走框架消息。
4. **合成信号归一事件模型**（494）：Connected/Disconnected 本不是 D-Bus 消息，却合成给上层，让"连接生命周期"与"消息生命周期"共用一套回调 API。
5. **同步调用复用异步原语**：sd_bus_call（2417）内部就是循环 process/wait 等特定 cookie 的应答，没有第二套阻塞代码路径。

## 六、新人提示

调 D-Bus 问题先开 `SD_BUS_DEBUG=1`：bus_set_state 的每次迁移（556-557）与每条消息（3024 log_debug_bus_message）都会打出来，状态卡在哪一态（认证？Hello？）一眼可见。写服务端时记住 vtable 回调在瀑布最底（3050），框架消息到不了你手里；filter 若返回非 0 会吞掉信号，慎用。watch_bind 态是"dbus-daemon 未起"的正常表现而非错误。读这份文件建议两条线并进：连接线（1067→1141→3310 的 switch）与消息线（2082→3011→3067）；公共 API 的语义全在头文件 sd-bus.h 的注释里，本文件只实现不重复文档。Kylin 工作区提示：麒麟桌面/服务大量 IPC 走 dbus-broker 或 dbus-daemon，sd-bus 的 remarshal 路径（2014）处理过 libdbus 老对端的 marshalling 差异，自研服务接入时若遇 "marshalling error" 先怀疑消息签名不匹配而非传输层。
