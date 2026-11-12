"""
Peano 自然数的 Python 模拟（讲透Lean4数学 01 章配套）。
目的：让"2+2=4"的证明过程在 bash 里跑出来，建立直觉。
注意：这不是机械证明（用 Python），只是数值/结构验证。
真正的机械证明见 01-NaturalNumberGame讲透.md 的 NNG.lean（lake build 通过）。

跑法：
    cd 讲透Lean4数学
    python3 -u experiments/01_peano_python.py
"""
import sys
sys.setrecursionlimit(10000)  # Peano 表示的大数会爆递归（这是反直觉发现之一）


# === Peano 自然数（用 tuple 表示，zero=(), succ=(n,)）===
ZERO = ()  # 0
def S(n): return (n,)  # 后继

# 整数 → Peano
def peano(n: int):
    result = ZERO
    for _ in range(n):
        result = S(result)
    return result

# Peano → 整数（便于打印）
def unpeano(p) -> int:
    count = 0
    while p != ZERO:
        p = p[0]
        count += 1
    return count


# === 加法定义（严格按 A1 + A2，递归在左参数）===
def add(n, m):
    if n == ZERO:           # A1: 0 + m = m
        return m
    else:                   # A2: S(k) + m = S(k + m)
        k = n[0]
        return S(add(k, m))


# === 乘法定义（练习 1 答案）===
def mul(n, m):
    if n == ZERO:           # M1: 0 × m = 0
        return ZERO
    else:                   # M2: S(k) × m = (k × m) + m
        k = n[0]
        return add(mul(k, m), m)


# === 验证 L1：n + 0 = n（对所有 n in [0, max_n]）===
def verify_add_zero_r(max_n=20):
    for i in range(max_n + 1):
        n = peano(i)
        if unpeano(add(n, ZERO)) != i:
            return False, f"L1 失败 at n={i}"
    return True, f"L1 (n+0=n) 验证通过 (n ∈ [0, {max_n}])"


# === 验证 L3：n+m = m+n ===
def verify_add_comm(max_n=15):
    for i in range(max_n + 1):
        for j in range(max_n + 1):
            n, m = peano(i), peano(j)
            if unpeano(add(n, m)) != unpeano(add(m, n)):
                return False, f"L3 失败 at ({i},{j})"
    return True, f"L3 (n+m=m+n) 验证通过 (n,m ∈ [0,{max_n}]²)"


# === 验证 L4：(n+m)+k = n+(m+k) ===
def verify_add_assoc(max_n=10):
    for i in range(max_n + 1):
        for j in range(max_n + 1):
            for k in range(max_n + 1):
                n, m, kk = peano(i), peano(j), peano(k)
                lhs = unpeano(add(add(n, m), kk))
                rhs = unpeano(add(n, add(m, kk)))
                if lhs != rhs:
                    return False, f"L4 失败 at ({i},{j},{k})"
    return True, f"L4 ((n+m)+k=n+(m+k)) 验证通过 (n,m,k ∈ [0,{max_n}]³)"


# === 验证乘法 ===
def verify_mul(max_n=10):
    for i in range(max_n + 1):
        for j in range(max_n + 1):
            if unpeano(mul(peano(i), peano(j))) != i * j:
                return False, f"mul 失败 at {i}×{j}"
    return True, f"mul 验证通过 (n,m ∈ [0,{max_n}]²)"


def main():
    print("=" * 60)
    print("Natural Number Game: Peano 算术的 Python 验证")
    print("=" * 60)

    # [1] 2+2=4 的逐步展开
    print("\n[1] 2+2=4 的逐步展开（Peano 表示）：")
    two = S(S(ZERO))
    four = S(S(S(S(ZERO))))
    result = add(two, two)
    print(f"    two       = {two}")
    print(f"    two + two = {result}")
    print(f"    four      = {four}")
    print(f"    two+two == four?  {result == four}")
    print(f"    unpeano(two+two)  = {unpeano(result)}")

    # [2] 反直觉：Peano 表示的代价
    print("\n[2] 反直觉：Peano 表示的代价")
    print(f"    peano(100) 的 tuple 嵌套深度 = 100")
    big = peano(100)
    print(f"    unpeano(peano(100)) = {unpeano(big)}")
    try:
        # 试图构造 2000 层嵌套（Python 默认递归限制 1000）
        huge = peano(2000)
        print(f"    unpeano(peano(2000)) = {unpeano(huge)}")
    except RecursionError:
        print(f"    peano(2000) 触发 RecursionError → 必须设 sys.setrecursionlimit")
    print("    → 这就是为什么 Lean 用归纳类型而非运行时嵌套数据结构")

    # [3] 验证所有引理
    print("\n[3] 验证引理（数值采样，Lean 才是完备证明）：")
    for fn in [verify_add_zero_r, verify_add_comm, verify_add_assoc, verify_mul]:
        ok, msg = fn()
        status = "✓" if ok else "✗"
        print(f"    {status} {msg}")

    # [4] 反直觉：加法/乘法定义不对称
    print("\n[4] 反直觉：定义的不对称（递归在左参数）")
    print("    A1: 0 + m = m      ← 左单位元 = 定义（基础情形）")
    print("    L1: n + 0 = n      ← 右单位元 = 定理（需归纳）")
    print("    M1: 0 × m = 0      ← 左零元 = 定义")
    print("    MR: n × 0 = 0      ← 右零元 = 定理")
    print("    → 因为递归在左参数：左是基础情形（定义），右需要归纳")
    print("    → 如果改定义让递归在右参数，则左右互换（对称镜像）")

    # [5] 关键洞察
    print("\n[5] 关键洞察：")
    print("    - 2+2=4 是计算（按定义展开 4 步）")
    print("    - 交换律 n+m=m+n 是定理（需要对 n 归纳 + L1 + L2）")
    print("    - Python 只验证数值采样，Lean 验证所有自然数（归纳完备）")
    print("    - 你的 ai-os-dd 里的 induction 和这里的数学归纳是同一个 Lean tactic")

    print("\n" + "=" * 60)
    print("✓ Python 数值验证完成")
    print("  要 100% 机械证明 → 见 01-NaturalNumberGame讲透.md 的 NNG.lean")
    print("=" * 60)


if __name__ == "__main__":
    main()
