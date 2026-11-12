# mcp_server.py — 把 harness 助手层一对一搬上 MCP 的 stdio 服务器

## 一、角色定位

`src/mcp_server.py` 是 browser-harness 的 **MCP（Model Context Protocol）门面**：一个跑在 stdio 上的服务器，把 helpers 层的浏览器操作逐个包装成 MCP 工具，让任何 MCP 客户端（Claude Desktop、Codex、其他 agent 宿主）不写一行胶水代码就能驱动这台机器上的真实 Chrome。文件头明确设计意图（mcp_server.py:9-11）："The server starts on stdio and exposes one MCP tool per browser-harness helper. Each tool ensures the daemon is running, calls the existing helper, and returns JSON text."

它是纯粹的**薄包装层**：不含任何浏览器逻辑，导航、点击、JS 求值全部转发给 `browser_harness.helpers`（:29-53 导入 22 个函数），守护进程的自愈由 `admin.ensure_daemon`（:28）承担。

**勘误（相对常见误记）**：工具数量是 **23 个**，不是 20 个——从 `browser_new_tab`（:138）到 `browser_stop_recording`（:288）逐个数：new_tab/goto/page_info/click/type/fill/press/scroll/screenshot/list_tabs/current_tab/switch_tab/close_tab/ensure_real_tab/wait/wait_for_load/wait_for_element/js/cdp/upload_file/http_get/start_recording/stop_recording。另注意它住在 `src/` 直下而**不在 browser_harness 包内**——这是把 MCP 依赖做成可选 extra 的布局手段（见第五节）。

## 二、内部结构

- **服务器单例（:55）**：`SERVER = MCPServer("browser-harness")`，模块级，main() 只是 `SERVER.run()`（:294-296）。
- **序列化三件套（:58-96）**：`_normalize()` 递归把 NaN/Infinity 换成 None（:65）——注释解释了为什么要在这里做：`json.dumps(allow_nan=False)` 抛异常发生在调用 `default` 回调**之前**，所以 NaN 不能留给 `_json_default` 兜底（:59-63）；`_json_default()` 处理 bytes/datetime/Decimal/Path（:76-86）；`_dump()` 合成"永不抛错"的 JSON 文本（:89-96）。
- **stdout 防污染（:99-113）**：`_stderr_stdout()` 上下文管理器把 `sys.stdout` 临时换成 `sys.stderr`。原因写在 docstring 里：start_recording/stop_recording 等 helper 会 print 状态（:103-104），而 MCP stdio 模式下任何非 JSON-RPC 的 stdout 输出都会**打断协议流**。
- **`_tool` 装饰器（:116-135）**：全文件的核心抽象。包装后的 wrapper 做三件事——`ensure_daemon()` 保证守护进程活着（:128）；helper 调用包在 stdout 重定向下（:129-130）；任何异常转成 `ToolError`（MCP 的 tool-error 通道，:132-133）而非让服务器崩溃。注册时工具名取 `fn.__name__`、描述取 `fn.__doc__`（:135），参数 schema 直接由被包函数的类型注解生成。
- **23 个工具定义（:138-291）**：全部是一到三行的转发，多数补一个 `{"ok": True}` 或带语义键的返回壳（如 browser_screenshot 附 width/height/size_bytes，:196-200）。

## 三、外部连接

- **browser_harness.helpers**：唯一的业务依赖面。每个工具对应一个 helper，参数原样透传（例：browser_press 的 modifiers 位域 1=Alt/2=Ctrl/4=Meta/8=Shift，:179）。
- **browser_harness.admin.ensure_daemon**：每次工具调用前跑一遍，冷启动时这里可能阻塞数十秒（本地 Chrome 握手等待），MCP 客户端的工具超时要为此留余量。
- **mcp_cli.py**：控制台入口 `browser-harness-mcp`（mcp_cli.py:5-16）。它用 `from mcp_server import main` 顶层模块导入（:8），捕获 `ModuleNotFoundError` 并给出安装指引 `pip install 'browser-harness[mcp]'`（:10-14）——这就是 mcp_server.py 不放进包里的配套理由：`mcp` SDK 是可选依赖，缺了它时 `browser_harness` 本体导入路径完全不经过这段代码。
- **pyproject 的 `[mcp]` extra**：声明 mcp SDK 与独立入口脚本。
- **运行方式**：文档给出 `uv run python -m mcp_server`（:7）；客户端侧则把它配置为 stdio MCP server。

