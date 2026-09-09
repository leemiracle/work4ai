# -*- coding: utf-8 -*-
"""倒金字塔信息保留模拟:前置结构 vs 编年结构的截断保真实拍。

00 章(倒金字塔的信息熵视角/反直觉 1)与 03 章层 1(前缀最优装填)、
04 章走廊 2(自动摘要的保真断言)配套实验。纯标准库(random)。

信息量的近似: 把一篇稿拆成带权重的「信息单元」(核心 w=3 / 重要 w=2 / 背景 w=1),
每个单元用一组关键词表示——单元被认为「已传达」当且仅当其全部关键词
都出现在已读前缀文本里(关键词集合近似信息量,见 04 章走廊 2)。

同一批 13 个信息单元,两种装填(内容全同,只动段序):
  · 倒金字塔: 导语(5 核心)→ 展开(3 重要)→ 调查(2)→ 背景(3)   ——前缀最优
  · 编年体:   起烟经过 → 蔓延 → 扑救 → 结果 → 调查处置 → 提示  ——时序装填
对照: Part1  按段截断的信息覆盖率曲线——前置结构前三段的碾压级优势
      Part2  随机断线模拟(电报模型: 断点均匀落在全文字符上,段内按比例交付)
             ——倒金字塔当年为之而生的那个不可靠信道,今天的蒙特卡洛重演
      Part3  导语的「压缩映射」判定: 倒金字塔首段是否装下全部核心单元

跑法: python experiments/00_inverted_pyramid.py
"""

import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------- 信息单元库(关键词集合近似信息量) ----------
# weight: 3=核心(5W 要害) 2=重要(展开) 1=背景
FACTS = {
    "事件":     (3, ["光明商场", "火灾", "明火", "扑灭"]),
    "伤亡":     (3, ["2人轻伤"]),
    "时间":     (3, ["周三", "凌晨"]),
    "地点":     (3, ["滨河区", "光明商场"]),
    "扑救":     (3, ["消防", "控制火势", "2小时"]),
    "起火点":   (2, ["三层", "仓储区"]),
    "过火面积": (2, ["过火面积", "1200"]),
    "疏散":     (2, ["疏散", "120"]),
    "调查组":   (2, ["调查组"]),
    "初查原因": (1, ["电气线路"]),
    "商场背景": (1, ["1998"]),
    "停业整顿": (1, ["停业整顿"]),
    "防火提示": (1, ["冬季防火"]),
}
CORE = {name for name, (w, _) in FACTS.items() if w == 3}
TOTAL_INFO = sum(w for w, _ in FACTS.values())          # 27

# ---------- 两版文本(虚构示例稿,内容全同,只动段序) ----------
INVERTED = [
    "周三凌晨2时许,江城市滨河区光明商场发生火灾,消防救援队伍奋战2小时控制火势,"
    "明火已被扑灭,事故造成2人轻伤。",
    "起火点位于商场三层仓储区,过火面积约1200平方米,火灾期间共疏散周边居民与商户120余人。",
    "市政府当日成立事故调查组,起火原因初查指向电气线路老化。",
    "公开资料显示,该商场1998年开业,是滨河区体量最大的综合商场。",
    "商场目前已停业整顿,恢复营业时间待定。",
    "消防部门同期发布冬季防火提示,提醒商户检修线路。",
]
CHRONO = [
    "周三凌晨2时许,滨河区光明商场值班保安在巡查时发现顶棚飘出烟雾——这家1998年开业的"
    "商场货品密集,夜间仅有三名值班人员。",
    "烟雾很快转为明火,火势自三层仓储区向外蔓延,过火面积约1200平方米。",
    "江城消防出动28辆消防车,奋战2小时控制火势,并疏散周边居民与商户120余人。",
    "至清晨,光明商场火灾的明火被全部扑灭,事故造成2人轻伤,无重大伤亡。",
    "当日下午,市政府成立事故调查组,初步调查显示起火疑似电气线路老化,商场即日起停业整顿。",
    "消防部门当晚发布冬季防火提示,提醒老旧商户检修线路。",
]


