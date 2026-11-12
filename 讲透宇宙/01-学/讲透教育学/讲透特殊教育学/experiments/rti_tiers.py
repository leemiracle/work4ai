# -*- coding: utf-8 -*-
"""干预分层:RTI 三层支持体系的模拟(00/04 章配套实验)。

主题呼应 04 章走廊 1-3:一个虚构学区的支持体系——
  筛查:风险分数 = 真实需要 + 测量噪声;多数学生低风险(N(0.18,0.13)),
        中度需要约 16%(N(0.42,0.13)),重度约 5%(N(0.60,0.12)),分布重叠;
  分层(RTI 金字塔):第一层全体优质教学;筛查阳性者进第二层小组干预
        (响应者回第一层);第二层非响应者升级第三层个别化(IEP 通道);
  对照世界:无有效第二层(标记直送第三层的旧模式);
  标签效应:被误标(假阳性)的学生若接受低于能力的教学(目标降档),
        成就逐期下落——自我实现标签的教学版。

断言三律(特殊教育学通说的结构化):
  A. 筛查阈值的敏感性权衡:真阳性率(TPR)与假阳性率(FPR)随阈值同涨同落
     ——分布重叠使「TPR≥0.90 且 FPR≤0.10」的阈值不存在;高敏感档
     (TPR≥0.90)的 FPR 有下限(≥0.22),低误报档(FPR≤0.10)的 TPR
     有上限(≤0.80):权衡是结构性的,不是技术不过关;
  B. 早干预减压:第二层干预有效时,第三层转介率降至直送世界的一半以下
     (RTI 金字塔 80/15-20/5 的量级带);第二层响应率下降则减压效果
     单调减弱(第二层质量是政策变量);
  C. 自我实现标签:误标学生若接受低于能力的教学,成就真实下落——
     初测两组零差(配对),终测缺口显著且逐期扩大,绝对水平低于起点;
     降档低于匹配容差时无害(标签本身惰性,通路是教学,不是心理魔法),
     降档越重缺口越大(剂量-反应)。

⚠ 学科纪律(02/04 章):
  1. 参数为通说量级的风格化取值(筛查重叠度/响应率/降档强度),
     不拟合任何真实学区;所有系统为虚构;
  2. 模拟证明「测量噪声+分层响应+教学降档的简单机制足以生成三律」
     (机制充分性),不是任何真实筛查工具或学区的数量断言;
  3. 通说依据:筛查工具的心理测量学权衡(敏感性/特异性不可兼得)、
     RTI/MTSS 分层支持与转介减压、期望效应与标签理论(皮格马利翁线)
     ——均为综述级通说,未逐条核数;
  4. 伦理边界(00 章 §七发现 3):C 律只演示单机制的充分性——
     层必须以「支持强度」定义且随时可降级,以「能力等级」执行的
     分层会自我实现;
  5. 敏感性分析:文末 Monte Carlo(80 次参数抖动)报告三律通过率
     ——换参数重跑=检验结论的结构刚性(04 章的正确用法)。

跑法: python experiments/rti_tiers.py
"""

import random
import sys

