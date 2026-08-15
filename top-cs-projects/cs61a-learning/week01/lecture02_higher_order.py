"""
CS 61A Day 1 - Lecture 2: Higher-Order Functions (高阶函数)
=========================================================
覆盖主题（composingprograms.com Ch 1.6）：
- 函数作为参数
- 函数作为返回值（闭包）
- Lambda 表达式
- 函数装饰器（decorator）
- 通用化模式（generalize patterns）

核心论文/教材：
- Abelson & Sussman SICP 1.3 "Formulating Abstractions with Higher-Order Procedures"
- John DeNero composingprograms.com 1.6
- Hughes 1989 "Why Functional Programming Matters"

本文件实现：
- 函数作为参数（map/reduce 等通用模式）
- 函数作为返回值（闭包 / 计数器 / 函数工厂）
- 装饰器（memoize / timer / logger）
- 反直觉：闭包捕获名字而非值

运行：
    python3 lecture02_higher_order.py
"""

from __future__ import annotations
import time
import functools
from typing import Callable, Any


# ============ 1. 函数作为参数 ============

def demo_function_as_argument():
    """函数作为参数 = 把'操作'抽象出来"""
    print("📋 1. 函数作为参数（把'做什么'参数化）")
    
    nums = [1, 2, 3, 4, 5]
    
    # 案例：写一个通用的"处理每个元素"的函数
    def apply_to_each(fn, items):
        """高阶函数：对每个元素应用 fn"""
        result = []
        for x in items:
            result.append(fn(x))
        return result
    
    # 同一个 apply_to_each，传不同 fn，得到完全不同结果
    print(f"   nums = {nums}")
    print(f"   apply_to_each(square, nums) = {apply_to_each(lambda x: x*x, nums)}")
    print(f"   apply_to_each(double, nums) = {apply_to_each(lambda x: x*2, nums)}")
    print(f"   apply_to_each(is_even, nums) = {apply_to_each(lambda x: x%2==0, nums)}")
    print(f"   apply_to_each(str, nums)     = {apply_to_each(str, nums)}")
    
    print(f"\n   💡 这就是 Python 内置 map 的原理——你刚重新发明了它")


# ============ 2. 函数作为返回值（闭包）============

def demo_closure():
    """函数作为返回值 = 函数工厂 + 状态封装"""
    print("\n📋 2. 闭包：函数返回函数")
    
    # 案例 1: 函数工厂（make_adder）
    def make_adder(n):
        """返回一个把 n 加到输入上的函数"""
        def adder(x):
            return x + n
        return adder
    
    add_5 = make_adder(5)
    add_10 = make_adder(10)
    print(f"   add_5 = make_adder(5)")
    print(f"   add_10 = make_adder(10)")
    print(f"   add_5(3) = {add_5(3)}    （5+3）")
    print(f"   add_10(3) = {add_10(3)}   （10+3）")
    print(f"   💡 add_5 和 add_10 是「不同实例」——每个闭包有自己的 n")
    
    # 案例 2: 计数器（用闭包封装可变状态）
    def make_counter(start=0):
        count = [start]  # 用 list 包装以突破闭包限制
        def increment():
            count[0] += 1
            return count[0]
        def get():
            return count[0]
        return increment, get
    
    inc, get = make_counter(100)
    print(f"\n   inc, get = make_counter(100)")
    print(f"   inc() → {inc()}  inc() → {inc()}  inc() → {inc()}")
    print(f"   get() = {get()}    （外部只能通过接口访问 count）")
    print(f"   💡 count 被闭包「私有化」——OOP 之前的封装手段")
    
    # 案例 3: 函数组合（function composition）
    def compose(f, g):
        """返回 f(g(x))"""
        return lambda x: f(g(x))
    
    f = compose(lambda x: x + 1, lambda x: x * 2)  # (x*2)+1
    print(f"\n   compose(x+1, x*2)(5) = {f(5)}    （(5*2)+1）")
    print(f"   💡 函数组合是函数式编程的核心——Haskell 的 . 操作符")


# ============ 3. Lambda 表达式 ============

def demo_lambda():
    """lambda = 匿名函数（用完即弃）"""
    print("\n📋 3. Lambda 表达式")
    
    # 等价的两种写法
    def square_def(x): return x * x
    square_lambda = lambda x: x * x
    
    print(f"   def square(x): return x*x   → square(4) = {square_def(4)}")
    print(f"   square = lambda x: x*x      → square(4) = {square_lambda(4)}")
    print(f"   ✓ 完全等价（Python 把它们视为同一对象类型）")
    
    # lambda 的真正用途：作为参数即时定义
    nums = [3, 1, 4, 1, 5, 9, 2, 6]
    print(f"\n   lambda 的常见用途：")
    print(f"     sorted({nums}, key=lambda x: -x)")
    print(f"     = {sorted(nums, key=lambda x: -x)}    （按降序）")
    print(f"     sorted({nums}, key=lambda x: (x % 2, x))")
    print(f"     = {sorted(nums, key=lambda x: (x % 2, x))}    （先偶后奇）")
    
    print(f"\n   💡 反直觉：lambda 限制为单表达式——不能有 if/for/while")
    print(f"      def 函数能做的事，lambda 几乎都不能")
    print(f"      PEP 8 建议：lambda 仅用于简单的 key= 参数，其他都用 def")


# ============ 4. 装饰器（decorator）============

