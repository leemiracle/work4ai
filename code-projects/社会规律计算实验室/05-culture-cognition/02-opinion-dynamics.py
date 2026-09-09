"""
02-opinion-dynamics.py · 观点动力学 · DeGroot + HK + SIR
=========================================================
子领域 5 · culture-cognition · 第 2 节

历史 · 直觉 · 数学
-------------------
观点动力学是文化/传播/认知子领域的核心数学工具。三个里程碑：

1. **DeGroot (1974)**：线性平均模型——观点是邻居的加权平均
   · x_i(t+1) = Σ w_ij x_j(t)，W = [w_ij] 是权重矩阵
   · 收敛到"加权平均共识"
   · 应用：社交媒体影响力、专家共识形成

2. **Hegselmann-Krause (2002)**：有界信任模型（已在子领域 4 讲过）
   · 只听观点接近的人 → 极化涌现

3. **SIR 模型 (1927)**：流行病模型
   · 信息扩散与疾病扩散同构
   · S（易感）→ I（感染）→ R（康复）
   · 一个推文传播 = 一个病毒传播

本节把三者串起来：从"观点如何变化"到"观点如何扩散"。
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
np.random.seed(42)


# ============================================================
# Part 1: DeGroot 模型——线性平均
# ============================================================

print("=" * 70)
print("Part 1: DeGroot 模型——共识形成")
print("=" * 70)
print("""
DeGroot 1974：每人观点 = 邻居观点的加权平均
  x(t+1) = W · x(t)
  长期：x(∞) = W^∞ · x(0)
  
如果 W 是不可约非周期的（连通图），最终所有人达成共识。
共识值取决于 W 和初始 x(0)。
""")

# 构造一个社交网络（随机图）
N = 50
G_adj = (np.random.rand(N, N) < 0.1).astype(float)
np.fill_diagonal(G_adj, 1)  # 自连接
# 行归一化得到 W
W = G_adj / G_adj.sum(axis=1, keepdims=True)

# 初始观点
x0 = np.random.uniform(0, 1, N)
x = x0.copy()
history = [x.copy()]

for t in range(30):
    x = W @ x
    history.append(x.copy())

history = np.array(history)
print(f"  初始观点标准差：{x0.std():.3f}")
print(f"  最终观点标准差：{x.std():.3f}（应该接近 0）")
print(f"  最终共识值：{x.mean():.3f}")
print(f"  → DeGroot 模型下，连通网络必然达成共识")


# ============================================================
# Part 2: 加入了"权威节点"的 DeGroot
# ============================================================

print("\n" + "=" * 70)
print("Part 2: 权威节点——少数人塑造共识")
print("=" * 70)

# 让节点 0 成为"权威"——很多节点连向他
W2 = G_adj.copy()
W2[:, 0] = 5  # 节点 0 权重高
W2 = W2 / W2.sum(axis=1, keepdims=True)

history2 = []
x = x0.copy()
x[0] = 0.9  # 权威节点观点是 0.9
fixed_node = 0
for t in range(30):
    new_x = W2 @ x
    new_x[fixed_node] = 0.9  # 权威不变
    x = new_x
    history2.append(x.copy())
history2 = np.array(history2)

print(f"  权威节点观点：固定为 0.9")
print(f"  最终平均观点：{x.mean():.3f}（应该被拉向 0.9）")
print(f"  → 少数权威节点能塑造整个群体的共识")


# ============================================================
# Part 3: SIR 信息扩散模型
# ============================================================

print("\n" + "=" * 70)
print("Part 3: SIR 信息扩散——一条推文如何传播")
print("=" * 70)
print("""
SIR 模型：
  · S（Susceptible 易感）：还没看到信息
  · I（Infected 感染）：正在转发
  · R（Recovered 康复）：看过但不再转发
  
传染率 β：S 看到信息后转发的概率
康复率 γ：I 不再转发的概率

基本再生数 R0 = β / γ：
  · R0 > 1：信息病毒式传播
  · R0 < 1：信息消亡
  · R0 = 1：临界点
