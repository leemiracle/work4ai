# Lab04 — 超标量乱序：寄存器重命名 / Issue / ROB

> 这是姚永斌《超标量处理器设计》全书的核心章节。
> 现代处理器的"魔法"全部在这里：寄存器重命名、Tomasulo 算法、ROB、推测执行。

---

## 0. 学习目标（一句话）

**用微基准反推飞腾 D3000M 的微架构参数**（ROB 大小、Issue Queue 深度、物理寄存器数、Load/Store Queue 容量），并理解每个机制存在的"为什么"。

---

## 1. 对应教材与课程

| 来源 | 章节 | 重点 |
|------|------|------|
| 📕 姚永斌超标量 | **Ch7 寄存器重命名** | ROB/ARF/PRF 三种方案 |
| 📕 姚永斌超标量 | **Ch8 发射** | 集中式 vs 分布式、唤醒-选择 |
| 📕 姚永斌超标量 | **Ch10 提交** | ROB 结构、异常处理 |
| 📕 姚永斌超标量 | **Ch9.6 Memory Disambiguation** | 推测 load/store |
| 📗 CAQA 5th | **Ch3 §3.2-3.5** | Tomasulo、ROB 经典理论 |
| 📗 CAQA 5th | **Ch3 §3.6** | Hardware-Based Speculation |
| 🎓 | Onur Mutlu ETHz CA Lecture 8-12 | 进阶 |

---

## 2. 核心概念速览

### 2.1 三种寄存器重命名方案对比

```
方案 A：基于 ROB 的重命名（早期 Alpha 21064）
   重命名寄存器 = ROB 表项
   优点：简单
   缺点：ROB 容量 = 重命名容量

方案 B：ARF 扩展（早期 Pentium Pro）
   每个 ARF 后跟多个"扩展"寄存器
   优点：恢复快
   缺点：复杂

方案 C：统一的 PRF（现代主流：Alpha 21264, 飞腾 D3000M 可能是这种）
   32 ARF（逻辑）+ N 个 PRF（物理）
   RAT (Register Alias Table) 维护 ARF → PRF 映射
   优点：容量大、灵活
   缺点：恢复需要 checkpoint 或 walk
```

### 2.2 乱序执行的关键数据结构

```
┌──────────────────────────────────────────────┐
│  ROB (Reorder Buffer)                          │
│  ─────────────────────                         │
│  作用：让指令"按序提交"，即使执行是乱序的      │
│  容量：飞腾 D3000M 预计 128-192 项              │
└──────────────────────────────────────────────┘
                  ↓
┌──────────────────────────────────────────────┐
│  Issue Queue / Reservation Station            │
│  ─────────────────────                         │
│  作用：等操作数就绪后唤醒 → 选择 → 发射到 EX  │
│  容量：飞腾 D3000M 预计 32-64 项                │
└──────────────────────────────────────────────┘
                  ↓
┌──────────────────────────────────────────────┐
│  PRF (Physical Register File)                 │
│  ─────────────────────                         │
│  32 逻辑寄存器 + N 物理寄存器（"重命名容量"）  │
│  飞腾 D3000M 预计 N = 128-256                  │
└──────────────────────────────────────────────┘
```

### 2.3 数学：乱序窗口的三个独立瓶颈

指令并行度同时受多个窗口约束，IPC 取最紧的那个：

$$
\text{IPC} = \min\!\left(W,\ \frac{|\text{ROB}|}{L_{\text{avg}}},\ \frac{|\text{PRF}|}{L_{\text{depchain}}},\ \frac{|\text{LDQ}|}{L_{\text{mem}}}\right)
$$

- $W$：发射宽度（飞腾 4-wide）
- $|\text{ROB}| / L_{\text{avg}}$：ROB 窗口能容纳的「在飞指令数 ÷ 平均延迟」
- $|\text{PRF}| / L_{\text{depchain}}$：物理寄存器能容纳的「在飞依赖链深度」
- $|\text{LDQ}| / L_{\text{mem}}$：Load Queue 能容纳的「在飞 miss 数」

⚠ **关键认知：这三个窗口是独立的**，本 Lab 的三个实验分别打其中一个：
- 4.1 rename_capacity → 打 PRF（但浅链主要打发射带宽，见该实验诚实声明）
- 4.2 rob_size → 打 min(ROB, LDQ)（load 类实验两者混淆，结果是 ROB 下界）
- 4.3 load_store_spec → 观察 LDQ + disambiguator 行为

