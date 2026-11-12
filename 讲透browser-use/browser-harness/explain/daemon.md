# daemon.py 精讲 — 常驻 CDP 中继：连接、恢复与关停的全部状态机

> 源码：`src/browser_harness/daemon.py`（894 行）｜图谱层 L02「守护进程本体与云认证」

## ① 角色定位

daemon 是唯一的**长寿命进程**：持有到 Chrome（或云端浏览器）的 CDP WebSocket 连接、维护"当前 session/target"状态、缓存最近 500 条 CDP 事件（`BUF`，daemon.py:37），并通过 `_ipc.serve` 把这些能力以单行 JSON 协议暴露给短命客户端。一行 `python -m browser_harness.daemon` 即可拉起（admin.py:579-588 正是这么孵化的）。

它的存在理由写在两处矛盾里：客户端进程只有 90 秒预算且随时蒸发（不能持有 WS 连接），而 Chrome 144+ 的本地授权弹窗又要求**那条引发弹窗的连接一直活着等用户点 Allow**（daemon.py:118-122）——所以必须有一个既比客户端长命、又能无限等待的东西。

`BROWSER_KIND` 在启动时三态定型：有 `BU_BROWSER_ID` 为 cloud，有 `BU_CDP_WS/BU_CDP_URL` 为 cdp，否则 local（daemon.py:117），后续大量分支（握手超时、专用标签页、关停清理）都由它驱动。

## ② 内部结构

- **导入期副作用**（daemon.py:13-31）：与 helpers 相同的 `_load_env` 在 import 时执行；随后 daemon.py:33-36 冻结 NAME/SOCK/LOG/PID 四个路径常量。
- **浏览器画像层**（daemon.py:38-216）：三平台 Chrome 系 profile 目录清单（Chrome/Canary/Edge 各通道/Brave/Comet/Arc/Dia，daemon.py:38-74）；`remote_debugging_user_enabled` 读各 profile `Local State` 的 chrome://inspect 开关（daemon.py:155-171）；`browser_running_for_profile` 用 `SingletonLock` 符号链接尾部的 PID 判进程存活（daemon.py:187-203）；Windows 无 SingletonLock，退化为 tasklist 进程名匹配，查不到就**假设在运行**以保守留在恢复路径（daemon.py:206-216）。
- **WS 端点发现 `get_ws_url`**（daemon.py:264-342）：优先级 `BU_CDP_WS` > `BU_CDP_URL`（HTTP 端点经 `/json/version` 升级，404 时用 `_ws_from_devtools_active_port` 按端口反查，daemon.py:243-261）> 扫描各 profile 的 `DevToolsActivePort` 文件。三级都失败再探测 9222/9223（daemon.py:331-339）。每个 HTTP 探测都把 403 翻译成"权限弹窗未批准"的明确报错（daemon.py:280, 311, 337）。
- **`_PatientCDPClient`**（daemon.py:410-421）：继承 cdp_use 的 CDPClient，唯一改动是把本地握手的 `open_timeout` 换成 `LOCAL_HANDSHAKE_TIMEOUT = None`（daemon.py:123）——授权弹窗没有期限，设期限会导致连接断开、下次重试又开一个新连接又一个新弹窗。
- **`Daemon` 类**（daemon.py:424-808）：见下文数据流。
- **serve/main/入口**（daemon.py:811-894）。

## ③ 外部连接

- **上游 `_ipc`**：serve 起监听、expected_token 鉴权、cleanup_endpoint 收尾（daemon.py:829, 669, 863）。
- **auth.py**：cloud 模式下 `stop_remote` 取 API key 调 `PATCH /browsers/{id}` 停掉计费浏览器，3 次退避重试（daemon.py:345-372）。
- **paths.py**：`inspect_marker()` 标记"恢复流程开过 chrome://inspect 标签页"（daemon.py:394-400）。
- **下游消费者**：helpers 的每个 `cdp()`/meta 请求、admin 的 `daemon_alive`（用真实 CDP 调用探测而非纯 ping，admin.py:525-536 注释：僵尸 daemon 能答 meta 却连不上 Chrome）、run.py 的 `daemon_browser_kind` 遥测。
- **`_enable_default_domains` 同时服务两个入口**：首次 attach 与 `set_session`（switch_tab/new_tab 之后）——注释点明漏掉它 `wait_for_network_idle` 会在换标签页后静默失聪（daemon.py:541-553）。

## ④ 数据流

**启动**（main → Daemon.start，daemon.py:635-663）：get_ws_url → 建 client（local 用 Patient 版）→ `attach_first_page` → 猴补丁事件注册表：包一层 `tap` 把每条 CDP 事件灌进 `self.events` deque、同步维护 dialog 状态、在 load 事件后异步补马标记（daemon.py:659-663, 626-633）。

