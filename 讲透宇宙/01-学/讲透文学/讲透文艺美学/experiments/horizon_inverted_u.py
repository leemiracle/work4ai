# -*- coding: utf-8 -*-
"""期待视野-倒U-经典化三律模拟:文艺美学家族实验(GB/T 75014)。

00-体系结构.md(§七反直觉三发现)、03-可构造与结构.md(两条结构引擎的
严格可构造性)、04-文艺美学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random),无第三方依赖;固定种子 20260907 可复现。

三幕:
  幕一 期待视野=贝叶斯更新,审美新奇=先验-后验偏移量(姚斯 1967 的算术版):
      读者带类型先验 e=(0.90,0.05,0.03,0.02)(K=4 题材:悬疑/世情/武侠/科幻),
      文本逐段给出题材证据;Dirichlet-多项式共轭更新,后验=(α·e+counts)/(α+m)。
      文本偏离度 λ:真值混合 θ_λ=(1-λ)e+λ·u(λ=0 复制品,λ=1 乱码,u 均匀)。
      新奇 = TV(后验, 先验);可读性 = 证据在先验下的几何平均预测概率;
      审美价值 ≈ 新奇×可读(03 章引擎 1 的骨架假设,显式声明)。
      断言:①λ=0(强证据支持先验)新奇≈0(无聊的复制品)
            ②λ=1 偏移最大但可读性崩塌(不可读——另一端失败)
            ③价值峰在 0<λ*<1 内点(熟悉的陌生有计算结构)。
  幕二 伯莱因倒 U 与时尚引擎(Berlyne 1971;暴露衰减):
      唤醒 A=新奇 n×复杂度 c,偏好 P(A)=exp(-k(A-A*)²)(倒 U,A*=0.5,k=30);
      重复暴露使感知新奇按 ρ^t 衰减(ρ=0.85,习惯化)。
      断言:①新鲜品偏好对新奇取内点峰;复杂度乘性折抵最优新奇(n*=A*/c)
            ②恰在峰值的新品暴露后单调跌落(昨日最优今日最受伤);
              当年太新的品(0.9)先升后降(滑向峰值再滑离)——非单调轨迹
            ③逐季最优新奇 n*_t=A*/ρ^t 单调上涨,第 5 季烧穿新奇尺度(>1)
              ——每次满足都为下一次厌倦付费(时尚的引擎)。
  幕三 经典化的幸存者过滤器(姚斯接受史的统计补完):
      M=4000 部作品各带真质量 q~N(0.5,0.20);每代评论打分 s=q+ε(ε~N(0,0.15)),
      s<τ=0.5 淘汰,幸存者进入下一代,共 8 代。
      断言:①8 代幸存集均值真质 ≫ 1 代幸存集(世代过滤收紧样本)
            ②幸存者筛选时表观分>均值真值(被噪声抬进门的虚高),
              而重新盲评回落到真值(均值回归)
            ③幸存集均值远高于总体均值——用幸存集估计「当代平均质量」
              是幸存者偏差(今人读到的经典是被时间选过的样本)。

跑法: python3 -u experiments/horizon_inverted_u.py
"""

import math
import random

SEED = 20260907  # 检索校准日作种子,可复现

# ==================== 幕一:期待视野=贝叶斯更新 ====================

K = 4
GENRES = ("悬疑", "世情", "武侠", "科幻")
PRIOR = (0.90, 0.05, 0.03, 0.02)      # 读者的类型先验(期待视野):重口味悬疑读者
UNIFORM = (0.25, 0.25, 0.25, 0.25)
ALPHA = 80.0                          # Dirichlet 先验强度(视野的顽固度)
M_SEG = 80                            # 每部文本的段落数(证据量)
REPS = 40                             # 每个 λ 独立生成 40 部文本取平均(压单样本噪声)


def tv_dist(p, q):
    """全变差距离 TV(p,q)=0.5·Σ|pᵢ-qᵢ|——先验-后验偏移量(审美新奇)。"""
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q))


