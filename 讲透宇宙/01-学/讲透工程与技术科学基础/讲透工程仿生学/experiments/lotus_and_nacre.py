# -*- coding: utf-8 -*-
"""
荷叶与珍珠母(教学版)
=====================

家族实验 · 讲透工程仿生学(GB/T 41040)
主题呼应走廊 C1/C2:润湿角模型(Wenzel/Cassie)与砖泥结构
拉拔能量学的教学版——「荷叶的秘密一半是空气」「95% 脆材料
组成韧材料」两句话的最小定量标本。

模型一(润湿,律1律2):Young 本征角 θ_Y 描述光滑均质面的
润湿性;真实表面有微结构,两个经典式给出表观角 θ*:
    Wenzel(全浸润,液体填满结构):cosθ* = r·cosθ_Y,r≥1 粗糙度
    Cassie(复合浸润,结构截留空气):cosθ* = f·(cosθ_Y+1)−1,
    f∈[0,1] 固液接触中固体占比
律1:Wenzel 粗糙度放大——θ_Y>90° 时 θ* 随 r 单调升(疏更疏),
     θ_Y<90° 时单调降(亲更亲),θ_Y=90° 是不动点:
     粗糙度不改变润湿性,只放大本征润湿性。
律2:Cassie 气垫——f→0 时 cosθ*→−1、θ*→180°;荷叶参数
     (f≈0.05~0.1,θ_Y≈110°)θ*>150° 达超疏水阈值;同一微
     结构下 Cassie 态比 Wenzel 态高约 26°(浸润坍塌的代价)。
律3:砖泥结构增韧——一维 brick-mortar 拉拔锯齿力-位移模型
     (界面密度可调):每个界面「弹性上升→跌落→摩擦滑移」,
     断裂功=力-位移曲线下面积(数值积分);界面密度加倍,
     总断裂功近乎翻倍且数十倍于均质对照,峰值力不变——
     裂纹偏转与拔出的能量学:珍珠母「脆材料组成韧材料」
     (强韧解耦:峰值力由界面强度定,断裂功由界面次数定)。

物理约定:润湿律取静态角;滚动角/滞后需另建模型(04 章
走廊边界)。砖泥教学模型中断裂功随密度近似线性是下界;
真实珍珠母的过程区并行参与给出超线性增益(通说)。
均质对照取同峰值力的线弹性脆断(弹性储能即全部断裂功)。

只用标准库 random/math;固定随机种子,结果可复现;
全部断言通过时打印「全部断言通过」并以退出码 0 结束。
"""

import math
import random

# ----------------------------------------------------------------常量
DEG = math.pi / 180.0

# 砖泥模型参数(N·mm 记 mJ)
F_PK = 100.0        # 单界面峰值力 N(界面剪切强度×界面面积的集中参数)
DELTA_RISE = 0.05   # 弹性上升段位移 mm
F_FR = 40.0         # 残余摩擦力 N(跌落后的滑移平台)
DELTA_SLIP = 0.40   # 每界面滑移长度 mm
K_HOMO = 2000.0     # 均质对照刚度 N/mm
F_CRIT = 100.0      # 均质对照临界力 N(与 F_PK 同级:同强度比韧性)


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


# ----------------------------------------------------------------律1:Wenzel

def wenzel_angle(theta_y_deg, r):
    """Wenzel 表观角:cosθ* = r·cosθ_Y(物理裁剪到 [−1,1])。"""
    c = r * math.cos(theta_y_deg * DEG)
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))


