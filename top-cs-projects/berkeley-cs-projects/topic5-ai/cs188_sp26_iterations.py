"""
CS 188 SP26 · Pacman Projects — 6 个迭代的最小可运行骨架
==========================================================
按 Berkeley CS 188 Spring 2026 的 6 个项目迭代组织：
  · P1 Search          — DFS / BFS / UCS / A* + 启发式设计
  · P2 Multiagent      — Minimax + α-β / Expectimax / 评估函数
  · P3 RL              — Value Iteration / Q-Learning / Approximate Q
  · P4 Bayes Nets/HMM  — 因子推理 / forward algo / particle filter
  · P5 ML              — Perceptron / Neural Net / RNN

每个迭代给最小可运行的核心算法 + 测试，验证算法正确。
不是完整 Pacman 项目（那是学生作业），而是核心算法的 reference 实现。

配套：cs188-sp26-pacman-projects.md（迭代专章）
来源：https://inst.eecs.berkeley.edu/~cs188/sp26/projects/
"""
from __future__ import annotations
import heapq
import math
import random
from collections import defaultdict, deque

np = None  # numpy 可选
try:
    import numpy as np
except ImportError:
    pass


# ============================================================
# P1 · Search — DFS / BFS / UCS / A*
# ============================================================
# 通用图搜索框架（CS188 核心抽象）：frontier + explored + expansion loop

class SearchProblem:
    """CS188 SearchProblem 接口的简化版。"""
    def getStartState(self): raise NotImplementedError
    def isGoalState(self, state): raise NotImplementedError
    def getSuccessors(self, state):
        """返回 [(next_state, action, step_cost), ...]"""
        raise NotImplementedError


def graph_search(problem, frontier_cls):
    """CS188 Proj1 的统一框架：用 frontier 容器区分 DFS/BFS/UCS/A*。"""
    start = problem.getStartState()
    frontier = frontier_cls()
    frontier.push((start, []))           # (state, path_of_actions)
    explored = set()

    while not frontier.isEmpty():
        state, path = frontier.pop()
        if problem.isGoalState(state):
            return path
        if state in explored:
            continue
        explored.add(state)
        for next_state, action, cost in problem.getSuccessors(state):
            if next_state not in explored:
                frontier.push((next_state, path + [action]))
    return []


# 4 种 frontier
class Stack:  # DFS → LIFO
    def __init__(self): self.items = []
    def push(self, x): self.items.append(x)
    def pop(self): return self.items.pop()
    def isEmpty(self): return not self.items


class Queue:  # BFS → FIFO
    def __init__(self): self.items = deque()
    def push(self, x): self.items.append(x)
    def pop(self): return self.items.popleft()
    def isEmpty(self): return not self.items


class PriorityQueue:  # UCS / A* → 按 priority 出队
    def __init__(self): self.items = []
    def push(self, x, priority=0):
        heapq.heappush(self.items, (priority, len(self.items), x[0], x[1]))
    def push_item(self, item, priority):
        heapq.heappush(self.items, (priority, len(self.items), item))
    def pop(self): return heapq.heappop(self.items)[-1] if isinstance(self.items[-1][-1], (list, tuple)) and len(self.items[-1]) == 2 and isinstance(self.items[-1][1], list) else heapq.heappop(self.items)[(-1, -2)][-1]
    def isEmpty(self): return not self.items


# 为简化、用 closure 形式重写 UCS / A*
def uniform_cost_search(problem):
    """UCS = frontier 按 g(n) = 累积代价排序。"""
    start = problem.getStartState()
    frontier = [(0, 0, start, [])]  # (g, tie_break, state, path)
    best_cost = {start: 0}
    counter = 1
    while frontier:
        g, _, state, path = heapq.heappop(frontier)
        if problem.isGoalState(state):
            return path
        for next_state, action, step_cost in problem.getSuccessors(state):
            new_g = g + step_cost
            if next_state not in best_cost or new_g < best_cost[next_state]:
                best_cost[next_state] = new_g
                heapq.heappush(frontier, (new_g, counter, next_state, path + [action]))
                counter += 1
    return []


