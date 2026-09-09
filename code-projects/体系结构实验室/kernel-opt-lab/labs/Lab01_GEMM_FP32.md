# Lab01 — FP32 GEMM：从 Naive 到 98.6% 峰值

> 源文件：[`src/gemm_f32.c`](../src/gemm_f32.c)（210 行）
> 阶段：学习路径 §1（算子优化之王）
> 目标成绩：**39.45 GFLOPS（98.6% of 40 峰值）**

---

## 0. 学习目标

读完本 Lab，你能回答：
- GEMM 的三重循环为什么慢？瓶颈在哪？
- `pack_B_blk` 布局解决了什么问题？
- `vfmaq_laneq_f32` 微内核怎么用满 4 FVU？
- MR=1 / MR=2 / MR=8 各对应几个 FVU？为什么 MR=8 最优？

---

## 1. 数学定义

$$C_{M \times N} = A_{M \times K} \times B_{K \times N}$$

本项目固定 $M=N=K=1024$，FP32。一次 GEMM 的 FLOPS = $2MNK = 2 \times 1024^3 \approx 2.15 \text{ GFLOP}$。

---

## 2. D3000 理论峰值推导

```
4 FVU（Flexible Vector Unit，自研向量单元）
× 2.5 GHz
× 4 lane（FP32 每向量 4 个浮点）
× 2（FMA = 一次乘 + 一次加，算两次）
= 40 GFLOPS
```

**这就是一切优化的天花板**。39.45 GFLOPS = 98.6% of 40。

---

## 3. 三版本演进（`gemm_f32.c` 的核心结构）

文件里保留了**三个版本的完整对照**——这是最好的教材：

| 函数 | 行号 | MR | 累加器数 | 用几个 FVU | 实测 GFLOPS | 利用率 |
|------|------|:--:|:-------:|:---------:|:----------:|:------:|
| `gemm_f32_v5_single` | 33-52 | 1 | 1 (c0) | 1 FVU | 10.15 | 25% |
| `gemm_f32_v4_dual` | 55-81 | 2 | 2 (c0,c1) | 2 FVU | 19.59 | 49% |
| `gemm_f32_v5_mr8` | **84-141** | **8** | **8 (c0..c7)** | **4 FVU** | **39.45** | **98.6%** |

### 3.1 为什么 MR 翻倍 ≈ 性能翻倍？

D3000 有 4 个独立 FVU，每个 FVU 每周期能发 1 条 FMA。MR（微内核行数）决定你能同时喂几个 FVU：
- MR=1：只算 1 行，只有 1 个累加器 → 1 个 FVU 在干活，3 个闲着
- MR=2：2 行 → 2 个 FVU
- MR=8：8 行 → 4 个 FVU 全开（每个 FVU 分 2 行）

---

## 4. 微内核详解（MR=8，本项目精华）

### 4.1 pack_B_blk：数据布局重排（第 25-30 行）

```c
/* pack B 行主 [N][K] → B_blk[N/4][K][4] */
static void pack_B_blk(const float *B, float *B_blk) {
    for (int jb = 0; jb < N / 4; jb++)
        for (int k = 0; k < K; k++)
            for (int ji = 0; ji < 4; ji++)
                B_blk[jb * K * 4 + k * 4 + ji] = B[(jb * 4 + ji) * K + k];
}
```

**为什么？** 原始 B 是行主序 `[N][K]`，算 $C_{i,j}$ 时要访问 $B_{k,j}$，跨列跨步大、cache 不友好。重排成 `[N/4][K][4]`——把每 4 列打包成连续的 16 字节（一个 NEON 向量），让微内核能 `vld1q_f32` 一次取 4 个。

> ⚠️ pack 有代价（1024³ 约 5-10ms），但摊到多次 GEMM 上就划算。这是 Goto 论文的核心洞察之一。

### 4.2 v5_mr8 微内核（第 84-122 行）逐行解读

```c
for (int i = 0; i < M8; i += 8) {        // 外层：每次处理 8 行（MR=8）
    for (int jb = 0; jb < N / 4; jb++) { // 每次处理 4 列（一个 NEON 向量宽）
        const float *b_base = &B_blk[jb * K * 4];
        // ★ 8 个独立累加器 → 4 FVU 全开
        float32x4_t c0=vdupq_n_f32(0), c1=..., ..., c7=...;
        for (int k = 0; k < K; k += 4) { // k 维每次 4（一个向量）
            // 取 8 行 A 的向量
            float32x4_t a0=vld1q_f32(&A[(i+0)*K+k]), ..., a7=...;
            // 取 B 的 4 个向量（k, k+1, k+2, k+3）
            float32x4_t b0=..., b1=..., b2=..., b3=...;
            // ★ 核心：32 条 vfmaq_laneq_f32，把 4 FVU 喂满
            c0=vfmaq_laneq_f32(c0,b0,a0,0); c1=vfmaq_laneq_f32(c1,b0,a1,0);
            ...（8 行，每个累加器 × b0 的 lane 0）
            c0=vfmaq_laneq_f32(c0,b1,a0,1); ...（lane 1）
            c0=vfmaq_laneq_f32(c0,b2,a0,2); ...（lane 2）
            c0=vfmaq_laneq_f32(c0,b3,a0,3); ...（lane 3）
        }
        // 存回 8 行结果
        vst1q_f32(&C[(i+0)*N+jb*4],c0); ... vst1q_f32(&C[(i+7)*N+jb*4],c7);
    }
}
```

