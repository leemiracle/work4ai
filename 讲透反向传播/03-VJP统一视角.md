# 03 · VJP 统一视角：梯度形状为何与参数一致

> 反传里每个节点做的事，抽象成一句话：**接收上游梯度 $\bar v$，输出雅可比-向量积 $J^\top\bar v$**。而 $J^\top\bar v$ 自动与该节点的输入同形——这就是"梯度形状与参数一致"的**精确原因**，不是框架"特意保证"。

---

## 一、直觉层：每个节点是一台"梯度转换机"

把计算图想象成一排节点。反向时，每个节点做同一件事：

- **输入**：从下游收到一个"上游梯度" $\bar v$（告诉你"输出方向的梯度"）。
- **处理**：用自己的局部雅可比 $J$，算 $J^\top\bar v$。
- **输出**：把 $J^\top\bar v$ 传给上游节点。

这就是链式法则在张量上的机械执行。

## 二、数学层：VJP 与维度规则

### 2.1 一个算子的 VJP

设某算子 $g:\mathbb{R}^p \to \mathbb{R}^q$（输入 $p$ 维，输出 $q$ 维），雅可比 $J_g \in \mathbb{R}^{q\times p}$。

反传在该节点：输入上游梯度 $\bar v \in \mathbb{R}^q$，输出 $J_g^\top\bar v \in \mathbb{R}^p$。

**关键**：$J_g^\top\bar v \in \mathbb{R}^p$，**维度等于该算子的输入维度**。

### 2.2 形状一致的精确原因

以 `z1 = W1·x`（$W_1\in\mathbb{R}^{64\times1}$, $x\in\mathbb{R}^1$）为例：
- 雅可比 $J = \partial z_1/\partial x = W_1 \in \mathbb{R}^{64\times1}$。
- 反传：$\partial L/\partial x = J^\top\cdot\partial L/\partial z_1 = W_1^\top\cdot\partial L/\partial z_1 \in \mathbb{R}^1$。

**$\partial L/\partial x$ 的形状 = $x$ 的形状，由 $J^\top\bar v$ 的维度规则自动保证。**

> 🎯 推论：**任何"梯度形状对不上"的报错，根源一定是某个算子的 VJP 实现错了**（雅可比转置维度搞反），不是框架 bug。读懂这点，调试反传形状错误从"玄学"变"线性代数检查"。

## 三、常见算子的 VJP（速查）

| 算子 | 前向 | VJP（局部导数作用）|
|------|------|-------------------|
| 加法 $a+b$ | $a+b$ | 梯度原样传回（$J^\top=I$）|
| 乘法 $a\cdot b$ | $a\cdot b$ | $\partial L/\partial a = b\cdot\bar v$, $\partial L/\partial b = a\cdot\bar v$ |
| ReLU | $\max(0,x)$ | $\bar v \odot \mathbb{1}(x>0)$（掩码，见激活函数01章）|
| 矩阵乘 $Wx$ | $Wx$ | $\partial L/\partial W = \bar v\cdot x^\top$, $\partial L/\partial x = W^\top\bar v$ |
| sum | $\sum x_i$ | $\bar v$ 广播回原 shape |

> 注意 Linear 层的对称美：$\partial L/\partial W = \bar v\cdot x^\top$ 和 $\partial L/\partial x = W^\top\bar v$ 互为"转置对偶"——这正是雅可比转置的体现。

## 四、代码层：VJP 与形状实证

```bash
cd experiments && python3 02_vjp_and_shapes.py
```

```
f(x) = [x0*x1, x1+x2²]  (R³→R²)
VJP = J^T·v̄, v̄=[1,1]: [3, 3, 8]   (与输入 x 同形, R³)
MLP 每层 grad.shape == param.shape: 全部 True
```

## 五、批判性视角

- **VJP 的"自动同形"是数学必然，但有代价**：高维雅可比的转置-向量积仍需计算（框架靠算子级反向函数实现，不是真去构造大雅可比矩阵）。
- **手写反传时最易错的就是 VJP 维度**。梯度检查（实验04）就是用数值微分独立抓这类错。

---

## 📌 下一步

带着 VJP 视角，进入 [04-手算一个MLP的反传.md](04-手算一个MLP的反传.md)，把每一步链式法则亲手落到 numpy。

## ✍️ 练习

1. 为什么 `grad.shape` 必然等于 `param.shape`？用 VJP 维度规则解释。
2. `z = Wx`，写出 $\partial L/\partial W$ 和 $\partial L/\partial x$，验证它们互为转置对偶。
3. 跑实验02，把 f 改成 R²→R³，验证 VJP 与输入同形。
