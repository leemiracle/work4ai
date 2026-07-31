# 04 · 手算一个 MLP 的反传

> 前面讲透了原理（VJP/反向模式）。本章把链式法则**逐步落到 numpy 代码**，亲手复现 PyTorch 的 backward——证明反传不是黑盒。这是"理解反传"最扎实的一步。

---

## 一、网络与前向

MLP：$x(1) \xrightarrow{W_1,b_1} z_1(64) \xrightarrow{\text{ReLU}} a_1(64) \xrightarrow{W_2,b_2} \hat y(1)$

$$
z_1 = W_1 x + b_1,\quad a_1 = \text{ReLU}(z_1),\quad \hat y = W_2 a_1 + b_2
$$

损失（单样本 MSE）：$L = \tfrac12(\hat y - y)^2$

## 二、反向：从 $L$ 往回，每步一个 VJP

### 第 1 步：损失对输出
$$
\frac{\partial L}{\partial \hat y} = \hat y - y
$$

### 第 2 步：到 $W_2, b_2$（Linear 的 VJP）
$$
\frac{\partial L}{\partial W_2} = \frac{\partial L}{\partial \hat y}\cdot a_1^\top,\qquad
\frac{\partial L}{\partial b_2} = \frac{\partial L}{\partial \hat y}
$$
继续往回传：
$$
\frac{\partial L}{\partial a_1} = W_2^\top\cdot\frac{\partial L}{\partial \hat y}
$$

### 第 3 步：经 ReLU（掩码 VJP）
$$
\frac{\partial L}{\partial z_1} = \frac{\partial L}{\partial a_1}\odot\mathbb{1}(z_1>0)
$$
> ReLU 的局部导数就是 $(z_1>0)$ 的 0/1 掩码（见「讲透激活函数01章」）。

### 第 4 步：到 $W_1, b_1$
$$
\frac{\partial L}{\partial W_1} = \frac{\partial L}{\partial z_1}\cdot x^\top,\qquad
\frac{\partial L}{\partial b_1} = \frac{\partial L}{\partial z_1}
$$

**每一步都是"上游梯度 × 该层局部导数（VJP）"**，形状自动与参数一致。

## 三、代码层：numpy 手算 vs autograd 对拍

```bash
cd experiments && python3 03_mlp_by_hand.py
```

```python
# 前向
z1 = W1 @ x + b1; a1 = np.maximum(0, z1); yhat = W2 @ a1 + b2; L = 0.5*(yhat-y)**2
# 反向
dL_dyhat = yhat - y
dL_dW2 = dL_dyhat @ a1.T; dL_db2 = dL_dyhat
dL_da1 = W2.T @ dL_dyhat; dL_dz1 = dL_da1 * (z1>0)
dL_dW1 = dL_dz1 @ x.T; dL_db1 = dL_dz1
```

与 PyTorch autograd 对拍：

```
dL/dW1 手算 vs autograd 最大差: 2.6e-06  ✓
dL/db1 手算 vs autograd 最大差: 0       ✓
dL/dW2 手算 vs autograd 最大差: 3.8e-06  ✓
dL/db2 手算 vs autograd 最大差: 9.5e-07  ✓
```

**全一致（差在浮点误差）。你能亲手复现 backward，说明反传彻底不是黑盒。**

## 四、批判性视角

- **手算是理解工具，不是生产工具**。真实网络用框架自动算（实验01 的手写引擎也只是教学）。
- **最易错的步骤**：ReLU 的掩码方向、矩阵乘的转置、广播（$b$ 的梯度要 sum over batch）。用梯度检查（实验04）抓错。
- **batch 维度的处理**：单样本清晰，多样本时梯度是对 batch 的平均（PyTorch loss 默认 mean）。

---

## 📌 下一步

理解了手算反传，进入 [05-计算图与自动微分.md](05-计算图与自动微分.md)，看 PyTorch 怎么自动完成这一切（动态图/grad_fn/拓扑排序）。

## ✍️ 练习

1. 把上述 MLP 改成 batch=5（$x$ 是 (1,5)），手算时 $b$ 的梯度为什么要 `.sum(axis=1)`？
2. 把 ReLU 换成 sigmoid，重写第 3 步（局部导数变成 $a_1(1-a_1)$）。
3. 跑实验03，故意把 `dL_dW2 = dL_dyhat @ a1`（漏了转置），看与 autograd 差多少，体会"形状一致≠数值正确"。
