#!/usr/bin/env python3
"""E3 · bi-temporal fact invalidation 模拟器（规则模拟，非 LLM 实验）

讲透Graph Ch03 的核心实验。Graphiti 的核心机制：
  事实带 validity window，新事实到来时旧事实被**作废（invalidated）而非删除**。
三种记忆存储对决：

  OverwriteStore  覆盖式（普通 dict）——只知道现在，历史被抹掉
  AppendOnlyStore 追加式（只加不废）——历史都在，但现在自相矛盾
  BiTemporalStore 双时间线（valid_from/valid_to + 溯源）——两个都能答

时间线（用户 Kendra）：
  2024-09  loves(Adidas)          2026-03  loves(Nike)  ← 作废 Adidas
  2025-06  lives_in(Berlin)       2026-07  lives_in(Munich) ← 作废 Berlin
  2025-11  role(IC)               （不变的事实）

查询电池：4 道"现在问" + 4 道"当时问"（as-of）。
输出：E3_result.json + E3_bitemporal.png
"""
import json
import os
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda s: date.fromisoformat(s)

# ---------- 事实流: (ingested, valid_from, subject, predicate, object) ----------
FACTS = [
    ("2024-09-10", "2024-09-10", "Kendra", "loves", "Adidas"),
    ("2025-06-01", "2025-06-01", "Kendra", "lives_in", "Berlin"),
    ("2025-11-20", "2025-11-20", "Kendra", "role", "IC"),
    ("2026-03-05", "2026-03-01", "Kendra", "loves", "Nike"),     # 换鞋
    ("2026-07-18", "2026-07-01", "Kendra", "lives_in", "Munich")  # 搬家
]

# ---------- 三种存储 ----------
class OverwriteStore:
    """普通 KV：后写的覆盖先写的（大多数 naive memory 的行为）。"""
    def __init__(self):
        self.kv = {}
    def add(self, ing, vf, s, p, o):
        self.kv[(s, p)] = (o, ing)          # 覆盖 = 历史蒸发
    def query(self, s, p, as_of=None):
        if (s, p) not in self.kv:
            return None
        o, ing = self.kv[(s, p)]
        if as_of and ing > as_of:            # 只能按"何时得知"硬扛，还常错
            return None
        return [o]

class AppendOnlyStore:
    """只追加不作废：所有历史事实永远可返回。"""
    def __init__(self):
        self.facts = []
    def add(self, ing, vf, s, p, o):
        self.facts.append((ing, vf, s, p, o))
    def query(self, s, p, as_of=None):
        hits = [(ing, vf, o) for ing, vf, ss, pp, o in self.facts
                if ss == s and pp == p and (as_of is None or vf <= as_of)]
        return [o for _, _, o in hits] or None

class BiTemporalStore:
    """双时间线 + 作废不删除（Graphiti 语义的玩具版）。"""
    def __init__(self):
        self.edges = []  # dict: s,p,o,valid_from,valid_to,ingested,invalidated_at
    def add(self, ing, vf, s, p, o):
        # 矛盾检测: 同 (s,p) 且 object 不同 → 旧事实窗口关闭（不删除）
        for e in self.edges:
            if e["s"] == s and e["p"] == p and e["o"] != o and e["valid_to"] is None:
                if vf >= e["valid_from"]:
                    e["valid_to"] = vf
                    e["invalidated_at"] = ing
        self.edges.append({"s": s, "p": p, "o": o, "valid_from": vf,
                           "valid_to": None, "ingested": ing, "invalidated_at": None})
    def query(self, s, p, as_of=None):
        t = as_of or date.max
        return [e["o"] for e in self.edges
                if e["s"] == s and e["p"] == p
                and e["valid_from"] <= t and (e["valid_to"] is None or e["valid_to"] > t)]
    def provenance(self, s, p):
        return [{"o": e["o"], "valid": f"{e['valid_from']}→{e['valid_to'] or '现在'}",
                 "ingested": e["ingested"]} for e in self.edges if e["s"] == s and e["p"] == p]

stores = {"覆盖式": OverwriteStore(), "追加式": AppendOnlyStore(), "bi-temporal": BiTemporalStore()}
for ing, vf, s, p, o in FACTS:
    for st in stores.values():
        st.add(D(ing), D(vf), s, p, o)

# ---------- 查询电池 ----------
NOW_QUERIES = [  # (subject, predicate, 期望答案集合, 题面)
    ("Kendra", "loves", {"Nike"}, "现在喜欢什么品牌？"),
    ("Kendra", "lives_in", {"Munich"}, "现在住哪？"),
    ("Kendra", "role", {"IC"}, "现在什么角色？"),
    ("Kendra", "loves", {"Adidas"}, "『还』喜欢 Adidas 吗？（应为否/空）"),
]
ASOF_QUERIES = [
    ("Kendra", "loves", {"Adidas"}, "2025-01-15", "2025 年 1 月时喜欢什么？"),
    ("Kendra", "lives_in", {"Berlin"}, "2026-01-01", "2026 年元旦住哪？"),
    ("Kendra", "lives_in", {"Munich"}, "2026-08-01", "2026-08 时住哪？"),
    ("Kendra", "role", {"IC"}, "2026-08-01", "2026-08 时角色？"),
]