def covered_facts(prefix_text):
    """前缀文本里已传达的信息单元集合: 单元全部关键词都出现才算传达。"""
    return {name for name, (_, kws) in FACTS.items()
            if all(kw in prefix_text for kw in kws)}


def info_of(fact_names):
    return sum(FACTS[n][0] for n in fact_names)


def prefix_infos(paras):
    """返回逐段前缀的 (累计信息量列表, 每段增量列表)。"""
    cum, inc, acc = [], [], 0
    for k in range(1, len(paras) + 1):
        got = info_of(covered_facts("".join(paras[:k])))
        inc.append(got - acc)
        acc = got
        cum.append(got)
    return cum, inc


# ---------- Part 1:按段截断的覆盖率曲线 ----------
def part1_coverage():
    bar = "=" * 64
    print(bar)
    print("Part 1 · 按段截断的信息覆盖率: 前置结构 vs 编年结构(同 13 单元,总信息 %d)" % TOTAL_INFO)
    print(bar)
    cum_i, inc_i = prefix_infos(INVERTED)
    cum_c, inc_c = prefix_infos(CHRONO)
    cov_i = [c / TOTAL_INFO for c in cum_i]
    cov_c = [c / TOTAL_INFO for c in cum_c]

    print("%6s %10s %6s   %10s %6s   %8s" % ("读至第k段", "倒金字塔", "增量", "编年体", "增量", "前置优势"))
    for k in range(len(cov_i)):
        print("%6d %10.4f %6d   %10.4f %6d   %+8.4f"
              % (k + 1, cov_i[k], inc_i[k], cov_c[k], inc_c[k], cov_i[k] - cov_c[k]))

    print("→ 倒金字塔前三段装下 %.0f%% 的信息量,编年体同期只有 %.0f%%——"
          % (100 * cov_i[2], 100 * cov_c[2]))
    print("  前置优势最陡处恰在前两段: 导语独占 %.0f%%,是全文的压缩映射。"
          % (100 * cov_i[0]))

    # 断言组: 前置结构的前三段优势(00 章美之时刻 1 的数值化)
    assert cov_i[0] >= 0.5, "倒金字塔导语应装下过半信息量(压缩映射判定)"
    assert cov_i[0] > cov_c[0], "单读首段,倒金字塔必须压制编年体"
    assert cov_i[2] >= 0.8, "前置结构前三段覆盖率应 >=80%(03 章前缀最优)"
    assert cov_i[2] - cov_c[2] >= 0.2, "前三段前置优势应 >=20 个百分点"
    assert all(cov_i[k] >= cov_c[k] for k in range(3)), "前缀优势在 k=1..3 逐段成立"
    assert cov_i[-1] == cov_c[-1] == 1.0, "读完全文,两结构信息量必须打平(内容全同)"
    return cum_i, inc_i, cum_c, inc_c


# ---------- Part 2:随机断线模拟(电报模型) ----------
def expected_retention(paras, cum, inc):
    """解析期望: 断点均匀落在全文字符上;落在第 j 段内按线性比例交付该段信息。

    E[保留] = Σ_j (L_j/T) · (cum_{j-1} + inc_j/2),其中 cum_{-1}=0。
    """
    lens = [len(p) for p in paras]
    total = sum(lens)
    exp = 0.0
    for j, L in enumerate(lens):
        base = cum[j - 1] if j else 0.0
        exp += (L / total) * (base + inc[j] / 2)
    return exp / TOTAL_INFO


