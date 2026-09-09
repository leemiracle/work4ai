# micrograd：100 行吃透自动微分

> 精读 `karpathy/micrograd`，源码来自 `/github-repos/references/micrograd/`。
> 整个库只有两个文件：`engine.py`（94 行，反向传播引擎）+ `nn.py`（60 行，神经网络层）。
> 读完这两份文件，你就理解了 PyTorch `autograd` 的全部核心思想。

---

## 一、它到底干了什么

用一句话说：**micrograd 是一个能自动求导的标量计算器**。你用 Python 的 `+ - * **` 写出任意表达式，它会自动算出每个变量对最终结果的梯度。

跑通后的效果（来自 `test/test_engine.py` 第 4-11 行的真实用法）：

```python
x = Value(-4.0)
z = 2 * x + 2 + x
q = z.relu() + z * x
h = (z * z).relu()
y = h + q + q * x
y.backward()           # 一行触发反向传播
print(x.grad)          # 自动算出 dy/dx
```

同一套表达式，micrograd 算出的梯度跟 PyTorch 的 `torch.Tensor` 逐位相等（测试文件第 14-26 行拿 PyTorch 做了对照）。这就是它的威力：**用 94 行复刻了工业级 autograd 的本质**。

---

## 二、反向传播的本质：链式法则 + 拓扑序

在看代码之前，先把数学直觉钉死。反向传播只有两件事：

1. **链式法则**：如果 `y = f(x)`，`z = g(y)`，那么 `dz/dx = (dz/dy) * (dy/dx)`。每个算子只需知道"我的输出对每个输入的局部导数"，剩下的交给链式法则层层传递。
2. **拓扑序**：要正确传播梯度，必须**先算完所有依赖、最后回到输入**。也就是把计算图排成一个"从输出到输入"的线性序列，逆序遍历。

micrograd 把每个数学运算变成一个图节点。每个节点记住三件事：
- **怎么算前向**（算出 `data`）
- **怎么算反向**（把下游传来的 `grad` 往上游推，这个逻辑存在 `_backward` 闭包里）
- **我的爹妈是谁**（存在 `_prev` 里，用于拓扑排序）

下面逐段拆开看。

---

## 三、逐行精读 `engine.py`

### 3.1 Value 类的构造：五个字段定天下

```python
class Value:
    """ stores a single scalar value and its gradient """

    def __init__(self, data, _children=(), _op=''):
        self.data = data
        self.grad = 0
        # internal variables used for autograd graph construction
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op # the op that produced this node, for graphviz / debugging / etc
```

逐字段解释：

| 字段 | 含义 | 为什么这么设计 |
|------|------|----------------|
| `data` | 这个标量的当前值 | 前向计算的结果 |
| `grad` | 梯度，初始 0 | **必须初始为 0**，后面反向传播用 `+=` 累加 |
| `_backward` | 反向传播函数，默认空操作 | **闭包**，每个运算算完后动态定义。这是整个引擎的灵魂 |
| `_prev` | 产生本节点的输入节点集合 | 拓扑排序要靠它回溯父节点 |
| `_op` | 产生本节点的运算名（如 `'+'`） | 仅用于可视化/调试，不参与计算 |

**程序员视角的关键洞察**：`_backward` 被设计成一个**闭包**而非类方法。每执行一次加法，就当场创建一个新的闭包，闭包捕获了 `self`、`other`、`out` 三个引用。这样反向传播时调用 `out._backward()` 就能把梯度精确地发回给参与这次加法的两个操作数。换种写法（比如把反向逻辑写成 if-else 分支）会非常笨重，闭包是最优雅的方案。

**坑在哪**：`grad` 初始化为 0 而不是 None，是因为一个变量可能被多个路径引用（比如 `y = x + x`，x 出现在两个分支），梯度必须**累加**而非覆盖。后面你会看到所有 `_backward` 里都是 `+=`。

### 3.2 加法 `__add__`：链式法则的第一次出场

```python
def __add__(self, other):
    other = other if isinstance(other, Value) else Value(other)
    out = Value(self.data + other.data, (self, other), '+')

    def _backward():
        self.grad += out.grad
        other.grad += out.grad
    out._backward = _backward

    return out
```

**第 1 行**：`other = other if isinstance(other, Value) else Value(other)` —— 这是**类型提升**。让你可以写 `Value(2) + 3`，Python 会自动把 `3` 包成 `Value(3)`。没有这行，`x + 1` 直接报错，用起来极不方便。

**第 2 行**：创建输出节点 `out`，把 `self` 和 `other` 记为它的 `_children`。这就是在**构建计算图**。

