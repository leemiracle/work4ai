# -*- coding: utf-8 -*-
"""
场地勘察三律(教学版)
====================

家族实验 · 讲透勘查技术(GB/T 41065)
主题呼应:证据的三道工序——检出(变点分层)、归一(能量校正)、配平(布孔优化)。

模型:
  [律1] CPT 变点分层:双层地基锥尖阻力序列
        qc(z) = 层均值(上层 5 MPa,下层 15 MPa)+ 高斯噪声(固定种子),
        界面真值 10.0 m,采样步长 0.1 m;
        统计量 D(i)=|mean(右窗)−mean(左窗)| 的峰 → 界面检出,
        assert |检出深度 − 10.0| ≤ 0.5 m,且对窗口宽度稳健。
        连续采样的分辨率兑换成界面深度的精度(00 章反直觉②的数据面)。
  [律2] N60 能量比校正(Skempton 1986 通说基准):
        N60 = N × ER/60(传递能量比 ER 以 60% 为基准)。
        同一地层真值 N60 恒定;四台钻机 ER=45/55/72/90,
        实测 N = N60×60/ER 各不相同(锤越没劲击数越多);
        assert 校正后 N60 的变异系数显著小于原始 N 的变异系数
        ——跨钻机可比性正是校正的目的:击数是仪器读数,不是土性。
  [律3] 贪心主动布孔:一维场地 [0,100],先验协方差核
        r(d)=exp(−d²/(2ℓ²)),预测方差 σ²(x)=σ₀²·Π_h (1−r(d(x,h)))
        (简单克里金式:每孔按距离核衰减地缩减方差,缩减可乘累积);
        参数场用固定种子随机场实现(核平滑白噪声,协方差结构已知)。
        已有 n0=4 孔(偏居左半场)后逐孔贪心——每步选使总预测方差
        最小的位置;对照均匀等距加同样 k=5 孔;
        assert 贪心总预测方差 ≤ 均匀(信息价值布孔对行政间距的胜利)。

只用标准库 math/random/statistics;固定随机种子,可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random
import statistics


# ----------------------------------------------------------------模型件

def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


def cv(values):
    """变异系数 = 总体标准差 / 均值(量纲一,跨钻机离散度的量度)。"""
    m = statistics.mean(values)
    assert m > 0, "CV 仅对正均值有定义(击数/阻力恒正)"
    return statistics.pstdev(values) / m


# ----------------------------------------------------------------实验 1

def experiment1():
    """CPT 变点分层:滑动窗口均值差检出双层界面,误差≤±0.5 m。"""
    section("实验 [1] CPT 变点分层:滑动窗口均值差检出地层界面")

    random.seed(20260908)
    dz = 0.1                                  # 采样步长 0.1 m(粗版每 10 cm 一点)
    n_pts = 200                               # 0.1 m .. 20.0 m
    depths = [(i + 1) * dz for i in range(n_pts)]
    q1, q2, z_true, sigma = 5.0, 15.0, 10.0, 0.8

    def make_profile():
        """双层地基 + 高斯噪声的 qc 序列(固定种子下可复现)。"""
        prof = []
        for z in depths:
            mu = q1 if z < z_true else q2
            prof.append(mu + random.gauss(0.0, sigma))
        return prof

    def detect_interface(profile, w):
        """滑窗均值差:D(i)=|mean(profile[i:i+w]) − mean(profile[i−w:i])|,
        argmax 即界面;边界两侧各留一个窗。"""
        best_i, best_d = None, -1.0
        for i in range(w, len(profile) - w):
            left = sum(profile[i - w:i]) / w
            right = sum(profile[i:i + w]) / w
            diff = abs(right - left)
            if diff > best_d:
                best_d, best_i = diff, i
        return depths[best_i], best_d

    qc = make_profile()

    # (a) 主检:窗长 2.0 m(20 点),检出 vs 真值
    w0 = 20
    z_det, d_stat = detect_interface(qc, w0)
    err = abs(z_det - z_true)
    m_up = statistics.mean(qc[: depths.index(
        min(depths, key=lambda z: abs(z - z_det)))])
    m_dn = statistics.mean(qc[depths.index(
        min(depths, key=lambda z: abs(z - z_det))):])
    print(f"(a) 上层均值 {q1} MPa / 下层均值 {q2} MPa,界面真值 {z_true} m,"
          f"噪声 σ={sigma} MPa,步长 {dz} m")
    print(f"    窗长 {w0 * dz:.1f} m:检出界面 z*={z_det:.2f} m"
          f"(统计量峰值 D={d_stat:.2f} MPa;分层读数 {m_up:.2f}/{m_dn:.2f} MPa)")
    print(f"    检出误差 |z*−z_true| = {err:.2f} m")
    assert err <= 0.5, "实验[1]:界面检出误差应≤±0.5 m"

    # (b) 窗宽稳健性:5/10/20/40 点(0.5~4.0 m)都能钉住界面
    print("(b) 窗宽稳健性(同一序列换窗长):")
    print("   窗长   检出 z*   误差")
    for w in (5, 10, 20, 40):
        zw, _ = detect_interface(qc, w)
        ew = abs(zw - z_true)
        print(f"  {w * dz:4.1f} m   {zw:5.2f} m   {ew:.2f}")
        assert ew <= 0.5, f"实验[1]:窗长 {w * dz:.1f} m 的检出误差应≤0.5 m"

    # (c) 信噪账:均值差 10 MPa,窗均值的噪声标准差 σ·sqrt(2/w)
    for w in (5, 20):
        noise_sd = sigma * math.sqrt(2.0 / w)
        print(f"(c) 窗长 {w * dz:.1f} m:窗均值差噪声 σ_D≈{noise_sd:.2f} MPa,"
              f"信号 10 MPa,信噪比 {10.0 / noise_sd:.0f}:1")
    print("断言通过:①主检误差≤0.5 m ②窗宽 0.5~4.0 m 全部稳健 "
          "——连续曲线的采样密度兑换成分层精度,"
          "每 2 cm 一点的真 CPT 比本例 0.1 m 还密 20 倍(00 章反直觉②)")


# ----------------------------------------------------------------实验 2

def experiment2():
    """N60 能量比校正:同层土四台钻机,校正后跨钻机可比。"""
    section("实验 [2] N60 能量比校正:N60 = N × ER/60")

    random.seed(60)
    n60_true = 12.0                                  # 该层土的"真值"(恒定)
    rigs = [("A 吊锤(老式)", 45), ("B 吊锤", 55),
            ("C 环刀锤(安全型)", 72), ("D 自动落锤", 90)]

    # 实测:N = N60×60/ER + 击数噪声(取整,≥1)——锤能量越低,击数越高
    rows = []
    for name, er in rigs:
        n_meas = max(1, round(n60_true * 60.0 / er + random.gauss(0.0, 0.3)))
        rows.append((name, er, n_meas))

    raws = [r[2] for r in rows]
    corrected = [r[2] * r[1] / 60.0 for r in rows]   # N60 = N × ER/60
    cv_raw, cv_60 = cv(raws), cv(corrected)

    print(f"(a) 同一地层(真值 N60={n60_true:.0f}),四台钻机实测:")
    print("   钻机                ER(%)   实测 N   校正 N60")
    for (name, er, n), c in zip(rows, corrected):
        print(f"   {name:<18s}  {er:4d}    {n:3d}     {c:5.2f}")
    print(f"(b) 原始 N:均值 {statistics.mean(raws):.2f},CV={cv_raw:.4f}")
    print(f"    校正 N60:均值 {statistics.mean(corrected):.2f},"
          f"CV={cv_60:.4f}")
    print(f"(c) CV 比:校正后是原始的 {cv_60 / cv_raw:.1%}"
          "——仪器效应除掉,读数才归到土")
    assert cv_60 < cv_raw / 3.0, \
        "实验[2]:N60 校正后变异系数应显著小于原始 N(<1/3)"
    assert abs(statistics.mean(corrected) - n60_true) < 1.0, \
        "实验[2]:校正后均值应回到真值附近(击数取整粒度 ER/60 内)"
    print("断言通过:①校正后 CV 显著小于原始 CV(跨钻机可比性) "
          "②校正后均值回到真值——击数是仪器读数,能量比是它的"
          "计量学换算(02 章仪器效应分离规则的出生地)")


# ----------------------------------------------------------------实验 3

def experiment3():
    """贪心主动布孔:每步选方差缩减最大处,对照均匀等距加孔。"""
    section("实验 [3] 贪心主动布孔 ≤ 均匀等距:总预测方差对比")

    random.seed(3)
    length, n_grid, ell, sigma0 = 100.0, 201, 15.0, 1.0
    xs = [i * length / (n_grid - 1) for i in range(n_grid)]   # 候选点 0..100

    # (a) 固定种子随机场:核平滑白噪声(先验协方差结构=同款核)
    n_src = 101
    ss = [i * length / (n_src - 1) for i in range(n_src)]
    eps = [random.gauss(0.0, 1.0) for _ in ss]
    field = []
    for x in xs:
        acc = 0.0
        for e, sj in zip(eps, ss):
            d = x - sj
            acc += e * math.exp(-d * d / (2.0 * ell * ell))
        field.append(acc)

    # (b) 简单克里金式方差模型:每孔按距离核衰减缩减方差,可乘累积
    def r_kernel(d):
        return math.exp(-d * d / (2.0 * ell * ell))

    def var_at(x, holes):
        v = sigma0
        for h in holes:
            v *= (1.0 - r_kernel(abs(x - h)))
        return v

    def total_var(holes):
        return sum(var_at(x, holes) for x in xs)

    def observed(h):
        """孔位处的场值观测(取最近格点的随机场实现值)。"""
        return field[xs.index(min(xs, key=lambda t: abs(t - h)))]

    # (c) 初始 4 孔偏居左半场(模拟既有孔网的历史遗留偏置)
    holes0 = [5.0, 15.0, 25.0, 35.0]
    k_add = 5
    v0 = total_var(holes0)
    print(f"(a) 场地 [0,{length:g}] m,先验核 ℓ={ell:g} m;"
          f"初始 {len(holes0)} 孔 {holes0},总预测方差 {v0:.2f} σ₀²")

    # (d) 贪心:每步选使总方差最小的候选点
    holes_g = list(holes0)
    print("(b) 贪心逐孔(每步选总方差缩减最大处):")
    prev_v = v0
    for step in range(k_add):
        best_x, best_v = None, None
        for x in xs:
            if min(abs(x - h) for h in holes_g) < 1e-9:
                continue                          # 已有孔位不重复
            v = total_var(holes_g + [x])
            if best_v is None or v < best_v:
                best_v, best_x = v, x
        holes_g.append(best_x)
        print(f"   第 {step + 1} 孔 → x={best_x:6.2f} m,"
              f"总方差 {best_v:.2f}(Δ={prev_v - best_v:.2f})")
        prev_v = best_v

    # (e) 对照:均匀等距加 5 孔(间距 20 m 的规则网,不看已有孔)
    holes_u = list(holes0) + [10.0 + 20.0 * j for j in range(k_add)]
    tg, tu = total_var(holes_g), total_var(holes_u)
    print(f"(c) 贪心孔网 {sorted(round(h, 1) for h in holes_g)}")
    print(f"    均匀孔网 {sorted(round(h, 1) for h in holes_u)}")
    print(f"(d) 总预测方差:贪心 {tg:.2f} σ₀²·点 vs 均匀 {tu:.2f} σ₀²·点"
          f"(贪心省 {(tu - tg) / tu:.1%})")
    max_g = max(var_at(x, holes_g) for x in xs)
    max_u = max(var_at(x, holes_u) for x in xs)
    print(f"(e) 最大点方差:贪心 {max_g:.3f} vs 均匀 {max_u:.3f} σ₀²"
          "——均匀网在已有孔旁浪费了两孔(10/30 m 处方差本已≈0)")
    assert tg <= tu, "实验[3]:贪心布孔的总预测方差应不劣于均匀等距"

    # (f) 对照真值场:两种孔网的核权重预测误差(实现层面,仅读数)
    def mse(holes):
        errs = []
        for x, z_true in zip(xs, field):
            ws = [(h, r_kernel(abs(x - h))) for h in holes]
            wsum = sum(w for _, w in ws)
            if wsum < 1e-12:
                z_hat = 0.0
            else:
                z_hat = sum(observed(h) * w for h, w in ws) / wsum
            errs.append((z_hat - z_true) ** 2)
        return statistics.mean(errs)

    print(f"(f) 对照随机场实现:贪心预测 MSE {mse(holes_g):.3f} vs "
          f"均匀 {mse(holes_u):.3f}——单次实现两者相当;"
          "方差优势是先验期望意义上的(大数定理下才兑现)")
    print("断言通过:贪心(每步最大方差缩减)总预测方差 ≤ 均匀等距 "
          "——布孔是买信息,间距是价格;规范间距是零先验的默认策略,"
          "AI 布孔(01 章方向二)是把先验变成数据驱动的同一件事")


# ----------------------------------------------------------------主控

def main():
    print("场地勘察三律(教学版)——讲透勘查技术家族实验")
    print("变点分层 + N60 能量校正 + 贪心布孔;纯标准库"
          "(math/random/statistics);固定种子,可复现")
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("全部断言通过:①CPT 变点分层检出双层界面(误差≤±0.5 m,"
          "窗宽稳健)②N60=N×ER/60 校正后跨钻机 CV 显著小于原始 N "
          "③贪心主动布孔总预测方差≤均匀等距加孔")
    print("=" * 64)


if __name__ == "__main__":
    main()
