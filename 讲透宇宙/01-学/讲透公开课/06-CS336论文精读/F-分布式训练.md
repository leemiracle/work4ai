# F · 分布式训练系统（6 篇）

> **CS336 L7-L8 + A2 的核心**——如何在多 GPU/多机上训大模型。
> 对应讲座：**L7、L8（parallelism）**｜ 作业：**A2（分布式训练）**

---

## F1. Shazeer et al. – Mixture of Experts (2017) ⭐⭐

- **链接**：[arxiv.org/abs/1701.06538](https://arxiv.org/pdf/1701.06538.pdf) · Google

**核心**：MoE 的奠基。FFN 替换成多个"专家"FFN，**软路由**（top-k 加权）。让参数容量远大于计算量。

**💡 工程经验**：
1. 这是 Switch Transformer（C1.6，top-1 硬路由）的前身。软路由更平滑但计算更贵。
2. MoE 的本质：**稀疏激活**——每个 token 只用部分参数，所以能"以相同 FLOPs 塞更多知识"。
3. 现代 MoE（DeepSeek-V3、Mixtral、Qwen-MoE）都是这条线的工业实现。

---

## F2. GPipe – Efficient Gradient Partitioning (2018) ⭐⭐

- **链接**：[arxiv.org/abs/1811.06965](https://arxiv.org/pdf/1811.06965.pdf) · Google

**核心问题**：模型大到单 GPU 放不下（如 100B 模型权重 ~200GB），怎么训？

**方法**：**流水线并行（Pipeline Parallelism）**——把模型按层切成 $N$ 段，每段放一个 GPU。前向时数据像流水线一样流过 GPU 1→2→...→N；反向时反向流回。

**关键 trick**：**micro-batching**——把一个大 batch 切成 $M$ 个 micro-batch，让多个 micro-batch 在流水线里**重叠执行**（GPU 1 处理 micro-batch 2 时，GPU 2 在处理 micro-batch 1），提高利用率。

**💡 工程经验**：
1. **流水线 bubble（气泡）**是主要开销——首尾的 GPU 在等数据。micro-batch 越多，bubble 占比越小。
2. GPipe 是**同步**流水线（所有 micro-batch 算完再反向）——简单但 bubble 大。后续 PipeDream 用异步减少 bubble 但更复杂。
3. CS336 A2 教的就是这类并行。

---

## F3. Shoeybi et al. – Megatron-LM (2019) ⭐⭐⭐

- **链接**：[arxiv.org/abs/1909.08053](https://arxiv.org/pdf/1909.08053.pdf) · NVIDIA

**核心问题**：单层（如大的 FFN）就超过单 GPU 显存，流水线并行不够。

**方法**：**张量并行（Tensor Parallelism）**——把单个矩阵乘法**切到多个 GPU**。对 $Y = XW$，把 $W$ 按列切：$W = [W_1, W_2]$，每个 GPU 算 $XW_i$，最后拼接。对 FFN 的两层，巧妙利用分块让中间不需通信。

```
FFN:   h = activation(X W1)       # W1 按列切, 各GPU独立算, 不需通信
       out = h W2                  # W2 按行切, 各GPU算部分和, 一次 all-reduce
```

**💡 工程经验**：
1. **张量并行把单层切到多 GPU**——和流水线（切层间）正交，可组合。
2. **通信开销**：每个 transformer block 要 2 次 all-reduce（attention + FFN）。所以张量并行**跨 GPU 通信要快**（NVLink），否则通信吃掉收益。
3. Megatron-LM 是 NVIDIA 的开源训练框架，被广泛采用。CS336 A2 用 PyTorch DDP/FSDP，但概念相通。

**📍 CS336 角色**：L7/L8 + A2。

---

## F4. Rajbhandari et al. – ZeRO (2019) ⭐⭐⭐

- **链接**：[arxiv.org/abs/1910.02054](https://arxiv.org/abs/1910.02054) · Microsoft

**核心问题**：数据并行（DDP）每个 GPU 都存**完整**的：① 模型权重 ② 梯度 ③ 优化器状态（Adam 的 $m,v$，是权重 2 倍大）。70B 模型单卡要 ~1.4TB——爆显存。

**方法**：**ZeRO（Zero Redundancy Optimizer）**——把这些状态**分片**到各 GPU，用时再聚合：

| 阶段 | 分片什么 | 显存节省 |
|------|---------|---------|
| **ZeRO-1** | 优化器状态 | 4× |
| **ZeRO-2** | + 梯度 | 8× |
| **ZeRO-3** | + 权重 | ~N×（N=GPU数） |

ZeRO-3 等价于**全分片**——每个 GPU 只存 $1/N$ 的所有东西，前向/反向时按需 all-gather 拉取。

**💡 工程经验**：
1. **ZeRO 是训练百亿+模型的标配**——PyTorch FSDP 本质就是 ZeRO-3 的官方实现。
2. **通信换显存**——ZeRO-3 每层都要 all-gather 权重，通信量大。所以 **ZeRO-2 常是甜点**（省 8 倍显存，通信只多梯度 reduce）。
3. CS336 A2 让学生实现 DDP/ZeRO 风格的分布式训练。
4. **DeepSpeed**（微软）是 ZeRO 的开源实现框架，和 Megatron 组合是工业标配。

**📍 CS336 角色**：**L7 核心 + A2**。

---

## F5. Narayanan et al. – Megatron 3D Parallelism (2021) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2104.04473](https://arxiv.org/pdf/2104.04473.pdf) · NVIDIA

**核心**：**组合三种并行**——数据并行（DP）+ 张量并行（TP）+ 流水线并行（PP），构成 **3D 并行**。

**关键设计**：
- **TP 放最内层**（NVLink 同机，通信快）
- **PP 放中间层**（跨机但每步通信大）
- **DP 放最外层**（跨机，all-reduce 通信）
- 配比：如 3072 GPU = 8(TP) × 12(PP) × 32(DP)

**结果**：训练 **1T 参数模型**，**52% MFU**（Model FLOPs Utilization）。

**💡 工程经验**：
1. **MFU 是衡量训练效率的金标准**——理论 FLOPs 的百分之多少真正用于计算（其余被通信/等待浪费）。50%+ 是优秀。
2. **并行的"洋葱"结构**：TP 在最内（通信最频但量小）→ PP 中间 → DP 最外（通信最少但量最大）。这个层次是经验最优。
3. **重叠通信与计算**——前向算第 $i$ 层时，同时预取第 $i+1$ 层的权重（通信），隐藏延迟。
4. 这是 LLaMA、GPT-4 等大模型训练的工业实现基础。

**📍 CS336 角色**：**L7/L8 核心**。

---

## F6. Megascale (2024) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2402.15627](https://arxiv.org/pdf/2402.15627.pdf) · 字节跳动

**核心**：在 Megatron 3D 基础上进一步优化，训练 **175B 模型在 12,288 GPU 上达 55.2% MFU**（比 Megatron 的 52% 又高）。

**关键优化**：
- **通信-计算重叠**更精细（算子级调度）
- **并行 attention/FFN**（GPT-J 式）
- **LAMB 优化器**支持超大 batch
- **sliding window attention**

**💡 工程经验**：
1. **从 52% 到 55% MFU 靠的是无数细节优化**——每个百分点都是数百万美元的 GPU 时间节省。
2. Megascale 代表 **2024 训练系统工程的最高水平**。DeepSeek-V3 报告（2024 底）称达 ~57% MFU，又进一步。
3. 这些优化大多在算法层（算子调度），不改模型架构——**系统工程的价值常被低估**。
4. CS336 L7 用这些当"工业最佳实践"参照。

**📍 CS336 角色**：L7 前沿案例。

---

## F 类总结：并行技术栈

```
单 GPU 放不下模型?
├─ 流水线并行 (GPipe): 切层间
├─ 张量并行 (Megatron): 切层内
└─ ZeRO/FSDP: 分片权重/梯度/优化器状态

万卡训练?
└─ 3D 并行: TP(内) × PP(中) × DP(外)
    + 通信-计算重叠
    + 追求 55%+ MFU
```

**MFU 计算速查**（[Bahdanau FLOPs Calculus](./D-Scaling-Laws.md#d3)）：
$$\text{MFU} = \frac{\text{实际 tokens/sec} \times 6N}{\text{GPU数} \times \text{GPU峰值FLOPS}}$$

> **核心经验**：分布式训练是**系统工程**，不是调几个 API。理解 3D 并行的层次结构 + 通信开销 + MFU 计算，才能真正训大模型。CS336 A2 让学生从 DDP 起步，逐步理解 ZeRO/TP/PP——这是从"会跑 PyTorch"到"会训大模型"的关键一跃。
