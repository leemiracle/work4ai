# 计算机系统基础 + 体系结构 + 操作系统（10 门）深度展开

> **来源**：csdiy.wiki + v0.11 LEARNING-PATH 已有信息
> **判定基准**：飞腾 D3000 NEON 算子优化项目（这是项目核心领域）

---

## 计算机系统基础（2 门）

### 1. ⭐⭐⭐ CMU 15-213: CSAPP ｜ 核心（lens 01 性能架构师）
- **讲师**：Randal Bryant / David O'Hallaron
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：150h
- **官网**：http://csapp.cs.cmu.edu/
- **视频**：[Bilibili BV1iW411d7hd](https://www.bilibili.com/video/BV1iW411d7hd)
- **教材**：*Computer Systems: A Programmer's Perspective, 3/E* (CSAPP)
- **核心 Lab**：
  - **Data Lab**（位运算）
  - **Cache Lab** ⭐⭐⭐（cache 模拟与优化，量化 cache miss）
  - **Arch Lab**（Y86-64 流水线优化）
  - **Performance Lab**（代码性能优化）
- **核心价值**：**第 5 章（优化程序性能）+ 第 6 章（存储器层次结构）= 所有 kernel 优化理论根基**。Cache Lab 让你亲手量化 cache miss 对性能的影响。**cache 友好代码三原则（局部性/分块/避免冲突 miss）是 GEMM tiling 的直接理论依据**

### 2. Stanford CS110: Principles of Computer Systems ｜ 中等
- **官网**：https://web.stanford.edu/class/cs110/
- 系统入门

---

## 体系结构（4 门）

### 3. ⭐⭐⭐ UCB CS61C: Great Ideas in Computer Architecture ｜ 核心（Project 4 = 手写 SIMD GEMM）
- **讲师**：Dan Garcia
- **难度**：🌟🌟🌟🌟 ｜ **学时**：100h
- **官网**：https://cs61c.org/
- **视频**：[Su20 Bilibili](https://www.bilibili.com/video/BV1fC4y147iZ/) / [Fa20 Bilibili](https://www.bilibili.com/video/BV17b42177VG/)
- **教材**：*Computer Organization and Design RISC-V Edition* (Hennessy & Patterson)
- **4 个 Project**：
  - P1：C 语言（Game of Life）
  - P2：**RISC-V 汇编手写神经网络**识别 MNIST
  - P3：Logisim 搭建**二级流水线 CPU**
  - **P4：OpenMP + SIMD 并行优化矩阵运算** ⭐⭐⭐
- **核心价值**：**Project 4 是 csdiy 全站唯一让本科生手写 SIMD+OpenMP GEMM 的作业**。虽用 x86 SSE（非 ARM NEON），但 SIMD 向量化循环、数据布局重排、Cache-aware tiling 方法论完全可迁移到飞腾 NEON

### 4. ⭐⭐⭐ ETHz: Computer Architecture (Onur Mutlu) ｜ 核心（lens 05/12 硬件/芯片）
- **讲师**：**Onur Mutlu**（体系结构顶级学者）
- **难度**：🌟🌟🌟🌟 ｜ **学时**：70h+
- **官网**：[2022 Fall](https://safari.ethz.ch/architecture/fall2022/doku.php?id=start)
- **视频**：[Bilibili 2020](https://www.bilibili.com/video/BV1Vf4y1i7YG/)
- **核心内容**：
  - **Memory systems**（DRAM、新非易失性存储、memory controller）⭐
  - **Processing-in-memory (PIM)** ⭐
  - **Parallel computing**（多核、coherence/consistency、GPU）⭐
  - **Specialized systems for ML** ⭐⭐
- **5 个 Project**：内存/cache 相关，Verilog 设计 MIPS 流水线 + C 周期精确模拟器
- **核心价值**：**业界最深入的体系结构课**。Memory systems 讲解让你理解 **Flash Attention 为什么要减少 HBM 读写**（对抗 memory wall）。Cache hierarchy tradeoff 直接指导 GEMM tiling 参数

### 5. ETHz DDCA: Digital Design and Computer Architecture ｜ 中等
- **官网**：[2023](https://safari.ethz.ch/digitaltechnik/spring2023/)
- **视频**：[YouTube](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrloMa2fUYWPGiZUBQo2) / [Bilibili](https://www.bilibili.com/video/BV1MA411s7qq/)
- **教材**：Harris & Harris, *Digital Design and Computer Architecture*
- **9 个 Lab**（Basys 3 FPGA + Vivado，从组合/时序电路到完整 CPU）
- CS61C 和 ETH CA 的先修课

### 6. Coursera: Nand2Tetris ｜ 弱（零基础）
- **官网**：[Part I](https://www.coursera.org/learn/build-a-computer/) / [Part II](https://www.coursera.org/learn/nand2tetris2/)
- **教材**：《计算机系统要素：从零开始构建现代计算机》
- 10 个 Project 从零造计算机，零基础入门

---

## 操作系统（4 门）

### 7. ⭐⭐⭐ MIT 6.S081: Operating System Engineering ｜ 核心（lens 03 OS）
- **讲师**：MIT
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：150h
- **官网**：https://pdos.csail.mit.edu/6.828/2024/schedule.html
- **视频**：[2020 Bilibili](https://www.bilibili.com/video/BV19k4y1C7kA)
- **教材**：xv6 book + OSTEP
- **核心 Lab**（基于 xv6-riscv）：
  - **Lec 14-15: Virtual Memory / Page Tables** ⭐⭐⭐ → hugepage + TLB + `DTLB_WALK` PMU 事件
  - Lec on File system / Scheduling
- **核心价值**：**Virtual Memory / Page Tables 章节直接对应 lens 03 OS 专家盲区 ④⑤（TLB/hugepage）**。xv6 Lab 亲手实现页表管理

### 8. ⭐⭐⭐ UCB CS162: Operating Systems and Systems Programming ｜ 核心（lens 03 调度）
- **讲师**：UC Berkeley
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：150h
- **官网**：https://cs162.eecs.berkeley.edu/
- **视频**：[2020 Bilibili](https://www.bilibili.com/video/BV1e7411A7vM)
- **核心内容**：**Lec on Scheduling** → CFS / OMP_PROC_BIND / context switch
- **核心价值**：直接对应 lens 03 OS 专家盲区 ②⑤（线程绑定 / context-switch）

### 9. ⭐⭐ NJU OS（蒋炎岩）｜ 中等（中文）
- **官网**：https://jyywiki.cn/
- **视频**：[Bilibili](https://www.bilibili.com/video/BV1N7411C7S8)
- 中文 OS，并发/内存管理章节对应 OpenMP/mlockall

### 10. HIT OS ｜ 弱（中文入门）
- 哈工大 OS，中文入门

---

## 项目相关性总览

| 等级 | 课程 | 核心价值 |
|---|---|---|
| ⭐⭐⭐ 核心 | CMU 15-213 CSAPP, UCB CS61C (P4 SIMD GEMM), ETHz CA (Onur Mutlu), MIT 6.S081 (VM/TLB), UCB CS162 (调度) | **项目 5 大理论根基**：性能优化 + SIMD + 体系结构 + 虚存 + 调度 |
| ⭐⭐ 中等 | Stanford CS110, ETHz DDCA, NJU OS | 系统入门 + 硬件设计 + 中文 OS |
| ⭐ 弱 | Nand2Tetris, HIT OS | 零基础入门 |
