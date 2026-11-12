# G-Assist 新人入门指南（ONBOARDING）

> 基于知识图谱（496 节点 / 639 边 / 10 层 / 15 步 tour，commit `2f8b3b62`）与源码逐锚核实撰写，所有锚均经源码验证。

## ① 项目定位与一句话概述

**一句话**：G-Assist 是 NVIDIA 的实验性 RTX 本地 AI 助手生态仓——本体（Inference Engine + Overlay）闭源，本仓承载其全部**扩展面**：插件协议与三语言 SDK、15 个示例插件、测试模拟器、助手本体 RISE 接口的 C++/Python 绑定。

README 开篇即定位："an experimental on-device AI Assistant"（`README.md:3`），核心卖点是本地 SLM 跑在 RTX GPU、经 NVIDIA Overlay 交互免切窗（`README.md:9-11`）。新人先分清两个子系统：

- **插件侧**（`plugins/`）：社区扩展。三语言 SDK（`README.md:17-19`），插件以子进程被引擎拉起，走 stdin/stdout JSON-RPC。
- **本体侧**（`api/`）：RISE（Runtime Inference System Engine）接口——nvapi.h 尾部扩展段 + C++ 演示 + Python ctypes 绑定，让外部程序直接与助手对话（LLM 问答、流式 ASR）。

图谱视角：L04-L09 为插件侧，L02-L03 为本体侧，L10 是独立的 Agent Skills 发布线。

## ② 技术栈与代码版图（10 层图谱导读）

全仓语言构成：Python（SDK + 模拟器 + 多数示例）、C++（RISE API + LogiLED/hello-world-cpp）、Node.js（一 SDK 一示例）、批处理与 JSON。10 层从治理到发布信任链：

| 层 | 名称 | 导读 |
|---|---|---|
| L01 | 仓库治理与工程基础 | README/CONTRIBUTING/SECURITY + GitLab CI 与子模块 |
| L02 | RISE C++ API 与 NVAPI 头文件 | nvapi.h 尾部 RISE 段 + main.cpp/gassist_cli.cpp + miniaudio |
| L03 | Python RISE 绑定 | wrapper.cpp→python_binding.dll→rise.py 链 + 3498 行 pywebview GUI |
| L04 | 插件协议 V2 与三语言 SDK | 生态宪法层：协议规范 + 三语言实现 + 迁移指南 |
| L05 | 插件模拟器测试引擎 | 纯 Python 镜像 C++ 引擎：IPC/分帧/manifest/热监视 + validator |
| L06 | plugin-builder 脚手架 | Cursor 规则目录——"文档即脚手架" |
| L07 | 示例插件·入门与模板 | hello-world 三语言版 + template_plugin（V1 手写）+ mcp-stdio-example |
| L08 | 示例插件·在线服务集成 | Spotify/Gemini/Discord/Twitch/天气/股价/IFTTT |
| L09 | 示例插件·硬件灯效 | LogiLED/Nanoleaf/OpenRGB + old_v1 代际对照 |
| L10 | Agent Skills 与签名评测 | SKILL.md + 双轨 evals + Sigstore 签名 |

新人读码顺序 = tour 编排：「最小插件解剖」（步骤 2）→「V2 协议规范」（步骤 3）→「Python SDK 核心实现」（步骤 4）→「模拟器引擎」（步骤 8）；本体侧按「RISE C++ API」（步骤 13）→「Python RISE 绑定链」（步骤 14）走。最大文件 `api/bindings/python/rise-gui-desktop-direct.py`（3498 行）与 `api/c++/main.cpp`（1459 行）均属本体侧，插件开发者可后置。

## ③ 核心架构：插件协议 V2 与三语言 SDK

**协议是整个生态的契约核心**。V2 = JSON-RPC 2.0 over stdin/stdout，帧格式 `[4-byte big-endian length][UTF-8 JSON payload]`（`PLUGIN_MIGRATION_GUIDE_V2.md:441`）。V1→V2 质变（`PLUGIN_MIGRATION_GUIDE_V2.md:36-38`）：消息格式从"裸 JSON + `<<END>>` 分隔符"改为长度前缀分帧；心跳从插件自建线程改为引擎驱动 ping/pong。

