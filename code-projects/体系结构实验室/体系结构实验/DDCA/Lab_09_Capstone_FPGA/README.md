# Lab 09 — Capstone: FPGA 综合实战

> **一句话目标**：把 L06 流水线 MIPS + L07 Cache + L08 异常**综合到真实 FPGA 板**（Xilinx Nexys 4 DDR）——
> 用按钮控制 CPU，看七段显示输出。
> **这是 DDCA 的最终高潮**：你的代码在真实的硅片上跑。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | Harris & Harris **Ch1-A.9**（FPGA + Vivado 实战）|
| 🎥 Mutlu | [Lecture 21-22: FPGA](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| 🛠 工具 | **Vivado 2023+** + Nexys 4 DDR 板 |
| ⏱ 预计工时 | 20–40 小时 |

---

## 1. 你将做的事

| # | 任务 | 难度 |
|---|------|------|
| 1 | 把 L06 的 Verilog 移植到 Vivado | ⭐⭐ |
| 2 | 写 `.xdc` 约束文件（管脚映射）| ⭐⭐ |
| 3 | 综合 + 实现（Synthesis + Implementation）| ⭐⭐ |
| 4 | 生成比特流（.bit）| ⭐ |
| 5 | 烧到 FPGA 板 | ⭐ |
| 6 | 用按钮、开关、LED、七段显示调试 | ⭐⭐⭐ |

---

## 2. FPGA 基础知识

### 2.1 FPGA 是什么

FPGA（Field-Programmable Gate Array）= **可现场编程的硬件**：
- 你用 Verilog 描述电路
- 综合工具把 Verilog 转换为查找表（LUT）+ 触发器（FF）配置
- 烧到 FPGA 板上 → 真实的电路按你的描述工作

### 2.2 Nexys 4 DDR 板

最常用的教学板：

```
       ┌─────────────────────────────────────┐
       │                                     │
       │  ┌─────────────────────────────┐    │
       │  │                             │    │
       │  │     Artix-7 FPGA            │    │
       │  │     (XC7A100T-1CSG324C)     │    │
       │  │                             │    │
       │  └─────────────────────────────┘    │
       │                                     │
       │  [Switches x16]  [Buttons x5]      │
       │                                     │
       │  [LEDs x16]  [7-Segment x8]        │
       │                                     │
       │  [VGA] [USB-UART] [Microphone]     │
       │  [Accelerometer] [Temperature]     │
       │                                     │
       │  [100 MHz Clock]                   │
       │                                     │
       └─────────────────────────────────────┘
```

**关键资源**：
- 100 MHz 时钟（你需要 PLL 分频到合适频率）
- 16 个开关（输入数据）
- 5 个按钮（控制信号）
- 16 个 LED（状态输出）
- 8 个 7 段数码管（数据显示）

---

## 3. 完整流程

### 3.1 创建 Vivado 项目

```bash
# 在 Vivado 里：
1. File → New Project
2. 选 Nexys 4 DDR 板（或 xc7a100tcsg324-1 芯片）
3. 加入 L06 的所有 .v 文件
4. 加 mips_top_xilinx.v（顶层包装）
5. 加 nexys4.xdc（约束文件）
```

### 3.2 顶层模块（包装 L06）

```verilog
// mips_top_xilinx.v
module mips_top_xilinx (
    input         clk_100MHz,        // 板上 100MHz 时钟
    input         reset_btn,         // 中央按钮
    input  [15:0] switches,          // 输入数据
    input  [4:0]  buttons,
    output [15:0] leds,
    output [6:0]  seg,               // 七段（共阳）
    output [7:0]  an,                // 7 段位选
    output        dp                 // 小数点
);
    // 1. 时钟分频（100MHz → 50MHz，或更低便于观察）
    wire clk;
    clk_div #(.DIV(2)) clk_gen (
        .clk_in(clk_100MHz),
        .clk_out(clk)
    );

    // 2. CPU 实例
    wire [31:0] cpu_pc, cpu_alu_result;
    wire        cpu_mem_write;
    mips_top cpu (
        .clk(clk), .reset(reset_btn),
        .pc(cpu_pc), .alu_result(cpu_alu_result),
        .instr(), .mem_write(cpu_mem_write)
    );

    // 3. 输出：PC 低 16 位显示到 LED + 7 段
    assign leds = cpu_pc[15:0];

    // 4. 7 段显示 ALU 结果
    mmio_segment seg_driver (
        .clk(clk),
        .addr(32'hFFFF0000),
        .write_data(cpu_alu_result),
        .write_en(1'b1),   // 持续显示
        .cs(),
        .seg(seg),
        .an(an)
    );

    assign dp = 1'b1;   // 共阳，1 = 灭
endmodule
```

### 3.3 `.xdc` 约束文件

```tcl
# nexys4.xdc（节选）

# 时钟
set_property -dict { PACKAGE_PIN E3    IOSTANDARD LVCMOS33 } [get_ports clk_100MHz]
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports clk_100MHz]

# 按钮（reset）
set_property -dict { PACKAGE_PIN C12   IOSTANDARD LVCMOS33 } [get_ports reset_btn]

# 16 个开关
set_property -dict { PACKAGE_PIN J15   IOSTANDARD LVCMOS33 } [get_ports {switches[0]}]
set_property -dict { PACKAGE_PIN L16   IOSTANDARD LVCMOS33 } [get_ports {switches[1]}]
# ... 16 行 ...

# 16 个 LED
set_property -dict { PACKAGE_PIN H17   IOSTANDARD LVCMOS33 } [get_ports {leds[0]}]
# ... 16 行 ...

# 7 段数码管（8 个数字）
set_property -dict { PACKAGE_PIN T10   IOSTANDARD LVCMOS33 } [get_ports {seg[0]}]
# ... 7 行 ...

set_property -dict { PACKAGE_PIN J17   IOSTANDARD LVCMOS33 } [get_ports {an[0]}]
# ... 8 行 ...
```

### 3.4 综合 + 实现 + 比特流

```tcl
# Vivado Tcl Console:
synth_design -top mips_top_xilinx -part xc7a100tcsg324-1
opt_design
place_design
route_design
write_bitstream -force mips_top.bit
```

或在 GUI 里点 "Generate Bitstream"。

### 3.5 烧到板

1. USB 连接 Nexys 4
2. 板上电源开关拨到 ON
3. Vivado → Open Hardware Manager → Open Target → Auto Connect
4. Program Device → 选 `mips_top.bit`
5. **看着 LED 闪烁 PC，七段显示 ALU 结果**

---

## 4. 调试技巧

### 4.1 综合失败

**常见错误**：
- 引脚没在 xdc 里映射
- 时钟约束错（关键路径过不了 50MHz）
- 位宽不匹配

**调试**：看 Vivado 的 Synthesis 报告 + Implementation 时序报告。

### 4.2 烧上去不工作

**调试神器：ila（Integrated Logic Analyzer）**——
Vivado 内置逻辑分析仪，可以在板子上抓波形：

```verilog
// 加到顶层
ila_0 your_ila (
    .clk(clk),
    .probe0(cpu_pc),         // 32 bit
    .probe1(cpu_alu_result)  // 32 bit
);
```

→ 在 Hardware Manager 里实时抓波形，**就像 GTKWave 但在真实硬件上**。

### 4.3 按键消抖

按钮按下会产生 ~10ms 的抖动，需要去抖：

```verilog
module debouncer (
    input  clk, noisy_btn,
    output clean_btn
);
    reg [19:0] counter;
    reg        sync1, sync2;

    always @(posedge clk) begin
        sync1 <= noisy_btn;
        sync2 <= sync1;
    end

    always @(posedge clk) begin
        if (sync2 != noisy_btn) counter <= 0;
        else if (counter < 20'hFFFFF) counter <= counter + 1;
    end

    assign clean_btn = (counter == 20'hFFFFF) ? sync2 : clean_btn;
endmodule
```

---

## 5. 实战项目

### 5.1 用 CPU 控制 LED 流水灯

```mips
# 在 RAM 里跑
main:
    li   $t0, 1
loop:
    sw   $t0, 0xFFFF0010($zero)   # MMIO 写 LED
    sll  $t0, $t0, 1              # 左移 1 位
    beq  $t0, $zero, reset        # 8 位都跑完
    j    loop
reset:
    li   $t0, 1
    j    loop
```

**期望**：LED 1, 2, 4, 8, ... 流水闪烁。

### 5.2 用七段显示秒表计数

每秒 +1，从 0000 计数到 9999，循环。

### 5.3 终极：跑 Pong 游戏

VGA 输出 + 按钮控制球拍——这是 capstone 的目标。

---

## 6. 常见坑

### 坑 1：时钟约束没写

```tcl
# ❌ 没有 create_clock → Vivado 不知道时钟频率
# ✅ 必须显式约束
create_clock -period 10.00 [get_ports clk]
```

→ 不写时钟约束，Vivado 假设任意频率，时序会假通过，**但烧上去不工作**。

### 坑 2：组合逻辑环路

```verilog
assign a = b;
assign b = a;   // ❌ 无限循环！
```

→ 综合工具会报 "combinational loop"，**必须解决**。

### 坑 3：未初始化的 reg

```verilog
reg [31:0] data;
always @(posedge clk) ...   // data 没初值，烧上去是 X
```

→ FPGA 上电后 reg 是 0（不像仿真），但**最好显式 reset**。

### 坑 4：PLL 没生成

如果需要 200MHz 时钟（PLL），必须用 Vivado 的 IP Catalog 生成 Clocking Wizard。

### 坑 5：板子电源/端口没接好

- USB 线必须能传数据（不是只能充电）
- 板上 jumper J6 在 JTAG 模式

---

## 7. 与本项目其他模块的连接

### 7.1 与 [`Expert_03_HW_Designer`](../../Expert_03_HW_DesignER/) 的连接

L09 完成后，你**已经具备 FPGA 工程师能力**——
可以开始读 [`Expert_03/rtl/`](../../Expert_03_HW_DesignER/rtl/) 的 Verilog，并自己实现更复杂的设计。

### 7.2 与 [`Expert_13_VLSI_Physical`](../../Expert_13_VLSI_Physical/) 的连接

L09 是 **FPGA**——可编程的硬件。
真实 CPU（飞腾）是 **ASIC**——一次性烧录的固定电路。

ASIC 流程：
- Verilog → 逻辑综合 → 门级网表 → 布局布线 → GDSII → 流片 → 硅片

FPGA 是 ASIC 的"预演"——让你在烧 ASIC 之前先在可编程硬件上验证设计。

### 7.3 与 [`Expert_14_Process_Manufacturing`](../../Expert_14_Process_Manufacturing/) 的连接

FPGA 用 **28nm 工艺**（Nexys 4 Artix-7），飞腾用 **14nm**。
FPGA 的等价"门数"远低于同尺寸 ASIC，但**可重编程**是巨大优势。

→ 学完 L09 你会理解：为什么工业级芯片（飞腾、Apple）选择 ASIC 而不是 FPGA。

---

## 8. 扩展挑战

1. **加 VGA 输出**：让 CPU 在显示器上画图
2. **加 UART 接收**：从电脑发数据给 CPU
3. **加 Audio 输出**：CPU 控制 PWM 播放音乐
4. **加 SRAM 接口**：把数据存到板上的外部 SRAM
5. **多核**：在 FPGA 上放 2 个 MIPS CPU + 共享 Cache（极难）
6. **RISC-V**：把 L05/L06 的 MIPS 改为 RV32I（与 [`Capstone`](../../Capstone/cpu_simulator/) 同 ISA）

---

## 9. 检查清单

- [ ] Vivado 项目能综合 + 实现 + 生成比特流
- [ ] 烧到板后 LED 显示 PC 计数（CPU 在跑）
- [ ] 七段显示 ALU 结果
- [ ] 按钮能控制 CPU（如 reset）
- [ ] 至少跑 1 个真实小程序（如流水灯）
- [ ] 用 ila 调试过至少 1 个 bug

---

## 📌 下一步

🎉🎉🎉 **完成 L09 后，你已完成整个 DDCA 课程！**

你拥有的：
- 一台自己设计的 MIPS CPU（L05-L08）
- 在真实 FPGA 板上跑（L09）
- 流水线 + Cache + 异常（工业级特性）

### 后续路径

1. **回到本项目 Lab**：用 perf 观测飞腾真机——你会**真切感受到**工业 CPU 比你的 MIPS 复杂 50 倍
2. **Capstone**：用 Python 实现 RV32I 流水线（与 L06 思想一致，软件视角）
3. **L01-L09 复盘**：把 DDCA 学到的概念总结成博客或 GitHub repo
4. **进阶课程**：
   - [`Expert_02`](../../Expert_02_Architect/) 工业级 CPU 架构
   - [`Expert_03`](../../Expert_03_HW_DesignER/) Verilog 工程实战
   - [`Expert_13`](../../Expert_13_VLSI_Physical/) VLSI 物理设计
5. **挑战研究**：从 MIPS 改写一个 RISC-V CPU（参考 [`Capstone/cpu_simulator`](../../Capstone/cpu_simulator/)）

> 💡 Onur Mutlu 在课程最后说："现在你已经懂计算机是怎么工作的——
> 接下来去做一些**没人做过的东西**。"

DDCA 完成，是研究的起点，不是终点。
