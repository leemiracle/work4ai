"""
实验 06 —— 优化器对梯度的加工: 反传的原始梯度如何变成更新量
对应文档: 07-各种梯度的全景.md
核心: 反传算出的"原始梯度 g"通常不直接用于更新, 而是经优化器加工:
  - SGD+Momentum: 对 g 做指数移动平均(平滑)
  - Adam: 一阶矩(动量) + 二阶矩(自适应学习率) + 偏差校正
本实验透视: 同一个原始梯度, 经不同优化器加工后, 实际更新量天差地别.
跑法: python3 06_optimizer_gradients.py
"""
import torch
import numpy as np

print("=" * 66)
print("一、同一个原始梯度, 不同优化器加工成不同的'实际更新'")
print("=" * 66)
# 模拟: 连续 10 步, 原始梯度 g 在两个方向上交替(模拟振荡)
# 方向0 恒为 +1, 方向1 在 +1/-1 间振荡
torch.manual_seed(0)
grads = [(torch.tensor([1.0, 1.0])), (torch.tensor([1.0, -1.0]))] * 5   # 10 步
print(f"  原始梯度序列(方向0恒+1, 方向1振荡): 第0步={grads[0].tolist()}, 第1步={grads[1].tolist()} ...")

# 用 PyTorch 优化器看实际参数变化(等价于看'加工后的梯度')
def simulate(opt_factory, name):
    torch.manual_seed(0)
    p = torch.zeros(2)
    opt = opt_factory([p])
    traj = [p.clone().tolist()]
    for g in grads:
        opt.zero_grad()
        p.grad = g.clone()
        opt.step()
        traj.append(p.clone().tolist())
    return traj

traj_sgd = simulate(lambda ps: torch.optim.SGD(ps, lr=0.1), "SGD")
traj_mom = simulate(lambda ps: torch.optim.SGD(ps, lr=0.1, momentum=0.9), "Momentum")
traj_adam = simulate(lambda ps: torch.optim.Adam(ps, lr=0.1), "Adam")

print(f"\n  10步后参数位置 (起点 [0,0]):")
print(f"    纯SGD:     {traj_sgd[-1]}  (方向0缓慢前进, 方向1振荡不前)")
print(f"    Momentum:  {traj_mom[-1]}  (方向0加速冲, 方向1振荡被平滑抵消!)")
print(f"    Adam:      {traj_adam[-1]}  (方向0自适应, 方向1因方差大被抑制)")
print("  => Momentum 平滑了振荡方向; Adam 给稳定方向更大步长、给振荡方向更小步长")

print("\n" + "=" * 66)
print("二、透视 Momentum: 原始梯度 vs 动量(平滑后的梯度)")
print("=" * 66)
# 手动实现 momentum 看它如何加工梯度
beta = 0.9
v = np.zeros(2)   # 动量(梯度的指数移动平均)
print(f"  {'步':>3} {'原始梯度':>16} {'动量v(平滑后)':>18} {'实际更新方向':>16}")
for step, g in enumerate(grads):
    v = beta * v + (1 - beta) * np.array(g.tolist())   # 动量更新
    print(f"  {step:>3} {str(g.tolist()):>16} {str(v.round(3).tolist()):>18} {str((0.1*v).round(3).tolist()):>16}")
print("  => 动量 v 是原始梯度的平滑版; 振荡方向(+1/-1)的 v 趋近0, 稳定方向(+1)的 v 趋近1")
print("     Momentum 更新用的不是当前 g, 而是累积的 v -> 抑制振荡、加速稳定方向")

print("\n" + "=" * 66)
print("三、透视 Adam: m(一阶矩) + v(二阶矩) -> 自适应每参数学习率")
print("=" * 66)
m = np.zeros(2); v = np.zeros(2); b1, b2, eps, lr = 0.9, 0.999, 1e-8, 0.1
print(f"  {'步':>3} {'g':>10} {'m(均值)':>12} {'v(方差)':>12} {'更新=m/(√v+ε)':>18}")
for step, g in enumerate(grads[:6]):
    g = np.array(g.tolist())
    m = b1*m + (1-b1)*g
    v = b2*v + (1-b2)*g**2
    mhat = m/(1-b1**(step+1)); vhat = v/(1-b2**(step+1))
    upd = lr * mhat/(np.sqrt(vhat)+eps)
    print(f"  {step:>3} {str(g.round(2)):>10} {str(m.round(2)):>12} {str(v.round(2)):>12} {str(upd.round(3)):>18}")
print("  => Adam: 方差大的方向(振荡) v大 -> 更新被√v缩放 -> 步长小; 稳定方向步长大")
print("     即'每个参数有自己的学习率', 自动适应梯度的尺度和稳定性")

print("\n核心洞察:")
print("  - 反传输出的是'原始梯度 g', 它只是原料")
print("  - Momentum: 用 g 的指数平均(动量)平滑振荡")
print("  - Adam: 用 g 的一阶矩(方向)+二阶矩(尺度)做自适应每参数学习率")
print("  - 理解这条链: 反传(算g) -> 优化器(加工g) -> 参数更新")