def mc_retention(paras, cum, inc, trials=50000, seed=20260907):
    """蒙特卡洛: 断点均匀取自 [0, 总字符数),重复 trials 次取平均保留率。

    断点落在第 j+1 段内 → 已完整交付前 j 段 + 该段内的字符比例 × 该段信息增量。
    """
    rng = random.Random(seed)
    lens = [len(p) for p in paras]
    edges = []
    acc = 0
    for L in lens:
        acc += L
        edges.append(acc)                      # edges[j] = 前 j+1 段的累计字符
    total = acc
    s = 0.0
    for _ in range(trials):
        cut = rng.uniform(0, total)
        j = 0
        while j < len(edges) and cut >= edges[j]:
            j += 1                             # j = 完整交付的段数
        if j >= len(lens):
            s += cum[-1]                       # 断在末尾之后: 全文到达
        else:
            start = edges[j - 1] if j else 0
            frac = (cut - start) / lens[j]
            s += (cum[j - 1] if j else 0.0) + frac * inc[j]
    return s / trials / TOTAL_INFO


def part2_random_cut(cum_i, inc_i, cum_c, inc_c):
    print()
    print("=" * 64)
    print("Part 2 · 随机断线模拟(电报模型: 断点均匀落在全文字符上,段内按比例交付)")
    print("=" * 64)
    exp_i = expected_retention(INVERTED, cum_i, inc_i)
    exp_c = expected_retention(CHRONO, cum_c, inc_c)
    mc_i = mc_retention(INVERTED, cum_i, inc_i)
    mc_c = mc_retention(CHRONO, cum_c, inc_c)
    print("%-8s %10s %10s   %s" % ("结构", "解析期望", "蒙特卡洛", "(样本 50000)"))
    print("%-8s %10.4f %10.4f" % ("倒金字塔", exp_i, mc_i))
    print("%-8s %10.4f %10.4f" % ("编年体", exp_c, mc_c))
    print("→ 同一条随时会断的线路,倒金字塔的期望信息保留率高出 %.1f 个百分点:"
          % ((exp_i - exp_c) * 100))
    print("  结构把『断线』从风险变成了可接受的截断——这就是 1860s 战地电报的算术。")
    assert abs(mc_i - exp_i) < 0.02, "蒙特卡洛应收敛到解析期望(倒金字塔)"
    assert abs(mc_c - exp_c) < 0.02, "蒙特卡洛应收敛到解析期望(编年体)"
    assert exp_i - exp_c >= 0.10, "随机断线下前置结构的期望保留优势应 >=10 个百分点"


# ---------- Part 3:导语的压缩映射判定 ----------
def part3_lead_mapping():
    print()
    print("=" * 64)
    print("Part 3 · 导语的压缩映射判定: 首段是否装下全部核心单元")
    print("=" * 64)
    lead_i = covered_facts(INVERTED[0])
    lead_c = covered_facts(CHRONO[0])
    core_names = "、".join(sorted(CORE))
    got_i = "、".join(sorted(lead_i & CORE))
    got_c = "、".join(sorted(lead_c & CORE))
    missing = "、".join(sorted(CORE - lead_c))
    print("核心单元(%d 个): %s" % (len(CORE), core_names))
    print("倒金字塔首段覆盖 %d/%d: %s" % (len(lead_i & CORE), len(CORE), got_i))
    print("编年体首段覆盖   %d/%d: %s" % (len(lead_c & CORE), len(CORE), got_c))
    print("编年体首段缺失: %s——读者要读到第 4 段才知道结果" % missing)
    assert CORE <= lead_i, "倒金字塔导语=压缩映射: 核心单元必须全在首段"
    assert {"事件", "伤亡", "扑救"} <= (CORE - lead_c), "编年体首段应缺失结论性核心单元"
    print("→ 『首段即全文』不是修辞,是可断言的结构性质(04 章摘要保真断言的种子)。")


if __name__ == "__main__":
    ci, ii, cc, ic = part1_coverage()
    part2_random_cut(ci, ii, cc, ic)
    part3_lead_mapping()
    print()
    print("[ALL ASSERTS PASSED] 倒金字塔信息保留模拟 全部命中。")
