# Lab02 — 数据类型扩展：INT8 点积与 FP16 反直觉陷阱

> 源文件：[`src/gemm_s8.c`](../src/gemm_s8.c)（245 行）+ [`src/gemm_f16.c`](../src/gemm_f16.c)（309 行）
> 阶段：学习路径 §2
> 目标成绩：INT8 **77.74 GOPS（97.2%）** / FP16 **39.01 GFLOPS（78%，MR=2 而非 MR=8！）**

---

## 0. 学习目标

- INT8 + UDOT 为什么是边缘 AI 的主力？
- `vdotq_s32` 微内核的"A 复制成 16 字节"技巧
- **反直觉**：FP16 为什么 MR=8 反而比 MR=2 慢？
- FP16 累加精度 bug 是什么？

---

## 1. INT8 GEMM（`gemm_s8.c`）

### 1.1 为什么 INT8？

| 数据类型 | 每向量 lane 数 | D3000 峰值 | 数据量（vs FP32）|
|---------|:------------:|:---------:|:---------------:|
| FP32 | 4 | 40 GFLOPS | 1× |
| FP16 | 8 | 50 GFLOPS | 1/2 |
| **INT8** | **16** | **80 GOPS** | **1/4** |

边缘 AI 内存带宽紧张，INT8 数据量是 FP32 的 1/4，峰值还翻倍——双倍收益。

### 1.2 UDOT 指令

```c
int32x4_t vdotq_s32(int32x4_t c, int8x16_t a, int8x16_t b);
// c[i] += sum_{m=0..3} a[i*4+m] × b[i*4+m],  for i=0..3
// 一条指令 = 16 次乘加！
```

### 1.3 "A 复制成 16 字节"技巧（第 64-71 行）

`vdotq` 要求 a 和 b 都是 16 字节（16 个 INT8）。但 A 的一行在 k 维只有 4 个 INT8，怎么填满 16 字节？

```c
int32x2_t a2 = vld1_s32((const int32_t*)&A[i * K + k]);  // 取 4 字节（1 个 int32）
int32x4_t a4 = vdupq_lane_s32(a2, 0);                    // 广播成 16 字节（4 个相同 int32）
int8x16_t a16 = vreinterpretq_s8_s32(a4);                // 重解释为 16 个 INT8
int8x16_t b_blk = vld1q_s8(&b_base[k * 4]);              // B 的 4×4 块（4 个 j × 4 个 k）
c0 = vdotq_s32(c0, a16, b_blk);                          // 一次算 4 个 j 的点积
```

**关键洞察**：把 A 的 4 字节复制 4 次 → 和 B 的 4×4 块做点积 → 一次得到 4 个输出。这是 INT8 GEMM 的标准技巧。

### 1.4 v5_mr8（第 104-157 行）

和 Lab01 的 FP32 同理：8 个累加器 c0..c7（int32x4_t），喂满 4 FVU。寄存器：8(c) + 8(a16) + 1(b_blk) = 17 个，够用。

实测 **77.74 GOPS（97.2% of 80）**——D3000 上效率最高的算子。

---

## 2. FP16 GEMM 的反直觉陷阱（`gemm_f16.c`）

### 2.1 理论预期

FP16 每向量 8 lane（vs FP32 的 4 lane）→ 理论峰值 = 4 FVU × 2.5GHz × 8 lane × 2 = **50 GFLOPS**。
按 Lab01 的逻辑，MR=8 应该最优。

### 2.2 实测打脸（v0.8 重大发现）

| MR | 实测 GFLOPS | 利用率 |
|:--:|:----------:|:------:|
| 2 | **39.01** | 78% |
| 8 | 35 | 70% ← **反而慢！** |

### 2.3 真因

D3000 单条 `vfmaq_laneq_f16` 指令的**实际吞吐 < 4/cyc**。4 FVU × 8 lane 是理论值，但单条 FP16 FMA 指令在 D3000 上只能发 1-2 条/周期（FVU 的 FP16 通路有瓶颈）。MR=8 时代码依赖 8 个累加器的 FMA 链，但指令发射速度跟不上，反而被 stall 拖累。

**结论**：
- FP32/INT8 → 用 MR=8（4 FVU 全开）
- FP16 → 用 MR=2（避开吞吐瓶颈）

> 这是本项目最重要的反直觉发现之一。**通用架构假设（lane 多就快）在具体芯片上必须实测验证。**

### 2.4 FP16 累加精度 bug（算法科学家 lens）

FP16 只有 10 位尾数，直接累加 K=1024 个 FP16 乘积会严重丢精度（大数吃小数）。

**正确做法**：FP16 输入 → **FP32 累加** → FP16 输出。
```c
// ❌ 错：float16x8_t 累加器
// ✅ 对：用 fp32 累加，最后转回 fp16
float32x4_t acc_f32 = vcvtf32_f16(...);  // 提升
// ... FP32 FMA 累加 ...
float16x8_t out = vcvtf16_f32(acc_f32);  // 降回
```

本项目 `gemm_f16.c` 的 v4_dual 部分处理了，P0 待彻底统一。

---

## 3. 跑法

```bash
make gemm_s8 && ./bin/gemm_s8          # INT8，看 77.74 GOPS
make gemm_f16 && ./bin/gemm_f16        # FP16，对比 MR=2 vs MR=8
```

---

## 4. 假设 → 实验 → 解释

**假设 A**：INT8 峰值 80 = FP32 峰值 40 的 2 倍？
- 解释：<details>✅ 对。INT8 每 16 lane（vs FP32 的 4 lane），4 FVU × 16 × 2.5G × 2 = 80 GOPS。</details>

**假设 B（反直觉）**：FP16 lane 数是 FP32 的 2 倍，所以 FP16 MR=8 比 FP32 MR=8 快？
- 解释：<details>❌ FP16 MR=8（35）比 FP32 MR=8（39.45）还慢！FP16 FMA 指令吞吐瓶颈 + 累加精度问题双重原因。FP16 在 D3000 上是"理论美、实测坑"。</details>

---

## 5. 陷阱

1. **FP16 照搬 FP32 的 MR=8 经验** → 反而慢。必须实测
2. **INT8 累加用 int32** → 正确（vdotq 输出 int32）。但要注意溢出（K=1024 × 127² ≈ 1.6e7 < 2³¹，安全）
3. **gemm_s8.c 用 malloc 不是 posix_memalign** → P0 技术债
4. **D3000 不支持 I8MM**（v8.6 `SMMLA`），只能用 UDOT 手动实现。详见 [`扩展专题.md`](../扩展专题.md) §6

---

## 6. 练习题

1. 在 `gemm_s8.c` 里把累加器从 int32 改成 int16，观察溢出（K 多大时炸？）
2. FP16：实测 MR=4，画出 MR=1/2/4/8 的 GFLOPS 曲线，找到真实最优点
3. 用 FP32 累加重写 FP16 GEMM 的微内核，对比精度（max_diff）
4. 用 [`common/perf_stat_run.sh`](../common/perf_stat_run.sh) 对比 INT8 vs FP32 的 IPC

---

## 参考
- [`扩展专题.md`](../扩展专题.md) §2（FP16 陷阱）+ §3（UDOT）+ §6（缺失的 I8MM/BF16）
- [`isa_reference/v8.4_dotprod.md`](../isa_reference/v8.4_dotprod.md)
- [`isa_reference/v8.2_fp16.md`](../isa_reference/v8.2_fp16.md)
- [`docs/lenses/02-algorithm-scientist.md`](../docs/lenses/02-algorithm-scientist.md)（FP16 累加 bug 原诊断）
