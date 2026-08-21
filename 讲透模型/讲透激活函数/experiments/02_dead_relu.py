"""
实验 02 —— Dead ReLU (神经元死亡) 与 优化器惯性
对应文档: 02-为0与为1发生了什么.md
核心结论:
  1. Dead ReLU: 若某神经元输入恒 <= 0, 则其梯度恒为 0, 权重永不更新 -> 神经元"死亡"
  2. 但"梯度=0 不更新"有特例:
     - 带动量优化器(SGD+Momentum/Adam): 即使当前梯度为0, 历史动量仍会推动权重变化
     - 权重衰减(Weight Decay/L2): 即使梯度为0, 权重也会按比例衰减
跑法: python3 02_dead_relu.py
"""
import torch
import torch.nn as nn

torch.manual_seed(0)

# ---------------------------------------------------------------
# 第一部分: 复现 Dead ReLU
# 一个单神经元: x -> (Wx + b) -> ReLU -> ...
# 故意把偏置 b 设成很大负数, 使 Wx+b 恒 < 0, ReLU 输出恒为 0
# ---------------------------------------------------------------
print("=" * 64)
print("第一部分: 复现 Dead ReLU")
print("=" * 64)

W = torch.tensor([[1.0, 2.0]], requires_grad=True)
b = torch.tensor([-100.0], requires_grad=True)   # 巨大负偏置 -> 神经元恒死
inputs = torch.tensor([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]])
target = torch.tensor([1.0, 1.0, 1.0])

for step in range(3):
    pre = inputs @ W.t() + b          # 线性部分
    out = torch.relu(pre)             # ReLU
    loss = ((out.squeeze() - target) ** 2).mean()
    loss.backward()
    print(f"step {step}: 线性输出={pre.tolist()}  ReLU输出={out.tolist()}  "
          f"dW={W.grad.tolist()}  db={b.grad.tolist()}")
    # 用纯 SGD(无动量), lr 小, 观察 W/b 是否动
    with torch.no_grad():
        W -= 0.01 * W.grad
        b -= 0.01 * b.grad
    W.grad.zero_(); b.grad.zero_()

print("==> 线性输出恒为负 -> ReLU 恒为 0 -> 梯度恒为 0 -> W/b 完全不更新 (神经元死亡)!\n")

# ---------------------------------------------------------------
# 第二部分: 优化器惯性——即使梯度=0, 权重仍可能变化
# ---------------------------------------------------------------
print("=" * 64)
print("第二部分: 优化器惯性 (梯度=0 时权重仍变?)")
print("=" * 64)

# 构造一个梯度恰好为 0 的死神经元参数
def make_dead():
    p = torch.tensor([[5.0, 7.0]], requires_grad=True)
    return p

# (A) 纯 SGD, 无动量无衰减
pA = make_dead()
optA = torch.optim.SGD([pA], lr=0.1)
# 构造梯度=0: relu 负输入
def zero_grad_step(p, opt):
    pre = torch.relu(torch.tensor([-10.0]))   # 恒死
    loss = (pre * p).sum() * 0.0             # 强制 loss 与 p 无关梯度 -> grad=0
    opt.zero_grad()
    loss.backward()
    g = p.grad.clone() if p.grad is not None else None
    opt.step()
    return g

print(f"初始权重: {pA.tolist()}")
for i in range(3):
    g = zero_grad_step(pA, optA)
    print(f"[纯SGD]      step {i}: grad={g}  权重={pA.tolist()}")

# (B) SGD + Momentum
pB = make_dead()
optB = torch.optim.SGD([pB], lr=0.1, momentum=0.9, nesterov=False)
# 先制造一段非零梯度建立动量, 再让梯度变 0
x_dummy = torch.tensor([1.0, 1.0])
for i in range(5):
    loss = (pB * x_dummy).sum()  # 非零梯度
    optB.zero_grad(); loss.backward(); optB.step()
print(f"\n[SGD+Momentum] 建立动量后权重: {pB.tolist()}")
for i in range(3):
    g = zero_grad_step(pB, optB)  # 之后梯度全 0
    print(f"[SGD+Momentum] step {i}: grad={g.tolist()}  权重={pB.tolist()}")

# (C) Adam + Weight Decay
pC = make_dead()
optC = torch.optim.AdamW([pC], lr=0.1, weight_decay=0.1)
for i in range(3):
    g = zero_grad_step(pC, optC)
    print(f"[AdamW+WD]    step {i}: grad={g.tolist()}  权重={pC.tolist()}")

print()
print("结论:")
print("  - 纯 SGD: 梯度=0 -> 权重纹丝不动")
print("  - Momentum: 即使梯度=0, 历史动量仍推动权重变化 (优化器惯性)")
print("  - Weight Decay: 梯度=0 时权重仍按比例衰减 -> 权重也在变")
print("  ==> 严格说'梯度为0则权重不更新'只在纯SGD无衰减时成立!")
