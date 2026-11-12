# -*- coding: utf-8 -*-
"""社会地理学三律实验:Moran's I 隔离签名 / 邻里效应剂量-距离饱和 / Gibrat→齐普夫。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(格局引擎/衰减引擎)与
04-社会地理学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),固定随机种子,assert 自验证。

三幕:
  幕一 空间自相关 Moran's I 的两副面孔(隔离的空间签名)。
      20×20 网格两分类(各 50%,Rook 邻接):同配格局由「相邻同类偏好」
      局部交换生成,随机散布为对照。
      断言:同配格局 I>0.6 且对 1000 次随机置换的零分布检验 p<0.01;
      随机格局 |I|<0.05 且置换检验不显著(p>0.05)。
      点题:隔离不是印象,是有签名可检验的空间统计量——
      同样 50/50 的比例,格局可以天差地别(比例≠隔离)。
  幕二 邻里效应的剂量-距离饱和(暴露有半径)。
      个体结果 = 基线 + β×加权邻里质量 + 个体噪声;权重 w(d)=1/(1+d/λ)
      随距离衰减(λ=感受半径),固定活动窗 W(个体最大采样半径)。
      断言:把个体迁往好邻里,收益随 λ 增大而严格上升但边际递减
      (Q(λ*/2)→Q(2λ*) 的增量 > Q(2λ*)→Q(4λ*) 的增量),存在半效应
      尺度 λ*(收益达饱和值一半的半径);蒙特卡洛加噪后组均值曲线
      仍复现确定论的剂量-距离形状;留守者收益恒为 0。
      点题:搬家改变暴露,但暴露有半径——隔一条感受边界的「好街区」
      只是背景板。
  幕三 齐普夫城市层级与 Gibrat 生成机制(层级的统计必然)。
      100 个同规模城市,500 期对数正态比例增长(增长率与规模无关,
      带 Gabaix 反射壁:S 不低于初始规模);对照=无随机差异的等速增长。
      断言:终态 rank-size 分布在 log-log 上线性,斜率≈−1(容差 0.15);
      对照臂全部城市规模几乎相同(极差比≈1)。
      点题:城市层级不是规划的产物,是比例增长的统计必然——
      需要解释的是偏离 −1 的部分,不是层级的存在。

跑法: python -u experiments/space_and_city.py
"""

import math
import random
import statistics

# ==================== 幕一:Moran's I 的两副面孔 ====================

N_SIDE = 20          # 20×20 网格
N_CELLS = N_SIDE * N_SIDE


def build_rook_neighbors(side):
    """Rook 邻接(上下左右)的邻居表与无向边表。"""
    neigh = []
    edges = []
    for r in range(side):
        for c in range(side):
            i = r * side + c
            ns = []
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < side and 0 <= cc < side:
                    ns.append(rr * side + cc)
            neigh.append(ns)
    for i in range(side * side):
        for j in neigh[i]:
            if j > i:
                edges.append((i, j))
    return neigh, edges


NEIGH, EDGES = build_rook_neighbors(N_SIDE)


def morans_i(vals):
    """二元/连续值通用 Moran's I(对称二元 W,Rook 邻接)。

    I = (n/S0)·Σ_ij w_ij·(x_i−x̄)(x_j−x̄) / Σ_i(x_i−x̄)²;Σ_ij 对
    有序对求和=2×Σ_边。S0=Σ_ij w_ij=2×边数。
    """
    n = len(vals)
    xbar = sum(vals) / n
    z = [v - xbar for v in vals]
    den = sum(zi * zi for zi in z)
    num = 0.0
    for i, j in EDGES:
        num += z[i] * z[j]
    num *= 2.0
    s0 = 2.0 * len(EDGES)
    return (n / s0) * num / den


def local_same(vals, i):
    """格子 i 与邻居同类的边数(局部同配数)。"""
    return sum(1 for k in NEIGH[i] if vals[k] == vals[i])


