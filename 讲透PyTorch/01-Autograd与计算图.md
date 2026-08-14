# 01 · Autograd 与计算图：反传的数学本质与 PyTorch 实现

> **PyTorch 的灵魂。** 这章回答两个问题：① 反传到底在算什么（数学本质）？② `loss.backward()` 在框架底层干了什么（工程实现）？很多人把"反向传播 = 链式法则"当口头禅——这是不精确的。链式法则是 200 年前的数学定理，反传是把它变成 **O(前向同阶)** 算法的具体执行。钉死这个区别，才算真懂 autograd。
>
> 如果只跑一次实验，**先跑 `experiments/01_autograd_from_scratch.py`**——90 行纯 Python 复刻整个 autograd 引擎，看完再读本章，一切豁然开朗。

---

## 一、为什么需要 autograd：数值微分为何不可行

反传的终极目标：**算出损失 $L$ 对每个参数 $\theta_i$ 的偏导数 $\partial L/\partial\theta_i$**（梯度），供梯度下降用。

最朴素的办法是**数值微分**（中心差分）：

$$
f'(x) \approx \frac{f(x+\epsilon) - f(x-\epsilon)}{2\epsilon}
$$

每算一个参数的梯度，要跑**两次前向**。百亿参数就要跑两千亿次前向——**彻底不可行**。

```bash
cd experiments && python3 13_numerical_vs_backprop.py
```

```
参数量   数值微分(s)   反传(s)   慢几倍
   100       0.012      0.0005     24x
   500       0.06       0.0005    120x
  1000       0.12       0.0006    200x
  2000       0.24       0.0006    400x
```

数值微分耗时随参数量**线性增长**（要跑 $n$ 次前向），反传**几乎不变**。推到千亿参数，差距是天文数字。**这就是为什么必须有 autograd**——它把"求所有偏导"的代价从 $O(n)$ 降到 $O(1)$（相对参数数）。

---

## 二、直觉层：前向记账，反向算账

### 2.1 一个比喻

- **前向传播**：你每做一笔交易，自动记一笔账（`+` 记成"加法"、`*` 记成"乘法"、`relu` 记成"截断"）。你不算结果怎么来的，只**记录"我是怎么算的"**。
- **反向传播**：月底要查"每个原始投入（参数）对最终盈亏（loss）有多大影响"。你**从最终结果倒着翻账本**，用链式法则把影响一路摊回每个输入。

### 2.2 关键：每个运算都留下"出生证明"

PyTorch 里，只要你对 `requires_grad=True` 的 tensor 做运算，结果 tensor 会带一个 `grad_fn`——记录"我是被哪个运算造出来的、怎么对这个运算求导"。

```python
x = torch.tensor([2.0], requires_grad=True)
y = x * 3        # y.grad_fn = <MulBackward>  ← 记住了"我是乘法"
```

> 🎯 这正是手写版（实验01）里每个 `Value` 的 `_backward` 和 `_prev`。PyTorch 的 `grad_fn` = 手写版的 `_backward`；`_prev` = 计算图的父子边。

---

## 三、数学层：反传 = 反向模式自动微分

### 3.1 链式法则 vs 反传：定理 vs 算法

| | 链式法则（数学）| 反传（算法）|
|---|---|---|
| 是什么 | 定理：$\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y}\frac{\partial y}{\partial x}$ 成立 | 算法：O(前向同阶) 算出所有 $\partial L/\partial\theta_i$ |
| 作用 | 告诉你等式**成立** | 告诉你**怎么高效算出来** |
| 关系 | 反传是链式法则在计算图上的**系统性、高效执行** |

### 3.2 反传算的是 VJP（雅可比-向量积）

给定可微函数 $f:\mathbb{R}^n \to \mathbb{R}^m$，反传一次算出的是**雅可比-向量积（VJP, Vector-Jacobian Product）**：

$$
\boxed{\;\text{反传输出} = J_f^\top \bar{v}, \quad J_f \in \mathbb{R}^{m\times n},\ \bar{v}\in\mathbb{R}^m\;}
$$

- $J_f$ 是 $f$ 的**雅可比矩阵**（$\partial f_i/\partial x_j$，函数在某点的最佳线性近似）。
- 反传**不显式构造 $J_f$**（太大），而是把它的转置直接作用在一个向量 $\bar v$ 上。
- $\bar v$ 是"上游梯度"（最终是 $\partial L/\partial L = 1$）。

