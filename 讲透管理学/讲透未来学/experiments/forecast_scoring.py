# -*- coding: utf-8 -*-
"""预测评分实验:Brier 评分与校准曲线如何分辨「技能」与「运气」(02/04 章配套实验)。

02 章 §1.2「预言的证据学」+ 04 章 C4 走廊的成品,四段演示:
  A. 聚合级:两类预测者各答数万题——技能型(信号准确率略高于基线,按贝叶斯后验报价)
     与运气型(无信号,凭直觉喊 75%/25%)。Brier 评分显著区分;校准曲线
     (预测概率 vs 实际频率)技能型贴近对角线,直觉型呈平台状偏离。
  B. 生涯级(小样本 M=20):同一批问题反复对决——裸命中率频繁分不出两类,
     Brier 评分的胜率显著更高。断言:Brier 能区分,裸命中率在样本小时不能。
  C. 预言的自我实现:无技能的「大嗓门」预言者恒报 90%,且预言影响行为
     (正反馈:预测越笃定,众人行动越把它推成真)→ 命中率虚高;
     沉默的孪生对照(同样的零技能,不发布)命中率停在基线。
  D. 分辨率注解:技能型报价与结局的相关 > 0(有分辨率),运气型 ≈ 0。

设计声明(选样纪律,承家族 04 章 §0):
  - 世界设为「每题五五开」——刻意隔离「知道基率」这项技能,让分辨率单独受检;
    现实中基率知识也是技能(参考类预测),本实验不度量它。
  - 技能型报价=贝叶斯后验(先验 0.5,信号准确率 a∈[0.53,0.63])——构造上即「校准」,
    所以它的校准曲线贴近对角线是数学必然,实验演示的是这条性质可以用来识人。
  - 固定种子=可复现演示;换种子重跑=敏感性分析。

跑法: python experiments/forecast_scoring.py
"""

import math
import random
import sys

R_CAREERS = 4000        # 模拟「分析师生涯」的次数(B 段)
M_PER_CAREER = 20       # 每个生涯的题数(刻意小样本)
SKILL_LO, SKILL_HI = 0.53, 0.63   # 每题信号准确率区间(期望 0.58,略高于基线 0.5)
GUT_HI, GUT_LO = 0.75, 0.25       # 运气型:无信号,凭直觉喊高价(过度自信)
FEEDBACK = 0.30         # 预言对行为的正反馈强度(C 段)
ANNOUNCE = 0.90         # 大嗓门预言者的恒定报价
N_PROPHECY = 40000      # C 段题数
BINS = [(0.1 * i, 0.1 * (i + 1)) for i in range(10)]   # 校准分箱(0.1 宽)


def simulate_career(rng):
    """一个 M 题的小生涯:同一批问题,两类预测者作答(配对比较)。"""
    qs_skill, qs_luck, os_ = [], [], []
    for _ in range(M_PER_CAREER):
        a = SKILL_LO + (SKILL_HI - SKILL_LO) * rng.random()  # 本题的信号质量
        o = 1 if rng.random() < 0.5 else 0                   # 真实结局(五五开世界)
        s = o if rng.random() < a else 1 - o                 # 技能型的信号(准确率 a)
        qs_skill.append(a if s == 1 else 1.0 - a)            # 贝叶斯后验报价
        qs_luck.append(GUT_HI if rng.random() < 0.5 else GUT_LO)  # 直觉喊价(与结局无关)
        os_.append(o)
    return qs_skill, qs_luck, os_


def brier(qs, os_):
    """布里尔评分:mean (p - outcome)^2,越低越好。"""
    return sum((q - o) ** 2 for q, o in zip(qs, os_)) / len(qs)


def hit_rate(qs, os_):
    """裸命中率:把 p>0.5 压成 0/1 再数对错——信息全部压毁(04 章 §7 的坏尺子)。"""
    return sum(1 for q, o in zip(qs, os_) if (q > 0.5) == (o == 1)) / len(qs)


