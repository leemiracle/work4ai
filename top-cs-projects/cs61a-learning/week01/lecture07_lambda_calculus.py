"""
CS 61A Day 4-5 合并 - Lecture 7-10: Lambda Calculus + Currying + Newton
========================================================================
Day 4-5 合并：你的 Python 已工程级，加速讲 SICP 真正的「思想飞跃」。

主题：
- Lambda 演算（Church numerals —— 计算的数学基础）
- 柯里化（Currying）—— 把多参数函数变成单参数链
- Y 组合子 —— 不用 def 实现递归（lambda 演算的奇迹）
- 牛顿法 —— 函数式数值计算（不动点迭代）

核心教材：
- SICP 1.3 "Formulating Abstractions with Higher-Order Procedures"
- SICP 1.1.7 "Example: Square Roots by Newton's Method"
- Church 1936 "An Unsolvable Problem of Elementary Number Theory"

本文件实现：
- Church numerals（用纯函数编码数字）
- 柯里化（add_curried(2)(3) = 5）
- Y 组合子（不用 def 实现 factorial）
- 牛顿法（用不动点迭代开方）
- 反直觉：函数本身可以做"数据"

运行：
    python3 lecture07_lambda_calculus.py
"""

from __future__ import annotations
from typing import Callable


# ============ 1. Church Numerals（用函数编码数字）============

def demo_church_numerals():
    """Alonzo Church 1936：数字 = 高阶函数"""
    print("📋 1. Church Numerals（用函数编码数字）")
    
    # Church 数字 n = 一个函数，接收 f 和 x，返回 f 应用 n 次
    # zero = lambda f: lambda x: x          # f 不应用
    # one  = lambda f: lambda x: f(x)       # f 应用 1 次
    # two  = lambda f: lambda x: f(f(x))    # f 应用 2 次
    # three = lambda f: lambda x: f(f(f(x)))
    
    zero = lambda f: lambda x: x
    one = lambda f: lambda x: f(x)
    two = lambda f: lambda x: f(f(x))
    three = lambda f: lambda x: f(f(f(x)))
    
    # 怎么"读"Church 数字？传入 lambda x: x+1 和 0
    def church_to_int(cn):
        return cn(lambda x: x + 1)(0)
    
    print(f"   zero = {church_to_int(zero)}")
    print(f"   one = {church_to_int(one)}")
    print(f"   two = {church_to_int(two)}")
    print(f"   three = {church_to_int(three)}")
    
    # 教堂加法：m + n = 把 f 应用 m+n 次
    # add(m, n) = lambda f: lambda x: m(f)(n(f)(x))
    def add_church(m, n):
        return lambda f: lambda x: m(f)(n(f)(x))
    
    five = add_church(two, three)
    print(f"\n   add_church(two, three) = {church_to_int(five)}")
    
    # 教堂乘法：m * n = 把 f 应用 m*n 次
    # mul(m, n) = lambda f: m(n(f))
    def mul_church(m, n):
        return lambda f: m(n(f))
    
    six = mul_church(two, three)
    print(f"   mul_church(two, three) = {church_to_int(six)}")
    
    # 教堂幂：m^n
    def pow_church(m, n):
        return n(m)  # m 自乘 n 次（Church 数字的幂定义极简）
    
    eight = pow_church(two, three)
    print(f"   pow_church(two, three) = {church_to_int(eight)}")
    
    print(f"\n   💡 反直觉：纯函数可以编码所有自然数！")
    print(f"      这是 lambda 演算的核心洞察：「函数 = 数据 = 计算」")
    print(f"      SICP 期末 Scheme 解释器就是把这套思想用到底——")
    print(f"      解释器本身就是一个 Church-style 的高阶函数")


# ============ 2. 柯里化（Currying）============

def demo_currying():
    """柯里化：把多参数函数变成单参数链"""
    print("\n📋 2. 柯里化（Currying）")
    
    # 普通 2 参数函数
    def add_uncurried(a, b):
        return a + b
    
    # 柯里化版本：每次只接收一个参数
    def add_curried(a):
        def inner(b):
            return a + b
        return inner
    
    print(f"   普通版：add(2, 3) = {add_uncurried(2, 3)}")
    print(f"   柯里化版：add(2)(3) = {add_curried(2)(3)}")
    
    # 柯里化的实际用途：partial application（部分应用）
    add_5 = add_curried(5)        # 创建"加 5"的函数
    add_10 = add_curried(10)      # 创建"加 10"的函数
    print(f"\n   部分应用：")
    print(f"   add_5 = add_curried(5); add_5(3) = {add_5(3)}")
    print(f"   add_10 = add_curried(10); add_10(3) = {add_10(3)}")
    
    # 3 参数柯里化
    def add_three_curried(a):
        return lambda b: lambda c: a + b + c
    
    print(f"\n   3 参数柯里化：")
    print(f"   add_three(1)(2)(3) = {add_three_curried(1)(2)(3)}")
    print(f"   add_1_2 = add_three(1)(2); add_1_2(3) = {add_three_curried(1)(2)(3)}")
    
    # 用 lambda 更简洁
    add_lambda = lambda a: lambda b: a + b
    print(f"\n   lambda 版：lambda a: lambda b: a+b")
    print(f"   add_lambda(2)(3) = {add_lambda(2)(3)}")
    
    print(f"\n   💡 柯里化的本质：把「多输入函数」变成「单输入函数的链」")
    print(f"      Haskell 自动柯里化：add 2 3 = (add 2) 3")
    print(f"      Python 不自动，但写起来不难——多看几次就习惯")


