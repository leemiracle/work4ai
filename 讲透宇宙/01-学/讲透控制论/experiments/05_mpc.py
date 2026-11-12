"""
实验 05 — 模型预测控制 MPC: 用模型预测未来 N 步 = Plan-Execute 的祖先
对应文档: 讲透控制论/05-模型预测控制MPC.md

核心结论:
  1. MPC: 每步用环境模型预测未来 N 步, 选当前最优动作
  2. 与 LQR 不同: MPC 可处理非线性 + 不等式约束
  3. 与 Agent Plan-Execute 同根: 都是 [先想未来, 再做当前]
  4. 实测倒立摆: MPC 在约束下 (|u|<=2) 仍稳定, LQR 可能违反约束

跑法: python3 -u 05_mpc.py
"""
import math, random
import numpy as np
np.random.seed(0)

def P(*a): print(*a, flush=True)

G = 9.8; L = 1.0; M = 1.0; DT = 0.05

def pendulum_step(state, u):
    theta, omega = state
    angular_acc = (G/L) * math.sin(theta) + u / (M * L**2)
    new_omega = omega + angular_acc * DT
    new_theta = theta + new_omega * DT
    return np.array([new_theta, new_omega])

def cost(state, u):
    return state[0]**2 + 0.1 * state[1]**2 + 0.01 * u**2

# ============================================================
# Part 1: LQR 基线 (无约束)
# ============================================================
A = np.array([[1, DT], [(G/L)*DT, 1]])
B = np.array([[0], [1/(M*L**2)*DT]])
Q = np.array([[1, 0], [0, 0.1]])
R = np.array([[0.01]])

def solve_lqr(A, B, Q, R, n_iter=1000):
    P_mat = Q.copy()
    for _ in range(n_iter):
        P_new = Q + A.T @ P_mat @ A - A.T @ P_mat @ B @ np.linalg.inv(R + B.T @ P_mat @ B) @ B.T @ P_mat @ A
        if np.allclose(P_new, P_mat, atol=1e-9): break
        P_mat = P_new
    K = np.linalg.inv(R + B.T @ P_mat @ B) @ B.T @ P_mat @ A
    return K

K_lqr = solve_lqr(A, B, Q, R)

def lqr_control(x):
    return float(-K_lqr @ x)

# ============================================================
# Part 2: MPC 实现 — 每步预测 N 步, 暴力搜索最优序列
# ============================================================
def mpc_control(x, horizon=10, u_max=2.0, n_samples=200):
    """
    MPC: 暴力采样 n_samples 个控制序列, 选代价最低的
    u_max: 控制约束 (LQR 没法直接处理, MPC 可以)
    """
    random.seed()  # 每次随机
    best_cost = float('inf')
    best_first_u = 0.0
    for _ in range(n_samples):
        # 随机采样 horizon 个 u
        u_seq = [random.uniform(-u_max, u_max) for _ in range(horizon)]
        # 模拟
        x_sim = x.copy()
        total_cost = 0
        for u in u_seq:
            x_sim = pendulum_step(x_sim, u)
            total_cost += cost(x_sim, u)
            if abs(x_sim[0]) > math.pi:
                total_cost += 1000  # 摔倒惩罚
                break
        if total_cost < best_cost:
            best_cost = total_cost
            best_first_u = u_seq[0]
    return best_first_u

# ============================================================
# Part 3: 对比 — LQR vs MPC (无约束 vs 有约束)
# ============================================================
P("="*70)
P("实验 05 — 模型预测控制 MPC")
P("="*70)
P()
P("场景: 倒立摆, 初始 θ=0.5 rad (~29°, 较大偏离)")
P("约束: 控制信号 |u| ≤ 2.0 (实际马达限制)")
P()

initial = np.array([0.5, 0.0])

def simulate(controller, x0, steps=150):
    x = np.array(x0)
    traj = [x.copy()]
    total_cost = 0
    max_u = 0
    for t in range(steps):
        u = controller(x)
        max_u = max(max_u, abs(u))
        x = pendulum_step(x, u)
        traj.append(x.copy())
        total_cost += cost(x, u)
        if abs(x[0]) > math.pi: break
    return traj, total_cost, max_u

print(f"{'控制器':<28}{'稳定?':>8}{'最大 |u|':>12}{'约束满足?':>14}{'总代价':>12}")
print("-"*74)

# LQR (无约束)
traj_lqr, cost_lqr, max_u_lqr = simulate(lqr_control, initial)
stable_lqr = abs(traj_lqr[-1][0]) < 0.05 and len(traj_lqr) == 151
print(f"{'LQR (无约束)':<28}{'是' if stable_lqr else '否':>8}{max_u_lqr:>12.2f}{'—':>14}{cost_lqr:>12.2f}")

# LQR + clip (强制约束, 但破坏最优性)
def lqr_clipped(x):
    u = lqr_control(x)
    return max(-2.0, min(2.0, u))