def corr(qs, os_):
    """报价与结局的相关系数——分辨率的代理指标。"""
    n = len(qs)
    mq, mo = sum(qs) / n, sum(os_) / n
    cov = sum((q - mq) * (o - mo) for q, o in zip(qs, os_)) / n
    vq = sum((q - mq) ** 2 for q in qs) / n
    vo = sum((o - mo) ** 2 for o in os_) / n
    return cov / math.sqrt(vq * vo) if vq > 0 and vo > 0 else 0.0


def calibration_rows(qs, os_):
    """按 0.1 宽度分箱,返回 [(bin, n, 预测均值, 实际频率)](箱内样本≥30 才列)。"""
    rows = []
    for lo, hi in BINS:
        idx = [i for i, q in enumerate(qs) if lo <= q < hi]
        if len(idx) >= 30:
            mq = sum(qs[i] for i in idx) / len(idx)
            fo = sum(os_[i] for i in idx) / len(idx)
            rows.append(((lo, hi), len(idx), mq, fo))
    return rows


def calib_mae(rows):
    """加权校准误差:sum(n*|预测均值-实际频率|)/sum(n)——越贴近对角线越小。"""
    tot = sum(n for _, n, _, _ in rows)
    return sum(n * abs(mq - fo) for _, n, mq, fo in rows) / tot


def print_calibration(name, rows):
    print(f"\n  {name} 校准曲线(预测概率 vs 实际频率;# = 偏离对角线的程度):")
    for (lo, hi), n, mq, fo in rows:
        dev = abs(mq - fo)
        bar = "#" * int(dev * 100)
        print(f"    [{lo:.1f},{hi:.1f})  n={n:<6} 均值 {mq:.3f} → 实际 {fo:.3f}"
              f"  偏差 {dev:.3f} {bar}")


