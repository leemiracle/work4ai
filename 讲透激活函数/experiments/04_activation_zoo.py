"""
实验 04 —— 激活函数全家桶: 函数曲线 + 导数曲线
对应文档: 03-激活函数家族综述.md
产出: activation_functions.png, activation_derivatives.png
覆盖: Sigmoid, Tanh, ReLU, LeakyReLU, ReLU6, GELU, SiLU(Swish), Mish
跑法: python3 04_activation_zoo.py
"""
import torch
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

x = torch.linspace(-6, 6, 1000)

# 名字 -> (值, 导数, 显示名, 颜色)
acts = [
    ("sigmoid", lambda v: torch.sigmoid(v),
     lambda v: torch.sigmoid(v) * (1 - torch.sigmoid(v)), r"Sigmoid $\frac{1}{1+e^{-x}}$", "C0"),
    ("tanh", lambda v: torch.tanh(v),
     lambda v: 1 - torch.tanh(v) ** 2, r"Tanh $\frac{e^x-e^{-x}}{e^x+e^{-x}}$", "C1"),
    ("relu", lambda v: F.relu(v),
     lambda v: (v > 0).float(), r"ReLU $\max(0,x)$", "C2"),
    ("leaky", lambda v: F.leaky_relu(v, 0.1),
     lambda v: torch.where(v > 0, torch.ones_like(v), 0.1 * torch.ones_like(v)),
     r"LeakyReLU $\max(0.1x,x)$", "C3"),
    ("relu6", lambda v: F.relu6(v),
     lambda v: torch.where((v > 0) & (v < 6), torch.ones_like(v), torch.zeros_like(v)),
     r"ReLU6 $\min(\max(0,x),6)$", "C4"),
    ("gelu", lambda v: F.gelu(v),
     None, r"GELU $x\Phi(x)$", "C5"),
    ("silu", lambda v: F.silu(v),
     lambda v: torch.sigmoid(v) + v * torch.sigmoid(v) * (1 - torch.sigmoid(v)),
     r"SiLU/Swish $x\sigma(x)$", "C6"),
    ("mish", lambda v: F.mish(v),
     None, r"Mish $x\tanh(\text{softplus}(x))$", "C7"),
]

# 用 autograd 求统一导数 (含 GELU/Mish 这种难解析的)
def grad_by_autograd(fn, x):
    xv = x.clone().requires_grad_(True)
    yv = fn(xv)
    g = torch.autograd.grad(yv.sum(), xv)[0]
    return g.detach()

# ---- 图1: 函数曲线 ----
fig, ax = plt.subplots(figsize=(10, 6))
for key, fn, dfn, label, c in acts:
    ax.plot(x.numpy(), fn(x).numpy(), label=label, color=c, linewidth=2)
ax.axhline(0, color="gray", linewidth=0.5); ax.axvline(0, color="gray", linewidth=0.5)
ax.set_title("Activation Functions", fontsize=14)
ax.set_xlabel("x"); ax.set_ylabel("f(x)")
ax.set_ylim(-1.5, 6); ax.grid(alpha=0.3); ax.legend(fontsize=9, loc="upper left")
plt.tight_layout(); plt.savefig("activation_functions.png", dpi=110); plt.close()
print("saved: activation_functions.png")

# ---- 图2: 导数曲线 ----
fig, ax = plt.subplots(figsize=(10, 6))
for key, fn, dfn, label, c in acts:
    g = dfn(x) if dfn is not None else grad_by_autograd(fn, x)
    ax.plot(x.numpy(), g.numpy(), label=label, color=c, linewidth=2)
ax.axhline(0, color="gray", linewidth=0.5); ax.axvline(0, color="gray", linewidth=0.5)
ax.set_title("Derivatives of Activation Functions", fontsize=14)
ax.set_xlabel("x"); ax.set_ylabel("f'(x)")
ax.set_ylim(-0.2, 1.5); ax.grid(alpha=0.3); ax.legend(fontsize=9, loc="upper left")
plt.tight_layout(); plt.savefig("activation_derivatives.png", dpi=110); plt.close()
print("saved: activation_derivatives.png")

# ---- 关键洞察打印 ----
print("\n关键洞察:")
print(f"  Sigmoid 导数最大值 (x=0): {(torch.sigmoid(torch.tensor(0.0))*(1-torch.sigmoid(torch.tensor(0.0)))).item():.3f}  <-- 仅0.25, 连乘必消失")
print(f"  Tanh    导数最大值 (x=0): {(1-torch.tanh(torch.tensor(0.0))**2).item():.3f}  <-- 比 sigmoid 好(=1), 但|x|稍大即骤降, 深层仍消失")
print(f"  ReLU    正轴导数:        1.000  <-- 恒=1, 连乘不消失 (本系列革命性所在)")
print(f"  GELU    正轴远端导数:    ~1.000  <-- 平滑过渡, 优化地貌更平滑")
print(f"  Mish    负轴有微小正隆起:        <-- 非单调, 保留少量负信息流")
