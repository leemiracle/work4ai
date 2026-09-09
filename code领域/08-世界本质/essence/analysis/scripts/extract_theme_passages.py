#!/usr/bin/env python3
"""Extract theme-relevant passages from 6 EPUB/MOBI books for 4 theme files."""

import json
import re
from pathlib import Path

BASE = Path("/mnt/c/workspace/essence/data/political-books-extracted")

BOOKS = {
    "万历十五年": {
        "file": "epub_05314f688e0d76c44aa385c98f502f93.json",
        "short": "万历十五年",
        "author": "黄仁宇",
    },
    "毛泽东文集": {
        "file": "epub_e077fb766e516aebbf6ad28d9cf81a48.json",
        "short": "毛泽东文集",
        "author": "毛泽东",
    },
    "邓小平文选": {
        "file": "epub_0695ef24be80eecef2179ca7122c88a9.json",
        "short": "邓小平文选(第一卷)",
        "author": "邓小平",
    },
    "置身事内": {
        "file": "epub_fc25bf25f43b22b0ef1ac62c8642850a.json",
        "short": "置身事内",
        "author": "兰小欢",
    },
    "人类简史": {
        "file": "mobi_f124b57a8baef3d0e363c9ee9ebcb01a.json",
        "short": "人类简史",
        "author": "尤瓦尔·赫拉利",
    },
    "中国社会学经典文库": {
        "file": "epub_677b2a39917dfc890ce34c57eb3b159f.json",
        "short": "中国社会学经典文库",
        "author": "费孝通等",
    },
}


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


def load_pages(filepath):
    """Load text as list of pages for position tracking."""
    with open(filepath, encoding='utf-8') as f:
        d = json.load(f)
    ft = d['full_text']
    pages = []
    if isinstance(ft, list):
        for i, p in enumerate(ft):
            if isinstance(p, dict):
                pages.append({'index': i, 'text': p.get('text', '')})
            elif isinstance(p, str):
                pages.append({'index': i, 'text': p})
    else:
        pages.append({'index': 0, 'text': str(ft)})
    return pages


def extract_sentences_with_keywords(full_text, keywords, min_len=30, max_len=300, max_results=8):
    """Extract sentences containing any of the keywords."""
    sentences = re.split(r'[。！？\n]', full_text)
    results = []
    seen_keys = set()

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < min_len or len(sent) > max_len:
            continue

        for kw in keywords:
            if kw in sent:
                # Deduplicate by first 40 chars
                key = sent[:40]
                if key not in seen_keys:
                    seen_keys.add(key)
                    results.append((kw, sent))
                break

    return results[:max_results]