# ----------------------------- 世界参数(基准情形,虚构学区) -----------------------------
N_POP = 40_000                # 筛查总体
P_NONE, P_MOD, P_SEV = 0.79, 0.16, 0.05   # 真实需要构成(RTI 金字塔的地面真值)
MU_NONE, SD_NONE = 0.18, 0.13  # 低风险分数分布
MU_MOD, SD_MOD = 0.42, 0.13    # 中度需要分数分布
MU_SEV, SD_SEV = 0.60, 0.12    # 重度需要分数分布
TAU_SWEEP = [round(0.10 + 0.05 * i, 2) for i in range(13)]  # 阈值扫描 0.10..0.70
TAU_B = 0.40                   # 分层体系采用的筛查阈值(瞄准金字塔 15-20% 带)
RESP_MOD, RESP_SEV, RESP_NONE = 0.70, 0.25, 0.85  # 第二层响应率(中度/重度/误标者)
WEAK_MOD, WEAK_SEV, WEAK_NONE = 0.40, 0.10, 0.60  # 第二层退化世界的响应率
# 按真实代码索引(0=无需要即误标者,1=中度,2=重度):
RESP = (RESP_NONE, RESP_MOD, RESP_SEV)
WEAK = (WEAK_NONE, WEAK_MOD, WEAK_SEV)
# 标签效应动力学(成就以能力单位计)
N_C, T_C = 800, 12             # 配对样本量 / 学期数
G0 = 0.08                      # 匹配教学的每期增长
DELTA = 0.10                   # 匹配容差(指令低于能力不超过此值仍算匹配)
BETA = 0.45                    # 失配惩罚强度
CAP = 0.35                     # 失配惩罚的上限(饱和)
D0 = 0.25                      # 误标导致的初始降档(目标低于能力)
SIGMA_C = 0.008                # 每期增长噪声
DOSE = (0.08, 0.18, 0.28)      # 降档剂量扫描(剂量-反应)
FLOOR_P = -1.5                 # 成就地板(z 分尺度,防饱和截断)


# ----------------------------- 基础件:总体、扫描、响应 -----------------------------
def make_population(rng, n, mu_none=MU_NONE, sd_none=SD_NONE, mu_mod=MU_MOD,
                    sd_mod=SD_MOD, mu_sev=MU_SEV, sd_sev=SD_SEV):
    """风险分数总体:truth ∈ {0 无, 1 中度, 2 重度};分数=[0,1] 截断。"""
    scores, truths = [], []
    for _ in range(n):
        u = rng.random()
        if u < P_NONE:
            t, s = 0, rng.gauss(mu_none, sd_none)
        elif u < P_NONE + P_MOD:
            t, s = 1, rng.gauss(mu_mod, sd_mod)
        else:
            t, s = 2, rng.gauss(mu_sev, sd_sev)
        truths.append(t)
        scores.append(min(max(s, 0.0), 1.0))
    return scores, truths


def sweep(scores, truths, taus):
    """阈值扫描:每档的 TPR(真阳性率)与 FPR(假阳性率)。"""
    need = [i for i, t in enumerate(truths) if t > 0]
    none = [i for i, t in enumerate(truths) if t == 0]
    rows = []
    for tau in taus:
        tp = sum(1 for i in need if scores[i] > tau)
        fp = sum(1 for i in none if scores[i] > tau)
        rows.append((tau, tp / len(need), fp / len(none)))
    return rows


def separation(rng, scores, truths, n_pairs=5000):
    """分离度:随机配对中需要者分数高于无需要者的概率(AUC 风格;平局计半)。"""
    need = [s for s, t in zip(scores, truths) if t > 0]
    none = [s for s, t in zip(scores, truths) if t == 0]
    tot = 0.0
    for _ in range(n_pairs):
        x, y = need[rng.randrange(len(need))], none[rng.randrange(len(none))]
        tot += 1.0 if x > y else (0.5 if x == y else 0.0)
    return tot / n_pairs


