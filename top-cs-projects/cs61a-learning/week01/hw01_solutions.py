"""
CS 61A HW 1 前 5 题（Q1-Q5）
============================
来源：composingprograms.com / CS 61A fa24 公开作业（适配学习用）

⚠️ 学习规则：
- 先自己尝试（每题给一个空的 starter）
- 卡住再看「💡 提示」
- 最后对照参考解
- 不直接抄——抄了等于没学

每题都跑了测试，确认答案正确。
"""

from operator import add, sub


# ============ Q1: a_plus_abs_b ============

def a_plus_abs_b(a, b):
    """Return a + abs(b), but without calling abs.

    >>> a_plus_abs_b(2, 3)
    5
    >>> a_plus_abs_b(2, -3)
    5
    
    💡 提示：
    - 如果 b >= 0：a + b
    - 如果 b < 0：a - b （减负数 = 加正数 = a + |b|）
    - 用 conditional expression 选 operator：add or sub
    - 写法：op = add if b >= 0 else sub; return op(a, b)
    """
    # === YOUR CODE HERE ===
    op = add if b >= 0 else sub
    return op(a, b)


# ============ Q2: two_of_three ============

def two_of_three(i, j, k):
    """Return x*x + y*y, where x and y are the two largest of i, j, k.

    >>> two_of_three(1, 2, 3)
    13   # 2² + 3² = 4 + 9
    >>> two_of_three(5, 3, 1)
    34   # 5² + 3² = 25 + 9
    >>> two_of_three(10, 2, 8)
    164  # 10² + 8² = 100 + 64
    >>> two_of_three(5, 5, 5)
    50   # 5² + 5²
    
    💡 提示（多种思路）：
    - 思路 A（暴力）：把三个数放 list，排序，取后两个的平方和
    - 思路 B（巧）：用 min/max —— 总和² - min² - max²... 不对
    - 思路 C（CS 61A 想要的）：不排序，用条件
        和 = i² + j² + k² - min(i,j,k)²
        （把最小的那个平方减掉）
    - 思路 C 的代码：return i*i + j*j + k*k - min(i, j, k)**2
    """
    # === YOUR CODE HERE ===
    return i*i + j*j + k*k - min(i, j, k)**2


# ============ Q3: largest_factor ============

def largest_factor(n):
    """Return the largest factor of n that is smaller than n.

    >>> largest_factor(15)   # factors: 1, 3, 5, 15 → answer 5
    5
    >>> largest_factor(80)   # factors: 1, 2, 4, 5, 8, 10, 16, 20, 40, 80 → answer 40
    40
    >>> largest_factor(13)   # prime, only factor is 1
    1
    
    💡 提示：
    - 一个数 n 的最大因子（除自己外）= n / 最小素因子
    - 但更简单的思路：从 n//2 倒着试到 1，第一个能整除的就是
    - 关键：n 的最大真因子不会超过 n//2（因为最小因子 ≥ 2）
    - 代码：
        for i in range(n//2, 0, -1):
            if n % i == 0:
                return i
    """
    # === YOUR CODE HERE ===
    factor = n // 2
    while factor > 0:
        if n % factor == 0:
            return factor
        factor -= 1
    return 1


# ============ Q4: if_function vs statement ============

def if_function(condition, true_result, false_result):
    """Return true_result if condition is a true value,
    and false_result otherwise.

    >>> if_function(True, 2, 3)
    2
    >>> if_function(False, 2, 3)
    3
    >>> if_function(3==2, 'yes', 'no')
    'no'
    """
    if condition:
        return true_result
    else:
        return false_result


def with_if_statement():
    """使用 if 语句版本"""
    if c():
        return t()
    else:
        return f()


def with_if_function():
    """使用 if_function() 高阶函数版本"""
    return if_function(c(), t(), f())


def c():
    print("c 被调用了")
    return False

def t():
    print("t 被调用了")
    return 1

def f():
    print("f 被调用了")
    return 2


# 💡 反直觉解释：
# with_if_statement：根据 c() 的结果，只调用 t() 或 f() 中的一个
# with_if_function：c(), t(), f() 三个都被调用！
# 因为 Python 在调用 if_function 时，必须先求所有参数的值


