"""
UC Berkeley EECS — 杂项微项目集（deCal / 入门 / 专题）
覆盖：CS 198 deCal / CS 9K / Data 6 / CS 188 Pacman 进阶 / CS M11 / Stat 154 / EE 127 App / CS 191 Quantum / CS 198-126 / CS 198-127
"""
import math
import random
from collections import Counter, defaultdict


# ============ CS 198 deCal：Python 入门 ============

def cs198_python_basics():
    """CS198 deCal: Python 基础"""
    print("\n📋 CS198 deCal: Python 基础（列表推导 vs 循环）")
    # 列表推导 vs for 循环
    squares_loop = []
    for i in range(10):
        squares_loop.append(i ** 2)
    squares_comp = [i ** 2 for i in range(10)]
    assert squares_loop == squares_comp
    print(f"   [i² for i in range(10)] = {squares_comp}")
    # 带条件
    evens = [i for i in range(20) if i % 2 == 0]
    print(f"   [i for i if i%2==0] = {evens}")
    # dict comprehension
    square_map = {i: i ** 2 for i in range(5)}
    print(f"   {{i: i²}} = {square_map}")


# ============ CS 9K Python：递归 ============

def cs9k_recursion():
    """CS9K: 递归（汉诺塔）"""
    print("\n📋 CS9K: 汉诺塔递归")
    moves = []
    def hanoi(n, src, aux, dst):
        if n == 1:
            moves.append((src, dst))
            return
        hanoi(n - 1, src, dst, aux)
        moves.append((src, dst))
        hanoi(n - 1, aux, src, dst)
    hanoi(3, "A", "B", "C")
    print(f"   3 层汉诺塔 {len(moves)} 步（=2³-1）:")
    for i, (s, d) in enumerate(moves):
        print(f"     {i+1}: {s} → {d}")


# ============ Data 6：抽样 ============

def data6_sampling():
    """Data 6: 简单随机抽样 vs 分层抽样"""
    print("\n📋 Data 6: 抽样方法")
    random.seed(42)
    # 总体 1000 学生
    population = [("CS", random.gauss(85, 5)) for _ in range(600)] + \
                 [("EE", random.gauss(82, 5)) for _ in range(400)]
    # 简单随机抽样
    srs = random.sample(population, 100)
    srs_mean = sum(x[1] for x in srs) / len(srs)
    # 分层抽样
    cs_sample = random.sample([p for p in population if p[0] == "CS"], 60)
    ee_sample = random.sample([p for p in population if p[0] == "EE"], 40)
    strat_mean = (sum(x[1] for x in cs_sample) + sum(x[1] for x in ee_sample)) / 100
    true_mean = sum(x[1] for x in population) / len(population)
    print(f"   真实均值: {true_mean:.2f}")
    print(f"   简单随机抽样均值: {srs_mean:.2f} (误差 {abs(srs_mean-true_mean):.3f})")
    print(f"   分层抽样均值: {strat_mean:.2f} (误差 {abs(strat_mean-true_mean):.3f})")
    print(f"   → 分层抽样通常方差更小")


# ============ CS 188 Pacman 进阶：期望最大搜索 ============

def cs188_expectimax():
    """CS188 进阶: Expectimax（随机 Ghost）"""
    print("\n📋 CS188 进阶: Expectimax")
    # 博弈树: MAX 节点取 max, CHANCE 节点取期望
    tree = {
        "type": "MAX",
        "children": [
            {"type": "CHANCE", "probs": [0.5, 0.5],
             "children": [{"value": 10}, {"value": 2}]},
            {"type": "CHANCE", "probs": [0.5, 0.5],
             "children": [{"value": 8}, {"value": 4}]},
        ],
    }
    def expectimax(node):
        if "value" in node:
            return node["value"]
        if node["type"] == "MAX":
            return max(expectimax(c) for c in node["children"])
        # CHANCE
        return sum(p * expectimax(c) for p, c in zip(node["probs"], node["children"]))
    val = expectimax(tree)
    print(f"   Expectimax 值: {val}")
    print(f"   左分支期望: {0.5*10+0.5*2}=6, 右分支期望: {0.5*8+0.5*4}=6")
    print(f"   MAX 选 max(6,6) = 6")
    print(f"   vs Minimax 会假设 Ghost 最优 → 保守策略")


# ============ CS M11 Cognition：ACT-R 产生式 ============

def csm11_actr():
    """CS M11: ACT-R 认知架构（产生式规则）"""
    print("\n📋 CS M11: ACT-R 产生式（加法回忆）")
    productions = [
        ("IF goal=add AND arg1=N AND arg2=0 THEN result=N", "加 0 规则"),
        ("IF goal=add AND arg1=N AND arg2=M THEN retrieve N+M", "检索规则"),
        ("IF retrieved=X THEN result=X AND done=True", "完成规则"),
    ]
    for rule, desc in productions:
        print(f"   {desc}: {rule}")
    print("   ACT-R 用产生式 + 声明性记忆模拟人类认知。")


# ============ Stat 154：k-NN 分类 ============

