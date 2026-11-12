# -*- coding: utf-8 -*-
# 格律、对仗与文体兴替:中国古代文学家族(GB/T 13745 75024)的最小计算实验。
#
# 对应章:00-体系结构.md 七节(反直觉发现三律)、03-可构造与结构.md(可构造
# 谱系左端三对象)、04-中国古代文学转代码.md(三条代码走廊)。纯标准库
# (math/random/statistics),无第三方依赖;随机处固定种子,逐次可复现。
#
# 三律:
#   律一 律诗格律的形式系统(五言律诗):
#       平仄骨架由「对(联内偶位相反)+粘(联间偶位相承)+韵句限定(偶数句
#       及入韵首句必平收)」三条规则,从首句起式确定性推导出四式标准谱
#       (仄起/平起 x 首句入韵/不入韵,即王力《诗词格律》四式)。
#       断言:(1)四式谱可程序化推导、与通行四式逐一相同、且两两互不相同
#       (2)在「一三不论、二四分明」近似下(五言句内第 1/3 字自由、
#       第 2/4 字与句脚锁定),每式自由位=16、可行变体数=2^16=65536
#       ——逐句枚举 2^5 与联级全枚举 2^10 双重验证;再叠「避孤平(仄平
#       仄仄平)/避三平调(句脚三连平)」两条细律,四式合计从 262144 收缩
#       到 29952——格律是约束编程:骨架定死,自由位有限,禁手再砍一刀。
#   律二 对仗的平行匹配(颔联/颈联的词性配对):
#       出句按词性序列模板生成(数量+禽鸟+动词+颜色+景物,五言工对模板),
#       对句从按词性分桶的词库中取对位词。断言:(1)平行约束下合格对句数
#       =各位置桶大小之积(161280,全枚举验证);叠「避同位重字」层后
#       =∏(桶-1)=99099,同样全枚举验证 (2)桶大小不齐时,对最窄桶 +1 词
#       带来的总增益最大(敏感度=总数/桶宽,argmax 恰为 argmin)——
#       「工对难得」的组合学本体:对仗的上限由最贫词性的桶决定。
#   律三 「一代有一代之文学」的错峰(王国维《宋元戏曲考·序》命题):
#       诗/词/曲/小说四体裁各按双 logistic 生命周期(上升 logistic x
#       下降 logistic)兴起-鼎盛-衰落,峰值错开。断言:(1)相邻体裁峰值
#       间隔显著大于 0(实测约 200-400 年),且相邻体裁的活跃重叠期
#       (各自归一化强度>=0.55)非空并容纳跨界文人(苏轼之于诗词/白朴
#       之于词曲) (2)主导体裁(强度 argmax)序列恒为[诗->词->曲->小说],
#       每次换代开关都落在相邻两峰之间,各体裁峰值落在自己的主导期内,
#       断代代表年(盛唐 750/南宋 1200/元 1320/明 1580/清 1750)与
#       「唐之诗、宋之词、元之曲、明清之小说」逐一对应——文体的兴衰
#       周期与王朝周期错峰更替,不是同步开关。
#
# 跑法: python -u experiments/meter_parallel_genres.py

import math
import random

PING, ZE = 1, 0  # 平=1,仄=0(只作二值约束使用,不涉音韵构拟)


def sigma(x):
    return 1.0 / (1.0 + math.exp(-x))


# ==================== 律一:律诗格律的形式系统 ====================
# 五言律的四種句式(平=1/仄=0):
#   A 仄仄平平仄(仄起仄收) B 平平仄仄平(平起平收)
#   C 平平平仄仄(平起仄收) D 仄仄仄平平(仄起平收)
TYPE_A, TYPE_B, TYPE_C, TYPE_D = (0, 0, 1, 1, 0), (1, 1, 0, 0, 1), (1, 1, 1, 0, 0), (0, 0, 0, 1, 1)
RHYME_TYPES = (TYPE_B, TYPE_D)    # 韵句:平收
NONRHYME_TYPES = (TYPE_A, TYPE_C)  # 非韵句:仄收
TYPE_NAME = {TYPE_A: "仄仄平平仄", TYPE_B: "平平仄仄平",
             TYPE_C: "平平平仄仄", TYPE_D: "仄仄仄平平"}

