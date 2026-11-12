# 03 · plugins/plugin_emulator：宿主侧测试引擎

## 一、角色定位

`plugin_emulator` 是 **G-Assist 引擎（宿主）的模拟器**——plugins/plugin_emulator/README.md:3 自述 "emulates the engine's plugin communication capabilities for plugin development and testing...without needing the full G-Assist engine"。它站在 V2 协议的**宿主端**：拉起插件子进程、发 initialize/execute/ping、收 stream/complete 通知、维护心跳看门狗，并叠加真引擎没有的测试设施（验证报告、LLM 裁判、文件监控、交互菜单）。与 02 篇的关系是**协议两端配对**：插件用 gassist_sdk 写（插件侧），在 emulator 里跑（宿主侧）；`plugins/plugin_emulator/protocol.py:8` 明言 "mirrors the C++ PluginProtocolV2.h implementation"——对标的 C++ 头是**闭源引擎内部的 PluginProtocolV2.h，不在本仓**（仓内 sdk/cpp 的 gassist_sdk.hpp 是插件侧镜像，勿混淆）。10 文件职责：`engine.py`（1249 行，编排核心+交互菜单）、`manager.py`（668 行，插件注册表）、`plugin.py`（837 行，单插件进程封装）、`protocol.py`（350 行，V2 协议实现）、`manifest.py`（438 行，manifest.json 解析）、`validator.py`（1360 行，合规记分卡）、`watcher.py`（302 行，变更监控）、`cli.py`（446 行，命令行入口）、`__main__.py`（12 行，`python -m plugin_emulator`）、`__init__.py`（105 行，公共面）。

## 二、内部结构

**protocol.py** 是宿主侧协议常量与帧工具的家：`MAX_MESSAGE_SIZE` 10MB（plugins/plugin_emulator/protocol.py:23）、`PING_TIMEOUT_MS=1000`（:26）、`INPUT_ACK_TIMEOUT_MS=2000`（:29）、`EXECUTE_TIMEOUT_MS=30000`（:32）、`PING_INTERVAL_MS=2000`（:35）、`HEARTBEAT_TIMEOUT_MS=5000`（:38）——与 PROTOCOL_V2.md:262 超时表逐项对应。`frame_message`（:178，`struct.pack('>I')` :201）与 `decode_length`（:206）做帧编解码，`classify_message`（:253）按 id/method/result 组合判 request/response/notification，五个 `build_*_request` 构造器（initialize :284/execute :296/shutdown :320/ping :329/input :339）让引擎侧"说话"类型安全。

**plugin.py** 把单个插件进程包成对象：`start`（plugins/plugin_emulator/plugin.py:176）用 `subprocess.Popen` 起进程，stdin/stdout 双 PIPE、**stderr=STDOUT 并入协议流**（plugins/plugin_emulator/plugin.py:202-212）、`bufsize=0` 无缓冲（:210）、win32 加 CREATE_NO_WINDOW（:211）；随后起 daemon 读线程 `_reader_loop`（:219-224，:624）。`stop`（:236）优雅路径是关 stdin→等 2 秒→kill（:254-268）。命令行构建 `_build_command_line`（:487）对 .py 插件找解释器（`_find_python` :510 依次试 `GA_PYTHON_DEV` 环境变量 :515 → 插件根 bundles 的 python/python.exe :520-523 → PATH 的 python/python3/py :526）；`_build_environment`（:533）给插件目录下的 libs 注入 PYTHONPATH（:538-545）。

