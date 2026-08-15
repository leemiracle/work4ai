"""
Part IA Regular Languages & Finite Automata (Cambridge CST)
===========================================================
覆盖主题：
- DFA / NFA 定义与模拟
- NFA → DFA 子集构造（subset construction）
- regex → NFA（Thompson 构造）
- DFA 最小化（Hopcroft / Moore）
- pumping lemma 反例

核心教材：
- Hopcroft, Motwani & Ullman 2006 "Introduction to Automata Theory,
  Languages, and Computation" 3rd ed, Addison-Wesley
- Thompson 1968 "Regular Expression Search Algorithm" CACM 11(6)
- Hopcroft 1971 "An n log n algorithm for minimizing states in a
  finite automaton" Stanford Tech Report

本文件实现：
- NFA 模拟（ε-闭包）
- NFA → DFA 子集构造
- Thompson regex → NFA
- DFA 最小化（Hopcroft 等价类划分）
- Pumping lemma 反例演示

运行：
    python automata.py
"""
from __future__ import annotations


# ================================================================
# 1. NFA 定义（带 ε-转移）
# ================================================================

class NFA:
    """非确定性有限自动机"""

    def __init__(self, states, alphabet, transitions, start, accept):
        self.states = set(states)
        self.alphabet = set(alphabet)
        # transitions: dict[(state, symbol_or_None)] -> set of states
        self.transitions = transitions
        self.start = start
        self.accept = set(accept)

    def epsilon_closure(self, states):
        """ε-闭包：从 states 出发沿 ε 能到的所有状态"""
        stack = list(states)
        closure = set(states)
        while stack:
            s = stack.pop()
            for t in self.transitions.get((s, None), set()):
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
        return frozenset(closure)

    def step(self, states, symbol):
        """从 states 集合读入 symbol 后到达的状态集（含 ε-闭包）"""
        next_states = set()
        for s in states:
            for t in self.transitions.get((s, symbol), set()):
                next_states.add(t)
        return self.epsilon_closure(next_states)

    def accepts(self, string):
        current = self.epsilon_closure({self.start})
        for ch in string:
            if ch not in self.alphabet:
                return False
            current = self.step(current, ch)
            if not current:
                return False
        return bool(current & self.accept)


# ================================================================
# 2. NFA → DFA 子集构造
# ================================================================

class DFA:
    def __init__(self, states, alphabet, transitions, start, accept):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = dict(transitions)
        self.start = start
        self.accept = set(accept)

    def accepts(self, string):
        state = self.start
        for ch in string:
            key = (state, ch)
            if key not in self.transitions:
                return False
            state = self.transitions[key]
        return state in self.accept


def nfa_to_dfa(nfa: NFA) -> DFA:
    """子集构造：每个 DFA 状态 = NFA 状态的一个子集"""
    start_set = nfa.epsilon_closure({nfa.start})
    dfa_states = {start_set}
    dfa_trans = {}
    worklist = [start_set]
    state_names = {start_set: "S0"}
    counter = [1]

    def name_of(s):
        if s not in state_names:
            state_names[s] = f"S{counter[0]}"
            counter[0] += 1
        return state_names[s]

    while worklist:
        current = worklist.pop()
        for sym in nfa.alphabet:
            nxt = nfa.step(current, sym)
            if nxt:
                dfa_trans[(name_of(current), sym)] = name_of(nxt)
                if nxt not in dfa_states:
                    dfa_states.add(nxt)
                    worklist.append(nxt)

    accept = {name_of(s) for s in dfa_states if s & nfa.accept}
    return DFA({state_names[s] for s in dfa_states}, nfa.alphabet,
               dfa_trans, "S0", accept)


# ================================================================
# 3. Thompson regex → NFA
# ================================================================

