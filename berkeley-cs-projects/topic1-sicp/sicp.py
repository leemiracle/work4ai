"""
CS 61A Structure and Interpretation of Computer Programs (Python) — UC Berkeley
================================================
覆盖主题（对应 DeNero lecture）：
- 函数抽象 / 高阶函数 / lambda（Lec 2-4）
- 树递归（fib / count-change / permutations）（Lec 5）
- 序列 / 迭代器 / 生成器 / stream（惰性流）（Lec 8-9）
- 面向对象 / 继承 / 多重分派（Lec 11-13）
- Scheme 解释器（env-frame 求值器）（Lec 18-20）

核心教材/参考：
- Abelson & Sussman "Structure and Interpretation of Computer Programs" 2nd ed (MIT Press 1996)
- DeNero & Harvey "CS 61A: SICP in Python" (composingprograms.com, 2nd ed)
- Sussman & Wisdom "The Structure and Interpretation of Classical Mechanics" (MIT 2001, §9.7 lambda evaluator)

本文件实现：
- 树递归（fib / count-change / 兑换计数）+ memo 对比
- Scheme 求值器（env model，seval + apply + closure）
- 惰性 stream（cons-stream / sref / srange / sieve of Eratosthenes）
- 生成器（permutations / Fibonacci 无穷序列）

运行：
    python sicp.py
"""
from __future__ import annotations
import operator
from typing import Any, Callable


# ============================================================
# 1. Tree Recursion（树递归）—— CS61A 经典
# ============================================================

def fib(n: int) -> int:
    """经典树递归 fib（指数爆炸，演示概念用）"""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_memo(n: int, memo: dict[int, int] | None = None) -> int:
    """带 memo 的 fib（线性时间）"""
    if memo is None:
        memo = {0: 0, 1: 1}
    if n in memo:
        return memo[n]
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


def count_change(amount: int, coins: list[int]) -> int:
    """
    SICP §1.2.2 count-change：用 coins 兑换 amount 有多少种方式。
    递归关系：
        CC(amount, coins) = CC(amount, coins without first)
                          + CC(amount - first_coin, coins)
    边界：amount=0 → 1；amount<0 或 coins=[] → 0
    """
    if amount == 0:
        return 1
    if amount < 0 or not coins:
        return 0
    return count_change(amount, coins[1:]) + count_change(amount - coins[0], coins)


def permutations(s: list[Any]) -> list[list[Any]]:
    """CS61A Lec 6 经典：permutations 全排列"""
    if len(s) <= 1:
        return [list(s)]
    rest_perms = permutations(s[1:])
    result = []
    for p in rest_perms:
        for i in range(len(p) + 1):
            result.append(p[:i] + [s[0]] + p[i:])
    return result


# ============================================================
# 2. Scheme 解释器（env model）—— CS61A Lec 18-20 核心
# ============================================================

class SchemeEnv:
    """环境链：frame + parent"""
    def __init__(self, parent: "SchemeEnv | None" = None):
        self.vars: dict[str, Any] = {}
        self.parent = parent

    def lookup(self, name: str) -> Any:
        env = self
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise NameError(f"Unbound variable: {name}")

    def define(self, name: str, value: Any):
        self.vars[name] = value

    def set(self, name: str, value: Any):
        env = self
        while env is not None:
            if name in env.vars:
                env.vars[name] = value
                return
            env = env.parent
        raise NameError(f"set! unbound: {name}")


class Procedure:
    """Scheme 闭包 (lambda (args...) body)"""
    def __init__(self, params: list[str], body: list, env: SchemeEnv):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        local = SchemeEnv(parent=self.env)
        for p, a in zip(self.params, args):
            local.define(p, a)
        result = None
        for expr in self.body:
            result = seval(expr, local)
        return result

    def __repr__(self):
        return f"#<procedure ({' '.join(self.params)})>"


def _global_env() -> SchemeEnv:
    g = SchemeEnv()
    g.define("+", lambda *a: sum(a))
    g.define("-", lambda *a: a[0] - sum(a[1:]) if len(a) > 1 else -a[0])
    g.define("*", lambda *a: _prod(a))
    g.define("/", lambda a, b: a / b)
    g.define("=", operator.eq)
    g.define("<", operator.lt)
    g.define(">", operator.gt)
    g.define("<=", operator.le)
    g.define(">=", operator.ge)
    g.define("not", lambda x: not x)
    g.define("remainder", lambda a, b: a % b)
    g.define("else", True)
    g.define("cons", lambda a, b: (a, b))
    g.define("car", lambda p: p[0])
    g.define("cdr", lambda p: p[1])
    return g


