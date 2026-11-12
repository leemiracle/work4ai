"""AHP 层次分析法可视化: 权重柱状图 + 一致性"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

A = np.array([[1, 1/3, 1/5], [3, 1, 1/3], [5, 3, 1]], dtype=float)
criteria = ["成本 Cost", "质量 Quality", "速度 Speed"]
ev, vec = np.linalg.eig(A)
idx = np.argmax(ev.real)
w = vec[:, idx].real
w = w / w.sum()
lam = ev[idx].real
n = A.shape[0]
CI = (lam - n) / (n - 1)
RI = {3: 0.58, 4: 0.9, 5: 1.12}[n]
CR = CI / RI

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
ax = axes[0]
bars = ax.bar(criteria, w, color=["#e74c3c", "#3498db", "#2ecc71"], alpha=0.85)
ax.set_ylabel("权重 weight"); ax.set_ylim(0, 0.8)
ax.set_title(f"AHP 权重 (λmax={lam:.3f})")
for b, val in zip(bars, w):
    ax.text(b.get_x() + b.get_width() / 2, val + 0.01, f"{val:.3f}", ha="center", fontweight="bold")
ax.grid(axis="y", alpha=0.3)

ax2 = axes[1]
ax2.axis("off")
ax2.text(0.5, 0.85, "一致性检验 Consistency Check", ha="center", fontsize=13, fontweight="bold")
ax2.text(0.1, 0.65, f"λmax = {lam:.4f}", fontsize=11)
ax2.text(0.1, 0.52, f"CI = (λmax − n)/(n−1) = {CI:.4f}", fontsize=11)
ax2.text(0.1, 0.39, f"RI (n={n}) = {RI}", fontsize=11)
color = "green" if CR < 0.1 else "red"
ax2.text(0.1, 0.24, f"CR = CI/RI = {CR:.4f}", fontsize=13, fontweight="bold", color=color)
verdict = "✓ 一致 (CR<0.1), 判断可信" if CR < 0.1 else "✗ 不一致, 需修订两两比较"
ax2.text(0.1, 0.10, verdict, fontsize=12, color=color, fontweight="bold")
ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)

fig.suptitle("Analytic Hierarchy Process (Saaty)", fontsize=13)
fig.tight_layout()
fig.savefig("/tmp/opencode/management_toolkit/ahp.png", dpi=115)
print(f"weights={w.round(4)}, CR={CR:.4f} -> ahp.png")
