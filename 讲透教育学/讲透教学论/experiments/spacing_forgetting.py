# -*- coding: utf-8 -*-
"""间隔重复与遗忘曲线受控模拟:间隔效应/自适应间隔扩展/分散学习效应三律检验(00/04 章配套实验)。

主题呼应代码走廊 1(04 章 §二):艾宾浩斯式遗忘曲线(保持率随时间指数衰减,
参数化为记忆强度 s 的函数 R(t)=exp(-t/s))+ 保留率阈值触发的间隔重复(SRS)干预:

  - 检索成功(概率=触发时的保持率 R):强度乘以增益 m(R)=min(β+c·(1-R), mcap)
    ——检索越接近遗忘(1-R 越大)加固越强,但失败风险同步升高(合意困难);
  - 检索失败:强度回退为 ρ 倍(重新学习);
  - 下次复习间隔 g = s·ln(1/θ):保持率恰好降到 θ 时触发(SM-2 式调度)。

断言三律(记忆研究/教学论通说):
  A. 间隔效应:同等学习次数下,集中练习(当日重读)的保持率衰减显著快于
     间隔练习(末态半衰期差 >2 倍;45 天后平均保持率差 >3 倍);
  B. 自适应间隔扩展(SRS 数学原理:间隔×保留率阈值触发):
     复习间隔随记忆强度几何扩展(逐次严格递增,单步比值≈增益);
     难项自动获得更短的间隔与更多的复习次数;调度不变量保证
     全程保持率 ≥ θ(观察窗内任意时刻都不会遗忘到阈值以下才复习);
  C. 分散学习效应:学习总时长固定(同 8 次学习动作)时,分散安排的
     60 天长期保持显著优于集中(≥1.8 倍)。

⚠ 学科纪律(02/04 章):
  1. 参数为通说量级的风格化取值,不是任何真实实验的拟合;
  2. 模拟证明的是「指数遗忘+阈值触发的简单机制足以生成三律」(机制充分性),
     不是对真实学习者数据的预测——真实最优间隔随测验延迟而变
     (塞佩达等 2006 的元分析结论),远比本模型精细;
  3. 通说依据:艾宾浩斯遗忘曲线(1885)、间隔效应/分散学习元分析(2006)、
     检索练习效应(2006)、SM-2 以降的 SRS 实践——均为综述级通说,未逐条核数;
  4. 敏感性分析:文末 Monte Carlo(200 次参数抖动)报告三律通过率——
     换参数重跑=检验结论的结构刚性(04 章的正确用法);θ 的抖动取
     SRS 实践区间 0.85-0.95:θ→1 是「复习过早=没有遗忘」的退化区,
     间隔优势按机制消失(模型自带的边界条件,见运行输出的机制边界演示)。

跑法: python experiments/spacing_forgetting.py
"""

import math
import random
import sys

# ----------------------------- 模型参数(基准情形) -----------------------------
S0 = 1.0         # 初始记忆强度(天;保持率半衰期 = S0·ln2 ≈ 0.69 天)
BETA = 1.55      # 集中重读增益(保留率≈1 时的乘子:流畅重读几乎不加固)
C = 8.0          # 检索增益斜率:m(R) = BETA + C·(1-R),随难度线性上升
MCAP = 3.2       # 增益上限(过难检索的边际收益封顶)
RHO = 0.5        # 检索失败的强度回退系数
THETA = 0.9      # SRS 触发阈值:保持率降到 0.9 就复习
HORIZON = 60.0   # 断言 B 的观察窗(天)

# 断言 B 的两种学习材料(难度=编码质量:初始强度+增益斜率打折)
EASY = {"s0": 1.0, "cmul": 1.2}    # 易项:m(θ)=1.55+8*1.2*0.1=2.51
HARD = {"s0": 0.5, "cmul": 0.5}    # 难项:m(θ)=1.55+8*0.5*0.1=1.95


def retention(t, s):
    """艾宾浩斯式指数遗忘:间隔 t 天后的保持率(强度 s 为时间常数)。"""
    return math.exp(-t / s) if s > 0.0 else 0.0


def gain(R, beta=BETA, c=C, mcap=MCAP):
    """检索成功一次的强度乘子:越接近遗忘(1-R 越大)加固越强,封顶 mcap。"""
    return min(beta + c * (1.0 - R), mcap)


def half_life(s):
    """保持率降到 50% 所需天数(强度的时间刻度)。"""
    return s * math.log(2.0)


