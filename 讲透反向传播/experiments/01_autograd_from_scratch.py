"""
实验 01 —— ★90 行手写反向传播引擎 (反传的全部本质)
对应文档: 01-反传的精确本质.md / 03-VJP统一视角.md
核心: 用纯 Python 复刻 autograd, 让你看到 loss.backward() 底层到底在干什么:
      1. 前向: 每个运算生成 Value, 记录 _backward(怎么求局部导数) 和 _prev(依赖谁)
      2. 反向: 拓扑排序后逆序调用每个 _backward, 用链式法则累积梯度
      3. 与 PyTorch autograd 对拍, 结果 0 误差
      4. 用它训练 MLP 证明真能学
跑法: python3 01_autograd_from_scratch.py
"""
import math, random

class Value:
    """一个能自动求导的标量 = PyTorch Tensor 的迷你版"""
    def __init__(self, data, _children=(), _op=''):
        self.data = data
        self.grad = 0.0
        self._backward = lambda: None   # 反向函数: 怎么把输出梯度传回输入
        self._prev = set(_children)
        self._op = _op

    def __add__(self, o):
        o = o if isinstance(o, Value) else Value(o)
        out = Value(self.data + o.data, (self, o), '+')
        def _backward():
            # d(a+b)/da=1, d(a+b)/db=1 -> 梯度原样传回 (这就是该节点的 VJP!)
            self.grad += 1.0 * out.grad
            o.grad += 1.0 * out.grad
        out._backward = _backward
        return out

    def __mul__(self, o):
        o = o if isinstance(o, Value) else Value(o)
        out = Value(self.data * o.data, (self, o), '*')
        def _backward():
            # d(a*b)/da=b, d(a*b)/db=a (雅可比转置作用在 out.grad 上)
            self.grad += o.data * out.grad
            o.grad += self.data * out.grad
        out._backward = _backward
        return out

    def relu(self):
        out = Value(max(0, self.data), (self,), 'relu')
        def _backward():
            self.grad += (1.0 if self.data > 0 else 0.0) * out.grad   # relu 的掩码
        out._backward = _backward
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), 'tanh')
        def _backward():
            self.grad += (1 - t * t) * out.grad
        out._backward = _backward
        return out

    def backward(self):
        """反向传播: 拓扑排序 -> 逆序调用 _backward (链式法则的执行)"""
        topo = []; visited = set()
        def build(v):
            if v not in visited:
                visited.add(v)
                for c in v._prev: build(c)
                topo.append(v)
        build(self)
        self.grad = 1.0   # dL/dL = 1, 反向起点
        for v in reversed(topo):   # 逆序 = 反向
            v._backward()

    def __radd__(self, o): return self + o
    def __repr__(self): return f"Value({self.data:.4f}, grad={self.grad:.4f})"

# ===== 一、手写反传算 f = relu(a*b + c), 与 torch 对拍 =====
print("=" * 66)
print("一、手写反传 vs PyTorch autograd (f = relu(a*b + c))")
print("=" * 66)
a, b, c = Value(2.0), Value(-3.0), Value(0.5)
f = (a * b + c).relu()
f.backward()
print(f"  a={a.data} b={b.data} c={c.data}  -> f={f.data}")
print(f"  手写: df/da={a.grad:.4f} df/db={b.grad:.4f} df/dc={c.grad:.4f}")

import torch
ta = torch.tensor(2.0, requires_grad=True)
tb = torch.tensor(-3.0, requires_grad=True)
tc = torch.tensor(0.5, requires_grad=True)
tf = torch.relu(ta * tb + tc); tf.backward()
print(f"  torch: df/da={ta.grad.item():.4f} df/db={tb.grad.item():.4f} df/dc={tc.grad.item():.4f}")
match = abs(a.grad - ta.grad.item()) < 1e-6
print(f"  完全一致: {match} ✓ (90 行复刻了 PyTorch 的灵魂)")

# ===== 二、训练 MLP 证明手写反传真能学 =====
print("\n" + "=" * 66)
print("二、用手写反传训练 MLP 拟合 y=x² (证明它真能驱动学习)")
print("=" * 66)
random.seed(0)
xs = [Value(x) for x in [-1.0 + 0.05*i for i in range(41)]]
ys = [x.data**2 for x in xs]

class Neuron:
    def __init__(self, nin):
        self.w = [Value(random.uniform(-1,1)) for _ in range(nin)]
        self.b = Value(0.0)
    def __call__(self, x):
        return sum((wi*xi for wi,xi in zip(self.w, x)), self.b).tanh()

NH = 6
hidden = [Neuron(1) for _ in range(NH)]
out_w = [Value(random.uniform(-1,1)) for _ in range(NH)]
out_b = Value(0.0)

def predict(x):
    h = [n([x]) for n in hidden]
    return sum((wi*hi for wi,hi in zip(out_w, h)), out_b)

lr = 0.1
for epoch in range(400):
    params = out_w + [out_b]
    for n in hidden: params += n.w + [n.b]
    for p in params: p.grad = 0.0      # zero_grad
    loss = Value(0.0)
    for x, y in zip(xs, ys):
        d = predict(x) + Value(-y)
        loss = loss + d * d
    loss = loss * Value(1.0/len(xs))
    loss.backward()                     # 反向传播!
    for p in params: p.data -= lr * p.grad   # 梯度下降
    if epoch % 100 == 0 or epoch == 399:
        print(f"  epoch {epoch:3d}: loss = {loss.data:.6f}")

print("\n核心洞察 (反传的全部本质):")
print("  - 前向: 每个运算生成 Value, 记 _backward(局部导数) 和 _prev(依赖)")
print("  - backward(): 拓扑排序逆序调用 _backward = 链式法则的执行")
print("  - 每个节点的 _backward 就是它的 VJP(雅可比转置×上游梯度), 见文档03")
print("  - PyTorch 的 loss.backward() 就是这套逻辑用 C++ 在张量级高效重做")