def demo_decorator():
    """装饰器 = 接收函数返回函数的高阶函数的语法糖"""
    print("\n📋 4. 装饰器（@syntax）")
    
    # 案例 1: 计时装饰器
    def timer(fn):
        """测量 fn 的执行时间"""
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1e6
            print(f"      [timer] {fn.__name__} took {elapsed:.2f} μs")
            return result
        return wrapper
    
    @timer
    def slow_sum(n):
        return sum(range(n))
    
    print(f"   @timer 装饰的函数：")
    result = slow_sum(1000)
    print(f"   slow_sum(1000) = {result}")
    
    # 案例 2: memoize 装饰器（缓存）
    def memoize(fn):
        cache = {}
        @functools.wraps(fn)
        def wrapper(*args):
            if args not in cache:
                cache[args] = fn(*args)
                print(f"      [memo] computed {fn.__name__}{args} → {cache[args]}")
            else:
                print(f"      [memo] cached {fn.__name__}{args} → {cache[args]}")
            return cache[args]
        return wrapper
    
    @memoize
    def fib(n):
        if n < 2: return n
        return fib(n-1) + fib(n-2)
    
    print(f"\n   @memoize 装饰的 fib：")
    print(f"   fib(5) 计算过程：")
    fib(5)
    
    print(f"\n   💡 反直觉：朴素递归 fib(40) 约 1 亿次调用")
    print(f"      memoize 后只需 40 次计算 + 40 次缓存查找")
    print(f"      时间复杂度 O(2^n) → O(n) —— 装饰器加 5 行代码")


# ============ 5. 通用化模式（CS 61A 精髓）============

def demo_generalize():
    """高阶函数的真正威力：识别并抽象重复模式"""
    print("\n📋 5. 通用化模式（CS 61A 的核心训练）")
    
    # 案例：求 1+2+...+n vs 求 1*2*...*n vs 求 1²+2²+...+n²
    # 看似 3 个不同问题，其实是一个"累积"模式
    
    def accumulate(combiner, start, n, term):
        """
        通用累积函数：
        combiner: 如何把当前值合并到累积器（如 +, *）
        start: 初始值
        n: 上界（1 到 n）
        term: 对每个 i 应用什么变换
        """
        result = start
        for i in range(1, n + 1):
            result = combiner(result, term(i))
        return result
    
    # 同一个 accumulate，做完全不同的事
    sum_n = accumulate(lambda a, b: a + b, 0, 5, lambda x: x)
    product_n = accumulate(lambda a, b: a * b, 1, 5, lambda x: x)
    sum_squares = accumulate(lambda a, b: a + b, 0, 5, lambda x: x * x)
    
    print(f"   accumulate 是「累积」的通用模式")
    print(f"   accumulate(+, 0, 5, id)      = {sum_n}    （1+2+3+4+5）")
    print(f"   accumulate(*, 1, 5, id)      = {product_n}    （1*2*3*4*5 = 5!）")
    print(f"   accumulate(+, 0, 5, square)  = {sum_squares}   （1²+2²+3²+4²+5²）")
    
    print(f"\n   💡 这是 SICP 的灵魂：识别重复模式 → 抽象成高阶函数")
    print(f"      CS 61A 期末 Scheme 项目就是把这套思想用到极致——")
    print(f"      你会写一个解释器，让同样思想在另一个语言里跑起来")


# ============ 6. 反直觉：闭包捕获名字 vs 值 ============

def demo_closure_late_binding():
    """最反直觉的闭包案例——很多老手也会踩坑"""
    print("\n📋 6. 反直觉：闭包捕获「名字」不是「值」")
    
    # 创建 3 个"应该"分别打印 0/1/2 的函数
    funcs = []
    for i in range(3):
        funcs.append(lambda: i)  # 期望捕获当前 i 的值
    
    print(f"   for i in range(3):")
    print(f"       funcs.append(lambda: i)")
    print(f"   [f() for f in funcs] = {[f() for f in funcs]}    （期望 [0,1,2]，实际全 2）")
    
    print(f"\n   根因：lambda 捕获的是「变量 i」本身，不是「i 当前的值」")
    print(f"      循环结束后 i=2，所以 3 个 lambda 都返回 2")
    
    # 修复方案 1：默认参数（在 def 时求值）
    funcs1 = [lambda i=i: i for i in range(3)]
    print(f"\n   修复 1（默认参数 i=i）: {[f() for f in funcs1]}    ✓")
    
    # 修复方案 2：高阶函数（factory）
    def make_func(i):
        return lambda: i
    funcs2 = [make_func(i) for i in range(3)]
    print(f"   修复 2（make_func 工厂）: {[f() for f in funcs2]}    ✓")
    
    print(f"\n   💡 这个 trap 在 asyncio 回调、Qt 信号、JS 事件处理里天天出现")
    print(f"      是「函数式编程进阶」的第一道门槛")


# ============ main ============

def main():
    print("=" * 60)
    print("CS 61A Day 1 - Lecture 2: Higher-Order Functions")
    print("=" * 60)
    
    demo_function_as_argument()
    demo_closure()
    demo_lambda()
    demo_decorator()
    demo_generalize()
    demo_closure_late_binding()
    
    print("\n" + "=" * 60)
    print("💡 高阶函数的元洞察：")
    print("   函数是「一等公民」——可以赋值、传参、返回、存储")
    print("   这让 Python 不仅是命令式语言，也是函数式语言")
    print("   CS 61A 后半学期会用这套思想写 Scheme 解释器")
    print("=" * 60)


if __name__ == "__main__":
    main()
