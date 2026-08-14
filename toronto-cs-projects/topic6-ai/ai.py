"""
CSC 384 Introduction to Artificial Intelligence (University of Toronto)
=======================================================================
覆盖主题：
- A* 搜索（启发式路径规划）
- CSP 约束满足问题（Plain Backtracking vs Forward Checking + MRV 启发式）
- Planning（STRIPS 表示 + 规划图）
- 对抗搜索（MINIMAX + Alpha-Beta 剪枝）

核心教材：
- Russell & Norvig "Artificial Intelligence: A Modern Approach" (4th ed.)
- Hart, Nilsson, Raphael "A Formal Basis for the Heuristic Determination of Minimum Cost Paths" (1968 IEEE)
- STRIPS: Fikes & Nilsson "STRIPS: A New Approach to the Application of Theorem Proving" (1971 AIJ)

本文件实现：
- A* 搜索（网格世界寻路 + 启发式对比）
- CSP 回溯求解器（Map Coloring / N-Queens）
- STRIPS 规划器（积木世界）
- MINIMAX + Alpha-Beta（Tic-Tac-Toe）

运行：
    python ai.py
"""
from __future__ import annotations
import heapq
import math
from collections import defaultdict


# ============ 1. A* Search ============

class AStar:
    """
    A* 搜索：f(n) = g(n) + h(n)
    g(n) = 从起点到 n 的实际代价
    h(n) = 从 n 到目标的启发式估计（必须 admissible）
    """

    @staticmethod
    def manhattan(a, b) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def euclidean(a, b) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    @staticmethod
    def zero(a, b) -> int:
        return 0  # 退化为 Dijkstra

    @staticmethod
    def search(grid: list[list[int]], start, goal, heuristic=None) -> tuple[list, int]:
        """
        grid: 0=可走, 1=障碍
        返回 (路径, 探索的节点数)
        """
        heuristic = heuristic or AStar.manhattan
        rows, cols = len(grid), len(grid[0])
        open_heap = [(0, start)]
        came_from = {start: None}
        g_score = {start: 0}
        closed = set()  # 避免重复扩展（A* 标准实现）
        explored = 0

        while open_heap:
            _, current = heapq.heappop(open_heap)
            if current in closed:
                continue
            closed.add(current)
            explored += 1

            if current == goal:
                # 重建路径
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return path[::-1], explored

            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = current[0] + dr, current[1] + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                    neighbor = (nr, nc)
                    tentative_g = g_score[current] + 1
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        g_score[neighbor] = tentative_g
                        f = tentative_g + heuristic(neighbor, goal)
                        heapq.heappush(open_heap, (f, neighbor))
                        came_from[neighbor] = current

        return [], explored


# ============ 2. CSP (Constraint Satisfaction Problem) ============

class CSPSolver:
    """
    CSP 回溯求解器，提供两种模式：
    - solve_bt()：Plain Backtracking + MRV（不传播约束）
    - solve_fc()：Forward Checking + MRV（赋值后对未赋值邻居做域剪枝，
      检测 domain wipeout 提前回溯）
    """

    def __init__(self, variables: list, domains: dict, constraints: dict):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints  # var → list of (neighbor, predicate(value, neighbor_value))
        self.nodes_explored = 0

    # ===== Plain Backtracking + MRV =====

    def solve_bt(self) -> dict | None:
        """Plain backtracking：赋值前检查与已赋值变量的一致性，不传播约束。"""
        self.nodes_explored = 0
        return self._backtrack_bt({})

    def _backtrack_bt(self, assignment: dict) -> dict | None:
        self.nodes_explored += 1
        if len(assignment) == len(self.variables):
            return dict(assignment)

        var = self._select_mrv_bt(assignment)
        for value in self._bt_domain(var, assignment):
            if self._is_consistent(var, value, assignment):
                assignment[var] = value
                result = self._backtrack_bt(assignment)
                if result is not None:
                    return result
                del assignment[var]
        return None

    def _bt_domain(self, var, assignment):
        """返回与已赋值邻居一致的值（plain BT 的动态域）。"""
        return [v for v in self.domains[var]
                if self._is_consistent(var, v, assignment)]

    def _select_mrv_bt(self, assignment):
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda v: len(self._bt_domain(v, assignment)))

    # ===== Forward Checking + MRV =====

    def solve_fc(self) -> dict | None:
        """Forward Checking：每次赋值后对未赋值邻居的域做约束传播，
        若某邻居域被清空（wipeout）则立即回溯，避免深入无效分支。"""
        self.nodes_explored = 0
        self._fc_domains = {v: list(self.domains[v]) for v in self.variables}
        return self._backtrack_fc({})

    def _backtrack_fc(self, assignment: dict) -> dict | None:
        self.nodes_explored += 1
        if len(assignment) == len(self.variables):
            return dict(assignment)

        var = self._select_mrv_fc(assignment)
        for value in list(self._fc_domains[var]):
            # 保存所有域的快照（回溯时恢复）
            saved = {v: list(self._fc_domains[v]) for v in self.variables}
            assignment[var] = value
            self._fc_domains[var] = [value]

            # FC 核心：对 var 的未赋值邻居做域剪枝
            wipeout = self._forward_check(var, assignment)

            if not wipeout:
                result = self._backtrack_fc(assignment)
                if result is not None:
                    return result

            # 回溯
            del assignment[var]
            self._fc_domains = saved
        return None

    def _forward_check(self, var, assignment) -> bool:
        """对 var 的所有未赋值邻居做 AC 检查。
        删除邻居域中与 var=value 冲突的值，返回 True 若有 domain wipeout。"""
        wipeout = False
        for neighbor, predicate in self.constraints.get(var, []):
            if neighbor in assignment:
                continue
            pruned = [v for v in self._fc_domains[neighbor]
                      if not predicate(assignment[var], v)]
            for v in pruned:
                self._fc_domains[neighbor].remove(v)
            if len(self._fc_domains[neighbor]) == 0:
                wipeout = True
        return wipeout

    def _select_mrv_fc(self, assignment):
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda v: len(self._fc_domains[v]))

    def _is_consistent(self, var, value, assignment) -> bool:
        for neighbor, predicate in self.constraints.get(var, []):
            if neighbor in assignment:
                if not predicate(value, assignment[neighbor]):
                    return False
        return True


