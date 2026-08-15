"""
CS 61A Day 2 - Lecture 3-4 合并: Control + Recursion（递归 = SICP 的灵魂）
=========================================================================
你已有 Python 经验，跳过 if/while/for 语法。专注：
- print vs return（最容易混淆的概念）
- 控制流 = 程序的「时间维度」
- 递归 = 自己调用自己（CS 61A 后半学期的地基）
- 迭代 vs 递归的等价与转换
- 反直觉：递归不一定慢（尾调用优化）

核心教材：
- SICP 1.2 "Procedures and the Processes They Generate"
- composingprograms.com 1.7 "Recursive Functions"

本文件实现：
- print vs return 的 5 个陷阱
- 迭代 → 递归 的系统转换法
- 线性递归 vs 树递归（fib 对比）
- 尾递归（tail recursion）与 Python 为何不做 TCO
- 反直觉：递归版本的 GCD 比 迭代版可读性更强

运行：
    python3 lecture03_recursion.py
"""

from __future__ import annotations
import sys
sys.setrecursionlimit(10000)  # 避免 Python 默认 1000 限制


# ============ 1. print vs return（最容易混淆）============

def demo_print_vs_return():
    """5 个经典 print/return 陷阱"""
    print("📋 1. print vs return（卡住 80% 的初学者）")
    
    # 陷阱 1: print 不等于 return
    def bad_square(x):
        print(x * x)        # 只显示，不返回
    
    def good_square(x):
        return x * x        # 真返回
    
    print(f"   bad_square(3) = {bad_square(3)}    （输出 9 但返回 None！）")
    print(f"   good_square(3) = {good_square(3)}    （真返回 9）")
    
    # 陷阱 2: print 后还想用结果
    try:
        result = bad_square(5) + 1  # None + 1 → TypeError
    except TypeError as e:
        print(f"   bad_square(5) + 1 → TypeError: {e}")
    
    # 陷阱 3: None 判等
    print(f"   bad_square(3) == None → {bad_square(3) == None}    （print 函数默认返回 None）")
    print(f"   good_square(3) == None → {good_square(3) == None}")
    
    print(f"\n   💡 规则：函数要么 print（不返回值）要么 return（不显示）")
    print(f"      混用 = bug 源。CS 61A HW 自动评测只看 return 值，不看 print")


# ============ 2. 迭代 → 递归 的系统转换法 ============

def demo_iteration_to_recursion():
    """任何迭代都能转成递归——3 步法"""
    print("\n📋 2. 迭代 → 递归的系统转换法")
    
    # 案例 1: 求阶乘（迭代版）
    def factorial_iter(n):
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
    
    # 转 3 步法：
    # Step 1: 识别"状态变量" → result, i
    # Step 2: 识别"递归情况" → 把当前 i 累乘后，进入下一轮
    # Step 3: 识别"基础情况" → i > n 时停止
    def factorial_rec(n, i=1, result=1):
        if i > n:                       # 基础情况
            return result
        return factorial_rec(n, i + 1, result * i)  # 递归情况
    
    print(f"   案例 1: 阶乘")
    print(f"     factorial_iter(5) = {factorial_iter(5)}")
    print(f"     factorial_rec(5)  = {factorial_rec(5)}")
    
    # 案例 2: 列表求和（迭代 → 递归）
    def sum_iter(lst):
        total = 0
        for x in lst:
            total += x
        return total
    
    def sum_rec(lst):
        if not lst:                     # 基础情况：空列表
            return 0
        return lst[0] + sum_rec(lst[1:])   # 递归：第一个 + 剩余的和
    
    print(f"\n   案例 2: 列表求和")
    print(f"     sum_iter([1,2,3,4,5]) = {sum_iter([1,2,3,4,5])}")
    print(f"     sum_rec([1,2,3,4,5])  = {sum_rec([1,2,3,4,5])}")
    print(f"     递归展开: 1 + (2 + (3 + (4 + (5 + 0))))")
    
    print(f"\n   💡 3 步法模板：")
    print(f"     def rec(state):")
    print(f"         if base_condition(state):")
    print(f"             return base_value")
    print(f"         return combine(current, rec(next_state))")


# ============ 3. 线性递归 vs 树递归（核心概念）============

