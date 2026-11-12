# 12 · SDK 门面与消费端——client 五类句柄、ComputerUseAgent、MCP host 与外围工具

## 一、角色定位

这一篇覆盖引擎之外的全部"用法层"，回答两个问题：**应用代码怎么用**（S15）与**Agent/模型怎么用**（S16）。

- `computer_use_engine/client/`（computer.py 270 行 / factory.py 34 行 / host.py 44 行）：**Python SDK 门面**。docstring（computer.py:4）"Human intent: a desktop, an application instance, a window, or a control."——`Computer/App/Window/Element` 四个公开类 + `UI` 基类把人类词汇翻译成 03 篇的 9 种 InterfaceRequest。
- `computer_use_agent/`（agent.py 91 / toolkit.py 136 / cli/main.py 218）：**DeepAgent 消费端**。`ComputerUseAgent` 组装 openJiuwen DeepAgent + ComputerUseToolkit + 上下文压缩轨；CLI 单任务/交互双入口共用同一 agent（main.py:4 docstring）。
- `interface_adapter/mcp/`（server.py 244 / session.py 431）：**MCP 宿主**。父进程 server 注册 `computer_use/computer_use_reset` 两工具；`ExecutionSession` 监督 Python worker 子进程（单飞行、45 秒看门狗、reset 三段屏障）。
- `scripts/native.py`（426 行）：**三平台驱动构建与权限入口**（`build_mac_os/build_linux/build_windows` + `permissions`）。

值得先钉死的结构事实：**Agent 不直接 import 引擎**——`ComputerUseToolkit` 经 `McpConnection` 走 MCP stdio 协议到 `interface_adapter/mcp/server.py`（toolkit.py:58），工具执行发生在 MCP 宿主的 worker 进程里。SDK 直连（进程内）与 MCP（进程外）是两条平行的接入路。

## 二、内部结构

**client/computer.py——五类句柄**
- `Computer`（L55-128）：构造仅 `session_controller()` + `WeakValueDictionary` 应用缓存（L59）。`app(selector)`（L61-84）接受整型引用（经 `interfaces.application` 解析）或字符串 selector，按 key 缓存 App 句柄；桌面级操作 `read/click/scroll/drag/type_text/press_key` 全部走 `controller.act(method, dict(desktopRef=...))`（L97-99 等）——**桌面输入必须携带最新 desktopRef**，坐标先过 `desktop.check_coordinates`（L96）。
- `UI`（L131-181）：`_internal=False` 即 `TypeError("Use Computer.app() or App.window(); UI is not directly constructible")`（L133-134）——防绕过构造；`controller.register(self, scope)` 挂进 bindings；`element(target, timeout_ms)`（L140-148，timeout 钳 0-10000）→ `ResolveElement`；read/click/scroll/drag/type_text/paste/press_key → `ObserveUI/UIPointer/UIKeyboard`。
- `App`（L184-195）：`InstanceState` + `_anchor/_image`；`window(ref)` 委托 `controller.interfaces.window`（03 篇）。`Window`（L198-203）：持 `_app/_instance/_anchor`，`_window_identity` 取 `state.selection.root`。
- `Element`（L206-264）：同样 `_internal` 保护；`read/read_text`（length 钳 1-16384，L225-228）；`type_text(text, replace=)`（L238-243，replace 用 `type(...) is not bool` 精确校验后映射 `insert/replace` 两意图）；`perform_action`（L259-264，错误提示"copy a Secondary Actions name from this element"）。
- `factory.py`：`controller_adapters()`（L14-26）打包八件回调（create_app/create_window/observation_state/action_result/captured_text/register_image/image_delivery_epoch/image_delivery_required）注入 SessionController；`native_computer(port)`（L33-34）一站式返回可用 Computer。
- `host.py`：`computer_host()`（L25-44）返回 `Record(computer, close)`，close 关 transport 并 `wait_closed`；模块导出七类 handler 设置器（L12-22，action/observation/diagnostic/handle/text_page/preview/execution_guard）——宿主据此汇集全部事件流。

