# 02 · plugins/sdk/python/gassist_sdk：插件侧 Python SDK

## 一、角色定位

`gassist_sdk` 是 **G-Assist 插件开发者用的客户端 SDK**——跑在插件进程里，代表插件与宿主引擎通过 stdin/stdout 上的 **V2 协议（JSON-RPC 2.0 + 4 字节大端长度前缀帧）** 通信。PROTOCOL_V2.md:5 明言"基于 JSON-RPC 2.0（same as MCP）"，且 **"All plugins MUST use Protocol V2. Legacy V1 is no longer supported"**。五模块分工：`plugin.py`（900 行，Plugin/MCPPlugin 两大类）、`protocol.py`（252 行，帧编解码与字节流读写）、`types.py`（169 行，dataclass 类型）、`mcp.py`（1206 行，MCP 服务器对接与工具自动发现）、`__init__.py`（91 行，公共 API 面）。它是三语 SDK 家族之一——`plugins/sdk/cpp/gassist_sdk.hpp`（424 行）与 `plugins/sdk/nodejs/gassist-sdk.js` 与它逐结构镜像。`plugins/sdk/python/setup.py:40-42` 的 `install_requires` 为空并注释 **"No external dependencies - uses only standard library!"**——零依赖是它的分发承诺。

## 二、内部结构

**plugin.py**：基类 `Plugin`（`plugins/sdk/python/gassist_sdk/plugin.py:86`）构造时注册 SIGTERM/SIGINT 关停钩子（`plugins/sdk/python/gassist_sdk/plugin.py:128-129`）；命令注册走 `@plugin.command(...)` 装饰器（`plugins/sdk/python/gassist_sdk/plugin.py:133-154`，handler 连同 name/description 存进 `self._commands`；模块级另有独立 `command()` 装饰器 `plugins/sdk/python/gassist_sdk/plugin.py:69-83`，只打标记不注册）。主循环 `_run_loop`（`plugins/sdk/python/gassist_sdk/plugin.py:224`）是**单线程同步读循环**：阻塞读一条→按 method 路由（`plugins/sdk/python/gassist_sdk/plugin.py:250-259`：ping/initialize/execute/input/shutdown 五方法）→再读下一条。子类 `MCPPlugin`（`plugins/sdk/python/gassist_sdk/plugin.py:457`）叠加 MCP 工具自动发现：`@plugin.discoverer`（`plugins/sdk/python/gassist_sdk/plugin.py:631`）与 `@plugin.action_poller`（`plugins/sdk/python/gassist_sdk/plugin.py:647`）装饰器、启动发现 `_startup_discovery`（`plugins/sdk/python/gassist_sdk/plugin.py:738`）、会话管理线程（`plugins/sdk/python/gassist_sdk/plugin.py:676`）、MCP 不可用时回退缓存的懒重连 handler（`plugins/sdk/python/gassist_sdk/plugin.py:802-838`）。

**protocol.py**：`Protocol` 类（`plugins/sdk/python/gassist_sdk/protocol.py:35`）持读写双锁；`MAX_MESSAGE_SIZE = 10*1024*1024`（`plugins/sdk/python/gassist_sdk/protocol.py:46`，10MB 上限）。`read_message`（`plugins/sdk/python/gassist_sdk/protocol.py:61`）先读 4 字节头 `struct.unpack(">I")`（`plugins/sdk/python/gassist_sdk/protocol.py:78`）、超限抛 `ProtocolError`（`plugins/sdk/python/gassist_sdk/protocol.py:80-81`），再校验 `jsonrpc=="2.0"`（`plugins/sdk/python/gassist_sdk/protocol.py:101`）。字节流双路径在 `_read_bytes` 分派（`plugins/sdk/python/gassist_sdk/protocol.py:170-175`）：win32 走 kernel32.ReadFile（`plugins/sdk/python/gassist_sdk/protocol.py:177`），posix 走 `sys.stdin.buffer.read`（`plugins/sdk/python/gassist_sdk/protocol.py:204`）。

**types.py 与 __init__.py**：`Context`（`types.py:33`，含 `last_user_message()` `types.py:41`）、`SystemInfo`（`types.py:53`）、`CommandResult`（`types.py:63`）、JSON-RPC 三件套（`types.py:85/115/144`）、`ErrorCode`（`types.py:158`，标准 -327xx 加自定义 -1/-2/-3）。`plugins/sdk/python/gassist_sdk/__init__.py:66-87` 的 `__all__` 导出四组公共面：Core Plugin / Types / Protocol Errors / MCP 全家（含 `HAS_REQUESTS`）。

