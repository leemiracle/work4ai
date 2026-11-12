# mac/context.py —— 一个"设计完整却无法导入"的会话上下文化石

## 一、角色定位

`mlx_use/mac/context.py` 设计上是"应用会话上下文"：用 async-with 生命周期（`MacAppContext`）把"锁定一个目标 App → 挂 AXObserver 增量监听 → 随时取 UI 状态 → 按 index 执行动作"封装成声明式对象，配套 `MacAppConfig`（目标与重试参数）与 `MacAppSession`（pid+树构建器+observer 的运行时三元组）。这是上游 `mac_use` 项目里更早一代的架构设想——**带事件驱动的增量感知**。

但它是全仓库最重要的反面教材：**这个模块从未被任何代码导入**（grep 全仓 `mac.context` 零命中，仅 TYPE_CHECKING 引用不存在的 manager），而且根本 import 不了——第一步就 `ImportError`。真正跑起来的链路（Agent 持有 MacUITreeBuilder + 轮询建树）完全绕开了它。读它的价值在于理解"项目原本想去哪"以及"为什么最终形态选择了无状态轮询"。

## 二、内部结构

**`MacAppConfig`（context.py:34-42）**：dataclass，`bundle_id` 必填，`highlight_elements`/`ui_poll_interval`/`max_retries`/`retry_delay` 四个调优项——除 bundle_id 外全部无消费者。

**`MacAppSession`（context.py:45-52）**：`pid` + `tree_builder` + `observer`（pyobjc 对象）。

**`MacAppContext`（context.py:54-186）**七个方法：
- `__aenter__/__aexit__`（context.py:62-67）：async-with 协议，进出调 initialize/close。
- `initialize`（context.py:69-77）：解析 pid，组装 Session，`_setup_observer` 挂监听。
- `_setup_observer`（context.py:79-96）：`AXObserverCreate` 建观察者（context.py:85），注册 `kAXUIElementDestroyedNotification` 与焦点变化通知（context.py:91-92），把 observer 的 run loop source 加进当前 CFRunLoop（context.py:95）。回调里 `asyncio.create_task(self._handle_ui_change())`（context.py:83）。
- `_get_app_pid`（context.py:98-113）：`NSWorkspace.runningApplications()` + `NSPredicate` 按 bundle id 过滤（context.py:100-105）；没找到就 `launchApplication_` 并睡 2 秒（context.py:107-111）。
- `get_state`（真身 context.py:121-132）：`build_tree(pid)` 后组装 `MacUIState(ui_tree/interactive_elements/active_pid/frontmost_app)`。
- 动作三分支 `perform_action`（context.py:139-150）：按 `type` 字符串分发 `click`/`type`/`focus_window`，各自的 index 寻址走 `tree_builder._element_cache`（context.py:157,165）。
- `focus_window`（context.py:168-178）：取 `kAXWindowsAttribute` 列表，对目标窗口 `AXUIElementPerformAction(windows[i], kAXRaiseAction)`（context.py:174-177）——本文件唯一一段干净可用的 pyobjc 逻辑。

## 三、外部连接

- **`mlx_use.mac.views`（context.py:26）**：导入 `MacAppInfo, MacUIState`——但 views.py 里只有 `TabInfo` 与 `BrowserState` 两个 browser-use 残留类，而 views.py 自己又在导入不存在的 `mlx_use.dom.*` 模块。三重断裂。
- **`MacManager`（context.py:28-29）**：TYPE_CHECKING 前向引用，`mac/manager.py` 不存在——mac 目录只有 actions/context/element/tree/views 五个文件。构造器 `manager` 参数（context.py:55）因此永远无法合法实例化。
- **tree/actions**：正确引用 `MacUITreeBuilder`、`click`、`type_into`（context.py:24-25），但 context.py:158 的 `click(element)` 单参调用与 actions.py 的双参签名不匹配。

## 四、数据流

