#!/usr/bin/env python3
"""
tinytorch/nn.py — 神经网络层

参照：PyTorch torch.nn / micrograd nn.py
csdiy 对应：nanoGPT精读(各组件) + tinytransformer

模块清单：
  Module       — 基类（参数管理/零梯度/模式切换）
  Linear       — 全连接层
  Embedding    — 词嵌入
  LayerNorm    — 层归一化
  Dropout      — 随机失活
  ReLU/Tanh    — 激活函数
  Sequential   — 层堆叠
"""
import random, math
from .tensor import Value

class Module:
    """基类（参照 PyTorch nn.Module）"""
    def __init__(self):
        self.training = True
    def parameters(self):
        """返回所有可训练参数（递归子模块）"""
        params = []
        for attr in vars(self).values():
            if isinstance(attr, Value):
                params.append(attr)
            elif isinstance(attr, list):
                params.extend(v for v in attr if isinstance(v, Value))
            elif isinstance(attr, Module):
                params.extend(attr.parameters())
            elif isinstance(attr, list) and all(isinstance(m, Module) for m in attr):
                for m in attr:
                    params.extend(m.parameters())
        return params
    def zero_grad(self):
        for p in self.parameters():
            p.grad = 0.0
    def train(self): self.training = True
    def eval(self): self.training = False
    def __call__(self, *args):
        return self.forward(*args)

class Linear(Module):
    """全连接层 y = Wx + b（参照 nn.Linear）"""
    def __init__(self, fan_in, fan_out, bias=True):
        super().__init__()
        # Kaiming 初始化（参照 He 2015）
        std = math.sqrt(2.0 / fan_in)
        self.weight = [[Value(random.gauss(0, std)) for _ in range(fan_in)] for _ in range(fan_out)]
        self.bias = [Value(0.0) for _ in range(fan_out)] if bias else None
    def forward(self, x):
        """x: [Value] of size fan_in → [Value] of size fan_out"""
        out = []
        for j in range(len(self.weight)):
            neuron = sum((self.weight[j][i] * x[i] for i in range(len(x))), Value(0.0))
            if self.bias:
                neuron = neuron + self.bias[j]
            out.append(neuron)
        return out

class Embedding(Module):
    """词嵌入（参照 nn.Embedding / nanoGPT §7.1）"""
    def __init__(self, vocab_size, d_model):
        super().__init__()
        std = 0.02
        self.table = [[Value(random.gauss(0, std)) for _ in range(d_model)]
                      for _ in range(vocab_size)]
        self.d_model = d_model
    def forward(self, token_ids):
        """token_ids: [int] → [[Value]] embedding vectors"""
        return [list(self.table[tid]) for tid in token_ids]

class LayerNorm(Module):
    """层归一化（参照 Ba 2016 / nanoGPT §三）"""
    def __init__(self, dim, eps=1e-5):
        super().__init__()
        self.gamma = [Value(1.0) for _ in range(dim)]
        self.beta = [Value(0.0) for _ in range(dim)]
        self.eps = eps; self.dim = dim
    def forward(self, x):
        """x: [Value] → [Value] normalized"""
        n = len(x)
        mean = sum(v.data for v in x) / n
        var = sum((v.data - mean) ** 2 for v in x) / n
        std = math.sqrt(var + self.eps)
        return [(x[i] - Value(mean)) / Value(std) * self.gamma[i] + self.beta[i]
                for i in range(n)]

class Dropout(Module):
    """随机失活（参照 Srivastava 2014 / nn.Dropout）"""
    def __init__(self, p=0.1):
        super().__init__()
        self.p = p
    def forward(self, x):
        if not self.training or self.p == 0:
            return x
        scale = 1.0 / (1 - self.p)
        return [v * Value(0.0 if random.random() < self.p else scale) for v in x]

class ReLU(Module):
    def forward(self, x): return [v.relu() for v in x]

class Tanh(Module):
    def forward(self, x): return [v.tanh() for v in x]

class Sigmoid(Module):
    def forward(self, x): return [v.sigmoid() for v in x]

class Sequential(Module):
    """层堆叠（参照 nn.Sequential）"""
    def __init__(self, *layers):
        super().__init__()
        self.layers = list(layers)
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x
    def parameters(self):
        params = []
        for layer in self.layers:
            if isinstance(layer, Module):
                params.extend(layer.parameters())
        return params


def MLP(fan_in, dims):
    """便捷构造多层感知机（参照 micrograd MLP）"""
    layers = []
    prev = fan_in
    for d in dims[:-1]:
        layers.extend([Linear(prev, d), Tanh()])
        prev = d
    layers.append(Linear(prev, dims[-1]))
    return Sequential(*layers)