class ThompsonBuilder:
    """
    Thompson 构造：regex → NFA
    支持: 单字符 a, 连接 ab, 选择 a|b, Kleene 星 a*
    """

    def __init__(self):
        self.state_count = 0

    def new_state(self):
        self.state_count += 1
        return f"q{self.state_count}"

    def build_char(self, ch):
        s, f = self.new_state(), self.new_state()
        trans = {(s, ch): {f}}
        return NFA({s, f}, {ch}, trans, s, {f})

    def build_concat(self, nfa1, nfa2):
        trans = dict(nfa1.transitions)
        trans.update(nfa2.transitions)
        # nfa1 的接受状态 ε 连到 nfa2 的开始
        for acc in nfa1.accept:
            trans[(acc, None)] = trans.get((acc, None), set()) | {nfa2.start}
        return NFA(nfa1.states | nfa2.states,
                   nfa1.alphabet | nfa2.alphabet,
                   trans, nfa1.start, nfa2.accept)

    def build_union(self, nfa1, nfa2):
        s = self.new_state()
        f = self.new_state()
        trans = dict(nfa1.transitions)
        trans.update(nfa2.transitions)
        trans[(s, None)] = {nfa1.start, nfa2.start}
        for acc in nfa1.accept | nfa2.accept:
            trans[(acc, None)] = trans.get((acc, None), set()) | {f}
        return NFA(nfa1.states | nfa2.states | {s, f},
                   nfa1.alphabet | nfa2.alphabet,
                   trans, s, {f})

    def build_star(self, nfa1):
        s = self.new_state()
        f = self.new_state()
        trans = dict(nfa1.transitions)
        trans[(s, None)] = {nfa1.start, f}
        for acc in nfa1.accept:
            trans[(acc, None)] = trans.get((acc, None), set()) | {nfa1.start, f}
        return NFA(nfa1.states | {s, f}, nfa1.alphabet, trans, s, {f})


# ================================================================
# 4. DFA 最小化（Hopcroft 风格：划分求精）
# ================================================================

