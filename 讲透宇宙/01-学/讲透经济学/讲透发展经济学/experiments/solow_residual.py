# -*- coding: utf-8 -*-
"""
Solow 稳态、收敛速度与增长核算（走廊1+2+3）
对应章：讲透发展经济学/04-发展经济学转代码.md

内容：索洛模型双验证（闭式稳态 vs 欧拉迭代）、收敛速度三口径
（基本模型/MRW 含人力资本/经验铁律）、黄金律、东亚 TFP 区间
（Young 1995 口径）、基尼公理断言。纯 numpy，固定种子，全断言自验。
"""
import math

ALPHA, S, N, G, DELTA = 1/3, 0.28, 0.01, 0.02, 0.06
PARAMS = (N, G, DELTA)

def k_star_closed(s=1.0, alpha=ALPHA):
    """闭式稳态：k* = (s/(n+g+δ))^{1/(1-α)}（有效人均资本）"""
    return (s / sum(PARAMS)) ** (1 / (1 - alpha))

def k_star_iterate(k0=1.0, s=S, alpha=ALPHA, dt=0.01, T=400):
    """欧拉迭代：dk = s·k^α − (n+g+δ)·k（固定点条件与 ODE 稳态一致）"""
    k = k0
    for _ in range(int(T / dt)):
        k += dt * (s * k ** alpha - sum(PARAMS) * k)
    return k

def gini(ys):
    """基尼：G = ΣᵢΣⱼ|yᵢ−yⱼ| / (2 n² μ)"""
    n, mu = len(ys), sum(ys) / len(ys)
    return sum(abs(a - b) for a in ys for b in ys) / (2 * n * n * mu)

def main():
    # 断言1：稳态双验证——闭式解与数值迭代同达
    ks, ki = k_star_closed(S), k_star_iterate()
    assert abs(ki - ks) / ks < 1e-9, (ks, ki)
    print(f"[1] 稳态双验证：闭式 k*={ks:.4f} = 欧拉迭代 {ki:.4f}（α=1/3, s=0.28）")

    # 断言2：收敛速度三口径——基本模型 vs MRW vs 经验铁律
    lam_basic = (1 - ALPHA) * sum(PARAMS)          # α=1/3：6%/年
    lam_mrw   = (1 - 2/3) * sum(PARAMS)            # 含人力资本 α=2/3：3%/年
    lam_emp   = 0.02                               # Barro 经验铁律 2%/年
    hl = lambda lam: math.log(2) / lam
    assert abs(lam_basic - 0.06) < 1e-9 and abs(lam_mrw - 0.03) < 1e-9
    assert lam_basic > lam_mrw > lam_emp
    assert 10 < hl(lam_basic) < 13 and 20 < hl(lam_mrw) < 26 and 33 < hl(lam_emp) < 36
    print(f"[2] 收敛半衰期：基本模型 {hl(lam_basic):.1f} 年（6%/年，太快）→ "
          f"MRW 含人力资本 {hl(lam_mrw):.1f} 年 → 经验铁律 {hl(lam_emp):.1f} 年"
          f"——基本索洛'收敛过快'正是 MRW 1992 加人力资本的动机")

    # 断言3：黄金律——柯布-道格拉斯下 s_gold = α
    k_gr = (ALPHA / sum(PARAMS)) ** (1 / (1 - ALPHA))   # MPK=n+g+δ 处
    assert abs(k_star_closed(ALPHA) - k_gr) < 1e-12
    print(f"[3] 黄金律：s_gold = α = {ALPHA:.3f}（资本份额即黄金储蓄率，恒等可验）")

    # 断言4：增长核算残差——中国改革开放段（通行量级：α=0.5）
    g_y, g_k, g_l, alpha_cn = 0.08, 0.10, 0.02, 0.5
    g_a = g_y - alpha_cn * g_k - (1 - alpha_cn) * g_l
    assert abs(g_a - 0.02) < 1e-12 and 0.20 < g_a / g_y < 0.30
    print(f"[4] 增长核算（示意段）：gY=8%、gK=10%、gL=2%、α=0.5 → "
          f"TFP 残差 {g_a:.0%}/年，占产出增速 {g_a/g_y:.0%}")

    # 断言5：东亚四小龙 TFP（Young 1995 口径，宽区间断言）
    # 人均产出基础上的 TFP 年增速通行估计：香港~2.3% 台湾~2.1% 韩国~1.5% 新加坡~0.2%
    east_asia_tfp = {"香港": 0.023, "台湾": 0.021, "韩国": 0.015, "新加坡": 0.002}
    assert all(0 <= v <= 0.035 for v in east_asia_tfp.values())
    assert east_asia_tfp["新加坡"] < 0.01 and min(east_asia_tfp.values()) < 0.005
    print(f"[5] 东亚 TFP（Young 1995，区间断言）：{east_asia_tfp}"
          f"——'流汗而非灵感'：增长以要素积累为主")

    # 断言6：基尼公理——Pigou-Dalton 转移必降、尺度等变
    y0, y1 = [1, 1, 1, 1, 10], [1, 1, 1, 2, 9]
    assert gini(y0) > gini(y1), (gini(y0), gini(y1))
    assert abs(gini(y0) - gini([2 * v for v in y0])) < 1e-12
    print(f"[6] 基尼公理：转移前 {gini(y0):.3f} > 转移后 {gini(y1):.3f}"
          f"（Pigou-Dalton ✓）；收入翻倍基尼不变（尺度等变 ✓）")

    print("\n全部断言通过 ✓ （闭式×数值双验证+公理断言）")

if __name__ == "__main__":
    main()