### 4.3 `vfmaq_laneq_f32(c, b, a, lane)` 到底干了什么？

```
c[0..3] += b[0..3] × a[lane]   // a 的第 lane 个元素广播，和 b 逐元素乘，加到 c
```

一条指令 = 4 次乘加。k 循环每步 4 次（lane 0,1,2,3）= 16 次乘加。
8 个累加器 × 16 = 128 次乘加 / k 步。这 128 条 FMA 指令分发到 4 FVU，每个 FVU 分 32 条。

### 4.4 寄存器压力

8(c0..c7) + 8(a0..a7) + 4(b0..b3) = **20 个向量寄存器**。D3000 有 32 个 NEON 寄存器（V0-V31），够用。这就是为什么 MR=8 是上限——MR=16 会溢出到栈，反而变慢。

---

## 5. 跑法与预期输出

```bash
make gemm_f32 && ./bin/gemm_f32
```

预期（1024³）：
```
=== FP32 GEMM v5 (MR=8, 4 FVU) ===

Correctness (8x8):
  v5_single (MR=1)  vs scalar: ✅ (max_diff=0.00e+00)
  v4_dual   (MR=2)  vs scalar: ✅ (max_diff=0.00e+00)
  v5_mr8    (MR=8)  vs scalar: ✅ (max_diff=0.00e+00)

Performance (1024^3, 3 iter):
  v5_single (MR=1):  ~210 ms  ~10 GFLOPS  (100% of 10)
  v4_dual   (MR=2):  ~110 ms  ~20 GFLOPS  (100% of 20)
  v5_mr8    (MR=8):  ~54 ms   ~39 GFLOPS  (98% of 40)  ← 最优
```

---

## 6. 假设 → 实验 → 解释

**假设 A**：naive 三重循环（`gemm_f32_scalar`，第 143 行）能跑多少？
- 实验：注释掉 NEON 版本，只跑 scalar
- 解释：<details>约 1-3 GFLOPS（~5%）。瓶颈：B 按列访问 cache miss 严重；C 反复读写；编译器无法自动向量化这种跨步访问。</details>

**假设 B**：MR=8 改成 MR=4 会怎样？
- 实验：把 `i += 8` 改 `i += 4`，删掉 c4..c7
- 解释：<details>约 20 GFLOPS（只用 2 FVU）。MR=4 时累加器不够多，FVU 利用率下降。</details>

---

## 7. 陷阱

1. **不绑核/不锁频**：DVFS + 调度漂移会让 v5_mr8 测出 30-45 GFLOPS 的随机波动。必须 `taskset -c 0` + `cpupower frequency-set -g performance`
2. **编译器优化掉 pack**：如果 pack 后的 Bb 没被读取，编译器会删掉整个 pack。`escape(Bb)` 或确保读它
3. **尾部处理**（第 123-140 行）：M=1024 是 8 倍数不会触发，但通用代码必须处理 M%8≠0 的尾巴行
4. **本文件已用 `posix_memalign`**（第 161 行）——其他算子（如 gemm_s8）还在用 malloc，是 P0 技术债

---

## 8. 这一步的盲区（诚实段）

- **没有 KC 分块**：当前 K=1024 全部在内循环，如果 K 很大（如 4096+），A 的子块会溢出 L1。生产级 GEMM（如 OpenBLAS）会做三层分块（MC×KC×NC）。本项目简化了
- **没有 prefetch**：性能架构师 lens 指出，加 `__builtin_prefetch` 还能 +5-8%
- **pack 代价未摊销**：本文件每次 GEMM 都重新 pack B，生产场景应缓存 pack 后的 B

---

## 9. 练习题

1. 把 MR=8 改成 MR=16，跑一下，观察是否变慢。用 `objdump -d` 看有没有栈溢出（`str q_reg, [sp, ...]`）
2. 在 k 循环里加 `__builtin_prefetch(&A[(i+0)*K+k+64], 0, 1)`，看性能变化
3. 画出 MR=8 时，4 FVU 怎么分配 8 个累加器的（提示：每个 FVU 分 2 个累加器）
4. 量一下 `pack_B_blk` 本身耗时占 GEMM 总耗时的比例

---

## 参考
- *Anatomy of High-Performance Matrix Multiplication* (Goto & Van de Geijn, 2008) — GEMM 分块圣经
- [`扩展专题.md`](../扩展专题.md) §1（NEON）+ §5（4 FVU 推导）
- [`isa_reference/v8.0_asimd.md`](../isa_reference/v8.0_asimd.md)（vfmaq 指令详情）
- [`项目宪法.md`](../项目宪法.md) §5（D3000 实测锚点）
