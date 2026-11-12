# browser_use/browser/session.py 精讲——BrowserSession 与 13 只 watchdog 的装配现场

## 一、角色定位

`browser_use/browser/session.py`（4197 行）定义 `BrowserSession`——框架与真实浏览器之间的唯一边界。Agent 以为在调"浏览器"，实际调的全是这里的方法：导航（`navigate_to` L2484）、取状态（`get_browser_state_summary` L1613）、取元素（`get_element_by_index` L2544）、截图（`take_screenshot` L4077）。三重身份：**CDP 连接管理器**（经 cdp-use 连本地/远程 Chromium）、**事件总线宿主**（浏览器操作事件化）、**watchdog 装配车间**（`attach_all_watchdogs()` L1706-1855 挂 13 只按需拼装）。

重要勘误：**全仓不存在独立的 `class Browser`**。`Browser` 是 `BrowserSession` 纯别名——类型桩在根包 `__init__.py:52`，运行时走懒加载表 `__init__.py:86`。搜 `class Browser(` 扑空是正常的。

## 二、内部结构

**文件顶部三个支撑类型**：`Target`（L80，浏览器目标 page/iframe/worker，被控制的实体）；`CDPSession`（L95，通往某 target 的通道）；`ResilientEventBus`（L113-138，bubus EventBus 子类，`step()`/`wait_until_idle()` 在总线拆掉后变 no-op 而非 assert——注释引 ENG-5280：warm-Lambda 恢复时 worker 会在 dispatch 前 step 已停的总线）。

**BrowserSession 本体（L141 起）**是 Pydantic BaseModel（`model_config` L163-168：`validate_assignment=True` + `extra='forbid'`）。构造器**三个 `__init__` 重载**（L172 云端 / L208 本地 / L269 真实现）：云模式吃 `cloud_profile_id` 等，本地模式吃 `executable_path`/`headless` 等，公共参数双模式通用——未显式传的由 `BrowserProfile` 承接。**配置与身份分离**："浏览器怎么配"住 profile（`browser/profile.py` L585 起 `BrowserProfile` 继承四个 Playwright 参数家族，L568 起 `ProxySettings`），"这次会话是谁"住 session。

`model_post_init`（L699-705）建 `_connection_lock` 与 `_reconnect_event`，`_register_session_event_handlers`（L707-731）挂 9 个核心事件处理器（Start/Stop/Navigate/SwitchTab/TabCreated/TabClosed/AgentFocusChanged/FileDownloaded/CloseTab），开头**防重复注册断言**（L716-721）：同名 handler 已存在即 RuntimeError。

**start() 是事件驱动的（L734-740）**：只派发 `BrowserStartEvent`，真正逻辑在 `on_BrowserStartEvent`（L802-921）：L814 **先 attach watchdog 再做任何事**（LocalBrowserWatchdog 要接 BrowserLaunchEvent）；无 cdp_url 时三岔路——云端（L819-833 create_browser 拿回 cdpUrl）、本地（L834-843 派发 BrowserLaunchEvent）、皆非报错（L845）；连接包在 `_connection_lock` 防并发（L850），`asyncio.wait_for(connect, 15.0)`（L857）防慢 WebSocket 挂死——超时清理注释（L859-862）值得读：**CancelledError 是 BaseException，绕过 `except Exception` 清理**，必须手动停掉半初始化 client 置 None，否则下次 start 跳过重连；成功后派发 `BrowserConnectedEvent`（L886，恢复 storage_state）。

**stop 与 kill 分野（L750-799）**：`kill()` 强杀进程；`stop()` 只拆总线清缓存、进程留着（为重连）；`close()` 是 stop 别名（L797）。两者最后都重建全新 `ResilientEventBus`。

**watchdog 装配线（L1706-1855）**——本文件高光段，`_watchdogs_attached` 防重复挂载（L1709-1711），13 只装配如下：

| watchdog | 行号 | 职责 |
|---|---|---|
| DownloadsWatchdog | L1737-1744 | 下载追踪、PDF 自动下载 |
| StorageStateWatchdog | L1754-1763 | **条件装配**：仅当 storage_state/user_data_dir 存在，启用保守参数 |
| LocalBrowserWatchdog | L1771-1776 | 本地浏览器进程启停 |
| SecurityWatchdog | L1778-1783 | allowed_domains 限制（导航本体已收回 BrowserSession 做） |
| AboutBlankWatchdog | L1786-1792 | about:blank 页与首屏动画 |
| PopupsWatchdog | L1795-1799 | JS 对话框/alert/beforeunload |
| PermissionsWatchdog | L1802-1805 | 剪贴板/麦克风等权限 |
| DefaultActionWatchdog | L1808-1820 | **动作执行引擎**：click/type/scroll 等执行者 || ScreenshotWatchdog | L1823-1828 | 截图 |
| DOMWatchdog | L1831-1835 | DOM 树构建（依赖前者） |
| RecordingWatchdog | L1838-1840 | 视频录制 |
| HarRecordingWatchdog | L1843-1846 | **条件装配**：配 record_har_path 时 |
| CaptchaWatchdog | L1849-1852 | **条件装配**：captcha_solver 开启时 |

