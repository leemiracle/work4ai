"""
组织网络分析 ONA 可视化 —— 揭示"非正式组织"
用 Zachary 空手道俱乐部(经典社会网络数据)演示:
  - 度中心性(谁连接多) / 介数中心性(谁是信息桥) / 特征向量中心性(谁连大腕)
  - 社区检测(组织里的非正式派系)
管理者用 ONA 找出真正的"连接者""孤岛""意见领袖", 而非只看组织架构图。
运行: python viz_ona.py  ->  ona_karate.png
"""
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

G = nx.karate_club_graph()
deg = dict(G.degree())
btw = nx.betweenness_centrality(G)
eig = nx.eigenvector_centrality(G, max_iter=2000)
comms = list(nx.community.greedy_modularity_communities(G))
cmap = {}
for i, c in enumerate(comms):
    for node in c:
        cmap[node] = i

pos = nx.spring_layout(G, seed=3)
sizes = [180 + deg[n] * 130 for n in G.nodes()]
colors = [cmap[n] for n in G.nodes()]
top_btw = max(btw, key=btw.get)
top_deg = max(deg, key=deg.get)

fig, ax = plt.subplots(figsize=(10, 8.5))
nx.draw_networkx_edges(G, pos, alpha=0.25, ax=ax)
nc = nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors,
                            cmap="tab10", alpha=0.9, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
# 高亮两个关键意见领袖
nx.draw_networkx_nodes(G, pos, nodelist=[top_btw], node_size=sizes[top_btw],
                       node_color="none", edgecolors="red", linewidths=3, ax=ax)
nx.draw_networkx_nodes(G, pos, nodelist=[top_deg], node_size=sizes[top_deg],
                       node_color="none", edgecolors="darkgreen", linewidths=3, ax=ax)
ax.set_title(f"Organizational Network Analysis (Zachary Karate Club)\n"
             f"size=degree  color=community({len(comms)})  "
             f"red ring=top betweenness(node {top_btw})  "
             f"green ring=top degree(node {top_deg})", fontsize=10)
ax.axis("off")
fig.tight_layout()
out = "/tmp/opencode/management_toolkit/ona_karate.png"
fig.savefig(out, dpi=115)
print(f"[图] 已保存 {out}")
print(f"节点={G.number_of_nodes()} 边={G.number_of_edges()} 社区={len(comms)} 大小={[len(c) for c in comms]}")
print(f"度中心性最高: {top_deg}  介数最高: {top_btw}")
print("管理学解读: 节点0与33是事实上的'双领袖', 高中心性=影响力; ")
print("           社区检测还原了历史上的真实派系分裂(经典结论)。")
