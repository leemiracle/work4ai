"""
Programming Paradigms — ETH Zürich
==================================
覆盖主题：
- 函数式（curry / monad / 尾调用）
- 逻辑式（mini-Prolog 合一 + 回溯）
- 并发（CSP 通信顺序进程）
- 惰性求值（streams / thunks）

核心教材/论文：
- Pierce "Types and Programming Languages" (MIT Press, 2002)
- Hoare "Communicating Sequential Processes" CACM 21(8): 666-677 (1978) — CSP
- Hudak "Conception, Evolution, and Application of Functional Programming Languages" ACM Computing Surveys 21(3): 359-411 (1989)
- Warren "Programming in Prolog" (Springer, classic)

本文件实现：
1. Maybe/List monad + curry
2. Mini-Prolog（合一 + 深度优先回溯 SLD）
3. CSP 进程代数（通道通信模拟）
4. 惰性流（Haskell 风格无限序列）

运行：
    python paradigms.py
"""
from __future__ import annotations
import random
from collections import deque


# ============ 1. 函数式：Monad + Curry ============

class Maybe:
    """Maybe monad: Just(x) | Nothing"""
    def __init__(self, val=None, is_just=False):
        self.val = val
        self.is_just = is_just

    @staticmethod
    def just(x):
        return Maybe(x, True)

    @staticmethod
    def nothing():
        return Maybe(None, False)

    def bind(self, f):  # >>= operator
        if not self.is_just:
            return Maybe.nothing()
        return f(self.val)

    def __repr__(self):
        return f"Just({self.val})" if self.is_just else "Nothing"


def curry(f):
    """柯里化：f(a,b,c) → f(a)(b)(c)"""
    arity = f.__code__.co_argcount
    def _curried(*args):
        if len(args) >= arity:
            return f(*args)
        return lambda *more: _curried(*(args + more))
    return _curried


def safe_div(x, y):
    """用 Maybe monad 处理除零"""
    if y == 0:
        return Maybe.nothing()
    return Maybe.just(x / y)


# monad 链式
def monad_pipeline():
    # Just(10) >>= (λx → Just(x/2)) >>= (λy → Just(y+1))
    result = (Maybe.just(10)
              .bind(lambda x: safe_div(x, 2))
              .bind(lambda y: Maybe.just(y + 1)))
    return result


# ============ 2. 逻辑式：Mini-Prolog ============

class Term:
    """项：常量 / 变量 / 复合项"""
    pass


class Var(Term):
    def __init__(self, name): self.name = name
    def __repr__(self): return f"?{self.name}"


class Atom(Term):
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
    def __eq__(self, o): return isinstance(o, Atom) and self.name == o.name
    def __hash__(self): return hash(self.name)


class Struct(Term):
    """复合项: functor(arg1, arg2, ...)"""
    def __init__(self, functor, args):
        self.functor = functor
        self.args = args
    def __repr__(self):
        return f"{self.functor}({', '.join(repr(a) for a in self.args)})"


def unify(t1: Term, t2: Term, subst: dict) -> dict | None:
    """合一算法（Robinson 1965）"""
    if subst is None:
        return None
    t1 = walk(t1, subst)
    t2 = walk(t2, subst)

    if isinstance(t1, Var) and isinstance(t2, Var) and t1.name == t2.name:
        return subst
    if isinstance(t1, Var):
        subst[t1.name] = t2
        return subst
    if isinstance(t2, Var):
        subst[t2.name] = t1
        return subst
    if isinstance(t1, Atom) and isinstance(t2, Atom):
        return subst if t1 == t2 else None
    if isinstance(t1, Struct) and isinstance(t2, Struct):
        if t1.functor != t2.functor or len(t1.args) != len(t2.args):
            return None
        for a, b in zip(t1.args, t2.args):
            subst = unify(a, b, subst)
            if subst is None:
                return None
        return subst
    return None


def walk(t: Term, subst: dict) -> Term:
    """查找变量的绑定"""
    while isinstance(t, Var) and t.name in subst:
        t = subst[t.name]
    return t


