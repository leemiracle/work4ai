# 02 · control_surface_map：51 项控件别名表与两个查询函数

> 源码：src/control_surface_map.h（42 行）/ src/control_surface_map.cpp（115 行）。行号锚全部经源码核实。

## 角色定位

这个模块回答一个问题：配置文件里人类写的控件别名（`rewind`、`sl0`、`kn3`）如何变成程序能匹配的 MIDI 控件号与控件类型。它是纯数据层——一张设备别名表、一个设备注册表、两个查询函数，无 I/O、无平台代码、不依赖 main.cpp。唯一消费者是 main.cpp `ReadConfigFile` 的别名回退分支（main.cpp:534 调 `mapControl`）。没有它，配置只能写裸数字；有了它可写语义别名——可读且带类型校验。

## 内部结构

**头文件只有一个类型**：`ControlSurface`（control_surface_map.h:23-38），内嵌 Type 枚举 Button/Slider/RotaryKnob 加 type/channel 两字段，带默认与双参构造；接口是两个自由函数声明（control_surface_map.h:40）。

**实现三层**：①构造宏（control_surface_map.cpp:28-30）`BUTTON`/`SLIDER`/`KNOB` 展开成对应 Type 的临时对象，表里一行一个控件、类型醒目。②别名表 `controlMap_Korg_nanoKONTROL2`（control_surface_map.cpp:34-86，`map<string, ControlSurface>`），**逐行清点共 51 项**——走带 11 键（通道 41-46 与 58-62，control_surface_map.cpp:35-45）、S 排 8 键（S0-S7=32-39）、M 排 8 键（M0-M7=48-55）、R 排 8 键（R0-R7=64-71）、滑条 8 路（sl0-sl7=0-7）、旋钮 8 路（kn0-kn7=16-23），合计 35 Button、8 Slider、8 RotaryKnob。③注册表 `controlSurfaces` 把设备名 "nanoKONTROL2" 映到表地址（control_surface_map.cpp:88，仅此一张），模块静态指针 `controlSurfaceMap` 记录激活表、初值 nullptr（control_surface_map.cpp:92）。

**两个查询函数**：`setControlSurfaceType`（control_surface_map.cpp:94-103）find 验存在后把激活指针指过去，未知名返回 false；`mapControl`（control_surface_map.cpp:105-114）在激活表 find 别名，命中拷入 out 返回 true。

## 外部连接

- **上游**：main.cpp `ReadConfigFile` 是唯一直接消费者——`device_map nanoKONTROL2` 指令触发 `setControlSurfaceType`（main.cpp:509）；`button`/`knob`/`slider` 的通道参数 strtol 失败时走 `mapControl` 别名回退（main.cpp:534），拿到 `ControlSurface` 后做类型交叉校验：`button` 只认 Button（main.cpp:541）、`knob` 只认 RotaryKnob、`slider` 只认 Slider（main.cpp:587-588）。
- **下游**：无。别名只在解析期消费一次；运行期 `HandleMidiInput` 查的是 main.cpp 自己的数字键热表。**扩展点**：支持新控制器只需注册一张表进 `controlSurfaces`（control_surface_map.cpp:88），配置里 `device_map` 换名即可，主程序零改动。

## 数据流

解析期单向流：配置行 `button rewind xxx` → strtol 发现非整数（main.cpp:530）→ `mapControl(surf, "rewind")` 得 `{Button, 43}` → 类型校验通过 → `new_config.buttons[43] = "xxx"`。此后运行期 MIDI 事件带的控件号 43 直接命中热表，别名退场。

前置契约：`mapControl` 能工作的前提是激活指针已被 `setControlSurfaceType` 指向有效表——但代码不强制：函数开头直接 `controlSurfaceMap->find(...)`（control_surface_map.cpp:107），若配置没写 `device_map` 却用别名就是空指针解引用。

## 设计决策

- **数据与逻辑彻底分离**：51 项表纯声明式初始化，查询函数不含设备知识——新增设备的全部工作量是抄一张表。
- **注册表两级映射**（设备名→表→别名→控件）：为多设备预留的结构，解释了查询为何拆成两个函数而非一个带设备参数的调用。
- **std::map 而非 unordered_map**：表小且只在启动期查几次，有序可读性收益大于性能差异；main.cpp 侧运行期热表才用 unordered_map。

## 新人提示

- **数字口径勘误**：图谱与任务描述称 56 项，逐行清点实为 **51 项**；核数=表体 control_surface_map.cpp:35-85 每行一项，11+8+8+8+8+8。
- 别名表与 nanoKONTROL2 真机固件发出的 MIDI CC 号对应（滑条 0-7、旋钮 16-23、S/M/R 32-39/48-55/64-71、走带 41-46 与 58-62）；别名大小写敏感，`sl0`/`kn0` 小写前缀、S/M/R 大写。
- 加表项零风险，但删 `device_map` 行会让别名列变致命（空指针）；排查"配置好好的突然段错误"先查有没有 `device_map`。
- 该文件无平台宏，最适合作为第一个读的 .cpp。
