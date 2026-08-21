"""
实验 01 —— ★手写 autograd 引擎 (理解计算图本质)
对应文档: 01-Autograd与计算图.md
核心目标: 用 ~90 行纯 Python 实现一个迷你 autograd (受 Karpathy micrograd 启发),
          让你亲眼看清 PyTorch 的 loss.backward() 到底在做什么:
          1. 前向传播时, 每个运算悄悄记录"怎么算的"(_backward) 和"依赖谁"(_prev)
          2. 反向传播时, 拓扑排序后逆序调用每个节点的 _backward, 用链式法则累积梯度
          3. 最后和 torch.autograd 对拍, 结果完全一致
跑法: python3 01_autograd_from_scratch.py
"""
import math

class Value:
    """一个能自动求导的标量 (PyTorch Tensor 的迷你版)"""
    def __init__(self, data, _children=(), _op=''):
        self.data = data
        self.grad = 0.0                 # 梯度, 初始为 0
        self._backward = lambda: None   # 反向函数: 怎么把输出梯度传回输入
        self._prev = set(_children)     # 这个运算依赖哪些输入节点
        self._op = _op                  # 运算类型 (调试用)

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), '+')
        def _backward():
            # d(a+b)/da = 1, d(a+b)/db = 1 -> 梯度原样传回
            self.grad += 1.0 * out.grad
            other.grad += 1.0 * out.grad
        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), '*')
        def _backward():
            # d(a*b)/da = b, d(a*b)/db = a
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def relu(self):
        out = Value(max(0, self.data), (self,), 'relu')
        def _backward():
            # relu'(x) = 1 if x>0 else 0  (这就是"讲透激活函数"里的掩码!)
            self.grad += (1.0 if self.data > 0 else 0.0) * out.grad
        out._backward = _backward
        return out

    def sigmoid(self):
        s = 1 / (1 + math.exp(-self.data))
        out = Value(s, (self,), 'sigmoid')
        def _backward():
            # sigmoid'(x) = s(1-s)
            self.grad += s * (1 - s) * out.grad
        out._backward = _backward
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), 'tanh')
        def _backward():
            # tanh'(x) = 1 - tanh(x)^2
            self.grad += (1 - t * t) * out.grad
        out._backward = _backward
        return out

    def backward(self):
        """反向传播: 拓扑排序 -> 逆序调用 _backward"""
        topo = []
        visited = set()
        def build(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build(child)
                topo.append(v)
        build(self)
        # 自己的梯度 = 1 (dL/dL = 1)
        self.grad = 1.0
        # 逆序反向 (从输出往输入传)
        for v in reversed(topo):
            v._backward()

    def __repr__(self):
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f})"

# ============================================================
# 第一部分: 用手写 autograd 算一个表达式 f = relu(a*b + c) 的梯度
# ============================================================
print("=" * 64)
print("第一部分: 手写 autograd 算 f = relu(a*b + c)")
print("=" * 64)
a, b, c = Value(2.0), Value(-3.0), Value(0.5)
d = a * b            # a*b
e = d + c            # a*b + c
f = e.relu()         # relu(a*b + c)
print(f"  a={a.data}, b={b.data}, c={c.data}")
print(f"  前向: a*b={d.data}, +c={e.data}, relu={f.data}")

f.backward()         # 触发反向传播
print(f"  反向梯度: df/da={a.grad:.4f}, df/db={b.grad:.4f}, df/dc={c.grad:.4f}")

# ============================================================
# 第二部分: 和 torch.autograd 对拍, 验证正确性
# ============================================================
print("\n" + "=" * 64)
print("第二部分: 与 PyTorch autograd 对拍验证")
print("=" * 64)
import torch
ta = torch.tensor(2.0, requires_grad=True)
tb = torch.tensor(-3.0, requires_grad=True)
tc = torch.tensor(0.5, requires_grad=True)
tf = torch.relu(ta * tb + tc)
tf.backward()
print(f"  PyTorch: df/da={ta.grad.item():.4f}, df/db={tb.grad.item():.4f}, df/dc={tc.grad.item():.4f}")
print(f"  手写:    df/da={a.grad:.4f}, df/db={b.grad:.4f}, df/dc={c.grad:.4f}")
match = abs(a.grad - ta.grad.item()) < 1e-6 and abs(b.grad - tb.grad.item()) < 1e-6
print(f"  完全一致: {match} ✓")

# ============================================================
# 第三部分: 用手写 autograd 训练一个小 MLP (证明它真能学)
# ============================================================
print("\n" + "=" * 64)
print("第三部分: 用手写 autograd 训练 MLP 拟合 sin(x)")
print("=" * 64)
import random
random.seed(0)

# 数据
xs = [Value(x) for x in [-1.0 + 0.05*i for i in range(41)]]   # x ∈ [-1, 1]
ys = [x.data ** 2 for x in xs]                                  # 目标 y = x^2 (抛物线, 易学)

# 一个 1-4-1 的 MLP (手写). 隐藏层用 tanh (避免 Dead ReLU, 见"讲透激活函数02章")
NH = 4
class Neuron:
    def __init__(self, nin):
        self.w = [Value(random.uniform(-1,1)) for _ in range(nin)]
        self.b = Value(0.0)
    def __call__(self, x):
        act = sum((wi*xi for wi,xi in zip(self.w, x)), self.b)
        return act.tanh()
class Layer:
    def __init__(self, nin, nout):
        self.neurons = [Neuron(nin) for _ in range(nout)]
    def __call__(self, x):
        return [n(x) for n in self.neurons]

mlp_w = [Value(random.uniform(-1,1)) for _ in range(NH)]   # 输出层权重
mlp_b = Value(0.0)
hidden = Layer(1, NH)

def predict(x):
    h = hidden([x])                # NH 个隐藏神经元
    out = sum((wi*hi for wi,hi in zip(mlp_w, h)), mlp_b)
    return out

lr = 0.1
for epoch in range(400):
    # 收集所有参数
    params = mlp_w + [mlp_b]
    for n in hidden.neurons:
        params += n.w + [n.b]
    # 清零梯度 (对应 optimizer.zero_grad!)
    for p in params: p.grad = 0.0
    # 前向 + loss
    loss = Value(0.0)
    for x, y in zip(xs, ys):
        pred = predict(x)
        diff = pred + Value(-y)     # pred - y
        loss = loss + diff * diff   # 累加 (pred-y)^2
    loss = loss * Value(1.0/len(xs))
    # 反向
    loss.backward()
    # 梯度下降 (对应 optimizer.step!)
    for p in params:
        p.data -= lr * p.grad
    if epoch % 100 == 0 or epoch == 399:
        print(f"  epoch {epoch:3d}: loss = {loss.data:.6f}")

print("\n核心洞察:")
print("  - 前向: 每个运算(+,*,relu)都生成一个 Value, 记住'_backward'和'_prev'")
print("  - backward(): 拓扑排序后逆序调用 _backward, 链式法则自动累积梯度")
print("  - 这就是 PyTorch loss.backward() 的本质, 只不过 PyTorch 用 C++ 在张量级做")
print("  - 训练三件套清晰可见: zero_grad(清零) -> backward(求梯度) -> step(更新)")
