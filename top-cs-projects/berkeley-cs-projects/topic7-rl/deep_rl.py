"""
CS 285 Deep Reinforcement Learning — UC Berkeley (Levine)
================================================
覆盖主题：
- Policy Gradient（REINFORCE）（Lec 5-6）
- TRPO / PPO（natural gradient + clipped）（Lec 7-9）
- DQN（target network + experience replay）（Lec 10-11）
- SAC（soft actor-critic, max-entropy）（Lec 13-14）

核心教材/参考：
- Sutton & Barto "Reinforcement Learning: An Introduction" 2nd ed (MIT 2018), §13 Policy Gradient
- Mnih et al. "Human-level control through deep reinforcement learning" Nature 518 (2015), DQN, arXiv:1312.5602
- Haarnoja et al. "Soft Actor-Critic: Off-Policy Maximum Entropy Deep RL with a Stochastic Actor" ICML 2018, arXiv:1801.01290
- Schulman et al. "Trust Region Policy Optimization" ICML 2015, arXiv:1502.05477
- Schulman et al. "Proximal Policy Optimization Algorithms" (2017), arXiv:1707.06347
- Williams "REINFORCE: Simple Statistical Gradient-Following Algorithms" Machine Learning (1992)

本文件实现：
- REINFORCE（policy gradient 蒙特卡洛）
- DQN（target network + replay buffer）
- SAC entropy 自动调节
- 共轭梯度法（TRPO 求解 H⁻¹g 的核心子程序）

运行：
    python deep_rl.py
"""
from __future__ import annotations
import math
import random
from collections import defaultdict, deque


# ============================================================
# 环境：简化网格世界 / CartPole-like
# ============================================================

class GridWorld:
    """
    4x4 网格：
    - 起点 (0,0)，终点 (3,3) reward +10
    - 每步 -0.01
    - 陷阱 (1,1) reward -10（结束）
    actions: 0=up, 1=down, 2=left, 3=right
    """
    def __init__(self):
        self.size = 4
        self.reset()

    def reset(self):
        self.pos = (0, 0)
        return self.pos

    def step(self, action):
        r, c = self.pos
        if action == 0:
            r = max(0, r - 1)
        elif action == 1:
            r = min(self.size - 1, r + 1)
        elif action == 2:
            c = max(0, c - 1)
        elif action == 3:
            c = min(self.size - 1, c + 1)
        self.pos = (r, c)
        if self.pos == (3, 3):
            return self.pos, 10.0, True
        if self.pos == (1, 1):
            return self.pos, -10.0, True
        return self.pos, -0.01, False


# ============================================================
# 1. REINFORCE（Williams 1992）
# ============================================================

class REINFORCEAgent:
    """
    Policy Gradient Theorem:
        ∇J(θ) = E[∇log π_θ(a|s) · G_t]
    其中 G_t = Σ γ^k r_{t+k} 是蒙特卡洛回报。
    这里用 softmax 策略 + 线性特征（tabular 对应 one-hot state）。
    """
    def __init__(self, n_states, n_actions, lr=0.01, gamma=0.99):
        self.n_states = n_states
        self.n_actions = n_actions
        self.lr = lr
        self.gamma = gamma
        # 策略参数 θ(s, a)
        self.theta = defaultdict(lambda: [0.0] * n_actions)

    def policy(self, state):
        """softmax 策略"""
        logits = self.theta[state]
        m = max(logits)
        exp_l = [math.exp(l - m) for l in logits]
        total = sum(exp_l)
        return [e / total for e in exp_l]

    def choose(self, state):
        probs = self.policy(state)
        r = random.random()
        cum = 0
        for a, p in enumerate(probs):
            cum += p
            if r <= cum:
                return a
        return self.n_actions - 1

    def update(self, trajectory):
        """
        trajectory: [(s, a, r), ...]
        G_t = Σ γ^k r_{t+k}  →  ∇log π(a|s) = one_hot(a) - π(s)
        """
        T = len(trajectory)
        for t in range(T):
            s, a, _ = trajectory[t]
            # 蒙特卡洛回报
            G = sum(self.gamma ** (k - t) * trajectory[k][2] for k in range(t, T))
            probs = self.policy(s)
            # ∇log π(a|s) = e_a - π(s)  (softmax gradient)
            grad = [-probs[ai] for ai in range(self.n_actions)]
            grad[a] += 1
            # θ ← θ + lr * G * grad
            for ai in range(self.n_actions):
                self.theta[s][ai] += self.lr * G * grad[ai]


