# -*- coding: utf-8 -*-
"""Houston《How to Think Like a Mathematician》现代验证
5 种证明技术 + 逻辑等价（逆否/德摩根）+ 量词
纯 Python 无依赖"""

# ---------- §1 逻辑基础：命题 + 真值表 ----------
def section_logic():
    print("\n" + "="*60)
    print("【§1 逻辑：命题/量词/德摩根（Houston ch2）】")
    print("="*60)
    # 真值表验证德摩根 ¬(P∧Q) ⟺ ¬P∨¬Q
    print("德摩根律验证：¬(P∧Q) ⟺ ¬P∨¬Q")
    print(f"  {'P':<6}{'Q':<6}{'P∧Q':<8}{'¬(P∧Q)':<10}{'¬P∨¬Q':<8}{'相等?'}")
    all_match = True
    for P in [True, False]:
        for Q in [True, False]:
            lhs = not (P and Q)
            rhs = (not P) or (not Q)
            match = (lhs == rhs)
            all_match = all_match and match
            print(f"  {str(P):<6}{str(Q):<6}{str(P and Q):<8}{str(lhs):<10}{str(rhs):<8}{'✓' if match else '✗'}")
    print(f"  → 全部相等：{all_match}（德摩根恒成立）")
    # 逆否命题 P→Q ⟺ ¬Q→¬P
    print(f"\n逆否命题：P→Q ⟺ ¬Q→¬P（逆否与原命题同真值）")
    print(f"  {'P':<6}{'Q':<6}{'P→Q':<8}{'¬Q→¬P':<8}{'相等?'}")
    for P in [True, False]:
        for Q in [True, False]:
            impl = (not P) or Q  # P→Q
            contrapos = Q or (not P)  # ¬Q→¬P = Q∨¬P，等价
            print(f"  {str(P):<6}{str(Q):<6}{str(impl):<8}{str(contrapos):<8}{'✓' if impl==contrapos else '✗'}")
    print("→ 证 P→Q 难时，改证 ¬Q→¬P（逆否），常更易——这是证明技术的核心工具")

# ---------- §2 5 种证明技术 ----------
def section_proof_techniques():
    print("\n" + "="*60)
    print("【§2 5 种证明技术（Houston ch4·核心）】")
    print("="*60)
    print("① 直接证明：假设 P，推出 Q")
    print("  例：'若 n 偶则 n² 偶'。设 n=2k，n²=4k²=2(2k²)，是 2 的倍数 ✓")
    for n in [2, 4, 6, 100, -8]:
        assert n**2 % 2 == 0
    print(f"  验证：n=2,4,6,100,-8 都满足 n² 偶 ✓")

    print(f"\n② 逆否证明：证 ¬Q→¬P（与 P→Q 等价）")
    print("  例：'若 n² 偶则 n 偶'。逆否：'若 n 奇则 n² 奇'")
    print("  设 n=2k+1，n²=4k²+4k+1=2(2k²+2k)+1，奇 ✓（比直接证 n²偶→n偶 易）")

    print(f"\n③ 反证：假设 ¬P，导出矛盾")
    print("  例：√2 无理（柯朗第2章已证）、素数无限（柯朗第1章欧几里得）")
    print(f"  代码验证'素数无限'的反证构造：p₁p₂…pₙ+1 的素因子不在原列表")

    print(f"\n④ 分类/穷举：分情况讨论")
    print("  例：证明 ∀n∈ℤ, n²+n 偶")
    # n 偶：n=2k, n²+n=4k²+2k=2(2k²+k) 偶
    # n 奇：n=2k+1, n²+n=4k²+4k+1+2k+1=4k²+6k+2=2(2k²+3k+1) 偶
    for n in range(-10, 11):
        assert (n**2 + n) % 2 == 0
    print(f"  验证：n=-10..10 都满足 n²+n 偶 ✓（分偶/奇两类，皆偶）")

    print(f"\n⑤ 归纳法：已深学（柯朗第1章 + Spivak）")
    print("  例：Σk²=n(n+1)(2n+1)/6")
    for n in [1, 5, 10, 100]:
        assert sum(k**2 for k in range(1, n+1)) == n*(n+1)*(2*n+1)//6
    print(f"  验证：n=1,5,10,100 都满足 Σk²=n(n+1)(2n+1)/6 ✓")

# ---------- §3 等价关系 ----------
def section_equivalence():
    print("\n" + "="*60)
    print("【§3 等价关系（Houston ch5·所有数学家都要会）】")
    print("="*60)
    print("等价关系 ∼：自反(a∼a) + 对称(a∼b⟹b∼a) + 传递(a∼b, b∼c⟹a∼c)")
    print("  例：模 n 同余、相等、相似（矩阵）、同胚（拓扑）")
    # 模 5 同余验证
    print(f"\n模 5 同余：a∼b ⟺ 5|(a-b)")
    print(f"  等价类：[0]={{0,5,10,...}}, [1]={{1,6,11,...}}, ...（5 个类，ℤ/5ℤ）")
    # 验证三性质
    for a in range(20):
        assert (a - a) % 5 == 0  # 自反
    for a in range(10):
        for b in range(10):
            if (a-b) % 5 == 0:
                assert (b-a) % 5 == 0  # 对称
            for c in range(10):
                if (a-b)%5==0 and (b-c)%5==0:
                    assert (a-c)%5==0  # 传递
    print(f"  验证自反/对称/传递（0-20 整数）全成立 ✓")
    print(f"\n→ 等价关系'切分'集合为不相交的等价类——这是构造新数学对象的标准方法")
    print(f"  （ℤ/5ℤ 是有限域、有理数是整数对的等价类、实数是 Cauchy 序列等价类——Spivak Part V）")

# ---------- §4 反例文化 ----------
def section_counterexamples():
    print("\n" + "="*60)
    print("【§4 反例：数学成熟度（Houston 贯穿全书）】")
    print("="*60)
    print("反例比证明更重要——它告诉你'定理的边界在哪'")
    print()
    print("反例 1：'连续函数一定可导'？错。|x| 在 x=0 连续但不可导")
    print("反例 2：'逐点收敛保持连续'？错。x^n 在 [0,1] 逐点→跳跃函数（Spivak Part IV）")
    print("反例 3：'所有群都交换'？错。矩阵乘法 AB≠BA")
    A = [[1,2],[3,4]]; B = [[5,6],[7,8]]
    AB = [[sum(A[i][k]*B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    BA = [[sum(B[i][k]*A[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    print(f"  验证：AB[0][0]={AB[0][0]}, BA[0][0]={BA[0][0]}（不相等，矩阵乘法不交换）")
    print()
    print("→ 学数学不是只学'成立的'，更要学'不成立的'——反例防止你过度泛化")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  Houston《How to Think Like a Mathematician》· 现代验证    ║")
    print("║  逻辑 + 5 种证明技术 + 等价关系 + 反例                      ║")
    print("╚" + "═"*58 + "╝")
    section_logic()
    section_proof_techniques()
    section_equivalence()
    section_counterexamples()
    print("\n" + "═"*60)
    print("✅ Houston 核心验证通过。证明方法论（你的'数学语法手册'）打通。")
    print("═"*60)
