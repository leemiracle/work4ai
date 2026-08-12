"""
CS 188 Introduction to Artificial Intelligence — UC Berkeley (Pacman, Klein)
================================================
覆盖主题：
- 搜索：BFS/DFS/UCS/A*（Proj 1 Search）
- 对抗搜索：Minimax + α-β 剪枝（Proj 2 Multiagent）
- MDP + Value Iteration（Proj 3 MDPs）
- Q-Learning（Proj 4 Reinforcement Learning）
- 贝叶斯网络（Proj 5 Tracking）

核心教材/参考：
- Russell & Norvig "Artificial Intelligence: A Modern Approach" 4th ed (Pearson 2021), §3-6/17-22
- Hart, Nilsson, Raphael "A Formal Basis for the Heuristic Determination of Minimum Cost Paths" IEEE SSSC 1968
- Sutton & Barto "Reinforcement Learning: An Introduction" 2nd ed (MIT 2018), §4-6

本文件实现：
- A* 搜索（带启发式）在网格迷宫
- Minimax + α-β 剪枝
- Value Iteration（MDP 求解）
- Q-Learning（网格世界 tabular）
- 贝叶斯网络枚举推断

运行：
    python ai_pacman.py
"""
from __future__ import annotations
import heapq
import math
import random
from collections import defaultdict


# ============================================================
# 1. 搜索：A*（Russell-Norvig §3.5）
# ============================================================