CrashWatchdog 被注释停用（L1729-1734）。每只模式一致：`model_rebuild()` → 构造（event_bus + browser_session 双引用）→ `attach_to_session()` 自注册；成片注释掉的 `event_bus.on(...)` 是订阅收敛后的化石。

## 三、外部连接

- **被 Agent 调**：`run()` 第一步 `await self.browser_session.start()`（agent/service.py L2583）；每步取状态（L1097）、CAPTCHA 等待（L1047）、重连查询（L1272-1273）。
- **被 Tools 调**：每个动作处理器收到同一 session 引用。
- **向下依赖**：cdp-use `CDPClient`（L3463 以下约 30 个 `_cdp_*` 私有方法是薄封装）；`SessionManager` 管 target 树。
- **事件协议**：出站 Launch→Connected→StateRequest→Reconnecting/Reconnected；入站九大业务事件（L723-731）。外部编排器只听事件即可还原全程。

## 四、数据流

一次状态获取（Agent 每步都走）：`get_browser_state_summary(include_screenshot, cached)` →（缓存路径 L1619-1632：缓存存在且 selector_map 非空且不缺截图才直接返回）→ 派发 `BrowserStateRequestEvent`（L1635-1644）→ DOMWatchdog 与 ScreenshotWatchdog 响应 → 汇成 `BrowserStateSummary`。**超时保护讲究**（L1651-1694）：捕获超时不抛异常，而是构造"不可行动"降级状态——空 selector_map、无截图、errors 带"元素索引不安全，用导航/等待等非索引动作恢复"，并清缓存查找路径（L1659-1661）。设计动机在注释里：**宁可让模型看不到元素，也不让它拿旧页面索引点新页面**。

重连是另一条关键流：`_attach_ws_drop_callback`（L2358-2390）给 CDP client 消息处理任务挂 done 回调——任务退出即 WS 掉线，非故意停止就 fire `_auto_reconnect`（L2291-2356）：1s/2s/4s 指数退避、单飞锁（`_reconnecting` + `_reconnect_event`）、单次 15s 超时、成功派 `BrowserReconnectedEvent`。Agent 侧配合：step 遇连接错就等 `_reconnect_event` 收敛。

## 五、设计决策与取舍

1. **事件驱动与直接调用双轨并存**（docstring L144-148 明言 2-layer）：高层走事件（可被 watchdog 拦截/增强/录制），底层保留直接 CDP 调用。代价是两种风格混排。
2. **watchdog 按需装配而非全量常驻**：三只条件装配，省资源也避免副作用（无 user_data_dir 时自动存 cookie 反而污染状态）。
3. **启动失败一条清晰消息**（L742-748）：云端缺 API key 在入口 fail-fast，不让总线把同一错误打五遍。
4. **缓存带有效性自检**（L1619-1632）：校验"selector_map 非空 + 不缺截图"，防让模型看到空页。
5. **Pydantic 模型做运行时主体**：每次属性赋值过校验，热路径有开销；换来 profile 覆盖、序列化、拷贝全链路统一。

## 六、新人提示（坑/勘误）

- **别找 `class Browser`**：不存在，别名在根 `__init__.py:52` 桩 + L86 懒加载表。同理 `Controller` 是 tools.service.Tools 的 3 行 shim，beta/service.py 是 Rust 二进制包装层——先认清别名表再画架构图。
- **`stop()` 不杀浏览器**：进程退出要 `kill()`；只 stop 浏览器还在后台，CI 里越积越多。
- **watchdog 只挂一次**：`_watchdogs_attached` 置位后重复调用跳过（L1709）；kill 后总线重建，靠下次 start 重挂。
- **`_cdp_*` 私有方法别直接调**：L3463 以下薄封装无守卫无重试；公开方法（`get_tabs` L2392）才带"未连接返回空"防御。
- **L2358 的 WS 掉线探测依赖私有属性** `_message_handler_task`：cdp-use 升级改名会静默失效，重连"突然不工作"先查这。
