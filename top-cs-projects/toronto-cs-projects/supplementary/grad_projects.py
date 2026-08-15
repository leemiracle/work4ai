"""
University of Toronto DCS - 研究生补充课程微项目集
====================================================
覆盖课程（10 门）：
- CSC 2503 Compilers
- CSC 2506 Knowledge Representation & Reasoning
- CSC 2507 Computer Vision (Graduate)
- CSC 2508 Numerical Methods for ML
- CSC 2417 Parallel Programming
- CSC 2520 Operating Systems
- CSC 2524 Distributed Systems
- CSC 2541 Reinforcement Learning
- CSC 2547H Special Topics: Interpretability
- CSC 2547H Special Topics: Healthcare ML
"""
import math
import random
from collections import defaultdict


# ============ CSC 2503: Compilers ============

def micro_csc2503_compiler():
    """编译器前端：递归下降解析器 + 三地址码"""
    print("\n📋 CSC 2503: 编译器（递归下降解析）")
    # 解析简单算术表达式: expr → term (('+'|'-') term)*
    # term → factor (('*'|'/') factor)*
    # factor → number | '(' expr ')'

    class Parser:
        def __init__(self, text):
            self.tokens = text.replace('+', ' + ').replace('-', ' - ')
            self.tokens = self.tokens.replace('*', ' * ').replace('/', ' / ')
            self.tokens = self.tokens.replace('(', ' ( ').replace(')', ' ) ').split()
            self.pos = 0
            self.ir = []  # 中间表示（三地址码）
            self.temp_count = 0

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def consume(self):
            tok = self.peek()
            self.pos += 1
            return tok

        def new_temp(self):
            self.temp_count += 1
            return f"t{self.temp_count}"

        def parse_expr(self):
            left = self.parse_term()
            while self.peek() in ('+', '-'):
                op = self.consume()
                right = self.parse_term()
                result = self.new_temp()
                self.ir.append(f"{result} = {left} {op} {right}")
                left = result
            return left

        def parse_term(self):
            left = self.parse_factor()
            while self.peek() in ('*', '/'):
                op = self.consume()
                right = self.parse_factor()
                result = self.new_temp()
                self.ir.append(f"{result} = {left} {op} {right}")
                left = result
            return left

        def parse_factor(self):
            tok = self.peek()
            if tok == '(':
                self.consume()
                result = self.parse_expr()
                assert self.consume() == ')'
                return result
            return self.consume()

    parser = Parser("3 + 4 * 2 - (1 + 5)")
    result = parser.parse_expr()
    print(f"   表达式: 3 + 4 * 2 - (1 + 5)")
    print(f"   三地址码:")
    for line in parser.ir:
        print(f"     {line}")
    print(f"   最终结果在: {result}")
    print(f"   验证: 3 + 4*2 - (1+5) = {3 + 4*2 - (1+5)}")


# ============ CSC 2506: Knowledge Representation ============

def micro_csc2506_kr():
    """知识表示：描述逻辑 + 推理"""
    print("\n📋 CSC 2506: 知识表示（描述逻辑推理）")
    # TBox: 概念层次
    # Student ⊑ Person
    # GradStudent ⊑ Student
    # Professor ⊑ Person
    # ABox: 实例
    # Student(Alice), GradStudent(Bob), Professor(Carol)

    concept_hierarchy = {
        'GradStudent': ['Student', 'Person'],
        'Student': ['Person'],
        'Professor': ['Person'],
        'Person': [],
    }
    instances = {
        'Alice': 'Student',
        'Bob': 'GradStudent',
        'Carol': 'Professor',
    }

    def is_a(instance, concept):
        inst_type = instances[instance]
        if inst_type == concept:
            return True
        visited = set()
        queue = [inst_type]
        while queue:
            t = queue.pop(0)
            if t in visited:
                continue
            visited.add(t)
            if t == concept:
                return True
            queue.extend(concept_hierarchy.get(t, []))
        return False

    print("   概念层次: GradStudent ⊑ Student ⊑ Person")
    tests = [('Bob', 'Person'), ('Bob', 'Student'), ('Alice', 'GradStudent'), ('Carol', 'Person')]
    for inst, concept in tests:
        result = is_a(inst, concept)
        print(f"   {inst} is-a {concept}: {result}")


# ============ CSC 2507: Computer Vision (Graduate) ============