> 🎯 **这一行公式就是反传的全部数学本质。** 所有手算推导（"局部梯度 × 上游梯度"）都是它的具体展开。

### 3.3 为什么是"反向"而非"前向"：m≪n 的不对称

自动微分（AD）有两种模式，差别在梯度沿计算图往哪个方向传：

| 模式 | 一次传播算出 | 算出**全部**梯度需要 |
|------|------------|-------------------|
| 前向模式（JVP）| $\partial y_j/\partial x_i$（**一个**输入方向）| **n 次**（n=输入维度）|
| 反向模式（VJP = 反传）| $J^\top\bar v$（**一个**输出方向对所有输入）| **m 次**（m=输出维度）|

深度学习的损失函数 $L(\theta): \mathbb{R}^n \to \mathbb{R}$：
- **输入 $n$**（参数）：数十亿到千亿。
- **输出 $m=1$**（loss 是标量）。

代入：
- 前向模式要跑 $n \sim 10^{10}$ 次 → **彻底不可行**。
- 反向模式只跑 $m=1$ 次 → **一次反传算出 loss 对所有参数的梯度**。

> 🎯 **这才是"一次反传算所有梯度"的数学根基**：不是魔法，是 $m\ll n$ 的结构让反向模式以 1 次代价胜出。**反传是深度学习唯一可行的求导方式，因为它精确卡在这个不对称上。**

**O(N) 一次的精确证明**：设前向有 $N$ 个算子，第 $i$ 个前向代价 $c_i$，总前向 $= \sum c_i = O(N)$。反传对每个算子做一次 VJP（$J_i^\top\bar v$），**算 $J_i^\top\bar v$ 的代价与算该算子前向 $c_i$ 同量级**（雅可比结构能复用前向中间结果）。所以反传总代价 $= \sum c_i = O(N)$，**与一次前向同阶**。

> 反传把"求所有偏导"的代价从 $O(n)$ 降到 $O(1)$（相对参数数）。**不是常数优化，是渐近阶的胜利。**

**推论**：若要算 loss 对**输入**的雅可比且输入维度小（如可解释性里 $\partial L/\partial x$, $x$ 是一张图），前向模式可能更快。PyTorch 提供 `torch.autograd.functional.jvp`（前向）和 `vjp`（反向）两种（实验14）。

### 3.4 VJP 与梯度形状为何一致

设某算子 $g:\mathbb{R}^p \to \mathbb{R}^q$（输入 $p$ 维，输出 $q$ 维），雅可比 $J_g \in \mathbb{R}^{q\times p}$。反传在该节点：输入上游梯度 $\bar v \in \mathbb{R}^q$，输出 $J_g^\top\bar v \in \mathbb{R}^p$。

**关键**：$J_g^\top\bar v \in \mathbb{R}^p$，**维度等于该算子的输入维度**。

以 `z1 = W1·x`（$W_1\in\mathbb{R}^{64\times1}$, $x\in\mathbb{R}^1$）为例：
- 雅可比 $J = \partial z_1/\partial x = W_1 \in \mathbb{R}^{64\times1}$。
- 反传：$\partial L/\partial x = J^\top\cdot\partial L/\partial z_1 = W_1^\top\cdot\partial L/\partial z_1 \in \mathbb{R}^1$。

**$\partial L/\partial x$ 的形状 = $x$ 的形状，由 $J^\top\bar v$ 的维度规则自动保证。**

> 🎯 推论：**任何"梯度形状对不上"的报错，根源一定是某个算子的 VJP 实现错了**（雅可比转置维度搞反），不是框架 bug。读懂这点，调试反传形状错误从"玄学"变"线性代数检查"。

### 3.5 常见算子的 VJP 速查

| 算子 | 前向 | VJP（局部导数作用）|
|------|------|-------------------|
| 加法 $a+b$ | $a+b$ | 梯度原样传回（$J^\top=I$）|
| 乘法 $a\cdot b$ | $a\cdot b$ | $\partial L/\partial a = b\cdot\bar v$, $\partial L/\partial b = a\cdot\bar v$ |
| ReLU | $\max(0,x)$ | $\bar v \odot \mathbb{1}(x>0)$（掩码，见「讲透激活函数01章」）|
| 矩阵乘 $Wx$ | $Wx$ | $\partial L/\partial W = \bar v\cdot x^\top$, $\partial L/\partial x = W^\top\bar v$ |
| sum | $\sum x_i$ | $\bar v$ 广播回原 shape |

