# -*- coding: utf-8 -*-
"""科学信任的结构模拟:两群体×信息环境(中性 vs 极化媒体)——
00/04 章配套实验,呼应 Cologna et al. 2025(Nature Human Behaviour,
《Trust in scientists across 68 countries》,检索校准 2026-09-07 素材包)
的"全球信任总体高但极化"结构:均值平稳而组间差扩大。

模型(零模型,非预测;个体信任 t∈[0,1]):
- 两个群体:高信任组 A / 低信任组 B(初始信任不同,均值对称于真相值)
- 每步个体收到信号:s = truth + amp_i·(组内均值−truth) + 噪声
  amp_i = base + exagg·χ_i(净放大系数),χ_i = 选择接触水平
  = min(1, sel·|t_i−truth| / d_ref)——信源选择机制:个体信念偏离
  真相越远,越多地只消费"本群体的媒体",而群体媒体对既有偏向
  净放大(回音室正反馈:偏离→选择接触→更强放大→更偏离)
    中性媒体:base=0(信号只反映真相,两组都收敛)
    极化媒体:base=1(群体媒体全反射)+ exagg>0 且 sel>0(选择接触
    使偏离个体的净放大升到 1+exagg)
    极化媒体·无选择接触:sel=0(χ≡0,净放大停在 1,组间差停滞)
- 公共危机事件:全体信任受同幅冲击(水平冲击);但低信任组本来就
  在真相下方,冲击在"偏离度"上主要落在低信任组头上;危机后进入
  修复期(信号中加入公共修复传播项),低信任组因"归因体制"对修复
  信号打折扣(attribution)——恢复不对称

三组断言:
  ① 总体均值掩盖极化:各环境下总体均值都平稳(±0.03),
     中性媒体组间差收敛(<40% 初值),极化媒体组间差扩大(>140%)
  ② 回音室机制:极化媒体下组间信任差逐步严格单调扩大;
     同样极化媒体下去掉选择接触,组间差停滞(选择接触反馈
     是分化的发动机)
  ③ 危机不对称恢复:公共危机后,高信任组恢复、低信任组不恢复
     反而下行,组间差超过危机前——危机放大既有分化

⚠ 史学纪律(02/04 章):这是零模型,不是历史重放;参数=史观,
外推任何真实国家的信任走势都是越权(04 章走廊三警告)。

跑法: python experiments/trust_polarization.py
"""
import random

# ── 全局参数(改动即新史观,引用结果必附参数)─────────────────────
SEED = 20260907
N_PER_GROUP = 400          # 每组人数(有限群体涨落 << 系统性漂移)
TRUTH = 0.70               # 可观察的真相值(两组共享同一科学)
LR = 0.12                  # 个体更新率
NOISE = 0.03               # 信号噪声 σ
INIT_A, INIT_B, INIT_SD = 0.80, 0.60, 0.06   # 两组初始均值(对称于真相)/组内标准差
DIV_STEPS = 40             # 分化期步数
SHOCK = 0.18               # 公共危机冲击(水平等幅)
REC_STEPS = 20             # 修复期步数
CAMPAIGN = 0.02            # 修复期公共传播项(加入信号)
ATTR_B = 0.20              # 低信任组对修复信号的接受折扣(归因体制)
D_REF = 0.35               # 选择接触饱和参考偏离(个体偏离达到 sel 分之该值即满格)

# 环境参数化:中性媒体 / 极化媒体 / 极化媒体但无选择接触(敏感性)
ENV_NEUTRAL = dict(base=0.0, exagg=0.0, sel=0.0)
ENV_POLAR = dict(base=1.0, exagg=0.22, sel=2.0)
ENV_POLAR_NOSEL = dict(base=1.0, exagg=0.22, sel=0.0)


def clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def make_groups(rng):
    """对称初始化:两组均值对称于真相,个体重采样至 [0.02,0.98] 防截断。"""
    groups = {}
    for name, mu in (("A", INIT_A), ("B", INIT_B)):
        vals = []
        while len(vals) < N_PER_GROUP:
            v = rng.gauss(mu, INIT_SD)
            if 0.02 <= v <= 0.98:
                vals.append(v)
        groups[name] = vals
    return groups


