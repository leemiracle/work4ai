# -*- coding: utf-8 -*-
"""
朝代起止年表：把"背朝代"升级成"算结构"（对应章：00/03/04）
家族：讲透中国古代史（GB/T 77030）

口径声明（计量史学第一条纪律：口径透明）：
- 年份用整数，公元前用负数（前 221 = -221）。
- 时长 = 止年 - 起年（不+1）；若按含头含尾的通行计数，整体 +1。
  例：秦（-221 至 -206）本表 15 年，与通行"秦朝十五年"一致；
  隋（581-618）本表 37 年，通行含头尾计数为 38 年。
- 秦止年取前 206（刘邦入关、秦亡于汉元年岁首之交），非前 207。
- 清朝起年取 1644（入关纪年），不含后金（1616）与改国号"清"（1636）。
- 元朝起年取 1271（定国号"大元"），不含蒙古汗国（1206）。
- 分裂段为保守粗计：西晋 280-316 的短暂统一计入分裂段，
  故"大一统覆盖率"是下界估计；北宋与辽的对峙未计为分裂（口径见注）。
数据口径：夏商周起年依"夏商周断代工程"方案；如与最新研究不符以学界为准。
"""

# (朝代, 起年, 止年, 统一王朝?)
DYNASTIES = [
    ("夏",   -2070, -1600, False),   # 约年
    ("商",   -1600, -1046, False),   # 约年
    ("周",   -1046,  -256, False),   # 西周+东周
    ("秦",    -221,  -206, True),
    ("西汉",  -202,     8, True),
    ("新",       9,    23, False),
    ("东汉",    25,   220, True),
    ("三国",   220,   280, False),
    ("西晋",   266,   316, True),    # 统一于280，旋即八王之乱
    ("东晋",   317,   420, False),   # 十六国并立
    ("南北朝", 420,   589, False),
    ("隋",     581,   618, True),
    ("唐",     618,   907, True),
    ("五代十国", 907, 960, False),
    ("北宋",   960,  1127, True),    # 与辽对峙，口径注：仍计统一主体
    ("南宋",  1127,  1279, False),   # 宋金对峙
    ("辽",     916,  1125, False),
    ("金",    1115,  1234, False),
    ("元",    1271,  1368, True),
    ("明",    1368,  1644, True),
    ("清",    1644,  1912, True),
]

# 五代（中原五朝）更替
WUDAI = [
    ("后梁", 907, 923), ("后唐", 923, 936), ("后晋", 936, 947),
    ("后汉", 947, 951), ("后周", 951, 960),
]

# 三大分裂段（粗粒度，保守口径）
SPLIT_SEGMENTS = [(220, 589), (907, 960), (1127, 1279)]

dur = lambda d: d[2] - d[1]


def main():
    # 断言1：周朝约 790 年，全表最长（两倍于第二名量级）
    zhou = next(d for d in DYNASTIES if d[0] == "周")
    assert dur(zhou) == 790, dur(zhou)
    ranked = sorted(DYNASTIES, key=dur, reverse=True)
    assert ranked[0][0] == "周"
    print(f"[1] 全表最长 = 周 {dur(zhou)} 年（西周+东周）；"
          f"第二名 {ranked[1][0]} {dur(ranked[1])} 年")

    # 断言2：唐/明/清落在 268-289 —— "三百年周期律"的粗投影
    d = {x[0]: dur(x) for x in DYNASTIES}
    assert d["唐"] == 289 and d["明"] == 276 and d["清"] == 268, d
    assert all(260 <= d[k] <= 290 for k in ("唐", "明", "清"))
    print(f"[2] 唐 {d['唐']} / 明 {d['明']} / 清 {d['清']} 年"
          "—— 三大一体式王朝全部压在 268-289 带内（人口-土地周期的粗投影）")

    # 断言3：秦与隋是"短命统一、制度长命"双子星
    unified = [x for x in DYNASTIES if x[3]]
    assert d["秦"] == 15 and 36 <= d["隋"] <= 38
    two_shortest = sorted(unified, key=dur)[:2]
    assert {x[0] for x in two_shortest} == {"秦", "隋"}, two_shortest
    print(f"[3] 统一王朝中最短两朝 = 秦 {d['秦']} 年、隋 {d['隋']} 年——"
          "但郡县/科举雏形恰由这两朝奠基：王朝会死，制度长存")

    # 断言4：秦统一至清亡 2133 年，大一统覆盖率 ≈73%（保守下界）
    span = 1912 - (-221)
    assert span == 2133, span
    split_years = sum(b - a for a, b in SPLIT_SEGMENTS)
    unified_years = span - split_years
    ratio = unified_years / span
    assert 0.70 < ratio < 0.76 and abs(ratio - 0.731) < 0.005, ratio
    print(f"[4] 前221→1912 共 {span} 年，分裂段 {split_years} 年，"
          f"大一统覆盖 {unified_years} 年 = {ratio:.1%}（下界）")

    # 断言5：五代十国 53 年 5 朝，平均约 10.6 年一朝；后汉仅 4 年
    span_wudai = 960 - 907
    durs = [b - a for _, a, b in WUDAI]
    assert span_wudai == 53 and len(WUDAI) == 5
    # 后梁16 后唐13 后晋11 后汉4 后周9，合计恰为 53
    assert durs == [16, 13, 11, 4, 9], durs
    assert sum(durs) == span_wudai and min(durs) == 4
    print(f"[5] 五代各朝 {dict(zip([w[0] for w in WUDAI], durs))} 年"
          f"—— 53 年 5 朝，平均 {sum(durs)/5:.1f} 年：分裂期的政权半衰期")

    print("\n全部断言通过 ✓ （编年数据化=走廊1：把兴亡叙事变成可复算结构）")


if __name__ == "__main__":
    main()
