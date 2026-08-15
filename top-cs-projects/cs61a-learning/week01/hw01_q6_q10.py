"""
CS 61A HW 1 后 5 题（Q6-Q10）—— Day 2 主题：递归 + 控制
========================================================
每题含：题面 + 测试 + 提示 + 参考解。
"""

import math


# ============ Q6: falling（下降阶乘）============

def falling(n, k):
    """Return the falling factorial of n by k (n * (n-1) * ... * (n-k+1)).
    
    >>> falling(6, 3)   # 6 * 5 * 4
    120
    >>> falling(4, 0)   # 空乘 = 1
    1
    >>> falling(4, 3)   # 4 * 3 * 2
    24
    >>> falling(4, 1)   # 4
    4
    >>> falling(4, 5)   # k > n，根据题意应返回 0（或视为不可达）
    0
    
    💡 提示：
    - 思路 A（迭代）：result = 1; for i in range(k): result *= n - i
    - 思路 B（递归）：k=0 返回 1; 否则 n * falling(n-1, k-1)
    - 边界：k > n 时返回 0（题目约定）
    """
    # === YOUR CODE HERE ===
    if k > n:
        return 0
    result = 1
    for i in range(k):
        result *= n - i
    return result


# ============ Q7: divisible_by（过滤）============

def divisible_by(k, nums):
    """Return the count of elements in nums that are divisible by k.
    
    >>> divisible_by(3, [3, 6, 9, 10, 12])
    4   # 3, 6, 9, 12 都能被 3 整除
    >>> divisible_by(5, [10, 15, 20, 21])
    3
    >>> divisible_by(7, [1, 2, 3])
    0
    
    💡 提示：
    - 用 list comprehension 或 filter
    - 思路 A：return sum(1 for x in nums if x % k == 0)
    - 思路 B：return len([x for x in nums if x % k == 0])
    - 思路 C（递归，不推荐）：if not nums: return 0; return (1 if nums[0]%k==0 else 0) + divisible_by(k, nums[1:])
    """
    # === YOUR CODE HERE ===
    return sum(1 for x in nums if x % k == 0)


# ============ Q8: sum_squares_of_digits ============

def sum_squares_of_digits(n):
    """Sum the squares of each digit of n.
    
    >>> sum_squares_of_digits(123)   # 1² + 2² + 3²
    14
    >>> sum_squares_of_digits(999)   # 9² * 3
    243
    >>> sum_squares_of_digits(5)
    25
    
    💡 提示：
    - 用递归（Day 2 主题！）：if n < 10: return n*n; else (n%10)² + sum_squares_of_digits(n//10)
    - 或用迭代 + str(n) 转字符串处理
    """
    # === YOUR CODE HERE ===
    if n < 10:
        return n * n
    last = n % 10
    rest = n // 10
    return last * last + sum_squares_of_digits(rest)


# ============ Q9: count_partitions（SICP 经典）============

def count_partitions(n, m):
    """Count the number of partitions of n using parts up to size m.
    
    >>> count_partitions(6, 4)
    9   # 4+2, 4+1+1, 3+3, 3+2+1, 3+1+1+1, 2+2+2, 2+2+1+1, 2+1+1+1+1, 1+1+1+1+1+1
    >>> count_partitions(5, 5)
    7
    >>> count_partitions(2, 1)
    1   # 只能 1+1
    >>> count_partitions(10, 10)
    42
    
    💡 提示（SICP 经典递归）：
    - 一个 n 用最大部分 m 的分拆数 = 两种情况之和：
      A) 用至少一个 m：(分拆 n-m 用最大 m)
      B) 不用 m（即最大部分 m-1）：(分拆 n 用最大 m-1)
    - 基础情况：
      n=0 → 1（空分拆）
      n<0 → 0（不可能）
      m=0 但 n>0 → 0
    - 代码：
      if n == 0: return 1
      elif n < 0: return 0
      elif m == 0: return 0
      else: return count_partitions(n-m, m) + count_partitions(n, m-1)
    """
    # === YOUR CODE HERE ===
    if n == 0:
        return 1
    elif n < 0:
        return 0
    elif m == 0:
        return 0
    else:
        return count_partitions(n - m, m) + count_partitions(n, m - 1)


