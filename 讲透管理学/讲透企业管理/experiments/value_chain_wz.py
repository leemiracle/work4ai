# -*- coding: utf-8 -*-
"""价值链与微笑曲线:多环节利润池分配仿真。

00-体系结构.md(微笑曲线反直觉/美之时刻 2)、03-可构造与结构.md(构造 1:价值链
schema)与 04-企业管理转代码.md(走廊 1)的配套实验。纯标准库(random/math)。

模型(议价能力 × 进入壁垒的利润池分配):
  价值链四环节:研发 → 制造 → 品牌 → 渠道。
  微笑曲线口径:左端=研发,右端=品牌+渠道(营销侧),中段=制造。
  环节 i 的分配权重      w_i = b_i × e_i
    b_i:议价能力(对上下游的谈判力——掌握替代选择多的一方更强)
    e_i:进入壁垒/不可替代性(专利、模具、品牌资产、渠道网络……)
  全链利润池 P(终端价格高于总成本的部分)按权重比例瓜分:
    份额 s_i = w_i / Σ w_j;环节利润 = s_i × P;
    环节利润率 m_i = s_i × P / R_i(R_i=环节营收基数;制造环节营收基数最大,
    所以同一份额摊到巨大的分母上,利润率被摊薄——这正是微笑曲线的机制核)。
  微笑指数 SMILE = 两端环节平均利润率 / 制造环节利润率,>1 即微笑曲线成立。

蒙特卡洛层:每一轮谈判各环节的"当日话语权"带噪声 w_i×(1+ε),ε~U(−δ,+δ);
  T 轮平均逼近期望分配(大数定律),同时检验分配机制对谈判噪声的稳健性。

核心断言:
  ① 制造进入壁垒下降(产能过剩:人人可进、环节高度可替代)→ 制造利润率下降、
     两端份额上升,微笑指数加深;
  ② 某环节创新抬高自身不可替代性(e_i↑)→ 该环节份额上升、其余环节份额
     下降(利润池总盘不变下的零和重分配);制造环节创新则微笑曲线变平;
  ③ 微笑指数对制造壁垒参数严格单调(壁垒越高曲线越平),且蒙特卡洛均值与
     解析解一致(噪声不改变分配格局)。

跑法: python3 -u experiments/value_chain_wz.py
"""

import math
import random

SEED = 20260907
T = 6000        # 谈判轮数(蒙特卡洛)
DELTA = 0.30    # 每轮话语权噪声幅度 ±30%
POOL = 300.0    # 全链利润池(每台终端产品,货币单位)

# 环节:(名称, 议价能力 b, 进入壁垒 e, 营收基数 R)
LINKS = [
    ("研发", 1.00, 1.60, 160.0),   # 左端:技术专利与标准,营收基数小
    ("制造", 0.80, 0.70, 620.0),   # 中段:组装制造,营收基数最大→利润率被摊薄
    ("品牌", 0.90, 1.30, 200.0),   # 右端:品牌资产
    ("渠道", 1.10, 1.40, 420.0),   # 右端:渠道网络
]
ENDS = ("研发", "品牌", "渠道")     # 微笑曲线两端(右端=品牌+渠道)
MID = "制造"


def shares(bargain, barriers):
    """解析份额:w_i = b_i×e_i 归一化。"""
    ws = [b * e for b, e in zip(bargain, barriers)]
    tot = sum(ws)
    return [w / tot for w in ws]


def margins(bargain, barriers, revs, pool=POOL):
    """解析环节利润率:份额×利润池/营收基数。"""
    return [s * pool / r for s, r in zip(shares(bargain, barriers), revs)]


def smile_index(bargain, barriers, revs, pool=POOL):
    """微笑指数=两端平均利润率/制造利润率。"""
    ms = dict(zip([l[0] for l in LINKS], margins(bargain, barriers, revs, pool)))
    end_avg = sum(ms[n] for n in ENDS) / len(ENDS)
    return end_avg / ms[MID]


def mc_shares(bargain, barriers, t=T, delta=DELTA, rng=None):
    """蒙特卡洛份额:每轮话语权带 ±δ 均匀噪声,T 轮平均。"""
    rng = rng or random.Random(SEED)
    acc = [0.0] * len(bargain)
    for _ in range(t):
        ws = [b * e * max(0.05, 1.0 + rng.uniform(-delta, delta))
              for b, e in zip(bargain, barriers)]
        tot = sum(ws)
        for i, w in enumerate(ws):
            acc[i] += w / tot
    return [a / t for a in acc]


def report(title, bargain, barriers):
    names = [l[0] for l in LINKS]
    revs = [l[3] for l in LINKS]
    ms = dict(zip(names, margins(bargain, barriers, revs)))
    ss = dict(zip(names, shares(bargain, barriers)))
    print("== %s ==" % title)
    for n in names:
        bar = "#" * max(1, int(round(ms[n] * 40)))
        print("  %-4s 份额 %6.1f%%  利润率 %6.2f%%  %s"
              % (n, 100 * ss[n], 100 * ms[n], bar))
    sm = smile_index(bargain, barriers, revs)
    print("  微笑指数(两端/制造) = %.2f\n" % sm)
    return sm


