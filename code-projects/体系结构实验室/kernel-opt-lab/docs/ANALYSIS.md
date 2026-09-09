# 瓶颈分析报告 — bench_gemm 1024³ FP32

> 日期：2026-06-29（v0.3 重大更新）
> 目标：定位 `gemm_f32` 在 D3000 单核上的真实瓶颈
> 方法：完整 PMU 统计 + 对比实验 + 正确性验证

---

## TL;DR（v0.3 更新）

| 项 | 原 bench_gemm.c | 修正后（v4）|
|---|---|---|
| 1024³ FP32 实测 | 9.27 GFLOPS | **19.59 GFLOPS** |
| 算法正确性 | ❌ 64/64 错 | ✅ PASS |
| 理论峰值（分母）| 40 GFLOPS ❌ | 20 GFLOPS（dual FVU）|
| 真实利用率 | N/A（算法错）| **97.9% of 20** |

**两层 bug 都已修复**：
1. 分母 bug：4 处 single FVU 分母填了 dual FVU 数字
2. **算法 bug**：`vfmaq_laneq` / `vdotq_laneq` 的 a/b 角色错位，算的是外积不是内积

→ 详见 [`SHARE.md`](SHARE.md) 的完整调查故事。

---

## 1. 分母 bug 是怎么发现的

### 1.1 Raw throughput 验证（消除访存干扰）

`bench_*_raw` 函数纯寄存器计算（无 load/store），结果：

```
SDOT raw       79.70 GOPS    ← 理论 80（dual FVU），吻合
FMLA F16 raw   39.94 GFLOPS  ← 理论 40，吻合
FMLA F32 raw   19.98 GFLOPS  ← 理论 20，吻合
```

→ D3000 单核**真实峰值**：FP32 dual FVU = 20 GFLOPS（不是 40）

### 1.2 `gemm_f32` 内层循环分析

```c
for (int k = 0; k < K; k += 4) {
    float32x4_t a0 = vld1q_f32(&A[i*K+k]);
    float32x4_t b0..b3 = vld1q_f32(...);   // 4 次 load
    c0 = vfmaq_laneq_f32(c0, a0, b0, 0);  // ┐
    c0 = vfmaq_laneq_f32(c0, a0, b1, 1);  // │
    c0 = vfmaq_laneq_f32(c0, a0, b2, 2);  // │ 4 次 FMLA
    c0 = vfmaq_laneq_f32(c0, a0, b3, 3);  // ┘ 全部累加到 c0
}
```

**关键**：4 次 FMLA 全部依赖 `c0`（RAW 依赖链），所以即使微架构支持 dual FVU，**实际只用 1 个**。
- 4 MAC/cycle × 2.5 GHz = **10 GFLOPS**（single FVU 真实峰值）

→ bench_gemm.c 第 423 行 `peak_gflops = 16.0 * 2.5` = 40 是错的（应该是 4 × 2.5 = 10）

---

## 2. 完整 PMU 数据（1024³ FP32 single FVU）

```
                 值             含义
cycles           2.84G          总周期
instructions     4.05G          总指令
IPC              1.43           insn/cycle（D3000 上限约 4）
stalled-backend  51.62%  ←★★★  后端（执行+访存）停顿
stalled-frontend 0.11%          前端 OK
L1D refill/access 5.1%          L1 命中良好
L2D refill/access 20.1%  ←★★   L2 命中一般
L3D refill/access 7.3%          部分流量打 DDR
branch-misses    17K            几乎没有
L1d TLB refill  5.3M            可接受
L2d TLB refill  29K             可接受
```

### 2.1 解读

1. **前端 OK**（0.11%）→ 不是取指瓶颈
2. **分支 OK**（17K misses）→ 不是预测失败
3. **后端 51.62% 停顿** → **真瓶颈**，等数据
4. **L2 miss 20%** → 数据布局没优化好，跨步访问破坏 cache line
5. **L3 miss 7.3%** → 部分流量打到 DDR，引发长延迟

---

## 3. 验证：dual FVU 能拿多少

### 3.1 实现

仿照已有的 `gemm_s8_sdot_dual`，把 M 维度并行 2 个独立累加器：

```c
float32x4_t c0 = vdupq_n_f32(0);
float32x4_t c1 = vdupq_n_f32(0);    // 新增
for (int k = 0; k < K; k += 4) {
    float32x4_t a0 = vld1q_f32(&A[(i+0)*K+k]);
    float32x4_t a1 = vld1q_f32(&A[(i+1)*K+k]);  // 新增
    float32x4_t b0..b3 = vld1q_f32(...);
    c0 = vfmaq_laneq_f32(c0, a0, b0, 0);   // c0、c1 独立
    c1 = vfmaq_laneq_f32(c1, a1, b0, 0);   // → 打破 RAW 链
    ... // 共 8 次 FMLA，但 b 只 load 4 次
}
```