def sample_counts(rng, theta, m):
    """从题材混合 θ 抽 m 段证据,返回各题材计数。"""
    counts = [0] * K
    for _ in range(m):
        u, acc = rng.random(), 0.0
        for i in range(K):
            acc += theta[i]
            if u < acc:
                counts[i] += 1
                break
        else:
            counts[K - 1] += 1
    return counts


def posterior(counts):
    """Dirichlet-多项式共轭:后验均值=(α·先验+计数)/(α+m)。"""
    return [(ALPHA * PRIOR[i] + counts[i]) / (ALPHA + M_SEG) for i in range(K)]


def readability(counts):
    """可读性=证据在先验下的几何平均预测概率 exp(Σ fₖ·ln eₖ)。"""
    m = sum(counts)
    return math.exp(sum((counts[i] / m) * math.log(PRIOR[i]) for i in range(K)))


def text_mix(lam):
    """文本真值混合:θ_λ=(1-λ)·先验+λ·均匀。λ=0 复制品,λ=1 乱码。"""
    return tuple((1 - lam) * PRIOR[i] + lam * UNIFORM[i] for i in range(K))


def act1():
    print("=" * 84)
    print("幕一 期待视野=贝叶斯更新:新奇=先验-后验偏移,价值=新奇×可读")
    print("=" * 84)
    rng = random.Random(SEED)
    print(f"\n读者先验(期待视野)e = {PRIOR}(题材 {GENRES}, α={ALPHA:.0f}, 每文本 {M_SEG} 段)")
    print(f"文本偏离度 λ:θ_λ=(1-λ)·e+λ·均匀;每个 λ 生成 {REPS} 部文本取平均\n")
    print(f"{'λ':>4} {'新奇(TV)':>9} {'可读性':>8} {'价值=新奇×可读':>14}   读数")

    stats = {}
    for i in range(11):
        lam = i / 10.0
        novs, reads = [], []
        for _ in range(REPS):
            counts = sample_counts(rng, text_mix(lam), M_SEG)
            novs.append(tv_dist(posterior(counts), PRIOR))
            reads.append(readability(counts))
        nov = sum(novs) / REPS
        rd = sum(reads) / REPS
        stats[lam] = (nov, rd, nov * rd)
        note = {0.0: "复制品:强证据支持先验,信念不动", 1.0: "乱码:偏移最大,但可读性崩塌"}.get(lam, "")
        print(f"{lam:>4.1f} {nov:>9.3f} {rd:>8.3f} {nov * rd:>14.4f}   {note}")

    lam_star = max(stats, key=lambda l: stats[l][2])
    print("\n读数:")
    print("  · λ=0:证据恰按先验比例到来,后验≈先验,新奇≈0——精确喂饱视野的复制品")
    print("  · λ=1:四题材等概率涌来,信念被拉向均匀(偏移最大),但每段都在先验的")
    print("    低概率区(可读性=几何平均预测概率)——不可读,另一端失败")
    print(f"  · 价值峰在 λ*={lam_star:.1f}(内点):熟悉给出可读性,陌生给出新奇,")
    print("    乘积在中等偏离处最大——「熟悉的陌生」有计算结构")

    # 断言一:三律
    assert stats[0.0][0] < 0.05, f"复制品新奇应≈0,实测 {stats[0.0][0]:.3f}"
    assert stats[1.0][0] > 0.25, f"乱码偏移应大,实测 {stats[1.0][0]:.3f}"
    assert stats[1.0][1] < 0.2 * stats[0.0][1], "乱码可读性应崩塌(<复制品的 20%)"
    assert 0.2 < lam_star < 0.8, f"价值峰应在内点,实测 λ*={lam_star}"
    assert stats[lam_star][2] > 1.2 * stats[1.0][2], "峰值价值应显著高于乱码端"
    assert stats[lam_star][2] > 2.0 * stats[0.0][2], "峰值价值应显著高于复制品端"
    print(f"\n✓ 幕一断言通过:新奇 {stats[0.0][0]:.3f}(λ=0) → {stats[1.0][0]:.3f}(λ=1),"
          f"可读性 {stats[1.0][1]:.3f}<{0.2 * stats[0.0][1]:.3f};"
          f"价值峰 λ*={lam_star:.1f}——中等偏离最优,两端皆失败")

    # 展示:λ* 文本的逐段信念偏移(每 20 段一看)
    rng2, traj, cum = random.Random(SEED + 1), [], [0] * K
    for seg in range(1, M_SEG + 1):
        u, acc = rng2.random(), 0.0
        for i in range(K):
            acc += text_mix(0.5)[i]
            if u < acc:
                cum[i] += 1
                break
        else:
            cum[K - 1] += 1
        if seg % 20 == 0:
            post = [(ALPHA * PRIOR[i] + cum[i]) / (ALPHA + seg) for i in range(K)]
            traj.append(tv_dist(post, PRIOR))
    print(f"\nλ=0.5 单部文本的逐段更新(每 20 段一读):新奇 "
          + " → ".join(f"{v:.3f}" for v in traj))
    print("  证据逐段累积,信念被一步步拉离先验——阅读即贝叶斯过程的最小演出")


