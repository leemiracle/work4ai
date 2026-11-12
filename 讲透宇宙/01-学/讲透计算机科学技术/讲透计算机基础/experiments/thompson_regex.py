# -*- coding: utf-8 -*-
"""
thompson_regex.py —— 走廊①的正典实验：正则 → Thompson NFA → 子集构造 DFA
对应章：00-体系结构（表达力层级）、03-可构造与结构（描述效率≠执行效率）、
        04-计算机基础转代码（走廊①完全保真样板）

实验内容：
  1. 解析正则（支持 | * ( ) . 连接 与 {n} 重复语法糖）
  2. Thompson 构造：AST → NFA（状态数线性）
  3. 子集构造：NFA → DFA（ε-闭包 + move）
  4. 经典指数族 (a|b)*a(a|b){n}（"倒数第 n+1 个字符是 a"）：
     实测 NFA 状态数线性增长、DFA 状态数指数增长——
     "同一语言，描述短≠执行结构小"的最小现场（DFA 最少状态 = 2^(n+1) 教材经典）
  5. NFA 模拟与 DFA 匹配在随机串上判定一致（构造正确性自验证）

运行：python thompson_regex.py
"""
import random

# ── 1. 正则解析（递归下降，支持 a|b、a*、ab、( )、. 、x{n}） ──────────────
class Node:
    def __init__(self, kind, *kids):
        self.kind, self.kids = kind, kids  # kind ∈ {sym, alt, cat, star}

def parse(s):
    pos = 0
    def peek(): return s[pos] if pos < len(s) else None
    def alt():
        nonlocal pos
        left = cat()
        if peek() == '|':
            pos += 1
            return Node('alt', left, alt())
        return left
    def cat():
        nonlocal pos
        parts = []
        while peek() is not None and peek() not in '|)':
            parts.append(post())
        return parts[0] if len(parts) == 1 else (Node('cat', *parts) if parts else Node('sym', ''))
    def post():
        nonlocal pos
        n = prim()
        while True:
            c = peek()
            if c == '*':
                pos += 1; n = Node('star', n)
            elif c == '{':  # x{n} 语法糖：展开为 n 份 cat
                pos += 1
                k = ''
                while peek() != '}':
                    k += s[pos]; pos += 1
                pos += 1  # 吃掉 }
                n = Node('cat', *([n] * int(k)))
            else:
                return n
    def prim():
        nonlocal pos
        c = peek()
        if c == '(':
            pos += 1
            inner = alt()
            assert peek() == ')', "括号不匹配"
            pos += 1
            return inner
        if c == '.':
            pos += 1
            return Node('sym', '.')
        pos += 1
        return Node('sym', c)
    tree = alt()
    assert pos == len(s), f"未消费完: {s[pos:]}"
    return tree

# ── 2. Thompson 构造：AST → NFA ────────────────────────────────────────────
class NFA:
    def __init__(self):
        self.next = 0
        self.eps = {}        # state -> set(states)
        self.trans = {}      # (state, ch) -> set(states)
    def new(self):
        self.eps[self.next] = set(); self.next += 1
        return self.next - 1
    def build(self, node):  # 返回 (start, end)
        if node.kind == 'sym':
            s, e = self.new(), self.new()
            if node.kids[0]:
                self.trans.setdefault((s, node.kids[0]), set()).add(e)
            else:
                self.eps[s].add(e)  # 空串
            return s, e
        if node.kind == 'cat':
            first_s, _ = self.build(node.kids[0])
            prev_e = first_s
            prev_s = first_s
            ss, ee = prev_s, None
            starts, ends = [], []
            for k in node.kids:
                a, b = self.build(k); starts.append(a); ends.append(b)
            for a, b in zip(starts[:-1], starts[1:]):
                self.eps[ends[starts.index(a)]].add(b) if False else None
            # 重新正确连接（上面 index 写法易错，直接重写）
            for i in range(len(starts) - 1):
                self.eps[ends[i]].add(starts[i + 1])
            return starts[0], ends[-1]
        if node.kind == 'alt':
            s, e = self.new(), self.new()
            for k in node.kids:
                a, b = self.build(k)
                self.eps[s].add(a); self.eps[b].add(e)
            return s, e
        if node.kind == 'star':
            s, e = self.new(), self.new()
            a, b = self.build(node.kids[0])
            self.eps[s] |= {a, e}; self.eps[b] |= {a, e}
            return s, e
    def states(self):
        return self.next

# ── 3. 子集构造：NFA → DFA ────────────────────────────────────────────────
def eps_closure(nfa, S):
    stack, seen = list(S), set(S)
    while stack:
        u = stack.pop()
        for v in nfa.eps.get(u, ()):
            if v not in seen:
                seen.add(v); stack.append(v)
    return frozenset(seen)

def subset_construction(nfa, start, end, alphabet):
    q0 = eps_closure(nfa, {start})
    dfa_trans, D, queue = {}, {q0: 0}, [q0]
    accept = set()
    while queue:
        Q = queue.pop()
        if end in Q:
            accept.add(D[Q])
        for ch in alphabet:
            moved = set()
            for u in Q:
                moved |= nfa.trans.get((u, ch), set())
            if not moved:
                continue
            T = eps_closure(nfa, moved)
            if T not in D:
                D[T] = len(D); queue.append(T)
            dfa_trans[(D[Q], ch)] = D[T]
    return D, dfa_trans, accept