# ============================================================
# 2. DQN（Mnih 2015，target network）
# ============================================================

class QNetwork:
    """简化 Q-network：线性 Q(s,a) = w[s,a]"""
    def __init__(self, n_states, n_actions):
        self.n_states = n_states
        self.n_actions = n_actions
        self.params = defaultdict(lambda: [0.0] * n_actions)

    def forward(self, state):
        return list(self.params[state])

    def copy_from(self, other):
        self.params = defaultdict(lambda: [0.0] * self.n_actions,
                                   {k: list(v) for k, v in other.params.items()})


class DQNAgent:
    """
    DQN (Mnih 2015):
        target = r + γ max_a' Q_target(s', a')
        loss = (Q(s,a) - target)²
    Tricks: replay buffer + target network（每 C 步同步）+ ε-greedy。
    """
    def __init__(self, n_states, n_actions, lr=0.1, gamma=0.95,
                 epsilon=0.3, buffer_size=1000, target_sync=50):
        self.n_actions = n_actions
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.q = QNetwork(n_states, n_actions)
        self.q_target = QNetwork(n_states, n_actions)
        self.q_target.copy_from(self.q)
        self.buffer = deque(maxlen=buffer_size)
        self.target_sync = target_sync
        self.step_count = 0

    def choose(self, state):
        if random.random() < self.epsilon:
            return random.randrange(self.n_actions)
        qs = self.q.forward(state)
        return max(range(self.n_actions), key=lambda a: qs[a])

    def store(self, s, a, r, s2, done):
        self.buffer.append((s, a, r, s2, done))

    def update(self, batch_size=16):
        if len(self.buffer) < batch_size:
            return
        batch = random.sample(self.buffer, batch_size)
        for s, a, r, s2, done in batch:
            target = r if done else r + self.gamma * max(self.q_target.forward(s2))
            current = self.q.forward(s)[a]
            td_error = target - current
            self.q.params[s][a] += self.lr * td_error
        self.step_count += 1
        if self.step_count % self.target_sync == 0:
            self.q_target.copy_from(self.q)


# ============================================================
# 3. SAC entropy temperature（Haarnoja 2018）
# ============================================================

class SACSimple:
    """
    SAC 核心思想：max E[r + α·H(π)]
    H(π) = -Σ π(a) log π(a) 是策略熵。
    α 越大 → 鼓励探索；α → 0 → 退化为标准 RL。
    用 softmax temperature τ ≈ α 来演示。
    """
    def __init__(self, n_states, n_actions):
        self.n_actions = n_actions
        self.q = defaultdict(lambda: [0.0] * n_actions)
        self.alpha = 0.5  # temperature

    def policy(self, state):
        """softmax(Q/α) —— 高 α = 更均匀，低 α = 更贪心"""
        qs = self.q[state]
        m = max(qs)
        exp_q = [math.exp((q - m) / self.alpha) for q in qs]
        total = sum(exp_q)
        return [e / total for e in exp_q]

    def entropy(self, state):
        """策略熵 H(π(·|s))"""
        probs = self.policy(state)
        return -sum(p * math.log(p + 1e-10) for p in probs if p > 1e-10)

    def choose(self, state):
        probs = self.policy(state)
        r = random.random()
        cum = 0
        for a, p in enumerate(probs):
            cum += p
            if r <= cum:
                return a
        return self.n_actions - 1

    def update_q(self, s, a, r, s2):
        """Soft Bellman: Q(s,a) ← r + γ(Σ π(a'|s') Q(s',a') + α H)"""
        probs_s2 = self.policy(s2)
        v_s2 = sum(probs_s2[i] * self.q[s2][i] for i in range(self.n_actions))
        soft_v = v_s2 + self.alpha * self.entropy(s2)
        self.q[s][a] = r + 0.95 * soft_v


# ============================================================
# 4. 共轭梯度法（TRPO 求解 H⁻¹g 的核心子程序, Schulman 2015）
# ============================================================

