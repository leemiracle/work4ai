"""
实验 03 —— 梯度消失: 为什么 ReLU 的导数=1 是革命性的
对应文档: 02-为0与为1发生了什么.md
核心结论:
  1. 反向传播是局部导数的连乘: 串联 L 层, 梯度被乘以 f'(x)^L
  2. Sigmoid 局部导数最大才 0.25, 连乘 20 层 -> 梯度衰减到 ~1e-12 (消失)
  3. ReLU 正半轴局部导数恒为 1, 连乘 20 层仍是 1 -> 深层网络可训练
跑法: python3 03_gradient_vanishing.py
"""
import torch
import torch.nn as nn

torch.manual_seed(0)

# ---------------------------------------------------------------
# 构造 20 层全连接网络, 分别用 Sigmoid / ReLU
# 测量反向传播后"每一层权重的梯度范数", 看是否随深度衰减
# ---------------------------------------------------------------
def build(depth, act):
    layers = []
    layers.append(nn.Linear(64, 64))
    for _ in range(depth - 1):
        layers.append(act)
        layers.append(nn.Linear(64, 64))
    return nn.Sequential(*layers)

def grad_norm_profile(model, depth):
    # model 里 Linear 在偶数下标 (0,2,4,...)
    x = torch.randn(8, 64)
    y = model(x)
    loss = y.pow(2).sum()
    loss.backward()
    norms = []
    for m in model:
        if isinstance(m, nn.Linear) and m.weight.grad is not None:
            norms.append(m.weight.grad.norm().item())
    return norms

depth = 20
print("=" * 64)
print(f"梯度消失对比: {depth} 层全连接网络")
print("=" * 64)

for name, act in [("Sigmoid", nn.Sigmoid()), ("ReLU", nn.ReLU())]:
    model = build(depth, act)
    norms = grad_norm_profile(model, depth)
    print(f"\n[{name}] 每层权重梯度范数 (从浅到深, 共 {len(norms)} 个 Linear 层):")
    for i, n in enumerate(norms):
        bar = "#" * int(min(40, n * 4))
        print(f"  Linear {i:2d}: {n:10.4e}  {bar}")
    if norms:
        ratio = norms[0] / max(norms[-1], 1e-30)
        print(f"  浅层/深层 梯度比 = {ratio:.2e}")

print("\n关键数字背后的数学:")
print("  Sigmoid 最大导数 f'(0) = 0.25 -> 0.25^20 ≈", f"{0.25**20:.2e}", "(梯度消失)")
print("  ReLU    正轴导数 f'(x) = 1.00 -> 1.00^20 = ", f"{1.0**20:.2e}", "(梯度不消失)")
print("==> 这就是 1·1·1···1=1 让极深网络变得可训练的根本原因!")
