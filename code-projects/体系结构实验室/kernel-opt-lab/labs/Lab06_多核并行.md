# Lab06 — 多核并行：从 57% 到 92% 效率的关键一跃

> 源文件：[`src/multicore_tiled.c`](../src/multicore_tiled.c)（190 行）+ [`src/multicore.c`](../src/multicore.c)
> 阶段：学习路径 §6（关键突破点）
> 目标成绩：**4 核 MC×NC 分块 143 GFLOPS（92.4%），flat 只有 57%**

---

## 0. 学习目标

- flat 多核为什么只有 57% 效率？
- MC×NC 分块怎么解决？分块大小怎么选？
- 为什么 `OMP_PROC_BIND=close` 在 D3000 上反而慢（反直觉！）？

---

## 1. 问题：flat 并行的 57% 之谜

### 1.1 flat 思路（`gemm_flat`，第 91-95 行）

```c
static void gemm_flat(const float *A, const float *B_blk, float *C, int nthreads) {
    #pragma omp parallel for num_threads(nthreads) schedule(static)
    for (int i = 0; i < N; i += 8)       // 8 核各抢几行
        gemm_mr8_sub(&A[i*N], B_blk, &C[i*N], 8, N, N, N);
}
```

看起来很合理：每个核算 C 的若干行，互不干扰。**预期 8 核 ≈ 8× 单核 ≈ 316 GFLOPS**。

### 1.2 实测打脸

```
线程 | GFLOPS | 效率
  1  |  39    | 100%
  4  |  ~94   | 60%   ← 远低于预期 4×
  8  | ~170   | 57%   ← 灾难
```

---

## 2. 真因诊断：L3 双段

D3000 的 L3 是 **8MB 共享，但分两段**（硬件专家 lens 发现）：
- 核 0-3 共享一段 4MB
- 核 4-7 共享另一段（跨段访问走 ring/bus，延迟翻倍）

flat 并行时，每个核写 C 的不同行，但 **C 整体是 1024×1024×4 = 4MB**，8 核同时写 → C 反复在各核 L3 间弹来弹去（cache 一致性流量爆炸）。

**OS 专家盲区⑥**：flat 模式下 8 核的 C 工作集超 L3 容量，应做 MC×NC 分块。

---

## 3. 解法：MC×NC 分块（`gemm_tiled`，第 99-136 行）

### 3.1 核心思想

不让每个核乱抢行，而是**把 C 切成方块**，每个核独占一块：

```c
for (int ic = 0; ic < N; ic += MC) {           // M 维分块，MC=256
    int MC_now = ...;
    #pragma omp parallel for num_threads(nthreads) schedule(static)
    for (int ii = 0; ii < MC_now; ii += 8) {   // 块内并行
        gemm_mr8_sub(&A[(ic+ii)*N], Bb, &C[(ic+ii)*N], ...);
    }
}
```

### 3.2 分块大小怎么选？

- **MC=256**：每块 C = 256×256×4 = 256KB → 装进 L2（512KB）
- **NC=1024**（全宽）：B 子块 = 1024×1024×4 = 4MB → 装进 L3 一段
- 关键：**同一时刻所有核在同一 MC 块内**，它们的 C 工作集都在同一段 L3 里，跨段流量消失

### 3.3 实测翻身

```
线程 | flat GFLOPS | tiled GFLOPS | tiled 效率
  1  |    39       |    39        |  100%
  2  |    ~75      |    ~76       |  97%
  4  |    ~94      |   143        |  92%   ← 翻盘
  8  |   ~170      |   ~170       |  ~57%  ← 8 核仍受 L3 双段限
```

> **4 核 tiled 143 GFLOPS 是本项目最高纪录**（v0.9）。8 核没进一步提升是因为核 4-7 跨段，但 4 核已经把一段 L3 用满。

---

## 4. 关键代码细节

### 4.1 tail 安全修复（第 110-132 行）

```c
if (M_sub == 8)
    gemm_mr8_sub(...);       // 正常 8 行
else {
    /* tail：标量兜底，避免静默错误 */
    // 原代码 if(M_sub==8) 跳过 tail → 奇数 MC_now 时尾部行静默错误
}
```