def judge(ret, gold):
    if ret is None:
        return bool(not gold)  # 查无 + 期望空 = 对
    return set(ret) == gold

report = {name: {"now": [], "asof": []} for name in stores}
for s, p, gold, desc in NOW_QUERIES:
    for name, st in stores.items():
        ret = st.query(s, p)
        if desc.startswith("『还』"):
            ok = ret is None or "Adidas" not in ret  # 不应再返回 Adidas 作为当前事实
        else:
            ok = judge(ret, gold)
        report[name]["now"].append({"q": desc, "ret": ret, "gold": sorted(gold), "ok": bool(ok)})

for s, p, gold, t, desc in ASOF_QUERIES:
    for name, st in stores.items():
        ret = st.query(s, p, as_of=D(t))
        ok = judge(ret, gold)
        report[name]["asof"].append({"q": desc, "as_of": t, "ret": ret,
                                     "gold": sorted(gold), "ok": bool(ok)})

scores = {name: {"now": sum(r["ok"] for r in rep["now"]),
                 "asof": sum(r["ok"] for r in rep["asof"])} for name, (rep) in
          ((n, report[n]) for n in stores)}

print("=" * 76)
print("E3 · bi-temporal fact invalidation 模拟器")
print("=" * 76)
for name in stores:
    sc = scores[name]
    print(f"\n【{name}】 现在问 {sc['now']}/4 · 当时问 {sc['asof']}/4")
    for kind in ("now", "asof"):
        for r in report[name][kind]:
            mark = "✅" if r["ok"] else "❌"
            print(f"   {mark} {r['q']}  返回={r['ret']}  gold={r['gold']}")
bt = stores["bi-temporal"]
print("\n【bi-temporal 溯源演示】loves 的完整时间线（作废不删除）:")
for e in bt.provenance("Kendra", "loves"):
    print(f"   {e['o']:<8} valid {e['valid']}   ingested {e['ingested']}")

total = {name: scores[name]["now"] + scores[name]["asof"] for name in stores}
print("\n" + "-" * 76)
print(f"总分: 覆盖式 {total['覆盖式']}/8 · 追加式 {total['追加式']}/8 · bi-temporal {total['bi-temporal']}/8")
print("覆盖式活在没有历史的世界；追加式活在矛盾的世界；bi-temporal 两个世界都能答。")

# ---------- 图 ----------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.6))

names = list(stores)
x = range(len(names))
w = 0.35
ax1.bar([i - w / 2 for i in x], [scores[n]["now"] for n in names], width=w, label="现在问", color="#2a9d8f")
ax1.bar([i + w / 2 for i in x], [scores[n]["asof"] for n in names], width=w, label="当时问 (as-of)", color="#e9c46a")
ax1.set_xticks(x)
ax1.set_xticklabels(names)
ax1.set_ylim(0, 4.6)
ax1.set_ylabel("答对题数 (满分4)")
ax1.set_title("三种存储 × 两类时间问题")
ax1.legend(fontsize=9)
ax1.grid(axis="y", alpha=0.3)

# 右图: loves 事实的 validity window 时间带
ax2.set_title("validity window（loves）: 作废≠删除")
facts_loves = [e for e in bt.edges if e["p"] == "loves"]
for i, e in enumerate(facts_loves):
    x0 = date.fromisoformat("2024-09-01").toordinal()
    vf = e["valid_from"].toordinal()
    vt = (e["valid_to"] or date(2026, 12, 31)).toordinal()
    ax2.barh(i, vt - vf, left=vf - x0, height=0.45,
             color="#2a9d8f" if e["valid_to"] is None else "#adb5bd")
    ax2.text(vf - x0 + 10, i, f"{e['o']}  ({e['valid_from']}→{e['valid_to'] or '…'})",
             va="center", fontsize=9)
ax2.set_yticks([])
import matplotlib.dates as mdates
ax2.set_xlim(0, (date(2026, 12, 31) - date.fromisoformat("2024-09-01")).days)
ax2.set_xticks([D("2025-01-01").toordinal() - x0, D("2025-07-01").toordinal() - x0,
                D("2026-01-01").toordinal() - x0, D("2026-07-01").toordinal() - x0])
ax2.set_xticklabels(["2025-01", "2025-07", "2026-01", "2026-07"])
ax2.grid(axis="x", alpha=0.3)

fig.suptitle("E3 · 双时间线：覆盖失史、追加生伪、作废不删除两全", fontsize=12)
fig.tight_layout()
png = os.path.join(HERE, "E3_bitemporal.png")
fig.savefig(png, dpi=130)

result = {
    "experiment": "E3 bi-temporal fact invalidation simulator",
    "type": "规则模拟（非 LLM 实验）",
    "facts": FACTS,
    "scores": {k: {kk: int(vv) for kk, vv in v.items()} for k, v in scores.items()},
    "detail": report,
    "provenance_loves": bt.provenance("Kendra", "loves"),
    "png": os.path.basename(png),
}
with open(os.path.join(HERE, "E3_result.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)
print("\n落盘: E3_result.json + E3_bitemporal.png")
