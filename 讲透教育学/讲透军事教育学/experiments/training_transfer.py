# -*- coding: utf-8 -*-
"""训练迁移仿真:情境相似度 × 训练多样性 × 压力条件(军事教育学的最小模型)。

呼应 00-体系结构.md 反直觉 1-3(军事训练是最早的教学系统设计/迁移窄化/
压力与绩效)、03-可构造与结构.md(引擎 2:保真度-迁移引擎)与
04-军事教育学转代码.md(走廊 3/4)的配套实验。纯标准库(random+math)。

文献通说陈述(非检索校准,详见家族 00 章):
  · 桑代克共同要素说(1901+):训练迁移的量由训练情境与任务情境的相似
    要素决定——形式训练说(练此心智必利彼)被实证抛弃;
  · 林克训练器(1929):低保真模拟装置产生真实技能迁移——相似要素是
    稀疏的,"买哪一维仿真"先于"买多少仿真";
  · 耶克斯-多德森定律(1908):唤醒(压力)与绩效呈倒 U;压力接种训练
    (梅肯鲍姆,1985):训练中渐进引入压力可抬高执行退化的承受阈——
    但训练压力本身有成本(挤占低压下的打磨)。

模型(保真度-迁移引擎的最小编码):
  情境 = d 维特征向量(玩具参数:噪声/时限/协同/陌生度……,非任何
    真实部队参数);任务环境中心取原点。
  技能 = 以训练分布为中心的"泛化场":
      perf(e) = peak · exp( -‖e-center‖² / (2·bandwidth²) )
    center=训练样本均值;bandwidth=训练多样性强制的泛化半径
    (经验带宽 = 1.5 × 训练样本逐维标准差);peak 随多样性 σ 上升而
    略降(专化损失:peak = 1 - 0.35σ)。
  仿真度 sim∈[0,1]:模拟器情境与任务情境的距离 = (1-sim)·D_MAX
    ——sim 越高,训练装置离任务环境越近(模拟器有效性参数)。
  压力因子(耶克斯-多德森的简化执行退化版):
      factor(P, P_cap) = 1 / (1 + k·max(0, P - P_cap))
    P=任务压力,P_cap=承受阈;压力接种=以训练压力 P_inoc 把承受阈抬到
    接种水平,但接种成本压低压下峰值(×(1-0.15·P_inoc))。

断言(自验,9 seed 蒙特卡洛平均):
  1) 模拟器有效性:任务环境表现随仿真度 sim 单调不降;高保真组
     (sim≥0.85)均值 ≥2.5× 低保真组(sim≤0.35);顶段增益 < 中段增益
     (仿真度的边际收益在接近全仿真时递减)。
  2) 迁移窄化:窄训练(σ=0.25)在训练情境的峰值高于宽训练(σ=0.65),
     但在新情境(距训练分布 1.3)的表现 ≥3× 劣于宽训练;且峰值随 σ
     单调降、带宽随 σ 单调升——"专化-泛化带宽交换"。
  3) 压力退化与接种:高任务压力(P=0.9)下常压训练组保持率 <0.7;
     渐进接种组保持率更高、绝对表现反超常压组 ≥1.15×;而零压力时
     接种组略逊于常压组(接种成本)——压力训练的适度性。

跑法: python3 -u experiments/training_transfer.py
"""

import math
import random

SEEDS = tuple(range(20260900, 20260909))   # 9 个种子
D = 6             # 情境特征维数(玩具参数)
D_MAX = 2.0       # sim=0 时模拟器情境与任务情境的距离
BW_FACTOR = 1.5   # 经验带宽 = BW_FACTOR × 训练样本逐维 std
P0 = 1.0          # 基准峰值
SPEC_COST = 0.35  # 专化损失:peak = P0·(1 - SPEC_COST·σ)
K_STRESS = 1.5    # 压力退化斜率
CAP0 = 0.30       # 常压训练的承受阈
INOC_COST = 0.15  # 接种成本系数(训练压力压低峰值)
N_TRAIN = 250     # 训练样本数
N_OPS = 300       # 任务环境采样点数
JITTER = 0.05     # 任务环境的抖动幅度


# ---------- 基础件 ----------

def rand_unit(rng):
    """随机单位方向向量(D 维)。"""
    v = [rng.gauss(0.0, 1.0) for _ in range(D)]
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v]


def shift(center, direction, d):
    """从 center 沿 direction 移动距离 d。"""
    return [c + direction[j] * d for j, c in enumerate(center)]


def train(rng, center, sigma):
    """采样训练分布 → 技能三元组 (center_hat, bandwidth, peak)。"""
    pts = [[center[j] + rng.gauss(0.0, sigma) for j in range(D)]
           for _ in range(N_TRAIN)]
    center_hat = [sum(p[j] for p in pts) / N_TRAIN for j in range(D)]
    std_sum = 0.0
    for j in range(D):
        m = center_hat[j]
        var = sum((p[j] - m) ** 2 for p in pts) / N_TRAIN
        std_sum += math.sqrt(var)
    bandwidth = max(0.08, BW_FACTOR * std_sum / D)
    peak = P0 * (1.0 - SPEC_COST * sigma)
    return center_hat, bandwidth, peak


