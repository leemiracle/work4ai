# 01 · 数据并行 DDP / FSDP

> 数据并行是最实用的分布式范式。本章讲 **DDP**（经典数据并行，每卡完整模型）→ **FSDP**（PyTorch 原生的 ZeRO-3，分片数据并行）。FSDP 是现在微调大模型的事实标准（Llama/Qwen 微调首选）。
>
> 配套：[00 显存账](./00-为什么必须分布式.md) + [02 ZeRO](./02-ZeRO.md)

---

## 一、DDP（DistributedDataParallel）：经典数据并行

### 1.1 核心思路

每张卡有**完整模型副本**，但训练**不同 batch 的数据**。每步反向传播后，**AllReduce 同步梯度**——所有卡的模型保持一致。

```
GPU 0: 完整模型 + batch_0 → 前向 → 反向 → 梯度 g_0 ┐
GPU 1: 完整模型 + batch_1 → 前向 → 反向 → 梯度 g_1 ├→ AllReduce(g_0..g_3) → 平均梯度 g
GPU 2: 完整模型 + batch_2 → 前向 → 反向 → 梯度 g_2 │   → 每卡用 g 更新本地模型 → 保持一致
GPU 3: 完整模型 + batch_3 → 前向 → 反向 → 梯度 g_3 ┘
```

等价于用 batch_size = $4 \times \text{batch}_\text{per\_gpu}$ 做SGD，但 4 倍并行。

### 1.2 AllReduce（Ring 算法）

DDP 的关键操作是 **AllReduce**：所有卡都拿到所有卡梯度的**和**（或平均）。

**Ring AllReduce**（最常用）：
- N 张卡排成环
- 第 1 阶段（reduce-scatter）：每卡把自己的一段绕环传，N-1 步后每卡有 1/N 的聚合结果
- 第 2 阶段（all-gather）：把聚合结果绕环广播
- 总通信量：$2(N-1) \cdot \frac{\text{模型大小}}{N}$，每卡 $\frac{2(N-1)}{N} \cdot \text{模型大小}$

**关键**：通信量**和卡数 N 几乎无关**（$\frac{N-1}{N} \approx 1$）——这就是 DDP 能线性扩展的原因。

### 1.3 DDP 的瓶颈：大模型装不下

[00 篇](./00-为什么必须分布式.md) 算过：Llama-70B 训练要 840GB，DDP 每卡要装完整 840GB——单卡 80GB 装不下 1/10。

**所以 DDP 只适合小模型**（单卡能装下），大模型必须用 FSDP/ZeRO/TP/PP。

### 1.4 DDP 代码（PyTorch）

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

dist.init_process_group("nccl")  # 初始化 NCCL 后端
model = MyModel().cuda()
model = DDP(model, device_ids=[local_rank])   # 包装

for batch in dataloader:
    loss = model(batch)
    loss.backward()    # DDP 自动在反向时 AllReduce 梯度
    optimizer.step()
    optimizer.zero_grad()
```

---

## 二、FSDP：分片数据并行（PyTorch 原生 ZeRO-3）

### 2.1 核心思路

FSDP（Fully Sharded Data Parallel）= PyTorch 原生版的 ZeRO-3：**把模型参数、梯度、optimizer state 全部分片到各卡**，用到时临时聚合。

```
模型参数 W 切成 N 份：GPU 0 持有 W_0, GPU 1 持有 W_1, ...

前向某一层时：
   AllGather: 每卡聚齐这一层的完整 W → 前向算 → 释放 W
反向某一层时：
   AllGather: 聚齐 W → 反向算梯度 → 释放 W
   ReduceScatter: 把梯度分片聚合（每卡只留自己负责的梯度片）
optimizer 更新：
   每卡只更新自己负责的 W_i 片 → 不需要通信
```

### 2.2 显存对比

| 方法 | 每卡显存（Ψ=params）| 大模型能训吗 |
|------|---------------------|------------|
| DDP | 16Ψ | ❌（70B 要 840GB）|
| FSDP | 16Ψ/N + 临时 gather | ✅（N 足够大时每卡 < 80GB）|

Llama-70B（140GB 权重）用 8 卡 FSDP：每卡 ~18GB 权重片 + optimizer 片——单卡 80GB 够用。

### 2.3 FSDP 的代价：通信量增加

FSDP 每层前向 + 反向都要 AllGather（聚齐参数）+ ReduceScatter（分片梯度）——**通信量是 DDP 的 2-3 倍**。

| 方法 | 每步通信量 |
|------|----------|
| DDP | 2Ψ（梯度 AllReduce）|
| FSDP | ~4-6Ψ（参数 AllGather × 2 + 梯度 ReduceScatter）|

所以 FSDP **更依赖高带宽网络**——跨机 FSDP 效率会掉。

### 2.4 FSDP 的关键工程细节

1. **分片粒度**：按 layer 切（通常），每层独立 gather/release
2. **混合精度**：参数 FP16 存，master weight FP32（ZeRO 的做法）
3. **activation checkpointing**：配合用，进一步省激活显存
4. **CPU/NVMe offload**：极端情况把分片卸载到 CPU/SSD（DeepSpeed 的 ZeRO-Infinity）

### 2.5 FSDP 代码（PyTorch 2.x）

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP

model = MyModel().cuda()
model = FSDP(model)   # 自动分片

for batch in dataloader:
    loss = model(batch)
    loss.backward()    # FSDP 自动 AllGather/ReduceScatter
    optimizer.step()
```

> 🎯 **PyTorch 2.x 推荐 FSDP 而非 DDP** 训大模型。HuggingFace Trainer / Accelerate 都已支持 FSDP。

---

## 三、DDP vs FSDP 选型

| 场景 | 选 | 原因 |
|------|---|------|
| 小模型（< 单卡显存）| DDP | 通信少，效率最高 |
| 大模型微调（Llama-7B/13B）| DDP + LoRA | LoRA 让模型"小"了 |
| 大模型全参微调（70B）| **FSDP** | 单卡装不下 |
| 训练新大模型 | FSDP / ZeRO-3 / Megatron | 必须 |

---

## 四、一句话总结

> 🎯 **三句话**：
> 1. **DDP**：每卡完整模型 + 分数据，AllReduce 同步梯度——线性扩展但大模型装不下。
> 2. **FSDP**（PyTorch 原生 ZeRO-3）：参数/梯度/optimizer 全分片，用时 gather——能训大模型，但通信量 ×2-3。
> 3. 选型：小模型 DDP，大模型全参微调 FSDP，配 LoRA 用 DDP 即可。

📌 **下一步**：[02 ZeRO](./02-ZeRO.md) 看 DeepSpeed 怎么把 FSDP 思路做到极致（三阶段渐进分片）。
