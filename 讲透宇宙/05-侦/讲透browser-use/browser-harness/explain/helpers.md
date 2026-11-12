# helpers.py 精讲 — 浏览器控制总入口与 agent 扩展点

> 源码：`src/browser_harness/helpers.py`（668 行）｜图谱层 L04「浏览器控制助手层与 agent 扩展点」

## ① 角色定位

helpers.py 是整个 harness 面向调用方的**唯一门面**：agent 脚本里的 `goto_url()`、`click_at_xy()`、`js()`、`page_info()` 全部定义在这里。它不直接连浏览器，而是把每个动作包装成 JSON 请求，经 `_ipc` 发给常驻 daemon，由 daemon 转发 CDP（Chrome DevTools Protocol）命令——所以客户端永远是"薄"的：无 WebSocket、无异步事件循环，一次 `cdp()` 就是一次 socket 往返（helpers.py:52-77）。

文件头三行注释划定了双层结构：核心助手在本文件，**agent 可编辑的助手**放在 `BH_AGENT_WORKSPACE/agent_helpers.py`（helpers.py:1-5），并在模块导入末尾通过 `_load_agent_helpers()` 把后者注入本模块 globals（helpers.py:653-668）。run.py 的 `from .helpers import *`（run.py:33）加上 `exec(code, globals())`（run.py:409）使这些函数像内建函数一样直接可用。

## ② 内部结构

模块按"基础设施 → 导航 → 输入 → 视觉 → 标签页 → 等待 → 工具"分节：

- **导入期副作用**：`_load_env()` 在 import 时读 `REPO_ROOT/.env` 与 `AGENT_WORKSPACE/.env`，`os.environ.setdefault` 注入且不覆盖已有环境变量（helpers.py:19-36）；helpers.py:38 冻结 `NAME = BU_NAME`；helpers.py:650 与 helpers.py:668 两个尾部导入/调用同样在 import 期执行。
- **IPC 发送层**：`_send()` 统一处理连接（5s）、响应超时（默认 5s，截图 60s，helpers.py:41-45）、错误冒泡。`_IPCResponseTimeout` 携带上下文重抛——注释明说裸 TimeoutError 的 str 为空，调用方只能打印无用信息（helpers.py:58-65）。`cdp()` 是裸协议出口，`**params` 透传任意 CDP 参数（helpers.py:72-77）。
- **JS 求值链**：`_runtime_value`/`_decode_unserializable_js_value` 处理 CDP 的 `unserializableValue`（NaN/Infinity/BigInt 后缀 `n`，helpers.py:102-113）；`js()` 先按表达式原样求值，遇到 "Illegal return statement" 才补函数包装重试，避免错杀嵌套函数里的 return（helpers.py:561-591）。
- **输入系统**：三档保真度——`type_text` 用 `Input.insertText`（快但绕过框架监听器，helpers.py:196-197）；`fill_input` 面向 React/Vue 受控输入，focus→select-all→逐键 `press_key`→合成 input/change 事件（helpers.py:208-247）；`press_key` 维护 US 物理键盘三张映射表（`_KEYS`/`_PUNCTUATION_KEYS`/`_SHIFTED_CHARS`），保证 `e.key/e.code/e.keyCode` 三者一致，非美式字符（CJK/emoji）宁可只发 char 事件也不伪造物理键（helpers.py:249-324）。
- **标签页管理**：`switch_tab` 默认只换 attach 不换可见标签页；U+1F434 马标记随 attach 移动，剥前缀用 `slice(3)` 因为该 emoji 在 JS UTF-16 里是代理对加空格共 3 个码元（helpers.py:409-427）。
- **等待原语**：`wait_for_load` 轮询 readyState（对 SPA 失效）；`wait_for_element` 用 `checkVisibility` 走祖先链判断可见性并带旧 Chrome 回退（helpers.py:504-517）；`wait_for_network_idle` 基于 `drain_events()` 的请求记账，**按 active session 过滤**——后台轮询页会持续向 daemon 全局事件缓冲灌 Network 事件，不过滤会毒化空闲判定（helpers.py:526-559）。

## ③ 外部连接

