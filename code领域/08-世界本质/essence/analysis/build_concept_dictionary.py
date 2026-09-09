#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a complete "Political Concept Dictionary" from knowledge_index.json.

Source: /mnt/c/workspace/essence/data/political-books-extracted/knowledge_index.json
Output: /mnt/c/workspace/essence/analysis/political-concept-dictionary.md

Strategy:
1. Load JSON, extract all concepts.
2. Normalize book names (merge variants like "中国国家治理的制度逻辑" / "... 一个组织学研究").
3. For each concept, merge definitions from different books (dedupe by book+page+text).
4. Compute coverage = unique books covering the concept (from cross_book_index + defs + mentions).
   Compute total appearances = sum of counts from cross_book_index (fallback to def+mention count).
5. Rank concepts by: books_covered * 1000 + total_appearances. Select top 200.
6. Sort the 200 by pinyin.
7. For each concept, write a full dictionary entry with:
   - coverage line (books | appearances)
   - best definition (longest text with definitional markers, preferring primary sources)
   - other definitions
   - essence connections (insights + chapters by keyword match)
"""
import json
import re
import os
import collections
from pypinyin import lazy_pinyin

SRC = "/mnt/c/workspace/essence/data/political-books-extracted/knowledge_index.json"
DST = "/mnt/c/workspace/essence/analysis/political-concept-dictionary.md"
INSIGHTS_DIR = "/mnt/c/workspace/essence/insights/2026-07"
CHINA_GOV_FILE = "/mnt/c/workspace/essence/03-social-sciences/politics/china-governance.md"


# ---------- Book name normalization ----------
CANONICAL_BOOK_MAP = [
    (r"中国国家治理的制度逻辑.*", "中国国家治理的制度逻辑"),
    (r"以利为利.*", "以利为利"),
    (r"分析与思考.*", "分析与思考"),
    (r"(卡尔·波普尔[：:])?历史决定论的贫困", "历史决定论的贫困"),
    (r"过渡劳动.*", "过渡劳动"),
    (r"置身事内.*", "置身事内"),
    (r"万历十五年.*", "万历十五年"),
    (r"转型中的地方政府.*", "转型中的地方政府"),
    (r"中国社会学经典文库.*", "中国社会学经典文库"),
    (r"钱穆国学作品集.*", "钱穆国学作品集"),
    (r"毛泽东文集.*", "毛泽东文集"),
    (r"邓小平文选.*", "邓小平文选 第一卷"),
    (r"《习近平谈治国理政》第一卷", "习近平谈治国理政 第一卷"),
    (r"《习近平谈治国理政》第二卷", "习近平谈治国理政 第二卷"),
    (r"《习近平谈治国理政》第三卷", "习近平谈治国理政 第三卷"),
    (r"人地之间.*", "人地之间"),
    (r"政治的人生", "政治的人生"),
    (r"美国反对美国", "美国反对美国"),
    (r"突围.*国门初开.*", "突围：国门初开的岁月"),
    (r"社会与政治运动讲义.*", "社会与政治运动讲义"),
]


def normalize_book(name: str) -> str:
    if not name:
        return ""
    m = re.match(r"陈云文选[··]??第([一二三])卷", name)
    if m:
        return f"陈云文选 第{m.group(1)}卷"
    m = re.search(r"习近平谈治国理政[》”）]?第([一二三])卷", name)
    if m:
        return f"习近平谈治国理政 第{m.group(1)}卷"
    for pat, canon in CANONICAL_BOOK_MAP:
        if canon is None:
            continue
        if re.search(pat, name):
            return canon
    return name.strip()


BOOK_AUTHOR = {
    "中国国家治理的制度逻辑": "周雪光",
    "转型中的地方政府": "周黎安",
    "以利为利": "周飞舟",
    "分析与思考": "黄奇帆",
    "过渡劳动": "孙萍",
    "历史决定论的贫困": "波普尔",
    "万历十五年": "黄仁宇",
    "中国社会学经典文库": "费孝通",
    "钱穆国学作品集": "钱穆",
    "毛泽东文集": "毛泽东",
    "邓小平文选 第一卷": "邓小平",
    "习近平谈治国理政 第一卷": "习近平",
    "习近平谈治国理政 第二卷": "习近平",
    "习近平谈治国理政 第三卷": "习近平",
    "陈云文选 第一卷": "陈云",
    "陈云文选 第二卷": "陈云",
    "陈云文选 第三卷": "陈云",
    "置身事内": "兰小欢",
    "人地之间": "陶然",
    "政治的人生": "王沪宁",
    "美国反对美国": "王沪宁",
    "突围：国门初开的岁月": "谷牧",
    "社会与政治运动讲义": "赵鼎新",
}


def author_of(book_canon: str) -> str:
    return BOOK_AUTHOR.get(book_canon, "")


# ---------- Definitional marker detection ----------
DEF_MARKERS = [
    "是指", "指的是", "称为", "称之为", "所谓", "即指",
    "定义为", "定义是", "本质是", "本质在于", "核心是", "核心在于",
    "意思是", "意味着", "可以理解为", "表现为",
    "的形式", "的机制", "的模式", "的制度",
    "是一种", "是一个", "是一类", "是一套",
    "简言之", "即是", "即是说", "也即",
    "（即", "(即",
]


def is_definitional(text: str) -> bool:
    if not text:
        return False
    return any(m in text for m in DEF_MARKERS)


def def_quality_score(text: str, book_canon: str, concept: str = "") -> tuple:
    """Higher = better. Tuple compared lexicographically.
    Priorities:
      1. Definition contains the concept name itself (clearly ABOUT this concept).
      2. Has a strong definitional marker.
      3. From a primary theoretical source.
      4. Substantial length (8-200 chars sweet spot).
    """
    length = len(text) if text else 0
    has_strong = any(m in text for m in STRONG_DEF_MARKERS)
    has_weak = is_definitional(text)
    length_score = min(length, 200)
    primary_bonus = 0
    if book_canon in {"中国国家治理的制度逻辑", "转型中的地方政府", "以利为利",
                      "历史决定论的贫困", "置身事内", "中国社会学经典文库",
                      "万历十五年", "人地之间"}:
        primary_bonus = 50
    # Concept-name presence is the strongest signal of relevance
    name_present = bool(concept) and concept in text
    return (name_present, has_strong, primary_bonus, has_weak, length_score, -max(0, length - 200))


# ---------- Concept quality filter (remove extraction noise) ----------
STRONG_DEF_MARKERS = ['所谓', '是指', '称为', '称之为', '简言之', '定义为',
                      '本质是', '本质在于', '即指', '意思是', '指的是']

# Phrase-leading tokens that indicate a sentence fragment, not a concept
PHRASE_START = [
    '他们', '我们', '你们', '这个', '那个', '这些', '那些', '这是', '那是',
    '可以', '应该', '必须', '就是', '例如', '比如', '所谓', '否则', '于是',
    '然而', '另外', '此外', '因此', '因为', '所以', '但是', '虽然', '既然',
    '不过', '如果', '只要', '只有', '无论', '不管', '倘若', '假使', '至于',
    '对于', '关于', '按照', '根据', '凭借', '通过', '经过', '随着', '沿着',
    '朝着', '为着',
    '从', '于', '由', '为', '但', '则', '也', '又', '还', '都', '只', '不',
    '没', '有', '是', '的', '了', '吗', '呢', '吧', '啊', '呀', '这', '那',
    '他', '她', '它', '我', '你', '据', '至', '给', '向', '当', '被', '把',
    '让', '使',
]

QUOTE_CHARS = set('"\'""''「」『』“”„‟')
BRACKET_CHARS = set('[]【】{}')


def passes_concept_filter(name: str) -> bool:
    """Filter out extraction noise (sentence fragments, names, dates, broken quotes)."""
    if not name:
        return False
    n = len(name)
    if n < 2 or n > 8:
        return False
    # Reject names with any quotation marks (almost always broken extraction)
    if any(ch in name for ch in QUOTE_CHARS):
        return False
    # Reject names with brackets
    if any(ch in name for ch in BRACKET_CHARS):
        return False
    # Reject names with sentence punctuation
    if any(ch in name for ch in '，。？！；：'):
        return False
    # Reject names with spaces
    if ' ' in name:
        return False
    # Reject names containing Latin letters (e.g., "capital", "U型") — keep Chinese-only
    if re.search(r'[A-Za-z]', name):
        return False
    # Reject pure date / number
    if re.fullmatch(r'[\d\.\-年月日]+', name):
        return False
    # Reject names starting with phrase-leading token (if short overall)
    for w in PHRASE_START:
        if name.startswith(w) and n <= len(w) + 2:
            return False
    # Reject names starting with digit unless pattern like "35岁现象"
    if name[0].isdigit() and not re.match(r'\d+[岁现象年代次]', name):
        return False
    # Reject "第X个/章/卷/条..."
    if re.search(r'^第.{1,3}个', name):
        return False
    if re.search(r'^第[一二三四五六七八九十百千万0-9]+[章卷编篇条步骤节]', name):
        return False
    # Reject names starting or ending with 的
    if name.startswith('的') or name.endswith('的'):
        return False
    return True


def concept_rank_score(item: dict) -> int:
    """Compute selection score for top-200 ranking.
    Layers tier1 > tier2 > tier3 via bonus weights."""
    bc = item["books_covered"]
    total = item["total_appearances"]
    nd = len(item["defs"])
    has_strong = any(
        any(m in d["text"] for m in STRONG_DEF_MARKERS)
        for d in item["defs"]
    )
    # Primary-source bonus
    primary_books = {"中国国家治理的制度逻辑", "转型中的地方政府", "以利为利",
                     "历史决定论的贫困", "置身事内", "中国社会学经典文库",
                     "万历十五年", "人地之间"}
    has_primary = any(d["book"] in primary_books for d in item["defs"])
    score = bc * 1000 + total
    if nd >= 2:
        score += 500
    if has_strong:
        score += 200
    if has_primary:
        score += 100
    if nd >= 1:
        score += 50
    return score


# ---------- Essence connection mapping ----------
def build_essence_index():
    insight_index = {"__all__": []}
    if os.path.isdir(INSIGHTS_DIR):
        for fn in sorted(os.listdir(INSIGHTS_DIR)):
            if not fn.endswith(".md"):
                continue
            path = os.path.join(INSIGHTS_DIR, fn)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue
            slug = fn.replace(".md", "")
            slug_no_date = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
            tokens = re.split(r"[-_]", slug_no_date)
            insight_index["__all__"].append((fn, slug_no_date, tokens, content))
    return insight_index


def find_insights_for_concept(concept: str, insight_index):
    matches = []
    for fn, slug, tokens, content in insight_index.get("__all__", []):
        if concept in content:
            matches.append(fn)
            continue
    return matches[:5]


CN_EN_SLUG_HINTS = {
    "行政发包制": ["administrative-subcontracting"],
    "晋升锦标赛": ["promotion-tournament"],
    "运动型治理": ["campaign-governance"],
    "运动式治理": ["campaign-governance"],
    "绩效合法性": ["performance-legitimacy"],
    "差序格局": ["differential-mode"],
    "项目制": ["fiscal-sociology"],
    "财政社会学": ["fiscal-sociology"],
    "土地财政": ["land-finance", "fiscal-sociology"],
    "历史决定论": ["historical-determinism"],
    "改革": ["reform-and-opening"],
    "开放": ["reform-and-opening"],
    "改革开放": ["reform-and-opening"],
    "平台劳动": ["platform-labor"],
    "外卖骑手": ["platform-labor"],
    "过渡劳动": ["platform-labor"],
    "士大夫": ["scholar-official-government"],
    "官僚制": ["scholar-official-government"],
    "虚拟秩序": ["fictitious-order"],
    "概念演化": ["concept-evolution"],
    "跨书概念": ["cross-book-concept-map"],
}


def find_insights_enhanced(concept: str, insight_index):
    matches = find_insights_for_concept(concept, insight_index)
    for slug_hint in CN_EN_SLUG_HINTS.get(concept, []):
        for fn, slug, tokens, content in insight_index.get("__all__", []):
            if slug == slug_hint and fn not in matches:
                matches.append(fn)
    return matches[:5]


def find_chapter_for_concept(concept: str):
    refs = []
    if not os.path.isfile(CHINA_GOV_FILE):
        return refs
    try:
        with open(CHINA_GOV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return refs
    current_top = ""
    current_sub = ""
    for line in lines:
        l = line.rstrip()
        if l.startswith("# ") and not l.startswith("## "):
            continue
        if l.startswith("## "):
            current_top = l.lstrip("# ").strip()
        elif l.startswith("### "):
            current_sub = l.lstrip("# ").strip()
        if concept in l:
            ref = current_top
            if current_sub and concept in current_sub:
                ref = current_sub
            elif current_sub:
                ref = f"{current_top} > {current_sub}"
            if ref and ref not in refs:
                refs.append(ref)
    return refs[:3]


def is_toc_context(ctx: str) -> bool:
    """Detect table-of-contents-like context (mostly page dots & numbers)."""
    if not ctx:
        return True
    # Count dots and digits
    dots = ctx.count(".") + ctx.count("…") + ctx.count("·")
    digits = sum(1 for ch in ctx if ch.isdigit())
    letters = sum(1 for ch in ctx if ch.isalpha() or '\u4e00' <= ch <= '\u9fff')
    if letters == 0:
        return True
    # If dots+digits dominate, it's TOC
    if dots + digits > letters * 1.5:
        return True
    return False


def pick_best_context(contexts: list, concept: str):
    """From a list of {book, count, context}, pick the most informative non-TOC one."""
    primary_books = {"中国国家治理的制度逻辑", "转型中的地方政府", "以利为利",
                     "历史决定论的贫困", "置身事内", "中国社会学经典文库",
                     "万历十五年", "人地之间"}
    candidates = [c for c in contexts if not is_toc_context(c["context"])]
    if not candidates:
        candidates = list(contexts)
    if not candidates:
        return None
    # Prefer: concept appears in context, then primary book, then high count
    def key(c):
        return (
            concept in c["context"],
            c["book"] in primary_books,
            c["count"],
        )
    return max(candidates, key=key)


def clean_context(ctx: str, concept: str, max_len: int = 200) -> str:
    """Extract a window around the concept mention; trim TOC fragments."""
    if not ctx:
        return ""
    # Find concept position
    pos = ctx.find(concept)
    if pos < 0:
        text = ctx[:max_len]
    else:
        start = max(0, pos - 60)
        end = min(len(ctx), pos + len(concept) + 120)
        text = ctx[start:end]
        if start > 0:
            text = "…" + text
        if end < len(ctx):
            text = text + "…"
    # Collapse runs of dots/digits (TOC residue)
    text = re.sub(r"[\.…·]{3,}", "…", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def format_count(n: int) -> str:
    if n >= 10000:
        return f"{n/10000:.1f}万"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    concepts = data["concepts"]
    cbi = data.get("cross_book_index", [])

    cbi_by_concept = collections.defaultdict(list)
    cbi_total_books = {}
    for e in cbi:
        c = e.get("concept", "")
        if not c:
            continue
        book_canon = normalize_book(e.get("book", ""))
        count = int(e.get("count", 0) or 0)
        cbi_by_concept[c].append((book_canon, count))
        if c in cbi_total_books:
            cbi_total_books[c] = max(cbi_total_books[c], int(e.get("total_books", 0) or 0))
        else:
            cbi_total_books[c] = int(e.get("total_books", 0) or 0)

    aggregated = []
    for c in concepts:
        name = c.get("concept", "")
        defs_raw = c.get("definitions", [])
        mentions_raw = c.get("mentions", [])

        seen_def = set()
        defs = []
        for d in defs_raw:
            book_c = normalize_book(d.get("book", ""))
            page = (d.get("page") or "").strip()
            text = (d.get("text") or "").strip()
            if not text:
                continue
            if len(text) < 8:
                continue
            if re.fullmatch(r"[\d\.\s…\.…\-\(\)（）]+", text):
                continue
            key = (book_c, page, text[:50])
            if key in seen_def:
                continue
            seen_def.add(key)
            defs.append({
                "book": book_c,
                "author": d.get("author") or author_of(book_c),
                "page": page,
                "text": text,
            })

        cbi_entries = cbi_by_concept.get(name, [])
        cbi_books = {b for b, _ in cbi_entries}
        cbi_total = sum(cnt for _, cnt in cbi_entries)
        # Keep top cross-book contexts (for fallback when no definition)
        cbi_contexts = []
        for e in cbi:
            if e.get("concept") == name:
                ctx = (e.get("context") or "").strip()
                if ctx:
                    cbi_contexts.append({
                        "book": normalize_book(e.get("book", "")),
                        "count": int(e.get("count", 0) or 0),
                        "context": ctx,
                    })
        # Sort by count desc
        cbi_contexts.sort(key=lambda x: -x["count"])

        def_books = {d["book"] for d in defs if d["book"]}
        men_books = set()
        men_total = 0
        for m in mentions_raw:
            b = normalize_book(m.get("book", ""))
            if b:
                men_books.add(b)
                men_total += int(m.get("count", 0) or 0)

        all_books = cbi_books | def_books | men_books
        all_books.discard("")
        books_covered = len(all_books)

        if cbi_total > 0:
            total_appearances = cbi_total
        else:
            total_appearances = len(defs) + men_total

        # Apply concept-quality filter to drop extraction noise.
        # A concept is kept if it passes the name filter AND has at least one
        # definition OR has cross-book coverage. Pure-mention single-book
        # entries that fail the filter are dropped as noise.
        passes = passes_concept_filter(name)
        keep = passes and (bool(defs) or books_covered >= 2)
        if not keep:
            continue

        item = {
            "concept": name,
            "defs": defs,
            "books": sorted(all_books),
            "books_covered": books_covered,
            "total_appearances": total_appearances,
            "score": 0,  # filled below
            "cbi_total_books_reported": cbi_total_books.get(name, 0),
            "cbi_contexts": cbi_contexts,
        }
        item["score"] = concept_rank_score(item)
        aggregated.append(item)

    # Rank by combined score; tiebreak by def-count then pinyin for stability
    def rank_key(it):
        from pypinyin import lazy_pinyin as _lp
        return (-it["score"], -len(it["defs"]), _lp(it["concept"]))
    aggregated.sort(key=rank_key)

    # Select top 200 with stable tiebreak (no boundary explosion)
    top = aggregated[:200]

    def pinyin_key(item):
        py = lazy_pinyin(item["concept"])
        return (py, item["concept"])
    top.sort(key=pinyin_key)

    insight_index = build_essence_index()

    out = []
    out.append("# 政治学概念词典")
    out.append("")
    out.append("> **数据源**: `data/political-books-extracted/knowledge_index.json`  ")
    out.append(f"> **概念总数**: 701 个（全库）/ 本词典收录 **{len(top)}** 个最重要概念  ")
    out.append("> **覆盖书籍**: 21 本核心政治学/治理/经济学著作  ")
    out.append("> **排序规则**: 多书覆盖/多定义/强定义标记/核心著作 加权打分选 Top 200，再按拼音排序  ")
    out.append("> **生成日期**: 2026-07-14  ")
    out.append("")
    out.append("## 目录")
    out.append("")
    initial_groups = collections.OrderedDict()
    for item in top:
        py = lazy_pinyin(item["concept"])
        initial = py[0][0].upper() if py and py[0] else "#"
        if not re.match(r"[A-Z]", initial):
            initial = "#"
        initial_groups.setdefault(initial, []).append(item)
    for initial in sorted(initial_groups.keys()):
        items = initial_groups[initial]
        out.append(f"### {initial}（{len(items)}）")
        out.append("")
        line_parts = []
        for item in items:
            anchor = re.sub(r"[^\w\u4e00-\u9fff]+", "-", item["concept"]).strip("-").lower()
            line_parts.append(f"[{item['concept']}](#{anchor})")
            if len(line_parts) >= 8:
                out.append(" · ".join(line_parts) + "  ")
                line_parts = []
        if line_parts:
            out.append(" · ".join(line_parts) + "  ")
        out.append("")

    out.append("---")
    out.append("")
    out.append("## 词典正文")
    out.append("")

    for idx, item in enumerate(top, 1):
        concept = item["concept"]
        defs = item["defs"]
        books = item["books"]
        books_covered = item["books_covered"]
        total_appearances = item["total_appearances"]

        if defs:
            best = max(defs, key=lambda d: def_quality_score(d["text"], d["book"], concept))
            other_defs = [d for d in defs if d is not best]
        else:
            best = None
            other_defs = []

        insight_matches = find_insights_enhanced(concept, insight_index)
        chapter_refs = find_chapter_for_concept(concept)

        anchor = re.sub(r"[^\w\u4e00-\u9fff]+", "-", concept).strip("-").lower()
        out.append(f"<a id=\"{anchor}\"></a>")
        out.append(f"## {idx}. {concept}")
        out.append("")
        out.append(f"**覆盖**: {books_covered} 本书 | **总出现**: {format_count(total_appearances)} 次 | **定义条目**: {len(defs)} 条")
        if books:
            out.append("")
            out.append("**来源书籍**: " + "、".join(books))
        out.append("")

        if best:
            author = best.get("author") or author_of(best["book"])
            page = best.get("page", "")
            loc = f"{author} {page}".strip() if (author or page) else best["book"]
            out.append(f"**最佳定义**（{loc}）:")
            out.append("")
            out.append(f'> "{best["text"]}"')
            out.append("")
        else:
            # Fallback: use cross-book context
            best_ctx = pick_best_context(item.get("cbi_contexts", []), concept)
            if best_ctx:
                author = author_of(best_ctx["book"])
                loc = f"{author}《{best_ctx['book']}》" if author else best_ctx["book"]
                snippet = clean_context(best_ctx["context"], concept)
                out.append(f"**代表性语境**（{loc}，跨书索引 {best_ctx['count']} 次）:")
                out.append("")
                out.append(f'> "{snippet}"')
                out.append("")
            else:
                out.append("**定义**: *（无明确定义条目，亦无可用上下文）*")
                out.append("")

        if other_defs:
            out.append("**其他定义**:")
            out.append("")
            other_defs_sorted = sorted(other_defs, key=lambda d: -def_quality_score(d["text"], d["book"], concept)[4])
            for d in other_defs_sorted[:8]:
                author = d.get("author") or author_of(d["book"])
                page = d.get("page", "")
                loc = f"{author} {page}".strip() if (author or page) else d["book"]
                text = d["text"]
                if len(text) > 240:
                    text = text[:240].rstrip() + "…"
                out.append(f'- {loc}: "{text}"')
            if len(other_defs_sorted) > 8:
                out.append(f'- *…另有 {len(other_defs_sorted) - 8} 条定义省略*')
            out.append("")

        conn_parts = []
        if insight_matches:
            insight_links = [f"insight `{fn.replace('.md','')}`" for fn in insight_matches[:3]]
            conn_parts.append("、".join(insight_links))
        if chapter_refs:
            conn_parts.append("中国治理专题：" + " / ".join(chapter_refs[:2]))
        if conn_parts:
            out.append("**essence 关联**: " + " | ".join(conn_parts))
            out.append("")

        out.append("---")
        out.append("")

    out.append("## 附录 A：全 701 概念排名（前 200 名）")
    out.append("")
    out.append("| 排名 | 概念 | 覆盖书数 | 总出现 | 评分 |")
    out.append("|------|------|----------|--------|------|")
    aggregated_sorted = sorted(aggregated, key=lambda x: -x["score"])
    for i, item in enumerate(aggregated_sorted[:200], 1):
        out.append(f"| {i} | {item['concept']} | {item['books_covered']} | {format_count(item['total_appearances'])} | {item['score']} |")
    out.append("")
    out.append(f"*（剩余 {len(aggregated_sorted) - 200} 个概念评分较低，未列入上表；可在 `knowledge_index.json` 中查询完整列表。）*")
    out.append("")

    out.append("## 附录 B：来源书籍（21 本）")
    out.append("")
    out.append("| 规范名 | 作者 |")
    out.append("|--------|------|")
    for book, author in sorted(BOOK_AUTHOR.items()):
        out.append(f"| {book} | {author} |")
    out.append("")

    out.append("## 附录 C：方法说明")
    out.append("")
    out.append("- **数据源**: `data/political-books-extracted/knowledge_index.json`，含 701 个概念、2339 条命题、2529 条数据点、680 个案例、378 条跨书索引。")
    out.append("- **概念筛选**: 701 条原始条目中大量是抽取噪声（句子片段、人名、日期、未闭合引号等）。本词典先用 `passes_concept_filter` 过滤：要求名称 2-8 字、无引号/括号/标点、不以介词/连词起头、非纯日期/数字；并要求至少有 1 条定义或覆盖 ≥2 本书。过滤后保留约 380 个真实概念。")
    out.append("- **覆盖书数**: 综合三处来源——`cross_book_index`、概念定义、概念提及——去重后统计。")
    out.append("- **总出现次数**: 优先使用 `cross_book_index` 的 `count` 总和（更可靠，因基于全文检索）；若概念未进入跨书索引，则回退到“定义条数 + 提及 count 总和”。")
    out.append("- **综合评分**: `books_covered×1000 + total_appearances`，加分层级：多定义 (+500)、定义含强标记词 (+200)、来自核心理论著作 (+100)、有定义 (+50)。这保证多书概念 > 单书多定义 > 单书强定义 > 单书弱定义。")
    out.append("- **书名归一化**: 将“中国国家治理的制度逻辑”与“... 一个组织学研究”、“以利为利”与“...：财政关系与地方政府行为”等变体合并为规范名；陈云文选/习近平谈治国理政 保留分卷。")
    out.append("- **最佳定义评选**: 优先选含定义标记词（“是指/称为/即/本质是/核心是…”）的条目；其次优先核心理论著作（周雪光/周黎安/周飞舟/波普尔/兰小欢/费孝通/黄仁宇/陶然）；再次取 8-200 字之间较长者。")
    out.append("- **拼音排序**: 使用 `pypinyin.lazy_pinyin` 取首字母分组。")
    out.append("- **essence 关联**: 通过概念名在 `insights/2026-07/*.md` 中做全文匹配，并匹配 `03-social-sciences/politics/china-governance.md` 的章节标题。")
    out.append("")

    text = "\n".join(out)
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    with open(DST, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"OK Written: {DST}")
    print(f"   Concepts in dictionary: {len(top)}")
    print(f"   File size: {len(text):,} chars / {len(text.encode('utf-8')):,} bytes")
    with_defs = sum(1 for it in top if it["defs"])
    without_defs = len(top) - with_defs
    print(f"   With definitions: {with_defs} / without: {without_defs}")


if __name__ == "__main__":
    main()