def resolve_term(t: Term, subst: dict) -> Term:
    """用绑定替换变量"""
    t = walk(t, subst)
    if isinstance(t, Struct):
        return Struct(t.functor, [resolve_term(a, subst) for a in t.args])
    return t


class MiniProlog:
    """Mini Prolog 引擎（SLD 归结）"""

    def __init__(self):
        self.rules: list[tuple[Struct, list[Struct]]] = []  # (head, body)

    def add_fact(self, fact: Struct):
        self.rules.append((fact, []))

    def add_rule(self, head: Struct, body: list[Struct]):
        self.rules.append((head, body))

    def query(self, goal: Struct) -> list[dict]:
        """深度优先 SLD 归结"""
        solutions = []
        self._prove([goal], {}, solutions, 0)
        return solutions

    def _prove(self, goals: list[Struct], subst: dict, solutions: list, depth: int):
        if depth > 100:
            return  # 防无限
        if not goals:
            solutions.append(dict(subst))
            return
        goal = goals[0]
        rest = goals[1:]
        for head, body in self.rules:
            new_subst = dict(subst)
            renamed_head = self._rename(head)
            if unify(goal, renamed_head, new_subst) is not None:
                renamed_body = [self._rename(b) for b in body]
                renamed_rest = [self._rename(g) for g in rest]
                self._prove(renamed_body + renamed_rest, new_subst, solutions, depth + 1)

    _counter = 0

    def _rename(self, term: Term) -> Term:
        MiniProlog._counter += 1
        suffix = str(MiniProlog._counter)
        def _r(t):
            if isinstance(t, Var):
                return Var(t.name + suffix)
            if isinstance(t, Struct):
                return Struct(t.functor, [_r(a) for a in t.args])
            return t
        return _r(term)


# ============ 3. 并发：CSP ============

class CSPChannel:
    """同步通道（ rendezvous）"""

    def __init__(self, name):
        self.name = name
        self.buffer = deque()
        self.waiting_recv = deque()

    def send(self, val):
        """阻塞发送（模拟）"""
        self.buffer.append(val)

    def recv(self):
        if self.buffer:
            return self.buffer.popleft()
        return None


def csp_producer_consumer():
    """
    CSP 示例：生产者-消费者
    P = send(ch, 1) → send(ch, 2) → STOP
    C = recv(ch) → recv(ch) → STOP
    """
    ch = CSPChannel("data")
    # 模拟交错执行
    producer_log = []
    consumer_log = []

    # Producer
    for i in range(1, 6):
        ch.send(i)
        producer_log.append(f"send({i})")

    # Consumer
    while True:
        val = ch.recv()
        if val is None:
            break
        consumer_log.append(f"recv({val})")

    return producer_log, consumer_log


def csp_dining_philosophers():
    """简化的哲学家就餐（避免死锁的方案：资源排序）"""
    n = 3
    forks = [CSPChannel(f"fork{i}") for i in range(n)]
    # 初始化叉子可用
    for f in forks:
        f.send(True)

    eaten = 0
    # 每个哲学家先拿编号小的叉子（避免死锁）
    for i in range(n):
        f1 = forks[i]
        f2 = forks[(i + 1) % n]
        # 按编号排序获取
        lo, hi = (f1, f2) if i < (i + 1) % n else (f2, f1)
        lo.recv()  # 拿左叉
        hi.recv()  # 拿右叉
        eaten += 1
        hi.send(True)  # 放回右
        lo.send(True)  # 放回左
    return eaten


# ============ 4. 惰性求值 ============

class LazyStream:
    """
    惰性流（Haskell 风格）
    head 是已求值的值，tail 是 thunk（延迟计算）
    """

    def __init__(self, head, tail_fn=None):
        self.head = head
        self._tail_fn = tail_fn
        self._tail = None

    @property
    def tail(self):
        if self._tail is None and self._tail_fn:
            self._tail = self._tail_fn()
        return self._tail

    def take(self, n: int) -> list:
        result = []
        node = self
        while node and len(result) < n:
            result.append(node.head)
            node = node.tail
        return result


