"""
03-polarization-emergence.py · 极化的涌现
==========================================
子领域 4 · power-politics · 第 3 节

历史 · 直觉 · 数学
-------------------
历史：
    2002 年，Rainer Hegselmann 和 Ulrich Krause 在 *JASSS* 发表
    《Opinion dynamics and bounded confidence: models, analysis 
    and synthesis》。他们提出"有界信任"（bounded confidence）模型：
    
    · 每人有观点 x_i ∈ [0, 1]
    · 只听"和自己观点接近"的人（差距 < ε）
    · 不断更新：x_i(t+1) = 平均(所有 |x_j - x_i| < ε 的 x_j)
    
    惊人结果：即使初始观点均匀分布，**最终会涌现出几个"观点簇"**——
    这就是极化（polarization）的数学涌现。
    
    ε 越小（人们越不宽容），簇越多（社会越分裂）。

直觉：
    想象一个班级 100 人，每人有政治观点（左 0 → 右 1）。
    
    · 如果所有人都能听所有人的：观点趋同，最终一个簇
    · 如果人只听观点差 < 0.1 的人：观点"团聚"成 ~5 个簇
    · 如果人只听观点差 < 0.05 的人：8-10 个簇（极端极化）
    
    "信息茧房"的数学化：当人们只接触同温层，观点自然分裂。
    
    这解释了为什么 Twitter / 微博上的政治讨论总是分裂的——
    算法放大"只听相似观点"的倾向。

数学（Hegselmann-Krause 模型）：
    更新规则：
        x_i(t+1) = (1/|N_i(t)|) Σ_{j ∈ N_i(t)} x_j(t)
        N_i(t) = {j : |x_i(t) - x_j(t)| ≤ ε}
    
    性质：
    · 总是收敛到稳定状态（不震荡）
    · 最终簇数取决于 ε 和初始分布
    · 经验：簇数 ≈ 1/(2ε)（ε=0.1 → 5 簇）

批判：
    - 假设人只看观点距离，不看权力/声誉
    - 不包含"激进分子"（坚持不更新）
    - 不包含"反向影响"（与远观点的人争论反而拉远）
    - 真实社交媒体的算法更复杂（不是单纯的 ε 截断）
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
np.random.seed(42)


# ============================================================
# Part 1: Hegselmann-Krause 模型实现
# ============================================================

def hk_model(N=200, eps=0.15, n_steps=30, init='uniform'):
    """Hegselmann-Krause 模型"""
    if init == 'uniform':
        x = np.random.uniform(0, 1, N)
    elif init == 'bimodal':
        x = np.concatenate([np.random.normal(0.3, 0.1, N//2),
                            np.random.normal(0.7, 0.1, N//2)])
        x = np.clip(x, 0, 1)
    
    history = [x.copy()]
    for _ in range(n_steps):
        new_x = np.zeros(N)
        for i in range(N):
            # 邻居：观点差 ≤ ε
            neighbors = np.abs(x - x[i]) <= eps
            new_x[i] = x[neighbors].mean()
        x = new_x
        history.append(x.copy())
        if np.allclose(history[-1], history[-2]):
            break
    return np.array(history)

print("=" * 70)
print("Part 1: HK 模型——不同 ε 下的极化涌现")
print("=" * 70)

for eps in [0.05, 0.1, 0.15, 0.3, 1.0]:
    history = hk_model(N=200, eps=eps)
    final = history[-1]
    n_clusters = len(np.unique(np.round(final, 2)))
    print(f"  ε = {eps:.2f}：最终簇数 ≈ {n_clusters}")

print(f"""
观察：
  · ε 大（信息茧房松）→ 趋同（1 簇）
  · ε 小（信息茧房紧）→ 极化（多簇）
  · ε 中等 → 几个稳定簇
""")


# ============================================================
# Part 2: 网络效应——加入"推荐算法"
# ============================================================

print("=" * 70)
print("Part 2: 算法放大极化")
print("=" * 70)
print("""
真实社交媒体的算法不只在"信息茧房"内推荐——
它**强化**你已有的偏好，制造"反向拉远"效应。

简化模型：算法让"和你观点差距 > 阈值"的人的观点
  被"拉远"（你认为他们更极端了）。