# ============ Q5: sum_digits ============

def sum_digits(n):
    """Sum all the digits of n.

    >>> sum_digits(7)        # 7
    7
    >>> sum_digits(123)      # 1+2+3
    6
    >>> sum_digits(10080)    # 1+0+0+8+0
    9
    >>> sum_digits(99999)    # 9*5
    45
    
    💡 提示：
    - 经典递归/迭代：用 n % 10 取最后一位，n // 10 去掉最后一位
    - 代码（迭代版）：
        total = 0
        while n > 0:
            total += n % 10
            n = n // 10
        return total
    - 递归版（更优雅）：
        if n < 10: return n
        return (n % 10) + sum_digits(n // 10)
    """
    # === YOUR CODE HERE ===
    total = 0
    while n > 0:
        total += n % 10
        n = n // 10
    return total


# ============ 测试 ============

def test_all():
    """跑所有测试"""
    print("=" * 60)
    print("CS 61A HW 1 测试结果（前 5 题）")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Q1
    print("\n📋 Q1: a_plus_abs_b")
    cases = [(2, 3, 5), (2, -3, 5), (-2, 3, 1), (-2, -3, 1), (0, 0, 0)]
    for a, b, expected in cases:
        result = a_plus_abs_b(a, b)
        ok = result == expected
        print(f"   a_plus_abs_b({a}, {b}) = {result}, expected {expected}  {'✓' if ok else '✗'}")
        if ok: passed += 1
        else: failed += 1
    
    # Q2
    print("\n📋 Q2: two_of_three")
    cases = [(1, 2, 3, 13), (5, 3, 1, 34), (10, 2, 8, 164), (5, 5, 5, 50), (0, 0, 1, 1)]
    for i, j, k, expected in cases:
        result = two_of_three(i, j, k)
        ok = result == expected
        print(f"   two_of_three({i}, {j}, {k}) = {result}, expected {expected}  {'✓' if ok else '✗'}")
        if ok: passed += 1
        else: failed += 1
    
    # Q3
    print("\n📋 Q3: largest_factor")
    cases = [(15, 5), (80, 40), (13, 1), (4, 2), (100, 50), (17, 1)]
    for n, expected in cases:
        result = largest_factor(n)
        ok = result == expected
        print(f"   largest_factor({n}) = {result}, expected {expected}  {'✓' if ok else '✗'}")
        if ok: passed += 1
        else: failed += 1
    
    # Q4
    print("\n📋 Q4: if_function vs statement")
    print(f"   with_if_statement() 输出（只调 c, 然后 t 或 f 之一）:")
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result_stmt = with_if_statement()
    print("     " + buf.getvalue().replace("\n", "\n     ").rstrip())
    print(f"     返回值: {result_stmt}")
    
    print(f"\n   with_if_function() 输出（c, t, f 全部被调用）:")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result_fn = with_if_function()
    print("     " + buf.getvalue().replace("\n", "\n     ").rstrip())
    print(f"     返回值: {result_fn}")
    
    print(f"\n   💡 关键洞察：Python 函数调用 = 立即求所有参数")
    print(f"      所以 if_function(c(), t(), f()) 等于：")
    print(f"        1. 求 c() → False")
    print(f"        2. 求 t() → 1（即使不会被用）")
    print(f"        3. 求 f() → 2")
    print(f"        4. if_function(False, 1, 2) → 2")
    print(f"      而 if statement 是短路求值！")
    print(f"      这是「短路与求值顺序」的核心教学")
    
    # Q5
    print("\n📋 Q5: sum_digits")
    cases = [(7, 7), (123, 6), (10080, 9), (99999, 45), (0, 0), (1111, 4)]
    for n, expected in cases:
        result = sum_digits(n)
        ok = result == expected
        print(f"   sum_digits({n}) = {result}, expected {expected}  {'✓' if ok else '✗'}")
        if ok: passed += 1
        else: failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} passed, {failed} failed")
    if failed == 0:
        print("🎉 全部通过！可以进入 HW 1 后 5 题（Q6-Q10）了")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
