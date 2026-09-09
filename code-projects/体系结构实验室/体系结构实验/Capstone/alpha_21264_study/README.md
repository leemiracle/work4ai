# Capstone-A: Alpha 21264 vs 飞腾 D3000M 微架构对比

> 选自 📕 姚永斌《超标量处理器设计》Ch11 + 论文 Kessler 1999

---

## 1. 任务

1. 精读论文：Kessler et al., "The Alpha 21264 Microprocessor", IEEE Micro, 1999.
2. 论文笔记 → `notes.md`
3. 画出 21264 微架构图（取指 → 重命名 → 发射 → 执行 → 提交）→ `arch_diagram.md`
4. 用 Lab00-Lab04 反推的飞腾 D3000M 微架构参数，填对比表 → `comparison.md`

---

## 2. Alpha 21264 关键参数（来自论文）

| 参数 | 21264 (1999) |
|------|-------------|
| 工艺 | 0.35 μm CMOS |
| 频率 | 600 MHz |
| 晶体管数 | 15.2 M |
| Issue Width | **4-wide（含 2 INT + 2 FP）** |
| 流水线深度 | 7 stages (INT), 9 stages (FP) |
| L1 I-Cache | 64KB, 2-way |
| L1 D-Cache | 64KB, 2-way, dual-port |
| L2 Cache | 外挂（off-chip）|
| 分支预测 | **全局 + 局部混合 (TourghMatch)** |
| 寄存器重命名 | **统一 PRF: 80 PR (INT) + 72 PR (FP)** |
| Issue Queue | 20 entries (INT) + 15 entries (FP) |
| ROB | 隐含（在 IQ + LQ/SQ 中）|
| Load Queue | 32 entries |
| Store Queue | 32 entries |
| 关键特性 | Speculation, OoO, Banked CLQ |

---

## 3. 飞腾 D3000M 反推参数（来自本项目 Lab00-Lab04）

| 参数 | D3000M (2023) | 反推依据 |
|------|--------------|---------|
| 工艺 | (未公开) | - |
| 频率 | **2.5 GHz** | /sys/devices/.../scaling_cur_freq |
| Issue Width | **4-wide** | Lab00 null_loop IPC=4.00 |
| ALU 端口 | **2/cycle** | Lab00 loop_add IPC=2.00 |
| L1 D-Cache | 64KB, 4-way, **1.6 ns** | Lab03 |
| **L2 Cache** | **512 KB**, 8-way, 4-8 ns | Lab03（实测，不是 1MB）|
| L3-1 | 4 MB（核 0-3 共享）| Lab03 |
| L3-2 | 8 MB（核 0-7 共享）, 14 ns | Lab03 |
| 分支预测 | 实际效果接近 100% 单调 | Lab02 branch_predict |
| **fmadd latency** | **4 cycles** | Lab02 dep_chain_1 |
| 寄存器重命名 | ≥ 50 PR（n=12 时 IPC saturate）| Lab04 rename_capacity |
| ISA | ARMv8.4-A（FP16/UDOT/SM3/SM4）| Lab01 isa_features |

---

## 4. 对比要点（写在 comparison.md 里）

### 4.1 频率/工艺
- 21264: 0.35μm @ 600 MHz
- D3000M: 现代工艺 @ 2.5 GHz
- **频率提升 4×，但同期 CPU 频率提升不到 4× → 飞腾频率并不领先**

### 4.2 IPC 极限
- 21264: 4-wide
- D3000M: 4-wide
- **25 年间 Issue Width 几乎没变！这是 ILP Wall 的实证**

### 4.3 Cache 层级
- 21264: L1 私有, L2 off-chip（昂贵）
- D3000M: L1/L2 私有, L3 共享
- **D3000M 的 L2 = 512KB 私有远超 21264**

### 4.4 寄存器重命名
- 21264: 80 PR (INT)
- D3000M: ≥ 50 PR
- **D3000M 可能没有 21264 多，但够用**

### 4.5 关键差异
- 21264 是 **真 OoO 双 cluster**（两个 cluster 各自独立，跨 cluster bypass 慢）
- D3000M 应该是单 cluster
- 21264 的分支预测是 **hybrid (Tournament)**，D3000M 应该也类似

---

## 5. 25 年间的演进总结

| 维度 | 21264 (1999) | D3000M (2023) | 演进倍数 |
|------|-------------|---------------|---------|
| 频率 | 600 MHz | 2.5 GHz | 4× |
| IPC（理论）| 4 | 4 | 1×（ILP Wall）|
| L2 Cache | 0 (off-chip) | 512KB | ∞ |
| L3 Cache | 0 | 8 MB | ∞ |
| 核数 | 1 | 8 (multi-chip × N) | 8×+ |
| 总 FLOPS | ~2.4 GFLOPS | ~160 GFLOPS (8 核) | 67× |
| ISA | Alpha (RISC, 死) | ARMv8.4-A | - |

**核心洞察**：性能提升主要来自 **多核 + 大 cache**，而不是单核 ILP 提升。
这是 Hennessy & Patterson 在 2019 图灵奖演讲的核心观点。

---

## 6. 报告产出（已完成）

```
Capstone/alpha_21264_study/
├── README.md            ← 本文件
├── notes.md             ← 论文精读笔记（Kessler 1999，10 节）
├── arch_diagram.md      ← 21264 微架构图（5 张 mermaid 图）
├── comparison.md        ← 21264 vs D3000M 对比（数据来自实测）
└── collect_lab_data.py  ← 一键重跑 Lab 反推实验，自动生成 markdown
```
