# -*- coding: utf-8 -*-
"""Bass 创新扩散模拟 + SIR 简单传染对照(p/q 参数扫描)。

00 章效果钟摆/03 章层 2 与钢筋/04 章走廊 1 配套实验。纯标准库。

Bass(1969): dF/dt = (p + qF)(1 − F)
  p = 外部影响系数(大众媒介/广告:与已采用者无关的恒定点火)
  q = 内部影响系数(人际口碑:随已采用比例 F 增长)
  解析解 F(t) = (1 − e^{−(p+q)t}) / (1 + (q/p)·e^{−(p+q)t})
  峰值时点 t* = ln(q/p)/(p+q);峰值渗透率 F* = (q − p)/(2q)
SIR 对照: dS/dt=−βSI, dI/dt=βSI−γI, dR/dt=γI(纯接触传染+康复≈内容过气/降权)
阈值传染(复杂传染平均场): dF/dt = λF(1−F)(F−θ),θ=临界大多数(双稳态)

断言(exit 0 即通过):
  A1 S 曲线语法:累计采用单增有界 ∈[0,1];采用率单峰
  A1b 解析对照:Euler 数值解 ≈ Bass 解析解(最大偏差 < 0.01)
  A2 峰值时点律:t̂* ≈ ln(q/p)/(p+q)(经典 p=.03,q=.38 → t*≈6.19)
  A3 q 扫描:口碑 q 越大峰值越早(t̂* 严格单调下降)
  A4 p 扫描:外火 p 越大峰值越早(t̂* 严格单调下降)——投放提前曲线,不抬天花板
  A5 峰值渗透律:口碑最响时市场约半数已采用(F̂* ≈ (q−p)/2q < 50%)
  A6 饱和律:无康复项 → 终渗透率 > 99%
  A7 无阈值律:p>0 零火种仍起飞;纯口碑(p=0)零火种永不启动(需要火种)
  A8 临界大多数:阈值传染不过 θ 线熄火归零,过线燎原至饱和(双稳态)
  B1 熄灭:R0<1 疫情自灭(终规模 < 5%)
  B2 群体免疫墙:R0=2.5 终规模 ≈89% < 100%(对照 Bass 的 99%+)
  B3 峰值后移:SIR 峰值时累计感染(≈60%)> Bass 峰值渗透率(≈46%)

跑法: python experiments/00_diffusion.py
"""

import math

DT = 0.01


def simulate_bass(p, q, f0=0.0, t_end=80.0, dt=DT):
    """Euler 积分 Bass 方程。返回 (时间列, 累计采用列, 瞬时采用率列)。"""
    f, ts, fs, rates = f0, [], [], []
    for k in range(int(t_end / dt)):
        rate = (p + q * f) * (1.0 - f)
        ts.append(k * dt)
        fs.append(f)
        rates.append(rate)
        f = min(1.0, f + rate * dt)
    return ts, fs, rates


def bass_analytic(p, q, t):
    """Bass 解析解(p>0,F0=0)。"""
    e = math.exp(-(p + q) * t)
    return (1.0 - e) / (1.0 + (q / p) * e)


def simulate_sir(beta, gamma, i0=0.001, t_end=100.0, dt=DT):
    """Euler 积分 SIR。返回 (时间列, 感染列, 累计感染列=i+r)。"""
    s, i, r = 1.0 - i0, i0, 0.0
    ts, i_arr, cum = [], [], []
    for k in range(int(t_end / dt)):
        ts.append(k * dt)
        i_arr.append(i)
        cum.append(i + r)
        inf = beta * s * i
        rec = gamma * i
        s -= inf * dt
        i += (inf - rec) * dt
        r += rec * dt
    return ts, i_arr, cum


def simulate_threshold(lam, theta, f0, t_end=80.0, dt=DT):
    """阈值传染(复杂传染平均场):dF/dt = λF(1−F)(F−θ)。返回累计采用轨迹。"""
    f, traj = f0, []
    for k in range(int(t_end / dt)):
        traj.append(f)
        f = f + lam * f * (1.0 - f) * (f - theta) * dt
    return traj


