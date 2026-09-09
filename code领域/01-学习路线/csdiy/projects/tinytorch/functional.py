#!/usr/bin/env python3
"""
tinytorch/functional.py — 函数式 API（参照 torch.nn.functional）

常用函数：
  softmax / log_softmax / sigmoid / relu / tanh / gelu
  matmul / linear / embedding
  cross_entropy / mse_loss
"""
import math
from .tensor import Value

def softmax(logits: list[Value]) -> list[Value]:
    """Softmax（参照 torch.nn.functional.softmax）"""
    max_val = max(l.data for l in logits)
    exps = [math.exp(l.data - max_val) for l in logits]
    s = sum(exps)
    probs = [e / s for e in exps]
    # 用 Value 包装（保持计算图）
    result = []
    for i, p in enumerate(probs):
        v = Value(p, (logits[i],), 'softmax')
        def make_backward(idx):
            def _backward():
                grad = probs[idx]
                for j in range(len(probs)):
                    logits[j].grad += grad * ((1.0 if j == idx else 0.0) - probs[j]) * v.grad
            return _backward
        v._backward = make_backward(i)
        result.append(v)
    return result

def sigmoid(x: Value) -> Value:
    """Sigmoid（参照 torch.sigmoid）"""
    return x.sigmoid()

def relu(x: Value) -> Value:
    """ReLU"""
    return x.relu()

def gelu(x: Value) -> Value:
    """GELU 激活函数（参照 torch.nn.functional.gelu）
    GELU(x) = 0.5x(1 + tanh(√(2/π)(x + 0.044715x³)))"""
    # 近似实现
    inner = x.data + 0.044715 * x.data ** 3
    tanh_val = math.tanh(math.sqrt(2 / math.pi) * inner)
    result = 0.5 * x.data * (1 + tanh_val)
    out = Value(result, (x,), 'gelu')
    def _backward():
        # GELU 导数（近似）
        x_val = x.data
        inner = x_val + 0.044715 * x_val ** 3
        tanh_val = math.tanh(math.sqrt(2 / math.pi) * inner)
        sech2 = 1 - tanh_val ** 2
        deriv = 0.5 * (1 + tanh_val) + 0.5 * x_val * sech2 * math.sqrt(2 / math.pi) * (1 + 3 * 0.044715 * x_val ** 2)
        x.grad += deriv * out.grad
    out._backward = _backward
    return out

def linear(x: list[Value], weight: list[list[Value]], bias: list[Value] = None) -> list[Value]:
    """线性变换 y = xW^T + b（参照 torch.nn.functional.linear）"""
    out_dim = len(weight)
    in_dim = len(weight[0])
    result = []
    for j in range(out_dim):
        neuron = sum(weight[j][i] * x[i] for i in range(min(in_dim, len(x))))
        if bias:
            neuron = neuron + bias[j]
        result.append(neuron)
    return result

def embedding(indices: list[int], table: list[list[Value]]) -> list[list[Value]]:
    """嵌入查找（参照 torch.nn.functional.embedding）"""
    return [list(table[idx]) for idx in indices]

def dropout(x: list[Value], p: float = 0.1, training: bool = True) -> list[Value]:
    """Dropout（参照 torch.nn.functional.dropout）"""
    import random
    if not training or p == 0:
        return x
    scale = 1.0 / (1 - p)
    return [v * Value(0.0 if random.random() < p else scale) for v in x]

def layer_norm(x: list[Value], gamma: list[Value] = None, beta: list[Value] = None, eps: float = 1e-5) -> list[Value]:
    """Layer Normalization（参照 torch.nn.functional.layer_norm）"""
    n = len(x)
    mean = sum(v.data for v in x) / n
    var = sum((v.data - mean) ** 2 for v in x) / n
    std = math.sqrt(var + eps)
    normed = [(x[i] - Value(mean)) / Value(std) for i in range(n)]
    if gamma:
        normed = [normed[i] * gamma[i] for i in range(n)]
    if beta:
        normed = [normed[i] + beta[i] for i in range(n)]
    return normed
