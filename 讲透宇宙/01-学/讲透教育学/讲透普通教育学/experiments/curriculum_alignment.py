# -*- coding: utf-8 -*-
"""课程-教学-评价对齐的受控模拟:对齐度参数化与「结构>投入」(00/03/04 章配套实验)。

主题呼应建构性对齐(constructive alignment,Biggs)与逆向设计
(威金斯-麦克泰)的教学版:把一个学段的课程系统拆成**三层**——

  - 目标层(课程标准):M 条学习目标,各带标准权重(值得学的程度);
    高价值目标(迁移探究/协作表达)难出题、难评分;
  - 教学层(教师的时间分配):总课时 T 固定,教师按「应试系数 α」在
    考试蓝图与标准权重之间分配:w_teach = α·w_exam + (1-α)·w_std;
  - 考试层(考试蓝图):w_exam 给各目标的抽样权重——完全对齐=按标准
    权重抽;错位蓝图=只抽好测的(记忆/计算/规范),考不了的记 0。

学习产出(凹生产函数——边际收益递减):
    mastery_i = 1 - exp( -e_l · c_i · n_{l,i} · T·w_teach_i / d_i )
  c_i=目标可学速度,d_i=目标难度;e_l=学习者效率,n=逐目标噪声(CRN 配对)。
  真实产出 attain = Σ w_std_i · mastery_i(按标准计量);
  考试分数 score = Σ w_exam_i · mastery_i(按自家蓝图计量)。

四个系统(同课时同 α,共享随机数):
  A 对齐系统    :蓝图=标准权重 → w_teach≡w_std(对 α 不变——结构不变量);
  B 错位系统    :蓝图只抽可测 6 条,迁移/协作记 0 权重;
  C 错位+加课时 :B 的课时 ×1.25(投入修法:加量);
  D 修结构      :蓝图改回标准权重,课时不变(结构修法:对齐)。

断言三律:
  A. 对齐最优:同课时下,完全对齐系统的真实产出比错位系统高 ≥0.10
     ——教考评一致时学习产出最高;
  B. 为考而教:错位系统的产出结构变形——①考试分数与真实产出分离
     (score−attain ≥0.25:分数繁荣,产出塌陷);②未考目标崩塌
     (迁移/协作的掌握度 ≤ 对齐系统的 50%):考什么会什么,未考的丢;
  C. 结构>投入:修结构(D−B)的产出增益 ≥ 加课时(C−B)的 2 倍
     且 ≥0.08——边际收益递减使「补配置」胜过「加投入」。

⚠ 学科纪律(02/04 章):
  1. 参数为风格化取值(凹生产/蓝图偏斜/应试系数),非任何真实学区拟合;
  2. 模拟证明『凹生产+蓝图错位+应试系数』的简单机制足以生成三律
     (机制充分性),不预测任何真实政策效果;「为考而教」(反拨效应
     washback)与坎贝尔定律(指标一旦成为目标,就不再是好指标)
     为文献通说构念,方向是靶,量级不可比;
  3. 建构性对齐的通说依据:Biggs 建构性对齐、威金斯-麦克泰逆向设计
     (从目标反推评价与教学)、泰勒原理(评价对目标的回检);
  4. 方差缩减:四个系统共享同一随机数(每名学习者的效率与逐目标噪声
     逐点配对)——A 的「w_teach≡w_std 对 α 不变」是代数恒等,
     结构保证而非抽样运气;
  5. 敏感性分析:文末 Monte Carlo(200 次参数抖动)报告三律通过率。

跑法: python experiments/curriculum_alignment.py
"""

import math
import random
import sys

