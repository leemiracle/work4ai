# Lab06 — ARM 内存模型与并发

> ARMv8 内存模型是 ARM 最独特、也最容易被忽视的部分。
> x86 是 TSO（Total Store Order），ARM 是 **RCpc（Relaxed Consistency, processor consistent）**，
> 这意味着**几乎所有的访存操作都可能被重排**——除非你显式加屏障。

---

## 0. 学习目标（一句话）

**实证地看到 ARM 内存重排现象**，并掌握 `dmb/dsb/isb` 等屏障指令的代价与正确使用方式。

---

## 1. 对应教材与课程

| 来源 | 章节 | 重点 |
|------|------|------|
| 📗 CAQA 5th | **Appendix + Sorin et al.** | 内存一致性模型理论 |
| 📕 姚永斌超标量 | **Ch9.6 Memory Disambiguation** | 推测 load/store |
| 📖 | ARM ARM (DDI 0487) | "Memory Ordering" 章节 |
| 📖 | Sorin, Hill, Wood, **"A Primer on Memory Consistency and Cache Coherence"** (2nd, 2020) | 圣经 |
| 📖 | Maranget et al., **"A Tutorial Introduction to the ARM and POWER Relaxed Memory Models"** (PLDI 2012) | 经典 |
| 📖 | McKenney, **"Is Parallel Programming Hard, and, If So, What Can You Do About It?"** | RCU 大神写 |

---

## 2. 核心概念速览

### 2.1 ARMv8 内存序层级（从严到松）

| 层级 | 屏障指令 | C/C++ 对应 | 用法 |
|------|---------|----------|------|
| Sequential Consistency | `dmb ish` 全屏障 | `memory_order_seq_cst` | 最严，几乎不用 |
| **Release / Acquire** | `stlr` / `ldar` | `memory_order_release/acquire` | 无锁队列标配 |
| **LRCPC**（v8.1+） | `stlur` / `ldapur` | RCpc 增强版 | 更细粒度控制 |
| Relaxed | 普通 load/store | `memory_order_relaxed` | 计数器自增 |

### 2.2 经典 Store-Store 重排实验

```
CPU0:                CPU1:
  x = 1;               while (flag == 0);
  flag = 1;            r0 = x;       // r0 可能读到 0！
```

**TSO (x86)**：r0 不会是 0（store 顺序保留）
**ARM RCpc**：**r0 可能是 0**——store x 和 store flag 可以重排！

加 `stlr` (Store-Release) 即可阻止。

### 2.3 屏障代价（飞腾 D3000M 实测，2026-07-02）

| 屏障 | 代价 (cycles) | 用途 |
|------|-------------|------|
| 无屏障 (relaxed) | 0 | 紧密循环里的计数器 |
| `ldar/stlr` (acq/rel) | ⚠️ 测不出（见下注） | 无锁数据结构 |
| `dmb ish` (seq_cst) | **~7** (实测) | 罕见用 |
| `dsb ish` (等完成) | ~7 (实测，近 dmb) | DMA、I/O |
| `isb` (指令同步) | **~34** (实测) | 修改代码后 |
| `dmb ishst` (仅 store-store) | ~2 (实测) | 生产者-消费者 |

> ⚠️ **`ldar/stlr` 方法学受限**：纯指令吞吐 + 同地址 L1 命中下，ldar/stlr 测出与 nop 同（~0.4ns），
> **acquire/release 语义从未真正触发**。要测真实代价须跨核 producer-consumer 往返（见诊断报告 §2.1）。
> 旧表"~2 cyc"是 L1 命中吞吐，非 ordering 代价。

---

## 3. 实验列表

### 3.1 实验 6.1：内存序代价（`mem_order_cost.c`）

测量不同内存序的原子操作 latency。

### 3.2 实验 6.2：Store-Store 重排（`store_store_reorder.c`）

跑 Maranget 经典实验，看 ARM 上是否真有重排。

### 3.3 实验 6.3：Message Passing（`message_passing.c`）

经典的 MP pattern：
- CPU0 写 data，然后写 flag（用 stlr 阻止重排）
- CPU1 读 flag（用 ldar），如果 flag==1 才读 data

**实测（飞腾 D3000M，2026-07-02，2核 2M trials/模式，data/flag 不同 cacheline）**：
| 模式 | 重排次数(data==0) | 占比 |
|------|------------------|------|
| relaxed（普通 str/ldr）| **55 / 2,000,000** | **0.0027%** |
| release/acquire（stlr/ldar）| **0 / 2,000,000** | 0% |

**关键结论**：飞腾 D3000M 对 **store-load（MP）真发生重排**（55次），但对 store-store 保守（见 store_store_reorder.c 实测 0次）。两者互补，完整呈现 ARM RCpc 内存模型——**这是飞腾内存模型最直接的实证**。stlr/ldar 完全消除重排，证明 acquire/release 是无锁数据结构的必备。

### 3.4 实验 6.4：LRCPC vs SC（`lrcpc_test.c`）

飞腾支持 LRCPC（v8.1+）。对比 `ldapur/stlur` vs `ldar/stlar` 的性能。

### 3.5 实验 6.5：RCU 模式（`rcu_test.c`）

测试 RCU（Read-Copy-Update）模式在飞腾上的扩展性。

---

## 4. 学完应该掌握的检查清单

- [ ] 能解释为什么 ARM 上 store-store 会重排
- [ ] 能解释 `ldar/stlr` 与 `dmb ish` 的语义和代价差异
- [ ] 能写出无锁队列的 acquire/release 内存序正确版本
- [ ] 能跑出"无屏障时 ARM 重排率"

---

## 5. 编译与运行

```bash
cd Lab06_内存模型与并发
make
./mem_order_cost
./store_store_reorder    # 跑几千万次找重排
./message_passing
./lrcpc_test
```

---

📌 **下一步**：进入 [`Lab07_密码学专题/`](../Lab07_密码学专题/)。
