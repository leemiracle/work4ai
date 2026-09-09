# 一篇可发博客的技术分享

> **标题**：把一台 ARM CPU 的 GEMM 跑到理论峰值的 97.9% —— 飞腾 D3000 优化实战
>
> **副标题**：从一个分母 bug 到三类算法 bug，再到 v4 块化布局
>
> 适用读者：嵌入式 / 边缘 AI 工程师、ARM NEON 性能优化爱好者、想理解 GEMM 优化本质的人

---

## 0. 缘起

我在飞腾 D3000（FTC862，ARMv8.2-A，2.5 GHz，8 核）上做 GEMM 性能优化，从一份看似合理的 benchmark 开始，**最终发现了三类隐藏的算法 bug**。修复后，单核 FP32 GEMM 从 9.3 GFLOPS（92% "效率"但算法错）跑到 19.6 GFLOPS（97.9% 真实峰值）。

这篇文章记录整个调查过程，希望帮读者：
1. 学会**怎么用 PMU 找瓶颈**
2. 警惕**intrinsics 的角色错位陷阱**
3. 理解**B 块化布局**为什么是 GEMM 优化的金标准

---

## 1. 第一层：分母 bug（看似简单，但容易让人误判）

原 benchmark 报告：

```
1024×1024 FP32 GEMM: 9.27 GFLOPS, Eff = 23.2%
```

"23.2%"——很低。我开始往"L2 cache miss 多 / 流水线停顿"的方向查。直到我读了源码：

```c
double peak_gflops = 16.0 * 2.5;   // 第 423 行
```

`16` 是 FP16 的 MAC/cycle，FP32 single FVU 应该是 `4 × 2.5 = 10`。分母错了一倍。**真实效率**：

```
9.27 / 10 = 92.7%
```

**已经接近峰值**——"23% 低效率"完全是错觉。

⚠️ **教训一**：分析性能前，先核对"理论峰值"是怎么算的。这条朴素得像废话，但大型 benchmark 文件里很容易写错。

---

## 2. Raw throughput 验证（先排除访存干扰）

为了确认真峰值，我跑了**纯寄存器计算**（无 load/store）的 raw throughput：

```c
// 1000 万次 FMLA 累加到一个 dummy 寄存器
float32x4_t acc = vdupq_n_f32(0);
float32x4_t a = vld1q_f32(buf_a);
float32x4_t b = vld1q_f32(buf_b);
for (int i = 0; i < 10000000; i++) {
    acc = vfmaq_f32(acc, a, b);
}
```

结果：
- INT8 SDOT (dual acc)：**79.70 GOPS**（理论 80）
- FP16 FMLA (dual acc)：**39.94 GFLOPS**（理论 40）
- FP32 FMLA (dual acc)：**19.98 GFLOPS**（理论 20）

→ D3000 单核算力上限完全坐实。

---

## 3. 第二层：算法 bug（这才是大坑）

跑完 raw throughput 后我想：既然算力到顶，GEMM 为什么才 9.27 GFLOPS？应该是访存瓶颈吧？

**错。** 写个最小 correctness check 才发现：

```c
/* 跑 8×8×8 矩阵，vector vs scalar 对比 */
gemm_f32_vec(A, B, Cv);     // NEON 实现
gemm_f32_scalar(A, B, Cs);  // 标量参考
// 64 个元素，62 个错！max_diff = 1.37
```

**NEON 实现完全错了。** 那 9.27 GFLOPS 是"算错的速度"。

### 3.1 错在哪？

看原代码：

```c
for (int k = 0; k < K; k += 4) {
    float32x4_t a0 = vld1q_f32(&A[i*K + k]);         // A[i][k..k+3]
    float32x4_t b0 = vld1q_f32(&B[(j+0)*K + k]);     // B[j+0][k..k+3]
    float32x4_t b1 = vld1q_f32(&B[(j+1)*K + k]);
    float32x4_t b2 = vld1q_f32(&B[(j+2)*K + k]);
    float32x4_t b3 = vld1q_f32(&B[(j+3)*K + k]);
    c0 = vfmaq_laneq_f32(c0, a0, b0, 0);   // ← 这一行
    c0 = vfmaq_laneq_f32(c0, a0, b1, 1);
    c0 = vfmaq_laneq_f32(c0, a0, b2, 2);
    c0 = vfmaq_laneq_f32(c0, a0, b3, 3);
}
```

