# Nand2Tetris 延伸阅读

> 完成或学习中遇到任何瓶颈，都可以从这份单子找到下一本书。

---

## 1. 必读（Nand2Tetris 旅程的姐妹书）

### 1.1 Nand2Tetris 本身

| 书 | 作者 | 版本 | 难度 |
|----|------|------|------|
| *The Elements of Computing Systems* | Nisan & Schocken | MIT Press 2021 (2nd) | ⭐⭐ |
| 《计算机系统要素：从零开始构建现代计算机》| 同上 | 中文译本 | ⭐⭐ |

### 1.2 同类经典（做 Nand2Tetris 时搭配读）

| 书 | 关系 |
|----|------|
| 📘 Patterson & Hennessy《计算机组成与设计 RISC-V 版》| 本项目 [`Lab01`](../../Lab01_ISA与汇编/) 主教材。Nand2Tetris 用 Hack，这本书用 RISC-V——两套 ISA 互补 |
| 📗 Harris & Harris《数字设计和计算机体系结构》| 提供 Verilog 实现的 Hack CPU（直接对接 [`Expert_03`](../../Expert_03_HW_DesignER/)）|
| 📕 姚永斌《超标量处理器设计》| 本项目 [`Lab04`](../../Lab04_超标量乱序/) 主教材，从单周期（Hack）到乱序（飞腾）|

---

## 2. 编译器方向（P06-P11 之后深挖）

### 2.1 入门

| 书 | 适合 |
|----|------|
| 《编译原理》（龙书）Aho, Lam, Sethi, Ullman | 经典教材，学完 P10-P11 后读更有效 |
| Engineering a Compiler (Cooper & Torczon) | 现代编译器工程视角，比龙书更工业 |
| *Crafting Interpreters* (Robert Nystrom) | 用 Java + C 实现两个解释器，免费在线 |
| *Write Yourself a Scheme in 48 Hours* | 用 Haskell 写 Lisp 解释器，免费在线 |

### 2.2 进阶

| 书 | 重点 |
|----|------|
| Compilers: Principles, Techniques, and Tools（龙书第二版）| SSA、优化、垃圾回收 |
| *Static Program Analysis* (Anders Møller, Michael Schwartzbach) | 静态分析免费在线 |
| *Engineering a Compiler* 第 2 版 | 工程实现 |

### 2.3 JIT 与虚拟机

