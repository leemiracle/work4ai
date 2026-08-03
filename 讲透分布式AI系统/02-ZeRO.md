# 02 · ZeRO 三阶段（DeepSpeed）

> ZeRO（Zero Redundancy Optimizer）是 DeepSpeed 的核心创新——**发现数据并行里有 3 种冗余，可以渐进地消除**。ZeRO-1/2/3 三阶段，每一阶段多分一份、显存多省一倍。FSDP（[01 篇](./01-DDP与FSDP.md)）本质就是 ZeRO-3 的 PyTorch 原生实现。本章把 ZeRO 的数学讲透。
>
> 配套：DeepSpeed [ZeRO 论文](https://arxiv.org/abs/1910.02054)（SC 2020）

---

## 一、ZeRO 的核心洞察：DP 的三种冗余

[00 篇](./00-为什么必须分布式.md) 算过，混合精度 Adam 训练每卡显存 = **16Ψ bytes**（Ψ = 参数数）：

| 部分 | 大小 | DP 下是否冗余 |
|------|------|------------|
| 参数 FP16 | 2Ψ | **是**（每卡完整副本）|
| 梯度 FP16 | 2Ψ | **是** |
| Master 权重 FP32 | 4Ψ | **是** |
| Optimizer momentum FP32 | 4Ψ | **是** |
| Optimizer variance FP32 | 4Ψ | **是** |

**ZeRO 的洞察**：DP 模式下，每卡都存了完整副本——**这 16Ψ 有大量冗余，可以分摊到 N 卡**。

但分摊有代价：要通信重新聚合。ZeRO 的艺术就是"**分多少 vs 通信多少**"的权衡。

---

## 二、ZeRO 三阶段

### 2.1 ZeRO-1：分 Optimizer State

**思路**：optimizer state（master + momentum + variance = 12Ψ）有 N 卡份冗余——分成 N 片，每卡只存 12Ψ/N。

```
每卡显存：2Ψ(参数) + 2Ψ(梯度) + 12Ψ/N(optimizer)
通信：和 DDP 一样（梯度 AllReduce）
更新：每卡只更新自己的 optimizer 片，然后 AllGather 参数片
```

**显存收益**：从 16Ψ → 4Ψ + 12Ψ/N。N=64 时，从 16Ψ → 4.19Ψ——**省 4 倍**。

**通信代价**：基本和 DDP 一样（不增加）。

### 2.2 ZeRO-2：+ 分 Gradient

**思路**：梯度（2Ψ）也分片。反向算完梯度后，**ReduceScatter**——每卡只保留自己负责的梯度片。

```
每卡显存：2Ψ(参数) + 2Ψ/N(梯度) + 12Ψ/N(optimizer)
通信：ReduceScatter（比 AllReduce 略少）
```

**显存收益**：4Ψ + 14Ψ/N。N=64 时 → 4.22Ψ。

**通信代价**：基本不变（ReduceScatter 是 AllReduce 的一半）。

### 2.3 ZeRO-3：+ 分 Parameter（= FSDP）

**思路**：连参数（2Ψ）也分片。前向/反向用到时 **AllGather** 临时聚齐。

```
每卡显存：16Ψ/N
通信：每层 AllGather × 2（前向+反向）—— 通信量增加 2-3 倍
```

**显存收益**：16Ψ/N。N=64 时 → 0.25Ψ——**线性下降，理论上无限卡就能训无限大模型**。

**通信代价**：明显增加（这就是 [01 篇](./01-DDP与FSDP.md) FSDP 的代价）。

### 2.4 三阶段对比表

| 阶段 | 分什么 | 每卡显存 | 通信量（相对 DDP）|
|------|--------|---------|------------------|
| DDP（baseline）| 不分 | 16Ψ | 1× |
| **ZeRO-1** | optimizer state | $4\Psi + 12\Psi/N$ | 1× |
| **ZeRO-2** | + gradient | $2\Psi + 14\Psi/N$ | ~1× |
| **ZeRO-3**（= FSDP）| + parameter | $16\Psi/N$ | ~2-3× |

> 🎯 **关键权衡**：ZeRO-1/2 是"**免费午餐**"（省显存不增通信），ZeRO-3 是"**显存换通信**"（省显存但通信翻倍）。

### 2.5 实例：Llama-70B（Ψ = 70B）

| 方法 | 每卡显存 | 8 卡 H100（80GB）够吗 |
|------|---------|---------------------|
| DDP | 16×70B = 1120 GB | ❌ 远不够 |
| ZeRO-1 | 4×70 + 12×70/8 = 280+105 = 385 GB | ❌ |
| ZeRO-2 | 2×70 + 14×70/8 = 140+122 = 262 GB | ❌ |
| ZeRO-3 | 16×70/8 = 140 GB | ❌（要 2 卡才够）|
| ZeRO-3 + 32 卡 | 16×70/32 = 35 GB | ✅ |

**结论**：Llama-70B 训练至少要 ZeRO-3 + 32 卡以上。

---

## 三、ZeRO-Infinity：卸载到 CPU/NVMe

ZeRO-3 还不够？把分片**卸载到 CPU 内存甚至 NVMe SSD**：

- **ZeRO-Offload**（2021）：optimizer state 卸到 CPU（GPU 算前向/反向，CPU 算 optimizer 更新）
- **ZeRO-Infinity**（2021）：参数/梯度/optimizer 全部能卸到 CPU/NVMe

**代价**：PCIe 带宽（~32 GB/s）远低于 GPU HBM（~3 TB/s）——慢 100 倍。但能训超大模型。

> 🔑 **使用场景**：单机/少卡训超大模型（研究/原型）。生产用多卡 ZeRO-3 更快。

---

## 四、ZeRO 的局限

1. **通信量大**（ZeRO-3）：跨机时效率掉得厉害
2. **不适合超长上下文**：activation 没分片（要配合 activation checkpointing 或 sequence parallel）
3. **和 TP 不一定兼容**：某些 Megatron + ZeRO 组合要小心

**所以超大规模训练用 3D 并行**（DP + TP + PP），不是纯 ZeRO。见 [03 篇](./03-TP与PP.md)。

---

## 五、DeepSpeed 的使用

```python
 import deepspeed
model, optimizer, _, _ = deepspeed.initialize(
    model=model,
    optimizer=optimizer,
    config={
        "zero_optimization": {
            "stage": 3,              # ZeRO-3
            "offload_optimizer": {"device": "cpu"},   # 可选 CPU 卸载
            "offload_param": {"device": "cpu"},
        },
        "train_batch_size": ...,
    }
)
```

**实际选型**：多数情况用 HuggingFace Trainer 的 `deepspeed` 配置，比手写简单。FSDP（PyTorch 原生）是替代选择，不需 DeepSpeed 库。

---

## 六、一句话总结

> 🎯 **三句话**：
> 1. ZeRO 洞察：DP 下 optimizer state / gradient / parameter 三种冗余可分摊。
> 2. 三阶段渐进：ZeRO-1（分 optimizer，免费午餐）→ ZeRO-2（+ 梯度，仍免费）→ **ZeRO-3（+ 参数 = FSDP，显存换通信）**。
> 3. 显存公式：$16\Psi \to 16\Psi/N$（ZeRO-3），代价是通信量 ×2-3。

📌 **下一步**：[03 TP/PP](./03-TP与PP.md) 学模型并行——切矩阵/切层，是超大规模训练的另一条主线。
