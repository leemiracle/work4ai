#!/usr/bin/env python3
"""
Update 5 analysis files with EPUB/MOBI content.
1. Append concept frequency table to cross-book-analysis.md + update header
2. Append EPUB supplement to theme-central-local-relations.md
3. Append EPUB supplement to theme-economic-system.md
4. Create theme-legitimacy-and-regime.md
5. Append EPUB supplement to theme-society-and-labor.md
"""

import os

ANALYSIS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(ANALYSIS_DIR, "scripts")

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def append_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)

# ============================================================
# 1. Update cross-book-analysis.md
# ============================================================
print("=" * 60)
print("1. Updating political-books-cross-book-analysis.md")
print("=" * 60)

cross_path = os.path.join(ANALYSIS_DIR, "political-books-cross-book-analysis.md")
cross_content = read_file(cross_path)

# Update header: "19 本书" -> "25 本书（19本PDF + 6本EPUB/MOBI）"
old_header = "> 基于 19 本书（7,012,284字）的全文分析\n> 提取 44 个关键概念在每本书中的出现频率和上下文"
new_header = "> 基于 25 本书（19本PDF + 6本EPUB/MOBI）的全文分析\n> 提取 44 个关键概念在每本书中的出现频率和上下文\n> EPUB/MOBI 补充于 2026-07-13"

if old_header in cross_content:
    cross_content = cross_content.replace(old_header, new_header)
    print("  [OK] Header updated: 19 -> 25 books")
else:
    print("  [WARN] Header pattern not found, trying alternate...")
    # Try simpler replacement
    cross_content = cross_content.replace("基于 19 本书", "基于 25 本书（19本PDF + 6本EPUB/MOBI）")

write_file(cross_path, cross_content)
print("  [OK] Header saved")

# Append the EPUB concept frequency table
epub_table = read_file(os.path.join(SCRIPTS_DIR, "epub_concept_output.md"))
append_file(cross_path, "\n\n" + epub_table)
print("  [OK] EPUB concept frequency table appended")

# ============================================================
# 2. Append to theme-central-local-relations.md
# ============================================================
print("\n" + "=" * 60)
print("2. Updating theme-central-local-relations.md")
print("=" * 60)

central_path = os.path.join(ANALYSIS_DIR, "theme-central-local-relations.md")
central_epub = read_file(os.path.join(SCRIPTS_DIR, "theme_central_local_epub.md"))
append_file(central_path, "\n\n" + central_epub)
print("  [OK] EPUB supplement appended")

# ============================================================
# 3. Append to theme-economic-system.md
# ============================================================
print("\n" + "=" * 60)
print("3. Updating theme-economic-system.md")
print("=" * 60)

econ_path = os.path.join(ANALYSIS_DIR, "theme-economic-system.md")
econ_epub = read_file(os.path.join(SCRIPTS_DIR, "theme_economic_system_epub.md"))
append_file(econ_path, "\n\n" + econ_epub)
print("  [OK] EPUB supplement appended")

# ============================================================
# 4. Create theme-legitimacy-and-regime.md
# ============================================================
print("\n" + "=" * 60)
print("4. Creating theme-legitimacy-and-regime.md")
print("=" * 60)

legit_path = os.path.join(ANALYSIS_DIR, "theme-legitimacy-and-regime.md")
legit_epub = read_file(os.path.join(SCRIPTS_DIR, "theme_legitimacy_regime_epub.md"))

legit_header = """# 主题分析：合法性与政体

> 本主题分析聚焦"合法性"(legitimacy)概念在政治学文献中的多重维度，
> 以及不同政体(regime)类型如何建构和维持统治正当性。
>
> **数据源**：
> - 19本PDF书籍的概念分析（见 `political-books-cross-book-analysis.md`）
> - 6本EPUB/MOBI书籍的全文提取（下方EPUB补充部分）
>
> **核心问题**：
> 1. 什么是"合法性"？韦伯的三种类型（传统型/魅力型/法理型）如何映射到中国语境？
> 2. "绩效合法性"与"程序合法性"的张力如何塑造当代中国治理？
> 3. 毛泽东的"人民民主专政"、邓小平的"四项基本原则"如何定义政体属性？
> 4. 黄仁宇的"数目字管理"如何从技术层面解释传统帝国治理能力的局限？
> 5. 赫拉利的"想象的秩序/虚构故事"如何从人类学视角解释合法性的根基？
>
> **文件创建日期**：2026-07-13

---

## PDF书籍中的合法性概念分布

> 以下为19本PDF书籍中与"合法性"直接相关的概念频率（来自 `political-books-cross-book-analysis.md`）：
>
> | 概念 | 出现在几本书 | 总出现次数 |
> |------|------------|-----------|
> | 合法性 | 7本 | 100次 |
> | 绩效合法性 | 7本 | 334次 |
> | 权威 | 13本 | 666次 |
> | 主权 | 11本 | 390次 |
> | 党国 | 10本 | 147次 |
>
> 详细上下文摘录见 `political-books-cross-book-analysis.md` 对应章节。

---

## EPUB/MOBI补充数据

### 概念频率（6本EPUB/MOBI）

| 概念 | 万历十五年 | 毛泽东文集 | 邓小平文选 | 置身事内 | 人类简史 | 社会学经典 | 新增合计 |
|------|-----------|-----------|-----------|---------|---------|-----------|---------|
| 权威 | 25 | 4 | 30 | 10 | 7 | 578 | 654 |
| 主权 | 1 | 82 | 110 | 5 | 3 | 243 | 444 |
| 合法性 | 1 | - | 6 | - | 4 | 195 | 206 |
| 民族主义 | - | 35 | 12 | - | 18 | 7 | 72 |
| 党国 | - | 9 | - | - | - | 7 | 16 |
| 绩效合法性 | - | - | - | - | - | - | 0 |

> **关键发现**：「绩效合法性」在EPUB/MOBI中出现0次——这是周雪光、周黎安等学者的学术构造概念，
> 在经典文本中不直接出现。但合法性（206次）和权威（654次）的高频出现，
> 说明合法性问题贯穿从毛泽东到邓小平到当代的整个政治思想谱系。

---

"""

write_file(legit_path, legit_header + legit_epub + "\n\n---\n\n> **本文件为\"世界本质\"探索项目的知识沉淀。**\n> 使用方式：作为 `knowledge-graph/connections.md` 的素材源。")
print(f"  [OK] File created: {legit_path}")

# ============================================================
# 5. Append to theme-society-and-labor.md
# ============================================================
print("\n" + "=" * 60)
print("5. Updating theme-society-and-labor.md")
print("=" * 60)

soc_path = os.path.join(ANALYSIS_DIR, "theme-society-and-labor.md")
soc_epub = read_file(os.path.join(SCRIPTS_DIR, "theme_society_labor_epub.md"))
append_file(soc_path, "\n\n" + soc_epub)
print("  [OK] EPUB supplement appended")

print("\n" + "=" * 60)
print("ALL 5 FILES UPDATED SUCCESSFULLY")
print("=" * 60)
print(f"\nFiles modified:")
print(f"  1. {cross_path}")
print(f"  2. {central_path}")
print(f"  3. {econ_path}")
print(f"  4. {legit_path} (NEW)")
print(f"  5. {soc_path}")
