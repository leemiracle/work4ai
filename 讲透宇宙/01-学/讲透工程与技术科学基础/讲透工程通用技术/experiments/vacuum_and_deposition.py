# -*- coding: utf-8 -*-
"""
真空平均自由程与薄膜沉积均匀性(教学版)
======================================

家族实验 · 讲透工程通用技术(GB/T 41070)
主题呼应走廊 C1-C3:把「真空是一种谱系」「行星盘换均匀性」「自限制=ALD 的工艺本体」
各写成一个可计算、可断言的模型。

模型:
  [律1] 平均自由程(理想气体分子刚球模型):
        λ = k·T / (√2·π·d²·P)
        空气分子有效直径 d=3.72 Å,T=300 K(常数:玻尔兹曼 k=1.380649e-23 J/K)。
        λ·P = kT/(√2·π·d²) = 6.7368e-3 m·Pa(与压强无关的谱系常数):
        P=10⁵ Pa(大气)→λ≈6.7e-8 m(67 nm 量级,分子挤成一团);
        P=10⁻⁴ Pa(高真空)→λ≈67 m(分子互不相撞)——同一根公式跨 9 个量级,
        且 λ 与 P 严格反比:压强每降一个量级,λ 升一个量级(逐点断言)。
  [律2] 行星盘公转+自转让厚度均匀(点源沉积的几何模型):
        沉积源为点源,位于系统轴上、距基片面高度 h(以基片半径 R=1 为单位);
        基片上径向距离 r 处的瞬时沉积通量(余弦发射+平方衰减):
        T(r) = h / (h² + r²)^{3/2}   (即 cosθ/L²,cosθ=h/L,L=√(h²+r²))。
        静止盘(基片圆心正对源):边缘/中心厚度比 =(1+1/h²)^{-3/2},
        h=3.5 时中心到边缘落差 >10%(不均匀);
        行星盘(基片圆心绕系统轴公转 R_orb=18,同时自转):基片上距圆心 ρ 的点,
        时间平均厚度 = 对 ψ 积分 T(√(R_orb²+ρ²+2·R_orb·ρ·cosψ))——
        多角度平均把 1/L³ 型径向梯度抹平,整盘不均匀度(极差/均值)<1%。
  [律3] ALD 自限制 vs CVD 流量单调:
        ALD 每循环生长量 GPC(D) = GPC_max·(1−e^{−D/D₀})(表面反应位饱和曲线):
        剂量欠饱和段 GPC 随剂量陡升,过饱和段 GPC 恒定——后半段(20 个递增
        剂量点的后 10 个)标准差/均值<1% 且极差/均值<0.5%;剂量翻倍厚度不动。
        CVD 沉积速率 R(F) = R_max·F/(F+K):随流量严格单调增,流量翻倍速率
        显著上移——「多了」在两种工艺里是两种物理学(工艺本体的分岔点)。

三个实验(全部断言自验证):
  [1] λ 跨 9 量级:大气端 67 nm、高真空端 67 m;逐十倍档严格反比;
      附克努森数判据(腔体 0.5 m:λ=D 的流态分界落在 10⁻²~10⁻¹ Pa)。
  [2] 行星盘:静止盘中心-边缘落差 >10%;行星盘整盘(极差/均值)<1%;
      附固定种子蒙特卡洛互证(轨道随机采样≈解析积分)。
  [3] ALD 饱和平台 vs CVD 单调:后半段 std/mean<1% 且极差/mean<0.5%;
      CVD 全程严格单调;剂量/流量翻倍的对照实验。

只用标准库 math/random/statistics;固定随机种子,可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random
import statistics


# ----------------------------------------------------------------模型件

K_B = 1.380649e-23          # 玻尔兹曼常数 J/K(SI 精确定值)
D_AIR = 3.72e-10            # 空气分子有效直径 m(刚球模型通说值)
T_ROOM = 300.0              # 室温 K


def mfp(p, t=T_ROOM, d=D_AIR):
    """平均自由程 λ = kT/(√2·π·d²·P)(理想气体刚球模型)。"""
    return K_B * t / (math.sqrt(2.0) * math.pi * d * d * p)


def flux_point_source(r, h):
    """点源瞬时沉积通量 T(r)=h/(h²+r²)^{3/2}(cosθ/L²,h=源高,r=离轴距离)。"""
    return h / (h * h + r * r) ** 1.5


def flux_orbit_average(rho, r_orb, h, n=8192):
    """行星盘时间平均通量:基片上距盘心 ρ 的点,对轨道角 ψ 的中点积分。

    自转使点的初始方位 irrelevant,唯一不变量是到轴的距离
    √(R_orb²+ρ²+2·R_orb·ρ·cosψ)——自转把「哪个点」变成「哪个半径环」。
    """
    total = 0.0
    for i in range(n):
        psi = (i + 0.5) * 2.0 * math.pi / n
        r = math.sqrt(r_orb * r_orb + rho * rho
                      + 2.0 * r_orb * rho * math.cos(psi))
        total += flux_point_source(r, h)
    return total / n


def nonuniformity(values):
    """不均匀度=(最大−最小)/均值,以百分数返回。"""
    mean = statistics.mean(values)
    return (max(values) - min(values)) / mean * 100.0


def gpc_ald(dose, gpc_max=0.11, d0=1.0):
    """ALD 每循环生长量 GPC(D)=GPC_max·(1−e^{−D/D₀})(表面饱和曲线)。"""
    return gpc_max * (1.0 - math.exp(-dose / d0))


def rate_cvd(flow, r_max=1.0, k_half=40.0):
    """CVD 沉积速率 R(F)=R_max·F/(F+K)(流量供给型,无自限制)。"""
    return r_max * flow / (flow + k_half)


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ----------------------------------------------------------------实验 1

def experiment1():
    """平均自由程跨 9 个量级,且与压强严格反比。"""
    section("实验 [1] 平均自由程:P 降 9 个量级,λ 升 9 个量级(67 nm→67 m)")

    # (a) 两端锚点:大气压与高真空
    lam_hi = mfp(1.0e5)                     # 10⁵ Pa(大气压)
    lam_lo = mfp(1.0e-4)                    # 10⁻⁴ Pa(高真空)
    print(f"(a) λ·P = kT/(√2·π·d²) = {K_B * T_ROOM / (math.sqrt(2.0) * math.pi * D_AIR ** 2):.4e} m·Pa"
          " ——与压强无关的谱系常数")
    print(f"    P=10⁵ Pa:λ={lam_hi:.4e} m ≈ {lam_hi * 1e9:.1f} nm(67 nm 量级,分子挤成一团)")
    print(f"    P=10⁻⁴ Pa:λ={lam_lo:.2f} m(≈67 m,分子互不相撞)")
    assert abs(lam_hi - 6.7e-8) < 0.1e-8, \
        "实验[1]:大气压端 λ 应为 6.7×10⁻⁸ m(67 nm 量级)"
    assert abs(lam_lo - 67.0) < 1.0, \
        "实验[1]:10⁻⁴ Pa 端 λ 应约 67 m"
    assert abs(lam_lo / lam_hi - 1.0e9) < 1e-6, \
        "实验[1]:两端应相差恰 9 个量级"

    # (b) 十倍档谱系表:从大气到高真空,逐档打印
    print("(b) 压强十倍档谱系(真空不是一种状态,是一整条谱):")
    print("   P (Pa)      λ            流态区(通说区间)")
    regimes = {5: "大气", 4: "低(粗)真空", 3: "低(粗)真空", 2: "中真空",
               1: "中真空", 0: "高真空", -1: "高真空", -2: "高真空",
               -3: "高真空", -4: "超高真空边缘"}
    lam_prev = None
    for expo in range(5, -5, -1):
        p = 10.0 ** expo
        lam = mfp(p)
        note = f"{lam:.3e} m"
        print(f"   10^{expo:+d}   {note:>14}  {regimes[expo]}")
        if lam_prev is not None:
            # 严格反比:压强降十倍,自由程升恰十倍(逐点断言)
            assert abs(lam / lam_prev - 10.0) < 1e-12, \
                f"实验[1]:10^{expo} Pa 档 λ 未按反比升十倍"
        lam_prev = lam
    print("    断言:每降一个量级 λ 恰升一个量级(λ∝1/P 逐点成立)")

    # (c) 克努森数判据:λ 与腔体特征尺寸同量级处分态
    chamber = 0.5                            # 0.5 m 腔体(教学取值)
    kn = lambda p: mfp(p) / chamber
    assert kn(1.0e-1) < 1.0 < kn(1.0e-2), \
        "实验[1]:0.5 m 腔体的黏滞/分子流分界应落在 10⁻²~10⁻¹ Pa"
    p_split = (K_B * T_ROOM / (math.sqrt(2.0) * math.pi * D_AIR ** 2)) / chamber
    print(f"(c) 克努森数 Kn=λ/D(D=0.5 m):Kn=1 在 P={p_split:.2e} Pa"
          "——分界两侧,气体从『连续流体』变『分子弹道』,"
          "同一台泵、同一套计算方法在这条线两侧不再通用(真空支的分水岭)")
    print("断言通过:①大气端 λ≈6.7×10⁻⁸ m ②高真空端 λ≈67 m "
          "③跨 9 量级且逐档严格反比——『抽真空』抽的不是一种东西")


# ----------------------------------------------------------------实验 2

def experiment2():
    """行星盘公转+自转让厚度均匀:静止盘>10% 不均,行星盘<1%。"""
    section("实验 [2] 行星盘:静止盘落差>10% → 公转+自转后整盘<1%")

    h, r_orb = 3.5, 18.0                     # 源高/公转半径(基片半径=1 为单位)
    rhos = [i / 10.0 for i in range(11)]     # 盘上采样点 ρ=0.0~1.0

    # (a) 静止盘:基片圆心正对源,径向厚度 T(ρ)=h/(h²+ρ²)^{3/2}
    static = [flux_point_source(rho, h) for rho in rhos]
    u_static = nonuniformity(static)
    edge_center = static[-1] / static[0]
    print(f"(a) 静止盘(h={h:g}):中心-边缘厚度比={edge_center:.4f},"
          f"整盘不均匀度(极差/均值)={u_static:.2f}%")
    print(f"    边缘通量/中心通量 =(1+1/h²)^(-3/2)="
          f"{(1 + 1 / (h * h)) ** -1.5:.4f}(cosθ 投影+平方衰减的双重惩罚)")
    assert u_static > 10.0, \
        "实验[2]:静止点源盘的中心-边缘落差应大于 10%"

    # (b) 行星盘:同一源、同一高度,基片绕轴公转 R_orb 并自转
    planet = [flux_orbit_average(rho, r_orb, h) for rho in rhos]
    u_planet = nonuniformity(planet)
    print(f"(b) 行星盘(同源同 h,公转 R_orb={r_orb:g}):"
          f"整盘不均匀度={u_planet:.3f}%")
    assert u_planet < 1.0, \
        "实验[2]:行星盘时间平均厚度偏差应小于 1%"
    print(f"    改善因子:{u_static / u_planet:.0f}×——每点在时间平均上"
          "经历同一圈环带分布,1/L³ 径向梯度被轨道平均抹平")

    # (c) 蒙特卡洛互证:轨道角随机采样 ≈ 解析积分(固定种子)
    random.seed(20260908)
    print("(c) 蒙特卡洛互证(每点 5 万次轨道采样,固定种子):")
    for rho in (0.0, 0.5, 1.0):
        m = 50000
        acc = 0.0
        for _ in range(m):
            psi = random.uniform(0.0, 2.0 * math.pi)
            r = math.sqrt(r_orb * r_orb + rho * rho
                          + 2.0 * r_orb * rho * math.cos(psi))
            acc += flux_point_source(r, h)
        mc = acc / m
        quad = flux_orbit_average(rho, r_orb, h)
        rel = abs(mc - quad) / quad * 100.0
        print(f"    ρ={rho:.1f}:MC={mc:.6e}  积分={quad:.6e}  偏差={rel:.3f}%")
        assert rel < 0.5, "实验[2]:蒙特卡洛与积分不合"

    # (d) 均匀性的代价:时间平均通量整体下跌(速率-均匀性交换)
    rate_static = statistics.mean(static)
    rate_planet = statistics.mean(planet)
    print(f"(d) 代价:平均沉积速率 {rate_static:.4e} → {rate_planet:.4e}"
          f"(×{rate_planet / rate_static:.3f})——运动学抹平了梯度,"
          "也把源摊薄了;真实设备用大面积源/多源/穹顶几何把速率找回来,"
          "行星机构负责余下的运动学半边(0 章假设二的账)")
    print("断言通过:①静止盘落差>10% ②行星盘整盘<1% "
          "③MC 与积分一致——均匀性是『让每点经历同一分布』,不是『让源变匀』")


# ----------------------------------------------------------------实验 3

def experiment3():
    """ALD 自限制饱和平台 vs CVD 流量单调。"""
    section("实验 [3] ALD 自限制 vs CVD 流量单调:两种『多了』的物理学")

    # (a) ALD 饱和曲线:20 个递增剂量点
    doses = [0.5 * i for i in range(1, 21)]           # D=0.5~10(×D₀)
    gpcs = [gpc_ald(d) for d in doses]
    print("(a) ALD 每循环生长量 GPC(饱和曲线 GPC_max=0.11 nm/cycle):")
    print("   剂量 D    GPC(nm/cycle)")
    for d, g in zip(doses, gpcs):
        bar = "#" * int(g / 0.11 * 30)
        print(f"   {d:5.1f}    {g:.5f}  {bar}")
    assert all(gpcs[i] < gpcs[i + 1] for i in range(19)), \
        "实验[3]:GPC 应随剂量单调上升(欠饱和段供给驱动)"
    assert gpcs[0] < 0.55 * gpcs[-1] < gpcs[-1], \
        "实验[3]:起点应明显欠饱和(<0.55×平台),否则曲线无对比度"

    # (b) 过饱和平台:后 10 点 std/mean<1% 且极差/mean<0.5%
    half = gpcs[10:]
    mean_h = statistics.mean(half)
    std_h = statistics.stdev(half)
    range_h = (max(half) - min(half)) / mean_h * 100.0
    print(f"(b) 过饱和段(后 10 点):std/mean={std_h / mean_h * 100:.4f}% "
          f"<1%;极差/均值={range_h:.4f}% <0.5%")
    assert std_h / mean_h < 0.01, "实验[3]:ALD 平台段标准差/均值应<1%"
    assert range_h < 0.5, "实验[3]:ALD 平台段极差/均值应<0.5%"

    # (c) CVD 速率:20 个递增流量点,严格单调
    flows = [float(f) for f in range(1, 21)]          # F=1~20(任意单位)
    rates = [rate_cvd(f) for f in flows]
    mono = all(rates[i] < rates[i + 1] for i in range(19))
    print(f"(c) CVD 沉积速率 R(F)=R_max·F/(F+K):20 点严格单调增={mono}")
    for f, r in zip(flows[::4], rates[::4]):
        print(f"    F={f:5.1f}  R={r:.4f}")
    assert mono, "实验[3]:CVD 速率应随流量严格单调增(无自限制机制)"

    # (d) 对照实验:供给翻倍,两种工艺各发生什么
    g_lo, g_hi = gpc_ald(20.0), gpc_ald(40.0)         # 剂量翻倍(深饱和区)
    r_lo, r_hi = rate_cvd(20.0), rate_cvd(40.0)       # 流量翻倍
    print(f"(d) 供给翻倍对照:ALD 剂量 20→40:GPC {g_lo:.6f}→{g_hi:.6f}"
          f"(相对变化 {(g_hi / g_lo - 1) * 100:.2e}%);"
          f"CVD 流量 20→40:R {r_lo:.4f}→{r_hi:.4f}(+{(r_hi / r_lo - 1) * 100:.1f}%)")
    assert abs(g_hi / g_lo - 1.0) < 1e-6, \
        "实验[3]:ALD 过饱和后剂量翻倍 GPC 应纹丝不动(自限制)"
    assert r_hi > 1.4 * r_lo, \
        "实验[3]:CVD 流量翻倍速率应显著上移(供给驱动)"
    print("    断言:ALD 厚度=循环数×饱和 GPC(表面反应位是硬顶),"
          "CVD 厚度=流量×时间(气相供给没有顶)——"
          "**自限制=ALD 的工艺本体**:多了不涨;CVD 的『多了』一直涨")
    print("断言通过:①ALD 平台 std/mean<1% 且极差<0.5% ②CVD 全程严格单调 "
          "③供给翻倍的两种命运——饱和曲线把『化学计量』写成了工艺参数")


# ----------------------------------------------------------------主控

def main():
    print("真空平均自由程与薄膜沉积均匀性(教学版)——讲透工程通用技术家族实验")
    print("λ=kT/(√2·π·d²·P) 跨 9 量级 + 行星盘均匀化 + ALD 自限制;"
          "纯标准库(math/random/statistics);固定种子,可复现")
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("全部断言通过:①平均自由程跨 9 量级且逐档严格反比"
          "(67 nm↔67 m)②行星盘让整盘厚度偏差从>10%降到<1%"
          "(多角度时间平均)③ALD 过饱和平台恒定(std/mean<1%,极差<0.5%)"
          "而 CVD 速率随流量单调增——自限制=ALD 的工艺本体")
    print("=" * 64)


if __name__ == "__main__":
    main()
