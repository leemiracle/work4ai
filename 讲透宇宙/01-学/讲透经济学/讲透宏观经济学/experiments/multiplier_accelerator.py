"""萨缪尔森乘数-加速数模型（1939）：内生周期与稳定性分区（断言自验）
对应《讲透宏观经济学》00 章（短期段）、02 章 §5（恒等式+行为方程的最小组）、
04 章（走廊 2：波动系统模拟——Blanchard-Kahn 式判定的最小可跑版）。

模型：
    C_t = c·Y_{t−1}                    （消费函数：乘数）
    I_t = v·(Y_{t−1} − Y_{t−2})        （加速数：投资对产出变化的反应）
    Y_t = C_t + I_t + G                （收入恒等式）
联立 ⟹ 二阶线性差分方程：Y_t = (c+v)·Y_{t−1} − v·Y_{t−2} + G
特征方程：x² − (c+v)x + v = 0
Jury 稳定性判据（二阶）：稳定 ⟺ v < 1 且 c < 1
判别式 Δ=(c+v)²−4v：Δ<0 复根（振荡），Δ≥0 实根（单调/过阻尼）

断言（自验证）——判据与模拟行为互证，四分区各一组：
    (a) c=0.60, v=0.50：复根且稳定 ⟹ 振荡收敛（末期缺口 < 期初的 5%）
    (b) c=0.60, v=1.50：复根且不稳定 ⟹ 振荡发散（包络按 |x| 增长）
    (c) c=0.90, v=0.05：实根且稳定 ⟹ 单调收敛（无超调）
    (d) c=0.85, v=2.00：Δ≥0 且 v>1 ⟹ 单调发散（指数增长）
    (e) 增长包络校验：|特征根|^t 与模拟包络同数量级（复根情形 (b)）
"""
import numpy as np

G_BAR = 1.0            # 恒定政府支出（单位化）
T_SIM = 120            # 模拟期数


def classify(c, v):
    """返回 (稳定?, 振荡?, 模最大值)。Jury 判据 + 判别式。"""
    coeff = [1.0, -(c + v), v]                     # x² − (c+v)x + v
    roots = np.roots(coeff)
    stable = (v < 1.0) and (c < 1.0)               # 二阶 Jury 条件
    oscillatory = np.iscomplex(roots[0])
    return stable, oscillatory, roots


def simulate(c, v, T=T_SIM, y0=(1.0, 1.0)):
    """从 (Y_0, Y_1)=y0 出发迭代差分方程，返回路径。"""
    Y = np.zeros(T)
    Y[0], Y[1] = y0
    for t in range(2, T):
        Y[t] = (c + v) * Y[t - 1] - v * Y[t - 2] + G_BAR
    return Y


def main():
    cases = [
        ("(a) c=0.60, v=0.50", 0.60, 0.50, "振荡收敛"),
        ("(b) c=0.60, v=1.50", 0.60, 1.50, "振荡发散"),
        ("(c) c=0.90, v=0.05", 0.90, 0.05, "单调收敛"),
        ("(d) c=0.85, v=2.00", 0.85, 2.00, "单调发散"),
    ]
    moduli = {}
    for label, c, v, expect in cases:
        stable, osc, roots = classify(c, v)
        Y = simulate(c, v)
        # 行为判据：以均衡 G/(1−c) 为中心，看偏离幅度首尾对比与超调
        y_eq = G_BAR / (1.0 - c)
        dev = Y - y_eq
        peak_dev = np.max(np.abs(dev[2:30]))
        # 收敛性：偏离的 20 期滑动最大绝对值，末期 vs 期初
        early = np.max(np.abs(dev[2:20]))
        late = np.max(np.abs(dev[-20:]))
        converged = late < 0.05 * max(early, 1e-12) + 1e-9
        # 振荡判定：去均值序列符号翻转 ≥2 次才算（单次穿越≠振荡，单调发散也会穿一次均值）
        flips = np.sum(np.sign(dev[2:40])[1:] * np.sign(dev[2:40])[:-1] < 0)
        overshoot = flips >= 2
        r = float(np.max(np.abs(roots)))
        moduli[label[:3]] = r
        print(f"{label}  预期={expect}")
        print(f"    Jury稳定={stable}  复根={osc}  |根|max={r:.3f}  "
              f"模拟收敛={converged}  模拟振荡={overshoot}")
        if expect == "振荡收敛":
            assert stable and osc and converged and overshoot
        elif expect == "振荡发散":
            assert (not stable) and osc and (not converged) and overshoot
        elif expect == "单调收敛":
            assert stable and (not osc) and converged and (not overshoot)
        elif expect == "单调发散":
            assert (not stable) and (not osc) and (not converged)
        else:
            raise ValueError(expect)

    # ── (e) 增长包络：发散振荡的包络增速 ≈ |特征根|/期 ──
    c, v = 0.60, 1.50
    roots = np.roots([1.0, -(c + v), v])
    r_mod = float(np.abs(roots[0]))                 # 共轭复根模相等
    Y = simulate(c, v, T=80)
    # 包络：局部极大点 (t, peak) 序列；每期包络增速 = ln(peak) 对 t 的回归斜率
    tp = [(t, Y[t]) for t in range(2, 79)
          if Y[t] >= Y[t - 1] and Y[t] >= Y[t + 1] and Y[t] > Y[0]]
    ts = np.array([p[0] for p in tp], dtype=float)
    ps = np.array([p[1] for p in tp])
    growth_emp = float(np.exp(np.polyfit(ts, np.log(ps), 1)[0]))
    ratio = growth_emp / r_mod
    print(f"(e) 振荡发散包络增速：实测={growth_emp:.3f}/期  |根|={r_mod:.3f}  "
          f"比值={ratio:.2f}   (断言 ∈ [0.85, 1.15]——峰值相位漂移留带宽)")
    assert 0.85 < ratio < 1.15, "发散包络每期增速应由特征根模决定"

    print("\n全部断言通过 ✅  乘数×加速数：行为类型完全由特征根决定，"
          "内生周期无需外生周期假设。")
    print("带走一句（04 章）：判据是 O(1) 的解析计算，仿真是 O(T) 的算力——"
          "先判据后仿真。")

if __name__ == "__main__":
    main()