协议常量以模拟器层为基准（注释明言对齐 C++ 引擎）：MAX_MESSAGE_SIZE 10MB、PING_TIMEOUT_MS 1000、HEARTBEAT_TIMEOUT_MS 5000、EXECUTE_TIMEOUT_MS 30000（`plugins/plugin_emulator/protocol.py:23-38`）。三语言 SDK 复刻同一组不变量：Python `gassist_sdk/protocol.py:46`、Node.js `gassist-sdk.js:26`、C++ `plugins/sdk/cpp/gassist_sdk.hpp:58`——**同一契约的三份语言面**，跨语言对照读是理解协议的最快路径。

Python SDK 是参考实现：`Plugin.run()` 主循环（`plugins/sdk/python/gassist_sdk/plugin.py:202`）分派 ping/initialize/execute/input/shutdown 五种请求（`plugins/sdk/python/gassist_sdk/plugin.py:250-258`）；`@plugin.command` 注册命令（`plugins/sdk/python/gassist_sdk/plugin.py:133`）、`plugin.stream()` 流式输出（`plugins/sdk/python/gassist_sdk/plugin.py:156`）、`set_keep_session()` 控制 passthrough（`plugins/sdk/python/gassist_sdk/plugin.py:193`，同文件）。协议层处理粘包与部分读，Windows 用 windll 把管道设为二进制模式。`__init__.py` docstring 内嵌两种插件最小示例（`plugins/sdk/python/gassist_sdk/__init__.py:20-31`），是全仓最高扇入枢纽（入度 14）；MCP 层 `mcp.py` 实现 HTTP/SSE 与 stdio 双传输、Tools/Resources/Prompts 三能力，`MCPPlugin` + `@plugin.discoverer` 把现成 MCP server 工具自动发现为 G-Assist 函数（`plugins/sdk/python/gassist_sdk/__init__.py:49` re-export）。

## ④ RISE C++ API 与 Python 绑定线

RISE 是助手本体对外的原生接口，藏在 **nvapi.h 尾部**：全文件 25533 行，25311 行后是本仓扩展的 RISE 段——`NV_RISE_CONTENT_TYPE` 枚举定义 TEXT/GRAPH/CUSTOM_BEHAVIOR/PROGRESS_UPDATE 等 10 种内容类型（`api/c++/nvapi.h:25313-25325`），`NvAPI_RegisterRiseCallback` 注册回调（`nvapi.h:25392-25412`），`NvAPI_RequestRise` 发请求（`nvapi.h:25452-25473`）。**甄别**：README:29 链接指向 GitHub nvapi 仓 L25283，与本地 25311 行有偏移——以本地为准。

C++ 演示线：`api/c++/main.cpp`（1459 行）用单头库 miniaudio 做麦克风采集（`api/c++/main.cpp:36-42`），`MicrophoneDataCallback`（`api/c++/main.cpp:122`）积累 PCM 样本，配 WAV 加载工具（`api/c++/main.cpp:581`），演示 LLM 对话、流式 ASR 与实时识别；`gassist_cli.cpp`（539 行）是命令行客户端。

Python 绑定链是"薄封装"样本：`wrapper.cpp` 十来行转调 nvapi64.lib 编出 `python_binding.dll`；`rise.py` 模块级 `ctypes.CDLL` 加载同目录 DLL（`api/bindings/python/rise/rise.py:193-195`），配置 argtypes/restype（`rise.py:206-209`），C 结构体复刻为 ctypes.Structure（`rise.py:44` 起），暴露 `register_rise_client()`（`rise.py:214`）、`send_rise_command()`（`rise.py:242`）与流式 ASR PoC `send_audio_chunk()`（`rise.py:322-341`）。上层是 3498 行 pywebview 桌面直连 GUI。**平台边界：仅 Windows**。

## ⑤ 插件生命周期：从 manifest 到 G-Assist 引擎

一个插件从被发现到被调用的完整链路：

