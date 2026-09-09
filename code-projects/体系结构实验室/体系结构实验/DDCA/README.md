# ETH Zurich DDCA：用 Verilog 从零造一台 MIPS CPU

> **一句话定位**：Onur Mutlu 主讲的 ETH Zurich **Digital Design and Computer Architecture**，
> 配合 **Harris & Harris《Digital Design and Computer Architecture (MIPS Edition)》**，
> 用 **工业标准 Verilog** + **MIPS ISA** + **真实 FPGA 综合**——
> 9 个 lab 从门电路一路造到流水线 MIPS CPU。
>
> **这是 Nand2Tetris 的工业级进阶**——同样的"从零造 CPU"理念，但用真正的硬件描述语言、真正的 ISA、能烧到真正的 FPGA 板上。

---

## 0. 本目录在项目中的位置

本项目现在拥有 **4 个互补的"造 CPU"路径**：

| 路径 | 工具链 | ISA | 难度 | 真实度 |
|------|--------|-----|------|--------|
| [`Nand2Tetris/`](../Nand2Tetris/) | 自定义 HDL + Python 工具 | Hack（教学专用）| ⭐⭐ | 仿真 |
| **本目录（DDCA）** | **Verilog + Vivado/iverilog + FPGA** | **MIPS**（研究/工业经典）| **⭐⭐⭐** | **可综合到真实 FPGA** |
| [`Capstone/cpu_simulator`](../Capstone/cpu_simulator/) | Python | RV32I（RISC-V）| ⭐⭐⭐⭐ | 软件模拟 |
| [`Lab00`–`Lab07`](../Lab00_测量基础设施/) | C + perf + PMU | ARMv8-A（飞腾）| ⭐⭐⭐⭐⭐ | 真实工业硅片 |

**四层抽象梯度**：

```
                  想象力  ←────────────→  现实
   ───────────────────────────────────────────────────→
   Nand2Tetris  →  DDCA  →  Capstone  →  Lab（飞腾真机）
   (Hack CPU)     (MIPS)   (RV32I)      (ARMv8-A)
   
   教学级 ──────────────────────────────── 工业级
   能仿真即可      能综合到 FPGA    能模拟流水线    能用 perf 实测
```

### 与 Nand2Tetris 的核心差别

| 维度 | Nand2Tetris | DDCA（本目录）|
|------|-------------|---------------|
| HDL | **自定义**（仅 1 种原语 Nand）| **Verilog**（IEEE 1364-2005 标准）|
| 模拟器 | HardwareSimulator（Java）| iverilog / ModelSim / Vivado |
| 综合 | ❌ 不能综合 | ✅ 可烧到 FPGA 板 |
| ISA | Hack（4 种指令格式，教学专用）| **MIPS**（RISC 鼻祖之一）|
| 数据通路宽度 | 16 位 | 32 位 |
| 流水线 | 无（单周期）| **5 级流水 + 冒险检测 + 前递** |
| Cache | 无 | Lab 07 实现直接映射 Cache |
| 异常处理 | 无 | Lab 08 实现 syscall/overflow/IRQ |
| FPGA 板 | 不需要 | Lab 09 烧到 Xilinx Nexys 4 |
| 工程量 | ~200 小时 | ~400–600 小时 |

→ **DDCA 是 Nand2Tetris 的"现实版"**：用 Verilog 替代教学 HDL、用 MIPS 替代 Hack、用真实 FPGA 替代纯仿真。

---

## 1. 关于这门课

### 1.1 课程信息

