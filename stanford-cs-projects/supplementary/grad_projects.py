"""
第二批研究生项目：覆盖 5 门重要课程

1. CS312 - Deep Learning Alchemy（训练工程）
2. CS224V - Conversational Virtual Assistants（SMT-based LLM）
3. CS238 - Decision Making under Uncertainty（POMDP）
4. CS145 - Modern Data Systems（SQL + Vector DB）
5. CS227A - Robot Perception（多模态融合）
"""
from __future__ import annotations
import math
import random
import re
import hashlib
from collections import defaultdict, Counter
from dataclasses import dataclass, field


# ============================================
# 🎯 CS312: Deep Learning Alchemy
# 训练工程：怎么把 loss 真正跑下来
# ============================================

@dataclass
class TrainingConfig:
    lr: float = 1e-3
    batch_size: int = 32
    warmup_steps: int = 100
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    beta1: float = 0.9
    beta2: float = 0.999
    eps: float = 1e-8


class AdamW:
    """AdamW 优化器（带 weight decay 解耦）"""

    def __init__(self, params: list[list[float]], config: TrainingConfig):
        self.params = params
        self.cfg = config
        self.t = 0
        self.m = [[0.0] * len(p) for p in params]  # 一阶矩
        self.v = [[0.0] * len(p) for p in params]  # 二阶矩

    def step(self, grads: list[list[float]]):
        self.t += 1
        cfg = self.cfg
        for i, (p, g) in enumerate(zip(self.params, grads)):
            for j in range(len(p)):
                # 梯度裁剪
                if cfg.grad_clip > 0:
                    g[j] = max(-cfg.grad_clip, min(cfg.grad_clip, g[j]))
                # Warmup
                warmup_lr = cfg.lr * min(1.0, self.t / max(cfg.warmup_steps, 1))
                # 一阶/二阶矩
                self.m[i][j] = cfg.beta1 * self.m[i][j] + (1 - cfg.beta1) * g[j]
                self.v[i][j] = cfg.beta2 * self.v[i][j] + (1 - cfg.beta2) * g[j] ** 2
                # Bias correction
                m_hat = self.m[i][j] / (1 - cfg.beta1 ** self.t)
                v_hat = self.v[i][j] / (1 - cfg.beta2 ** self.t)
                # Update + decoupled weight decay
                p[j] -= warmup_lr * m_hat / (math.sqrt(v_hat) + cfg.eps)
                p[j] -= warmup_lr * cfg.weight_decay * p[j]


def diagnose_loss(loss_history: list[float]) -> dict:
    """DL Alchemy：诊断训练问题"""
    if not loss_history:
        return {"status": "empty"}

    issues = []
    recent = loss_history[-10:]
    early = loss_history[:10]

    # Loss 不下降
    if recent[-1] >= early[-1] * 0.95:
        issues.append("loss_not_decreasing")
        issues.append("可能原因: lr 太小 / 数据有问题 / 模型容量不足")

    # Loss 爆炸
    if max(loss_history) > 10 * loss_history[0]:
        issues.append("loss_explosion")
        issues.append("可能原因: lr 太大 / 梯度未裁剪 / 数值不稳定")

    # Loss NaN
    if any(math.isnan(l) if isinstance(l, float) else False for l in loss_history):
        issues.append("loss_nan")
        issues.append("可能原因: log(0) / 除以 0 / fp16 溢出")

    # Loss 平稳
    if len(loss_history) > 50:
        plateau_std = (sum((l - recent[0])**2 for l in recent) / len(recent)) ** 0.5
        if plateau_std < 1e-4:
            issues.append("loss_plateau")
            issues.append("可能原因: lr 已衰减 / 陷入局部最优 / 数据噪声")

    # Oscillation
    diffs = [abs(recent[i] - recent[i-1]) for i in range(1, len(recent))]
    if diffs and sum(diffs) / len(diffs) > 0.05 * recent[-1]:
        issues.append("loss_oscillating")
        issues.append("可能原因: lr 太大 / batch_size 太小")

    return {
        "final_loss": loss_history[-1],
        "initial_loss": loss_history[0],
        "reduction_pct": (1 - loss_history[-1]/loss_history[0]) * 100 if loss_history[0] else 0,
        "issues": issues,
    }


