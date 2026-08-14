# CS241: Embedded Systems Workshop

> Stanford University | 本科课程 | 嵌入式系统实战工坊
> Instructor: **Philip Levis**（TinyOS 作者，传感器网络先驱）
> 先修: CS107（系统基础）+ 基础电路知识
> 难度: ⭐⭐⭐⭐
> 定位: 传感器 / IoT / RTOS，软硬结合的嵌入式全栈

---

## 📚 课程定位

CS241 是 Stanford **嵌入式系统实战工坊**，由 **Philip Levis** 教授主讲。Levis 是 **TinyOS**（无线传感器网络操作系统）的核心作者，在低功耗嵌入式系统领域享有盛誉。课程以**项目驱动**，让学生亲手搭建传感器节点、写固件、处理中断、跑 RTOS，理解"代码如何与物理世界交互"。

### Philip Levis 教授
- Stanford CS 教授，研究方向：无线传感器网络、低功耗系统、网络协议
- 代表作：**TinyOS**（组件化嵌入式 OS）、nesC 语言、网络协议栈设计
- 教学风格：强调系统思维与动手实践

---

## 🎯 学习目标

1. 理解嵌入式系统的**硬件抽象**（GPIO / ADC / 中断 / 定时器）
2. 掌握**中断驱动**与**轮询**两种 I/O 范式
3. 学习 **RTOS**（实时操作系统）的任务调度与资源管理
4. 构建完整的**传感器采集 → 处理 → 通信** pipeline
5. 处理低功耗、实时性、可靠性等嵌入式核心约束

---

## 📅 核心模块

### Part 1: 嵌入式硬件基础
- 微控制器架构（ARM Cortex-M / ESP32 / Arduino）
- **GPIO**：数字输入输出
- **ADC**：模拟信号采样（温度 / 光照 / 加速度）
- **中断**：硬件中断 vs 软件中断

### Part 2: 固件开发
- 裸机编程（bare-metal）vs RTOS
- 中断服务程序（ISR）设计
- 状态机驱动的固件架构

### Part 3: 实时操作系统（RTOS）
- FreeRTOS / Zephyr / TinyOS
- 任务调度（优先级抢占 / 时间片）
- 信号量 / 互斥锁 / 消息队列
- 实时性保证（deadline / 抖动）

### Part 4: 通信协议
- **有线**: I2C / SPI / UART
- **无线**: BLE / WiFi / LoRa / Zigbee
- 物联网协议：MQTT / CoAP

### Part 5: IoT 与系统集成
- 传感器网络拓扑
- 边缘计算（edge inference）
- 低功耗设计（sleep / duty cycling）

---

## 💻 项目代码

📁 `supplementary/undergrad_projects.py::cs241_demo()`

实现了嵌入式传感器系统的核心模式：**传感器采样 + 中断驱动**：
- 模拟温度传感器（带噪声 + 偶发尖峰）
- **中断处理函数**：温度超阈值触发 alert
- 20s 采样统计（均值 + alert 次数）

**运行**：
```bash
cd supplementary && python3 -c "from undergrad_projects import cs241_demo; cs241_demo()"
```

**输出示例**：温度超阈值触发 `⚠️ High temp` 中断 alert，20s 统计 `avg=20.4°C, alerts=2`；关键概念 GPIO / ADC / 中断 / RTOS / 低功耗。

---

## 📊 关键概念/资源

### 🔴 必读 P0
1. **Levis et al.** "TinyOS: An Operating System for Sensor Networks"
2. **FreeRTOS 官方文档** — 最广泛使用的 RTOS
3. **ARM Cortex-M 编程手册**

### 🟡 P1
4. **Zephyr RTOS 文档** — 新一代 IoT RTOS
5. **ESP32 官方 SDK**（ESP-IDF）
6. *Making Embedded Systems*（Elecia White）— 工程实践

### 核心概念
- **中断延迟（Interrupt Latency）**：从硬件触发到 ISR 执行的时间
- **Duty Cycling**：周期性休眠以省电
- **优先级反转（Priority Inversion）**：RTOS 经典陷阱

---

## 🎯 适用人群

- **IoT / 嵌入式工程师**: CS241 是核心训练
- **机器人硬件**: CS241 → CS123（Pupper 固件）
- **边缘 AI**: 把 ML 部署到微控制器（TinyML）
- **低功耗系统研究**: 读 TinyOS / 传感器网络论文

---

## 🚀 扩展

完成后推荐：
1. **CS140** — Operating Systems（对比 RTOS 与通用 OS）
2. **CS123** — Building AI-Enabled Robots（Pupper 嵌入式固件）
3. **EE149** — Introduction to Embedded Systems（更偏电路）
4. TinyML：TensorFlow Lite Micro / Edge Impulse（微控制器上的 ML）
5. 实习：Apple（嵌入式）/ Tesla（车载）/ Nest / IoT 初创

---

**对应代码**: `supplementary/undergrad_projects.py::cs241_demo()`