- **向 _ipc**：`ipc.connect/request/sock_addr/_TMP` 全部经 helpers.py:10 的 `from . import _ipc as ipc`；调试截图与默认截图路径落在 `ipc._TMP`（helpers.py:180, 334）。
- **与 recorder 的刻意循环依赖**：helpers.py:648-650 在文件**底部**导入 recorder 的三个函数，注释写明"让 recorder 自己的 `from . import helpers` 看到一个完整定义的模块"；recorder 侧则在 `_capture` 内延迟导入 helpers（recorder.py:264）。这是教科书式的底部导入解环法。
- **与 run.py**：`from .helpers import *` 后 `_install_helper_trace()` 给所有公开可调用对象包上 trace 壳（run.py:181-190）；`_load_agent_helpers` 注入的名字同样会被包住。
- **与 mcp_server.py**：src/mcp_server.py 的 23 个 `browser_*` 工具是本文件函数的一行薄包装（如 `browser_goto` → `goto_url`）。
- **http_get 的双通道**：设了 `BROWSER_USE_API_KEY` 就走 fetch-use 代理（反爬/住宅 IP/重试），否则本地 urllib+gzip（helpers.py:628-645）。

## ④ 数据流

一次 `click_at_xy(300, 400)` 的完整路径：

1. （可选）`BH_DEBUG_CLICKS` 时先用 PIL 在截图上画红圈十字存盘（helpers.py:175-192）；
2. `cdp("Input.dispatchMouseEvent", ...)` 两次（pressed+released，helpers.py:193-194）→ `_send` → `ipc.connect` → daemon `handle()` → CDP WS → Chrome；
3. run.py 的 `_traced` 包装器记录时长并调用 `recorder.observe("click_at_xy", ...)`（run.py:169-175）；
4. recorder 若在录制，等 0.15s 页面重绘后截 JPEG 帧并写 events.jsonl。

`goto_url` 另有域技能钩子：`BH_DOMAIN_SKILLS=1` 时按 URL hostname 取一级域，列出 `AGENT_WORKSPACE/domain-skills/<域>/*.md` 前 10 个文件名附在返回值里（helpers.py:152-157）——只报文件名不读内容，agent 自己决定是否去读。

## ⑤ 设计决策与取舍

- **无状态客户端 + 常驻 daemon**：每次 CDP 调用新建 socket，换来的是客户端零清理负担、90 秒进程预算内可随时退出的简单模型；代价是每动作一次连接开销（本地命名 socket 可忽略，云端 60s 截图预算已在注释里为它留足）。
- **select-all 不走 press_key**：Ctrl/Cmd+A 若经 `press_key` 会附带 `char` 事件，Chrome 把它当可打印字符 "a"，字段根本没清空——所以 fill_input 直接构造带 `commands:["SelectAll"]` 的 `rawKeyDown`（helpers.py:227-238）。这是"事件保真度"压倒"API 复用"的典型取舍。
- **修饰键判定看浏览器 OS 而非本进程 OS**：`_select_all_modifier` 读 `Browser.getVersion` 的 UA 判断 Meta/Ctrl（helpers.py:199-206），因为 macOS 上远程控制 Linux 浏览器时二者可能不一致。
- **Illegal-return 二段式**：先裸跑再包装，牺牲偶发的一次重试换取常见路径零意外包装（helpers.py:585-591）。
- **agent_helpers 注入用 globals 直写**：跳过下划线名、不注册任何钩子——保持"agent 扩展点"零仪式感，代价是命名冲突时静默覆盖。

## ⑥ 新人提示（坑/勘误）

- **导入即副作用**：import helpers 会建目录（_ipc.py:22-25）、读 .env、执行 agent_helpers.py。写测试或复用模块时别假设 import 无害。
- `type_text` 后提交按钮仍 disabled 不是 bug——受控组件请换 `fill_input`（docstring 明示，helpers.py:209-213）。
- `page_info()` 在原生对话框打开时返回 `{"dialog": {...}}` 而非页面几何——JS 线程被冻结，这是唯一诚实答案（helpers.py:159-169）。
- `current_tab()` 必须走 meta 请求而不能自查 `Target.getTargetInfo`：daemon 对 `Target.*` 一律剥 session 当浏览器级调用，不带 targetId 时 Chrome 静默返回浏览器自身目标（daemon.py:682-693 注释）。
- `new_tab` 坚持"先建空白再导航"：把 URL 直接传 `createTarget` 会与 attach 竞态，wait_for_load 可能在导航开始前就返回（helpers.py:432-446）。
- 马标记可关：`BH_TAB_MARKER=0`（helpers.py:390-393）；emoji 是代理对，手工剥前缀别写成 `slice(1)`。
- `capture_screenshot(max_dim=1800)`：为部分图像 LLM 的 2000px 单边限制预留（helpers.py:331-333）。