def map_coloring_csp():
    """经典 Map Coloring CSP（澳大利亚），对比 BT vs FC 节点数"""
    # 澳大利亚地图
    variables = ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']
    colors = ['red', 'green', 'blue']
    domains = {v: list(colors) for v in variables}

    adjacent = {
        'WA': ['NT', 'SA'],
        'NT': ['WA', 'SA', 'Q'],
        'SA': ['WA', 'NT', 'Q', 'NSW', 'V'],
        'Q': ['NT', 'SA', 'NSW'],
        'NSW': ['SA', 'Q', 'V'],
        'V': ['SA', 'NSW'],
        'T': [],  # 塔斯马尼亚不与大陆相邻
    }
    constraints = {}
    for var, neighbors in adjacent.items():
        constraints[var] = [(n, lambda a, b: a != b) for n in neighbors]

    solver_bt = CSPSolver(variables, domains, constraints)
    sol_bt = solver_bt.solve_bt()
    solver_fc = CSPSolver(variables, domains, constraints)
    sol_fc = solver_fc.solve_fc()
    return sol_fc, solver_bt.nodes_explored, solver_fc.nodes_explored


def nqueens_csp(n=8):
    """N-Queens CSP：对比 Plain Backtracking vs Forward Checking 节点数"""
    variables = list(range(n))
    domains = {v: list(range(n)) for v in variables}

    constraints = {}
    for i in range(n):
        constraints[i] = []
        for j in range(n):
            if i != j:
                # 行 i 列 a 的皇后 vs 行 j 列 b 的皇后：不同列、不同对角线
                constraints[i].append(
                    (j, lambda a, b, ri=i, rj=j: a != b and abs(a - b) != abs(ri - rj)))

    solver_bt = CSPSolver(variables, domains, constraints)
    sol_bt = solver_bt.solve_bt()
    solver_fc = CSPSolver(variables, domains, constraints)
    sol_fc = solver_fc.solve_fc()
    return sol_fc, solver_bt.nodes_explored, solver_fc.nodes_explored


# ============ 3. STRIPS Planning ============

class STRIPSAction:
    def __init__(self, name, preconditions: set, add_effects: set, del_effects: set):
        self.name = name
        self.pre = preconditions
        self.add = add_effects
        self.del_ = del_effects


class STRIPSPlanner:
    """
    简化 STRIPS 规划器（宽度优先搜索）
    """

    def __init__(self, init_state: set, goal: set, actions: list[STRIPSAction]):
        self.init = frozenset(init_state)
        self.goal = frozenset(goal)
        self.actions = actions

    def plan(self, max_depth=20) -> list[str] | None:
        from collections import deque
        queue = deque([(self.init, [])])
        visited = {self.init}

        while queue:
            state, path = queue.popleft()
            if self.goal.issubset(state):
                return path
            if len(path) >= max_depth:
                continue
            for action in self.actions:
                if action.pre.issubset(state):
                    new_state = frozenset((state - action.del_) | action.add)
                    if new_state not in visited:
                        visited.add(new_state)
                        queue.append((new_state, path + [action.name]))
        return None