def dfa_match(trans, accept, s, dfa_id_of=None):
    st = 0
    for ch in s:
        if (st, ch) not in trans:
            return False
        st = trans[(st, ch)]
    return st in accept

def nfa_accepts(nfa, start, end, s):
    cur = eps_closure(nfa, {start})
    for ch in s:
        nxt = set()
        for u in cur:
            nxt |= nfa.trans.get((u, ch), set())
        cur = eps_closure(nfa, nxt) if nxt else frozenset()
        if not cur:
            return False
    return end in cur

# ── 4. 经典指数族实测 ──────────────────────────────────────────────────────
print("═" * 62)
print("经典语言 (a|b)*a(a|b){n}（倒数第 n+1 个字符是 a）")
print(f"{'n':>3} {'NFA状态':>8} {'DFA状态':>10} {'DFA/NFA':>8}")
print("-" * 62)
nfa_counts, dfa_counts = [], []
for n in range(1, 11):
    rx = f"(a|b)*a(a|b){{{n}}}"
    nfa = NFA()
    s, e = nfa.build(parse(rx))
    D, T, A = subset_construction(nfa, s, e, {'a', 'b'})
    nfa_counts.append(nfa.states()); dfa_counts.append(len(D))
    print(f"{n:>3} {nfa.states():>8} {len(D):>10} {len(D)/nfa.states():>7.1f}x")
print("-" * 62)

# ── 断言 1：NFA 线性、DFA 指数 ────────────────────────────────────────────
ratio_nfa = nfa_counts[-1] / nfa_counts[2]     # n=10 vs n=3
ratio_dfa = dfa_counts[-1] / dfa_counts[2]
assert ratio_dfa > 100, f"DFA 增长未达指数级: {ratio_dfa:.0f}"
assert ratio_nfa < 2.5, f"NFA 增长超出线性: {ratio_nfa:.1f}"
assert dfa_counts[4] == 2 ** 6 + 1, f"n=5 的 DFA 状态数 != 2^(n+1)+1=65: {dfa_counts[4]}"
print(f"[断言1 ✓] n:3→10  NFA 增长 {ratio_nfa:.1f}×（线性），"
      f"DFA 增长 {ratio_dfa:.0f}×（指数，理论 2^7=128）；n=5 时 DFA=2^6+1=65 实测 {dfa_counts[4]}")

# ── 断言 2：DFA 状态数 = 2^(n+1)+1（滑窗类 + 1 个陷阱态） ─────────────────
for n in (1, 2, 3, 4):
    assert dfa_counts[n - 1] == 2 ** (n + 1) + 1, f"n={n}: {dfa_counts[n-1]} != {2**(n+1)+1}"
print("[断言2 ✓] n=1..4 DFA 状态数恰为 2^(n+1)+1（Myhill–Nerode 滑窗类+陷阱态）")

# ── 断言 3：NFA/DFA 判定一致（随机串自验证） ───────────────────────────────
random.seed(42)
n = 4
rx = f"(a|b)*a(a|b){{{n}}}"
nfa = NFA(); s, e = nfa.build(parse(rx))
D, T, A = subset_construction(nfa, s, e, {'a', 'b'})
mismatch = 0
for _ in range(500):
    L = random.randint(0, 12)
    w = ''.join(random.choice('ab') for _ in range(L))
    if nfa_accepts(nfa, s, e, w) != dfa_match(T, A, w):
        mismatch += 1
assert mismatch == 0, f"NFA/DFA 判定不一致 {mismatch} 例"
hand = {'': False, 'a': False, 'aabaa': True, 'ababa': True, 'babaa': False}  # n=4: 倒数第5字符
for w, want in hand.items():
    if len(w) >= n + 1:
        assert dfa_match(T, A, w) == want, f"手例 {w} 判定错"
print(f"[断言3 ✓] 500 条随机串 NFA/DFA 判定全一致；手例核对通过")

# ── 尾声：ReDoS 对照（同一语言的另一种实现命运） ───────────────────────────
import re, time
pat = re.compile("(a+)+$")          # 经典灾难回溯模式（指数级回溯）
poison = "a" * 18 + "b"             # 18 层嵌套选择 → 数十万次回溯
t0 = time.perf_counter(); pat.match(poison); t1 = time.perf_counter()
print(f"\n带走：同一语言，Thompson/NFA 路线状态线性（n=10 时 {nfa_counts[-1]} 态），"
      f"\n      子集构造 DFA 指数（{dfa_counts[-1]} 态）——描述效率与执行结构的分离。"
      f"\n      回溯引擎（Python re 近似演示）在毒输入上耗时 {(t1-t0)*1000:.1f}ms——"
      f"\n      这就是 RE2 选择自动机路线、2016 年 Stack Overflow 宕机 34 分钟的全部原因。")
print("\n[ALL ASSERTS PASSED] 走廊①（正则→引擎）是完全保真的样板：每一步都是定理的直接实现。")
