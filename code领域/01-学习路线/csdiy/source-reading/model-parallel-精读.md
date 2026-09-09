# 模型并行精读：数据并行 / 张量并行 / 流水线并行

> 参照：Megatron-LM / DeepSpeed / FSDP / Ray
>
> csdiy 对应：consistent-hashing精读 + tinyllm + AI前沿

---

## 一、问题：7B 模型训练需要多少显存

```
LLaMA-7B 训练显存需求：
  模型权重 (BF16):     14 GB
  梯度 (BF16):        14 GB
  优化器状态 (FP32 AdamW): 56 GB  ← 最大！
  激活值 (BF16):      ~10 GB
  ─────────────────────────────
  总计:               ~94 GB → 一张 A100 (80GB) 放不下
```

**解法**：把模型/数据/梯度分到多张 GPU 上。

---

## 二、数据并行（Data Parallelism）

### 原理

```
GPU 0: 完整模型 + 数据 batch 0
GPU 1: 完整模型 + 数据 batch 1
GPU 2: 完整模型 + 数据 batch 2
GPU 3: 完整模型 + 数据 batch 3

→ 各自前向+反向 → AllReduce 梯度 → 同步更新
```

### DDP（DistributedDataParallel）

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

model = model.to(rank)
model = DDP(model, device_ids=[rank])
# DDP 自动处理梯度同步
```

### ZeRO 优化（DeepSpeed）

ZeRO 把数据并行的冗余状态分片：

```
ZeRO-1: 分片优化器状态 → 56GB / 4 GPU = 14GB
ZeRO-2: 分片优化器 + 梯度 → (56+14)/4 = 17.5GB
ZeRO-3: 分片优化器 + 梯度 + 模型权重 → (56+14+14)/4 = 21GB
```

**ZeRO-3 ≈ FSDP（PyTorch 原生版）**。

---

## 三、张量并行（Tensor Parallelism）

### 原理

把单个矩阵乘法切分到多 GPU 上。

### 行并行（Row Parallel）

```
Y = X @ W  →  W 切成 [W_0 | W_1]
GPU 0: Y_0 = X @ W_0
GPU 1: Y_1 = X @ W_1
Y = [Y_0 | Y_1]  ← 拼接
```

### 列并行（Column Parallel）

```
Y = X @ W  →  W 按行切成 [W_0] / [W_1]
GPU 0: Y_0 = X @ W_0
GPU 1: Y_1 = X @ W_1
Y = Y_0 + Y_1  ← AllReduce 求和
```

### Megatron-LM 的 MLP 并行

```
Linear1: 列并行 → 每张 GPU 算一半的 hidden dim
GeLU
Linear2: 行并行 → 每张 GPU 算一半，最后 AllReduce
→ 一次 AllReduce per MLP layer
```

### Attention 的并行

```
Multi-Head Attention 天然适合张量并行：
  GPU 0: head 0-3
  GPU 1: head 4-7
  → 各自独立计算 → 最后 AllReduce
```

---

## 四、流水线并行（Pipeline Parallelism）

### 原理

把模型**按层**切分到多 GPU。

```
GPU 0: Layer 0-7    → 中间结果发给 GPU 1
GPU 1: Layer 8-15   → 中间结果发给 GPU 2
GPU 2: Layer 16-23  → 中间结果发给 GPU 3
GPU 3: Layer 24-31  → 输出
```

### 气泡问题

```
朴素流水线（无重叠）:
GPU 0: [F0----][--------][--------][B0----]
GPU 1: [--------][F1----][--------][B1----]
GPU 2: [--------][--------][F2----][B2----]
GPU 3: [--------][--------][--------][F3-B3]
                    ↑ 气泡（GPU 空闲）↑
```

### 1F1B 调度（减少气泡）

```
交替前向-反向，减少空闲时间：
GPU 0: [F0][F1][F2][B0][B1][B2]
GPU 1:    [F0][F1][F2][B0][B1][B2]
...
```

---

## 五、三种并行对比

| 维度 | 数据并行 | 张量并行 | 流水线并行 |
|------|---------|---------|-----------|
| 切分对象 | 数据 | 权重矩阵 | 模型层 |
| 通信 | AllReduce（梯度） | AllReduce（每层） | Send/Recv（层间） |
| 通信量 | 大（梯度同步） | 中（每层结果） | 小（激活值） |
| 负载均衡 | 天然均衡 | 需要等大 head | 最后一层可能不等 |
| 扩展性 | 最好 | 中等 | 中等 |
| 跨节点 | ✅（网络够快） | ❌（通信太频繁） | ✅ |

---

## 六、3D 并行（全部组合）

训练超大模型时同时使用三种并行：

```
LLaMA-65B 训练（1024 GPU）:
  数据并行: 4 路（4 组 GPU）
  流水线并行: 8 路（65B / 8 ≈ 8B/层段）
  张量并行: 8 路（8 张 GPU/GPU 组）

  4 × 8 × 8 = 256 GPU/副本 × 4 副本 = 1024 GPU
```

### DeepSpeed/Megatron 的配置

```python
# 3D 并行配置
deepspeed_config = {
    "zero_optimization": {"stage": 3},  # ZeRO-3 数据并行
    "pipeline": {"stages": 8},          # 8 路流水线
    "tensor_model_parallel_size": 8,    # 8 路张量并行
}
```

---

## 七、选择指南

```
模型放得下单 GPU 吗？
├── 是 → 数据并行（DDP），最简单
├── 放不下，但加 ZeRO-3 可以 → FSDP/ZeRO-3
├── 还是放不下
│   ├── 层数多 → 加流水线并行
│   └── 层很宽 → 加张量并行
└── 超大模型（100B+）→ 3D 并行
```

---

## 八、一句话总结

> 数据并行切数据（最简单），张量并行切矩阵（通信密），流水线并行切层（通信少但有气泡）。
>
> 训练 LLaMA-65B = 数据并行 × 流水线 × 张量 = 3D 并行。
>
> **DeepSpeed/FSDP 把数据并行做到极致（ZeRO-3），张量+流水线并行用于超大规模。**

---

*配套：[consistent-hashing精读](consistent-hashing-精读.md) | [mixed-precision精读](mixed-precision-精读.md) | [kv-cache-原理](kv-cache-原理-精读.md)*