> 注意 Linear 层的对称美：$\partial L/\partial W = \bar v\cdot x^\top$ 和 $\partial L/\partial x = W^\top\bar v$ 互为"转置对偶"——这正是雅可比转置的体现。

---

## 四、机制层：PyTorch 怎么自动反传

### 4.1 动态计算图（define-by-run）

前向时，PyTorch 自动建一张**有向无环图（DAG）**：节点是 tensor，边是运算。
- **叶子节点**：输入 `x` 和参数（`requires_grad=True`）
- **非叶子节点**：每步运算结果，带 `grad_fn`（记录"我是哪个运算算出来的"）

> 动态图（define-by-run）：每次前向都重建图，跑完就扔。这是 PyTorch 灵活、好调试的根基（对比 TF1 的静态图）。

### 4.2 backward() 的执行

`loss.backward()`：
1. 设 $\partial L/\partial L = 1$（反向起点）
2. 从 `loss` 节点出发，**拓扑逆序**遍历
3. 每个节点：用自己的 `grad_fn`（局部 VJP）把上游梯度传给输入
4. 梯度**累加**到叶子参数的 `.grad`

这正是实验01 手写引擎 `backward()` 的 C++ 高效版。

### 4.3 四个必懂的细节（实验02 透视）

**① 梯度累积：为何必须 `optimizer.zero_grad()`**

```python
# 实验02 实测: 连续 backward 不清零, 梯度一直加
第1次 backward: x.grad = 4
第2次 backward: x.grad = 8   ← 累加, 不是覆盖!
```

PyTorch 梯度**默认累加**（设计选择，支持梯度累积等技巧）。训练循环每步**必须** `zero_grad()`，否则梯度爆炸。这是新手最常踩的坑。

**② 计算图用后即焚**：`backward()` 后默认**释放图**（省内存）。同一个 loss 不能 backward 两次（除非 `retain_graph=True`）。

**③ 三种断梯度方式**：

| 方式 | 用途 |
|------|------|
| `with torch.no_grad():` | **推理/评估**时不建图（省内存+加速）|
| `tensor.detach()` | 把 tensor 从图上摘下当普通数据（如记录 loss 用 `loss.item()`）|
| `tensor.requires_grad_(False)` | 冻结参数（如预训练 backbone）|

**④ 叶子节点（leaf）**：用户创建的 `requires_grad=True` tensor 是叶子。它们的 `.grad` 才是优化器要用的。中间结果的 `.grad` 默认不保留（省内存）。

### 4.4 梯度检查：验证反传正确性

写自定义算子时，反传可能写错。用**梯度检查**（数值微分独立验证解析梯度）：

```bash
cd experiments && python3 16_gradient_check.py
```

```python
torch.autograd.gradcheck(f, x)   # 内部用中心差分对比解析梯度
```

实验16 演示：故意写错的 backward（如立方少了因子）会被 gradcheck 当场揭穿。**工程实践：开发/调试时用 gradcheck，训练时用反传（快）。**

---

## 五、代码层：从手写到自动

### 5.1 90 行手写 autograd 引擎（实验01）

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

### 5.2 手算一个 MLP 的反传（实验15）

把链式法则**逐步落到 numpy**，亲手复现 PyTorch 的 backward——证明反传不是黑盒。

MLP：$x(1) \xrightarrow{W_1,b_1} z_1(64) \xrightarrow{\text{ReLU}} a_1(64) \xrightarrow{W_2,b_2} \hat y(1)$，损失 $L = \tfrac12(\hat y - y)^2$。反向四步：

$$
\frac{\partial L}{\partial \hat y} = \hat y - y \;\Rightarrow\;
\frac{\partial L}{\partial W_2} = \frac{\partial L}{\partial \hat y}\cdot a_1^\top,\;
\frac{\partial L}{\partial a_1} = W_2^\top\cdot\frac{\partial L}{\partial \hat y}
$$

经 ReLU（掩码 VJP）：$\frac{\partial L}{\partial z_1} = \frac{\partial L}{\partial a_1}\odot\mathbb{1}(z_1>0)$，再到 $W_1, b_1$。

```bash
cd experiments && python3 15_mlp_by_hand.py
```

```
dL/dW1 手算 vs autograd 最大差: 2.6e-06  ✓
dL/dW2 手算 vs autograd 最大差: 3.8e-06  ✓   （全一致, 差在浮点误差）
```