**第 4-6 行**：定义反向闭包。这里藏着加法的导数规律：加法对两个输入的局部导数都是 1，所以 `self.grad += out.grad`（即 `1 * out.grad`），`other.grad += out.grad` 同理。

**为什么用 `+=` 而不是 `=`**：考虑 `y = x + x`。前向时 x 参与了两次加法，反向时 x 的 `_backward` 会被调用两次。如果用 `=`，第二次会覆盖第一次的梯度，结果错误。用 `+=` 才符合链式法则（一个节点对 x 的总贡献是所有路径之和）。

**`+=` 的陷阱**：闭包捕获的是 `self` 和 `other` 的**引用**，不是值。如果在调用 `_backward` 之前 `out.grad` 还没被设置好，就会累加到错误值上。所以反向传播必须保证"先设置好下游 grad，再调用上游 `_backward`"——这正是后面 `backward()` 里拓扑排序干的事。

### 3.3 乘法 `__mul__`：乘积法则登场

```python
def __mul__(self, other):
    other = other if isinstance(other, Value) else Value(other)
    out = Value(self.data * other.data, (self, other), '*')

    def _backward():
        self.grad += other.data * out.grad
        other.grad += self.data * out.grad
    out._backward = _backward

    return out
```

乘法的导数是 `d(ab)/da = b`，`d(ab)/db = a`。所以反向时：
- `self` 收到的梯度 = `other.data * out.grad`（即"另一个因子的值 × 下游梯度"）
- `other` 收到的梯度 = `self.data * out.grad`

**这里的精髓**：`other.data` 和 `self.data` 用的是**前向计算时的快照值**，闭包已经捕获了当时的引用。这解释了为什么自动微分要求"先完整跑一遍前向、再跑反向"——反向依赖前向算出的中间值。

**换成你会怎么写**：新手可能把导数公式硬编码成 `self.grad += self.data * out.grad`（把 a 对 a 求导写成 a），这是错的。乘法里 a 的导数是 b 不是 a。这种细节正是"手写反向传播容易出错"的原因，而 micrograd 把每个算子的局部导数封装好，消除人肉出错。

### 3.4 幂运算 `__pow__`：只支持常数次幂

```python
def __pow__(self, other):
    assert isinstance(other, (int, float)), "only supporting int/float powers for now"
    out = Value(self.data**other, (self,), f'**{other}')

    def _backward():
        self.grad += (other * self.data**(other-1)) * out.grad
    out._backward = _backward

    return out
```

**第 2 行的 assert**：刻意限制 `other` 必须是 `int/float`，不能是 `Value`。为什么？因为如果底数和指数都是变量，那就是 `a^b`，导数要用 `a^b * ln(a)`，实现复杂。micrograd 为了"教学清晰"，只处理 `x^n` 这种指数为常数的情形，导数就是 `n * x^(n-1)`。

**注意 `_children`**：只有 `(self,)`，没有 other，因为 other 是个 Python 数，不在图里。

这个 `__pow__` 是个**基础积木**。后面你会看到，除法、减法全是用它和加法、乘法拼出来的——这就是"最小算子集"的设计哲学。

### 3.5 ReLU：分段函数的导数

```python
def relu(self):
    out = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')

    def _backward():
        self.grad += (out.data > 0) * out.grad
    out._backward = _backward

    return out
```

ReLU 的导数：输入 > 0 时为 1，否则为 0。代码用 `(out.data > 0)` 得到一个布尔值，Python 里 `True` 当 1、`False` 当 0，乘上 `out.grad` 就完成了梯度门控。

**为什么用 `out.data > 0` 而不是 `self.data > 0`**：等价。但用 `out.data` 语义更清晰——"输出为正的位置才放梯度过去"。这是 Karpathy 的小巧思，可读性更好。

**坑**：ReLU 在 0 点导数未定义，这里 `data == 0` 时 `out.data == 0`，`out.data > 0` 为 False，所以梯度为 0。这是工程上常见的约定（PyTorch 也是这么处理的）。

### 3.6 `backward()`：拓扑排序——整个引擎最核心的 15 行

```python
def backward(self):

    # topological order all of the children in the graph
    topo = []
    visited = set()
    def build_topo(v):
        if v not in visited:
            visited.add(v)
            for child in v._prev:
                build_topo(child)
            topo.append(v)
    build_topo(self)

    # go one variable at a time and apply the chain rule to get its gradient
    self.grad = 1
    for v in reversed(topo):
        v._backward()
```

**这是反向传播的全部魔法所在。** 分两步看：

**第一步：DFS 拓扑排序（第 3-11 行）**

`build_topo(v)` 是一个经典的后序 DFS（post-order DFS）。逻辑是：
1. 如果 v 没访问过，标记为已访问
2. 先递归访问 v 的所有子节点
3. **子节点都访问完了，再把 v 自己追加进 topo**