# ----------------------------- 模型参数(基准情形) -----------------------------
GOALS = [
    # (id, 名称, 层, 标准权重 w_std, 可学速度 c, 难度 d)
    ("G1", "事实记忆", "基础", 0.08, 1.30, 1.0),
    ("G2", "基础计算", "基础", 0.08, 1.30, 1.0),
    ("G3", "规范语法", "基础", 0.08, 1.30, 1.0),
    ("G4", "阅读理解", "中层", 0.12, 0.90, 1.2),
    ("G5", "应用建模", "中层", 0.12, 0.90, 1.2),
    ("G6", "实验操作", "中层", 0.12, 0.90, 1.2),
    ("G7", "迁移探究", "高值", 0.20, 0.55, 1.8),
    ("G8", "协作表达", "高值", 0.20, 0.55, 1.8),
]
M = len(GOALS)
W_STD = [g[3] for g in GOALS]
# 错位蓝图:好测的 6 条超采,考不了的 2 条记 0(「考不了的暂不考」)
W_EXAM_MIS = [0.20, 0.20, 0.20, 0.13, 0.13, 0.14, 0.00, 0.00]
W_EXAM_ALI = list(W_STD)

ALPHA = 0.85        # 应试系数:教学分配跟随蓝图的程度(0=只按标准教,1=完全为考而教)
T_HOURS = 20.0      # 学段总教学时数(基准)
N_LEARNERS = 2000
INPUT_BUMP = 1.25   # 投入修法:课时 +25%
HI_IDX = (6, 7)     # 高值难测目标(错位蓝图中权重为 0)


def teach_weights(w_exam, alpha):
    """教学层分配:w_teach = α·w_exam + (1-α)·w_std(线性混合,天然归一)。"""
    return [alpha * we + (1.0 - alpha) * ws for we, ws in zip(w_exam, W_STD)]


def run_system(w_exam, alpha, t_hours, effs, noises):
    """跑一个系统:返回(真实产出 attain, 考试分数 score, 逐目标平均掌握度)。"""
    w_teach = teach_weights(w_exam, alpha)
    att = sc = 0.0
    m_by_goal = [0.0] * M
    n = len(effs)
    for l in range(n):
        e = effs[l]
        row = noises[l]
        for i in range(M):
            rate = e * GOALS[i][4] * row[i] * t_hours * w_teach[i] / GOALS[i][5]
            m = 1.0 - math.exp(-rate)          # 凹生产:边际收益递减
            att += W_STD[i] * m
            sc += w_exam[i] * m
            m_by_goal[i] += m
    return att / n, sc / n, [x / n for x in m_by_goal]


def sample(rng, n):
    """CRN 素材:每名学习者的效率 e 与逐目标噪声 n(CRN 配对,各系统共用)。"""
    effs = [rng.uniform(0.7, 1.3) for _ in range(n)]
    noises = [[rng.uniform(0.95, 1.05) for _ in range(M)] for _ in range(n)]
    return effs, noises


def base_case():
    rng = random.Random(20260907)
    effs, noises = sample(rng, N_LEARNERS)
    sys_a = run_system(W_EXAM_ALI, ALPHA, T_HOURS, effs, noises)
    sys_b = run_system(W_EXAM_MIS, ALPHA, T_HOURS, effs, noises)
    sys_c = run_system(W_EXAM_MIS, ALPHA, T_HOURS * INPUT_BUMP, effs, noises)
    # 结构修法 D:蓝图改回标准权重——即使教师完全应试(α=1),分配也落回标准
    sys_d = run_system(W_EXAM_ALI, 1.0, T_HOURS, effs, noises)
    return sys_a, sys_b, sys_c, sys_d, effs, noises