| 资源 | 内容 |
|------|------|
| [pyxis/blog: "JIT compiler"] | JIT 入门博客 |
| *Implementing a JIT Compiler` (Rafal Janik)* | JIT 实战 |
| LuaJIT 源码 | 高质量栈式 VM + trace JIT |
| V8 源码 | 工业级 JS JIT |

---

## 3. 操作系统方向（P12 之后深挖）

### 3.1 经典

| 书 | 关系 |
|----|------|
| OSTEP（Operating Systems: Three Easy Pieces）| 免费在线，最易读的 OS 入门 |
| CSAPP（Computer Systems: A Programmer's Perspective）| 本项目 [`Expert_04`](../../Expert_04_OS_Kernel/) 主参考 |
| 《现代操作系统》Tanenbaum | 经典 OS 教材 |
| 《操作系统导论》Remzi Arpaci-Dusseau | OSTEP 中文版 |

### 3.2 内核实战

| 资源 | 内容 |
|------|------|
| MIT 6.S081（原 6.828）| 用 RISC-V 写 xv6，免费课程 |
| Linux Kernel Development (Robert Love) | Linux 内核实战 |
| *Writing an OS from Scratch* | 用 Rust 写 OS |
| OSDev Wiki | 业余 OS 开发社区 |

---

## 4. 硬件设计方向（P01-P05 之后深挖）

### 4.1 HDL 与 FPGA

| 资源 | 内容 |
|------|------|
| 《数字设计和计算机体系结构》Harris & Harris | Verilog + FPGA 实战 |
| *FPGA Prototyping by Verilog Examples* (Pong Chu) | 上手 FPGA 板 |
| nand2tetris → Verilog 移植 | 社区项目，搜 "nand2tetris verilog" |

### 4.2 工业级硬件设计

| 资源 | 内容 |
|------|------|
| 《超标量处理器设计》姚永斌 | 本项目 [`Lab04`](../../Lab04_超标量乱序/) 主教材 |
| Computer Architecture: A Quantitative Approach (Hennessy & Patterson) | 本项目 [`Expert_02`](../../Expert_02_Architect/) 圣经 |
| *Computer Organization and Design RISC-V* | Patterson 最新版，ARM 版也有 |

### 4.3 VLSI 与物理实现

| 资源 | 内容 |
|------|------|
| CMOS VLSI Design (Weste & Harris) | [`Expert_13`](../../Expert_13_VLSI_Physical/) 主参考 |
| *Digital Integrated Circuits* (Rabaey) | 晶体管级电路 |

---

## 5. 视频课程

### 5.1 Nand2Tetris 官方

| 资源 | 链接 |
|------|------|
| **Coursera Part I**（P01-P06）| [Build a Modern Computer from First Principles: From Nand to Tetris](https://www.coursera.org/learn/build-a-computer) |
| **Coursera Part II**（P07-P12）| [Nand to Tetris Part II](https://www.coursera.org/learn/nand2tetris2) |
| **TED 演讲**（强烈推荐先看）| [Shimon Schocken: The self-organizing computer course](https://www.ted.com/talks/shimon_schocken_the_self_organizing_computer_course) |
| **YouTube 频道**| [youtube.com/@nand2tetris](https://www.youtube.com/@nand2tetris) |

### 5.2 同类优质课程

| 资源 | 与 Nand2Tetris 关系 |
|------|---------------------|
| MIT 6.004（Computation Structures）| MIT 内部版"从 Nand 到 CPU" |
| Berkeley CS61C | 本项目 [`Lab01`](../../Lab01_ISA与汇编/) 主参考 |
| OnLabs *Build an 8-bit computer from scratch* | Ben Eater 真实硬件版（与 Nand2Tetris 互补）|
| Berkeley CS152 | 体系结构研究生级（[`Expert_02`](../../Expert_02_Architect/) 同级）|

---

## 6. 社区与开源

### 6.1 社区

| 渠道 | 用途 |
|------|------|
| [nand2tetris Slack](https://nand2tetris.slack.com) | 官方问答 |
| [Stack Overflow: nand2tetris tag](https://stackoverflow.com/questions/tagged/nand2tetris) | 程序员问答 |
| Reddit /r/nand2tetris | 业余讨论 |
| Reddit /r/ECE | 电子工程大社区 |

### 6.2 优秀社区实现（参考用，不要抄）

| 项目 | 内容 |
|------|------|
| [havivha/nand2tetris](https://github.com/havivha/nand2tetris) | 一个完整参考实现 |
| [aaronbpadilla/nand2tetris](https://github.com/aaronbpadilla/nand2tetris) | Python 版翻译器 |
| [kamrik/nand2tetris](https://github.com/kamrik/nand2tetris) | 简洁版参考 |

### 6.3 相关开源工具

| 工具 | 用途 |
|------|------|
| [nand2tetris/web-ide](https://github.com/nand2tetris/web-ide) | 官方在线 IDE（开源） |
| [nand2tetris-zoo](https://github.com/ ALCo/nand2tetris-zoo) | 多语言实现的动物园 |
| Verilog iVerilog | 替代 HDL 模拟器 |
| GTKWave | 波形查看器（与 iVerilog 配合） |

---

## 7. 与本项目其他文档的关系

| 本项目文档 | 配合读 Nand2Tetris 的哪一部分？ |
|-----------|--------------------------------|
| [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) | P01-P05（让分层模型从抽象变具体）|
| [`背景知识/Great_Ideas_体系结构思想.md`](../../背景知识/Great_Ideas_体系结构思想.md) | 全部 12 个 project |
| [`Lab01`](../../Lab01_ISA与汇编/) | P02 + P04 + P06（ALU + 汇编 + 汇编器）|
| [`Lab02`](../../Lab02_流水线与ILP/) | P05（CPU 架构）|
| [`Lab03`](../../Lab03_存储层次/) | P03（时序 + RAM）|
| [`Lab04`](../../Lab04_超标量乱序/) | P05（CPU 内部）|
| [`Lab05`](../../Lab05_并行与SIMD/) | P02（ALU + 向量化）|
| [`Lab06`](../../Lab06_内存模型与并发/) | P12（OS）|
| [`Expert_02`](../../Expert_02_Architect/) | P05（CPU 设计决策）|
| [`Expert_03`](../../Expert_03_HW_Designer/) | P01-P03（HDL → Verilog）|
| [`Expert_04`](../../Expert_04_OS_Kernel/) | P12（OS）|
| [`Expert_11`](../../Expert_11_Compiler_Research/) | P06-P11（工具链）|
| [`Capstone/cpu_simulator`](../../Capstone/cpu_simulator/) | P05（CPU 模拟器）|

---

## 📌 阅读建议

1. **入门顺序**：先看 Shimon Schocken 的 TED 演讲（15 分钟）→ 读 Nisan & Schocken 的书前言 → 开始做 P01
2. **不要囤书**：每本书**配合对应 project 读**，不要一次买十本
3. **善用免费资源**：Coursera、OSTEP、CSAPP 课件、TED 都是免费的
4. **读源码 > 读书**：完成 P05 后，直接读 [`Capstone/cpu_simulator/rv32i_sim.py`](../../Capstone/cpu_simulator/rv32i_sim.py) 源码