def step(groups, env, rng, campaign=0.0, accept=None):
    """推进一步:信号=真相+净放大×组偏离+噪声+(修复期)公共传播×接受度。"""
    means = {g: sum(v) / len(v) for g, v in groups.items()}
    for g, vals in groups.items():
        acc = 1.0 if accept is None else accept[g]
        gm, d_g = means[g], means[g] - TRUTH
        for i, t in enumerate(vals):
            # 选择接触:个体偏离越大,越多只消费本群体媒体(χ→1)
            chi = min(1.0, env["sel"] * abs(t - TRUTH) / D_REF) if env["sel"] else 0.0
            amp = env["base"] + env["exagg"] * chi
            s = TRUTH + amp * d_g \
                + rng.gauss(0.0, NOISE) + campaign * acc
            vals[i] = clamp01(t + LR * (clamp01(s) - t))
    return means


def series(groups, env, steps, rng, campaign=0.0, accept=None):
    """记录每步(总均值, A 均值, B 均值, 组间差)。"""
    out = []
    for _ in range(steps):
        step(groups, env, rng, campaign=campaign, accept=accept)
        ma = sum(groups["A"]) / N_PER_GROUP
        mb = sum(groups["B"]) / N_PER_GROUP
        out.append(((ma + mb) / 2.0, ma, mb, ma - mb))
    return out