def main():
    names = [l[0] for l in LINKS]
    base_b = [l[1] for l in LINKS]
    base_e = [l[2] for l in LINKS]
    revs = [l[3] for l in LINKS]

    # ---- 0. 基线:微笑曲线成立 ----
    sm_base = report("基线:研发1.6 / 制造0.7 / 品牌1.3 / 渠道1.4", base_b, base_e)
    assert sm_base > 1.0, "基线参数下微笑曲线应成立(指数>1),实际 %.2f" % sm_base

    # ---- ① 制造壁垒下降=产能过剩 → 利润池向两端迁移,微笑加深 ----
    e_oversupply = list(base_e)
    e_oversupply[1] = 0.40                      # 制造人人可进
    sm_over = report("制造产能过剩(制造壁垒 0.7→0.4)", base_b, e_oversupply)
    ms_base = margins(base_b, base_e, revs)
    ms_over = margins(base_b, e_oversupply, revs)
    ss_base = shares(base_b, base_e)
    ss_over = shares(base_b, e_oversupply)
    assert ms_over[1] < ms_base[1], "产能过剩应压低制造利润率"
    assert sum(ss_over[i] for i, n in enumerate(names) if n in ENDS) \
        > sum(ss_base[i] for i, n in enumerate(names) if n in ENDS), \
        "利润池应向两端迁移"
    assert sm_over > sm_base, "微笑曲线应加深(%.2f > %.2f)" % (sm_over, sm_base)

    # ---- ② 创新抬高不可替代性 → 利润池重分配(零和) ----
    e_inno = list(base_e)
    e_inno[0] = 2.40                            # 研发专利化:不可替代性↑
    sm_inno = report("研发创新(研发壁垒 1.6→2.4)", base_b, e_inno)
    ss_inno = shares(base_b, e_inno)
    assert ss_inno[0] > ss_base[0], "创新环节份额应上升"
    for i in (1, 2, 3):
        assert ss_inno[i] < ss_base[i], "其余环节份额应下降(零和重分配)"
    assert sm_inno > sm_base, "研发更不可替代时微笑应更深"

    e_mfg_inno = list(base_e)
    e_mfg_inno[1] = 1.50                        # 制造工艺创新:自身壁垒↑
    sm_mfg = report("制造工艺创新(制造壁垒 0.7→1.5)", base_b, e_mfg_inno)
    assert shares(base_b, e_mfg_inno)[1] > ss_base[1], "制造创新应夺回份额"
    assert sm_mfg < sm_base, "制造不可替代性上升时微笑曲线应变平(%.2f < %.2f)" \
        % (sm_mfg, sm_base)

    # ---- ③ 微笑指数对制造壁垒严格单调 + 蒙特卡洛与解析一致 ----
    grid = [0.30 + 0.20 * k for k in range(10)]  # 0.30 ... 2.10
    smiles = []
    print("== 制造壁垒扫描(微笑指数单调性)==")
    for e_m in grid:
        e_scan = list(base_e)
        e_scan[1] = e_m
        sm = smile_index(base_b, e_scan, revs)
        smiles.append(sm)
        print("  制造壁垒 e=%.2f → 微笑指数 %.2f" % (e_m, sm))
    assert all(smiles[k] > smiles[k + 1] + 1e-9 for k in range(len(smiles) - 1)), \
        "微笑指数应随制造壁垒严格单调下降(壁垒↑曲线变平)"
    assert smiles[0] > 2.0 * smiles[-1], "低壁垒与高壁垒两端应差出一倍以上"

    mc = mc_shares(base_b, base_e)
    an = shares(base_b, base_e)
    print("\n== 蒙特卡洛(T=%d, δ=±%.0f%%)vs 解析 ==" % (T, 100 * DELTA))
    for i, n in enumerate(names):
        print("  %-4s 解析 %6.1f%% | 蒙特卡洛 %6.1f%% | 差 %+.3f%%"
              % (n, 100 * an[i], 100 * mc[i], 100 * (mc[i] - an[i])))
        assert abs(mc[i] - an[i]) < 0.012, "蒙特卡洛份额偏离解析解超阈值"
    ms_mc = dict(zip(names, [s * POOL / r for s, r in zip(mc, revs)]))
    end_avg_mc = sum(ms_mc[n] for n in ENDS) / len(ENDS)
    sm_mc = end_avg_mc / ms_mc[MID]
    assert abs(sm_mc - sm_base) < 0.6, \
        "蒙特卡洛微笑指数应贴近解析值(|%.2f−%.2f|<0.6)" % (sm_mc, sm_base)

    print("\n全部断言通过:微笑曲线=议价能力×进入壁垒的利润池分配结果;"
          "壁垒参数决定曲线深浅,创新决定利润池归属,噪声不改变格局。")


if __name__ == "__main__":
    main()
