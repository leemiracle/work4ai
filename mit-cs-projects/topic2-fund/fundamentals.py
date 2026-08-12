"""
6.101 Fundamentals of Programming（MIT）
================================================
覆盖主题：
- S-expr 解析器（reader/lexer/parser）（Lecture 3-4）
- eval/apply 求值器（Lecture 5-6）
- 闭包与词法作用域（Lecture 7）
- 尾调用优化 demo（Lecture 8）

核心教材/论文：
- Abelson & Sussman, "Structure and Interpretation of Computer Programs" (SICP) MIT Press 1996, Ch 4 Metacircular Evaluator
- Sussman & Steele 1975 "Scheme: An Interpreter for Extended Lambda Calculus" AI Memo 349, MIT
- Steele 1977 "Debunking the 'Expensive Procedure Call' Myth" MIT AI Memo 443 (tail calls)

本文件实现：
- 完整 mini-Lisp 解释器（tokenize → parse → eval）
- 支持：算术、lambda 闭包、let 绑定、if 条件、递归、quote
- 词法作用域环境链
- 尾调用优化（TCO）检测 demo
- 反直觉发现：Y-combinator 在不支持递归的语言里实现递归

运行：
    python fundamentals.py
"""
from __future__ import annotations
import math
from typing import Any


# ============ 1. Tokenizer + Parser (reader) ============

def tokenize(source: str) -> list[str]:
    """把源码切成 token。'(...) 内整体作为一个字符串 token。"""
    tokens = []
    i = 0
    while i < len(source):
        c = source[i]
        if c in ' \t\n\r':
            i += 1
        elif c == ';':  # 注释
            while i < len(source) and source[i] != '\n':
                i += 1
        elif c == '(' or c == ')':
            tokens.append(c); i += 1
        elif c == "'":  # quote 简写
            tokens.append("'"); i += 1
        else:
            j = i
            while j < len(source) and source[j] not in ' \t\n\r()\';':
                j += 1
            tokens.append(source[i:j])
            i = j
    return tokens


def parse(tokens: list[str]) -> list[Any]:
    """解析 token 流为 AST（嵌套 list）。支持多个顶层表达式。"""
    exprs = []
    pos = 0
    while pos < len(tokens):
        expr, pos = _parse_one(tokens, pos)
        exprs.append(expr)
    return exprs


def _parse_one(tokens: list[str], pos: int) -> tuple[Any, int]:
    tok = tokens[pos]
    if tok == '(':
        lst = []
        pos += 1
        while tokens[pos] != ')':
            item, pos = _parse_one(tokens, pos)
            lst.append(item)
        return lst, pos + 1
    if tok == "'":
        item, pos = _parse_one(tokens, pos + 1)
        return ['quote', item], pos
    if tok == ')':
        raise SyntaxError("意外的 ')'")
    return _atom(tok), pos + 1


def _atom(tok: str) -> Any:
    try:
        return int(tok)
    except ValueError:
        pass
    try:
        return float(tok)
    except ValueError:
        pass
    if tok == '#t':
        return True
    if tok == '#f':
        return False
    return tok  # symbol


# ============ 2. Environment + Evaluator ============

class Env:
    """词法作用域环境链"""
    def __init__(self, params=(), args=(), parent=None):
        self.vars = dict(zip(params, args))
        self.parent = parent

    def lookup(self, sym: str) -> Any:
        env = self
        while env is not None:
            if sym in env.vars:
                return env.vars[sym]
            env = env.parent
        raise NameError(f"未绑定变量: {sym}")

    def set(self, sym: str, val: Any):
        self.vars[sym] = val


class Closure:
    """lambda 闭包"""
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env


def make_global_env() -> Env:
    env = Env()
    env.vars.update({
        '+': lambda *a: sum(a),
        '-': lambda *a: a[0] - sum(a[1:]) if a else 0,
        '*': lambda *a: math.prod(a) if a else 1,
        '/': lambda *a: a[0] if len(a) == 1 else a[0] // a[1] if all(isinstance(x, int) for x in a) else a[0] / a[1],
        '=': lambda a, b: a == b,
        '<': lambda a, b: a < b,
        '>': lambda a, b: a > b,
        '<=': lambda a, b: a <= b,
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda a, b: [a] + (b if isinstance(b, list) else [b]),
        'null?': lambda x: x == [] or x is None,
        'list': lambda *a: list(a),
        'display': lambda x: print(x) or x,
        'not': lambda x: not x,
    })
    return env


def lisp_eval(expr: Any, env: Env) -> Any:
    """求值器（eval）"""
    # 自求值
    if isinstance(expr, (int, float, bool)):
        return expr
    # 变量引用
    if isinstance(expr, str):
        return env.lookup(expr)
    if not isinstance(expr, list) or not expr:
        return expr

    head = expr[0]
    # special forms
    if head == 'quote':
        return expr[1]
    if head == 'if':
        _, cond, then, *els = expr
        if lisp_eval(cond, env):
            return lisp_eval(then, env)
        return lisp_eval(els[0], env) if els else None
    if head == 'define':
        name, val = expr[1], expr[2]
        env.set(name, lisp_eval(val, env))
        return name
    if head == 'lambda':
        params, body = expr[1], expr[2]
        return Closure(params, body, env)
    if head == 'let':
        bindings = expr[1]
        new_env = Env(parent=env)
        for name, val in bindings:
            new_env.set(name, lisp_eval(val, env))
        return lisp_eval(expr[2], new_env)
    # function application (apply)
    fn = lisp_eval(head, env)
    args = [lisp_eval(a, env) for a in expr[1:]]
    return lisp_apply(fn, args, env)


