# -*- coding: utf-8 -*-
"""
simulation_kernels.py — 仿真科学技术家族双标本：蒙特卡洛走廊 + 离散事件走廊

对应章：04-仿真科学技术转代码（走廊①蒙特卡洛/走廊②离散事件——本章代码骨架的原样实现）；
       03-可构造与结构（✨美之时刻②维数免疫的 2D 现场 / ✨美之时刻③ Little 定律不变量现场）；
       00-体系结构（发源一：乌拉姆/冯诺依曼蒙特卡洛 1946；发源三：离散事件/排队）。
GB/T 13745 41315 仿真科学技术 · 家族层实验。纯标准库，无外部依赖。

运行：python simulation_kernels.py   （自验证：全部 assert 通过 → exit 0）
"""

import heapq
import math
import random
from collections import deque

PI = math.pi
SEED = 20260907  # 建族日


# ─────────────────────────────────────────────────────────────────
# 走廊①：蒙特卡洛 π 估计（发源一的最小标本）
# ─────────────────────────────────────────────────────────────────

def monte_carlo_pi(n, rng):
    """朴素蒙特卡洛：往 [0,1]^2 均匀撒 n 点，π̂ = 4×落入单位圆盘的比例。

    误差 O(1/√N)（中心极限定理背书），与维数无关——03 章"维数免疫"。
    返回 (pi_hat, inside_count)。
    """
    inside = 0
    for _ in range(n):
        x = rng.random() - 0.5
        y = rng.random() - 0.5
        if x * x + y * y <= 0.25:
            inside += 1
    return 4.0 * inside / n, inside


def pi_variance_experiment(n_reps=400, n_pts=1000):
    """方差缩减现场（04 章工程师落点 2："买样本不如买方差缩减"）。

    对照两种估计量的跨重复方差：
      朴素：f = 圆盘示性函数的均值
      控制变量：g = 到圆心距离平方（E[g]=1/6，与 f 强负相关），
                校正估计 f - b·(g - E[g])，b 为样本回归斜率
    同样本量下方差显著下降 → 达到同精度需要的样本更少。
    """
    rng = random.Random(SEED + 1)
    f_means, g_means = [], []
    for _ in range(n_reps):
        f_sum = g_sum = 0.0
        for _ in range(n_pts):
            x = rng.random() - 0.5
            y = rng.random() - 0.5
            r2 = x * x + y * y
            f_sum += 1.0 if r2 <= 0.25 else 0.0
            g_sum += r2
        f_means.append(f_sum / n_pts)
        g_means.append(g_sum / n_pts)

    def var(xs):
        m = sum(xs) / len(xs)
        return sum((v - m) ** 2 for v in xs) / (len(xs) - 1)

    def cov(xs, ys):
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (len(xs) - 1)

    b = cov(f_means, g_means) / var(g_means)          # 控制变量斜率
    cv = [f - b * (g - 1.0 / 6.0) for f, g in zip(f_means, g_means)]
    var_naive, var_cv = var(f_means), var(cv)
    pi_cv = 4.0 * sum(cv) / len(cv)
    return var_naive, var_cv, b, pi_cv


# ─────────────────────────────────────────────────────────────────
# 走廊②：M/M/1 离散事件仿真（发源三的最小标本，事件调度世界观）
# ─────────────────────────────────────────────────────────────────

def mm1(lam, mu, n_departures, seed):
    """事件调度世界观的 M/M/1：heapq 事件表 + 时钟跳到下一事件。

    到达 Poisson(λ)，服务 Exp(μ)，单服务台 FIFO。
    返回统计量：利用率 / 时间平均队长 L / 平均逗留 W / 到达率 λ̂。
    理论锚（ρ=λ/μ）：利用率=ρ，L=ρ/(1-ρ)，W=1/(μ-λ)，Little：L=λW。
    """
    rng = random.Random(seed)
    heap = [(rng.expovariate(lam), 1)]        # 事件表：(时间戳, 类型) 1=到达 2=离开
    prev = 0.0
    busy = False
    n_sys = 0
    waiting = deque()                          # 排队者的到达时刻（FIFO）
    arr_cur = 0.0                              # 正在被服务者的到达时刻
    area_L = 0.0                               # ∫N(t)dt（Little 的 L）
    area_busy = 0.0                            # ∫busy(t)dt（利用率分子）
    n_arr = n_dep = 0
    sum_W = 0.0

    while n_dep < n_departures:
        t, ev = heapq.heappop(heap)            # 时钟直接跳到下一事件（✨时间跳变）
        dt = t - prev
        area_L += n_sys * dt
        area_busy += dt if busy else 0.0
        prev = t
        if ev == 1:                            # 到达
            n_arr += 1
            n_sys += 1
            if busy:
                waiting.append(t)
            else:
                busy = True
                arr_cur = t
                heapq.heappush(heap, (t + rng.expovariate(mu), 2))
            heapq.heappush(heap, (t + rng.expovariate(lam), 1))
        else:                                  # 离开
            n_dep += 1
            sum_W += t - arr_cur
            n_sys -= 1
            if waiting:
                arr_cur = waiting.popleft()
                heapq.heappush(heap, (t + rng.expovariate(mu), 2))
            else:
                busy = False

    T = t
    return {
        "rho": lam / mu,
        "util": area_busy / T,                 # 模拟利用率
        "L": area_L / T,                       # 时间平均队长
        "W": sum_W / n_dep,                    # 平均逗留时间
        "lam_hat": n_arr / T,                  # 模拟到达率
        "T": T, "n_dep": n_dep,
    }