为什么是"先递归子节点、最后追加自己"？因为这样保证：**任何节点出现在 topo 列表时，它所有的依赖（输入）都已经排在它前面**。这就是拓扑序的定义。

举个具体例子，`y = (x*2) + x` 的图：x 是叶子，`x*2` 依赖 x，`+` 依赖 `x*2` 和 x。拓扑排序后 `topo = [x, x*2, y]`（x 必须最先，y 必须最后）。

**第二步：逆序调用 `_backward`（第 14-16 行）**

- `self.grad = 1`：根节点的梯度是 1（∂y/∂y = 1），这是链式法则的起点种子。
- `for v in reversed(topo)`：逆序遍历，从 y 一路回到 x。每访问一个节点就调它的 `_backward()`，把它的 grad 按"局部导数"分配给上游。

**为什么必须逆序**：因为 `_backward` 读的是 `out.grad`（下游传来的梯度）。只有下游先被处理、grad 已正确累加，上游才能拿到正确的值。拓扑序保证"v 的所有下游排在 v 后面"，逆序就保证"v 被处理时它的所有下游已经处理完"。这是**数据依赖决定的顺序**，错一点全盘皆错。

**为什么不用 BFS 或其他顺序**：只有拓扑逆序能保证每个节点被处理时，它从下游收到的梯度已经齐全。这正是反向传播"back"这个词的字面含义——从后往前。

### 3.7 魔术方法：用最少的算子拼出完整算术

```python
def __neg__(self): # -self
    return self * -1

def __radd__(self, other): # other + self
    return self + other

def __sub__(self, other): # self - other
    return self + (-other)

def __rsub__(self, other): # other - self
    return other + (-self)

def __rmul__(self, other): # other * self
    return self * other

def __truediv__(self, other): # self / other
    return self * other**-1

def __rtruediv__(self, other): # other / self
    return other * self**-1
```

这一段是**"最小算子集"哲学的完美体现**。真正实现反向逻辑的只有 `__add__`、`__mul__`、`__pow__`、`relu` 四个。其余运算全是它们的组合：

- 减法 = 加法 + 取负（`-x = x * -1`）
- 除法 = 乘法 + 负幂（`x/y = x * y**-1`）
- `__radd__`/`__rmul__` 处理 `2 + x` 这种"左操作数不是 Value"的情况，转发给 `__add__`/`__mul__`

**程序员视角的启示**：定义好少数几个核心算子，其余通过组合实现。这是好的 API 设计——既减少代码、又减少 bug 面。PyTorch 内部也大量采用这种"复合算子"思路。

---

## 四、逐行精读 `nn.py`：怎么把引擎拼成神经网络

### 4.1 Module 基类：两个方法的契约

```python
class Module:

    def zero_grad(self):
        for p in self.parameters():
            p.grad = 0

    def parameters(self):
        return []
```

只有两个方法，且 `parameters()` 默认返回空列表。这是个**抽象基类的雏形**（没用 `abc`，靠约定）。

- `zero_grad`：训练循环开始前清零所有参数梯度。**必须做**，否则梯度会跨 batch 累加（因为 `_backward` 用的是 `+=`）。
- `parameters`：返回所有可训练参数。子类（Neuron/Layer/MLP）各自重写它，层层向上收集。

### 4.2 Neuron：一个神经元长什么样

```python
class Neuron(Module):

    def __init__(self, nin, nonlin=True):
        self.w = [Value(random.uniform(-1,1)) for _ in range(nin)]
        self.b = Value(0)
        self.nonlin = nonlin

    def __call__(self, x):
        act = sum((wi*xi for wi,xi in zip(self.w, x)), self.b)
        return act.relu() if self.nonlin else act

    def parameters(self):
        return self.w + [self.b]
```

**第 3 行**：每个权重 `w` 是一个独立的 `Value`，初值 `uniform(-1,1)`。`b` 偏置初始为 0。

**第 7-9 行是核心**：`act = sum((wi*xi for wi,xi in zip(self.w, x)), self.b)`。

这一行做了三件事，写法极简：
1. `zip(self.w, x)` 把每个权重和对应输入配对
2. `wi*xi` 是 Value 乘 Value，触发 `__mul__`，自动建图
3. `sum(..., self.b)` 的第二个参数是**初始值**——直接用 `self.b` 当起点，省掉单独 `+ self.b`

Python 的 `sum(iterable, start)` 用法在这里被玩出花：start 就是非线性激活前的偏置。**这是把"加权和 + 偏置"压缩成一行的技巧**。

第 9 行：根据 `nonlin` 决定要不要套 ReLU。最后一层通常不要激活（输出层是线性的）。

