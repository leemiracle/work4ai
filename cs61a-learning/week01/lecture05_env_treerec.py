"""
CS 61A Day 3 - Lecture 5-6: Environments + Tree Recursion Patterns
==================================================================
你已有 Python 经验，跳过基础。重点：
- 环境图（environment diagrams）——CS 61A 最强教学工具
- 树递归的 4 大经典模式：count change / Pascal / Hanoi / mutual recursion
- 互相递归（mutual recursion）
- 反直觉：用递归描述问题 → 自动得到算法

核心教材：
- SICP 1.2.2 "Tree Recursion"（count change 是这里的灵魂案例）
- composingprograms.com 1.7 + 2.3 (Recursion + Mutable sequences)

本文件实现：
- 可视化环境图（嵌套 frame）
- count_partitions（SICP 经典）
- Pascal 三角形（递归定义）
- Tower of Hanoi（递归算法 = 数学定义）
- 互相递归 is_even / is_odd
- 反直觉：递归数论 = 不用 % 的奇偶判定

运行：
    python3 lecture05_env_treerec.py
"""

from __future__ import annotations


# ============ 1. 环境图（CS 61A 最强工具）============

def demo_environment_diagram():
    """画嵌套环境图——让闭包/作用域可视化"""
    print("📋 1. 环境图：可视化嵌套作用域")
    
    # 案例：高阶函数 + 闭包的环境
    def make_adder(n):
        def adder(x):
            return x + n
        return adder
    
    # 调用 make_adder(5) 创建的环境链：
    # global frame:
    #   make_adder → func(n)
    #   add_5 → func(x)  ← 调用 make_adder(5) 的返回值
    # f1: make_adder<call>(n=5) → 创建 adder 函数（其父帧是 f1）
    # f2: adder<call>(x=3) → 查找 x: 3, 查找 n: 沿链向上到 f1 找到 5
    
    add_5 = make_adder(5)
    result = add_5(3)
    
    print("   调用 add_5 = make_adder(5); add_5(3) 的环境链：")
    print("   ┌─ global")
    print("   │   make_adder → <func make_adder(n)>")
    print("   │   add_5 → <func adder(x)> [parent=f1]")
    print("   │")
    print("   ├─ f1: make_adder<call> [parent=global]")
    print("   │   n → 5")
    print("   │   adder → <func adder(x)> [parent=f1]  ← 这就是返回值")
    print("   │")
    print("   └─ f2: adder<call> [parent=f1]")
    print("       x → 3")
    print("       return x + n  # 查找 x: 3（当前帧）, n: 5（f1）")
    
    print(f"\n   结果：add_5(3) = {result}")
    print(f"\n   💡 关键洞察：adder 函数的 parent 是 f1（创建它的帧）")
    print(f"      不是 global——这就是「词法作用域」的本质")
    print(f"      函数记住自己「出生地」，无论之后被传到哪里")


# ============ 2. Count Partitions（SICP 灵魂案例）============

def demo_count_partitions():
    """SICP 1.2.2 经典：用递归描述分拆问题"""
    print("\n📋 2. Count Partitions（SICP 灵魂案例）")
    
    def count_partitions(n, m):
        """把 n 分拆成最大部分不超过 m 的方案数"""
        if n == 0: return 1
        elif n < 0: return 0
        elif m == 0: return 0
        else:
            # 两种情况之和：
            # A) 至少用一个 m：分拆 n-m 用最大 m
            # B) 不用 m：分拆 n 用最大 m-1
            with_m = count_partitions(n - m, m)
            without_m = count_partitions(n, m - 1)
            return with_m + without_m
    
    # 列出所有分拆
    def list_partitions(n, m, prefix=[]):
        if n == 0:
            yield list(prefix)
            return
        if n < 0 or m == 0:
            return
        # 用 m
        prefix.append(m)
        yield from list_partitions(n - m, m, prefix)
        prefix.pop()
        # 不用 m
        yield from list_partitions(n, m - 1, prefix)
    
    print(f"   count_partitions(6, 4) = {count_partitions(6, 4)}")
    print(f"   所有分拆：")
    for p in list(list_partitions(6, 4)):
        print(f"     {' + '.join(map(str, p))} = 6")
    
    print(f"\n   💡 这是「递归描述 = 自动算法」的最佳案例：")
    print(f"      把问题分成两种互斥情况（用 m / 不用 m），递归解决更小问题")
    print(f"      不用想「怎么遍历」，递归定义本身决定算法")