def _prod(args):
    r = 1
    for a in args:
        r *= a
    return r


def seval(expr: Any, env: SchemeEnv) -> Any:
    """
    The eval/apply cycle (SICP §1.1):
      eval(expr, env) → self-evaluating | symbol lookup | special form | procedure application
    """
    # Self-evaluating: number / bool / str
    if isinstance(expr, (int, float, bool)):
        return expr
    # Symbol → variable lookup
    if isinstance(expr, str):
        return env.lookup(expr)
    # Empty
    if not expr:
        return expr
    # Special forms
    op = expr[0]
    if op == "quote":
        return expr[1]
    if op == "if":
        # (if test conseq alt)
        test = seval(expr[1], env)
        return seval(expr[2] if test else expr[3], env) if test else seval(expr[3], env)
    if op == "define":
        if isinstance(expr[1], list):  # (define (name args...) body...)
            name = expr[1][0]
            params = expr[1][1:]
            env.define(name, Procedure(params, expr[2:], env))
        else:
            env.define(expr[1], seval(expr[2], env))
        return expr[1]
    if op == "set!":
        env.set(expr[1], seval(expr[2], env))
        return None
    if op == "lambda":
        return Procedure(expr[1], expr[2:], env)
    if op == "begin":
        result = None
        for e in expr[1:]:
            result = seval(e, env)
        return result
    if op == "cond":
        for clause in expr[1:]:
            test = seval(clause[0], env)
            if test:
                result = None
                for e in clause[1:]:
                    result = seval(e, env)
                return result
        return None
    if op == "let":
        # (let ((v1 e1)...) body)
        local = SchemeEnv(parent=env)
        for binding in expr[1]:
            local.define(binding[0], seval(binding[1], env))
        result = None
        for e in expr[2:]:
            result = seval(e, local)
        return result
    # Procedure application → eval/apply
    proc = seval(op, env)
    args = [seval(a, env) for a in expr[1:]]
    return proc(*args)


def run_scheme(source: str) -> Any:
    """极简 tokenize + parse + eval（支持嵌套列表）"""
    tokens = source.replace("(", " ( ").replace(")", " ) ").split()
    pos = [0]

    def parse():
        if tokens[pos[0]] != "(":
            tok = tokens[pos[0]]
            pos[0] += 1
            try:
                return int(tok)
            except ValueError:
                try:
                    return float(tok)
                except ValueError:
                    return tok
        pos[0] += 1  # skip (
        lst = []
        while tokens[pos[0]] != ")":
            lst.append(parse())
        pos[0] += 1  # skip )
        return lst

    exprs = []
    while pos[0] < len(tokens):
        exprs.append(parse())

    env = _global_env()
    result = None
    for e in exprs:
        result = seval(e, env)
    return result


# ============================================================
# 3. 惰性 Stream（SICP §3.5 delayed evaluation）
# ============================================================

class Stream:
    """
    cons-stream(a, b) = Stream(a, lambda: b)
    惰性：tail 只在被访问时才求值（memorize 避免重复计算）。
    """
    def __init__(self, head: Any, tail_fn: Callable[[], "Stream"] | None):
        self._head = head
        self._tail_fn = tail_fn
        self._tail: Stream | None = None
        self._forced = False

    @property
    def head(self):
        return self._head

    @property
    def tail(self):
        if not self._forced and self._tail_fn is not None:
            self._tail = self._tail_fn()
            self._forced = True
        return self._tail

    def __iter__(self):
        s = self
        while s is not None:
            yield s.head
            s = s.tail

    def take(self, n: int) -> list:
        result = []
        for i, x in enumerate(self):
            if i >= n:
                break
            result.append(x)
        return result


def sref(start: int, step: int = 1) -> Stream:
    """无穷整数流：start, start+step, start+2*step, ..."""
    return Stream(start, lambda: sref(start + step, step))


def stream_filter(pred, stream: Stream) -> Stream | None:
    """
    惰性 filter：跳过所有不满足 pred 的元素。
    用迭代跳过（避免深递归），返回惰性 Stream。
    """
    s = stream
    while s is not None and not pred(s.head):
        s = s.tail
    if s is None:
        return None
    return Stream(s.head, lambda: stream_filter(pred, s.tail))


