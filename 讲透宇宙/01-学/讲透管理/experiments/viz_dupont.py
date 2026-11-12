"""杜邦分析 ROE 三因素分解可视化"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

net_margin, asset_turn, equity_mult = 0.08, 1.5, 2.0
ROA = net_margin * asset_turn
ROE = ROA * equity_mult

fig, ax = plt.subplots(figsize=(13, 7))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")


def box(x, y, w, h, text, color):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.01", facecolor=color,
                                edgecolor="black", linewidth=1.2))
    ax.text(x, y, text, ha="center", va="center", fontsize=10, fontweight="bold")


def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                 arrowstyle="->", mutation_scale=14, color="gray"))


box(0.5, 0.9, 0.28, 0.1, f"ROE = {ROE:.1%}", "lightcoral")
for x, txt, val, col in [(0.2, "净利率\n(盈利能力)", f"{net_margin:.1%}", "lightblue"),
                         (0.5, "资产周转\n(运营效率)", f"{asset_turn}", "lightblue"),
                         (0.8, "权益乘数\n(财务杠杆)", f"{equity_mult}", "wheat")]:
    box(x, 0.62, 0.22, 0.1, f"{txt}\n{val}", col)
    arrow(x, 0.67, 0.5, 0.85)
# 进一步分解: 净利率=净利/营收
box(0.2, 0.32, 0.22, 0.09, "净利 / 营收", "lightyellow")
arrow(0.2, 0.365, 0.2, 0.57)
box(0.5, 0.32, 0.22, 0.09, "营收 / 总资产", "lightyellow")
arrow(0.5, 0.365, 0.5, 0.57)
box(0.8, 0.32, 0.22, 0.09, "总资产 / 权益", "lightyellow")
arrow(0.8, 0.365, 0.8, 0.57)

ax.set_title(f"DuPont Analysis: ROE = Net Margin × Asset Turnover × Equity Multiplier "
             f"= {net_margin:.0%} × {asset_turn} × {equity_mult} = {ROE:.1%}\n"
             f"(ROA = {ROA:.1%})", fontsize=12)
fig.text(0.5, 0.04, "管理诊断: 利润率低→查成本/定价; 周转低→查库存/应收; "
         "杠杆高→查偿债风险(放大ROE也放大风险)", ha="center", fontsize=9, style="italic")
fig.tight_layout()
fig.savefig("/tmp/opencode/management_toolkit/dupont.png", dpi=115)
print(f"ROE={ROE:.2%}, ROA={ROA:.2%} -> dupont.png")