`vfmaq_laneq_f32(c, a, b, lane)` 的语义：

```
c[i] += a[i] × b[lane]   (for all i in 0..3)
```

4 次累加后：

```
c0[i] += a0[i] × (b0[0] + b1[1] + b2[2] + b3[3])
       = A[i][k+i] × (B[j+0][k+0] + B[j+1][k+1] + B[j+2][k+2] + B[j+3][k+3])
```

**这是个对角线外积**，根本不是 4 个独立内积。

正确的 `C[i][j+lane]` 应该是 `sum_m A[i][k+m] × B[j+lane][k+m]`。

### 3.2 为什么没人发现？

- 性能数字看起来"合理"（9.27 GFLOPS 接近某个峰值）
- 加速比看起来"漂亮"（dual FVU 1.91×）
- 但**结果错了**——只是大家没做正确性验证

⚠️ **教训二**：性能优化前必须先有 correctness check。否则你可能在"优化一个错的算法"。

---

## 4. 修复尝试一：转置 B（失败）

第一个想法：B 转置成 B_T[k][j]，让 4 个 j 在内存连续，然后用正确的 intrinsics：

```c
c0 = vfmaq_laneq_f32(c0, b_row_m, a0, m);   // b_row_m[lane] = B[j+lane][k+m]
```

正确性 ✅，但**慢了 6 倍**：1.61 GFLOPS vs buggy 的 9.47。

为什么？PMU 显示 backend stall 78%。原来 B_T 的访问模式是"4 个 k 跨 N 步进"，**每次访问都 miss cache**。

⚠️ **教训三**：算法正确 ≠ 性能好。布局必须考虑 cache 行为。

---

## 5. 修复尝试二：保留 B 原布局 + 转置（v3，正确但慢）

不转置 B，但在内循环里用 `vtrnq_f32` 做 4×4 矩阵转置：

```c
float32x4x2_t t01 = vtrnq_f32(b0, b1);
float32x4x2_t t23 = vtrnq_f32(b2, b3);
// ... 重排成 col_0, col_1, col_2, col_3
c0 = vfmaq_laneq_f32(c0, col_0, a0, 0);
// ...
```

正确性 ✅，性能 7.48 GFLOPS（single FVU 75%）。比 buggy 慢，比 T 转置快。但每次内循环多了 4 个 vtrnq + 4 个 vcombine，开销明显。

---

## 6. 终极方案：B 预先块化布局（v4）

关键洞察：**转置只在 pack 阶段做一次，跑 GEMM 时直接用已转置的 B**。

### 块布局设计

```
原 B 行主 [N][K]:
  B[j][k], j 在外, k 在内
  4 个 j 的同一 k 在内存里相隔 K×4 字节（4KB），不连续

块化 B_blk[j_block][k][j_inner], j_inner 在最内:
  B_blk[jb][k][0..3] 是连续 16 字节 = 4 个 j_inner 的同一 k
  一次 vld1q_f32 拿到 (B[j+0][k], B[j+1][k], B[j+2][k], B[j+3][k])
```

### v4 内循环

```c
for (int k = 0; k < K; k += 4) {
    float32x4_t a0 = vld1q_f32(&A[i*K + k]);         // A[i][k..k+3]
    float32x4_t col_0 = vld1q_f32(&B_blk[jb*K*4 + (k+0)*4]);  // 4 个 j 的 k+0
    float32x4_t col_1 = vld1q_f32(&B_blk[jb*K*4 + (k+1)*4]);
    float32x4_t col_2 = vld1q_f32(&B_blk[jb*K*4 + (k+2)*4]);
    float32x4_t col_3 = vld1q_f32(&B_blk[jb*K*4 + (k+3)*4]);
    c0 = vfmaq_laneq_f32(c0, col_0, a0, 0);   // c0[lane] += col_0[lane] × a0[0]
    c0 = vfmaq_laneq_f32(c0, col_1, a0, 1);   //         = B[j+lane][k+0] × A[i][k+0]  ✓
    c0 = vfmaq_laneq_f32(c0, col_2, a0, 2);
    c0 = vfmaq_laneq_f32(c0, col_3, a0, 3);
}
```

