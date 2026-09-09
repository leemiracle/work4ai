# 并行与分布式 + 编译原理（8 门）深度展开

> **来源**：csdiy.wiki + v0.11 LEARNING-PATH 已有信息
> **判定基准**：飞腾 D3000 NEON 算子优化项目（OpenMP/Winograd/未来 TVM 集成所需）

---

## 并行与分布式系统（2 门）

### 1. ⭐⭐⭐ CMU 15-418 / Stanford CS149: Parallel Computing ｜ 核心（世界级 Roofline 标杆）
- **讲师**：**Kayvon Fatahalian**（现 Stanford）+ Pat Hanrahan
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：150h
- **官网**：
  - [CMU 15-418](https://www.cs.cmu.edu/afs/cs/academic/class/15418-s18/www/index.html)
  - [Stanford CS149](https://gfxcourses.stanford.edu/cs149/fall21)
- **视频**：[CS149 YouTube](https://youtube.com/playlist?list=PLoROMvodv4rMp7MTFr4hQsDEcX7Bx6Odp)
- **作业**：5 个编程作业（CUDA、OpenMP、MPI、Spark）
- **GitHub**：[PKUFlyingPig/CS149-parallel-computing](https://github.com/PKUFlyingPig/CS149-parallel-computing)
- **核心内容**：
  - 现代并行架构设计原则 + **硬件资源利用** ⭐⭐
  - **SIMD 向量化、CUDA、OpenMP** ⭐⭐⭐
  - **Roofline 性能模型** ⭐⭐⭐（csdiy 全站对本项目价值最高的内容）
  - 并行程序瓶颈分析、GPU 编程模型
- **核心价值**：**Kayvon Fatahalian 的 Roofline 模型讲解是世界级标杆**——你需要用 Roofline 判断 NEON GEMM 是 compute-bound 还是 memory-bound。SIMD/CUDA 作业训练的**向量化思维**直接迁移到 NEON intrinsics

### 2. ⭐⭐ MIT 6.824: Distributed System ｜ 中等（CXL/远端内存）
- **讲师**：MIT（Robert Morris 等）
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：100h
- **官网**：https://pdos.csail.mit.edu/6.824/
- **视频**：[Bilibili](https://www.bilibili.com/video/BV1x7411C7am)
- **核心 Lab**：Go 语言实现 Raft + 分布式 KV store
- **核心价值**：**Lec on Raft / Consensus** → CXL 多节点一致性、REMOTE_ACCESS PMU 事件

---

## 编译原理（6 门）

### 3. ⭐⭐⭐ Machine Learning Compilation (MLC) ｜ 核心（TVM TensorIR）
- **讲师**：**Tianqi Chen（陈天奇）**（TVM 创始人之一）
- **难度**：🌟🌟🌟 ｜ **学时**：30h
- **官网**：https://mlc.ai/summer22-zh/
- **视频**：[Bilibili](https://www.bilibili.com/video/BV15v4y1g7EU)
- **笔记**：https://mlc.ai/zh/index.html
- **作业**：[GitHub notebooks](https://github.com/mlc-ai/notebooks/blob/main/assignment)
- **核心内容**：
  - ML 编译的**通用抽象与变换**
  - 计算图优化（算子融合、常量折叠）⭐⭐
  - **TensorIR / Tensor Program 优化** ⭐⭐⭐
  - **Loop transformation**：tiling、unrolling、vectorization ⭐⭐⭐
  - **硬件后端适配** ⭐⭐
- **核心价值**：**TVM 是本项目最直接相关的工业级框架**。TensorIR 的 loop tiling/vectorization/unrolling 就是手写 NEON GEMM 做的事情——TVM 只是自动化了。学习后可用 `tensorize` 把 NEON 指令注入计算图，让手写 kernel 被 TVM 自动调度

### 4. ⭐⭐ Stanford CS143: Compilers ｜ 中等
- **讲师**：Stanford
- **难度**：🌟🌟🌟🌟 ｜ **学时**：100h
- **官网**：https://web.stanford.edu/class/cs143/
- **视频**：[YouTube](https://www.youtube.com/playlist?list=PL84BC2385C6F2E0D4)
- 经典编译原理（lex/yacc + 代码生成）
- **核心价值**：**Code Generation / Instruction Scheduling** → PhyGCC -O3 vs 手写 ASM 的对比基础

### 5. PKU 编译原理实践 ｜ 中等（中文）
- **讲师**：助教 MaxXing
- **难度**：🌟🌟🌟🌟 ｜ **学时**：60h
- **官网**：https://pku-minic.github.io/online-doc/#/
- 从零实现 SysY → **RISC-V** 汇编编译器，自研 Koopa IR

### 6. NJU 编译原理 ｜ 中等（中文）
- **官网**：http://docs.compilers.cpl.icu/
- **视频**：[Bilibili](https://space.bilibili.com/479141149/lists/2312309)
- 用 ANTLR v4，10 书面 + 8-10 编程作业

### 7. ⭐⭐ KAIST CS420: Compiler Design ｜ 中等（LLVM backend）
- **官网**：https://github.com/kaist-cp/cs420
- **GitHub**：[kaist-cp/cs420](https://github.com/kaist-cp/cs420)
- **核心价值**：**LLVM backend 实战**——理解 auto-vectorization 在 LLVM 里的实现

### 8. USTC 编译 / SJTU 编译 ｜ 中等（中文）
- **USTC**：https://ustc-compiler-principles.github.io/2023
  - Lab3 后端代码生成 + Lab6 寄存器分配 = NEON 指令选择前提
- **SJTU**：https://ipads.se.sjtu.edu.cn/courses/compilers
  - LLVM IR + 活跃分析 + 寄存器分配 + GC

---

## 项目相关性总览

| 等级 | 课程 | 核心价值 |
|---|---|---|
| ⭐⭐⭐ 核心 | CMU 15-418/CS149 (Roofline+SIMD), MLC (TVM TensorIR) | **Roofline 世界级标杆 + TVM 自动化手写 NEON** |
| ⭐⭐ 中等 | MIT 6.824 (CXL), Stanford CS143 (code gen), KAIST CS420 (LLVM), USTC/SJTU 编译 | 分布式 + 编译 backend |
| ⭐ 弱 | PKU 编译, NJU 编译 | 中文入门 |
