# browser_use/browser/watchdog_base.py + watchdogs/default_action_watchdog.py — 看门狗体系

## ① 角色定位

browser-use 的运行时是事件驱动的：浏览器操作被建模成事件经 bubus EventBus 派发，watchdog 是挂在总线上的 handler 集合。BaseWatchdog（watchdog_base.py:15）只定义协议："按方法名自动注册 handler"——子类里任何 `on_EventTypeName(self, event)` 方法都会在 attach 时被绑到对应事件。实现层在 `browser/watchdogs/` 目录，共 14 个子类：DefaultActionWatchdog（default_action_watchdog.py:42，3758 行、全仓最大类）、DownloadsWatchdog、DOMWatchdog、SecurityWatchdog、LocalBrowserWatchdog、StorageStateWatchdog、ScreenshotWatchdog、PopupsWatchdog、PermissionsWatchdog、RecordingWatchdog、HarRecordingWatchdog、CaptchaWatchdog、AboutBlankWatchdog、CrashWatchdog。要破除的误解："watchdog"这名字严重低估了它——DefaultActionWatchdog 实际是**默认动作执行引擎**，click/type/scroll/下拉框/键盘/上传全由它的 handler 落地，是类库中离真实浏览器最近的一层。

## ② 内部结构

**BaseWatchdog（321 行）**分四块。pydantic 模型约束（watchdog_base.py:24-29）：extra='forbid' 强制一切状态必须是显式 Field 或 PrivateAttr，validate_assignment=False 防赋值重校验抹掉私有属性。LISTENS_TO/EMITS 两个 ClassVar（watchdog_base.py:33-34）静态声明事件面，attach 时双向断言：handler 声明不在 LISTENS_TO 里的事件 assert 失败（watchdog_base.py:272），反向缺失只 warning（284-291）。`attach_to_session`（watchdog_base.py:243）扫描 browser/events.py 全部 BaseEvent 子类，按 `on_Xxx` 前缀匹配自动注册。最重的是 `attach_handler_to_session` 里的 `make_unique_handler` 包装器（watchdog_base.py:93-207）：每个 handler 执行前都过**断路器**——CDP WebSocket 已断且不是 8 个生命周期事件（watchdog_base.py:78-89）就直接跳过；正在重连则等 `_reconnect_event`（上限 RECONNECT_WAIT_TIMEOUT），仍断就抛 ConnectionError（watchdog_base.py:98-123）。handler 抛错时它会 `get_or_create_cdp_session` 自愈崩掉的 CDP session（watchdog_base.py:177-202），自愈失败且是 ConnectionClosed 类才放行 re-raise。另有防重复注册 RuntimeError（216-221）与 `__del__` 清理 `*_task(s)` 的后手（293-321）。

**DefaultActionWatchdog（3758 行）**结构是"12 个 on_ 入口 + 约 25 个 _impl 实现"：on_ClickElementEvent（default_action_watchdog.py:338）、on_ClickCoordinateEvent（390）、on_TypeTextEvent（452）、on_ScrollEvent（514）、on_GoBackEvent（2373）、on_RefreshEvent（2431）、on_WaitEvent（2450）、on_SendKeysEvent（2478）、on_UploadFileEvent（2692）、on_ScrollToTextEvent（2730）、下拉框双入口（2824/3300）。点击链路最能体现纵深：入口先做防御（session 存活检查、file input/select 拦截返回 validation_error），识别打印按钮则改走 CDP printToPDF（`_handle_print_button_click`，239），其余进入 `_execute_click_with_download_detection`（45）——点击同时向 DownloadsWatchdog 注册三个直接回调，0.5 秒没下载开始就当普通点击返回，开始了最长等 30 秒并区分"仍在推进/疑似停滞"两种超时（166-209）。`_click_element_node_impl`（703）是多级回退漏斗：scrollIntoViewIfNeeded → 拿 rect 转四边形取可见面积最大者 → 遮挡检查（`_check_element_occlusion`，574，elementFromPoint + label/input 关联三情形）→ 遮挡或无几何退 JS `this.click()` → 否则鼠标三段 dispatchMouseEvent。

## ③ 外部连接