**mcp.py**：`MCP_PROTOCOL_VERSION = "2024-11-05"`（`mcp.py:68`）——**与 docstring 引用的 2025-06-18 规范（`mcp.py:5`）差一代**，握手实际发送前者（`mcp.py:972` initialize 的 protocolVersion）。requests 用 try/except 探测（`mcp.py:59-64`，失败只禁 HTTP 传输）。类清单：sanitize_name(:88)/FunctionDef(:103)/FunctionRegistry(:142)/MCPTransport 抽象基类(:278)/StdioTransport(:309)/HTTPTransport(:386，POST+mcp-session-id 头+可选 SSE)/MCPSessionManager(:562)/MCPClient(:813)。

## 三、外部连接

- **与宿主引擎**：stdin/stdout 全双工；stdout 上的日志会污染协议流，故 SDK logging 只写文件（`plugins/sdk/python/gassist_sdk/plugin.py:48-54`，落 cwd 或 temp 的 gassist_sdk.log，路径探测在 `plugins/sdk/python/gassist_sdk/plugin.py:34-46`）。
- **与 MCP 服务器**：HTTP/stdio 双传输，完整 MCP 生命周期（initialize→initialized 通知→会话刷新→shutdown）。
- **与 C++ SDK 镜像**：`plugins/sdk/cpp/gassist_sdk.hpp:47` 同名 namespace gassist，`class Protocol`（hpp:56，10MB 上限 hpp:58，read_message hpp:70）、`class Plugin`（hpp:202，command hpp:222/stream hpp:228/run hpp:245/handle_ping hpp:301/handle_execute hpp:332）——与 Python 侧 `_handle_ping`/`_handle_execute`（plugins/sdk/python/gassist_sdk/plugin.py:270/314）一一对应，帧格式与方法集完全同构。
- **与 plugin_emulator**：emulator 是宿主侧模拟器（本系列 03 篇）。**勘误**：任务口径"SDK protocol.py 的 PING 1000ms/HEARTBEAT 5000ms"实为 emulator 侧常量——`plugins/plugin_emulator/protocol.py:26` `PING_TIMEOUT_MS=1000`、`:35` `PING_INTERVAL_MS=2000`、`:38` `HEARTBEAT_TIMEOUT_MS=5000`；SDK 的 protocol.py **不含任何计时常量**（计时责任全在宿主），规范依据是 PROTOCOL_V2.md:106"respond within 1 second"与 :126"miss 2 consecutive pings → engine watchdog 终止"。

## 四、数据流

**生命周期**：宿主拉起插件→`initialize`（`plugins/sdk/python/gassist_sdk/plugin.py:281` 应答 name/version/`protocol_version="2.0"`（`plugins/sdk/python/gassist_sdk/plugin.py:302`）/commands 清单）→宿主周期 `ping`（`plugins/sdk/python/gassist_sdk/plugin.py:270` 回显 timestamp）→用户触发 `execute`（`plugins/sdk/python/gassist_sdk/plugin.py:314`：取 function/arguments/context/system_info 并还原对象）→handler 执行期间可随时 `plugin.stream(...)`（`plugins/sdk/python/gassist_sdk/plugin.py:156`，method="stream" 的**通知**，靠 `self._current_request_id`（`plugins/sdk/python/gassist_sdk/plugin.py:336`）关联）→结束发 `complete` 通知（`plugins/sdk/python/gassist_sdk/plugin.py:422`，带 success/data/keep_session）或 `error` 通知（`plugins/sdk/python/gassist_sdk/plugin.py:435`）→宿主发 `shutdown` 置 `_running=False`（`plugins/sdk/python/gassist_sdk/plugin.py:391`）。

**passthrough 模式**：handler 调 `set_keep_session(True)`（`plugins/sdk/python/gassist_sdk/plugin.py:193`）后，后续用户输入走 `input`（`plugins/sdk/python/gassist_sdk/plugin.py:356`：先回 acknowledged，再分派给名为 `on_input` 的命令，无则回显）——多轮对话型插件的入口。

**参数注入**：`_call_handler`（`plugins/sdk/python/gassist_sdk/plugin.py:396`）用 `inspect.signature` 反射 handler 形参（`plugins/sdk/python/gassist_sdk/plugin.py:404` 方法体内 `import inspect`）：按名从 arguments 取值、`context`/`system_info` 形参注入对象、`**kwargs` 全量透传（`plugins/sdk/python/gassist_sdk/plugin.py:409-418`）——handler 签名即声明式依赖。