# ----------------------------- 两种练习机制 -----------------------------
def massed_final_strength(n_acts, s0=S0, beta=BETA):
    """集中练习:n_acts 次学习动作全部挤在第 0 天(重读,必成功,每次乘 β)。

    重读不经过遗忘(保留率≈1),增益取 m(1)=β——流畅重读几乎不加固。
    """
    return s0 * beta ** (n_acts - 1)


def srs_run(n_acts, s0=S0, beta=BETA, c=C, mcap=MCAP, rho=RHO, theta=THETA,
            rng=None):
    """间隔练习:1 次初始学习 + (n_acts-1) 次阈值触发复习。

    每次复习:成功(概率=R=θ)→ s *= gain(θ);失败 → s *= ρ。
    返回 (各次学习日, 末次学习日, 末态强度)。
    """
    rng = rng if rng is not None else random.Random(0)
    s, t = s0, 0.0
    log_th = math.log(1.0 / theta)
    days = [0.0]
    for _ in range(n_acts - 1):
        gap = s * log_th               # 调度:保持率恰好降到 θ 时复习
        t += gap
        R = retention(gap, s)          # 调度不变量:恒等于 θ
        s = s * gain(R, beta, c, mcap) if rng.random() < R else s * rho
        days.append(t)
    return days, t, s


def mean_retention_at(day, n_acts, spaced, n=2000, seed=7, **kw):
    """n 名虚拟学习者在第 day 天的平均保持率(间隔臂含随机检索成败)。"""
    rng = random.Random(seed)
    total = 0.0
    for _ in range(n):
        if spaced:
            _, last, s = srs_run(n_acts, rng=rng, **kw)
            total += retention(day - last, s)
        else:
            total += retention(day, massed_final_strength(n_acts, **{
                k: v for k, v in kw.items() if k in ("s0", "beta")}))
    return total / n


