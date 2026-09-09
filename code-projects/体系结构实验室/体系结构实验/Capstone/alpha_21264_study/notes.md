# Alpha 21264 论文精读笔记

> 论文：R. E. Kessler, "The Alpha 21264 Microprocessor", *IEEE Micro*, Vol. 19, No. 2, March/April 1999, pp. 24–36.
>
> 对应教材：📕 姚永斌《超标量处理器设计》第 11 章（真实案例研究）

---

## 0. 一句话定位

Alpha 21264 是 **1999 年微架构的巅峰之作**——首款商用**乱序执行 + 推测 + 双 cluster**的超标量 RISC。
它把"如何榨干 ILP"做到了 0.35μm 工艺下的极限，并被后来的 Sandy Bridge / Zen / Apple Firestorm 反复借鉴。
读懂它，就懂了现代 OoO CPU 的骨架。

---

## 1. 时代背景与设计目标

- **1996–1998 设计期**：Alpha 21164（前代）是顺序 4-wide，ILP 受限；Intel Pentium Pro（1995）已率先乱序。
- **21264 的使命**：在保持 Alpha RISC 简洁 ISA 的前提下，把 IPC 从 21164 的 ~1.5 提到 2+。
- **设计哲学**：
  1. **高频率优先**（600MHz 在 0.35μm 是激进目标）
  2. **ILP 优先于时钟**（4-wide OoO）
  3. **大 cache 优先**（64KB L1 在当时是巨无霸）

---

## 2. 顶层微架构参数

| 参数 | 21264 |
|------|------|
| 工艺 | 0.35μm CMOS（后期版本 0.18μm） |
| 频率 | 600 MHz（首版） → 1.25 GHz（最终版） |
| 晶体管 | 15.2 M |
| 功耗 | 72 W @ 600MHz（气冷极限） |
| ISA | Alpha（64-bit RISC，2022 已彻底死亡） |
| **Issue Width** | **4-wide（2 INT + 2 FP）** |
| 流水线 | 7 stages (INT) / 9 stages (FP) |
| L1 I-Cache | 64KB, 2-way, 1 cycle 访问 |
| L1 D-Cache | 64KB, **2-way, dual-port**（双 bank） |
| L2 Cache | **off-chip**（外挂 SRAM，64–8MB） |
| 分支预测 | **Hybrid Tournament**（全局 + 局部 + 选择器） |
| **寄存器重命名** | **统一 PRF: 80 INT + 72 FP** |
| Issue Queue | 20 entries (INT) + 15 entries (FP) |
| Load Queue | 32 entries |
| Store Queue | 32 entries |

---

## 3. 流水线（7 stages，INT）

```
0  IF   (Instruction Fetch) —— 取 4 条指令/周期，分支预测决定 PC
1  —    (Slotting)          —— 预解码 + cache 路预测
2  ID   (Swap)              —— 寄存器重命名 + issue queue 写入
3  —    (Issue)             —— 从 IQ 选 4 条指令（基于 ready 信号）
4  EX   (Register Read + ALU)
5  MEM  (Data Cache)
6  WB   (Commit to ARF)
```

注意 21264 的 stage 命名比较特别（Slotting/Swap），对应教科书的"重命名在 ID 完成"。

---

## 4. 三大创新（论文核心）

### 4.1 双 Cluster（最显眼）

21264 把 INT 执行单元**复制成两份**（cluster U / cluster V），每个 cluster 含完整 ALU + 寄存器堆副本。
- **为什么**：单 cluster 的 PRF 端口数会爆炸（4-wide 需 8 读 + 4 写 = 12 端口），FPGA/硅片代价巨大。
- **代价**：跨 cluster 数据传递要 1 cycle 额外延迟（"bypass delay"），编译器需要避免。
- **遗产**：现代 Apple M1 / AMD Zen 4 的"复杂执行端口 + 简单执行端口"分层是这一思想的演化。

### 4.2 Hybrid Tournament 分支预测器

**三层预测器**：
1. **全局预测器**（Gshare）：用全局历史（12 bit）索引 4K entry 2-bit 饱和器。
2. **局部预测器**：用 PC 索引 1K entry 局部历史（10 bit），再用局部历史索引 1K entry 3-bit 饱和器。
3. **选择器**（Choice Predictor）：4K entry 2-bit，决定本轮用全局还是局部。

**关键洞察**：不同程序对预测器偏好不同——规则代码（如 `if (flag)`）适合局部，循环代码适合全局。
Tournament 让硬件自动选最佳预测器，21264 的预测准确率超过 **95%**（当时创纪录）。

后来这成为标准：Intel NetBurst 改用 Bi-Modal，AMD Jaguar 用 Perceptron，但都源自这一思想。

### 4.3 Way Prediction + Banked D-Cache

