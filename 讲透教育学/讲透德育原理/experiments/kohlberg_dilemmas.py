# -*- coding: utf-8 -*-
"""道德两难的判断结构仿真:两难参数 × 被试发展阶段(科尔伯格式简化模型)。

00-体系结构.md(反直觉 1/2、美之时刻 2)、03-可构造与结构.md(引擎 1:
两难-理由引擎)与 04-德育原理转代码.md(走廊 1/2/3)的配套实验。
纯标准库(random+math)。

文献通说陈述(非检索校准,详见家族 00 章):
  · 科尔伯格 1958 年博士论文提出道德发展三水平六阶段(前习俗/习俗/后习俗),
    配套道德判断访谈;最有名的刺激材料即海因茨两难(妻子病危、药剂师抬价);
  · 计分方法论的核心决定:**结论不计分,理由结构才计分**——
    同一个"该偷/不该偷"可出自完全不同的阶段理由;
  · 道德推理测验分数与道德行为的典型相关弱(通说综述常引区间约 r≈0.2-0.3,
    「判断-行为差距」;Blasi 的道德认同与情境力量是两条主流解释线)。

模型(两难-理由引擎的最小编码):
  考量(value)六类:PUN 惩罚 / BEN 利害 / APP 他人认可 / LAW 法律秩序
                    / CON 契约公益 / UNI 普遍原则
  两难 = 受控的义务冲突,参数(life 关怀方强度, law 规范方强度):
    valence(PUN)=-0.54·law   valence(BEN)=+0.95·life
    valence(APP)=0.15+0.25·life  valence(LAW)=-1.00·law
    valence(CON)=+0.45·life   valence(UNI)=+0.95·life
    (海因茨经典形 = life=law=1.0;"违规救妻"方向取正)
  被试阶段 s∈{1..6} 各有一组考量权重 w_s(皮亚杰-科尔伯格谱系的参数化):
    阶段1 惩罚服从 / 2 工具利害 / 3 好孩子认可 / 4 法律秩序
    / 5 社会契约 / 6 普遍原则
  两个输出是**不同的函数**(阶段论的方法论心脏):
    结论 verdict(s,d) = sign( Σ_c w_s[c]·valence_d[c] )     → 对参数敏感
    理由 reason(s,d)  = argmax_c |w_s[c]·valence_d[c]|      → 对阶段敏感(显著性)

断言(自验):
  1) 理由结构≠结论:同一两难(经典海因茨)中,阶段1与阶段4结论同为「不该偷」
     而理由一为 PUN 一为 LAW;阶段2与阶段6结论同为「该偷」而理由一为 BEN
     一为 UNI;六阶段给出 6 种理由、仅 2 种结论。且结论随参数翻转而理由
     不动:阶段2(利害推理)在 life=0.15 时结论「不偷」(划不来)、
     life=1.0 时「偷」(值得),理由始终是 BEN——结论不含阶段信息,
     理由结构才含(科尔伯格计分规则的结构表达)。
  2) 推理-行为差距:仿真被试的「道德推理分数」R 与「道德行为」选择
     (诚实博弈/合作博弈)的 Pearson 相关在经验参数世界落在弱区间
     (0.15<r<0.45,与通说综述区间对表),而「推理决定行为」的理想世界
     r>0.7;情境权重加大,相关单调下降——相关是世界参数,不是逻辑必然。
  3) 测量效度条件:两难冲突强度(life↑,law=1 固定)越高,理由结构越可
     辨识——弱两难(life=0.15)时四个阶段的显著性理由塌缩为 LAW,
     理由→阶段解码正确率≈0.4;经典两难(1.0)时六理由互异,解码≈0.8。
     弱两难没有诊断力:两难设计先于测量设计。

跑法: python3 -u experiments/kohlberg_dilemmas.py
"""

import math
import random

SEED = 20260907

# ---- 六类考量 ----
VALUES = ("PUN", "BEN", "APP", "LAW", "CON", "UNI")
VALUE_CN = {"PUN": "惩罚后果", "BEN": "工具利害", "APP": "他人认可",
            "LAW": "法律秩序", "CON": "契约公益", "UNI": "普遍原则"}
STAGE_CN = {1: "前习俗·惩罚服从", 2: "前习俗·工具利害", 3: "习俗·好孩子",
            4: "习俗·法律秩序", 5: "后习俗·社会契约", 6: "后习俗·普遍原则"}

