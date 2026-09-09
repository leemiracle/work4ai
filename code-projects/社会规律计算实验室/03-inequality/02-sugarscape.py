"""
02-sugarscape.py · Sugarscape · 财富分布的涌现
================================================
子领域 3 · inequality · 最经典模型

历史 · 直觉 · 数学
-------------------
历史：
    1996 年，Brookings Institution 的 Joshua Epstein 和 Robert Axtell
    出版《Growing Artificial Societies》。他们造了一个"人工社会"
    叫 Sugarscape（糖境）——一个 2D 网格，每格有不同含糖量，
    上面生活着一群"糖人"。
    
    每个糖人有：
    · 位置（在网格上）
    · 视野（能看多远）
    · 代谢率（每回合消耗多少糖）
    · 当前糖储量（财富）
    
    规则极简：每回合去找最近的高糖格子，吃糖，扣代谢。
    
    令人震惊的结果：即使**所有糖人完全平等**（只是视野/代谢随机
    抽样），跑几百回合后，**财富分布是高度不平等的幂律**！
    
    20% 糖人拥有 80% 财富——帕累托法则自发涌现。
    
    这就是 ABM（Agent-Based Model）的胜利——**没有"剥削"，没有
    "市场失灵"，没有"制度不公"，不平等从微观随机规则涌现**。

直觉：
    想象一个公平社会：所有人能力随机但有上限，所有人努力工作，
    没有特权，没有继承。
    
    跑下来还是不平等。为什么？
    · 随机初始位置的微小差异 → 累积成巨大差异
    · 高代谢（倒霉）+ 远离糖源 → 立刻死亡
    · 视野好（运气）+ 高糖位置 → 财富累积
    
    "起跑线上的随机抖动" + "正反馈" = 不平等涌现。
    
    这对"机会平等"的政策有深刻含义——光公平起跑线不够。

数学：
    Sugarscape 不是数学模型，是**计算模型**。但结果可以用统计描述：
    · 财富分布 P(w) ~ w^(-α)，α ≈ 1-2（帕累托指数）
    · 基尼系数 G ≈ 0.5-0.7（不平等）
    
    关键：与"理性个体最优化"无关，是**群体动力学**的涌现。

批判：
    - Sugarscape 的简化太极端——真实社会有制度、产权、教育
    - 但简化正是它的力量——证明"光随机就够"
    - 不解释不平等的全部，只解释一部分——制度/历史同样重要
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import random
random.seed(42); np.random.seed(42)


# ============================================================
# Part 1: 实现 Sugarscape
# ============================================================

class SugarScape:
    """简化版 Sugarscape —— Epstein-Axtell 1996"""
    
    def __init__(self, width=50, height=50, n_agents=250):
        self.W, self.H = width, height
        # 糖地形：两个糖峰
        self.sugar_capacity = self._make_terrain()
        self.sugar_current = self.sugar_capacity.copy()
        self.agents = []
        self._init_agents(n_agents)
        self.wealth_history = []  # 记录每回合的财富分布
        self.gini_history = []
    
    def _make_terrain(self):
        """造两个糖峰的地形"""
        x, y = np.meshgrid(np.arange(self.W), np.arange(self.H))
        # 糖峰 1
        peak1 = np.maximum(0, 4 - np.sqrt((x - 15)**2 + (y - 15)**2) / 3)
        # 糖峰 2
        peak2 = np.maximum(0, 4 - np.sqrt((x - 35)**2 + (y - 35)**2) / 3)
        capacity = np.maximum(peak1, peak2).astype(int)
        return capacity
    
    def _init_agents(self, n):
        """初始化 agents，所有属性随机均匀分布（公平起跑线）"""
        positions = random.sample([(i, j) for i in range(self.W) for j in range(self.H)], n)
        for pos in positions:
            self.agents.append({
                'pos': pos,
                'vision': random.randint(1, 6),     # 视野
                'metabolism': random.randint(1, 4),  # 代谢率
                'wealth': random.randint(5, 25),     # 初始财富
                'alive': True
            })
    
    def step(self):
        """一回合"""
        random.shuffle(self.agents)  # 随机顺序，避免位置偏好
        for a in self.agents:
            if not a['alive']:
                continue
            # 找视野内糖最多的格子
            best_pos = a['pos']
            best_sugar = self.sugar_current[a['pos'][1], a['pos'][0]]
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                for v in range(1, a['vision'] + 1):
                    nx, ny = a['pos'][0] + dx * v, a['pos'][1] + dy * v
                    if 0 <= nx < self.W and 0 <= ny < self.H:
                        # 检查是否被占
                        occupied = any(other['pos'] == (nx, ny) 
                                       for other in self.agents if other['alive'])
                        if not occupied and self.sugar_current[ny, nx] > best_sugar:
                            best_sugar = self.sugar_current[ny, nx]
                            best_pos = (nx, ny)
            # 移动
            a['pos'] = best_pos
            # 吃糖
            a['wealth'] += self.sugar_current[best_pos[1], best_pos[0]]
            self.sugar_current[best_pos[1], best_pos[0]] = 0
            # 代谢
            a['wealth'] -= a['metabolism']
            # 死亡判定
            if a['wealth'] < 0:
                a['alive'] = False
        
        # 糖再生
        self.sugar_current = np.minimum(self.sugar_current + 1, self.sugar_capacity)
        
        # 记录
        wealths = [a['wealth'] for a in self.agents if a['alive']]
        if wealths:
            self.wealth_history.append(wealths)
            self.gini_history.append(self._gini(wealths))
    
    @staticmethod
    def _gini(wealths):
        """计算基尼系数"""
        sorted_w = np.sort(wealths)
        n = len(sorted_w)
        cum = np.cumsum(sorted_w)
        return (n + 1 - 2 * np.sum(cum) / cum[-1]) / n
    
    def alive_count(self):
        return sum(1 for a in self.agents if a['alive'])


# ============================================================
# Part 2: 跑仿真
# ============================================================

print("=" * 70)
print("Part 2: Sugarscape 仿真")
print("=" * 70)

sim = SugarScape(width=50, height=50, n_agents=250)
print(f"  初始化：{len(sim.agents)} 个糖人")
print(f"  初始基尼系数：{sim._gini([a['wealth'] for a in sim.agents]):.3f}")

for step in range(150):
    sim.step()
    if step in [0, 10, 50, 100, 149]:
        alive = sim.alive_count()
        gini = sim.gini_history[-1] if sim.gini_history else 0
        wealths = [a['wealth'] for a in sim.agents if a['alive']]
        print(f"  第 {step+1:3d} 回合：存活 {alive:3d}，"
              f"基尼 {gini:.3f}，"
              f"max/min = {max(wealths)}/{min(wealths)}")

final_wealths = sim.wealth_history[-1]
print(f"\n  最终财富分布统计：")
print(f"    总财富：{sum(final_wealths)}")
print(f"    平均：{np.mean(final_wealths):.1f}")
print(f"    标准差：{np.std(final_wealths):.1f}")
print(f"    基尼：{sim._gini(final_wealths):.3f}")
print(f"    帕累托检验：top 20% 占总财富的 {sum(sorted(final_wealths)[int(len(final_wealths)*0.8):])/sum(final_wealths):.1%}")


# ============================================================
# Part 3: 可视化
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# 3a: 糖地形
ax = axes[0, 0]
im = ax.imshow(sim.sugar_capacity, cmap='YlOrRd', origin='lower')
ax.set_title('糖地形（两个糖峰）\n糖人争相去高糖区', fontsize=12)
plt.colorbar(im, ax=ax, label='糖容量')

# 3b: 财富分布演化
ax = axes[0, 1]
for i, step_idx in enumerate([0, 4, 24, 99, 149]):
    if step_idx < len(sim.wealth_history):
        wealths = sim.wealth_history[step_idx]
        ax.hist(wealths, bins=30, alpha=0.5, label=f'第 {step_idx+1} 回合', density=True)
ax.set_xlabel('财富', fontsize=11)
ax.set_ylabel('密度', fontsize=11)
ax.set_title('财富分布演化\n从均匀到幂律', fontsize=12)
ax.legend()
ax.set_xlim(-10, 200)
ax.grid(alpha=0.3)

# 3c: 基尼系数演化
ax = axes[1, 0]
ax.plot(sim.gini_history, color='#E74C3C', linewidth=2)
ax.axhline(0.5, color='gray', linestyle='--', alpha=0.5, label='基尼=0.5（高度不平等）')
ax.set_xlabel('回合', fontsize=11)
ax.set_ylabel('基尼系数', fontsize=11)
ax.set_title('基尼系数演化\n从 0.2 涨到 0.5+（不平等涌现）', fontsize=12)
ax.legend()
ax.grid(alpha=0.3)

# 3d: 最终财富分布 log-log
ax = axes[1, 1]
sorted_w = np.sort(final_wealths)[::-1]
ranks = np.arange(1, len(sorted_w) + 1)
ax.loglog(ranks, sorted_w, 'o', markersize=4, alpha=0.5, color='#27AE60')
ax.set_xlabel('排名（log）', fontsize=11)
ax.set_ylabel('财富（log）', fontsize=11)
ax.set_title('财富排名曲线（log-log）\n直线=幂律=帕累托分布', fontsize=12)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('02-sugarscape.png', dpi=100, bbox_inches='tight')
print(f"\n  图已保存：02-sugarscape.png")


# ============================================================
# Part 4: 反直觉的发现
# ============================================================

print("\n" + "=" * 70)
print("Part 4: 反直觉发现")
print("=" * 70)
print("""
Epstein-Axtell Sugarscape 揭示了三个反直觉真相：

1. **不平等从微观规则涌现**
   · 没有制度、没有歧视、没有剥削
   · 只有随机初始条件 + 简单局部规则
   · 但基尼系数从 0.2 涨到 0.5+
   · → "公平起跑线"不够，需要主动补偿机制

2. **生态位决定命运**
   · 出生在糖峰附近 → 一辈子富裕
   · 出生在沙漠 + 高代谢 → 早早饿死
   · → 不平等的根源是"位置 + 运气"
   · → "个人努力"的边际效应远小于"初始位置"

3. **死亡重新洗牌，但只洗一次**
   · 穷人死得早 → 财富分布看起来"平均一些"
   · 但这是统计假象：活着的人差距持续扩大
   · → 用"死亡率"作为均衡器是不道德的

政策含义：
  · Piketty 的 r > g（资本回报 > 增长）是制度层面
  · Sugarscape 是个体层面
  · 两者叠加 = 不平等的双重根源
""")

print("=" * 70)
print("✓ 02-sugarscape.py 跑通")
print("=" * 70)
print("推荐阅读：Epstein & Axtell《Growing Artificial Societies》")