def cs312_demo():
    print("\n📋 CS312: Deep Learning Alchemy")
    # 模拟训练
    random.seed(42)
    config = TrainingConfig(lr=0.01, batch_size=8)
    # 简单线性回归：y = 2x + 1
    true_w, true_b = 2.0, 1.0
    X = [[random.gauss(0, 1)] for _ in range(100)]
    Y = [true_w * x[0] + true_b + random.gauss(0, 0.1) for x in X]

    w = [random.gauss(0, 0.1)]
    b = [0.0]
    opt = AdamW([w, b], config)
    history = []
    for epoch in range(50):
        total_loss = 0
        for x, y in zip(X, Y):
            pred = w[0] * x[0] + b[0]
            loss = (pred - y) ** 2
            grad_w = 2 * (pred - y) * x[0]
            grad_b = 2 * (pred - y)
            opt.step([[grad_w], [grad_b]])
            total_loss += loss
        history.append(total_loss / len(X))

    diag = diagnose_loss(history)
    print(f"   真实参数: w={true_w}, b={true_b}")
    print(f"   学到参数: w={w[0]:.3f}, b={b[0]:.3f}")
    print(f"   Loss: {history[0]:.3f} → {history[-1]:.3f}")
    print(f"   诊断: {diag}")


# ============================================
# 🎤 CS224V: SMT-based 非幻觉 LLM Agent
# Monica Lam 风格
# ============================================

class SMTSolver:
    """
    Satisfiability Modulo Theories 简化版
    用于约束 LLM 输出，确保事实一致性
    """

    def __init__(self):
        self.facts: set[str] = set()
        self.rules: list[tuple[str, str]] = []  # (condition, conclusion)

    def add_fact(self, fact: str):
        self.facts.add(fact.lower())

    def add_rule(self, cond: str, concl: str):
        self.rules.append((cond.lower(), concl.lower()))

    def check_consistency(self, claim: str) -> tuple[bool, str]:
        """检查 claim 是否与已知事实一致"""
        claim_lower = claim.lower()
        # 直接矛盾
        for fact in self.facts:
            if fact in claim_lower or claim_lower in fact:
                return True, "✓ 直接支持"
        # 用规则推导
        for cond, concl in self.rules:
            if cond in claim_lower and concl not in self.facts:
                return False, f"违反规则: {cond} → {concl}"
        # 没找到支持 → 不可证
        return False, "无法验证（缺乏证据）"


class NonHallucinatingAgent:
    """
    CS224V 核心思想：用 SMT 约束 LLM，确保输出可证
    """

    def __init__(self):
        self.solver = SMTSolver()
        # 知识库
        self.solver.add_fact("transformer 提出于 2017")
        self.solver.add_fact("bert 基于 encoder")
        self.solver.add_fact("gpt 基于 decoder")
        self.solver.add_fact("react 是 yao 2022 提出")
        self.solver.add_rule("encoder-only", "适合分类")
        self.solver.add_rule("decoder-only", "适合生成")

    def answer(self, question: str) -> dict:
        """生成 + 验证"""
        # Mock: 假装 LLM 给出答案
        if "transformer" in question.lower() and "哪一年" in question:
            candidate = "Transformer 于 2017 年提出"
        elif "bert" in question.lower():
            candidate = "BERT 基于 encoder 架构"
        elif "gpt" in question.lower():
            candidate = "GPT 基于 decoder 架构"
        elif "react" in question.lower():
            candidate = "ReAct 是 Yao 2022 提出的"
        else:
            candidate = "我不知道答案（避免幻觉）"

        # SMT 验证
        consistent, reason = self.solver.check_consistency(candidate)

        return {
            "answer": candidate if consistent else "[拒绝回答 - 无法验证]",
            "verified": consistent,
            "reason": reason,
        }


def cs224v_demo():
    print("\n📋 CS224V: Non-Hallucinating LLM (SMT-based)")
    agent = NonHallucinatingAgent()

    questions = [
        "Transformer 是哪一年提出的？",
        "BERT 基于什么架构？",
        "ReAct 是谁提出的？",
        "什么是量子纠缠？",  # 不在知识库
    ]
    for q in questions:
        result = agent.answer(q)
        print(f"   Q: {q}")
        print(f"   A: {result['answer']}")
        print(f"   Verified: {result['verified']} - {result['reason']}")


# ============================================
# 🎲 CS238: POMDP（部分可观测 MDP）
# ============================================