**MCP 发现流**（MCPPlugin.run，`plugins/sdk/python/gassist_sdk/plugin.py:667`）：启动发现（连不上 MCP 就装缓存占位 handler，真正调用时才重连重发现，`plugins/sdk/python/gassist_sdk/plugin.py:814-831`）→MCPSessionManager 后台线程保活与轮询→tools 变化回调 `_on_tools_changed`（`plugins/sdk/python/gassist_sdk/plugin.py:706`）重跑 discoverer、写缓存、更新 manifest.json。

## 五、设计决策

1. **延迟 import 拆依赖**：`from .mcp import ...` 在 plugin.py 共 **4 处、全在 MCPPlugin 方法体内**（`plugins/sdk/python/gassist_sdk/plugin.py:587/613/681/758`，注释称避免循环导入）——真正收益是纯命令插件（只用基类）**完全不需要 mcp.py/requests 可加载**，配合空 install_requires 兑现零依赖承诺。注：任务口径"5 处"按源码实为 4 处。同理 `import tempfile`（`plugins/sdk/python/gassist_sdk/plugin.py:36`）与 `import inspect`（`plugins/sdk/python/gassist_sdk/plugin.py:404/566`）均为方法体内延迟。
2. **同步读循环而非线程**：单线程"读一条处理一条"（docstring 自夸 "no threading required!"，`plugins/sdk/python/gassist_sdk/plugin.py:91`）——ping 天然在读循环内即时应答，并发复杂度推给宿主（引擎侧才有 watchdog）；MCPPlugin 需要后台轮询时才引入 MCPSessionManager 线程。
3. **win32 kernel32 直调**：Windows 管道有缓冲/编码坑，`GetStdHandle(-10/-11)`（`plugins/sdk/python/gassist_sdk/protocol.py:56-57`）拿原始句柄后 ReadFile/WriteFile+FlushFileBuffers（`plugins/sdk/python/gassist_sdk/protocol.py:241`）保证字节精确；posix 用 `sys.stdin/stdout.buffer`（`plugins/sdk/python/gassist_sdk/protocol.py:210/248`）。import 期即分流（`plugins/sdk/python/gassist_sdk/protocol.py:15-18`）。
4. **容错序列化**：`safe_serialize` default handler（`plugins/sdk/python/gassist_sdk/protocol.py:133-138`）把不可序列化对象降级为字符串占位并告警，插件返回奇怪对象不断流。
5. **版本代差如实标注**：MCP 按 2024-11-05 握手、docstring 引 2025-06-18（mcp.py:68 vs :5）；`plugins/sdk/python/setup.py:18` version="2.0.0" 而 `plugins/sdk/python/gassist_sdk/__init__.py:65` `__version__="3.1.0"` 双口径并存——跨语言对照以 initialize 应答的 protocol_version="2.0"（`plugins/sdk/python/gassist_sdk/plugin.py:302`）为准。
6. **三语同构**：Python/C++/Node 三 SDK 的 Protocol+Plugin 骨架、10MB 上限、五方法路由一致（C++ hpp:56-421、JS gassist-sdk.js:24/136），宿主无需感知插件实现语言。

## 六、新人提示

- **最小插件四步**：`Plugin("name")` → `@plugin.command("fn")` → handler 返回值即 complete 的 data → `plugin.run()`；照 `plugins/sdk/python/gassist_sdk/plugin.py:6-15` docstring 抄即可。
- **别用 print/logging 打 stdout**：stdout 是协议通道，调试走 `plugin.log()`（`plugins/sdk/python/gassist_sdk/plugin.py:182`，method="log" 通知）或文件日志。
- **stream 只在 execute/input 期间有效**：`_current_request_id` 为 None 时静默丢弃并告警（`plugins/sdk/python/gassist_sdk/plugin.py:169-171`）。
- **超时预算记牢**（PROTOCOL_V2.md:262 表）：ping→pong 1s、input→ack 2s、execute→complete 30s、会话总长 5 分钟，超时宿主直接杀进程——重活要边做边 `stream()` 且别超 30s。
- **写 MCP 插件先看 `plugins/sdk/python/gassist_sdk/plugin.py:486-511` 完整示例**（Stream Deck 场景）；`mcp` property 惰性建客户端（`plugins/sdk/python/gassist_sdk/plugin.py:608`），MCP 服务器不在线时插件仍可从缓存启动。
- **协议抓包**：帧是二进制前缀头不能直接 cat 管道；用 emulator（03 篇）或读 gassist_sdk.log 的 `SENDING MESSAGE:` 日志（`plugins/sdk/python/gassist_sdk/protocol.py:141`）。
- 跨语言移植对齐 `types.py:158` 的 ErrorCode 与 keep_session 语义；C++ 侧无 Notification dataclass 但 JSON 形状相同（hpp:390 send_complete）。