def experiment1():
    """律1:粗糙度放大本征润湿性——疏更疏/亲更亲/90° 不动点。"""
    section("律1 [Wenzel] cosθ*=r·cosθ_Y:粗糙度放大,不改方向")
    # (a) r=1 恒等:粗糙度取 1 时退化为 Young 本征角
    max_dev = max(abs(wenzel_angle(t, 1.0) - t) for t in
                  (60.0, 70.0, 90.0, 110.0, 150.0))
    assert max_dev < 1e-9, "律1:r=1 未退化为 Young 角"
    print(f"(a) r=1 恒等式:|θ*−θ_Y| 最大 {max_dev:.2e} ✓")

    # (b) 本征疏水 θ_Y=110°:θ* 随 r 单调升(疏更疏)
    print("(b) θ_Y=110°(本征疏水),扫粗糙度 r:")
    print("   r     θ*_W   Δθ*")
    prev = None
    mono_hydro = True
    for r in [1.0 + 0.25 * k for k in range(7)]:
        th = wenzel_angle(110.0, r)
        d = "" if prev is None else f"{th - prev:+.2f}"
        if prev is not None and th <= prev + 1e-9:
            mono_hydro = False
        print(f"  {r:4.2f}  {th:6.2f}  {d}")
        prev = th
    assert mono_hydro, "律1:疏水侧 θ* 未随 r 单调升"
    assert wenzel_angle(110.0, 1.0) < wenzel_angle(110.0, 2.5), \
        "律1:疏水侧应有 θ*(2.5)>θ*(1.0)"

    # (c) 本征亲水 θ_Y=70°:θ* 随 r 单调降(亲更亲)
    print("(c) θ_Y=70°(本征亲水),扫粗糙度 r:")
    print("   r     θ*_W   Δθ*")
    prev = None
    mono_philo = True
    for r in [1.0 + 0.25 * k for k in range(7)]:
        th = wenzel_angle(70.0, r)
        d = "" if prev is None else f"{th - prev:+.2f}"
        if prev is not None and th >= prev - 1e-9:
            mono_philo = False
        print(f"  {r:4.2f}  {th:6.2f}  {d}")
        prev = th
    assert mono_philo, "律1:亲水侧 θ* 未随 r 单调降"
    assert wenzel_angle(70.0, 2.5) < wenzel_angle(70.0, 1.0), \
        "律1:亲水侧应有 θ*(2.5)<θ*(1.0)"

    # (d) 90° 不动点:本征角 90° 的表面,粗糙度不再改变表观角
    dev90 = max(abs(wenzel_angle(90.0, r) - 90.0) for r in
                (1.3, 1.7, 2.2, 2.5))
    assert dev90 < 1e-9, "律1:θ_Y=90° 不是不动点"
    print(f"(d) 不动点:θ_Y=90° 时任意 r 下 θ*=90°(最大偏差 {dev90:.2e})"
          "——粗糙度是放大器不是换向器")
    print("断言通过:①θ_Y>90° 单调升(疏更疏)②θ_Y<90° 单调降"
          "(亲更亲)③θ_Y=90° 不动点——放大本征润湿性")


# ----------------------------------------------------------------律2:Cassie

def cassie_angle(theta_y_deg, f):
    """Cassie-Baxter 表观角:cosθ* = f·(cosθ_Y+1)−1。"""
    c = f * (math.cos(theta_y_deg * DEG) + 1.0) - 1.0
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))