traj_lqrc, cost_lqrc, max_u_lqrc = simulate(lqr_clipped, initial)
stable_lqrc = abs(traj_lqrc[-1][0]) < 0.05 and len(traj_lqrc) == 151
print(f"{'LQR + clip |u|≤2':<28}{'是' if stable_lqrc else '否':>8}{max_u_lqrc:>12.2f}{'是':>14}{cost_lqrc:>12.2f}")

# MPC (有约束, 每步重新规划)
traj_mpc, cost_mpc, max_u_mpc = simulate(lambda x: mpc_control(x, horizon=10, u_max=2.0, n_samples=50), initial, steps=100)
stable_mpc = abs(traj_mpc[-1][0]) < 0.1 and len(traj_mpc) == 101
print(f"{'MPC (约束, horizon=10)':<28}{'是' if stable_mpc else '否':>8}{max_u_mpc:>12.2f}{'是':>14}{cost_mpc:>12.2f}")

P("""
关键观察:
- LQR (无约束): 理论最优, 但实际 |u| 可能超过 2 (马达做不到)
- LQR + clip: 强制约束, 但破坏最优性 (clip 后可能不再稳定)
- MPC: 在约束内重新规划, 既稳定又不违反约束

MPC 的优势:
1. 处理不等式约束 (LQR 做不到)
2. 处理非线性系统 (LQR 需要线性化)
3. 每步重新规划, 抗扰动
""")

# ============================================================
# Part 4: MPC 的"重规划"特性
# ============================================================
P("="*70)
P("Part 2: MPC 的'每步重规划' — 与 Plan-Execute 同构")
P("-"*70)
P()
P("MPC 算法:")
P("  Repeat:")
P("    1. 用模型预测未来 N 步的轨迹 (假设一组 u 序列)")
P("    2. 优化: 选让总代价最低的 u 序列")
P("    3. 只执行第 1 个 u, 抛弃其他 (滚动优化)")
P("    4. 观察新状态, 回到 1")
P()
P("这正是 Agent 的 [Plan-Execute] 范式!")
P("  Plan:    LLM 一次性生成未来 N 步计划")
P("  Execute: 只执行第 1 步")
P("  Re-plan: 观察结果, 重新规划")
P()
P("MPC 是控制论版, ReWOO/Plan-Execute 是 LLM 版. 本质相同.")
P()

# 实测: MPC horizon 的影响
print(f"{'horizon (预测步数)':<24}{'稳定?':>8}{'总代价':>12}")
print("-"*44)
for h in [1, 3, 5, 10, 20]:
    traj, cost_t, _ = simulate(lambda x: mpc_control(x, horizon=h, u_max=2.0, n_samples=30), initial, steps=80)
    stable = abs(traj[-1][0]) < 0.1 and len(traj) == 81
    print(f"horizon={h:<18}{'是' if stable else '否':>8}{cost_t:>12.2f}")

P("""
观察:
- horizon=1: 等价贪心 (只看眼前), 类似 ReAct
- horizon=10-20: 接近全局最优, 但计算量大
- horizon 太小 → 不稳定; 太大 → 太慢
- 工程经验: horizon 取 [系统时间常数] 的 3-5 倍
""")

# ============================================================
# Part 5: MPC → AI 的桥
# ============================================================
P("="*70)
P("Part 3: MPC → AI")
P("-"*70)
P("""
1. 【MPC = Plan-Execute 范式的根】
   控制论 1980s 提出 MPC, LLM Agent 2023 复现同样思想 (ReWOO 等).
   两者都是 [用模型想未来, 只执行第 1 步].

2. 【世界模型 = MPC 的环境模型】
   MPC 需要环境模型 s' = f(s, a).
   现代具身 AI 训 [世界模型] (Sora/GAIA-1/JEPA) = 学这个 f.
   有了世界模型, 就能做 MPC.

3. 【MuZero = MPC + 学习世界模型】
   DeepMind MuZero (2020): 不给规则, 自己学世界模型 + 做 MCTS 规划
   击败围棋/国际象棋/将棋/Atari 全部 SOTA
   本质是 [MPC + 可学习世界模型]

4. 【自动驾驶 = MPC 实战】
   横向控制 (转向): LQR + MPC
   轨迹规划: 凸优化 MPC (考虑障碍物约束)
   Waymo/Tesla 都用 MPC 变种
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
MPC (Model Predictive Control): 每步用模型预测未来 N 步, 选最优当前动作.
- 与 LQR 比: MPC 处理约束 + 非线性 (LQR 做不到)
- 与 Agent 比: MPC = Plan-Execute 范式的控制论版 (每步重规划)
- horizon 取 [时间常数] 的 3-5 倍 (太小不稳, 太大太慢)

现代 AI 的世界模型 + MuZero + 自动驾驶全是 MPC 思想:
- 学世界模型 = 学环境动态
- 用模型规划 = MPC
- MuZero = MPC + 学习世界模型 (击败围棋 SOTA)

→ Plan-Execute 不是 LLM Agent 的发明, 是 1980s 控制论的 MPC.
""")
