#!/usr/bin/env python3
"""
深度知识提取 v2：中国国家治理的制度逻辑（周雪光）
改进：TOC直接解析、案例模式收紧、定义模式优化
"""

import json
import re
import os

INPUT_PATH = "/mnt/c/workspace/essence/data/political-books-extracted/26cf383bac61.json"
OUTPUT_PATH = "/mnt/c/workspace/essence/analysis/extracted-knowledge-zhou-xueguang.md"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

pages = data["full_text"]
page_map = {p["page"]: p["text"] for p in pages}

def get_text(page_num):
    return page_map.get(page_num, "")

def clean(t):
    """Remove leading standalone page numbers."""
    lines = t.strip().split("\n")
    while lines and re.match(r"^\d{1,4}$", lines[0].strip()):
        lines.pop(0)
    return "\n".join(lines)

# ============================================================
# 4. CHAPTER STRUCTURE — parse TOC from pages 5-8
# ============================================================
# The TOC uses "第 X 章" (with thin spaces). Parse the known structure.

# Build TOC manually from the known structure + extract subsections from TOC pages
toc_entries = []

# Parse TOC pages (5-8) for chapter/unit/section structure
toc_raw = ""
for pg in [5, 6, 7, 8]:
    toc_raw += get_text(pg) + "\n"

# Remove the dot leaders and page numbers
toc_cleaned = re.sub(r'[\.…·]+\s*\d*', '', toc_raw)
toc_cleaned = re.sub(r'\n\s*\d+\s*\n', '\n', toc_cleaned)

# Extract chapters: "第 X 章  Title"
# The pattern in text is: 第 + space + number + 章
chapter_re = re.compile(r'第\s*([\d一二三四五六七八九十]+)\s*章\s*([^\n]+)')
unit_re = re.compile(r'第\s*([一二三四五六七八九十]+)\s*单元\s*([^\n]+)')

for m in unit_re.finditer(toc_cleaned):
    unit_num = m.group(1)
    unit_title = m.group(2).strip()
    toc_entries.append(("unit", unit_num, unit_title))

for m in chapter_re.finditer(toc_cleaned):
    ch_num = m.group(1)
    ch_title = m.group(2).strip()
    # Clean title: remove trailing whitespace, dots
    ch_title = re.sub(r'\s+', ' ', ch_title).strip()
    # Remove page numbers at end
    ch_title = re.sub(r'\s*\d+$', '', ch_title).strip()
    if len(ch_title) > 1:
        toc_entries.append(("chapter", ch_num, ch_title))

# Extract section titles from TOC (indented subsections)
# These are lines with significant leading whitespace in the TOC
section_titles_from_toc = []
for line in toc_raw.split("\n"):
    stripped = line.strip()
    # Remove dot leaders and page numbers
    cleaned_line = re.sub(r'[\.…·]+\s*\d*', '', stripped).strip()
    cleaned_line = re.sub(r'\s*\d+$', '', cleaned_line).strip()
    if not cleaned_line or len(cleaned_line) < 3:
        continue
    # Skip if it's a chapter or unit line
    if re.match(r'第\s*[\d一二三四五六七八九十]+\s*[单章编]', cleaned_line):
        continue
    if re.match(r'^(目|自|参考|出版|Contents|Preface|Chapter|Part|Bibliography|Afterword)', cleaned_line):
        continue
    if re.match(r'^\d+$', cleaned_line):
        continue
    # These are section titles
    section_titles_from_toc.append(cleaned_line)

# Parse chapter page numbers directly from TOC (book page + offset 10 = PDF page)
chapter_pages = {}
for m in re.finditer(r'第\s*(\d+)\s*章\s*([^…\n]*?)…+\s*(\d+)', toc_raw):
    ch_num = m.group(1)
    book_pg = int(m.group(3))
    pdf_pg = book_pg + 10  # offset: book page 1 = PDF page 11
    chapter_pages[ch_num] = (pdf_pg, m.group(2).strip())