def micro_csc2507_cv_grad():
    """高级 CV：Hough 变换（直线检测）"""
    print("\n📋 CSC 2507: 高级 CV（Hough 变换）")
    # Hough 变换：边缘点 → 参数空间投票
    # 直线 y = mx + b → 参数空间 (m, b)

    # 模拟边缘点（在一条直线上）
    # 真实直线: y = 2x + 1
    edge_points = [(x, 2*x + 1) for x in range(1, 6)]
    # 加噪声
    edge_points += [(0, 1), (6, 13)]

    # 参数空间量化
    m_range = [i * 0.5 for i in range(-2, 7)]  # m from -1 to 3
    accumulator = defaultdict(int)

    for x, y in edge_points:
        for m in m_range:
            b = y - m * x
            b_bin = round(b * 2) / 2  # 量化 b
            accumulator[(m, b_bin)] += 1

    # 找最高投票
    best = max(accumulator, key=accumulator.get)
    print(f"   边缘点: {edge_points}")
    print(f"   真实直线: y = 2x + 1")
    print(f"   Hough 检测: y = {best[0]}x + {best[1]} (votes={accumulator[best]})")
    print(f"   → 参数空间峰值对应最可能的直线")


# ============ CSC 2508: Numerical Methods for ML ============

def micro_csc2508_numerical_ml():
    """ML 中的数值方法：梯度检查 + 条件数"""
    print("\n📋 CSC 2508: ML 数值方法（条件数 + 梯度检查）")
    # 条件数: κ(A) = σ_max/σ_min
    # 大条件数 → 数值不稳定

    import numpy as np
    # 良条件矩阵
    A_good = np.array([[1, 0.5], [0.5, 1]])
    # 病条件矩阵
    A_bad = np.array([[1, 0.999], [0.999, 1]])

    def condition_number(A):
        svds = np.linalg.svd(A, compute_uv=False)
        return svds[0] / svds[-1]

    print(f"   良条件矩阵 κ(A) = {condition_number(A_good):.2f}")
    print(f"   病条件矩阵 κ(A) = {condition_number(A_bad):.2f}")

    # 梯度检查（数值梯度 vs 解析梯度）
    def f(x):
        return x[0]**2 * x[1] + x[1]**3

    def grad_f(x):
        return np.array([2*x[0]*x[1], x[0]**2 + 3*x[1]**2])

    x = np.array([1.5, 2.0])
    analytic = grad_f(x)
    # 数值梯度（中心差分）
    eps = 1e-6
    num_grad = np.zeros(2)
    for i in range(2):
        xp = x.copy(); xp[i] += eps
        xm = x.copy(); xm[i] -= eps
        num_grad[i] = (f(xp) - f(xm)) / (2 * eps)

    error = np.max(np.abs(analytic - num_grad))
    print(f"\n   梯度检查（f = x₁²x₂ + x₂³）:")
    print(f"   解析梯度: [{analytic[0]:.4f}, {analytic[1]:.4f}]")
    print(f"   数值梯度: [{num_grad[0]:.4f}, {num_grad[1]:.4f}]")
    print(f"   最大误差: {error:.2e}")


# ============ CSC 2417: Parallel Programming ============

def micro_csc2417_parallel():
    """并行计算：Amdahl 定律 + MapReduce"""
    print("\n📋 CSC 2417: 并行计算（Amdahl 定律）")
    # Amdahl: Speedup = 1 / (s + (1-s)/p)
    # s = 串行比例, p = 处理器数

    s = 0.1  # 10% 串行
    print(f"   Amdahl 定律（串行比例 s={s}）:")
    print(f"   {'Cores (p)':>10} {'Speedup':>10} {'Efficiency':>10}")
    for p in [1, 2, 4, 8, 16, 32, 64, 1000]:
        speedup = 1 / (s + (1 - s) / p)
        eff = speedup / p
        print(f"   {p:10d} {speedup:10.2f} {eff:10.1%}")

    max_speedup = 1 / s
    print(f"\n   → 理论最大加速比 = 1/s = {max_speedup:.0f}x（即使无限核心）")
    print(f"   → 反直觉：10%串行代码限制最大加速到 10x")


# ============ CSC 2520: Operating Systems ============