| 项 | 内容 |
|----|------|
| **课程名** | Digital Design and Computer Architecture（DDCA, 227-0014-00L）|
| **学校** | ETH Zurich, Department of Information Technology and Electrical Engineering |
| **主讲** | [Prof. Onur Mutlu](https://people.inf.ethz.ch/omutlu/)（同是 SAFARI 研究组组长、前卡内基梅隆教授）|
| **教材** | *Digital Design and Computer Architecture* by David Harris & Sarah Harris（**MIPS Edition**）|
| **课程网站** | [safari.ethz.ch/ddca](https://safari.ethz.ch/digital_design_and_computer_architecture/)|
| **视频讲座** | [YouTube: Onur Mutlu's DDCA Lectures](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| **难度** | 本科 3 年级 / 研究生入门级 |
| **前置** | 数字电路基础（推荐但非必需）|

### 1.2 为什么这门课值得学

Onur Mutlu 是计算机体系结构领域顶级研究者（Google Scholar 引用 6 万+），他的版本比原版 Harris 增加了：

- ✅ **更深的数字电路基础**（CMOS、时序约束、亚稳态）
- ✅ **更现代的视角**（DRAM main memory 章节是 Mutlu 的研究强项）
- ✅ **前沿研究讨论**（Rowhammer、Spectre 简介、compute in memory）
- ✅ **完整的 Verilog 工程实践**（不是 toy example）
- ✅ **真实 FPGA 板**（Xilinx Nexys 4 / Basys 3）

→ 学完 DDCA 你**直接具备初级硬件工程师的能力**——这不是 Nand2Tetris 能给你的。

### 1.3 Harris & Harris 书的特点

| 特点 | 说明 |
|------|------|
| **MIPS Edition vs ARM Edition** | 本书有两个版本。ETH 用 MIPS 版（更适合学指令集原理）；ARM 版更接近现代手机 CPU |
| **Verilog vs VHDL** | 同一内容有两个 HDL 版本。ETH 用 **Verilog** 版（更接近工业实践，与 Synopsys/Cadence 工具兼容）|
| **章节结构** | 9 章，前 3 章组合/时序逻辑、4 章 Verilog、5 章构建块、6 章 MIPS ISA、7 章微架构（单周期 + 流水线）、8 章存储、9 章 I/O |

### 1.4 Onur Mutlu 风格

Mutlu 的讲座有三个独特风格：

1. **质疑精神**：每讲一个设计都问"为什么不这样设计？"——形成批判性直觉
2. **历史脉络**：从 IBM 360 → MIPS → x86 → ARM → RISC-V，让学生看到 ISA 的演化逻辑
3. **前沿锚定**：每周都引用近期 ISCA/MICRO/HPCA 论文，让学生感受到"今天学的概念就是工业正在研究的"

---

## 2. 9 个 Lab 总览（一张图）

```
   ┌────────── Lab 1-4：数字电路基础（Harris Ch1-5）──────────┐
   │                                                          │
   │  L01        L02         L03         L04                  │
   │ Verilog  → 组合电路  →  ALU    →  时序电路                 │
   │ 入门       7段显示     加法器      Reg/Counter             │
   │ iverilog  truth→gate  RCA/CLA    FSM                     │
   │ GTKWave   multiplex   shift       状态机                  │
   │                                                          │
   └──────────────────────────────────────────────────────────┘
                                ↓
   ┌────────── Lab 5-6：MIPS CPU 设计（Harris Ch6-7）──────────┐
   │                                                          │
   │         L05 单周期 MIPS            L06 流水线 MIPS         │
   │         ──────────────             ──────────────         │
   │         MIPS ISA 32 条指令         5 级 IF/ID/EX/MEM/WB   │
   │         datapath + control         hazard detection        │
   │         机器码 → 内存 → 跑          forwarding             │
   │         IPC ≤ 1                    load-use stall         │
   │                                  分支预测初探              │
   │                                                          │
   └──────────────────────────────────────────────────────────┘
                                ↓
   ┌────────── Lab 7-9：完整计算机（Harris Ch8-9）──────────────┐
   │                                                          │
   │  L07 Cache       L08 异常/中断    L09 FPGA 综合             │
   │  直接映射        syscall/IRQ      Nexys 4 DDR              │
   │  write-through   overflow 处理    烧到真实芯片              │
   │  hit/miss        vec table        七段显示 + 按钮           │
   │                                                          │
   └──────────────────────────────────────────────────────────┘
```

### 2.1 全表：9 个 Lab 一览

| # | Lab 名称 | 你将构建 | 主要工具 | 预计工时 |
|---|---------|---------|---------|---------|
| **L01** | [Verilog Basics](./Lab_01_Verilog_Basics/) | 4 个简单模块（mux/decoder/full-adder/dff）+ testbench | iverilog + GTKWave | 8–12h |
| **L02** | [Combinational Logic](./Lab_02_Combinational/) | 7 段数码管译码器 + ALU 前置 | iverilog | 10–15h |
| **L03** | [ALU](./Lab_03_ALU/) | **MIPS ALU**（add/sub/and/or/slt/shifter）| iverilog + 自检 testbench | 12–18h |
| **L04** | [Sequential Logic](./Lab_04_Sequential/) | 寄存器 + 计数器 + FSM（红绿灯）| iverilog + 时序仿真 | 10–15h |
| **L05** | [Single-Cycle MIPS](./Lab_05_SingleCycle_MIPS/) | **单周期 MIPS CPU**（32 条指令完整实现）| iverilog + 汇编器 | 30–50h |
| **L06** | [Pipelined MIPS](./Lab_06_Pipelined_MIPS/) | **5 级流水线 MIPS** + forwarding + hazard | iverilog + 复杂 testbench | 40–60h |
| **L07** | [Memory & I/O](./Lab_07_Memory_IO/) | 直接映射 Cache + 简单 I/O | iverilog + 内存模型 | 15–25h |
| **L08** | [Exceptions & Interrupts](./Lab_08_Exceptions/) | 在 L06 基础上加 syscall/IRQ/overflow | iverilog + 异常 testbench | 15–20h |
| **L09** | [FPGA Capstone](./Lab_09_Capstone_FPGA/) | 把 L06 烧到 Nexys 4 DDR | **Vivado** + FPGA 板 | 20–40h |

**总工时**：业余时间 12–18 个月；全职 6–9 个月。

---

## 3. DDCA 与本项目其他模块的交叉映射

> 这是把 DDCA 融入项目的核心价值——每个 lab 都能在 Lab00-Lab07 / Nand2Tetris / Capstone / Expert 里找到**理论对照**。

| DDCA Lab | 知识点 | Nand2Tetris 对应 | Lab 真机观测 | Capstone / Expert |
|----------|--------|------------------|-------------|-------------------|
| L01 Verilog | 组合电路 + Verilog 语法 | [`P01`](../Nand2Tetris/Project_01_BooleanLogic/) | — | [`Expert_03/rtl/`](../Expert_03_HW_Designer/rtl/) |
| L02 组合 | 数码管 + 译码器 | [`P01 Mux/DMux`](../Nand2Tetris/Project_01_BooleanLogic/) | — | — |
| L03 ALU | MIPS ALU（add/sub/slt）| [`P02 Hack ALU`](../Nand2Tetris/Project_02_BooleanArithmetic/) | [`Lab01 §3.4`](../Lab01_ISA与汇编/)（实测 ALU 延迟）| [`Expert_03/rtl/alu.v`](../Expert_03_HW_Designer/rtl/) |
| L04 时序 | Reg/Counter/FSM | [`P03 时序`](../Nand2Tetris/Project_03_SequentialLogic/) | — | [`Expert_03/rtl/two_bit_predictor.v`](../Expert_03_HW_Designer/rtl/) |
| L05 单周期 MIPS | **datapath + control** | [`P05 Computer.hdl`](../Nand2Tetris/Project_05_ComputerArchitecture/) | [`Lab02`](../Lab02_流水线与ILP/)（流水线对照）| [`Capstone/cpu_simulator`](../Capstone/cpu_simulator/)（Python 版）|
| L06 流水线 MIPS | **5 级 + 冒险 + 前递** | —（Nand2Tetris 不做流水线）| [`Lab02`](../Lab02_流水线与ILP/) + [`Lab04`](../Lab04_超标量乱序/) | [`Capstone/rv32i_sim.py`](../Capstone/cpu_simulator/) + [`Expert_03/forwarding_unit.v`](../Expert_03_HW_Designer/rtl/) |
| L07 Memory/IO | Cache + 直接映射 | —（Nand2Tetris 无 Cache）| [`Lab03`](../Lab03_存储层次/)（实测 L1/L2/L3）| — |
| L08 异常 | syscall / IRQ / overflow | —（Hack 无异常）| [`Expert_04_OS_Kernel`](../Expert_04_OS_Kernel/)（syscall 延迟）| — |
| L09 FPGA | 综合到 Nexys 4 | —（Nand2Tetris 不综合）| — | [`Expert_13_VLSI_Physical`](../Expert_13_VLSI_Physical/)（真实硅片流程）|

**记忆口诀**：

> **Nand2Tetris 给你直觉，DDCA 给你工程能力，Lab 给你真机观测，Capstone 给你研究深度——四个角度不重复。**

---

## 4. MIPS vs Hack vs RV32I vs ARM64 四 ISA 对照

| 特性 | Hack（Nand2Tetris）| **MIPS（DDCA）** | RV32I（Capstone）| ARM64（飞腾）|
|------|---------------------|------------------|------------------|---------------|
| 设计目的 | 教学（极简）| **研究/教学经典** | 研究/工业入门 | 工业生产 |
| 指令长度 | 16 位固定 | 32 位固定 | 32 位固定 | 32 位固定 |
| 寄存器数 | 2（A, D）+ M 别名 | **32 个通用 + HI/LO** | 31 个 | 31 个 |
| 指令数（基础）| 4 种格式 | **~70 条（MIPS-1）** | 37 | ~1000（含 NEON/SVE）|
| 流水线 | 单周期 | 5 级 | 5 级 | 15+ 级 OoO |
| 寻址模式 | 1 种（间接）| 3 种（R/I/J）| imm/reg | imm/reg/shift/offset |
| 条件码 | zr/ng | **无（用 BEQ/BNE + SLT）** | 无 | NZCV |
| 乘除 | 软件 | **硬件（HI/LO 寄存器）** | 硬件 | 硬件 |
| 字长 | 16 位 | **32 位** | 32 位 | 64 位 |
| 典型应用 | Nand2Tetris 教学 | **早期工作站（SGI, Sony PS1）** | 嵌入式 / IoT | 手机 / 服务器 |

### 4.1 MIPS 的历史地位

MIPS（**M**illions of Instructions Per Second）由 John Hennessy 于 1981 年在 Stanford 创建：

- 1985 MIPS Computer Systems 商业化
- 1980s-90s **工作站主流**（SGI、Silicon Graphics）
- 1994 **Sony PlayStation 1** 用 MIPS R3000A（童年的 MIPS 经典案例）
- 2000s 让位给 x86 / ARM
- 2018 后又复苏（嵌入式、IoT、网络设备）
- 2021 Wave Computing 推动 MIPS Open

**Hennessy + Patterson 的代表作《Computer Architecture: A Quantitative Approach》就是用 MIPS 作教学 ISA**——MIPS 是 RISC 设计的"参考实现"。

→ 学懂 MIPS = 学懂 RISC 设计哲学。

### 4.2 MIPS 对后续 ISA 的影响

```
1981 MIPS (Stanford)
   │
   ├── 1987 SPARC (Sun)        ← 类似 RISC
   ├── 1990 ARMv1 (Acorn)      ← 借鉴 RISC 思想
   ├── 1996 PowerPC            ← 同为 RISC
   └── 2010 RISC-V             ← 直接继承 MIPS/SPARC/ARM 经验
```

**ARM 的 RISC 根基来自 MIPS**——所以学 MIPS 后看 ARM64 会觉得"思路一样，细节不同"。

---

## 5. 工具链

### 5.1 模拟器（开源，免费）

| 工具 | 用途 | 平台 | 安装 |
|------|------|------|------|
| **Icarus Verilog (iverilog)** | Verilog 编译 + 仿真 | Linux/Mac/Win | `apt install iverilog` / `brew install icarus-verilog` |
| **GTKWave** | 波形查看器 | 同上 | `apt install gtkwave` |
| **Verilator** | C++ + Verilog 协同仿真 | 同上 | `apt install verilator`（可选，更快的现代替代）|
| **Yosys** | 开源综合工具 | 同上 | `apt install yosys`（L09 综合 + 比特流）|

**最简组合**：`iverilog + GTKWave` 就能跑 L01-L08 的所有 lab。

### 5.2 商业工具（学校常有 license）

| 工具 | 公司 | 用途 | 学校获取 |
|------|------|------|---------|
| **ModelSim / QuestaSim** | Siemens EDA | 行业标准仿真 | ETH 课程提供 |
| **Vivado** | AMD/Xilinx | FPGA 综合 + 烧录 | 学校 Vivado License |
| **Quartus Prime** | Intel/Altera | FPGA 综合（如用 Altera 板）| 免费版可用 |
| **VCS** | Synopsys | 大规模 IC 验证 | 公司/学校 license |

### 5.3 FPGA 开发板

| 板 | 芯片 | 推荐 |
|----|------|------|
| **Digilent Nexys 4 DDR** | Xilinx Artix-7 | **ETH 推荐**，最全外设（七段、按钮、LED、VGA、麦克风、加速度计）|
| Digilent Basys 3 | Xilinx Artix-7 | 入门版，便宜 |
| DE10-Lite | Intel MAX 10 | Intel 平台替代 |
| Tang Primer 20K | Anlogic EG20 | 国产开源，便宜 |

> 💡 **无板也可学**：L01-L08 完全可以在仿真器里跑，**L09 才需要 FPGA 板**。
> 如果你只想学概念不烧板，可以跳过 L09，或者用开源工具 Verilator + Yosys 做云综合。

### 5.4 与本项目工具链的对照

| 工具 | 仿真层级 | 项目里对应工具 |
|------|---------|---------------|
| iverilog | L1-L2（RTL 仿真）| [`Expert_03/rtl/`](../Expert_03_HW_Designer/rtl/) 同源 |
| Vivado | L1-L2（可综合）| —（本项目不涉及 FPGA 综合）|
| iverilog + Verilator | L1-L2（高速仿真）| [`Capstone/cpu_simulator`](../Capstone/cpu_simulator/)（Python）|
| nand2tetris HardwareSimulator | L1-L2（教学仿真）| [`Nand2Tetris`](../Nand2Tetris/) |
| **飞腾真机 + perf** | L1-L5 全部 | [`Lab00-Lab07`](../) |

---

## 6. 学习路径（不同读者的入口）

### 🌱 路径 A：零硬件基础（推荐先做 Nand2Tetris 再来）

```
Nand2Tetris P01-P05（5–8 个月）
    ↓
DDCA L01-L04（2–3 个月，建立 Verilog 直觉）
    ↓
DDCA L05 单周期 MIPS（1–2 个月，最关键）
    ↓
DDCA L06 流水线 MIPS（2–3 个月，最复杂）
    ↓
本项目 Lab02 / Lab04（2–3 个月，看真机流水线）
    ↓
本项目 Capstone（1–2 个月，写 RV32I 模拟器）
```

**总耗时**：业余 2 年。

### 🎓 路径 B：已会 Nand2Tetris，想升级到 Verilog

直接进 DDCA L01（2 周上手 Verilog）→ L02-L04（复习 + Verilog 化）→ L05-L06（高潮）。

**总耗时**：6–9 个月。

### 🛠 路径 C：已懂电路，想学 MIPS 设计

跳过 L01-L04（Verilog 1 周速成即可）→ 直接进 L05（单周期 MIPS）→ L06（流水线）。

**总耗时**：4–6 个月。

### 🏭 路径 D：硬件工程师，想做研究

直接读 Harris & Harris Ch7 + L06 流水线 MIPS → 然后跳到本项目 [`Lab04`](../Lab04_超标量乱序/) 学乱序 + [`Capstone`](../Capstone/cpu_simulator/)。

**总耗时**：3–4 个月。

### 🔬 路径 E：Mutlu 迷弟/迷妹（研究生向）

完整跑 Mutlu 的讲座视频（60h+）+ 全部 9 个 lab + 期末考试题。

**总耗时**：9–12 个月全职。

---

## 7. 与"思想母题"的连接

每个 DDCA Lab 都对应 [`Great_Ideas_体系结构思想.md`](../背景知识/Great_Ideas_体系结构思想.md) 的若干条母题：

| DDCA Lab | 对应的 Great Idea |
|----------|------------------|
| L01 Verilog | **抽象**（用 HDL 描述电路）|
| L02 组合 | **抽象** + **接口**（模块化设计）|
| L03 ALU | **抽象**（运算的统一）|
| L04 时序 | **依赖前态**（状态机）+ **可靠性**（亚稳态规避）|
| L05 单周期 MIPS | **接口**（ISA = 软硬件契约）+ **预测**（PC 自增）|
| L06 流水线 MIPS | **流水线**（吞吐量优化）+ **并行**（指令级并行）|
| L07 Cache | **局部性**（空间/时间）+ **存储层次** |
| L08 异常 | **可靠性**（异常处理）+ **抽象**（OS 层）|
| L09 FPGA 综合 | **抽象**（HDL → 比特流）|

→ **DDCA 是 Great Ideas 在工程实践中的体现**。

---

## 8. 与"分层模型"的连接

[`处理器分层模型.md`](../背景知识/处理器分层模型.md) 定义了 5 层抽象栈：

| 层 | DDCA 覆盖了哪一层？ |
|----|---------------------|
| L5 应用 | ❌（DDCA 不写应用）|
| L4 OS + ABI | △（L08 触及异常/syscall）|
| L3 ISA | ✅ **L05-L06 实现完整 MIPS ISA** |
| L2 微架构 | ✅ **L06 实现 5 级流水 + 前递** |
| L1 物理实现 | ✅ **L09 综合到真实 FPGA** |

**DDCA 是 4 个路径中唯一覆盖 L1 物理实现的**——这是它独有的价值。
Nand2Tetris 只到 L2 仿真，Capstone 只到 L2/L3 模拟，Lab 只到 L5 观测。

---

## 9. 本目录的结构

```
DDCA/
├── README.md                          ← 本文（主入口）
├── Lab_01_Verilog_Basics/             ← Verilog 入门
│   ├── README.md
│   ├── rtl/                           ← Verilog 源码（你写）
│   └── tb/                            ← testbench（自检）
├── Lab_02_Combinational/              ← 组合电路
├── Lab_03_ALU/                        ← MIPS ALU
├── Lab_04_Sequential/                 ← 时序电路
├── Lab_05_SingleCycle_MIPS/           ← 单周期 MIPS CPU（高潮 1）
│   ├── rtl/
│   ├── tb/
│   └── sw/                            ← 测试用 MIPS 汇编程序
├── Lab_06_Pipelined_MIPS/             ← 流水线 MIPS（高潮 2）
├── Lab_07_Memory_IO/                  ← Cache + I/O
├── Lab_08_Exceptions/                 ← 异常/中断
├── Lab_09_Capstone_FPGA/              ← FPGA 综合实战
│   ├── rtl/
│   └── constraints/                   ← .xdc 约束文件
├── tools/                             ← 工具链使用指南
└── bibliography/                      ← 延伸阅读
```

每个 `Lab_XX/README.md` 都按统一结构：

1. 一句话目标
2. 对应 Harris & Harris 章节与 Mutlu 讲座
3. 你将构建的模块
4. 关键概念（理论速览）
5. Verilog 骨架代码（核心 lab 提供）
6. 测试方案（testbench + 期望波形）
7. 常见坑（语法 + 综合）
8. 与本项目其他模块的连接
9. 扩展挑战
10. 检查清单

---

## 10. 参考文献

| 编号 | 文献 | 说明 |
|------|------|------|
| 📘 | **Harris, D. & Harris, S.** *Digital Design and Computer Architecture (MIPS Edition)* 2nd ed. Elsevier, 2015 | 本课程指定教材 `[官方]` |
| 📙 | 同上中译本 | 《数字设计和计算机体系结构》|
| 🌐 | [ETH DDCA 课程主页](https://safari.ethz.ch/digital_design_and_computer_architecture/) | Mutlu 课程网站 |
| 🎥 | [DDCA Lectures YouTube](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) | Mutlu 全部讲座视频 |
| 🎓 | [Onur Mutlu's SAFARI Group](https://safari.ethz.ch/) | Mutlu 研究组（含讲义、论文）|
| 📰 | Hennessy & Patterson, *CAQA* 5th ed. | 进阶读物（项目 [`Expert_02`](../Expert_02_Architect/) 用）|
| 📰 | Patterson & Hennessy, *Computer Organization and Design: The Hardware/Software Interface (MIPS Edition)* | 与 Harris 风格不同，但 MIPS Edition 经典 |
| 📰 | *MIPS Architecture for Programmers Volume II-A: The MIPS32 Instruction Set Manual* | MIPS 官方手册 `[官方]` |
| 🛠 | IEEE Std 1364-2005 (Verilog) / IEEE Std 1800-2017 (SystemVerilog) | Verilog 标准 |

---

## 11. 常见问题

### Q1：必须先做 Nand2Tetris 再做 DDCA 吗？
**不必**。但 Nand2Tetris 的 Hack 比 MIPS 简单 10 倍，先用 Hack 建立"CPU 是什么"的直觉再学 MIPS 更顺。

### Q2：用 MIPS Edition 还是 ARM Edition？
**MIPS Edition**。原因：
- ETH 用 MIPS 版
- MIPS 比 ARM64 简单（4 种指令格式 vs ARM 的几十种）
- 学懂 MIPS 后看 ARM64 觉得"思路一样"

### Q3：FPGA 板必须买吗？
**不必须**。L01-L08 全部在 iverilog + GTKWave 仿真器里跑。
L09 才需要 FPGA 板。**没有板可以用 Verilator + Yosys 做云综合**。

### Q4：和 Nand2Tetris 哪个先做？
**先 Nand2Tetris（P01-P05），再 DDCA（L01-L06）**。
理由：Nand2Tetris 的 HDL 比 Verilog 简单，让你先学概念；DDCA 用 Verilog 学工程实现。

### Q5：DDCA 完成后能直接看懂工业 CPU 吗？
**不能**。DDCA 的 MIPS 是教学级 RISC，没有：
- 乱序执行（→ [`Lab04`](../Lab04_超标量乱序/)）
- Cache 层次（→ [`Lab03`](../Lab03_存储层次/)）
- 分支预测（→ [`Lab02`](../Lab02_流水线与ILP/)）
- 虚拟内存 / TLB（→ [`Lab03`](../Lab03_存储层次/)）

→ **做完 DDCA 再做本项目 Lab，正好补全这些工业特性**。

### Q6：MIPS 学了有用吗？工业上不都用 ARM 了吗？
**有用**。MIPS 是所有 RISC 的"参考语言"，学懂 MIPS 后看 ARM/RISC-V/SPARC/POWER 都觉得"换皮"。
**MIPS 现在仍用于嵌入式、网络设备、IoT**（如部分路由器、PS1-PS2、龙芯早期芯片）。

### Q7：Mutlu 的视频太长（60+ 小时）怎么办？
分批看：
- **必看**：Lectures 1-7（数字电路 + MIPS ISA）+ Lectures 13-15（流水线）
- **建议看**：Lectures 16-20（存储、I/O）
- **可选看**：Lectures 21-30（前沿主题：DRAM、GPU）
- **跳过**：Lectures 8-12（如果已会 Verilog）

---

## 📌 下一步

**如果你完全零基础**：

1. 先看 Shimon Schocken 的 [TED 演讲](https://www.ted.com/talks/shimon_schocken_the_self_organizing_computer_course)（建立"造 CPU"直觉）
2. 先做 Nand2Tetris 的 [`P01-P02`](../Nand2Tetris/Project_01_BooleanLogic/)（1 个月）
3. 然后进 DDCA 的 [`Lab_01`](./Lab_01_Verilog_Basics/)（Verilog 入门）

**如果你已经做过 Nand2Tetris**：

1. 看 Mutlu 的 Lecture 1（[Intro to DDCA](https://www.youtube.com/watch?v=UJRpNHiqNz4&list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5)）
2. 直接进 [`Lab_01`](./Lab_01_Verilog_Basics/)（用 Verilog 重写 Hack CPU 的 6 个芯片）
3. 4 周内上手 Verilog，然后做 L05 单周期 MIPS（高潮）

**如果你已经懂 Verilog，想直接学 MIPS**：

1. 跳到 [`Lab_05_SingleCycle_MIPS/`](./Lab_05_SingleCycle_MIPS/)
2. 看 Harris & Harris 第 6 章（MIPS ISA）
3. 实现 32 条 MIPS 指令

**如果你只想了解、不打算做**：

1. 通读本文 §1-§4（30 分钟）
2. 浏览每个 Lab 的 README（每个 5 分钟）
3. 在 YouTube 上看几集 Mutlu 的讲座（建立直觉即可）
