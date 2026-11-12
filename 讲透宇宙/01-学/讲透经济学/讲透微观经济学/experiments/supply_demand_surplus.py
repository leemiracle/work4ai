"""线性市场：均衡、消费者/生产者剩余、税负分担与无谓损失（断言自验）
对应《讲透微观经济学》00 章（板块 3）、03 章（均衡=z(p)=0 的最小版）、
04 章（走廊 1 均衡求解 + 走廊 2 剩余计算）。

模型：
    需求 P = a − b·Q          （a>0, b>0）
    供给 P = c + d·Q          （c>0, d>0，a>c 保证正均衡）
    均衡：Q* = (a−c)/(b+d)，P* = (a·d + c·b)/(b+d)
    消费者剩余 CS = ½(a−P*)Q*；生产者剩余 PS = ½(P*−c)Q*
    从量税 t（卖方税）：Q_t = (a−c−t)/(b+d)
        买方价 P_b = a − b·Q_t；卖方价 P_s = P_b − t
        买方税负份额 = d/(b+d)；卖方份额 = b/(b+d)
        无谓损失 DWL = ½·t·(Q* − Q_t)（线性情形的三角形）

断言（自验证）：
    (a) 数值求根均衡 = 解析均衡（相对误差 < 1e-10）
    (b) CS/PS 数值梯形积分 = 解析三角形（误差 < 1e-8）
    (c) 税后买方价涨幅 / t = d/(b+d)（税负分担结构公式，误差 < 1e-10）
    (d) DWL 凸性：DWL(t) ≈ ½·t²/(b+d)，且 DWL(2t)/DWL(t) = 4（线性精确二次）
"""
import numpy as np

# ── 校准（教学用参数） ──
A, B, C, D = 10.0, 1.0, 2.0, 1.0     # 需求 P=10−Q，供给 P=2+Q
T = 2.0                               # 从量税


def demand(q):
    return A - B * q


def supply(q):
    return C + D * q


def excess_z(q):
    """超额需求 z(q)=需求价−供给价；z=0 即均衡数量。"""
    return demand(q) - supply(q)


def bisect_root(f, lo, hi, tol=1e-14, itmax=200):
    """手写二分求根（单调函数上与 brentq 同效，自包含无 scipy 依赖）。"""
    flo = f(lo)
    for _ in range(itmax):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if abs(fm) < tol or (hi - lo) < tol:
            return mid
        if flo * fm <= 0:
            hi = mid
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi)


def main():
    # ── (a) 均衡：数值求根 vs 解析 ──
    q_star = bisect_root(excess_z, 0.0, (A - C) / B + 1.0)
    q_ana = (A - C) / (B + D)
    p_star = demand(q_star)
    p_ana = (A * D + C * B) / (B + D)
    eq_err = max(abs(q_star - q_ana) / q_ana, abs(p_star - p_ana) / p_ana)
    print(f"(a) 均衡：数值 Q*={q_star:.10f} P*={p_star:.10f}  "
          f"解析 Q*={q_ana:.10f} P*={p_ana:.10f}  相对误差={eq_err:.2e}   (断言 < 1e-10)")
    assert eq_err < 1e-10, "单调超额需求下二分求根必中解析均衡"

    # ── (b) 剩余：数值梯形积分 vs 解析三角形 ──
    grid = np.linspace(0.0, q_star, 2_000_001)
    cs_num = np.trapezoid(demand(grid) - p_star, grid)
    ps_num = np.trapezoid(p_star - supply(grid), grid)
    cs_ana = 0.5 * (A - p_star) * q_star
    ps_ana = 0.5 * (p_star - C) * q_star
    cs_err = abs(cs_num - cs_ana)
    ps_err = abs(ps_num - ps_ana)
    print(f"(b) CS：数值={cs_num:.8f} 解析={cs_ana:.8f} 误差={cs_err:.2e}  |  "
          f"PS：数值={ps_num:.8f} 解析={ps_ana:.8f} 误差={ps_err:.2e}   (断言各 < 1e-8)")
    assert cs_err < 1e-8 and ps_err < 1e-8, "线性剩余=三角形，数值积分应精确吻合"

    # ── (c) 税负分担：买方价涨幅/t = d/(b+d) ──
    q_tax = (A - C - T) / (B + D)
    p_buy = A - B * q_tax                     # 买方含税价
    p_sell = p_buy - T                        # 卖方净价
    buyer_share = (p_buy - p_star) / T
    buyer_share_ana = D / (B + D)
    c_err = abs(buyer_share - buyer_share_ana)
    print(f"(c) 税负分担：买方份额实测={buyer_share:.10f}  公式 d/(b+d)="
          f"{buyer_share_ana:.10f}  误差={c_err:.2e}   (断言 < 1e-10)")
    assert c_err < 1e-10, "买方税负份额应由 d/(b+d) 给出"
    assert p_buy > p_star > p_sell, "税收楔子：买方价升、卖方价降、夹住原均衡"

    # ── (d) 无谓损失：DWL(t)=½t²/(b+d)，精确二次（凸性） ──
    def dwl(t):
        q_t = (A - C - t) / (B + D)
        return 0.5 * t * (q_ana - q_t)

    ratio = dwl(2 * T) / dwl(T)
    d_err = abs(dwl(T) - 0.5 * T * T / (B + D))
    print(f"(d) DWL：DWL(t)={dwl(T):.6f}  解析 ½t²/(b+d)={0.5*T*T/(B+D):.6f}  "
          f"误差={d_err:.2e}  |  DWL(2t)/DWL(t)={ratio:.10f}   (断言误差<1e-12 且比值=4)")
    assert d_err < 1e-12 and abs(ratio - 4.0) < 1e-12, "线性市场 DWL 精确二次增长"
    # 附：总剩余守恒检查（税前 CS+PS = 税后 CS+PS+税入+DWL）
    q_t = (A - C - T) / (B + D)
    p_b = A - B * q_t
    cs_t = 0.5 * (A - p_b) * q_t
    ps_t = 0.5 * (p_b - T - C) * q_t
    revenue = T * q_t
    total_before = cs_ana + ps_ana
    total_after = cs_t + ps_t + revenue + dwl(T)
    assert abs(total_before - total_after) < 1e-10
    print("    附：税前总剩余 = 税后 CS+PS+税入+DWL（会计恒等 ✅）——"
          "税收不是损失，无谓损失才是损失。")

    print("\n全部断言通过 ✅  线性市场：均衡=z(p)的零点，剩余=积分，"
          "税负分担=斜率之比，DWL=精确二次凸性。")
    print("带走一句（00 章）：弹性小的一方承担更多税——"
          "'谁能跑谁少缴'是一切转嫁问题的第一直觉。")

if __name__ == "__main__":
    main()