# ============ Q10: is_palindrome（字符串递归）============

def is_palindrome(s):
    """Return True if s is a palindrome (case-insensitive, ignore non-letters).
    
    >>> is_palindrome("racecar")
    True
    >>> is_palindrome("A man a plan a canal Panama")
    True
    >>> is_palindrome("hello")
    False
    >>> is_palindrome("")
    True
    >>> is_palindrome("a")
    True
    
    💡 提示（递归版，Day 2 主题）：
    - 先过滤掉非字母 + 转小写
    - 递归：if len(s) <= 1: True; else s[0] == s[-1] and is_palindrome(s[1:-1])
    """
    # === YOUR CODE HERE ===
    # 先过滤
    clean = ''.join(c.lower() for c in s if c.isalpha())
    # 递归
    if len(clean) <= 1:
        return True
    return clean[0] == clean[-1] and is_palindrome(clean[1:-1])


# ============ 测试 ============

def test_all():
    print("=" * 60)
    print("CS 61A HW 1 后 5 题测试（Q6-Q10）")
    print("=" * 60)
    
    passed, failed = 0, 0
    
    # Q6
    print("\n📋 Q6: falling")
    cases = [(6, 3, 120), (4, 0, 1), (4, 3, 24), (4, 1, 4), (4, 5, 0), (10, 4, 5040)]
    for n, k, exp in cases:
        r = falling(n, k)
        ok = r == exp
        print(f"   falling({n}, {k}) = {r}, expected {exp}  {'✓' if ok else '✗'}")
        passed += ok; failed += not ok
    
    # Q7
    print("\n📋 Q7: divisible_by")
    cases = [(3, [3, 6, 9, 10, 12], 4), (5, [10, 15, 20, 21], 3), (7, [1, 2, 3], 0), (2, [2, 4, 6, 8], 4)]
    for k, nums, exp in cases:
        r = divisible_by(k, nums)
        ok = r == exp
        print(f"   divisible_by({k}, {nums}) = {r}, expected {exp}  {'✓' if ok else '✗'}")
        passed += ok; failed += not ok
    
    # Q8
    print("\n📋 Q8: sum_squares_of_digits")
    cases = [(123, 14), (999, 243), (5, 25), (0, 0), (100, 1)]
    for n, exp in cases:
        r = sum_squares_of_digits(n)
        ok = r == exp
        print(f"   sum_squares_of_digits({n}) = {r}, expected {exp}  {'✓' if ok else '✗'}")
        passed += ok; failed += not ok
    
    # Q9
    print("\n📋 Q9: count_partitions (SICP 经典)")
    cases = [(6, 4, 9), (5, 5, 7), (2, 1, 1), (10, 10, 42), (1, 1, 1)]
    for n, m, exp in cases:
        r = count_partitions(n, m)
        ok = r == exp
        print(f"   count_partitions({n}, {m}) = {r}, expected {exp}  {'✓' if ok else '✗'}")
        passed += ok; failed += not ok
    
    # Q10
    print("\n📋 Q10: is_palindrome")
    cases = [("racecar", True), ("A man a plan a canal Panama", True), 
             ("hello", False), ("", True), ("a", True), ("ab", False), ("aa", True)]
    for s, exp in cases:
        r = is_palindrome(s)
        ok = r == exp
        print(f"   is_palindrome({s!r}) = {r}, expected {exp}  {'✓' if ok else '✗'}")
        passed += ok; failed += not ok
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} passed, {failed} failed")
    if failed == 0:
        print("🎉 HW 1 全 10 题完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