**attach 策略**（daemon.py:442-523）：命名 daemon（BU_NAME≠default 且非 cloud）在 `_dedicated_target_lock` 内**创建专属标签页**，避免并行 daemon 抢同一个 tab 互相覆盖导航（daemon.py:452-472）；默认 daemon 则按"真实页面 > 可复用空白页 > 新标签页 > chrome://inspect 页接管"级联（daemon.py:484-506），接管后顺手关掉恢复流程留下的 inspect 标签页（daemon.py:513-520）。

**请求处理 `handle`**（daemon.py:665-808）：meta 家族（ping/drain_events/session/current_tab/connection_status/set_session/pending_dialog/shutdown）逐一分派；其余按 CDP 方法转发，但 `Target.*` 一律剥 session 当浏览器级调用（daemon.py:767）。`set_session` 是性能敏感点：旧 session 的 Network.disable 与新 session 的四个 enable **并行 gather**，把最坏 ~22s 压回 5s IPC 预算内（daemon.py:709-734 注释）。

**陈旧 session 恢复**（daemon.py:770-808）："Session with given id not found" 时，显式带 session 的调用方直接收错误（不暗中改道），默认 session 才进恢复：注册 recovery task → 锁内重 attach → 查 `_session_replacements` 替换链（跨多次恢复仍落回原标签页，daemon.py:565-576）→ 用替换 session 重试一次。显式调用方要求"精确 session"的语义优先于"自动救活"。

**关停**（serve finally + handle 的 shutdown，daemon.py:740-761, 836-863）：shutdown 先立 `_shutting_down` 屏障、取消并限时 2s 排干在途恢复（daemon.py:596-611），再 strict 停 cloud——**cloud 停失败会把 `_shutting_down` 翻回 False 让 daemon 存活**，保住"稍后可重试计费清理"的权威（daemon.py:753-759）；serve 的 finally 复刻同一屏障后才按"恢复同款锁序"关专属标签页，保证清理与创建永不竞态（daemon.py:843-862）；最后 finally 里 `stop_remote()` + 删 PID 文件（daemon.py:891-894）。

## ⑤ 设计决策与取舍

- **PID 文件语义是"指纹"不是"号码"**：`_publish_own_pid` 永不截断父进程在持锁期发布的记录——另一个冷启动调用者若看到空 PID 文件会误判并孵出兄弟 daemon（daemon.py:77-99）。杀进程前 admin 用 `identify` 的端到端验证（活 IPC + 自报 PID）取代盲信 pid 文件（PID 复用防护）。
- **弹窗无限等待 vs 一切调用可超时**：本地握手无期限（弹窗语义）与 IPC 响应 5s 硬期限（客户端预算）并存——前者靠 daemon 长命兜底，后者靠"报错指导 agent 下一步"兜底。
- **事件缓冲定长 deque(500)**：旧事件被挤掉是接受的行为；`drain_events` 取走即清（daemon.py:678-680），消费节奏由客户端自负。
- **日志安全**：连接信息只记 host:port 拓扑，CDP 凭证与云商会话路径一律 `<redacted-cdp-endpoint>`（daemon.py:223-233）。
- **恢复的边界保守主义**：替换链有却当前 session 变了（用户主动换了标签页）就不重试——宁可让调用方收到错误，也不把请求打到用户没同意的页面上（daemon.py:796-799 注释）。

## ⑥ 新人提示（坑/勘误）

- `LOCAL_HANDSHAKE_TIMEOUT = None` 是**有意为之**（daemon.py:118-122 注释），别"修复"成数值——那会制造弹窗断连-重试-再弹窗风暴。
- Chrome 147+ 在默认 user-data-dir 上禁用了 `/json/*` HTTP 发现：404 时用 DevToolsActivePort 第二行的 ws path 直接拼 URL（daemon.py:312-315）；且**不要信任文件里的 ws path 去连**——若 Chrome 曾以别的 user-data-dir 在同端口启动，留下的浏览器 UUID 已过期，WS upgrade 会 404，正确做法是经 `/json/version` 重新解析（daemon.py:303-306 注释）。
- 命名 daemon ≠ 隔离浏览器：多个 BU_NAME 共享同一浏览器实例，隔离只在"专属标签页"粒度（daemon.py:452-472）。
- `_record_event` 里 load 事件触发的是 `_schedule_tab_marker`（fire-and-forget task + 2s 超时），同步 IPC 路径绝不等它（daemon.py:613-633）。
- 排查 daemon 问题先看 `ipc.log_path` 的日志文件；入口处每次启动会清空重写（daemon.py:882）。
- daemon 进程死掉不会自动清理 socket 文件——POSIX 端 serve 启动时的 unlink（_ipc.py:170）与 `cleanup_endpoint` 兜底；但"端口复用假活"只能靠 ping 语义排除，裸 connect 判活是错的。
