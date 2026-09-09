# -*- coding: utf-8 -*-
"""问责制的反身性失灵模拟:古德哈特教育版/权重集中度/抽样审计三律检验(02/04 章配套实验)。

主题呼应 02 章证据栏与 04 章走廊 1(问责设计走廊):学校产出分解为
  真实学力(不可直接观测,社会真正想要的)+ 应试努力(可观测,对测验分数
  边际贡献大)的参数化模型:

  - 学校把一单位资源按 x∈[0,1] 分给真实学力建设,1-x 给应试训练;
  - 产出函数取凹形(边际递减):g(u)=u^ρ;
  - 真实价值 H(x)=a_H·g(x)+b_H·g(1-x),载荷 a_H≫b_H(应试对真实学力贡献小);
  - 测验分数 S(x)=a_S·g(x)+b_S·g(1-x),载荷 b_S>a_S(teaching to the test:
    应试对可观测分数的边际贡献更大);
  - 学校行为假设:最大化问责奖惩(指标分+期望罚金),不最大化真实价值——
    这是"被考核者的最优反应",不是道德滑坡。

断言三律(教育管理/组织研究通说,古德哈特定律教育版):
  A. 只考可观测指标(单指标=测验分数)时,学校最优资源分配从社会最优
     (argmax H)移向应试侧(argmax S)——资源从不可观测侧转移到可观测侧,
     真实学力相对损失>15%(古德哈特教育版:指标成为目标即失真);
  B. 权重集中度定律:把问责权重集中到最可博弈指标(纯测验)扭曲最大;
     在载荷异质的指标池上均匀分散权重,扭曲显著下降,且扭曲量随集中度
     μ 单调上升(多指标分散降低扭曲);
  C. 抽样审计定律:以概率 p 随机深查不可观测侧(真实学力),发现
     "真实教学份额低于下限 x_c"按缺口罚 F——存在审计强度阈值
     p·F > max(平均收益斜率, 边际收益斜率),越过阈值后转移策略的
     期望收益转负(argmax 回到遵守区,payoff(遵守)>payoff(转移))。
     —— 问责设计三教训:多指标、分散权重、抽样深查。

闭式解福利:对 a·x^ρ+b·(1-x)^ρ 型凹产出,argmax x*=a^k/(a^k+b^k),
k=1/(1-ρ);基准情形用闭式解与网格搜索互验。

⚠ 学科纪律(02/04 章):
  1. 参数为通说量级的风格化取值,不是任何真实学校系统的拟合;
  2. 模拟证明的是「载荷不对称+最优化反应的简单机制足以生成三律」
     (机制充分性),不是对真实问责制度效果的数量预测;
  3. 通说依据:古德哈特定律教育版(高利害测验引发应试窄化,现象级共识)、
     多指标与低利害化的设计教训(问责研究通说)、审计抽样思想
     (委托代理文献通说)——均为综述级通说,未逐条核数;
  4. 敏感性分析:文末 Monte Carlo(200 次参数抖动)报告三律通过率——
     换参数重跑=检验结论的结构刚性(04 章的正确用法)。

跑法: python experiments/accountability_perverse.py
"""

import math
import random
import sys

# ----------------------------- 模型参数(基准情形) -----------------------------
RHO = 0.5      # 产出凹度:g(u)=u^ρ(边际递减)
A_H, B_H = 1.0, 0.25   # 真实学力载荷:真实教学 vs 应试(应试贡献小)
A_S, B_S = 0.7, 1.0    # 测验分数载荷:应试边际贡献 > 真实教学(可观测性不对称)
# 指标池:K 个指标,各自是 H 与 S 的凸组合,t=对测验的贴近度
#   t=0:纯真实学力指标(如延迟后测/综合素质档案)
#   t=1:纯应试指标(如高利害统考);中间为混合载荷指标
POOL_T = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
AUD_P, AUD_F = 0.3, 5.0   # 基准审计参数:概率 p=0.3,单位缺口罚金 F=5


def prod(u, rho=RHO):
    """凹产出函数 g(u)=u^ρ(边际递减;u≥0)。"""
    return u ** rho if u > 0.0 else 0.0


def make_output(a, b, rho=RHO):
    """构造产出函数 f(x)=a·g(x)+b·g(1-x)(x=真实学力份额)。"""
    return lambda x: a * prod(x, rho) + b * prod(1.0 - x, rho)


