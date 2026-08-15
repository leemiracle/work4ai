"""
项目风险: PERT三点估计 + 蒙特卡洛 —— 把单点估算变成分布
管理者常报"工期=X周"(单点), 但活动工期本是不确定。
用三角分布采样关键路径上各活动, 叠加得总工期分布,
给出 P10/P50/P90 与按期完工概率。
运行: python viz_risk.py  -> pert_risk.png
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(11)
# 关键路径 4 个活动 (乐观, 最可能, 悲观) 周
acts = [(2, 3, 6), (1, 2, 5), (2, 4, 9), (3, 5, 10)]
total = sum(rng.triangular(a, m, b, 200_000) for a, m, b in acts)

p10, p50, p90 = np.percentile(total, [10, 50, 90])
# 单点(最可能之和)估算
single = sum(m for _, m, _ in acts)
# 在单点工期内完工的概率
prob = np.mean(total <= single)

fig, ax = plt.subplots(figsize=(11, 6))
ax.hist(total, bins=120, color="C0", alpha=0.7, density=True)
for p, c, lbl in [(p10, "C2", "P10"), (p50, "C1", "P50(median)"),
                  (p90, "C3", "P90")]:
    ax.axvline(p, color=c, lw=2, label=f"{lbl} = {p:.1f}w")
ax.axvline(single, color="k", ls="--", lw=2,
           label=f"single-point est = {single}w")
ax.set_xlabel("project duration (weeks)"); ax.set_ylabel("density")
ax.set_title("PERT + Monte Carlo: from a number to a distribution")
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout()
out = "/tmp/opencode/management_toolkit/pert_risk.png"
fig.savefig(out, dpi=115)

print(f"[图] 已保存 {out}")
print(f"单点(最可能)估算 = {single} 周")
print(f"蒙特卡洛  P10={p10:.2f}  P50={p50:.2f}  P90={p90:.2f} 周")
print(f"按单点({single}w)完工的概率 = {prob:.1%}")
print("解读: 单点估算系统性低估工期(右偏分布), 用 P90 做承诺更稳健。")
