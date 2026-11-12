# -*- coding: utf-8 -*-
"""Leslie 矩阵人口投影:稳定人口定理与人口动量的数值实拍(00/03/04 章配套实验)。

模型(单性/女性人口,15 年一组,率恒定,封闭人口):
    n_{t+1} = L · n_t,   L = ⎡f0  f1  f2⎤
                          ⎢s0   0   0⎥ ,  n = (组0, 组1, 组2)
                          ⎣ 0  s1   0⎦
    f_i:组 i 每名女性一个周期产下的女婴数(母龄分组);s_i:组 i→组 i+1 存活率。

断言(00 章 §七反直觉 1 + 03 章 §三的数值版):
    A1  经验增长率 total(t+1)/total(t) 收敛到解析主特征值 λ1(特征多项式二分求根);
    A2  年龄结构收敛到解析稳定向量 v1=(λ1², s0·λ1, s0·s1)/‖·‖(Perron-Frobenius);
    A3  人口动量(Keyfitz 1971):生育率骤降到更替水平(净再生产率=1)后,
        总人口并未停止增长——之后 ≥4 个周期(60 年)始终高于初始水平
        (先增后带年龄结构回声振荡),最终停在新平台上。

⚠ 简化声明:单性人口、15 年粗分组、率恒定、无迁移——现实官方预测(队列要素法)
  把这些全部按年龄×性别×年份细化,再加迁移项(04 章 §3 的扩展练习)。

跑法: python 讲透统计学/讲透人口统计学/experiments/00_leslie.py
"""
import sys

# ── 参数(0-14 / 15-29 / 30-44 三组,女性人口)────────────────────────────
S0, S1 = 0.98, 0.97                     # 组间存活率:0→1 组、1→2 组
F_HIGH = (0.05, 0.90, 0.45)             # 高生育场景:净再生产率 > 1(增长型)
N0_SEED = (500.0, 300.0, 200.0)         # 任意非稳定初始结构(演示收敛过程)
T_CONV = 60                             # 收敛期数(次主特征值模比≈0.53,衰减充分)


def leslie(f0, f1, f2):
    """按参数组装 3×3 Leslie 矩阵(嵌套列表)。"""
    return ((f0, f1, f2), (S0, 0.0, 0.0), (0.0, S1, 0.0))


def project(L, n, steps):
    """n_{t+1} = L·n_t;返回轨迹 [n_0, n_1, ..., n_steps](每项为三元组)。"""
    (f0, f1, f2), (s0, _, _), (_, s1, _) = L
    hist = [tuple(n)]
    for _ in range(steps):
        n0, n1, n2 = hist[-1]
        hist.append((f0 * n0 + f1 * n1 + f2 * n2, s0 * n0, s1 * n1))
    return hist


def char_poly(lam, f0, f1, f2):
    """det(λI−L) = λ³ − f0λ² − s0·f1·λ − s0·s1·f2(Euler-Lotka 方程移项)。"""
    return lam ** 3 - f0 * lam ** 2 - S0 * f1 * lam - S0 * S1 * f2


def dominant_eigenvalue(f0, f1, f2):
    """特征多项式的唯一正根:Leslie 矩阵不可约 ⇒ Perron-Frobenius 唯一正特征值。
    g(λ) 在正根右侧恒正 ⇒ 二分法可靠收敛。"""
    g = lambda lam: char_poly(lam, f0, f1, f2)
    lo, hi = 0.0, 1.0 + f0 + S0 * f1 + S0 * S1 * f2    # g(lo)<0, g(hi)>0
    assert g(lo) < 0 < g(hi), "二分区间失效:检查参数正性"
    for _ in range(200):                                # 200 次 → 双精度收敛
        mid = (lo + hi) / 2.0
        if g(mid) < 0.0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def stable_shares(lam):
    """主特征向量 v1=(λ², s0·λ, s0·s1) 归一化为年龄份额。"""
    v = (lam * lam, S0 * lam, S0 * S1)
    z = sum(v)
    return tuple(x / z for x in v)


def net_reproduction(f0, f1, f2):
    """净再生产率 NRR = f0 + s0·f1 + s0·s1·f2(一名新生女婴一生预期生多少女婴)。"""
    return f0 + S0 * f1 + S0 * S1 * f2