def extract_paragraphs_with_keywords(full_text, keywords, context_chars=200, max_results=5):
    """Extract paragraphs (larger context) containing keywords."""
    results = []
    seen_positions = set()

    for kw in keywords:
        start = 0
        while True:
            idx = full_text.find(kw, start)
            if idx == -1:
                break

            # Check if this position is too close to a previous result
            too_close = False
            for prev_pos in seen_positions:
                if abs(idx - prev_pos) < context_chars:
                    too_close = True
                    break

            if not too_close:
                ctx_start = max(0, idx - context_chars // 2)
                ctx_end = min(len(full_text), idx + context_chars)
                snippet = full_text[ctx_start:ctx_end].replace('\n', ' ').strip()
                # Clean up snippet
                snippet = re.sub(r'\s+', ' ', snippet)
                results.append((kw, idx, snippet))
                seen_positions.add(idx)

            start = idx + len(kw)
            if len(results) >= max_results:
                break
        if len(results) >= max_results:
            break

    return results[:max_results]


def find_specific_passages(full_text, search_phrases, context_before=100, context_after=300, max_results=3):
    """Find specific known passages/phrases with generous context."""
    results = []
    for phrase in search_phrases:
        idx = full_text.find(phrase)
        if idx != -1:
            start = max(0, idx - context_before)
            end = min(len(full_text), idx + len(phrase) + context_after)
            snippet = full_text[start:end].replace('\n', ' ').strip()
            snippet = re.sub(r'\s+', ' ', snippet)
            results.append((phrase, snippet))

            # Find more occurrences
            next_idx = full_text.find(phrase, idx + len(phrase))
            if next_idx != -1 and len(results) < max_results:
                start = max(0, next_idx - context_before)
                end = min(len(full_text), next_idx + len(phrase) + context_after)
                snippet2 = full_text[start:end].replace('\n', ' ').strip()
                snippet2 = re.sub(r'\s+', ' ', snippet2)
                results.append((phrase, snippet2))

    return results[:max_results]


def format_quote(book_short, author, passage_id, text):
    """Format a quote in the project style."""
    # Truncate very long passages
    if len(text) > 500:
        text = text[:500] + "……"
    return f"> **《{book_short}》** | {author} | {passage_id}\n>\n> {text}"


# ─── Theme extraction definitions ─────────────────────────────────────────────

THEMES = {
    "central_local": {
        "title": "央地关系专题",
        "books_keywords": {
            "毛泽东文集": {
                "phrases": ["论十大关系", "中央和地方的关系", "应当在巩固中央统一领导的前提下，扩大一点地方的权力"],
                "keywords": ["中央和地方", "统一领导", "地方积极性", "大权独揽，小权分散", "发挥地方的积极性", "两条腿走路", "集权", "分权", "中央集权"],
            },
            "邓小平文选": {
                "phrases": ["放权让利", "权力下放", "扩大自主权", "调动地方的积极性"],
                "keywords": ["权力下放", "放权", "自主权", "地方积极性", "条块", "统一领导", "集中统一", "分散主义"],
            },
            "置身事内": {
                "phrases": ["地方政府", "分税制", "土地财政", "转移支付"],
                "keywords": ["地方政府经济", "地方发展", "政府与经济", "财政体制", "土地财政", "分税制", "转移支付", "预算外", "融资平台", "城投"],
            },
        },
    },
    "economic_system": {
        "title": "经济体制专题",
        "books_keywords": {
            "邓小平文选": {
                "phrases": ["改革开放", "社会主义市场经济", "市场经济", "解放思想，实事求是", "发展才是硬道理"],
                "keywords": ["改革开放", "市场经济", "商品经济", "经济体制", "所有制", "私营经济", "外资", "引进", "发展生产力", "解放生产力"],
            },
            "置身事内": {
                "phrases": ["土地财政", "产业政策", "政府投资", "地方债务"],
                "keywords": ["土地财政", "土地出让", "产业政策", "政府投资", "基础设施投资", "地方债务", "城投", "融资平台", "房地产"],
            },
            "毛泽东文集": {
                "phrases": ["公私兼顾", "劳资两利", "发展生产，繁荣经济"],
                "keywords": ["公私兼顾", "劳资两利", "经济政策", "新民主主义经济", "国家资本主义", "统购统销", "合作社"],
            },
        },
    },
    "legitimacy_regime": {
        "title": "合法性与政体专题",
        "books_keywords": {
            "毛泽东文集": {
                "phrases": ["人民民主专政", "新民主主义", "论人民民主专政"],
                "keywords": ["人民民主专政", "新民主主义", "阶级斗争", "无产阶级专政", "民主", "专政", "革命", "工农联盟", "统一战线"],
            },
            "邓小平文选": {
                "phrases": ["四项基本原则", "坚持社会主义道路", "坚持无产阶级专政"],
                "keywords": ["四项基本原则", "坚持共产党的领导", "坚持社会主义", "坚持人民民主专政", "坚持马列主义", "资产阶级自由化", "动乱", "安定团结"],
            },
            "万历十五年": {
                "phrases": ["数目字管理", "道德代替法律", "以道德代替法制"],
                "keywords": ["道德", "礼仪", "文官制度", "皇权", "君权", "合法", "传统政治", "治理失败", "体制", "数目字管理", "法治", "人治", "文官"],
            },
            "人类简史": {
                "phrases": ["想象的秩序", "虚构故事", "想象的现实"],
                "keywords": ["虚构", "想象", "想象的秩序", "想象的共同体", "神话", "故事", "合法性", "信仰", "秩序", "协作", "大规模合作"],
            },
        },
    },
    "society_labor": {
        "title": "社会与劳动专题",
        "books_keywords": {
            "中国社会学经典文库": {
                "phrases": ["差序格局", "乡土中国", "费孝通"],
                "keywords": ["差序格局", "乡土", "熟人社会", "礼俗", "法理", "血缘", "地缘", "关系", "面子", "人情", "社区", "村落", "家族", "宗族"],
            },
            "毛泽东文集": {
                "phrases": ["中国社会各阶级的分析", "谁是我们的敌人", "阶级分析"],
                "keywords": ["阶级分析", "地主", "富农", "中农", "贫农", "雇农", "工人阶级", "农民阶级", "资产阶级", "小资产阶级", "阶级斗争", "群众路线"],
            },
        },
    },
}


def process_theme(theme_key, theme_def, texts):
    """Process one theme and generate markdown."""
    lines = []
    lines.append(f"\n## EPUB补充（2026-07-13）")
    lines.append(f"\n> 以下内容从 EPUB/MOBI 全文中自动提取，标注：书名 + 定位标记 + 原文摘录。")
    lines.append("")

    for book_name, search_def in theme_def["books_keywords"].items():
        if book_name not in texts:
            continue

        text = texts[book_name]
        info = BOOKS[book_name]
        lines.append(f"### {info['short']}（{info['author']}）")
        lines.append("")

        # First, find specific known phrases (most valuable)
        phrases = search_def.get("phrases", [])
        if phrases:
            phrase_results = find_specific_passages(text, phrases, context_before=150, context_after=400, max_results=3)
            if phrase_results:
                for phrase, snippet in phrase_results:
                    # Find approximate position
                    pos_idx = text.find(phrase)
                    passage_id = f"搜索词「{phrase[:15]}」" if len(phrase) > 15 else f"搜索词「{phrase}」"
                    lines.append(format_quote(info['short'], info['author'], passage_id, snippet))
                    lines.append("")

        # Then, find keyword-based sentences
        keywords = search_def.get("keywords", [])
        if keywords:
            sentence_results = extract_sentences_with_keywords(text, keywords, min_len=40, max_len=400, max_results=6)
            if sentence_results:
                lines.append(f"*关键词句提取（{', '.join(keywords[:5])}{'…' if len(keywords) > 5 else ''}）*：")
                lines.append("")
                for kw, sent in sentence_results:
                    passage_id = f"关键词「{kw}」"
                    lines.append(format_quote(info['short'], info['author'], passage_id, sent))
                    lines.append("")

        lines.append("---")
        lines.append("")

    return '\n'.join(lines)


def main():
    print("Loading all texts...")
    texts = {}
    for name, info in BOOKS.items():
        texts[name] = load_full_text(BASE / info["file"])
        print(f"  {name}: {len(texts[name]):,} chars")

    results = {}

    for theme_key, theme_def in THEMES.items():
        print(f"\nProcessing theme: {theme_def['title']}")
        md = process_theme(theme_key, theme_def, texts)
        results[theme_key] = md

        # Save individual theme output
        outpath = Path(f"/mnt/c/workspace/essence/analysis/scripts/theme_{theme_key}_epub.md")
        outpath.write_text(md, encoding='utf-8')
        print(f"  Saved to: {outpath}")

    print("\nDone!")


if __name__ == '__main__':
    main()
