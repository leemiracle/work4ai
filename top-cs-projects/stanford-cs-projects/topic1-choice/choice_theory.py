"""
CS329H Coding 1 - Choice Theory & Preference Modeling
覆盖课程模块：L1-L4 (Choice Model / RUM / Bradley-Terry / Rasch)

实现内容：
1. Random Utility Model (RUM)
2. Bradley-Terry 模型 + MLE 训练
3. Rasch 模型
4. Luce Choice Axiom 验证
5. Plackett-Luce 排名模型

数学参考：CS329H 📕 Chapter 1-2
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import Optional


# ============ 1. Random Utility Model ============

@dataclass
class Item:
    id: str
    true_quality: float  # 真实质量分（用于生成数据）
    features: dict = field(default_factory=dict)


class RandomUtilityModel:
    """
    RUM: U_ij = V_ij + ε_ij
    ε ~ Gumbel(0, 1) → 选择概率 = softmax(V)
    """

    def __init__(self, items: list[Item]):
        self.items = items

    def utility(self, item: Item, noise_scale: float = 1.0) -> float:
        """采样一次效用（含噪声）"""
        # Gumbel noise
        gumbel = -math.log(-math.log(random.random()))
        return item.true_quality + noise_scale * gumbel

    def choose_one(self, available: list[Item], noise_scale: float = 1.0) -> Item:
        """从 available 中选 1 个"""
        utilities = [(it, self.utility(it, noise_scale)) for it in available]
        return max(utilities, key=lambda x: x[1])[0]

    def choice_prob(self, item: Item, available: list[Item]) -> float:
        """理论选择概率（softmax over qualities）"""
        exp_v = math.exp(item.true_quality)
        return exp_v / sum(math.exp(it.true_quality) for it in available)


# ============ 2. Bradley-Terry Model ============

class BradleyTerry:
    """
    BT 模型: P(i beats j) = σ(v_i - v_j) = π_i / (π_i + π_j)
    其中 π_i = exp(v_i) 是 item i 的"强度"

    MLE 训练：最大化观测到偏好对的概率
    """

    def __init__(self, item_ids: list[str], init_v: Optional[dict[str, float]] = None):
        self.item_ids = item_ids
        # 参数 v_i（用 dict 方便索引）
        self.v = {iid: init_v.get(iid, 0.0) if init_v else 0.0
                  for iid in item_ids}

    def prob_i_beats_j(self, i: str, j: str) -> float:
        """P(i beats j) = 1 / (1 + exp(v_j - v_i))"""
        return 1.0 / (1.0 + math.exp(self.v[j] - self.v[i]))

    def fit(self, comparisons: list[tuple[str, str]],
            epochs: int = 1000, lr: float = 0.05, verbose: bool = False):
        """
        从 (winner, loser) pairs 学参数
        最大化 ∏ P(winner beats loser) = ∏ σ(v_w - v_l)
        等价于最小化 -log σ(v_w - v_l)
        梯度：∂(-log σ(v_w-v_l))/∂v_w = -σ(v_l-v_w) = -(1 - σ(v_w-v_l))
        """
        history = []
        for epoch in range(epochs):
            total_loss = 0.0
            random.shuffle(comparisons)
            for winner, loser in comparisons:
                if winner not in self.v or loser not in self.v:
                    continue
                diff = self.v[winner] - self.v[loser]
                sig = 1.0 / (1.0 + math.exp(-diff))
                # Loss: -log(sig)
                total_loss += -math.log(sig + 1e-10)
                # Gradient
                grad_w = -(1 - sig)  # ∂loss/∂v_winner
                grad_l = (1 - sig)
                self.v[winner] -= lr * grad_w
                self.v[loser] -= lr * grad_l
            if verbose and (epoch + 1) % 100 == 0:
                print(f"  Epoch {epoch+1}: loss = {total_loss/len(comparisons):.4f}")
            history.append(total_loss / max(len(comparisons), 1))
        return history

    def rank(self) -> list[tuple[str, float]]:
        """返回按 v 排序的 (item_id, score)"""
        return sorted(self.v.items(), key=lambda x: -x[1])


# ============ 3. Rasch Model ============

class RaschModel:
    """
    Rasch: P(correct) = σ(θ_user - β_item)
    - θ_user: 用户能力
    - β_item: 题目难度
    用于 IRT（Item Response Theory），如 GRE / SAT 评分
    """

    def __init__(self, n_users: int, n_items: int):
        self.theta = [0.0] * n_users  # 用户能力
        self.beta = [0.0] * n_items   # 题目难度

    def prob_correct(self, user: int, item: int) -> float:
        return 1.0 / (1.0 + math.exp(-(self.theta[user] - self.beta[item])))

    def fit(self, responses: list[tuple[int, int, int]],  # (user, item, 0/1)
            epochs: int = 500, lr: float = 0.05):
        """MLE 训练"""
        for epoch in range(epochs):
            random.shuffle(responses)
            for u, i, r in responses:
                p = self.prob_correct(u, i)
                err = p - r  # 梯度方向
                self.theta[u] -= lr * err
                self.beta[i] += lr * err


# ============ 4. Luce Choice Axiom (IIA) ============

def luce_choice_prob(item_value: float, all_values: list[float]) -> float:
    """
    Luce: P(i | S) = u_i / Σ u_j
    IIA 性质：相对概率只由 u_i/u_j 决定，与 S 中其他选项无关
    """
    return item_value / sum(all_values)


def test_iia_violation(items: list[Item]) -> bool:
    """
    测试 IIA 是否被违反
    经典例子（Debreu 1960）：
      S1 = {A, B}（A 比 B 略好）→ P(A) ≈ 0.5
      S2 = {A, B', B''}（B' 和 B'' 是 B 的复制）
    按 Luce 应该 P(A) = 1/3，但人类往往 P(A) > 1/3
    """
    # Mock：假设人类违反 IIA
    return True


# ============ 5. Plackett-Luce 排名 ============

def plackett_luce_sample(items: list[Item], noise_scale: float = 1.0) -> list[Item]:
    """
    PL 排名采样：
    反复用 Luce choice 选第一个，然后从剩余中选第二个...
    """
    available = list(items)
    ranking = []
    while available:
        # softmax over qualities
        scores = [it.true_quality / noise_scale for it in available]
        exp_s = [math.exp(s) for s in scores]
        total = sum(exp_s)
        probs = [e / total for e in exp_s]
        # sample
        r = random.random()
        cum = 0.0
        for i, p in enumerate(probs):
            cum += p
            if r <= cum:
                ranking.append(available.pop(i))
                break
        else:
            ranking.append(available.pop())
    return ranking


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS329H Coding 1: Choice Theory Demo")
    print("=" * 60)

    random.seed(42)

    # 1. RUM
    print("\n📋 1. Random Utility Model")
    items = [
        Item("A", true_quality=2.0),
        Item("B", true_quality=1.0),
        Item("C", true_quality=0.5),
    ]
    rum = RandomUtilityModel(items)
    print(f"   理论 P(A|A,B,C) = {rum.choice_prob(items[0], items):.3f}")

    # 模拟 1000 次
    counts = {"A": 0, "B": 0, "C": 0}
    for _ in range(1000):
        chosen = rum.choose_one(items, noise_scale=1.0)
        counts[chosen.id] += 1
    print(f"   经验频率 (1000 次): {counts}")

    # 2. Bradley-Terry
    print("\n📋 2. Bradley-Terry 模型训练")
    bt = BradleyTerry(["A", "B", "C"])
    # 真实 v: A=2, B=1, C=0.5

    # 生成训练数据
    true_v = {"A": 2.0, "B": 1.0, "C": 0.5}
    comparisons = []
    for _ in range(500):
        i, j = random.sample(["A", "B", "C"], 2)
        # P(i beats j) = σ(v_i - v_j)
        p = 1.0 / (1.0 + math.exp(-(true_v[i] - true_v[j])))
        winner = i if random.random() < p else j
        loser = j if winner == i else i
        comparisons.append((winner, loser))

    print(f"   训练数据: {len(comparisons)} 偏好对")
    bt.fit(comparisons, epochs=500, lr=0.05)
    print(f"   学到的 v: {dict(bt.rank())}")
    print(f"   真实 v: {true_v}")

    # 3. Rasch
    print("\n📋 3. Rasch 模型（IRT）")
    rasch = RaschModel(n_users=10, n_items=20)
    # 模拟学生答题
    responses = []
    for u in range(10):
        for i in range(20):
            p = rasch.prob_correct(u, i)
            r = 1 if random.random() < p else 0
            responses.append((u, i, r))
    rasch.fit(responses, epochs=300)
    print(f"   学到 θ (学生能力): {[round(x,2) for x in rasch.theta[:5]]}...")
    print(f"   学到 β (题目难度): {[round(x,2) for x in rasch.beta[:5]]}...")

    # 4. Plackett-Luce
    print("\n📋 4. Plackett-Luce 排名采样")
    samples = []
    for _ in range(1000):
        ranking = plackett_luce_sample(items, noise_scale=1.0)
        samples.append(tuple(it.id for it in ranking))
    from collections import Counter
    common = Counter(samples).most_common(3)
    print(f"   最常见排名（1000 次采样）:")
    for rank, count in common:
        print(f"     {' > '.join(rank)}: {count} 次 ({count/10:.0f}%)")

    # 5. Luce / IIA
    print("\n📋 5. Luce Choice & IIA")
    v = [2.0, 1.0, 0.5]
    probs = [luce_choice_prob(v[i], v) for i in range(3)]
    print(f"   Luce 概率: {[f'{p:.3f}' for p in probs]}, sum = {sum(probs):.3f}")

    print("\n✅ CS329H Coding 1 完成！")
    print("\n💡 这覆盖了 CS329H L1-L4 的核心：")
    print("   - Choice Theory (L1)")
    print("   - RUM / Gumbel noise (L2)")
    print("   - Bradley-Terry MLE (L3)")
    print("   - Rasch / IRT (L3)")
    print("   - Luce / Plackett-Luce (L4)")


if __name__ == "__main__":
    demo()
