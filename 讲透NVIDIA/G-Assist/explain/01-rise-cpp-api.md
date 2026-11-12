# 01 · api/c++/：RISE C++ API 与两个 CLI 示例

## 一、角色定位

`api/c++/` 是 **RISE（Runtime Inference System Engine，NVIDIA 端侧推理引擎）的官方 C++ 客户端示范目录**（`api/c++/README.md:1-3` 自述），"厂商头 + 可编译样例"组合：`nvapi.h`（25533 行厂商头）尾部 25310-25533 行追加 **RISE 专用接口段——这是全仓 Python binding 线的 C 源头**；`gassist_cli.cpp`（539 行）是**无交互最小 CLI**（`--asr <wav>` / `--llm "<prompt>"`，结果只进 stdout，`gassist_cli.cpp:8-12`）；`main.cpp`（1459 行）是**交互菜单版 demo**：LLM 聊天 / WAV ASR / **实时麦克风 ASR** 三选项（`api/c++/main.cpp:1405-1408`）；`miniaudio.h`（95649 行）是第三方单头音频库，只为麦克风 demo 服务。一句话：示范第三方应用如何用**两个 NvAPI 函数（注册回调 + 发请求）**接入 RISE 的流式语音/文字通道。

## 二、内部结构

**两示例"四件套复制粘贴共享"**：`gassist_cli.cpp` 与 `main.cpp` 各自独立可编译、无公共源文件，于是 `Semaphore`（`gassist_cli.cpp:35` / `api/c++/main.cpp:51`，mutex+condition_variable 手搓计数信号量）、`WavHeader`（`gassist_cli.cpp:99-115`，`#pragma pack(push,1)` 单字节对齐）、`LoadWavFile`（`gassist_cli.cpp:117`，只收 audioFormat==1 且 16bit 的 PCM）、`Base64Encode`（`gassist_cli.cpp:148`）在两文件逐字重复——样例哲学是**每个文件拷走即可编译，宁复制不引依赖**。

**gassist_cli.cpp 主线**：全局状态区（`gassist_cli.cpp:70-93`）用**内容类型位掩码**追踪流式完成度——`CT_TEXT/CT_CUSTOM_BEHAVIOR/CT_CUSTOM_BEHAVIOR_RESULT/CT_GRAPH` 四位（`gassist_cli.cpp:82-85`），类型首次收到数据置"期望"位、回调报 `completed==1` 置"完成"位，`AllExpectedTypesComplete()`（`gassist_cli.cpp:90-93`）要求**全部期望类型到齐才释放信号量**（一次 LLM 应答可能并发流回正文/工具调用/图表）。`InitializeRise`（`gassist_cli.cpp:278`）做 Initialize+RegisterRiseCallback 后**轮询等 READY 回调、30 秒超时**（`gassist_cli.cpp:294-302`）。

**main.cpp 增量**：`RiseCallbackHandler`（`api/c++/main.cpp:222`）处理面更宽；`GetContentTypeName`（`api/c++/main.cpp:187`）把枚举转可读名，其中**值 10 标为 "RESERVED (ASR)"，但 `NV_RISE_CONTENT_TYPE_RESERVED = 10` 是 `api/c++/main.cpp:178` 客户端自定义 constexpr，nvapi.h 枚举只定义到 UPDATE_INFO=9**——客户端样例"逆向"出的未文档化内容类型。麦克风区定义 `MIC_SAMPLE_RATE=16000` 单声道（`api/c++/main.cpp:109`）与音频线程回调 `MicrophoneDataCallback`（`api/c++/main.cpp:122`）。

## 三、外部连接

**nvapi.h 是唯一核心依赖**。RISE 段内容：`NV_RISE_CONTENT_TYPE` 枚举（`nvapi.h:25313-25325`，INVALID=0 到 UPDATE_INFO=9 十值）；回调载荷 `NV_RISE_CALLBACK_DATA_V1`（`nvapi.h:25330`，super+contentType+content+completed 四字段）；入口函数 `NvAPI_RegisterRiseCallback`（`nvapi.h:25412`）与 `NvAPI_RequestRise`（`nvapi.h:25473`），均注明 **Windows 10+、since Release r570**；请求结构 `NV_REQUEST_RISE_SETTINGS_V1`（`nvapi.h:25418-25444`，version/contentType/content/completed/reserved[32]，版本宏走 `MAKE_NVAPI_VERSION`，`nvapi.h:25446`）；另有 `NvAPI_UninstallRise`（`nvapi.h:25519`，仍有客户端注册时失败）。

**miniaudio 调用面极小**：95649 行单头库只被调 5 个生命周期入口——`ma_context_init`（`api/c++/main.cpp:909`）、`ma_context_get_devices`（`api/c++/main.cpp:921`）、`ma_device_config_init`（`api/c++/main.cpp:983`）、`ma_device_init`（`api/c++/main.cpp:991`）、`ma_device_start`（`api/c++/main.cpp:1038`），外加 uninit/stop 清理组；编译期用 `MA_NO_DECODING/ENCODING/GENERATION`（`api/c++/main.cpp:39-41`）裁能力。

**构建**：`rise_demo_client.sln:6,8` 装载 `rise_demo_client`（编 main.cpp）与 `gassist_cli` 两工程，x64 Console，链接目录内 `nvapi64.lib`（`gassist_cli.vcxproj:70`）。任务书说的"三工程"实为**跨目录**：第三个 `python_binding.vcxproj` 在 `api/bindings/python/`（`python_binding.vcxproj:124` 只编 `wrapper.cpp`，DynamicLibrary 产出 Python 扩展），把同一 RISE 接口包给 Python。

