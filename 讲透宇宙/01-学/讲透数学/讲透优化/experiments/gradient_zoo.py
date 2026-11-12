#!/usr/bin/env python3
"""讲透优化实验 2：优化器动物园竞速。
GD / 重球 / Nesterov / Nelder-Mead 四者在 Rosenbrock 与病态二次上的对决。
产出：zoo.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "sans-serif"]

def rosen(x):
    return (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2

def grad_rosen(x):
    return np.array([-2*(1-x[0]) - 400*x[0]*(x[1]-x[0]**2), 200*(x[1]-x[0]**2)])

def run(oracle, grad, x0, steps, lr, beta, kind):
    x = np.array(x0, float); v = np.zeros_like(x); traj = [x.copy()]
    for _ in range(steps):
        if kind == "gd":
            x = x - lr * grad(x)
        elif kind == "mom":
            v = beta * v - lr * grad(x); x = x + v
        elif kind == "nag":
            v = beta * v - lr * grad(x + beta * v); x = x + v
        traj.append(x.copy())
    return np.array(traj)

x0 = (-1.2, 1.0)
res = {}
res["GD(η=2e-3)"] = run(rosen, grad_rosen, x0, 5000, 2e-3, 0, "gd")
res["重球(β=.9)"] = run(rosen, grad_rosen, x0, 5000, 2e-3, .9, "mom")
res["NAG(β=.9)"] = run(rosen, grad_rosen, x0, 5000, 1.5e-3, .9, "nag")
# 教学注记：NAG 用 lr=2e-3+β=.95 会发散（nan）——前瞻点飞出谷壁，"预见过猛"的实证；
# NAG 需要配更小步长，这是它对步长敏感的公认代价。
rnm = minimize(rosen, x0, method="Nelder-Mead")
print(f"Nelder-Mead: {rnm.nfev} 次评估 → f={rnm.fun:.3e}")
for name, T in res.items():
    print(f"{name}: f 终值={rosen(T[-1]):.3e}")

fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
xx, yy = np.meshgrid(np.linspace(-1.6, 1.6, 300), np.linspace(-0.5, 2.0, 300))
ZZ = (1-xx)**2 + 100*(yy-xx**2)**2
ax[0].contour(xx, yy, np.log10(ZZ+1e-10), levels=40, cmap="viridis")
for (name, T), c in zip(res.items(), ["r", "tab:orange", "tab:cyan"]):
    ax[0].plot(T[::40, 0], T[::40, 1], "-", c=c, label=name)
    ax[0].plot(T[-1, 0], T[-1, 1], "*", c=c, ms=14)
ax[0].plot(1, 1, "k+", ms=14, label="最优点")
ax[0].legend(fontsize=8); ax[0].set_title("Rosenbrock 轨迹（每 40 步采样）")
for (name, T), c in zip(res.items(), ["r", "tab:orange", "tab:cyan"]):
    ax[1].semilogy([rosen(t) for t in T[::10]], c=c, label=name)
ax[1].set_xlabel("步（×10）"); ax[1].set_ylabel("f（log）")
ax[1].legend(fontsize=8); ax[1].set_title("下降速度：前瞻 vs 惯性 vs 朴素")
fig.tight_layout(); fig.savefig("zoo.png", dpi=140)
print("saved zoo.png")