# ----------------------------- 断言 A:间隔效应 -----------------------------
def check_A(n_acts=6, day=45.0, n=2000, seed=7, **kw):
    """A 间隔效应:同 6 次学习动作,集中(全在第 0 天) vs 间隔(阈值触发)。"""
    s_m = massed_final_strength(n_acts, **{k: v for k, v in kw.items()
                                           if k in ("s0", "beta")})
    r_m = retention(day, s_m)
    r_s = mean_retention_at(day, n_acts, spaced=True, n=n, seed=seed, **kw)
    hl_m, hl_s = half_life(s_m), None
    # 间隔臂半衰期取 2000 次仿真的中位数(末态强度)
    rng = random.Random(seed + 1)
    fins = sorted(srs_run(n_acts, rng=rng, **kw)[2] for _ in range(n))
    hl_s = half_life(fins[n // 2])
    return r_m, r_s, hl_m, hl_s


# ----------------------------- 断言 B:自适应间隔扩展 -----------------------------
def srs_gaps_deterministic(s0, m, theta=THETA, horizon=HORIZON):
    """确定性 SRS(检索必成功,乘子恒 m):窗内间隔表/末态强度/末次复习日。"""
    s, t, gaps = s0, 0.0, []
    log_th = math.log(1.0 / theta)
    while True:
        gap = s * log_th
        if t + gap > horizon:
            break
        t += gap
        gaps.append(gap)
        s *= m
    return gaps, s, t


def check_B(beta=BETA, c=C, theta=THETA, horizon=HORIZON):
    """B 自适应扩展:易/难两材料的确定性间隔表 + 随机版扩展占比。"""
    out = {}
    for name, item in (("易项", EASY), ("难项", HARD)):
        m = min(beta + c * item["cmul"] * (1.0 - theta), MCAP)
        gaps, s_end, t_end = srs_gaps_deterministic(item["s0"], m, theta, horizon)
        r_end = retention(horizon - t_end, s_end)   # 窗末保持率(不变量:≥θ)
        out[name] = {"m": m, "gaps": gaps, "s_end": s_end,
                     "t_end": t_end, "r_end": r_end}
    return out


def expansion_fraction(item, rho=RHO, theta=THETA, horizon=HORIZON,
                       rng=None, beta=BETA, c=C):
    """随机成败版:相邻复习间隔中『扩展』步骤的占比(失败一步会回缩)。"""
    rng = rng if rng is not None else random.Random(0)
    m = min(beta + c * item["cmul"] * (1.0 - theta), MCAP)
    s, t, gaps = item["s0"], 0.0, []
    log_th = math.log(1.0 / theta)
    while True:
        gap = s * log_th
        if t + gap > horizon:
            break
        t += gap
        gaps.append(gap)
        s = s * m if rng.random() < theta else s * rho
    if len(gaps) < 2:
        return 1.0
    steps = (g2 / g1 for g1, g2 in zip(gaps, gaps[1:]))
    return sum(1 for r in steps if r > 1.0) / (len(gaps) - 1)


# ----------------------------- 断言 C:分散学习效应 -----------------------------
def check_C(n_acts=8, day=60.0, n=2000, seed=11, **kw):
    """C 固定预算:同 8 次学习动作,集中 vs 分散,第 60 天平均保持率。"""
    r_m = mean_retention_at(day, n_acts, spaced=False, n=1, seed=seed,
                            **{k: v for k, v in kw.items()
                               if k in ("s0", "beta")})
    r_s = mean_retention_at(day, n_acts, spaced=True, n=n, seed=seed, **kw)
    return r_m, r_s


# ----------------------------- 报告与断言 -----------------------------
def main():
    if hasattr(sys.stdout, "reconfigure"):           # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    random.seed(20260907)

    print("=" * 72)
    print("间隔重复与遗忘曲线受控模拟:间隔效应·自适应扩展·分散学习效应三律")
    print("=" * 72)
    print(f"模型:R(t)=exp(-t/s);集中重读增益 β={BETA},检索增益 "
          f"m(R)=min({BETA}+{C}(1-R), {MCAP}),失败回退 ρ={RHO},阈值 θ={THETA}")

    # ---- 断言 A ----
    r_m, r_s, hl_m, hl_s = check_A()
    print(f"\n[断言A 间隔效应] 同样 6 次学习动作,第 45 天:")
    print(f"  集中(全在第0天重读):末态强度 {massed_final_strength(6):6.1f} 天,"
          f" 半衰期 {hl_m:5.1f} 天, 保持率 {r_m:.3f}")
    print(f"  间隔(阈值触发复习):  中位末态强度 → 半衰期 {hl_s:5.1f} 天,"
          f" 平均保持率 {r_s:.3f}")
    assert hl_s > 2.0 * hl_m, f"间隔效应失败:半衰期 {hl_s:.1f} 未达集中组 2 倍({hl_m:.1f})"
    assert r_s > 0.15 and r_m < 0.06, "间隔效应失败:45 天保持率量级异常"
    assert r_s / r_m > 3.0, f"间隔效应失败:保持率比 {r_s/r_m:.1f} < 3"
    print(f"  ✓ 半衰期 {hl_s/hl_m:.1f} 倍,45 天保持率 {r_s/r_m:.1f} 倍"
          " —— 集中练习的保持率衰减显著快于间隔练习(间隔效应)")

    # ---- 断言 B ----
    B = check_B()
    print(f"\n[断言B 自适应间隔扩展] {HORIZON:.0f} 天窗口,易项 vs 难项:")
    for name in ("易项", "难项"):
        d = B[name]
        seq = " → ".join(f"{g:.2f}" for g in d["gaps"])
        print(f"  {name}(m={d['m']:.2f}, 复习 {len(d['gaps'])} 次):"
              f" 间隔序列 {seq}")
        print(f"          窗末保持率 {d['r_end']:.3f}(≥θ 由调度不变量保证)")
    e, h = B["易项"], B["难项"]
    for name, d in B.items():
        gaps = d["gaps"]
        assert all(g2 > g1 for g1, g2 in zip(gaps, gaps[1:])), \
            f"自适应扩展失败:{name}间隔未逐次严格递增"
        ratios = [g2 / g1 for g1, g2 in zip(gaps, gaps[1:])]
        assert all(1.5 < r < 3.3 for r in ratios), f"扩展比值越界:{name}"
        assert d["r_end"] >= THETA - 1e-9, f"调度不变量失败:{name}窗末保持率<θ"
    k_min = min(len(e["gaps"]), len(h["gaps"]))
    assert all(h["gaps"][k] < e["gaps"][k] for k in range(k_min)), \
        "自适应失败:难项未自动获得更短间隔"
    assert len(h["gaps"]) > len(e["gaps"]), \
        "自适应失败:难项复习次数未多于易项"
    rng = random.Random(20260907)
    frac = (sum(expansion_fraction(EASY, rng=rng) for _ in range(200))
            + sum(expansion_fraction(HARD, rng=rng) for _ in range(200))) / 400
    assert frac >= 0.75, f"随机版扩展占比过低:{frac:.2f}"
    print(f"  ✓ 间隔随强度几何扩展(单步比值≈增益 m);难项逐段间隔更短、"
          f"复习更多({len(h['gaps'])}>{len(e['gaps'])} 次)——间隔×阈值触发"
          "的自适应调度;随机成败版扩展步骤占比 "
          f"{frac:.0%}(失败步回缩属合意困难的价格)")

    # 机制边界演示:复习过早(θ→1)时,间隔优势按机制消失
    adv = lambda th: (min(BETA + C * (1.0 - th), MCAP) / BETA) ** 5   # noqa: E731
    print(f"  ⚙ 机制边界:同为 5 次复习,θ=0.9 时间隔/集中的强度优势 "
          f"{adv(0.9):.1f}×,θ=0.99(复习过早)时跌到 {adv(0.99):.1f}×"
          " —— 没有遗忘就没有间隔优势,三律自带边界条件")


    # ---- 断言 C ----
    r_m2, r_s2 = check_C()
    print(f"\n[断言C 分散学习效应] 同样 8 次学习动作(总时长固定),第 60 天:")
    print(f"  集中(全在第0天):平均保持率 {r_m2:.3f}")
    print(f"  分散(阈值触发):平均保持率 {r_s2:.3f}")
    assert r_m2 < 0.30 and r_s2 > 0.40, "分散学习效应失败:量级异常"
    assert r_s2 / r_m2 >= 1.8, f"分散学习效应失败:保持率比 {r_s2/r_m2:.2f} < 1.8"
    print(f"  ✓ 分散安排的长期保持为集中的 {r_s2/r_m2:.1f} 倍"
          " —— 学习总时长固定时,分散安排优于集中(分散学习效应)")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性分析:200 次抖动(β/c/ρ 各±10%;θ 取 SRS 实践区间 0.85-0.95)")
    n_draws, need = 200, 0.90
    jit = lambda base: base * random.uniform(0.9, 1.1)   # noqa: E731
    passes = {"A 间隔": 0, "B 扩展": 0, "C 分散": 0}
    for _ in range(n_draws):
        beta, c, rho = jit(BETA), jit(C), jit(RHO)
        # θ 不做对称抖动而取实践区间:θ→1 是「复习过早=没有遗忘」的退化区,
        # 间隔优势按机制消失(见上文机制边界演示)——那是三律的边界条件,
        # 不是三律不稳健;SRS 产品的真实阈值多在 0.85-0.95。
        theta = random.uniform(0.85, 0.95)
        kw = {"beta": beta, "c": c, "rho": rho, "theta": theta}
        ok_a = ok_b = ok_c = True
        # A:放宽为比值≥2(抽样 300)
        r_mj, r_sj, hl_mj, hl_sj = check_A(n=300, seed=13, **kw)
        ok_a = (r_sj > r_mj) and (r_sj / r_mj >= 2.0) and (hl_sj > 2.0 * hl_mj)
        # B:确定性三查 + 随机扩展占比
        Bj = check_B(beta=beta, c=c, theta=theta)
        for d in Bj.values():
            gaps = d["gaps"]
            if not (len(gaps) >= 3
                    and all(g2 > g1 for g1, g2 in zip(gaps, gaps[1:]))
                    and d["r_end"] >= theta - 1e-9):
                ok_b = False
        if not (all(Bj["难项"]["gaps"][k] < Bj["易项"]["gaps"][k]
                    for k in range(min(len(Bj["难项"]["gaps"]),
                                       len(Bj["易项"]["gaps"]))))
                and len(Bj["难项"]["gaps"]) >= len(Bj["易项"]["gaps"])):
            ok_b = False
        # C:放宽为比值≥1.5(抽样 300)
        r_mj2, r_sj2 = check_C(n=300, seed=17, **kw)
        ok_c = (r_sj2 > r_mj2) and (r_sj2 / r_mj2 >= 1.5)
        passes["A 间隔"] += ok_a
        passes["B 扩展"] += ok_b
        passes["C 分散"] += ok_c
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『指数遗忘+阈值触发的简单机制足以生成三律』,")
    print("  不是真实学习者数据的预测;增益/回退/阈值均为风格化参数。")
    print("  真实的最优间隔随测验延迟而变(塞佩达等 2006),换参数重跑、")
    print("  把增益改成随材料的函数,是使用本脚本的正确姿势(04 章 §二)。")


if __name__ == "__main__":
    main()
