"""
实验 03 — 稳定性: 特征值 / 李雅普诺夫 / 发散演示
对应文档: 讲透控制论/03-稳定性.md

核心结论:
  1. 离散系统稳定性: 状态矩阵 A 的所有特征值 |λ| < 1
  2. |λ| 越接近 1, 收敛越慢; |λ| > 1 → 系统发散
  3. 李雅普诺夫函数 V(x) 单调递减 ⟹ 系统稳定
  4. AI 训练发散 (loss爆炸) / mode collapse / GAN 训练不稳 = 控制论不稳定

跑法: python3 -u 03_stability.py
"""
import math
import numpy as np
np.random.seed(0)

def P(*a): print(*a, flush=True)

P("="*70)
P("实验 03 — 稳定性: 特征值 / 李雅普诺夫")
P("="*70)
P()

# ============================================================
# Part 1: 离散系统稳定性 — 特征值 |λ| < 1
# ============================================================
P("Part 1: 离散系统稳定性 — 特征值判据")
P("-"*70)
P("  x(t+1) = A · x(t)")
P("  稳定 ⟺ A 的所有特征值 |λ| < 1")
P()

def simulate_discrete(A, x0, steps=50):
    """模拟离散系统"""
    x = np.array(x0, dtype=float)
    traj = [x.copy()]
    for _ in range(steps):
        x = A @ x
        traj.append(x.copy())
        if np.linalg.norm(x) > 1e10:  # 检测发散
            break
    return traj

print(f"{'矩阵 A':<28}{'特征值':>20}{'稳定?':>10}{'最终 |x|':>14}")
print("-"*72)

matrices = [
    ([[0.5, 0], [0, 0.5]], "衰减"),
    ([[0.9, 0], [0, 0.9]], "慢衰减"),
    ([[1.0, 0], [0, 1.0]], "保持"),
    ([[1.05, 0], [0, 1.05]], "慢发散"),
    ([[1.5, 0], [0, 1.5]], "快发散"),
    ([[0.9, 0.5], [-0.3, 0.7]], "振荡衰减"),
    ([[1.1, 0.3], [-0.2, 0.95]], "复特征值 > 1"),
]
for A_list, name in matrices:
    A = np.array(A_list, dtype=float)
    eigenvalues = np.linalg.eigvals(A)
    stable = all(abs(lam) < 1 for lam in eigenvalues)
    traj = simulate_discrete(A, [1.0, 1.0])
    final_norm = np.linalg.norm(traj[-1])
    eig_str = ", ".join(f"{lam.real:+.2f}{lam.imag:+.2f}j" for lam in eigenvalues)
    print(f"{name:<24}[{eig_str}]{'稳定' if stable else '发散':>10}{final_norm:>14.2e}")

P("""
关键观察:
- 所有 |λ| < 1: 系统衰减到 0 (稳定)
- 任何 |λ| > 1: 系统发散 (不稳定)
- |λ| = 1: 边界 (临界稳定, 实际不安全)
- 复特征值: 系统振荡 (虚部表示振荡频率)

[这就是为什么 01 实验 Kp=5 发散] — 反馈增益太大, 闭环矩阵特征值 > 1.
""")

# ============================================================
# Part 2: 李雅普诺夫函数 — 能量观点
# ============================================================
P("="*70)
P("Part 2: 李雅普诺夫函数 V(x) — 稳定的能量判据")
P("-"*70)
P()
P("李雅普诺夫 1892: 找一个'能量函数' V(x), 若 V 沿系统轨迹单调递减 → 系统稳定")
P("  V(x) > 0, V(0) = 0, dV/dt < 0 ⟹ 系统稳定")
P()

# 例子: 二阶系统 V(x) = 1/2 (x^2 + v^2) (动能+势能)
def second_order_with_lyapunov(zeta, wn, x0=2.0, v0=0.0, steps=500, dt=0.1):
    x, v = x0, v0
    V_history = []
    x_history = []
    for t in range(steps):
        # 系统: ẍ + 2ζω_n ẋ + ω_n² x = 0
        a = -wn**2 * x - 2*zeta*wn*v
        v = v + a * dt
        x = x + v * dt
        # 李雅普诺夫函数: V = 1/2 (ω_n² x² + v²)
        V = 0.5 * (wn**2 * x**2 + v**2)
        V_history.append(V)
        x_history.append(x)
    return x_history, V_history

