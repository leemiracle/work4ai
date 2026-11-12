# Korgi 新手导航（ONBOARDING）

> 图谱基线：23 节点 / 28 边 / 5 层 / 11 步 tour @ 8ebbd0e7。行号锚全部经源码核实（2026-11-08）。

## 1. 项目定位与核心价值

Korgi 是 NVIDIA 2019 年开源（MIT 许可）的极简 C++ 工具：把 KORG nanoKONTROL2 MIDI 控制器的旋钮、滑条、按钮实时转换成 Q2PRO（Quake2 引擎现代化分支）RCON 协议的 UDP 包。README.md:3 定位一句话 "converts input from a MIDI device into UDP packets"；README.md:7 说明专为 nanoKONTROL2 设计——项目名 Korgi 取自设备厂商 KORG。

典型场景是"用实体调音台的手感调游戏画面参数"：bin/korgi.conf:9-12 官方示例正是滑条绑 `sun_elevation 0 90`、旋钮绑 `sun_azimuth 0 360`、两按钮发 `physical_sky 1/0` 做开关。全仓实质文件仅 4 个、零第三方依赖即完成"硬件输入→协议打包→网络发送"，是这类桥接的最小范本。

## 2. 总体架构

图谱 5 层：L01 构建与许可（CMakeLists.txt+LICENSE）→ L02 文档（README）→ L03 运行时配置（bin/korgi.conf）→ L04 控件映射数据层（control_surface_map.h/.cpp）→ L05 主程序（main.cpp）。前两层是静态外围，L03 是运行时输入，L04/L05 是代码主体——main.cpp 是唯一复杂节点（fanOut=15），control_surface_map 是它唯一的本地依赖。系统单进程单线程，一个事件循环串起 MIDI 读入、查表翻译、UDP 发包三步。

## 3. 核心模块地图

**main.cpp（693 行，全仓心脏）**五组函数：

- 生命周期：`main`（main.cpp:660）按"配置→socket→MIDI→事件循环"启动；`Run`（main.cpp:630）平台分岔主循环。
- UDP 通道：`OpenSocket`（main.cpp:94）/`CloseSocket`（main.cpp:120）。
- MIDI 输入：`OpenMidiDevice`（main.cpp:220）/`CloseMidiDevice`（main.cpp:301）双平台；`MidiInCallback` Windows 回调；`GetMidiDeviceMatchingName` Linux 按名找设备；`PrintMidiDevices` 调试枚举、无调用方。
- 配置：`ReadConfigFile`（main.cpp:417）解析 8 种指令；`tokenize`（main.cpp:378）支持双引号；`ConfigFileChanged`（main.cpp:335 Windows / main.cpp:370 Linux 桩）热重载探测。
- 转换核心：`HandleMidiInput`（main.cpp:132）——控件号+0-127 值进、RCON 包出。

**control_surface_map**：`ControlSurface` 结构（control_surface_map.h:23，Type 枚举 Button/Slider/RotaryKnob + channel）；51 项 nanoKONTROL2 别名表（control_surface_map.cpp:34-86，见第 7 节勘误）；`setControlSurfaceType`（control_surface_map.cpp:94）选表、`mapControl`（control_surface_map.cpp:105）查表。

**数据结构**（main.cpp）：`KorgiConfig`（main.cpp:83）含连接参数与 buttons、knobs 两张 unordered_map（slider 与 knob 共用 knobs 表）；`KnobMapping`（main.cpp:76）是 cvar 名+min+max 三元组。

## 4. 数据流/控制流

**启动序列**（main.cpp:662-681）：默认读 korgi.conf（argv[1] 可覆盖）→ 空跑一次 `ConfigFileChanged()` 初始化时间戳基线 → `ReadConfigFile()` → `OpenSocket()` → `OpenMidiDevice()` → 注册 SIGINT → `Run()`。任何一步失败直接退出，顺序即依赖。

**事件流两平台汇入同一函数**：

- Windows：`midiInOpen` 注册回调（main.cpp:223），winmm 推送事件；回调过滤 MIM_DATA、从 dwParam1 解出控件号与值（main.cpp:190-191）转 `HandleMidiInput`。主循环只 `Sleep(50)` 空转（main.cpp:636）。
- Linux：连 ALSA、建接收端口（main.cpp:245）、按名订阅设备（main.cpp:250）、取 poll 描述符；`Run` 里 `poll` 60 秒超时（main.cpp:638），逐事件取 `data.control.param/value` 作控件号/值（main.cpp:643-644）转 `HandleMidiInput`。