# ============ 3. Y 组合子（lambda 演算的奇迹）============

def demo_y_combinator():
    """Y = λf.(λx.f(x x))(λx.f(x x))
    让匿名 lambda 也能递归！"""
    print("\n📋 3. Y 组合子（不用 def 实现递归）")
    
    # 普通 def 递归
    def fact_def(n):
        return 1 if n == 0 else n * fact_def(n - 1)
    
    # Y 组合子版：函数不引用自己
    # 思路：写一个"接收递归函数并返回值"的函数，然后用 Y 把它"递归化"
    
    # fact_func 接收一个"假设的 fact"函数，返回一个真正的 fact 函数
    fact_func = lambda fact: lambda n: 1 if n == 0 else n * fact(n - 1)
    
    # Y 组合子让 fact_func 真正递归
    # Y(f) = f(Y(f)) —— 不动点
    # Python 实现（用 lambda，但需要惰性求值，所以用 Z combinator 变种）
    
    # Z combinator（Y 在严格求值语言中的变种）
    Z = lambda f: (lambda x: f(lambda y: x(x)(y)))(lambda x: f(lambda y: x(x)(y)))
    
    fact_y = Z(fact_func)
    
    print(f"   def 版 factorial(5) = {fact_def(5)}")
    print(f"   Y 组合子版 factorial(5) = {fact_y(5)}")
    print(f"   Y 组合子版 factorial(10) = {fact_y(10)}")
    
    # fib 同样可以
    fib_func = lambda fib: lambda n: n if n < 2 else fib(n-1) + fib(n-2)
    fib_y = Z(fib_func)
    
    print(f"\n   Y 组合子版 fib(10) = {fib_y(10)}")
    
    print(f"\n   💡 反直觉：Y 组合子让纯 lambda（无 def、无名字）也能递归")
    print(f"      这是 lambda 演算的「不动点定理」：")
    print(f"      Y(f) 是 f 的不动点，即 f(Y(f)) = Y(f)")
    print(f"      Y 组合子 = 一切递归的「起源」")
    print(f"      Lisp 1960 就用这套——你后面写的 Scheme 解释器也包含")


# ============ 4. 牛顿法（不动点迭代）============

def demo_newton_method():
    """SICP 1.1.7 经典：用高阶函数做数值计算"""
    print("\n📋 4. 牛顿法（不动点迭代开方）")
    
    # 求平方根：找 y 使 y² = x，即 y = x/y 的不动点
    
    def average(a, b):
        return (a + b) / 2
    
    def improve(guess, x):
        """牛顿改进：用 guess 和 x/guess 的平均"""
        return average(guess, x / guess)
    
    def good_enough(guess, x, tolerance=1e-10):
        return abs(guess * guess - x) < tolerance
    
    def sqrt_iter(guess, x):
        """递归迭代到收敛"""
        if good_enough(guess, x):
            return guess
        return sqrt_iter(improve(guess, x), x)
    
    def sqrt(x):
        return sqrt_iter(1.0, x)
    
    print(f"   sqrt(2) = {sqrt(2):.15f}    （真值 {2**0.5:.15f}）")
    print(f"   sqrt(4) = {sqrt(4):.15f}")
    print(f"   sqrt(9) = {sqrt(9):.15f}")
    print(f"   sqrt(0.0001) = {sqrt(0.0001):.15f}    （真值 0.01）")
    
    # 通用不动点求值器（高阶函数）
    def fixed_point(f, first_guess, tolerance=1e-10):
        """找 f 的不动点 x，使 f(x) = x"""
        def try_next(guess):
            next_val = f(guess)
            if abs(next_val - guess) < tolerance:
                return next_val
            return try_next(next_val)
        return try_next(first_guess)
    
    # 用不动点求 sqrt
    def sqrt_via_fp(x):
        return fixed_point(lambda y: (y + x/y) / 2, 1.0)
    
    print(f"\n   用不动点求 sqrt(2) = {sqrt_via_fp(2):.15f}")
    
    # 黄金比 φ 是 x = 1 + 1/x 的不动点
    phi = fixed_point(lambda x: 1 + 1/x, 1.0)
    print(f"   黄金比 φ = {phi:.15f}    （真值 {(1+5**0.5)/2:.15f}）")
    
    # 立方根：x = y³ 的不动点
    def cbrt(x):
        return fixed_point(lambda y: (2*y + x/y/y) / 3, 1.0)
    print(f"   立方根 ∛27 = {cbrt(27):.15f}    （真值 3）")
    
    print(f"\n   💡 高阶函数 + 不动点 = 数值计算的通用范式")
    print(f"      「找 f 的不动点」是 SICP 反复出现的主题——")
    print(f"      微积分的不动点 / 类型推断的不动点 / 抽象解释的不动点")
    print(f"      数学、计算、逻辑都共享同一思想")


