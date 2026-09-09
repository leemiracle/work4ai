# Lab02 — 流水线、ILP、分支预测

> "为什么一段看似一样的代码，改写一下就快 10 倍？答案藏在流水线和分支预测里。"
>
> 这是 Patterson Ch4 和姚永斌 Ch1/Ch4 的核心内容。

---

## 0. 学习目标（一句话）

**实证地理解三类冒险（数据/控制/结构）的真实代价**，并掌握**乱序执行和分支预测**如何"魔法般地"消除这些代价——以及它们的极限。

---

## 1. 对应教材与课程

| 来源 | 章节 | 重点 |
|------|------|------|
| 📘 Patterson RISC-V | **Ch4 (Pipelining)** | 经典 5 级流水线、冒险、forwarding、分支预测基础 |
| 📕 姚永斌超标量 | **Ch1 (超标量概览)** | 顺序 vs 乱序执行的本质差异 |
| 📕 姚永斌超标量 | **Ch4 (分支预测)** | 2-bit / 局部 / 全局 / 竞争预测器 |
| 📕 姚永斌超标量 | **Ch9.6 (Memory Disambiguation)** | 推测 load/store |
| 📗 CAQA 5th | **Ch3 (ILP)** | Tomasulo、ROB、Speculation 经典理论 |
| 📗 CAQA 5th | **App C** | 流水线基础（背景） |
| 🎓 CS61C | Proj3 | 用 Logisim 搭 2 级流水线 CPU |

---

## 2. 核心概念速览

### 2.1 直觉：3 类冒险

```
数据冒险 (Data Hazard):  后指令需要前指令的结果
   add x1, x2, x3
   add x4, x1, x5    ← 等 x1 准备好（RAW）

控制冒险 (Control Hazard): 分支结果未定，不知道取哪条路
   cmp x1, x2
   bne L1            ← 跳还是不跳？

结构冒险 (Structural Hazard): 多条指令争同一硬件资源
   fmul v0, v1, v2
   fmul v3, v4, v5   ← 如果只有 1 个乘法器，必须等
```

**经典 5 级流水线**：IF → ID → EX → MEM → WB

### 2.2 数学：流水线 CPI 公式

$$
\text{CPI}_{\text{actual}} = \text{CPI}_{\text{ideal}} + \sum_{k} (\text{stall rate}_k \times \text{stall cycles}_k)
$$

- 理想 CPI = 1（每周期退休 1 条指令）
- 飞腾 D3000M：4-wide 超标量，**理论 CPI 下限 = 0.25**（IPC = 4）
- 实测 IPC：从 0.01（链表追逐）到 3.99（完美可预测分支）

### 2.3 分支预测：成本与收益

**分支预测失败代价**：
$$
T_{\text{mispred}} = T_{\text{penalty}} \times \text{mispred\_rate} \times \text{branch\_frequency}
$$

飞腾 D3000M 失败代价 ≈ **15-20 cycles**（典型深流水线）。

### 2.4 一张图：乱序执行的数据流

```
        ┌────────── 重排序缓存 (ROB) ──────────┐
        │                                       │
   IF → ├─ ID → RS (Reservation Station)        │
   (取指) │      ↓  ↑                            │
   多发射 │     重命名 (Rename)                  │
   4/cyc │      ↓  ↑                            │
        │     Issue (就绪 → 执行)               │
        │      ↓                                │
        │     EX (ALU/FPU/LSU)                  │
        │      ↓                                │
        │     WB → ROB → Commit (按序退休)      │
        └───────────────────────────────────────┘
```

---

## 3. 实验列表

### 3.1 实验 2.1：数据相关 RAW/WAW/WAR（`data_hazards.c`）

**现象**：把 `a = a*a + 1` 改成 `a[i] = a[i]*a[i] + 1`，IPC 立刻涨。

**假设**：
- 依赖链版本：`x = x*x + 1` 循环 N 次，每次必须等上一次的 x，IPC < 0.5
- 独立版本：`x[i] = x[i]*x[i] + 1` 循环 N 次，可并行 N 个，IPC 接近 4

**关键代码**：
```c
// RAW 依赖链：1 个变量更新
double dep_chain(double x, int n) {
    for (int i = 0; i < n; i++) x = x*x + 1.0;
    return x;
}

// ILP 友好：N 个独立变量
double indep_chain(double *x, int n) {
    double acc = 0;
    for (int i = 0; i < n; i++) {
        x[i] = x[i]*x[i] + 1.0;  // 每次独立
        acc += x[i];
    }
    return acc;
}
```

**运行**：
```bash
make data_hazards
./data_hazards
```