def argmax_peak(ts, ys):
    """返回 (峰值时刻, 峰值)。"""
    k = max(range(len(ys)), key=lambda j: ys[j])
    return ts[k], ys[k]


def unimodal(ys):
    """采用率序列是否单峰(先升后降,不回弹)。"""
    up = True
    for a, b in zip(ys, ys[1:]):
        if up:
            if b < a - 1e-12:
                up = False
        elif b > a + 1e-12:
            return False
    return True


def main():
    P, Q = 0.03, 0.38                     # Bass 经典参数带(耐用消费品经验值)
    print("=" * 66)
    print("Bass 创新扩散 + SIR 传染对照:信息扩散 vs 病毒扩散")
    print(f"  经典参数 p={P}(外部/媒介), q={Q}(内部/口碑), dt={DT}")
    print("=" * 66)

    # ---------- A1/A1b: S 曲线语法 + 解析对照 ----------
    ts, fs, rates = simulate_bass(P, Q)
    assert all(0.0 <= f <= 1.0 for f in fs), "渗透率越界"
    assert all(b >= a - 1e-12 for a, b in zip(fs, fs[1:])), "累计采用不单调"
    assert unimodal(rates), "采用率非单峰(违反 S 曲线形态)"
    err = max(abs(f - bass_analytic(P, Q, t)) for t, f in zip(ts, fs))
    print(f"[A1 ] S 曲线语法:累计采用单增有界,采用率单峰 ✓")
    print(f"[A1b] 解析对照:Euler vs 闭式解最大偏差 = {err:.5f} < 0.01")
    assert err < 0.01

    # ---------- A2: 峰值时点律 ----------
    t_star = math.log(Q / P) / (P + Q)
    t_hat, r_hat = argmax_peak(ts, rates)
    print(f"[A2 ] 峰值时点:实测 t̂*={t_hat:.2f} vs 理论 t*=ln(q/p)/(p+q)={t_star:.2f}")
    assert abs(t_hat - t_star) < 0.3

    # ---------- A3: q 扫描(口碑越强,峰值越早) ----------
    print("[A3 ] q 扫描(p=0.03):")
    q_grid = [0.20, 0.28, 0.38, 0.50]
    t_peaks_q = []
    for q in q_grid:
        tq, _, rq = simulate_bass(P, q)
        tk, _ = argmax_peak(tq, rq)
        t_peaks_q.append(tk)
        print(f"      q={q:.2f} → t̂*={tk:5.2f}(理论 {math.log(q / P) / (P + q):5.2f})")
    assert all(a > b for a, b in zip(t_peaks_q, t_peaks_q[1:])), "q 增大峰值未提前"
    assert all(abs(m - math.log(q / P) / (P + q)) < 0.35
               for m, q in zip(t_peaks_q, q_grid))

    # ---------- A4: p 扫描(外火越强,峰值越早;终规模不动) ----------
    print("[A4 ] p 扫描(q=0.38):")
    p_grid = [0.01, 0.03, 0.06, 0.10]
    t_peaks_p = []
    for p in p_grid:
        tp, fp, rp = simulate_bass(p, Q)
        tk, _ = argmax_peak(tp, rp)
        t_peaks_p.append(tk)
        print(f"      p={p:.2f} → t̂*={tk:5.2f}, 终渗透={fp[-1]:.4f}(天花板≈1 不随 p 动)")
    assert all(a > b for a, b in zip(t_peaks_p, t_peaks_p[1:])), "p 增大峰值未提前"

    # ---------- A5: 峰值渗透律 ----------
    f_star = (Q - P) / (2 * Q)
    k_hat = min(range(len(ts)), key=lambda j: abs(ts[j] - t_hat))
    f_hat = fs[k_hat]
    print(f"[A5 ] 峰值渗透:口碑最响时已采用 F̂*≈{f_hat:.3f} vs 理论 (q−p)/2q={f_star:.3f}"
          f"(未采用者 {1 - f_hat:.2f} 仍略多——热度顶点不是普及顶点)")
    assert abs(f_hat - f_star) < 0.02

    # ---------- A6: 饱和律 ----------
    print(f"[A6 ] 饱和律:无康复项,终渗透率 = {fs[-1]:.4f} > 0.99(信息不愈,全员到达)")
    assert fs[-1] > 0.99

    # ---------- A7: 无阈值律 ----------
    _, f_p0, _ = simulate_bass(P, 0.0, f0=0.0)   # 纯外部(去掉口碑)
    _, f_q0, _ = simulate_bass(0.0, Q, f0=0.0)   # 纯口碑零火种
    print(f"[A7 ] 无阈值律:p>0 零火种 → 终渗透 {f_p0[-1]:.3f}(外火不灭,无需火种);"
          f"p=0 零火种 → 永为 {f_q0[-1]:.1f}(口碑需要第一个采用者)")
    assert f_p0[-1] > 0.9
    assert f_q0[-1] < 1e-9

    # ---------- A8: 临界大多数(阈值传染双稳态) ----------
    lam, theta = 2.0, 0.20
    below = simulate_threshold(lam, theta, f0=0.15)
    above = simulate_threshold(lam, theta, f0=0.25)
    print(f"[A8 ] 临界大多数 θ={theta}:F₀=0.15(不过线)→ 归零 {below[-1]:.3f};"
          f"F₀=0.25(过线)→ 燎原 {above[-1]:.3f}")
    print("      ——行为采纳(复杂传染)才有真正的启动线;Bass 的 qF(1−F) 任何正火种都自持(慢而已)")
    assert below[-1] < 0.02
    assert above[-1] > 0.97

    # ---------- B 段: SIR 对照 ----------
    print("-" * 66)
    ts_s, i_arr, cum = simulate_sir(0.5, 0.2)            # R0 = 2.5
    _, _, cum_die = simulate_sir(0.15, 0.4)              # R0 = 0.375
    final = cum[-1]
    print(f"[B1 ] 熄灭:R0=0.375 → 终规模 {cum_die[-1]:.4f} < 0.05(接触强度不足自灭)")
    assert cum_die[-1] < 0.05
    print(f"[B2 ] 群体免疫墙:R0=2.5 → 终规模 {final:.3f} ∈(0.80,0.97)"
          f"(理论解析 ≈0.893;对照 Bass 的 0.99+:康复墙让一部分人永远没染上)")
    assert 0.80 < final < 0.97
    t_i_pk, _ = argmax_peak(ts_s, i_arr)
    cum_at_peak = cum[min(range(len(ts_s)), key=lambda j: abs(ts_s[j] - t_i_pk))]
    print(f"[B3 ] 峰值后移:SIR 峰值时累计感染 ≈{cum_at_peak:.2f}(理论 S=1/R0=0.40)"
          f" > Bass 峰值渗透 {f_hat:.2f}")
    print("      ——机理:SIR 减速靠易感者耗尽(墙在后面),Bass 减速靠市场剩余(墙在前面)")
    assert cum_at_peak > f_hat + 0.05
    assert 0.55 < cum_at_peak < 0.68

    print("=" * 66)
    print("读数:")
    print("  · 信息扩散(Bass):外火 p 无阈值点火,口碑 q 定节奏,全员到达;")
    print("    热度峰值(t*)可由 ln(q/p)/(p+q) 先验估计——投放买的是'提前',不是'更高'")
    print("  · 病毒/潮流扩散(SIR):康复=过气/降权,终规模有群体免疫墙<100%——")
    print("    平台降权(升 γ)是压终规模的最短杠杆(01 章练习 3 的机器版)")
    print("  · 行为采纳(阈值传染):启动线 θ 真实存在,不过线的种子预算是纯浪费")
    print("\n[自验证断言] 全部通过 ✓  (A1/A1b/A2/A3/A4/A5/A6/A7/A8/B1/B2/B3)")


if __name__ == "__main__":
    main()
