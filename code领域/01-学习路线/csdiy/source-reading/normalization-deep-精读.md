# Normalization 精读：BatchNorm vs LayerNorm vs RMSNorm

> 参照：Ioffe 2015 (BN) / Ba 2016 (LN) / Zhang 2019 (RMSNorm)
>
> csdiy 对应：tinynorm(原) + transformer-attention-deep + tinytorch/nn.py

---

## 一、为什么需要 Normalization

### 内部协变量偏移（Internal Covariate Shift）

深层网络中，每层的输入分布随着前层权重更新而变化 → 后层需要不断适应 → 训练变慢。

### Normalization 的目标

**固定每层的输入分布**（均值=0，方差=1）→ 训练更稳定、更快收敛。

---

## 二、BatchNorm（Ioffe 2015）

### 计算

```
# 对一个 batch 的同一维度做归一化
μ = mean(x[:, dim])     # 跨 batch 的均值
σ² = var(x[:, dim])     # 跨 batch 的方差
x_hat = (x - μ) / √(σ² + ε)
output = γ × x_hat + β  # 可学习的缩放和偏移
```

### 特点

- **跨样本归一化**：用同一个 batch 内所有样本的统计量
- 依赖 batch size（太小 → 统计量不准）
- 训练/推理行为不同（推理用 running mean/var）
- CNN 标配

### 问题

```
batch_size=1 → BN 无效（方差=0）
序列模型 → 每个 timestep 的 BN 统计量不同 → 困惑
```

---

## 三、LayerNorm（Ba 2016）

### 计算

```
# 对单个样本的所有维度做归一化
μ = mean(x[sample, :])    # 跨维度的均值
σ² = var(x[sample, :])    # 跨维度的方差
x_hat = (x - μ) / √(σ² + ε)
output = γ × x_hat + β
```

### 特点

- **跨维度归一化**：每个样本独立计算
- **不依赖 batch size**（batch=1 也能用）
- 训练/推理行为一致
- **Transformer 标配**（GPT/BERT/Llama 全用）

### 你的 tinytorch/nn.py 的实现

```python
class LayerNorm(Module):
    def __init__(self, dim, eps=1e-5):
        self.gamma = [Value(1.0) for _ in range(dim)]
        self.beta = [Value(0.0) for _ in range(dim)]
    def forward(self, x):
        n = len(x)
        mean = sum(v.data for v in x) / n
        var = sum((v.data - mean) ** 2 for v in x) / n
        std = sqrt(var + self.eps)
        return [(x[i] - Value(mean)) / Value(std) * self.gamma[i] + self.beta[i]
                for i in range(n)]
```

### Pre-LN vs Post-LN

```
Post-LN（原始 Transformer）:
  x = LayerNorm(x + Sublayer(x))    # LN 在残差之后
  → 深层训练不稳定

Pre-LN（GPT-2+，包括 nanoGPT）:
  x = x + Sublayer(LayerNorm(x))    # LN 在子层之前
  → 残差路径无 LN → 梯度更通畅 → 深层稳定
```

---

## 四、RMSNorm（Zhang 2019，LLaMA 用）

### 计算

```
# LayerNorm 的简化版：去掉均值，只用 RMS
rms = √(mean(x²) + ε)
output = x / rms × γ    # 只有缩放，没有偏移
```

### vs LayerNorm

| 维度 | LayerNorm | RMSNorm |
|------|-----------|---------|
| 均值减法 | ✅ | ❌ |
| 方差归一化 | ✅ | 用 RMS 替代 |
| 偏移 β | ✅ | ❌ |
| 参数量 | 2d (γ+β) | d (只有 γ) |
| 速度 | 标准 | **快 7-64%** |
| 效果 | 标准 | 接近 LN |

### 为什么 LLaMA 选 RMSNorm

1. 更快（减均值操作看似简单但在大规模训练中累积显著）
2. 效果不比 LN 差
3. 参数更少（只有 γ，没有 β）

---

## 五、GroupNorm / InstanceNorm（补充）

### GroupNorm（Wu 2018）

```
把 d 维分成 G 组，每组做 LayerNorm
→ 折中：不像 BN 依赖 batch，也不像 LN 跨所有维度
```

适用：CNN（特别是小 batch 场景）。

### InstanceNorm

```
每个样本每个 channel 独立归一化
→ 风格迁移用（去除对比度/亮度差异）
```

---

## 六、完整对比表

| 方法 | 归一化维度 | 依赖 batch | 参数 | 训练≠推理 | 代表 |
|------|-----------|-----------|------|---------|------|
| BatchNorm | 跨样本×同维度 | ✅ | 2d + running | ✅ | ResNet |
| LayerNorm | 跨维度×同样本 | ❌ | 2d | ❌ | Transformer |
| RMSNorm | 跨维度×同样本 | ❌ | d | ❌ | LLaMA |
| GroupNorm | 跨维度组 | ❌ | 2d | ❌ | CNN |
| InstanceNorm | 每样本每通道 | ❌ | 2d | ❌ | StyleGAN |

---

## 七、选择决策树

```
你的模型是什么？
│
├── Transformer (GPT/BERT/LLaMA)
│   ├── 需要最快速度？→ RMSNorm（LLaMA/Qwen）
│   └── 标准选择？→ LayerNorm（GPT-2/BERT/nanoGPT）
│
├── CNN (ResNet/VGG)
│   ├── batch 够大 (≥32)？→ BatchNorm
│   └── batch 小？→ GroupNorm
│
└── RNN/LSTM
    → LayerNorm（不能用 BN）
```

---

## 八、一句话总结

> Normalization 固定每层输入分布 → 训练更稳更快。
>
- BN 跨样本（CNN），LN 跨维度（Transformer），RMSNorm 是 LN 的快速版（LLaMA）。
> **Pre-LN 比 Post-LN 更稳定 → GPT-2+ 全用 Pre-LN。**

---

*配套：[transformer-attention-deep](transformer-attention-deep-精读.md) | [tinytorch/nn.py](../projects/tinytorch/nn.py) | [weight-init精读](weight-init-精读.md)*
