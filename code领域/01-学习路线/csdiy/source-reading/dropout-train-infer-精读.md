# Dropout 精读：训练时失活、推理时激活

> 参照：Srivastava et al. 2014 / PyTorch nn.Dropout / tinytorch/nn.py
>
> csdiy 对应：tinytorch + nanoGPT精读 + 过拟合

---

## 一、问题：过拟合

模型在训练集上表现好（99%），但在测试集上差（70%）。

原因：模型"记住"了训练数据的噪声而非泛化模式。

### Dropout 的解法

每次前向传播时，随机"关闭"一部分神经元（设为 0）。

```
训练时:
  [0.5] [0.0] [0.3] [0.8]     第 1 次前向（随机关闭 #1）
  [0.0] [0.7] [0.3] [0.0]     第 2 次前向（随机关闭 #0, #3）
  [0.5] [0.7] [0.0] [0.8]     第 3 次前向（随机关闭 #2）

  → 每次都是不同的"子网络"在训练 → 类似集成学习
```

---

## 二、数学细节

### 标准 Dropout

训练时：以概率 p 将神经元设为 0。
```
输出: x_i * m_i,  m_i ~ Bernoulli(1-p)
```

推理时：不做 dropout，但**乘以 (1-p)** 补偿。

### Inverted Dropout（PyTorch/现代版）

训练时：以概率 p 将神经元设为 0，**同时乘以 1/(1-p)** 补偿。
```
输出: x_i * m_i / (1-p),  m_i ~ Bernoulli(1-p)
```

推理时：**不做任何操作**（直接输出 x_i）。

**为什么用 Inverted**：推理时不需要额外计算（部署更快）。

---

## 三、代码实现

### tinytorch 版（参照 tinytorch/nn.py）

```python
class Dropout(Module):
    def __init__(self, p=0.1):
        self.p = p

    def forward(self, x):
        if not self.training or self.p == 0:
            return x  # 推理模式：直接返回

        # 训练模式：Inverted Dropout
        scale = 1.0 / (1 - self.p)
        return [v * Value(0.0 if random.random() < self.p else scale)
                for v in x]
```

### PyTorch 版

```python
dropout = nn.Dropout(p=0.1)

# 训练模式
model.train()
output = dropout(x)  # 随机失活 + 缩放

# 推理模式
model.eval()
output = dropout(x)  # 直接返回 x（不变）
```

---

## 四、为什么 Dropout 防止过拟合

### 视角 1：集成学习

每次前向传播 = 一个不同的"子网络"在训练。

N 个神经元 + p=0.5 → 平均每次有 N/2 个激活 → 相当于训练了 2^(N/2) 个不同子网络。

推理时 = 所有子网络的"平均"（类似随机森林）。

### 视角 2：防止协同适应

没有 Dropout 时，两个神经元可能形成"依赖关系"（A 激活时 B 也必须激活）。

Dropout 迫使每个神经元**独立有用**——因为搭档随时可能被关闭。

### 视角 3：正则化

Dropout 等价于 L2 正则化的随机版本——约束权重幅度，防止过度依赖某个神经元。

---

## 五、Dropout 在 Transformer 中的应用

```python
# nanoGPT 的 Block（参照 nanoGPT精读 §六）
class Block:
    def forward(self, x):
        x = x + self.attn(self.ln1(x))       # Attention 子层
        x = x + self.ff(self.ln2(x))          # FFN 子层
        return x

# 实际上 dropout 用在多处：
# 1. Attention 权重上：dropout(attn_weights)
# 2. 残差连接前：dropout(attn_output)
# 3. FFN 输出：dropout(ffn_output)
# 4. 词嵌入上：dropout(token_emb + pos_emb)
```

GPT-2 的 dropout = 0.1。LLaMA 的 dropout = 0.0（大量数据时不需要）。

---

## 六、Dropout 变体

| 变体 | 区别 | 用在哪 |
|------|------|--------|
| Standard | 随机失活神经元 | 全连接层 |
| Spatial | 随机失活整个 channel | CNN |
| Attention | 随机失活 attention 权重 | Transformer |
| DropConnect | 随机失活权重（不是输出） | 理论研究 |
| DropPath | 随机跳过整个残差块 | ResNet/Vision Transformer |

---

## 七、train()/eval() 的工程重要性

```python
# 忘记切换到 eval() 是最常见的 bug
model.train()   # ← 训练模式（有 Dropout）
output = model(x)  # ← 随机失活 → 每次结果不同

model.eval()    # ← 推理模式（无 Dropout）
output = model(x)  # ← 确定性 → 每次结果相同
```

**忘记 model.eval() = 推理结果每次都不同 = 无法调试**。

---

## 八、一句话总结

> Dropout = 训练时随机关闭神经元（防过拟合）+ Inverted 缩放（推理时无需补偿）。
>
> train() 模式有 Dropout，eval() 模式没有。
>
> **模型性能差距的 30% 来自正则化技巧——Dropout 是其中最简单有效的。**

---

*配套：[tinytorch/nn.py](../projects/tinytorch/nn.py) | [nanoGPT精读](nanoGPT-读懂最小GPT.md) | [transformer-attention-deep-精读](transformer-attention-deep-精读.md)*