第 11-12 行：`parameters` 返回 `[w0, w1, ..., wn, b]`，供优化器使用。

### 4.3 Layer 和 MLP：组合的艺术

```python
class Layer(Module):

    def __init__(self, nin, nout, **kwargs):
        self.neurons = [Neuron(nin, **kwargs) for _ in range(nout)]

    def __call__(self, x):
        out = [n(x) for n in self.neurons]
        return out[0] if len(out) == 1 else out

    def parameters(self):
        return [p for n in self.neurons for p in n.parameters()]
```

Layer 就是 nout 个并排的 Neuron。前向时每个神经元吃同样的输入 x，各自产出。`**kwargs` 把 `nonlin` 等参数透传给 Neuron。

**第 8 行的小细节**：`return out[0] if len(out) == 1 else out`——如果只有一个输出，直接返回标量；否则返回列表。这让"最后一层只输出一个值"的用法更自然（不用每次 `out[0]`）。

**第 10 行**：双层列表推导 + 扁平化。`[p for n in neurons for p in n.parameters()]` 等价于"先遍历每个神经元，再遍历它的参数"，结果是一维列表。这是 Python 里展平嵌套列表的惯用法。

```python
class MLP(Module):

    def __init__(self, nin, nouts):
        sz = [nin] + nouts
        self.layers = [Layer(sz[i], sz[i+1], nonlin=i!=len(nouts)-1) for i in range(len(nouts))]

    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]
```

**第 4 行的技巧**：`sz = [nin] + nouts`，把输入维度拼到层大小列表前面。比如 `MLP(3, [4, 4, 1])`，`sz = [3, 4, 4, 1]`，相邻两两配对就是 `[3→4, 4→4, 4→1]`，正好是三层。这是**用列表索引表达层间连接**的简洁写法。

**第 5 行**：`nonlin=i!=len(nouts)-1`——除了最后一层，每层都用 ReLU。这个布尔表达式直接当参数传，Pythonic 到骨子里。

整个 MLP 60 行不到，但已经能跑一个标准的"输入层-隐藏层-输出层"全连接网络。配合 `engine.py` 的 autograd，训练循环只要：

```python
model = MLP(3, [4, 4, 1])
for step in range(100):
    # 前向
    ypred = [model(x) for x in xs]
    loss = sum((yout - ygt)**2 for ygt, yout in zip(ys, ypred))
    # 反向
    model.zero_grad()
    loss.backward()
    # 更新（朴素 SGD）
    for p in model.parameters():
        p.data -= 0.05 * p.grad
```

---

## 五、动手扩展：从读懂到会改

读完不能动手，等于没读懂。三个递进练习：

### 练习 1：加一个 `tanh` 激活函数

仿照 `relu`，在 Value 类加方法。提示：`tanh(x)` 的导数是 `1 - tanh(x)^2`，所以反向时用 `out.data`（前向算出的 tanh 值）即可：

```python
def tanh(self):
    import math
    t = math.tanh(self.data)
    out = Value(t, (self,), 'tanh')
    def _backward():
        self.grad += (1 - t**2) * out.grad
    out._backward = _backward
    return out
```

加完后，把 Neuron 的 `act.relu()` 换成 `act.tanh()`，跑一遍训练对比收敛。

### 练习 2：加一个 sigmoid

导数是 `σ(x)(1-σ(x))`，思路一样。注意 sigmoid 容易数值溢出，可以考虑用 `1/(1+exp(-x))` 的稳定实现。

### 练习 3：接一个真实分类任务

用 `nn.py` 的 MLP 跑 `sklearn.datasets.make_moons`（仓库里有 `demo.ipynb` 就是干这个的）。把训练 loss 画出来，调一下隐藏层大小和步长，感受超参对收敛的影响。

### 练习 4（进阶）：把标量引擎改成向量引擎

micrograd 是**标量**引擎（每个 Value 只存一个数），所以矩阵乘法要靠循环，极慢。试着把 `data` 改成 `numpy.ndarray`，反向时用矩阵运算。你会发现"向量化"是 autograd 性能跃迁的关键一步——而这就是 PyTorch tensor 的核心。

---

## 六、一句话总结

> **反向传播 = 每个算子定义局部导数（`_backward` 闭包）+ 拓扑排序决定调用顺序。**

micrograd 把这两件事用 94 行讲透。剩下的所有框架（PyTorch、JAX、TensorFlow）的 autograd，都只是在这个骨架上做了工程优化：标量换张量、Python 闭包换 C++ 算子、单机换分布式。**思想没变过。**

读懂 micrograd，你下次用 `loss.backward()` 时，脑子里会有一个清晰的画面：梯度如何沿着拓扑序逆流而上，最终汇聚到每一个参数的 `.grad` 里。