""")

def sir_on_network(N, avg_degree, beta, gamma, days=50):
    """网络上的 SIR"""
    import networkx as nx
    G = nx.erdos_renyi_graph(N, avg_degree / N)
    # 初始：1 个感染
    state = np.array(['S'] * N)
    state[0] = 'I'
    S = [N - 1]; I = [1]; R = [0]
    
    for d in range(days):
        new_state = state.copy()
        for i in range(N):
            if state[i] == 'I':
                # 传染邻居
                for nb in G.neighbors(i):
                    if state[nb] == 'S' and np.random.rand() < beta:
                        new_state[nb] = 'I'
                # 自己康复
                if np.random.rand() < gamma:
                    new_state[i] = 'R'
        state = new_state
        S.append((state == 'S').sum())
        I.append((state == 'I').sum())
        R.append((state == 'R').sum())
        if I[-1] == 0:
            break
    return S, I, R

# 不同 R0 的对比
print(f"\n  不同 R0 下的传播规模：")
for beta, gamma in [(0.05, 0.1), (0.1, 0.1), (0.2, 0.1), (0.4, 0.1)]:
    R0 = beta / gamma * 10  # 接触数 10
    S, I, R = sir_on_network(1000, 10, beta, gamma, days=100)
    infected_total = R[-1] + I[-1]
    print(f"    β={beta}, γ={gamma}, R0≈{R0:.1f}: 感染 {infected_total}/1000 = {infected_total/10:.0f}%")


# ============================================================
# Part 4: 可视化
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# 4a: DeGroot 共识形成
ax = axes[0, 0]
for i in range(0, N, 5):
    ax.plot(range(31), history[:, i], alpha=0.5, linewidth=0.8)
ax.axhline(history[-1].mean(), color='red', linestyle='--', linewidth=2,
          label=f'共识值 = {history[-1].mean():.2f}')
ax.set_xlabel('迭代步', fontsize=11)
ax.set_ylabel('观点值', fontsize=11)
ax.set_title('DeGroot：连通网络必然达成共识', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# 4b: 权威节点
ax = axes[0, 1]
for i in range(0, N, 5):
    ax.plot(range(len(history2)), history2[:, i], alpha=0.5, linewidth=0.8)
ax.axhline(0.9, color='red', linestyle='--', linewidth=2, label='权威节点（固定 0.9）')
ax.set_xlabel('迭代步', fontsize=11)
ax.set_ylabel('观点值', fontsize=11)
ax.set_title('权威节点塑造共识\n（少数人塑造多数人观点）', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# 4c: SIR 不同 R0
ax = axes[1, 0]
for beta, gamma, color, label in [(0.05, 0.1, '#3498DB', 'R0≈5'),
                                    (0.1, 0.1, '#27AE60', 'R0≈10'),
                                    (0.2, 0.1, '#F39C12', 'R0≈20')]:
    S, I, R = sir_on_network(1000, 10, beta, gamma, days=80)
    ax.plot(I, label=f'β={beta}, {label}', linewidth=2, color=color)
ax.set_xlabel('时间', fontsize=11)
ax.set_ylabel('正在转发人数', fontsize=11)
ax.set_title('SIR：R0 决定信息爆发规模', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# 4d: 阈值模型——创新扩散
ax = axes[1, 1]
# Bass 模型简化：采纳者 = (p + q * F(t)) * (N - F(t))
# p = 创新系数, q = 模仿系数
def bass_diffusion(N_total, p, q, T=30):
    adopters = [N_total * p]
    cumulative = [adopters[0]]
    for t in range(1, T):
        new = (p + q * cumulative[-1] / N_total) * (N_total - cumulative[-1])
        adopters.append(new)
        cumulative.append(cumulative[-1] + new)
    return np.array(adopters), np.array(cumulative)

for p, q, color, label in [(0.03, 0.38, '#E74C3C', 'iPhone'),
                            (0.01, 0.5, '#9B59B6', 'TikTok'),
                            (0.001, 0.3, '#3498DB', '电动车')]:
    new_adopters, cum = bass_diffusion(1000, p, q)
    ax.plot(cum, label=f'{label} (p={p}, q={q})', linewidth=2, color=color)
ax.set_xlabel('时间', fontsize=11)
ax.set_ylabel('累计采纳者', fontsize=11)
ax.set_title('Bass 扩散模型\n（p=创新，q=模仿）', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('02-opinion-dynamics.png', dpi=100, bbox_inches='tight')
print(f"\n  图已保存：02-opinion-dynamics.png")


# ============================================================
# Part 5: 综合思考
# ============================================================

print("\n" + "=" * 70)
print("Part 5: 综合思考——三个模型的统一视角")
print("=" * 70)
print("""
DeGroot / HK / SIR 看似不同，本质都在描述**扩散动力学**：

  · DeGroot：观点在网络上"平滑扩散"（连续值）
  · HK：观点在有界信任下"分裂扩散"（多峰）
  · SIR：信息在网络上"传染扩散"（离散状态）

数学骨架都是：x(t+1) = f(W, x(t))

应用：
  · DeGroot → 分析 Facebook/Twitter 上的影响力
  · HK → 解释政治极化、商业品牌分化
  · SIR → 预测 meme 病毒式传播、谣言扩散

前沿：
  · LLM 时代的"AI agent 观点动力学"——AI 也能影响人类共识
  · Park et al. 2023 Generative Agents：AI agent 之间也有观点动力学
""")

print("=" * 70)
print("✓ 02-opinion-dynamics.py 跑通")
print("=" * 70)
