# -*- coding: utf-8 -*-
"""早期干预的收益与衰减:三因素(先天/环境/干预)与 skills 的自我生产(00/01/04 章配套实验)。

主题呼应佩里学前项目(HighScope Perry Preschool Study,1962-1967 入组,
123 名 3-4 岁弱势儿童随机分组,两年高质量学前+每周家访,追踪至 40 岁;
Schweinhart et al. 2005,通说):把儿童发展拆成**三因素**——

  - 先天能力 A:个体潜能(长期重新占优的"回落基座"之一);
  - 家庭环境 E:0-6 岁最主要的输入源(弱势=环境最低 25 分位);
  - 早期干预 D:高质量学前(教育+非认知训练+家访)的剂量。

双通道技能(5 岁入小学时的状态):
  认知通道 C(可测的学业/智力):受 A/E/D 影响;入学后学校教育"给所有人",
    认知优势被逐步等化——传递系数 T_c(t)=exp(-LAM_C·(t-5)) 衰减;
  非认知通道 N(动机/坚持/社会性):同样受干预增益,但高保留
    T_n(t)=exp(-LAM_N·(t-5))——skills beget skills(技能的自我生产:
    早期技能让儿童从后续经验中汲取更多,优势自我维持,通说)。

成年结果(25 岁检查点):
  连续结果 Y(收入/生活指数)= 0.30·C + 0.50·N + 0.20·E + 噪声;
  长尾结果 grad(高中毕业)= 潜变量 0.25·C + 0.65·N + 0.10·E + 噪声 > 阈值
    ——非认知主导(Heckman 通说:毕业/犯罪这类长尾结果主要走非认知通道)。

两世界对照(CRN 同随机数配对):每个儿童在"干预世界"与"对照世界"
共用同一 (A, E, 初始技能, 噪声) 序列——组内差=该儿童的干预效应,
不受抽样运气污染(方差缩减,与教育技术学家族实验同纪律)。

断言三律(通说的结构表达):
  A. 干预组间差:弱势组内,干预 vs 对照,成年连续结果显著为正
     (ΔY≥0.20)且长尾结果改善(毕业率差≥0.08)——佩里主发现;
  B. 衰减与保留:①认知通道效应 10 岁时衰减过半(T_c(10)≤0.5,
     入学准备/IQ 优势的 fadeout);②非认知通道成年高保留
     (T_n(25)≥0.80,技能自我生产);③最弱势组(弱势内干预前基线
     技能最低四分位,只按干预前特征分层)的毕业率效应≥0.08
     且不低于弱势组平均的 80%——「智商增益会蒸发,人生结果不会」;
  C. 目标效率:同等总预算(普遍=全员剂量 1;定向=弱势 25% 剂量 4,
     均为 1.0·N 预算单位)下,定向到弱势组的总成年结果增量
     ≥ 普遍干预的 1.5 倍——三个现实机制:非弱势挤出(多数中产家庭
     本会自费,公共供给多为替代)、普遍方案的弱势参与缺口(信息/
     交通/信任)、弱势组的补偿性响应(基线刺激越少边际收益越大)。

⚠ 学科纪律(02/04 章):
  1. 参数为通说量级的风格化取值(佩里量级校准:弱势组初期认知
     效应≈0.6σ、控制组毕业率≈55-60%、干预组差≈15-20pp),不是任何
     真实实验的拟合;
  2. 模拟证明的是「三因素+双通道传递+挤出/参与/响应三机制足以
     生成三律」(机制充分性),不是对真实政策的预测;
  3. 通说依据:佩里学前项目与 Abecedarian 随机证据、Heckman 曲线
     (早期投资回报)与技能自我生产(Heckman-Kautz 非认知通道)、
     Head Start 评估的 IQ fadeout(认知通道衰减)、目标效率与
     普遍补贴的挤出/参与缺口(政策研究通说)——均为综述级通说;
  4. 机制边界:文末把挤出/参与缺口/响应异质三个机制关到零——
     断言 C 翻转(普遍反超)。目标效率不是先验真理,是现实机制的
     经验结论;断言 C 的靶是"有挤出与响应异质"的现实区;
  5. 敏感性分析:文末 Monte Carlo(200 次参数抖动)报告三律通过率;
     传递率抖动保持机制约束(LAM_C≥0.14 保认知衰减过半,
     LAM_N≤0.012 保非认知高保留)。

跑法: python experiments/early_intervention_decay.py
"""

