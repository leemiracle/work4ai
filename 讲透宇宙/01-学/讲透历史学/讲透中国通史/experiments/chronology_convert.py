# -*- coding: utf-8 -*-
"""
通史的最小计算现场：干支纪年引擎 + 王朝节律表
对应章：02（活的六十进制）+ 03（事实节律层）+ 04（纪年引擎/王朝数据）

断言：
A. 干支换算：2024=甲辰、1984=甲子、辛亥年=1911（公元→干支）
B. 干支循环自检：任意连续 61 年中天干 10 循环、干支对 60 循环
C. 王朝数据表：秦(前221)至清(1911)跨度合计 + 统一/分裂节律统计
   （统一期总时长 > 分裂期总时长——"分久必合"的节律层数据形态）
"""
GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"

# 王朝节律表：(名称, 起年, 讫年, 统一?)  起讫用代表性年份（政权的通行起讫口径）
DYNASTIES = [
    ("秦",     -221, -207, True),
    ("西汉",   -202,   8,   True),
    ("新",       9,    23,   True),
    ("东汉",    25,   220,   True),
    ("三国",   220,   280,  False),
    ("西晋",   280,   316,   True),
    ("东晋十六国", 317, 420, False),
    ("南北朝", 420,   589,  False),
    ("隋",     589,   618,   True),
    ("唐",     618,   907,   True),
    ("五代十国", 907, 960,  False),
    ("北宋辽", 960, 1127,   False),   # 对峙期
    ("南宋金", 1127, 1279,  False),   # 对峙期
    ("元",    1279,  1368,   True),
    ("明",    1368,  1644,   True),
    ("清",    1644,  1911,   True),
]


def year2ganzhi(y: int) -> str:
    """公元年→干支（公元4年为甲子：汉平帝元始四年，天文历算通行锚点）"""
    g = GAN[(y - 4) % 10]
    z = ZHI[(y - 4) % 12]
    return g + z


def ganzhi2years(gz: str, lo: int, hi: int) -> list:
    """干支→公元年（区间内**全部**解——60 循环歧义是学科事实，返回列表）"""
    g, z = GAN.index(gz[0]), ZHI.index(gz[1])
    return [y for y in range(lo, hi + 1)
            if (y - 4) % 10 == g and (y - 4) % 12 == z]


def main():
    print("═" * 60)
    print("① 干支引擎（公元 ↔ 干支）")
    for y, gz in [(2024, "甲辰"), (2025, "乙巳"), (1984, "甲子"),
                  (2026, "丙午"), (1900, "庚子"), (1911, "辛亥")]:
        got = year2ganzhi(y)
        print(f"   {y:>5d} → {got}   （预期 {gz}）")
        assert got == gz, f"{y} 应为 {gz}，得 {got}"
    print("   [断言A通过] 2024=甲辰、1984=甲子、辛亥年=1911 全部命中")
    sols = ganzhi2years("辛亥", 1850, 1950)
    assert sols == [1851, 1911], f"反查辛亥应得[1851,1911]，得 {sols}"
    print(f"   反查：辛亥 → {sols}（区间内双解！）")
    print("   ——1851 太平天国与 1911 辛亥革命都是辛亥年：60 循环歧义")
    print("     不是 bug，是纪年系统的本体属性（语境消歧=02 章的学科现场）。")

    print("═" * 60)
    print("② 六十甲子循环自检（连续 61 年）")
    seq = [year2ganzhi(y) for y in range(1900, 1961)]
    assert seq[0] == seq[60], "60 年应回到同一干支"
    assert len(set(seq[:60])) == 60, "前 60 年应两两不同"
    gan_cycle = len(set(s[0] for s in seq[:10])) == 10
    assert gan_cycle, "天干应 10 循环"
    print("   [断言B通过] 61 年窗口：干支对 60 循环、天干 10 循环，无碰撞")
    print("   ——10 与 12 的 lcm=60：两个独立循环的相遇周期即纪年周期")

    print("═" * 60)
    print("③ 王朝节律表（秦 前221 → 清 1911）")
    print(f"   {'朝代':<8s}{'起':>6s}{'讫':>6s}{'时长':>6s}  统一?")
    tongnian, fenlian = 0, 0
    for name, a, b, uni in DYNASTIES:
        span = b - a
        (tongnian if uni else fenlian).__class__  # noop line keep simple
        if uni:
            tongnian += span
        else:
            fenlian += span
        print(f"   {name:<8s}{a:>6d}{b:>6d}{span:>5d}年  {'统一' if uni else '分裂/对峙'}")
    total = tongnian + fenlian
    print(f"   ─────────────────────────────────")
    print(f"   统一期合计   {tongnian:>5d} 年 ({tongnian/total:.0%})")
    print(f"   分裂/对峙合计 {fenlian:>4d} 年 ({fenlian/total:.0%})")
    print(f"   两千年总跨度 {total} 年（表覆盖 {sum(b-a for _,a,b,_ in DYNASTIES)} 年）")
    assert tongnian > fenlian, "节律层：统一时长应大于分裂时长"
    n_uni = sum(1 for r in DYNASTIES if r[3])
    n_fen = len(DYNASTIES) - n_uni
    assert n_uni >= n_fen, "统一王朝数不少于分裂段数"
    print(f"   [断言C通过] 统一 {n_uni} 段 vs 分裂 {n_fen} 段——'分久必合'")
    print("   作为**节律层数据形态**成立；但注意 03 章：这是叙事概括，")
    print("   不是力学定律（机制解释层柔性，断言强度天然降一级）。")

    print("═" * 60)
    print("现场注：北宋辽/南宋金按'对峙'计入分裂段（统一判定的连续谱问题")
    print("——羁縻/称臣/南北市场一体化都让'统一'不是布尔值，03/04 章裂缝清单）。")


if __name__ == "__main__":
    main()
    print("\n[ALL ASSERTS PASSED] 干支引擎双向命中 / 60循环自检 / 王朝节律统计成立")