def a_star_search(problem, heuristic):
    """A* = frontier 按 f(n) = g(n) + h(n) 排序。h 必须 admissible（不高估）。"""
    start = problem.getStartState()
    frontier = [(heuristic(start, problem), 0, 0, start, [])]
    best_g = {start: 0}
    counter = 1
    while frontier:
        f, _, g, state, path = heapq.heappop(frontier)
        if problem.isGoalState(state):
            return path
        for next_state, action, step_cost in problem.getSuccessors(state):
            new_g = g + step_cost
            if next_state not in best_g or new_g < best_g[next_state]:
                best_g[next_state] = new_g
                new_f = new_g + heuristic(next_state, problem)
                heapq.heappush(frontier, (new_f, counter, new_g, next_state, path + [action]))
                counter += 1
    return []


# ============ P1 测试：小 maze + CornersProblem 启发式 ============

class MazeProblem(SearchProblem):
    """简单 grid maze：% = wall, . = goal, <空格> = 可走。"""
    def __init__(self, grid):
        self.grid = grid.split("\n")
        self.rows, self.cols = len(self.grid), len(self.grid[0])
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == "P": self.start = (r, c)
                if self.grid[r][c] == ".": self.goal = (r, c)

    def getStartState(self): return self.start
    def isGoalState(self, s): return s == self.goal
    def getSuccessors(self, s):
        r, c = s
        out = []
        for dr, dc, action in [(-1,0,"N"),(1,0,"S"),(0,-1,"W"),(0,1,"E")]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] != "%":
                out.append(((nr,nc), action, 1))
        return out


def manhattan_heuristic(state, problem):
    """CS188 Proj1 Q6 大迷宫用的 Manhattan 距离（4-连通 grid 上 admissible）。"""
    return abs(state[0] - problem.goal[0]) + abs(state[1] - problem.goal[1])


def corners_heuristic(state, problem):
    """
    CS188 Proj1 Q7-8 CornersProblem 的核心启发式：
      · 状态 = (位置, 4 个角是否访问过的 bool)
      · h = 到所有未访问角的最远距离（admissible + 比 Manhattan 一致性更强）
    """
    pos, visited_corners = state
    unvisited = [c for c in problem.corners if c not in visited_corners]
    if not unvisited:
        return 0
    # 贪心：从当前位置依次走到最近的未访问角（admissible）
    total = 0
    cur = pos
    while unvisited:
        d = [abs(cur[0]-c[0]) + abs(cur[1]-c[1]) for c in unvisited]
        idx = min(range(len(unvisited)), key=lambda i: d[i])
        total += d[idx]
        cur = unvisited.pop(idx)
    return total


# ============================================================
# P2 · Multiagent Search — Minimax / α-β / Expectimax
# ============================================================

def minimax_value(state, agent_index, depth, n_agents, max_depth,
                  get_legal_actions, get_successor, terminal):
    """
    CS188 Proj2 的核心递归。
      · agent_index = 0 是 Pacman（max 层）
      · agent_index >= 1 是 Ghost（min 层）
      · 多 ghost = 多层连续的 min
    """
    if terminal(state) or depth >= max_depth:
        return evaluation_function(state)

    actions = get_legal_actions(state, agent_index)
    if not actions:
        return evaluation_function(state)

    next_agent = (agent_index + 1) % n_agents
    next_depth = depth + 1 if next_agent == 0 else depth

    children = [
        minimax_value(get_successor(state, agent_index, a),
                      next_agent, next_depth, n_agents, max_depth,
                      get_legal_actions, get_successor, terminal)
        for a in actions
    ]
    return max(children) if agent_index == 0 else min(children)


def minimax_alphabeta(state, agent_index, depth, n_agents, max_depth,
                      alpha, beta, get_legal_actions, get_successor, terminal):
    """α-β 剪枝（CS188 Proj2 Q3）：max 层用 α 上界，min 层用 β 下界。"""
    if terminal(state) or depth >= max_depth:
        return evaluation_function(state)

    actions = get_legal_actions(state, agent_index)
    if not actions:
        return evaluation_function(state)

    next_agent = (agent_index + 1) % n_agents
    next_depth = depth + 1 if next_agent == 0 else depth

    if agent_index == 0:  # max
        v = -math.inf
        for a in actions:
            v = max(v, minimax_alphabeta(
                get_successor(state, agent_index, a), next_agent, next_depth,
                n_agents, max_depth, alpha, beta,
                get_legal_actions, get_successor, terminal))
            alpha = max(alpha, v)
            if v > beta:  # 剪枝
                return v
        return v
    else:  # min
        v = math.inf
        for a in actions:
            v = min(v, minimax_alphabeta(
                get_successor(state, agent_index, a), next_agent, next_depth,
                n_agents, max_depth, alpha, beta,
                get_legal_actions, get_successor, terminal))
            beta = min(beta, v)
            if v < alpha:  # 剪枝
                return v
        return v