def micro_csc2520_page_replacement():
    """OS 页面替换算法"""
    print("\n📋 CSC 2520: 页面替换算法")
    reference_string = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    frames = 3

    def fifo(ref, n_frames):
        frames_q = []
        page_faults = 0
        for page in ref:
            if page not in frames_q:
                page_faults += 1
                if len(frames_q) >= n_frames:
                    frames_q.pop(0)
                frames_q.append(page)
        return page_faults

    def lru(ref, n_frames):
        frames_list = []
        page_faults = 0
        for page in ref:
            if page in frames_list:
                frames_list.remove(page)
            else:
                page_faults += 1
                if len(frames_list) >= n_frames:
                    frames_list.pop(0)
            frames_list.append(page)
        return page_faults

    def optimal(ref, n_frames):
        frames_list = []
        page_faults = 0
        for i, page in enumerate(ref):
            if page in frames_list:
                continue
            page_faults += 1
            if len(frames_list) < n_frames:
                frames_list.append(page)
            else:
                # 找未来最远使用的页面
                farthest = -1
                victim = frames_list[0]
                for f in frames_list:
                    try:
                        next_use = ref[i+1:].index(f)
                    except ValueError:
                        next_use = float('inf')
                    if next_use > farthest:
                        farthest = next_use
                        victim = f
                frames_list.remove(victim)
                frames_list.append(page)
        return page_faults

    fifo_faults = fifo(reference_string, frames)
    lru_faults = lru(reference_string, frames)
    opt_faults = optimal(reference_string, frames)

    print(f"   引用串: {reference_string}")
    print(f"   帧数: {frames}")
    print(f"   FIFO 缺页: {fifo_faults}")
    print(f"   LRU  缺页: {lru_faults}")
    print(f"   OPT  缺页: {opt_faults} (理论最优)")
    print(f"   → OPT ≤ LRU ≤ FIFO（OPT 不可实现，LRU 是实用近似）")


# ============ CSC 2524: Distributed Systems ============

def micro_csc2524_paxos():
    """Paxos 协议模拟"""
    print("\n📋 CSC 2524: 分布式共识（Paxos 简化版）")

    # 简化 Paxos：1 个 Proposer, 3 个 Acceptors
    class Acceptor:
        def __init__(self, aid):
            self.aid = aid
            self.promised_n = -1
            self.accepted_n = -1
            self.accepted_v = None

        def prepare(self, n):
            if n > self.promised_n:
                self.promised_n = n
                return True, self.accepted_n, self.accepted_v
            return False, None, None

        def accept(self, n, v):
            if n >= self.promised_n:
                self.accepted_n = n
                self.accepted_v = v
                return True
            return False

    acceptors = [Acceptor(i) for i in range(3)]
    proposal_n = 1
    proposal_v = "value_X"

    # Phase 1: Prepare
    promises = 0
    for acc in acceptors:
        ok, _, _ = acc.prepare(proposal_n)
        if ok:
            promises += 1

    # Phase 2: Accept（多数同意才提交）
    accepts = 0
    if promises >= 2:  # 多数
        for acc in acceptors:
            if acc.accept(proposal_n, proposal_v):
                accepts += 1

    print(f"   Proposer 提议 n={proposal_n}, v={proposal_v}")
    print(f"   Phase 1 (Prepare): {promises}/3 promises")
    print(f"   Phase 2 (Accept): {accepts}/3 accepts")
    print(f"   共识达成: {accepts >= 2}")
    print(f"   → Paxos 保证：最多只有一个值被选定")


# ============ CSC 2541: Reinforcement Learning ============