设想中的数据流：`bundle_id → NSWorkspace 查/启动 → pid → AXObserver 事件 → _handle_ui_change → get_state → MacUIState`；动作流：`{'type':'click','index':n} → _element_cache[n] → actions.click → bool`。现实中的数据流：**不存在**。真实链路里 Agent（agent/service.py:205）直接调 `MacUITreeBuilder.build_tree(pid)` 每步全量重建，pid 来自 `ActionResult.current_app_pid` 的接力。这个模块设想的"会话内增量状态"被简化成了"每步推倒重来"。

## 五、设计决策与取舍

- **事件驱动 vs 轮询**：observer 方案（AXNotification 触发更新）理论上是正解——省 CPU、低延迟、能捕捉动画中间态。被放弃的根因可以从代码质量反推：pyobjc 的 observer 需要 CFRunLoop 与 asyncio 事件循环共存（callback 里 `asyncio.create_task` 在 CF 回调线程没有 event loop，context.py:83 会 RuntimeError），需要手动管理 notification 生命周期，需要处理 pid 失效。轮询方案（agent/service.py:194 的 sleep(1) + build_tree）粗糙但每一步都可调试。**作者用可运行性换了架构优雅**。
- **index 寻址复用 tree 的缓存**（context.py:157/165）：与 Controller 真实实现（controller/service.py:54/83）完全同构——说明这套寻址约定是从该原型固化为正式架构的。

## 六、新人提示（坑与勘误）

1. **模块不可导入，三重 ImportError 串联**：① context.py:26 要的 `MacAppInfo/MacUIState` 在 mac/views.py 中不存在（那里只有 TabInfo/BrowserState）；② mac/views.py 自己 `from mlx_use.dom... import` 的 dom 目录整个不存在；③ `MacManager` 模块不存在。三者修好之前，这文件是纯文本化石。
2. **六处死引用（AST 验证）**：`AXObserverAddNotification`（context.py:91-92）、`kAXFocusedUIElementChangedNotification`（context.py:92）、`AXObserverGetRunLoopSource`（context.py:95,118）、`kCFRunLoopDefaultMode`（context.py:95,118）、`NSWorkspace`（context.py:100,136）、`NSPredicate`（context.py:103）——全部**使用但从未导入**。import 链修通后，`initialize` 一进 `_setup_observer` 就是 NameError。补法：`from AppKit import NSWorkspace, NSPredicate`、`from ApplicationServices import AXObserverAddNotification, AXObserverGetRunLoopSource, kAXFocusedUIElementChangedNotification`、`from CoreFoundation import kCFRunLoopDefaultMode`。
3. **`get_state` 空覆盖（context.py:185-186）**：文件末尾有第二个 `async def get_state(self): pass`，Python 类体顺序执行，**后者覆盖前者**——真的实现（context.py:121-132）成为死代码，任何 `get_state()` 调用返回 None。连带 `_handle_ui_change`（context.py:180-183）等价于空操作。这是"改完没删旧壳/复制粘贴收尾"的典型事故，静态看 L121 的实现会觉得功能完备，运行时完全是另一回事。
4. **`click(element)` 签名失配（context.py:158）**：actions.py:43 的 `click(element, action)` 需要两个参数，这里只传一个——TypeError。
5. **可变默认参数 + 硬编码**（context.py:55）：`config: MacAppConfig = MacAppConfig(bundle_id='com.apple.Notes')`——默认值是共享的 dataclass 实例，且把"备忘录"写死成默认目标。
6. **launch 后 pid 竞态**（context.py:107-113）：`launchApplication_` 返回 True 后直接 `return app.processIdentifier() if app else None`，但 `app` 还是过滤时拿到的旧引用（未运行时它常是 None）——刚启动的 App pid 要重新查 runningApplications 才有。
7. **谁在读它**：没有任何运行时代码导入此模块；它的存在唯一作用是考古——证明 index 寻址、pid 接力、`_element_cache` 约定在上游 mac_use 原型里已经成型。新人想加"AX 事件驱动感知"功能时，先读这份残骸能少走一遍老路（尤其是 run loop 共存的坑）。

（行号锚：context.py:24-26,28-29,34-42,45-52,54,55,62-67,69-77,79-96,83,98-113,115-119,121-132,134-137,139-150,152-158,160-166,168-178,180-183,185-186；agent/service.py:194,205；controller/service.py:54,83；actions.py:43）