true_value = make_output(A_H, B_H)   # 真实学力 H(x)(社会想要的)
score = make_output(A_S, B_S)        # 测验分数 S(x)(可观测指标)


def x_optimal(a, b, rho=RHO):
    """闭式最优份额:argmax[a·x^ρ+b·(1-x)^ρ] = a^k/(a^k+b^k),k=1/(1-ρ)。"""
    k = 1.0 / (1.0 - rho)
    pa, pb = a ** k, b ** k
    return pa / (pa + pb)


def argmax_grid(f, lo=0.0, hi=1.0, n=4001):
    """网格搜索 argmax(通用 ρ 与组合指标用;基准情形与闭式解互验)。"""
    best_x, best_v = lo, f(lo)
    for i in range(1, n):
        x = lo + (hi - lo) * i / (n - 1)
        v = f(x)
        if v > best_v:
            best_x, best_v = x, v
    return best_x


def rel_distortion(x, rho=RHO, a_h=A_H, b_h=B_H):
    """真实学力的相对损失:1 - H(x)/H(x*),以社会最优 x* 为参照。"""
    h = make_output(a_h, b_h, rho)
    return 1.0 - h(x) / h(x_optimal(a_h, b_h, rho))


def blended_loads(t_list, weights, a_h=A_H, b_h=B_H, a_s=A_S, b_s=B_S):
    """指标组合的等效载荷:每个指标是 H/S 的凸组合(贴近度 t),
    组合的等效载荷 = 载荷的加权和(线性组合保持结构)。"""
    a = sum(w * ((1.0 - t) * a_h + t * a_s) for t, w in zip(t_list, weights))
    b = sum(w * ((1.0 - t) * b_h + t * b_s) for t, w in zip(t_list, weights))
    return a, b


# ----------------------------- 断言 A:古德哈特教育版 -----------------------------
def check_A(rho=RHO, a_h=A_H, b_h=B_H, a_s=A_S, b_s=B_S):
    """A 单指标问责:社会最优(argmax H) vs 学校最优反应(argmax S)。"""
    x_soc = x_optimal(a_h, b_h, rho)          # 社会最优(完美观测真实价值)
    x_sco = x_optimal(a_s, b_s, rho)          # 只考可观测分数的最优反应
    d = rel_distortion(x_sco, rho, a_h, b_h)
    return x_soc, x_sco, d


# ----------------------------- 断言 B:权重集中度定律 -----------------------------
def check_B(rho=RHO, a_h=A_H, b_h=B_H, a_s=A_S, b_s=B_S, pool=POOL_T):
    """B 集中度-扭曲曲线:μ=0(指标池均匀分散)→μ=1(全部权重压在最可博弈指标 t=1)。"""
    h = make_output(a_h, b_h, rho)
    x_soc = x_optimal(a_h, b_h, rho)
    k = len(pool)
    path = []
    for i in range(11):                        # μ: 0.0 → 1.0 步长 0.1
        mu = i / 10.0
        weights = [(1.0 - mu) / k] * k
        weights[-1] += mu                      # 集中份额全部加在 t=1(纯测验)
        a, b = blended_loads(pool, weights, a_h, b_h, a_s, b_s)
        x_eff = x_optimal(a, b, rho)
        path.append({"mu": mu, "x": x_eff,
                     "loss": 1.0 - h(x_eff) / h(x_soc)})   # 真实学力相对损失
    return path


# ----------------------------- 断言 C:抽样审计定律 -----------------------------
def payoff_fn(p_f, x_c, a_s=A_S, b_s=B_S, rho=RHO):
    """期望收益:指标分 − p·F·max(0, x_c−x)(深查以概率 p 发现缺口并按缺口罚)。"""
    s = make_output(a_s, b_s, rho)
    return lambda x: s(x) - p_f * max(0.0, x_c - x)


def check_C(rho=RHO, a_h=A_H, b_h=B_H, a_s=A_S, b_s=B_S,
            p_f=AUD_P * AUD_F, floor_gap=0.05):
    """C 抽样审计:下限 x_c=x*−gap;返回(无审计转移点/遵守点/两处收益/最优反应)。"""
    s = make_output(a_s, b_s, rho)
    x_soc = x_optimal(a_h, b_h, rho)
    x_sco = x_optimal(a_s, b_s, rho)
    x_c = x_soc - floor_gap                   # 监管下限:真实教学份额不低于此
    pay = payoff_fn(p_f, x_c, a_s, b_s, rho)
    x_best = argmax_grid(pay)
    return {"x_c": x_c, "x_transfer": x_sco, "x_best": x_best,
            "pay_transfer": pay(x_sco), "pay_comply": pay(x_c)}


