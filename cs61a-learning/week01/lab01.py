"""
CS 61A Day 3 - Lab 01：递归应用实战（4 题）
============================================
Lab 是 CS 61A 的"动手练手"环节，比 HW 更接近考试。
本 Lab 强化 Day 2-3 学的递归思维。
"""

from operator import add, mul


# ============ Lab Q1: repeated（高阶函数+递归）============

def repeated(f, n):
    """Return the function that computes the nth application of f.
    
    >>> repeated(lambda x: x + 1, 3)(5)   # ((5+1)+1)+1 = 8
    8
    >>> repeated(lambda x: x * 2, 3)(1)   # ((1*2)*2)*2 = 8
    8
    >>> repeated(lambda x: x ** 2, 2)(3)  # (3**2)**2 = 81
    81
    
    💡 提示：
    - 递归定义：repeated(f, 1) = f; repeated(f, n) = compose(f, repeated(f, n-1))
    - compose(g, f)(x) = g(f(x))
    """
    # === YOUR CODE HERE ===
    if n == 1:
        return f
    return lambda x: f(repeated(f, n - 1)(x))


# ============ Lab Q2: num_eights（数字处理）============

def num_eights(pos):
    """Return the number of times 8 appears as a digit of pos.
    
    >>> num_eights(88888888)
    8
    >>> num_eights(123456789)
    1
    >>> num_eights(0)
    0
    >>> num_eights(8808)
    3
    
    💡 提示（递归版）：
    - if pos == 0: return 0
    - else: (1 if pos%10 == 8 else 0) + num_eights(pos // 10)
    """
    # === YOUR CODE HERE ===
    if pos == 0:
        return 0
    return (1 if pos % 10 == 8 else 0) + num_eights(pos // 10)


# ============ Lab Q3: digit_distance ============

def digit_distance(n):
    """Return the sum of absolute differences between adjacent digits of n.
    
    >>> digit_distance(121)    # |1-2| + |2-1| = 1 + 1 = 2
    2
    >>> digit_distance(555)    # 0 + 0 = 0
    0
    >>> digit_distance(73591)  # 2+2+4+8 = 16
    16
    >>> digit_distance(7)      # 单位数无邻居
    0
    
    💡 提示（递归）：
    - if n < 10: return 0
    - else: abs(n%10 - (n//10)%10) + digit_distance(n//10)
    """
    # === YOUR CODE HERE ===
    if n < 10:
        return 0
    last = n % 10
    second_last = (n // 10) % 10
    return abs(last - second_last) + digit_distance(n // 10)


# ============ Lab Q4: interleaved_sum（互相递归）============

def interleaved_sum(n, odd_func, even_func):
    """Compute odd_func(1) + even_func(2) + odd_func(3) + ... up to n.
    
    >>> interleaved_sum(5, lambda x: x, lambda x: x*x)  # 1 + 4 + 3 + 16 + 5
    29
    >>> interleaved_sum(4, lambda x: x, lambda x: x*x)  # 1 + 4 + 3 + 16
    24
    
    💡 提示：用互相递归
    - sum_from(k) where k is odd: apply odd_func(k), then call sum_from_even(k+1)
    - sum_from_even(k): apply even_func(k), then call sum_from(k+1)
    """
    # === YOUR CODE HERE ===
    def sum_from_odd(k):
        if k > n:
            return 0
        return odd_func(k) + sum_from_even(k + 1)
    
    def sum_from_even(k):
        if k > n:
            return 0
        return even_func(k) + sum_from_odd(k + 1)
    
    return sum_from_odd(1)


# ============ 测试 ============

def test_all():
    print("=" * 60)
    print("CS 61A Day 3 Lab 01 测试（4 题）")
    print("=" * 60)
    
    passed, failed = 0, 0
    
    # Lab Q1
    print("\n📋 Lab Q1: repeated")
    cases = [
        (lambda x: x + 1, 3, 5, 8),
        (lambda x: x * 2, 3, 1, 8),
        (lambda x: x ** 2, 2, 3, 81),
        (lambda x: x + 10, 4, 0, 40),
        (lambda x: x, 1, 99, 99),
    ]
    for f, n, x, exp in cases:
        r = repeated(f, n)(x)
        ok = r == exp
        print(f"   repeated(f, {n})({x}) = {r}, expected {exp}  {'✓' if ok else '✗'}")
        passed += ok; failed += not ok
    
    # Lab Q2
    print("\n📋 Lab Q2: num_eights")
    cases = [(88888888, 8), (123456789, 1), (0, 0), (8808, 3), (88, 2), (1, 0)]
    for n, exp in cases:
        r = num_eights(n)
        ok = r == exp
        print(f"   num_eights({n}) = {r}, expected {exp}  {'✓' if ok else '✗'}")
        passed += ok; failed += not ok
    
    # Lab Q3
    print("\n📋 Lab Q3: digit_distance")
    cases = [(121, 2), (555, 0), (73591, 18), (7, 0), (12, 1), (987, 2)]
    for n, exp in cases:
        r = digit_distance(n)
        ok = r == exp
        print(f"   digit_distance({n}) = {r}, expected {exp}  {'✓' if ok else '✗'}")
        passed += ok; failed += not ok
    
    # Lab Q4
    print("\n📋 Lab Q4: interleaved_sum（互相递归）")
    cases = [(5, lambda x: x, lambda x: x*x, 29), (4, lambda x: x, lambda x: x*x, 24),
             (1, lambda x: x, lambda x: x*x, 1), (10, lambda x: 1, lambda x: 0, 5)]
    for n, of, ef, exp in cases:
        r = interleaved_sum(n, of, ef)
        ok = r == exp
        print(f"   interleaved_sum({n}, odd, even) = {r}, expected {exp}  {'✓' if ok else '✗'}")
        passed += ok; failed += not ok
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} passed, {failed} failed")
    if failed == 0:
        print("🎉 Lab 01 全过！进入 Day 4")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