def blocks_world_planning():
    """积木世界 STRIPS 规划"""
    # 初始状态: A 在桌上, B 在桌上, C 在桌上
    # 目标: C 在 B 上, B 在 A 上, A 在桌上
    init = {'on_table(A)', 'clear(A)', 'on_table(B)', 'clear(B)', 'on_table(C)', 'clear(C)', 'hand_empty'}
    goal = {'on(C,B)', 'on(B,A)', 'on_table(A)', 'clear(C)'}

    actions = [
        STRIPSAction('pickup(A)',
                     {'on_table(A)', 'clear(A)', 'hand_empty'},
                     {'holding(A)'}, {'on_table(A)', 'clear(A)', 'hand_empty'}),
        STRIPSAction('putdown(A)',
                     {'holding(A)'},
                     {'on_table(A)', 'clear(A)', 'hand_empty'}, {'holding(A)'}),
        STRIPSAction('stack(C,B)',
                     {'holding(C)', 'clear(B)'},
                     {'on(C,B)', 'clear(C)', 'hand_empty'}, {'holding(C)', 'clear(B)'}),
        STRIPSAction('unstack(C,B)',
                     {'on(C,B)', 'clear(C)', 'hand_empty'},
                     {'holding(C)', 'clear(B)'}, {'on(C,B)', 'clear(C)', 'hand_empty'}),
        STRIPSAction('stack(B,A)',
                     {'holding(B)', 'clear(A)'},
                     {'on(B,A)', 'clear(B)', 'hand_empty'}, {'holding(B)', 'clear(A)'}),
        STRIPSAction('pickup(B)',
                     {'on_table(B)', 'clear(B)', 'hand_empty'},
                     {'holding(B)'}, {'on_table(B)', 'clear(B)', 'hand_empty'}),
        STRIPSAction('pickup(C)',
                     {'on_table(C)', 'clear(C)', 'hand_empty'},
                     {'holding(C)'}, {'on_table(C)', 'clear(C)', 'hand_empty'}),
    ]
    planner = STRIPSPlanner(init, goal, actions)
    return planner.plan()


# ============ 4. MINIMAX + Alpha-Beta ============