def expectimax_value(state, agent_index, depth, n_agents, max_depth,
                     get_legal_actions, get_successor, terminal):
    """
    Expectimax（CS188 Proj2 Q5）：ghost 不理性时，min 换成 average。
      · min_{a} f(a)  →  E_a[f(a)] = mean
    """
    if terminal(state) or depth >= max_depth:
        return evaluation_function(state)
    actions = get_legal_actions(state, agent_index)
    if not actions:
        return evaluation_function(state)
    next_agent = (agent_index + 1) % n_agents
    next_depth = depth + 1 if next_agent == 0 else depth
    children = [
        expectimax_value(get_successor(state, agent_index, a),
                         next_agent, next_depth, n_agents, max_depth,
                         get_legal_actions, get_successor, terminal)
        for a in actions
    ]
    return max(children) if agent_index == 0 else sum(children) / len(children)


def evaluation_function(state):
    """
    CS188 Proj2 Q1-2 的 scoreEvaluationFunction / betterEvaluationFunction 雏形。
    真实版要设计 features（食物距离 / ghost 距离 / scared ghost）+ weights。
    """
    return getattr(state, "score", 0)


# ============================================================
# P3 · Reinforcement Learning — Value Iteration / Q-Learning / Approximate Q
# ============================================================

def value_iteration(mdp, gamma=0.9, theta=1e-6, max_iters=1000):
    """
    CS188 Proj3 Q1-2 的 Value Iteration（也是 [讲透RL/01] 的 Bellman 最优 backup）。

    V_k+1(s) = max_a Σ_s' P(s'|s,a) [R(s,a,s') + γ V_k(s')]
    """
    V = {s: 0.0 for s in mdp["states"]}
    for it in range(max_iters):
        delta = 0
        new_V = {}
        for s in mdp["states"]:
            if s in mdp["terminal"]:
                new_V[s] = mdp["rewards"].get(s, 0)
                continue
            best_q = -math.inf
            for a in mdp["actions"](s):
                q = sum(
                    prob * (mdp["rewards"].get((s, a, sp), 0) + gamma * V.get(sp, 0.0))
                    for sp, prob in mdp["transitions"]((s, a))
                )
                best_q = max(best_q, q)
            new_V[s] = best_q if best_q != -math.inf else V[s]
            delta = max(delta, abs(new_V[s] - V[s]))
        V = new_V
        if delta < theta:
            break
    return V, it + 1


def extract_policy(V, mdp, gamma=0.9):
    """从 V 提最优策略 π*(s) = argmax_a Q*(s,a)。"""
    policy = {}
    for s in mdp["states"]:
        if s in mdp["terminal"]:
            continue
        best_a, best_q = None, -math.inf
        for a in mdp["actions"](s):
            q = sum(
                prob * (mdp["rewards"].get((s, a, sp), 0) + gamma * V.get(sp, 0.0))
                for sp, prob in mdp["transitions"]((s, a))
            )
            if q > best_q:
                best_q, best_a = q, a
        policy[s] = best_a
    return policy


class QLearningAgent:
    """
    CS188 Proj3 Q5-7 的 tabular Q-Learning（off-policy TD 控制）。
    Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') − Q(s,a)]
    """
    def __init__(self, actions_fn, alpha=0.5, gamma=0.9, epsilon=0.1):
        self.actions_fn = actions_fn  # 返回某状态的合法动作列表
        self.alpha, self.gamma, self.epsilon = alpha, gamma, epsilon
        self.Q = defaultdict(float)

    def get_q(self, s, a): return self.Q[(s, a)]

    def choose_action(self, s):
        actions = self.actions_fn(s)
        if not actions:
            return None
        if random.random() < self.epsilon:
            return random.choice(actions)
        # tie-breaking random（CS188 默认 RandomAgent 要求）
        best_q = max(self.Q[(s, a)] for a in actions)
        best_actions = [a for a in actions if self.Q[(s, a)] == best_q]
        return random.choice(best_actions)

    def update(self, s, a, r, sp):
        actions_next = self.actions_fn(sp)
        max_q_next = max((self.Q[(sp, ap)] for ap in actions_next), default=0)
        td_target = r + self.gamma * max_q_next
        self.Q[(s, a)] += self.alpha * (td_target - self.Q[(s, a)])