import math
import random
import sys

# ----------------------------- 模型参数(基准情形) -----------------------------
N_CHILDREN = 4000    # 模拟儿童数
E_CUT = -0.6745      # 弱势定义:家庭环境标准分最低 25% 的分界

# 干预增益(5 岁入小学时点,剂量=1 且回应=1 时的效应,标准化单位)
BETA_C = 0.25        # 认知通道增益(一年普通质量量级)
BETA_N = 0.22        # 非认知通道增益(动机/社会性,测量难但下游长)
DOSE_EXP = 0.60      # 剂量-收益凹指数(质量/时长的边际递减,通说方向)
RESP_GAMMA = 0.30    # 补偿性响应:环境每低 1σ,增益乘子 +0.30

# 供给机制(公共剂量的"净增量"因子)
DOSE_UNIV, DOSE_TARGET = 1.0, 4.0   # 同预算:全员×1 vs 弱势 25%×4(均为 1.0N)
TAKEUP_WEAK = 0.50    # 普遍方案的弱势参与缺口(信息/交通/信任,通说方向)
CROWD_NONWEAK = 0.12  # 非弱势挤出:多数家庭本会自费,公共供给多为替代
CROWD_WEAK = 0.95     # 定向项目带外展/家访,参与接近足额

# 5 岁后的传递(学校等化 vs 技能自我生产)
LAM_C = 0.16          # 认知优势年衰减率(学校教育给所有人→优势被追平)
LAM_N = 0.008         # 非认知优势年衰减率(高保留:skills beget skills)
AGE_10, AGE_ADULT = 10.0, 25.0

# 成年结果(25 岁检查点)
W_Y = (0.30, 0.50, 0.20)   # 连续结果:认知/非认知/环境
W_G = (0.25, 0.65, 0.10)   # 毕业潜变量:非认知主导(Heckman 通说)
TAU_G = -0.80               # 毕业阈值(校准:全样本基线毕业率≈88%,弱势≈55%)
SIG_Y, SIG_G = 0.30, 0.40   # 结果噪声(CRN 共享)


def make_children(n, seed):
    """生成儿童元组 (A, E, C0, N0, uy, ug);uy/ug 为成年结果噪声(CRN 共享)。"""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        a = rng.gauss(0.0, 1.0)
        e = rng.gauss(0.0, 1.0)
        c0 = 0.50 * a + 0.50 * e + 0.30 * rng.gauss(0.0, 1.0)  # 5 岁认知基线
        n0 = 0.30 * a + 0.70 * e + 0.40 * rng.gauss(0.0, 1.0)  # 5 岁非认知基线
        out.append((a, e, c0, n0, rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)))
    return out


def resp_mult(e):
    """补偿性响应:家庭刺激越少,同等干预的边际收益越大(通说方向)。"""
    return 1.0 + RESP_GAMMA * max(0.0, -e)


def gains(dose_eff, e):
    """有效剂量→5 岁时点增益(认知/非认知)。"""
    scale = (dose_eff ** DOSE_EXP) * resp_mult(e)
    return BETA_C * scale, BETA_N * scale


def transmit(c5, n5, a, e, age):
    """5 岁技能向年龄 t 的传递:技能项×T + 基座回落项×(1-T)。

    T_c 衰减快=学校等化(课堂给所有人,认知优势被追平);
    T_n 衰减慢=技能自我生产(早期技能让儿童从后续经验中汲取更多)。
    """
    t_c = math.exp(-LAM_C * (age - 5.0))
    t_n = math.exp(-LAM_N * (age - 5.0))
    c = t_c * c5 + (1.0 - t_c) * (0.60 * a + 0.40 * e)
    n = t_n * n5 + (1.0 - t_n) * (0.30 * a + 0.50 * e)
    return c, n


