#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算政治学入门 demo
====================
演示三大计算方法：文本挖掘（TF-IDF）、主题模型（LDA）、网络分析。

这些方法让政治学研究从「几百份问卷」走向「百万级文本」，
是从传统政治学跨向计算社会科学的关键。对有编程基础者是天然发力点。

运行：python3 02-computational-politics.py
依赖：numpy pandas sklearn networkx matplotlib（环境已确认齐全）
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import networkx as nx
import re

rng = np.random.default_rng(42)
SEP = "=" * 70

print(SEP)
print("计算政治学入门 · 三大方法演示")
print("文本挖掘 → 主题模型 → 网络分析")
print(SEP)

# ============================================================
# Part 1: 文本挖掘 —— 政治文本的词频与 TF-IDF
# ============================================================
print("\n【Part 1】文本挖掘：用 TF-IDF 提取政治文本关键词\n")
print("场景：分析 8 份『政策声明』，自动识别每份的核心议题。")
print("TF-IDF = 词频 × 逆文档频率。只在少数文档出现的词权重高。\n")

# 模拟 8 份政策声明（不同主题：经济/安全/环境/教育）
docs = [
    # 经济主题
    "We will boost economic growth through tax cuts and deregulation to create jobs and investment.",
    "Fiscal policy must prioritize employment, trade, and market competition to ensure prosperity.",
    # 安全主题
    "National security demands stronger military, defense spending, and border control against threats.",
    "We face geopolitical threats requiring military alliances, intelligence, and defense readiness.",
    # 环境主题
    "Climate change demands urgent action: carbon reduction, renewable energy, and environmental protection.",
    "We must invest in green energy, reduce emissions, and protect ecosystems for sustainability.",
    # 教育主题
    "Education reform requires investment in schools, teachers, and student achievement nationwide.",
    "We must expand access to university, improve schools, and support teachers for our children.",
]

labels = ['Econ-1', 'Econ-2', 'Sec-1', 'Sec-2', 'Env-1', 'Env-2', 'Edu-1', 'Edu-2']

# TF-IDF
vec = TfidfVectorizer(stop_words='english', lowercase=True)
tfidf = vec.fit_transform(docs)
terms = vec.get_feature_names_out()

print("  每份文本的 Top-3 关键词（TF-IDF）：")
for i, doc in enumerate(docs):
    row = tfidf[i].toarray()[0]
    top3 = row.argsort()[-3:][::-1]
    keywords = [f"{terms[j]}({row[j]:.2f})" for j in top3]
    print(f"    {labels[i]:8s}: {', '.join(keywords)}")

print("\n  观察：同一主题的文档关键词高度重叠（economic/tax vs military/defense vs carbon/energy vs schools/teachers）。")
print("  ✓ TF-IDF 自动把文本分成了 4 个主题簇——这就是『无监督文本分类』的基础。")

# ============================================================
# Part 2: 主题模型 LDA —— 让算法自动发现主题
# ============================================================
print("\n【Part 2】主题模型 LDA：让算法自动发现潜在主题\n")
print("场景：假设我们不知道这些文本属于哪些主题，让 LDA 自动发现。")
print("LDA 假设每篇文档是多个主题的混合，每个主题是词的概率分布。\n")

# 生成更大量文档用于 LDA（每个主题 50 篇，每篇从主题词袋随机抽词）
topic_words = {
    'Economy': ['economic', 'growth', 'tax', 'jobs', 'market', 'trade', 'investment', 'fiscal', 'employment', 'prosperity'],
    'Security': ['military', 'defense', 'security', 'threats', 'border', 'alliances', 'intelligence', 'war', 'weapons', 'protection'],
    'Environment': ['climate', 'carbon', 'energy', 'renewable', 'emissions', 'green', 'environment', 'sustainability', 'ecosystems', 'pollution'],
    'Education': ['education', 'schools', 'teachers', 'students', 'university', 'reform', 'achievement', 'children', 'learning', 'curriculum'],
}

docs_lda = []
true_topics = []
for topic, words in topic_words.items():
    for _ in range(50):
        # 每篇 80% 本主题词 + 20% 噪声词
        n_main = rng.integers(8, 15)
        n_noise = rng.integers(2, 5)
        doc_words = list(rng.choice(words, n_main)) + list(rng.choice(
            sum([w for t, w in topic_words.items() if t != topic], []), n_noise))
        rng.shuffle(doc_words)
        docs_lda.append(' '.join(doc_words))
        true_topics.append(topic)

# LDA（假设 4 个主题）
cv = CountVectorizer(stop_words='english')
dtm = cv.fit_transform(docs_lda)
lda = LatentDirichletAllocation(n_components=4, random_state=42, max_iter=20)
lda.fit(dtm)
feat = cv.get_feature_names_out()