# ==================== 幕二:伯莱因倒 U 与时尚引擎 ====================

RHO, ASTAR, K_DOME = 0.85, 0.5, 30.0  # 习惯化速率 / 最优唤醒 / 倒 U 陡度


def preference(n, c=1.0, t=0):
    """偏好=倒 U:exp(-k(A-A*)²),A=感知新奇 ρ^t·n × 复杂度 c。"""
    arousal = (RHO ** t) * n * c
    return math.exp(-K_DOME * (arousal - ASTAR) ** 2)


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 伯莱因倒 U 与时尚引擎(P=exp(-{K_DOME:.0f}(A-{ASTAR})²),暴露衰减 ρ={RHO})")
    print("=" * 84)

    # 2a 新鲜品:偏好对新奇取内点峰;复杂度乘性折抵
    print("\n[2a] 新鲜品的倒 U(暴露 t=0):")
    grid = [0.05 * i for i in range(1, 20)]  # 0.05..0.95
    for c in (0.8, 1.0, 1.25):
        vals = [preference(n, c) for n in grid]
        n_star = max(range(len(grid)), key=lambda j: vals[j])
        print(f"  复杂度 c={c:<4} 最优新奇 n*={grid[n_star]:.2f}(理论 A*/c={ASTAR / c:.3f})"
              f"  P(峰)={vals[n_star]:.3f}")
    v_flat = [preference(n) for n in grid]
    n_peak = max(range(len(grid)), key=lambda j: v_flat[j])
    print(f"  c=1.0 两端: P(0.05)={v_flat[0]:.4f}, P(0.95)={v_flat[-1]:.4f}"
          f" —— 峰 P({grid[n_peak]:.2f})={v_flat[n_peak]:.3f}:太熟悉无聊,太陌生不可读")
    assert 0.3 < grid[n_peak] < 0.7, "倒 U 峰应在中等新奇"
    assert v_flat[0] < 0.05 * v_flat[n_peak] and v_flat[-1] < 0.05 * v_flat[n_peak], "两端应远低于峰"
    for c in (0.8, 1.25):
        vals = [preference(n, c) for n in grid]
        n_star = grid[max(range(len(grid)), key=lambda j: vals[j])]
        assert abs(n_star - ASTAR / c) <= 0.06, f"c={c} 的 n* 应≈A*/c(乘性折抵)"
    print("  ✓ 2a 断言通过:内点峰+两端塌陷;复杂度涨 25%,最优新奇按 1/c 折抵")

    # 2b 暴露轨迹:峰值品单调跌落;太新品先升后降
    print("\n[2b] 同一部作品的暴露轨迹(感知新奇 ρ^t·n 沿倒 U 滑动):")
    print(f"{'t':>3} {'P(0.50)':>9} {'P(0.90)':>9}   读数")
    L50, L90 = [], []
    for t in range(9):
        L50.append(preference(0.50, t=t))
        L90.append(preference(0.90, t=t))
    for t in (0, 2, 4, 6, 8):
        note = {0: "开局:0.50 在峰值,0.90 在右支(太新)",
                4: "0.50 已滑离峰;0.90 恰滑到峰值附近"}.get(t, "")
        print(f"{t:>3} {L50[t]:>9.3f} {L90[t]:>9.3f}   {note}")
    t_star_90 = max(range(9), key=lambda j: L90[j])
    print(f"  · 0.50:单调跌落,L₅={L50[5]:.3f}——昨日恰在峰值的品,今日最受伤")
    print(f"  · 0.90:先升后降,峰值出现在 t*={t_star_90}(ρ^t·0.9≈A*),"
          f"L₈={L90[8]:.3f}——「慢热」的算术真相")
    assert all(L50[t] > L50[t + 1] for t in range(8)), "峰值品应单调跌落"
    assert L50[5] < 0.12, f"峰值品第 5 次暴露应跌破 0.12,实测 {L50[5]:.3f}"
    assert 0 < t_star_90 < 8 and L90[t_star_90] > 0.95, "太新品应内点峰值(先升后降)"
    assert L90[8] < 0.2 * L90[t_star_90], "太新品最终也应跌落(过熟即无聊)"
    print(f"  ✓ 2b 断言通过:峰值品单调跌(L₅={L50[5]:.3f});"
          f"太新品 t*={t_star_90} 内点峰后跌——两条轨迹都是「满足为厌倦付费」")

    # 2c 时尚引擎:逐季最优新奇单调上涨,第 5 季烧穿尺度
    print("\n[2c] 时尚引擎:每季观众要求的新鲜度 n*_t=A*/ρ^t:")
    seq = [ASTAR / RHO ** t for t in range(6)]
    for t, v in enumerate(seq):
        flag = "  ← 烧穿新奇尺度!" if v > 1.0 else ""
        print(f"  第 {t} 季 n*={v:.3f}{flag}")
    assert all(seq[t] < seq[t + 1] for t in range(5)), "最优新奇应逐季单调上涨"
    assert seq[4] >= 1.9 * seq[0], "第 4 季要求的新鲜度应≈首季的 1.9 倍"
    assert seq[5] > 1.0, "第 5 季应烧穿新奇尺度(>1)"
    print("  ✓ 2c 断言通过:昨日的新颖被暴露磨损为今日的熟悉,要维持同样的唤醒,"
          "只能逐季加码新奇,直到超出尺度——引擎最终要求换血")