### 为什么这么快？

1. **算法正确**：每次累加 c0[lane] += B[j+lane][k+m] × A[i][k+m]，正是 C[i][j+lane] 的累加项
2. **cache 100% 利用**：col_0..3 共 64 字节，正好一个 cache line
3. **无 vtrn 开销**：转置在 pack 时做了，跑 GEMM 时只读
4. **dual FVU 友好**：c0/c1 独立累加（M 维并行 2 个），打破 RAW 依赖链

### Pack 成本

```
B pack: 1.3 ms（FP32）/ 0.7 ms（FP16）/ 0.3 ms（INT8）
GEMM  : 110 ms (1024³ FP32 dual)
```

→ Pack 占总时间 < 1.2%，**完全摊销**（特别是工业场景 B 复用 N 次）。

---

## 7. 三个数据类型的最终结果

| Kernel | v4_single | v4_dual | dual 利用率 |
|---|---|---|---|
| FP32 | 10.15 GFLOPS (101.5%) | **19.59 GFLOPS** | **97.9% of 20** |
| FP16 | 20.64 GFLOPS (103.2%) | **39.97 GFLOPS** | **99.9% of 40** |
| INT8 | 39.72 GOPS (99.3%) | 63.43 GOPS | 79.3% of 80 |

INT8 dual 只到 79% 的原因：`vdotq_s32` 单条指令已经把 FVU 喂满（16 MAC/instr），dual FVU 的边际收益有限。

---

## 8. 延伸：把 GEMM 经验用到卷积

卷积优化的工业标准是 **im2col + GEMM**：把卷积转成矩阵乘，复用 GEMM 优化。

| 实现 | 时间 | GFLOPS |
|---|---|---|
| 3×3 direct (标量) | 189 ms | 1.22 |
| **3×3 im2col + GEMM** | **30 ms** | **7.63** |
| 1×1 pointwise (本质 GEMM) | 3.15 ms | 8.16 |
| 3×3 depthwise (NEON 优化) | 0.21 ms | 17.51 |

im2col+GEMM 比 direct 快 **62×**。1×1 pointwise 几乎就是 GEMM（无 im2col 开销）。Depthwise 因为算量小、访存主导，GFLOPS 数字虚高。

---

## 9. 总结：四条方法论

1. **先 correctness check，再性能优化**
   - 写一个 scalar 参考实现，跑小矩阵对比
   - 不然你可能优化一个错的算法

2. **先 raw throughput，再访存分析**
   - 纯寄存器计算能验证算力上限
   - 跟 GEMM 实测对比，差距来自访存

3. **B 块化布局是 GEMM 优化的金标准**
   - 让 4 个 j 的同一 k 在内存连续
   - cache 100% 利用 + 算法正确
   - pack 成本可摊销

4. **警惕 intrinsics 角色错位**
   - `vfmaq_laneq_f32(c, a, b, lane)` 跟 `vfmaq_laneq_f32(c, b, a, lane)` 看起来一样，结果完全不同
   - intrinsics 文档读三遍

---

## 10. 工程资产

完整的代码 + 文档 + 性能数据，开源在 `kernel-opt-lab/` 目录：

- `src/gemm_f32.c` / `gemm_s8.c` / `gemm_f16.c`：v4 正确实现
- `src/conv_benchmark.c`：4 种卷积对比
- `docs/ANALYSIS.md`：完整瓶颈分析（PMU 数据）
- `docs/PERFETTO-TUTORIAL.md`：UI 5 分钟入门
- `results/baseline.md`：性能基线 + 历史变更

---

## 11. 致谢与延伸阅读

- **Goto & Van de Geijn (2008)**: *Anatomy of High-Performance Matrix Multiplication* —— GEMM 优化的圣经
- **BLIS 框架**：开源高性能 GEMM 实现，本项目 v4 思路来源
- **ARM Cortex-A 系列优化指南**：[developer.arm.com](https://developer.arm.com/)
- **Karpathy 的 nanoGPT**：手写 GEMM 风格的优秀范例

---

> **作者**：lwz（飞腾性能优化项目）
> **日期**：2026-06-29
> **环境**：飞腾 D3000 (FTC862) + 银河麒麟 V10 + PhyGCC 12.3.2