例如飞腾 D3000M（预估 ROB=128-192, LDQ=32-64, PRF=128-256）：
- 纯 ALU 负载（L_avg=4）：ROB/4 = 32-48，够 4-wide 跑满 → IPC≈4
- 访存负载（L_avg=50）：ROB/50 = 2.5-3.8 → 表面看 IPC 卡在 2-3
- **但若 LDQ=48 先满**，访存 IPC 实际卡在 48/50 ≈ 0.96（每链 1 miss）——这才是 load 真实瓶颈

---

## 3. 实验列表

### 3.1 实验 4.1：寄存器重命名容量（`rename_capacity.c`）

**现象**：构建 N 条独立浮点链，N 越多 IPC 越高；但 N 超过重命名容量后，IPC 不再涨。

**关键代码**：
```c
double chains_N(double x, int n_iter, int n_chains) {
    double v[MAX_CHAINS];
    for (int i = 0; i < n_chains; i++) v[i] = x + i;
    for (int i = 0; i < n_iter; i++) {
        // 展开 N 条独立依赖链
        for (int j = 0; j < n_chains; j++) {
            v[j] = v[j] * v[j] + 1.0;
        }
    }
    double s = 0;
    for (int j = 0; j < n_chains; j++) s += v[j];
    return s;
}
```

**预期**（浅链，每链每迭代 1 步 fmul+fadd）：
- n_chains = 1 → IPC ≈ 0.25（fmul+fadd 串行链 ~8 cyc/op，**教科书估算**）
- n_chains = 4 → IPC ≈ 1.0（4 条独立链填满 4-wide）
- n_chains ≥ 12 → IPC ≈ 3-4（撞 4-wide 发射带宽上限）

> 📌 **飞腾实测**（诊断报告 §5）：n=1 实测 IPC **0.94**（远高于 0.25 的教科书估算——
> 乱序引擎跨循环迭代找并行，单链也能部分填满流水线）；n≥12 saturate IPC **~3.45**。

⚠ **诚实声明（概念修正）**：浅链的 saturate 点 = **发射带宽瓶颈**，不是 PRF 拐点。
初版 README 说「n=64 IPC 反而下降 → 重命名容量极限」是**错误认知**：
浅链每条链只占 1 个活跃寄存器，N=64 也只压 64 个 PRF，远未到飞腾 PRF（128-256）。
要测真 PRF 拐点，必须用**深链**（每链 L 步长依赖，N×L 撑满 PRF），
见 `rename_capacity.c` 文件末尾「深链 PRF 探测」扩展注释（留作练习）。

**反推（若做深链扩展）**：当 IPC 从 4-wide 理论值掉下来的拐点 N\*，
满足 N\* × L ≈ PRF_size，即 PRF_size ≈ N\* × L。

---

### 3.2 实验 4.2：ROB 大小（`rob_size.c`）

**现象**：跑 N 个独立 load，让它们都阻塞（cache miss），看能"在飞"的最大指令数。

**关键代码**：
```c
// 构造 N 个独立的 L3 miss load
double *ptrs[N];  // 每个指向不同 cache line
// 让每个 load 都 miss 到 DRAM

double rob_throughput_test(double **ptrs, int n) {
    double s = 0;
    for (int i = 0; i < n; i++) {
        s += *ptrs[i];  // N 个独立 load，无依赖
    }
    return s;
}
```

**预期**（N 条独立 pointer-chasing 链，每步 miss 到 DRAM）：
- 当 n < window：N 个 load 并行飞，每步总延迟 ≈ 1 次 DRAM miss（~100-300 ns）
- 当 n > window：window 满，前端 stall，每步延迟线性增长
- 拐点 n\* ≈ window

⚠ **关键陷阱（概念修正）**：load 类实验的窗口上限 = **min(ROB, LDQ)**，不是纯 ROB。
现代乱序核的 LDQ（Load Queue）通常比 ROB 小（Skylake: ROB=224/LDQ=72；M1: ROB~600/LDQ~340）。
所以本实验测得的拐点是 **LDQ 上界，是 ROB 的下界**。
要分离 ROB vs LDQ，需对照实验：用纯 ALU 长延迟链（不占 LSQ）单独压 ROB。

**反推**：
- 拐点 n\* ≈ LDQ_size（load 窗口的真瓶颈）
- ROB_size ≥ n\*（上界要用 ALU 链或 STALL_FRONTEND PMU 辅助）

---

### 3.3 实验 4.3：Memory Disambiguation（`load_store_spec.c`）