# ─────────────────────────────────────────────────────────────────
# 主流程：三段自验证
# ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 64)
    print("GB/T 41315 讲透仿真科学技术 · 家族实验：蒙特卡洛 + M/M/1 离散事件")
    print("仿真=用可操纵的替身系统换知识——在数字世界里便宜地犯错")
    print("=" * 64)

    # ── 1) 蒙特卡洛 π：误差 < 1e-2（任务书公差）────────────────
    print("\n[1] 蒙特卡洛 π 估计（N=400,000，CLT 保证误差 O(1/√N)）")
    rng = random.Random(SEED)
    pi_hat, inside = monte_carlo_pi(400_000, rng)
    err = abs(pi_hat - PI)
    print(f"  π̂ = {pi_hat:.5f}   真值 π = {PI:.5f}   |误差| = {err:.5f}")
    assert err < 1e-2, f"π 估计误差 {err:.5f} 超出 1e-2"
    print(f"  [OK] 落盘 {inside} 点，|误差| < 1e-2 —— 统计推理档的自带 ±")

    # ── 2) 方差缩减：同样本量，方差砍半（04 章第一定律）─────────
    print("\n[2] 方差缩减（控制变量 g=到圆心距离平方，E[g]=1/6，400 重复×1000 点）")
    var_naive, var_cv, b, pi_cv = pi_variance_experiment()
    ratio = var_cv / var_naive
    print(f"  朴素估计量方差     = {var_naive:.3e}")
    print(f"  控制变量估计量方差 = {var_cv:.3e}   （斜率 b = {b:.3f}）")
    print(f"  方差比 = {ratio:.3f}  → 同精度所需样本约为朴素版的 {ratio:.0%}")
    print(f"  控制变量 π̂ = {pi_cv:.5f}（|误差| = {abs(pi_cv - PI):.5f}）")
    assert var_cv < var_naive, "控制变量未能降方差（理论强负相关，不应发生）"
    assert abs(pi_cv - PI) < 2e-2, "控制变量估计偏离公差"
    print("  [OK] 买样本不如买方差缩减——蒙特卡洛性能工程第一定律现场")

    # ── 3) M/M/1：模拟利用率 vs 理论 ρ（误差 < 5%）────────────
    print("\n[3] M/M/1 离散事件仿真（λ=0.7, μ=1.0, 200,000 完成事件）")
    r = mm1(lam=0.7, mu=1.0, n_departures=200_000, seed=SEED)
    rho, util = r["rho"], r["util"]
    util_err = abs(util - rho) / rho
    print(f"  模拟利用率 = {util:.4f}   理论 ρ = {rho:.2f}   相对误差 = {util_err:.2%}")
    assert util_err < 0.05, f"利用率误差 {util_err:.2%} 超出 5%"

    L, W, lam_hat = r["L"], r["W"], r["lam_hat"]
    L_theory, W_theory = rho / (1 - rho), 1.0 / (1.0 - 0.7)
    little_lhs, little_rhs = L, lam_hat * W
    little_err = abs(little_lhs - little_rhs) / L
    print(f"  时间平均队长 L = {L:.4f}   理论 ρ/(1-ρ) = {L_theory:.4f}"
          f"   偏差 {abs(L - L_theory) / L_theory:.2%}")
    print(f"  平均逗留   W = {W:.4f}   理论 1/(μ-λ) = {W_theory:.4f}"
          f"   偏差 {abs(W - W_theory) / W_theory:.2%}")
    print(f"  Little 定律：L = {little_lhs:.4f}  vs  λ̂·W = {little_rhs:.4f}"
          f"   偏差 {little_err:.2%}（无分布假设的守恒律）")
    assert abs(L - L_theory) / L_theory < 0.10, "队长 L 偏离理论值超 10%"
    assert abs(W - W_theory) / W_theory < 0.10, "逗留 W 偏离理论值超 10%"
    assert little_err < 0.05, f"Little 定律偏差 {little_err:.2%} 超出 5%"
    print("  [OK] 不变量对答案：Little 定律免费自查通过（03 章 ✨美之时刻③）")

    # ── 4) 利用率→1，延迟爆炸（00 章反直觉 3 的现场）──────────
    print("\n[4] ρ 扫描：利用率逼近 1，队长非线性爆炸（各 60,000 完成事件）")
    Ls = {}
    for rho_t in (0.5, 0.7, 0.9):
        rr = mm1(lam=rho_t, mu=1.0, n_departures=60_000, seed=SEED + int(rho_t * 10))
        Ls[rho_t] = rr["L"]
        print(f"  ρ={rho_t:.1f}:  模拟 L = {rr['L']:.3f}   理论 = {rho_t / (1 - rho_t):.3f}")
    assert Ls[0.9] > Ls[0.7] > Ls[0.5], "队长未随 ρ 单调上升"
    assert Ls[0.9] / Ls[0.5] > 3.0, "ρ=0.9 vs 0.5 的队长比未体现非线性放大"
    print("  [OK] ρ 0.5→0.9 只升 0.4，队长翻数倍——真产线试不起，替身随便试")

    print("\n" + "=" * 64)
    print("[ALL ASSERTS PASSED] 蒙特卡洛走廊 + 离散事件走廊双标本自验证通过。")
    print("带走一句（00 章）：随机性与事件跳变，一个是统计结构的钥匙，")
    print("一个是离散结构的钥匙——两条走廊合起来就是仿真学科的两只手。")
    print("=" * 64)


if __name__ == "__main__":
    main()