**HandleMidiInput（main.cpp:132-182）**：查 buttons/knobs 两表——按钮按下（值>0）原文入包，弹起无动作；旋钮/滑条把 0-127 归一化后按 `min*(1-v)+max*v` 线性插值（main.cpp:158-161）拼 "cvar 值"；最终统一 `\xff\xff\xff\xffrcon 密码 命令` 经 `sendto` 发出（main.cpp:174-176）——4 个 0xFF 是 Quake 系带外消息头。未映射通道只打印不发包。

**热重载流**：`Run` 每轮调 `ConfigFileChanged`（main.cpp:652），Windows 用文件时间戳比基线，变了就重读配置；new_config 以旧配置为基底（main.cpp:419），全部成功才原子替换 g_config（main.cpp:616-620），失败保留旧配置继续跑。Linux 桩恒 false 不支持。

## 5. 环境与运行方式

- **构建**：CMake ≥ 3.10，唯一目标 korgi（CMakeLists.txt:5），四种构建配置产物统一输出 bin/（CMakeLists.txt:18）。
- **依赖**：Linux 需 ALSA 开发库（CMakeLists.txt:11）；Windows 靠 `#pragma comment` 自动链 winmm/ws2_32（main.cpp:46）。
- **运行**：`korgi [conf路径]`，默认当前目录 korgi.conf。stdout 实时回显——同控件连续触发用 `\r` 原地覆盖、换控件换行（main.cpp:134）。
- **平台分工**：`device`（数字 ID）Windows 专用、`device_name`（名字匹配）Linux 专用，korgi.conf:4-7 注释明示。

## 6. 设计决策与权衡

- **各平台用最地道 API，不做统一抽象**：Windows 回调推送、Linux poll 轮询，4 个函数 `#ifdef` 分岔；代价是双份实现，收益是零抽象层。
- **别名表与裸通道号双轨**：别名经 `mapControl` 翻译并强校验类型（main.cpp:541、main.cpp:587-588）；扩展新设备只需注册一张表（control_surface_map.cpp:88），主程序零改动。
- **配置原子替换 + fire-and-forget UDP**：热重载全成功才提交；无连接无确认无重试，密码明文进包——RCON 本就是明文协议，内网工具定位可接受；换引擎只需改 main.cpp:174 打包格式一行。
- **button 命令段不走 tokenize**：直接取行内剩余（main.cpp:519），天然支持带空格命令。

## 7. 已知问题与勘误

1. **控件表实为 51 项非 56**：逐行清点 control_surface_map.cpp:35-85 = 11 走带 + 24 个 S/M/R + 8 滑条 + 8 旋钮。
2. **CloseMidiDevice 释放顺序颠倒**：main.cpp:307 先 free 订阅、main.cpp:308 又把该指针传 unsubscribe——use-after-free，应先退订再 free。
3. **mapControl 无空表防护**：control_surface_map.cpp:107 直接解引用初值 nullptr 的激活指针（control_surface_map.cpp:92）；配置没写 `device_map` 却用别名即崩溃，README.md:27 的"无映射请用通道号"是唯一防线。
4. **"midiChannel" 命名误导**：全仓所谓 channel 实为 MIDI CC controller number（控件号 0-71）而非 MIDI 通道（0-15）。
5. **热重载改 connect 不生效**：`g_sendToAddr` 只在 OpenSocket 填充（main.cpp:107），改地址须重启。
6. **midiInGetDevCaps 传参可疑**：main.cpp:232 传 `(UINT_PTR)&变量` 地址值而非设备 ID，Windows 打印设备名大概率恒失败。
7. **Linux 无热重载**（main.cpp:370 桩恒 false），README 未提该差异。
8. **CMake 用 `if (UNIX)` 判 ALSA**（CMakeLists.txt:10）：macOS 等会被 REQUIRED 卡死，应为 LINUX。
9. **死代码**：`PrintMidiDevices`（main.cpp:316）无调用方；`#if`/`#ifdef _WIN32` 混用。

## 8. 新人上手路线

1. 读 README（32 行）对照 bin/korgi.conf 过 8 种指令。
2. 从 main.cpp:660 的 `main` 顺启动序列走一遍骨架。
3. 精读 HandleMidiInput（main.cpp:132-182）：查表、按钮分支、插值、RCON 打包单函数全覆盖。
4. 对照别名表认控件号：S=32-39、M=48-55、R=64-71、走带=41-46/58-62、滑条=0-7、旋钮=16-23。
5. 带问题回看：为何 Windows 回调 Linux poll？热重载边界？然后加一条旋钮映射，按第 4 节数据流推演它会发出什么包。

记忆钩子：**配置（ReadConfigFile）→ 映射（mapControl）→ 事件（HandleMidiInput）→ UDP（OpenSocket）**，四步就是 Korgi 的全部。
