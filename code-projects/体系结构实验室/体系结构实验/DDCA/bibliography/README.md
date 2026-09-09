# DDCA 延伸阅读

> Harris & Harris + Onur Mutlu 之外的扩展资源。

---

## 1. 必读（DDCA 旅程的姐妹书）

### 1.1 主教材

| 书 | 作者 | 版本 |
|----|------|------|
| *Digital Design and Computer Architecture (MIPS Edition)* | David Harris & Sarah Harris | Elsevier 2015（2nd） |
| 《数字设计和计算机体系结构》| 同上 | 中译本 |

### 1.2 同类教材（互补）

| 书 | 与 Harris 的关系 |
|----|------------------|
| *Computer Organization and Design: The Hardware/Software Interface (MIPS Edition)* - Patterson & Hennessy | 同样用 MIPS，但视角更高层（讲 ISA，不讲电路）|
| *Computer Organization and Design RISC-V Edition* - Patterson & Hennessy | 同上，RISC-V 版本，与本项目 [`Lab01`](../../Lab01_ISA与汇编/) 主教材对应 |
| *Logic and Computer Design Fundamentals* - Mano & Kime | 更老的数字电路教材，风格更"传统" |

---

## 2. Onur Mutlu 的其他课程

Mutlu 教多门高级课程，**学完 DDCA 后**可以进阶：

