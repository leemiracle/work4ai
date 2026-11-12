# 03 · korgi.conf：8 种配置指令与 RCON 映射写法

> 源码：bin/korgi.conf（14 行示例）+ README.md 配置节 + src/main.cpp 的 ReadConfigFile（main.cpp:417-623）。行号锚全部经源码核实。

## 角色定位

korgi.conf 是 Korgi 的全部用户界面——除配置路径本身外无命令行参数（main.cpp:664）、无 GUI，连哪台 Q2PRO、密码、设备、控件映射都由这份纯文本定义。bin/korgi.conf 随构建产物放 bin/，14 行演示 4 个连接/设备指令加 4 条映射——滑条变太阳高度角推子、旋钮变方位角、两按钮变物理天空开关（korgi.conf:9-12）。README.md:13 说明路径规则：默认当前目录 korgi.conf，唯一参数可换文件名。

## 内部结构

**词法层**（main.cpp:431-441）：逐行 fgets，掐掉 `#` 注释与换行（main.cpp:435），`tokenize`（main.cpp:378，支持双引号取整段）以空白分词。

**指令层 8 种分三组**：

1. 连接组：`connect <address> [port]`（main.cpp:444，端口缺省保持现值，默认 27910）；`password <password>`（main.cpp:459，**必填**，缺失即整体失败 main.cpp:610）。
2. 设备组：`device <id>`（main.cpp:472，Windows 数字设备号）；`device_name <name>`（main.cpp:485，Linux 按名匹配，默认 nanoKONTROL2）；`device_map <name>`（main.cpp:498，启用别名表，见 02 篇）。
3. 映射组：`button <id> <command...>`（main.cpp:516）；`knob|slider <id> <cvar> <min> <max>`（main.cpp:553，同分支处理）。

示例解剖：korgi.conf:1-2 本机地址与示例密码；:4-7 平台分工注释；四条映射见数据流节。

## 外部连接

配置是三个子系统的汇聚点：连接组喂 `OpenSocket`（地址进 `g_sendToAddr`，main.cpp:107）；设备组喂 `OpenMidiDevice`（Windows 用 device 走 midiInOpen，Linux 用 device_name 按名匹配）；映射组填 buttons/knobs 两张运行期热表供 `HandleMidiInput` 逐事件查询（main.cpp:144）。

所有指令有行级校验：出错报 `文件:行号: 原因`（main.cpp:602）并置失败——**任何错误都不提交新配置**（main.cpp:616-620），热重载可放心试错。

## 数据流

**映射语义两条路径**：

- `button` 通道参数先 strtol 试整数，非整数走别名查表并校验类型为 Button（main.cpp:530-548）。命令段**不 tokenize**——直接取通道词之后一整段（main.cpp:519），命令可含空格。运行期按钮按下（值>0）原文发送，弹起无动作（main.cpp:149）。
- `knob`/`slider` 取通道/cvar/min/max 四参（main.cpp:557），别名回退时类型须分别为 RotaryKnob/Slider（main.cpp:587-588）。运行期值 0-127 归一化后线性插值 `min*(1-v)+max*v`（main.cpp:158-161），格式化成 `cvar 值` 三位小数。README.md:31 点破：MIDI 侧 knob 与 slider 毫无区别（同表同插值），两个名字纯为可读性。

**示例四行效果**（korgi.conf:9-12）：`slider 0 sun_elevation 0 90` 滑条全程控制太阳高度；`knob 16 sun_azimuth 0 360` 旋钮一圈扫方位；两个 `button` 用 S0/R0 模拟物理天空开关。每条事件封成 `\xff\xff\xff\xffrcon qwerty <命令>` 的 UDP 包发往 127.0.0.1:27910（main.cpp:174-176）。

**热重载**：Windows 保存即触发（时间戳比较 main.cpp:335，Run 循环周期性检查），映射即时生效；但 connect 改地址不生效（socket 目标只在启动时填），Linux 完全不支持（main.cpp:370 桩恒 false）。

## 设计决策

- **行式语法而非 key=value**：让 button 的"剩余全收"语义（main.cpp:519）自然成立——命令带空格无需转义，为 RCON 命令量身定做。
- **双通道寻址**：裸数字与别名共存，别名列自动带类型校验——类型写错启动时即报，不留到运行期行为诡异。
- **解析失败不提交 + 报完所有错**：调试体验好、旧配置继续服务，热重载零风险。
- **默认值内建**（main.cpp:85）：地址/端口/device/device_name 都有缺省，最小配置只需 password 加映射两行；示例文件还自带平台分工注释（korgi.conf:4），配置自解释。

## 新人提示

- 第一份配置：抄 bin/korgi.conf 改 password 与 connect 即可跑通；想用别名就把通道号换成 `sl0`/`kn0`/`S0` 并加一行 `device_map nanoKONTROL2`（不加这行用别名会空指针崩溃，见 02 篇）。
- 排错先看 stderr：解析错误全带 `文件名:行号`，密码缺失有终检（main.cpp:610）。通道号速查：滑条 0-7、旋钮 16-23、S 排 32-39、M 排 48-55、R 排 64-71、走带 41-46/58-62。
- min/max 支持负数小数，插值线性——非线性手感得拆多档按钮模拟。
- 改 connect 记得重启进程；改映射随便存盘（仅 Windows）。示例密码别进生产——RCON 密码明文进包。
