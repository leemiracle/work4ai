"""
Einführung in die Programmierung (EPROG) — ETH Zürich
=====================================================
覆盖主题：
- 基础数据结构（链表 / 栈 / 队列 / 动态数组）
- 排序算法对比与排序网络（比较器网络）
- 函数式编程基础（OCaml / Scala 风格 in Python）：curry、代数数据类型 pattern matching、不可变

核心教材：
- "Structure and Interpretation of Computer Programs" Abelson & Sussman 1996 (MIT Press)
- Okasaki "Purely Functional Data Structures" 1999 (Cambridge University Press)
- "Introduction to Algorithms" Cormen Leiserson Rivest Stein 3rd ed. (CLRS)

本文件实现：
1. 比较器排序网络（Batcher 奇偶归并网络）+ 正确性零一原理验证
2. 不可变链表 + 栈/队列（Okasaki 风格）
3. FP curry / 模式匹配 + foldr 建表
4. 主 demo：排序网络 vs 顺序排序——反直觉：网络深度 = 并行轮次

运行：
    python intro.py
"""
from __future__ import annotations
import random
from functools import reduce


# ============ 1. 排序网络（Batcher 奇偶归并） ============

def comparator(a: int, b: int) -> tuple[int, int]:
    """比较器：小→a，大→b"""
    return (a, b) if a <= b else (b, a)


def batcher_odd_even_merge_network(n: int) -> list[tuple[int, int]]:
    """
    返回 Batcher 奇偶归并网络的比较器序列 (i, j)。
    对长度 n 的序列排序，网络深度 O((log n)^2)。
    """
    comps: list[tuple[int, int]] = []

    def merge(lo: int, n: int, r: int):
        step = r * 2
        if step < n:
            merge(lo, n, step)
            merge(lo + r, n, step)
            for i in range(lo + r, lo + n - r, step):
                comps.append((i, i + r))
        else:
            comps.append((lo, lo + r))

    def sort(lo: int, n: int):
        if n > 1:
            m = n // 2
            sort(lo, m)
            sort(lo + m, m)
            merge(lo, n, 1)

    sort(0, n)
    return comps


def apply_network(arr: list[int], comps: list[tuple[int, int]]) -> list[int]:
    """在网络中依次应用比较器"""
    a = list(arr)
    for i, j in comps:
        a[i], a[j] = comparator(a[i], a[j])
    return a


def network_depth(n: int, comps: list[tuple[int, int]]) -> int:
    """
    计算网络深度（并行轮次）：
    每个位置构成依赖图，深度 = 最长路径。
    """
    layer = [0] * n
    for i, j in comps:
        l = max(layer[i], layer[j]) + 1
        layer[i] = l
        layer[j] = l
    return max(layer) if layer else 0


def verify_zero_one_principle(n: int, comps: list[tuple[int, int]]) -> bool:
    """
    零一原理：一个比较器网络是排序网络 ⟺ 它能正确排序所有 0/1 序列。
    验证全部 2^n 个 0/1 输入。
    """
    for mask in range(1 << n):
        arr = [(mask >> k) & 1 for k in range(n)]
        out = apply_network(arr, comps)
        if out != sorted(arr):
            return False
    return True


# ============ 2. 不可变数据结构（Okasaki 风格） ============

class ImmutableList:
    """
    不可变单链表（Cons list），函数式风格。
    所有操作返回新列表，不修改原列表。
    """
    __slots__ = ('head', 'tail', '_len')
    _empty_sentinel = object()

    def __init__(self, head=_empty_sentinel, tail=None):
        self.head = head
        self.tail = tail
        self._len = 0 if self.is_empty() else 1 + (tail._len if tail else 0)

    def is_empty(self) -> bool:
        return self.head is ImmutableList._empty_sentinel

    def cons(self, x) -> 'ImmutableList':
        return ImmutableList(x, self)

    def __len__(self):
        return self._len

    def to_list(self) -> list:
        result = []
        node = self
        while not node.is_empty():
            result.append(node.head)
            node = node.tail
        return result

    @staticmethod
    def from_list(lst: list) -> 'ImmutableList':
        """foldr 建表"""
        empty = ImmutableList()
        return reduce(lambda acc, x: acc.cons(x), reversed(lst), empty)

    def map(self, f) -> 'ImmutableList':
        """递归 map（不修改 self）"""
        if self.is_empty():
            return self
        return ImmutableList(f(self.head), self.tail.map(f))

    def filter(self, pred) -> 'ImmutableList':
        if self.is_empty():
            return self
        if pred(self.head):
            return ImmutableList(self.head, self.tail.filter(pred))
        return self.tail.filter(pred)

    def foldr(self, f, init):
        if self.is_empty():
            return init
        return f(self.head, self.tail.foldr(f, init))