# ============================================================
# 1. DEFINITIONS (定义性陈述)
# ============================================================
# Refined patterns — must have clear definitional structure
def_patterns = [
    # 所谓X就是/所谓X是指 — strong definition
    r'所谓[^。\n，]{2,25}(?:就是|是指|便是)[^。\n]{3,150}',
    # X是指Y (concept + 是指 + explanation)
    r'[\u4e00-\u9fff""''「]{2,20}[""''」]?(?:，)?是指[^。\n]{8,150}',
    # 意味着 — but only when preceded by a concept
    r'[\u4e00-\u9fff]{3,15}意味着[^。\n]{8,120}',
    # 可以定义为
    r'[^。\n]{2,20}可以定义为[^。\n]{8,150}',
    # 特指/意指/泛指
    r'(?:特指|意指|泛指|定义为)[^。\n，]{8,120}',
    # 指的是/指的是
    r'(?:指的是|即指)[^。\n，]{8,120}',
    # "...即..." definitions
    r'[，；]([^。\n]{2,15})，即([^。\n]{5,80})[，。；]',
    # "X，就是Y" / "X，就是指Y"
    r'[""「]([^""」]{2,15})[""」](?:，)?(?:就是|是指|便是|就是指)([^。\n]{5,100})',
    # 意为/意即
    r'(?:意为|意即)[^。\n，]{8,100}',
    # "简言之，X是Y" 
    r'(?:简言之|简而言之|换言之)[，,]?\s*[^。\n]{5,120}',
]

definitions = []
for p in pages:
    text = clean(p["text"])
    page_num = p["page"]
    if page_num <= 10:
        continue  # skip TOC/preface front matter
    for pattern in def_patterns:
        for m in re.finditer(pattern, text):
            snippet = m.group(0).strip()
            if len(snippet) < 10:
                continue
            cn = len(re.findall(r'[\u4e00-\u9fff]', snippet))
            if cn < 8:
                continue
            # Skip pure propositions (handled separately)
            if snippet.startswith(('我认为', '本书', '我的论点', '这一')):
                continue
            definitions.append({"page": page_num, "text": snippet[:300]})

# Deduplicate
seen = set()
uniq = []
for d in definitions:
    k = (d["page"], d["text"][:50])
    if k not in seen:
        seen.add(k)
        uniq.append(d)
definitions = sorted(uniq, key=lambda x: (x["page"], x["text"]))

# ============================================================
# 2. KEY DATA (关键数据)
# ============================================================
data_patterns = [
    # Percentages with context
    r'[^。\n，]{5,50}\d+(?:\.\d+)?\s*%[^。\n]{0,60}',
    # 万/亿 with units
    r'\d+(?:\.\d+)?(?:多|余)?(?:万|亿)(?:人|元|美元|吨|亩|个|名|件|次|场|年|公里|平方米|公顷|美元|块|分)[^。\n]{0,50}',
    # Year ranges: 2004-2005年
    r'(?:19|20)\d{2}[\—\-–](?:19|20)?\d{2}\s*年[^。\n]{0,60}',
    # 占 + percentage
    r'占[^。\n]{2,40}\d+(?:\.\d+)?\s*%[^。\n]{0,40}',
    # Comparison with numbers
    r'(?:增长|下降|上升|减少|提高|降低|增加|扩大|缩小|超过|不足|不到)[^。\n]{0,30}\d+(?:\.\d+)?(?:%|倍|万|亿|个)[^。\n]{0,40}',
    # Fiscal/economic data
    r'(?:GDP|财政收入|财政支出|税收|预算|赤字|人均|比例|总额|总量)[^。\n]{0,30}\d[^。\n]{0,50}',
]

key_data = []
for p in pages:
    text = clean(p["text"])
    page_num = p["page"]
    if page_num <= 10:
        continue
    for pattern in data_patterns:
        for m in re.finditer(pattern, text):
            snippet = m.group(0).strip()
            if len(snippet) < 6:
                continue
            # Must contain at least one digit
            if not re.search(r'\d', snippet):
                continue
            cn_or_d = len(re.findall(r'[\u4e00-\u9fff0-9]', snippet))
            if cn_or_d < 10:
                continue
            key_data.append({"page": page_num, "text": snippet[:250]})

seen = set()
uniq = []
for d in key_data:
    k = (d["page"], d["text"][:50])
    if k not in seen:
        seen.add(k)
        uniq.append(d)
key_data = sorted(uniq, key=lambda x: x["page"])

# ============================================================
# 3. CORE THEORETICAL PROPOSITIONS (核心理论命题)
# ============================================================
prop_triggers = [
    '我认为', '本书提出', '本书的基本', '本书的核',
    '我的论点是', '我的观点是', '我的核心', '我的基本',
    '基本矛盾是', '核心机制是', '核心问题是', '基本问题是',
    '本章提出', '在此提出', '我在此提出', '我提出',
    '提出一个', '提出了一个', '提出"控制权"',
    '这一章', '本章中',
    '理论框架', '分析框架', '理论模型',
    '核心观点', '基本观点', '基本思路',
    '总的来看', '简而言之', '简言之',
    '由此可以', '因此可以', '这表明', '这说明',
    '笔者的', '笔者的观', '笔者的论',
    '这一矛盾', '这一机制', '这一逻辑',
    '我的基本判断', '我的判断',
]