# ============ 3. Pascal 三角形（递归定义）============

def demo_pascal():
    """Pascal 三角形：递归定义 = 数学定义"""
    print("\n📋 3. Pascal 三角形（递归定义）")
    
    def pascal(row, col):
        """Pascal 三角形 row 行 col 列（0-indexed）"""
        if col == 0 or col == row:
            return 1
        return pascal(row - 1, col - 1) + pascal(row - 1, col)
    
    def print_pascal_triangle(rows):
        for r in range(rows):
            # 缩进
            print("   " + "  " * (rows - r - 1), end="")
            for c in range(r + 1):
                print(f"{pascal(r, c):3}", end=" ")
            print()
    
    print("   Pascal 三角形（前 7 行）：")
    print_pascal_triangle(7)
    
    print(f"\n   💡 Pascal 三角形 = (a+b)^n 的展开系数")
    print(f"      每个数 = 上方两个数之和（递归定义！）")
    print(f"      数学定义直接 = 算法，无需循环")


# ============ 4. Tower of Hanoi（递归算法 = 数学定义）============

def demo_hanoi():
    """汉诺塔：递归算法的标杆案例"""
    print("\n📋 4. Tower of Hanoi（递归算法标杆）")
    
    def hanoi(n, source, target, auxiliary):
        """
        把 n 个盘子从 source 移到 target，可用 auxiliary 辅助。
        返回移动步骤列表。
        """
        if n == 1:
            return [(n, source, target)]
        steps = []
        steps.extend(hanoi(n - 1, source, auxiliary, target))  # 上 n-1 个移到 auxiliary
        steps.append((n, source, target))                       # 最大盘移到 target
        steps.extend(hanoi(n - 1, auxiliary, target, source))  # 再把 n-1 个移到 target
        return steps
    
    steps = hanoi(3, 'A', 'C', 'B')
    print(f"   Hanoi(3, A, C, B) 需要 {len(steps)} 步：")
    for n, src, dst in steps:
        print(f"     把盘 {n} 从 {src} → {dst}")
    
    print(f"\n   💡 Hanoi 的最少步数 = 2^n - 1")
    print(f"      Hanoi(10) = {2**10 - 1} 步")
    print(f"      Hanoi(64) = {2**64 - 1} 步 ≈ 5850 亿年（宇宙年龄的 42 倍）")
    print(f"      这是「印度梵塔传说」——僧侣搬完后世界末日")


# ============ 5. 互相递归（Mutual Recursion）============

def demo_mutual_recursion():
    """互相递归：两个函数互相调用——比单函数递归更强大"""
    print("\n📋 5. 互相递归（Mutual Recursion）")
    
    # 案例：不用 % 判断奇偶（教学案例，不是推荐用法）
    def is_even(n):
        if n == 0: return True
        return is_odd(n - 1)
    
    def is_odd(n):
        if n == 0: return False
        return is_even(n - 1)
    
    print(f"   互相递归判断奇偶（不用 %）：")
    for i in range(8):
        print(f"     is_even({i}) = {is_even(i)}, is_odd({i}) = {is_odd(i)}")
    
    # 案例：用互相递归做有限状态机
    print(f"\n   案例 2：表达式语法（FSM 用互相递归模拟）")
    def parse_number(s, i=0):
        """从位置 i 开始解析数字，返回 (number, next_i)"""
        start = i
        while i < len(s) and s[i].isdigit():
            i += 1
        if start == i:
            raise ValueError(f"Expected digit at {i}")
        return int(s[start:i]), i
    
    def parse_factor(s, i=0):
        """解析 factor: number | ( expr )"""
        if s[i] == '(':
            val, i = parse_expr(s, i + 1)
            assert s[i] == ')', f"Expected ')' at {i}"
            return val, i + 1
        return parse_number(s, i)
    
    def parse_term(s, i=0):
        """解析 term: factor (* factor | / factor)*"""
        val, i = parse_factor(s, i)
        while i < len(s) and s[i] in '*/':
            op = s[i]
            right, i = parse_factor(s, i + 1)
            val = val * right if op == '*' else val // right
        return val, i
    
    def parse_expr(s, i=0):
        """解析 expr: term (+ term | - term)*"""
        val, i = parse_term(s, i)
        while i < len(s) and s[i] in '+-':
            op = s[i]
            right, i = parse_term(s, i + 1)
            val = val + right if op == '+' else val - right
        return val, i
    
    # 测试 mini 表达式解析器（互相递归的实战）
    tests = ["1+2*3", "(1+2)*3", "10/2+3", "2*3+4*5"]
    for expr in tests:
        result, end = parse_expr(expr)
        print(f"     parse({expr!r}) = {result}    （解析到位置 {end}）")
    
    print(f"\n   💡 互相递归 = 语法解析的基础（BNF 文法 → 互相递归函数）")
    print(f"      CS 61A 后半学期写 Scheme 解释器时，整个 parser 就是互相递归")