def conjugate_gradient(A_matvec, b, n_iter=10, tol=1e-6):
    """
    共轭梯度法（CG）解 Ax = b（只需矩阵-向量乘，不需要存 A）。
    这是 TRPO 求解 H⁻¹g 的核心子程序（TRPO 还需 Fisher 矩阵、KL 约束、line search）。
    """
    x = [0.0] * len(b)
    r = list(b)
    p = list(r)
    rsold = sum(ri * ri for ri in r)
    for _ in range(n_iter):
        Ap = A_matvec(p)
        pAp = sum(pi * api for pi, api in zip(p, Ap))
        if abs(pAp) < tol:
            break
        alpha = rsold / pAp
        x = [xi + alpha * pi for xi, pi in zip(x, p)]
        r = [ri - alpha * api for ri, api in zip(r, Ap)]
        rsnew = sum(ri * ri for ri in r)
        if math.sqrt(rsnew) < tol:
            break
        beta = rsnew / rsold
        p = [ri + beta * pi for ri, pi in zip(r, p)]
        rsold = rsnew
    return x


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("CS 285 Deep RL Demo")
    print("=" * 60)
    random.seed(42)
    env = GridWorld()

    # 1. REINFORCE
    print("\n📋 1. REINFORCE Policy Gradient")
    agent = REINFORCEAgent(16, 4, lr=0.01, gamma=0.99)
    returns = []
    for ep in range(2000):
        s = env.reset()
        traj = []
        ep_reward = 0
        for _ in range(50):
            a = agent.choose(s)
            s2, r, done = env.step(a)
            traj.append((s, a, r))
            ep_reward += r
            s = s2
            if done:
                break
        agent.update(traj)
        returns.append(ep_reward)
    recent_avg = sum(returns[-100:]) / 100
    print(f"   训练 2000 episodes")
    print(f"   前 100 平均 reward: {sum(returns[:100])/100:.2f}")
    print(f"   后 100 平均 reward: {recent_avg:.2f}")

    # 2. DQN
    print("\n📋 2. DQN（target network + replay）")
    dqn = DQNAgent(16, 4, lr=0.1, gamma=0.95, epsilon=0.2)
    returns_dqn = []
    for ep in range(1000):
        s = env.reset()
        ep_reward = 0
        for _ in range(50):
            a = dqn.choose(s)
            s2, r, done = env.step(a)
            dqn.store(s, a, r, s2, done)
            dqn.update(batch_size=8)
            ep_reward += r
            s = s2
            if done:
                break
        returns_dqn.append(ep_reward)
    print(f"   后 100 平均 reward: {sum(returns_dqn[-100:])/100:.2f}")
    print(f"   (target sync every {dqn.target_sync} steps → 稳定训练)")

    # 3. SAC entropy
    print("\n📋 3. SAC Entropy 自动调节")
    sac = SACSimple(16, 4)
    ent_at = {}
    for alpha in [0.1, 0.5, 1.0, 2.0]:
        sac.alpha = alpha
        # 给定固定 Q 值
        sac.q[(0, 0)] = [1.0, 5.0, 2.0, 0.5]
        probs = sac.policy((0, 0))
        ent = sac.entropy((0, 0))
        ent_at[alpha] = ent
        print(f"   α={alpha:.1f}: Q=[1,5,2,0.5] → π={[f'{p:.2f}' for p in probs]}, H={ent:.3f} nats")

    # 4. 共轭梯度法
    print("\n📋 4. 共轭梯度法（TRPO 核心：CG 解 H⁻¹g）")
    # 简单 SPD 矩阵 [[2,1],[1,2]]
    A = [[2, 1], [1, 2]]
    b = [3, 3]
    x = conjugate_gradient(lambda p: [A[0][0]*p[0]+A[0][1]*p[1], A[1][0]*p[0]+A[1][1]*p[1]], b)
    print(f"   Ax=b: A={A}, b={b}")
    print(f"   CG 解: x = [{x[0]:.4f}, {x[1]:.4f}]  (精确解 [1.0, 1.0])")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print("   SAC 的 α 参数：Q=[1,5,2,0.5]（最优 action 明显是 a=1）：")
    print(f"   α=0.1（低熵）: 策略几乎全选 a=1，熵≈{ent_at[0.1]:.3f} nats（贪心）")
    print(f"   α=2.0（高熵）: 策略接近均匀，熵≈{ent_at[2.0]:.3f} nats（强探索）")
    print("   → '最大熵 RL' 认为适度探索 > 贪心：")
    print("   α 自动调节时，前期高熵探索覆盖所有模式，后期降熵收敛。")
    print("   这就是 SAC 在连续控制任务上超过 DDPG 的核心原因。")
    print()
    print("   DQN 用 target network 把 Q 值'冻结'在旧网络，")
    print("   避免了'追逐移动目标'导致的不稳定（Mnih 2015 的关键 trick）。")


if __name__ == "__main__":
    demo()
