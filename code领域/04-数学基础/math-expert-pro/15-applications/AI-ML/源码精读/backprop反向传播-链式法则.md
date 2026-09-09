# 反向传播精读：计算图构建 + 链式法则

> 参照：micrograd + PyTorch autograd + cs231n Backprop
>
> csdiy 对应：tinytorch/tensor.py + micrograd精读 + nanoGPT精读

---

## 一、计算图：前向传播的副产品

每个运算自动构建一个有向无环图（DAG）。

```
# 代码
a = Value(2.0)
b = Value(3.0)
c = a * b       # 创建节点 c，边 a→c, b→c
d = c + a       # 创建节点 d，边 c→d, a→d
e = d.tanh()    # 创建节点 e，边 d→e

# 构建的 DAG：
#     a ──→ c ──→ d ──→ e
#     │           ↑
#     └───────────┘
```

每个 Value 节点记录：
- `data`：当前值
- `grad`：梯度（反向传播时填充）
- `_prev`：父节点集合
- `_backward`：局部梯度计算函数

---

## 二、链式法则：反向传播的核心

### 数学基础

如果 `y = f(g(x))`，则 `dy/dx = f'(g(x)) × g'(x)`。

对于复杂图，链式法则是**沿路径连乘**：

```
e = tanh(d)
d = c + a
c = a * b

∂e/∂a = ∂e/∂d × ∂d/∂a        （d 对 a 的贡献）
       + ∂e/∂d × ∂d/∂c × ∂c/∂a  （d→c→a 的贡献）

     = sech²(d) × 1 + sech²(d) × 1 × b
     = sech²(8) × (1 + 3)
     ≈ 0.000035
```

### 为什么需要拓扑排序

梯度必须**从输出到输入**逆序传播。但图中的节点可能有多条路径（如 a 同时影响 c 和 d）。

拓扑排序保证：**在计算某节点的梯度前，它所有后继节点的梯度已经算完**。

```
拓扑序: [a, b, c, d, e]
逆序传播: e → d → c → b → a
```

---

## 三、tinytorch/tensor.py 的实现

```python
def backward(self):
    # 1. 拓扑排序（DFS 后序）
    topo = []
    visited = set()
    def build_topo(v):
        if v not in visited:
            visited.add(v)
            for child in v._prev:
                build_topo(child)
            topo.append(v)
    build_topo(self)

    # 2. 种子梯度
    self.grad = 1.0

    # 3. 逆序传播（链式法则）
    for node in reversed(topo):
        node._backward()
```

每个运算的 `_backward` 定义了局部梯度：

```python
# 乘法：z = x * y
# ∂z/∂x = y,  ∂z/∂y = x
def _backward():
    x.grad += y.data * z.grad   # 注意是 +=（多路径累加）
    y.grad += x.data * z.grad

# 加法：z = x + y
# ∂z/∂x = 1,  ∂z/∂y = 1
def _backward():
    x.grad += 1 * z.grad
    y.grad += 1 * z.grad

# tanh：z = tanh(x)
# ∂z/∂x = 1 - tanh²(x) = 1 - z²
def _backward():
    x.grad += (1 - z.data**2) * z.grad
```

---

## 四、梯度累加：多条路径的梯度求和

当节点 a 通过多条路径影响输出 e 时，梯度需要**累加**：

```
a → c → d → e
a → d → e

∂e/∂a = ∂e/∂d × ∂d/∂a  +  ∂e/∂d × ∂d/∂c × ∂c/∂a
```

代码中用 `+=` 而非 `=`（参照 PyTorch autograd 的累加梯度行为）。

---

## 五、为什么 PyTorch 比 tinytorch 快 1000 倍

| 维度 | tinytorch | PyTorch |
|------|-----------|---------|
| 数据类型 | Python float | C++ tensor（连续内存） |
| 矩阵运算 | Python for 循环 | BLAS / cuDAGEMM |
| 图构建 | Python 对象 | C++ autograd engine |
| 并行 | 无 | GPU CUDA |

但**数学原理完全一样**。tinytorch 用最透明的方式展示了 autograd 的本质。

---

## 六、一句话总结

> 反向传播 = 前向构建 DAG → 拓扑排序 → 逆序沿链式法则求导。
>
> 每个节点的 `_backward` 定义了局部梯度，路径交汇处用 `+=` 累加。
>
> **理解了这 15 行拓扑排序代码，你就理解了 PyTorch autograd 的全部核心。**

---

*配套：micrograd精读（`micrograd-100行吃透自动微分.md`） | tinytorch/tensor.py（`../projects/tinytorch/tensor.py`）*