def main():
    print("=" * 76)
    print("科学信任的结构模拟:两群体 × 信息环境(中性 vs 极化媒体)")
    print(f"参数:N={N_PER_GROUP}×2  truth={TRUTH}  初始 A={INIT_A}/B={INIT_B}"
          f"(对称)  分化{DIV_STEPS}步→危机{SHOCK}→修复{REC_STEPS}步")
    print("=" * 76)

    # ── 运行一:中性 / 极化 / 极化无选择接触(同种子对照)──────────
    runs = {}
    for label, env in (("neutral", ENV_NEUTRAL), ("polar", ENV_POLAR),
                       ("polar_nosel", ENV_POLAR_NOSEL)):
        rng = random.Random(SEED)                     # 每次同种子:可对照
        runs[label] = series(make_groups(rng), env, DIV_STEPS, rng)

    print(f"\n{'步':>4} | {'中性:总均值 组间差':>20} | {'极化:总均值 组间差':>20}"
          f" | {'极化无选择接触':>14}")
    for k in (0, 4, 9, 19, DIV_STEPS - 1):
        n, p, q = runs["neutral"][k], runs["polar"][k], runs["polar_nosel"][k]
        print(f"{k+1:>4} |   {n[0]:.3f}   {n[3]:+.3f}     |   {p[0]:.3f}   {p[3]:+.3f}"
              f"     |   {q[3]:+.3f}")

    # 断言 ①:总体均值掩盖极化(各环境均值都平稳,组间差方向相反)
    for label in ("neutral", "polar", "polar_nosel"):
        means = [r[0] for r in runs[label]]
        assert max(means) - min(means) < 0.03, \
            f"断言①[{label}]:总体均值应平稳(±0.03 内)"
    gap0 = runs["polar"][0][3]
    gapN = runs["neutral"][-1][3]
    gapP = runs["polar"][-1][3]
    gap_no_sel = runs["polar_nosel"][-1][3]
    assert gapN < 0.4 * gap0, "断言①:中性媒体下组间差应收敛到 40% 以下"
    assert gapP > 1.4 * gap0, "断言①:极化媒体下组间差应扩大到 140% 以上"
    print(f"\n断言 ① 通过:各环境总均值都平稳(<±0.03)——组间差:中性 "
          f"{gap0:.3f}→{gapN:+.3f}(收敛) vs 极化 {gap0:.3f}→{gapP:.3f}(扩大) ✓")
    print("            ——总均值平稳恰恰可能掩盖极化(均值是最危险的读数)")

    # 断言 ②:回音室——极化下组间差严格单调扩大;选择接触是发动机
    gaps = [r[3] for r in runs["polar"]]
    assert all(g2 > g1 for g1, g2 in zip(gaps, gaps[1:])), \
        "断言②:极化媒体下组间差应逐步严格单调扩大"
    assert abs(gap_no_sel - gap0) < 0.05, \
        "断言②:无选择接触时组间差应停滞(媒体无法独力放大)"
    assert gapP > gap_no_sel + 0.08, \
        "断言②:有选择接触的分化应显著深于无选择接触"
    print(f"\n断言 ② 通过:极化下组间差 {DIV_STEPS} 步严格单调扩大 "
          f"({gaps[0]:.3f}→{gaps[-1]:.3f}) ✓")
    print(f"            选择接触敏感性:同媒体下去掉选择接触,组间差停在 "
          f"{gap_no_sel:.3f}(初值 {gap0:.3f})——"
          f"选择接触反馈贡献了全部净分化 ✓")

    # ── 运行二:危机实验(极化环境,分化 40 步后公共危机+修复期)──
    rng = random.Random(SEED)
    groups = make_groups(rng)
    pre = series(groups, ENV_POLAR, DIV_STEPS, rng)          # 危机前分化
    for g in groups:                                          # 危机:水平等幅冲击
        groups[g] = [clamp01(t - SHOCK) for t in groups[g]]
    crisis = {g: sum(v) / N_PER_GROUP for g, v in groups.items()}
    post = series(groups, ENV_POLAR, REC_STEPS, rng,          # 修复期
                  campaign=CAMPAIGN, accept={"A": 1.0, "B": ATTR_B})

    gap_pre = pre[-1][3]
    a_pre, b_pre = pre[-1][1], pre[-1][2]
    a_end, b_end = post[-1][1], post[-1][2]
    # 断言 ③:恢复不对称——A 恢复、B 不恢复反下行,组间差超危机前
    assert a_end > crisis["A"] + 0.03, \
        "断言③:高信任组危机后应恢复(+0.03 以上)"
    assert b_end < crisis["B"], \
        "断言③:低信任组危机后应不恢复(归因体制压低修复信号接受)"
    assert (a_end - crisis["A"]) - (b_end - crisis["B"]) > 0.08, \
        "断言③:两组恢复量之差应显著(不对称恢复)"
    assert post[-1][3] > gap_pre, \
        "断言③:危机后组间差应超过危机前(危机放大既有分化)"

    print(f"\n危机实验(冲击 -{SHOCK} 于全体,修复期公共传播×归因折扣 "
          f"A×1.0/B×{ATTR_B}):")
    print(f"  {'':<12}{'高信任组A':>10}{'低信任组B':>12}{'组间差':>9}")
    print(f"  {'危机前':<12}{a_pre:>10.3f}{b_pre:>12.3f}{gap_pre:>9.3f}")
    print(f"  {'危机后即时':<12}{crisis['A']:>10.3f}{crisis['B']:>12.3f}"
          f"{crisis['A']-crisis['B']:>9.3f}")
    print(f"  {'修复{0}步后'.format(REC_STEPS):<12}{a_end:>10.3f}{b_end:>12.3f}"
          f"{a_end-b_end:>9.3f}")
    print("断言 ③ 通过:A 恢复 "
          f"{a_end-crisis['A']:+.3f} / B {b_end-crisis['B']:+.3f}"
          f"(不对称),组间差 {gap_pre:.3f}→{a_end-b_end:.3f}(超危机前) ✓")
    print("            ——水平等幅的冲击落在偏离度上主要砸中低信任组,"
          "危机放大既有分化")

    print("\n" + "=" * 76)
    print("三组断言全部通过:均值掩盖极化 / 回音室单调分化 / 危机不对称恢复 ✓")
    print("\n⚠ 史学纪律:零模型非预测;参数=史观——本脚本解释结构"
          "(『为什么均值会骗人』),")
    print("  不预报任何国家的信任走势;真实数据的极化指数见 03 章 "
          "subgroup_means 纪律。")


if __name__ == "__main__":
    main()