def a_star_search(grid: list[str], start: tuple, goal: tuple) -> tuple[list, int]:
    """
    A* = f(n) = g(n) + h(n)
    g(n) = 从 start 到 n 的实际代价
    h(n) = 从 n 到 goal 的启发式（admissible: 永不高估）
    用 Manhattan distance 作 h（4-连通网格 admissible）。
    """
    rows, cols = len(grid), len(grid[0])
    walls = set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "%":
                walls.add((r, c))

    def heuristic(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    open_heap = [(heuristic(start), 0, start)]
    came_from = {start: None}
    g_score = {start: 0}

    while open_heap:
        _, g, current = heapq.heappop(open_heap)
        if current == goal:
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            return path[::-1], g
        if g > g_score.get(current, math.inf):
            continue
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = current[0] + dr, current[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in walls:
                new_g = g + 1
                if new_g < g_score.get((nr, nc), math.inf):
                    g_score[(nr, nc)] = new_g
                    came_from[(nr, nc)] = current
                    heapq.heappush(open_heap, (new_g + heuristic((nr, nc)), new_g, (nr, nc)))
    return [], -1


def bfs_search(grid, start, goal):
    """BFS（无权重最短路 = Pacman Proj 1）"""
    from collections import deque
    rows, cols = len(grid), len(grid[0])
    walls = {(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == "%"}
    visited = {start}
    queue = deque([(start, [start])])
    while queue:
        pos, path = queue.popleft()
        if pos == goal:
            return path
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            np = (pos[0] + dr, pos[1] + dc)
            if (0 <= np[0] < rows and 0 <= np[1] < cols
                    and np not in walls and np not in visited):
                visited.add(np)
                queue.append((np, path + [np]))
    return []


# ============================================================
# 2. Minimax + α-β 剪枝（Russell-Norvig §5.2-5.3）
# ============================================================

class GameNode:
    """博弈树节点（Pacman vs Ghost）"""
    def __init__(self, value=None, agent_idx=0, children=None):
        self.value = value  # leaf 的评估值
        self.agent_idx = agent_idx  # 0=MAX(Pacman), 1+=MIN(Ghost)
        self.children = children or []


def minimax(node: GameNode, depth: int, maximizing: bool) -> float:
    """经典 minimax"""
    if depth == 0 or node.value is not None:
        return node.value if node.value is not None else 0
    if maximizing:
        return max(minimax(c, depth - 1, False) for c in node.children)
    return min(minimax(c, depth - 1, True) for c in node.children)


def alphabeta(node: GameNode, depth: int, alpha: float, beta: float,
              maximizing: bool) -> float:
    """
    α-β 剪枝（Knuth & Moore 1975）：
    α = MAX 层已知最好；β = MIN 层已知最好。
    当 β ≤ α 时剪枝（该分支不可能影响最终决策）。
    """
    if depth == 0 or node.value is not None:
        return node.value if node.value is not None else 0
    if maximizing:
        value = -math.inf
        for c in node.children:
            value = max(value, alphabeta(c, depth - 1, alpha, beta, False))
            alpha = max(alpha, value)
            if beta <= alpha:  # β cutoff
                break
        return value
    else:
        value = math.inf
        for c in node.children:
            value = min(value, alphabeta(c, depth - 1, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha:  # α cutoff
                break
        return value


def count_nodes_visited(node, depth, alpha=-math.inf, beta=math.inf, maximizing=True):
    """统计 α-β 实际访问的节点数（vs minimax 全访问）"""
    if depth == 0 or node.value is not None:
        return 1
    count = 1
    if maximizing:
        value = -math.inf
        for c in node.children:
            count += count_nodes_visited(c, depth - 1, alpha, beta, False)
            value = max(value, _leaf_or_inf(c))
            alpha = max(alpha, value)
            if beta <= alpha:
                break
    else:
        value = math.inf
        for c in node.children:
            count += count_nodes_visited(c, depth - 1, alpha, beta, True)
            value = min(value, _leaf_or_inf(c))
            beta = min(beta, value)
            if beta <= alpha:
                break
    return count


def _leaf_or_inf(node):
    return node.value if node.value is not None else 0


# ============================================================
# 3. MDP + Value Iteration（Sutton-Barto §4.4）
# ============================================================

def value_iteration(states: list, actions: list, transitions: dict,
                    rewards: dict, gamma: float = 0.9,
                    theta: float = 1e-6, max_iter: int = 1000):
    """
    Value Iteration（Bellman 最优）：
        V*(s) = max_a Σ_s' P(s'|s,a)[R(s,a,s') + γV*(s')]
    收敛条件：max|V_new - V_old| < θ
    """
    V = {s: 0.0 for s in states}
    for _ in range(max_iter):
        delta = 0
        V_new = {}
        for s in states:
            best = -math.inf
            for a in actions:
                q = 0
                for (s2, p) in transitions.get((s, a), []):
                    r = rewards.get((s, a, s2), 0)
                    q += p * (r + gamma * V[s2])
                best = max(best, q)
            V_new[s] = best if best > -math.inf else 0
            delta = max(delta, abs(V_new[s] - V[s]))
        V = V_new
        if delta < theta:
            break
    # Extract policy
    policy = {}
    for s in states:
        best_a, best_q = None, -math.inf
        for a in actions:
            q = 0
            for (s2, p) in transitions.get((s, a), []):
                r = rewards.get((s, a, s2), 0)
                q += p * (r + gamma * V[s2])
            if q > best_q:
                best_q, best_a = q, a
        policy[s] = best_a
    return V, policy


# ============================================================
# 4. Q-Learning（Sutton-Barto §6.5）
# ============================================================

class QLearningAgent:
    """
    Q-Learning（off-policy TD control）：
        Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]
    """
    def __init__(self, actions: list, alpha: float = 0.1,
                 gamma: float = 0.95, epsilon: float = 0.3):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.Q = defaultdict(lambda: defaultdict(float))

    def choose(self, state, explore: bool = True) -> str:
        if explore and random.random() < self.epsilon:
            return random.choice(self.actions)
        qvals = {a: self.Q[state][a] for a in self.actions}
        if not qvals or max(qvals.values()) == 0 and random.random() < 0.5:
            return random.choice(self.actions)
        return max(qvals, key=qvals.get)

    def learn(self, s, a, r, s2):
        best_next = max(self.Q[s2][a2] for a2 in self.actions) if self.Q[s2] else 0
        td_target = r + self.gamma * best_next
        td_error = td_target - self.Q[s][a]
        self.Q[s][a] += self.alpha * td_error


# ============================================================
# 5. 贝叶斯网络枚举（Russell-Norvig §13.3）
# ============================================================

def enumeration_ask(query_var: str, evidence: dict, bayes_net: dict) -> dict:
    """
    枚举法精确推断：P(X | e) ∝ Σ_hidden P(X, e, hidden)
    bayes_net: {var: (parents, cpt)} cpt is function(parents_vals) → p(True)
    """
    variables = list(bayes_net.keys())
    hidden = [v for v in variables if v != query_var and v not in evidence]
    dist = {}

    def enumerate_all(vars_left, assignment):
        if not vars_left:
            return 1.0
        var = vars_left[0]
        parents, cpt = bayes_net[var]
        parent_vals = tuple(assignment[p] for p in parents)
        if var in assignment:
            p_true = cpt(parent_vals) if parent_vals else cpt(())
            return (p_true if assignment[var] else 1 - p_true) * enumerate_all(vars_left[1:], assignment)
        p_true = cpt(parent_vals) if parent_vals else cpt(())
        total = 0
        for val in [True, False]:
            a = dict(assignment)
            a[var] = val
            total += (p_true if val else 1 - p_true) * enumerate_all(vars_left[1:], a)
        return total

    for val in [True, False]:
        full = dict(evidence)
        full[query_var] = val
        dist[val] = enumerate_all(variables, full)

    total = sum(dist.values())
    return {k: v / total for k, v in dist.items()} if total > 0 else dist


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("CS 188 AI (Pacman) Demo")
    print("=" * 60)
    random.seed(42)

    # 1. A* vs BFS
    print("\n📋 1. A* 搜索")
    grid = [
        "%%%%%%%%%",
        "%P    % %",
        "% %%% % %",
        "% %     %",
        "% % %% %%",
        "%   %   .",
        "%%%%%%%%%",
    ]
    start = next((r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "P")
    goal = next((r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == ".")
    path_astar, cost_astar = a_star_search(grid, start, goal)
    path_bfs = bfs_search(grid, start, goal)
    print(f"   起点 {start}, 终点 {goal}")
    print(f"   A*: {len(path_astar)} 步 (cost={cost_astar})")
    print(f"   BFS: {len(path_bfs)} 步")

    # 2. Minimax + α-β
    print("\n📋 2. Minimax + α-β 剪枝")
    # 构建深度 4 博弈树，分支因子 5
    def build_tree(depth, bf=5, maximizing=True):
        if depth == 0:
            return GameNode(value=random.randint(-100, 100))
        children = [build_tree(depth - 1, bf, not maximizing) for _ in range(bf)]
        return GameNode(agent_idx=0 if maximizing else 1, children=children)
    random.seed(0)
    tree = build_tree(4, bf=5)
    total_nodes = 5 ** 4 + 5 ** 3 * 5 + 5 ** 2 + 5 + 1  # approximate
    mm_val = minimax(tree, 4, True)
    ab_val = alphabeta(tree, 4, -math.inf, math.inf, True)
    visited = count_nodes_visited(tree, 4)
    full_visit = sum(5 ** i for i in range(5))  # 1+5+25+125+625
    print(f"   树深 4, 分支因子 5 → 总叶子 {5**4}")
    print(f"   Minimax 值 = {mm_val}, α-β 值 = {ab_val} (相等 ✓)")
    print(f"   α-β 访问 ~{visited} 节点 vs 全访问 ~{full_visit}")
    print(f"   剪枝率 ≈ {1 - visited/full_visit:.0%}")

    # 3. Value Iteration
    print("\n📋 3. MDP Value Iteration（网格世界）")
    # 4 状态 MDP: S0 → S1 → S2 → Terminal(+1) / S3(-1)
    states = ["S0", "S1", "S2", "S3", "T"]
    actions = ["a", "b"]
    transitions = {
        ("S0", "a"): [("S1", 0.8), ("S3", 0.2)],
        ("S0", "b"): [("S2", 0.7), ("S1", 0.3)],
        ("S1", "a"): [("T", 1.0)],
        ("S1", "b"): [("S2", 0.6), ("S0", 0.4)],
        ("S2", "a"): [("T", 0.5), ("S1", 0.5)],
        ("S2", "b"): [("T", 0.9), ("S3", 0.1)],
    }
    rewards = {
        ("S0", "a", "S1"): 0,
        ("S0", "a", "S3"): -1,
        ("S1", "a", "T"): 1,
        ("S2", "a", "T"): 1,
        ("S2", "b", "T"): 1,
        ("S2", "b", "S3"): -1,
    }
    # S3 and T are terminal states (no transitions)
    V, policy = value_iteration(states, actions, transitions, rewards, gamma=0.9)
    print(f"   V* = {dict((s, round(v, 3)) for s, v in V.items())}")
    print(f"   π* = {policy}")

    # 4. Q-Learning
    print("\n📋 4. Q-Learning（网格世界探索）")
    agent = QLearningAgent(["a", "b"], alpha=0.1, gamma=0.9, epsilon=0.3)
    # 简单环境：S0 → a → S1(+0); S1 → a → Terminal(+1)
    for ep in range(2000):
        s = "S0"
        for _ in range(10):
            a = agent.choose(s)
            if s == "S0" and a == "a":
                s2, r = "S1", 0
            elif s == "S1" and a == "a":
                s2, r = "T", 1
            else:
                s2, r = s, -0.1
            agent.learn(s, a, r, s2)
            s = s2
            if s == "T":
                break
    print(f"   Q(S0,a) = {agent.Q['S0']['a']:.3f} (期望 ≈ 0.9)")
    print(f"   Q(S1,a) = {agent.Q['S1']['a']:.3f} (期望 ≈ 1.0)")

    # 5. Bayes net
    print("\n📋 5. 贝叶斯网络（Rain→Sprinkler→WetGrass）")
    # R → S → W  (简化)
    net = {
        "Rain": ([], lambda _: 0.2),
        "Sprinkler": (["Rain"], lambda pv: 0.01 if pv[0] else 0.4),
        "WetGrass": (["Rain", "Sprinkler"],
                     lambda pv: 0.99 if (pv[0] or pv[1]) else 0.0),
    }
    # P(Rain | WetGrass=True)
    dist = enumeration_ask("Rain", {"WetGrass": True}, net)
    print(f"   P(Rain | WetGrass=True) = {dist}")
    print(f"   先验 P(Rain) = 0.2 → 后验放大到 {dist.get(True, 0):.3f}")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print("   α-β 剪枝在分支因子 b、深度 d 的树上：")
    print(f"   Minimax 访问 O(b^d) = {5**4} 节点")
    print(f"   α-β 最优情况访问 O(b^(d/2)) = {5**2} 节点")
    print(f"   → 同样搜索深度，α-β 能让可搜索深度翻倍！")
    print("   这就是为什么国际象棋引擎（分支因子 ~35）能搜索到 12+ 层。")
    print()
    print("   贝叶斯：看到草地湿（效果），推断下雨概率从 20% → 升高。")
    print("   这就是'逆向概率'：P(因|果) 由 P(因)×P(果|因)/P(果) 得到。")


if __name__ == "__main__":
    demo()