1. **发现**：引擎扫描插件目录，目录名即调用名（`README.md:170-185` 四件套：plugin.py + manifest.json + config.json + libs/）。
2. **manifest 声明**：`manifestVersion: 1` / name / executable / persistent / `protocol_version: "2.0"` / functions 数组——`plugins/examples/hello-world/manifest.json:2-8` 与函数定义体（同文件 :9-46）。tags 是 SLM 意图匹配关键词，description 质量决定被选中概率。
3. **拉起与握手**：引擎读 executable（.py 直接跑无需编译），stdin 发 initialize，随后 ping/execute/input/shutdown 分派（SDK 侧 `plugins/sdk/python/gassist_sdk/plugin.py:250-258`）。模拟器 `Plugin` 类（`plugins/plugin_emulator/plugin.py`，837 行）完整镜像 C++ 引擎：拉子进程、长度前缀 IPC、心跳跟踪、握手。
4. **运行时语境**：引擎把插件 libs/ 自动注入 Python path——hello-world 保留手动兜底（`plugins/examples/hello-world/plugin.py:42-45`）；日志与配置落 `ProgramData/NVIDIA Corporation/nvtopps/rise/plugins/<name>/`（`plugins/sdk/python/gassist_sdk/plugin.py:60-65`）。
5. **tether 绑定（进阶）**：7 个真实服务示例（stock/spotify/ifttt/discord/nanoleaf/twitch/openrgb）manifest 带 `"tethered": true` 与 tether_config——heartbeat_interval 5 / heartbeat_timeout 20 / onboarding_timeout 60 / allow_passthrough true（`plugins/examples/stock/manifest.json:55-61`）。**甄别**：tether_config 只在这 7 个 manifest 出现且模拟器不消费——给本仓外 C++ 引擎读，勿在模拟器里找实现。

## ⑥ 开发第一个插件的最短路径

官方推荐 = 拷贝 hello-world 起步（`plugins/examples/hello-world/plugin.py:28` 自述"intentionally minimal to serve as a starting point"）。最短路径五步：

1. `cp -r plugins/examples/hello-world plugins/myplugin`，改 manifest 与目录名。
2. 写命令函数：`@plugin.command("say_hello")` 注册（`plugins/sdk/python/gassist_sdk/plugin.py:113`），docstring 即函数描述，返回字符串或 dict。
3. 流式用 `plugin.stream()`（`plugins/sdk/python/gassist_sdk/plugin.py:157-163`）；多轮对话用 `set_keep_session(True)` 进 passthrough，后续消息经 `on_input` 回调（`plugins/sdk/python/gassist_sdk/plugin.py:191`、`:203-256`）。
4. 入口即 `if __name__ == "__main__": plugin.run()`（`plugins/sdk/python/gassist_sdk/plugin.py:265-267`）。
5. Windows 下用共享脚手架 `plugins/examples/setup.bat`（520 行批处理）：`:setup_plugin:70` 按语言分流 `:setup_python:115`/`:setup_cpp:146`/`:setup_nodejs:188`，deploy_plugin 把 SDK 拷进 libs/ 并部署到 ProgramData——**15 个示例共用这一个 setup.bat**。

README 量化承诺："~20 lines of business logic vs. ~200+ lines of boilerplate"（`README.md:160`）。接 MCP 生态：`mcp-stdio-example/plugin.py`（257 行）演示把现成 stdio MCP server 作子进程拉起、其全部工具代理为 G-Assist 函数；或直接用 `MCPPlugin` + `@plugin.discoverer`。想彻底看穿协议读 `template_plugin`——但**甄别**：它是 V1 手写范式（文件头自述 "`<<END>>` delimiter" 与心跳线程，`plugins/examples/template_plugin/plugin.py` docstring、`:64-65`、`:204`），manifest **无** protocol_version 字段，属旧代际教学材料，勿照抄。

## ⑦ 测试与质量保障（emulator + evals）