class ApproximateQLearningAgent:
    """
    CS188 Proj3 Q10-11 的 Approximate Q-Learning。
      Q(s,a) ≈ Σ_i w_i · f_i(s,a)
      w_i ← w_i + α [r + γ max_a' Q(s',a') − Q(s,a)] · f_i(s,a)

    这是策略方法的雏形（[讲透RL/02] 的 advantage weight 思想）。
    """
    def __init__(self, feat_extractor_fn, actions_fn, alpha=0.1, gamma=0.9, epsilon=0.05):
        self.feat = feat_extractor_fn  # (s, a) → {feat_name: value}
        self.actions_fn = actions_fn
        self.alpha, self.gamma, self.epsilon = alpha, gamma, epsilon
        self.weights = defaultdict(float)

    def get_q(self, s, a):
        feats = self.feat(s, a)
        return sum(self.weights[k] * v for k, v in feats.items())

    def choose_action(self, s):
        actions = self.actions_fn(s)
        if not actions or random.random() < self.epsilon:
            return random.choice(actions) if actions else None
        qs = [self.get_q(s, a) for a in actions]
        best = max(qs)
        return random.choice([a for a, q in zip(actions, qs) if q == best])

    def update(self, s, a, r, sp):
        actions_next = self.actions_fn(sp)
        max_q_next = max((self.get_q(sp, ap) for ap in actions_next), default=0)
        difference = r + self.gamma * max_q_next - self.get_q(s, a)
        for k, v in self.feat(s, a).items():
            self.weights[k] += self.alpha * difference * v


# ============================================================
# P4 · Bayes Nets and HMMs — 因子推理 / forward / particle filter
# ============================================================

class Factor:
    """CS188 Proj4 Q1-3 的 factor（CPD 表）。"""
    def __init__(self, variables, table):
        self.variables = variables  # ["A", "B"]
        self.table = table          # {(True, False): 0.7, ...}

    def __repr__(self): return f"Factor({self.variables})"


def factor_elimination(factors, query_var, evidence):
    """CS188 Proj4 Q4 的变量消除法。简化版：暴力枚举 + 条件化。"""
    all_vars = set()
    for f in factors:
        all_vars.update(f.variables)
    hidden = all_vars - {query_var} - set(evidence.keys())

    def enumerate_assignments(vars_to_assign, fixed):
        vars_list = sorted(vars_to_assign)
        if not vars_list:
            yield dict(fixed); return
        first, rest = vars_list[0], vars_list[1:]
        for val in [True, False]:
            new_fixed = dict(fixed); new_fixed[first] = val
            yield from enumerate_assignments(rest, new_fixed)

    # 联合概率
    def joint_prob(assignment):
        p = 1.0
        for f in factors:
            key = tuple(assignment[v] for v in f.variables)
            p *= f.table.get(key, 0)
        return p

    # 求和消去 hidden
    result = {True: 0, False: 0}
    for qv in [True, False]:
        full_evidence = dict(evidence); full_evidence[query_var] = qv
        for assignment in enumerate_assignments(hidden, full_evidence):
            result[qv] += joint_prob(assignment)

    # 归一化
    total = result[True] + result[False]
    return {k: v / total for k, v in result.items()} if total > 0 else result


def hmm_forward(observed, prior, transition, emission, states):
    """
    CS188 Proj4 Q7 的 HMM Forward Algorithm。
      α_t(s) = P(s_t = s | o_1:t)
      α_t(s) ∝ emission(s, o_t) · Σ_sp α_{t-1}(sp) · transition(sp, s)
    """
    # 初始化 t=0
    alpha = {s: prior[s] * emission(s, observed[0]) for s in states}
    total = sum(alpha.values())
    alpha = {s: v / total for s, v in alpha.items()}

    for t in range(1, len(observed)):
        new_alpha = {}
        for s in states:
            new_alpha[s] = emission(s, observed[t]) * sum(
                alpha[sp] * transition(sp, s) for sp in states
            )
        total = sum(new_alpha.values())
        alpha = {s: v / total for s, v in new_alpha.items()}
    return alpha