def main():
    if hasattr(sys.stdout, "reconfigure"):          # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    rng = random.Random(20260907)

    print("=" * 70)
    print("预测评分实验:技能 vs 运气 vs 自我实现的预言")
    print(f"(技能型:信号准确率 U[{SKILL_LO},{SKILL_HI}] 按贝叶斯后验报价;"
          f"运气型:无信号喊 {GUT_LO}/{GUT_HI})")
    print("=" * 70)

    # ---------- A+B 段:生涯模拟 ----------
    pool_qs_skill, pool_qs_luck, pool_os = [], [], []
    brier_wins = hit_wins = 0
    for _ in range(R_CAREERS):
        qs_s, qs_l, os_ = simulate_career(rng)
        pool_qs_skill += qs_s
        pool_qs_luck += qs_l
        pool_os += os_
        if brier(qs_s, os_) < brier(qs_l, os_):
            brier_wins += 1
        if hit_rate(qs_s, os_) > hit_rate(qs_l, os_):
            hit_wins += 1

    n_all = len(pool_os)
    b_skill, b_luck = brier(pool_qs_skill, pool_os), brier(pool_qs_luck, pool_os)
    h_skill, h_luck = hit_rate(pool_qs_skill, pool_os), hit_rate(pool_qs_luck, pool_os)

    print(f"\n[A] 聚合级({n_all} 题合并):")
    print(f"    布里尔评分:技能型 {b_skill:.4f}  运气型 {b_luck:.4f}"
          f"  差 {b_luck - b_skill:.4f}")
    print(f"    裸命中率  :技能型 {h_skill:.4f}  运气型 {h_luck:.4f}"
          f"  差 {h_skill - h_luck:.4f}")
    print(f"    分辨率代理(报价×结局相关):技能型 {corr(pool_qs_skill, pool_os):+.3f}"
          f"  运气型 {corr(pool_qs_luck, pool_os):+.3f}")

    rows_s = calibration_rows(pool_qs_skill, pool_os)
    rows_l = calibration_rows(pool_qs_luck, pool_os)
    mae_s, mae_l = calib_mae(rows_s), calib_mae(rows_l)
    print_calibration("技能型", rows_s)
    print_calibration("运气型", rows_l)
    print(f"\n    校准误差(加权 MAE):技能型 {mae_s:.4f}  运气型 {mae_l:.4f}"
          f"  —— 技能型贴近对角线,运气型平台状偏离")

    wr_b, wr_h = brier_wins / R_CAREERS, hit_wins / R_CAREERS
    print(f"\n[B] 生涯级(单个生涯仅 {M_PER_CAREER} 题,对决 {R_CAREERS} 次):")
    print(f"    同一生涯内 Brier 分出高下的胜率:技能型 {wr_b:.1%}")
    print(f"    同一生涯内裸命中率分出高下的胜率:技能型 {wr_h:.1%}")
    print(f"    —— 小样本下裸命中率经常分不出(甚至偶有反向),Brier 稳定站队技能")

    # ---------- C 段:预言的自我实现 ----------
    hit_infl = hit_ctrl = 0
    for _ in range(N_PROPHECY):
        # 大嗓门:恒报 90%,无任何技能;行为反应把事件概率从 0.5 推向 0.5+FEEDBACK*(0.9-0.5)
        p_eff = 0.5 + FEEDBACK * (ANNOUNCE - 0.5)
        if rng.random() < p_eff:
            hit_infl += 1
        if rng.random() < 0.5:                       # 沉默的孪生对照(零技能,不发布)
            hit_ctrl += 1
    hit_infl /= N_PROPHECY
    hit_ctrl /= N_PROPHECY

    print(f"\n[C] 预言的自我实现(零技能预言者,恒报 {ANNOUNCE:.0%},"
          f"正反馈强度 {FEEDBACK}):")
    print(f"    大嗓门预言者的命中率:{hit_infl:.4f}(世界被预言推向了它)")
    print(f"    沉默孪生对照的命中率:{hit_ctrl:.4f}(停在基线)")
    print(f"    —— 命中率虚高 {hit_infl - hit_ctrl:.4f},全部来自预言对世界的作用,")
    print(f"      不是信息:记录无法区分「知道未来」与「改变未来」(00 章预测的悖论)。")
    print(f"      镜像情形(自我否定):预警灾难→众人防范→灾难未至→预言显得『错』。")

    # ---------- 断言(固定种子下的确定性自验) ----------
    print("\n" + "=" * 70)
    print("断言(固定种子,确定性自验):")
    assert b_luck - b_skill > 0.05, "聚合级:Brier 应显著区分技能与运气"
    print(f"  1. 聚合 Brier:运气型高出技能型 {b_luck - b_skill:.4f} > 0.05 ✓")
    assert wr_b > 0.80, "生涯级:Brier 胜率应显著高于抛硬币"
    print(f"  2. 生涯级 Brier 胜率 {wr_b:.1%} > 80% —— Brier 能区分 ✓")
    assert wr_h < 0.78, "生涯级:裸命中率不应稳定区分"
    print(f"  3. 生涯级裸命中率胜率 {wr_h:.1%} < 78% —— 小样本下不能区分 ✓")
    assert wr_b - wr_h > 0.08, "Brier 与裸命中率的分辨力差距应显著"
    print(f"  4. 分辨力差距 {wr_b - wr_h:.1%} > 8% —— Brier 是更好的尺子 ✓")
    assert mae_s < 0.02 and mae_l > 0.20, "校准:技能型应贴近对角线,运气型偏离"
    print(f"  5. 校准误差:技能型 {mae_s:.4f} < 0.02,运气型 {mae_l:.4f} > 0.20 ✓")
    assert hit_infl > 0.58 and hit_infl - hit_ctrl > 0.08, "自我实现应使命中率虚高"
    print(f"  6. 自我实现:命中率 {hit_infl:.4f} 高出对照 {hit_infl - hit_ctrl:.4f} ✓")

    print("\n⚠ 证据学纪律:固定种子=可复现演示,不是显著性定理;"
          "\n  换种子重跑(敏感性分析)是使用本脚本的正确姿势(04 章 §0)。"
          "\n  现实世界里『知道基率』也是技能(参考类预测),本实验刻意不度量它。")


if __name__ == "__main__":
    main()
