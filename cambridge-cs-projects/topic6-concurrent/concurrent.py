"""
Part IB Concurrent & Distributed Systems (Cambridge CST)
========================================================
覆盖主题：
- 互斥与锁（mutex / spinlock / Peterson）
- 死锁检测（资源分配图）
- CSP（Communicating Sequential Processes）trace 语义
- LTL 模型检测（mini SPIN）

核心教材：
- Hoare 1985 "Communicating Sequential Processes" Prentice Hall
- Ben-Ari 2006 "Principles of Concurrent and Distributed Programming" 2nd ed
- Tanenbaum & Van Steen 2017 "Distributed Systems" 3rd ed, Pearson
- Lamport 1978 "Time, Clocks, and the Ordering of Events in a Distributed
  System" CACM

本文件实现：
- Peterson 互斥算法验证
- 资源分配图死锁检测
- CSP trace 等价验证
- LTL 模型检测（状态空间搜索 + 反例路径）

运行：
    python concurrent.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict


# ================================================================
# 1. Peterson 互斥算法
# ================================================================

class PetersonLock:
    """Peterson 算法: 两进程互斥"""

    def __init__(self):
        self.flag = [False, False]  # 进程 i 想进临界区
        self.turn = 0               # 谁的回合（礼让）

    def lock(self, pid: int):
        other = 1 - pid
        self.flag[pid] = True
        self.turn = other  # 礼让对方
        # 等待: 对方也想进 且 回合给对方
        while self.flag[other] and self.turn == other:
            pass  # spin

    def unlock(self, pid: int):
        self.flag[pid] = False


def verify_peterson_mutual_exclusion():
    """
    真正的状态空间 BFS 验证 Peterson 算法满足互斥。

    状态 = (pc0, pc1, flag0, flag1, turn)，枚举所有可达状态，
    检查 ¬(pc0==3 ∧ pc1==3) 即两个进程不可能同时在临界区。

    每个进程的 pc（程序计数器）:
      0 = remainder（剩余区）
      1 = flag[i] 已置 True，下一步设 turn
      2 = turn 已设，检查等待条件（自旋点）
      3 = critical section（临界区），下一步清 flag 回到 0

    返回 dict: {
        'mutual_exclusion': bool,
        'reachable_states': int,
        'total_states': int,       # 理论上限 4×4×2×2×2 = 128
        'cs_states': int,          # 至少一方在 CS 的可达态数
        'violation': state or None
    }
    """
    init = (0, 0, False, False, 0)  # (pc0, pc1, flag0, flag1, turn)

    def step(state, who):
        """process `who` 执行一步后的新状态；None 表示该进程当前阻塞（无新状态）"""
        pc0, pc1, f0, f1, turn = state
        pcs = [pc0, pc1]
        flags = [f0, f1]
        pc = pcs[who]
        j = 1 - who
        if pc == 0:          # remainder → set flag
            flags[who] = True
            pcs[who] = 1
        elif pc == 1:        # flag set → set turn
            turn = j
            pcs[who] = 2
        elif pc == 2:        # check wait condition
            if not (flags[j] and turn == j):
                pcs[who] = 3   # enter CS
            else:
                return None    # blocked (spin — self-loop, 不产生新状态)
        elif pc == 3:        # CS → clear flag, back to remainder
            flags[who] = False
            pcs[who] = 0
        else:
            return None
        return (pcs[0], pcs[1], flags[0], flags[1], turn)

    visited = set()
    queue = [init]
    visited.add(init)
    cs_count = 0
    violation = None

    while queue:
        state = queue.pop(0)
        pc0, pc1 = state[0], state[1]
        if pc0 == 3 or pc1 == 3:
            cs_count += 1
            if pc0 == 3 and pc1 == 3:
                violation = state  # 互斥违反
        for who in (0, 1):
            ns = step(state, who)
            if ns is not None and ns not in visited:
                visited.add(ns)
                queue.append(ns)

    total_possible = 4 * 4 * 2 * 2 * 2  # pc0 × pc1 × flag0 × flag1 × turn
    return {
        'mutual_exclusion': violation is None,
        'reachable_states': len(visited),
        'total_states': total_possible,
        'cs_states': cs_count,
        'violation': violation,
    }


# ================================================================
# 2. 死锁检测（资源分配图）
# ================================================================

@dataclass
class ResourceAllocationGraph:
    """资源分配图: 进程 → 资源 (申请/分配)"""
    # edges: (process, resource, type) type='R'(request) or 'A'(assign)
    processes: set = field(default_factory=set)
    resources: set = field(default_factory=set)
    edges: set = field(default_factory=set)  # (p, r, 'R'/'A')

    def request(self, p, r): self.edges.add((p, r, 'R')); self.processes.add(p); self.resources.add(r)
    def assign(self, p, r): self.edges.add((p, r, 'A')); self.processes.add(p); self.resources.add(r)

    def has_deadlock(self) -> bool:
        """检测环（简化：找进程→资源→进程→...的环）"""
        # 构建进程→进程的 wait-for 图
        wait_for = defaultdict(set)
        for p, r, t in self.edges:
            if t == 'R':  # p 等待 r
                for p2, r2, t2 in self.edges:
                    if r2 == r and t2 == 'A':  # r 被 p2 占有
                        wait_for[p].add(p2)
        # DFS 检测环
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {p: WHITE for p in self.processes}

        def dfs(u):
            color[u] = GRAY
            for v in wait_for[u]:
                if color[v] == GRAY:
                    return True
                if color[v] == WHITE and dfs(v):
                    return True
            color[u] = BLACK
            return False

        for p in self.processes:
            if color[p] == WHITE and dfs(p):
                return True
        return False


# ================================================================
# 3. CSP Trace 语义
# ================================================================

class CSPProcess:
    """
    CSP 进程的 trace 语义。
    P 的行为 = 可观察事件序列（trace）的集合。
    """

    def __init__(self, name: str, traces: set[tuple]):
        self.name = name
        self.traces = traces  # set of event tuples

    def prefix(self, event) -> "CSPProcess":
        """a → P: 在 P 的每个 trace 前加 event"""
        return CSPProcess(f"{event}→{self.name}",
                          {(event,) + t for t in self.traces})

    def choice(self, other: "CSPProcess") -> "CSPProcess":
        """P □ Q: 外部选择，traces 取并"""
        return CSPProcess(f"{self.name}□{other.name}",
                          self.traces | other.traces)

    def parallel(self, other: "CSPProcess", sync_events: set) -> "CSPProcess":
        """P ||| Q: 在 sync_events 上同步"""
        new_traces = set()
        for t1 in self.traces:
            for t2 in other.traces:
                # 合并: 非同步事件自由交错，同步事件必须匹配
                merged = _merge_traces(t1, t2, sync_events)
                new_traces.update(merged)
        return CSPProcess(f"{self.name}|||{other.name}", new_traces)

    def traces_eq(self, other: "CSPProcess") -> bool:
        return self.traces == other.traces


def _merge_traces(t1, t2, sync_events):
    """递归合并两个 trace（简化版）"""
    if not t1 and not t2:
        return {()}
    if not t1:
        return {t2}
    if not t2:
        return {t1}
    result = set()
    if t1[0] in sync_events and t2[0] in sync_events:
        if t1[0] == t2[0]:
            for rest in _merge_traces(t1[1:], t2[1:], sync_events):
                result.add((t1[0],) + rest)
    else:
        if t1[0] not in sync_events:
            for rest in _merge_traces(t1[1:], t2, sync_events):
                result.add((t1[0],) + rest)
        if t2[0] not in sync_events:
            for rest in _merge_traces(t1, t2[1:], sync_events):
                result.add((t2[0],) + rest)
    return result


# ================================================================
# 4. LTL 模型检测（mini SPIN）
# ================================================================

@dataclass
class KripkeState:
    """状态机的一个状态"""
    id: int
    labels: set  # 原子命题
    successors: list = field(default_factory=list)


class ModelChecker:
    """
    mini 模型检测器:
    检查 LTL 公式 □p (always p), ◇p (eventually p), p→◇q
    通过状态空间搜索 + 反例路径。
    """

    def __init__(self, states: dict[int, KripkeState], init: int):
        self.states = states
        self.init = init

    def check_always(self, prop: str) -> tuple[bool, list]:
        """□p: 所有可达状态都满足 p。返回 (holds, counterexample)"""
        visited = set()
        stack = [(self.init, [self.init])]
        while stack:
            sid, path = stack.pop()
            s = self.states[sid]
            if prop not in s.labels:
                return False, path  # 反例
            if sid in visited:
                continue
            visited.add(sid)
            for nxt in s.successors:
                if nxt not in visited:
                    stack.append((nxt, path + [nxt]))
        return True, []

    # ---- 辅助: 可达集 / SCC / 反例路径 ----

    def _reachable_set_from(self, start: int) -> set[int]:
        """从 start 出发的所有可达状态"""
        visited = set()
        stack = [start]
        while stack:
            s = stack.pop()
            if s in visited:
                continue
            visited.add(s)
            for nxt in self.states[s].successors:
                if nxt not in visited:
                    stack.append(nxt)
        return visited

    def _tarjan_scc(self, reachable: set[int]) -> list[list[int]]:
        """Tarjan SCC 算法，返回强连通分量列表（仅含 reachable 中的状态）"""
        import sys
        sys.setrecursionlimit(100000)
        index_counter = [0]
        t_stack = []
        on_stack = {}
        index = {}
        lowlinks = {}
        result = []

        def strongconnect(v):
            index[v] = index_counter[0]
            lowlinks[v] = index_counter[0]
            index_counter[0] += 1
            t_stack.append(v)
            on_stack[v] = True
            for w in self.states[v].successors:
                if w not in reachable:
                    continue
                if w not in index:
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif on_stack.get(w, False):
                    lowlinks[v] = min(lowlinks[v], index[w])
            if lowlinks[v] == index[v]:
                scc = []
                while True:
                    w = t_stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == v:
                        break
                result.append(scc)

        for v in sorted(reachable):
            if v not in index:
                strongconnect(v)
        return result

    def _path_to_set_from(self, start: int, targets: set[int]) -> list[int]:
        """BFS: 从 start 到 targets 中任一状态的最短路径"""
        from collections import deque
        visited = {start: None}
        queue = deque([start])
        while queue:
            s = queue.popleft()
            if s in targets:
                path = []
                cur = s
                while cur is not None:
                    path.append(cur)
                    cur = visited[cur]
                return list(reversed(path))
            for nxt in self.states[s].successors:
                if nxt not in visited:
                    visited[nxt] = s
                    queue.append(nxt)
        return []

    # ---- LTL eventually (SCC-based) ----

    def check_eventually(self, prop: str, start: int = None) -> tuple[bool, list]:
        """
        LTL eventually ◇q: 从 start（默认 init）出发的**所有**无限路径上，
        q 最终成立。

        正确语义（≠ 可达性）:
          ◇q 被违反 ⟺ 存在一条无限路径始终避开 q。
          在有限状态机中，无限路径必然最终循环，
          故等价于: 存在一个可达的、不含 q 的带环 SCC。

        返回 (holds, counterexample_path)。
        反例路径 = 从 start 到违反 SCC 入口的路径 + 循环示意。
        """
        if start is None:
            start = self.init
        reachable = self._reachable_set_from(start)
        sccs = self._tarjan_scc(reachable)
        for scc in sccs:
            if any(prop in self.states[s].labels for s in scc):
                continue  # SCC 内有 q 态，此 SCC 不会永远避开 q
            # SCC 内无 q：检查是否有环（能支撑一条无限路径）
            has_cycle = (len(scc) >= 2 or
                         (len(scc) == 1 and scc[0] in self.states[scc[0]].successors))
            if has_cycle:
                cex = self._path_to_set_from(start, set(scc))
                return False, cex
        return True, []

    def check_leads_to(self, p: str, q: str) -> bool:
        """
        p → ◇q: 从每个满足 p 的可达状态出发，所有路径最终 q 成立。
        即: ∀ s ∈ reachable, p(s) ⟹ ◇q 从 s 成立。
        """
        reachable = self._reachable_set_from(self.init)
        for sid in reachable:
            if p in self.states[sid].labels:
                ok, _ = self.check_eventually(q, start=sid)
                if not ok:
                    return False
        return True


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part IB Concurrent & Distributed Systems — Demo")
    print("=" * 64)

    # 1. Peterson
    print("\n📋 1. Peterson 互斥算法验证（状态空间 BFS）")
    result = verify_peterson_mutual_exclusion()
    print(f"   互斥满足? {result['mutual_exclusion']}")
    print(f"   状态空间: 可达 {result['reachable_states']} / 理论上限 {result['total_states']}"
          f"（{result['reachable_states']/result['total_states']:.0%} 可达）")
    print(f"   至少一方在 CS 的可达态: {result['cs_states']}")
    print(f"   违反态: {result['violation']}")
    print(f"   Peterson: flag[i]=True; turn=1-i; while(flag[1-i] && turn==1-i));")

    # 2. 死锁检测
    print("\n📋 2. 死锁检测（资源分配图）")
    rag = ResourceAllocationGraph()
    # P1 持有 R1 申请 R2; P2 持有 R2 申请 R1 → 死锁
    rag.assign("P1", "R1")
    rag.request("P1", "R2")
    rag.assign("P2", "R2")
    rag.request("P2", "R1")
    dl = rag.has_deadlock()
    print(f"   P1→R1(分配), P1→R2(申请), P2→R2(分配), P2→R1(申请)")
    print(f"   死锁? {dl}  (环 P1→P2→P1)")

    rag2 = ResourceAllocationGraph()
    rag2.assign("P1", "R1")
    rag2.request("P1", "R2")
    rag2.assign("P2", "R2")
    print(f"   无环情况死锁? {rag2.has_deadlock()}")

    # 3. CSP
    print("\n📋 3. CSP Trace 语义")
    STOP = CSPProcess("STOP", {()})
    # a→STOP
    a_stop = STOP.prefix("a")
    print(f"   STOP traces: {STOP.traces}")
    print(f"   a→STOP traces: {a_stop.traces}")
    # (a→STOP) □ (b→STOP)
    b_stop = STOP.prefix("b")
    choice = a_stop.choice(b_stop)
    print(f"   (a→STOP) □ (b→STOP) traces: {choice.traces}")

    # parallel 组合 trace 爆炸
    p = CSPProcess("P", {("a",), ("a", "a"), ("a", "a", "a")})
    q = CSPProcess("Q", {("b",), ("b", "b"), ("b", "b", "b")})
    para = p.parallel(q, sync_events=set())
    print(f"   P traces={len(p.traces)}, Q traces={len(q.traces)}, "
          f"P|||Q traces={len(para.traces)} "
          f"({len(p.traces)}×{len(q.traces)}={len(p.traces)*len(q.traces)})")

    # 4. LTL 模型检测
    print("\n📋 4. LTL 模型检测（SCC-based mini SPIN）")
    # 状态机: S0-{start}→S1-{a,busy}→S2-{b,done}→S1 (循环)
    states = {
        0: KripkeState(0, {"start"}),
        1: KripkeState(1, {"a", "busy"}),
        2: KripkeState(2, {"b", "done"}),
    }
    states[0].successors = [1]
    states[1].successors = [2]
    states[2].successors = [1]  # 循环

    mc = ModelChecker(states, init=0)

    ok, cex = mc.check_always("busy")
    print(f"   模型 A: S0→S1→S2→S1 (循环含 done)")
    print(f"   □busy (总是busy)? {ok}  反例: {cex}")

    ok, path = mc.check_eventually("done")
    print(f"   ◇done (必然done)? {ok}  所有路径最终到达 done")

    leads = mc.check_leads_to("busy", "done")
    print(f"   busy→◇done (busy必然导致done)? {leads}")

    # 模型 B: 有一个不含 goal 的循环 → ◇goal 被违反
    states2 = {
        10: KripkeState(10, {"init"}),
        11: KripkeState(11, {"work"}),
        12: KripkeState(12, {"stuck"}),   # 自环，不含 goal
    }
    states2[10].successors = [11]
    states2[11].successors = [12]
    states2[12].successors = [12]  # 自环死循环
    mc2 = ModelChecker(states2, init=10)
    ok2, cex2 = mc2.check_eventually("goal")
    print(f"\n   模型 B: S10→S11→S12→S12 (自环，无 goal)")
    print(f"   ◇goal (必然goal)? {ok2}  反例路径: {cex2}")
    print(f"   → SCC {cex2[-1] if cex2 else '?'} 不含 goal 且有自环 → 存在无限路径避开 goal")

    print("\n✅ Concurrent & Distributed Systems 完成！")
    print("\n💡 反直觉发现：")
    print(f"   - Peterson 状态空间: {result['total_states']} 种理论组合中仅 "
          f"{result['reachable_states']} 可达（{result['reachable_states']/result['total_states']:.0%}）"
          f"——绝大多数状态不可达")
    print(f"   - 互斥验证: {result['cs_states']} 个可达态有一方在 CS，"
          f"但 0 个两方同时在 CS（无需暴力枚举所有路径，BFS 即可覆盖）")
    print(f"   - LTL ◇q ≠ 可达性: 模型 B 中 goal 可达但 ◇goal=False"
          f"（存在自环 SCC 永远避开 goal）")
    print(f"   - CSP parallel: {len(p.traces)}×{len(q.traces)} traces → "
          f"{len(para.traces)} traces（交织爆炸）")


if __name__ == "__main__":
    demo()
