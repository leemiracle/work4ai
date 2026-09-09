#!/usr/bin/env python3
"""Extract the most important specific passages for each theme."""

import json
import re
from pathlib import Path

BASE = Path("/mnt/c/workspace/essence/data/political-books-extracted")


def load_full_text(filepath):
    with open(filepath, encoding='utf-8') as f:
        d = json.load(f)
    ft = d['full_text']
    if isinstance(ft, list):
        parts = []
        for p in ft:
            if isinstance(p, dict):
                parts.append(p.get('text', ''))
            elif isinstance(p, str):
                parts.append(p)
        return '\n'.join(parts)
    return str(ft)


def extract_passage(text, phrase, context_before=200, context_after=600, occurrence=0):
    """Extract a passage around a specific phrase."""
    start = 0
    for i in range(occurrence + 1):
        idx = text.find(phrase, start)
        if idx == -1:
            return None
        if i == occurrence:
            s = max(0, idx - context_before)
            e = min(len(text), idx + len(phrase) + context_after)
            snippet = text[s:e].replace('\n', ' ').strip()
            return re.sub(r'\s+', ' ', snippet)
        start = idx + len(phrase)
    return None


# Load texts
texts = {}
book_map = {
    "毛泽东文集": "epub_e077fb766e516aebbf6ad28d9cf81a48.json",
    "邓小平文选": "epub_0695ef24be80eecef2179ca7122c88a9.json",
    "置身事内": "epub_fc25bf25f43b22b0ef1ac62c8642850a.json",
    "万历十五年": "epub_05314f688e0d76c44aa385c98f502f93.json",
    "人类简史": "mobi_f124b57a8baef3d0e363c9ee9ebcb01a.json",
    "社会学经典": "epub_677b2a39917dfc890ce34c57eb3b159f.json",
}

for name, fn in book_map.items():
    texts[name] = load_full_text(BASE / fn)
    print(f"Loaded {name}: {len(texts[name]):,} chars")


print("\n" + "=" * 80)
print("TARGETED EXTRACTIONS")
print("=" * 80)

# ─── 央地关系 ────────────────────────────────────────────────────────────

print("\n【央地关系】")

# 毛泽东：论十大关系 - 中央和地方的关系
passage = extract_passage(texts["毛泽东文集"], "中央和地方的关系也是一个矛盾", 50, 800)
if passage:
    print(f"\n✓ 毛泽东·论十大关系（中央和地方的关系）:\n{passage[:500]}...")

# 毛泽东：大权独揽
passage = extract_passage(texts["毛泽东文集"], "大权独揽", 100, 400)
if passage:
    print(f"\n✓ 毛泽东·大权独揽:\n{passage[:400]}")

# 邓小平：权力下放 - 政治体制改革
passage = extract_passage(texts["邓小平文选"], "第二个内容是权力要下放", 200, 400)
if passage:
    print(f"\n✓ 邓小平·权力下放:\n{passage[:500]}")

# 邓小平：调动地方积极性
passage = extract_passage(texts["邓小平文选"], "发挥中央和地方两个积极性", 200, 400)
if passage:
    print(f"\n✓ 邓小平·两个积极性:\n{passage[:400]}")

# 置身事内：分税制改革的完整论述
passage = extract_passage(texts["置身事内"], "1994年分税制改革", 50, 800)
if passage:
    print(f"\n✓ 置身事内·分税制改革:\n{passage[:500]}...")

# 置身事内：土地财政
passage = extract_passage(texts["置身事内"], "所谓", 0, 0)
# Find the land finance definition
for term in ["地方政府为了应对财政压力而发展出的", "地方可以增加预算外收入，其中最重要的就是围绕土地"]:
    passage = extract_passage(texts["置身事内"], term, 200, 400)
    if passage:
        print(f"\n✓ 置身事内·土地财政:\n{passage[:500]}")


# ─── 经济体制 ────────────────────────────────────────────────────────────

print("\n\n【经济体制】")

# 邓小平：社会主义也可以搞市场经济
passage = extract_passage(texts["邓小平文选"], "社会主义也可以搞市场经济", 50, 600)
if passage:
    print(f"\n✓ 邓小平·社会主义也可以搞市场经济:\n{passage[:500]}...")

# 邓小平：市场经济不存在根本矛盾
passage = extract_passage(texts["邓小平文选"], "社会主义和市场经济不存在根本矛盾", 50, 600)
if passage:
    print(f"\n✓ 邓小平·市场与社会主义不矛盾:\n{passage[:500]}...")