- L1 D-Cache 是 2-way，但 21264 用 **Way Prediction**：每次访问只激活 1 way（节能 + 减 port）。
- D-Cache 分 **8 个 bank**，每个 bank 单口，但 8 bank 错峰可当多端口用。
- 这两个技巧在 1999 年极激进，后被 Intel Pentium M / Core 微架构全面采用。

---

## 5. 寄存器重命名细节

- INT：32 ARF + **48 额外 PR** = 80 PR 总容量（PRF 物理寄存器堆）。
- FP：32 ARF + **40 额外 PR** = 72 PR。
- 重命名表（Register Alias Table）用 SRAM 实现，2 cycle 重命名延迟。
- 80 PR 在 1999 年是超大窗口（Pentium Pro 只有 40 ROB），允许同时存在 ~80 条 in-flight 指令。

**这意味着**：理论上可以掩盖 80 cycle 的 L2 miss 延迟——但实际受 IQ/LQ/SQ 容量限制，约 40–50 cycle。

---

## 6. 内存系统

- **L1 D-Cache 64KB / 2-way / dual-port**：dual-port 通过 8-bank 错峰实现，论文详细讲了 bank conflict 处理。
- **L1 I-Cache 64KB / 2-way**：含 way-hint + way-prediction。
- **L2 off-chip**：21264 没有 on-die L2！用外挂 B-cache（SRAM 颗粒）。这是 0.35μm 工艺的限制——做不下。
- 后来 21264A / 21264C 改用 0.18μm 加上 on-die L2（1.75–8MB）。

---

## 7. 关键工程权衡（论文反复强调）

1. **频率 vs IPC**：21264 选择高 IPC（4-wide OoO），代价是 7 stage 流水线（频率受限）。
   相比之下 Intel Pentium 4 选高频率 + 简单 IPC（20+ stage），后被证明是死路。
2. **cluster 复制 vs 单大 PRF**：选了前者，省了端口复杂度，但编译器负担加重。
3. **off-chip L2 vs on-die**：被迫选前者（工艺限制），导致 L2 延迟 ~12 cycle（比 on-die 慢 3×）。

---

## 8. 性能数据（来自论文 + 后续 SPEC 测试）

- SPECint95 base：~35（600MHz 版本）—— 比 Pentium II 450MHz 高 50%
- SPECfp95 base：~50 —— 浮点是 Alpha 传统强项
- 典型 IPC：**1.8–2.4**（实际代码，非峰值 4）
- 功耗效率：72W / 600MHz = 0.12 W/MHz（很高，但 0.35μm 是这样）

---

## 9. 历史地位与遗产

- **商业化失败**：Alpha 1998 被 Compaq 收购，2001 卖给 Intel，ISA 2022 EOL。
- **技术遗产巨大**：
  - 双 cluster → Apple M1 P-core 的"Complex + Simple"端口分层
  - Hybrid 预测器 → 所有现代 CPU 的分支预测基础
  - Way prediction → Intel Core 微架构
  - Banked cache → 现代 GPU 内存系统
- **21264 团队**：很多人后来去了 AMD（设计 K8/Opteron）和 Intel（设计 Core）。

---

## 10. 与本项目（飞腾 D3000M）的对比维度

| 维度 | 21264 (1999) | 飞腾 D3000M (2023) |
|------|-------------|---------------------|
| 工艺 | 0.35μm | 现代工艺（推测 7nm 等效） |
| 频率 | 600 MHz | 2.5 GHz |
| Issue Width | 4-wide | 4-wide（实测） |
| 寄存器重命名 | 80 INT PR | ≥ 50 PR（实测拐点 n=10） |
| 分支预测 | Tournament Hybrid | 现代变体（推测 TAGE-like） |
| L1 | 64KB / 2-way | 64KB / 4-way（实测） |
| L2 | off-chip | **on-die 512KB / 8-way**（实测） |
| L3 | 无 | **8MB on-die shared** |
| 多核 | 单核 | 8 核 / chip |

详细对比见 [`comparison.md`](./comparison.md)。

---

## 11. 推荐延伸阅读

1. 🔧 Kessler 1999 原论文（本笔记的基础）
2. 📕 姚永斌《超标量处理器设计》Ch11 — 中文最好的 21264 案例
3. 📗 Hennessy & Patterson《CAQA》第 3 章（ILP）
4. 📄 Seznec et al., "TAGE-SC-L branch predictor" (2014) — 现代预测器奠基
5. 📄 Reid, "The Alpha 21264 Microprocessor"（同作者的技术报告版本，更详细）

---

📌 **下一步**：打开 [`arch_diagram.md`](./arch_diagram.md) 看可视化微架构图，
然后 [`comparison.md`](./comparison.md) 看 21264 vs 飞腾 D3000M 的数据对比。