## 四、数据流

以一次"打开页面并截图"为例：

1. MCP 客户端经 stdio 发 tools/call `browser_goto {url}`。
2. `SERVER` 分发到 wrapper → `ensure_daemon()`（必要时拉起守护进程、等 Chrome Allow 弹窗）。
3. `goto_url(url)` 经 IPC 走守护进程 → CDP → Chrome，返回导航结果 dict。
4. wrapper 在 `_stderr_stdout()` 里执行（helper 若 print 不会碰 stdout）→ `_dump()` 序列化成 JSON 文本。
5. MCP 把 JSON 文本作为工具结果回给客户端；若第 3 步抛异常，则包成 `ToolError(str(exc))` 走错误通道（:132-133），原始异常用 `from exc` 保留链。
6. 截图类工具结果只含本地文件路径与几何信息（:200），图像字节不进协议——客户端自己按路径读文件。

数据形态的关键约束：**一切进 MCP 的值必须 JSON 安全**。这就是 `_normalize` 先行、`_dump` 兜底的原因——JS 求值（browser_js，:256-259）返回什么类型完全不受控，NaN/日期/大整数都可能出现在里面。

## 五、设计决策与取舍

- **薄包装而非重实现**：工具层零逻辑，浏览器语义的单一事实源保持在 helpers。代价是 helpers 的 API 即 MCP 的 API——给 helper 改签名或 docstring 等于改对外协议（:135 的 `description=fn.__doc__ or ""` 让 docstring 成为注册材料的一部分）。
- **工具级 ensure_daemon（:128）而非连接级**：MCP 客户端随时可能断连重连、长时间闲置后突然调用，把自愈放在每次调用前最鲁棒；代价是每调用多一次 ping 开销（守护进程健在时几乎为零）。
- **ToolError 通道承载一切失败（:132-133）**：包括守护进程启动失败。agent 客户端因此能在工具错误文本里读到"chrome-not-running"这类可行动的提示，而不是看到服务器消失。
- **stdout 重定向范围最小化（:99-113）**：只在 helper 执行期间替换 `sys.stdout`，不用全局重定向，避免吞掉 MCP 框架自己的合法 stdout 写入。
- **图像不进协议**：browser_screenshot 返回路径+尺寸（:196-200），避免 stdio 上搬运二进制 base64 的膨胀。
- **保留两个逃生舱口**：`browser_cdp` 直通任意 CDP 方法（:262-265，params 展开成 kwargs）；`browser_js` 直通任意表达式求值（:256-259）。组合它们可以做到本文件没封装的一切，这让 23 个工具的封闭清单不至于成为能力天花板。
- **`browser_http_get` 是唯一的"无浏览器"工具**（:275-279 docstring 明写 "browser-less"）：服务器进程直接发 HTTP，绕开守护进程链路，适合抓取不需要 cookie/渲染的纯文本。

## 六、新人提示

- **加新工具 = 写一个 helper + 一个 `@_tool` 函数**。注意 docstring 会原样变成工具描述，写给人看的措辞会直接进模型的工具选择决策；参数注解决定 schema，缺省值就是工具默认值。
- **绝对不要在工具函数里 print**。必须输出诊断信息时用 `sys.stderr`。历史上 helper 的 print 就是靠 `_stderr_stdout()`（:99-113）救回来的，绕过 wrapper 直接 print 会当场弄脏协议流。
- **返回值里出现 NaN 不会崩但会变 null**（:65）：下游若靠数值判断成败，注意这个静默替换。
- **客户端超时配置**：首次调用可能触发完整守护进程冷启动（Chrome 未开时还要开浏览器、等 Allow 弹窗），MCP 客户端默认的短超时会把这次调用掐死；报错文案会经由 ToolError 传回，可作为排障线索。
- **勘误**：不要到 `browser_harness/` 包里找 MCP 服务器——它在 `src/mcp_server.py`，测试对应 `tests/unit/test_mcp_server.py`；包内只有 16 行的 `mcp_cli.py` 入口垫片。
- **`import mcp` 失败的处理在 mcp_cli 不在本文件**：本文件顶层 `from mcp.server import MCPServer`（:24）直接硬依赖；缺依赖时的友好报错全靠入口垫片，绕过垫片直接 `python -m mcp_server` 会得到裸 ImportError。
