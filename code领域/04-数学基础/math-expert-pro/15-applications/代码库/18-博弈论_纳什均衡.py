"""
博弈论：纳什均衡与演化博弈动力学
================================
数学概念：博弈论 / 纳什均衡 / 囚徒困境 / 混合策略 / 复制器方程 / 演化稳定策略
应用领域：经济学 / 生物学 / AI（多智能体）/ 政治学 / 密码学
核心思想：博弈论研究理性决策者之间的策略互动。
  纳什均衡：没有玩家能通过单方面改变策略来获益（互锁状态）
  囚徒困境：个体理性导致集体非理性（合作 vs 背叛）
  混合策略：以概率混合多种行动 → 纳什证明所有有限博弈都有混合均衡
  复制器方程：dx_i/dt = x_i[f_i(x) - φ(x)]（策略频率的演化）
  演化稳定策略（ESS）：种群中无法被突变策略入侵的策略
运行方式：python "18-博弈论_纳什均衡.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import itertools

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 博弈论基础 ============

def find_nash_equilibria(payoff_A, payoff_B):
    """寻找 2×2 双矩阵博弈的纯策略纳什均衡。
    payoff_A, payoff_B: 行玩家/列玩家的收益矩阵
    返回：纯策略纳什均衡列表
    """
    n_rows, n_cols = payoff_A.shape
    equilibria = []

    for i, j in itertools.product(range(n_rows), range(n_cols)):
        # 检查行玩家是否想改变
        row_best = all(payoff_A[i, j] >= payoff_A[i2, j] for i2 in range(n_rows))
        # 检查列玩家是否想改变
        col_best = all(payoff_B[i, j] >= payoff_B[i, j2] for j2 in range(n_cols))

        if row_best and col_best:
            equilibria.append((i, j))

    return equilibria


def mixed_strategy_nash_2x2(payoff_A, payoff_B):
    """计算 2×2 博弈的混合策略纳什均衡。
    返回：行玩家混合概率 p（选第一行的概率），列玩家混合概率 q
    """
    a, b = payoff_A[0]  # 行玩家选行0时的收益
    c, d = payoff_A[1]  # 行玩家选行1时的收益
    e, f = payoff_B[:, 0]  # 列玩家选列0时的收益
    g, h = payoff_B[:, 1]  # 列玩家选列1时的收益

    # 行玩家使列玩家无差异：q*b + (1-q)*a = q*d + (1-q)*c
    # 列玩家使行玩家无差异：p*e + (1-p)*g = p*f + (1-p)*h
    denom_q = (b - a - d + c)
    denom_p = (e - f - g + h)

    p = (h - g) / denom_p if abs(denom_p) > 1e-10 else 0.5
    q = (a - c) / denom_q if abs(denom_q) > 1e-10 else 0.5

    p = np.clip(p, 0, 1)
    q = np.clip(q, 0, 1)
    return p, q


# ============ 2. 演化博弈（复制器动力学）============

def replicator_dynamics(payoff_matrix, x0, t_max=20, dt=0.01):
    """复制器方程：dx_i/dt = x_i[f_i(x) - φ(x)]
    payoff_matrix: n×n 收益矩阵（对称博弈）
    x0: 初始策略频率向量
    返回：t, X（时间，频率矩阵）
    """
    n = len(x0)
    t = np.arange(0, t_max, dt)
    X = np.zeros((len(t), n))
    X[0] = x0

    for k in range(len(t) - 1):
        x = X[k]
        fitness = payoff_matrix @ x  # 各策略的适应度
        avg_fitness = x @ fitness      # 平均适应度 φ(x)
        dx = x * (fitness - avg_fitness)
        X[k + 1] = np.clip(x + dt * dx, 0, 1)
        X[k + 1] /= X[k + 1].sum()  # 归一化

    return t, X


# ============ 3. 经典博弈定义 ============

# 囚徒困境
PD_A = np.array([[-1, -3],    # 行：沉默/背叛；列：沉默/背叛
                  [0, -2]])    # 收益（负的刑期年数）
PD_B = np.array([[-1, 0],
                  [-3, -2]])

# 协调博弈（开车左/右）
COOR_A = np.array([[1, 0],
                    [0, 1]])
COOR_B = np.array([[1, 0],
                    [0, 1]])

# 鹰鸽博弈（Hawk-Dove）
HD_A = np.array([[-0.5, 2],    # 鹰/鸽 vs 鹰/鸽
                  [0, 1]])
HD_B = np.array([[-0.5, 0],
                  [2, 1]])


# ============ 4. 实验 ============

def main():
    print("=" * 60)
    print("实验 1：囚徒困境——个体理性导致集体非理性")
    print("=" * 60)

    equilibria_pd = find_nash_equilibria(PD_A, PD_B)
    p_pd, q_pd = mixed_strategy_nash_2x2(PD_A, PD_B)

    print("囚徒困境收益矩阵（收益=刑期年数的负数）：")
    print(f"         沉默    背叛")
    print(f"沉默  ({PD_A[0,0]:+.0f},{PD_B[0,0]:+.0f})  ({PD_A[0,1]:+.0f},{PD_B[0,1]:+.0f})")
    print(f"背叛  ({PD_A[1,0]:+.0f},{PD_B[1,0]:+.0f})  ({PD_A[1,1]:+.0f},{PD_B[1,1]:+.0f})")
    print(f"\n纯策略纳什均衡: {['沉默','背叛'][equilibria_pd[0][0]]}/{['沉默','背叛'][equilibria_pd[0][1]]}")
    print(f"→ （背叛，背叛）是唯一均衡，但双方沉默收益更高！")
    print(f"\n[解读] 这就是'困境'——理性个体选择互相背叛（各判2年），")
    print(f"       而合作（互相沉默）各判1年。个体理性 ≠ 集体最优。")

    print("\n" + "=" * 60)
    print("实验 2：协调博弈——多均衡的博弈")
    print("=" * 60)

    equilibria_coor = find_nash_equilibria(COOR_A, COOR_B)
    print(f"协调博弈（靠左走/靠右走）：")
    print(f"纯策略纳什均衡: {len(equilibria_coor)} 个")
    for eq in equilibria_coor:
        side = ['左', '右']
        print(f"  ({side[eq[0]]},{side[eq[1]]}) → 收益各 1")

    print(f"\n[解读] 多个均衡中选哪个？这是博弈论的核心难题。")
    print(f"       聚焦点（Schelling）、沟通、文化惯例帮助选择。")

    print("\n" + "=" * 60)
    print("实验 3：鹰鸽博弈——演化稳定策略（ESS）")
    print("=" * 60)

    # 鹰鸽博弈的复制器动力学
    # 资源 V=2，打斗成本 C=4 → 鹰鸽收益矩阵
    V, C = 2, 4
    HD_payoff = np.array([
        [(V - C) / 2, V],     # 鹰 vs 鹰 / 鹰 vs 鸽
        [0, V / 2]             # 鸽 vs 鹰 / 鸽 vs 鸽
    ])

    print(f"鹰鸽博弈（资源 V={V}, 打斗成本 C={C}）：")
    print(f"       鹰        鸽")
    print(f"鹰  ({HD_payoff[0,0]:+.1f}  )  ({HD_payoff[0,1]:.1f})")
    print(f"鸽  ({HD_payoff[1,0]:.1f}  )  ({HD_payoff[1,1]:.1f})")

    # ESS：鹰的比例 x* = V/C
    x_ess = V / C
    print(f"\n演化稳定策略（ESS）：鹰的比例 x* = V/C = {x_ess:.2f}")
    print(f"  当 x < {x_ess}：鹰有优势（资源 > 成本期望）→ x 增加")
    print(f"  当 x > {x_ess}：鸽有优势（打斗成本太高）→ x 减少")
    print(f"  x* = {x_ess} 是稳定平衡")

    # 演化动力学
    x0_values = [0.1, 0.3, x_ess, 0.7, 0.9]
    print(f"\n复制器动力学模拟（不同初始频率）：")
    for x0 in x0_values:
        x0_vec = np.array([x0, 1 - x0])
        t, X = replicator_dynamics(HD_payoff, x0_vec, t_max=30)
        x_final = X[-1, 0]
        direction = "→↑" if x_final > x0 + 0.01 else "→↓" if x_final < x0 - 0.01 else "→="
        print(f"  x₀={x0:.1f} → x_final={x_final:.3f} {direction}")

    print(f"\n[解读] 演化博弈解释了为什么自然界存在'有限攻击'而非'不死不休'。")
    print(f"       ESS = 进化的稳定终点——'适者'不一定是'最强者'。")

    print("\n" + "=" * 60)
    print("实验 4：石头剪刀布——循环博弈与极限环")
    print("=" * 60)

    RPS_payoff = np.array([
        [0, -1, 1],    # 石头
        [1, 0, -1],    # 布
        [-1, 1, 0]     # 剪刀
    ], dtype=float)

    # 简单 RPS（零和）
    x0_rps = np.array([0.5, 0.3, 0.2])
    t_rps, X_rps = replicator_dynamics(RPS_payoff, x0_rps, t_max=50)

    print(f"石头剪刀布：")
    print(f"初始策略频率: 石头={x0_rps[0]:.1f} 布={x0_rps[1]:.1f} 剪刀={x0_rps[2]:.1f}")
    print(f"最终策略频率: 石头={X_rps[-1,0]:.3f} 布={X_rps[-1,1]:.3f} 剪刀={X_rps[-1,2]:.3f}")
    print(f"ESS = 均匀混合 (1/3, 1/3, 1/3)")
    print(f"\n[解读] RPS 的复制器动力学是'循环'——不会收敛，而是周期性振荡。")
    print(f"       这对应现实中的'生态循环'（如捕食者-猎物数量振荡）。")

    # ============ 5. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：囚徒困境收益矩阵可视化
    ax = axes[0, 0]
    im = ax.imshow(PD_A, cmap='RdYlGn', vmin=-3, vmax=0)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{PD_A[i,j]:+.0f}", ha='center', va='center', fontsize=16, fontweight='bold')
    ax.set_xticks([0, 1]); ax.set_xticklabels(['沉默', '背叛'])
    ax.set_yticks([0, 1]); ax.set_yticklabels(['沉默', '背叛'])
    ax.set_title('囚徒困境收益（行玩家）\n均衡=(背叛,背叛) 但合作更优')
    plt.colorbar(im, ax=ax)

    # 图 2：鹰鸽博弈复制器动力学
    ax = axes[0, 1]
    for x0_h in [0.05, 0.2, 0.4, x_ess, 0.7, 0.95]:
        x0_vec = np.array([x0_h, 1 - x0_h])
        t_h, X_h = replicator_dynamics(HD_payoff, x0_vec, t_max=30)
        ax.plot(t_h, X_h[:, 0], lw=1.5, alpha=0.7, label=f'x₀={x0_h:.2f}')
    ax.axhline(x_ess, color='red', ls='--', lw=2, label=f'ESS x*={x_ess:.2f}')
    ax.set_xlabel('时间')
    ax.set_ylabel('鹰的比例 x(t)')
    ax.set_title('鹰鸽博弈演化动力学（所有轨迹→ESS）')
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)

    # 图 3：RPS 复制器动力学（3D 相空间投影）
    ax = axes[1, 0]
    ax.plot(t_rps, X_rps[:, 0], 'r-', lw=1.5, label='石头')
    ax.plot(t_rps, X_rps[:, 1], 'g-', lw=1.5, label='布')
    ax.plot(t_rps, X_rps[:, 2], 'b-', lw=1.5, label='剪刀')
    ax.axhline(1/3, color='gray', ls=':', alpha=0.5)
    ax.set_xlabel('时间')
    ax.set_ylabel('策略频率')
    ax.set_title('石头剪刀布：循环振荡（不收敛）')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 4：RPS 三角相图
    ax = axes[1, 1]
    # 三角形坐标
    from matplotlib.patches import Polygon
    triangle = Polygon([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]], fill=False, edgecolor='black')
    ax.add_patch(triangle)
    # 轨迹
    x_tri = X_rps[:, 1] + 0.5 * X_rps[:, 2]
    y_tri = (np.sqrt(3) / 2) * X_rps[:, 2]
    ax.plot(x_tri, y_tri, 'b-', lw=1.5)
    ax.plot(x_tri[0], y_tri[0], 'go', markersize=10, label='起点')
    ax.plot(1/3 + 0.5/3, np.sqrt(3)/6, 'r*', markersize=15, label='均衡(1/3,1/3,1/3)')
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.0)
    ax.text(-0.05, -0.03, '石头', ha='center', fontsize=10)
    ax.text(1.05, -0.03, '布', ha='center', fontsize=10)
    ax.text(0.5, 0.95, '剪刀', ha='center', fontsize=10)
    ax.set_title('RPS 三角相图（循环轨迹）')
    ax.legend(fontsize=8)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig("18-博弈论_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 18-博弈论_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 纳什均衡：互锁状态（没人能单方面获益）")
    print("2. 囚徒困境：个体理性 → 集体非理性（合作 vs 背叛）")
    print("3. 混合策略：概率混合 → 所有有限博弈都有均衡（Nash 1950）")
    print("4. ESS：演化稳定策略 = 进化的纳什均衡")
    print("5. 复制器方程：策略频率的演化动力学")
    print("\n[解读] 博弈论是'理性互动的数学'——")
    print("       从拍卖设计到多智能体 AI 到演化生物学，")
    print("       纳什均衡是理解'多个决策者互相影响'的通用框架。")
    print("       AlphaStar/OpenAI Five 训练多智能体博弈用的就是这套理论。")


if __name__ == "__main__":
    main()
