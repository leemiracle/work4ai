#!/usr/bin/env python3
"""Count concept frequency in 6 EPUB/MOBI books and generate updates for cross-book analysis."""

import json
import re
from pathlib import Path
from collections import OrderedDict

BASE = Path("/mnt/c/workspace/essence/data/political-books-extracted")

# Book mappings
BOOKS = OrderedDict([
    ("万历十五年", {
        "file": "epub_05314f688e0d76c44aa385c98f502f93.json",
        "short": "万历十五年",
        "author": "黄仁宇",
    }),
    ("毛泽东文集", {
        "file": "epub_e077fb766e516aebbf6ad28d9cf81a48.json",
        "short": "毛泽东文集",
        "author": "中共中央文献研究室",
    }),
    ("邓小平文选", {
        "file": "epub_0695ef24be80eecef2179ca7122c88a9.json",
        "short": "邓小平文选(第一卷)",
        "author": "邓小平",
    }),
    ("置身事内", {
        "file": "epub_fc25bf25f43b22b0ef1ac62c8642850a.json",
        "short": "置身事内",
        "author": "兰小欢",
    }),
    ("人类简史", {
        "file": "mobi_f124b57a8baef3d0e363c9ee9ebcb01a.json",
        "short": "人类简史",
        "author": "尤瓦尔·赫拉利",
    }),
    ("中国社会学经典文库", {
        "file": "epub_677b2a39917dfc890ce34c57eb3b159f.json",
        "short": "中国社会学经典文库",
        "author": "费孝通等",
    }),
])

# The 44 concepts from the existing analysis
# Format: (display_name, [search_terms])
CONCEPTS = [
    ("权力", ["权力"]),
    ("开放", ["开放"]),
    ("维稳", ["维稳", "稳定"]),
    ("制度", ["制度"]),
    ("权威", ["权威"]),
    ("改革", ["改革"]),
    ("意识形态", ["意识形态"]),
    ("社会主义", ["社会主义"]),
    ("资本主义", ["资本主义"]),
    ("主权", ["主权"]),
    ("市场经济", ["市场经济"]),
    ("腐败", ["腐败"]),
    ("党国", ["党国"]),
    ("数字治理", ["数字治理", "数字化"]),
    ("全球化", ["全球化"]),
    ("绩效合法性", ["绩效合法性"]),
    ("附近", ["附近"]),
    ("法治", ["法治"]),
    ("人治", ["人治"]),
    ("有效治理", ["有效治理"]),
    ("共谋", ["共谋"]),
    ("民主化", ["民主化"]),
    ("一统体制", ["一统体制"]),
    ("分税制", ["分税制"]),
    ("民族主义", ["民族主义"]),
    ("集体行动", ["集体行动"]),
    ("合法性", ["合法性"]),
    ("晋升锦标赛", ["晋升锦标赛", "锦标赛"]),
    ("国家与社会", ["国家与社会"]),
    ("社会运动", ["社会运动"]),
    ("国家能力", ["国家能力"]),
    ("土地财政", ["土地财政"]),
    ("逆向软预算约束", ["逆向软预算约束", "软预算约束"]),
    ("运动式治理", ["运动式治理", "运动型治理"]),
    ("行政发包", ["行政发包", "逐级发包"]),
    ("官僚制", ["官僚制", "官僚体制"]),
    ("数目字管理", ["数目字管理"]),
    ("悬浮", ["悬浮"]),
    ("文化霸权", ["文化霸权"]),
    ("路径依赖", ["路径依赖"]),
    ("半脱嵌", ["半脱嵌"]),
    ("大共同体", ["大共同体"]),
    ("小共同体", ["小共同体"]),
    ("关系丛", ["关系丛"]),
]


def load_full_text(filepath):
    """Load full text from JSON file."""
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


def count_concept(text, search_terms):
    """Count occurrences of a concept (any of its search terms)."""
    total = 0
    for term in search_terms:
        total += text.count(term)
    return total


