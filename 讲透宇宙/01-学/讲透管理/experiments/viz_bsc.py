"""平衡计分卡 BSC 四象限可视化"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

perspectives = [
    ("财务 Financial\n\"股东怎么看我们？\"", ["营收增长率 +15%", "ROE 24%", "EVA > 0"],
     "lightcoral"),
    ("客户 Customer\n\"客户怎么看我们？\"", ["NPS 62", "客户留存 92%", "客诉下降 20%"],
     "khaki"),
    ("内部流程 Process\n\"我们必须擅长什么？\"", ["交付准时率 98%", "缺陷率 <3σ→6σ", "周期时间 −30%"],
     "lightgreen"),
    ("学习成长 Learning\n\"如何持续创造价值？\"", ["员工敬业度 80", "培训时长 40h/人", "新技能认证 +25%"],
     "skyblue"),
]

fig, ax = plt.subplots(figsize=(12, 8.5))
ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.axis("off")
positions = [(0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)]  # 财务/客户/流程/学习
for (x, y), (title, metrics, color) in zip(positions, perspectives):
    ax.add_patch(plt.Rectangle((x - 0.48, y - 0.48), 0.96, 0.96,
                               facecolor=color, alpha=0.35, edgecolor="black", lw=1.5))
    ax.text(x, y + 0.38, title, ha="center", va="center", fontsize=11, fontweight="bold")
    for i, m in enumerate(metrics):
        ax.text(x, y + 0.18 - i * 0.22, "• " + m, ha="center", va="center", fontsize=9.5)
# 因果箭头: 学习→流程→客户→财务
arrows = [((0.5, 0.5), (1.5, 0.5)), ((1.5, 0.5), (1.5, 1.5)), ((1.5, 1.5), (0.5, 1.5))]
for (x1, y1), (x2, y2) in arrows:
    ax.annotate("", xy=(x2, y2 + (0.5 if y2 > y1 else 0) - 0.48),
                xytext=(x1 + 0.48, y1), arrowprops=dict(arrowstyle="->", lw=2, color="gray"))
ax.text(1, 1.02, "因果实录\n学习成长 → 内部流程 → 客户价值 → 财务成果",
        ha="center", fontsize=9, style="italic", color="dimgray",
        bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.8))
ax.set_title("Balanced Scorecard (Kaplan & Norton)\n把战略分解为四视角可衡量目标",
             fontsize=13, pad=12)
fig.tight_layout()
fig.savefig("/tmp/opencode/management_toolkit/bsc.png", dpi=115)
print("-> bsc.png")