> 安全专家 lens 盲区③发现的 bug：奇数行被静默跳过。本项目 v0.9 已修。

### 4.2 B 预 pack（第 102-103 行）

```c
float *Bb = kl_xmalloc(N * N * sizeof(float));
pack_B_sub(B, Bb, 0, N, N);   // 复用 Lab01 的 pack 布局
```

> 注意：这里用 `kl_xmalloc`（malloc），**不是 posix_memalign**——是 P0 技术债。多核场景下对齐更关键（跨核 cache line 对齐）。

---

## 5. 反直觉发现：OMP_PROC_BIND=close 反而慢

通用建议说 `OMP_PROC_BIND=close`（紧凑绑核）对计算密集型好。**但在 D3000 上实测反而慢！**

原因：D3000 拓扑特殊（L3 双段），`close` 把核 0-3 绑一段、4-7 绑另一段，跨段一致性开销大。而 `spread` 或不绑反而让 OS 调度器自己选最优。

**教训**（项目宪法 §7 第 10 条）：**通用 OS 调优建议必须本机验证，D3000 拓扑特殊**。

```bash
# 验证：对比两种绑定
OMP_PROC_BIND=close OMP_NUM_THREADS=4 ./bin/multicore_tiled   # 反而慢
OMP_PROC_BIND=spread OMP_NUM_THREADS=4 ./bin/multicore_tiled  # 试试
```

---

## 6. 跑法

```bash
make multicore_tiled && OMP_NUM_THREADS=4 ./bin/multicore_tiled
make multicore && OMP_NUM_THREADS=8 ./bin/multicore          # flat 对照
```

输出是 markdown 表格，可直接贴进报告。

---

## 7. 假设 → 实验 → 解释

**假设 A**：8 核 tiled 能到 8×39 = 312 GFLOPS？
- 解释：<details>❌ 不能。核 4-7 跨 L3 段，效率掉到 57%。4 核（同一段）已是最优配置。</details>

**假设 B**：MC 改成 512（更大块）会更好？
- 实验：`gemm_tiled(A, B, C, 4, 512, N)`
- 解释：<details>❌ 更差。MC=512 时每块 C = 512×256×4 = 512KB > L2(512KB)，溢出。MC=256 是 L2 适配的甜点。</details>

---

## 8. 陷阱

1. **OMP_NUM_THREADS 设超过 4 收益递减**：L3 双段是硬限制
2. **不测 flat 对照**：没有 flat 基线，看不出 tiled 的价值
3. **MC 选错**：MC 太大溢出 L2，太小并行度不够。用 [`docs/OPTIMAL-PARAMS.md`](../docs/OPTIMAL-PARAMS.md) 的推导
4. **hugepage 没开**：4MB 的 C 跨页表 TLB miss 严重。`echo always > /sys/kernel/mm/transparent_hugepage/enabled`

---

## 9. 这一步的盲区（诚实段）

- **只测了 power-of-2 线程数**：5/6/7 核的行为没探索
- **NC 没分块**：当前 NC=1024（全宽），更严谨应 NC 分块让 B 子块也装 L3
- **NUMA 未探**：多芯片场景（D3000 可多芯片）的 NUMA 效应未测

---

## 10. 练习题

1. 跑 `OMP_NUM_THREADS=4,5,6,7,8 ./bin/multicore_tiled`，画出 GFLOPS-线程数曲线，找到拐点
2. 对比 MC=128/256/512 三种分块，验证 L2 适配假说
3. 开 hugepage 后重测，看 TLB miss（用 `sudo perf stat -e dTLB-load-misses ./bin/multicore_tiled`）
4. 用 [`common/perf_stat_run.sh`](../common/perf_stat_run.sh) 测 flat vs tiled 的 cache-misses 差异

---

## 参考
- [`docs/lenses/03-os-runtime-expert.md`](../docs/lenses/03-os-runtime-expert.md)（盲区⑥的原诊断）
- [`docs/lenses/05-hardware-engineer.md`](../docs/lenses/05-hardware-engineer.md)（L3 双段结构）
- [`results/baseline.md`](../results/baseline.md)（143 GFLOPS 实测记录）
- [`项目宪法.md`](../项目宪法.md) §7 第 10 条（本机验证纪律）