def experiment2():
    """律2:复合浸润——f→0 时 θ*→180°;荷叶稳过 150°;两态差。"""
    section("律2 [Cassie] cosθ*=f(cosθ_Y+1)−1:空气垫在 +1 里")
    theta_y = 110.0          # 荷叶蜡晶的本征角(通说量级)
    smooth = cassie_angle(theta_y, 1.0)
    assert abs(smooth - theta_y) < 1e-9, "律2:f=1 未退化为 Young 角"
    print(f"光滑蜡面(f=1):θ*={smooth:.1f}°——只有材料,离自洁差得远\n")

    # (a) f 扫描:f→0 时 cosθ*→−1,θ*→180°
    print("(a) θ_Y=110°,扫固面占比 f(空气占比 1−f):")
    print("   f      θ*_C")
    prev = None
    mono_f = True
    for f in (1.0, 0.5, 0.2, 0.1, 0.05, 0.01, 0.001, 0.0001):
        th = cassie_angle(theta_y, f)
        if prev is not None and th <= prev - 1e-9:
            mono_f = False
        print(f"  {f:7.4f} {th:7.2f}")
        prev = th
    assert mono_f, "律2:θ* 未随 f 减小而单调升"
    assert cassie_angle(theta_y, 0.001) > 177.0, "律2:f=0.001 未达 >177°"
    assert cassie_angle(theta_y, 0.0001) > 179.0, "律2:f=1e-4 未达 >179°"
    cos_limit = 0.0001 * (math.cos(theta_y * DEG) + 1.0) - 1.0
    print(f"    f→0 极限:cosθ*→−1(取 f=1e-4 时 cosθ*={cos_limit:.6f},"
          f"θ*={cassie_angle(theta_y, 0.0001):.2f}°)——空气不浸润,"
          "躺在气垫上的液滴趋向完美球")

    # (b) 荷叶参数区间:f≈0.05~0.1 ⇒ θ*>150°(超疏水阈值)
    print("\n(b) 荷叶参数区间(f≈0.05~0.1,θ_Y≈110°):")
    for f in (0.10, 0.09, 0.08, 0.07, 0.06, 0.05):
        th = cassie_angle(theta_y, f)
        print(f"  f={f:.2f}  θ*={th:.2f}°  {'超疏水 ✓' if th > 150 else '未达标'}")
        assert th > 150.0, f"律2:荷叶区间 f={f} 未过 150°"
    assert smooth < 150.0, "律2:光滑面不应达标(材料单独不够)"
    print(f"    对照:光滑蜡面 {smooth:.0f}° < 150°——材料×结构缺一不可")

    # (c) 同一微结构,两种浸润态:Cassie(气垫)vs Wenzel(全浸润)
    r_tex, f_tex = 2.0, 0.1        # 同一微结构的两种刻画
    th_c = cassie_angle(theta_y, f_tex)
    th_w = wenzel_angle(theta_y, r_tex)
    print(f"\n(c) 同一微结构(固面占比 f={f_tex},粗糙度 r={r_tex}):"
          f"Cassie 态 {th_c:.2f}° vs Wenzel 态 {th_w:.2f}°,"
          f"差 {th_c - th_w:.2f}°")
    assert th_c - th_w > 15.0, "律2:两态之差应超过 15°"
    assert th_c > th_w > smooth, "律2:应有 Cassie>Wenzel>光滑"
    print("    高压把气垫按进去(Cassie→Wenzel 浸润坍塌),"
          "接触角掉约 26°——超疏水表面的头号失效模式")
    print("断言通过:①f→0 ⇒ θ*→180° ②荷叶区间稳过 150° ③"
          "同一微结构 Cassie 比 Wenzel 高约 26°——荷叶的秘密一半是空气")


# ----------------------------------------------------------------律3:砖泥

def brick_mortar_curve(n_iface, f_pk=F_PK, d_rise=DELTA_RISE,
                       f_fr=F_FR, d_slip=DELTA_SLIP, jitter=0.0,
                       pts_per_seg=25):
    """一维砖泥拉拔锯齿力-位移曲线:N 个界面串行破坏。

    每界面三段:弹性升 0→F_pk(位移 d_rise)、瞬时跌落到
    摩擦平台 F_fr、恒力滑移(位移 d_slip)。jitter>0 时各界面
    F_pk/F_fr 带 ±jitter 比例随机涨落。返回 (u_list, F_list)。
    """
    us, fs = [], []
    u = 0.0
    us.append(0.0)
    fs.append(0.0)
    for _ in range(n_iface):
        f_pk_i = f_pk * (1.0 + random.uniform(-jitter, jitter))
        f_fr_i = f_fr * (1.0 + random.uniform(-jitter, jitter))
        us.append(u)                                   # 界面切换:瞬时卸载
        fs.append(0.0)                                 # 到 0(零宽,无面积)
        for k in range(1, pts_per_seg + 1):            # 段1:弹性上升
            us.append(u + d_rise * k / pts_per_seg)
            fs.append(f_pk_i * k / pts_per_seg)
        u += d_rise
        us.append(u)                                   # 段2:跌落(零位移宽度)
        fs.append(f_fr_i)
        for k in range(1, pts_per_seg + 1):            # 段3:摩擦滑移
            us.append(u + d_slip * k / pts_per_seg)
            fs.append(f_fr_i)
        u += d_slip
    us.append(u)                                       # 分离:力归零
    fs.append(0.0)
    return us, fs