**预期结果**（飞腾 D3000M）：
| 版本 | IPC | CPI | 备注 |
|------|-----|-----|------|
| dep_chain (1-dep) | 0.25 | 4.0 | fmul 4cyc + fadd 4cyc 串行 |
| dep_chain ×2 (2 vars) | 0.5 | 2.0 | 两条独立链，但仍部分阻塞 |
| dep_chain ×4 (4 vars) | 1.0 | 1.0 | 充分利用 4-wide |
| indep_chain (N vars) | 2.0-3.0 | 0.3-0.5 | 完美 ILP |

**解释**：
- 依赖链 CPI = fmul_latency + fadd_latency ≈ 4 + 4 = 8 cyc/op → 实际可能更快因为 fmadd
- 多个独立链可同时跑，IPC 随链数线性增长
- indep_chain 还有访存隐藏在计算后，IPC 受限于 load 带宽

**缺陷与陷阱**：
- 编译器可能 unroll dep_chain，把 1 个变量拆成 4 个虚拟独立变量
- 用 `volatile` 或 `asm` 强制保留依赖

**扩展思考**：
- 飞腾 D3000M 浮点 fmul 的实际 latency 是多少？（用本实验反推）

---

### 3.2 实验 2.2：分支预测（`branch_predict.c`）

**现象**：同一段 if/else，分支模式不同性能差 5-10 倍。

**假设**：
- `if (i < N/2)` 单调分支 → IPC 接近 4
- `if (rand())` 随机分支 → IPC 跌到 1-2
- `if (i & 1)` 周期 2 分支 → IPC ≈ 3（局部预测器能识别周期模式）

**关键代码**：
```c
// 可预测分支（i 单调递增）
uint64_t sum_predictable(const uint32_t *r, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++) {
        if (i < n/2) s += r[i];
        else         s -= r[i];
    }
    return s;
}

// 随机分支
uint64_t sum_random(const uint32_t *r, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++) {
        if (r[i] < 0x80000000U) s += r[i];
        else                    s -= r[i];
    }
    return s;
}

// 周期 4 模式分支
uint64_t sum_periodic(const uint32_t *r, size_t n) {
    uint64_t s = 0;
    for (size_t i = 0; i < n; i++) {
        if ((i & 3) == 0) s += r[i];
        else              s -= r[i];
    }
    return s;
}
```

**运行**：
```bash
make branch_predict
./branch_predict
# 同时用 perf stat 采集分支预测失败率：
sudo perf stat -e branches,branch-misses ./branch_predict
```

**预期结果**：
| 模式 | IPC | mispred rate | 备注 |
|------|-----|--------------|------|
| 单调 | 3.5-4.0 | < 0.1% | 分支预测器完美 |
| 周期 4 | 3.0-3.5 | ~ 0% | 局部预测器识别周期 |
| 周期 16 | 2.5-3.0 | < 5% | 长周期也能学 |
| 随机(伪随机源) | 0.7-1.5 | ~ 19% (实测) | 飞腾 TAGE 对伪随机 80% 准确率，要 50% 需密码学随机 |

**解释**：飞腾的分支预测器应该有：
- 2-bit 饱和计数器（识别简单模式）
- 局部历史（识别短周期）
- 全局历史（识别跨分支相关）
- RAS（Return Address Stack，识别函数返回）
- 可能还有 TAGE 类预测器（识别长周期）

**缺陷与陷阱**：
- 编译器可能用 `cmov` 替代分支（无分支代码！），那 mispred rate 永远 0
- 用 `-fno-if-conversion -fno-guess-branch-probability` 强制保留分支
- 或者用 `asm volatile goto` 阻止优化

**扩展思考**：
- 写一个"反预测器"分支序列（用 LFSR 让模式看起来无规律但实际有）
- 测一下间接跳转（函数指针）的 mispred 代价

---

### 3.3 实验 2.3：循环展开（`loop_unroll.c`）

**现象**：把 `for (i=0; i<N; i++)` 改成 `for (i=0; i<N; i+=4)`，IPC 通常会涨。

**假设**：
- 不展开：循环控制开销（i++、cmp、branch）占 30%
- 展开 4 倍：控制开销降到 7.5%
- 展开 16 倍：可能溢出寄存器，反而变慢

> 📌 **飞腾实测**（诊断报告 §3）：IPC **非单调**递增——unroll **2** 已达最优点，
> unroll 4 与 2 持平，unroll 8+ 因寄存器压力开始下降。"甜点"比常识的 4 倍更早。

**关键代码**：
```c
double sum_unroll0(const double *a, size_t n) {
    double s = 0;
    for (size_t i = 0; i < n; i++) s += a[i];
    return s;
}

double sum_unroll4(const double *a, size_t n) {
    double s0=0, s1=0, s2=0, s3=0;
    size_t i;
    for (i = 0; i + 3 < n; i += 4) {
        s0 += a[i+0]; s1 += a[i+1]; s2 += a[i+2]; s3 += a[i+3];
    }
    for (; i < n; i++) s0 += a[i];
    return s0 + s1 + s2 + s3;
}

double sum_unroll16(const double *a, size_t n) { /* ... */ }
```