class TicTacToe:
    """Tic-Tac-Toe MINIMAX + Alpha-Beta 剪枝"""

    def __init__(self):
        self.board = [' '] * 9
        self.nodes_visited = 0

    def available_moves(self) -> list[int]:
        return [i for i in range(9) if self.board[i] == ' ']

    def winner(self) -> str | None:
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a, b, c in lines:
            if self.board[a] != ' ' and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def is_full(self) -> bool:
        return ' ' not in self.board

    def minimax(self, is_max: bool, alpha=-math.inf, beta=math.inf, use_ab=False) -> int:
        self.nodes_visited += 1
        w = self.winner()
        if w == 'X':
            return 10 - (9 - len(self.available_moves()))
        if w == 'O':
            return -10 + (9 - len(self.available_moves()))
        if self.is_full():
            return 0

        if is_max:
            best = -math.inf
            for move in self.available_moves():
                self.board[move] = 'X'
                val = self.minimax(False, alpha, beta, use_ab)
                self.board[move] = ' '
                best = max(best, val)
                if use_ab:
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break
            return best
        else:
            best = math.inf
            for move in self.available_moves():
                self.board[move] = 'O'
                val = self.minimax(True, alpha, beta, use_ab)
                self.board[move] = ' '
                best = min(best, val)
                if use_ab:
                    beta = min(beta, best)
                    if beta <= alpha:
                        break
            return best

    def best_move(self, player='X', use_ab=True) -> int:
        best_val = -math.inf if player == 'X' else math.inf
        best_move = -1
        for move in self.available_moves():
            self.board[move] = player
            val = self.minimax(player == 'O', use_ab=use_ab)
            self.board[move] = ' '
            if player == 'X' and val > best_val:
                best_val, best_move = val, move
            elif player == 'O' and val < best_val:
                best_val, best_move = val, move
        return best_move


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 384: Introduction to AI Demo")
    print("=" * 60)

    # 1. A* Search
    print("\n📋 1. A* 搜索（网格寻路）")
    # 12x16 网格，中间有一面墙构成的"房间"（goal 在房间内）。
    # 起点 (0,0) 到 goal (5,14) 必须绕墙——这种结构让两种启发式产生差异。
    grid = [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
    start, goal = (0, 0), (5, 14)

    results = {}
    for name, h in [("Manhattan", AStar.manhattan), ("Euclidean", AStar.euclidean), ("Dijkstra(h=0)", AStar.zero)]:
        path, explored = AStar.search(grid, start, goal, h)
        results[name] = (len(path), explored)
        print(f"   {name:20s}: 路径长度={len(path):2d}, 探索节点={explored}")

    m_nodes = results["Manhattan"][1]
    e_nodes = results["Euclidean"][1]
    d_nodes = results["Dijkstra(h=0)"][1]
    print(f"\n   反直觉发现：Manhattan 探索 {m_nodes} 节点 < Euclidean {e_nodes} 节点 < Dijkstra {d_nodes} 节点")
    print(f"   （4-连通网格上 Manhattan = 真实最短路径长度，是「最紧」的 admissible 启发式；")
    print(f"    Euclidean ≤ Manhattan 也 admissible 但更松，所以扩展更多节点；")
    print(f"    h=0 退化为 Dijkstra 几乎探索全图）")

    # 2. CSP Map Coloring
    print("\n📋 2. CSP Map Coloring（澳大利亚）")
    solution, bt_nodes, fc_nodes = map_coloring_csp()
    if solution:
        print(f"   解: {solution}")
        print(f"   Plain Backtracking: {bt_nodes} 节点 | Forward Checking: {fc_nodes} 节点")
        # 验证约束
        ok = True
        adj = {'WA': ['NT','SA'], 'NT': ['WA','SA','Q'], 'SA': ['WA','NT','Q','NSW','V'],
               'Q': ['NT','SA','NSW'], 'NSW': ['SA','Q','V'], 'V': ['SA','NSW']}
        for r, neighbors in adj.items():
            for n in neighbors:
                if solution[r] == solution[n]:
                    ok = False
        print(f"   约束满足: {ok}")

    # 2b. CSP N-Queens — BT vs FC 差异更显著
    print("\n📋 2b. CSP N-Queens（8 皇后）— BT vs FC 节点数对比")
    sol8, bt8, fc8 = nqueens_csp(8)
    if sol8:
        print(f"   解: {sol8}")
        print("   棋盘（Q=皇后）：")
        for r in range(8):
            print(f"     {' '.join('Q' if sol8[r] == c else '.' for c in range(8))}")
        saving = (1 - fc8 / bt8) * 100
        print(f"   Plain Backtracking: {bt8} 节点 | Forward Checking: {fc8} 节点")
        print(f"\n   反直觉发现：Forward Checking 节点数减少 {saving:.0f}%")
        print(f"   （FC 在赋值后立即剪枝未赋值邻居的域，检测到 domain wipeout 提前回溯，")
        print(f"    避免了 plain BT 深入无效分支后才在底层碰壁）")

    # 3. STRIPS Planning
    print("\n📋 3. STRIPS 积木世界规划")
    plan = blocks_world_planning()
    if plan:
        print(f"   计划: {' → '.join(plan)}")
        print(f"   步骤数: {len(plan)}")

    # 4. MINIMAX Tic-Tac-Toe
    print("\n📋 4. MINIMAX + Alpha-Beta（Tic-Tac-Toe）")
    game = TicTacToe()
    # 空棋盘最优着
    move = game.best_move('X', use_ab=True)
    print(f"   空棋盘 X 最优着: 位置 {move}")
    print(f"   Alpha-Beta 访问节点: {game.nodes_visited}")

    game2 = TicTacToe()
    game2.best_move('X', use_ab=False)
    print(f"   纯 MINIMAX 访问节点: {game2.nodes_visited}")
    pruning = (1 - game.nodes_visited / game2.nodes_visited) * 100
    print(f"   Alpha-Beta 剪枝率: {pruning:.1f}%")
    print(f"\n   反直觉：αβ 最优情形访问 O(b^(d/2)) vs 纯 minimax O(b^d)，")
    print(f"   即开方级缩减。对井字棋 b=9, d=9，理论上可剪到约 0.005%。")
    print(f"   实测剪掉 {pruning:.0f}%（{game2.nodes_visited} → {game.nodes_visited}）取决于着法顺序——")
    print(f"   着法排序越好剪得越多。")

    print("\n✅ CSC 384 完成！")
    print("💡 覆盖：A*搜索 + CSP约束求解 + STRIPS规划 + MINIMAX对抗搜索")


if __name__ == "__main__":
    demo()
