# 01 · main.cpp：启动序列、双平台事件循环与全仓心脏

> 源码：src/main.cpp（693 行）。行号锚全部经源码核实。

## 角色定位

main.cpp 是 Korgi 唯一的可执行主体，图谱里唯一的 complex 节点（fanOut=15）。一个文件装下五件事：配置解析（含热重载）、UDP 通道、MIDI 输入的 Windows/Linux 双实现、事件循环、MIDI 值到 Q2PRO RCON 包的转换。没有类没有命名空间，架构是"一组全局变量 + 一组自由函数"：`g_config`（main.cpp:83）是全局状态中枢，平台句柄在 main.cpp:52-70 按平台二选一编译。理解它的钥匙是接受"平台宏织锦"形态：Windows 走 WinSock2+winmm（main.cpp:30），Linux 走 ALSA+poll，平台无关的解析与打包逻辑只有一份。

## 内部结构

函数五组：**生命周期** `main`（main.cpp:660）与 `Run`（main.cpp:630）；**UDP 通道** `OpenSocket`（main.cpp:94）/ `CloseSocket`（main.cpp:120）；**MIDI 输入** `OpenMidiDevice`（main.cpp:220）/ `CloseMidiDevice` 双平台成对，`MidiInCallback`（main.cpp:185）仅 Windows，`GetMidiDeviceMatchingName` 仅 Linux，`PrintMidiDevices` 无调用方的调试枚举；**配置** `ReadConfigFile`（main.cpp:417，全仓最长函数）、`tokenize`（main.cpp:378）、`ConfigFileChanged`（main.cpp:335 Windows / main.cpp:370 Linux 桩）；**转换核心** `HandleMidiInput`（main.cpp:132）。Linux 侧还用宏把 `inet_pton`/`strcpy` 别名成 Windows 名（main.cpp:67），让一份函数体两平台都能编译。

## 外部连接

向内仅依赖 control_surface_map.h（main.cpp:72）：只用 `mapControl`/`setControlSurfaceType` 做别名解析。向外连两个世界：硬件侧是 winmm 回调注册（main.cpp:223）或 ALSA 订阅（main.cpp:276）；网络侧是纯 UDP `sendto`（main.cpp:176），目标是配置里 `connect` 指定的 Q2PRO 服务器；输出除 UDP 外还有 stdout 实时回显。

## 数据流

**启动序列**（main.cpp:662-681）顺序即依赖：默认 korgi.conf、argv[1] 可覆盖 → 先调一次 `ConfigFileChanged()` 初始化时间戳基线（main.cpp:668）→ `ReadConfigFile()` → `OpenSocket()` → `OpenMidiDevice()` → 注册 SIGINT → `Run()`；退出逆序清理。

**Run 双形态**（main.cpp:630-658）：Windows 主循环只剩 `Sleep(50)` 空转，真正入口是 winmm 推送的 `MidiInCallback`——过滤 MIM_DATA 后从 dwParam1 第 2、3 字节解出 CC 控件号与 0-127 值（main.cpp:190-191）直调 `HandleMidiInput`；Linux 侧 `poll` 阻塞至多 60 秒（main.cpp:638），逐事件取 `data.control.param/value` 作控件号/值（main.cpp:643-644）转 `HandleMidiInput`。两平台每轮末尾都查配置变化热重载（main.cpp:652），`g_terminate`（SIGINT 置位）退出。

**HandleMidiInput 三段式**（main.cpp:132-182）：查 buttons/knobs 两表（main.cpp:144）；按钮按下（值>0）取配置原文为命令（main.cpp:149），旋钮/滑条归一化后 `min*(1-v)+max*v` 插值、`%.3f` 格式化（main.cpp:158-162）；命令非空则拼 `\xff\xff\xff\xffrcon 密码 命令` 一次 `sendto`（main.cpp:174-176），未映射通道只打印不发包。

## 设计决策

- **回调推送 vs poll 轮询不是偏好而是平台 API 本性**：winmm 只有回调式输入、ALSA seq 天然是就绪描述符模型；作者拒绝造统一抽象层，代价是 4 个函数双份实现。
- **顺序启动失败即退**：三步初始化任何一步 false 直接 return 1，无重试无降级——工具型程序的正确姿态。
- **热重载原子性**：new_config 以旧 g_config 为基底（main.cpp:419），全文件零错误才整体替换（main.cpp:616）；出错仍报完所有错误行号，运行中实例零风险。

## 新人提示

- 先抓 main.cpp:660 的骨架，再跳 main.cpp:132 的 HandleMidiInput——中间 500 行都是这两点的支撑。
- 全仓 "channel" 实指 MIDI CC controller number（控件号 0-71）而非 MIDI 通道（0-15），别被命名带偏。
- 围观两处已知缺陷学反面教材：CloseMidiDevice 先 free 再用同指针 unsubscribe 的 use-after-free（main.cpp:307-308）；`midiInGetDevCaps` 传地址值当设备 ID（main.cpp:232）。
- 热重载只覆盖映射与密码：`g_sendToAddr` 只在 OpenSocket 填一次（main.cpp:107），改 connect 地址必须重启。想换引擎只改 main.cpp:174 的包格式；想加 MIDI 设备改的是另一个文件（见 02 篇）。