def lisp_apply(fn: Any, args: list, env: Env) -> Any:
    if isinstance(fn, Closure):
        new_env = Env(fn.params, args, fn.env)
        return lisp_eval(fn.body, new_env)
    if callable(fn):
        return fn(*args)
    raise TypeError(f"不可调用: {fn}")


def run_lisp(source: str, env: Env = None) -> list:
    """运行一段 mini-Lisp 源码，返回所有顶层表达式结果"""
    if env is None:
        env = make_global_env()
    tokens = tokenize(source)
    exprs = parse(tokens)
    results = []
    for e in exprs:
        results.append(lisp_eval(e, env))
    return results


# ============ 3. 尾调用检测 ============

def is_tail_call(body: Any) -> tuple[bool, str]:
    """检测 body 是否是尾调用形式（简化：body 本身是函数调用）"""
    if isinstance(body, list) and body and isinstance(body[0], str):
        if body[0] not in ('if', 'let', 'lambda', 'define', 'quote'):
            return True, body[0]
    return False, ""


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.101 Fundamentals: mini-Lisp 解释器")
    print("=" * 65)

    env = make_global_env()

    # --- 基本算术 ---
    print("\n📋 1. 基本算术与解析")
    tests = [
        "(+ 1 2 3)",
        "(* (+ 2 3) (- 10 4))",
        "'(1 2 3)",
        "(car '(a b c))",
        "(cdr '(a b c))",
        "(cons 1 '(2 3))",
    ]
    for src in tests:
        tokens = tokenize(src)
        ast = parse(tokens)[0]
        val = lisp_eval(ast, env)
        print(f"  {src:<25} → tokens={tokens}")
        print(f"  {'':25}   AST={ast}")
        print(f"  {'':25}   = {val}")

    # --- 闭包与词法作用域 ---
    print("\n📋 2. 闭包与词法作用域")
    run_lisp("(define adder (lambda (x) (lambda (y) (+ x y))))", env)
    run_lisp("(define add5 (adder 5))", env)
    r = run_lisp("(add5 10)", env)[0]
    print(f"  (define adder (lambda (x) (lambda (y) (+ x y))))")
    print(f"  (define add5 (adder 5))   ; add5 捕获了 x=5 的环境")
    print(f"  (add5 10) = {r}")

    # --- 递归 ---
    print("\n📋 3. 递归（factorial / fibonacci）")
    run_lisp("""
        (define fact
          (lambda (n)
            (if (= n 0) 1 (* n (fact (- n 1))))))
    """, env)
    run_lisp("""
        (define fib
          (lambda (n)
            (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2))))))
    """, env)
    fact5 = run_lisp("(fact 5)", env)[0]
    fib10 = run_lisp("(fib 10)", env)[0]
    print(f"  (fact 5) = {fact5}")
    print(f"  (fib 10) = {fib10}")

    # --- 尾递归 vs 普通递归 ---
    print("\n📋 4. 尾递归形式")
    run_lisp("""
        (define fact-tail
          (lambda (n acc)
            (if (= n 0) acc (fact-tail (- n 1) (* acc n)))))
    """, env)
    fact_tail = run_lisp("(fact-tail 5 1)", env)[0]
    print(f"  (fact-tail 5 1) = {fact_tail}  ; 累加器模式，尾递归")
    body = parse(tokenize("(fact-tail (- n 1) (* acc n))"))[0]
    tc, name = is_tail_call(body)
    print(f"  尾调用检测: is_tail={tc}, callee={name}")

    # --- let 绑定 ---
    print("\n📋 5. let 局部绑定")
    r = run_lisp("(let ((x 3) (y 4)) (+ (* x x) (* y y)))", env)[0]
    print(f"  (let ((x 3) (y 4)) (+ (* x x) (* y y))) = {r}")

    # --- 反直觉发现：Y-combinator ---
    print("\n" + "=" * 65)
    print("💡 反直觉发现：Y-combinator——无 define 也能递归")
    print("=" * 65)
    print("在没有 'define' 的纯 lambda 演算中，仍可实现递归。")
    print("Y = λf.(λx.f(x x))(λx.f(x x))  把 'self-reference' 编码进函数本身。")
    print()
    # 用 Python 层模拟 Y-combinator（避免 lisp 求值器无限展开）
    Y = lambda f: (lambda x: f(lambda *a: x(x)(*a)))(lambda x: f(lambda *a: x(x)(*a)))
    fact_func = Y(lambda self: lambda n: 1 if n == 0 else n * self(n - 1))
    fib_func = Y(lambda self: lambda n: n if n < 2 else self(n-1) + self(n-2))
    print(f"  Y-combinator factorial(5) = {fact_func(5)}")
    print(f"  Y-combinator fib(10)      = {fib_func(10)}")
    print("  → 自引用是计算的基本性质，不需要语言内置 '递归' 关键字。")
    print("  → 这就是为什么函数式编程把一切归结为 lambda。")

    print("\n✅ 6.101 Demo 完成！")


if __name__ == "__main__":
    demo()