# 通行四式(王力《诗词格律》口径)——推导结果的对照标准
CANONICAL = {
    ("仄起", "不入韵"): [TYPE_A, TYPE_B, TYPE_C, TYPE_D, TYPE_A, TYPE_B, TYPE_C, TYPE_D],
    ("仄起", "入韵"):   [TYPE_D, TYPE_B, TYPE_C, TYPE_D, TYPE_A, TYPE_B, TYPE_C, TYPE_D],
    ("平起", "不入韵"): [TYPE_C, TYPE_D, TYPE_A, TYPE_B, TYPE_C, TYPE_D, TYPE_A, TYPE_B],
    ("平起", "入韵"):   [TYPE_B, TYPE_D, TYPE_A, TYPE_B, TYPE_C, TYPE_D, TYPE_A, TYPE_B],
}


def rhyme_mate(line):
    # 「对」:联内对句取唯一一个平收句式,其第 2/4 字(下标 1/3)与本句相反
    cands = [t for t in RHYME_TYPES if t[1] != line[1] and t[3] != line[3]]
    assert len(cands) == 1, "对规则下对句应唯一"
    return cands[0]


def adhere_mate(line):
    # 「粘」:下联出句取唯一一个仄收句式,其第 2/4 字与上联对句相承(相同)
    cands = [t for t in NONRHYME_TYPES if t[1] == line[1] and t[3] == line[3]]
    assert len(cands) == 1, "粘规则下出句应唯一"
    return cands[0]


def derive_schema(first, first_rhymes):
    # 从首句起式,对/粘交替推导八句全谱(纯确定性,无搜索)
    assert (first[4] == PING) == first_rhymes, "首句句式与入韵与否应一致"
    lines = [first]
    for _ in range(3):           # 首联之外的三个联
        lines.append(rhyme_mate(lines[-1]))    # 对句
        lines.append(adhere_mate(lines[-1]))   # 粘:下一联出句
    lines.append(rhyme_mate(lines[-1]))        # 尾联对句
    for i in (1, 3, 5, 7):
        assert lines[i][4] == PING, "偶数句必平收(押韵)"
    for i in (2, 4, 6):
        assert lines[i][4] == ZE, "非首句的奇数句必仄收"
    return lines


def feasible_line_patterns(t, strict=False):
    # 「一三不论、二四分明」:句内第 2/4 字与句脚(第 5 字)锁定,第 1/3 字自由。
    # 枚举全部 2^5=32 种平仄组合,过滤出与骨架在锁定位一致者。
    out = []
    for bits in range(32):
        p = tuple((bits >> (4 - i)) & 1 for i in range(5))
        if p[1] != t[1] or p[3] != t[3] or p[4] != t[4]:
            continue
        if strict:
            # 细律一(避孤平):B 式句第一字拗仄且第三字不救 -> 仄平仄仄平
            if t is TYPE_B and p[0] == ZE and p[2] == ZE:
                continue
            # 细律二(避三平调):句脚三连平
            if p[2] == PING and p[3] == PING and p[4] == PING:
                continue
        out.append(p)
    return out