**computer_use_agent——DeepAgent 消费端**
- `ComputerUseAgent(DeepAgent)`（agent.py:20）：构造（L27-73）组装 `ComputerUseToolkit` + `ContextProcessorRail`（DialogueCompressor 用模型自身配置，L44-55）+ options 字典（workspace 默认 `~/.computer-use/agent/workspace` L61、`prompt_mode="minimal"`、`parallel_tool_calls=False` L69——**工具调用强制串行**）；`apply_deep_agent_parts(self, resolve_deep_agent_parts(model, **options))`（L73）；`compact`（L75-77）直达 context_engine。
- `ComputerUseToolkit`（toolkit.py:52-136）：`DesktopTool`（L24-49）把 MCP 工具适配成 openJiuwen `Tool`（ToolCard `idempotent=False`、`additionalProperties=False`）；`tools` 两件——`computer_use`（title+code 两参数，title 是给用户看的调用标题）与 `computer_use_reset`（L61-73）；`call`（L86-103）三事件观测：`tool_call` 先发、`CancelledError→tool_cancelled` 且 **`effect: "possible"`**（L90-92）、异常→`tool_error` 同样 possible——三值语义穿透到 agent 观测层；成功结果同时保留渲染文本与 `mcp_result` 原始负载（L99-102）；`close`（L108-125）四步：`cancel_current`→`timeout(10)` 内 reset→关连接→从 Runner 资源管理器摘除工具，`asyncio.shield` 保证幂等（L109-111）。
- `cli/main.py`：parser（L24-35）`task` 为 `nargs="?"`——**单任务与交互共用同一 agent**；`--desktop` 直通 MCP 进程环境变量。

**interface_adapter/mcp——宿主与监督**
- `server.py`：`DESCRIPTION`（L26-46）是写给模型的行为契约——"Actions emit dispatched/verified receipts only, without automatically reading trees or screenshots"（动作只发回执不自动读）、"One call at a time; 45 s without native command progress; command starts/completions renew the watchdog, printing does not"（L40-42）。`capabilities()`（L63-73）声明四个 experimental 能力（host/preview v2/demo-foreground/history）；`call_tool`（L129-197）：reset 在无会话时也成功返回（L134-148）；`title` 先 `trim`（L155-156）；会话惰性创建 `ExecutionSession(45000, preview?, demo_foreground?)`（L171-176）；progress_token 存在时把 worker 进度转发成 MCP progress 通知（L177-195）。`cli`（L232-240）`--desktop` 覆盖 `COMPUTER_USE_DESKTOP`。
- `session.py` 的 `ExecutionSession`（L33-）：**45 秒看门狗**——`stalled()`（L113-114）触发 `reset("Execution exceeded 45000 ms without native command progress.")`；`progress()`（L116-126）在 native 命令开始/完成时续命并转发 on_progress，**print 不续命**；**reset 三段屏障**（L322-365）：`_resetting` 幂等去重→`_generation+1`+kill 子进程+关 writer+清 pending→`retire()` 协程先 `shield(starting)`（等启动任务落地）、再处理 **late kill**（L347-354，注释："Process creation yields in Python. A reset during that yield must retire the newly created worker before admitting any later call."——进程创建让出事件循环的窗口期诞生的 worker 也必须被退休）、最后等待 earlier/exited 两代退出。

**scripts/native.py**：`build_mac_os`（L34-67，swift build + 手工组装 `.app` bundle，Info.plist 带 `LSUIElement` 无 Dock 应用）/`build_linux`（L77）/`build_windows`（L150）/`build_native`（L139 平台分派）；`permissions`（L278-）与 `read_permissions`（L243-）是三平台权限检查/请求入口；`linux_session_launcher`（L329-）给登录会话 D-Bus 环境做启动包装。

## 三、外部连接

- **SDK 直连路**：应用代码 → `client/` 五类 → `SessionController.run`（03 篇）→ interaction 管线。`computer_host` 是 CLI/测试的标准宿主。
- **Agent 路**：`ComputerUseAgent` → `DesktopTool.invoke` → `ComputerUseToolkit.call` → `McpConnection`（stdio）→ `interface_adapter/mcp/server.py` → `ExecutionSession`（Python worker 子进程，内嵌 SDK 直连路）→ 引擎。**两条路在 SessionController 会合**。
- **事件汇聚**：`host.py` 七个 set_*_handler 与 toolkit 的 `on_event`、MCP 的 notifications/computer-use/preview（server.py:165-169）构成三层观测面；`toolkit.emit` 的三事件是 agent 侧行为日志。
- **外围**：`scripts/native.py` 产出三平台驱动二进制，被 `paths.py:native_driver()` 定位（04 篇 `_connect` 消费）；README 所说"build the native driver on the MCP host"的动作即 `python -m scripts.native build`。

