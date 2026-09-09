# -*- coding: utf-8 -*-
"""讲透史学理论 · 实验：叙事句时间装置的可执行化
对应 04-史学理论转代码.md 走廊①：Danto 叙事句 → 事件表+谓词解锁表 → 各时刻可断言集。

三条推论验证（03 章）：
  R1 知识前沿单调性：可断言集随 t 单调不减
  R2 叙事滞后必然性："开端/结束/最危险"类意义谓词解锁必然滞后于事件
  R3 每代重写权：t 增加解锁新谓词（新句子出现）——重写是内建功能

跑法: python narrative_danto.py
"""
# ── 事件表（事件时间）─────────────────────────────
EVENTS = {
    "二战结束": 1945, "马歇尔计划": 1948, "柏林墙建立": 1961,
    "古巴导弹危机": 1962, "柏林墙倒塌": 1989, "苏联解体": 1991,
    "北约首轮东扩": 1999, "9·11事件": 2001,
}
# ── 叙事句表：句子 → (事件时间 e, 谓词解锁时间 u) ──
# u 的确定：谓词的意义需要哪些后续事件补完（史学编纂共识的硬编码）
SENTENCES = {
    "1945年二战结束":                       (1945, 1945),
    "1948年马歇尔计划开启了冷战秩序":          (1948, 1961),  # "冷战秩序"需对立结构显形（柏林墙）
    "1961年柏林墙建成冷战欧洲格局定型":        (1961, 1962),  # "定型"需危机检验后回望
    "1962年古巴导弹危机是冷战最危险时刻":      (1962, 1991),  # "最危险"需冷战全程结束才可比
    "1989年柏林墙倒塌成为冷战结束的标志":      (1989, 1991),  # "结束的标志"需苏联解体确认
    "1991年苏联解体结束了冷战":              (1991, 1991),
    "1999年北约东扩是后冷战秩序的第一块基石":   (1999, 2001),  # "后冷战秩序"需 9·11 后语境
    "2001年9·11事件定义了21世纪头十年":      (2001, 2011),  # "头十年"需十年走完
}
LAGS = sorted(((e, u, s) for s, (e, u) in SENTENCES.items()))

def assertable(sentence: str, t: int) -> bool:
    e, u = SENTENCES[sentence]
    return e <= t and u <= t

def sayable_set(t: int):
    return {s for s in SENTENCES if assertable(s, t)}

print("═" * 64)
print("① 叙事滞后清单（R2：意义谓词的解锁滞后）")
print("═" * 64)
lag_pairs = [(s, u - e) for s, (e, u) in SENTENCES.items() if u > e]
for s, lag in sorted(lag_pairs, key=lambda x: -x[1]):
    print(f"  滞后 {lag:>2} 年 | {s}")
n_lag = len(lag_pairs)
print(f"  共 {n_lag}/{len(SENTENCES)} 句存在正滞后")
assert n_lag >= 4, "至少 4 句应存在叙事滞后"
assert ("1962年古巴导弹危机是冷战最危险时刻" in dict(lag_pairs))
assert dict(lag_pairs)["1962年古巴导弹危机是冷战最危险时刻"] == 29

print()
print("═" * 64)
print("② 知识前沿单调性（R1）：可断言集随 t 只增不减")
print("═" * 64)
T = list(range(1945, 2027))
prev = sayable_set(T[0])
mono = True
gains = []
for t in T[1:]:
    cur = sayable_set(t)
    if not prev <= cur:
        mono = False
        break
    if len(cur) > len(prev):
        gains.append((t, len(cur) - len(prev)))
    prev = cur
for t, g in gains:
    print(f"  {t} 年：可断言集 +{g} 句（前沿推进）")
assert mono, "可断言集必须单调不减"
assert len(gains) >= 4, "前沿应至少推进 4 次"
print("  ✓ 单调性全程成立（1945-2026 无一次收缩）")

print()
print("═" * 64)
print("③ 每代重写权（R3）：同一事件，新谓词随 t 解锁")
print("═" * 64)
# 同锚事件的多重书写：柏林墙倒塌（1989）
wall = [s for s in SENTENCES if "柏林墙倒塌" in s]
for t in (1989, 1990, 1995):
    print(f"  t={t}: 对'柏林墙倒塌'可说的句子 = "
          f"{[s for s in wall if assertable(s, t)] or '（无——事件谓词未解锁）'}")
assert not assertable("1989年柏林墙倒塌成为冷战结束的标志", 1990), \
    "1990 年不可能说出'冷战结束的标志'"
assert assertable("1989年柏林墙倒塌成为冷战结束的标志", 1991), \
    "1991 年起该句可说"
print("  ✓ '冷战结束的标志'在 1990 不可说、1991 可说——")
print("    不是史料不足，是叙事句的语法结构（滞后不可压缩）")

print()
print("ALL ASSERTS PASSED —— 叙事句时间装置可执行化：")
print("  事件表+谓词解锁表两张人编表 → 可断言集全自动计算。")
print("带走一句（03/04 章）：史学的'历史性'不在对象在过去，")
print("而在知识结构必然指向叙述者之后——每代重写是时间装置的内建功能。")