def act1():
    print("=" * 84)
    print("律一 律诗格律的形式系统(五言律诗:对+粘+韵句限定,从首句起式推导)")
    print("=" * 84)

    # 断言 1a:四式谱可程序化推导,且与通行四式(王力《诗词格律》口径)逐一相同
    schemas = {}
    for first, rhymes in [(TYPE_A, False), (TYPE_D, True), (TYPE_C, False), (TYPE_B, True)]:
        key = ("仄起" if first[1] == ZE else "平起", "入韵" if rhymes else "不入韵")
        schemas[key] = derive_schema(first, rhymes)
    print("  推导出的四式标准谱:")
    for key, lines in schemas.items():
        joined = " / ".join("".join("平" if c else "仄" for c in ln) for ln in lines[:2])
        assert lines == CANONICAL[key], f"{key} 推导谱与通行谱不符"
        print(f"    {key[0]}首句{key[1]}: {joined} / ...(八句)")
    keys = list(schemas)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            assert schemas[keys[i]] != schemas[keys[j]], "四式谱应两两不同"
    print("  四式与通行谱逐一相同,且两两互不相同——对+粘+韵句限定是完备的"
          "推导规则:首句一起,八句的平仄骨架唯一确定")

    # 断言 1b:一三不论近似下,每式自由位=16,可行变体数=2^16=65536
    print("\n  「一三不论、二四分明」近似:第 2/4 字与句脚锁定,第 1/3 字自由")
    key0 = ("仄起", "不入韵")
    per_line = [len(feasible_line_patterns(t)) for t in schemas[key0]]
    print(f"    逐句枚举 2^5=32 种平仄,各句可行数 = {per_line}(每句 2 个自由位)")
    assert all(n == 4 for n in per_line), "每句可行数应为 2^2=4"
    # 联级全枚举验证:一联 10 个字位,2^10=1024 种组合中可行者应为 4x4=16
    for ci in range(4):
        t_a, t_b = schemas[key0][2 * ci], schemas[key0][2 * ci + 1]
        feas_a = feasible_line_patterns(t_a)
        feas_b = feasible_line_patterns(t_b)
        count = sum(1 for bits in range(1024)
                    if tuple((bits >> (9 - k)) & 1 for k in range(5)) in feas_a
                    and tuple((bits >> (4 - k)) & 1 for k in range(5)) in feas_b)
        assert count == 16, f"联 {ci + 1} 全枚举可行数应为 16,实测 {count}"
    n_free_bits = 8 * 2
    for key, lines in schemas.items():
        free = 1
        for t in lines:
            free *= len(feasible_line_patterns(t))
        assert free == 2 ** n_free_bits == 65536, f"{key} 变体数应为 2^16"
    print("    联级全枚举(2^10=1024)验证:每联可行 = 16;整式变体数 = 4^8")
    print(f"    = 2^16 = {2 ** 16} = 每式自由位(8 句 x 2 位)的 2 次幂——")
    print("    变体数=2^自由位数,枚举与计数一致")

    # 断言 1c:叠「避孤平/避三平调」细律后,可行空间收缩
    strict_per_type = {t: len(feasible_line_patterns(t, strict=True))
                       for t in (TYPE_A, TYPE_B, TYPE_C, TYPE_D)}
    print("\n  叠加细律(避孤平:禁仄平仄仄平;避三平调:禁句脚三连平):")
    for t in (TYPE_A, TYPE_B, TYPE_C, TYPE_D):
        print(f"    {TYPE_NAME[t]}: {len(feasible_line_patterns(t))} -> "
              f"{strict_per_type[t]} 种")
    assert (strict_per_type[TYPE_A], strict_per_type[TYPE_B],
            strict_per_type[TYPE_C], strict_per_type[TYPE_D]) == (4, 3, 4, 2)
    loose_total = strict_total = 0
    for key, lines in schemas.items():
        loose_total_line = 1
        strict_total_line = 1
        for t in lines:
            loose_total_line *= len(feasible_line_patterns(t))
            strict_total_line *= strict_per_type[t]
        assert loose_total_line == 65536
        loose_total += loose_total_line
        strict_total += strict_total_line
        print(f"    {key[0]}首句{key[1]}: {loose_total_line} -> {strict_total_line}")
    print(f"    四式合计: {loose_total}(=2^18) -> {strict_total}")
    assert loose_total == 262144 and strict_total == 29952
    print("  读数:")
    print("  · 格律是约束编程:对+粘+韵句限定把八句骨架定死,「一三不论」")
    print("    只买到 2^16 个变体;避孤平/避三平调两条禁手再砍掉 88.6%——")
    print("    律诗的「自由」是有精确额度的自由")
    print("  · 推导无搜索:给定首句起式,全篇平仄是三条规则的确定输出——")
    print("    近体诗的形式系统在「可判定」这一层与程序语言同构")

    print(f"\n✓ 律一断言通过:四式推导=通行谱且互不相同;每式变体 2^16=65536")
    print(f"  (逐句/联级双枚举验证);细律后四式合计收缩至 29952")


# ==================== 律二:对仗的平行匹配 ====================
# 出句按词性序列模板生成(五言工对模板:数量+禽鸟+动词+颜色+景物,
# 参照「两个黄鹂鸣翠柳,一行白鹭上青天」的词性骨架);对句逐位从同词性
# 桶中取词。桶大小故意不齐,以暴露瓶颈位。

POS_TEMPLATE = ["数量", "禽鸟", "动词", "颜色", "景物"]