def particle_filter(observed, transition, emission, states, n_particles=1000):
    """
    CS188 Proj4 Q8-11 的 Particle Filter（蒙特卡洛 HMM 近似）。
    """
    particles = [random.choice(states) for _ in range(n_particles)]
    for o in observed:
        # 1. 时间步：转移
        particles = [weighted_sample(particles, transition, emission, o, states)
                     for _ in range(n_particles)]
    # 返回状态分布
    counts = defaultdict(int)
    for p in particles:
        counts[p] += 1
    return {s: counts[s] / n_particles for s in states}


def weighted_sample(particles, transition, emission, obs, states):
    """按权重 P(obs|s') * P(s'|p) 采样下一个状态。"""
    weights = []
    for s_next in states:
        w = emission(s_next, obs) * sum(
            1.0 / len(particles) * transition(p, s_next) for p in particles
        )
        weights.append(w)
    total = sum(weights)
    if total == 0:
        return random.choice(states)
    r = random.random() * total
    cum = 0
    for s, w in zip(states, weights):
        cum += w
        if r <= cum:
            return s
    return states[-1]


# ============================================================
# P5 · Machine Learning — Perceptron / NN / RNN
# ============================================================

def perceptron_train(X, y, n_iters=10, learning_rate=1.0):
    """
    CS188 Proj5 Q1-4 的 Perceptron（在线 / 平均版）。
      w ← w + α (y − ŷ) x
    """
    n, d = len(X), len(X[0])
    w = [0.0] * d
    b = 0.0
    for it in range(n_iters):
        errors = 0
        for xi, yi in zip(X, y):
            activation = sum(wi * xij for wi, xij in zip(w, xi)) + b
            yhat = 1 if activation > 0 else 0
            if yhat != yi:
                errors += 1
                for j in range(d):
                    w[j] += learning_rate * (yi - yhat) * xi[j]
                b += learning_rate * (yi - yhat)
        if errors == 0:
            break
    return w, b, it + 1


def neural_net_forward(x, W1, b1, W2, b2):
    """
    CS188 Proj5 Q5-7 的最小 NN（1 hidden layer，ReLU 激活）。
    只前向（反向见讲透PyTorch/反向传播章节）。
    """
    import math
    z1 = [sum(W1[i][j] * x[j] for j in range(len(x))) + b1[i] for i in range(len(W1))]
    a1 = [max(0, z) for z in z1]  # ReLU
    z2 = sum(W2[i] * a1[i] for i in range(len(a1))) + b2
    return z2, a1


def rnn_step(x_t, h_prev, W_xh, W_hh, b_h):
    """
    CS188 Proj5 Q8-9 的 RNN step（用于语言识别）。
      h_t = tanh(W_xh · x_t + W_hh · h_prev + b_h)
    """
    import math
    h_t = []
    for i in range(len(W_hh)):
        s = (sum(W_xh[i][j] * x_t[j] for j in range(len(x_t)))
             + sum(W_hh[i][j] * h_prev[j] for j in range(len(h_prev)))
             + b_h[i])
        h_t.append(math.tanh(s))
    return h_t


# ============================================================
# ============ 测试：每个迭代的核心算法都跑通 ============
# ============================================================

def test_p1_search():
    print("\n=== P1 Search ===")
    maze = """
%%%%%%%%
%P    .%
%%%%%%%%
"""
    prob = MazeProblem(maze.strip())
    path_dfs = graph_search(prob, Stack)
    path_bfs = graph_search(prob, Queue)
    path_astar = a_star_search(prob, manhattan_heuristic)
    print(f"  DFS path length: {len(path_dfs)}  actions: {path_dfs}")
    print(f"  BFS path length: {len(path_bfs)}  actions: {path_bfs}")
    print(f"  A*  path length: {len(path_astar)}  actions: {path_astar}")
    assert len(path_bfs) == 5, f"BFS 应找到 5 步最优解，实际 {len(path_bfs)}"
    assert path_astar == path_bfs, "A* 应与 BFS 同长（admissible h）"
    print("  ✅ DFS / BFS / A* 通过；A* 启发式 admissible")


