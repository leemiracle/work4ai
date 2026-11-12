"""
实验 03 — 网络结构: 小世界 / 无标度 / 神经拓扑
对应文档: 讲透系统论/03-网络结构.md

核心结论:
  1. 规则网络: 聚集高 + 路径长 (晶格)
  2. 随机网络: 聚集低 + 路径短 (Erdős-Rényi)
  3. 小世界 (Watts-Strogatz): 聚集高 + 路径短 (社交网络)
  4. 无标度 (Barabási-Albert): 度分布幂律 (互联网/神经网络)
  5. 不同拓扑 → 不同动力学 (病毒传播/信息扩散)

跑法: python3 -u 03_networks.py
"""
import math, random
from collections import Counter, deque
import numpy as np
random.seed(0); np.random.seed(0)

def P(*a): print(*a, flush=True)

# ============================================================
# 网络生成
# ============================================================
def make_lattice(N, k=4):
    """规则环形网格: 每个节点连 k 个最近邻"""
    G = {i: set() for i in range(N)}
    for i in range(N):
        for d in range(1, k//2+1):
            G[i].add((i+d) % N)
            G[(i+d) % N].add(i)
    return G

def make_random(N, p):
    """Erdős-Rényi 随机网络: 每对节点以概率 p 相连"""
    G = {i: set() for i in range(N)}
    for i in range(N):
        for j in range(i+1, N):
            if random.random() < p:
                G[i].add(j); G[j].add(i)
    return G

def make_small_world(N, k=4, p_rew=0.1):
    """Watts-Strogatz 小世界: 规则网格 + 概率重连"""
    G = make_lattice(N, k)
    for i in range(N):
        neighbors = list(G[i])
        for nb in neighbors:
            if random.random() < p_rew:
                G[i].discard(nb); G[nb].discard(i)
                new = random.choice([j for j in range(N) if j != i and j not in G[i]])
                G[i].add(new); G[new].add(i)
    return G

def make_scale_free(N, m=2):
    """Barabási-Albert 无标度: 偏好依附"""
    # 初始完全图 m+1 个节点
    G = {i: set(range(m+1)) - {i} for i in range(m+1)}
    for new in range(m+1, N):
        # 按 degree 选中 m 个节点
        degrees = [len(G[i])*1.0 for i in range(new)]
        total = sum(degrees)
        chosen = []
        for _ in range(m):
            r = random.uniform(0, total)
            acc = 0
            for i, d in enumerate(degrees):
                if i in chosen: continue
                acc += d
                if acc >= r:
                    chosen.append(i)
                    total -= d
                    break
        for c in chosen:
            G[new].add(c); G[c].add(new)
        G[new] = G.get(new, set())
    return G

# ============================================================
# 网络度量
# ============================================================
def avg_path_length(G, n_samples=100):
    """平均最短路径长度 (采样估计)"""
    nodes = list(G.keys())
    total_len = 0; cnt = 0
    for _ in range(n_samples):
        s = random.choice(nodes); t = random.choice(nodes)
        if s == t: continue
        # BFS
        visited = {s}; q = deque([(s, 0)])
        found = False
        while q:
            n, d = q.popleft()
            if n == t:
                total_len += d; cnt += 1; found = True; break
            for m in G[n]:
                if m not in visited:
                    visited.add(m); q.append((m, d+1))
        if not found: total_len += len(nodes)  # 不连通惩罚
    return total_len / cnt if cnt > 0 else float('inf')

def clustering_coefficient(G):
    """聚集系数: 邻居之间也连的比例"""
    total = 0
    for n in G:
        neighbors = list(G[n])
        k = len(neighbors)
        if k < 2: continue
        # 邻居之间实际连接数
        links = 0
        for i in range(len(neighbors)):
            for j in range(i+1, len(neighbors)):
                if neighbors[j] in G[neighbors[i]]:
                    links += 1
        total += 2 * links / (k * (k-1))
    return total / len(G)

def degree_distribution(G):
    """度分布"""
    degrees = [len(G[n]) for n in G]
    return Counter(degrees)

# ============================================================
# Part 1: 四种网络拓扑对比
# ============================================================
P("="*70)
P("实验 03 — 网络结构: 小世界 / 无标度 / 神经拓扑")
P("="*70)
P()
P(f"N=500 节点的四种网络:")
P()

N = 500
networks = [
    ("规则网格 (k=4)",       make_lattice(N, 4)),
    ("随机 (p=0.01)",        make_random(N, 0.01)),
    ("小世界 (WS, p=0.1)",   make_small_world(N, 4, 0.1)),
    ("无标度 (BA, m=2)",     make_scale_free(N, 2)),
]

print(f"{'网络类型':<24}{'平均路径':>10}{'聚集系数':>12}{'最大度':>10}{'特征':<20}")
print("-"*76)
for name, G in networks:
    avg_pl = avg_path_length(G, n_samples=50)
    cc = clustering_coefficient(G)
    degrees = [len(G[n]) for n in G]
    max_deg = max(degrees)
    avg_deg = sum(degrees) / len(degrees)
    feature = ("路径长+聚集高" if avg_pl > 50 and cc > 0.4 else
               "路径短+聚集低" if avg_pl < 5 and cc < 0.1 else
               "路径短+聚集高" if avg_pl < 10 and cc > 0.2 else
               "幂律分布" if max_deg > 5 * avg_deg else "?")
    print(f"{name:<24}{avg_pl:>10.2f}{cc:>12.4f}{max_deg:>10}{feature:<20}")

P("""
观察:
- 规则网格: 路径长 (50+), 聚集高 (0.5) — 晶格、邻居都认识
- 随机网络: 路径短 (~3), 聚集低 (0.01) — 全随机, 邻居互不认识
- 小世界 (WS): 路径短 + 聚集高 — 社交网络 (朋友的朋友也认识)
- 无标度 (BA): 最大度极高 (hub) — 互联网/神经网络 (几个超大节点)
""")

# ============================================================
# Part 2: 度分布 — 区分随机 vs 无标度
# ============================================================
P("="*70)
P("Part 2: 度分布 — 随机(泊松) vs 无标度(幂律)")
P("-"*70)
P()

import statistics
print(f"{'网络':<18}{'平均度':>10}{'度标准差':>12}{'最大度':>10}{'分布性质':<20}")
print("-"*68)
for name, G in networks:
    degrees = [len(G[n]) for n in G]
    avg_d = statistics.mean(degrees)
    std_d = statistics.stdev(degrees)
    max_d = max(degrees)
    nature = "泊松 (窄)" if std_d < avg_d * 0.7 else "幂律 (宽, 有 hub)"
    print(f"{name:<18}{avg_d:>10.2f}{std_d:>12.2f}{max_d:>10}{nature:<20}")

P("""
关键差异:
- 随机网络: 度分布服从泊松 (窄峰), 度集中在平均值附近
- 无标度网络: 度分布服从幂律 P(k) ∝ k^(-γ), 有少数极大 hub

幂律的工程意义:
- 互联网: 几个超大网站 (Google/Facebook) + 大量小网站
- 神经网络: 几个超级神经元 (与所有其他神经元连接)
- 经济: 几个超大公司 + 大量小公司

幂律网络的特性:
- 对随机故障鲁棒 (大部分小节点断了无所谓)
- 对定向攻击脆弱 (干掉 hub 整个网络崩)
""")

# ============================================================
# Part 3: 网络结构 → AI 的桥
# ============================================================
P("="*70)
P("Part 3: 网络结构 → AI")
P("-"*70)
P("""
1. 【神经网络的拓扑】
   - 全连接 (MLP): 规则网络
   - CNN: 局部连接 + 权重共享 (类似晶格)
   - ResNet: 残差连接 = [捷径] → 类似小世界的长程边
   - Transformer attention: 动态全连接 (任意 token 都能交互)

2. 【LLM 的 attention = 动态小世界】
   - 静态网络: 固定拓扑
   - attention: 每个 token 动态决定连接权重
   - 这是 [可学习的拓扑] — 网络结构在训练中演化

3. 【MoE (Mixture of Experts) = 无标度】
   - 稀疏激活: 每个 token 只激活少数 expert
   - 几个 expert 被频繁使用 (= hub), 其他 expert 较少
   - 度分布呈现幂律

4. 【多 Agent 拓扑】
   - 中心化 (一个 boss): hub-spoke
   - 去中心化 (peer-to-peer): 全连接
   - 层级: 树形
   - 不同拓扑 → 不同协作效率
""")

# ============================================================
# Part 4: 拓扑决定动力学
# ============================================================
P("="*70)
P("Part 4: 拓扑决定动力学 — 病毒传播模拟")
P("-"*70)

def simulate_spread(G, p_infect=0.1, n_steps=30):
    """SIR 模型: 一个初始感染节点, 病毒以 p 概率传给邻居"""
    nodes = list(G.keys())
    infected = {random.choice(nodes)}
    recovered = set()
    history = []
    for t in range(n_steps):
        new_infected = set()
        for n in infected:
            for m in G[n]:
                if m not in infected and m not in recovered:
                    if random.random() < p_infect:
                        new_infected.add(m)
        recovered.update(infected)
        infected = new_infected
        total = len(infected) + len(recovered)
        history.append(total / len(nodes))
        if not infected: break
    return history

print(f"\n病毒传播模拟 (SIR, p_infect=0.1, N={N}):")
print(f"{'网络类型':<24}{'最终感染率':>12}{'达 50% 用时':>14}")
print("-"*50)
for name, G in networks:
    random.seed(0)
    history = simulate_spread(G, p_infect=0.1, n_steps=50)
    final = history[-1] if history else 0
    t_50 = next((i+1 for i, h in enumerate(history) if h > 0.5), ">50")
    print(f"{name:<24}{final:>12.1%}{t_50:>14}")

P("""
观察:
- 路径短的网络: 病毒传播快 (短时间大感染)
- 小世界 / 随机 / 无标度: 都快速传播 (因路径短)
- 规则网格: 传播慢 (因路径长)

拓扑决定动力学 — 这就是为什么 [网络结构] 是系统论的核心概念.
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
网络拓扑是 [组件如何连接] 的描述:
- 规则网格: 聚集高+路径长 (晶格)
- 随机: 聚集低+路径短 (泊松分布)
- 小世界: 聚集高+路径短 (社交网络, WS 模型)
- 无标度: 幂律分布 (互联网/神经网络, BA 模型)

AI 中的拓扑:
- MLP: 规则网络
- CNN: 局部+共享 (晶格变体)
- ResNet 残差: 长程边 (类似小世界)
- attention: 动态全连接
- MoE: 稀疏激活 (类似无标度)

拓扑决定动力学: 路径短 → 信息扩散快; 路径长 → 慢.
这解释了 [为什么 ResNet 比 MLP 强] — 残差连接让信息传播更高效.
""")
