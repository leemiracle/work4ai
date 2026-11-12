# 讲透 Korgi

> NVIDIA 的 MIDI 输入转 UDP 包工具：把 KORG nanoKONTROL2 控制器的旋钮/滑条/按钮实时转成 Q2PRO（Quake2 引擎）RCON 控制台命令——用实体调音台的手感调游戏画面参数。C++ 双平台（Win32 winmm / Linux ALSA）。

## 全链状态表（2026-11-08）

| 阶段 | 状态 | 产出 |
|---|---|---|
| 批分析 | ✅ 3 批 | 23 节点 / 28 边 |
| merge | ✅ 零丢失 | 无悬空边 |
| layers/tour | ✅ | 5 层 / 11 步 |
| finalize | ✅ validator 0/0 | knowledge-graph.json（23n/28e） |
| fingerprints | ✅ | 7 files @ 8ebbd0e7 |
| onboarding | ✅ | ONBOARDING.md 4467 字 / 55 锚 |
| explain | ✅ 3 篇 | main.cpp / control_surface_map / korgi.conf（2500/2499/2498 字，37/16/32 锚） |
| 锚终验 | ✅ 真坏 0 | 151 锚 150 好；唯一「坏」为 `127.0.0.1:27910` IP:port 正则误报非锚 |

图谱在仓内 `/usr-data/data2/repos/agent-repos/NVIDIA/Korgi/.understand-anything/knowledge-graph.json`。

## 源码甄别（写作期逐行实证）

1. **控件表实为 51 项非 56**——逐行清点 control_surface_map.cpp:35-85：11 走带 + 24 S/M/R + 8 滑条 + 8 旋钮；批产物 summary 的「56 项」口径已在图谱中修正为 51。
2. **CloseMidiDevice use-after-free**（main.cpp:307-308）：先 `snd_seq_port_subscribe_free` 再把同指针传 `snd_seq_unsubscribe_port`，释放顺序颠倒。
3. **mapControl 空指针陷阱**（control_surface_map.cpp:107 直接解引用初值 nullptr 的激活指针）：配置没写 `device_map` 却用别名即段错误。
4. **「midiChannel」命名误导**：全仓所谓 channel 实为 MIDI CC controller number（0-71），非 MIDI 通道（0-15）。
5. **热重载改 connect 不生效**：`g_sendToAddr` 只在 OpenSocket 填一次；且 Linux 热重载是恒 false 桩（main.cpp:370）。
6. `midiInGetDevCaps` 传 `(UINT_PTR)&变量` 地址值当设备 ID（main.cpp:232）；CMake `if(UNIX)` 会让 macOS 卡死在 REQUIRED ALSA；PrintMidiDevices 无调用方=死代码。
7. scanner 归类修正两处：CMakeLists 曾归 docs、korgi.conf 曾归 code，均按实质改判 config；tree-sitter 条件编译盲区手工补 5 函数（MidiInCallback[Win]/GetMidiDeviceMatchingName[Linux] 等双平台定义）。

## 阅读路线

按 `onboarding/ONBOARDING.md` 八节走；深读 explain 三篇：01 main.cpp（启动序列+双平台事件循环）→ 02 control_surface_map（51 项控件表）→ 03 korgi.conf（八种配置指令）。