# ==================== 幕三:经典化的幸存者过滤器 ====================

N_WORKS, MU_Q, SD_Q = 4000, 0.5, 0.20
SD_EPS, TAU, GENS = 0.15, 0.5, 8


def act3():
    print("\n" + "=" * 84)
    print(f"幕三 经典化的幸存者过滤器({N_WORKS} 部作品 × {GENS} 代评论,"
          f"q~N({MU_Q},{SD_Q}),噪声 N(0,{SD_EPS}),淘汰线 τ={TAU})")
    print("=" * 84)
    rng = random.Random(SEED)
    quality = [rng.gauss(MU_Q, SD_Q) for _ in range(N_WORKS)]
    alive = list(range(N_WORKS))
    pop_mean = sum(quality) / N_WORKS
    gate1 = None  # (幸存数, 均值真质, 均值表观分)

    print(f"\n{'代':>3} {'幸存数':>7} {'均值真质':>9} {'均值表观分':>10}")
    g8 = None
    for gen in range(1, GENS + 1):
        scores = {i: quality[i] + rng.gauss(0.0, SD_EPS) for i in alive}
        alive = [i for i in alive if scores[i] >= TAU]
        mean_q = sum(quality[i] for i in alive) / len(alive)
        mean_s = sum(scores[i] for i in alive) / len(alive)
        print(f"{gen:>3} {len(alive):>7} {mean_q:>9.3f} {mean_s:>10.3f}")
        if gen == 1:
            gate1 = (len(alive), mean_q, mean_s)
        if gen == GENS:
            g8 = (len(alive), mean_q, mean_s)
    g8_count, g8_mean_q, g8_mean_apparent = g8

    # 重新盲评:同一批幸存者,新评论重打分(无选择压力的独立测量)——应回落真值
    fresh = [quality[i] + rng.gauss(0.0, SD_EPS) for i in alive]
    fresh_mean = sum(fresh) / len(fresh)
    true_mean = g8_mean_q

    print(f"\n总体均值真质            : {pop_mean:.3f}")
    print(f"第 1 代幸存集({gate1[0]:>4} 部)均值真质: {gate1[1]:.3f}(表观分 {gate1[2]:.3f})")
    print(f"第 8 代幸存集({g8_count:>4} 部)均值真质: {true_mean:.3f}(表观分 {g8_mean_apparent:.3f})")
    print(f"第 8 代幸存集重新盲评均值: {fresh_mean:.3f}(无选择压力,回落到真质附近)")
    print("\n读数:")
    print("  · 8 代过滤后幸存集均值真质远高于 1 代——过滤器逐代收紧,留下的越来越")
    print("    是高真质+连续走运的样本;幸存率从 ~52% 掉到 ~18%")
    print("  · 第 1 代幸存者的表观分(0.70 左右)高于其均值真质(0.63 左右):被噪声")
    print("    抬进门的虚高;重新盲评(无选择压力)即回落到真值——均值回归")
    print("  · 幸存集均值(0.75+)与总体均值(0.50)之差≈0.25:今人读到的经典是被")
    print("    时间选过的样本,拿它估计「当代平均质量」是幸存者偏差")

    assert g8_mean_q > gate1[1] + 0.12, "8 代幸存集均值真质应远高于 1 代"
    assert g8_mean_q - pop_mean > 0.2, "幸存集均值远高于总体(幸存者偏差的量级)"
    assert gate1[2] > gate1[1] + 0.05, "第 1 代表观分应虚高于真值(噪声抬门)"
    assert g8_mean_apparent > true_mean + 0.005, "第 8 代筛选时表观分仍应虚高于真值"
    assert abs(fresh_mean - true_mean) < 0.02, "重新盲评应回落到真值附近"
    assert g8_count < 0.2 * N_WORKS, "8 代后幸存率应低于 20%"
    assert g8_count < 0.5 * gate1[0], "8 代幸存数应远少于 1 代"
    print(f"\n✓ 幕三断言通过:1 代→8 代均值真质 {gate1[1]:.3f}→{g8_mean_q:.3f}(+{g8_mean_q - gate1[1]:.2f});"
          f"总体→幸存 {pop_mean:.3f}→{g8_mean_q:.3f}(高估 {g8_mean_q - pop_mean:.2f});"
          f"盲评回落 |{fresh_mean:.3f}-{true_mean:.3f}|<0.02——经典=被时间选过的样本")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 期待视野=贝叶斯先验,审美新奇=先验-后验偏移:复制品偏移≈0(无聊),")
    print("     乱码偏移最大而可读性崩塌(不可读),中等偏离处新奇×可读最大")
    print("     ——「熟悉的陌生」有计算结构(姚斯审美距离/形式主义陌生化的算术和解)")
    print("  ② 偏好对唤醒取倒 U,暴露使感知新奇 ρ^t 衰减:峰值品单调跌落,太新品先升")
    print("     后降,逐季最优新奇 A*/ρ^t 单调上涨直至烧穿尺度——时尚的引擎:")
    print("     每次满足都为下一次厌倦付费(伯莱因倒 U+暴露效应)")
    print("  ③ 经典化=世代过滤器:幸存集均值逐代收紧,筛选时表观虚高、盲评回落;")
    print("     幸存集均值远高于总体——用幸存集估计「当代平均质量」是幸存者偏差")
    print("     (今人读到的经典是被时间选过的样本)")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