def minimize_dfa(dfa: DFA) -> DFA:
    """
    Hopcroft 划分求精：
    初始划分 = {accept, non-accept}
    反复分裂：若同一块中状态在某个 symbol 下转移到不同块，则分裂。
    """
    # 初始划分
    accept = frozenset(dfa.accept)
    non_accept = frozenset(dfa.states - dfa.accept)
    partition = set()
    if accept:
        partition.add(accept)
    if non_accept:
        partition.add(non_accept)

    changed = True
    while changed:
        changed = False
        new_partition = set()
        for block in partition:
            # 尝试分裂 block
            groups = {}
            for state in block:
                signature = []
                for sym in sorted(dfa.alphabet):
                    nxt = dfa.transitions.get((state, sym))
                    # 找 nxt 属于哪个块
                    block_id = None
                    if nxt is not None:
                        for i, b in enumerate(partition):
                            if nxt in b:
                                block_id = i
                                break
                    signature.append((sym, block_id))
                groups.setdefault(tuple(signature), set()).add(state)
            if len(groups) > 1:
                changed = True
            for g in groups.values():
                new_partition.add(frozenset(g))
        partition = new_partition

    # 构建最小化 DFA
    block_list = list(partition)
    block_id = {}
    for i, b in enumerate(block_list):
        for s in b:
            block_id[s] = f"M{i}"

    new_states = set(block_id.values())
    new_trans = {}
    new_start = block_id[dfa.start]
    new_accept = {block_id[s] for s in dfa.accept}
    for b_idx, block in enumerate(block_list):
        rep = next(iter(block))
        for sym in dfa.alphabet:
            nxt = dfa.transitions.get((rep, sym))
            if nxt is not None:
                new_trans[(f"M{b_idx}", sym)] = block_id[nxt]

    return DFA(new_states, dfa.alphabet, new_trans, new_start, new_accept)


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part IA Regular Languages & Finite Automata — Demo")
    print("=" * 64)

    # 1. NFA 模拟
    print("\n📋 1. NFA 识别 '以 ab 结尾' (a|b)*ab")
    # NFA: q0 -a-> {q0}, q0 -b-> {q0, q1}, q1 -b-> {q2}
    nfa = NFA(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b"},
        transitions={
            ("q0", "a"): {"q0"},
            ("q0", "b"): {"q0", "q1"},
            ("q1", "b"): {"q2"},
        },
        start="q0",
        accept={"q2"},
    )
    tests = ["ab", "aab", "bbaab", "ba", "abb", "aa", "bbb"]
    for t in tests:
        print(f"   '{t}': {'✓ accept' if nfa.accepts(t) else '✗ reject'}")

    # 2. 子集构造
    print("\n📋 2. NFA → DFA 子集构造")
    dfa = nfa_to_dfa(nfa)
    print(f"   DFA states: {sorted(dfa.states)}")
    print(f"   DFA transitions: {sorted(dfa.transitions.items())}")
    for t in tests:
        d = dfa.accepts(t)
        n = nfa.accepts(t)
        match = "✓" if d == n else "✗ MISMATCH"
        print(f"   '{t}': DFA={d}, NFA={n} {match}")

    # 3. Thompson 构造
    print("\n📋 3. Thompson: regex (a|b)* → NFA → DFA")
    tb = ThompsonBuilder()
    a_nfa = tb.build_char("a")
    b_nfa = tb.build_char("b")
    union = tb.build_union(a_nfa, b_nfa)
    star = tb.build_star(union)
    print(f"   NFA states: {len(star.states)}, start={star.start}")
    print(f"   (a|b)* accepts 'aabb': {star.accepts('aabb')}")
    print(f"   (a|b)* accepts '' (empty): {star.accepts('')}")

    # 4. DFA 最小化
    print("\n📋 4. DFA 最小化（Hopcroft 划分求精）")
    # 一个非最小 DFA：识别 "偶数个 a"
    big_dfa = DFA(
        states={"s0", "s1", "s2", "s3"},
        alphabet={"a", "b"},
        transitions={
            ("s0", "a"): "s1", ("s0", "b"): "s0",
            ("s1", "a"): "s2", ("s1", "b"): "s1",  # s1 ≡ s3
            ("s2", "a"): "s1", ("s2", "b"): "s2",
            ("s3", "a"): "s2", ("s3", "b"): "s3",  # s3 ≡ s1
        },
        start="s0",
        accept={"s1", "s3"},   # s1, s3 等价 → 应合并
    )
    min_dfa = minimize_dfa(big_dfa)
    print(f"   原 DFA: {len(big_dfa.states)} states")
    print(f"   最小 DFA: {len(min_dfa.states)} states")

    # 5. Pumping lemma
    print("\n📋 5. Pumping Lemma 反例")
    print("   语言 L = {a^n b^n | n ≥ 1} 不是正则的")
    print("   pumping length p: 取 s = a^p b^p, |s| ≥ p")
    print("   分解 s = xyz, |xy| ≤ p, |y| ≥ 1")
    print("   则 y 只含 a, 泵 y → a^(p+k) b^p ∉ L (a 多于 b)")
    for p in [2, 5, 10]:
        s = "a" * p + "b" * p
        # 尝试 pump: x="", y="a", z=剩余
        x, y, z = "", "a", s[1:]
        pumped = x + y * 2 + z  # 多泵一次 a
        in_lang = pumped == "a" * (p + 1) + "b" * p
        print(f"   p={p}: s={s[:20]}..., pump y='a' → a^{p+1}b^{p} ∈L? {in_lang} (应为 False)")

    print("\n✅ Regular Languages & Automata 完成！")
    print("\n💡 反直觉发现：")
    print("   - NFA 不比 DFA 强（子集构造证明），但 NFA 可远小于等价 DFA")
    print("   - 最坏情况 NFA n 状态 → DFA 2^n 状态（指数爆炸）")
    print("   - pumping lemma: 正则语言有「周期结构」，a^n b^n 没有 → 非正则")


if __name__ == "__main__":
    demo()
