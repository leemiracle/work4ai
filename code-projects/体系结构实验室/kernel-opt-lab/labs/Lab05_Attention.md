# Lab05 — Flash Attention：online softmax 与 NEON 分块

> 源文件：[`src/attention_neon.c`](../src/attention_neon.c)（313 行）+ [`src/attention.c`](../src/attention.c)
> 阶段：学习路径 §5
> 目标成绩：**单核 NEON Flash 6.58× / 8 核 16× vs Naive**

---

## 0. 学习目标

- Attention 为什么是 LLM 的性能瓶颈？（N² softmax）
- Naive 为什么慢？（实例化整个 N×N 矩阵，爆 L2）
- Flash Attention 的核心：**online softmax**（不实例化完整矩阵）
- NEON 怎么加速内积和 softmax？

---

## 1. Attention 数学

$$\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d}}\right) V$$

- $QK^T$：N×N 矩阵（N=1024 时 4MB）
- softmax：逐行归一化
- 乘 V：N×d 输出

FLOPS ≈ $4 N^2 d$（N=1024, d=64 时约 268 MFLOP）。

---

## 2. Naive 为什么慢（`attention_naive_scalar`，第 54-79 行）

```c
float *S = malloc(N * N * sizeof(float));   // ★ 实例化整个 N×N = 4MB
for (i, j) S[i][j] = dot(Q[i], K[j]) * SCALE;  // BMM1
// softmax(S[i])                                // 3 遍 N
for (i, d) O[i][d] = sum_j S[i][j] * V[j][d];   // BMM2
```

**瓶颈**：N=1024 时 S 是 4MB，**爆 L2（512KB）**，每次访问 S 都要回 DRAM。即使算得快，访存拖死。

---

## 3. Flash Attention 的核心：online softmax（`attention_flash_neon`，第 86-168 行）

### 3.1 关键思想

**不实例化完整 N×N 矩阵**。把 Q 和 K 分块（Br × Bc），每次只算一个小块 S_blk（Br×Bc），算完立即累加到 O，然后**丢弃 S_blk**。

### 3.2 online softmax 难点

标准 softmax 要先知道整行 max。但分块时，后面的块可能改变前面的 max。

**解法**：维护**运行中的 max（m_vec）和 sum（l_vec）**，每来一个新块就 rescale 旧结果：

```c
for (kj = 0; kj < N; kj += Bc) {          // K 分块
    // BMM1: S_blk = Q[qi..] · K[kj..]^T
    // m_new = max(m_vec, rowmax(S_blk))   ← 更新全局 max
    // scale_old = exp(m_vec - m_new)      ← 旧结果要缩放
    // O_blk *= scale_old                  ← rescale 旧 O
    // O_blk += softmax(S_blk) × V[kj..]   ← 累加新块（BMM2）
    // l_vec = l_vec * scale_old + row_sum ← 更新全局 sum
    m_vec = m_new;
}
O_blk /= l_vec;   // 最终归一化
```

**数学保证**：$O_i = \frac{\sum_j \text{softmax}(S_{ij}) V_j}{\sum_j \text{softmax}(S_{ij})}$，分块累加 + rescale 后与整体 softmax 代数等价（Dao 2022 证明）。

### 3.3 为什么快？

- S_blk（Br×Bc）很小（如 64×64 = 16KB），**装 L1**
- O_blk（Br×d）常驻寄存器/L1
- 永远不回访 DRAM 里的完整 N×N

---

## 4. NEON 加速点

### 4.1 内积（第 107-113 行）

```c
/* Q[i] · K[j]，d=64 → 16 次 NEON fma */
float32x4_t acc = vdupq_n_f32(0);
for (int kk = 0; kk < D; kk += 4) {
    float32x4_t q4 = vld1q_f32(&q_row[kk]);
    float32x4_t k4 = vld1q_f32(&k_row[kk]);
    acc = vfmaq_f32(acc, q4, k4);     // 4 lane fma
}
S_blk[i*Kb+j] = vaddvq_f32(acc) * SCALE;  // 横向加 4 lane + 缩放
```

### 4.2 BMM2 累加（第 144-149 行）

```c
for (int d = 0; d < D; d += 4) {
    float32x4_t o4 = vld1q_f32(&O_blk[i*D + d]);
    float32x4_t v4 = vld1q_f32(&v_row[d]);
    o4 = vfmaq_n_f32(o4, v4, p);      // O += p × V，4 lane 并行
    vst1q_f32(&O_blk[i*D + d], o4);
}
```

### 4.3 多核（`attention_flash_neon_omp`，第 171-239 行）

```c
#pragma omp parallel for num_threads(nthreads) schedule(static)
for (int qi = 0; qi < N; qi += Br) {   // Q 行并行，各核独立
    // 每个 qi 块互不依赖 → 完美并行
}
```

---

## 5. 跑法

```bash
make attention_neon && ./bin/attention_neon
```

预期（head_dim=64）：
```
  N    | Naive ms | NEON ms | 加速比 | 多核(8) ms | 多核加速
  1024 |   154    |   23.4  |  6.58× |    9.6     |  16.0×
```

---

## 6. 假设 → 实验 → 解释

**假设 A**：Naive 慢是因为算的多？
- 解释：<details>❌ 算量一样。慢是因为 N×N 矩阵爆 L2，访存主导。Flash 把工作集压进 L1。</details>

**假设 B**：Bc（K 块大小）越大越好？
- 解释：<details>❌ Bc 太大 → S_blk 爆 L1；太小 → 分块开销 + rescale 次数多。Bc=64 是 L1 适配甜点。</details>

---

## 7. 陷阱

1. **online softmax 的 rescale 不能漏**：忘 `O_blk *= scale_old` 会导致结果错（数值炸）
2. **exp 数值稳定**：必须减 max（`expf(S - m_new)`），否则溢出
3. **多核正确性**：各 qi 块独立，但 O_blk 是 thread-local（不能共享）。本项目已用 P1-9 修复验证（第 293-301 行）
4. **本文件用 malloc**（kl_xmalloc），不是 posix_memalign → P0 技术债

---

## 8. 这一步的盲区（诚实段）

- **无 causal mask**：LLM 解码要因果 mask（下三角），本项目未实现（算法科学家 lens P0）
- **无 KV-cache**：LLM 逐 token 解码要缓存 K/V，本项目每次全算
- **exp 用标量 expf**：生产级应用查表或多项式逼近（快 3-5×）
- **Br/Bc 未调优**：固定 64×64，不同 N 的最优点不同

---

## 9. 练习题

1. 加 causal mask（`if (kj+j > qi+i) S_blk[...] = -INFINITY`），测 LLM 解码场景
2. 实现 KV-cache：第二次算时复用之前的 K/V，只追加新 token
3. 把 `expf` 换成快速逼近（如 `expf_fast = 2^(x * 1.4427)` 用位操作），测精度/速度权衡
4. 对比 Br=32/64/128 时的性能，找到 L1 适配甜点

---

## 参考
- *FlashAttention: Fast and Memory-Efficient Exact Attention* (Dao et al., 2022) — online softmax 原论文
- [`src/attention.c`](../src/attention.c) — Naive 基线
- [`docs/lenses/02-algorithm-scientist.md`](../docs/lenses/02-algorithm-scientist.md)（causal + KV-cache 待办）
