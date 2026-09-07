# -*- coding: utf-8 -*-
"""教育扩张长时段受控模拟:梯度律/压缩律/残差律三律检验(00/03/04 章配套实验)。

主题呼应建制四波(00 章 §1.1):本脚本把后两波——义务教育/国民教育(波3)与
大众高等教育(波4)——的长时段扩张做成受控模拟:毛入学率随人均 GDP(指数增长,
参数化)越过层级阈值而逻辑斯蒂扩张,性别差距用「随全球规范扩散而指数衰减的
门槛差」建模。然后断言教育学三个经验通说:

  A. 梯度律:初等→中等→高等依次启动(启动年排序,间隔≥12年),各层增长呈
     S 型(逻辑斯蒂对称性:10%→50% 用时 ≈ 50%→90% 用时);
  B. 压缩律:后发国家同一阶段(初等 20%→80%)扩张用时短于先行国
     ——二战后教育扩张数据的通说(「后发压缩」);
  C. 残差律:性别差距随扩张收敛(已大幅扩张层:历史峰值>2020 年),且高等教育层
     残差最大(2020 年:高等>中等>初等;GPI 性别平指数同向改善)。

⚠ 史学纪律(02/04 章):
  1. 六国为「虚拟国家原型」(先行·英普型/中期·明治型/后发·东亚型…),
     参数是通说量级的风格化取值,不是任何真实国家的估计;
  2. 模拟证明的是「如此简单的机制足以生成三律」(机制充分性),
     不是「历史就是如此」——政治动员/战争中断/统计口径变化均未入模;
  3. 通说依据:Trow 1973 高教阶段论(15%/50% 阈值)、发展与教育社会学的
     后发压缩综述、各国 GPI 数据的长时段模式(均为综述级通说,未逐条核数);
  4. 敏感性分析:文末 Monte Carlo(200 次参数抖动)报告三律通过率——
     换参数重跑=检验叙事的结构刚性(04 章 §0 的正确用法)。

跑法: python experiments/enrollment_waves.py
"""

import math
import random
import sys

# ----------------------------- 模型参数(基准情形) -----------------------------
YEARS_END = 2020
LEVELS = ("初等", "中等", "高等")
THETA = {"初等": 0.55, "中等": 1.10, "高等": 1.90}   # 层级激活阈值(相对起点的对数GDP增量)
KAPPA = 6.0                                          # 逻辑斯蒂陡度(每对数GDP单位)
CAP = 100.0                                          # 毛入学率上限(%)
DELTA0 = {"初等": 0.80, "中等": 1.20, "高等": 1.80}   # 女性初始门槛差(对数GDP单位)
NORM_YEAR = 1900                                     # 性别规范全球扩散的参照年
LAMBDA = 0.025                                       # 门槛差年衰减率

# 六个虚拟国家原型:(名称, 现代学制建制起点年, 人均GDP对数增速)
# 增速随后发程度提高 = 「赶超」通说的风格化;压缩律的机制源。
COUNTRIES = [
    ("先行·英普型", 1805, 0.012),
    ("先行·欧陆型", 1830, 0.013),
    ("中期·明治型", 1875, 0.018),
    ("中期·拉美型", 1900, 0.020),
    ("后发·东亚型", 1950, 0.032),
    ("后发·非洲型", 1960, 0.030),
]
GROUPS = {"先行": [0, 1], "中期": [2, 3], "后发": [4, 5]}


def logistic(z):
    return CAP / (1.0 + math.exp(-z))


def simulate(start, r, theta=None, kappa=KAPPA, delta0=None, lam=LAMBDA):
    """受控模拟一国序列。返回 {层级: {"male": [(年,值)...], "female": [(年,值)...]}}。

    机制:对数GDP增量 g = r*(年-起点),单调增长;
    男/女毛入学率 = logistic(kappa*(g - 阈值)) 与 logistic(kappa*(g - 阈值 - 门槛差)),
    门槛差自 1900 年(全球规范扩散参照年)起以年率 lam 指数衰减。
    """
    theta = theta if theta is not None else THETA
    delta0 = delta0 if delta0 is not None else DELTA0
    out = {}
    for lv in LEVELS:
        male, female = [], []
        for year in range(start, YEARS_END + 1):
            g = r * (year - start)
            male.append((year, logistic(kappa * (g - theta[lv]))))
            off = delta0[lv] * math.exp(-lam * max(0, year - NORM_YEAR))
            female.append((year, logistic(kappa * (g - theta[lv] - off))))
        out[lv] = {"male": male, "female": female}
    return out