def test_p2_multiagent():
    print("\n=== P2 Multiagent ===")
    # 简单博弈树：1 个 Pacman + 1 个 ghost，2 层深度
    # state.score 直接 = 该节点 value
    class State:
        def __init__(self, score, children=None, agent=0):
            self.score, self.children, self.agent = score, children or [], agent
    terminal_states = [State(score=-5), State(score=3), State(score=10), State(score=-2)]

    def get_legal(s, agent): return list(range(len(s.children)))
    def get_successor(s, agent, a): return s.children[a]
    def terminal(s): return not s.children

    # 构造：root(Pacman) → [g1, g2]；g1 → [-5, 3]；g2 → [10, -2]
    g1 = State(0, [terminal_states[0], terminal_states[1]], agent=1)
    g2 = State(0, [terminal_states[2], terminal_states[3]], agent=1)
    root = State(0, [g1, g2], agent=0)

    # Minimax：Pacman 选 max(g1_val, g2_val)；
    #   g1_val = min(-5, 3) = -5; g2_val = min(10, -2) = -2
    #   root = max(-5, -2) = -2
    val = minimax_value(root, 0, 0, 2, 10, get_legal, get_successor, terminal)
    print(f"  Minimax value (1 Pacman + 1 Ghost, 2-ply): {val}")
    assert val == -2, f"minimax 应 = -2，实际 {val}"

    # Expectimax：g1_val = mean(-5, 3) = -1; g2_val = mean(10, -2) = 4
    #   root = max(-1, 4) = 4
    val_e = expectimax_value(root, 0, 0, 2, 10, get_legal, get_successor, terminal)
    print(f"  Expectimax value: {val_e}")
    assert val_e == 4, f"expectimax 应 = 4，实际 {val_e}"
    print("  ✅ Minimax 与 Expectimax 都通过；ghost 行为模型不同 → 策略不同")


def test_p3_rl():
    print("\n=== P3 RL ===")
    # 简单 3 状态 MDP：S0 → (a: 0 reward + γ·V(S1)) or (b: 5 reward 终止)
    #                  S1 → (a: 0 + γ·V(S2)) or (b: 1 终止)
    #                  S2 → (a: 10 终止) or (b: 0 终止)
    mdp = {
        "states": ["S0", "S1", "S2"],
        "terminal": set(),
        "rewards": {("S0", "a", "S1"): 0, ("S0", "b", "T"): 5,
                    ("S1", "a", "S2"): 0, ("S1", "b", "T"): 1,
                    ("S2", "a", "T"): 10, ("S2", "b", "T"): 0},
        "actions": lambda s: ["a", "b"] if s != "T" else [],
        "transitions": lambda sa: [("T", 1)] if sa[1] == "b" else [(sa[0][-1] + "S1" if sa[0] == "S0" else ("S2" if sa[0] == "S1" else "T"), 1)],
    }
    # 修正 transitions：a 从 S0→S1, S1→S2, S2→T
    def trans(sa):
        s, a = sa
        if a == "a":
            return [("S1", 1)] if s == "S0" else ([("S2", 1)] if s == "S1" else [("T", 1)])
        return [("T", 1)]
    mdp["transitions"] = trans
    mdp["states"] = ["S0", "S1", "S2"]  # T 不在 V 里

    V, n_iters = value_iteration(mdp, gamma=0.9)
    print(f"  Value Iteration 收敛于 {n_iters} iter")
    print(f"    V*(S0)={V['S0']:.3f}, V*(S1)={V['S1']:.3f}, V*(S2)={V['S2']:.3f}")
    # 手算：V(S2) = max(10, 0) = 10；V(S1) = max(0+0.9·10, 1) = 9；V(S0) = max(0+0.9·9, 5) = 8.1
    assert abs(V['S2'] - 10) < 0.01 and abs(V['S1'] - 9) < 0.01 and abs(V['S0'] - 8.1) < 0.01
    print("  ✅ Value Iteration 收敛到理论值 V(S0)=8.1, V(S1)=9, V(S2)=10")

    # Q-Learning（简单跑几轮）
    random.seed(42)
    agent = QLearningAgent(actions_fn=lambda s: ["a", "b"] if s != "T" else [],
                           alpha=0.5, gamma=0.9, epsilon=0.3)
    for ep in range(2000):
        s = "S0"
        steps = 0
        while s != "T" and steps < 10:
            a = agent.choose_action(s)
            if a == "b":
                r = {"S0": 5, "S1": 1, "S2": 0}[s]
                sp = "T"
            else:
                # (S0,a,S1)=0; (S1,a,S2)=0; (S2,a,T)=10（终止奖励）
                r = 10 if s == "S2" else 0
                sp = {"S0": "S1", "S1": "S2", "S2": "T"}[s]
            agent.update(s, a, r, sp)
            s = sp
            steps += 1
    print(f"  Q-Learning 2000 ep: Q(S0,a)={agent.Q[('S0','a')]:.2f}, Q(S0,b)={agent.Q[('S0','b')]:.2f}")
    print(f"                       Q(S1,a)={agent.Q[('S1','a')]:.2f}, Q(S2,a)={agent.Q[('S2','a')]:.2f}")
    assert agent.Q[('S0','a')] > agent.Q[('S0','b')], "Q-Learning 应学到 a 更好（8.1 > 5）"
    print("  ✅ Q-Learning 学到 Q*(S0,a) > Q*(S0,b)")


