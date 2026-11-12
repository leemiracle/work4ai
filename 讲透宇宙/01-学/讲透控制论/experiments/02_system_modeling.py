"""
实验 02 — 系统建模: 传递函数 / 状态空间 / 一阶 vs 二阶响应
对应文档: 讲透控制论/02-系统建模.md

核心结论:
  1. 一阶系统: T(t+1) = a*T + b*u, 响应无超调, 时间常数 τ = 1/(1-a)
  2. 二阶系统: 有阻尼比 ζ, ζ<1 欠阻尼(振荡), ζ=1 临界, ζ>1 过阻尼
  3. 状态空间: x(t+1) = A*x + B*u, 通用描述任意阶系统
  4. 阶跃响应: 看上升时间/超调/稳态值, 评估系统性能

跑法: python3 -u 02_system_modeling.py
"""
import math, statistics
def P(*a): print(*a, flush=True)

P("="*70)
P("实验 02 — 系统建模: 传递函数 / 状态空间 / 阶跃响应")
P("="*70)
P()

# ============================================================
# Part 1: 一阶系统 — 房间加热
# ============================================================
P("Part 1: 一阶系统 — τ·dT/dt + T = K·u")
P("-"*70)
P("  物理意义: 房间加热, T 趋向 (K*u + 外温), 时间常数 τ 决定响应快慢")
P()

def first_order_step(K, tau, target, T0=0.0, steps=50):
    """一阶系统阶跃响应. K=增益, tau=时间常数"""
    T = T0
    traj = []
    for t in range(steps):
        # 离散化: T(t+1) = T + dt/τ * (K*u - T)
        dt = 1.0
        T = T + dt/tau * (K*target - T)
        traj.append(T)
    return traj

print(f"{'τ (时间常数)':<16}{'63% 达到时间':>16}{'95% 达到时间':>16}{'稳态值':>10}")
print("-"*58)
for tau in [1, 2, 5, 10, 20]:
    traj = first_order_step(K=1.0, tau=tau, target=22.0, steps=200)
    # 找到 63% 和 95% 时间
    target = 22.0
    t63 = next((i for i, t in enumerate(traj) if t > 0.63*target), len(traj))
    t95 = next((i for i, t in enumerate(traj) if t > 0.95*target), len(traj))
    steady = traj[-1]
    print(f"{tau:<16}{t63:>16}{t95:>16}{steady:>10.2f}")

P("""
关键性质:
- 63% 达到时间 ≈ τ (一阶系统的定义性质)
- 95% 达到时间 ≈ 3τ
- 稳态值 = K * target (增益 * 输入)
- τ 越大响应越慢, 但永远不超调 (一阶系统的优点)
""")

# ============================================================
# Part 2: 二阶系统 — 弹簧+阻尼 / 倒立摆
# ============================================================
P("="*70)
P("Part 2: 二阶系统 — 阻尼比 ζ 决定是否振荡")
P("-"*70)
P()
P("  ··· + 2ζω_n · dx/dt + ω_n² · x = ω_n² · u")
P("  ζ = 阻尼比, ω_n = 自然频率")
P()

def second_order_step(zeta, wn, target, x0=0.0, v0=0.0, steps=100, dt=0.1):
    """二阶系统阶跃响应"""
    x, v = x0, v0
    traj = []
    for t in range(steps):
        # 离散: a = ω_n² (target - x) - 2ζω_n * v
        a = wn**2 * (target - x) - 2*zeta*wn*v
        v = v + a * dt
        x = x + v * dt
        traj.append(x)
    return traj

print(f"{'ζ':<8}{'性质':<14}{'最大超调':>12}{'达到稳态时间':>14}")
print("-"*48)
for zeta, name in [(0.1, "极欠阻尼"),
                    (0.3, "欠阻尼"),
                    (0.5, "适中"),
                    (0.7, "工程最优"),
                    (1.0, "临界阻尼"),
                    (2.0, "过阻尼")]:
    traj = second_order_step(zeta, wn=1.0, target=1.0, steps=500, dt=0.1)
    target = 1.0
    max_x = max(traj)
    overshoot = max(0, max_x - target)
    # 稳态时间: 最后 50 步都在 ±5% 内
    t_steady = next((i for i in range(len(traj)-50) if all(abs(traj[j]-target)<0.05 for j in range(i, i+50))), len(traj))
    print(f"{zeta:<8.1f}{name:<14}{overshoot:>12.4f}{t_steady:>14}")

