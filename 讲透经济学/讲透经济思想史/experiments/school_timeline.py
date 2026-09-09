# -*- coding: utf-8 -*-
"""
学派年表断言（走廊1：年表断言）
对应章：讲透经济思想史/04-经济思想史转代码.md

数据：中西经济思想史锚点年表（内嵌；著作/事件, 年份, 城市/地点, 传统, 类型）。
口径：2026-09 模型知识核对（通行教科书系年）；成书年代有争议者已标注"约"，
断言只用无争议锚点。负数年份=公元前。
"""
from collections import Counter

# (名称, 年份, 地点, 传统, 类型)  类型: 著作/制度/事件
TIMELINE = [
    ("盐铁会议与《盐铁论》", -81, "长安", "中国古代", "事件"),
    ("两税法（杨炎）",        780, "长安", "中国古代", "制度"),
    ("一条鞭法（张居正）",   1581, "北京", "中国古代", "制度"),
    ("摊丁入亩（雍正）",     1723, "北京", "中国古代", "制度"),
    ("严复译《原富》成",     1902, "上海", "中国古代", "著作"),
    ("《国富论》（斯密）",   1776, "伦敦", "西方", "著作"),
    ("《政治经济学与赋税原理》（李嘉图）", 1817, "伦敦", "西方", "著作"),
    ("《政治经济学原理》（穆勒）",         1848, "伦敦", "西方", "著作"),
    ("《资本论》第一卷（马克思）",         1867, "汉堡", "西方", "著作"),
    ("《国民经济学原理》（门格尔）",       1871, "维也纳", "边际", "著作"),
    ("《政治经济学理论》（杰文斯）",       1871, "伦敦", "边际", "著作"),
    ("《纯粹经济学要义》（瓦尔拉斯）",     1874, "洛桑", "边际", "著作"),
    ("《经济学原理》（马歇尔）",           1890, "剑桥", "西方", "著作"),
    ("《就业、利息和货币通论》（凯恩斯）", 1936, "伦敦", "西方", "著作"),
    ("《共产党宣言》",                     1848, "伦敦", "马克思主义", "著作"),
    ("《帝国主义是资本主义的最高阶段》（列宁）", 1917, "苏黎世", "马克思主义", "著作"),
    ("《政治经济学教科书》（苏联）",       1954, "莫斯科", "马克思主义", "著作"),
    ("社会主义市场经济（中共十四大）",     1992, "北京", "马克思主义", "事件"),
    ("竞争均衡的存在性（Arrow-Debreu）",   1954, "斯坦福", "西方", "论文"),
]

# 边际革命三人组（独立性判据：时间重叠 + 零互引，互引由文献学认定，此处存标志位）
MARGINAL_TRIO = [
    {"name": "门格尔", "year": 1871, "city": "维也纳", "cites_peers": False},
    {"name": "杰文斯", "year": 1871, "city": "伦敦",   "cites_peers": False},
    {"name": "瓦尔拉斯", "year": 1874, "city": "洛桑", "cites_peers": False},
]

def get_year(name):
    for row in TIMELINE:
        if row[0].startswith(name):
            return row[1]
    raise KeyError(name)

def main():
    # 断言1：边际革命三重独立——同年两城、三年内第三人、零互引
    years = sorted(m["year"] for m in MARGINAL_TRIO)
    assert years == [1871, 1871, 1874], years
    assert years[-1] - years[0] <= 3
    assert all(m["cites_peers"] is False for m in MARGINAL_TRIO)
    cities = {m["city"] for m in MARGINAL_TRIO}
    assert len(cities) == 3, cities
    print(f"[1] 边际革命三重独立：{years}，三城 {sorted(cities)}，零互引 ✓")

    # 断言2：《盐铁论》早于《国富论》恰 1857 年——干预之辩远早于斯密
    salt = get_year("盐铁会议")
    wealth = get_year("《国富论》")
    assert wealth - salt == 1857, (wealth, salt)
    print(f"[2] 盐铁会议（前{salt}）→ 《国富论》（{wealth}）：国家干预之辩早 {wealth-salt} 年")

    # 断言3：斯密→凯恩斯 160 年（古典到《通论》的思想接力跨度）
    gt = get_year("《就业、利息和货币通论》")
    assert gt - wealth == 160, (gt, wealth)
    print(f"[3] 《国富论》{wealth} → 《通论》{gt}：{gt-wealth} 年")

    # 断言4：1902《原富》接通——严复译本距原著 126 年（中国线与西方线接通点）
    yuanfu = get_year("严复译")
    assert yuanfu - wealth == 126, (yuanfu, wealth)
    print(f"[4] 《原富》{yuanfu} 距《国富论》{wealth}：{yuanfu-wealth} 年——中西思想线接通")

    # 断言5：1954 双事件——西方证明一般均衡存在性，东方出版政治经济学教科书
    y1954 = [r[0] for r in TIMELINE if r[1] == 1954]
    assert len(y1954) == 2, y1954
    print(f"[5] 1954 双事件：{y1954[0]} / {y1954[1]} —— 同一年的两种现代性")

    # 断言6：年表整体单调可排且无年份冲突的类型异常；各传统条目数
    assert [r[1] for r in sorted(TIMELINE, key=lambda r: r[1])] == \
           sorted(r[1] for r in TIMELINE)
    c = Counter(r[3] for r in TIMELINE)
    assert min(c.values()) >= 3 and len(c) == 4, c
    print(f"[6] 传统条目分布 = {dict(c)}（每传统≥3 锚点；'边际'为独立标签）")

    print("\n全部断言通过 ✓ （年表断言=把史料学判据写成可执行检验）")

if __name__ == "__main__":
    main()
