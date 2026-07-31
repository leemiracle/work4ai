# 01 · Autograd 与计算图

> **PyTorch 的灵魂。** 这章回答：你写 `loss.backward()`，框架底层到底干了什么？答案藏在「计算图 + 链式法则」里。如果你只跑一次，**先去跑 `experiments/01_autograd_from_scratch.py`**——90 行纯 Python 复刻了整个 autograd 引擎，看完再读本章，一切豁然开朗。

---

## 一、直觉层：前向记账，反向算账

### 1.1 一个比喻

- **前向传播**：你每做一笔交易，自动记一笔账（`+` 记成"加法"、`*` 记成"乘法"、`relu` 记成"截断"）。你不算结果怎么来的，只**记录"我是怎么算的"**。
- **反向传播**：月底要查"每个原始投入（参数）对最终盈亏（loss）有多大影响"。你**从最终结果倒着翻账本**，用链式法则把影响一路摊回每个输入。

### 1.2 关键：每个运算都留下"出生证明"

PyTorch 里，只要你对 `requires_grad=True` 的 tensor 做运算，结果 tensor 会带一个 `grad_fn`——记录"我是被哪个运算造出来的、怎么对这个运算求导"。

```python
x = torch.tensor([2.0], requires_grad=True)
y = x * 3        # y.grad_fn = <MulBackward>  ← 记住了"我是乘法"
```

> 🎯 这正是手写版（实验01）里每个 `Value` 的 `_backward` 和 `_prev`。PyTorch 的 `grad_fn` = 手写版的 `_backward`；`_prev` = 计算图的父子边。

---

## 二、数学层：链式法则在图上的执行

### 2.1 计算图是有向无环图（DAG）

前向时，PyTorch 自动建一张 DAG：

```
叶子(参数x,w,b) → 中间节点(运算) → ... → 输出(loss)
```

每个节点知道：自己的输入是谁、自己怎么求导（局部雅可比）。

### 2.2 反向 = 拓扑排序 + 链式法则

反向传播从 loss 出发（$\frac{\partial L}{\partial L}=1$），按**拓扑逆序**遍历每个节点，把"上游传来的梯度"乘以"本节点的局部导数"，传给输入：

$$
\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} \cdot \frac{\partial y}{\partial x}
$$

这和「讲透激活函数 01 章」的 ReLU 反向（$\frac{\partial L}{\partial X}=\frac{\partial L}{\partial Y}\odot M$）是**同一件事**——只不过那里是手算一个算子，这里是框架对整张图自动做。

> 数学上，反向传播 = **计算图上的链式法则** = 向量-雅可比积（VJP）。PyTorch 用反向模式自动微分（reverse-mode AD），对**多输入单输出**（loss 是标量）最高效。

---

## 三、四个必须懂的细节（实验02 透视）

### 3.1 梯度累积：为何必须 `optimizer.zero_grad()`

```python
# 实验02 实测: 连续 backward 不清零, 梯度一直加
第1次 backward: x.grad = 4
第2次 backward: x.grad = 8   ← 累加, 不是覆盖!
```

**PyTorch 设计选择**：梯度默认**累加**（为支持梯度累积等技巧）。训练循环每步**必须** `zero_grad()`，否则梯度爆炸。这是新手最常踩的坑。

### 3.2 计算图用后即焚

`backward()` 后，默认**释放计算图**（省内存）。所以同一个 loss 不能 backward 两次（除非 `retain_graph=True`）。

### 3.3 三种"切断梯度"的方式

| 方式 | 用途 |
|------|------|
| `with torch.no_grad():` | **推理/评估**时不建图（省内存+加速）|
| `tensor.detach()` | 把 tensor 从图上摘下当普通数据（如记录 loss 用 `loss.item()`）|
| `tensor.requires_grad_(False)` | 冻结参数（如预训练 backbone）|

### 3.4 叶子节点（leaf）

用户创建的 `requires_grad=True` tensor 是叶子。它们的 `.grad` 才是优化器要用的。中间结果的 `.grad` 默认不保留（省内存）。

---

## 四、代码层：90 行看穿 autograd

```bash
cd experiments && python3 01_autograd_from_scratch.py
```

手写引擎的核心（对应 PyTorch）：

```python
class Value:
    def __mul__(self, other):           # ← 对应 grad_fn=<MulBackward>
        out = Value(self.data * other.data, (self, other))
        def _backward():                 # ← 局部导数: d(a*b)/da=b
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out
    def backward(self):                  # ← 拓扑排序 + 逆序调用
        ...; self.grad = 1.0
        for v in reversed(topo): v._backward()
```

实验结果：手写 autograd 与 `torch.autograd` 对拍 **0 误差**，还能训练 MLP 拟合抛物线（loss 0.22→0.059）。**这就是 `loss.backward()` 的全部本质**，PyTorch 只是用 C++ 在张量级高效做同样的事。

---

## 五、训练三件套（贯穿全项目）

```
optimizer.zero_grad()   # 1. 清零(梯度累积)
loss = ...              # 2. 前向建图
loss.backward()         # 3. 反向求梯度(链式法则, 图随后释放)
optimizer.step()        # 4. 用梯度更新参数
```

这四步是所有 PyTorch 训练的骨架，每一步都对应 autograd 机制。

---

## 六、批判性视角

- **autograd 不免费**：建图+反向有内存和时间开销。所以推理一律 `no_grad`，取值用 `.item()`/`.detach()`。
- **高阶梯度**：PyTorch 支持二阶（`create_graph=True`），但贵且少用（主要 GAN/元学习）。
- **动态图代价**：PyTorch 每次前向都重建图（灵活但慢）——这正是 `torch.compile` 要解决的问题（见 06 章）。

---

## 📌 下一步

- 跑 `experiments/02_autograd_internals.py`，透视真实的 `grad_fn`/`no_grad`/`detach`/梯度累积。
- 进入 [02-nnModule](02-nnModule与参数管理.md)：autograd 之上，模型如何组织。
- 想看优化器如何用这些梯度 → [03-训练循环](03-训练循环.md)。

## 🔬 深度阅读（autograd 的真实实现）
- **ezyang "Autograd and Mutation"**（2026-03, blog.ezyang.com）— autograd 如何处理 in-place mutation 与 view aliasing：`CopySlices` 反向节点、base tensor 的 `grad_fn` rebase、多别名下的惰性 rebase（version counter）。**这是 autograd 最难的部分，ezyang 首次用 plain English 讲清。**
- **PyTorch Developer Podcast** — 有 autograd / backward engine 专题单集。
- 配合本教程实验01（90 行手写引擎）食用，从原理到真实实现打通。

## ✍️ 练习

1. 为什么 `optimizer.zero_grad()` 不能省？不用会怎样（实验02 有实测）？
2. `loss.backward()` 后能再调一次吗？为什么？怎么才能？
3. 推理时为什么必须 `torch.no_grad()`？不用会浪费什么？
4. （进阶）手写版的 `_backward` 用 `+=` 而非 `=`，为什么？（提示：一个节点可能被多条路径使用）