def demo_linear_vs_tree_recursion():
    """递归的两种形态：线性（1分支）vs 树（多分支）"""
    print("\n📋 3. 线性递归 vs 树递归（核心概念）")
    
    # 线性递归：每次只递归一次
    def factorial(n):
        if n <= 1: return 1
        return n * factorial(n - 1)   # 单分支
    
    # 树递归：每次递归多次
    def fib(n):
        if n < 2: return n
        return fib(n - 1) + fib(n - 2)  # 双分支 → 调用树指数增长
    
    print(f"   线性递归（阶乘）：")
    print(f"     factorial(5) = {factorial(5)}")
    print(f"     调用链: factorial(5)→factorial(4)→factorial(3)→factorial(2)→factorial(1)")
    print(f"     总调用数: 5 次 = O(n)")
    
    print(f"\n   树递归（斐波那契）：")
    print(f"     fib(10) = {fib(10)}")
    # 画 fib(5) 的调用树
    def fib_trace(n, depth=0):
        indent = "  " * depth
        if n < 2:
            print(f"{indent}fib({n}) = {n}")
            return n
        print(f"{indent}fib({n}) →")
        a = fib_trace(n - 1, depth + 1)
        b = fib_trace(n - 2, depth + 1)
        print(f"{indent}fib({n}) = {a} + {b} = {a + b}")
        return a + b
    
    print(f"     fib(5) 调用树：")
    fib_trace(5)
    
    # 统计调用次数
    call_count = [0]
    def fib_counted(n):
        call_count[0] += 1
        if n < 2: return n
        return fib_counted(n-1) + fib_counted(n-2)
    
    call_count[0] = 0
    fib_counted(10)
    calls_10 = call_count[0]
    call_count[0] = 0
    fib_counted(20)
    calls_20 = call_count[0]
    call_count[0] = 0
    fib_counted(30)
    calls_30 = call_count[0]
    
    print(f"\n     fib(10) 调用次数: {calls_10}")
    print(f"     fib(20) 调用次数: {calls_20}    ({calls_20 // calls_10}× 增长)")
    print(f"     fib(30) 调用次数: {calls_30}    ({calls_30 // calls_20}× 增长)")
    print(f"\n   💡 反直觉：朴素 fib 的调用数 ≈ φⁿ/√5（黄金比）—— 指数爆炸")
    print(f"      fib(100) 的调用数 > 宇宙原子数（10⁸⁰）")


# ============ 4. 尾递归（tail recursion）============

def demo_tail_recursion():
    """尾递归 = 递归调用是函数最后一个动作——可被编译器优化成循环"""
    print("\n📋 4. 尾递归（tail recursion）与 Python 为何不做 TCO")
    
    # 非尾递归：乘法在递归之后执行
    def factorial_non_tail(n):
        if n <= 1: return 1
        return n * factorial_non_tail(n - 1)  # 递归后还要乘 n
    
    # 尾递归：递归是最后动作（用累加器）
    def factorial_tail(n, acc=1):
        if n <= 1: return acc
        return factorial_tail(n - 1, n * acc)   # 直接返回递归结果
    
    print(f"   非尾递归 factorial(5) = {factorial_non_tail(5)}")
    print(f"   尾递归   factorial(5) = {factorial_tail(5)}")
    
    print(f"\n   非尾递归的执行轨迹（递归后还有工作）：")
    print(f"     factorial(5)")
    print(f"     = 5 * factorial(4)")
    print(f"     = 5 * (4 * factorial(3))")
    print(f"     = 5 * (4 * (3 * factorial(2)))")
    print(f"     = 5 * (4 * (3 * (2 * factorial(1))))")
    print(f"     = 5 * (4 * (3 * (2 * 1)))    ← 这才开始回溯计算")
    print(f"     = ... 需要 O(n) 栈空间")
    
    print(f"\n   尾递归的执行轨迹（递归是最后动作）：")
    print(f"     factorial(5, 1)")
    print(f"     = factorial(4, 5)")
    print(f"     = factorial(3, 20)")
    print(f"     = factorial(2, 60)")
    print(f"     = factorial(1, 120)")
    print(f"     = 120    ← 立即返回，无需回溯！")
    
    print(f"\n   💡 反直觉：Python 不做尾调用优化（TCO）！")
    print(f"      所以 Python 中 factorial_tail(2000) 仍会栈溢出")
    print(f"      原因：Guido van Rossum 认为栈追踪对调试更重要")
    print(f"      Scheme/Haskell/Elixir 都做 TCO——可以无限递归不爆栈")
    
    # 验证 Python 栈溢出
    try:
        factorial_tail(2000)
        print(f"   factorial_tail(2000) = 成功（意外）")
    except RecursionError:
        print(f"   factorial_tail(2000) = RecursionError（如预期，Python 无 TCO）")