BUCKETS = {
    "数量": ["一", "两", "三", "几", "半", "数", "千", "万", "孤", "双"],
    "禽鸟": ["黄鹂", "白鹭", "青鸟", "流莺", "孤鸿", "归雁", "沙鸥", "燕子",
             "鹧鸪", "寒蝉", "塞雁", "乳燕"],
    "动词": ["鸣", "上", "过", "度", "点", "翻", "宿", "辞", "带", "衔", "掠", "没"],
    "颜色": ["翠", "青", "白", "苍", "朱", "碧", "丹", "黄"],
    "景物": ["柳", "天", "波", "枫", "渚", "汀", "林", "山", "水", "月", "云",
             "雪", "江", "树"],
}


def act2():
    print("\n" + "=" * 84)
    print("律二 对仗的平行匹配(词性分桶取词;模板=数量+禽鸟+动词+颜色+景物)")
    print("=" * 84)
    rng = random.Random(75024)

    # 出句:固定种子从各桶抽词(如抽得「数声孤雁掠苍波」式骨架)
    out_line = [rng.choice(BUCKETS[pos]) for pos in POS_TEMPLATE]
    out_index = [BUCKETS[pos].index(w) for pos, w in zip(POS_TEMPLATE, out_line)]
    print("  出句(模板生成): " + "".join(out_line)
          + "  「" + "+".join(POS_TEMPLATE) + "」")

    sizes = [len(BUCKETS[p]) for p in POS_TEMPLATE]
    prod = 1
    for s in sizes:
        prod *= s
    print(f"\n  各位桶宽 = {sizes}(积 = {prod})")

    # 断言 2a:平行约束下合格对句数=各位置桶大小之积(全枚举验证)
    count = 0
    for a in BUCKETS[POS_TEMPLATE[0]]:
        for b in BUCKETS[POS_TEMPLATE[1]]:
            for c in BUCKETS[POS_TEMPLATE[2]]:
                for d in BUCKETS[POS_TEMPLATE[3]]:
                    for e in BUCKETS[POS_TEMPLATE[4]]:
                        count += 1
    assert count == prod, f"全枚举计数 {count} 应等于桶宽之积 {prod}"
    print(f"  (1) 全枚举合格对句 = {count} = ∏桶宽 {sizes} ——平行约束就是"
          "独立选择的乘积")

    # 叠「避同位重字」层:对句同位不得复用出句之字 -> ∏(桶宽-1),同样全枚举
    prod2 = 1
    for s in sizes:
        prod2 *= (s - 1)
    count2 = 0
    for ia, a in enumerate(BUCKETS[POS_TEMPLATE[0]]):
        if ia == out_index[0]:
            continue
        for ib, b in enumerate(BUCKETS[POS_TEMPLATE[1]]):
            if ib == out_index[1]:
                continue
            for ic, c in enumerate(BUCKETS[POS_TEMPLATE[2]]):
                if ic == out_index[2]:
                    continue
                for idd, d in enumerate(BUCKETS[POS_TEMPLATE[3]]):
                    if idd == out_index[3]:
                        continue
                    for ie, e in enumerate(BUCKETS[POS_TEMPLATE[4]]):
                        if ie == out_index[4]:
                            continue
                        count2 += 1
    assert count2 == prod2, f"避重字层全枚举 {count2} 应等于 ∏(桶-1) {prod2}"
    print(f"  (2) 叠避同位重字层: {count} -> {count2} = ∏(桶宽-1)"
          "——约束层叠,空间再缩")

    # 断言 2b:最窄的桶是瓶颈(对桶 +1 词的增益 = 总数/桶宽,窄桶增益最大)
    gains = []
    for i, s in enumerate(sizes):
        gains.append(prod // s)  # 桶 i 增 1 词,总数增 prod/s
    neck = gains.index(max(gains))
    narrow = sizes.index(min(sizes))
    print(f"\n  (3) 各位 +1 词的增益 = {[f'{POS_TEMPLATE[i]}:{g}' for i, g in enumerate(gains)]}")
    assert neck == narrow, "最大增益位应等于最窄桶位"
    print(f"  -> 瓶颈位 = 第 {neck + 1} 位「{POS_TEMPLATE[neck]}」桶(仅 "
          f"{sizes[neck]} 词):给它 +1 词,合格对句 +{gains[neck]} 首,")
    print("     全场最大——对仗的产能由最贫词性的桶决定(颜色/数量小类词最少,")
    print("     这正是「工对难得」:颔联颈联的好坏,卡在最窄的那一列词上)")
    print("  读数:")
    print("  · 律二只管词性平行(语义层);真实对仗还要叠律一的平仄(出句仄收/")
    print("    对句平收)——两律正交,可独立验证再复合")
    print("  · 词库桶宽=语言里该小类的「库存」:工对模板把每个位置锁死小类,")
    print("    库存最薄的词性就是诗人最难落笔的那一格")

    print(f"\n✓ 律二断言通过:平行约束合格数=∏桶宽={prod}(全枚举);避重字层"
          f"={count2};瓶颈位=最窄桶「{POS_TEMPLATE[neck]}」")


# ==================== 律三:「一代有一代之文学」的错峰 ====================
# 诗/词/曲/小说各按双 logistic 生命周期:强度 = 上升 logistic x 下降 logistic。
# 参数为风格化标定(断代节点取通说),不拟合具体文献计数。

T0, T1, DT = 500, 1950, 1  # 时间轴:公元 500-1950,逐年

GENRES = ["诗", "词", "曲", "小说"]
LIFECYCLE = {
    "诗":   (600, 0.018, 820, 0.002),
    "词":   (980, 0.012, 1300, 0.005),
    "曲":   (1235, 0.015, 1420, 0.008),
    "小说": (1480, 0.010, 1950, 0.006),
}


def intensity(g, t):
    tu, ku, td, kd = LIFECYCLE[g]
    return sigma(ku * (t - tu)) * sigma(kd * (td - t))


def half_window(g, level=0.55):
    # 归一化强度 >= level 的活跃窗(各自除以自己的峰值)
    peak = max(intensity(g, t) for t in range(T0, T1 + 1, DT))
    thr = level * peak
    ts = [t for t in range(T0, T1 + 1, DT) if intensity(g, t) >= thr]
    return ts[0], ts[-1], peak


def act3():
    print("\n" + "=" * 84)
    print("律三 「一代有一代之文学」的错峰(诗/词/曲/小说的双 logistic 生命周期)")
    print("=" * 84)

    years = list(range(T0, T1 + 1, DT))
    peaks = {}
    for g in GENRES:
        tp = max(years, key=lambda t: intensity(g, t))
        peaks[g] = tp
    print("  四体裁生命周期峰值年(数值 argmax):")
    for g in GENRES:
        w0, w1, pk = half_window(g)
        print(f"    {g:<3} 峰值 ≈ {peaks[g]}  活跃半窗 ≈ [{w0}, {w1}]")

    # 断言 3a:相邻体裁峰值间隔显著大于 0;重叠期非空且容纳跨界文人
    print("\n  (1) 相邻体裁峰值间隔:")
    gaps = []
    for g, h in zip(GENRES, GENRES[1:]):
        gaps.append(peaks[h] - peaks[g])
        print(f"    {g} -> {h}: 间隔 {peaks[h] - peaks[g]} 年")
    assert all(gp >= 150 for gp in gaps), f"相邻峰值间隔应显著为正,实测 {gaps}"
    overlaps = {}
    for g, h in zip(GENRES, GENRES[1:]):
        wa, wb = half_window(g), half_window(h)
        lo, hi = max(wa[0], wb[0]), min(wa[1], wb[1])
        overlaps[(g, h)] = (lo, hi)
        assert lo <= hi, f"{g}/{h} 活跃重叠期应为非空"
        print(f"    {g}∩{h} 重叠期 = [{lo}, {hi}],长 {hi - lo} 年")
    for (g, h) in overlaps:
        assert overlaps[(g, h)][1] - overlaps[(g, h)][0] >= 60
    su, bai = 1080, 1280  # 苏轼(诗+词)/白朴(词+曲,通说双栖)
    oa, ob = overlaps[("诗", "词")], overlaps[("词", "曲")]
    assert oa[0] <= su <= oa[1], f"苏轼活跃年 {su} 应落在诗词重叠期 {oa}"
    assert ob[0] <= bai <= ob[1], f"白朴活跃年 {bai} 应落在词曲重叠期 {ob}"
    print(f"    跨界文人在重叠期内:苏轼(诗+词,{su} 年)∈ 诗词重叠期;"
          f"白朴(词+曲,{bai} 年)∈ 词曲重叠期")
    print("    (元好问 1235 年亦在诗词重叠期;罗贯中曲/小说双栖为传说材料,")
    print("     只作文字提及,不设断言)")

    # 断言 3b:主导体裁序列与生命周期峰序对齐
    dom = [max(GENRES, key=lambda g: intensity(g, t)) for t in years]
    seq, switches = [dom[0]], []
    for t, g in zip(years, dom):
        if g != seq[-1]:
            switches.append((t, seq[-1], g))
            seq.append(g)
    print("\n  (2) 主导体裁(逐年 argmax)序列:", " -> ".join(seq))
    assert seq == GENRES, f"主导序列应为 {GENRES},实测 {seq}"
    for t, a, b in switches:
        assert peaks[a] < t < peaks[b], \
            f"{a}->{b} 的开关 {t} 应落在两峰({peaks[a]},{peaks[b]})之间"
    print("  换代开关:", ", ".join(f"{a}->{b}@{t}" for t, a, b in switches))
    print("  每次开关都落在相邻两峰之间;各体裁峰值落在自己的主导期内")
    for i, g in enumerate(GENRES):
        lo = T0 if i == 0 else switches[i - 1][0]
        hi = T1 if i == len(GENRES) - 1 else switches[i][0]
        assert lo <= peaks[g] <= hi, f"{g} 的峰值 {peaks[g]} 应落在其主导期 [{lo},{hi}]"

    # 断代代表年与「唐之诗、宋之词、元之曲、明清之小说」对应
    reps = [(750, "盛唐", "诗"), (1080, "北宋", "词"), (1200, "南宋", "词"),
            (1320, "元", "曲"), (1580, "明", "小说"), (1750, "清", "小说")]
    for t, era, want in reps:
        got = max(GENRES, key=lambda g: intensity(g, t))
        assert got == want, f"{era}({t}) 主导体裁应为 {want},实测 {got}"
    print("  断代代表年逐一命中:盛唐 750=诗/北宋 1080=词/南宋 1200=词/")
    print("  元 1320=曲/明 1580=小说/清 1750=小说——与王国维「凡一代有一代")
    print("  之文学:楚之骚,汉之赋,六代之骈语,唐之诗,宋之词,元之曲」的")
    print("  序列口径一致")
    print("  读数:")
    print("  · 峰值错开 200-400 年:文体换代不是王朝开关(唐亡于 907,诗的")
    print("    峰值在盛唐;宋亡于 1279,词的峰值在两宋之交)——文体周期与")
    print("    王朝周期错峰运行,「一代之文学」的「一代」是文体生命周期,")
    print("    不是朝代年表")
    print("  · 重叠期恒非空且有人跨双体裁:苏轼以诗为词、白朴词曲双栖——")
    print("    换代靠跨界的活人完成,不靠旧体裁一夜死亡")
    print("  · 风格化声明:四曲线是标定参数的示意模型(宋诗的强势被简化),")
    print("    断言只锚「错峰+重叠+序列对齐」三条结构性质,不锚幅度")

    print(f"\n✓ 律三断言通过:峰值 {peaks} 错峰(间隔 {gaps});重叠期非空且含")
    print(f"  跨界文人;主导序列 [诗->词->曲->小说] 与峰序对齐,开关均落两峰之间")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  1. 格律=约束编程:对+粘+韵句限定从首句确定推出四式谱(=通行四式")
    print("     且互不相同);一三不论下每式 2^16 变体(双枚举验证),叠避孤平/")
    print("     避三平调后四式合计 262144->29952——自由有精确额度")
    print("  2. 对仗=平行组合:合格对句数=∏桶宽(161280,全枚举),避重字层")
    print("     =∏(桶-1);最窄桶(颜色)是瓶颈,工对难得的组合学本体")
    print("  3. 兴替=错峰更替:四体裁峰值错开 200-400 年,重叠期非空且含跨界")
    print("     文人;主导序列[诗->词->曲->小说]与峰序对齐——文体周期与王朝")
    print("     周期不同步,「一代有一代之文学」是文体生命周期命题")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