**manager.py** 是插件注册表：`initialize`（manager.py:113）扫目录装载，`_load_plugin`（:202）逐个起进程，`_start_persistent_plugins`（:250）处理 persistent 声明，`_refresh_mcp_manifest`（:315）等 MCP 插件发现完工具后回读 manifest，`build_tool_catalog`（:646）把全部函数拼成 **OpenAI function calling 格式**的工具目录（描述加 `[Plugin: name]` 前缀 :661）。**watcher.py** 后台线程按 poll_interval 轮询目录 mtime（manifest+可执行文件双时间戳，watcher.py:108-147），变更回调 `_check_for_changes`（:149）驱动热重载。**manifest.py** 的 `ManifestParser.parse`（:151，注释"Mirrors the C++ parsePluginManifest()"）产出 `PluginManifest`（:119，name/executable/protocol_version/persistent/passthrough/functions/tags/mcp_* 字段），处理了 UTF-8 BOM（:172-174）。**validator.py**（:1-12 docstring）产出 PASS/FAIL/WARN/SKIP 记分卡，覆盖协议合规/心跳/超时/错误处理/manifest 准确性/流式行为。

## 三、外部连接

- **与插件进程**：每插件一个子进程，stdin/stdout 上的 V2 帧协议（见 02 篇插件侧实现）；`_send_and_wait`（plugins/plugin_emulator/plugin.py:563）按 request.id 建 per-request 响应队列（:578-579），读线程按 id 分发回包。
- **与 gassist_sdk 插件**：直接兼容——用 SDK 写的插件进程会被 emulator 拉起、initialize、execute；example_plugin/（manifest.json+plugin.py）是最小样例。
- **与外部 LLM 服务**：autonomous 模式的裁判走 NVIDIA API（requirements.txt 注释 "OpenAI-compatible, Set LLM_API_KEY"，可选依赖 `openai>=1.0.0`）。
- **与 CLI**：`__main__.py:9` 的 `python -m plugin_emulator` 进 `cli.py` 的子命令 list/exec/passthrough/test（cli.py:313/325/336/347）；`cmd_test`（:196）读 test_example_plugin.json 那样的测试套件（function/prompt/expectation/arguments 四元组）。

## 四、数据流

**交互模式**（默认）：`PluginEngine`（engine.py:82）初始化 PluginManager（:124）→装插件→`run_interactive`（engine.py:659）进菜单（列表/选插件/执行/验证/重载，`_show_main_menu` :754）。执行走 `execute`（engine.py:254）→manager.execute→Plugin 的 `_send_and_wait`→插件回 complete（含 keep_session 则切 passthrough，`awaiting_input` 状态）→`send_input`（engine.py:347）转发用户输入。

**autonomous 模式**：`test_function_autonomous`（engine.py:509）先真执行函数（:544），再让 LLM 裁判 `judge.assess_response` 对照 expectation 评估（:556）；判 FOLLOW_UP 且还有回合预算（EngineConfig 默认 `max_turns=3`，engine.py:79）就代用户追问（passthrough 内 `send_input` :570，非 passthrough 直接停 :574），终判 SUCCESS/ACCEPTABLE 算通过（:594），产出带 reasoning/confidence/turns_used 的 `AutonomousTestResult`（:51 定义）。裁判实例惰性获取（`_get_llm_judge` engine.py:484）：**方法体内延迟 `from llm_judge import LLMJudge`**（:491，需 sys.path.insert 指向父目录 :490），API key 取 config 或 `LLM_API_KEY` 环境变量（:493），缺 key 抛 ValueError（:495）。

**验证流**：菜单触发 `_menu_validate_plugin`（engine.py:1066）→`_run_validation`（:1103）**方法体内延迟 `from .validator import PluginValidator`**（:1105）→跑七类检查（manifest/启动/协议合规/心跳 ping/函数执行/错误处理/关停，:1120-1127）→打印记分卡，可选导出 JSON（:1145-1149）。

**读线程与心跳**：`_reader_loop`（plugins/plugin_emulator/plugin.py:624）**逐字节读**（注释自认"less efficient but more reliable for IPC" :641），缓冲区里增量解析 4 字节头+定长体；坏头（长度超 10MB）跳 4 字节重同步（:651-654）。`send_ping`（:447）/`update_heartbeat`（:462）/`is_heartbeat_expired`（:466）支撑引擎侧健康检查。