propositions = []
for p in pages:
    text = clean(p["text"])
    page_num = p["page"]
    if page_num <= 10:
        continue
    
    # Split into sentences
    sentences = re.split(r'(?<=[。！？\n])', text)
    
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 20:
            continue
        matched_trigger = None
        for trig in prop_triggers:
            if trig in sent[:15]:  # trigger must be near start
                matched_trigger = trig
                break
        if not matched_trigger:
            continue
        
        # Grab extended context if sentence is short
        if len(sent) < 50:
            idx = text.find(sent[:20])
            if idx >= 0:
                extended = text[idx:idx+300]
            else:
                extended = sent
        else:
            extended = sent
        
        cn = len(re.findall(r'[\u4e00-\u9fff]', extended))
        if cn < 15:
            continue
        
        propositions.append({
            "page": page_num,
            "text": extended[:300],
            "trigger": matched_trigger,
        })

seen = set()
uniq = []
for prop in propositions:
    k = (prop["page"], prop["text"][:50])
    if k not in seen:
        seen.add(k)
        uniq.append(prop)
propositions = sorted(uniq, key=lambda x: x["page"])

# ============================================================
# 5. KEY CASES (关键案例)
# ============================================================
# Tighter: require SPECIFIC place names or NAMED events
# Known place abbreviations in the book: FS镇, etc.
case_patterns = [
    # Specific place + event: 在XX县/市/镇/村/公社...发生了/推行了/实施了
    r'在[\u4e00-\u9fff]{1,6}(?:县|市|镇|村|乡|区|省|地区|公社|大队)[^。\n]{0,80}(?:发生|推行|实施|出现|开展|爆发|进行|启动|出台)[^。\n]{5,100}',
    # Named events in quotes
    r'[""「「]([^""」」]{2,20})(?:事件|运动|改革|案件|工程|政策|运动|风波|办法|模式|现象|制度)[""」」]',
    # Major historical events
    r'(?:大跃进|文化大革命|改革开放|大寨运动|人民公社|包产到户|退耕还林|"村村通"|村民选举|废除农业税|科学发展观|群众路线教育|整风运动|反右运动|四清运动|三反五反|"叫魂"|"大生产"|"大鸣大放")[^。\n]{5,120}',
    # 以...为例 with specific reference
    r'以[\u4e00-\u9fff]{2,15}(?:为例|为例子|的案例|的调查|的田野|的观察)[^。\n]{5,100}',
    # 案例/个案 + specific description
    r'(?:案例|个案|实例)[^。\n]{0,10}(?:表明|说明|显示|表明|展示)[^。\n]{10,120}',
    # Specific township/village fieldwork references
    r'(?:FS镇|南方某镇|北方某镇|某县|某市|某乡|某村|这个乡镇|这个镇|这个县|调研地|田野点)[^。\n]{10,120}',
    # Story/narrative markers
    r'(?:故事|经历|插曲|片段)[^。\n]{0,5}(?:是|中|里)[^。\n]{10,100}',
    # Specific person + official role + action
    r'[\u4e00-\u9fff]{2,4}(?:书记|市长|县长|镇长|乡长|村长|主任|局长)[^。\n]{0,5}(?:说|认为|表示|告诉|回忆|回忆道|说道|指出)[^。\n]{10,100}',
]

cases = []
for p in pages:
    text = clean(p["text"])
    page_num = p["page"]
    if page_num <= 10:
        continue
    for pattern in case_patterns:
        for m in re.finditer(pattern, text):
            snippet = m.group(0).strip()
            if len(snippet) < 12:
                continue
            cn = len(re.findall(r'[\u4e00-\u9fff]', snippet))
            if cn < 10:
                continue
            cases.append({"page": page_num, "text": snippet[:250]})

seen = set()
uniq = []
for c in cases:
    k = (c["page"], c["text"][:50])
    if k not in seen:
        seen.add(k)
        uniq.append(c)
cases = sorted(uniq, key=lambda x: x["page"])