def main():
    global ALPHA, T_HOURS
    if hasattr(sys.stdout, "reconfigure"):       # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    random.seed(20260907)

    # 权重自检(蓝图的算术是宪法)
    assert abs(sum(W_STD) - 1.0) < 1e-9, "标准权重未归一"
    assert abs(sum(W_EXAM_MIS) - 1.0) < 1e-9, "错位蓝图权重未归一"
    assert all(w >= 0 for w in W_EXAM_MIS), "蓝图权重出现负值"

    print("=" * 72)
    print("课程-教学-评价对齐模拟:教考评三层系统与「结构>投入」")
    print("=" * 72)
    print(f"模型:{M} 条学习目标(基础 3/中层 3/高值难测 2);总课时 {T_HOURS:.0f};"
          f"应试系数 α={ALPHA}(w_teach=α·w_exam+(1-α)·w_std)")
    print("凹生产:master=1-exp(-e·c·t/d),边际收益递减;"
          "真实产出按标准权重计量,考试分数按自家蓝图计量")

    (att_a, sc_a, ma), (att_b, sc_b, mb), (att_c, sc_c, mc), \
        (att_d, sc_d, md), effs, noises = base_case()

    print(f"\n{'系统':<14}{'真实产出(按标准)':<20}{'考试分数(按自家蓝图)':<24}")
    print(f"A 对齐        {att_a:.3f}              {sc_a:.3f}")
    print(f"B 错位        {att_b:.3f}              {sc_b:.3f}")
    print(f"C 错位+课时+25% {att_c:.3f}              {sc_c:.3f}")
    print(f"D 修结构(α=1)  {att_d:.3f}              {sc_d:.3f}")

    # ---- 逐目标掌握度剖面:考什么会什么,未考的丢 ----
    print("\n逐目标平均掌握度(对齐 A vs 错位 B):")
    print(f"{'目标':<10}{'标准权重':<10}{'蓝图权重':<10}{'A 掌握':<10}{'B 掌握':<10}")
    for i, g in enumerate(GOALS):
        print(f"{g[0]} {g[1]:<7}{W_STD[i]:<10.2f}{W_EXAM_MIS[i]:<10.2f}"
              f"{ma[i]:<10.3f}{mb[i]:<10.3f}")

    # ---- 断言 A:对齐最优 ----
    print(f"\n[断言A 对齐最优] 真实产出:对齐 {att_a:.3f} vs 错位 {att_b:.3f}"
          f"(差 {att_a-att_b:.3f})")
    assert att_a - att_b >= 0.10, f"对齐优势失败:{att_a-att_b:.3f} < 0.10"
    print("  ✓ 同课时下教考评一致(蓝图按标准权重抽)的产出最高——"
          "凹生产下,按价值比例分配时间是对资源配置的合理解")

    # ---- 断言 B:为考而教 ----
    gap = sc_b - att_b
    hi_a = sum(ma[i] for i in HI_IDX) / len(HI_IDX)
    hi_b = sum(mb[i] for i in HI_IDX) / len(HI_IDX)
    print(f"\n[断言B 为考而教] 错位系统:分数 {sc_b:.3f} − 产出 {att_b:.3f} "
          f"= {gap:.3f};未考目标掌握 {hi_b:.3f} vs 对齐 {hi_a:.3f}"
          f"(比 {hi_b/hi_a:.2f})")
    assert gap >= 0.25, f"分数-产出分离不足:{gap:.3f} < 0.25"
    assert hi_b <= 0.5 * hi_a, f"未考目标未崩塌:{hi_b:.3f} > 0.5×{hi_a:.3f}"
    print("  ✓ 考试分数繁荣与真实产出塌陷同源:考什么会什么,未考的丢——")
    print("    反拨效应(washback)的机制版:蓝图即课程的隐形编辑器")

    # ---- 断言 C:结构>投入 ----
    gain_struct = att_d - att_b
    gain_input = att_c - att_b
    print(f"\n[断言C 结构>投入] 修结构增益 {gain_struct:.3f} vs 加课时增益 "
          f"{gain_input:.3f}(比 {gain_struct/max(gain_input,1e-9):.1f} 倍)")
    assert gain_struct >= 2.0 * gain_input, \
        f"结构优势失败:{gain_struct:.3f} < 2×{gain_input:.3f}"
    assert gain_struct >= 0.08, f"结构增益过小:{gain_struct:.3f} < 0.08"
    print("  ✓ 边际收益递减让「加课时」大部分耗在已饱和的可测目标上,")
    print("    而「改蓝图」把课时从超采区搬到饥饿区——配置效率>规模扩张")
    assert abs(att_d - att_a) < 1e-9, "结构修法的 α 不变性被破坏"
    print(f"  ✓ 结构不变量:蓝图对齐后,即使教师完全应试(α=1.0,产出 {att_d:.3f}"
          f"≈A 的 {att_a:.3f}),分配也落回标准——修结构消掉了 α 这个难题")

    # ---- 机制边界:应试系数扫描(个体理性 vs 系统最优) ----
    print("\n⚙ 机制边界:错位蓝图下扫描应试系数 α(单教师弃考会怎样)")
    keep = ALPHA
    for a in (1.00, 0.85, 0.70, 0.50):
        ALPHA = a
        at, s, _ = run_system(W_EXAM_MIS, a, T_HOURS, effs, noises)
        print(f"  α={a:.2f}:真实产出 {at:.3f},错位考卷上的分数 {s:.3f}")
    ALPHA = keep
    print("  —— 单教师降低 α(少为考而教):真实产出↑,但学生在错位考卷上")
    print("    分数↓——为考而教是错位系统里的个体理性行为;解药在蓝图(结构),")
    print("    不在教师的觉悟(02 章「语言的社会学」同款分层)")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性分析:200 次抖动(速度/难度/课时/应试系数各±5%-10%)")
    n_draws, need = 200, 0.90
    passes = {"A 对齐最优": 0, "B 为考而教": 0, "C 结构>投入": 0}
    for d in range(n_draws):
        rng = random.Random(41000 + d)
        jit = lambda lo, hi: rng.uniform(lo, hi)   # noqa: E731
        c_ba = jit(1.17, 1.43)
        c_mi = jit(0.81, 0.99)
        c_hi = jit(0.495, 0.605)
        d_ba, d_mi, d_hi = jit(0.90, 1.10), jit(1.08, 1.32), jit(1.62, 1.98)
        cs = [c_ba] * 3 + [c_mi] * 3 + [c_hi] * 2
        ds = [d_ba] * 3 + [d_mi] * 3 + [d_hi] * 2
        alpha = jit(0.80, 0.90)
        t_h = jit(18.0, 22.0)
        effs_j, noises_j = sample(rng, 400)
        # 参数化抖动(改写全局 GOALS 的速度/难度列)
        saved = [(g[4], g[5]) for g in GOALS]
        for i in range(M):
            GOALS[i] = GOALS[i][:4] + (cs[i], ds[i])
        a_j = run_system(W_EXAM_ALI, alpha, t_h, effs_j, noises_j)
        b_j = run_system(W_EXAM_MIS, alpha, t_h, effs_j, noises_j)
        c_j = run_system(W_EXAM_MIS, alpha, t_h * INPUT_BUMP, effs_j, noises_j)
        dd_j = run_system(W_EXAM_ALI, 1.0, t_h, effs_j, noises_j)
        for i, (cc, dd_) in enumerate(saved):    # 全局态自洁
            GOALS[i] = GOALS[i][:4] + (cc, dd_)
        ok_a = (a_j[0] - b_j[0]) >= 0.09
        ok_b = ((b_j[1] - b_j[0]) >= 0.18
                and sum(b_j[2][i] for i in HI_IDX) <= 0.55 * sum(a_j[2][i] for i in HI_IDX))
        ok_c = ((dd_j[0] - b_j[0]) >= 1.8 * (c_j[0] - b_j[0])
                and (dd_j[0] - b_j[0]) >= 0.07)
        passes["A 对齐最优"] += ok_a
        passes["B 为考而教"] += ok_b
        passes["C 结构>投入"] += ok_c
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『凹生产+蓝图错位+应试系数』足以生成")
    print("  三律,不是任何真实学区的预测;目标分层与蓝图偏斜均为风格化设定。")
    print("  现实中考试还承担选拔/分流功能(中等教育学支),对齐不是唯一价值;")
    print("  真实证据请回 01 章素材与课程研究的原始文献。")


if __name__ == "__main__":
    main()