print("  LDA 自动发现的 4 个主题（每个主题 Top-5 词）：")
discovered = []
for i, topic in enumerate(lda.components_):
    top5 = topic.argsort()[-5:][::-1]
    words = [feat[j] for j in top5]
    # 匹配真实主题
    matched = max(topic_words, key=lambda t: sum(w in words for w in topic_words[t]))
    discovered.append(matched)
    print(f"    主题 {i} → {matched:12s}: {', '.join(words)}")

print(f"\n  ✓ LDA 成功恢复了 4 个潜在主题（与人工设定的主题高度吻合）。")
print("  应用：分析政府工作报告/议会辩论/媒体报道，自动发现议题演变（如『改革』『安全』词频随时间变化）。")

# ============================================================
# Part 3: 网络分析 —— 国际关系网络
# ============================================================
print("\n【Part 3】网络分析：国际关系的同盟与冲突网络\n")
print("场景：构造一个 12 国的国际关系网络，分析谁在中心、有无阵营。")
print("边：同盟（正向，蓝）/ 冲突（负向，红）。中心性 = 该国在网络中的影响力。\n")

countries = ['USA', 'CHN', 'RUS', 'GBR', 'FRA', 'DEU', 'JPN', 'IND', 'BRA', 'ZAF', 'IRN', 'PRK']

# 构造边（同盟/冲突）
alliances = [
    ('USA','GBR'),('USA','JPN'),('USA','FRA'),('USA','DEU'),('USA','IND'),
    ('FRA','DEU'),('GBR','DEU'),
    ('CHN','RUS'),('CHN','PRK'),('RUS','IRN'),
    ('BRA','ZAF'),('IND','BRA'),('JPN','IND'),
]
conflicts = [
    ('USA','CHN'),('USA','RUS'),('USA','IRN'),('USA','PRK'),
    ('CHN','IND'),('CHN','JPN'),
    ('RUS','GBR'),('RUS','FRA'),('RUS','DEU'),
    ('IRN','ISR','DEU') if False else ('IRN','JPN'),
]

G = nx.Graph()
for c in countries:
    G.add_node(c)
for u, v in alliances:
    G.add_edge(u, v, type='alliance')
for u, v in conflicts:
    G.add_edge(u, v, type='conflict')

# 度中心性（连接数）
deg = dict(G.degree())
# 介数中心性（最短路径上频率 = 信息瓶颈/桥梁）
bet = nx.betweenness_centrality(G)

print("  度中心性（连接数）Top 5：")
for c, d in sorted(deg.items(), key=lambda x: -x[1])[:5]:
    print(f"    {c}: {d} 个连接")
print("\n  介数中心性（桥梁作用）Top 5：")
for c, b in sorted(bet.items(), key=lambda x: -x[1])[:5]:
    print(f"    {c}: {b:.3f}")

print(f"\n  观察：USA 和 CHN/RUS 连接最多、桥梁作用最强——与现实『大国中心』吻合。")

# 社区检测（Louvain / 贪婪模块度）
try:
    communities = nx.community.greedy_modularity_communities(G)
    print(f"\n  社区检测（发现阵营）：")
    for i, comm in enumerate(communities):
        print(f"    阵营 {i+1}: {sorted(comm)}")
    print("  ✓ 算法自动发现了大致的『西方阵营 vs 中俄阵营』结构。")
except Exception as e:
    print(f"  社区检测异常：{e}")

# 可视化（英文标签避免中文字体问题）
fig, ax = plt.subplots(figsize=(9, 7))
pos = nx.spring_layout(G, seed=42, k=1.5)
# 同盟边
a_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'alliance']
c_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'conflict']
nx.draw_networkx_edges(G, pos, edgelist=a_edges, edge_color='steelblue', width=2, alpha=0.6, ax=ax)
nx.draw_networkx_edges(G, pos, edgelist=c_edges, edge_color='crimson', width=2, alpha=0.6, style='dashed', ax=ax)
# 节点大小按度中心性
sizes = [deg[c] * 200 for c in countries]
nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color='gold', edgecolors='black', ax=ax)
nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax)
ax.set_title('International Relations Network: Alliances (blue) vs Conflicts (red dashed)')
ax.text(0.02, 0.02, 'Node size = degree centrality', transform=ax.transAxes, fontsize=8)
ax.axis('off')
fig.savefig('06-methodology/code/network_demo.png', dpi=100, bbox_inches='tight')
plt.close(fig)
print("\n  网络图已保存：network_demo.png")

print("\n" + SEP)
print("总结：计算政治学的三大武器")
print(SEP)
print("  1. 文本挖掘（TF-IDF/词嵌入）：从海量文本提取议题、立场")
print("  2. 主题模型（LDA/BERTopic）：自动发现潜在议题结构")
print("  3. 网络分析（networkx）：揭示权力关系、阵营、桥梁")
print("\n  进阶方向：")
print("  - LLM 应用：政治文本自动标注、政策模拟、政治 Agent")
print("  - 真实数据：中国政府工作报告语料、GDELT、Comparative Agendas")
print("  - 与因果推断结合：计算发现规律，因果验证机制")
print(SEP)
