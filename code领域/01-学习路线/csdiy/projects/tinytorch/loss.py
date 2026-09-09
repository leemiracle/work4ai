#!/usr/bin/env python3
"""
tinytorch/loss.py — 损失函数

参照：PyTorch nn.functional / Focal Loss (Lin 2017)
csdiy 对应：AI核心 + tinytorch

模块清单：
  mse_loss        — 均方误差（回归）
  cross_entropy   — 交叉熵（分类）
  binary_ce       — 二元交叉熵
  focal_loss      — Focal Loss（解决类别不平衡）
"""
import math
from .tensor import Value

def mse_loss(pred, target):
    """均方误差（参照 nn.MSELoss）
    pred: [Value], target: [float] → Value (loss)"""
    n = len(pred)
    diffs = [(pred[i] - target[i]) ** 2 for i in range(n)]
    return sum(diffs, Value(0.0)) * (1.0 / n)

def cross_entropy(logits, target_idx):
    """交叉熵（参照 nn.CrossEntropyLoss）
    logits: [Value] (未归一化), target_idx: int → Value (loss)

    内部做了 softmax + NLL，梯度计算合并"""
    n = len(logits)
    # softmax with numerical stability
    max_val = max(l.data for l in logits)
    exps = [math.exp(l.data - max_val) for l in logits]
    s = sum(exps)
    probs = [e / s for e in exps]

    # loss = -log(prob[target])
    loss_val = -math.log(probs[target_idx] + 1e-8)
    loss = Value(loss_val, tuple(logits), 'CE')

    # 自定义 backward（softmax + CE 合并梯度 = probs - one_hot）
    def _backward():
        for i in range(n):
            grad = probs[i] - (1.0 if i == target_idx else 0.0)
            logits[i].grad += grad * loss.grad
    loss._backward = _backward

    # 保持计算图连通（让 backward 拓扑排序能到达 logits）
    for l in logits:
        loss._prev.add(l)
    return loss

def binary_ce(pred_prob, target):
    """二元交叉熵（参照 nn.BCELoss）
    pred_prob: Value (sigmoid 后的概率), target: float (0 or 1)"""
    p = pred_prob.data
    eps = 1e-8
    p = min(max(p, eps), 1 - eps)
    loss_val = -(target * math.log(p) + (1 - target) * math.log(1 - p))
    loss = Value(loss_val, (pred_prob,), 'BCE')

    def _backward():
        pred_prob.grad += (p - target) / (p * (1 - p) + eps) * loss.grad
    loss._backward = _backward
    return loss

def focal_loss(logits, target_idx, gamma=2.0):
    """Focal Loss（参照 Lin 2017 / RetinaNet）
    降低易分样本权重，聚焦难分样本"""
    n = len(logits)
    max_val = max(l.data for l in logits)
    exps = [math.exp(l.data - max_val) for l in logits]
    s = sum(exps)
    probs = [e / s for e in exps]
    pt = probs[target_idx]

    loss_val = -((1 - pt) ** gamma) * math.log(pt + 1e-8)
    loss = Value(loss_val, tuple(logits), f'Focal(γ={gamma})')

    def _backward():
        for i in range(n):
            mod = ((1 - pt) ** gamma) if i == target_idx else 1.0
            grad = mod * (probs[i] - (1.0 if i == target_idx else 0.0))
            logits[i].grad += grad * loss.grad
    loss._backward = _backward
    for l in logits:
        loss._prev.add(l)
    return loss