@dataclass
class POMDP:
    """简化 POMDP: 机器人在房间里找宝藏"""
    states: list[str]  # ['left', 'center', 'right']
    actions: list[str]  # ['move_left', 'move_right', 'search']
    observations: list[str]  # ['see_glitter', 'see_nothing', 'at_wall']
    # T[s][a][s'] = 概率
    transition: dict = field(default_factory=dict)
    # O[s'][o] = 概率
    observation_model: dict = field(default_factory=dict)
    # R[s][a] = reward
    reward: dict = field(default_factory=dict)


class BeliefState:
    """信念状态：对真实状态的分布"""

    def __init__(self, states: list[str]):
        self.belief = {s: 1.0 / len(states) for s in states}

    def update(self, action: str, observation: str, pomdp: POMDP):
        """贝叶斯滤波"""
        new_belief = {}
        for s_new in pomdp.states:
            # 预测：P(s_new | belief, action) = Σ P(s_new|s,a) belief(s)
            pred = sum(
                pomdp.transition.get(s_old, {}).get(action, {}).get(s_new, 0) * self.belief[s_old]
                for s_old in pomdp.states
            )
            # 观测：P(o | s_new)
            obs_prob = pomdp.observation_model.get(s_new, {}).get(observation, 0.1)
            new_belief[s_new] = pred * obs_prob

        # 归一化
        total = sum(new_belief.values())
        if total > 0:
            new_belief = {k: v / total for k, v in new_belief.items()}
        self.belief = new_belief

    def most_likely(self) -> str:
        return max(self.belief, key=self.belief.get)


def cs238_demo():
    print("\n📋 CS238: POMDP - 模糊世界中的决策")
    # 简单 POMDP：机器人在 3 个房间，找宝藏（在 right 房间）
    pomdp = POMDP(
        states=['left', 'center', 'right'],
        actions=['move_left', 'move_right', 'search'],
        observations=['see_treasure', 'see_empty'],
    )
    # 转移概率
    pomdp.transition = {
        'left': {'move_left': {'left': 0.9, 'center': 0.1, 'right': 0},
                 'move_right': {'left': 0.1, 'center': 0.8, 'right': 0.1},
                 'search': {'left': 1.0}},
        'center': {'move_left': {'left': 0.8, 'center': 0.2, 'right': 0},
                   'move_right': {'left': 0, 'center': 0.2, 'right': 0.8},
                   'search': {'center': 1.0}},
        'right': {'move_left': {'left': 0, 'center': 0.8, 'right': 0.2},
                  'move_right': {'left': 0, 'center': 0.1, 'right': 0.9},
                  'search': {'right': 1.0}},
    }
    # 观测模型
    pomdp.observation_model = {
        'left': {'see_treasure': 0.0, 'see_empty': 1.0},
        'center': {'see_treasure': 0.1, 'see_empty': 0.9},
        'right': {'see_treasure': 0.9, 'see_empty': 0.1},
    }
    # 奖励
    pomdp.reward = {
        'left': {'search': -1},
        'center': {'search': -1},
        'right': {'search': 10},  # 找到宝藏
    }

    # 初始信念：不知道在哪
    belief = BeliefState(pomdp.states)

    # 模拟一个 episode
    true_state = random.choice(pomdp.states)
    print(f"   初始 belief: {belief.belief}")
    print(f"   (Hidden) 真实位置: {true_state}")

    history = []
    for step in range(5):
        # 简单策略：若最可能在 right，search；否则 move_right
        if belief.most_likely() == 'right':
            action = 'search'
        else:
            action = 'move_right'

        # 真实转移
        trans = pomdp.transition[true_state][action]
        r = random.random()
        cum = 0
        for s_new, p in trans.items():
            cum += p
            if r <= cum:
                true_state = s_new
                break

        # 观测
        obs_p = pomdp.observation_model[true_state]
        r = random.random()
        obs = 'see_treasure' if r < obs_p['see_treasure'] else 'see_empty'

        # 信念更新
        belief.update(action, obs, pomdp)
        reward = pomdp.reward.get(true_state, {}).get(action, 0)
        history.append((step, action, obs, reward, belief.belief.copy()))
        print(f"   Step {step}: action={action}, obs={obs}, reward={reward}, belief={belief.belief}")

    print(f"   Total reward: {sum(h[3] for h in history)}")


# ============================================
# 🗄️ CS145: Modern Data Systems
# SQL + Vector Index (HNSW 简化)
# ============================================