**现象**：store 后 load 同一地址，load 必须等 store（forwarding）。但 store 后 load 不同地址，load 可以推测执行。更深层的：store 的**地址**尚未算出时，load 能否推测越过？这正是姚永斌《超标量》Ch9.6 的核心议题。

**4 种模式**（紧凑循环，L1-resident 缓冲排除 miss 干扰，纯测指令级机制）：

| 模式 | 描述 | 预期 CPI |
|------|------|----------|
| A 同址依赖 | store→load 同地址 | 最高（等 forwarding ~3-5 cyc）|
| B 异址独立 | store→load 不同地址，地址都早定 | 最低（推测并行）|
| C 地址依赖 | store 地址慢定（mul 链），load 地址早定 | 中-高（看 disambiguator 激进程度）|
| D 推测误判 | 每 16 次 load 与 store alias 1 次 | 中（推测失败惩罚）|

**关键代码**（模式 C，最揭示性）：
```c
// store 地址经 4 步 mul 链慢定（~12 cyc 才算出）
uint32_t a = i ^ g_poison;
a = a * 2654435761u + 1;
a = a * 2654435761u + 2;
a = a * 2654435761u + 3;
a = a * 2654435761u + 4;
a &= MASK;
g_buf[a] = i;            // store，地址刚算出
s += *pl;                // load，地址早定且绝不与 store 冲突
```

**预期**：
- CPI(A) 最高：每轮 load 等 store buffer forwarding
- CPI(B) 最低：disambiguator 一眼判断不冲突，load 推测并行
- CPI(C) 是关键判据：
  - 若 CPI(C) ≈ CPI(A) → 飞腾 disambiguator **保守**（地址未定就阻塞 load）
  - 若 CPI(C) ≈ CPI(B) → 飞腾**激进推测**（赌 load 与未定址 store 不冲突）
- CPI(D) 介于 A/B 之间；推测失败惩罚 ≈ (CPI(D) − CPI(B)) × 16

---

### 3.4 实验 4.4：反推飞腾 D3000M 微架构（综合）

综合 4.1 + 4.2 + 4.3 的结果，填表：

| 参数 | 推测值 | 验证方法 |
|------|--------|---------|
| Issue Width | 4-wide（Lab00 已知）| null_loop IPC=4 |
| ALU 端口数 | 2/周期 | loop_add IPC=2 |
| ROB 大小 | 128-192 | rob_size 拐点 |
| Issue Queue | 32-64 | 同上 |
| 物理寄存器数（PRF） | 128-256 | rename_capacity 拐点 |
| L1 D-Cache latency | 4 cyc | cache_sizes |
| L2 latency | 12 cyc | cache_sizes |
| Branch mispred penalty | 15-20 cyc | branch_predict |

**这是整个项目的"研究性"成果**——你将得到一份"飞腾 D3000M 实测微架构参数表"，对比姚永斌书中的 Alpha 21264。

---

## 4. 学完应该掌握的检查清单

- [ ] 能解释寄存器重命名为什么能消除 WAW/WAR 但不能消除 RAW
- [ ] 能区分 ROB、Issue Queue、PRF 三个数据结构的作用
- [ ] 能用 latency 拐点实验反推 ROB 大小
- [ ] 能解释 Memory Disambiguation 的"推测 load"机制
- [ ] 能解释 Alpha 21264 vs 飞腾 D3000M 的微架构差异

---

## 5. 参考文献

| 编号 | 文献 | 章节 |
|------|------|------|
| 📕 | 姚永斌超标量 | Ch7, Ch8, Ch10 |
| 📗 | CAQA 5th | Ch3 §3.2-3.6 |
| 📖 | Tomasulo, "An Efficient Algorithm for Exploiting Multiple Arithmetic Units" (1967) | 经典原始论文 |
| 📖 | Smith & Sohi, "Microarchitecture of Superscalar Processors" (1998) | 综述 |
| 📖 | Kessler, "The Alpha 21264 Microprocessor" (1999) | 真实案例 |

---

## 6. 编译与运行

```bash
cd Lab04_超标量乱序
make
./rename_capacity
./rob_size
./load_store_spec
# 综合填表：
./reverse_engineer_summary.sh
```

---

📌 **下一步**：完成 Lab04 后，进入 [`Lab05_并行与SIMD/`](../Lab05_并行与SIMD/)。在那里你将把所有知识综合起来——GEMM 优化全栈：朴素→分块→向量化→多线程，目标逼近飞腾的 FLOPS 极限。
