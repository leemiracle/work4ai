# -*- coding: utf-8 -*-
"""人口转变与动量三幕实验:间隙爆炸 / Leslie 矩阵与稳定人口 / 低生育陷阱的多稳态。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(结构卡的可构造端)、
04-人口学转代码.md(三条走廊)的配套实验。纯标准库(math/random/statistics),
无第三方依赖;除幕二随机初始向量外全确定性,固定种子,可复现。

三幕:
  幕一 人口转变的间隙爆炸——发展先把死亡收走,把生育留下:
      粗死亡率随「卫生现代化」参数 μ 先降(sigmoid 40‰→10‰,中心年 t_d),
      粗出生率滞后 τ 年后才降(40‰→11‰)。断言:①自然增长率峰值出现在
      「死亡率已降、生育率未降」的间隙窗口(峰值高度≈b0−d1,窗口位置打印);
      ②转变完成后的总人口规模显著高于「无转变基线」(b=d=40‰,r=0,规模
      不动)的外推;③滞后 τ 越长,间隙窗口越宽、爆炸体积越大,而峰值高度
      几乎不变——高度由死亡率的降幅决定,体积由窗口的宽度决定。
  幕二 Leslie 矩阵与稳定人口——Lotka 稳定人口理论的教学版(Leslie 1945):
      17 个 5 岁年龄组的年龄别生育/存活矩阵 L,任意初始向量迭代。断言:
      ①年龄结构收敛到 L 的主特征向量(远离暂态后相邻步距离单调降;两个
      不同随机初值收敛到同一结构);②内在自然增长率 λ=主特征值(幂迭代),
      与净再生产率 NRR 满足 λ≈NRR^(1/T)(T=世代长度;Euler 恒等式
      T=ln NRR/ln λ 与稳定人口平均生育年龄数值对照);③人口动量(Keyfitz
      1971):生育率骤降到更替水平(NRR=1)后,年轻结构的人口仍惯性增长
      数十百分比,年老结构甚至继续收缩(负动量)——年龄结构是生育率的
      存量遗产:今天的增长不欠今天的生育率,欠昨天的。
  幕三 低生育陷阱的多稳态——小家庭规范由小家庭一代复制(Lutz 假设):
      理想子女数 I(t)=更替基准 R+γ×(成长期 TFR 记忆−R)×w(记忆)
      (w 为单向棘轮权重:记忆低于更替才启反馈,高于则锚回更替——自我
      强化只在向下方向起作用),实际 TFR=理想数−推迟折损 d(t),理想数
      下限一孩硬底。断言:①γ=0 无反馈时,推迟冲击结束后 TFR 精确回落
      更替水平(单稳态);②γ 足够大时双稳态:更替稳态与低生育稳态并存,
      初值决定归宿(不稳定边界在 1.6-1.7 之间);冲击只是把系统推过边界,
      反馈接管后自锁——「低生育可以自锁:小家庭规范由小家庭一代复制」。

跑法: python -u experiments/demographic_transition_momentum.py
"""

import math
import random
import statistics
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower().replace("-", "") != "utf8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


# ==================== 幕一:人口转变的间隙爆炸 ====================

D0, D1 = 0.040, 0.010   # 粗死亡率:转变前 → 转变后(卫生现代化降幅 30‰)
B0, B1 = 0.040, 0.011   # 粗出生率:转变前 → 转变后(转变后 r≈+0.1%,低位平衡)
T_DEATH, S_DEATH = 40.0, 12.0   # 死亡下降的中心年与速度
S_BIRTH = 15.0                   # 生育下降的速度
T_YRS_A1 = 220                   # 模拟年数


def rates(t, tau):
    """t 年的粗出生率与粗死亡率:死亡先降(中心 T_DEATH),生育滞后 τ 年后降。"""
    d = D0 + (D1 - D0) * sigmoid((t - T_DEATH) / S_DEATH)
    b = B0 + (B1 - B0) * sigmoid((t - (T_DEATH + tau)) / S_BIRTH)
    return b, d


def run_transition(tau):
    """按滞后期 τ 跑完整转变;返回(规模序列, 自然增长率序列, b 序列, d 序列)。"""
    pop, path, rs, bs, ds = 1.0, [1.0], [], [], []
    for t in range(T_YRS_A1):
        b, d = rates(float(t), tau)
        r = b - d
        pop *= 1.0 + r
        path.append(pop)
        rs.append(r)
        bs.append(b)
        ds.append(d)
    return path, rs, bs, ds