## 四、数据流

**ASR（WAV 版，`DoASR`，`gassist_cli.cpp:311`）**：读 WAV→立体声转单声（`gassist_cli.cpp:322-330`）→复位状态排空信号量→**700 样本/块**切片（`gassist_cli.cpp:343`；`api/c++/main.cpp:1132` 注释互证 "~44ms at 16kHz"）→int16 转 float32（÷32768.0f）→Base64→拼 **`CHUNK:<id>:<sample_rate>:<base64>`**（`gassist_cli.cpp:363-364`）→`NvAPI_RequestRise` 以 TEXT+`completed=0` 发送→**每块等确认信号量再发下一块**（`gassist_cli.cpp:380`，间 20ms 背压）→置 `g_waitingForAsrFinal=true` 后发 **`STOP:`**（`gassist_cli.cpp:399`）→回调只认 `ASR_FINAL:` 前缀、跳过 `ASR_INTERIM:`（`gassist_cli.cpp:192-196`）→15 秒超时等终稿。

**麦克风版差异**（`DemoASRMicrophone`，`api/c++/main.cpp:899`）：音频线程把 float32 样本压进互斥锁 `micBuffer`，主循环凑满 700 样本即发（`api/c++/main.cpp:1155-1157`）。两道防御：发送前校验载荷不超 `content` 容量（`api/c++/main.cpp:1218-1221`）；启动后 **500ms 内必须有 RMS>0.0005 真实音频**（`api/c++/main.cpp:1031-1033`），计时从 `ma_device_start` 调用**前**开始——注释明说蓝牙麦初始化可能阻塞数秒（`api/c++/main.cpp:1028-1036`）。STOP 阶段先置等待标志、睡 100ms 等 in-flight 回调、排空信号量后才发 STOP（`api/c++/main.cpp:1273-1286`），终稿优先 `lastAsrFinalResponse`（`api/c++/main.cpp:1361`），10 秒超时。

**LLM（`DoLLM`，`gassist_cli.cpp:438`）**：拼 JSON `{"prompt":...,"context_assist":{},"client_config":{}}`（`gassist_cli.cpp:451`）单次发送（`completed=1`），60 秒超时收流式聚合结果；GRAPH 数据单独进 `g_chartData`，结束时以 `[CHART_DATA]` 标记打 **stderr** 与正文分流（`gassist_cli.cpp:528-534`）。

## 五、设计决策

1. **复制优于抽库**：四件套双份，读者拷单文件即可编译；代价是重复代码与演化漂移（两文件回调已分成 `RiseCallback` 与 `RiseCallbackHandler` 两套）。
2. **位掩码完成追踪**：expected/completed 双 bitmask 解决"多内容类型并发流式、何时算应答结束"，比计数器紧凑，但依赖"首次见到才算期望"的动态语义（`gassist_cli.cpp:78-81` 注释自述）。
3. **文本通道复用**：音频不走独立内容类型，Base64 后塞进 TEXT 的前缀文本协议（CHUNK/STOP/ASR_FINAL）——极简，但二进制安全性强压给 Base64（+33% 体积）且无校验和，`api/c++/main.cpp:1218` 的容量检查是唯一防线。
4. **厂商头零侵入追加**：RISE 段接尾部、沿用 `MAKE_NVAPI_VERSION` 与 super-struct 版本化惯例，客户端不需新链接库（仍只链 nvapi64.lib）。
5. **SAL 注解"书挡"结构**：nvapi.h:38 以 `#include"nvapi_lite_salstart.h"` 开场（**零空格 `#include"` 写法，六处 include 全如此**，格式化工具"修复"反而失真）；salstart 把 `__in/__out` 等 SAL 批注定义为空宏并记 `__nvapi_undef__*` 标志（`nvapi_lite_salstart.h:39-41`）、尾部定义 `NVAPI_INTERFACE` 声明宏（`nvapi_lite_salstart.h:813`）；文件尾 `#include"nvapi_lite_salend.h"`（nvapi.h:25533）按标志 `#undef` 还原（`nvapi_lite_salend.h:27-37`）——不支持 SAL 的编译器也能编译，且不污染外层宏空间。
6. **每块停等确认**：确定性背压，代价是吞吐受往返延迟限制。

## 六、新人提示

- **先读 README 再读码**：`api/c++/README.md` 的请求/响应格式表（LLM JSON、CHUNK、STOP、ASR_INTERIM/FINAL）与源码一一对应。
- **两二进制分工**：管道友好自动化选 `gassist_cli.exe`（stdout 只有终稿）；观察流式过程选 `rise_demo_client.exe`。
- **调麦克风开 `g_micDebugLogging`**（`api/c++/main.cpp:113`）：`[MIC_DEBUG]` 全链路日志（设备启动耗时、RMS 水位、每块发送/确认耗时），蓝牙麦不吐数据的排查路径全在里面。
- **别把 api/c++/main.cpp:178 的 RESERVED=10 当官方枚举**：只在这一个客户端文件定义，nvapi.h 升级补官方定义后可能撞名。
- **Windows 专用**：`strncpy_s`/`__cdecl`/r570 驱动依赖都表明示例只跑 Windows 10+；Linux 走 plugins 侧进程协议（见本系列 02 篇）。
- **`#pragma pack(push,8)`（nvapi.h:47）是结构兼容生命线**：复制结构定义须连同对齐与 reserved[32] 一起搬，否则回调数据错位。
- 想抽公共工具请参考 `audio_utils.h` 路线（inline 工具如 `EncodeAudioChunk` audio_utils.h:118、`DetectVoiceActivity` audio_utils.h:166），别建共享编译单元破坏单文件自包含惯例。