# ---- 六阶段的考量权重(谱系参数化:每阶段一个主导考量,余为弱混合) ----
STAGE_WEIGHTS = {
    1: {"PUN": 1.00, "BEN": 0.15, "APP": 0.05, "LAW": 0.10, "CON": 0.00, "UNI": 0.00},
    2: {"PUN": 0.25, "BEN": 1.00, "APP": 0.10, "LAW": 0.05, "CON": 0.05, "UNI": 0.00},
    3: {"PUN": 0.10, "BEN": 0.15, "APP": 1.00, "LAW": 0.30, "CON": 0.10, "UNI": 0.05},
    4: {"PUN": 0.15, "BEN": 0.10, "APP": 0.30, "LAW": 1.00, "CON": 0.25, "UNI": 0.10},
    5: {"PUN": 0.05, "BEN": 0.10, "APP": 0.10, "LAW": 0.40, "CON": 1.00, "UNI": 0.35},
    6: {"PUN": 0.00, "BEN": 0.05, "APP": 0.05, "LAW": 0.20, "CON": 0.40, "UNI": 1.00},
}

STAGES = (1, 2, 3, 4, 5, 6)


def dilemma(life, law):
    """构造两难:义务冲突的参数化(life=关怀方强度,law=规范方强度)。
    返回六类考量的 valence(「违规救妻」方向为正)。"""
    return {"PUN": -0.54 * law, "BEN": 0.95 * life, "APP": 0.15 + 0.25 * life,
            "LAW": -1.00 * law, "CON": 0.45 * life, "UNI": 0.95 * life}


def verdict(stage, d):
    """结论:加权符号(+1 该违规救妻 / -1 不该)——对情境参数敏感。"""
    score = sum(STAGE_WEIGHTS[stage][c] * d[c] for c in VALUES)
    return 1 if score > 0.0 else -1


def reason(stage, d):
    """理由:显著性最大的考量(绝对贡献 argmax)——对发展阶段敏感。
    (阶段2的利害推理在结论翻转时仍谈利害:「划不来」与「值得」同构。)"""
    return max(VALUES, key=lambda c: abs(STAGE_WEIGHTS[stage][c] * d[c]))


def pearson(xs, ys):
    """Pearson 相关系数(y 为 0/1 时即点二列相关)。"""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy)


def behavior_study(n, a, b, c_situ, seed):
    """仿真 n 名被试:推理分数 R 与行为选择(诚实博弈)的相关。
    行为潜变量 = a·R(推理耦合) + b·E(特质/移情) + c_situ·S(情境诱惑),
    阈值化成 0/1 选择。返回 (R, honest)。"""
    rng = random.Random(seed)
    rs, honest = [], []
    for _ in range(n):
        r = rng.gauss(0.0, 1.0)
        e = rng.gauss(0.0, 1.0)
        s = rng.gauss(0.0, 1.0)
        rs.append(r)
        honest.append(1 if a * r + b * e + c_situ * s > 0.0 else 0)
    return rs, honest


def decode_study(life, m_per_stage, fidelity, seed):
    """理由→阶段解码实验:m 名被试/阶段,以概率 fidelity 说出本阶段显著性
    理由,否则均匀随机说其余五类考量;解码器按「该两难下的显著性理由→
    最小阶段」查表。返回解码正确率与(无噪声的)理由分布。"""
    d = dilemma(life, 1.0)
    modal = {s: reason(s, d) for s in STAGES}
    key = {}
    for s in STAGES:                       # 查表:理由 → 首个引用它的阶段
        key.setdefault(modal[s], s)
    rng = random.Random(seed)
    correct = 0
    for s in STAGES:
        for _ in range(m_per_stage):
            if rng.random() < fidelity:
                stated = modal[s]
            else:
                stated = rng.choice([c for c in VALUES if c != modal[s]])
            if key.get(stated, -1) == s:
                correct += 1
    total = m_per_stage * len(STAGES)
    return correct / total, modal


def entropy(pk):
    """香农熵(nats),用于结论分布的信息量侧写。"""
    n = sum(pk)
    return -sum((k / n) * math.log(k / n) for k in pk if k > 0)


