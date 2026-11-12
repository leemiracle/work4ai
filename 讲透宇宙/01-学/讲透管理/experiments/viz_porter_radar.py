"""波特五力雷达图 (行业吸引力诊断)"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 五力: (名称, 强度1-5越高越不利, 权重)
forces = [
    ("行业内\n竞争", 4, 0.30),
    ("潜在\n进入者", 2, 0.20),
    ("替代品\n威胁", 3, 0.15),
    ("供应商\n议价", 3, 0.15),
    ("买方\n议价", 4, 0.20),
]
labels = [f[0] for f in forces]
scores = [f[1] for f in forces]
weights = [f[2] for f in forces]
weighted = sum(s * w for s, w in zip(scores, weights))

angles = np.linspace(0, 2 * np.pi, len(forces), endpoint=False).tolist()
values = scores + scores[:1]
angles_c = angles + angles[:1]

fig = plt.figure(figsize=(9, 9))
ax = fig.add_subplot(111, polar=True)
ax.plot(angles_c, values, color="C0", lw=2)
ax.fill(angles_c, values, color="C0", alpha=0.25)
ax.set_xticks(angles)
ax.set_xticklabels([f"{l}\n({w:.0%})" for l, w in zip(labels, weights)], fontsize=10)
ax.set_yticks([1, 2, 3, 4, 5])
ax.set_ylim(0, 5)
ax.set_title(f"Porter Five Forces (1=弱, 5=强)\n"
             f"加权竞争压力 = {weighted:.2f}/5  "
             f"({'压力较大' if weighted > 3 else '相对温和'})",
             fontsize=12, pad=20)
# 标注各力分数
for ang, val in zip(angles, scores):
    ax.annotate(str(val), xy=(ang, val), fontsize=11, fontweight="bold", ha="center",
                bbox=dict(boxstyle="round", fc="white", ec="gray"))
fig.tight_layout()
fig.savefig("/tmp/opencode/management_toolkit/porter_radar.png", dpi=115)
print(f"加权竞争压力 = {weighted:.2f} -> porter_radar.png")