**运行**：
```bash
make loop_unroll
./loop_unroll
```

**预期结果**：
| 展开倍数 | 时间 (N=1M) | IPC | 备注 |
|---------|------------|-----|------|
| 1× | 800 us | 2.0 | 编译器 -O2 自动 2x |
| 4× | 600 us | 2.7 | 4 个独立累加器 |
| 8× | 500 us | 3.2 | 8 个累加器 |
| 16× | 480 us | 3.3 | 接近寄存器上限 |
| 32× | 490 us | 3.3 | 不再快了 |

**解释**：循环展开 4 倍 = 4 个独立累加器 + 4 个独立 load → 充分利用 ILP。展开 16 倍时 16 个累加器可能溢出寄存器，效果不再增加。

**缺陷与陷阱**：
- 现代 GCC `-O3 -funroll-loops` 自动展开，手动展开未必有用
- 展开后 IC 变大，可能 I-cache miss
- 短数组展开反而慢（边界处理代码占大头）

**扩展思考**：
- 对比 PhyGCC 和社区 GCC 的展开策略
- 用 `#pragma GCC unroll 4` 控制展开倍数

---

### 3.4 实验 2.4：乱序执行的"魔法"（`ooo_magic.c`）

**现象**：一段代码，看起来需要 100 cycles，但因为乱序执行，实际只要 30 cycles。

**关键代码**：
```c
// 顺序执行思维：sum += load(addr1) + load(addr2) + load(addr3) + ...
// 乱序执行现实：3 个 load 可以并行，每个 100 cyc，但总时间只 100 cyc（不是 300）
double parallel_loads(const double *a, int n) {
    double s0=0, s1=0, s2=0, s3=0;
    for (int i = 0; i < n; i += 4) {
        s0 += a[i+0];   // 4 个 load 可并行发射
        s1 += a[i+1];
        s2 += a[i+2];
        s3 += a[i+3];
    }
    return s0+s1+s2+s3;
}

// 依赖链：每次 load 等上一次结果（链表追逐）
double serial_loads(double **ptrs, int n) {
    double s = 0;
    double **p = ptrs[0];
    for (int i = 0; i < n; i++) {
        s += *(double*)p;   // 必须等 *p 才能 p = next
        p = (double**)*p;
    }
    return s;
}
```

**预期**：
- parallel_loads：N=1M 时 ~ 100 us（每个 load 1 cycle，IPC=2-4）
- serial_loads：N=1000 时 ~ 50 ms（每个 load ~130 cycles 即 DRAM 延迟，IPC≈0.02）

> ⚠️ **方法学警告**：serial 链必须用 **16MB DRAM-resident 随机置换环**（Fisher-Yates）才能真展示乱序极限。
> 旧版用 4096 节点 L1-resident 顺序环（固定 stride），被 prefetcher 预取命中，serial IPC 虚高至 **1.25**（看似乱序"无效"，实为测量假象，见诊断报告 §1.4）。

**解释**：乱序引擎能在 issue queue 里看到多个独立指令，并行发射给不同的执行单元。但**真依赖链无法并行**——这是计算机科学的"信息论极限"。

**缺陷与陷阱**：链表追逐的 100 cycle 是 L1 miss + L2/L3 延迟，不能简单乘以 freq

---

## 4. 学完应该掌握的检查清单

- [ ] 能识别 RAW/WAW/WAR，并知道现代处理器用重命名消除 WAW/WAR
- [ ] 能解释为什么 `x = x*x + 1` 慢，`x[i] = x[i]*x[i]+1` 快
- [ ] 能用 perf stat 看到分支预测失败率，并把它换算成时间损失
- [ ] 知道循环展开不是万能药，何时反而会变慢
- [ ] 能解释乱序执行的极限：信息依赖链

---

## 5. 参考文献

| 编号 | 文献 | 章节 |
|------|------|------|
| 📘 | Patterson RISC-V 第2版 | Ch4 全章 |
| 📕 | 姚永斌超标量 | Ch1, Ch4 |
| 📗 | CAQA 5th | **Ch3 ILP** (核心) |
| 📖 | Smith & Sohi, "Microarchitecture of Superscalar Processors" | 经典综述 |
| 📖 | Yeh & Patt, "Two-Level Adaptation Branch Prediction" | 分支预测经典 |
| 📖 | Sprangle & Carmean, "Increasing Performance by ... Out-of-Order Execution" | 乱序综述 |

---

## 6. 编译与运行

```bash
cd Lab02_流水线与ILP
make
./data_hazards
./branch_predict
sudo perf stat -e branches,branch-misses ./branch_predict
./loop_unroll
./ooo_magic
```

---

📌 **下一步**：完成 Lab02 后，进入 [`Lab03_存储层次/`](../Lab03_存储层次/)。在那里你将看到**为什么 strided 访问慢 1000 倍**——Cache 层次的全部秘密。