def trapezoid(us, fs):
    """力-位移曲线下面积(梯形数值积分)。"""
    return sum(0.5 * (fs[i + 1] + fs[i]) * (us[i + 1] - us[i])
               for i in range(len(us) - 1))


def bm_analytic_work(n_iface, f_pk=F_PK, d_rise=DELTA_RISE,
                     f_fr=F_FR, d_slip=DELTA_SLIP):
    """解析式:每界面储能 ½F_pk·δ + 摩擦功 F_fr·δ_slip。"""
    return n_iface * (0.5 * f_pk * d_rise + f_fr * d_slip)


def experiment3():
    """律3:界面密度加倍→断裂功近乎翻倍;远超均质;峰力不变。"""
    section("律3 [砖泥] 拉拔锯齿:断裂功按界面次数计费")
    print(f"参数:F_pk={F_PK:g} N δ_rise={DELTA_RISE:g} mm "
          f"F_fr={F_FR:g} N δ_slip={DELTA_SLIP:g} mm\n")

    # (a) 数值积分 vs 解析式互证(线性段梯形积分为精确)
    w1_analytic = bm_analytic_work(1)
    for n in (4, 8):
        us, fs = brick_mortar_curve(n)
        w_num = trapezoid(us, fs)
        dev = abs(w_num - bm_analytic_work(n)) / bm_analytic_work(n)
        assert dev < 5e-3, f"律3:N={n} 数值积分偏离解析式"
        print(f"(a) N={n}:数值积分 W={w_num:.4f} mJ,"
              f"解析式 W={bm_analytic_work(n):.4f} mJ,相对偏差 {dev:.2e} ✓")

    # (b) 均质对照:同峰值力的线弹性脆断,断裂功=弹性储能
    delta_c = F_CRIT / K_HOMO
    w_homo = 0.5 * F_CRIT * delta_c
    print(f"\n(b) 均质脆性对照:F_crit={F_CRIT:g} N(与 F_pk 同级),"
          f"δ_c={delta_c:.4f} mm,W_homo=½F·δ={w_homo:.4f} mJ"
          "(裂纹一穿而过,只带走弹性储能)")

    # (c) 密度敏感性:N 扫描,断裂功严格单调升且近似线性
    print("\n(c) 界面密度扫描(N=1→12):")
    print("   N    W_N(mJ)   W_N/W_1   W_N/W_homo   F_max(N)")
    prev_w = None
    mono_w = True
    f_max_bm = 0.0
    for n in range(1, 13):
        us, fs = brick_mortar_curve(n)
        w = trapezoid(us, fs)
        f_max = max(fs)
        f_max_bm = max(f_max_bm, f_max)
        lin_dev = abs(w - n * w1_analytic) / (n * w1_analytic)
        assert lin_dev < 5e-3, f"律3:N={n} 偏离线性按次计费"
        if prev_w is not None and w <= prev_w + 1e-9:
            mono_w = False
        print(f"  {n:3d}   {w:7.3f}   {w / w1_analytic:7.3f}"
              f"      {w / w_homo:6.1f}       {f_max:6.1f}")
        prev_w = w
    assert mono_w, "律3:断裂功未随界面密度单调升"

    # (d) 核心断言:密度加倍,功近乎翻倍;远超均质;峰力不变
    w4 = bm_analytic_work(4)
    w8 = bm_analytic_work(8)
    us8, fs8 = brick_mortar_curve(8)
    w8_num = trapezoid(us8, fs8)
    ratio_dbl = w8 / w4
    assert 1.9 <= ratio_dbl <= 2.1, "律3:密度加倍应近乎翻倍"
    assert w4 / w_homo > 20.0, "律3:应远超均质对照(>20 倍)"
    assert max(fs8) <= F_PK * 1.001, "律3:峰值力不应超过界面强度"
    assert abs(max(fs8) - F_CRIT) / F_CRIT < 0.01, \
        "律3:峰值力应与均质对照同级(强韧解耦)"
    print(f"\n(d) 密度加倍:N=4→8,断裂功 {w4:.1f}→{w8:.1f} mJ"
          f"(比值 {ratio_dbl:.3f});")
    print(f"    对照均质:W(4)/W_homo={w4 / w_homo:.1f} 倍、"
          f"W(8)/W_homo={w8 / w_homo:.1f} 倍(数值积分 {w8_num:.1f} mJ);")
    print(f"    峰值力:砖泥 F_max≈{max(fs8):.0f} N ≈ 均质 F_crit="
          f"{F_CRIT:g} N,纹丝不动")
    print("    强韧解耦:峰值力由界面强度定,断裂功由界面次数定——")
    print("    裂纹偏转+摩擦拔出按次计费,脆材料组成韧材料")

    # (e) 鲁棒性:界面参数 ±5% 涨落,总功稳定(按次计费的稳健性)
    random.seed(20260908)
    trials = 50
    ratios = []
    for _ in range(trials):
        us, fs = brick_mortar_curve(8, jitter=0.05)
        ratios.append(trapezoid(us, fs) / w8_analytic_check())
    spread = max(abs(r - 1.0) for r in ratios)
    assert spread < 0.04, "律3:±5% 涨落下总功漂移超 4%"
    print(f"\n(e) 鲁棒性:8 界面、F_pk/F_fr 各 ±5% 涨落,{trials} 次试验,"
          f"总功相对名义值最大漂移 {spread * 100:.2f}%"
          "(单界面涨落被多界面求和平均掉)——按次计费的账本稳")
    print("断言通过:①数值积分=解析式 ②W 随 N 单调升、近似线性 "
          "③密度加倍功翻倍且数十倍于均质 ④峰值力不变(强韧解耦) "
          "⑤涨落下总功稳健")