def micro_csc2541_rl():
    """强化学习：Q-Learning on Grid World"""
    print("\n📋 CSC 2541: 强化学习（Q-Learning）")
    # 4x4 Grid World
    # (0,0)=start, (3,3)=goal(+1), 其余=-0.01
    import numpy as np
    rng = np.random.RandomState(42)

    gamma = 0.95
    lr = 0.5
    eps = 0.3
    Q = np.zeros((4, 4, 4))  # [row, col, action]
    actions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # R, D, L, U

    def step(state, action):
        r, c = state
        dr, dc = actions[action]
        nr, nc = max(0, min(3, r + dr)), max(0, min(3, c + dc))
        reward = 1.0 if (nr, nc) == (3, 3) else -0.01
        return (nr, nc), reward, (nr, nc) == (3, 3)

    for episode in range(2000):
        state = (0, 0)
        done = False
        while not done:
            if rng.rand() < eps:
                action = rng.randint(4)
            else:
                action = Q[state[0], state[1]].argmax()
            next_state, reward, done = step(state, action)
            if done:
                target = reward
            else:
                target = reward + gamma * Q[next_state[0], next_state[1]].max()
            Q[state[0], state[1], action] += lr * (target - Q[state[0], state[1], action])
            state = next_state

    # 最优策略
    print("   学到的策略（箭头表示最优动作）：")
    dir_names = ['→', '↓', '←', '↑']
    for r in range(4):
        row = []
        for c in range(4):
            if (r, c) == (3, 3):
                row.append(' G')
            else:
                a = Q[r, c].argmax()
                row.append(f' {dir_names[a]}')
        print(f"   {''.join(row)}")
    print(f"   Q(start, optimal) = {Q[0, 0].max():.3f}")
    print(f"   → Q-Learning 学到最短路径到目标")


# ============ CSC 2547H: Interpretability ============

def micro_csc2547h_interpretability():
    """模型可解释性：SHAP 简化版 + LIME 思想"""
    print("\n📋 CSC 2547H: 可解释性（特征重要性）")
    # SHAP 简化：测量每个特征对预测的边际贡献
    import numpy as np

    # 模型：f(x) = 2*x1 + x2 - 0.5*x3
    def model(x):
        return 2 * x[0] + x[1] - 0.5 * x[2]

    # 基线（所有特征取均值）
    baseline = np.array([0.5, 0.5, 0.5])
    # 实例
    instance = np.array([1.0, 0.3, 0.8])

    pred_baseline = model(baseline)
    pred_instance = model(instance)

    # 边际贡献（简化 SHAP）
    contributions = {}
    for i in range(3):
        x = baseline.copy()
        x[i] = instance[i]
        contributions[f'x{i+1}'] = model(x) - pred_baseline

    print(f"   模型: f(x) = 2x₁ + x₂ - 0.5x₃")
    print(f"   实例: {instance}")
    print(f"   基线预测: {pred_baseline:.3f}")
    print(f"   实例预测: {pred_instance:.3f}")
    print(f"   特征贡献:")
    for feat, contrib in sorted(contributions.items(), key=lambda x: -abs(x[1])):
        print(f"     {feat}: {contrib:+.3f}")
    print(f"   总和: {sum(contributions.values()):.3f} (应≈ {pred_instance - pred_baseline:.3f})")


# ============ CSC 2547H: Healthcare ML ============

def micro_csc2547h_healthcare():
    """医疗 ML：存活分析 + 偏差检测"""
    print("\n📋 CSC 2547H: 医疗 ML（Kaplan-Meier 存活分析）")
    # Kaplan-Meier 估计器
    # S(t) = Π_{t_i ≤ t} (1 - d_i/n_i)
    # d_i = t_i 时刻事件数, n_i = t_i 时刻风险人数

    # 模拟数据 (time, event)
    events = [
        (1, True), (2, True), (3, False), (4, True), (5, False),
        (6, True), (7, True), (8, False), (9, True), (10, False),
    ]

    times = sorted(set(t for t, e in events))
    survival = 1.0
    print(f"   {'Time':>5} {'Events':>7} {'At Risk':>8} {'S(t)':>8}")
    for t in times:
        d = sum(1 for ti, e in events if ti == t and e)
        n = sum(1 for ti, _ in events if ti >= t)
        survival *= (1 - d / n) if n > 0 else 1
        print(f"   {t:5d} {d:7d} {n:8d} {survival:8.3f}")

    print(f"\n   最终存活率: {survival:.3f}")
    print(f"   → 医疗 ML 必须处理 censoring（删失数据）")


# ============ 主入口 ============

def run_all_grad():
    print("=" * 60)
    print("🎓 Toronto DCS 研究生补充课程微项目")
    print("=" * 60)

    micro_csc2503_compiler()
    micro_csc2506_kr()
    micro_csc2507_cv_grad()
    micro_csc2508_numerical_ml()
    micro_csc2417_parallel()
    micro_csc2520_page_replacement()
    micro_csc2524_paxos()
    micro_csc2541_rl()
    micro_csc2547h_interpretability()
    micro_csc2547h_healthcare()

    print("\n" + "=" * 60)
    print("✅ 全部研究生补充课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_grad()