# ----------------------------- 序列统计工具 -----------------------------
def crossing(series, thresh):
    """首个达到阈值的年份;未达到返回 None。series=[(年, 值)...]"""
    for year, v in series:
        if v >= thresh:
            return year
    return None


def span(series, lo, hi):
    """从 lo% 到 hi% 的用时(年);任一未达到返回 None。"""
    t_lo, t_hi = crossing(series, lo), crossing(series, hi)
    return None if t_lo is None or t_hi is None else t_hi - t_lo


def gap_series(sim, lv):
    """性别差序列(男-女,百分点)。"""
    return [(y, m - f) for (y, m), (_, f) in
            zip(sim[lv]["male"], sim[lv]["female"])]


def value_at(series, year):
    for y, v in series:
        if y == year:
            return v
    return None


# ----------------------------- 三律检验 -----------------------------
def check_gradient(sim):
    """A 梯度律:启动年 初等<中等<高等 且间隔≥12年;S 型对称性(±25%)。"""
    acts = {lv: crossing(sim[lv]["male"], 10.0) for lv in LEVELS}
    if any(a is None for a in acts.values()):
        return False
    if not (acts["初等"] < acts["中等"] < acts["高等"]
            and acts["高等"] - acts["初等"] >= 12):
        return False
    for lv in LEVELS:                                  # S 型:前后半程用时接近
        t10, t50, t90 = (crossing(sim[lv]["male"], p) for p in (10.0, 50.0, 90.0))
        if None not in (t10, t50, t90):
            first, second = t50 - t10, t90 - t50
            if abs(first - second) > 0.25 * (t90 - t10):
                return False
    return True


def primary_duration(sim):
    """B 压缩律的被测:初等 20%→80% 用时(年)。"""
    return span(sim["初等"]["male"], 20.0, 80.0)


def check_residual(sim):
    """C 残差律:2020 年性别差 高等>中等>初等;已大幅扩张的层级(2020 男毛入学率
    ≥80%)其性别差历史峰值>2020 值(收敛);仍在扩张中的层级(后发国高教)收敛
    未完——残差仍在释放,恰是「高教层收敛最慢」的模型表述,故豁免收敛检验。"""
    gaps = {lv: gap_series(sim, lv) for lv in LEVELS}
    g2020 = {lv: value_at(gaps[lv], YEARS_END) for lv in LEVELS}
    if None in g2020.values():
        return False
    order = g2020["高等"] > g2020["中等"] > g2020["初等"]
    converge = True
    for lv in LEVELS:
        male2020 = value_at(sim[lv]["male"], YEARS_END)
        if male2020 >= 80.0:                           # 仅检验已大幅扩张的层级
            converge = converge and max(v for _, v in gaps[lv]) > g2020[lv]
    return order and converge


def gpi(sim, lv, year):
    """性别平指数 GPI=女/男(男<5% 视为层级未开,返回 None)。"""
    m, f = value_at(sim[lv]["male"], year), value_at(sim[lv]["female"], year)
    return None if m is None or m < 5.0 else f / m