def stat154_knn():
    """Stat 154: k-NN"""
    print("\n📋 Stat 154: k-NN 分类")
    train = [(1, 1, "A"), (2, 1, "A"), (3, 2, "A"),
             (6, 5, "B"), (7, 6, "B"), (8, 5, "B")]
    test = (4, 3)
    for k in [1, 3, 5]:
        dists = sorted([(math.sqrt((t[0]-test[0])**2+(t[1]-test[1])**2), t[2]) for t in train])
        neighbors = [d[1] for d in dists[:k]]
        counts = Counter(neighbors)
        pred = counts.most_common(1)[0][0]
        print(f"   k={k}, test={test} → 预测: {pred} (邻居: {neighbors})")


# ============ EE 127 App：线性规划应用 ============

def ee127_app_diet():
    """EE 127 App: 饮食问题 LP"""
    print("\n📋 EE 127 App: 饮食问题（LP 建模）")
    # min cost = 2x + 3y  s.t. 3x + y ≥ 8 (protein), x + 2y ≥ 6 (vitamin)
    print("   目标: min 2x + 3y  (食物成本)")
    print("   约束: 3x + y ≥ 8  (蛋白质 ≥ 8)")
    print("         x + 2y ≥ 6  (维生素 ≥ 6)")
    # 顶点枚举
    vertices = [(8/3, 0), (0, 8), (6, 0), (0, 3)]
    feasible = []
    for x, y in vertices:
        if 3*x + y >= 8 - 0.01 and x + 2*y >= 6 - 0.01:
            feasible.append((x, y, 2*x + 3*y))
    best = min(feasible, key=lambda v: v[2])
    print(f"   可行顶点: {feasible}")
    print(f"   最优: x={best[0]:.2f}, y={best[1]:.2f}, cost={best[2]:.2f}")


# ============ CS 191 Quantum：Bell 态 ============

def cs191_bell_state():
    """CS191: Bell 态（量子纠缠）"""
    print("\n📋 CS191: Bell 态 |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
    import cmath
    # Bell 态: |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
    # 测量：00 和 11 各 50%
    state = {"00": 1/math.sqrt(2), "11": 1/math.sqrt(2)}
    print(f"   概率振幅: {state}")
    print(f"   P(00) = {abs(state['00'])**2:.2f}")
    print(f"   P(11) = {abs(state['11'])**2:.2f}")
    # 纠缠：测量第一个 qubit → 第二个立即确定
    print("   纠缠性: 测得 qubit1=0 → qubit2 必为 0（瞬时关联）")
    # CHSH 不等式违反
    print("   Bell/CHSH 实验证明: |S| > 2 → 经典定域隐变量理论被否证")


# ============ CS 198-126 Rails deCal：MVC ============

def cs198_126_mvc():
    """CS198-126: Rails MVC 模式"""
    print("\n📋 CS198-126: MVC 架构（Rails 风格）")
    print("""
   Model-View-Controller:
   ┌─────────┐    ┌──────────┐    ┌─────────┐
   │  View   │ ←→ │   User   │ ←→ │Controler│
   │ (HTML)  │    │ (Browser)│    │(routes) │
   └─────────┘    └──────────┘    └────┬────┘
                                         │
                                    ┌────┴────┐
                                    │  Model  │
                                    │ (DB/ORM)│
                                    └─────────┘
   RESTful: GET /posts → index
            POST /posts → create
            PATCH /posts/:id → update
   """)


# ============ CS 198-127 ML deCal：K-means 可视化 ============

def cs198_127_kmeans():
    """CS198-127: K-means 从零"""
    print("\n📋 CS198-127: K-means 聚类")
    random.seed(42)
    data = [(random.gauss(0, 1), random.gauss(0, 1)) for _ in range(30)] + \
           [(random.gauss(5, 1), random.gauss(5, 1)) for _ in range(30)]
    k = 2
    centers = [data[random.randint(0, 59)], data[random.randint(0, 59)]]
    for iteration in range(10):
        clusters = defaultdict(list)
        for p in data:
            best = min(range(k), key=lambda i: (p[0]-centers[i][0])**2 + (p[1]-centers[i][1])**2)
            clusters[best].append(p)
        new_centers = []
        for i in range(k):
            if clusters[i]:
                cx = sum(p[0] for p in clusters[i]) / len(clusters[i])
                cy = sum(p[1] for p in clusters[i]) / len(clusters[i])
                new_centers.append((cx, cy))
            else:
                new_centers.append(centers[i])
        if new_centers == centers:
            break
        centers = new_centers
    print(f"   60 点 → 2 簇, {iteration+1} 次迭代收敛")
    print(f"   簇中心: {[(round(c[0],2), round(c[1],2)) for c in centers]}")
    print(f"   簇大小: {[len(v) for v in clusters.values()]}")


# ============ 主入口 ============

def run_all_micro():
    print("=" * 60)
    print("🎓 UC Berkeley EECS 杂项微项目（deCal / 入门 / 专题）")
    print("=" * 60)
    cs198_python_basics()
    cs9k_recursion()
    data6_sampling()
    cs188_expectimax()
    csm11_actr()
    stat154_knn()
    ee127_app_diet()
    cs191_bell_state()
    cs198_126_mvc()
    cs198_127_kmeans()
    print("\n" + "=" * 60)
    print("✅ 全部杂项微项目完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_micro()
