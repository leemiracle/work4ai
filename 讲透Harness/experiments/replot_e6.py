#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 results/e6_verify_cascade.json 重画图（修正标题诚实性，零模型调用）。"""
import json
from common import setup_cn_font, fig_save

d = json.load(open("results/e6_verify_cascade.json"))
setup_cn_font()
import matplotlib.pyplot as plt
import numpy as np

acc = d["acc"]
cost = d["cost"]
fig, ax = plt.subplots(figsize=(8.5, 4.4))
conds = ["all_flash\n(全便宜档)", "cascade\n(flash→V2→glm-5)", "all_glm5\n(全贵档)"]
costs = [cost["all_flash"], cost["cascade"], cost["all_glm5"]]
accs = [acc["all_flash"] * 100, acc["cascade"] * 100, acc["all_glm5"] * 100]
x = np.arange(3)
ax.bar(x - 0.18, costs, 0.36, label="加权成本单位", color="#457b9d")
ax2 = ax.twinx()
ax2.bar(x + 0.18, accs, 0.36, label="完成率 %", color="#2a9d8f")
ax.set_xticks(x)
ax.set_xticklabels(conds)
ax.set_ylabel("成本单位（flash=1, glm5=20）")
ax2.set_ylabel("完成率 %")
ax2.set_ylim(0, 118)
for i in range(3):
    ax.text(i - 0.18, costs[i] + 1, f"{costs[i]:.0f}", ha="center", fontsize=9)
    ax2.text(i + 0.18, accs[i] + 2, f"{accs[i]:.0f}%", ha="center", fontsize=9)
ax.set_title("E6 验证即级联：易分布上 cascade≡all_flash 成本(1/20)，零遗憾侧成立（升级0次触发）")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=9)
fig_save(fig, "e6_verify_cascade")
print("e6 png regenerated")