## 四、数据流

一次 Agent 点击：模型发 `computer_use(code="await app.element(7).click()")` → MCP `call_tool` 校验（title trim、code 非空）→ `ExecutionSession.execute`（45s 看门狗起表）→ worker 子进程执行 Python：SDK `Element.click` → `ActOnElement` → 03 篇适配 → 11 篇 WritePipeline → native → 回执；worker 的 stdout 汇成工具结果（`render_payload_text`+`mcp_result`）→ `DesktopTool` 返回 `ToolOutput(success=not result.isError)`；期间每有 native 命令开始/完成，`progress()` 续命并发 MCP progress。若 45s 无进展：`stalled→reset`——kill worker、清变量与观察、retire 屏障完成后下一次调用全新开始。

## 五、设计决策与权衡

1. **_internal 构造闸**：UI/Element 只能经 `Computer.app()/UI.element()` 诞生——句柄的身份（scope/instance/anchor）必须由会话状态机赋予，裸构造会绕过 bindings 注册（computer.py:133-134、208-209）。`computer_for_controller` 用 `object.__new__`（L267-270）是宿主侧的唯一后门。
2. **桌面级与 UI 级两套入参协议**：桌面输入带 `desktopRef`（截图代际校验，03 篇 controller.act L181-186 的 stale 检查）；UI 输入走 typed 请求记录。同一个 click 动词在两层有不同安全前提。
3. **工具描述即系统提示词的延伸**：MCP DESCRIPTION 把"不自动读、不自动重放、print 不续命"写进工具契约——模型的第一手行为规范来自工具 schema 而非隐藏 prompt，版本化随 SDK。
4. **看门狗按 native 进度续命而非总时长**：45s 是"无命令进展"的上限，长任务只要持续有 native 命令就合法；这把超时语义从 wall-clock 转成 liveness，与引擎侧两级超时（04 篇）互补。
5. **reset 的竞态完备性**：三段屏障+late kill 显式处理"进程创建 yield 窗口"——reset 期间恰有新 worker 诞生也会被退休，`_generation` 保证老代回调不污染新会话；这与驱动层 generation（04 篇）是同一思想在监督层的复刻。
6. **Agent 走 MCP 而非进程内 import**：工具执行隔离在 worker 子进程（超时/崩溃可 reset），模型代码（任意 Python）与宿主进程解耦；代价是每次调用的序列化开销——对 GUI 操作频率可忽略。
7. **`parallel_tool_calls=False`**（agent.py:69）：GUI 是单资源，并发工具调用只会制造竞态——在 agent 装配期就关死。

## 六、新人提示与坑

- **两条接入路别混**：SDK 直连（`from computer_use import Computer`）与 MCP 路（`computer_use_agent`）不共享句柄/观察状态；toolkit 的 close reset 的是 MCP worker，不影响进程内 SDK 会话。
- **`Element.type_text(replace=True)` 的边界**：replace 是"整控件替换"（intent=replace），容器元素会被 03 篇 `act_element` 拒绝（"full replacement requires a concrete input control"）——这不是 bug 而是防误清空。
- **`DesktopTool.render_for_llm` 只取 `data["content"]`**（toolkit.py:48-49）：`mcp_result` 原始负载仅供程序消费（日志/评估），不进模型上下文——上下文成本控制的一部分。
- **45s 看门狗的"进度"定义**：只有 native 命令开始/完成续命（server DESCRIPTION L40-42 钉死），**纯 Python 计算/打印不续命**——worker 里跑 >45s 的纯计算必被 reset，把重活拆成多次调用或在 native 侧做。
- **reset 是幂等的但不是瞬时的**：`_resetting` 去重后返回同一 task；retire 屏障要等两代子进程退出，连续 reset 调用都汇到同一个屏障上——别按同步语义测它的耗时。
- **`app()` 的 WeakValueDictionary**（computer.py:59）：App 句柄不持引用就被回收，同 selector 再取是新实例（`_instance` 状态不跨回收保留）——长任务请自己持有句柄变量。
- **`scripts/native.py` 是 macOS 优先**：`build_mac_os` 之外的平台构建函数存在但 `build_native`（L139）按 `sys.platform` 分派；权限检查入口 `permissions` 三平台行为不同（Linux 无 AX 时 X11 仍可用，05 篇）——CI 里跑权限检查别假设统一输出。