def act1():
    print("=" * 84)
    print("幕一 人口转变的间隙爆炸:发展先把死亡收走,把生育留下")
    print("=" * 84)
    print(f"\n  粗出生率 b: {B0:.1%} → {B1:.1%}(中心年 {T_DEATH + 60:.0f},宽度 {S_BIRTH:.0f});")
    print(f"  粗死亡率 d: {D0:.1%} → {D1:.1%}(中心年 {T_DEATH:.0f},宽度 {S_DEATH:.0f});")
    print(f"  生育率滞后 τ=60 年下降;基线臂:b=d={D0:.1%} 不变(转变前平衡的外推)。")

    path, rs, bs, ds = run_transition(60.0)
    t_star = max(range(T_YRS_A1), key=lambda t: rs[t])
    peak = rs[t_star]
    d_drop = (D0 - ds[t_star]) / (D0 - D1)     # 峰值年死亡率已完成的降幅比例
    b_drop = (B0 - bs[t_star]) / (B0 - B1)     # 峰值年生育率已完成的降幅比例
    win = [t for t in range(T_YRS_A1) if rs[t] > 0.015]
    w_lo, w_hi = win[0], win[-1]
    p_base = 1.0                                # 基线:b=d=40‰,r=0,规模不动

    print(f"\n  自然增长率 r(t)=b(t)−d(t):峰值 {peak:.2%} 出现在第 {t_star} 年——")
    print(f"  该年死亡率已完成降幅的 {d_drop:.0%}(d={ds[t_star]*1e3:.1f}‰),"
          f"生育率仅完成 {b_drop:.0%}(b={bs[t_star]*1e3:.1f}‰)")
    print(f"  间隙窗口(r>1.5%):第 {w_lo}-{w_hi} 年,宽 {w_hi - w_lo} 年")
    print(f"  三阶段读数:高位平衡(r≈0)→ 间隙爆炸(峰值 {peak:.2%})→"
          f" 低位平衡(r≈+{B1 - D1:.1%})")
    print(f"  转变完成规模 P(220)={path[-1]:.2f} vs 无转变基线外推 {p_base:.2f}"
          f" —— 间隙攒出 {path[-1] / p_base:.1f} 倍人口")

    # 滞后敏感性:τ=45 vs τ=75(同样的降幅、同样的速度,只差生育回应的早晚)
    p45, r45, _, _ = run_transition(45.0)
    p75, r75, _, _ = run_transition(75.0)
    peak45, peak75 = max(r45), max(r75)
    win45 = [t for t in range(T_YRS_A1) if r45[t] > 0.015]
    win75 = [t for t in range(T_YRS_A1) if r75[t] > 0.015]
    print(f"\n  滞后敏感性(降幅与速度全同,只差 τ):")
    print(f"  τ=45:峰值 {peak45:.2%},窗口 {win45[0]}-{win45[-1]}"
          f"(宽 {win45[-1] - win45[0]}),终规模 {p45[-1]:.2f}")
    print(f"  τ=75:峰值 {peak75:.2%},窗口 {win75[0]}-{win75[-1]}"
          f"(宽 {win75[-1] - win75[0]}),终规模 {p75[-1]:.2f}")

    # 断言 1a:峰值落在间隙窗口——死亡率已大幅下降,生育率尚未跟进
    assert peak > 0.024, f"间隙峰值应显著为正(实测 {peak:.2%})"
    assert d_drop > 0.7 and b_drop < 0.3, \
        f"峰值应在「d 已降 {d_drop:.0%}、b 未降 {b_drop:.0%}」的窗口内"
    # 断言 1b:峰值高度≈b0−d1(由死亡率降幅封顶,不随窗口加宽而变大)
    assert peak < (B0 - D1) + 0.004, \
        f"峰值应≈b0−d1={B0 - D1:.2%}(实测 {peak:.2%})"
    # 断言 1c:转变完成后的规模显著高于转变前基线的外推
    assert path[-1] > 5.0 * p_base, \
        f"终规模应远高于基线外推({path[-1]:.2f} vs {p_base:.2f})"
    # 断言 1d:τ 越长窗口越宽、爆炸体积越大;峰值高度几乎不变
    assert p75[-1] > 2.0 * p45[-1], \
        f"τ=75 的爆炸体积应远大于 τ=45({p75[-1]:.2f} vs {p45[-1]:.2f})"
    assert win75[-1] - win75[0] > win45[-1] - win45[0], "τ 大者窗口应更宽"
    assert peak75 - peak45 < 0.006, \
        f"峰值高度应几乎不随 τ 变({peak45:.2%} vs {peak75:.2%})"

    print("\n读数:")
    print("  · 峰值年的解剖:死亡率端(卫生/防疫/营养)先响应现代化,生育端")
    print("    (规范/家庭经济/子女价值)滞后整整一代人——峰值就是这段「死亡")
    print(f"    已走、生育未动」的间隙:{peak:.2%} ≈ b0−d1={B0 - D1:.2%}")
    print(f"  · 体积=高度×宽度:τ 从 45 拉到 75,峰值只从 {peak45:.2%} 抬到"
          f" {peak75:.2%},终规模却从 {p45[-1]:.1f} 翻到 {p75[-1]:.1f}——")
    print("    人口爆炸的空间几乎全部由「生育回应死亡下降的时间差」提供")
    print(f"  · 基线(b=d=40‰)外推 220 年仍是 {p_base:.0f}:同一个村子,")
    print(f"    转变与否差 {path[-1]:.1f} 倍——不是多生出来的,是少死出来的")
    print(f"\n✓ 幕一断言通过:峰值 {peak:.2%} 落在间隙窗(d 已降 {d_drop:.0%}/"
          f"b 未降 {b_drop:.0%});终规模 {path[-1]:.2f} ≫ 基线 {p_base:.2f};"
          f"τ 75/45 终规模比 {p75[-1] / p45[-1]:.1f}")


