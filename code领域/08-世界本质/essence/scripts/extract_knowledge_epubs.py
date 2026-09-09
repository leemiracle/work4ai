#!/usr/bin/env python3
"""Extract structured knowledge from extracted EPUB/MOBI full-text JSON files.

Extracts per book:
1. 目录结构 (TOC structure from chapter headings)
2. 定义性陈述 (Definitional statements)
3. 核心命题/论断 (Core propositions)
4. 关键数据 (Key data/numbers)
5. 关键案例 (Key cases/references)

Output: merged Markdown at analysis/extracted-knowledge-epubs.md
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("/mnt/c/workspace/essence/data/political-books-extracted")
OUTPUT_PATH = Path("/mnt/c/workspace/essence/analysis/extracted-knowledge-epubs.md")

# Load all epub/mobi extracted JSONs
book_files = sorted(DATA_DIR.glob("epub_*.json")) + sorted(DATA_DIR.glob("mobi_*.json"))

# ─── Knowledge extraction patterns ─────────────────────────────────────────────

# Definitional patterns - STRICT to minimize false positives
# Only match clear "term + definitional verb + definition" structures
DEFINITION_PATTERNS = [
    # 所谓X，就是/是指/即Y  (most reliable definitional marker in Chinese)
    (re.compile(r'所谓([\u4e00-\u9fff]{2,8})[，,、]?\s*(?:就是|是指|即|是|就是指)\s*([^\n。；！？]{10,120}[。；])'), '所谓'),
    # X，是指Y (formal definition)
    (re.compile(r'([\u4e00-\u9fff]{2,8})[，,、]\s*是指\s*([^\n。；！？]{10,120}[。；])'), '是指'),
    # X，系指Y (formal)
    (re.compile(r'([\u4e00-\u9fff]{2,8})[，,、]\s*系指\s*([^\n。；！？]{10,120}[。；])'), '系指'),
    # 称X为Y / 称之为X
    (re.compile(r'(?:称|叫做|称为|叫作|简称为|简称|又称为|又称)\s*"?([\u4e00-\u9fff]{2,8})"?[，,]\s*(?:即|也就是|就是|是指)?\s*([^\n。；！？]{10,120}[。；])'), '称'),
    # X的本质是Y
    (re.compile(r'([\u4e00-\u9fff]{2,8})\s*的(?:本质|核心|实质|关键)(?:是|在于|特征是)\s*([^\n。；！？]{10,120}[。；])'), '本质'),
    # 定义为X
    (re.compile(r'([\u4e00-\u9fff]{2,8})\s*可以(?:定义为|理解为)\s*([^\n。；！？]{10,120}[。；])'), '定义'),
]

# Common false-positive terms to exclude
DEFINITION_EXCLUDE = {
    '我们', '他们', '这个', '那个', '这些', '那些', '什么', '可以', '应该',
    '已经', '就是', '以为', '认为', '说明', '表示', '指出', '强调', '提出',
    '发现', '证明', '其实', '然而', '但是', '而且', '从而', '因此', '由于',
    '虽然', '尽管', '只有', '只要', '因为', '所以', '如果', '不仅', '不但',
    '不是', '不能', '不可', '不要', '不会', '没有', '使得', '使得', '接着',
    '以后', '之前', '之后', '当时', '此书', '此外', '其次', '另外', '同时',
    '对于', '关于', '至于', '按照', '根据', '通过', '随着', '虽然如此',
    '这一', '这种', '这类', '这样', '那边', '这里', '那里', '其他', '其余',
    '任何', '某些', '一些', '若干', '大部分', '大部分的', '然后', '即使',
    '以便', '以免', '虽然如此', '一旦', '一直', '一般', '一旦', '一切',
    '一定', '一般', '一直', '一方面', '另一方面', '与此', '对此', '其中',
    '上述', '下面', '上面', '前面', '后面', '中间', '旁边', '附近',
    '但是', '可能', '或许', '也许', '大概', '大约', '似乎', '好像',
    '于是', '总之', '总的来说', '归根结底', '归根到底', '换句话说',
    '尽管如此', '即使如此', '与此同时', '也就是说', '换言之',
    '措施', '次年', '心理', '赏赐', '原则', '办法', '问题', '情况',
    '方面', '部分', '内容', '形式', '结果', '影响', '作用', '关系',
    '条件', '因素', '前提', '基础', '特点', '特征', '性质', '功能',
    '目的', '目标', '意义', '价值', '标准', '规则', '制度', '机制',
    '体制', '体系', '系统', '结构', '模式', '方式', '方法', '手段',
    '途径', '道路', '方向', '趋势', '过程', '阶段', '时期', '时代',
    '历史', '现实', '理论', '实践', '经验', '教训', '启示', '结论',
}

# Proposition patterns: strong claims with markers
PROPOSITION_MARKERS = [
    '根本原因', '主要原因', '重要原因', '核心问题', '关键在于', '本质上',
    '归根结底', '归根到底', '最重要的', '最关键的', '实质上是',
    '由此可见', '因此可以', '这就意味着', '这表明', '这说明',
    '必然', '必须', '不可', '只有...才', '只要...就',
]

# Data patterns: numbers with units, percentages, dates with context
DATA_PATTERN = re.compile(
    r'([\u4e00-\u9fff]{0,20})'  # preceding context
    r'(\d[\d,]*\.?\d*\s*[%％万亿千百十百千万亿人次元吨亩年月日分之百分点倍])'  # number + unit
    r'([\u4e00-\u9fff]{0,30})'  # following context
)

# Case study markers
CASE_MARKERS = [
    '例如', '比如', '以...为例', '案例', '个案', '典型案例',
    '实例', '举例', '譬如', '如', '实践中',
]


def extract_toc(full_text_pages):
    """Extract table of contents from page structure."""
    toc = []
    for page in full_text_pages[:15]:  # TOC usually in first few pages
        text = page['text']
        # Look for chapter markers
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Chapter heading patterns
            if re.match(r'^第[一二三四五六七八九十百千零\d]+[章节篇卷部编编]', line):
                if len(line) < 80:
                    toc.append(line)
            elif re.match(r'^[\d]+[.．、]\s*[\u4e00-\u9fff]', line) and len(line) < 60:
                toc.append(line)
            elif re.match(r'^[一二三四五六七八九十]+[、，]\s*[\u4e00-\u9fff]', line) and len(line) < 60:
                toc.append(line)

    # Deduplicate while preserving order
    seen = set()
    unique_toc = []
    for item in toc:
        if item not in seen:
            seen.add(item)
            unique_toc.append(item)

    return unique_toc[:50]  # cap at 50 entries


def extract_definitions(full_text):
    """Extract definitional statements with strict quality control."""
    definitions = []
    seen = set()

    for pattern, ptype in DEFINITION_PATTERNS:
        for match in pattern.finditer(full_text):
            term = match.group(1).strip()
            definition = match.group(2).strip()

            # Quality filters
            if len(term) < 2 or len(definition) < 12:
                continue

            # Exclude common false-positive terms
            if term in DEFINITION_EXCLUDE:
                continue

            # Exclude if term contains function words
            if any(w in term for w in ['的话', '以来', '之后', '之前', '当中']):
                continue

            # The definition should contain meaningful content (not just dates/names)
            chinese_chars_in_def = len(re.findall(r'[\u4e00-\u9fff]', definition))
            if chinese_chars_in_def < 6:
                continue

            # Skip if definition starts with a pronoun or conjunction
            if definition[0] in '他她我你它这那其由但而为或且因所':
                continue

            key = term + definition[:20]
            if key not in seen:
                seen.add(key)
                definitions.append({
                    'term': term,
                    'definition': definition,
                })

    return definitions[:60]  # cap


def extract_propositions(full_text):
    """Extract core propositions/claims."""
    propositions = []
    seen = set()

    # Split into sentences
    sentences = re.split(r'[。！？\n]', full_text)

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 20 or len(sent) > 200:
            continue

        for marker in PROPOSITION_MARKERS:
            if marker in sent:
                # Quality check: should have meaningful content
                chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', sent))
                if chinese_chars < 10:
                    break

                # Clean up
                clean_sent = sent.strip('，。、；：！？ ')
                if len(clean_sent) < 15:
                    break

                key = clean_sent[:30]
                if key not in seen:
                    seen.add(key)
                    propositions.append(clean_sent)
                break  # one marker per sentence

    return propositions[:60]  # cap


def extract_key_data(full_text):
    """Extract key numerical data with context (handles Arabic and Chinese numerals)."""
    data_items = []
    seen = set()

    # Chinese numeral characters
    cn = r'[一二三四五六七八九十百千万零〇两]'

    # Get surrounding sentence context
    sentences = re.split(r'[。\n]', full_text)

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 15 or len(sent) > 200:
            continue

        has_data = False

        # Arabic numeral patterns with units
        if re.search(r'\d[\d,]*\.?\d*\s*[%％]|\d[\d,]*\.?\d*\s*万[亿万千元人吨亩]|\d[\d,]*\.?\d*\s*亿[万元人]|\d[\d,]*\.?\d*\s*百分点|\d{4}\s*年', sent):
            has_data = True

        # Chinese numeral patterns (common in older texts)
        if re.search(cn + r'+年', sent):  # Chinese numeral years
            has_data = True
        if re.search(cn + r'+[万千百亿]%?', sent):  # Chinese numeral quantities
            has_data = True
        if re.search(r'[百分之]' + cn + r'+' + cn + r'*', sent):  # 百分之X
            has_data = True

        if not has_data:
            continue

        # Filter: should have meaningful Chinese context
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', sent))
        if chinese_chars < 6:
            continue

        # Skip pure chapter/section references
        if re.match(r'^第?\d+[章节页]', sent):
            continue
        if re.match(r'^\d{3}\.', sent):  # "003." chapter numbering
            continue

        key = sent[:40]
        if key not in seen:
            seen.add(key)
            data_items.append(sent.strip())

    return data_items[:50]  # cap


def extract_cases(full_text):
    """Extract case studies and examples."""
    cases = []
    seen = set()

    sentences = re.split(r'[。\n]', full_text)

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 25 or len(sent) > 200:
            continue

        for marker in ['例如', '比如', '以', '案例', '个案', '实例', '举例', '譬如']:
            if marker in sent:
                chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', sent))
                if chinese_chars < 15:
                    break

                clean_sent = sent.strip('，。、；：！？ ')
                if len(clean_sent) < 20:
                    break

                key = clean_sent[:30]
                if key not in seen:
                    seen.add(key)
                    cases.append(clean_sent)
                break

    return cases[:40]  # cap


def extract_chapter_titles(full_text_pages):
    """Extract chapter/section titles from heading-like structures."""
    titles = []

    for page in full_text_pages:
        text = page['text']
        lines = text.split('\n')
        for line in lines[:5]:  # titles usually at start of page
            line = line.strip()
            # Various title patterns
            if re.match(r'^第[一二三四五六七八九十百零\d]+[章节篇卷编]', line) and len(line) < 80:
                titles.append(line)
            elif re.match(r'^[第卷编]?[\d]+', line) and 5 < len(line) < 60 and re.search(r'[\u4e00-\u9fff]{3,}', line):
                titles.append(line)

    # Deduplicate
    seen = set()
    unique = []
    for t in titles:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return unique[:40]


def process_book(book_data):
    """Process a single book and extract all knowledge types."""
    filename = book_data['filename']
    title = book_data.get('title', filename)
    author = book_data.get('author', '')
    total_chars = book_data['total_chars']
    fmt = book_data.get('format', 'unknown')

    # Fix MOBI title if it's a PDB internal name
    if title == 'Ren_Lei_Jian_Shi' or (fmt == 'mobi' and not re.search(r'[\u4e00-\u9fff]', title)):
        title = '人类简史（Sapiens: A Brief History of Humankind）'
        author = '尤瓦尔·赫拉利 (Yuval Noah Harari)'

    # Normalize full_text_pages for TOC extraction
    ft_raw = book_data['full_text']
    if isinstance(ft_raw, list):
        full_text_pages = [
            {'file': p.get('file', '') if isinstance(p, dict) else '',
             'text': p.get('text', '') if isinstance(p, dict) else str(p)}
            for p in ft_raw
        ]
    else:
        full_text_pages = [{'file': '', 'text': str(ft_raw)}]

    # Combine all text (handle both list-of-dicts and list-of-strings)
    ft = book_data['full_text']
    if isinstance(ft, list):
        parts = []
        for p in ft:
            if isinstance(p, dict):
                parts.append(p.get('text', ''))
            elif isinstance(p, str):
                parts.append(p)
        full_text = '\n'.join(parts)
    else:
        full_text = str(ft)

    print(f"  Processing: {title[:50]} ({total_chars:,} chars)")

    toc = extract_chapter_titles(full_text_pages)
    definitions = extract_definitions(full_text)
    propositions = extract_propositions(full_text)
    key_data = extract_key_data(full_text)
    cases = extract_cases(full_text)

    total_knowledge = len(toc) + len(definitions) + len(propositions) + len(key_data) + len(cases)
    print(f"    TOC: {len(toc)}, Defs: {len(definitions)}, Props: {len(propositions)}, "
          f"Data: {len(key_data)}, Cases: {len(cases)} = {total_knowledge} total")

    return {
        'filename': filename,
        'title': title,
        'author': author,
        'format': fmt,
        'total_chars': total_chars,
        'toc': toc,
        'definitions': definitions,
        'propositions': propositions,
        'key_data': key_data,
        'cases': cases,
        'total_knowledge': total_knowledge,
    }


def generate_markdown(all_results):
    """Generate the merged knowledge Markdown file."""
    lines = []
    lines.append("# EPUB/MOBI 知识提取汇总")
    lines.append("")
    lines.append(f"> 提取自 {len(all_results)} 本电子书（{sum(r['total_chars'] for r in all_results):,} 字符）")
    lines.append(f"> 生成日期：2026-07-13")
    lines.append("")

    # Summary table
    lines.append("## 提取概览")
    lines.append("")
    lines.append("| 书名 | 作者 | 格式 | 字符数 | 目录 | 定义 | 命题 | 数据 | 案例 | 合计 |")
    lines.append("|------|------|------|--------|------|------|------|------|------|------|")
    for r in all_results:
        lines.append(
            f"| {r['title'][:25]} | {r['author'][:15]} | {r['format']} | "
            f"{r['total_chars']:,} | {len(r['toc'])} | {len(r['definitions'])} | "
            f"{len(r['propositions'])} | {len(r['key_data'])} | {len(r['cases'])} | "
            f"{r['total_knowledge']} |"
        )
    lines.append("")

    # Per-book details
    for r in all_results:
        lines.append("---")
        lines.append("")
        lines.append(f"## {r['title']}")
        lines.append("")
        lines.append(f"- **文件**: `{r['filename']}`")
        lines.append(f"- **作者**: {r['author']}")
        lines.append(f"- **格式**: {r['format'].upper()}")
        lines.append(f"- **字符数**: {r['total_chars']:,}")
        lines.append(f"- **知识条目**: {r['total_knowledge']} 条")
        lines.append("")

        # TOC
        if r['toc']:
            lines.append("### 目录结构")
            lines.append("")
            for item in r['toc']:
                lines.append(f"- {item}")
            lines.append("")

        # Definitions
        if r['definitions']:
            lines.append("### 定义性陈述")
            lines.append("")
            for d in r['definitions']:
                lines.append(f"- **{d['term']}**: {d['definition']}")
            lines.append("")

        # Propositions
        if r['propositions']:
            lines.append("### 核心命题/论断")
            lines.append("")
            for i, p in enumerate(r['propositions'], 1):
                lines.append(f"{i}. {p}")
            lines.append("")

        # Key data
        if r['key_data']:
            lines.append("### 关键数据")
            lines.append("")
            for d in r['key_data']:
                lines.append(f"- {d}")
            lines.append("")

        # Cases
        if r['cases']:
            lines.append("### 关键案例/实例")
            lines.append("")
            for i, c in enumerate(r['cases'], 1):
                lines.append(f"{i}. {c}")
            lines.append("")

    return '\n'.join(lines)


def main():
    print("=" * 60)
    print("KNOWLEDGE EXTRACTION FROM EPUB/MOBI")
    print("=" * 60)

    all_results = []

    for book_file in book_files:
        print(f"\nLoading: {book_file.name}")
        with open(book_file, encoding='utf-8') as f:
            book_data = json.load(f)

        total_chars = book_data.get('total_chars', 0)

        if total_chars < 100 or not book_data.get('full_text'):
            print(f"  SKIPPED: only {total_chars} chars (image-only)")
            # Still record it
            all_results.append({
                'filename': book_data['filename'],
                'title': book_data.get('title', book_data['filename']),
                'author': book_data.get('author', ''),
                'format': book_data.get('format', 'epub'),
                'total_chars': total_chars,
                'toc': [],
                'definitions': [],
                'propositions': [],
                'key_data': [],
                'cases': [],
                'total_knowledge': 0,
                'note': '图片扫描版，无可提取文本（需OCR）'
            })
            continue

        result = process_book(book_data)
        all_results.append(result)

    # Generate Markdown
    print(f"\n{'='*60}")
    print("Generating Markdown output...")
    markdown = generate_markdown(all_results)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Saved to: {OUTPUT_PATH}")
    print(f"File size: {OUTPUT_PATH.stat().st_size:,} bytes")

    # Also save structured JSON
    json_path = OUTPUT_PATH.with_suffix('.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"JSON saved to: {json_path}")

    # Final summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    total_knowledge = sum(r['total_knowledge'] for r in all_results)
    total_chars = sum(r['total_chars'] for r in all_results)
    print(f"Books processed: {len(all_results)}")
    print(f"Total characters: {total_chars:,}")
    print(f"Total knowledge items: {total_knowledge}")
    print(f"\nPer-book breakdown:")
    for r in all_results:
        print(f"  {r['title'][:40]:<42} {r['total_chars']:>10,} chars  {r['total_knowledge']:>5} items")


if __name__ == '__main__':
    main()
