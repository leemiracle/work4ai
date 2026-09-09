# Alpha 21264 微架构图

> 用 Mermaid 画 21264 的取指-执行-提交数据通路。对应 [`notes.md`](./notes.md) 第 3–5 节。

---

## 1. 完整数据通路（顶视图）

```mermaid
flowchart LR
    subgraph IF["IF / 预测"]
        ICache["L1 I-Cache\n64KB / 2-way"] --> Pred["Hybrid Tournament\n分支预测器\nGlobal+Local+Choice"]
        Pred -->|"next PC"| ICache
    end
    subgraph ID["ID / 重命名"]
        Decode["解码"] --> RAT["Register Alias Table\n(重命名)"]
        RAT -->|"物理寄存器号"| IQ_INT["INT Issue Queue\n20 entries"]
        RAT -->|"物理寄存器号"| IQ_FP["FP Issue Queue\n15 entries"]
    end
    subgraph EX_INT["EX / 双 Cluster INT"]
        IQ_Int --> IQ_INT
        IQ_INT --> CU["Cluster U\nALU ×2 / BR / Shift"]
        IQ_INT --> CV["Cluster V\nALU ×2 / BR / Shift"]
        PRF_INT["PRF INT\n80 entries\n(cluster-shared)"]
        CU -.->|"bypass\n+1c if cross"| CV
        CU & CV --> PRF_INT
    end
    subgraph EX_FP["EX / FP"]
        IQ_FP --> FPU["FP Pipeline\nMul/Add/Cvt"]
        PRF_FP["PRF FP\n72 entries"]
        FPU --> PRF_FP
    end
    subgraph MEM["MEM"]
        CU & CV --> AGU["地址生成"]
        AGU --> DCache["L1 D-Cache\n64KB / 2-way / 8-bank\ndual-port"]
        DCache --> L2["L2 (off-chip)\n64KB–8MB SRAM"]
        LQ["Load Queue\n32 entries"] -.-> DCache
        SQ["Store Queue\n32 entries"] -.-> DCache
    end
    subgraph WB["Commit"]
        DCache & FPU & CU & CV --> ROB["Reorder Buffer\n(in IQ + LQ + SQ)"]
        ROB -->|"in-order retire"| ARF_INT["ARF INT\n32"]
        ROB -->|"in-order retire"| ARF_FP["ARF FP\n32"]
    end
    IF --> ID --> EX_INT & EX_FP --> MEM --> WB
```

---

## 2. 分支预测器结构（Hybrid Tournament）

```mermaid
flowchart TD
    PC["当前 PC"] --> GHist["Global History\n12 bits"]
    PC --> LHist["Per-PC Local History Table\n1K entries × 10 bits"]
    GHist & PC --> GPred["Global Predictor\n4K entries × 2-bit"]
    LHist --> LPred["Local Predictor\n1K entries × 3-bit\n(counter)"]
    PC --> Choice["Choice Predictor\n4K entries × 2-bit"]
    GPred -->|"taken/not taken"| Mux{"Mux"}
    LPred -->|"taken/not taken"| Mux
    Choice -->|"选哪个预测器"| Mux
    Mux --> Final["最终预测"]
    Final -.->|"update after resolve"| GPred & LPred & Choice & GHist & LHist
```

**关键**：Choice predictor 自动学习"对当前代码哪一种预测器更准"，是 1999 年最先进的自适应机制。

---

## 3. 双 Cluster 的物理寄存器堆方案

```mermaid
flowchart LR
    subgraph PRF["统一 PRF (80 entries) — 逻辑上"]
        PRFU["PRF Cluster-U 副本\n(读端口专用)"]
        PRFV["PRF Cluster-V 副本\n(读端口专用)"]
    end
    IQ["Issue Queue"] -->|"指令 #1"| ALU_U["ALU U1 + U2"]
    IQ -->|"指令 #2"| ALU_V["ALU V1 + V2"]
    ALU_U & ALU_V -->|"写入"| PRFB["PRF 写端口\n共享"]
    PRFB --> PRFU & PRFV
    PRFU -.->|"读"| ALU_U
    PRFV -.->|"读"| ALU_V
    ALU_U -.->|"跨 cluster 旁路\n+1 cycle"| ALU_V
```

**为什么**：4-wide 需要 8 读 + 4 写端口，单 PRF 物理代价爆炸（面积 ∝ 端口²）。
复制成两份每份只需 4 读 + 4 写端口（含写回），代价是写入时要广播到两份，跨 cluster 读要 1 cycle。

---

## 4. 流水线时序（INT 路径）

```mermaid
gantt
    title Alpha 21264 INT 7-stage Pipeline
    dateFormat X
    axisFormat %s
    section 指令生命周期
    IF (Instruction Fetch)        :0, 1
    Slotting (Pre-decode + Way-pred) :1, 1
    Swap (Rename + IQ write)      :2, 1
    Issue (Select 4 from IQ)      :3, 1
    RegRead + EX                  :4, 1
    MEM (Data Cache)              :5, 1
    WB (Commit to ARF)            :6, 1
```

**关键观察**：分支在 stage 1（IF）就预测，但实际解析在 stage 4（EX）。
错误预测 penalty = 4 cycle（要 flush 4 stage 流水线）。
Tournament 预测器的高准确率（>95%）让这条流水线的实际 flush 概率 < 5%。

---

## 5. 与飞腾 D3000M 的拓扑差异（对照图）

```mermaid
flowchart TB
    subgraph A21264["Alpha 21264 (1999)"]
        direction TB
        A1["单核\n4-wide OoO"]
        A2["双 cluster INT\n复制 ALU"]
        A3["80 INT PR + 72 FP PR"]
        A4["L1 64KB 私有\nL2 off-chip\nL3 无"]
        A5["7-stage INT / 9-stage FP"]
    end
    subgraph D3000M["飞腾 D3000M (2023)"]
        direction TB
        D1["8 核 / chip\n每核推测 4-wide OoO"]
        D2["单 cluster（推测）\n2 ALU ports/cycle 实测"]
        D3["≥50 PR（实测拐点）"]
        D4["L1 64KB / L2 512KB 私有\nL3 8MB on-die shared"]
        D5["推测 15+ stage\n（高频率代价）"]
    end
    A1 -.->|"25 年演进"| D1
    A2 -.->|"简化（不要双 cluster）"| D2
    A4 -.->|"L2/L3 on-die 化"| D4
    A5 -.->|"加深（追频率）"| D5
```

**核心洞察**：25 年间单核 IPC 几乎没变（仍 4-wide），性能提升主要来自：
1. **频率**（600MHz → 2.5GHz，4×）
2. **大容量 on-die cache**（off-chip L2 → 8MB L3）
3. **多核**（单核 → 8 核 / chip）

这是 Hennessy & Patterson 2019 图灵奖演讲的核心观点：**ILP Wall 已破，单核时代结束**。

---

📌 **下一步**：看 [`comparison.md`](./comparison.md) 的完整数据对比表。