| 课程 | 主题 |
|------|------|
| **[Computer Architecture (CA)](https://safari.ethz.ch/architecture/)** | 研究生级体系结构，含 ISCA/MICRO 论文 |
| **[Memory Systems (MS)](https://safari.ethz.ch/memory_systems/)** | DRAM 主存系统（Mutlu 研究强项）|
| **[Digital Design and Computer Architecture II (DDCA2)](https://safari.ethz.ch/digital_design_and_computer_architecture_2/)** | DDCA 进阶版，含更深的物理实现 |
| **[ECE 1742H: Parallel Computer Architecture** (CMU 时期)](https://www.ece.cmu.edu/~ece740/f13/lib/exe/fetch.php?media=wiki:schedule.pdf) | 多核系统 |

---

## 3. Verilog 进阶

### 3.1 入门

| 资源 | 内容 |
|------|------|
| *Verilog by Example* - Lee | 完整实战，150 页速通 |
| Verilog Modes - [asic-world.com](https://www.asic-world.com/verilog/) | 免费、全面 |
| *FPGA Prototyping by Verilog Examples* - Pong P. Chu | 配套 Nexys 4 |

### 3.2 进阶

| 资源 | 内容 |
|------|------|
| *SystemVerilog for Verification* - Spear | 现代 SV 验证 |
| *Writing Testbenches: Functional Verification of HDL Models* - Bergeron | 验证方法学 |
| *HDL Chip Design* - Smith | 综合 + 可综合性 |

---

## 4. MIPS 深挖

| 资源 | 内容 |
|------|------|
| [*MIPS Architecture for Programmers Volume II-A*](https://s3-eu-west-1.amazonaws.com/downloads-mips/documents/MD00086-2B-MIPS32BIS-AFP-06.02.pdf) | 官方 ISA 手册（必读）`[官方]` |
| *See MIPS Run* - Sweetman | MIPS 工业级使用指南 |
| [*MIPS History*](https://www.mips.com/products/architectures/mips32/) | 官方历史 |
| *Computer Architecture: A Quantitative Approach* - Hennessy & Patterson 附录 A | MIPS 完整指令集参考 |

---

## 5. CPU 设计进阶（学完 L06 之后）

| 书 | 内容 |
|----|------|
| *Computer Architecture: A Quantitative Approach (CAQA)* - Hennessy & Patterson | 本项目 [`Expert_02`](../../Expert_02_Architect/) 主教材 |
| *超标量处理器设计* - 姚永斌 | 本项目 [`Lab04`](../../Lab04_超标量乱序/) 主教材 |
| *Onur Mutlu's SAFARI Lectures* | [YouTube 研究讲座](https://www.youtube.com/@OnurMutluSAFARI) |

---

## 6. FPGA 进阶

| 资源 | 内容 |
|------|------|
| *FPGA Prototyping by Verilog Examples* - Pong P. Chu | 完整工程实战 |
| *Real World FPGA Design with Verilog* - Wilson | 工业级设计技巧 |
| [ZipCPU 博客](https://zipcpu.com/) | 高质量 Verilog/FPGA 博客 |
| [fpga4fun.com](https://www.fpga4fun.com/) | 各种小项目 |

---

## 7. 视频课程

### 7.1 DDCA 主线

| 资源 | 链接 |
|------|------|
| **ETH DDCA 全部讲座** | [YouTube Playlist](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| **Onur Mutlu SAFARI 主题演讲** | [SAFARI YouTube](https://www.youtube.com/@OnurMutluSAFARI) |
| **MIT 6.004 Computation Structures** | [OCW](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/) |

### 7.2 Verilog 入门视频

| 资源 | 链接 |
|------|------|
| *Verilog Tutorial for Beginners* | YouTube 多个 |
| *FPGA Tutorial* | YouTube |
| *FPGA 101* | fpga4fun |

---

## 8. 社区与开源

### 8.1 社区

| 渠道 | 用途 |
|------|------|
| [r/FPGA](https://www.reddit.com/r/FPGA/) | FPGA 爱好者 |
| [r/verilog](https://www.reddit.com/r/verilog/) | Verilog 问答 |
| [Stack Overflow: verilog tag](https://stackoverflow.com/questions/tagged/verilog) | 程序员问答 |
| [EEVblog Forum](https://www.eevblog.com/forum/) | 电子工程师社区 |

### 8.2 开源 MIPS CPU 实现

| 项目 | 内容 |
|------|------|
| [darklife/mips-cpu](https://github.com/darklife/mips-cpu) | 完整 MIPS CPU |
| [karlfreeman/mips-cpu](https://github.com/karlfreeman/mips-cpu) | 单周期 + 流水线 |
| [MIPSfpga](https://github.com/MIPSfpga/) | Imagination Technologies 官方教学 |
| [jiejieLiu/MIPS-CPU](https://github.com/jiejieLiu/MIPS-CPU) | 中文注释版 |

### 8.3 开源 FPGA 工具链

| 工具 | 用途 |
|------|------|
| [Yosys](https://github.com/YosysHQ/yosys) | 开源综合 |
| [nextpnr](https://github.com/YosysHQ/nextpnr) | 开源布局布线 |
| [Project X-Ray](https://github.com/f4pga/) | 开源 Xilinx 7 系列工具 |
| [SymbiFlow](https://github.com/SymbiFlow) | "GCC for FPGAs" |

---

## 9. 与本项目其他文档的关系

| 本项目文档 | 配合读 DDCA 的哪一部分？ |
|-----------|---------------------------|
| [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) | L01-L09（让分层从抽象变具体）|
| [`背景知识/Great_Ideas_体系结构思想.md`](../../背景知识/Great_Ideas_体系结构思想.md) | 全部 9 个 lab |
| [`Lab00_测量基础设施`](../../Lab00_测量基础设施/) | L05/L06（CPU 在飞腾真机上的对照）|
| [`Lab01_ISA与汇编`](../../Lab01_ISA与汇编/) | L05（MIPS vs ARM64 ISA 对照）|
| [`Lab02_流水线与ILP`](../../Lab02_流水线与ILP/) | L06（流水线对照）|
| [`Lab03_存储层次`](../../Lab03_存储层次/) | L07（Cache 对照）|
| [`Lab04_超标量乱序`](../../Lab04_超标量乱序/) | L06（顺序 vs 乱序）|
| [`Nand2Tetris`](../../Nand2Tetris/) | L01-L09（DDCA 的"教学版前置"）|
| [`Capstone/cpu_simulator`](../../Capstone/cpu_simulator/) | L06（Python 实现 RV32I 流水线）|
| [`Expert_02_Architect`](../../Expert_02_Architect/) | L06（工业级 CPU 架构）|
| [`Expert_03_HW_Designer`](../../Expert_03_HW_Designer/) | L01-L06（Verilog 实战）|
| [`Expert_04_OS_Kernel`](../../Expert_04_OS_Kernel/) | L08（异常/中断对照）|
| [`Expert_13_VLSI_Physical`](../../Expert_13_VLSI_Physical/) | L09（FPGA vs ASIC）|

---

## 📌 阅读建议

1. **入门顺序**：先看 Mutlu DDCA Lecture 1（建立直觉）→ 读 Harris & Harris Ch1-3（数字基础）→ 开始 L01
2. **不要囤书**：每本书**配合对应 lab 读**，不要一次买十本
3. **善用视频**：Mutlu 全部讲座免费，**优先看视频**再读章节
4. **多看源码**：完成 L05 后，直接读 [`Expert_03/rtl/`](../../Expert_03_HW_Designer/rtl/) 的 RV32I 实现
