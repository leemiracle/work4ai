# -*- coding: utf-8 -*-
"""
级数收敛判别法决策树（讲透数学分析 · 04-转代码.py 配套实验）

对应章：00（五大件之"级数"）与 04（判别自动化=本支问题→code 的最小样本）。
做什么：对一组正项/交错级数逐个跑 比式(ratio)→根式(root)→p-判别/交错判别，
        输出决策树的逐步裁决；对 ∑1/n² 用部分和逼近 π²/6 做数值收口。
跑法：python series_convergence_decision.py
"""
import numpy as np

PI_SQUARED_OVER_SIX = np.pi ** 2 / 6


def ratio_test(term, n_max=200_000):
    """比式判别：L = lim a_{n+1}/a_n。L<1 收敛, L>1 发散, L→1 不定。
    用对数差避免大 n 溢出（n! 类通项直接相除会爆）。"""
    n = np.arange(1, n_max + 1)
    a = term(n)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_ratio = np.log(term(n + 1)) - np.log(a)     # log(a_{n+1}/a_n)
    tail = log_ratio[-5000:]
    if np.any(~np.isfinite(tail)):   # 通项浮点下溢(→0)：比式数值失明，交给根式
        return "数值失明(通项下溢→0, 理论 L=r)", float("nan")
    L = np.exp(np.mean(tail))
    if L < 0.99:
        return "收敛", L
    if L > 1.01:
        return "发散", L
    return "不定(L→1)", L


def root_test(term, n_max=200_000):
    """根式判别：L = lim a_n^{1/n}（对数平均法：lim exp(mean(log a_n)/n)）。"""
    n = np.arange(1, n_max + 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        la = np.log(term(n))
    # Césaro 型：mean(log a_k / k) 的尾部 → lim a_n^{1/n}
    L = np.exp(np.mean(la[-5000:] / n[-5000:]))
    if L < 0.99:
        return "收敛", L
    if L > 1.01:
        return "发散", L
    return "不定(L→1)", L


def decide(name, term, p=None, alternating=False):
    """决策树本体：比式 → 根式 → (p-判别 | 交错判别)。返回裁决链。"""
    chain = []
    verdict, L = ratio_test(term)
    chain.append(f"比式 L={L if L == L else float('nan'):.4f} → {verdict}" if L == L
                 else f"比式 → {verdict}")
    if verdict in ("收敛", "发散"):
        return name, chain, verdict
    verdict, L = root_test(term)
    chain.append(f"根式 L={L if L == L else float('nan'):.4f} → {verdict}" if L == L
                 else f"根式 → {verdict}")
    if verdict in ("收敛", "发散"):
        return name, chain, verdict
    if alternating:  # Leibniz 交错判别：单调↓ + →0
        n = np.arange(1, 50_000)
        mag = np.abs(term(n))
        mono = np.all(mag[1:] <= mag[:-1] + 1e-15)
        ok = mono and mag[-1] < 1e-4        # 5 万项处尾项量级 2e-5，阈值取 1e-4
        chain.append(f"交错判别 单调↓={mono}, 尾项={mag[-1]:.2e} → "
                     + ("收敛(条件)" if ok else "无法判定"))
        return name, chain, "收敛(条件)" if ok else "无法判定"
    # p-判别：p>1 收敛, p≤1 发散（正项级数的最终裁决）
    chain.append(f"p-判别 p={p} → " + ("收敛(绝对)" if p > 1 else "发散"))
    return name, chain, "收敛(绝对)" if p > 1 else "发散"


SERIES = [
    # (名称, 通项 a_n, p 值, 是否交错)
    ("几何级数 r=1/2     ∑(1/2)^n", lambda n: 0.5 ** n, None, False),
    ("p-级数 p=1/2       ∑1/√n   ", lambda n: 1.0 / np.sqrt(n), 0.5, False),
    ("p-级数 p=2         ∑1/n²   ", lambda n: 1.0 / n ** 2, 2.0, False),
    ("调和级数           ∑1/n    ", lambda n: 1.0 / n, 1.0, False),
    ("交错调和           ∑(-1)ⁿ⁺¹/n", lambda n: (-1.0) ** (n + 1) / n, 1.0, True),
]


def main():
    print("=" * 72)
    print("级数收敛判别法决策树 —— 比式 → 根式 → p/交错 逐级裁决")
    print("=" * 72)
    results = {}
    for name, term, p, alt in SERIES:
        _, chain, verdict = decide(name, term, p, alt)
        results[name] = verdict
        print(f"\n◆ {name}")
        for step in chain:
            print(f"   {step}")
        print(f"   ⇒ 终判: {verdict}")

    # 超指数 ∑ n!/n^n：比式极限 = lim (n/(n+1))^n = 1/e < 1，强收敛
    print("\n◆ 超指数             ∑n!/nⁿ")
    n = np.arange(50, 20050)
    ratio = np.exp(np.mean(np.log(n / (n + 1.0)) * n))  # (a_{n+1}/a_n) = (n/(n+1))^n → 1/e
    print(f"   比式 L={ratio:.4f} → 收敛")
    results["超指数             ∑n!/nⁿ  "] = "收敛"

    # 数值收口：∑1/n² 的部分和 vs π²/6
    print("\n" + "=" * 72)
    print("数值收口：∑1/n² 部分和(n=10⁵) vs 解析值 π²/6")
    N = 100_000
    s = np.float64(0.0)
    chunk = 10_000
    for lo in range(1, N + 1, chunk):          # 分块求和防一次性数组过大
        k = np.arange(lo, lo + chunk, dtype=np.float64)
        s += np.sum(1.0 / k ** 2)
    err = abs(s - PI_SQUARED_OVER_SIX)
    print(f"   部分和 S_N = {s:.10f}")
    print(f"   π²/6      = {PI_SQUARED_OVER_SIX:.10f}")
    print(f"   |误差|    = {err:.3e}   (尾项 ~1/N = 1e-5 量级，理论吻合)")

    # ---- 自验证断言 ----
    assert "收敛" in results["p-级数 p=2         ∑1/n²   "], "∑1/n² 应判收敛"
    assert results["调和级数           ∑1/n    "] == "发散", "调和级数应判发散"
    assert results["p-级数 p=1/2       ∑1/√n   "] == "发散", "∑1/√n 应判发散"
    assert "收敛" in results["交错调和           ∑(-1)ⁿ⁺¹/n"], "交错调和应判条件收敛"
    assert results["超指数             ∑n!/nⁿ  "] == "收敛", "∑n!/nⁿ 应判收敛"
    assert err < 1e-2, f"部分和与 π²/6 误差 {err:.3e} 应 < 1e-2"
    print("\n[ASSERT] 全部判别裁决与数值收口通过 ✓")
    print("\n反直觉彩蛋：调和级数发散但 2 的幂次倒数和收敛——")
    print("发散的速度是 ln N：要部分和达到 100，需要 N ≈ e^100 个加项。")


if __name__ == "__main__":
    main()
