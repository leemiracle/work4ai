# 权重初始化精读：为什么 std=0.02

> 参照：He et al. 2015 / GPT-2 / nanoGPT / PyTorch init
>
> csdiy 对应：nanoGPT精读 §7.2 + tinytorch/nn.py + tinytransformer

---

## 一、问题：随机初始化不是随便随机

```
# 好的初始化
w = random.gauss(0, 0.02)  → 训练成功

# 坏的初始化
w = random.gauss(0, 10.0)  → 梯度爆炸，loss=NaN
w = random.gauss(0, 0.001) → 梯度消失，模型不学
```

**初始化决定了训练能不能开始**。

---

## 二、Xavier 初始化（Glorot 2010）

### 适用：Sigmoid/Tanh 激活

```
W ~ U(-√(6/(fan_in+fan_out)), √(6/(fan_in+fan_out)))
# 或正态版
W ~ N(0, 2/(fan_in+fan_out))
```

### 原理

目标：让每一层的输出方差 = 输入方差（信号不放大也不缩小）。

```
Var(output) = fan_in × Var(W) × Var(input)

要 Var(output) = Var(input) → Var(W) = 1/fan_in
```

但 Xavier 同时考虑前向和反向 → 取 `2/(fan_in+fan_out)` 的折中。

---

## 三、He / Kaiming 初始化（He 2015）

### 适用：ReLU 激活

```
W ~ N(0, 2/fan_in)
```

### 为什么 ReLU 需要不同的初始化

ReLU 会把一半的激活值设为 0 → 方差减半 → 需要 2× 补偿。

```
Var(ReLU(x)) = Var(x) / 2

→ Var(W) = 2/fan_in  （补偿 ReLU 的方差减半）
```

### 你的 tinytorch/nn.py 的实现

```python
class Linear(Module):
    def __init__(self, fan_in, fan_out):
        # Kaiming 初始化（He 2015）
        std = math.sqrt(2.0 / fan_in)
        self.weight = [[Value(random.gauss(0, std)) ...] ...]
```

---

## 四、GPT-2 的 std=0.02（Transformer 标配）

### nanoGPT 精读 §7.2

```python
def _init_weights(self, module):
    if isinstance(module, nn.Linear):
        torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        if module.bias is not None:
            torch.nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Embedding):
        torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
```

### 为什么是 0.02

1. **不是从理论推导的**，是 GPT-2 论文的经验值
2. 对于 d_model=768：`std=0.02` → `Var=0.0004` → 每层的信号衰减可控
3. 配合**残差连接** → 深层网络的激活稳定

### 残差投影的额外缩放

```python
# nanoGPT §7.2 的关键 trick
if module._qkv_same_dim:
    # 对 c_proj.weight（残差路径的投影）额外缩放
    module.weight.data.normal_(mean=0.0, std=0.02 / math.sqrt(2 * n_layer))
```

**为什么除以 √(2×n_layer)**：残差路径在每层累加 → 层数越多方差累积越大 → 除以 √n 让残差贡献的方差与层数无关。

---

## 五、初始化不好的后果

### 梯度爆炸（std 太大）

```
W ~ N(0, 1.0)  → 每层放大信号 ~√fan_in 倍
12 层 Transformer → 信号放大 12√768 ≈ 330 倍
→ softmax 饱和 → 梯度 = 0 → 训练停滞
```

### 梯度消失（std 太小）

```
W ~ N(0, 0.0001)  → 每层缩小信号
12 层 → 信号缩小到机器精度以下 → 梯度 = 0
```

### 检测方法

```python
# 训练前检查激活统计
for name, param in model.named_parameters():
    if 'weight' in name:
        print(f"{name}: mean={param.mean():.6f}, std={param.std():.6f}")

# 训练中检查梯度
for name, param in model.named_parameters():
    if param.grad is not None:
        print(f"{name} grad: mean={param.grad.mean():.6f}, std={param.grad.std():.6f}")
```

**健康指标**：每层激活 std ≈ 1.0，梯度 std 在 [0.001, 1.0] 范围内。

---

## 六、现代初始化策略

| 策略 | 公式 | 适用 |
|------|------|------|
| Xavier | `std = √(2/(fan_in+fan_out))` | Sigmoid/Tanh |
| He | `std = √(2/fan_in)` | ReLU |
| GPT-2 | `std = 0.02` | Transformer |
| GPT-2 + 残差缩放 | `std = 0.02/√(2×n_layer)` | 残差投影 |
| Orthogonal | QR 分解生成正交矩阵 | RNN/LSTM |
| Truncated Normal | `N(0, std)` 截断到 [-2σ, 2σ] | CNN |

---

## 七、一句话总结

> 初始化的目标：让每层的信号方差≈1，梯度方差不爆炸不消失。
>
- Tanh 用 Xavier，ReLU 用 He，Transformer 用 std=0.02+残差缩放。
> **训练失败的第一检查项永远是初始化。**

---

*配套：[nanoGPT精读 §7.2](nanoGPT-读懂最小GPT.md) | [tinytorch/nn.py](../projects/tinytorch/nn.py) | [dropout精读](dropout-train-infer-精读.md)*