**核心**：相同访存量，2× 计算量。

### 3.2 结果

| M | K | N | single GF | dual GF | speedup |
|---|---|---|---|---|---|
| 128 | 1024 | 128 | 10.15 | **19.76** | **1.95×** |
| 256 | 1024 | 256 | 9.81 | 19.07 | 1.94× |
| 512 | 1024 | 512 | 9.75 | 18.84 | 1.93× |
| 1024 | 1024 | 1024 | 9.21 | **17.61** | **1.91×** |

### 3.3 PMU 对照（dual 版）

```
IPC              1.43 → 1.62       ← 提升（指令并行度变高）
stalled-backend  51.62% → 51.06%   ← 几乎不变
L2D refill       137M → 195M       ← 略增（多了 a1 load）
```

→ **stall 比例没变**（数据通路还是那个），但**有效吞吐翻倍**。

---

## 4. 真正的天花板在哪

### 4.1 计算上限

```
4 MAC/cyc  (single FVU) × 2.5 GHz = 10 GFLOPS
8 MAC/cyc  (dual FVU)   × 2.5 GHz = 20 GFLOPS
```

→ 实测 17.61 GFLOPS = 88.1% dual FVU 峰值，还有 ~11% 提升空间。

### 4.2 访存上限（Roofline 视角）

```
D3000 单核 L3 带宽 ≈ 30-40 GB/s（实测需要单独 benchmark）
DDR 带宽 ≈ 25.6 GB/s（D3000 双通道 DDR4-3200）

FP32 GEMM 算术强度 = 2MNK / (4(MK+NK+MN)) bytes
1024³ 算术强度 = 2×1024³ / (4×3×1024²) = 1024/6 ≈ 171 FLOP/byte

→ 算术强度远高于拐点，是计算 bound，不是访存 bound
```

→ 结论：**1024³ 已经是计算瓶颈**，访存优化空间不大。但小矩阵（128³）会变成访存 bound。

### 4.3 微架构潜力（参考 FTC662 文档）

D3000 FTC662 在 4-wide 超标量基础上：
- 2 ALU/cycle
- 2 NEON FMLA/cycle（dual FVU）
- 2 load/store/cycle

→ `gemm_f32_dual` 已经接近 NEU 满载。再往上要靠：
- **同时让 LSU 也在工作**（prefetch / 软件流水线）
- **减少不必要的指令**（指令选择 / 内联汇编）

---

## 5. 下一步优化方向

| # | 方向 | 预期收益 | 难度 | 风险 |
|---|---|---|---|---|
| 1 | **B 矩阵块布局** | 1.1-1.3× | 中 | 改数据布局 API |
| 2 | **软件预取** | 1.05-1.1× | 低 | prefetch 时机难调 |
| 3 | **多核 OpenMP** | 4-8×（核数）| 低 | 跨核 cache 同步 |
| 4 | **手写微内核汇编** | 1.1-1.2× | 高 | 维护成本 |
| 5 | **JIT / 自适应** | 复杂场景大收益 | 极高 | 工程量大 |

**建议组合**：1 + 2 + 3，预计能把 1024³ 推到 19-20 GFLOPS（dual FVU 极限）。

---

## 6. 修复记录

### 6.1 已修复（2026-06-29）

| 文件 | 行 | 修改 |
|---|---|---|
| `bench_gemm.c` | 316 | INT8 single 分母 32 → 16（peak 40 GOPS）|
| `bench_gemm.c` | 365 | FP16 single 分母 16 → 8（peak 20 GFLOPS）|
| `bench_gemm.c` | 389 | FP32 small 分母 16 → 4（peak 10 GFLOPS）|
| `bench_gemm.c` | 423 | FP32 large 分母 16 → 4（peak 10 GFLOPS）|
| `bench_gemm.c` | +167 | 新增 `gemm_f32_dual` 函数（双累加器）|
| `bench_gemm.c` | +507 | 新增 Large GEMM single-vs-dual 对比段 |

### 6.2 待办

- [ ] B 矩阵块布局（gemm_f32_dual_blocked）
- [ ] 软件预取（gemm_f32_dual_prefetch）
- [ ] 多核 OpenMP 版本
- [ ] 单元测试：dual vs single 数值一致性校验

---

## 附：复现命令

```bash
cd /data/usershare/ai/飞腾/kernel-opt-lab

# 1. 编译
./scripts/build.sh

# 2. 看 dual FVU 加速比
./bin/bench_f32_dual

# 3. 完整 PMU 分析
./scripts/pmu-stat.sh ./bin/bench_only_large

# 4. trace 火焰图
./scripts/run-perfetto.sh ./bin/bench_gemm
```
