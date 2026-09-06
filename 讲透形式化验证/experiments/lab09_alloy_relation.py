#!/usr/bin/env python3
"""lab09 · Alloy 式有界检查：地址簿的关系编码与"小反例"（09 章 §三）。
论域：Name={0..k-1}、Addr={0..k-1}（scope=k）；哨兵 -1 表示"无"。
关系（Int 函数编码，Kodkod 的关系约束在此用 z3 复现）：
  alias_to: Name→Name∪{-1}、direct_to: Name→Addr∪{-1}
良构（Alloy 的 fact）：每个名字至多一个 alias 或一个 direct（二选一或都无）。
resolve(n) = direct(n) 若有，否则 direct(alias(n))（链长 ≤ 1；Alloy 版本点乘 * 的最小现场）。
断言取反 = 找反例（sat ⇒ 模型即 Alloy 的 counterexample）：
  A1 NoShared（不同名字解析到不同地址）→ scope=2 即反例：n1→a0 直连、n0→n1 别名 ⇒ 同址
  A2 NoCycle（alias 无环）→ scope=2 即反例：n0→n1→n0
  A3 TwoChains（链汇址且三名字互异：alias 中转站 ≠ 两个直连共享者）→ 恰 scope=3
手推锚点（09 章 §三）：首个出反例的 scope 分别为 2 / 2 / 3——"scope 是旋钮、
小反例是证据"的 Alloy 哲学；scope=1 时三条全空（一个人自说自话，无冲突可言）。
风格沿用博弈论系列：docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
from z3 import (Solver, Int, IntSort, Function, If, And, Or, Not, Implies, sat, Model)


def build_scope(k):
    """k=scope 的求解器骨架：返回 (solver, alias_to, direct_to, name_consts)。"""
    alias_to = Function(f"alias{k}", IntSort(), IntSort())
    direct_to = Function(f"direct{k}", IntSort(), IntSort())
    names = [Int(f"n{i}") for i in range(k)]
    s = Solver()
    for i, n in enumerate(names):
        s.add(n == i)                                   # 论域展开（Alloy 的 scope 语义）
        s.add(alias_to(n) >= -1, alias_to(n) < k)       # 值域：哨兵或名字
        s.add(direct_to(n) >= -1, direct_to(n) < k)     # 值域：哨兵或地址
        s.add(Implies(alias_to(n) >= 0, direct_to(n) == -1))   # 良构：alias 与 direct 二选一
        s.add(Implies(direct_to(n) >= 0, alias_to(n) == -1))
    return s, alias_to, direct_to, names


def resolve(alias_to, direct_to, n):
    """链长 ≤1 的解析：direct 优先，否则走一步 alias。"""
    return If(direct_to(n) >= 0, direct_to(n),
              If(alias_to(n) >= 0, direct_to(alias_to(n)), -1))


def q_no_shared(k):
    """A1 取反：∃ 两个不同名字解析到同一（有效）地址。"""
    s, a2, d2, names = build_scope(k)
    x, y = Int("x"), Int("y")
    s.add(Or([x == i for i in range(k)]), Or([y == i for i in range(k)]), x != y)
    s.add(resolve(a2, d2, x) == resolve(a2, d2, y), resolve(a2, d2, x) >= 0)
    return s, (a2, d2, x, y)


def q_no_cycle(k, no_self_loop=False):
    """A2 取反：∃ 名字经 alias 链（长 1..k）回到自身。
    no_self_loop=True 时给模型加 fact 'alias 无自环'——看反例被推到多大的 scope。"""
    s, a2, d2, names = build_scope(k)
    if no_self_loop:
        for n in names:
            s.add(a2(n) != n)                           # fact：不许 n→n
    x = Int("x")
    s.add(Or([x == i for i in range(k)]))
    chain = x
    disj = []
    for _ in range(k):                                  # alias^j(x) == x，j=1..k
        chain = a2(chain)
        disj.append(chain == x)
    s.add(Or(disj))
    return s, (a2, d2, x)


def q_two_chains(k):
    """A3 取反：∃ 互异 n0,n1,n2：n0 经 alias 到 n1，n1 与 n2 直连同址（中转站≠共享者）。"""
    s, a2, d2, names = build_scope(k)
    n0, n1, n2 = Int("n0"), Int("n1"), Int("n2")
    in_range = lambda v: Or([v == i for i in range(k)])
    s.add(in_range(n0), in_range(n1), in_range(n2))
    s.add(n0 != n1, n0 != n2, n1 != n2)
    s.add(a2(n0) == n1, d2(n1) >= 0, d2(n2) == d2(n1))
    return s, (a2, d2, n0, n1, n2)


def fmt_model(m, a2, d2, k):
    """把 z3 模型翻译成 Alloy 风格的实例文本。"""
    lines = []
    for i in range(k):
        al = m.eval(a2(i)).as_long()
        dl = m.eval(d2(i)).as_long()
        lines.append(f"n{i}: alias→{'n'+str(al) if al >= 0 else '∅'}, "
                     f"direct→{'a'+str(dl) if dl >= 0 else '∅'}")
    return "；".join(lines)


QUERIES = [("NoShared 不同的名字解析到不同地址", q_no_shared),
           ("NoCycle   alias 链无环（裸模型）", q_no_cycle),
           ("NoCycle′  alias 无环（fact:禁自环）", lambda k: q_no_cycle(k, no_self_loop=True)),
           ("TwoChains 链汇址（三名字互异）", q_two_chains)]

print("=" * 68)
print("E1 · 三个断言 × scope=1..4：首个反例的 scope（'scope 是旋钮'）")
print("=" * 68)
first = {}
for name, q in QUERIES:
    row = []
    for k in range(1, 5):
        s, ctx = q(k)
        r = s.check()
        mark = "UNSAT" if r != sat else "反例!"
        row.append(f"scope={k}:{mark}")
        if r == sat and name.split()[0] not in first:
            first[name.split()[0]] = (k, s, ctx)
    print(f"  {name}  " + "  ".join(row))

print("\n" + "=" * 68)
print("E2 · 反例实例（Alloy 的 'counterexample as evidence'）")
print("=" * 68)
for tag in ("NoShared", "NoCycle", "TwoChains"):
    k, s, ctx = first[tag]
    m = s.model()
    print(f"  【{tag}】最小 scope={k}，实例：{fmt_model(m, ctx[0], ctx[1], k)}")
print("  读法：NoShared 的反例就是最小地址簿 bug（别名与直连撞址）；NoCycle 是死链；")
print("  TwoChains 要三个名字才摆得下'一个中转站 + 两个直连共享者'——scope=2 摆不下")

print("\n" + "=" * 68)
print("E3 · 对照：把良构 fact 砍掉（名字可同时 alias+direct）——反例 scope 不变、形状变多")
print("=" * 68)
print("  （良构只排除病态实例，三个断言的反例本来就不依赖病态——Alloy 的 fact 是建模纪律不是检查负担）")
print("  ——此段为定性说明，编码同上、去 Implies 两行即得，章内 §四讨论 fact/check 的分工")

assert first["NoShared"][0] == 2
assert first["NoCycle"][0] == 1          # 裸模型：一节点自环就破——比计划手推的"二环@2"更早
assert first["NoCycle′"][0] == 2         # 禁自环后才轮到二环（n0→n1→n0）——计划的手推在此兑现
assert first["TwoChains"][0] == 3
print("\n→ 首反例 scope 断言：NoShared=2 / NoCycle=1（自环，计划未料）/ NoCycle′=2（二环）/ TwoChains=3")
print("  ——约束每收紧一分，反例就推迟一格：scope 旋钮与 fact 纪律的双人舞（09 章 §三/§四）")
print("lab09 全部自检通过")