# ============ 5. 反直觉：递归有时比迭代更清晰 ============

def demo_recursion_more_readable():
    """GCD（最大公约数）的递归版比迭代版更可读"""
    print("\n📋 5. 反直觉：递归有时比迭代更清晰")
    
    # 案例：GCD（欧几里得算法）
    # 迭代版
    def gcd_iter(a, b):
        while b:
            a, b = b, a % b
        return a
    
    # 递归版（几乎就是数学定义）
    def gcd_rec(a, b):
        if b == 0:
            return a
        return gcd_rec(b, a % b)
    
    print(f"   GCD 案例：")
    print(f"   迭代版: def gcd(a,b):")
    print(f"             while b: a,b = b, a%b")
    print(f"             return a")
    print(f"   递归版: def gcd(a,b):")
    print(f"             if b == 0: return a")
    print(f"             return gcd(b, a % b)")
    print(f"\n   gcd_iter(48, 18) = {gcd_iter(48, 18)}")
    print(f"   gcd_rec(48, 18)  = {gcd_rec(48, 18)}")
    
    print(f"\n   💡 递归版更接近数学定义「gcd(a,b) = gcd(b, a mod b), gcd(a,0)=a」")
    print(f"      SICP 的核心主张：「程序 = 数学表达的可执行版本」")
    print(f"      当递归更清晰时，优先用递归（Haskell 几乎不用循环）")


# ============ 6. 反直觉：递归实现的幂运算比迭代快 ============

def demo_fast_expt():
    """快速幂：O(log n) 的递归实现"""
    print("\n📋 6. 反直觉：递归的快速幂 O(log n) vs 迭代线性 O(n)")
    
    def slow_expt(b, n):
        """线性迭代：b^n = b * b * ... * b（n 次）"""
        result = 1
        for _ in range(n):
            result *= b
        return result
    
    def fast_expt(b, n):
        """O(log n) 递归：利用 b^n = (b^(n/2))^2 当 n 偶数"""
        if n == 0: return 1
        if n % 2 == 0:
            half = fast_expt(b, n // 2)
            return half * half      # 平方
        else:
            return b * fast_expt(b, n - 1)
    
    print(f"   slow_expt(2, 10) = {slow_expt(2, 10)}    （10 次乘法）")
    print(f"   fast_expt(2, 10) = {fast_expt(2, 10)}    （约 log₂10 ≈ 4 次乘法）")
    print(f"   fast_expt(2, 100) = {fast_expt(2, 100)}    （约 7 次乘法！）")
    print(f"   fast_expt(2, 1000) 有 {len(str(fast_expt(2, 1000)))} 位十进制    （约 10 次乘法）")
    
    print(f"\n   💡 反直觉：递归版本比迭代版本快 O(n/log n) 倍")
    print(f"      fast_expt(2, 1000000) 约 20 次递归调用 = 1 秒内完成")
    print(f"      slow_expt(2, 1000000) 需 100 万次乘法 = 数分钟")
    print(f"      SICP 经典案例：选对抽象 → 性能指数级提升")


# ============ main ============

def main():
    print("=" * 60)
    print("CS 61A Day 2 - Lecture 3-4: Control + Recursion")
    print("=" * 60)
    
    demo_print_vs_return()
    demo_iteration_to_recursion()
    demo_linear_vs_tree_recursion()
    demo_tail_recursion()
    demo_recursion_more_readable()
    demo_fast_expt()
    
    print("\n" + "=" * 60)
    print("💡 Day 2 元洞察：")
    print("   1. print ≠ return。函数的核心是「返回值」不是「显示」")
    print("   2. 迭代 ⟺ 递归。用 3 步法系统转换")
    print("   3. 树递归指数爆炸（fib 调用数 ≈ φⁿ）。用 memoize 或转迭代")
    print("   4. 尾递归可被优化为循环——但 Python 不做 TCO")
    print("   5. 选对递归形式 → O(log n) 快速幂 vs O(n) 线性幂")
    print("   6. 程序 = 数学表达的可执行版本——当递归更接近数学，优先用")
    print("=" * 60)


if __name__ == "__main__":
    main()