def run_world(kids, dose_of):
    """跑一个"世界":dose_of(a, e, weak)→有效剂量;返回每人 (Y, 毕业潜变量, 毕业)。"""
    res = []
    for (a, e, c0, n0, uy, ug) in kids:
        weak = e < E_CUT
        dc, dn = gains(dose_of(a, e, weak), e)
        c25, n25 = transmit(c0 + dc, n0 + dn, a, e, AGE_ADULT)
        y = W_Y[0] * c25 + W_Y[1] * n25 + W_Y[2] * e + SIG_Y * uy
        g = W_G[0] * c25 + W_G[1] * n25 + W_G[2] * e + SIG_G * ug
        res.append((y, g, g > TAU_G))
    return res


def summarize(res_ctrl, res_treat, idx_mask):
    """idx_mask 内的组内差(CRN 配对:同儿童两世界相减)。"""
    ys, gs = [], []
    for i, on in enumerate(idx_mask):
        if on:
            ys.append(res_treat[i][0] - res_ctrl[i][0])
            gs.append((1.0 if res_treat[i][2] else 0.0)
                      - (1.0 if res_ctrl[i][2] else 0.0))
    n = len(ys)
    return sum(ys) / n, sum(gs) / n


# ----------------------------- 断言 A/B/C(基准情形) -----------------------------
def base_case(n=N_CHILDREN, seed=20260907):
    kids = make_children(n, seed)
    weak = [e < E_CUT for (_, e, *_r) in kids]

    ctrl = run_world(kids, lambda a, e, w: 0.0)                        # 对照世界
    target = run_world(kids, lambda a, e, w: DOSE_TARGET * CROWD_WEAK if w else 0.0)
    univ = run_world(kids, lambda a, e, w:
                     DOSE_UNIV * (TAKEUP_WEAK if w else CROWD_NONWEAK))

    weak_mask = weak
    # 最弱势组:弱势组内**干预前基线技能**(C0+N0)最低的四分位。
    # 只按干预前特征分层(不能按结果分层——那是选择了噪声,方法论纪律)。
    weak_idx = [i for i, w in enumerate(weak) if w]
    weak_idx.sort(key=lambda i: kids[i][2] + kids[i][3])
    k = max(1, len(weak_idx) // 4)
    risk_mask = [False] * n
    for i in weak_idx[:k]:
        risk_mask[i] = True

    dy_w, dg_w = summarize(ctrl, target, weak_mask)
    dy_r, dg_r = summarize(ctrl, target, risk_mask)
    dy_all_u = sum(univ[i][0] - ctrl[i][0] for i in range(n)) / n
    dy_all_t = sum(target[i][0] - ctrl[i][0] for i in range(n)) / n
    grad_ctrl_weak = sum(1 for i in weak_idx if ctrl[i][2]) / len(weak_idx)
    grad_treat_weak = sum(1 for i in weak_idx if target[i][2]) / len(weak_idx)
    return {
        "dy_weak": dy_w, "dg_weak": dg_w,
        "dy_risk": dy_r, "dg_risk": dg_r,
        "univ_total": dy_all_u, "target_total": dy_all_t,
        "grad_ctrl_weak": grad_ctrl_weak, "grad_treat_weak": grad_treat_weak,
        "n_weak": len(weak_idx),
    }


def main():
    global BETA_C, BETA_N, DOSE_EXP, RESP_GAMMA, TAKEUP_WEAK
    global CROWD_NONWEAK, CROWD_WEAK, LAM_C, LAM_N, TAU_G
    if hasattr(sys.stdout, "reconfigure"):          # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 72)
    print("早期干预的收益与衰减:先天/环境/干预三因素 × skills 的自我生产")
    print("=" * 72)
    print(f"模型:N={N_CHILDREN} 儿童;弱势=环境最低 25%;干预=剂量×质量"
          f"(凹指数 {DOSE_EXP});认知年衰减 λ_c={LAM_C},"
          f"非认知 λ_n={LAM_N};CRN 两世界配对")
    tc10, tn25 = math.exp(-LAM_C * (AGE_10 - 5)), math.exp(-LAM_N * (AGE_ADULT - 5))
    print(f"传递:认知 T_c(10 岁)={tc10:.3f}(学校等化),"
          f"T_c(25 岁)={math.exp(-LAM_C * 20):.3f};"
          f"非认知 T_n(25 岁)={tn25:.3f}(技能自我生产)")

    r = base_case()
    print(f"\n弱势组(环境最低 25%, n={r['n_weak']}):")
    print(f"  毕业率:对照 {r['grad_ctrl_weak']:.1%} → 干预 {r['grad_treat_weak']:.1%}"
          f"(差 {r['dg_weak']:+.1%})")
    print(f"  成年连续结果 Y 的组内差:{r['dy_weak']:+.3f}(标准化单位)")

    # ---- 断言 A:干预组间差(佩里主发现) ----
    print(f"\n[断言A 干预组间差] 弱势组 ΔY={r['dy_weak']:.3f},"
          f"毕业率差 {r['dg_weak']:+.1%}")
    assert r["dy_weak"] >= 0.20, f"干预正效应失败:ΔY {r['dy_weak']:.3f} < 0.20"
    assert r["dg_weak"] >= 0.08, f"长尾改善失败:毕业率差 {r['dg_weak']:.1%} < 8pp"
    print("  ✓ 高质量早期干预对弱势组成年结果有显著正效应——连续端与长尾端"
          "同时改善(佩里主发现的结构表达)")

    # ---- 断言 B:衰减与保留 ----
    print(f"\n[断言B 衰减与保留] 认知 T_c(10)={tc10:.3f};非认知 T_n(25)={tn25:.3f};"
          f"最弱势组毕业率差 {r['dg_risk']:+.1%}(弱势组平均 {r['dg_weak']:+.1%})")
    assert tc10 <= 0.50, f"认知衰减失败:T_c(10)={tc10:.3f} > 0.5"
    assert tn25 >= 0.80, f"非认知保留失败:T_n(25)={tn25:.3f} < 0.80"
    assert r["dg_risk"] >= 0.08, f"长尾效应未保留:{r['dg_risk']:.1%} < 8pp"
    assert r["dg_risk"] >= 0.80 * r["dg_weak"], "最弱势组效应异常缩水"
    print("  ✓ 认知通道效应 10 岁衰减过半(IQ fadeout:学校教育给所有人,")
    print("    优势被追平);非认知通道成年高保留(skills beget skills);")
    print("    最弱势组的长尾结果(毕业)效应保留且不低于弱势组平均的八成")
    print("    ——「智商增益会蒸发,人生结果不会」:主通道是非认知,不是智商")

    # ---- 断言 C:目标效率(同预算:普遍 vs 定向) ----
    ratio = r["target_total"] / r["univ_total"] if r["univ_total"] > 0 else float("inf")
    print(f"\n[断言C 目标效率] 同预算(1.0N)总增量:定向 {r['target_total']:.4f}"
          f" vs 普遍 {r['univ_total']:.4f}(比 {ratio:.2f} 倍)")
    assert ratio >= 1.5, f"目标效率失败:定向/普遍={ratio:.2f} < 1.5"
    print("  ✓ 同等预算下,定向弱势组的边际收益更高——三个机制:")
    print(f"    非弱势挤出(净增量×{CROWD_NONWEAK})、普遍方案的弱势参与缺口"
          f"(×{TAKEUP_WEAK})、补偿性响应(环境-1σ→增益×{1+RESP_GAMMA:.2f})")

    # ---- 机制边界:把三个供给机制关到零 ----
    print("\n⚙ 机制边界:挤出=0、参与缺口=0、响应同质(γ=0)——现实机制全关")
    keep = (TAKEUP_WEAK, CROWD_NONWEAK, CROWD_WEAK, RESP_GAMMA)
    TAKEUP_WEAK, CROWD_NONWEAK, CROWD_WEAK, RESP_GAMMA = 1.0, 1.0, 1.0, 0.0
    r0 = base_case()
    ratio0 = r0["target_total"] / r0["univ_total"] if r0["univ_total"] > 0 else 0.0
    TAKEUP_WEAK, CROWD_NONWEAK, CROWD_WEAK, RESP_GAMMA = keep
    print(f"  定向/普遍 = {ratio0:.2f}(普遍反超)——目标效率不是先验真理:")
    print("  没有挤出与响应异质时,凹的剂量-收益曲线让「薄撒」占优;")
    print("  断言 C 的靶是「有挤出与参与缺口」的现实区(通说量级)")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性:200 次抖动(增益/凹指数/响应/挤出/参与/衰减")
    print("各±15%-40%;传递率保持机制约束:λ_c≥0.14(认知衰减过半),")
    print("λ_n≤0.012(非认知高保留)——机制约束不是自由参数)")
    n_draws, need = 200, 0.90
    passes = {"A 干预组间差": 0, "B 衰减与保留": 0, "C 目标效率": 0}
    g = globals()
    base = {"BETA_C": BETA_C, "BETA_N": BETA_N, "DOSE_EXP": DOSE_EXP,
            "RESP_GAMMA": RESP_GAMMA, "TAKEUP_WEAK": TAKEUP_WEAK,
            "CROWD_NONWEAK": CROWD_NONWEAK, "CROWD_WEAK": CROWD_WEAK,
            "LAM_C": LAM_C, "LAM_N": LAM_N}
    for d in range(n_draws):
        jit = lambda a, b: random.uniform(a, b)     # noqa: E731
        for k, v in (("BETA_C", jit(0.20, 0.30)), ("BETA_N", jit(0.18, 0.26)),
                     ("DOSE_EXP", jit(0.55, 0.65)), ("RESP_GAMMA", jit(0.25, 0.35)),
                     ("TAKEUP_WEAK", jit(0.45, 0.60)),
                     ("CROWD_NONWEAK", jit(0.10, 0.18)),
                     ("CROWD_WEAK", jit(0.90, 1.00)),
                     ("LAM_C", jit(0.14, 0.20)), ("LAM_N", jit(0.004, 0.012))):
            g[k] = v
        r2 = base_case(n=2400, seed=41000 + d)
        ok_a = (r2["dy_weak"] >= 0.15 and r2["dg_weak"] >= 0.06)
        ok_b = (math.exp(-g["LAM_C"] * 5) <= 0.50
                and math.exp(-g["LAM_N"] * 20) >= 0.75
                and r2["dg_risk"] >= 0.06
                and r2["dg_risk"] >= 0.75 * r2["dg_weak"])
        ok_c = ((r2["target_total"] / r2["univ_total"]
                 if r2["univ_total"] > 0 else 9e9) >= 1.25)
        passes["A 干预组间差"] += ok_a
        passes["B 衰减与保留"] += ok_b
        passes["C 目标效率"] += ok_c
    for k, v in base.items():                        # 恢复基准参数(全局态自洁)
        g[k] = v
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『三因素+双通道传递+供给三机制足以")
    print("  生成三律』,不是真实政策的预测;增益/衰减/挤出均为风格化参数,")
    print("  且固定了预算规模与弱势比例——现实中定向的识别成本、污名效应、")
    print("  普遍方案的政治可持续性都是本模型看不见的变量。真实证据请回 01 章")
    print("  素材(佩里/Abecedarian/Head Start 评估)与原始文献。")


if __name__ == "__main__":
    main()
