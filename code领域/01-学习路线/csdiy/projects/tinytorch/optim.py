#!/usr/bin/env python3
"""
tinytorch/optim.py — 优化器

参照：PyTorch torch.optim / Kingma 2014 (Adam) / Loshchilov 2019 (AdamW)
csdiy 对应：nanoGPT精读(train.py optimizer) + AI核心

模块清单：
  SGD          — 随机梯度下降
  Momentum     — SGD + 动量（参照 Sutskever 2013）
  Adam         — 自适应矩估计（参照 Kingma 2014）
  AdamW        — 解耦权重衰减（参照 Loshchilov 2019）
  CosineScheduler — 余弦退火学习率（参照 nanoGPT train.py）
"""
import math

class Optimizer:
    """基类（参照 PyTorch optim.Optimizer）"""
    def __init__(self, params, lr):
        self.params = list(params)
        self.lr = lr
        self.t = 0  # 全局步数
    def zero_grad(self):
        for p in self.params:
            p.grad = 0.0
    def step(self):
        self.t += 1
        self._step()

class SGD(Optimizer):
    """SGD（参照 PyTorch optim.SGD）"""
    def _step(self):
        for p in self.params:
            p.data -= self.lr * p.grad

class Momentum(Optimizer):
    """SGD + Momentum（参照 PyTorch SGD with momentum=0.9）"""
    def __init__(self, params, lr=0.01, momentum=0.9):
        super().__init__(params, lr)
        self.momentum = momentum
        self.v = {id(p): 0.0 for p in self.params}
    def _step(self):
        for p in self.params:
            self.v[id(p)] = self.momentum * self.v[id(p)] - self.lr * p.grad
            p.data += self.v[id(p)]

class Adam(Optimizer):
    """Adam（参照 Kingma 2014 / PyTorch optim.Adam）
    自适应学习率：每个参数有独立的 m（一阶矩）和 v（二阶矩）"""
    def __init__(self, params, lr=0.001, betas=(0.9, 0.999), eps=1e-8):
        super().__init__(params, lr)
        self.b1, self.b2 = betas
        self.eps = eps
        self.m = {id(p): 0.0 for p in self.params}
        self.v = {id(p): 0.0 for p in self.params}
    def _step(self):
        for p in self.params:
            pid = id(p)
            self.m[pid] = self.b1 * self.m[pid] + (1 - self.b1) * p.grad
            self.v[pid] = self.b2 * self.v[pid] + (1 - self.b2) * p.grad ** 2
            m_hat = self.m[pid] / (1 - self.b1 ** self.t)
            v_hat = self.v[pid] / (1 - self.b2 ** self.t)
            p.data -= self.lr * m_hat / (math.sqrt(v_hat) + self.eps)

class AdamW(Adam):
    """AdamW（参照 Loshchilov 2019 / nanoGPT 默认优化器）
    和 Adam 的区别：权重衰减不经过 m（解耦）"""
    def __init__(self, params, lr=0.001, weight_decay=0.01, **kw):
        super().__init__(params, lr, **kw)
        self.wd = weight_decay
    def _step(self):
        for p in self.params:
            pid = id(p)
            p.data -= self.lr * self.wd * p.data  # 解耦衰减（先衰减再更新）
            self.m[pid] = self.b1 * self.m[pid] + (1 - self.b1) * p.grad
            self.v[pid] = self.b2 * self.v[pid] + (1 - self.b2) * p.grad ** 2
            m_hat = self.m[pid] / (1 - self.b1 ** self.t)
            v_hat = self.v[pid] / (1 - self.b2 ** self.t)
            p.data -= self.lr * m_hat / (math.sqrt(v_hat) + self.eps)

class CosineScheduler:
    """余弦退火 + Warmup（参照 nanoGPT train.py §8.3）"""
    def __init__(self, optimizer, warmup_steps=100, max_steps=1000, max_lr=0.01, min_lr=0.001):
        self.opt = optimizer
        self.warmup = warmup_steps; self.max_steps = max_steps
        self.max_lr = max_lr; self.min_lr = min_lr
    def step(self):
        t = self.opt.t
        if t < self.warmup:
            lr = self.max_lr * (t + 1) / self.warmup
        else:
            progress = (t - self.warmup) / (self.max_steps - self.warmup)
            lr = self.min_lr + (self.max_lr - self.min_lr) * 0.5 * (1 + math.cos(math.pi * progress))
        self.opt.lr = lr
        return lr
