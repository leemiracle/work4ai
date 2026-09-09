# tinytorch — 深度学习框架

> 参照 micrograd (Karpathy) + PyTorch 核心，从零实现深度学习框架。
> 理解这 5 个文件 = 理解 PyTorch 的核心设计。

## 模块清单

| 文件 | 对应 PyTorch | 核心内容 |
|------|-------------|---------|
| `tensor.py` | `torch.Tensor` / `autograd` | Value 类 + 计算图 + 反向传播 |
| `nn.py` | `torch.nn` | Linear/Embedding/LayerNorm/Dropout/Sequential/MLP |
| `optim.py` | `torch.optim` | SGD/Momentum/Adam/AdamW + CosineScheduler |
| `loss.py` | `torch.nn.functional` | MSE/CrossEntropy/BCE/Focal Loss |
| `train.py` | `Lightning/Keras` | DataLoader/Trainer/accuracy |
| `demo.py` | — | XOR + 月亮分类 + 正弦回归 |

## 用法

```python
from tinytorch import MLP, Adam, cross_entropy, Value

model = MLP(2, [8, 8, 2])  # 2→8→8→2
optimizer = Adam(model.parameters(), lr=0.01)

for epoch in range(100):
    optimizer.zero_grad()
    logits = model([Value(0), Value(1)])  # 前向
    loss = cross_entropy(logits, target_idx=1)  # 损失
    loss.backward()  # 反向
    optimizer.step()  # 更新
```

## 端到端演示

```bash
python3 projects/tinytorch/demo.py
# Demo 1: XOR 非线性分类
# Demo 2: 月亮分类（2D）
# Demo 3: 正弦函数回归
```

## csdiy 知识交叉

- [micrograd-100行吃透自动微分](../../source-reading/micrograd-100行吃透自动微分.md) — tensor.py 的原理来源
- [nanoGPT 读懂最小GPT](../../source-reading/nanoGPT-读懂最小GPT.md) — optim/loss/train 的参照
- [rust-ownership-精读](../../source-reading/rust-ownership-精读.md) — Value 的所有权类比