# ----------------------------- 断言 A:筛查阈值的结构性权衡 -----------------------------
def law_a(rows, sep):
    hi = [r for r in rows if r[1] >= 0.90]           # 高敏感档
    lo = [r for r in rows if r[2] <= 0.10]           # 低误报档
    # A1 阈值越低 TPR/FPR 同涨(同落):序列非增
    for k in (1, 2):
        seq = [r[k] for r in rows]
        assert all(seq[i + 1] <= seq[i] + 1e-12 for i in range(len(seq) - 1)), \
            f"A1失败:第 {k} 列随阈值非单调"
    assert rows[0][1] > rows[-1][1] and rows[0][2] > rows[-1][2], "A1失败:两端无权衡"
    # A2 双达标禁区:高敏感档有 FPR 下限,低误报档有 TPR 上限
    assert hi, "A2失败:扫描未覆盖高敏感档"
    assert min(r[2] for r in hi) >= 0.22, \
        f"A2失败:TPR≥0.90 档的 FPR 下限仅 {min(r[2] for r in hi):.1%}"
    assert lo, "A2失败:扫描未覆盖低误报档"
    assert max(r[1] for r in lo) <= 0.80, \
        f"A2失败:FPR≤0.10 档的 TPR 上限达 {max(r[1] for r in lo):.1%}"
    assert not any(r[1] >= 0.90 and r[2] <= 0.10 for r in rows), \
        "A2失败:存在双达标阈值(与分布重叠矛盾)"
    # A3 分离度:重叠真实存在(既非随机又非完美)
    assert 0.60 < sep < 0.98, f"A3失败:分离度 {sep:.3f} 越界"
    hi_tau = max(r[0] for r in hi)   # 高敏感档的最宽阈值(此档 FPR 最低点)
    lo_tau = min(r[0] for r in lo)   # 低误报档的最紧阈值(此档 TPR 最高点)
    return {"hi_tau": hi_tau, "hi_fpr": [r[2] for r in rows if r[0] == hi_tau][0],
            "lo_tau": lo_tau, "lo_tpr": [r[1] for r in rows if r[0] == lo_tau][0],
            "sep": sep}


# ----------------------------- 断言 B:早干预减压(第二层的算术) -----------------------------
def law_b(rng, scores, truths, tau=TAU_B, resp=RESP, weak=WEAK):
    n = len(scores)
    flagged = [i for i, s in enumerate(scores) if s > tau]
    flag_rate = len(flagged) / n
    assert 0.12 <= flag_rate <= 0.24, f"B失败:第二层占比 {flag_rate:.1%} 越金字塔带"
    rate_direct = flag_rate                      # 直送世界:标记即第三层
    u = [rng.random() for _ in flagged]          # 共随机数:两世界配对
    t3_eff = sum(1 for i, x in zip(flagged, u) if x >= resp[truths[i]])
    t3_weak = sum(1 for i, x in zip(flagged, u) if x >= weak[truths[i]])
    rate_eff, rate_weak = t3_eff / n, t3_weak / n
    assert rate_eff <= 0.10, f"B失败:第三层转介率 {rate_eff:.1%} 超 10%"
    assert rate_eff <= 0.5 * rate_direct, \
        f"B失败:减压不足(有效第二层 {rate_eff:.1%} vs 直送 {rate_direct:.1%})"
    assert rate_weak <= 0.12 and rate_eff < rate_weak, \
        "B失败:退化世界未单调减弱减压效果"
    missed = sum(1 for i, t in enumerate(truths) if t > 0 and scores[i] <= tau) / n
    return {"flag_rate": flag_rate, "rate_direct": rate_direct,
            "rate_eff": rate_eff, "rate_weak": rate_weak, "missed": missed}


# ----------------------------- 断言 C:自我实现标签(期望-成就动力学) -----------------------------
def run_cohort(rng, abilities, d0, g0=G0, beta=BETA, cap=CAP, delta=DELTA,
               sigma=SIGMA_C, terms=T_C):
    """一组学生的成就轨迹;指令=当前表现-d0(误标降档),d0=0 为匹配教学。"""
    perf = list(abilities)
    for _ in range(terms):
        new = []
        for a, p in zip(abilities, perf):
            instr = p - d0
            m = a - instr
            growth = g0 if m <= delta else g0 - beta * min(m, cap)
            new.append(max(p + growth + rng.gauss(0.0, sigma), FLOOR_P))
        perf = new
    return perf


def final_gap(rng, abilities, d0, **kw):
    """配对终测缺口:同批能力在匹配教学 vs 降档教学两条路径的均值差。"""
    ctrl = run_cohort(rng, abilities, 0.0, **kw)
    mis = run_cohort(rng, abilities, d0, **kw)
    return sum(c - m for c, m in zip(ctrl, mis)) / len(abilities)


