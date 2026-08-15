"""
系统动力学可视化 —— 反馈、延迟与涌现
对比两个库存系统:
  (a) 一阶负反馈(无延迟): 库存平滑趋近稳态
  (b) 二阶系统(含供应链延迟): 库存过冲振荡 —— 啤酒游戏/牛鞭效应的数学根源
管理含义: 结构(反馈环 + 延迟)决定行为; 同样的"理性"局部策略,
         放进不同结构会产生截然不同的系统结果(Forrester/Sterman)。
运行: python viz_systems.py  ->  systems_dynamics.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

dt = 0.5
steps = 120
target, sales, tau = 100.0, 10.0, 5.0

# (a) 一阶负反馈: production = (target - inv)/tau
inv1 = [20.0]
for _ in range(steps):
    p = max((target - inv1[-1]) / tau, 0)
    inv1.append(inv1[-1] + (p - sales) * dt)

# (b) 二阶带延迟: 订单进入长度=delay 的管线, 经延迟到货
delay = 3
inv2 = [50.0]
pipe = [0.0] * delay
for _ in range(steps):
    order = max((target - inv2[-1]) / 4, 0)
    arrived = pipe.pop(0)
    pipe.append(order)
    inv2.append(inv2[-1] + (arrived - sales) * dt)

t = np.arange(steps + 1) * dt
fig, ax = plt.subplots(figsize=(11, 6))
ax.axhline(target, color="gray", ls=":", label="target inventory")
ax.plot(t, inv1, color="C2", lw=2, label="(a) 1st-order negative feedback (smooth)")
ax.plot(t, inv2, color="C3", lw=2, label="(b) 2nd-order w/ delay (oscillates → bullwhip)")
ax.set_xlabel("time"); ax.set_ylabel("inventory")
ax.set_title("System Dynamics: same goal, different structure → different behavior")
ax.legend(); ax.grid(alpha=0.3)
ax.annotate("delay → overshoot & oscillation\n(= bullwhip effect)",
            xy=(t[np.argmax(inv2)], max(inv2)), xytext=(t[40], max(inv2)+5),
            arrowprops=dict(arrowstyle="->", color="C3"), color="C3")
fig.tight_layout()
out = "/tmp/opencode/management_toolkit/systems_dynamics.png"
fig.savefig(out, dpi=115)
print(f"[图] 已保存 {out}")
print("稳态(无延迟) = target - sales*tau = 100 - 10*5 = 50 (持续补货抵消销售)")
print("含延迟系统: 过冲振荡, 难以稳定 —— 揭示管理中'延迟'的危害")