def find_context(text, term, max_context=80):
    """Find first occurrence with context."""
    idx = text.find(term)
    if idx == -1:
        return ""
    start = max(0, idx - max_context // 2)
    end = min(len(text), idx + len(term) + max_context // 2)
    snippet = text[start:end].replace('\n', ' ').strip()
    return snippet


def main():
    # Load all texts
    texts = {}
    for name, info in BOOKS.items():
        filepath = BASE / info["file"]
        text = load_full_text(filepath)
        texts[name] = text
        print(f"Loaded {name}: {len(text):,} chars")

    # Count concepts for each book
    results = {}  # concept -> {book: count}
    contexts = {}  # concept -> {book: context}

    for concept_name, search_terms in CONCEPTS:
        results[concept_name] = {}
        contexts[concept_name] = {}
        for book_name in BOOKS:
            text = texts[book_name]
            count = count_concept(text, search_terms)
            results[concept_name][book_name] = count
            if count > 0:
                # Find context for the first matching term
                for term in search_terms:
                    ctx = find_context(text, term)
                    if ctx:
                        contexts[concept_name][book_name] = ctx
                        break

    # Generate summary table
    print("\n" + "=" * 80)
    print("CONCEPT FREQUENCY SUMMARY")
    print("=" * 80)

    # Sort concepts by total count across new books
    concept_totals = []
    for concept_name, _ in CONCEPTS:
        total = sum(results[concept_name].values())
        book_count = sum(1 for v in results[concept_name].values() if v > 0)
        concept_totals.append((concept_name, book_count, total, results[concept_name]))

    # Sort by total count descending
    concept_totals.sort(key=lambda x: (-x[2], -x[1]))

    # Print to console
    for concept_name, book_count, total, book_counts in concept_totals:
        top_book = max(book_counts, key=book_counts.get) if total > 0 else "-"
        top_count = book_counts.get(top_book, 0)
        print(f"  {concept_name:<12} | {book_count}本 | {total:>6}次 | {top_book}({top_count})")

    # Generate Markdown output
    md_lines = []
    md_lines.append("## EPUB/MOBI 补充分析（2026-07-13）")
    md_lines.append("")
    md_lines.append("> 以下为 6 本 EPUB/MOBI 电子书中 44 个概念的出现频率统计。")
    md_lines.append("> 数据来源：EPUB/MOBI 全文文本提取。")
    md_lines.append("")

    # Summary table
    md_lines.append("### 概念频率汇总表（6本EPUB/MOBI）")
    md_lines.append("")
    md_lines.append("| 概念 | 万历十五年 | 毛泽东文集 | 邓小平文选 | 置身事内 | 人类简史 | 社会学经典 | 新增合计 |")
    md_lines.append("|------|-----------|-----------|-----------|---------|---------|-----------|---------|")

    for concept_name, book_count, total, book_counts in concept_totals:
        row = f"| {concept_name} "
        for book_name in BOOKS:
            count = book_counts.get(book_name, 0)
            row += f"| {count} " if count > 0 else "| - "
        row += f"| {total} |"
        md_lines.append(row)

    md_lines.append("")

    # Per-concept detail with contexts (only for concepts with significant counts)
    md_lines.append("### 概念上下文摘录（按出现频率排序，取每书第一条上下文）")
    md_lines.append("")

    for concept_name, book_count, total, book_counts in concept_totals:
        if total == 0:
            continue
        search_terms = [terms for cn, terms in CONCEPTS if cn == concept_name][0]
        md_lines.append(f"#### 「{concept_name}」— 新增 {book_count} 本书中出现，共 {total} 次")
        md_lines.append(f"**搜索词**: {', '.join(search_terms)}")
        md_lines.append("")
        md_lines.append("| 书名 | 出现次数 | 上下文摘录 |")
        md_lines.append("|------|---------|-----------|")
        for book_name in BOOKS:
            count = book_counts.get(book_name, 0)
            if count > 0:
                ctx = contexts[concept_name].get(book_name, "")[:120]
                md_lines.append(f"| {BOOKS[book_name]['short']} | {count} | {ctx} |")
        md_lines.append("")

    # Write output
    output_path = Path("/mnt/c/workspace/essence/analysis/scripts/epub_concept_output.md")
    output_path.write_text('\n'.join(md_lines), encoding='utf-8')
    print(f"\nOutput written to: {output_path}")

    # Also save JSON for later use
    json_output = {
        concept_name: {
            book_name: {
                "count": results[concept_name][book_name],
                "context": contexts[concept_name].get(book_name, "")
            }
            for book_name in BOOKS
        }
        for concept_name, _ in CONCEPTS
    }
    json_path = Path("/mnt/c/workspace/essence/analysis/scripts/epub_concept_data.json")
    json_path.write_text(json.dumps(json_output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"JSON data saved to: {json_path}")

    return results, contexts


if __name__ == '__main__':
    main()