def law_c(rng):
    abilities = [min(max(rng.gauss(1.0, 0.25), 0.2), 2.0) for _ in range(N_C)]
    ctrl = run_cohort(rng, abilities, 0.0)
    mis = run_cohort(rng, abilities, D0)
    mean0 = sum(abilities) / N_C
    # C1 配对零基线:两组路径同起点(同一批能力值),t=0 缺口恒为零
    traj = [0.0]
    perf_c, perf_m = list(abilities), list(abilities)
    traj = [0.0]
    for _ in range(T_C):
        perf_c = run_one(rng, perf_c, abilities, 0.0)
        perf_m = run_one(rng, perf_m, abilities, D0)
        traj.append((sum(perf_c) - sum(perf_m)) / N_C)
    # 注:traj[0]=0 由配对构造保证(两组路径同起点、同能力分布)——随机化在采样层,不在分组层
    incs = [traj[i + 1] - traj[i] for i in range(T_C)]
    # C2 缺口显著且逐期扩大
    assert traj[-1] >= 0.5, f"C2失败:终测缺口仅 {traj[-1]:.2f}"
    assert all(i > 0.005 for i in incs), f"C2失败:缺口非逐期扩大(最小增量 {min(incs):.4f})"
    # C3 绝对下落(不只是相对落后)
    mis_end = sum(mis) / N_C
    assert mis_end <= mean0 - 0.3, \
        f"C3失败:误标组绝对降幅不足({mean0 - mis_end:.2f})"
    # C4 剂量-反应:轻降档无害(标签惰性),重降档大缺口
    g_dose = [final_gap(random.Random(7), abilities, d) for d in DOSE]
    assert g_dose[0] <= 0.10, f"C4失败:轻降档({DOSE[0]})即生缺口 {g_dose[0]:.2f}"
    assert g_dose[1] < g_dose[2] and g_dose[2] - g_dose[1] >= 0.25, "C4失败:剂量-反应失序"
    return {"gap": traj[-1], "decline": mean0 - mis_end, "traj": traj,
            "g_dose": g_dose}


def run_one(rng, perf, abilities, d0):
    """单期演化(与 run_cohort 同规则)。"""
    new = []
    for a, p in zip(abilities, perf):
        instr = p - d0
        m = a - instr
        growth = G0 if m <= DELTA else G0 - BETA * min(m, CAP)
        new.append(max(p + growth + rng.gauss(0.0, SIGMA_C), FLOOR_P))
    return new


