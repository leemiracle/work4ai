# -*- coding: utf-8 -*-
"""
世界史大事年表数据断言（走廊1：年表断言 + 走廊2：共存区间查询）
对应章：讲透世界通史/04-世界通史转代码.md

数据口径：2026-09 模型知识核对，取学界共识中值；约年以"约"标注，
断言只写稳健到敢写死在代码里的事实。如与权威年表不符，以权威为准。
"""
HOMO_SAPIENS = -300000   # 智人出现（约，Jebel Irhout 等化石证据 ~30 万年前）

# 农业独立起源中心（中心, 驯化开始约年, 作物）——公元前为负
AGRI_CENTERS = [
    ("新月沃地",     -9500, "小麦/大麦"),
    ("新几内亚高地", -7000, "芋/香蕉（园艺）"),
    ("长江流域",     -6500, "稻"),
    ("中美洲",       -6500, "玉米（早期驯化）"),
    ("黄河流域",     -6000, "粟/黍"),
    ("安第斯",       -5000, "马铃薯/藜麦"),
    ("萨赫勒",       -2500, "高粱"),
]

# 成熟文字系统（独立起源，保守口径）
SCRIPTS = [
    ("楔形文字", -3200, "两河"),
    ("圣书字",   -3100, "埃及"),
    ("甲骨文",   -1250, "中国（成熟期）"),
    ("早期中美洲文字", -600, "萨波特克/奥尔梅克系"),
    ("玛雅文字", -300,  "玛雅"),
]

# 政治体区间表（名称, 起, 止）——用于共存查询
EMPIRES = [
    ("孔雀", -322, -185), ("汉", -202, 220), ("安息（帕提亚）", -247, 224),
    ("罗马", -27, 476), ("贵霜", 30, 375), ("法兰西（卡佩-瓦卢瓦）", 987, 1328),
    ("神圣罗马", 962, 1806), ("南宋", 1127, 1279), ("蒙古", 1206, 1368),
    ("马穆鲁克", 1250, 1517), ("奥斯曼", 1299, 1922), ("明", 1368, 1644),
]

# 哥伦布交换：美洲作物进入旧大陆的约年
EXCHANGE = [
    ("玉米入欧", 1494), ("花生入华", 1535), ("玉米入华", 1550),
    ("烟草入欧", 1558), ("马铃薯入欧", 1570), ("辣椒入华", 1591),
    ("番薯入华", 1593),
]

def count_at(year, rows):
    """走廊2：区间计数——某年并存的政权数"""
    return sum(1 for _, s, e in rows if s <= year <= e)

def main():
    # 断言1：时间尺度的悬殊——"原始社会占人类史九成以上"的算术版
    first_agri = min(y for _, y, _ in AGRI_CENTERS)          # 最早农业（最负=最早）
    first_script = max(y for _, y, _ in SCRIPTS)             # 此行占位不用，见下
    first_script = min(y for _, y, _ in SCRIPTS)             # 最早文字
    pre_agri = first_agri - HOMO_SAPIENS                     # 智人→农业
    agri_to_script = first_script - first_agri               # 农业→文字
    assert pre_agri > 40 * agri_to_script, (pre_agri, agri_to_script)
    print(f"[1] 智人→最早已知农业 {pre_agri} 年，最早农业→最早文字 {agri_to_script} 年"
          f"（{pre_agri // agri_to_script} 倍）——人类史的 98% 在农业之前")

    # 断言2：文字独立起源≥4 处；最早两处相距不到 300 年
    assert len(SCRIPTS) >= 4
    earliest_two = sorted(y for _, y, _ in SCRIPTS)[:2]
    assert earliest_two[1] - earliest_two[0] < 300, earliest_two
    print(f"[2] 成熟文字独立起源 {len(SCRIPTS)} 处；两河(-3200)与埃及(-3100)仅隔 "
          f"{earliest_two[1]-earliest_two[0]} 年——'传播还是独立'的第一现场")

    # 断言3：多中心世界——公元100年四帝国并存，1250年五强并存
    at_100 = count_at(100, EMPIRES)
    at_1250 = count_at(1250, EMPIRES)
    assert at_100 >= 4, at_100
    assert at_1250 >= 5, at_1250
    names_100 = [n for n, s, e in EMPIRES if s <= 100 <= e]
    names_1250 = [n for n, s, e in EMPIRES if s <= 1250 <= e]
    print(f"[3] 公元100年并存 {at_100} 帝国：{'、'.join(names_100)}")
    print(f"    公元1250年并存 {at_1250} 强：{'、'.join(names_1250)}")

    # 断言4：农业起源全部早于前2500（距今4500+）；其中≥4个中心早于前6000
    assert max(y for _, y, _ in AGRI_CENTERS) <= -2500
    assert sum(1 for _, y, _ in AGRI_CENTERS if y <= -6000) >= 4
    print(f"[4] {len(AGRI_CENTERS)} 个农业中心全部早于距今4500年，"
          f"其中 {sum(1 for _, y, _ in AGRI_CENTERS if y <= -6000)} 个早于距今8000年")

    # 断言5：哥伦布交换的窗口性——7种作物全部落在1492-1620
    assert len(EXCHANGE) >= 6
    assert all(1492 < y < 1620 for _, y in EXCHANGE), EXCHANGE
    span = max(y for _, y in EXCHANGE) - min(y for _, y in EXCHANGE)
    print(f"[5] {len(EXCHANGE)} 项美洲作物入旧大陆记录全部在 1492-1620 窗口，"
          f"跨度仅 {span} 年——'全球网络闭合'的数据指纹")

    print("\n全部断言通过 ✓ （年表断言+区间查询=世界通史的可计算骨架）")

if __name__ == "__main__":
    main()
