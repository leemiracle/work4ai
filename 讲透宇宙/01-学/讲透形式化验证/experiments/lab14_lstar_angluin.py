#!/usr/bin/env python3
"""lab14 · Angluin L*：观察表从零学出 "(a|b)*ab" 的最小 DFA（14 章 §二/§三）。
设定：MAT（最小充分教师）模型——学习者只有两种提问权：
  成员查询 MQ(w)：词 w 是否被目标接受；等价查询 EQ(H)：假设 H 与目标是否等价（不等给反例）。
目标 DFA（三态，即 (a|b)*ab 的最小自动机）：
  q0 --a--> q1 --b--> q2(接受)；q0 --b--> q0；q1 --a--> q1；q2 --a--> q1, --b--> q0
等价查询用"乘积 BFS 找最短区分词"精确实现（教学玩具里教师是完美的）。
手推锚点（14 章 §三）：观察表从 S={ε},E={ε} 起，经闭合/一致修复与反例前缀入行，
  收敛出的假设与目标等价（无区分词），且状态数 = minify(目标) = 3。
风格沿用博弈论系列：docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
from collections import deque

from automata.fa.dfa import DFA

TARGET = DFA(
    states={"q0", "q1", "q2"},
    input_symbols={"a", "b"},
    transitions={"q0": {"a": "q1", "b": "q0"},
                 "q1": {"a": "q1", "b": "q2"},
                 "q2": {"a": "q1", "b": "q0"}},
    initial_state="q0",
    final_states={"q2"},
)

mq_count = 0


def mq(w):
    """成员查询（计数供章内引用）。"""
    global mq_count
    mq_count += 1
    return TARGET.accepts_input(w)


def find_distinguish(target: DFA, hyp: DFA):
    """等价查询：乘积 BFS 找最短区分词；无则 None（等价）。"""
    if hyp is None:
        return ""
    seen = {(target.initial_state, hyp.initial_state)}
    q = deque([("", target.initial_state, hyp.initial_state)])
    while q:
        w, ts, hs = q.popleft()
        if (ts in target.final_states) != (hs in hyp.final_states):
            return w
        for ch in sorted(target.input_symbols):
            nt = target.transitions[ts][ch]
            nh = hyp.transitions[hs][ch]
            if (nt, nh) not in seen:
                seen.add((nt, nh))
                q.append((w + ch, nt, nh))
    return None


class Table:
    """观察表：S（行标签）/ E（列标签）/ T（成员值）。EXP = S∪S·Σ 由 fill 维护。"""

    def __init__(self):
        self.S = [""]
        self.E = [""]
        self.T = {}
        self.fill()

    def fill(self):
        for s in self.S + [s + c for s in self.S for c in "ab" if s + c not in self.S]:
            for e in self.E:
                if s + e not in self.T:
                    self.T[s + e] = mq(s + e)

    def row(self, s):
        return tuple(self.T.get(s + e) for e in self.E)

    def closed(self):
        return all(any(self.row(x) == self.row(s) for s in self.S)
                   for x in self._ext())

    def close(self):
        for x in self._ext():
            if not any(self.row(x) == self.row(s) for s in self.S):
                self.S.append(x)
                self.fill()
                return x
        return None

    def consistent(self):
        for s1 in self.S:
            for s2 in self.S:
                if self.row(s1) == self.row(s2):
                    for c in "ab":
                        if self.row(s1 + c) != self.row(s2 + c):
                            return (s1, s2, c)
        return None

    def _ext(self):
        return [s + c for s in self.S for c in "ab" if s + c not in self.S]

    def hypothesis(self):
        """从表构造假设 DFA：相同行 → 同一状态（一致条件保证转移良定义）。"""
        rows = {}
        for s in self.S:
            if self.row(s) not in rows:
                rows[self.row(s)] = f"q{len(rows)}"
        trans, finals = {}, set()
        for s in self.S:
            st = rows[self.row(s)]
            trans[st] = {c: rows[self.row(s + c)] for c in "ab"}
            if self.T[s]:
                finals.add(st)
        return DFA(states=set(rows.values()), input_symbols={"a", "b"},
                   transitions=trans, initial_state=rows[self.row("")],
                   final_states=finals)


def lstar():
    t = Table()
    snapshots = [(list(t.S), list(t.E), "初始")]
    rounds = 0
    eq_count = 0
    while True:
        rounds += 1
        while not t.closed() or t.consistent() is not None:
            if not t.closed():
                x = t.close()
                snapshots.append((list(t.S), list(t.E), f"闭合修复（加入行 {x!r}）"))
            else:
                s1, s2, c = t.consistent()
                t.E.append(c)
                t.fill()
                snapshots.append((list(t.S), list(t.E), f"一致修复（加入列 {c!r}：{s1!r}~{s2!r} 行同而后继异）"))
        hyp = t.hypothesis()
        eq_count += 1
        w = find_distinguish(TARGET, hyp)
        if w is None:
            return hyp, snapshots, rounds, eq_count
        for i in range(len(w) + 1):        # 反例全部前缀入 S（经典策略）
            if w[:i] not in t.S:
                t.S.append(w[:i])
        t.fill()
        snapshots.append((list(t.S), list(t.E), f"反例 {w!r} 前缀入行"))


print("=" * 68)
print("E1 · L* 学习 (a|b)*ab：观察表演化全记录")
print("=" * 68)
print("目标：三态最小 DFA（q2 接受；串以 ab 结尾才接受）")
hyp, snaps, rounds, eqs = lstar()
for i, (S, E, note) in enumerate(snaps):
    print(f"  [{i}] S={S} E={E} ← {note}")
w = find_distinguish(TARGET, hyp)
assert w is None
print(f"\n轮数 {rounds}，等价查询 {eqs} 次，成员查询 {mq_count} 次")
print(f"最终假设 {len(hyp.states)} 态，与目标无区分词 —— 等价 ✓")

print("\n" + "=" * 68)
print("E2 · automata-lib 交叉对拍")
print("=" * 68)
m = TARGET.minify()
assert len(m.states) == len(hyp.states) == 3, (len(m.states), len(hyp.states))
for w in ["", "a", "ab", "abab", "ba", "aab", "abb", "bbab"]:
    assert TARGET.accepts_input(w) == hyp.accepts_input(w), w
print(f"minify(目标)={len(m.states)} 态 = 假设 {len(hyp.states)} 态 ✓")
print("抽查 8 个词（ε/a/ab/abab/ba/aab/abb/bbab）双方接受一致 ✓")
print("→ L* 输出恰为最小自动机（Myhill-Nerode：行=等价类，最小性是定理不是巧合）")
print("\nlab14 全部自检通过")