装配点在 BrowserSession.attach_all_watchdogs（session.py:1706）：逐个 import、`model_rebuild()`、构造、attach；StorageStateWatchdog 按需启用（给了 storage_state 或 user_data_dir 才挂，间隔放宽到 60 秒，session.py:1737-1749）；CrashWatchdog 整段被注释禁用（session.py:1726-1732）。BrowserSession 自己也借 BaseWatchdog.attach_handler_to_session 注册九个 handler（session.py:711-718）——协议复用而非继承。watchdog 间协作有明文宪法（watchdog_base.py:40-42 注释）：**跨 watchdog 共享的状态与辅助方法必须放在 BrowserSession 上**；要暴露就发事件。`_downloads_watchdog.register_download_callbacks`（108）与 `_dom_watchdog.clear_cache`（523-525）是两条官方例外。底层命令经 cdp_use 走 CDP；上层 Tools/Controller 与 MCP server 只 dispatch 事件，从不直调。

## ④ 数据流

一次"点击第 33 号元素"的旅程：Agent 决策 → Controller 发 ClickElementEvent(node=EnhancedDOMTreeNode) → event_bus.dispatch → 断路器查 CDP 存活 → on_ClickElementEvent：is_file_input？打印按钮？→ `_execute_click_with_download_detection(_click_element_node_impl(node))` → cdp_client_for_node 路由到元素所在 frame → 滚动/坐标/遮挡三关 → Input.dispatchMouseEvent 三连 → 若触发下载，回调把 path/size 合进 click_metadata['download'] → 返回值沿总线回流。输入文本链路多一个分叉：`_input_text_element_node_impl`（1759）先判断 `_requires_direct_value_assignment`（1620）——date/time/color/range 及 datepicker 类 text 输入框走 `_set_value_directly`（1672）：React 兼容的 nativeInputValueSetter 绕过受控组件（1696-1702），按 focus→input→change→blur 补发事件，jQuery 存在再 trigger('change')；普通输入框 focus（`_focus_element_simple`，1563，DOM.focus 失败退点击）后逐字符派发；元素级失败还有"点一下再页打字"的回退（491-507）。

## ⑤ 设计决策与取舍

一是**命名约定即注册**：零装饰器零配置表，方法名就是布线，代价是改名即断线、LISTENS_TO 断言是唯一保险。二是**validation_error dict 不 raise**：点击 select/file-input 这类"模型选错了元素"返回 `{'validation_error': msg}`（default_action_watchdog.py:720/724），让 agent 下一步自我纠正，环境级错误才 raise BrowserError。三是**断路器+自愈包在 handler 外面**：注册时统一包装 CDP 断连处理，重连期间挂起等待而非丢事件。四是**下载检测用回调而非事件**：点击与下载时序紧耦合，DownloadsWatchdog 直连回调（注册/用毕注销，216-223）比再过总线低延迟。五是 get_dropdown_options 三类型探测（native select / ARIA menu-listbox / Semantic UI 类，2888-2963）加 combobox 专门通道（3094），承认"下拉框"根本不是一种东西。

## ⑥ 新人提示（坑/勘误）

- **任务书素材勘误**："watchdog 群 12 类"实数是 **14 个子类**（watchdogs/ 目录 14 个文件各一类，加 BaseWatchdog 本体），CrashWatchdog 有源码但被注释禁用（session.py:1726-1732）。
- **default_action_watchdog.py 在 browser/watchdogs/ 子目录**；33-39 行的 model_rebuild 为解 EnhancedDOMTreeNode 前向引用。
- **"看门狗"会误导搜索**：找"点击怎么实现的"别去 controller/tools，答案在这个文件；找"页面崩溃恢复"则发现 crash_watchdog 根本没挂载。
- **on_TypeTextEvent 的 index=0 有特殊语义**：backend_node_id 为 0/None 表示"对当前焦点元素打字"（460-471），不是 bug 是特性。
- **handler 重名注册当场 RuntimeError**（watchdog_base.py:216）：通常是 attach_to_session 被调了两次，查 _watchdogs_attached 守卫（session.py:587）。
- **组合键解析对 `++` 有特判**（2518-2527）：'ctrl++' 按"ctrl 加号"理解，朴素 split('+') 会拆坏。
- **敏感文本日志脱敏有两处**：watchdog 的 is_sensitive 分支（464-470）与 MCP server 侧启发式，两层独立。