def perf(e, skill):
    """泛化场:环境 e 处的表现。"""
    center, bw, peak = skill
    d2 = sum((x - c) ** 2 for x, c in zip(e, center))
    return peak * math.exp(-d2 / (2.0 * bw * bw))


def stress_factor(pressure, cap):
    """执行退化因子:压力超过承受阈的部分按比例退化。"""
    over = max(0.0, pressure - cap)
    return 1.0 / (1.0 + K_STRESS * over)


def mean_perf(rng, skill, target, pressure=0.0, cap=CAP0, peak_mult=1.0):
    """任务环境(以 target 为中心的小云)上的平均表现。"""
    center, bw, peak = skill
    total = 0.0
    for _ in range(N_OPS):
        e = [target[j] + rng.gauss(0.0, JITTER) for j in range(D)]
        total += perf(e, (center, bw, peak * peak_mult)) \
            * stress_factor(pressure, cap)
    return total / N_OPS


# ---------- 实验 1:模拟器有效性(仿真度单调 + 边际递减) ----------

SIM_GRID = (0.00, 0.15, 0.30, 0.45, 0.60, 0.75, 0.85, 0.95)
SIGMA_SIM = 0.45  # 固定中等训练多样性


def exp1_once(rng):
    """返回 {sim: 任务环境表现}。"""
    ops = [0.0] * D
    out = {}
    for sim in SIM_GRID:
        u = rand_unit(rng)
        sim_center = shift(ops, u, (1.0 - sim) * D_MAX)
        skill = train(rng, sim_center, SIGMA_SIM)
        out[sim] = mean_perf(rng, skill, ops)
    return out


def check1(avg):
    sims = SIM_GRID
    # 单调不降
    for a, b in zip(sims, sims[1:]):
        assert avg[b] >= avg[a] - 1e-9, \
            f"断言1失败:仿真度 {a}->{b} 表现下降({avg[a]:.4f}->{avg[b]:.4f})"
    low = sum(v for k, v in avg.items() if k <= 0.35) \
        / len([k for k in avg if k <= 0.35])
    high = sum(v for k, v in avg.items() if k >= 0.85) \
        / len([k for k in avg if k >= 0.85])
    assert high >= 2.5 * low, \
        f"断言1失败:高保真组未达低保真组 2.5 倍({high:.4f} vs {low:.4f})"
    gain_mid = avg[0.75] - avg[0.60]
    gain_top = avg[0.95] - avg[0.85]
    assert gain_mid > gain_top, \
        f"断言1失败:顶段增益未递减({gain_top:.4f} >= 中段 {gain_mid:.4f})"
    print("断言 1 ✅ 模拟器有效性:仿真度单调不降;"
          f"高保真组均值 {high:.3f} = {high/low:.1f}× 低保真组 {low:.3f};"
          f"顶段增益 {gain_top:.3f} < 中段增益 {gain_mid:.3f}(边际递减)")
    print("      仿真度-迁移曲线:",
          " ".join(f"{s:.2f}:{avg[s]:.3f}" for s in sims))


# ---------- 实验 2:迁移窄化(专化-泛化带宽交换) ----------

NOVEL_DIST = 1.3
SIG_NARROW, SIG_BROAD = 0.25, 0.65
SIGMA_GRID = (0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75)


def exp2_once(rng):
    """返回 {(标签): 表现};标签 in {窄/宽}×{训练情境,新情境} + 网格。"""
    origin = [0.0] * D
    u = rand_unit(rng)
    novel = shift(origin, u, NOVEL_DIST)
    out = {}
    for label, sig in (("窄", SIG_NARROW), ("宽", SIG_BROAD)):
        skill = train(rng, origin, sig)
        out[(label, "训练情境")] = mean_perf(rng, skill, origin)
        out[(label, "新情境")] = mean_perf(rng, skill, novel)
        out[("带宽", label)] = skill[1]
    out["网格"] = [(sig, train(rng, origin, sig)[1],
                    P0 * (1.0 - SPEC_COST * sig)) for sig in SIGMA_GRID]
    return out