## 五、设计决策

1. **宿主/插件两侧同协议不同实现**：SDK protocol.py（插件侧，kernel32 管道 IO）与 emulator protocol.py（宿主侧，帧构造器+超时常量）不共享代码——常量唯一权威在宿主侧，插件侧"被动守法"，这与真引擎的 C++ PluginProtocolV2.h ↔ gassist_sdk.hpp 分工完全同构。
2. **延迟 import 三层用途**：`_run_validation` 的 `from .validator import PluginValidator`（engine.py:1105）让交互模式不必预载 1360 行验证器；llm_judge 延迟 import（:491/:554）隔离可选依赖。**甄别**：`llm_judge.py` 全仓 find 零命中——engine.py:504 提示 "Make sure llm_judge.py is in the parent directory"，即 autonomous 模式依赖**仓外文件**，开箱即用会 ImportError，这是真实的供应链缺口。
3. **stderr 并入 stdout 的取舍**：plugins/plugin_emulator/plugin.py:206 把插件 stderr 合进协议管道换取"看得见插件报错"；代价是插件一旦往 stderr/stdout 打印非帧文本就破坏定长帧解析——靠读线程的跳 4 字节重同步兜底（:651-654），但乱序文本可能被当成长度头造成假等待。配套约束是 SDK 侧日志全走文件（02 篇）。
4. **逐字节读 + 跨平台简单化**：不用 overlapped IO/select，读线程 1 字节循环加增量解析，慢但对 Windows 管道语义最稳；解释器三级探测（GA_PYTHON_DEV→bundled→PATH）让 emulator 在"引擎自带 Python"与开发机两种环境都能拉起 .py 插件。
5. **mtime 轮询而非文件系统事件**：watcher 用 poll_interval 睡眠扫 mtime（watcher.py:96-105），免掉 watchdog/inotify 依赖，2 秒粒度对插件开发场景够用。
6. **工具目录面向 LLM**：`build_tool_catalog`（manager.py:646）直接产出 OpenAI function calling 形状——emulator 不只做协议测试，还充当"插件函数 → LLM 可调用工具"的桥（engine.py:242 `get_tool_catalog` 供推理用）。

## 六、新人提示

- **最快上手**：`python -m plugin_emulator -d /path/to/plugins`（README:36）进交互菜单；先 `list` 看装载结果，`select` 后 `exec` 执行，`validate` 出记分卡。
- **跑 autonomous 测试前**：确认 `LLM_API_KEY` 已设置、`pip install openai`、且 `llm_judge.py` 放在 plugins/ 父目录（仓内没有，需自备——见上文甄别）；测试套件照 test_example_plugin.json 的四元组写。
- **插件被杀了先看 stderr**：因为 stderr 并进了 stdout（plugins/plugin_emulator/plugin.py:206），崩溃栈可能以"坏帧"形式出现在日志里；把 plugin 日志级别调 DEBUG 看 reader 的 parse 报错最直接。
- **passthrough 插件调试**：菜单执行 keep_session=true 的函数后进入 passthrough（README"Automatic Passthrough Mode"），`--input` 发数据、`--exit` 退出（cli.py:99 提示文案）。
- **改了插件没生效**：watcher 2 秒轮询 mtime，等一下或菜单里 Reload；MCP 插件注意 `_refresh_mcp_manifest`（manager.py:315）的等待逻辑——工具发现完才会更新函数清单。
- **对齐引擎行为**：写自己的宿主/测试器时直接抄 emulator 的常量（plugins/plugin_emulator/protocol.py:23-38），别自己拍超时数；PROTOCOL_V2.md:262 是规范出处。
- **Validator 记分卡七类检查**是发布前自查清单（engine.py:1120-1127），SKIP 不等于 PASS——被跳过的检查（如无函数插件跳过执行检查）要人工确认原因。