def w8_analytic_check():
    """(e) 小节的名义值(与 (a) 同式,便于就近核对)。"""
    return bm_analytic_work(8)


# ----------------------------------------------------------------主控

def main():
    print("荷叶与珍珠母(教学版)——讲透工程仿生学家族实验")
    print("Wenzel/Cassie 润湿角模型 + 砖泥结构拉拔锯齿;纯标准库"
          "(random/math);固定种子,可复现")
    experiment1()
    experiment2()
    experiment3()
    print("\n" + "=" * 64)
    print("三律证据收拢:")
    print(f"  律1 Wenzel:θ_Y=110° 时 r=1→2.5 使 θ* 从 110.00° 升到 "
          f"{wenzel_angle(110.0, 2.5):.2f}°;θ_Y=70° 时降到 "
          f"{wenzel_angle(70.0, 2.5):.2f}°;θ_Y=90° 恒为 90°")
    print(f"  律2 Cassie:荷叶参数 θ*={cassie_angle(110.0, 0.10):.1f}°"
          f"(f=0.10)~{cassie_angle(110.0, 0.05):.1f}°(f=0.05),"
          f"均>150°;f=1e-4 时 θ*={cassie_angle(110.0, 0.0001):.2f}°;"
          f"同微结构两态差 {cassie_angle(110.0, 0.10) - wenzel_angle(110.0, 2.0):.1f}°")
    print(f"  律3 砖泥:N=4→8 断裂功 {bm_analytic_work(4):.0f}→"
          f"{bm_analytic_work(8):.0f} mJ(近乎翻倍),"
          f"为均质对照({0.5 * F_CRIT * F_CRIT / K_HOMO:.1f} mJ)的 "
          f"{bm_analytic_work(8) / (0.5 * F_CRIT * F_CRIT / K_HOMO):.0f} 倍,"
          "峰值力不变")
    print("全部断言通过:①粗糙度放大本征润湿性(90° 不动点) "
          "②Cassie 气垫:荷叶稳过 150°、两态差 26° ③砖泥按次计费:"
          "密度加倍功翻倍、远超均质、强韧解耦")
    print("=" * 64)


if __name__ == "__main__":
    main()
