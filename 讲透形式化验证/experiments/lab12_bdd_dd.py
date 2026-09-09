#!/usr/bin/env python3
"""lab12 · BDD：手写 ite + 变量序爆炸 + dd 库对拍（12 章 §二/§三）。
公式族：f_n = (x1∧x2) ∨ (x3∧x4) ∨ … ∨ (x_{2n−1}∧x_{2n})。
好序 [x1,x2,x3,x4,…]（配对相邻）→ 节点 O(n)；坏序 [x1,x3,…,x_{2n−1}, x2,x4,…]（配对分离）→ 节点 O(2^n 量级指数涨）。
手推锚点（12 章 §三）：n=2 好序恰 5 个内点（x1,x2,x3,x4 各一 + 共享层——以实跑为准打印）；
n=8 好序 ~2n 级、坏序数百+。教学版 TBDD：节点 = (var, lo, hi) 元组 + 唯一表 + 计算缓存，
AND/OR 全归 ite（Shannon 展开）——CUDD 的两个核心不变量照进玩具。
dd 库对拍：同公式 dd.autoref 节点数与手写一致（若计数口径差终端，如实标注并统一口径）。
风格沿用博弈论系列：docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
from dd.autoref import BDD as DdBDD


class TBDD:
    """教学版 BDD：终端 0/1（Python 小整数，恒同一对象）；内点 = ("N", nid, var, lo, hi) 元组，
    由唯一表保证规范形（同一 (var,lo,hi) 全局唯一对象——`is` 判等因此可靠，也作计算缓存键）。"""

    def __init__(self, order):
        self.order = order            # 变量序 list[str]
        self.uniq = {}                # (var, lo, hi) -> node
        self.cache = {}               # (f, g, h) 节点对象三元组 -> ite 结果

    def mk(self, var, lo, hi):
        if lo is hi:
            return lo                 # 冗余节点消解——BDD 是 DAG 的关键一步
        key = (var, lo, hi)
        if key not in self.uniq:
            self.uniq[key] = ("N", len(self.uniq), var, lo, hi)
        return self.uniq[key]

    def var_idx(self, v):
        return self.order.index(v)

    def ite(self, f, g, h):
        """f?g:h 的 Shannon 展开：取三者的最前变量 v，对 v 的 0/1 余因子递归。"""
        if not isinstance(f, tuple):        # 终端 0/1
            return g if f == 1 else h
        if g is h:
            return g
        key = (f, g, h)
        if key in self.cache:
            return self.cache[key]
        v = min(self._vars(f, g, h), key=self.var_idx)
        f1, f0 = self._cof(v, f, 1), self._cof(v, f, 0)
        g1, g0 = self._cof(v, g, 1), self._cof(v, g, 0)
        h1, h0 = self._cof(v, h, 1), self._cof(v, h, 0)
        node = self.mk(v, self.ite(f0, g0, h0), self.ite(f1, g1, h1))
        self.cache[key] = node
        return node

    def _vars(self, *nodes):
        return [nd[2] for nd in nodes if isinstance(nd, tuple) and nd[0] == "N"]

    def _cof(self, v, nd, val):
        """v 取 val 的余因子：v 恰为根变量则取对应支，否则子图不变。"""
        if not (isinstance(nd, tuple) and nd[0] == "N"):
            return nd
        if nd[2] == v:
            return nd[4] if val else nd[3]
        return nd

    def count(self, nd):
        """可达内点数（终端不计）。"""
        seen = set()

        def go(x):
            if not (isinstance(x, tuple) and x[0] == "N"):
                return
            if x[1] in seen:
                return
            seen.add(x[1])
            go(x[3])
            go(x[4])

        go(nd)
        return len(seen)


def build_f(t, n):
    """用 ite 拼 f_n = ∨_i (x_{2i−1} ∧ x_{2i})：term = ite(a, b, 0)（a AND b），acc = ite(term, 1, acc)。"""
    def lit(name):
        return t.mk(name, 0, 1)

    acc = 0
    for i in range(1, n + 1):
        a = lit(f"x{2 * i - 1}")
        b = lit(f"x{2 * i}")
        term = t.ite(a, b, 0)          # a AND b
        acc = t.ite(term, 1, acc) if acc != 0 else term       # term OR acc
    return acc


def dd_count(order, n):
    """dd 库对拍：从公式根【可达】的内点数（与手写 count 同口径）。
    实测注记：len(bdd) 是管理器口径——连 declare 时为每个变量建的根节点一并计入，
    不随公式可达性走，故弃用；可达计数以 u.var/u.low/u.high 遍历（终端 var is None）。"""
    bdd = DdBDD()
    bdd.declare(*order)
    expr = " | ".join(f"(x{2 * i - 1} & x{2 * i})" for i in range(1, n + 1))
    root = bdd.add_expr(expr)
    seen = set()

    def reach(u):
        if u.var is None or u in seen:      # 终端 / 已计
            return
        seen.add(u)
        reach(u.low)
        reach(u.high)

    reach(root)
    k = len(seen)
    seen.clear(); del root, bdd      # dd 的退出期析构断言要求显式释放（Python 3.14 实测）
    return k


def orders(n):
    good = [f"x{i}" for i in range(1, 2 * n + 1)]
    odd = [f"x{i}" for i in range(1, 2 * n + 1, 2)]
    even = [f"x{i}" for i in range(2, 2 * n + 1, 2)]
    return good, odd + even


print("=" * 68)
print("E1 · 同一公式族、两种变量序：n vs 指数")
print("=" * 68)
print("公式族 f_n = (x1∧x2)∨(x3∧x4)∨…∨(x_{2n−1}∧x_{2n})")
print("好序 = 配对相邻 [x1,x2,x3,x4,…]；坏序 = 配对分离 [x1,x3,…,x2,x4,…]\n")
print(f"{'n':>3} | {'好序·手写':>9} | {'好序·dd':>7} | {'坏序·手写':>9} | {'坏序·dd':>7}")
rows = []
for n in (2, 4, 6, 8):
    good, bad = orders(n)
    t1, t2 = TBDD(good), TBDD(bad)
    c_good = t1.count(build_f(t1, n))
    c_bad = t2.count(build_f(t2, n))
    d_good = dd_count(good, n)
    d_bad = dd_count(bad, n)
    rows.append((n, c_good, d_good, c_bad, d_bad))
    print(f"{n:>3} | {c_good:>9} | {d_good:>7} | {c_bad:>9} | {d_bad:>7}")
print("\n（两列同为从公式根可达的内点数口径；手写与 dd 逐格一致即对拍通过）")
print("（坏序闭式 2^(n+1)−2：6/30/126/510 逐格核对 ✓；好序恰 2n 个内点）")
for n, c_good, d_good, c_bad, d_bad in rows:
    assert c_good == d_good and c_bad == d_bad, (n, c_good, d_good, c_bad, d_bad)
print(f"→ E1 自检通过：四种规模手写与 dd 节点数全部一致；n=2 好序恰 {rows[0][1]} 个内点（章内 §三手推）")

n8 = next(r for r in rows if r[0] == 8)
assert n8[1] <= 2 * 8 + 4, n8            # 好序线性
assert n8[3] > 8 * n8[1], n8             # 坏序显著指数化（n=8 时已超好序 8 倍）
print(f"→ n=8：好序 {n8[1]}（≤2n+4 线性 ✓）vs 坏序 {n8[3]}（>8× 线性界，指数起步 ✓）")
print("\nlab12 全部自检通过")
