# -*- coding: utf-8 -*-
"""
大洋洲定居年表 + 去殖民年表（走廊1：测年序列）
对应章：讲透历史学/讲透大洋洲史/04-大洋洲史转代码.md

面板A：人类定居大洋洲的序列（BP=距 1950 年，取学界主流区间中值；
萨胡尔 65 ka=Madjedbebe 2017；NZ 1250-1275=Bunbury 2022 PNAS 贝叶斯碳十四；
东波利尼西亚短年代学=Wilmshurst 2011+Ioannidis 2021 基因网络法）
面板B：大洋洲政治独立年表（含自由联合协定国家）。
数据口径：2026-09 模型知识核对；中值为教学近似，如与文献不符以文献为准。
"""
from collections import Counter

# (区域, BP 中值, kind) kind: continent=大陆级; major=主要陆块; arch=群岛; isle=小岛
SETTLEMENT = [
    ("萨胡尔大陆（澳洲北部）", 65000, "continent"),   # Madjedbebe 2017
    ("新几内亚高地",           46000, "continent"),   # Ivane 山谷 49-43 ka
    ("近大洋洲离岛（俾斯麦-所罗门）", 35000, "arch"),  # New Ireland/Kilu 一线
    ("远大洋洲（拉皮塔前沿：瓦努阿图-斐济）", 3000, "arch"),  # Teouma ~1000 BC
    ("西波利尼西亚（汤加-萨摩亚）",     2800, "arch"),  # 拉皮塔东界
    ("东波利尼西亚（社会群岛）",          950, "arch"),  # 短年代学起点
    ("夏威夷",                              730, "arch"),
    ("拉帕努伊（复活节岛）",                725, "arch"),
    ("新西兰（奥特罗亚）",                  690, "major"),  # 人类最后定居的主要陆块
    ("查塔姆群岛",                          450, "isle"),  # 莫里奥里人
]

# (国家/政体, 独立年, kind) kind: state=主权国家; assoc=自由联合; dominion=自治领/联邦
INDEPENDENCE = [
    ("澳大利亚", 1901, "dominion"), ("新西兰", 1907, "dominion"),
    ("萨摩亚", 1962, "state"), ("瑙鲁", 1968, "state"),
    ("斐济", 1970, "state"), ("巴布亚新几内亚", 1975, "state"),
    ("所罗门群岛", 1978, "state"), ("图瓦卢", 1978, "state"),
    ("基里巴斯", 1979, "state"), ("瓦努阿图", 1980, "state"),
    ("密克罗尼西亚联邦", 1986, "assoc"), ("马绍尔群岛", 1986, "assoc"),
    ("帕劳", 1994, "assoc"),
]

def main():
    # ── 面板A：定居序列 ──
    bps = [bp for _, bp, _ in SETTLEMENT]

    # 断言A1：序列严格由老到新（扩张史的"单调表"）
    assert bps == sorted(bps, reverse=True), bps
    print(f"[A1] 定居序列单调 ✓ {len(SETTLEMENT)} 站：{SETTLEMENT[0][0]} → {SETTLEMENT[-1][0]}")

    # 断言A2：萨胡尔（65000 BP）与拉皮塔前沿（3000 BP）之间隔 ≥6 万年
    gap = 65000 - 3000
    assert gap >= 60000, gap
    print(f"[A2] 萨胡尔 → 远大洋洲隔 {gap//1000} 千年 —— 人类跨过第一条海峡后又等了六万年")

    # 断言A3："长停顿"：西波利尼西亚(2800)→东波利尼西亚(950) ≥1500 年
    pause = 2800 - 950
    assert pause >= 1500, pause
    print(f"[A3] 西波利尼西亚 → 东波利尼西亚'长停顿'约 {pause} 年 —— 史前史最大悬案之一")

    # 断言A4：东波利尼西亚三角在 ≤300 年内铺完（社会群岛→新西兰）
    span = 950 - 690
    assert 0 < span <= 300, span
    print(f"[A4] 东波利尼西亚三角铺完用时约 {span} 年（基因网络法 ~200 年量级）")

    # 断言A5：新西兰=人类最后定居的主要陆块（kind=major 的最后一站，约 AD 1260）
    nz = [s for s in SETTLEMENT if s[2] == "major"][0]
    assert nz[0].startswith("新西兰") and 750 > nz[1] >= 650, nz
    ad = 1950 - nz[1]
    print(f"[A5] {nz[0]} 定居约公元 {ad} 年 —— 人类最后定居的主要陆块（查塔姆等小岛更晚）")

    # ── 面板B：去殖民年表 ──
    # 断言B1：萨摩亚 1962 = 太平洋岛屿去殖民第一站
    islands = [(n, y) for n, y, k in INDEPENDENCE if k == "state"]
    first = min(islands, key=lambda t: t[1])
    assert first == ("萨摩亚", 1962), first
    print(f"[B1] 太平洋岛屿独立第一站：{first[0]} {first[1]}")

    # 断言B2：1970s 是高峰年代（5 国：斐济/巴新/所罗门/图瓦卢/基里巴斯）
    decades = Counter((y // 10) * 10 for _, y, k in INDEPENDENCE if k == "state")
    assert decades[1970] == 5 and decades.most_common(1)[0] == (1970, 5), decades
    print(f"[B2] 主权独立按年代 = {dict(sorted(decades.items()))} → 1970s 高峰（5 国）")

    # 断言B3：帕劳 1994 = 最后一块托管地落地（自由联合收官）
    last = max(INDEPENDENCE, key=lambda r: r[1])
    assert last[0] == "帕劳" and last[1] == 1994, last
    print(f"[B3] 收官：{last[0]} {last[1]} —— 联合国托管体系在太平洋的最后一页")

    print("\n全部断言通过 ✓ （测年序列=走廊1：把六万年航程变成可验证表格）")

if __name__ == "__main__":
    main()