# 邓小平：计划和市场都是方法
passage = extract_passage(texts["邓小平文选"], "计划和市场都是", 100, 500)
if passage:
    print(f"\n✓ 邓小平·计划和市场都是方法:\n{passage[:500]}")

# 邓小平：改革是中国的第二次革命
passage = extract_passage(texts["邓小平文选"], "改革是中国的第二次革命", 100, 500)
if passage:
    print(f"\n✓ 邓小平·改革是第二次革命:\n{passage[:400]}")

# 置身事内：城投公司与土地金融
passage = extract_passage(texts["置身事内"], "城投公司", 100, 500)
if passage:
    print(f"\n✓ 置身事内·城投公司:\n{passage[:500]}")

# 置身事内：地方债务
passage = extract_passage(texts["置身事内"], "地方政府债务", 100, 500)
if passage:
    print(f"\n✓ 置身事内·地方债务:\n{passage[:500]}")


# ─── 合法性与政体 ────────────────────────────────────────────────────────

print("\n\n【合法性与政体】")

# 毛泽东：人民民主专政的核心论述
passage = extract_passage(texts["毛泽东文集"], "各级政府都要加上", 300, 400)
if passage:
    print(f"\n✓ 毛泽东·人民民主专政:\n{passage[:500]}")

# 毛泽东：新民主主义论核心
passage = extract_passage(texts["毛泽东文集"], "建立各个革命阶级联合专政的新民主主义", 200, 400)
if passage:
    print(f"\n✓ 毛泽东·新民主主义:\n{passage[:400]}")

# 邓小平：四项基本原则原文
passage = extract_passage(texts["邓小平文选"], "必须坚持社会主义道路", 100, 500)
if passage:
    print(f"\n✓ 邓小平·四项基本原则:\n{passage[:500]}")

# 万历十五年：以道德代替法制
passage = extract_passage(texts["万历十五年"], "以道德代替法律", 100, 600)
if passage:
    print(f"\n✓ 万历十五年·以道德代替法律:\n{passage[:500]}...")

# 万历十五年：文官制度/传统体制失败
passage = extract_passage(texts["万历十五年"], "中国的传统政治", 50, 500)
if passage:
    print(f"\n✓ 万历十五年·传统政治:\n{passage[:500]}")

# 人类简史：虚构故事/想象的秩序
passage = extract_passage(texts["人类简史"], "任何大规模人类合作的根基", 200, 400)
if passage:
    print(f"\n✓ 人类简史·虚构故事:\n{passage[:500]}")

# 人类简史：想象的秩序
passage = extract_passage(texts["人类简史"], "想象建构的秩序", 100, 500)
if passage:
    print(f"\n✓ 人类简史·想象的秩序:\n{passage[:500]}")


# ─── 社会与劳动 ──────────────────────────────────────────────────────────

print("\n\n【社会与劳动】")

# 费孝通：差序格局定义
passage = extract_passage(texts["社会学经典"], "差序格局", 100, 500, 0)
if passage:
    print(f"\n✓ 费孝通·差序格局(1):\n{passage[:500]}")

passage = extract_passage(texts["社会学经典"], "差序格局", 100, 500, 1)
if passage:
    print(f"\n✓ 费孝通·差序格局(2):\n{passage[:500]}")

# 费孝通：乡土中国核心概念
for term in ["熟人社会", "乡土社会", "礼俗社会"]:
    passage = extract_passage(texts["社会学经典"], term, 100, 400)
    if passage:
        print(f"\n✓ 费孝通·{term}:\n{passage[:400]}")
        break

# 毛泽东：阶级分析
passage = extract_passage(texts["毛泽东文集"], "谁是我们的敌人？谁是我们的朋友？", 50, 600)
if passage:
    print(f"\n✓ 毛泽东·阶级分析开篇:\n{passage[:500]}...")

# 毛泽东：中国社会各阶级的分析
passage = extract_passage(texts["毛泽东文集"], "中国社会各阶级的分析", 50, 600)
if passage:
    print(f"\n✓ 毛泽东·中国社会各阶级的分析:\n{passage[:500]}...")

# 毛泽东：群众路线
passage = extract_passage(texts["毛泽东文集"], "从群众中来，到群众中去", 100, 400)
if passage:
    print(f"\n✓ 毛泽东·群众路线:\n{passage[:400]}")

print("\n\nDone!")