# ============ 5. 反直觉：用函数做数据（continuation）============

def demo_continuation():
    """Continuation-Passing Style（CPS）—— 把「下一步」作为参数"""
    print("\n📋 5. Continuation-Passing Style（CPS）")
    
    # 普通版
    def square_normal(x):
        return x * x
    
    # CPS 版：不 return 值，而是把值传给 continuation
    def square_cps(x, k):
        return k(x * x)
    
    print(f"   普通版：square(5) = {square_normal(5)}")
    print(f"   CPS 版：square_cps(5, print) → ", end="")
    square_cps(5, lambda v: print(v))
    
    # CPS 让"控制流"显式化
    print(f"\n   CPS 的串联（chain）：")
    print(f"   square_cps(5, lambda v: square_cps(v, lambda w: print('最终:', w)))")
    square_cps(5, lambda v: square_cps(v, lambda w: print(f"     最终: {w}")))
    
    print(f"\n   💡 CPS 是函数式编程的核心技术之一")
    print(f"      Scheme / OCaml / Haskell 都用它做异步/异常/协程")
    print(f"      async/await 本质就是 CPS 的语法糖")
    print(f"      JS Promise、Python asyncio 都是 CPS 的变体")


# ============ 6. 反直觉：lambda 演算 = 图灵完备 ============

def demo_lambda_turing_complete():
    """lambda 演算和图灵机等价——所有可计算函数都能用 lambda 表达"""
    print("\n📋 6. 反直觉：lambda 演算 = 图灵完备")
    
    # 用 lambda 实现 boolean
    T = lambda x: lambda y: x       # True：选第一个
    F = lambda x: lambda y: y       # False：选第二个
    
    def bool_to_str(b):
        return "True" if b("T")("F") == "T" else "False"
    
    print(f"   用 lambda 编码 Boolean：")
    print(f"   T = lambda x: lambda y: x    （选第一个）")
    print(f"   F = lambda x: lambda y: y    （选第二个）")
    
    # And = λp.λq. p q p
    AND = lambda p: lambda q: p(q)(p)
    OR = lambda p: lambda q: p(p)(q)
    NOT = lambda p: lambda a: lambda b: p(b)(a)
    
    print(f"\n   AND(T, T) = {bool_to_str(AND(T)(T))}")
    print(f"   AND(T, F) = {bool_to_str(AND(T)(F))}")
    print(f"   AND(F, T) = {bool_to_str(AND(F)(T))}")
    print(f"   OR(F, T)  = {bool_to_str(OR(F)(T))}")
    print(f"   NOT(T)    = {bool_to_str(NOT(T))}")
    print(f"   NOT(F)    = {bool_to_str(NOT(F))}")
    
    print(f"\n   💡 反直觉：boolean、number、list 全都能用 lambda 编码")
    print(f"      这就是 Church-Turing 论题的核心——")
    print(f"      「可计算 = lambda 演算 = 图灵机」")
    print(f"      你后面写的 Scheme 解释器本质上就是个 lambda 演算实现")


# ============ main ============

def main():
    print("=" * 60)
    print("CS 61A Day 4-5 - Lecture 7-10 合并")
    print("Lambda Calculus + Currying + Newton + Continuations")
    print("=" * 60)
    
    demo_church_numerals()
    demo_currying()
    demo_y_combinator()
    demo_newton_method()
    demo_continuation()
    demo_lambda_turing_complete()
    
    print("\n" + "=" * 60)
    print("💡 Day 4-5 元洞察：")
    print("   1. Church numerals：数字本质 = 函数应用次数")
    print("   2. 柯里化：多参数 = 单参数函数的链")
    print("   3. Y 组合子：不动点 = 让 lambda 递归")
    print("   4. 牛顿法 = 不动点迭代 = 高阶函数 + 数值")
    print("   5. CPS：把控制流显式化（async/await 的本质）")
    print("   6. Lambda 演算 = 图灵完备（一切计算的本质）")
    print("   CS 61A 后半学期写 Scheme 解释器就是这套思想的工程化")
    print("=" * 60)


if __name__ == "__main__":
    main()