def audit_threshold(rho=RHO, a_h=A_H, b_h=B_H, a_s=A_S, b_s=B_S,
                    floor_gap=0.05):
    """审计强度阈值:p·F 须压过两个斜率——
    ①平均收益斜率(整段转移的总收益/缺口);②下限处的边际收益斜率
    (压不过它,最优反应仍停在转移半途)。"""
    s = make_output(a_s, b_s, rho)
    x_soc = x_optimal(a_h, b_h, rho)
    x_sco = x_optimal(a_s, b_s, rho)
    x_c = x_soc - floor_gap
    avg_slope = (s(x_sco) - s(x_c)) / (x_c - x_sco)
    eps = 1e-4
    margin_slope = -(s(x_c) - s(x_c - eps)) / eps      # |S'(x_c)|
    return max(avg_slope, margin_slope), avg_slope, margin_slope


# ----------------------------- 报告与断言 -----------------------------
def main():
    if hasattr(sys.stdout, "reconfigure"):           # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    random.seed(20260907)

    print("=" * 72)
    print("问责制的反身性失灵模拟:古德哈特教育版·权重集中度·抽样审计三律")
    print("=" * 72)
    print(f"模型:产出 g(u)=u^{RHO};真实学力载荷 ({A_H},{B_H}),"
          f"测验分数载荷 ({A_S},{B_S});指标池 t={list(POOL_T)}")
    print(f"闭式解:x*=a^k/(a^k+b^k),k=1/(1-ρ)={1.0 / (1.0 - RHO):.1f}")

    # ---- 断言 A ----
    x_soc, x_sco, d = check_A()
    x_soc_g = argmax_grid(true_value)                 # 网格与闭式解互验
    x_sco_g = argmax_grid(score)
    assert abs(x_soc_g - x_soc) < 0.01 and abs(x_sco_g - x_sco) < 0.01, \
        "闭式解与网格搜索不一致(实现自检失败)"
    print(f"\n[断言A 古德哈特教育版] 资源分配(真实学力份额 x):")
    print(f"  社会最优(直接测真实价值):x* = {x_soc:.3f}")
    print(f"  单指标问责(只考测验分数):x  = {x_sco:.3f}"
          f" —— 资源向应试侧转移 {x_soc - x_sco:.2f}")
    print(f"  真实学力相对损失 {d:.1%}")
    assert x_sco < x_soc - 0.05, "古德哈特失败:最优反应未向应试侧转移"
    assert d > 0.15, f"古德哈特失败:真实学力损失 {d:.1%} < 15%"
    print("  ✓ 指标一旦成为唯一目标,被考核者把资源从不可观测侧转移到"
          "可观测侧——测量的对象被测量改写(古德哈特教育版)")

    # ---- 断言 B ----
    path = check_B()
    print(f"\n[断言B 权重集中度] μ:0=指标池均匀分散 → 1=全部权重压在纯测验:")
    marks = [p for p in path if p["mu"] in (0.0, 0.5, 1.0)]
    for p in marks:
        print(f"  μ={p['mu']:.1f}: 最优份额 x={p['x']:.3f},"
              f" 真实学力相对损失 {p['loss']:.1%}")
    losses = [p["loss"] for p in path]
    assert all(l2 >= l1 - 1e-12 for l1, l2 in zip(losses, losses[1:])), \
        "集中度定律失败:扭曲未随集中度单调上升"
    assert losses[-1] > losses[0] + 0.05, \
        f"集中度定律失败:集中扭曲 {losses[-1]:.1%} 未显著大于分散 {losses[0]:.1%}"
    assert losses[-1] > losses[len(losses) // 2] > losses[0], \
        "集中度定律失败:中间点次序异常"
    print(f"  ✓ 扭曲随权重集中度 μ 单调上升;均匀分散把损失从 "
          f"{losses[-1]:.0%} 压到 {losses[0]:.0%}"
          " —— 多指标分散降低扭曲(指标池含真实学力敏感指标时)")

    # ---- 断言 C ----
    p_f = AUD_P * AUD_F
    thr, avg_s, mar_s = audit_threshold()
    C0 = check_C(p_f=0.0)                             # 无审计对照
    C1 = check_C(p_f=p_f)                             # 抽样审计 p·F=1.5
    print(f"\n[断言C 抽样审计] 下限 x_c={C1['x_c']:.3f},"
          f"审计 p={AUD_P}×罚金 F={AUD_F}(强度 p·F={p_f:.1f}):")
    print(f"  无审计(p=0):最优反应停在 x={C0['x_best']:.3f}(转移区)")
    print(f"  审计阈值:p·F > max(平均收益斜率 {avg_s:.2f},"
          f"下限边际斜率 {mar_s:.2f}) = {thr:.2f}")
    print(f"  有审计:最优反应回到 x={C1['x_best']:.3f}(遵守区);"
          f"收益比较 遵守 {C1['pay_comply']:.3f} vs 转移 {C1['pay_transfer']:.3f}")
    assert C0["x_best"] < C1["x_c"] - 0.1, "审计定律失败:无审计对照未处于转移区"
    assert C1["x_best"] >= C1["x_c"] - 0.02, \
        f"审计定律失败:最优反应未回到遵守区({C1['x_best']:.3f})"
    assert C1["pay_comply"] > C1["pay_transfer"] + 0.1, \
        "审计定律失败:转移策略期望收益未转负"
    assert p_f > thr, "审计强度未越过阈值(参数自检失败)"
    print(f"  ✓ 越过阈值后,转移相对遵守的期望差 {C1['pay_transfer'] - C1['pay_comply']:+.2f}(转负)"
          f" —— 随机深查不可观测侧使博弈无利可图")
    print("  ⚙ 阈值扫描:强度 p·F 从 0 升到 1.5,最优反应单调回移——")
    scan = []
    for strength in (0.0, 0.4, 0.8, 1.2, 1.5):
        c = check_C(p_f=strength)
        scan.append((strength, c["x_best"]))
    print("      " + " ".join(f"{s:.1f}→{x:.2f}" for s, x in scan))
    assert all(x2 >= x1 - 1e-9 for (_, x1), (_, x2) in zip(scan, scan[1:])), \
        "阈值扫描失败:最优反应未随审计强度回移"
    print("      审计强度必须压过指标的边际收益——问责设计的工程公式")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性分析:200 次抖动(载荷各±20%;ρ∈[0.4,0.6])")
    n_draws, need = 200, 0.90
    passes = {"A 古德哈特": 0, "B 集中度": 0, "C 审计": 0}
    for _ in range(n_draws):
        a_h = random.uniform(0.85, 1.10)
        b_h = random.uniform(0.15, 0.30)
        a_s = random.uniform(0.55, 0.80)
        b_s = random.uniform(0.90, 1.10)
        rho = random.uniform(0.40, 0.60)
        # A:转移幅度>0.05 且真实学力相对损失>10%
        _, x_sco_j, d_j = check_A(rho, a_h, b_h, a_s, b_s)
        ok_a = (x_sco_j < x_optimal(a_h, b_h, rho) - 0.05) and (d_j > 0.10)
        # B:集中扭曲显著大于分散,且沿路径单调
        path_j = check_B(rho, a_h, b_h, a_s, b_s)
        losses_j = [p["loss"] for p in path_j]
        ok_b = (losses_j[-1] > losses_j[0] + 0.02
                and all(l2 >= l1 - 1e-12
                        for l1, l2 in zip(losses_j, losses_j[1:])))
        # C:审计强度取阈值×1.6+0.2(越过阈值的稳健设置),最优反应回遵守区
        thr_j, _, _ = audit_threshold(rho, a_h, b_h, a_s, b_s)
        c_j = check_C(rho, a_h, b_h, a_s, b_s, p_f=1.6 * thr_j + 0.2)
        ok_c = (c_j["x_best"] >= c_j["x_c"] - 0.05
                and c_j["pay_comply"] > c_j["pay_transfer"])
        passes["A 古德哈特"] += ok_a
        passes["B 集中度"] += ok_b
        passes["C 审计"] += ok_c
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『载荷不对称+最优反应的简单机制足以生成三律』,")
    print("  不是真实问责制度效果的数量预测;载荷/审计参数均为风格化取值。")
    print("  真实设计还需考虑:指标的测量误差与噪声(02 章识别难)、审计的误判率、")
    print("  多期博弈与指标替换竞速——把罚金改为误判率参数、把单期改为多期,")
    print("  是使用本脚本的正确姿势(04 章 §三落点 2)。")


if __name__ == "__main__":
    main()