class Stack:
    """不可变栈（基于 ImmutableList）"""
    def __init__(self):
        self._list = ImmutableList()

    def push(self, x) -> 'Stack':
        s = Stack()
        s._list = self._list.cons(x)
        return s

    def pop(self) -> tuple | None:
        if self._list.is_empty():
            return None
        return (self._list.head, self._list.tail)


# ============ 3. 函数式编程：curry / 模式匹配 ============

def curry(f):
    """将 f(a, b, c) 变成 f(a)(b)(c)"""
    def _curry(*args):
        if len(args) >= f.__code__.co_argcount:
            return f(*args)
        return lambda *more: _curry(*(args + more))
    return _curry


def foldl(f, init, lst):
    """尾递归左折叠"""
    acc = init
    for x in lst:
        acc = f(acc, x)
    return acc


# 代数数据类型：Option / Either（pattern matching 风格）
class Option:
    """ADT: Some(x) | None"""
    pass


class Some(Option):
    def __init__(self, val): self.val = val
    def __repr__(self): return f"Some({self.val})"


class Nothing(Option):
    def __repr__(self): return "Nothing"


def match_option(opt: Option, on_some, on_nothing):
    """模式匹配"""
    if isinstance(opt, Some):
        return on_some(opt.val)
    return on_nothing()


# ============ Demo ============

def demo():
    print("=" * 60)
    print("EPROG: 排序网络 + 不可变数据结构 + FP")
    print("=" * 60)
    random.seed(42)

    # 1. 排序网络
    print("\n📋 1. Batcher 奇偶归并排序网络")
    for n in [4, 8, 16]:
        comps = batcher_odd_even_merge_network(n)
        ok = verify_zero_one_principle(n, comps)
        depth = network_depth(n, comps)
        print(f"   n={n:2d}: {len(comps):2d} 个比较器, 深度={depth} (并行轮次), "
              f"零一原理={'✓' if ok else '✗'}")

    # 随机测试 n=8
    n = 8
    comps = batcher_odd_even_merge_network(n)
    test_arr = [random.randint(0, 99) for _ in range(n)]
    sorted_arr = apply_network(test_arr, comps)
    print(f"   测试: {test_arr} → {sorted_arr}  (正确: {sorted_arr == sorted(test_arr)})")

    # 2. 不可变链表
    print("\n📋 2. 不可变链表（Okasaki 风格）")
    lst = ImmutableList.from_list([3, 1, 4, 1, 5, 9, 2, 6])
    print(f"   原表: {lst.to_list()}, len={len(lst)}")
    mapped = lst.map(lambda x: x * x)
    filtered = lst.filter(lambda x: x > 3)
    print(f"   map(x²): {mapped.to_list()}    (原表不变: {lst.to_list()})")
    print(f"   filter(>3): {filtered.to_list()}")
    total = lst.foldr(lambda x, acc: x + acc, 0)
    print(f"   foldr(+, 0): {total}")

    # 3. 栈
    print("\n📋 3. 不可变栈")
    s = Stack()
    s = s.push(10).push(20).push(30)  # chain
    result = s.pop()
    print(f"   push 10→20→30 后 pop: {result[0] if result else None}")

    # 4. Curry + 模式匹配
    print("\n📋 4. 函数式：curry + Option 模式匹配")
    add3 = curry(lambda a, b, c: a + b + c)
    print(f"   curry(add)(1)(2)(3) = {add3(1)(2)(3)}")

    opt_safe_div = Some(10 / 2) if 2 != 0 else Nothing()
    msg = match_option(opt_safe_div, lambda v: f"结果是 {v}", lambda: "除零")
    print(f"   safe_div(10, 2): {msg}")
    opt_div0 = Nothing()
    msg0 = match_option(opt_div0, lambda v: f"结果是 {v}", lambda: "除零")
    print(f"   safe_div(10, 0): {msg0}")

    # 反直觉发现
    print("\n💡 反直觉发现：排序网络的并行性")
    n = 16
    comps = batcher_odd_even_merge_network(n)
    depth = network_depth(n, comps)
    seq_comparisons = n * (n - 1) // 2  # 冒泡排序
    print(f"   串行冒泡: {seq_comparisons} 轮比较")
    print(f"   Batcher网络: {len(comps)} 个比较器, 但只需 {depth} 个并行轮次")
    print(f"   → 并行加速比 = {seq_comparisons}/{depth} = {seq_comparisons/depth:.1f}x")
    print(f"   网络深度增长 O((log n)²) ≈ {depth}，远慢于比较数 O(n·(logn)²)")
    print("   这就是 GPU/硬件排序的基础：固定结构 + 完全并行。")

    print("\n✅ EPROG 完成！")


if __name__ == "__main__":
    demo()