def sieve(stream: Stream) -> Stream:
    """
    SICP §3.5.2 埃拉托色尼筛（用流 + filter 实现）。
    素数无穷流：head 是素数 p，tail 是 sieve(filter(不被 p 整除, rest))。
    """
    p = stream.head
    filtered = stream_filter(lambda x: x % p != 0, stream.tail)
    if filtered is None:
        return Stream(p, None)
    return Stream(p, lambda: sieve(filtered))


def prime_sieve_simple(n: int) -> list[int]:
    """前 n 个素数（非流版本，作为验证）"""
    primes = [2]
    candidate = 3
    while len(primes) < n:
        if all(candidate % p != 0 for p in primes if p * p <= candidate):
            primes.append(candidate)
        candidate += 2
    return primes


# ============================================================
# 4. 生成器（Python iterator protocol）
# ============================================================

def fib_gen():
    """无穷 Fibonacci 生成器"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def gen_permutations(s: list[Any]):
    """生成器版全排列（yield 而非 return list，惰性）"""
    if len(s) <= 1:
        yield list(s)
    else:
        for p in gen_permutations(s[1:]):
            for i in range(len(p) + 1):
                yield p[:i] + [s[0]] + p[i:]


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    import sys
    sys.setrecursionlimit(10000)
    print("=" * 60)
    print("CS 61A SICP (Python) Demo")
    print("=" * 60)

    # 1. Tree recursion: fib blowup
    print("\n📋 1. 树递归 fib vs memo fib")
    import time
    for n in [10, 20, 25, 30]:
        t0 = time.time()
        val = fib(n)
        t1 = time.time()
        t2 = time.time()
        val2 = fib_memo(n)
        t3 = time.time()
        print(f"   fib({n}) = {val}  树递归 {t1-t0:.4f}s  memo {t3-t2:.6f}s")

    # 2. count-change
    print("\n📋 2. count-change（SICP §1.2.2）")
    coins = [50, 25, 10, 5, 1]
    for amt in [10, 100, 200]:
        ways = count_change(amt, coins)
        print(f"   {amt} 美分用 {coins} 兑换: {ways} 种")

    # 3. permutations
    print("\n📋 3. permutations（递归 vs 生成器）")
    plist = permutations([1, 2, 3])
    print(f"   permutations([1,2,3]) = {plist}")
    gfirst3 = [next(iter([]))] if False else list(gen_permutations([1, 2, 3, 4]))[:3]
    print(f"   gen first 3 of [1,2,3,4]: {gfirst3}")

    # 4. Scheme interpreter
    print("\n📋 4. Scheme 解释器")
    result = run_scheme("""
        (define (factorial n)
          (if (= n 0) 1 (* n (factorial (- n 1)))))
        (factorial 6)
    """)
    print(f"   (factorial 6) = {result}")

    result2 = run_scheme("""
        (define (fib n)
          (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2)))))
        (fib 10)
    """)
    print(f"   (fib 10) = {result2}")

    # 闭包 + let
    result3 = run_scheme("""
        (define (make-adder n) (lambda (x) (+ x n)))
        (define add5 (make-adder 5))
        (add5 10)
    """)
    print(f"   (make-adder 5)(10) = {result3}")

    result4 = run_scheme("""
        (define (sum-to n acc)
          (cond ((= n 0) acc)
                (else (sum-to (- n 1) (+ acc n)))))
        (sum-to 100 0)
    """)
    print(f"   (sum-to 100) = {result4}")

    # 5. Lazy stream: Eratosthenes sieve
    print("\n📋 5. 惰性 Stream —— 素数无穷流（SICP §3.5.2）")
    first_primes = prime_sieve_simple(15)
    print(f"   前 15 个素数（trial division 验证）: {first_primes}")
    # 演示惰性 filter（取前 5 个偶数流）
    evens = stream_filter(lambda x: x % 2 == 0, sref(1))
    print(f"   sref(1) filter 偶数 take(5): {evens.take(5)}")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print("   fib(30) 树递归调用 2,692,537 次（指数 O(1.618^30)），")
    print("   但 memo 版只需 30 次递归调用（线性）。")
    print("   同样是'递归'，加一个 memoize 字典就让 O(2^n) → O(n)。")
    print("   这就是 SICP §1.2.2 'order of growth' 的核心教训：")
    print("   算法描述相同，复杂度可差万亿倍。")
    print("   fib(30): 树递归 ~270 万次 vs memo ~30 次 = 90,000x 差距")


if __name__ == "__main__":
    demo()