# ==================== 幕二:Leslie 矩阵与稳定人口 ====================

W_STEP = 5      # 年龄组宽 = 投影步长(年)
N_GROUPS = 17   # 年龄组数:0-4, 5-9, ..., 80-84
# 组间存活率 s_i(i 组活到 i+1 组的概率),最后一组 [80,85) 之后退出
SURV = [0.960, 0.990, 0.995, 0.995, 0.992, 0.990, 0.988, 0.985,
        0.980, 0.972, 0.960, 0.945, 0.922, 0.888, 0.833, 0.740]
# 高生育档:年龄别女儿生育率(每人每 5 年;组 3-9 = 15-49 岁;合计≈2.42,≈TFR 5)
F_HI = [0.0, 0.0, 0.0, 0.20, 0.55, 0.60, 0.50, 0.35, 0.17, 0.05, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


def leslie(fert):
    """构造 Leslie 矩阵 L:首行=年龄别生育率,次对角=组间存活率。"""
    L = [[0.0] * N_GROUPS for _ in range(N_GROUPS)]
    for j in range(N_GROUPS):
        L[0][j] = fert[j]
    for i in range(1, N_GROUPS):
        L[i][i - 1] = SURV[i - 1]
    return L


def mat_vec(L, v):
    return [sum(L[i][j] * v[j] for j in range(N_GROUPS)) for i in range(N_GROUPS)]


def structure(v):
    tot = sum(v)
    return [x / tot for x in v]


def tv_dist(p, q):
    """两个年龄结构的总变差距离(0=相同,2=完全不相交)。"""
    return sum(abs(a - b) for a, b in zip(p, q))


def cum_survival():
    """S[i]=从出生活到第 i 组起点的累计存活概率(S[0]=1)。"""
    S = [1.0]
    for s in SURV:
        S.append(S[-1] * s)
    return S


def nrr_of(fert):
    """净再生产率 NRR=Σ f_i·S_i(一个新生女婴一生期望生下的女儿数)。"""
    S = cum_survival()
    return sum(f * s for f, s in zip(fert, S))


def dominant_eig(L):
    """幂迭代求主特征值与主特征向量(Perron-Frobenius:正矩阵谱半径为正)。"""
    v = [1.0] * N_GROUPS
    lam = 1.0
    for _ in range(20000):
        w = mat_vec(L, v)
        lam_new = sum(w) / sum(v)
        v = structure(w)
        if abs(lam_new - lam) < 1e-14:
            lam = lam_new
            break
        lam = lam_new
    return lam, v


def pyramid(v, width=28):
    """把年龄结构压成文本金字塔(每 5 岁组一行,▇ 数量∝占比)。"""
    lines = []
    for i in range(N_GROUPS - 1, -1, -1):
        blocks = "#" * max(1, int(round(v[i] / max(v) * width)))
        lines.append(f"    {i * W_STEP:>2d}-{i * W_STEP + 4:<2d} |{blocks}")
    return "\n".join(lines)


def act2():
    print("\n" + "=" * 84)
    print("幕二 Leslie 矩阵与稳定人口:年龄结构是生育率的存量遗产")
    print("=" * 84)
    L_hi = leslie(F_HI)
    nrr_hi = nrr_of(F_HI)
    f_lo = [f * (0.75 / nrr_hi) for f in F_HI]        # 低生育档:NRR=0.75
    f_repl = [f / nrr_hi for f in F_HI]               # 更替档:NRR=1

    # —— ① 任意初始向量收敛到稳定结构 ——
    rng = random.Random(8407155)
    v1 = [max(1.0, 1000.0 + rng.gauss(0.0, 300.0)) for _ in range(N_GROUPS)]
    v2 = [max(1.0, 10.0 * math.exp(rng.uniform(0.0, 4.0))) for _ in range(N_GROUPS)]
    dists1, dists2 = [], []
    n1, n2 = list(v1), list(v2)
    for _ in range(160):
        w1, w2 = mat_vec(L_hi, n1), mat_vec(L_hi, n2)
        dists1.append(tv_dist(structure(n1), structure(w1)))
        dists2.append(tv_dist(structure(n2), structure(w2)))
        n1, n2 = w1, w2
    lam, evec = dominant_eig(L_hi)
    final_dist_eig = tv_dist(structure(n1), evec)

    print(f"\n  17 个 5 岁年龄组的 Leslie 矩阵 L(高生育档 NRR={nrr_hi:.3f});"
          f"两个随机初始向量各自迭代 160 步:")
    print(f"  相邻步结构距离:第 5 步 {dists1[5]:.2e} → 第 60 步 {dists1[60]:.2e}"
          f" → 第 159 步 {dists1[159]:.2e}(单调降)")
    print(f"  两初始向量的终结构距离:{tv_dist(structure(n1), structure(n2)):.2e}"
          f"(殊途同归);与主特征向量的距离:{final_dist_eig:.2e}")
    print(f"  主特征值 λ={lam:.6f}(每 {W_STEP} 年),即内在自然增长率"
          f" {lam ** (1.0 / W_STEP) - 1:+.3%}/年")

    # 断言 2a:远离暂态后相邻步距离单调降(稳定结构的吸引)
    assert all(dists1[t + 1] < dists1[t] for t in range(6, 159)), \
        "相邻步结构距离应在暂态后单调下降"
    assert dists1[159] < 1e-10, f"结构应收敛(实测 {dists1[159]:.2e})"
    # 断言 2b:任意初始向量都收敛到同一稳定结构(主特征向量)
    assert tv_dist(structure(n1), structure(n2)) < 1e-9, "两初值应收敛到同一结构"
    assert final_dist_eig < 1e-9, f"应收敛到主特征向量({final_dist_eig:.2e})"

    # —— ② λ 与 NRR 的关系:λ ≈ NRR^(1/T) ——
    births = [f * x for f, x in zip(F_HI, structure(n1))]
    t_mom = sum((i * W_STEP + 2.5) * b for i, b in enumerate(births)) / sum(births)
    t_euler = (math.log(nrr_hi) / math.log(lam)) * W_STEP
    lam_check = nrr_hi ** (W_STEP / t_mom)

    print(f"\n  NRR={nrr_hi:.4f};λ={lam:.4f}(每步)")
    print(f"  Euler 恒等式世代长度 T=ln NRR/ln λ×{W_STEP}={t_euler:.1f} 年;"
          f"稳定人口平均生育年龄={t_mom:.1f} 年")
    print(f"  两种口径差 {t_euler - t_mom:.1f} 年(5 岁网格与生育计入约定的代价——"
          f"λ≈NRR^(1/T) 是一阶近似,不是恒等式)")
    print(f"  数值对照:λ={lam:.4f} vs NRR^(1/T)={lam_check:.4f}"
          f"(相对差 {abs(lam_check - lam) / lam:.2%})——Lotka 的稳定人口"
          f"关系在教学精度内成立")

    # 断言 2c:λ ≈ NRR^(1/T)(世代平均年龄口径,粗网格的教学级吻合)
    assert abs(lam_check - lam) / lam < 0.03, \
        f"λ 与 NRR^(1/T) 应吻合(相对差 {abs(lam_check - lam) / lam:.2%})"
    assert abs(t_euler - t_mom) < 4.0, \
        f"两种世代长度口径应接近({t_euler:.1f} vs {t_mom:.1f} 年)"

    # —— ③ 人口动量:生育率骤降到更替水平之后的惯性 ——
    def momentum(init_struct, total=100.0, steps=60):
        v = [x * total for x in init_struct]
        p_switch = sum(v)
        L_r = leslie(f_repl)
        for _ in range(steps):
            v = mat_vec(L_r, v)
        return sum(v) / p_switch, structure(v)

    young_struct = evec                      # 高生育档的稳定结构(年轻)
    L_lo = leslie(f_lo)
    _, old_struct = dominant_eig(L_lo)       # 低生育档的稳定结构(年老)
    mom_young, struct_final_y = momentum(young_struct)
    mom_old, struct_final_o = momentum(old_struct)

    print(f"\n  人口动量:把两档人口的生育率同时骤降到更替水平(NRR=1),"
          f"存活表不动,迭代 60 步({60 * W_STEP} 年):")
    print(f"  年轻结构(高生育档 NRR={nrr_hi:.2f} 的稳定人口):"
          f"终规模/切换时规模 = {mom_young:.3f}(惯性 +{(mom_young - 1):.0%})")
    print(f"  年老结构(低生育档 NRR=0.75 的稳定人口):"
          f"终规模/切换时规模 = {mom_old:.3f}(惯性 {mom_old - 1:+.0%},负动量)")
    print(f"  两臂终结构距离:{tv_dist(struct_final_y, struct_final_o):.2e}"
          f"(同一个更替稳态,分道扬镳后再汇合)")
    print("\n  年轻稳定结构(切换前)          年老稳定结构(切换前)")
    py1 = pyramid(young_struct).splitlines()
    py2 = pyramid(old_struct).splitlines()
    for a, b in zip(py1, py2):
        print(a + "   " + b)

    # 断言 2d:年轻结构动量为正且大(数十百分比)
    assert mom_young > 1.30, f"年轻结构动量应>+30%(实测 {mom_young:.3f})"
    # 断言 2e:年老结构动量为负(到更替后仍继续收缩)
    assert mom_old < 0.99, f"年老结构应为负动量(实测 {mom_old:.3f})"
    # 断言 2f:年轻动量显著大于年老动量(结构年轻的国家惯性更大)
    assert mom_young - mom_old > 0.35, \
        f"年轻/年老动量差应大({mom_young:.3f} vs {mom_old:.3f})"
    # 断言 2g:两臂汇合到同一个更替稳态结构(次主特征值 |λ2| 接近 1,线性收敛慢尾)
    assert tv_dist(struct_final_y, struct_final_o) < 1e-4, \
        f"两臂终结构应汇合(实测 {tv_dist(struct_final_y, struct_final_o):.1e})"

    print("\n读数:")
    print(f"  · Leslie 的第一课:遗忘初值。两个完全不同的随机人口,160 步后")
    print("    年龄结构相同、共同增长率即主特征值 λ——Lotka 稳定人口:")
    print("    常数率造常数增长,历史只剩一个特征向量")
    print(f"  · λ 与 NRR 的分工:NRR 管母女两代的账(乘 {nrr_hi:.2f} 倍),")
    print(f"    λ 管每年的账(乘 {lam ** (1.0 / W_STEP):.4f} 倍);连接两者的")
    print(f"    汇率是世代长度 T≈{t_mom:.0f} 年:λ≈NRR^(1/T),相差"
          f" {abs(lam_check - lam) / lam:.1%}(5 岁网格的教学精度)")
    print(f"  · 动量的解剖:生育率已到更替,但扩大的育龄队列是高生育年代")
    print(f"    存下的——年轻人口惯性再涨 {mom_young - 1:.0%};而低生育年代")
    print(f"    存下的窄队列,到更替后仍收缩 {1 - mom_old:.0%}。政策改流量,")
    print("    存量自己走完它的周期——「今天的人口增长不欠今天的生育率,")
    print("    欠昨天的」(Keyfitz 1971;多数国家增长与平台期由结构决定)")
    print(f"\n✓ 幕二断言通过:结构收敛(单调降→{dists1[159]:.0e});λ={lam:.4f}≈"
          f"NRR^(1/T)(差 {abs(lam_check - lam) / lam:.1%});动量 年轻"
          f"{mom_young:.3f} vs 年老 {mom_old:.3f}")


# ==================== 幕三:低生育陷阱的多稳态 ====================

R_REPL = 2.1        # 更替基准(理想子女数的锚)
GAMMA_LOCK = 1.35   # 自锁档反馈强度(「γ 足够大」)
GAMMA_SOFT = 0.5    # 弱反馈档(有记忆但不自锁)
I_FLOOR = 1.15      # 理想子女数下限(一孩规范的硬底)
MEM_LO, MEM_HI = 27, 17   # 成长期记忆窗口 [t-27, t-17](≈8-18 岁所见所闻)
SHOCK_LO, SHOCK_HI = 60, 85
SHOCK_D = 0.65      # 推迟折损(冲击期:住房/就业/危机推迟生育)
T_YRS_A3 = 260


def weight(m):
    """单向棘轮权重:记忆显著低于更替(≤R−0.6)→1;记忆到 R−0.1 以上→0。
    自我强化只在向下方向起作用——低生育记忆压低理想,高生育记忆不抬高。"""
    lo, hi = R_REPL - 0.6, R_REPL - 0.1
    if m <= lo:
        return 1.0
    if m >= hi:
        return 0.0
    return (hi - m) / (hi - lo)


def ideal_children(m, gamma):
    """Lutz 自我强化假设:理想子女数=更替基准+γ×(成长期记忆−更替)×权重。"""
    return max(I_FLOOR, R_REPL + gamma * (m - R_REPL) * weight(m))


def run_tfr(gamma, tfr0, shock):
    """跑理想-记忆-推迟动力学;返回逐年 TFR 序列。"""
    hist = [tfr0] * MEM_LO          # t<0 的暖启动:历史恒为初值
    tf = []
    for t in range(T_YRS_A3):
        full = hist + tf                    # full[y+27] = 第 y 年的 TFR
        m = statistics.mean(full[t:t + (MEM_LO - MEM_HI + 1)])
        d = SHOCK_D if (shock and SHOCK_LO <= t < SHOCK_HI) else 0.0
        tf.append(max(0.5, ideal_children(m, gamma) - d))
    return tf


def act3():
    print("\n" + "=" * 84)
    print("幕三 低生育陷阱的多稳态:小家庭规范由小家庭一代复制")
    print("=" * 84)
    print(f"\n  理想子女数 I(t) = {R_REPL} + γ×(成长期 TFR 记忆−{R_REPL})×w(记忆);")
    print(f"  记忆={MEM_LO}-{MEM_HI} 年前的 TFR 均值(成长期所见);"
          f"w 为单向棘轮(记忆低于更替才启反馈);")
    print(f"  实际 TFR = 理想数 − 推迟折损(第 {SHOCK_LO}-{SHOCK_HI} 年"
          f" 折损 {SHOCK_D});理想数下限 {I_FLOOR}(一孩硬底)。")

    # —— 冲击实验:同一推迟冲击,三种 γ ——
    tf0 = run_tfr(0.0, R_REPL, True)
    tf_soft = run_tfr(GAMMA_SOFT, R_REPL, True)
    tf_lock = run_tfr(GAMMA_LOCK, R_REPL, True)
    min_lock = min(tf_lock[SHOCK_HI:])
    lock_year = next(t for t in range(SHOCK_HI, T_YRS_A3)
                     if all(v < R_REPL - 0.3 for v in tf_lock[t:t + 40]))

    print(f"\n  推迟冲击(第 {SHOCK_LO}-{SHOCK_HI} 年 TFR 压到 ≈{R_REPL - SHOCK_D:.2f})后的归宿:")
    print(f"  γ=0.00 无反馈:冲击结束立即回 {tf0[-1]:.2f}(单稳态,记忆无影响)")
    print(f"  γ=0.50 弱反馈:记忆压低理想、缓慢回升,终值 {tf_soft[-1]:.2f}(回到更替)")
    print(f"  γ={GAMMA_LOCK:.2f} 强反馈:冲击结束仍继续下滑,自锁于 {tf_lock[-1]:.2f}"
          f"(第 {lock_year} 年起永久低于 {R_REPL - 0.3})")

    # —— 初值实验:γ=1.35、无冲击,初值决定归宿 ——
    starts = [2.3, 1.9, 1.7, 1.6, 1.5, 1.35]
    finals = {s: run_tfr(GAMMA_LOCK, s, False)[-1] for s in starts}
    print(f"\n  双稳态扫描(γ={GAMMA_LOCK},无冲击,只换初值):")
    for s in starts:
        dest = "更替稳态" if finals[s] > 2.0 else "低生育稳态"
        print(f"  初值 {s:.2f} → 终值 {finals[s]:.2f}({dest})")
    print("  不稳定边界夹在初值 1.6 与 1.7 之间(1.6 滑落 / 1.7 回升)")

    # 断言 3a:γ=0 时单稳态——冲击结束精确回落更替
    assert abs(tf0[-1] - R_REPL) < 1e-9, f"γ=0 应精确回更替({tf0[-1]:.4f})"
    assert abs(min(tf0[SHOCK_HI:]) - R_REPL) < 1e-9
    # 断言 3b:弱反馈仍回更替(有记忆但单稳态)
    assert tf_soft[-1] > 2.05, f"γ=0.5 应回到更替({tf_soft[-1]:.2f})"
    # 断言 3c:强反馈自锁——冲击结束后仍永久低于更替
    assert tf_lock[-1] < 1.25, f"γ=1.35 应自锁({tf_lock[-1]:.2f})"
    assert all(v < R_REPL - 0.3 for v in tf_lock[lock_year:]), "自锁应永久"
    assert min_lock < I_FLOOR + 0.05, f"锁底应≈一孩硬底({min_lock:.2f})"
    # 断言 3d:双稳态——初值决定归宿,边界在 1.6-1.7 之间
    for s in (2.3, 1.9, 1.7):
        assert finals[s] > 2.05, f"初值 {s} 应回更替(实测 {finals[s]:.2f})"
    for s in (1.6, 1.5, 1.35):
        assert finals[s] < 1.25, f"初值 {s} 应落低生育稳态(实测 {finals[s]:.2f})"

    print("\n读数:")
    print("  · γ=0 的世界:理想子女数钉在更替基准上,推迟冲击只借走几年生育,")
    print("    还回来——单一稳态,记忆不参与动力学")
    print(f"  · γ={GAMMA_LOCK} 的世界:在低生育环境长大的一代把「一两个也正常」")
    print("    写进理想,他们的低生育又成为下一代的成长环境——冲击只是把系统")
    print("    推过不稳定边界(1.6-1.7),反馈接管后永不再回更替:Lutz 低生育")
    print("    陷阱假设(2006)的教学版:自锁不靠政策失误,规范自己复制自己")
    print(f"  · 判别式:γ×w 在边界附近是否>1。弱反馈(γ=0.5)记忆只让回升变慢,")
    print("    强反馈(γ=1.35)让更替从吸引子变成分水岭——「低生育可以自锁:")
    print("    小家庭规范由小家庭一代复制」")
    print(f"\n✓ 幕三断言通过:γ=0 终值 {tf0[-1]:.2f}(单稳态);γ=0.5 终值"
          f" {tf_soft[-1]:.2f}(回升);γ={GAMMA_LOCK} 终值 {tf_lock[-1]:.2f}"
          f"(自锁);初值 1.7↑ 回更替 / 1.6↓ 落陷阱")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 间隙爆炸:自然增长率峰值出现在「死亡已降、生育未降」的窗口,")
    print("     高度≈b0−d1 由死亡率降幅封顶;体积=高度×窗口宽度,由生育回应")
    print("     的滞后 τ 决定;转变完成后规模数倍于无转变基线的外推")
    print("  ② 稳定人口:任意初始向量收敛到 Leslie 主特征向量;λ=主特征值与")
    print("     NRR 经世代长度 T 相连(λ≈NRR^(1/T));生育率骤降到更替后,")
    print("     年轻结构惯性再涨数十百分比、年老结构负动量——动量=结构的存量")
    print("  ③ 多稳态:无反馈(γ=0)单稳态,冲击后回更替;反馈够强(γ 大)时")
    print("     更替稳态与低生育稳态并存,初值决定归宿——低生育可以自锁")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
