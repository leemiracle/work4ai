#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《君主论》概念分析 · 全栈精读的计算层
======================================
用 networkx 可视化核心概念网络 + matplotlib 展示章节主题演变。
演示"如何用计算工具读经典"——即使没有全文，也可手动整理概念数据做可视化。

运行：python3 君主论-概念分析.py
依赖：networkx matplotlib（环境已确认齐全）
"""
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

SEP = "=" * 70
print(SEP)
print("《君主论》概念分析 · 全栈精读计算层")
print(SEP)

# ============================================================
# Part 1: 概念共现网络
# ============================================================
print("\n【Part 1】核心概念网络\n")
print("手动整理《君主论》核心概念的关系，可视化全书的概念骨架。\n")

G = nx.Graph()

# 核心概念（节点）
concepts = {
    'virtu': '德能/力能（果敢+狡黠）',
    'fortuna': '命运/时运',
    'necessita': '必然性',
    'verita_effettuale': '实效真理',
    'lion': '狮（力量）',
    'fox': '狐（狡黠）',
    'feared': '被惧',
    'loved': '被爱',
    'borgia': '博尔贾（理想原型）',
    'power': '权力维持',
}
for c in concepts:
    G.add_node(c, label=concepts[c])

# 关系（边）
# (节点1, 节点2, 关系类型, 权重)
edges = [
    ('verita_effettuale', 'power', 'basis', 3),     # 实效真理是认识论基础
    ('virtu', 'fortuna', 'oppose', 5),               # virtù 对抗 fortuna（核心张力）
    ('virtu', 'lion', 'is', 2),                      # virtù 包含狮
    ('virtu', 'fox', 'is', 2),                       # virtù 包含狐
    ('virtu', 'feared', 'enables', 3),               # virtù 使被惧成为可能
    ('fortuna', 'power', 'limit', 4),                # fortuna 限制权力
    ('necessita', 'virtu', 'constrain', 3),          # 必然性框定 virtù
    ('feared', 'loved', 'oppose', 5),                # 被惧 vs 被爱（第17章）
    ('feared', 'power', 'secure', 4),                # 被惧更安全
    ('borgia', 'virtu', 'example', 2),               # 博尔贾是 virtù 的典范
    ('necessita', 'power', 'shape', 2),
]
for u, v, rel, w in edges:
    G.add_edge(u, v, relation=rel, weight=w)

# 度中心性（哪个概念连接最多 = 枢纽概念）
deg = dict(G.degree())
print("  概念的度中心性（连接数，越高越是枢纽）：")
for c, d in sorted(deg.items(), key=lambda x: -x[1]):
    marker = ' ◄ 枢纽' if d >= 3 else ''
    print(f"    {c:20s}: {d} 个连接{marker}")

# 介数中心性（桥梁作用）
bet = nx.betweenness_centrality(G)
print(f"\n  介数中心性（桥梁作用，连接不同概念簇）：")
for c, b in sorted(bet.items(), key=lambda x: -x[1])[:3]:
    print(f"    {c:20s}: {b:.3f}")

# 可视化
fig, ax = plt.subplots(figsize=(10, 7))
pos = nx.spring_layout(G, seed=42, k=2)
# 边按关系类型着色
rel_colors = {'oppose': 'crimson', 'basis': 'black', 'is': 'steelblue',
              'enables': 'green', 'limit': 'orange', 'constrain': 'purple',
              'secure': 'green', 'example': 'gray', 'shape': 'orange'}
for u, v, d in G.edges(data=True):
    color = rel_colors.get(d['relation'], 'gray')
    nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=color,
                           width=d['weight'], alpha=0.6, ax=ax)
# 节点大小按度中心性
sizes = [deg[c] * 400 + 300 for c in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color='lightyellow',
                       edgecolors='black', ax=ax)
nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
ax.set_title("Machiavelli's 'The Prince': Concept Network\n"
             "(red=opposition, green=enables/secure, size=centrality)")
ax.axis('off')
fig.savefig('01-political-theory/code/concept_network.png', dpi=100, bbox_inches='tight')
plt.close(fig)
print("\n  概念网络图已保存：concept_network.png")

# ============================================================
# Part 2: 章节主题演变
# ============================================================
print("\n【Part 2】章节主题演变（26 章）\n")
print("标注每章主题，看全书如何从『分类』走向『品质』走向『命运』。\n")

chapters = [
    (1, 11, 'Types of Principalities', '君主国分类'),
    (12, 14, 'Military', '军事'),
    (15, 19, 'Qualities of Prince (CORE)', '君主品质（核心）'),
    (20, 24, 'Consolidating Power', '巩固政权'),
    (25, 25, 'Fortune', '命运'),
    (26, 26, 'Call for Italy', '呼吁意大利统一'),
]

fig, ax = plt.subplots(figsize=(10, 4))
colors = ['#4ECDC4', '#45B7D1', '#FF6B6B', '#95E1D3', '#FFA07A', '#DDA0DD']
for i, (start, end, theme_en, theme_cn) in enumerate(chapters):
    ax.barh(0, end - start + 1, left=start, height=0.5, color=colors[i],
            edgecolor='black', label=theme_en)
    ax.text((start + end) / 2, 0, theme_en.split('(')[0].strip(),
            ha='center', va='center', fontsize=8, fontweight='bold')

ax.set_xlim(0, 27)
ax.set_ylim(-0.5, 0.5)
ax.set_xlabel('Chapter')
ax.set_yticks([])
ax.set_title("The Prince: Chapter Theme Evolution (26 chapters)")
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8)
fig.savefig('01-political-theory/code/chapter_themes.png', dpi=100, bbox_inches='tight')
plt.close(fig)

print("  全书结构：")
for start, end, en, cn in chapters:
    bar = '█' * (end - start + 1)
    print(f"    Ch {start:2d}-{end:2d}: {bar} {en}")
print("\n  章节主题图已保存：chapter_themes.png")

# ============================================================
# Part 3: virtù vs fortùna 的"五五开"可视化
# ============================================================
print("\n【Part 3】virtù vs fortuna：命运与能动性的张力\n")
print("马基雅维利估算『半归命运，半靠自己』。这是全书最深的哲学张力。\n")

fig, ax = plt.subplots(figsize=(6, 6))
sizes = [50, 50]
labels = ['fortuna\n(Fate/Uncertainty)\n不可控的时运', 
          'virtu\n(Agency/Capability)\n果敢+狡黠+决断']
colors = ['#FF9999', '#66B2FF']
wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                   autopct='%d%%', startangle=90,
                                   textprops={'fontsize': 10})
ax.set_title("Machiavelli's 50-50:\nHalf Fate, Half Agency", fontsize=13, fontweight='bold')
# 中心标注
ax.text(0, 0, 'Political\nSuccess', ha='center', va='center',
        fontsize=12, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='black'))
fig.savefig('01-political-theory/code/virtu_fortuna.png', dpi=100, bbox_inches='tight')
plt.close(fig)
print("  张力图已保存：virtu_fortuna.png")
print("\n  解读：这是反宿命论（人有 50% 空间），也是反狂妄（人不是全能）。")
print("        健康的政治哲学/人生哲学，都在这『五五开』的张力里。")

print("\n" + SEP)
print("计算层总结：用三种可视化读懂《君主论》的结构")
print(SEP)
print("  1. 概念网络：virtù 是枢纽（连接最多），核心张力是 fortuna vs virtù")
print("  2. 章节演变：15-19 章（君主品质）是全书核心")
print("  3. 五五开：命运与能动性的张力，是全书哲学基石")
print("\n  这就是『用计算工具读经典』——让结构可见，让关系清晰。")
print("  方法可复制到任何书：整理概念→画网络→看枢纽与张力。")
print(SEP)
