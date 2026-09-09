# Lab04 — Winograd 卷积：用换乘法把 21.5× 加速拿到手

> 源文件：[`src/conv_winograd_f44.c`](../src/conv_winograd_f44.c)（329 行）
> 阶段：学习路径 §4
> 目标成绩：**F(4,4) Winograd 21.5× vs Direct**

---

## 0. 学习目标

- 直接卷积为什么慢？
- Winograd 的数学魔术：怎么用**换乘法**降低乘法次数？
- F(4,3) 的三个变换矩阵 B^T / G / A^T 各干什么？
- 2D Winograd 怎么从 1D 推广？

---

## 1. 直接卷积为什么慢

3×3 卷积，每个输出要 9 次乘加（CIN × COUT 个通道）。56×56×64 的特征图：
```
FLOPS = 2 × 56 × 56 × 64 × 64 × 9 ≈ 232 MFLOP（单层）
```
标量直跑约 1.22 GFLOPS（0.19s）——瓶颈：im2col 前的跨步访存 + 9 个 MAC 的串行依赖。

---

## 2. Winograd F(m, r) 的数学

### 2.1 核心思想

Winograd 证明了：**计算 $y = \sum_{i=0}^{r-1} g_i \cdot d_i$（r 个乘加）可以用更少的乘法完成**，代价是额外的加法（变换）。

F(m, r)：m 个输出，r 个 kernel 元素，输入 tile = m + r - 1。

| | 直接 | Winograd F(2,3) | Winograd F(4,3) |
|--|:--:|:--:|:--:|
| 每 m 输出的乘法 | m×r = 6 | 4 | 6 |
| 理论加速 | 1× | 1.5× | **4×** |

### 2.2 F(4,3) 的三个矩阵（第 80-101 行，来自 Lavin & Gray 2016）

```c
B^T (6×6)：输入变换    d → V = B^T d B
G (6×3)：权重变换      g → U = G g G^T
A^T (4×6)：输出变换    M → Y = A^T M A
```

**四个步骤**（第 28-33 行注释）：
```
1. U = G g G^T     （权重变换，预计算一次）
2. V = B^T d B     （输入变换，每 tile 一次）
3. M = U ⊙ V       （逐元素乘，36 次/tile）
4. Y = A^T M A     （输出变换）
```

### 2.3 为什么换乘法更快？

直接卷积：16 个输出 × 9 MAC = **144 次乘法**。
Winograd F(4,4)：每 tile **36 次逐元素乘**（6×6）。
144 / 36 = **4× 理论加速**（变换开销摊到 channel 维后）。

---

## 3. 代码结构（`conv_winograd_f44.c`）

### 3.1 权重预变换（第 122-148 行，只算一次）

```c
/* U = G g G^T，每个 (oc, ic) 独立，3×3 → 6×6 */
winograd_transform_weight(weight, U);  // 推理时预计算，存起来
```

### 3.2 输入变换（第 151-168 行，每 tile 一次）

```c
/* V = B^T d B，d 是 6×6 输入 tile */
winograd_transform_input_tile(d, V);   // 两次矩阵乘
```

### 3.3 逐元素乘 + channel 聚合（第 220-225 行）

```c
for (int oc = 0; oc < COUT; oc++)
    for (int i,j)
        M_sum[oc][i][j] += U[oc][ic][i][j] * V[i][j];  // 36 次乘/tile
```

### 3.4 输出变换（第 229-235 行）

```c
winograd_transform_output_tile(M_sum[oc], Y);  // Y = A^T M A，6×6 → 4×4
```

---

## 4. F(4,4) vs F(2,3)

| | F(2,3) | F(4,3) |
|--|--------|--------|
| 输入 tile | 4×4 | 6×6 |
| 输出 tile | 2×2 | 4×4 |
| 乘法/tile | 16 | 36 |
| 理论加速 | 2.25× | **4×** |
| 实测 vs Direct | 14.8× | **21.5×** |
| 数值精度 | 好 | **较差**（变换矩阵含 1/24）|

> F(4,4) 比 F(2,3) **再快 31%**，但精度更差（tol 要放宽到 1e-2，见第 296 行）。

---

## 5. 跑法

```bash
make conv_winograd_f44 && ./bin/conv_winograd_f44
```

预期：
```
=== Winograd F(4×4, 3×3) ===
权重 F(4,3) 变换: ~0.5 ms

=== Correctness (3×3 conv 56×56×64→56×56×64) ===
  F(4,4) vs Direct           ✅ PASS (errs=0 max_diff=0.0001)

=== Performance ===
  Direct (scalar)  : ~190 ms   1.22 GFLOPS
  F(4,4) Winograd  : ~8.8 ms  26.19 GFLOPS (等效)   ← 21.5×!
```

---

## 6. 假设 → 实验 → 解释

**假设 A**：Winograd 用更多加法换乘法，为什么反而更快？
- 解释：<details>卷积是 compute-bound，乘法是瓶颈（FMA 延迟 4 cyc，加法 1 cyc）。换乘法 = 减少瓶颈指令。加法虽多但能并行。</details>

**假设 B**：F(6,3) 会比 F(4,3) 更快？
- 解释：<details>理论上是，但 F(6,3) 变换矩阵数值更大，精度更差（可能炸），且变换开销占比上升。F(4,3) 是精度/性能的甜点。</details>

---

## 7. 陷阱

1. **精度**：F(4,4) 的变换矩阵含 1/24 等小系数，FP32 还好，FP16/INT8 会炸。量化 Winograd 要特殊处理
2. **H/W 必须是 4 的倍数**（第 196 行）：否则要 padding 或 tail 处理
3. **变换没摊销**：本文件每次都重新变换权重，推理场景应缓存 U
4. **未 NEON 化**：当前变换是标量循环，生产级应向量化（+2-3×）

---

## 8. 练习题

1. 把 F(4,3) 的 A^T 矩阵改成 F(2,3) 的，观察精度变化（tol 能放到多少？）
2. 用 NEON 向量化 `winograd_transform_input_tile`（提示：6×6 矩阵乘可拆成 6 次 vmlaq）
3. 测 F(4,4) 在 CIN=COUT=128 时的加速比（通道更大时变换摊销更好）
4. 用 INT8 实现 Winograd（注意变换的数值范围，可能需要 INT32 中间值）

---

## 参考
- *Fast Algorithms for Convolutional Neural Networks* (Lavin & Gray, 2016) — Winograd 原论文
- [`src/conv_winograd.c`](../src/conv_winograd.c) — F(2,3) 对照版
- [`src/conv_winograd_int8.c`](../src/conv_winograd_int8.c) — INT8 版（未挂 Makefile）