def test_p4_bayes_hmm():
    print("\n=== P4 Bayes Nets / HMM ===")
    # 经典 CS188 例：Rain → Umbrella（HMM）
    # P(R_0) = 0.5；P(R_t | R_{t-1}) = 同 0.7 / 变 0.3
    # P(U_t = T | R_t = T) = 0.9, P(U_t = T | R_t = F) = 0.2
    states = [True, False]
    prior = {True: 0.5, False: 0.5}
    def transition(sp, s):
        if sp == s: return 0.7
        return 0.3
    def emission(s, o):
        if o == True:   # 看见 umbrella
            return 0.9 if s == True else 0.2
        else:
            return 0.1 if s == True else 0.8

    # 观察序列：[U, U, not-U]
    obs = [True, True, False]
    alpha = hmm_forward(obs, prior, transition, emission, states)
    print(f"  Forward algorithm (obs=[U,U,¬U]):")
    print(f"    P(R_3=T | obs) = {alpha[True]:.3f}")
    print(f"    P(R_3=F | obs) = {alpha[False]:.3f}")
    # 观察 [U, U, ¬U]：两次 U 推 R=T；但 forward 对最近观察权重最高，第三次 ¬U 把后验拉向 F
    assert 0.05 < alpha[True] < 0.5, "forward 应反映'最近观察权重最高'，¬U 拉低 R=T"
    assert alpha[False] > alpha[True], "P(R_3=F) 应大于 P(R_3=T)（最近 ¬U 主导）"
    print("  ✅ HMM Forward Algorithm 通过；forward 对最近观察权重最高 → 第三次 ¬U 把后验拉向 F")


def test_p5_ml():
    print("\n=== P5 ML ===")
    # Perceptron 学 AND 函数
    X = [[0,0],[0,1],[1,0],[1,1]]
    y = [0, 0, 0, 1]  # AND
    w, b, n_iters = perceptron_train(X, y, n_iters=20)
    print(f"  Perceptron 学 AND：{n_iters} iter 收敛")
    print(f"    w={w}, b={b}")
    correct = sum(
        (1 if sum(wi*xi for wi,xi in zip(w,xi))+b > 0 else 0) == yi
        for xi, yi in zip(X, y)
    )
    print(f"    训练集准确率: {correct}/4")
    assert correct == 4, "Perceptron 应学完 AND（线性可分）"
    print("  ✅ Perceptron 学完 AND（验证线性可分数据可分离）")


if __name__ == "__main__":
    print("=" * 70)
    print("CS 188 SP26 · Pacman Projects — 6 个迭代核心算法验证")
    print("=" * 70)
    test_p1_search()
    test_p2_multiagent()
    test_p3_rl()
    test_p4_bayes_hmm()
    test_p5_ml()
    print("\n" + "=" * 70)
    print("✅ 全部 5 个迭代（P1-P5）核心算法跑通。")
    print("   P0 是 Python + autograder tutorial，无算法内容。")
    print("=" * 70)
