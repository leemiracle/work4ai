# -*- coding: utf-8 -*-
"""
玛雅长历法 <-> 公历转换器（走廊1：历法转换）
对应章：讲透历史学/讲透美洲史/04-美洲史转代码.md（03 章美之时刻的可跑版）

历法：长历五元组 (baktun.katun.tun.uinal.kin) 连续计日：
  1 kin = 1 天；1 uinal = 20 kin；1 tun = 18 uinal = 360 天；
  1 katun = 20 tun = 7200 天；1 baktun = 20 katun = 144000 天
相关常数：GMT 584283（最主流的长历第 0 天对应儒略日数；
该常数有竞争值，代码里这行整数=几十年的树轮-天文-铭文学论战）。
公历为外推格里高利历，年份用天文编号（0=公元前1年，-3113=公元前3114年）。
数据口径：2026-09 模型知识核对；13.0.0.0.0=2012-12-21 与纪元起点
=前3114-08-11 为学界标准锚点，如与文献不符以文献为准。
"""

CORRELATION = 584283  # GMT 常数：JDN = 长历天数 + 584283

def long_count_to_days(b, k, t, u, x):
    """五元组 -> 距纪元第 0 天的天数"""
    return b * 144000 + k * 7200 + t * 360 + u * 20 + x

def jdn_to_gregorian(jdn):
    """儒略日数 -> 公历（天文年编号，纯整数算法）"""
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return year, month, day

def gregorian_to_jdn(year, month, day):
    """公历 -> 儒略日数（往返自验用）"""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

def long_count_to_gregorian(b, k, t, u, x):
    return jdn_to_gregorian(long_count_to_days(b, k, t, u, x) + CORRELATION)

def main():
    # 断言1：进位单位表（vigesimal 变体：18 uinal 凑 360 天贴近年）
    assert long_count_to_days(0, 0, 1, 0, 0) == 360
    assert long_count_to_days(0, 1, 0, 0, 0) == 7200
    assert long_count_to_days(1, 0, 0, 0, 0) == 144000
    print("[1] 单位表 ✓ 1 tun=360 天, 1 katun=7200 天, 1 baktun=144000 天")

    # 断言2：13.0.0.0.0 = 2012-12-21（'末日谣言'实为第 13 巴图恩翻页）
    y, m, d = long_count_to_gregorian(13, 0, 0, 0, 0)
    assert (y, m, d) == (2012, 12, 21), (y, m, d)
    print(f"[2] 13.0.0.0.0 = {y}-{m:02d}-{d:02d}  —— 第 13 巴图肯翻页日，谣言止于此")

    # 断言3：纪元第 0 天 = 前 3114 年 8 月 11 日（天文年 -3113）
    y, m, d = long_count_to_gregorian(0, 0, 0, 0, 0)
    assert (y, m, d) == (-3113, 8, 11), (y, m, d)
    print(f"[3] 0.0.0.0.0 = 公元前 3114 年 8 月 11 日（天文年 {y}）—— 长历纪元")

    # 断言4：连续性——12.19.19.17.19（uinal 位 0-17，非 0-19）的次日恰是 13.0.0.0.0
    assert (long_count_to_days(12, 19, 19, 17, 19) + 1
            == long_count_to_days(13, 0, 0, 0, 0))
    y, m, d = long_count_to_gregorian(12, 19, 19, 17, 19)
    assert (y, m, d) == (2012, 12, 20), (y, m, d)
    print(f"[4] 12.19.19.17.19 = {y}-{m:02d}-{d:02d}，次日翻页 —— 计数系统自洽")

    # 断言5：往返自验（含负年份）——公历↔JDN 转换器互逆
    for date in [(-3113, 8, 11), (2012, 12, 21), (1969, 7, 20), (1776, 7, 4)]:
        jdn = gregorian_to_jdn(*date)
        assert jdn_to_gregorian(jdn) == date, date
    print("[5] 公历↔儒略日往返自验 ✓（含天文负年份）")

    # 附加展示：古典期起点 9.0.0.0.0 落在 5 世纪（玛雅古典期断代坐标）
    y, m, d = long_count_to_gregorian(9, 0, 0, 0, 0)
    assert 400 <= y <= 470, (y, m, d)
    print(f"[+] 9.0.0.0.0 = {y}-{m:02d}-{d:02d} —— 古典期（约 250-900）中段坐标")

    print("\n全部断言通过 ✓ （历法转换=走廊1：把'无文字'变成可复算）")

if __name__ == "__main__":
    main()
