# -*- coding: utf-8 -*-
"""
logistic_bifurcation.py — 倍周期通向混沌：分岔级联 + Feigenbaum 普适常数数值探测

对应章：00-体系结构（✨美之时刻①：普适常数）/ 03-可构造与结构（§2.2 分岔结构刚性）/
       04-系统学转代码（走廊②：分岔/混沌走廊——"算得准"档）
GB/T 12020 系统学 · 家族层实验

运行：python logistic_bifurcation.py   （纯 numpy，无外部依赖）
"""

import numpy as np

R_TRANSIENT = 2000   # 瞬态扔掉步数（收敛到吸引子）
R_SAMPLE    = 800    # 采样步数（检测周期/混沌）
X0          = 0.4127 # 非平凡初值（避开不动点的对称轨道）


def orbit(r, n_transient=R_TRANSIENT, n_sample=R_SAMPLE, x0=X0):
    """迭代 logistic 映射，返回吸引子上的轨道样本。"""
    x = x0
    for _ in range(n_transient):
        x = r * x * (1.0 - x)
    out = np.empty(n_sample)
    for i in range(n_sample):
        x = r * x * (1.0 - x)
        out[i] = x
    return out


def detect_period(xs, tol=1e-6, max_p=64):
    """检测稳定周期：找最小 p 使轨道在容差内周期重复。返回 None 表示未检出（混沌/高周期）。"""
    for p in range(1, max_p + 1):
        if np.max(np.abs(xs[p:] - xs[:-p])) < tol:
            return p
    return None


def lyapunov_exponent(r, n=200_000, x0=X0):
    """李雅普诺夫指数：ln|f'(x_t)| 的时间平均（1D 映射标准算法）。"""
    x = x0
    s = 0.0
    for _ in range(2000):  # 瞬态
        x = r * x * (1.0 - x)
    for _ in range(n):
        s += np.log(abs(r * (1.0 - 2.0 * x)))
        x = r * x * (1.0 - x)
    return s / n


def locate_bifurcation(p_low, p_high, p_target, lo, hi, tol=1e-7):
    """二分定位周期从 p_target 倍增到 2*p_target 的分岔点 r*。

    注：分岔点附近收敛率 |f'|→1（临界慢化，critical slowing down），
    需要大瞬态才能把"慢收敛"与"真倍增"区分开——这正是 01 章方向四
    （tipping points 早期预警）的机制在本实验中的现场。
    """
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        per = detect_period(orbit(mid, n_transient=30_000))
        if per is not None and per <= p_target:
            lo = mid   # 仍是低周期
        else:
            hi = mid   # 已倍增/混沌
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def main():
    print("=" * 62)
    print("GB/T 12020 讲透系统学 · 实验：倍周期分岔通向混沌")
    print("映射: x_{t+1} = r * x_t * (1 - x_t)")
    print("=" * 62)

    # ── 1) 定点验证：三个 r 档位的行为 ─────────────────────────
    checks = [
        (2.8, 1, "周期1（不动点）"),
        (3.2, 2, "周期2（第一次倍周期）"),
        (3.5, 4, "周期4（第二次倍周期）"),
    ]
    print("\n[1] 档位行为（周期检测，容差 1e-6）")
    for r, expect, label in checks:
        p = detect_period(orbit(r))
        status = "OK" if p == expect else "FAIL"
        print(f"  r={r:4.2f}  检出周期={p:2d}  预期={expect}  [{status}] {label}")
        assert p == expect, f"r={r}: 周期 {p} != 预期 {expect}"

    lam4 = lyapunov_exponent(4.0)
    print(f"  r=4.00  李雅普诺夫指数 λ={lam4:.4f} (>0 → 混沌) [OK]")
    assert lam4 > 0, "r=4 应为混沌（λ>0）"
    # r=4 的解析值：λ = ln 2 ≈ 0.6931
    assert abs(lam4 - np.log(2)) < 1e-3, f"λ 应≈ln2≈0.6931，实测 {lam4:.4f}"
    print(f"         （解析值 ln2=0.6931 —— 精确命中，混沌也有定理）")

    # ── 2) 分岔级联 + Feigenbaum 普适比率 ─────────────────────
    print("\n[2] 分岔级联定位（二分搜索周期倍增点）")
    r1 = locate_bifurcation(1, 2, 1, 2.9, 3.1)     # 周期1 → 2
    r2 = locate_bifurcation(2, 4, 2, 3.3, 3.6)     # 周期2 → 4
    r3 = locate_bifurcation(4, 8, 4, 3.5, 3.6)     # 周期4 → 8
    r4 = locate_bifurcation(8, 16, 8, 3.55, 3.57)  # 周期8 → 16
    print(f"  r1(1→2)  = {r1:.6f}   （解析值 3.000000）")
    print(f"  r2(2→4)  = {r2:.6f}   （文献值 3.449490）")
    print(f"  r3(4→8)  = {r3:.6f}   （文献值 3.544090）")
    print(f"  r4(8→16) = {r4:.6f}   （文献值 3.564407）")
    print("  （偏差量级 = 临界慢化的足迹：越靠近分岔点收敛越慢，")
    print("    数值定位精度天然受瞬态步数限制——分岔点检测不到机器精度）")
    # 断言带按临界慢化标定：瞬态 30000 步 → 定位偏差 ~1e-3 量级
    assert abs(r1 - 3.0) < 1e-3, "r1 应为 3.0（±临界慢化带）"
    assert abs(r2 - 3.449490) < 1.5e-3, "r2 应≈3.4495"
    assert abs(r3 - 3.544090) < 1.5e-3, "r3 应≈3.5441"
    assert abs(r4 - 3.564407) < 1.5e-3, "r4 应≈3.5644"

    delta23 = (r2 - r1) / (r3 - r2)
    delta34 = (r3 - r2) / (r4 - r3)
    print(f"\n  Feigenbaum 比率 δ₂₃ = {delta23:.4f}")
    print(f"  Feigenbaum 比率 δ₃₄ = {delta34:.4f}")
    print(f"  （普适常数 δ = 4.6692016…——级联收敛中）")
    # 级联收敛慢：前几个分岔点的比率从 ~4.75 逼近 4.669；容差放宽到 [4.4, 4.9]
    assert 4.4 < delta23 < 4.9, f"δ₂₃ 超出收敛带: {delta23}"
    assert 4.4 < delta34 < 4.9, f"δ₃₄ 超出收敛带: {delta34}"

    # ── 3) 分岔图数据（供绘图/后续支层使用）───────────────────
    print("\n[3] 分岔图采样（r∈[2.5,4.0]×1000，输出末尾 5 行预览）")
    rs = np.linspace(2.5, 4.0, 1000)
    rows = []
    for r in rs:
        xs = orbit(r)
        rows.append((r, float(np.min(xs)), float(np.max(xs)), detect_period(xs)))
    for r, lo_, hi_, p in rows[::250]:
        tag = f"周期{p}" if p else "混沌/高周期"
        print(f"  r={r:5.3f}  x∈[{lo_:.4f},{hi_:.4f}]  {tag}")

    print("\n" + "=" * 62)
    print("[ALL ASSERTS PASSED] 倍周期级联 + Feigenbaum 普适性数值坐实。")
    print("带走一句（00 章）：换任何一维单峰映射重跑，δ 仍是 4.669——")
    print("普适性不是这条曲线的性质，是'分岔'这件事本身的性质。")
    print("=" * 62)


if __name__ == "__main__":
    main()