**你能亲手用 numpy 复现 backward，说明反传彻底不是黑盒。** 最易错的步骤：ReLU 的掩码方向、矩阵乘的转置、广播（$b$ 的梯度要 sum over batch）。

---

## 六、训练三件套（贯穿全项目）

```
optimizer.zero_grad()   # 1. 清零(梯度累积)
loss = ...              # 2. 前向建图
loss.backward()         # 3. 反向求梯度(链式法则, 图随后释放)
optimizer.step()        # 4. 用梯度更新参数
```

这四步是所有 PyTorch 训练的骨架，每一步都对应 autograd 机制。反传算出的"原始梯度"还会被优化器加工——这条链是 `反传(算g) → 优化器(加工g) → 参数更新`（详见 [03-训练循环](03-训练循环.md)）。

---

## 七、批判性视角

- **反传不是唯一求导方法**，只是深度学习场景（$m\ll n$）下最高效的。输入维度小的场景，前向模式 AD 反而更快。
- **反传要求函数可微**。不可导点（ReLU 在 0）用次梯度约定；不可微操作（采样）要 reparameterization 绕过（见 [10-内核精读](10-PyTorch内核精读.md) 的反传边界）。
- **autograd 不免费**：建图+反向有内存和时间开销。所以推理一律 `no_grad`，取值用 `.item()`/`.detach()`。
- **动态图代价**：PyTorch 每次前向都重建图（灵活但慢）——这正是 `torch.compile` 要解决的问题（见 [06 章](06-编译与图模式.md)）。
- **反传是"数学理想 + 工程边界"的合体**。数学上是 VJP，工程上还要解决 mutation/view/version——这是 PyTorch backward 最硬核的部分，ezyang 2026 才首次系统讲清（见 [10-内核精读](10-PyTorch内核精读.md)）。

---

## 📌 下一步

- 跑 `experiments/02_autograd_internals.py`，透视真实的 `grad_fn`/`no_grad`/`detach`/梯度累积。
- 跑 `experiments/14_vjp_and_shapes.py`，亲手验证 VJP 与梯度形状一致、JVP vs VJP 的代价差异。
- 进入 [02-nnModule](02-nnModule与参数管理.md)：autograd 之上，模型如何组织。
- 想看梯度如何变成"学习"（消失/爆炸/裁剪/优化器加工）→ [03-训练循环](03-训练循环.md)。
- 想挖到 mutation/view 边界（反传最硬核）→ [10-内核精读](10-PyTorch内核精读.md)。

## 🔬 深度阅读（autograd 的真实实现）

- **ezyang "Autograd and Mutation"**（2026-03, blog.ezyang.com）— autograd 如何处理 in-place mutation 与 view aliasing：`CopySlices` 反向节点、base tensor 的 `grad_fn` rebase、多别名下的惰性 rebase（version counter）。**这是 autograd 最难的部分，ezyang 首次用 plain English 讲清。** 详见 [10-内核精读](10-PyTorch内核精读.md)。
- **PyTorch Developer Podcast** — 有 autograd / backward engine 专题单集。

## ✍️ 练习

1. 用一句话区分"链式法则"和"反向传播"。
2. 为什么深度学习用反向模式而非前向模式？用 $m,n$ 解释。O(N) 证明里，"算 $J_i^\top\bar v$ 与前向 $c_i$ 同量级"——为什么？
3. 反传一次算出的 $J^\top\bar v$，$\bar v$ 是什么？为什么最终取 1？
4. 为什么 `grad.shape` 必然等于 `param.shape`？用 VJP 维度规则解释。任何"梯度形状对不上"的报错根源是什么？
5. 为什么 `optimizer.zero_grad()` 不能省？不用会怎样（实验02 有实测）？
6. `loss.backward()` 后能再调一次吗？为什么？怎么才能？
7. 推理时为什么必须 `torch.no_grad()`？不用会浪费什么？
8. 跑 `experiments/15_mlp_by_hand.py`，故意把 `dL_dW2 = dL_dyhat @ a1`（漏了转置），看与 autograd 差多少，体会"形状一致≠数值正确"。
9. 写一个自定义 `torch.autograd.Function`（如 `MyReLU`），用 `gradcheck` 验证它。
10. （进阶）手写版的 `_backward` 用 `+=` 而非 `=`，为什么？（提示：一个节点可能被多条路径使用）