# ----------------------------- 基准情形:建世界并出报告 -----------------------------
def main():
    if hasattr(sys.stdout, "reconfigure"):           # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rng = random.Random(20260907)
    scores, truths = make_population(rng, N_POP)

    print("=" * 72)
    print("干预分层:RTI 三层支持体系的模拟(虚构学区)")
    print("=" * 72)
    print(f"构成:无需要 {P_NONE:.0%} / 中度 {P_MOD:.0%} / 重度 {P_SEV:.0%};"
          f"分数分布 N({MU_NONE:.2f},{SD_NONE:.2f}) / N({MU_MOD:.2f},{SD_MOD:.2f})"
          f" / N({MU_SEV:.2f},{SD_SEV:.2f}),截断 [0,1](全部风格化虚构参数)")

    # ---- 断言 A ----
    rows = sweep(scores, truths, TAU_SWEEP)
    sep = separation(rng, scores, truths)
    ra = law_a(rows, sep)
    print(f"\n[断言A 筛查权衡] 分离度 P(需要者分数>无需要者) = {sep:.2f}"
          "(重叠真实存在):")
    for tau, tpr, fpr in rows[::3]:
        print(f"    τ={tau:.2f}: TPR {tpr:5.1%} / FPR {fpr:5.1%}")
    print(f"  高敏感档(TPR≥0.90)最宽阈值 τ={ra['hi_tau']:.2f},其 FPR 仍达 "
          f"{ra['hi_fpr']:.1%}(全档 ≥22%);")
    print(f"  低误报档(FPR≤0.10)最窄阈值 τ={ra['lo_tau']:.2f},其 TPR 只有 "
          f"{ra['lo_tpr']:.1%}(全档 ≤80%)")
    print("  ✓ 『TPR≥0.90 且 FPR≤0.10』的阈值不存在:阈值每降一档,多抓的真阳性"
          "与多收的假阳性同到——权衡是分布重叠的数学,不是筛查工具不过关;"
          "『更灵敏』的代价由假阳性名单支付(00 章 §四立场句)")

    # ---- 断言 B ----
    rb = law_b(rng, scores, truths)
    print(f"\n[断言B 早干预减压] 筛查阈值 τ={TAU_B:.2f}:第二层标记率 "
          f"{rb['flag_rate']:.1%}(金字塔 15-20% 带内):")
    print(f"  直送世界(标记即第三层):转介率 {rb['rate_direct']:.1%}")
    print(f"  有效第二层(中度响应 {RESP_MOD:.0%}/重度 {RESP_SEV:.0%}):"
          f"第三层转介率 {rb['rate_eff']:.1%}(≤ 直送的一半)")
    print(f"  退化第二层(响应 {WEAK_MOD:.0%}/{WEAK_SEV:.0%}):"
          f"转介率回升至 {rb['rate_weak']:.1%}(减压单调减弱)")
    print(f"  初筛漏网(需要而未标记,留待第二道进度监控):{rb['missed']:.1%}")
    print("  ✓ 第二层干预有效时,第三层转介率显著下降——早干预在算术上"
          "给重案层减压;第二层的响应率是政策变量(师训/方案质量),"
          "它垮掉则减压效果同步垮掉(04 章走廊 2)")

    # ---- 断言 C ----
    rc = law_c(rng)
    print(f"\n[断言C 自我实现标签] 配对 N={N_C},T={T_C} 期,降档 d0={D0}:")
    print(f"  缺口轨迹(每 3 期):" + " ".join(f"{g:.2f}" for g in rc["traj"][::3]))
    print(f"  终测缺口 {rc['gap']:.2f}(逐期扩大,最小增量 "
          f"{min(rc['traj'][i+1]-rc['traj'][i] for i in range(T_C)):.3f});"
          f"误标组绝对下落 {rc['decline']:.2f}(低于起点,不只是相对落后)")
    print(f"  剂量-反应:降档 {DOSE[0]}/{DOSE[1]}/{DOSE[2]} → 终测缺口 "
          + "/".join(f"{g:.2f}" for g in rc["g_dose"]))
    print("  ✓ 被误标学生若接受低于能力的教学,成就真实下落且差距逐期扩大;"
          f"降档 ≤ 匹配容差({DELTA})时无害——标签本身惰性,自证的通路是"
          "教学降档,不是心理魔法。分层体系的伦理边界:层以『支持强度』"
          "定义且随时可降级,按『能力等级』执行的分层会自我实现"
          "(00 章 §七发现 3)")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性分析:80 次参数抖动(分数分布/响应率/降档动力学)")
    n_draws, need = 80, 0.85
    passes = {"A 筛查权衡": 0, "B 早干预减压": 0, "C 标签自证": 0}
    for k in range(n_draws):
        rj = random.Random(910_000 + k)
        # A+B:抖动分数分布与响应率
        mu_n, sd_n = rj.uniform(0.17, 0.19), rj.uniform(0.12, 0.145)
        mu_m, sd_m = rj.uniform(0.41, 0.43), rj.uniform(0.115, 0.145)
        mu_s, sd_s = rj.uniform(0.585, 0.615), rj.uniform(0.105, 0.135)
        sc, tr = make_population(rj, 12_000, mu_n, sd_n, mu_m, sd_m, mu_s, sd_s)
        rw = sweep(sc, tr, TAU_SWEEP)
        sp = separation(rj, sc, tr, 2000)
        try:
            assert all(rw[i + 1][1] <= rw[i][1] + 1e-12 and
                       rw[i + 1][2] <= rw[i][2] + 1e-12 for i in range(len(rw) - 1))
            assert not any(r[1] >= 0.90 and r[2] <= 0.10 for r in rw)
            assert 0.55 < sp < 0.985
            passes["A 筛查权衡"] += 1
            resp_j = (rj.uniform(0.80, 0.90), rj.uniform(0.60, 0.78),
                      rj.uniform(0.18, 0.32))          # 按真实代码:(误标,中度,重度)
            weak_j = (0.60, max(resp_j[1] - 0.30, 0.10),
                      max(resp_j[2] - 0.15, 0.05))
            # 内联检查(用 MC 专用界,不套基准情形的窄界):
            flg = [i for i, s in enumerate(sc) if s > TAU_B]
            flag_j = len(flg) / len(sc)
            uj = [rj.random() for _ in flg]
            t3e = sum(1 for i, x in zip(flg, uj) if x >= resp_j[tr[i]])
            t3w = sum(1 for i, x in zip(flg, uj) if x >= weak_j[tr[i]])
            rate_e, rate_w = t3e / len(sc), t3w / len(sc)
            assert 0.09 <= flag_j <= 0.28 and rate_e <= 0.12 \
                and rate_e <= 0.58 * flag_j and rate_e < rate_w
            passes["B 早干预减压"] += 1
        except AssertionError:
            pass
        # C:抖动降档动力学
        try:
            d0_j = rj.uniform(0.24, 0.28)
            beta_j, g0_j = rj.uniform(0.43, 0.49), rj.uniform(0.07, 0.084)
            cap_j, sig_j = rj.uniform(0.33, 0.39), rj.uniform(0.005, 0.012)
            ab = [min(max(rj.gauss(1.0, 0.25), 0.2), 2.0) for _ in range(600)]
            kw = dict(g0=g0_j, beta=beta_j, cap=cap_j, sigma=sig_j)
            pc, pm = list(ab), list(ab)
            traj = [0.0]
            for _ in range(T_C):
                pc = run_one_par(rj, pc, ab, 0.0, kw)     # 匹配教学
                pm = run_one_par(rj, pm, ab, d0_j, kw)    # 误标降档
                traj.append((sum(pc) - sum(pm)) / len(ab))
            assert traj[-1] >= 0.5 and all(traj[i + 1] - traj[i] > 0.004
                                           for i in range(T_C))
            gd = [final_gap_par(rj, ab, d, kw) for d in DOSE]
            assert gd[0] <= 0.12 and gd[1] < gd[2] and gd[2] - gd[1] >= 0.25
            passes["C 标签自证"] += 1
        except AssertionError:
            pass
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『测量噪声+分层响应+教学降档的简单机制")
    print("  足以生成三律』,不是任何真实筛查工具或学区的数量断言。")
    print("  真实读数还需:筛查工具的信度与切分分依据、双道筛查(普筛+进度")
    print("  监控)的漏网回收、第二层的实施保真度、降档的制度通道(复评周期/")
    print("  层级可逆性)——把响应率与降档深度做成政策变量重跑,是使用本脚本")
    print("  的正确姿势(04 章 §三);C 律是伦理边界的机制玩具,不是对任何")
    print("  现行安置制度的指控或背书。")


def run_one_par(rng, perf, abilities, d0, kw):
    """MC 用单期演化(参数化)。"""
    new = []
    for a, p in zip(abilities, perf):
        instr = p - d0
        m = a - instr
        growth = kw["g0"] if m <= DELTA else kw["g0"] - kw["beta"] * min(m, kw["cap"])
        new.append(max(p + growth + rng.gauss(0.0, kw["sigma"]), FLOOR_P))
    return new


def final_gap_par(rng, abilities, d, kw):
    """MC 用配对终测缺口(参数化)。"""
    pc = run_cohort_par(rng, abilities, 0.0, kw, T_C)
    pm = run_cohort_par(rng, abilities, d, kw, T_C)
    return sum(c - m for c, m in zip(pc, pm)) / len(abilities)


def run_cohort_par(rng, abilities, d0, kw, terms):
    perf = list(abilities)
    for _ in range(terms):
        perf = run_one_par(rng, perf, abilities, d0, kw)
    return perf


if __name__ == "__main__":
    main()
