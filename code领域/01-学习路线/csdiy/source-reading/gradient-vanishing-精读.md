# 梯度消失/爆炸精读：深层网络训练的核心难题

> 参照：Bengio 1994 / He 2015 / ResNet (He 2016) / LayerNorm
>
> csdiy 对应：backprop-graph精读 + weight-init精读 + tinytorch

---

## 一、问题本质

### 梯度消失

```
深层网络反向传播时，梯度需要连乘很多层的导数：

∂L/∂w_1 = ∂L/∂y × ∂y/∂h_n × ... × ∂h_2/∂h_1 × ∂h_1/∂w_1

如果每层导数 |∂h_i/∂h_{i-1}| < 1:
  → 连乘 N 层 → 梯度指数衰减 → 接近 0 → 前面层不学习

10 层 × 每层导数=0.5 → 梯度 = 0.5^10 = 0.001 → 几乎为 0
```

### 梯度爆炸

```
如果每层导数 > 1:
  → 连乘 → 梯度指数增长 → NaN → 训练崩溃

10 层 × 每层导数=2.0 → 梯度 = 2^10 = 1024 → 参数被推飞
```

---

## 二、不同激活函数的影响

### Sigmoid（最差）

```
σ'(x) = σ(x)(1-σ(x))
最大值: σ'(0) = 0.25

→ 每层最多 0.25 → 10 层 = 0.25^10 ≈ 0.0000001
→ 几乎必然梯度消失
```

### Tanh（好一点）

```
tanh'(x) = 1 - tanh²(x)
最大值: tanh'(0) = 1.0

→ 最好情况导数=1，但大部分区域 < 1
→ 仍然容易梯度消失
```

### ReLU（好很多）

```
ReLU'(x) = 1 if x > 0, else 0

→ 正区间导数恒为 1 → 不衰减！
→ 但负区间导数=0 → "死神经元"（Dead ReLU）
```

### GELU / SwiGLU（Transformer 标配）

```
GELU'(x) ≈ 1（正区间），平滑过渡
→ 比 ReLU 更好的梯度流 → Transformer 标配

SwiGLU(x) = SiLU(xW) × xV → LLaMA 使用
→ 门控机制 → 梯度流更好
```

---

## 三、解决方案

### ① 残差连接（ResNet, He 2016）

```
标准: h = f(x)
残差: h = x + f(x)

∂h/∂x = 1 + f'(x)
→ 恒定有 1 的梯度通道 → 梯度不消失！

→ ResNet 让 1000+ 层训练成为可能
→ Transformer 的每个 Block 都有残差连接
```

### ② 层归一化（LayerNorm）

```
h = LayerNorm(x + Sublayer(x))

→ LayerNorm 把激活值归一化到均值=0, 方差=1
→ 防止激活值逐层放大/缩小
```

### ③ 好的初始化（参照 weight-init精读）

```
He 初始化: std = √(2/fan_in)
→ 保证前向方差≈1 + 反向方差≈1
→ 配合 ReLU → 梯度稳定
```

### ④ 梯度裁剪（Gradient Clipping）

```
# 防止梯度爆炸
if grad_norm > max_norm:
    grad = grad × (max_norm / grad_norm)

→ nanoGPT/Llama 训练标配
→ max_norm = 1.0
```

### ⑤ 门控机制（LSTM/GRU）

```
LSTM 的细胞状态 c_t 有加法更新：
  c_t = f_t × c_{t-1} + i_t × g_t

∂c_t/∂c_{t-1} = f_t
→ 遗忘门 f_t 可以保持接近 1 → 梯度不消失
→ LSTM 解决了 RNN 的梯度消失问题
```

---

## 四、Transformer 中的梯度流

### Pre-LN vs Post-LN（参照 normalization精读）

```
Post-LN: x = LayerNorm(x + Sublayer(x))
  → 残差路径上有 LayerNorm → 梯度被 LN 缩放
  → 深层训练不稳定

Pre-LN: x = x + Sublayer(LayerNorm(x))
  → 残差路径上无 LayerNorm → 梯度直接回传
  → 深层训练稳定 → GPT-2+ 全用 Pre-LN
```

### 残差路径的重要性

```
Transformer Block 的梯度流：

x → [LayerNorm → Attention] → +x → [LayerNorm → FFN] → +x

两条梯度路径：
  ① 主路径: x → Sublayer → ... → 梯度可能衰减
  ② 残差路径: x → +x → 梯度=1（恒定）

→ 残差连接保证深层 Transformer 的梯度健康
```

---

## 五、诊断梯度问题

### 检测梯度消失

```python
for name, param in model.named_parameters():
    if param.grad is not None:
        grad_norm = param.grad.norm().item()
        print(f"{name}: grad_norm = {grad_norm:.6f}")

# 健康指标: 0.001 < grad_norm < 10
# 梯度消失: grad_norm < 1e-6（前面层）
# 梯度爆炸: grad_norm > 100
```

### 检测激活值分布

```python
# 在 forward 中 hook
def activation_hook(module, input, output):
    print(f"{module}: mean={output.mean():.4f}, std={output.std():.4f}")

# 健康: mean≈0, std≈1（LayerNorm 后）
# 异常: std→0（消失）或 std→∞（爆炸）
```

---

## 六、一句话总结

> 梯度消失 = 连乘导数 < 1 → 指数衰减。
> 解法：残差连接（恒定梯度=1）+ LayerNorm + He 初始化 + ReLU/GELU。
>
> 梯度爆炸 = 连乘导数 > 1 → 指数增长。
> 解法：梯度裁剪（限制范数）。
>
> **残差连接是深度学习最重要的发明——没有它就没有 ResNet/Transformer/GPT。**

---

*配套：[backprop-graph精读](backprop-graph-精读.md) | [weight-init精读](weight-init-精读.md) | [normalization-deep精读](normalization-deep-精读.md) | [tinytorch/tensor.py](../projects/tinytorch/tensor.py)*