# ============================================================
# WRITE OUTPUT
# ============================================================
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
    out.write("# 《中国国家治理的制度逻辑》——深度知识提取\n\n")
    out.write("> **作者**：周雪光\n")
    out.write(f"> **来源文件**：{data['filename']}\n")
    out.write(f"> **总页数**：{data['pages']}  |  **总字数**：{data['total_chars']:,}\n")
    out.write(f"> **提取日期**：2026-07-13\n")
    out.write(f"> **提取方法**：Python 正则表达式自动提取\n\n")
    out.write("---\n\n")

    # ---- Section 4: Chapter Structure (put first for navigation) ----
    out.write("## 一、章节结构\n\n")
    
    # Units
    units = [e for e in toc_entries if e[0] == "unit"]
    chapters = [e for e in toc_entries if e[0] == "chapter"]
    
    out.write("### 单元（Part）\n\n")
    for _, num, title in units:
        out.write(f"- **第{num}单元** {title}\n")
    
    out.write("\n### 章（Chapter）\n\n")
    out.write("| 章号 | 标题 | 正文起始页 |\n|------|------|------------|\n")
    for _, num, title in chapters:
        body_page = chapter_pages.get(num, (None, None))[0]
        page_str = str(body_page) if body_page else "—"
        out.write(f"| 第{num}章 | {title} | {page_str} |\n")
    
    out.write("\n### 小节标题（从目录提取）\n\n")
    for i, title in enumerate(section_titles_from_toc):
        out.write(f"{i+1}. {title}\n")

    out.write("\n\n---\n\n")

    # ---- Section 1: Definitions ----
    out.write("## 二、定义性陈述\n\n")
    out.write(f"> 共提取 **{len(definitions)}** 条定义性陈述（按页码排序）。\n\n")
    current_page = None
    for d in definitions:
        if d["page"] != current_page:
            current_page = d["page"]
            out.write(f"\n### 📄 第 {d['page']} 页\n\n")
        out.write(f"- {d['text']}\n")

    out.write("\n\n---\n\n")

    # ---- Section 2: Key Data ----
    out.write("## 三、关键数据\n\n")
    out.write(f"> 共提取 **{len(key_data)}** 条关键数据（按页码排序）。\n\n")
    current_page = None
    for d in key_data:
        if d["page"] != current_page:
            current_page = d["page"]
            out.write(f"\n### 📄 第 {d['page']} 页\n\n")
        out.write(f"- {d['text']}\n")

    out.write("\n\n---\n\n")

    # ---- Section 3: Core Propositions ----
    out.write("## 四、核心理论命题\n\n")
    out.write(f"> 共提取 **{len(propositions)}** 条核心理论命题（按页码排序）。\n\n")
    current_page = None
    for prop in propositions:
        if prop["page"] != current_page:
            current_page = prop["page"]
            out.write(f"\n### 📄 第 {prop['page']} 页\n\n")
        out.write(f"- {prop['text']}\n")

    out.write("\n\n---\n\n")

    # ---- Section 5: Key Cases ----
    out.write("## 五、关键案例\n\n")
    out.write(f"> 共提取 **{len(cases)}** 条案例/故事（按页码排序）。\n\n")
    current_page = None
    for c in cases:
        if c["page"] != current_page:
            current_page = c["page"]
            out.write(f"\n### 📄 第 {c['page']} 页\n\n")
        out.write(f"- {c['text']}\n")

    out.write("\n\n---\n\n")

    # ---- Summary ----
    out.write("## 提取统计\n\n")
    out.write("| 类别 | 数量 |\n|------|------|\n")
    out.write(f"| 章节结构（单元+章+小节） | {len(units)} 单元 + {len(chapters)} 章 + {len(section_titles_from_toc)} 小节 |\n")
    out.write(f"| 定义性陈述 | {len(definitions)} |\n")
    out.write(f"| 关键数据 | {len(key_data)} |\n")
    out.write(f"| 核心理论命题 | {len(propositions)} |\n")
    out.write(f"| 关键案例 | {len(cases)} |\n")
    total = len(definitions) + len(key_data) + len(propositions) + len(cases)
    out.write(f"| **知识条目合计** | **{total}** |\n")

print(f"✅ 提取完成！\n")
print(f"  章节结构: {len(units)} 单元 + {len(chapters)} 章 + {len(section_titles_from_toc)} 小节")
print(f"  定义性陈述: {len(definitions)}")
print(f"  关键数据:   {len(key_data)}")
print(f"  理论命题:   {len(propositions)}")
print(f"  关键案例:   {len(cases)}")
print(f"  知识条目合计: {total}")
print(f"\n📁 输出文件: {OUTPUT_PATH}")