def main():
    try:  # Windows 控制台中文输出保险(纯标准库)
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    print("=" * 70)
    print("Leslie 矩阵人口投影:三年龄组 × 15 年/组(单性人口,率恒定)")
    print("=" * 70)

    # ── 第一幕:高生育矩阵的收敛(稳定人口定理)──────────────────────────
    lam1 = dominant_eigenvalue(*F_HIGH)
    v_star = stable_shares(lam1)
    nrr_high = net_reproduction(*F_HIGH)
    print(f"\n高生育场景 F={F_HIGH}, s=({S0}, {S1})")
    print(f"净再生产率 NRR = {nrr_high:.6f}(>1 ⇒ 增长型)")
    print(f"解析主特征值 λ1 = {lam1:.6f} / 15年(特征多项式二分求根)")
    print(f"解析稳定年龄结构 = {tuple(round(x, 4) for x in v_star)}")

    hist = project(leslie(*F_HIGH), N0_SEED, T_CONV)
    print(f"\n{'周期':>4} {'组0':>10} {'组1':>10} {'组2':>10} "
          f"{'总数':>10} {'周期增长率':>10}")
    rows = list(range(0, 5)) + [T_CONV - 1, T_CONV]
    for t in rows:
        n = hist[t]
        g = hist[t][0] + hist[t][1] + hist[t][2]
        g_prev = sum(hist[t - 1]) if t else None
        rate = f"{g / g_prev:.6f}" if g_prev else "     —"
        print(f"{t:>4} {n[0]:>10.1f} {n[1]:>10.1f} {n[2]:>10.1f} "
              f"{g:>10.1f} {rate:>10}")

    total_t, total_prev = sum(hist[T_CONV]), sum(hist[T_CONV - 1])
    lambda_emp = total_t / total_prev
    shares_emp = tuple(x / total_t for x in hist[T_CONV])
    print(f"\n经验增长率(第 {T_CONV} 周期)= {lambda_emp:.6f} vs 解析 λ1 = {lam1:.6f}")
    print(f"经验年龄结构          = {tuple(round(x, 4) for x in shares_emp)}")

    # 断言 A1:增长率收敛到主特征值(Perron-Frobenius 的数值版)
    err1 = abs(lambda_emp - lam1) / lam1
    assert err1 < 1e-9, f"增长率未收敛到 λ1(相对误差 {err1:.2e})"
    # 断言 A2:年龄结构收敛到解析稳定向量
    err2 = max(abs(a - b) for a, b in zip(shares_emp, v_star))
    assert err2 < 1e-9, f"年龄结构未收敛到稳定向量(最大偏差 {err2:.2e})"
    print(f"断言 A1/A2 通过:相对误差 {err1:.2e},结构偏差 {err2:.2e}"
          f" —— 稳定人口定理实拍 ✓")

    # ── 第二幕:人口动量(生育率骤降到更替水平)─────────────────────────
    print("\n" + "=" * 70)
    print("人口动量(Keyfitz 1971):生育率骤降到更替水平后,人口仍增长?")
    print("=" * 70)
    scale = 1.0 / nrr_high
    F_REP = tuple(f * scale for f in F_HIGH)     # 等比缩放 ⇒ NRR 恰为 1
    assert abs(net_reproduction(*F_REP) - 1.0) < 1e-12, "更替水平构造失败"
    print(f"更替场景 F = {tuple(round(f, 4) for f in F_REP)}(NRR = 1,长期 λ→1)")

    start = hist[-1]                              # 第一幕收敛后的「年轻、增长型」结构
    base = sum(start)
    start = tuple(x / base for x in start)        # 归一化:初始总人口 = 1
    mom = project(leslie(*F_REP), start, 8)
    print(f"\n{'年数':>6} {'总人口(初始=1)':>14} {'周期增长率':>10}")
    for t, n in enumerate(mom):
        tot = sum(n)
        rate = tot / sum(mom[t - 1]) if t else None
        print(f"{t * 15:>6} {tot:>14.4f} {f'{rate:.4f}' if rate else '     —':>10}")

    totals = [sum(n) for n in mom]
    print(f"\n读数:生育率骤降到更替水平,总人口并未停止增长——")
    print(f"      60 年内始终高于初始,峰值 {max(totals):.4f}(第 "
          f"{totals.index(max(totals)) * 15} 年),")
    print(f"      随后带年龄结构回声振荡,停驻在 ≈{totals[-1]:.3f} 的新平台上——育龄存量的惯性。")

    # 断言 A3:动量——更替切换后前 4 个周期(60 年)总人口均高于初始
    assert min(totals[1:5]) > 1.0, "人口动量未显现:更替切换后应保持高于初始"
    assert max(totals[1:]) > 1.03, "动量峰值过低,请检查初始结构"
    print("断言 A3 通过:更替水平切换后 60 年人口仍高于初始(00 章反直觉 1 的数值版)✓")


if __name__ == "__main__":
    main()