def check2(avg):
    assert avg[("窄", "训练情境")] > avg[("宽", "训练情境")], \
        "断言2失败:窄训练在训练情境的峰值未高于宽训练"
    ratio = avg[("宽", "新情境")] / max(avg[("窄", "新情境")], 1e-12)
    assert ratio >= 3.0, \
        f"断言2失败:新情境宽训练未达窄训练 3 倍({ratio:.1f}×)"
    grid = avg["网格"]
    for (s1, bw1, p1), (s2, bw2, p2) in zip(grid, grid[1:]):
        assert bw2 > bw1, f"断言2失败:带宽未随多样性单调升({s1}->{s2})"
        assert p2 < p1, f"断言2失败:峰值未随多样性单调降({s1}->{s2})"
    print("断言 2 ✅ 迁移窄化:训练情境窄 "
          f"{avg[('窄', '训练情境')]:.3f} > 宽 {avg[('宽', '训练情境')]:.3f}(专化占优);"
          f"新情境宽 {avg[('宽', '新情境')]:.3f} = {ratio:.0f}× "
          f"窄 {avg[('窄', '新情境')]:.4f}(泛化带宽交换);"
          "带宽随σ单调升、峰值随σ单调降")
    print("      带宽交换网格:",
          " ".join(f"σ{s:.2f}:bw{bw:.2f}/pk{p:.2f}" for s, bw, p in grid))


# ---------- 实验 3:压力退化与压力接种 ----------

P_CALM, P_HIGH = 0.10, 0.90
SIM3, SIGMA3 = 0.70, 0.45
P_INOC = 0.70  # 接种训练压力(承受阈抬至此)


def exp3_once(rng):
    """返回 {条件: 表现}:常压/接种 × 零压/高压。"""
    ops = [0.0] * D
    u = rand_unit(rng)
    sim_center = shift(ops, u, (1.0 - SIM3) * D_MAX)
    skill = train(rng, sim_center, SIGMA3)
    out = {}
    for label, cap, pmult in (("常压组", CAP0, 1.0),
                              ("接种组", P_INOC, 1.0 - INOC_COST * P_INOC)):
        out[(label, "零压")] = mean_perf(rng, skill, ops, P_CALM, cap, pmult)
        out[(label, "高压")] = mean_perf(rng, skill, ops, P_HIGH, cap, pmult)
    return out


def check3(avg):
    ret_n = avg[("常压组", "高压")] / avg[("常压组", "零压")]
    ret_i = avg[("接种组", "高压")] / avg[("接种组", "零压")]
    assert ret_n < 0.7, f"断言3失败:高压退化不明显(常压保持率 {ret_n:.3f})"
    assert ret_i > ret_n, \
        f"断言3失败:接种组保持率未高于常压组({ret_i:.3f} vs {ret_n:.3f})"
    overt = avg[("接种组", "高压")] / avg[("常压组", "高压")]
    assert overt >= 1.15, \
        f"断言3失败:高压下接种组未反超常压组 1.15 倍({overt:.2f}×)"
    cost = (avg[("常压组", "零压")] - avg[("接种组", "零压")]) \
        / avg[("常压组", "零压")]
    assert cost > 0.05, \
        f"断言3失败:零压下接种成本未显形({cost:.3f})"
    print("断言 3 ✅ 压力退化与接种:高压(P=0.9)下常压组保持率 "
          f"{ret_n:.3f}(退化);接种组保持率 {ret_i:.3f}、绝对表现 "
          f"{avg[('接种组', '高压')]:.3f} = {overt:.2f}× 常压组 "
          f"{avg[('常压组', '高压')]:.3f}(接种减轻退化);零压下接种组 "
          f"低 {cost:.1%}(接种成本——压力训练的适度性)")


# ---------- 主流程(多 seed 平均) ----------

def average(runs):
    """对多次运行的结果求均值(网格列表按位置平均)。"""
    keys = runs[0].keys()
    avg = {}
    for k in keys:
        vals = [r[k] for r in runs]
        if isinstance(vals[0], list):  # 网格:[(σ, 带宽, 峰值)] 按位置平均
            n_rows, n_cols = len(vals[0]), len(vals[0][0])
            avg[k] = [tuple(sum(v[r][c] for v in vals) / len(vals)
                            for c in range(n_cols))
                      for r in range(n_rows)]
        else:
            avg[k] = sum(vals) / len(vals)
    return avg


def main():
    print("=" * 72)
    print("训练迁移仿真——军事教育学(GB/T 88044)家族实验")
    print(f"参数:D={D} 维情境,D_MAX={D_MAX},种子数={len(SEEDS)},"
          f"蒙特卡洛 {N_OPS} 点/条件")
    print("=" * 72)

    for name, exp_once, chk in (("实验1 模拟器有效性", exp1_once, check1),
                                ("实验2 迁移窄化", exp2_once, check2),
                                ("实验3 压力接种", exp3_once, check3)):
        runs = []
        for seed in SEEDS:
            rng = random.Random(seed)
            runs.append(exp_once(rng))
        avg = average(runs)
        print(f"\n[{name}]")
        chk(avg)

    print("\n三断言全部通过(exit 0)。三个经典结论的参数化复现:"
          "仿真度买迁移(单调+边际递减)、过训买窄化(带宽交换)、"
          "压力买接种(渐进引入、适度为界)。")


if __name__ == "__main__":
    main()
