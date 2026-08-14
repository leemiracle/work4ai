# 03 · Tensor / Pipeline Parallel（Megatron）

> ZeRO（[02 篇](./02-ZeRO.md)）解决了"显存冗余"，但大模型训练还有另一条主线——**模型并行**：把模型本身切开分到多卡。Megatron-LM（NVIDIA）定义了两种切法：**TP（层内切矩阵）+ PP（层间切模型）**。本章把 Megatron 的切法精髓讲透——这是 GPT-3/Llama-405B 这类万亿参数训练的工程根基。
>
> 配套：[Megatron-LM 论文](https://arxiv.org/abs/1909.08053) + [`讲透公开课/03-T1 Megatron`](<../讲透公开课/03-AI Infra 源码导读清单.md>)

---

## 一、为什么 ZeRO 不够，还要模型并行

ZeRO-3（FSDP）虽然能训大模型，但有两个问题：

1. **通信量随模型增大线性涨**：每层 AllGather 整层参数——大模型通信成本爆炸
2. **不适合超大规模**：跨机时 ZeRO-3 通信效率掉得厉害

**模型并行**换思路：不"分冗余"，直接"**分模型本身**"——每卡只算一部分计算，永久持有部分权重，不需要反复 gather。

- **TP（Tensor Parallel）**：层内切矩阵（同一层多卡合作）
- **PP（Pipeline Parallel）**：层间切模型（不同层在不同卡）

---

## 二、Tensor Parallel（层内并行）

### 2.1 出发点：线性层怎么切

一个线性层 $Y = XW$（$X \in \mathbb{R}^{m \times k}$, $W \in \mathbb{R}^{k \times n}$）。两种切法：

### 2.2 Column Parallel（按列切）

把 $W$ 按列切：$W = [W_1 | W_2]$（$W_i \in \mathbb{R}^{k \times n/2}$）

```
GPU 0: 算 Y_1 = X · W_1     (m × n/2)
GPU 1: 算 Y_2 = X · W_2     (m × n/2)
输出 Y = [Y_1 | Y_2]         (列拼接)
```

**关键**：每卡都持有完整 $X$，但只算输出的一部分列。**前向不需要通信**（每卡独立算），输出可以本地保留供下一层用。

### 2.3 Row Parallel（按行切）

把 $W$ 按行切：$W = \begin{bmatrix} W_1 \\ W_2 \end{bmatrix}$（$W_i \in \mathbb{R}^{k/2 \times n}$），$X$ 也按列切：$X = [X_1 | X_2]$

```
GPU 0: 算 Y_1 = X_1 · W_1    (m × n)
GPU 1: 算 Y_2 = X_2 · W_2    (m × n)
Y = Y_1 + Y_2                (AllReduce 求和)
```

**关键**：输出需要 **AllReduce**（求和）——有通信。

### 2.4 Megatron 的 MLP 切法（精髓）

MLP 一层：$Y = \text{dropout}(\text{GELU}(X W_1) W_2)$。Megatron 的天才设计：

```
W_1 用 column parallel：  GPU 0 持有 W_1 的左半，GPU 1 持有右半
W_2 用 row parallel：    GPU 0 持有 W_2 的上半，GPU 1 持有下半

前向：
   X (每卡都有完整)
   GPU 0: A_0 = GELU(X · W_1_左半)      GPU 1: A_1 = GELU(X · W_1_右半)
          （column parallel：A_0 和 A_1 是输出的左右两半，本地保留，不通信）
   GPU 0: Z_0 = A_0 · W_2_上半           GPU 1: Z_1 = A_1 · W_2_下半
   Y = Z_0 + Z_1                         （row parallel：AllReduce 求和）
```

**关键洞察**：**两层 MLP 只需要 1 次 AllReduce**（在 $W_2$ 后）！中间的 GELU 激活本地算，不通信。这是 Megatron 设计的核心——**通过 column + row 的巧妙组合，把通信降到最小**。

### 2.5 Attention 的切法

Multi-head attention 天然适合 TP——**每个 head 分到一张卡**（或多卡共享）：

```
QKV projection: column parallel（按 head 切，每卡负责几个 head）
attention 计算: 每卡独立算自己 head 的 attention（不通信！）
output projection: row parallel → AllReduce
```

一个 attention block 也只 **1 次 AllReduce**。

### 2.6 TP 的代价：通信频繁

- 每个 MLP/attention block 都要 AllReduce（每层 2 次）
- **所以 TP 只适合机内**（NVLink ~900 GB/s）——跨机 AllReduce 会爆

> 🎯 **铁律**：**TP 的规模 = 机内 GPU 数**（如 8 卡 H100 用 TP=8）。跨机不用 TP，用 PP。

---

## 三、Pipeline Parallel（层间并行）

### 3.1 思路

把模型按层切成 $N$ 段，每段一张卡（或多张）。一个 micro-batch 顺序流过各段：

```
GPU 0: Layer 1-20   ─→ micro-batch 1 → 2 → 3 → 4 ...
GPU 1: Layer 21-40  ─→ （等 GPU 0 算完才轮到）
GPU 2: Layer 41-60  ─→
GPU 3: Layer 61-80  ─→
```

**问题**：如果一次只跑一个 micro-batch，GPU 0 算时 GPU 1/2/3 都闲着——**效率极低**。

### 3.2 解决：micro-batch 流水线

把一个大 batch 切成 $M$ 个 micro-batch，**让它们重叠流过流水线**：

```
时间 →
GPU 0: | F1 | F2 | F3 | F4 | B4 | B3 | B2 | B1 |       F=Forward, B=Backward
GPU 1:      | F1 | F2 | F3 | F4 | B4 | B3 | B2 | B1 |
GPU 2:           | F1 | F2 | F3 | F4 | B4 | B3 | B2 | B1 |
GPU 3:                | F1 | F2 | F3 | F4 | B4 | B3 | B2 | B1 |
```

### 3.3 Bubble（流水线空泡）

流水线开头和结尾有空闲——**bubble**。bubble 比例：

$$
\text{bubble 比例} = \frac{N-1}{M + N - 1}
$$

（$N$ = stage 数，$M$ = micro-batch 数）

- $M = N$：bubble = $(N-1)/(2N-1) \approx 50\%$（很糟）
- $M \gg N$：bubble → 0（理想）

> 🔑 **结论**：要消 bubble，**micro-batch 数 $M$ 要远大于 stage 数 $N$**。所以 PP 训练时 batch 切得细。

### 3.4 Schedule：GPipe vs 1F1B vs Interleaved

| Schedule | 怎么排 | bubble | 内存 |
|---------|--------|--------|------|
| **GPipe** | 所有 micro 先 forward 完，再全部 backward | 大 | **大**（要存所有 activation）|
| **1F1B** | forward 和 backward 交错（1 forward 1 backward）| 大 | **小**（早 backward 释放 activation）|
| **Interleaved** | 每个 stage 切成 $V$ 个虚拟段，循环跑 | **小**（$V$ 倍降低 bubble）| 中 |

**Megatron 默认用 Interleaved 1F1B**——bubble 和显存的折中。

---

## 四、3D 并行：组合 DP + TP + PP

万亿参数训练用 **3D 并行**——三种范式组合：

```
假设 1024 卡 = 8 节点 × 8 卡/节点

   ┌── 机内 8 卡：TP=8（吃 NVLink）
   │
每个节点 ── 跨 8 节点：PP=8（吃 InfiniBand）
   │
全局 ── DP=16（1024 / (8×8) = 16 路数据并行）
```

**为什么这么分**：
- TP 通信最频繁 → 放机内（NVLink 高带宽）
- PP 通信次频繁（层间 activation）→ 放跨机（IB 中带宽）
- DP 通信最少（每步一次梯度同步）→ 放最外层

**Llama-3-405B 训练**（16384 H100）就是这种 3D 并行结构。

### 4.1 显存 + 计算的分摊

3D 并行下，每个维度的作用：

| 维度 | 切什么 | 主要解决 |
|------|--------|---------|
| TP | 层内权重 | 单层权重装不下 |
| PP | 不同层 | 总层数太多 |
| DP | 数据 + ZeRO | optimizer/activation 冗余 |
| ZeRO（叠加）| optimizer/grad/param | 进一步省显存 |

> 🎯 **现代大模型训练 = TP（机内）+ PP（跨机）+ DP+ZeRO（全局）**。这是 GPT-4/Llama-3/DeepSeek-V3 训练的标准范式。

---

## 五、序列并行（Sequence Parallel，补充）

TP 之外，还有 **Sequence Parallel**（Megatron 2022）：把 **activation 按序列维度切**（不是按 head/列切）。在 attention 之外的区域（LayerNorm、dropout）省 activation 显存。

配合 TP 用，能进一步省 5-10x activation 显存——长上下文训练必备。

---

## 六、一句话总结

> 🎯 **三句话**：
> 1. **TP（Megatron）**：层内切矩阵，column + row 组合让一个 MLP/attention 只 1 次 AllReduce——但通信频繁，**只适合机内（NVLink）**。
> 2. **PP**：层间切模型，micro-batch 流水线，bubble = $(N-1)/(M+N-1)$——$M \gg N$ 才高效。
> 3. **3D 并行**：TP（机内）+ PP（跨机）+ DP+ZeRO（全局）= 万亿参数训练标准范式。

---

## 七、阶段二完结 + 系列地图

至此「讲透分布式AI系统」核心 4 篇（00-03）完成：

```
00 显存账 + 四范式总览
   ├─ 01 DDP / FSDP（数据并行，最实用）
   ├─ 02 ZeRO（DeepSpeed，分冗余）
   └─ 03 TP / PP（Megatron，模型并行）+ 3D 并行
```

待写：04 Ray 调度 / 05 推理分布式 / 06 通信优化。

📌 **下一步**：回到 [README](./README.md)，或进阶段三（讲透AI应用全景 03-06 深挖）。