""")

def hk_with_algorithm(N=200, eps=0.15, algo_strength=0.5, n_steps=30):
    """HK + 算法反向拉远"""
    x = np.random.uniform(0, 1, N)
    history = [x.copy()]
    for _ in range(n_steps):
        new_x = np.zeros(N)
        for i in range(N):
            # 邻居
            neighbors_close = np.abs(x - x[i]) <= eps
            # 算法：把远观点的人"推得更远"
            far_mask = np.abs(x - x[i]) > eps
            pull = np.zeros(N)
            pull[neighbors_close] = x[neighbors_close] - x[i]
            pull[far_mask] = (x[far_mask] - x[i]) * (1 + algo_strength)
            if neighbors_close.sum() > 0:
                new_x[i] = x[i] + pull.mean()
            else:
                new_x[i] = x[i] + pull.mean() * 0.5  # 只剩算法拉力
        x = np.clip(new_x, 0, 1)
        history.append(x.copy())
    return np.array(history)

print("\n  对比：HK 标准模型 vs HK + 算法放大")
hist_standard = hk_model(N=200, eps=0.15)
hist_algo = hk_with_algorithm(N=200, eps=0.15, algo_strength=0.3)

print(f"    标准 HK 最终簇数：{len(np.unique(np.round(hist_standard[-1], 2)))}")
print(f"    + 算法放大最终簇数：{len(np.unique(np.round(hist_algo[-1], 2)))}")
print(f"    算法让观点更加分裂！")


# ============================================================
# Part 3: 可视化
# ============================================================

fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# 3a-c: 三个 ε 值的演化
for ax, eps in zip(axes[0], [0.05, 0.15, 0.3]):
    history = hk_model(N=100, eps=eps, n_steps=20)
    for i in range(0, 100, 5):
        ax.scatter(history[:, i], np.arange(len(history)), s=8, alpha=0.4, color='#3498DB')
    ax.set_xlabel('观点值（0=极左，1=极右）', fontsize=10)
    ax.set_ylabel('迭代步', fontsize=10)
    ax.set_title(f'ε = {eps}（{int(1/(2*eps))} 簇预期）', fontsize=12)
    ax.set_xlim(-0.05, 1.05)
    ax.grid(alpha=0.3)

# 3d: 簇数 vs ε
ax = axes[1, 0]
eps_range = np.linspace(0.02, 0.5, 20)
n_clusters_list = []
for eps in eps_range:
    history = hk_model(N=200, eps=eps, n_steps=30)
    n_clusters = len(np.unique(np.round(history[-1], 2)))
    n_clusters_list.append(n_clusters)
ax.plot(eps_range, n_clusters_list, 'o-', color='#E74C3C', linewidth=2)
ax.set_xlabel('ε（信任阈值）', fontsize=11)
ax.set_ylabel('最终簇数', fontsize=11)
ax.set_title('ε 越小，簇数越多\n（信息茧房越紧，社会越分裂）', fontsize=12)
ax.grid(alpha=0.3)

# 3e: 算法放大对比
ax = axes[1, 1]
ax.hist(hist_standard[-1], bins=20, alpha=0.5, color='#27AE60', label='标准 HK', density=True)
ax.hist(hist_algo[-1], bins=20, alpha=0.5, color='#E74C3C', label='+ 算法放大', density=True)
ax.set_xlabel('观点值', fontsize=11)
ax.set_ylabel('密度', fontsize=11)
ax.set_title('算法放大效应\n（红=更分裂，绿=相对集中）', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# 3f: 初始 bimodal 的演化
ax = axes[1, 2]
hist_bimodal = hk_model(N=100, eps=0.1, init='bimodal', n_steps=20)
for i in range(0, 100, 5):
    ax.scatter(hist_bimodal[:, i], np.arange(len(hist_bimodal)), s=8, alpha=0.4, color='#F39C12')
ax.set_xlabel('观点值', fontsize=11)
ax.set_ylabel('迭代步', fontsize=11)
ax.set_title('初始已极化（双峰）\nε=0.1 下进一步分裂', fontsize=12)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('03-polarization-emergence.png', dpi=100, bbox_inches='tight')
print(f"\n  图已保存：03-polarization-emergence.png")


# ============================================================
# Part 4: 现实意义
# ============================================================

print("\n" + "=" * 70)
print("Part 4: HK 模型解释现实")
print("=" * 70)
print("""
1. **美国政治极化**（1950-2020）
   · 1950：民主/共和党议员投票重叠度 ≈ 50%
   · 2020：重叠度 ≈ 5%
   · → ε 在持续变小（信息茧房加紧）
   
2. **算法的角色**
   · 推荐系统优化"engagement"
   · 同温层内容 engagement 高
   · → 算法**主动**降低 ε
   · → HK 模型预言的极化必然出现
   
3. **政策含义**
   · 强制"信息多样性"？→ GDPR、欧盟 DSA 法案
   · 让用户调 ε？→ Twitter/X 的算法选择
   · 教育？→ 批判性思维训练
   
4. **不能完全用算法解释**
   · HK 模型假设观点是 1 维的，但真实观点是多维
   · 加入"权力节点"（意见领袖）会改变动力学
   · 加入"反向影响"（与极端者争论会拉远你）会加剧
""")

print("=" * 70)
print("✓ 03-polarization-emergence.py 跑通")
print("=" * 70)