print(f"二阶系统 V(x) = 1/2 (ω_n² x² + v²) 的演化:")
print(f"\n{'阻尼比 ζ':<10}{'初始 V':>10}{'最终 V':>10}{'V 单调递减?':>14}")
print("-"*44)
for zeta in [0.1, 0.3, 0.7, 1.0, 1.5]:
    _, V = second_order_with_lyapunov(zeta, wn=1.0)
    # 检查 V 是否单调递减
    monotonic = all(V[i+1] <= V[i] + 1e-6 for i in range(len(V)-1))
    print(f"{zeta:<10.1f}{V[0]:>10.3f}{V[-1]:>10.3f}{'是' if monotonic else '否':>14}")

P("""
关键观察:
- 对所有 ζ > 0, V 单调递减 → 系统稳定 (李雅普诺夫定理)
- ζ 越大, V 衰减越快 (能量耗散更快)
- 这是控制论的 [能量观点]: 稳定 = 能量持续耗散

李雅普诺夫的妙处:
- 不需要解微分方程, 直接判断稳定性
- 适用于非线性系统 (线性系统的特征值法不适用)
- 是 RLHF / 训练收敛性证明的数学工具
""")

# ============================================================
# Part 3: AI 中的稳定性问题
# ============================================================
P("="*70)
P("Part 3: AI 中的稳定性问题 — 全是控制论")
P("-"*70)
P("""
1. 【训练 loss 爆炸 = 系统发散】
   learning rate 过大 → 梯度更新幅度过大 → 闭环特征值 > 1 → 发散
   解决: warmup (逐步增加 lr), gradient clipping, 用 Adam (有自适应)

2. 【GAN 训练不稳 = 纳什均衡不收敛】
   Generator 和 Discriminator 互相博弈, 容易陷入振荡
   解决: WGAN (用 Wasserstein 距离让博弈平滑), 谱归一化

3. 【模式崩溃 (mode collapse)】
   GAN 的 Generator 只输出几个模式 → 信息论上 I(G(z);z) 太小
   这是 [系统退化] 现象, 控制论视角是 [收敛到局部稳定点]

4. 【强化学习的 value function 估计不稳】
   TD 学习在 off-policy 时容易发散 → Baird 反例
   解决: target network (DQN), 双 Q 学习

5. 【LLM 训练 loss spike】
   70B 模型训练时偶尔 loss 突然飙升 → 数值不稳定
   解决: 用 bf16 而非 fp16, gradient clipping, 重新初始化
""")

# ============================================================
# Part 4: 稳定性 → AI 训练实践
# ============================================================
P("="*70)
P("Part 4: AI 训练稳定性的工程经验")
P("-"*70)
P("""
1. 【学习率 = 反馈增益】
   lr 过大 (类似 Kp 过大) → 训练发散
   经验: 用 lr finder 找到 lr 上限, 然后用 1/3 - 1/10 训练

2. 【Warmup = 软启动】
   前 1000 步从 lr=0 线性增到目标, 避免初始震荡
   LLM 训练必备 (Chinchilla/GPT 训练都用)

3. 【梯度裁剪 = 防止单步发散】
   |∇| > 阈值时, ∇ ← ∇ * 阈值 / |∇|
   防止个别 batch 让训练崩盘

4. 【Adam = 自适应反馈】
   根据历史梯度大小自适应步长, 在不同方向用不同 lr
   这是 [自适应控制] 在 ML 里的化身

5. 【Target Network = 延迟反馈】
   DQN: target Q 用一个慢更新的网络算, 避免自举反馈环不稳
   这是 [低通滤波] 控制思想
""")

P("="*70)
P("一句话总结")
P("="*70)
P("""
稳定性是控制论的 [核心约束]:
- 线性系统: 所有特征值 |λ| < 1 ⟺ 稳定
- 非线性: 李雅普诺夫函数 V(x) 单调递减 ⟹ 稳定
- 实测: |λ|=1.05 慢发散, |λ|=1.5 快发散, |λ|=0.5 衰减

AI 训练不稳 = 控制论不稳定:
- loss 爆炸 / GAN 不收敛 / mode collapse / loss spike / TD 发散
- 全是特征值 > 1 或 V(x) 不单调递减
- 解决方案都是控制论: lr 调小, warmup, gradient clipping, Adam 自适应, target network
""")
