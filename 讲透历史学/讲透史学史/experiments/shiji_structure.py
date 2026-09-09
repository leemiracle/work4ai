# -*- coding: utf-8 -*-
"""讲透史学史 · 实验：编年换算与史书结构统计
对应 04-史学史转代码.md 走廊①②：封闭规则系统的完全机械化 + 结构统计。

跑法: python shiji_structure.py
断言全过输出 ALL ASSERTS PASSED。
"""
import numpy as np

# ──────────────────────────────────────────────
# ① 干支换算器（走廊①：模算术完全机械化）
# 干支 = 10天干 × 12地支 同步循环；公元 4 年 = 甲子年 → (year-4) 定锚
GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"

def ganzhi(year: int) -> str:
    """公元年 → 干支年（60 年一循环）"""
    return GAN[(year - 4) % 10] + ZHI[(year - 4) % 12]

print("═" * 60)
print("① 干支换算器：封闭规则系统 → 完全机械化")
print("═" * 60)

# 历史锚点断言（教科书级年份，全无歧义）
anchors = {
    1911: "辛亥",   # 辛亥革命
    1840: "庚子",   # 鸦片战争（庚子年）
    1898: "戊戌",   # 戊戌变法
    1900: "庚子",   # 庚子国变（八国联军）
    2026: "丙午",   # 当代验证锚
    1984: "甲子",   # 最近一个甲子年（60循环锚）
}
for y, expect in anchors.items():
    got = ganzhi(y)
    flag = "✓" if got == expect else "✗"
    print(f"  {y} → {got}  (期望 {expect}) {flag}")
    assert got == expect, f"干支换算错误: {y} 得 {got} 期望 {expect}"

# 60 年循环的结构断言
cycle = [ganzhi(4 + i) for i in range(60)]
assert len(set(cycle)) == 60, "60 年应有 60 个不同干支"
assert cycle[0] == "甲子" and cycle[59] == "癸亥", "首尾应为甲子/癸亥"
print(f"  循环完整性: 60 年 → {len(set(cycle))} 个不同干支（甲子…癸亥）✓")

# 同余多解性演示（03 章练习1 的代码化）：跨世纪干支需外部锚点
amb = [y for y in range(1740, 1930) if ganzhi(y) == "辛亥"]
print(f"  同余多解性演示: 1740-1929 间的'辛亥年' = {amb}（相隔恰 60）"
      f"→ 无朝代信息则无法定年 ✓")
assert amb == [1791, 1851, 1911], "辛亥年应为 1791/1851/1911（1911−60k）"

# ──────────────────────────────────────────────
# ② 《史记》五体结构核对（走廊②：结构统计的最小现场）
print()
print("═" * 60)
print("② 《史记》五体 = 多表数据库设计")
print("═" * 60)
shiji = {"本纪": 12, "表": 10, "书": 8, "世家": 30, "列传": 70}
total = sum(shiji.values())
print(f"  五体: {shiji}")
print(f"  合计: {total} 篇")
assert total == 130, "《史记》应为 130 篇"
assert shiji["本纪"] == 12 and shiji["列传"] == 70
print(f"  ✓ 12 本纪 + 10 表 + 8 书 + 30 世家 + 70 列传 = 130（核对通过）")

# 现代语义对照：五体即五种"表"
roles = {
    "本纪": "帝王时间轴（主键=在位年）",
    "表": "大事年表/谱系（时间网格）",
    "书": "制度专史（主题维）",
    "世家": "诸侯/勋贵（分封结构）",
    "列传": "人物传记（个体维）",
}
for k, v in roles.items():
    print(f"    {k}: {v}")
share = {k: v / total for k, v in shiji.items()}
print(f"  人物维占比（列传+世家）/全部 = "
      f"{(shiji['列传']+shiji['世家'])/total:.1%} —— 司马迁的数据库以人为中心")

# ──────────────────────────────────────────────
# ③ 二十四史体例延续（结构统计：纪传体的两千年稳定性）
print()
print("═" * 60)
print("③ 二十四史抽样：纪传体作为持久模式")
print("═" * 60)
# 硬编码抽样数据（篇数为通行统计；断言体例而非精确数字）
histories = [
    ("史记", 130, 12, 70), ("汉书", 100, 12, 70), ("后汉书", 120, 10, 80),
    ("三国志", 65, 4, 60), ("新唐书", 225, 10, 150), ("宋史", 496, 47, 255),
    ("明史", 332, 24, 220),
]
names, totals, benjis, liezhuans = zip(*histories)
arr = np.array(totals)
for n, t, b, l in histories:
    print(f"  {n}: {t} 卷（本纪 {b} / 列传 {l}）")
assert all(b >= 4 for b in benjis), "每部正史都有本纪"
assert all(l >= 60 for l in liezhuans), "列传为主体"
assert arr.max() == 496 and names[arr.argmax()] == "宋史", "宋史最巨"
assert arr.min() == 65 and names[arr.argmin()] == "三国志", "三国志最简"
# 列传占比的历时演化：人物维始终为主轴
lz_share = [l / t for (_, t, _, l) in histories]
print(f"  列传占比: {['%.0f%%' % (s*100) for s in lz_share]}")
assert all(s > 0.5 for s in lz_share), "列传在所有样本中应过半"
print(f"  ✓ 列传在所有样本中均过半——纪传体以人物为主轴两千年不变")

print()
print("ALL ASSERTS PASSED —— 走廊①的封闭规则可完全机械化；"
      "走廊②把史书体例变成可统计结构。")
print("带走一句（04 章）：体例即理论——《史记》的五体是两千年前"
      "的一次数据库 schema 设计。")