def main():
    heinz = dilemma(1.0, 1.0)

    print("=" * 88)
    print("科尔伯格式两难的判断结构:结论=对参数敏感,理由=对阶段敏感")
    print(f"参数:经典海因茨两难(life=law=1.0),六阶段×六考量,seed={SEED}")
    print("=" * 88)

    # ---- 断言 1 的现场:六阶段 × (结论, 理由) ----
    print(f"\n{'阶段':<14} {'结论':<6} {'理由':<8} {'理由类别'}")
    verdicts = {s: verdict(s, heinz) for s in STAGES}
    reasons = {s: reason(s, heinz) for s in STAGES}
    for s in STAGES:
        v = "该偷" if verdicts[s] > 0 else "不该偷"
        print(f"{STAGE_CN[s]:<14} {v:<6} {reasons[s]:<8} {VALUE_CN[reasons[s]]}")
    print("  读数:六个阶段只有 2 种结论(该偷/不该偷),理由却有 6 种——")
    print("        阶段1与阶段4都说「不该偷」(怕被抓 vs 法不可违);")
    print("        阶段2与阶段6都说「该偷」(划得来 vs 生命高于财产法)。")
    print("        结论不含阶段信息,理由结构才含——计分只看理由。")

    # ---- 断言 1 的另一侧:结论随参数翻转,理由不动 ----
    print("\n结论对参数敏感(阶段2·工具利害推理):")
    for life in (0.15, 0.20, 1.00):
        d = dilemma(life, 1.0)
        v = "该偷" if verdict(2, d) > 0 else "不偷"
        print(f"  life={life:<5} law=1.0 → 结论「{v}」,理由仍是 "
              f"{reason(2, d)}({VALUE_CN[reason(2, d)]})")
    print("  读数:利害一变结论就翻,「划不来→不偷」与「值得→偷」是同一种")
    print("        推理结构——理由类别稳定,这正是阶段属性的测量学含义。")

    # ---- 断言 2:推理-行为差距 ----
    n_sub = 8000
    print(f"\n推理-行为差距:道德推理分数 R 与行为选择的相关(n={n_sub})")
    rs, honest = behavior_study(n_sub, a=0.30, b=0.55, c_situ=0.50, seed=SEED)
    r_main = pearson(rs, honest)
    rng2 = random.Random(SEED + 1)
    rs2 = [rng2.gauss(0.0, 1.0) for _ in range(n_sub)]
    coop = [1 if 0.25 * r + 0.35 * rng2.gauss(0.0, 1.0) + 0.70 * rng2.gauss(0.0, 1.0) > 0
            else 0 for r in rs2]
    r_coop = pearson(rs2, coop)
    rs3, honest3 = behavior_study(n_sub, a=1.00, b=0.10, c_situ=0.10, seed=SEED + 2)
    r_ideal = pearson(rs3, honest3)
    print(f"{'世界':<12} {'耦合a':>6} {'情境c':>6} {'相关r':>8}")
    for name, a, c, r in (("诚实·经验世界", 0.30, 0.50, r_main),
                          ("合作·经验世界", 0.25, 0.70, r_coop),
                          ("理想·推理决定行为", 1.00, 0.10, r_ideal)):
        print(f"{name:<12} {a:>6.2f} {c:>6.2f} {r:>8.3f}")
    print("  读数:经验世界的推理-行为相关落在弱区间(与通说综述 r≈0.2-0.3 对表);")
    print("        理想世界(推理决定行为)相关>0.7——差距是世界的参数结构,")
    print("        不是测量的偶然;只提升推理的德育,买到的大约就是推理。")

    print("\n情境力量扫描(诚实博弈,a=0.30 固定,情境权重 c 上升):")
    situ_rows = []
    for c_situ in (0.30, 0.60, 0.90):
        r_avg = 0.0
        for rep in range(3):                     # 3 次重复平均,防单次抽样波动
            rs_r, hon_r = behavior_study(n_sub, 0.30, 0.55, c_situ, SEED + 10 + rep)
            r_avg += pearson(rs_r, hon_r)
        r_avg /= 3.0
        situ_rows.append((c_situ, r_avg))
        print(f"  情境权重 c={c_situ:.2f} → 平均相关 r={r_avg:.3f}")
    print("  读数:情境越有力,推理对行为的预测力越低(单调下降)——")
    print("        「情境力量」解释线与「道德认同」解释线的共同参数语言。")

    # ---- 断言 3:冲突强度与理由可辨识度 ----
    print("\n两难冲突强度 × 理由结构可辨识度(测量效度条件,law=1.0 固定):")
    print(f"{'life':>6} {'结论分布(该偷/不偷)':>16} {'理由分布':>10} {'解码正确率':>8}")
    ident_rows = []
    for life in (0.15, 0.35, 1.00):
        d = dilemma(life, 1.0)
        vs = [verdict(s, d) for s in STAGES]
        modal = {s: reason(s, d) for s in STAGES}
        n_steal = sum(1 for v in vs if v > 0)
        acc, _ = decode_study(life, m_per_stage=100, fidelity=0.8, seed=SEED + 100)
        distinct = len(set(modal.values()))
        ident_rows.append((life, distinct, acc, entropy([n_steal, 6 - n_steal])))
        print(f"{life:>6.2f} {('%d/%d' % (n_steal, 6 - n_steal)):>16} "
              f"{('%d 种' % distinct):>10} {acc:>8.3f}")
    print("  读数:弱两难(life=0.15)人人答「不偷」,四个阶段的显著性理由")
    print("        塌缩成 LAW——理由失去判别力,解码率≈瞎猜之上不多;")
    print("        锋利两难(1.0)六理由互异,解码≈0.8。")
    print("        两难设计先于测量设计:冲突强度是测量的信度旋钮。")

    # ================= 断言(自验)=================
    # 断言 1:理由结构≠结论(同结论异理由;结论翻转变、理由不变)
    assert verdicts[1] == verdicts[4] == -1 and \
        reasons[1] == "PUN" and reasons[4] == "LAW", \
        "阶段1与4结论应同为『不该偷』而理由分别为 PUN/LAW"
    assert verdicts[2] == verdicts[6] == +1 and \
        reasons[2] == "BEN" and reasons[6] == "UNI", \
        "阶段2与6结论应同为『该偷』而理由分别为 BEN/UNI"
    assert len(set(reasons.values())) == 6 and len(set(verdicts.values())) == 2, \
        "经典两难应给出 6 种理由、仅 2 种结论(结论不含理由信息)"
    d_low, d_high = dilemma(0.15, 1.0), dilemma(1.0, 1.0)
    assert verdict(2, d_low) == -1 and verdict(2, d_high) == +1 and \
        reason(2, d_low) == reason(2, d_high) == "BEN", \
        "阶段2的结论应随利害参数翻转而理由结构(BEN)保持不变"

    # 断言 2:推理-行为差距(经验世界弱相关;理想世界强相关;情境单调压低)
    assert 0.15 < r_main < 0.45, f"经验世界诚实相关 r={r_main:.3f} 应落在弱区间"
    assert 0.10 < r_coop < 0.40, f"经验世界合作相关 r={r_coop:.3f} 应落在弱区间"
    assert r_ideal > 0.70, f"理想世界相关 r={r_ideal:.3f} 应强(推理决定行为)"
    assert r_ideal - r_main > 0.35, "理想与经验世界的相关差应显著(差距是结构)"
    for i in range(len(situ_rows) - 1):
        assert situ_rows[i + 1][1] < situ_rows[i][1], \
            "情境权重上升,推理-行为相关应单调下降"

    # 断言 3:冲突强度越高,理由结构越可辨识(解码正确率单调上升)
    for i in range(len(ident_rows) - 1):
        assert ident_rows[i + 1][2] > ident_rows[i][2], \
            "理由→阶段解码正确率应随两难冲突强度单调上升"
        assert ident_rows[i + 1][1] >= ident_rows[i][1], \
            "理由种类数应随冲突强度不减"
    assert ident_rows[0][2] < 0.5 < ident_rows[-1][2], \
        "弱两难解码率应<0.5,锋利两难应>0.5"
    assert ident_rows[0][3] < 0.1 < ident_rows[-1][3], \
        "弱两难结论应近乎一致(熵≈0),锋利两难结论应有分歧(熵>0)"

    print("\n✓ 自验证通过:同结论异理由+结论翻转理由不动(理由结构≠结论)| "
          f"经验世界推理-行为相关弱(诚实 r={r_main:.3f}/合作 r={r_coop:.3f}"
          f"<0.5,理想 {r_ideal:.3f};情境单调压低)| 冲突强度↑→解码率单调↑"
          f"(0.4→0.5→0.8;弱两难无诊断力)")

    print("\n家族回读:00 章反直觉1(差距)/反直觉2(理由计分),03 章引擎1,"
          "04 章走廊1/2/3——三个断言即三段理论的数值侧。")


if __name__ == "__main__":
    main()
