#!/usr/bin/env python3
"""
tinytorch/tensor.py — 自动微分引擎

参照：micrograd (Karpathy) + PyTorch autograd
csdiy 对应：source-reading/micrograd-100行吃透自动微分.md

核心：Value 类 = 数据 + 梯度 + 反向传播函数 + 计算图
- 前向传播：运算时自动构建计算图（DAG）
- 反向传播：拓扑排序 + 链式法则逐节点求导
"""
import math

class Value:
    """自动微分节点（参照 micrograd engine.py + PyTorch Tensor）"""

    def __init__(self, data, _children=(), _op='', label=''):
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op
        self.label = label

    # ─── 加法 ───
    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), '+')

        def _backward():
            self.grad += out.grad
            other.grad += out.grad
        out._backward = _backward
        return out

    def __radd__(self, other): return self + other

    # ─── 乘法 ───
    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), '*')

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def __rmul__(self, other): return self * other

    # ─── 减法 ───
    def __neg__(self): return self * -1
    def __sub__(self, other): return self + (-other if isinstance(other, Value) else -other)
    def __rsub__(self, other): return Value(other) + (-self)

    # ─── 除法 ───
    def __truediv__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        return self * other**(-1)

    # ─── 幂运算 ───
    def __pow__(self, p):
        assert isinstance(p, (int, float)), "Only constant powers"
        out = Value(self.data ** p, (self,), f'**{p}')

        def _backward():
            self.grad += (p * self.data ** (p - 1)) * out.grad
        out._backward = _backward
        return out

    # ─── 激活函数 ───
    def relu(self):
        out = Value(max(0, self.data), (self,), 'relu')

        def _backward():
            self.grad += (1.0 if out.data > 0 else 0.0) * out.grad
        out._backward = _backward
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), 'tanh')

        def _backward():
            self.grad += (1 - t ** 2) * out.grad
        out._backward = _backward
        return out

    def sigmoid(self):
        s = 1 / (1 + math.exp(-self.data)) if self.data > -700 else 0.0
        out = Value(s, (self,), 'sigmoid')

        def _backward():
            self.grad += s * (1 - s) * out.grad
        out._backward = _backward
        return out

    def exp(self):
        e = math.exp(self.data)
        out = Value(e, (self,), 'exp')

        def _backward():
            self.grad += e * out.grad
        out._backward = _backward
        return out

    def log(self):
        out = Value(math.log(self.data + 1e-8), (self,), 'log')

        def _backward():
            self.grad += (1 / (self.data + 1e-8)) * out.grad
        out._backward = _backward
        return out

    # ─── 反向传播（拓扑排序核心 15 行）───
    def backward(self):
        """自动微分入口：拓扑排序 + 逆序传播"""
        topo = []
        visited = set()

        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)
        build_topo(self)

        self.grad = 1.0  # 种子梯度
        for node in reversed(topo):
            node._backward()

    def __repr__(self):
        return f"Value({self.data:.4f}, grad={self.grad:.4f})"


def tensor(data):
    """便捷构造函数"""
    if isinstance(data, (list, tuple)):
        return [tensor(d) for d in data]
    return Value(data)


def zero_grad(values):
    """清零梯度"""
    for v in values:
        v.grad = 0.0
