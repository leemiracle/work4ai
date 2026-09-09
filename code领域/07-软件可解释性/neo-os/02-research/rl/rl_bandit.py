"""最小 RL：k-armed bandit + ε-greedy + reward 更新
验证「试错 → 信用分配 → 策略改进」核心循环（RL 的 hello world）"""
import numpy as np

def bandit(k=10, steps=1000, eps=0.1, seed=42):
    rng = np.random.default_rng(seed)
    true_q = rng.normal(0, 1, k)  # 每个臂的真实期望（agent 不知道）
    Q = np.zeros(k)
    N = np.zeros(k)
    rewards = []
    for t in range(steps):
        # ε-greedy：以 ε 概率探索，否则选当前最优
        a = rng.integers(k) if rng.random() < eps else Q.argmax()
        r = rng.normal(true_q[a], 1)
        N[a] += 1
        Q[a] += (r - Q[a]) / N[a]
        rewards.append(r)
    return np.mean(rewards), Q, true_q

avg_r, Q_est, true_q = bandit()
print(f"平均 reward: {avg_r:.3f}（最优臂真实值 {true_q.max():.3f}）")
print(f"选中臂: {Q_est.argmax()}（真实最优 {true_q.argmax()}）")
print(f"估计 Q: {np.round(Q_est, 2)}")
print(f"真实 Q: {np.round(true_q, 2)}")