def make_assortative(seed, swaps):
    """相邻同类偏好生成:随机 50/50 起步,随机挑异类格对做贪心交换
    (交换后两格局部同配数之和不减则接受)——Schelling 式微观偏好
    涌现宏观隔离的最小版。"""
    rng = random.Random(seed)
    vals = [0] * (N_CELLS // 2) + [1] * (N_CELLS // 2)
    rng.shuffle(vals)
    idx0 = [i for i, v in enumerate(vals) if v == 0]
    idx1 = [i for i, v in enumerate(vals) if v == 1]
    for _ in range(swaps):
        i = idx0[rng.randrange(len(idx0))]
        j = idx1[rng.randrange(len(idx1))]
        pre = local_same(vals, i) + local_same(vals, j)
        vals[i], vals[j] = vals[j], vals[i]
        post = local_same(vals, i) + local_same(vals, j)
        if post >= pre:                       # 接受交换
            idx0[idx0.index(i)], idx1[idx1.index(j)] = j, i
        else:                                 # 回滚
            vals[i], vals[j] = vals[j], vals[i]
    return vals


def make_random_scatter(seed):
    """对照:同比例(各 50%)随机散布,无任何相邻偏好。"""
    rng = random.Random(seed)
    vals = [0] * (N_CELLS // 2) + [1] * (N_CELLS // 2)
    rng.shuffle(vals)
    return vals


def perm_test(vals, obs_i, reps, seed):
    """随机置换检验:打乱格值(保比例)reps 次构造零分布,单侧 p 值。"""
    rng = random.Random(seed)
    ge = 0
    for _ in range(reps):
        rng.shuffle(vals)
        if morans_i(vals) >= obs_i:
            ge += 1
    return (1 + ge) / (reps + 1), ge


def act1():
    print("=" * 84)
    print("幕一 Moran's I 的两副面孔:隔离不是印象,是有签名的统计量")
    print("=" * 84)
    n_same_edges = lambda v: sum(1 for i, j in EDGES if v[i] == v[j])
    print(f"\n20×20 网格({N_CELLS} 格,A/B 各 {N_CELLS // 2}),Rook 邻接,"
          f"无向边 {len(EDGES)} 条;I∈[−1,1],0=随机")

    vals_a = make_assortative(seed=20260901, swaps=120_000)
    i_a = morans_i(vals_a)
    same_a = n_same_edges(vals_a)
    vals_r = make_random_scatter(seed=20260903)
    i_r = morans_i(vals_r)
    same_r = n_same_edges(vals_r)

    print(f"\n{'格局':<12} {'同类边占比':>10} {'Moran I':>9}")
    print(f"{'同配生成':<12} {same_a / len(EDGES):>10.1%} {i_a:>9.3f}")
    print(f"{'随机散布':<12} {same_r / len(EDGES):>10.1%} {i_r:>9.3f}")

    reps = 1000
    p_a, ge_a = perm_test(list(vals_a), i_a, reps, seed=20260911)
    p_r, ge_r = perm_test(list(vals_r), i_r, reps, seed=20260912)
    print(f"\n置换检验({reps} 次打乱格值构造零分布):")
    print(f"  同配格局:p = {p_a:.4f}(零分布中 ≥I_obs 的 {ge_a} 次)→ 签名显著")
    print(f"  随机格局:p = {p_r:.3f}(≥I_obs 的 {ge_r} 次)→ 与随机无异")

    print("\n读数:")
    print("  · 同样 50/50 的比例,格局天差地别:比例(多样性)≠隔离(格局)")
    print("  · 『这个城市很隔离』从修辞变成统计量:可跟踪、可比较、可问责")
    print("  · 经典独立假设对空间数据失效(Tobler 第一定律)——空间数据")
    print("    的显著性先过置换检验这道闸(00 章第一争)")
    print("  · 刀口提醒:I 依赖单元与邻接定义(MAUP),跨研究比较先对刀口")

    assert i_a > 0.6, f"同配格局 I={i_a:.3f} 应 >0.6"
    assert p_a < 0.01, f"同配格局置换 p={p_a:.4f} 应 <0.01"
    assert abs(i_r) < 0.05, f"随机格局 I={i_r:.3f} 应 |I|<0.05"
    assert p_r > 0.05, f"随机格局置换 p={p_r:.3f} 应不显著(>0.05)"
    assert same_a > same_r, "同配格局同类边占比应高于随机"
    print(f"\n✓ 幕一断言通过:同配 I={i_a:.3f}>0.6 且 p={p_a:.4f}<0.01;"
        f"随机 I={i_r:.3f}(|I|<0.05)且不显著——隔离的签名成立")
    return i_a, i_r, p_a


# ================ 幕二:邻里效应的剂量-距离饱和 ================

L_SIDE = 101          # 场域边长
PATCH_C = (50, 50)    # 好邻里圆斑圆心
PATCH_R = 10          # 圆斑半径(好邻里物理范围)
WINDOW = 25           # 个体活动窗 W(最大采样半径,固定)
BETA = 1.0            # 邻里效应强度


def quality(cx, cy):
    """环境质量场:圆斑内 1(好邻里),斑外 0。预生成格心坐标表。"""
    return 1 if math.hypot(cx - PATCH_C[0], cy - PATCH_C[1]) <= PATCH_R else 0


def dose_at(hx, hy, lam):
    """个体的加权邻里质量(剂量):Q_λ = Σ_{d≤W} w(d)·q / N_W,
    w(d)=1/(1+d/λ);N_W=活动窗内格子数(固定分母→λ 只调权重陡度)。"""
    n_w = 0
    q = 0.0
    for dx in range(-WINDOW, WINDOW + 1):
        for dy in range(-WINDOW, WINDOW + 1):
            d = math.hypot(dx, dy)
            if d <= WINDOW:
                n_w += 1
                q += quality(hx + dx, hy + dy) / (1.0 + d / lam)
    return q / n_w


def act2():
    print("\n" + "=" * 84)
    print("幕二 邻里效应的剂量-距离饱和:搬家改变暴露,但暴露有半径")
    print("=" * 84)
    print(f"\n场域 {L_SIDE}×{L_SIDE};好邻里=半径 {PATCH_R} 圆斑;"
          f"活动窗 W={WINDOW};w(d)=1/(1+d/λ);β={BETA}")

    home_new = PATCH_C          # 迁入好邻里圆心
    home_old = (5, 5)           # 留守角点(活动窗内无好格)
    lam_grid = [0.5, 1, 2, 3, 5, 8, 12, 18, 25, 40, 60, 90]
    q_inf = dose_at(*home_new, lam=10 ** 9)   # 饱和值(权重全 1)
    print(f"\n确定论剂量扫描(迁入圆斑中心 vs 留守角点):")
    print(f"{'λ':>5} {'Q_λ(迁入)':>10} {'Q_λ(留守)':>10} {'收益=βΔQ':>9}")
    q_new = {}
    for lam in lam_grid:
        qn = dose_at(*home_new, lam)
        qo = dose_at(*home_old, lam)
        q_new[lam] = qn
        print(f"{lam:>5} {qn:>10.4f} {qo:>10.4f} {BETA * (qn - qo):>9.4f}")
    print(f"{'∞':>5} {q_inf:>10.4f} {'0.0000':>10} {BETA * q_inf:>9.4f}(饱和)")

    # 半效应尺度 λ*:收益达饱和一半的 λ(对数插值)
    def q_of(lam):
        xs = [math.log(l) for l in lam_grid]
        ys = [q_new[l] for l in lam_grid]
        x = math.log(lam)
        for k in range(len(xs) - 1):
            if xs[k] <= x <= xs[k + 1]:
                t = (x - xs[k]) / (xs[k + 1] - xs[k])
                return ys[k] + t * (ys[k + 1] - ys[k])
        return ys[0] if x < xs[0] else ys[-1]

    lo, hi = lam_grid[0], lam_grid[-1]
    lam_star = None
    for k in range(60):
        mid = math.exp((math.log(lo) + math.log(hi)) / 2)
        if q_of(mid) < 0.5 * q_inf:
            lo = mid
        else:
            hi = mid
    lam_star = math.exp((math.log(lo) + math.log(hi)) / 2)
    print(f"\n半效应尺度 λ* ≈ {lam_star:.1f}(收益达饱和值一半的感受半径)")

    inc_1 = q_of(2 * lam_star) - q_of(lam_star)
    inc_2 = q_of(4 * lam_star) - q_of(2 * lam_star)
    print(f"增量对照:Q(λ*)→Q(2λ*) = +{inc_1:.4f} > "
          f"Q(2λ*)→Q(4λ*) = +{inc_2:.4f}(边际递减)")

    # 蒙特卡洛:个体结果 = 基线 + β×Q_λ + 噪声;组均值复现确定论形状
    rng = random.Random(20260921)
    m_per = 800
    noise_sd = 0.4
    print(f"\n蒙特卡洛加噪(每组 {m_per} 人,噪声 σ={noise_sd}):")
    print(f"{'λ':>5} {' noisy 组均收益':>14} {'确定论 βQ':>10} {'偏差':>8}")
    noisy = {}
    for lam in (2, 8, 20, 90):
        s = 0.0
        for _ in range(m_per):
            s += BETA * q_of(lam) + rng.gauss(0.0, noise_sd) \
                 - (BETA * q_of(2))                   # 相对 λ=2 的组均增益
        noisy[lam] = s / m_per
        det = BETA * (q_of(lam) - q_of(2))
        print(f"{lam:>5} {noisy[lam]:>14.4f} {det:>10.4f} "
              f"{noisy[lam] - det:>8.4f}")
    se = noise_sd / math.sqrt(m_per)

    print("\n读数:")
    print("  · 收益随感受半径 λ 严格上升但边际递减——存在半效应尺度 λ*:")
    print("    λ 之内贡献过半,λ 之外锦上添花(『邻里多大』可被参数化)")
    print("  · 留守者(窗内无好格)收益恒 0:隔一条感受边界的『好街区』")
    print("    只是背景板——搬家的疗效=剂量的函数,不是地址的函数")
    print("  · 加噪后组均值仍贴确定论曲线(大数定律):个体不可预测,")
    print("    剂量-距离关系可预测——搬家试验『儿童期效应强、成人弱』")
    print("    的机制读法之一即有效半径与时间窗不同(01 章主线 A)")

    assert lam_grid[0] < lam_star < lam_grid[-1], "λ* 应落在扫描区间内部"
    assert all(q_new[b] > q_new[a] for a, b in zip(lam_grid, lam_grid[1:])), \
        "确定论剂量应随 λ 严格上升"
    assert 0 < inc_2 < inc_1, "边际递减:后段增量应严格小于前段"
    assert dose_at(*home_old, lam=8) == 0.0, "留守者活动窗内应无好格(收益 0)"
    for lam in (2, 8, 20, 90):
        det = BETA * (q_of(lam) - q_of(2))
        assert abs(noisy[lam] - det) < 4 * se, \
            f"λ={lam}:加噪组均收益应贴确定论(±4σ/√m)"
    assert abs(q_new[90] - q_inf) < 0.02, "λ=90 应接近饱和"
    print(f"\n✓ 幕二断言通过:剂量随 λ 严格上升且边际递减"
        f"(增量 {inc_1:.4f}>{inc_2:.4f});λ*≈{lam_star:.1f} 落在区间内;"
        f"留守者收益 0;加噪组均值贴确定论曲线(±4σ/√m 内)")
    return lam_star, q_inf


# ================ 幕三:齐普夫层级与 Gibrat 生成机制 ================

N_CITY = 100
T_PERIODS = 500
S0_CITY = 1000.0


def gibrat_run(seed, sigma, reflect=True):
    """Gibrat 比例增长:S←S·e^g,g~N(0,σ²) 与规模无关;
    反射壁(Gabaix):S 不低于初始规模。返回终态规模表。"""
    rng = random.Random(seed)
    sizes = [S0_CITY] * N_CITY
    for _ in range(T_PERIODS):
        for k in range(N_CITY):
            g = rng.gauss(0.0, sigma)
            s = sizes[k] * math.exp(g)
            if reflect:
                s = max(s, S0_CITY)
            sizes[k] = s
    return sizes


def rank_size_slope(sizes):
    """log(规模) 对 log(位序) 的 OLS 斜率(降序)。"""
    ss = sorted(sizes, reverse=True)
    xs = [math.log(r + 1) for r in range(len(ss))]
    ys = [math.log(s) for s in ss]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sxy / sxx
    a = my - b * mx
    r2 = (sxy ** 2) / (sxx * sum((y - my) ** 2 for y in ys))
    return b, a, r2


def act3():
    print("\n" + "=" * 84)
    print("幕三 齐普夫城市层级与 Gibrat:层级是比例增长的统计必然")
    print("=" * 84)
    sigma = 0.07
    print(f"\n{N_CITY} 个同规模城市(初始 {S0_CITY:.0f}),"
          f"{T_PERIODS} 期对数正态比例增长"
          f"(g~N(0,{sigma}²),与规模无关;Gabaix 反射壁)")

    sizes = gibrat_run(seed=20260935, sigma=sigma, reflect=True)
    b, a, r2 = rank_size_slope(sizes)
    top = sorted(sizes, reverse=True)[:5]
    lo5 = sorted(sizes)[:5]
    print(f"\n终态:前 5 名规模 {[f'{s:,.0f}' for s in top]};"
          f"后 5 名 {[f'{s:,.0f}' for s in lo5]}")
    print(f"最大/最小 = {max(sizes) / min(sizes):,.1f} 倍;"
          f"规模标差 {statistics.stdev(sizes):,.0f}")
    print(f"rank-size 回归:log(S) = {a:.3f} + ({b:.3f})·log(rank),"
          f"R² = {r2:.3f}")
    print(f"齐普夫参照:斜率 = −1;偏差 |b−(−1)| = {abs(b + 1):.3f}"
          f"(容差 0.15)")

    # 对照:无随机差异的等速增长(每期同一增长率作用于所有城市)
    sizes_c = [S0_CITY] * N_CITY
    rng = random.Random(20260932)
    for _ in range(T_PERIODS):
        g = rng.gauss(0.0, sigma)          # 每期共同的增长率,城市间无差异
        for k in range(N_CITY):
            sizes_c[k] = max(sizes_c[k] * math.exp(g), S0_CITY)
    ratio_c = max(sizes_c) / min(sizes_c)
    print(f"\n对照臂(等速增长,无随机差异):最大/最小 = {ratio_c:.6f},"
          f"标差 {statistics.stdev(sizes_c):.2e}——全部城市几乎同规模")

    print("\n读数:")
    print("  · 等规模起步+比例增长,500 期自己长出斜率≈−1 的层级——")
    print("    城市层级不需要设计师,只需要『增长率与规模无关』+随机差异")
    print("  · 对照臂(去掉随机差异)层级消失:分化的引擎是增长率的")
    print("    随机差异本身,不是增长本身")
    print("  · 正确的提问法:层级(-1)是背景,待解释的是偏离——")
    print("    哪个城市的规模显著高于位序-规模直线的预测(实验幕三的")
    print("    残差=城市研究的起点)")
    print("  · Gabaix 1999(QJE)证明:比例增长+反射壁→稳态分布即齐普夫——")
    print("    斜率 −1 是数学定理的输出,不是规划的成果")

    assert abs(b - (-1.0)) < 0.15, f"斜率 {b:.3f} 应≈−1(容差 0.15)"
    assert r2 > 0.9, f"log-log 线性度 R²={r2:.3f} 应>0.9"
    assert max(sizes) / min(sizes) > 50, "Gibrat 臂应长出量级分化"
    assert ratio_c < 1.001, "等速对照臂应几乎无分化(极差比≈1)"
    assert statistics.stdev(sizes_c) < 1e-3, "对照臂规模标差应≈0"
    print(f"\n✓ 幕三断言通过:斜率 {b:.3f}≈−1(偏差 {abs(b + 1):.3f}<0.15,"
        f"R²={r2:.3f});对照臂极差比 {ratio_c:.6f}≈1——"
        f"层级是比例增长的统计必然")
    return b, r2


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口(三律):")
    print("  ① 隔离的签名:同配格局 Moran's I>0.6 且置换检验 p<0.01;")
    print("     同比例随机散布 |I|<0.05 且不显著——比例≠隔离,格局可检验")
    print("  ② 暴露有半径:迁入好邻里的收益随感受半径 λ 上升但边际递减,")
    print("     存在半效应尺度 λ*;留守者收益恒 0;加噪组均值贴确定论曲线")
    print("  ③ 层级的必然:100 城 500 期对数正态比例增长→rank-size 斜率")
    print("     ≈−1(Gibrat→Zipf,Gabaix 1999 机制);等速对照层级消失")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