**插件模拟器**（`plugins/plugin_emulator/`）是开发闭环关键一环：无 G-Assist、无 GUI 也能本地测插件。`engine.py` 的 `PluginEngine`（`engine.py:82`）聚合五种模式 EngineMode：INTERACTIVE / ONE_SHOT / PASSTHROUGH / AUTONOMOUS / BATCH（`engine.py:28-34`），AUTONOMOUS 即 LLM judge 自治测试（LLM 懒加载，`engine.py:136-137`）；`plugin.py` 管子进程与 IPC；`manager.py` 管目录发现；`watcher.py` 热重载。**校验器把测试做成工程**：`validator.py` 按九大类实测插件、每类 0-100 记分（`validator.py:74-75`）、总分映射字母等级（`validator.py:108-130`）。CLI 五子命令 list/exec/passthrough/test/interactive（`cli.py:310-380`），自带样例 `example_plugin/` 与 `test_example_plugin.json`。发布前先过 `test` 是硬规矩。

**Agent Skills 评测线**（`skills/g-assist-mcp-skill/`）是针对技能文档的另一套质量体系：双轨 evals——CI 轨 `evals/evals.json` 16 条（测捏造工具名等 agent 行为）+ 真机轨 `evals/evals-hardware.json` 31 条（测 modeset 回滚等硬件副作用）；`BENCHMARK.md:3` 给出 "Overall verdict: PASS"。发布信任链由 `skill.oms.sig` 完成：文件头即 `application/vnd.dev.sigstore.bundle.v0.3+json`（Sigstore bundle v0.3），DSSE in-toto 载荷对 SKILL.md/evals 三件/skill-card.md 逐文件 sha256 签名，证书链主体 "NVIDIA Agent Skills Signing"——可审计的完整性闭环。

## ⑧ 上手清单与避坑（新人提示）

**上手清单**（按依赖序）：
1. 读 `README.md:140-162` 架构图与 Protocol V2 特性表；
2. 走 tour 步骤 2-4：hello-world → `PLUGIN_MIGRATION_GUIDE_V2.md` → SDK plugin.py；
3. 模拟器 `python -m plugin_emulator` 本地验证；
4. 拷 hello-world 写第一个插件，setup.bat 部署；
5. 需要本体能力再入 api/ 线（Windows only）。

**避坑七条**（全部源码实证）：
- **11 个 .exe 全是 Git LFS 指针存根**非真二进制：实测 11 个（logiled 2 个 + 其余 9 示例各 1），如 `plugins/examples/logiled/plugin-installer.exe` 是三行 LFS pointer（oid sha256:fa028bf1...，size 8242140）。**注意：背景材料称"9 个"，实测 11 个**；clone 不带 LFS 时不可执行。
- **plugin-builder 不是可运行插件**：`plugins/plugin-builder/plugin.py` 与 `requirements.txt` 均 0 字节占位，真资产是 `.cursor/rules/RULE.md` 的生成规则——"文档即脚手架"。
- **template_plugin 是 V1 范式**（`<<END>>` + 自建心跳线程），manifest 无 `protocol_version`；新插件一律 V2 SDK 并显式声明 `"protocol_version": "2.0"`（hello-world/manifest.json:8）。
- **Windows 二进制模式**：stdin/stdout 分帧必须先设二进制模式，SDK 已处理 win32/posix 双路径——手写 IPC 最易漏。
- **stdout 是协议通道**：插件里任何 print 都污染帧流，日志走文件（`plugins/sdk/python/gassist_sdk/plugin.py:70-74`）或 stderr。
- **config.json 放密钥**必须加 .gitignore（`README.md:203`）；示例群共同范式 = setup 向导 + `store_pending_call` 鉴权重试（`plugins/examples/discord/plugin.py:148-166`）——首跑无凭据存待执行调用，向导完成后补发。
- **两层"版本"勿混淆**：`manifestVersion: 1` 是 schema 版本（模拟器 `manifest.py:20` 的 PLUGIN_VERSION_SUPPORTED=1 对齐 C++ 引擎），`protocol_version: "2.0"` 才是通信协议代际。

**图谱使用建议**：改协议前先巡 L04 三个 SDK 常量是否同步；新增示例按 L07-L09 归类（入门/在线服务/硬件）；高扇入枢纽 `gassist_sdk/__init__.py`（入度 14）与 `nvapi.h`（入度 8）是两系引力中心，动它们要全仓回归。