def naturals_from(n: int) -> LazyStream:
    """无限自然数流"""
    return LazyStream(n, lambda: naturals_from(n + 1))


def fib_stream() -> LazyStream:
    """斐波那契流"""
    def _fib(a, b):
        return LazyStream(a, lambda: _fib(b, a + b))
    return _fib(0, 1)


def sieve(stream: LazyStream) -> LazyStream:
    """埃拉托色尼筛（惰性素数流）"""
    p = stream.head
    rest = stream.tail
    # 过滤掉 p 的倍数
    def _filtered():
        node = rest
        def _filter(s, f):
            if s is None:
                return None
            if s.head % f == 0:
                return _filter(s.tail, f)
            return LazyStream(s.head, lambda: _filter(s.tail, f))
        filtered = _filter(rest, p)
        if filtered is None:
            return LazyStream(p)
        return sieve(filtered)
    return LazyStream(p, _filtered)


# ============ Demo ============

def demo():
    print("=" * 60)
    print("Programming Paradigms: FP + LP + CSP + Lazy")
    print("=" * 60)

    # 1. FP / Monad
    print("\n📋 1. 函数式：Maybe Monad + Curry")
    result = monad_pipeline()
    print(f"   Just(10) >>= div(2) >>= +1 = {result}")
    bad = Maybe.just(10).bind(lambda x: safe_div(x, 0))
    print(f"   Just(10) >>= div(0) = {bad} (除零优雅处理)")

    add3 = curry(lambda a, b, c: a + b + c)
    print(f"   curry(add)(1)(2)(3) = {add3(1)(2)(3)}")

    # 2. Mini-Prolog
    print("\n📋 2. Mini-Prolog (SLD 归结)")
    engine = MiniProlog()
    # 事实
    engine.add_fact(Struct("parent", [Atom("alice"), Atom("bob")]))
    engine.add_fact(Struct("parent", [Atom("bob"), Atom("carol")]))
    engine.add_fact(Struct("parent", [Atom("bob"), Atom("dave")]))
    # 规则: grandparent(X, Z) :- parent(X, Y), parent(Y, Z)
    engine.add_rule(
        Struct("grandparent", [Var("X"), Var("Z")]),
        [Struct("parent", [Var("X"), Var("Y")]),
         Struct("parent", [Var("Y"), Var("Z")])]
    )
    # 查询: grandparent(X, carol)
    solutions = engine.query(Struct("grandparent", [Var("X"), Atom("carol")]))
    for sol in solutions:
        gp = resolve_term(Var("X"), sol)
        print(f"   grandparent(?X, carol) → X = {gp}")

    # 3. CSP
    print("\n📋 3. CSP: 生产者-消费者 + 哲学家")
    plog, clog = csp_producer_consumer()
    print(f"   Producer: {plog}")
    print(f"   Consumer: {clog}")
    eaten = csp_dining_philosophers()
    print(f"   3 个哲学家（资源排序避免死锁）全部就餐: {eaten}/3")

    # 4. 惰性求值
    print("\n📋 4. 惰性流（无限序列）")
    naturals = naturals_from(1)
    print(f"   naturals.take(5) = {naturals.take(5)}")
    fibs = fib_stream()
    print(f"   fib.take(10) = {fibs.take(10)}")
    primes = sieve(naturals_from(2))
    print(f"   primes(惰性埃氏筛).take(10) = {primes.take(10)}")

    # 反直觉
    print("\n💡 反直觉发现：惰性素数筛 vs 严格筛")
    print(f"   埃氏筛的惰性版: primes = sieve([2..])")
    print(f"   take(10) 只算前 10 个素数需要的部分，不计算无穷列表！")
    print(f"   这是 Haskell 一行代码生成素数的核心魔力。")

    print("\n✅ Programming Paradigms 完成！")


if __name__ == "__main__":
    demo()