# ============ 6. 反直觉：递归形态决定复杂度 ============

def demo_recursion_complexity():
    """同一个问题用不同递归形态，复杂度可能差指数级"""
    print("\n📋 6. 反直觉：递归形态决定复杂度")
    
    import time
    
    # fib 三种实现
    def fib_tree(n):
        """树递归 O(φⁿ)"""
        if n < 2: return n
        return fib_tree(n-1) + fib_tree(n-2)
    
    def fib_linear(n, a=0, b=1):
        """线性递归 O(n)（尾递归形式）"""
        if n == 0: return a
        return fib_linear(n - 1, b, a + b)
    
    from functools import lru_cache
    @lru_cache(maxsize=None)
    def fib_memo(n):
        """带 memoize 的树递归 O(n)"""
        if n < 2: return n
        return fib_memo(n-1) + fib_memo(n-2)
    
    # 计时
    print(f"   三种 fib 实现对比：")
    
    n = 25
    t0 = time.perf_counter(); r1 = fib_tree(n); t1 = time.perf_counter()
    print(f"     fib_tree({n}) = {r1}    耗时 {(t1-t0)*1000:.2f} ms（树递归）")
    
    t0 = time.perf_counter(); r2 = fib_linear(n); t1 = time.perf_counter()
    print(f"     fib_linear({n}) = {r2}    耗时 {(t1-t0)*1000:.4f} ms（线性递归）")
    
    t0 = time.perf_counter(); r3 = fib_memo(n); t1 = time.perf_counter()
    print(f"     fib_memo({n}) = {r3}    耗时 {(t1-t0)*1000:.4f} ms（带 memoize）")
    
    n = 35
    t0 = time.perf_counter(); r1 = fib_tree(n); t1 = time.perf_counter()
    print(f"\n     fib_tree({n}) = {r1}    耗时 {(t1-t0)*1000:.2f} ms")
    
    t0 = time.perf_counter(); r2 = fib_linear(n); t1 = time.perf_counter()
    print(f"     fib_linear({n}) = {r2}    耗时 {(t1-t0)*1000:.4f} ms")
    
    print(f"\n   💡 fib_tree(35) 比 fib_linear(35) 慢 {((t1-t0)*1000):.0f}×+ 量级")
    print(f"      树递归 O(φⁿ) vs 线性 O(n)")
    print(f"      memoize 把树递归变成 O(n) —— 但还是用 O(n) 空间")
    print(f"      线性递归 + 尾递归形式是 O(n) 时间 + O(1) 空间（如有 TCO）")


# ============ main ============

def main():
    print("=" * 60)
    print("CS 61A Day 3 - Lecture 5-6: Environments + Tree Recursion")
    print("=" * 60)
    
    demo_environment_diagram()
    demo_count_partitions()
    demo_pascal()
    demo_hanoi()
    demo_mutual_recursion()
    demo_recursion_complexity()
    
    print("\n" + "=" * 60)
    print("💡 Day 3 元洞察：")
    print("   1. 环境图让闭包/作用域「可视化」——CS 61A 的灵魂教学工具")
    print("   2. 递归定义 = 自动算法（count_partitions, Pascal, Hanoi）")
    print("   3. 互相递归 = 文法解析的基础（parse_expr ↔ parse_term ↔ parse_factor）")
    print("   4. 递归形态决定复杂度：树递归 O(φⁿ) vs 线性 O(n)")
    print("   5. memoize 能把树递归变成 O(n) —— 用空间换时间")
    print("   6. CS 61A 期末 Scheme 解释器 = 互相递归的极致应用")
    print("=" * 60)


if __name__ == "__main__":
    main()