class SimpleSQL:
    """极简 SQL 执行引擎"""

    def __init__(self):
        self.tables: dict[str, list[dict]] = {}

    def create_table(self, name: str, rows: list[dict]):
        self.tables[name] = rows

    def select_where(self, table: str, condition) -> list[dict]:
        """SELECT * FROM table WHERE condition(row)"""
        return [r for r in self.tables.get(table, []) if condition(r)]

    def join(self, t1: str, t2: str, on) -> list[dict]:
        """INNER JOIN"""
        result = []
        for r1 in self.tables.get(t1, []):
            for r2 in self.tables.get(t2, []):
                if on(r1, r2):
                    merged = {**r1, **r2}
                    result.append(merged)
        return result

    def group_by_count(self, table: str, key_fn) -> dict:
        """GROUP BY + COUNT"""
        counts = Counter(key_fn(r) for r in self.tables.get(table, []))
        return dict(counts)


class SimpleHNSW:
    """简化版 HNSW 向量索引"""

    def __init__(self, dim: int = 8, M: int = 4):
        self.dim = dim
        self.M = M  # 每个节点的邻居数
        self.nodes: dict[int, list[float]] = {}  # id → vector
        self.graph: dict[int, list[int]] = {}  # id → neighbors
        self._next_id = 0

    def add(self, vec: list[float]) -> int:
        nid = self._next_id
        self._next_id += 1
        self.nodes[nid] = vec
        self.graph[nid] = []
        # 连接到最近的 M 个节点
        if len(self.nodes) > 1:
            sims = [(other, self._cosine(vec, self.nodes[other]))
                    for other in self.nodes if other != nid]
            sims.sort(key=lambda x: -x[1])
            for other, _ in sims[:self.M]:
                self.graph[nid].append(other)
                self.graph[other].append(nid)
        return nid

    def search(self, query: list[float], k: int = 3) -> list[tuple[int, float]]:
        """贪婪搜索：从随机节点开始，跳到更近的邻居"""
        if not self.nodes:
            return []
        # 随机起点
        current = random.choice(list(self.nodes.keys()))
        current_sim = self._cosine(query, self.nodes[current])
        while True:
            improved = False
            for neighbor in self.graph.get(current, []):
                sim = self._cosine(query, self.nodes[neighbor])
                if sim > current_sim:
                    current = neighbor
                    current_sim = sim
                    improved = True
                    break
            if not improved:
                break
        # 返回 top-k（暴力作为 fallback）
        all_sims = [(nid, self._cosine(query, vec)) for nid, vec in self.nodes.items()]
        all_sims.sort(key=lambda x: -x[1])
        return all_sims[:k]

    @staticmethod
    def _cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x*x for x in a))
        nb = math.sqrt(sum(y*y for y in b))
        return dot / (na * nb + 1e-10)


def cs145_demo():
    print("\n📋 CS145: SQL + Vector DB")
    # SQL
    sql = SimpleSQL()
    sql.create_table("users", [
        {"id": 1, "name": "Alice", "age": 25, "city": "SF"},
        {"id": 2, "name": "Bob", "age": 30, "city": "NYC"},
        {"id": 3, "name": "Carol", "age": 25, "city": "SF"},
    ])
    sql.create_table("orders", [
        {"order_id": 101, "user_id": 1, "amount": 50},
        {"order_id": 102, "user_id": 1, "amount": 30},
        {"order_id": 103, "user_id": 2, "amount": 100},
    ])

    sf_users = sql.select_where("users", lambda r: r["city"] == "SF")
    print(f"   SF 用户: {sf_users}")

    user_orders = sql.join("users", "orders", lambda u, o: u["id"] == o["user_id"])
    print(f"   JOIN users + orders:")
    for r in user_orders:
        print(f"     {r['name']}: ${r['amount']}")

    age_dist = sql.group_by_count("users", lambda r: r["age"])
    print(f"   年龄分布: {age_dist}")

    # HNSW
    hnsw = SimpleHNSW(dim=4, M=3)
    random.seed(42)
    for _ in range(20):
        vec = [random.gauss(0, 1) for _ in range(4)]
        hnsw.add(vec)
    query = [1.0, 0.5, 0.0, -0.5]
    results = hnsw.search(query, k=3)
    print(f"   HNSW 检索 (k=3): 相似度 {[f'{s:.3f}' for _, s in results]}")