P("""
关键观察:
- ζ < 1: 欠阻尼, 系统振荡 (反弹几下才稳定)
- ζ = 0.7: 工程最优 (轻微超调, 快速稳定)
- ζ = 1: 临界阻尼 (不振荡, 最快达到稳态)
- ζ > 1: 过阻尼 (慢但稳定, 不振荡)

工程经验: 设计控制让 ζ ≈ 0.7 (最佳超调-速度权衡)
""")

# ============================================================
# Part 3: 状态空间 — 通用建模
# ============================================================
P("="*70)
P("Part 3: 状态空间 — x(t+1) = A·x + B·u")
P("-"*70)
P()
P("状态空间: 把任意阶系统写成 [状态 x, 输入 u] 的一阶微分方程组")
P("  连续: dx/dt = A·x + B·u, y = C·x + D·u")
P("  离散: x(t+1) = A·x + B·u")
P()

# 例子: 二阶系统在状态空间的表示
# x = [position, velocity]
# A = [[0, 1], [-ω_n², -2ζω_n]]
# B = [0, ω_n²]
zeta, wn = 0.5, 1.0
A = [[0, 1], [-wn**2, -2*zeta*wn]]
B = [0, wn**2]

# 离散仿真
def simulate_state_space(A, B, u_seq, x0, dt=0.1):
    """模拟离散状态空间"""
    n = len(A)
    x = list(x0)
    history = [list(x)]
    for u in u_seq:
        # dx/dt = A x + B u, 用欧拉法
        dx = [sum(A[i][j] * x[j] for j in range(n)) + B[i] * u for i in range(n)]
        x = [x[i] + dx[i] * dt for i in range(n)]
        history.append(list(x))
    return history

# 阶跃输入
u_seq = [1.0] * 500
history = simulate_state_space(A, B, u_seq, x0=[0.0, 0.0])
positions = [h[0] for h in history]

# 统计
overshoot = max(0, max(positions) - 1.0)
print(f"\n二阶系统 (ζ=0.5, ω_n=1) 状态空间仿真:")
print(f"  状态: x = [position, velocity]")
print(f"  A = {A}")
print(f"  B = {B}")
print(f"  最大超调: {overshoot:.3f}")
print(f"  稳态值: {positions[-1]:.3f}")

P("""
状态空间的优势:
1. 任意阶系统统一表示 (高阶 = 多维状态)
2. 多输入多输出 (MIMO) 自然扩展
3. 与现代控制理论 (LQR/Kalman/MPC) 直接对接
4. 与强化学习 MDP 同构 (state + action → next state)
""")

# ============================================================
# Part 4: 系统建模 → AI 的桥
# ============================================================
P("="*70)
P("Part 4: 系统建模 → AI")
P("-"*70)
P("""
1. 【MDP = 离散状态空间】
   强化学习的 MDP: (S, A, P, R)
   - S = 状态空间
   - A = 输入空间
   - P(s' | s, a) = 状态转移 (对应 A, B 矩阵)
   - R = 奖励
   本质就是 [随机化的离散状态空间方程].

2. 【RNN / Transformer 是状态空间模型】
   RNN: h(t+1) = σ(W·h(t) + U·x(t))
   - h 是 hidden state
   - 这就是 [状态空间方程]!
   Transformer: attention 等价于 [状态空间的全连接扩展]

3. 【世界模型 (World Models)】
   Yann LeCun 的 JEPA / Sora 的视频生成 = 学一个 [环境的状态空间模型]
   然后用这个模型做预测和控制.

4. 【线性系统理论 ↔ 神经网络可解释性】
   研究神经网络的 [线性区域] 行为, 用状态空间工具分析
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
系统建模是控制论的 [数学语言]:
- 一阶: τ·dT/dt + T = K·u, 时间常数 τ 决定响应快慢
- 二阶: 有阻尼比 ζ, ζ=0.7 工程最优 (轻微超调 + 快稳态)
- 状态空间: x(t+1) = A·x + B·u, 任意阶通用
- 与 AI 同构: MDP=随机状态空间, RNN=状态空间, 世界模型=状态空间模型
""")