# ----------------------------- 基准情形报告 -----------------------------
def main():
    if hasattr(sys.stdout, "reconfigure"):            # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    random.seed(20260907)                             # Monte Carlo 可复现

    print("=" * 72)
    print("教育扩张长时段受控模拟:梯度律·压缩律·残差律(虚拟国家原型 6 国)")
    print("=" * 72)

    sims = {name: simulate(start, r) for name, start, r in COUNTRIES}

    print(f"\n{'国家':<10}{'初等启动':>6}{'中等启动':>6}{'高等启动':>6}{'初等20→80用时':>12}")
    for name, start, r in COUNTRIES:
        assert check_gradient(sims[name]), f"梯度律失败:{name}"
        acts = {lv: crossing(sims[name][lv]["male"], 10.0) for lv in LEVELS}
        dur = primary_duration(sims[name])
        print(f"{name:<12}{acts['初等']:>8}{acts['中等']:>8}{acts['高等']:>8}{dur:>10}")
    print("\n断言A 梯度律通过 ✓ —— 六国全部 初等→中等→高等 依次启动(间隔≥12年),"
          "增长呈 S 型(半程对称)")

    durations = {n: primary_duration(sims[n]) for n, _, _ in COUNTRIES}
    gm = {g: sum(durations[COUNTRIES[i][0]] for i in idxs) / len(idxs)
          for g, idxs in GROUPS.items()}
    print(f"\n断言B 压缩律:初等 20%→80% 平均用时 先行 {gm['先行']:.1f} 年"
          f" / 中期 {gm['中期']:.1f} 年 / 后发 {gm['后发']:.1f} 年")
    assert gm["后发"] < gm["中期"] < gm["先行"], "压缩律失败:后发未快于先行"
    late_max = max(durations[COUNTRIES[i][0]] for i in GROUPS["后发"])
    early_min = min(durations[COUNTRIES[i][0]] for i in GROUPS["先行"])
    assert late_max < early_min, "压缩律失败:最慢后发国仍慢于最快先行国"
    print(f"              最慢后发 {late_max} 年 < 最快先行 {early_min} 年"
          f" —— 后发压缩成立 ✓")

    print(f"\n{'国家':<12}{'高教差1960':>9}{'高教差2020':>9}   2020 三层差(初/中/高)")
    t60, t20, gp60, gp20 = [], [], [], []
    for name, _, _ in COUNTRIES:
        assert check_residual(sims[name]), f"残差律失败:{name}"
        gaps = {lv: gap_series(sims[name], lv) for lv in LEVELS}
        g2020 = {lv: value_at(gaps[lv], YEARS_END) for lv in LEVELS}
        g1960 = value_at(gaps["高等"], 1960) or 0.0
        t60.append(g1960)
        t20.append(g2020["高等"])
        for yr, acc in ((1960, gp60), (YEARS_END, gp20)):
            v = gpi(sims[name], "高等", yr)
            if v is not None:
                acc.append(v)
        print(f"{name:<12}{g1960:>10.1f}{g2020['高等']:>10.1f}"
              f"      {g2020['初等']:.2f} / {g2020['中等']:.2f} / {g2020['高等']:.2f}")
    m60, m20 = sum(t60) / len(t60), sum(t20) / len(t20)
    assert m60 > m20, "残差律失败:高教性别差未随扩张收敛(1960→2020)"
    print(f"\n断言C 残差律通过 ✓ —— 高教性别差 六国均值 {m60:.1f}→{m20:.1f} 百分点;"
          " 2020 残差 高等>中等>初等")
    assert gp20 and sum(gp20) / len(gp20) > sum(gp60) / len(gp60), "GPI 未改善"
    print(f"              高教 GPI(已开国均值) {sum(gp60)/len(gp60):.2f} → "
          f"{sum(gp20)/len(gp20):.2f} —— 性别平指数同向改善 ✓")

    # ------------------- Monte Carlo 敏感性分析(±10% 参数抖动 ×200) -------------------
    print("\n" + "=" * 72)
    print("Monte Carlo 敏感性分析:200 次抖动(增速/陡度/阈值/门槛差/衰减率各±10%)")
    n_draws, need = 200, 0.90
    passes = {"A 梯度": 0, "B 压缩": 0, "C 残差": 0}
    for _ in range(n_draws):
        jit = lambda base: base * random.uniform(0.9, 1.1)   # noqa: E731
        theta = {lv: jit(THETA[lv]) for lv in LEVELS}
        delta0 = {lv: jit(DELTA0[lv]) for lv in LEVELS}
        kappa, lam = jit(KAPPA), jit(LAMBDA)
        ok_a, ok_c, durs = True, True, {}
        for name, start, r0 in COUNTRIES:
            sim = simulate(start, jit(r0), theta, kappa, delta0, lam)
            ok_a = ok_a and check_gradient(sim)
            ok_c = ok_c and check_residual(sim)
            durs[name] = primary_duration(sim)
        g = {k: sum(durs[COUNTRIES[i][0]] for i in idxs) / len(idxs)
             for k, idxs in GROUPS.items()}
        passes["A 梯度"] += ok_a
        passes["B 压缩"] += g["后发"] < g["中期"] < g["先行"]
        passes["C 残差"] += ok_c
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"
    print("\n⚠ 史学纪律提醒:本模拟证明『阈值+增速的简单机制足以生成三律』,")
    print("  不是历史复刻;Monte Carlo 已示参数稳健性,换机制(如加入政治动员")
    print("  变量)重跑是使用本脚本的正确姿势(04 章 §0)。")
    print("  通说依据为综述级陈述(未逐条核数);虚拟国家原型,非真实国别数据。")


if __name__ == "__main__":
    main()
