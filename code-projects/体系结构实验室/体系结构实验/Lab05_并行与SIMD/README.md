# Lab05 — 并行与 SIMD：GEMM 优化全栈

> 这是 Hennessy & Patterson Ch4 + Ch5 + CS61C Proj4 + MIT 6.172 L14/L15 的综合战场。
> 目标：把一个朴素 GEMM 优化到飞腾 D3000M 的 FLOPS 理论极限。

---

## 0. 学习目标（一句话）

**综合运用 ILP（Lab02）+ Cache（Lab03）+ 超标量（Lab04）+ SIMD（Lab01）+ 多核（OpenMP），
把朴素 GEMM 优化到飞腾峰值性能的 70%+**。

---

## 1. 对应教材与课程

| 来源 | 章节 | 重点 |
|------|------|------|
| 📘 Patterson RISC-V | **Ch6 (Parallel Processors)** | 多处理器基础、GPU、DSA |
| 📗 CAQA 5th | **Ch4 (DLP: Vector/SIMD/GPU)** | SIMD 编程模型、GPU 体系 |
| 📗 CAQA 5th | **Ch5 (TLP: Multiprocessors)** | 一致性、同步、MESI |
| 🎓 CS61C | Proj4 | 并行优化 Numpy (SIMD + OpenMP) |
| 🎓 MIT 6.172 | L14/L15 | Cache-friendly + Cache-oblivious 算法 |
| 📖 | Goto & van de Geijn, "Anatomy of High-Performance Matrix Multiplication" (2008) | GEMM 优化圣经 |

---

## 2. 核心概念速览

### 2.1 飞腾 D3000M 性能极限

```
2.5 GHz × 4-wide × 2 (NEON fmla 同时 2 个 double)
   = 2.5e9 × 4 × 2 × 2 = 40 GFLOPS/core
   × 8 cores = 320 GFLOPS

NEON fmla v0.2d, v1.2d, v2.2d  → 2 个 double 乘累加/cyc
   = 2.5e9 × 2 × 2 (mul + add) × 8 cores = 80 GFLOPS

实际可达目标: 60-80% of peak ≈ 50-65 GFLOPS/core
```

### 2.2 GEMM 优化五步走（Goto 算法）

```
Step 0: 朴素 O(n^3)                 ~ 1-2% peak
Step 1: 循环交换 (i,j,k → i,k,j)    ~ 5% peak   (cache-friendly)
Step 2: 分块 (i,j,k → 内层 tile)    ~ 20% peak  (L2/L1 命中)
Step 3: NEON 向量化                  ~ 40% peak  (4x speedup on float)
Step 4: 寄存器分块 (16×16 micro-kernel)  ~ 70% peak
Step 5: OpenMP 多核 + NUMA 感知       ~ 1× peak  (实测 bandwidth-bound, 双精度 ikj 多核无加速, roofline 带宽墙)
                                       要多核扩展必须 NEON fp32+寄存器分块 (compute-bound)
```

### 2.3 一张图：分块 GEMM

```
C (M×N) = A (M×K) × B (K×N)
        ┌────────────────────────────┐
        │ 分块:                                                      │
        │   for ii in M/MC:                                            │
        │     for jj in N/NC:                                          │
        │       for kk in K/KC:                                        │
        │         打包 A_ii,kk → A_pack (L2 友好)                       │
        │         打包 B_kk,jj → B_pack (L2 友好)                       │
        │         for i in MC/MR:                                        │
        │           for j in NC/NR:                                      │
        │             GEMM micro-kernel (MR × NR × KC, 全在寄存器)      │
        └────────────────────────────┘
```

---

## 3. 实验列表

### 3.1 实验 5.1：NEON intrinsic 实战（`neon_intrinsics.c`）

复习 Lab01 的 dot4，扩展到 4×4 矩阵乘。

### 3.2 实验 5.2：自动向量化 vs 手写（`auto_vectorize.c`）

对比 `-O3 -ftree-vectorize` vs NEON intrinsic 的代码质量和性能。

### 3.3 实验 5.3：GEMM 优化全栈（`gemm_full_stack.c`）

**这是整个项目的核心 capstone**：
- 朴素版本
- 循环交换
- 分块 (32×32)
- 寄存器分块 (8×8 + NEON)
- OpenMP 多核

**目标**：N=1024 双精度 GEMM，从 ~2 GFLOPS 优化到 ~30 GFLOPS。

### 3.4 实验 5.4：Cache-Oblivious GEMM（`cache_oblivious.c`）

递归分治 GEMM，不需知道 cache 参数也能接近最优。

### 3.5 实验 5.5：OpenMP 多核（`openmp_multicore.c`）

8 核扩展，测 NUMA 效应和 cache contention。

---

## 4. 学完应该掌握的检查清单

- [ ] 能写一个 NEON 4×4 矩阵乘 micro-kernel
- [ ] 能解释为什么 `for (i,j,k)` 比 `for (i,k,j)` 慢
- [ ] 能算出 GEMM 的理论 FLOPS 上限
- [ ] 能用 OpenMP 把单核 GEMM 扩展到 8 核，并测出加速比
- [ ] 能解释 Cache-Oblivious 为什么"自动适配任意 cache 层次"

---

## 5. 参考文献

| 📖 Goto & van de Geijn (2008) | GEMM 优化圣经 |
| 📖 Chellappa et al., "High Performance Matrix Multiply on GPUs" | GPU 视角 |
| 📖 Frigo et al., "Cache-Oblivious Algorithms" (1999/2012) | 理论 |
| 🎓 MIT 6.172 L14/L15 slides | 实战 |
| 🎓 CS61C Proj4 spec | 学生作业版 |

---

## 6. 编译与运行

```bash
cd Lab05_并行与SIMD
make
./neon_intrinsics
./auto_vectorize
./gemm_full_stack
OMP_NUM_THREADS=8 ./openmp_multicore
```

---

📌 **下一步**：完成 Lab05 后，进入 [`Capstone/`](../Capstone/)。三选一：
- A. 论文精读：Alpha 21264 vs 飞腾 D3000M 微架构对比
- B. 自写周期级 CPU 模拟器（RV32I）
- C. 工作负载刻画（如 llama.cpp 推理）