# ============================================
# 👁️ CS227A: Robot Perception
# 多模态融合：视觉 + 触觉 + 语言
# ============================================

@dataclass
class VisualObject:
    name: str
    color: str
    shape: str
    position: tuple  # (x, y, z)
    confidence: float


@dataclass
class TactileReading:
    pressure: float
    texture: str  # 'smooth', 'rough', 'soft'
    temperature: float


class MultiModalPerceiver:
    """融合视觉 + 触觉 + 语言指令"""

    def __init__(self):
        self.object_db = {
            "apple": {"color": "red", "shape": "round", "texture": "smooth"},
            "ball": {"color": "any", "shape": "round", "texture": "smooth"},
            "book": {"color": "any", "shape": "rectangular", "texture": "rough"},
            "cup": {"color": "any", "shape": "cylindrical", "texture": "smooth"},
        }

    def perceive(self, visual: list[VisualObject], tactile: TactileReading,
                 instruction: str) -> dict:
        """综合多模态信息"""
        # 1. 视觉候选
        candidates = visual
        # 2. 用触觉过滤（pressure > 0.5 + soft → 苹果可能）
        if tactile.texture == "smooth" and tactile.pressure < 0.7:
            candidates = [c for c in candidates if c.shape in ["round", "cylindrical"]]
        elif tactile.texture == "rough":
            candidates = [c for c in candidates if c.shape == "rectangular"]

        # 3. 用语言指令过滤
        target_word = self._extract_target(instruction)
        if target_word:
            candidates = [c for c in candidates
                          if target_word in c.name.lower()
                          or self._object_matches(c, target_word)]

        if not candidates:
            return {"action": "scan", "reason": "未找到目标"}

        target = max(candidates, key=lambda c: c.confidence)
        # 计算抓取动作
        grasp = self._compute_grasp(target.position, tactile.pressure)

        return {
            "action": "grasp",
            "target": target.name,
            "position": target.position,
            "grasp_force": grasp["force"],
            "grasp_pose": grasp["pose"],
            "confidence": target.confidence,
        }

    def _extract_target(self, instruction: str) -> str:
        for word in self.object_db:
            if word in instruction.lower():
                return word
        return ""

    def _object_matches(self, obj: VisualObject, target: str) -> bool:
        info = self.object_db.get(target, {})
        if info.get("shape") == obj.shape:
            return True
        if info.get("color") != "any" and info.get("color") == obj.color:
            return True
        return False

    @staticmethod
    def _compute_grasp(position: tuple, pressure: float) -> dict:
        x, y, z = position
        # 简化：force 随压力调整
        force = max(0.3, min(1.0, 0.5 + pressure * 0.5))
        return {"force": force, "pose": (x, y, z - 0.05)}


def cs227a_demo():
    print("\n📋 CS227A: Robot Perception (Multi-Modal)")
    perceiver = MultiModalPerceiver()

    scenarios = [
        {
            "visual": [
                VisualObject("red_apple", "red", "round", (0.5, 0.3, 0.1), 0.9),
                VisualObject("book", "blue", "rectangular", (0.6, 0.4, 0.05), 0.7),
            ],
            "tactile": TactileReading(0.4, "smooth", 22.0),
            "instruction": "Pick up the apple",
        },
        {
            "visual": [
                VisualObject("cup", "white", "cylindrical", (0.4, 0.2, 0.15), 0.85),
            ],
            "tactile": TactileReading(0.6, "smooth", 60.0),  # 温度高（咖啡）
            "instruction": "Hold the cup carefully",
        },
    ]
    for sc in scenarios:
        result = perceiver.perceive(sc["visual"], sc["tactile"], sc["instruction"])
        print(f"   Instruction: {sc['instruction']}")
        print(f"   Tactile: pressure={sc['tactile'].pressure}, "
              f"texture={sc['tactile'].texture}, temp={sc['tactile'].temperature}°C")
        print(f"   → Action: {result['action']}, target={result.get('target', '-')}, "
              f"force={result.get('grasp_force', 0):.2f}")


# ============================================
# 主入口
# ============================================

def main():
    print("=" * 60)
    print("🎓 Stanford CS 第二批研究生项目")
    print("=" * 60)
    cs312_demo()
    cs224v_demo()
    cs238_demo()
    cs145_demo()
    cs227a_demo()
    print("\n" + "=" * 60)
    print("✅ 第二批研究生项目完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
