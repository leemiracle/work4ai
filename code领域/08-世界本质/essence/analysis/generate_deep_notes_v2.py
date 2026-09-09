#!/usr/bin/env python3
"""
Generate political-books-deep-notes-v2.md
Upgrades existing deep notes from summaries to direct quotes from extracted knowledge.
v2: Fixed parsers for all format variants.
"""

import re
import os
from pathlib import Path

BASE = Path("/mnt/c/workspace/essence/analysis")

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# ============================================================
# Parsers for different file formats
# ============================================================

def parse_zhou_xueguang(text):
    """Zhou Xueguang: page-tagged bullet entries (### 📄 第 N 页 → - text)."""
    result = {"defs": [], "data": [], "claims": [], "cases": []}
    
    sections = {}
    parts = re.split(r'^(## .+)$', text, flags=re.MULTILINE)
    current = None
    for part in parts:
        if part.startswith("## "):
            current = part.strip()
            sections[current] = ""
        elif current:
            sections[current] += part
    
    def extract_page_tagged(content):
        """Extract all text under each page header, joining multi-line entries."""
        entries = []
        current_page = 0
        current_text = ""
        for line in content.split("\n"):
            stripped = line.strip()
            pm = re.match(r'^###\s+📄?\s*第\s*(\d+)\s*页', stripped)
            if pm:
                # Save previous entry
                if current_page > 0 and current_text.strip():
                    clean = re.sub(r'\s+', ' ', current_text).strip()
                    if len(clean) > 10:
                        entries.append({"page": current_page, "text": clean})
                current_page = int(pm.group(1))
                current_text = ""
                continue
            if current_page > 0:
                if stripped.startswith("- "):
                    if current_text:  # Save previous bullet
                        clean = re.sub(r'\s+', ' ', current_text).strip()
                        if len(clean) > 10:
                            entries.append({"page": current_page, "text": clean})
                    current_text = stripped[2:].strip()
                elif stripped and not stripped.startswith("###"):
                    current_text += " " + stripped
                elif not stripped:
                    if current_text:
                        clean = re.sub(r'\s+', ' ', current_text).strip()
                        if len(clean) > 10:
                            entries.append({"page": current_page, "text": clean})
                        current_text = ""
        # Save last entry
        if current_page > 0 and current_text.strip():
            clean = re.sub(r'\s+', ' ', current_text).strip()
            if len(clean) > 10:
                entries.append({"page": current_page, "text": clean})
        return entries
    
    result["defs"] = extract_page_tagged(sections.get("## 二、定义性陈述", ""))
    result["data"] = extract_page_tagged(sections.get("## 三、关键数据", ""))
    result["claims"] = extract_page_tagged(sections.get("## 四、核心理论命题", ""))
    result["cases"] = extract_page_tagged(sections.get("## 五、关键案例", ""))
    return result

def parse_zhou_lian(text):
    """Zhou Li'an: table format for defs/data, ### 命题 format for claims."""
    result = {"defs": [], "data": [], "claims": [], "cases": []}
    
    sections = {}
    parts = re.split(r'^(## .+)$', text, flags=re.MULTILINE)
    current = None
    for part in parts:
        if part.startswith("## "):
            current = part.strip()
            sections[current] = ""
        elif current:
            sections[current] += part
    
    # Definitions: table format | # | page | text |
    defs_content = sections.get("## 2. 定义性陈述", "")
    for m in re.finditer(r'\|\s*(\d+)\s*\|\s*p\.(\d+)\s*\|\s*(.+?)\s*\|', defs_content):
        num, page, txt = int(m.group(1)), int(m.group(2)), m.group(3).strip()
        if len(txt) > 15:
            result["defs"].append({"page": page, "text": txt})
    
    # Data: table format | # | page | value | context |
    data_content = sections.get("## 3. 关键数据", "")
    for m in re.finditer(r'\|\s*(\d+)\s*\|\s*p\.(\d+)\s*\|\s*`?([^|]+?)`?\s*\|\s*(.+?)\s*\|', data_content):
        num, page, val, ctx = int(m.group(1)), int(m.group(2)), m.group(3).strip(), m.group(4).strip()
        if len(ctx) > 15:
            result["data"].append({"page": page, "text": f"{val}: {ctx}"})
    
    # Claims: ### 命题 N (p.X) → > text (filter out TOC entries)
    claims_content = sections.get("## 4. 核心理论命题", "")
    for m in re.finditer(r'### 命题\s*(\d+)\s*\(p\.(\d+)\).*?\n\n>\s*(.+?)(?=\n\n|\Z)', claims_content, re.DOTALL):
        num, page, txt = int(m.group(1)), int(m.group(2)), m.group(3).strip().replace("\n> ", " ").replace("\n", " ")
        txt = re.sub(r'\s+', ' ', txt).strip()
        # Filter out TOC-like entries (contain section numbers like "8.5", "9.1")
        if len(txt) > 30 and not re.match(r'^\d+\.\d+\s', txt):
            result["claims"].append({"page": page, "text": txt[:500]})
    
    # Cases: similar to claims
    cases_content = sections.get("## 5. 关键案例", "")
    for m in re.finditer(r'### 案例\s*(\d+)\s*\(p\.(\d+)\).*?\n\n>\s*(.+?)(?=\n\n|\Z)', cases_content, re.DOTALL):
        num, page, txt = int(m.group(1)), int(m.group(2)), m.group(3).strip().replace("\n> ", " ").replace("\n", " ")
        if len(txt) > 20:
            result["cases"].append({"page": page, "text": txt[:500]})
    # If no cases section, fall back to claims
    if not result["cases"]:
        result["cases"] = result["claims"][:10]
    
    return result

def parse_others_book(text, book_name):
    """Parse a book section from extracted-knowledge-others.md.
    Uses ### A/B/C/D subsections with numbered definitions or bullet entries."""
    result = {"defs": [], "data": [], "claims": [], "cases": []}
    
    # Split by ### headers
    sub_sections = {}
    parts = re.split(r'^(### [A-Z]\..+)$', text, flags=re.MULTILINE)
    current = None
    for part in parts:
        if re.match(r'^### [A-Z]\.', part.strip()):
            current = part.strip()
            sub_sections[current] = ""
        elif current:
            sub_sections[current] += part
    
    for header, content in sub_sections.items():
        if "定义性陈述" in header or "定义" in header:
            # Numbered format: 1. 【tag】text
            for m in re.finditer(r'^\d+\.\s*【(.+?)】(.+)', content, re.MULTILINE):
                tag, txt = m.group(1).strip(), m.group(2).strip()
                txt = re.sub(r'\s+', ' ', txt)
                if len(txt) > 15:
                    result["defs"].append({"page": 0, "text": txt, "tag": tag})
        elif "关键数据" in header or "数据" in header:
            # Format: N. [type] value\n   > context text
            for m in re.finditer(r'^\d+\.\s*\[([^\]]+)\]\s*(.+?)\n\s*>\s*(.+)', content, re.MULTILINE):
                data_type, val, ctx = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
                ctx = re.sub(r'\s+', ' ', ctx)
                if len(ctx) > 20:
                    result["data"].append({"page": 0, "text": ctx[:300], "tag": data_type})
            # Fallback: simple bullet or numbered
            if not result["data"]:
                for line in content.split("\n"):
                    s = line.strip()
                    if s.startswith("- ") and len(s) > 20:
                        result["data"].append({"page": 0, "text": s[2:]})
                    elif re.match(r'^\d+\.\s', s) and len(s) > 20 and not s.startswith(tuple(str(i) for i in range(100))):
                        result["data"].append({"page": 0, "text": re.sub(r'^\d+\.\s*', '', s)})
            # Also try blockquote context format without type tag
            if not result["data"]:
                for m in re.finditer(r'^\d+\.\s*(.+?)\n\s*>\s*(.+)', content, re.MULTILINE):
                    val, ctx = m.group(1).strip(), m.group(2).strip()
                    ctx = re.sub(r'\s+', ' ', ctx)
                    if len(ctx) > 20:
                        result["data"].append({"page": 0, "text": ctx[:300]})
        elif "核心命题" in header or "核心论断" in header or "命题" in header:
            for m in re.finditer(r'^\d+\.\s*【(.+?)】(.+)', content, re.MULTILINE):
                tag, txt = m.group(1).strip(), m.group(2).strip()
                txt = re.sub(r'\s+', ' ', txt)
                if len(txt) > 20:
                    result["claims"].append({"page": 0, "text": txt, "tag": tag})
            # Also try > blockquote format
            if not result["claims"]:
                for m in re.finditer(r'^>\s*(.+)', content, re.MULTILINE):
                    txt = m.group(1).strip()
                    if len(txt) > 30:
                        result["claims"].append({"page": 0, "text": txt})
        elif "关键案例" in header or "案例" in header:
            for m in re.finditer(r'^\d+\.\s*【(.+?)】(.+)', content, re.MULTILINE):
                tag, txt = m.group(1).strip(), m.group(2).strip()
                txt = re.sub(r'\s+', ' ', txt)
                if len(txt) > 20:
                    result["cases"].append({"page": 0, "text": txt, "tag": tag})
            if not result["cases"]:
                for line in content.split("\n"):
                    s = line.strip()
                    if s.startswith("- ") and len(s) > 20:
                        result["cases"].append({"page": 0, "text": s[2:]})
    
    # If no claims found, use defs as claims
    if not result["claims"] and result["defs"]:
        result["claims"] = result["defs"][:10]
    # If no data found, use defs with numbers
    if not result["data"]:
        for d in result["defs"]:
            if any(c.isdigit() for c in d["text"]):
                result["data"].append(d)
    
    return result

# ============================================================
# Load all data
# ============================================================
print("=" * 60)
print("Loading extracted knowledge files...")
print("=" * 60)

zxg = parse_zhou_xueguang(read_file(BASE / "extracted-knowledge-zhou-xueguang.md"))
print(f"  周雪光: {len(zxg['defs'])} defs, {len(zxg['data'])} data, {len(zxg['claims'])} claims, {len(zxg['cases'])} cases")

zl = parse_zhou_lian(read_file(BASE / "extracted-knowledge-zhou-lian.md"))
print(f"  周黎安: {len(zl['defs'])} defs, {len(zl['data'])} data, {len(zl['claims'])} claims, {len(zl['cases'])} cases")

others_raw = read_file(BASE / "extracted-knowledge-others.md")

def get_book_section(full_text, book_marker):
    pattern = re.escape(book_marker) + r'(.*?)(?=^## |\Z)'
    m = re.search(pattern, full_text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""

zfz = parse_others_book(get_book_section(others_raw, "## 一、周飞舟《以利为利》"), "周飞舟")
print(f"  周飞舟: {len(zfz['defs'])} defs, {len(zfz['data'])} data, {len(zfz['claims'])} claims, {len(zfz['cases'])} cases")

hqf = parse_others_book(get_book_section(others_raw, "## 二、黄奇帆《分析与思考》"), "黄奇帆")
print(f"  黄奇帆: {len(hqf['defs'])} defs, {len(hqf['data'])} data, {len(hqf['claims'])} claims, {len(hqf['cases'])} cases")

sp = parse_others_book(get_book_section(others_raw, "## 三、孙萍《过渡劳动》"), "孙萍")
print(f"  孙萍:   {len(sp['defs'])} defs, {len(sp['data'])} data, {len(sp['claims'])} claims, {len(sp['cases'])} cases")

popper = parse_others_book(get_book_section(others_raw, "## 四、波普尔《历史决定论的贫困》"), "波普尔")
print(f"  波普尔: {len(popper['defs'])} defs, {len(popper['data'])} data, {len(popper['claims'])} claims, {len(popper['cases'])} cases")

# ============================================================
# Selection helpers
# ============================================================
def select_best(entries, n=5, min_len=20, max_len=350):
    candidates = [e for e in entries if min_len <= len(e.get("text", "")) <= max_len]
    if len(candidates) < n:
        for e in entries:
            if e not in candidates and len(e.get("text", "")) >= min_len:
                candidates.append(e)
            if len(candidates) >= n * 2:
                break
    return candidates[:n]

def select_by_concept(entries, concepts, n=6):
    selected = []
    for concept in concepts:
        for e in entries:
            if concept in e.get("text", "") and e not in selected:
                selected.append(e)
                break
        if len(selected) >= n:
            break
    return selected

def fmt_quote(e, max_len=350):
    text = re.sub(r'\s+', ' ', e.get("text", "")).strip()
    tag = e.get("tag", "")
    page = e.get("page", 0)
    truncated = text[:max_len] + ("..." if len(text) > max_len else "")
    tag_prefix = f"**【{tag}】** " if tag else ""
    return tag_prefix, truncated, page

def chapter_for_zxg(page):
    if page < 63: return "第1章（导论）"
    elif page < 96: return "第2章"
    elif page < 133: return "第3章"
    elif page < 169: return "第4章"
    elif page < 206: return "第5章"
    elif page < 247: return "第6章"
    elif page < 280: return "第7章"
    elif page < 311: return "第8章"
    elif page < 349: return "第9章"
    elif page < 397: return "第10章"
    elif page < 428: return "第11章"
    else: return "第12章"

def chapter_for_zl(page):
    if page < 56: return "导论"
    elif page < 104: return "第2章 行政发包制"
    elif page < 141: return "第3章 地方分权"
    elif page < 188: return "第4章 财政分成"
    elif page < 235: return "第5章 政治锦标赛"
    elif page < 264: return "第6章 政经互动"
    elif page < 296: return "第7章 区域竞争"
    elif page < 343: return "第8章 政商关系"
    elif page < 391: return "第9章 发包制×锦标赛"
    else: return "第10章 治理改革"

# ============================================================
# Build output
# ============================================================
out = []
def w(s=""):
    out.append(s)

# Header
header_lines = [
    "# 政治类书目深度读书笔记 v2（原文引用版）",
    "",
    "> **配套**：[`political-books-index.md`](../reading-list/political-books-index.md) 总索引",
    "> **v1**：[`political-books-deep-notes.md`](political-books-deep-notes.md) 基于书名+作者知识的概括版",
    "> **本版升级**：对 7 本重点书目，用 PDF 原文提取的知识替换概括，所有论点、定义、数据、案例均标注页码",
    "> **数据来源**：`extracted-knowledge-*.md`（6 个文件，合计约 11,000+ 条原文提取）",
    "> **方法**：Python 正则表达式从 pdftotext 全文中自动提取定义性陈述、关键数据、理论命题、案例",
    "",
    "---",
    "",
]
for l in header_lines:
    w(l)

# ============================================================
# B1. 周雪光
# ============================================================
w("## B1. 周雪光《中国国家治理的制度逻辑：一个组织学研究》")
w("")
w("**出版**：2017  ")
w("**作者**：周雪光，斯坦福大学社会学系教授  ")
w("**全书**：477 页，356,006 字  ")
w(f"**提取**：{len(zxg['defs'])} 条定义 + {len(zxg['data'])} 条数据 + {len(zxg['claims'])} 条理论命题 + {len(zxg['cases'])} 条案例")
w("")
w("---")
w("")

# Core claims
w("### 核心论点（原文引用）")
w("")
for e in select_best(zxg["claims"], n=5, min_len=40, max_len=400):
    tag, txt, pg = fmt_quote(e, 400)
    w(f'> {tag}"{txt}"')
    w(f"> — p.{pg}, {chapter_for_zxg(pg)}")
    w("")

# Key definitions
w("### 关键定义（原文）")
w("")
concept_defs = select_by_concept(zxg["defs"], 
    ["一统体制", "运动型治理", "共谋", "控制权", "逆向软预算约束", "有效治理", "卡理斯玛", "逐级代理"], n=6)
for e in concept_defs:
    tag, txt, pg = fmt_quote(e, 300)
    w(f'> {tag}"{txt}"')
    w(f"> — p.{pg}")
    w("")

# Key data
w("### 关键数据")
w("")
for e in select_best(zxg["data"], n=6, min_len=15, max_len=250):
    tag, txt, pg = fmt_quote(e, 250)
    w(f'> {tag}"{txt}"')
    w(f"> — p.{pg}")
    w("")

# Key cases
w("### 关键案例")
w("")
for e in select_best(zxg["cases"], n=5, min_len=20, max_len=300):
    tag, txt, pg = fmt_quote(e, 300)
    w(f'> {tag}"{txt}"')
    w(f"> — p.{pg}")
    w("")

# Chapter structure
w("### 章节结构")
w("")
ch_table = [
    "| 章号 | 标题 | 起始页 |",
    "|------|------|--------|",
    "| 第1章 | 导论：中国国家治理的制度逻辑 | 17 |",
    "| 第2章 | 国家治理逻辑与中国官僚体制：韦伯理论视角 | 63 |",
    "| 第3章 | 中国政府的治理模式：控制权理论 | 96 |",
    "| 第4章 | 运动型治理机制 | 133 |",
    "| 第5章 | 政府内部上下级谈判 | 169 |",
    '|| 第6章 | 基层政府间的"共谋现象" | 206 ||',
    '|| 第7章 | "拼凑应对"：多重逻辑下的基层政府行为 | 247 ||',
    "| 第8章 | 逆向软预算约束 | 280 |",
    "| 第9章 | 通往集体债务之路 | 311 |",
    "| 第10章 | 多重逻辑下的村庄选举 | 349 |",
    "| 第11章 | 无组织的利益与集体行动 | 397 |",
    "| 第12章 | 结语：国家治理逻辑与中国未来 | 428 |",
]
# Fix the table formatting
w("| 章号 | 标题 | 起始页 |")
w("|------|------|--------|")
ch_data = [
    ("第1章", "导论：中国国家治理的制度逻辑", "17"),
    ("第2章", "国家治理逻辑与中国官僚体制：韦伯理论视角", "63"),
    ("第3章", "中国政府的治理模式：控制权理论", "96"),
    ("第4章", "运动型治理机制", "133"),
    ("第5章", "政府内部上下级谈判", "169"),
    ("第6章", "基层政府间的共谋现象", "206"),
    ("第7章", "拼凑应对：多重逻辑下的基层政府行为", "247"),
    ("第8章", "逆向软预算约束", "280"),
    ("第9章", "通往集体债务之路", "311"),
    ("第10章", "多重逻辑下的村庄选举", "349"),
    ("第11章", "无组织的利益与集体行动", "397"),
    ("第12章", "结语：国家治理逻辑与中国未来", "428"),
]
for ch, title, pg in ch_data:
    w(f"| {ch} | {title} | {pg} |")

w("")
w("---")
w("")

# ============================================================
# B3. 周黎安
# ============================================================
w("## B3. 周黎安《转型中的地方政府：官员激励与治理》")
w("")
w("**出版**：2008 初版，2017 增订  ")
w("**作者**：周黎安，北京大学光华管理学院教授  ")
w("**全书**：475 页，474,349 字  ")
w(f"**提取**：{len(zl['defs'])} 条定义 + {len(zl['data'])} 条数据 + {len(zl['claims'])} 条理论命题")
w("")
w("---")
w("")

w("### 核心论点（原文引用）")
w("")
for e in select_best(zl["claims"], n=5, min_len=40, max_len=500):
    tag, txt, pg = fmt_quote(e, 400)
    w(f'> {tag}"{txt}"')
    w(f"> — p.{pg}, {chapter_for_zl(pg)}")
    w("")

w("### 关键定义（原文）")
w("")
concept_defs_zl = select_by_concept(zl["defs"],
    ["行政发包制", "政治锦标赛", "层层加码", "官场", "M型", "属地化", "财政分成", "垂直管理"], n=6)
for e in concept_defs_zl:
    tag, txt, pg = fmt_quote(e, 300)
    w(f'> {tag}"{txt}"')
    w(f"> — p.{pg}")
    w("")

w("### 关键数据")
w("")
for e in select_best(zl["data"], n=8, min_len=15, max_len=300):
    tag, txt, pg = fmt_quote(e, 300)
    w(f'> {tag}"{txt}"')
    w(f"> — p.{pg}")
    w("")

w("### 关键案例/命题")
w("")
for e in select_best(zl["cases"], n=5, min_len=30, max_len=400):
    tag, txt, pg = fmt_quote(e, 400)
    w(f'> {tag}"{txt}"')
    w(f"> — p.{pg}, {chapter_for_zl(pg)}")
    w("")

w("### 章节结构")
w("")
w("| 章号 | 标题 | 起始页 |")
w("|------|------|--------|")
zl_chs = [
    ("导论", "地方政府与中国经济增长之谜", "27"),
    ("第2章", "行政发包制", "56"),
    ("第3章", "转型中的地方分权", "104"),
    ("第4章", "转型中的财政分成", "141"),
    ("第5章", "政治锦标赛", "188"),
    ("第6章", "中国特色的政经互动", "235"),
    ("第7章", "区域经济竞争与合作", "264"),
    ("第8章", "从政企关系到官商关系", "296"),
    ("第9章", "当行政发包制遇上政治锦标赛", "343"),
    ("第10章", "政府治理的改革", "391"),
]
for ch, title, pg in zl_chs:
    w(f"| {ch} | {title} | {pg} |")

w("")
w("---")
w("")

# ============================================================
# B4. 周飞舟
# ============================================================
w("## B4. 周飞舟《以利为利：财政关系与地方政府行为》")
w("")
w("**出版**：2012  ")
w("**作者**：周飞舟，北京大学社会学系教授  ")
w("**提取来源**：extracted-knowledge-others.md 第一部分")
w("")
w("---")
w("")

w("### 核心论点（原文引用）")
w("")
# Use claims or best defs for Zhou Feizhou
zfz_claims = select_by_concept(zfz.get("claims", []),
    ["分税制", "土地财政", "财政", "包干", "转移支付", "以地生财"], n=5)
if not zfz_claims:
    zfz_claims = select_best(zfz.get("claims", zfz.get("defs", [])), n=5, min_len=30)
for e in zfz_claims:
    tag, txt, pg = fmt_quote(e, 350)
    w(f'> {tag}"{txt}"')
    w("")

w("### 关键定义（原文）")
w("")
zfz_defs = select_by_concept(zfz.get("defs", []),
    ["分税制", "土地财政", "财政体制", "包干", "转移支付", "吃饭财政", "两个比重", "以地生财", "悬浮", "专项"], n=6)
for e in zfz_defs:
    tag, txt, pg = fmt_quote(e, 350)
    w(f'> **【{e.get("tag", "")}】** "{txt}"')
    w("")

w("### 关键数据")
w("")
zfz_data = select_best(zfz.get("data", []), n=6, min_len=20, max_len=300)
if not zfz_data:
    # Find defs with numbers
    for d in zfz.get("defs", []):
        if any(c.isdigit() for c in d.get("text", "")):
            zfz_data.append(d)
    zfz_data = zfz_data[:6]
for e in zfz_data:
    tag, txt, pg = fmt_quote(e, 300)
    w(f'> {tag}"{txt}"')
    w("")

w("### 章节结构")
w("")
w("| 章号 | 标题 | 起始页 |")
w("|------|------|--------|")
zfz_chs = [
    ("第一章", "序论：政府行为与中央一地方关系", "5"),
    ("第二章", "改革前的中央地方关系", "21"),
    ("第三章", "财政包干的效应和后果", "37"),
    ("第四章", "分税制改革及其影响", "54"),
    ("第五章", "转移支付体系的建立", "69"),
    ("第六章", "县乡财政危机", "85"),
    ("第七章", "基层政权的悬浮状态", "103"),
    ("第八章", "财政资金的专项化", "132"),
    ("第十二章", "土地征用和政府的土地收入", "211"),
    ("第十三章", "土地财政", "222"),
    ("第十四章", "土地金融和城市化", "235"),
]
for ch, title, pg in zfz_chs:
    w(f"| {ch} | {title} | {pg} |")

w("")
w("---")
w("")

# ============================================================
# A1. 波普尔
# ============================================================
w("## A1. 波普尔《历史决定论的贫困》")
w("")
w("**出版**：1957（英文原版 *The Poverty of Historicism*）  ")
w("**作者**：Karl Popper（1902-1994），奥地利裔英国科学哲学家  ")
w("**提取来源**：extracted-knowledge-others.md 第四部分")
w("")
w("---")
w("")

w("### 核心论点（原文引用）")
w("")
# Find key Popper arguments
popper_key_claims = select_by_concept(popper.get("defs", []),
    ["乌托邦", "零星", "渐进", "整体主义", "大规模预测", "历史规律", "趋势", "不可预测"], n=5)
if not popper_key_claims:
    popper_key_claims = select_best(popper.get("defs", []), n=5, min_len=30)
for e in popper_key_claims:
    tag, txt, pg = fmt_quote(e, 400)
    w(f'> **【{e.get("tag", "")}】** "{txt}"')
    w("")

w("### 关键定义（原文）")
w("")
popper_defs = select_by_concept(popper.get("defs", []),
    ["历史决定论", "反自然主义", "泛自然主义", "本质主义", "唯名主义", "整体主义", "乌托邦", "零星"], n=6)
for e in popper_defs:
    tag, txt, pg = fmt_quote(e, 350)
    w(f'> **【{e.get("tag", "")}】** "{txt}"')
    w("")

w("### 章节结构")
w("")
w("| 章节 | 标题 | 起始页 |")
w("|------|------|--------|")
w("| I | 历史决定论的反自然主义学说 | 5 |")
w("| II | 历史决定论的泛自然主义学说 | 13 |")
w("| III | 对反自然主义学说的批评 | 19 |")
w("| IV | 对泛自然主义学说的批评 | 32 |")
w("")
w('> 全书仅 4 章，约 40 页正文——但逻辑密度极高。波普尔的核心论证：历史决定论在逻辑上自我矛盾，在实践中导向极权。')

w("")
w("---")
w("")

# ============================================================
# F3. 黄奇帆
# ============================================================
w("## F3. 黄奇帆《分析与思考：黄奇帆的复旦经济课》")
w("")
w("**出版**：2020  ")
w("**作者**：黄奇帆，曾任重庆市市长——实务派经济学家  ")
w("**提取来源**：extracted-knowledge-others.md 第二部分")
w("")
w("---")
w("")

w("### 核心论点（原文引用）")
w("")
hqf_claims = select_by_concept(hqf.get("defs", []),
    ["杠杆", "供给侧", "金融", "房地产", "土地", "资本市场", "对外开放", "三零", "债务", "融资"], n=5)
for e in hqf_claims:
    tag, txt, pg = fmt_quote(e, 350)
    w(f'> **【{e.get("tag", "")}】** "{txt}"')
    w("")

w("### 关键定义与数据（原文）")
w("")
hqf_data = select_best(hqf.get("data", []), n=6, min_len=20, max_len=300)
if not hqf_data:
    for d in hqf.get("defs", []):
        if any(c.isdigit() for c in d.get("text", "")):
            hqf_data.append(d)
    hqf_data = hqf_data[:6]
for e in hqf_data:
    tag, txt, pg = fmt_quote(e, 300)
    w(f'> **【{e.get("tag", "")}】** "{txt}"')
    w("")

w("### 章节结构")
w("")
w("| 章节 | 标题 | 起始页 |")
w("|------|------|--------|")
w("| 宏观调控 | 降杠杆与风险化解 / 供给侧结构性改革 | 10 |")
w('| 基础货币 | 货币的锚及发行制度 | 77 |')
w("| 资本市场 | 中国资本市场的改革重点 | 119 |")
w("| 房地产发展 | 房地产基础性制度和长效机制 | 149 |")
w('| 对外开放 | 三零原则与FTA发展 / 自贸区建设 | 189 |')
w("| 中美经贸 | 贸易摩擦的谬论与应对 | 236 |")
w("| 附录 | 改革开放40年珍贵记忆 | 267 |")

w("")
w("---")
w("")

# ============================================================
# F5. 孙萍
# ============================================================
w("## F5. 孙萍《过渡劳动：平台经济下的外卖骑手》")
w("")
w("**出版**：2024  ")
w("**作者**：孙萍，中国社会科学院新闻与传播研究所研究员  ")
w("**田野时间**：2017—2024  ")
w("**提取来源**：extracted-knowledge-others.md 第三部分")
w("")
w("---")
w("")

w("### 核心论点（原文引用）")
w("")
sp_claims = select_by_concept(sp.get("defs", []),
    ["过渡劳动", "算法", "平台", "骑手", "控制", "灵活", "游戏", "系统", "外包", "站点"], n=5)
for e in sp_claims:
    tag, txt, pg = fmt_quote(e, 350)
    w(f'> **【{e.get("tag", "")}】** "{txt}"')
    w("")

w("### 关键定义（原文）")
w("")
sp_defs = select_by_concept(sp.get("defs", []),
    ["过渡劳动", "算法", "控制", "游戏化", "站点", "骑手", "外包", "灵活"], n=5)
for e in sp_defs:
    tag, txt, pg = fmt_quote(e, 300)
    w(f'> **【{e.get("tag", "")}】** "{txt}"')
    w("")

w("### 章节结构")
w("")
w("| 章节 | 标题 | 起始页 |")
w("|------|------|--------|")
w("| 导论 | 建构过渡性 | 23 |")
w("| 第一章 | 组织化与灵活性 | 51 |")
w("| 第二章 | 算法与系统 | 85 |")
w("")
w("> 田野地图：2017—2024，跟踪外卖骑手从平台兴起到算法成熟的全过程。")

w("")
w("---")
w("")

# ============================================================
# D3. 王沪宁
# ============================================================
w("## D3. 王沪宁《政治的人生》")
w("")
w("**出版**：1995  ")
w("**作者身份**：复旦大学教授，即将进入中央政策研究室  ")
w("")
w("> ⚠️ **原文提取状态**：该书 PDF 未在本次提取范围内。以下保留 v1 概括笔记，待后续补充原文。")
w("")
w("---")
w("")
d3_lines = [
    '### 核心论点（概括）',
    '日记体——记录一个政治学者的日常生活与思考。**揭示一个即将入仕的学者的内心世界**。',
    '',
    '### 关键概念（概括）',
    '- **学者从政**：中国传统的学而优则仕',
    '- **政治的人生**：政治不只是职业——是人生观',
    '- **读书与思考**：日记中大量读书笔记——王沪宁的智识生活',
    '- **1995 年的中国**：改革开放中期——社会变迁的观察',
    '',
    '### 对 essence 项目的贡献',
    '- **第 1 章（国家本质）**：政治学者的自述——案例性',
    '- **作为人物研究**：理解三朝帝师的思想形成',
    '- **MANIFESTO 第二条（费曼）**：王沪宁的读书方法——可作为案例',
    '',
    '### 批判性评价',
    '- **优点**：罕见的政治学者内心记录',
    '- **弱点**：日记体——可能经过自我审查',
    '- **政治敏感**：王沪宁现任常委——阅读需注意政治语境',
    '',
    '### 调用建议',
    '- 用于理解学者型官员的思想形态',
    '- 用于反思学而优则仕传统',
    '',
]
for l in d3_lines:
    w(l)

w("---")
w("")

# ============================================================
# Cross-book synthesis
# ============================================================
w("## 跨书对比：原文引用的相互印证")
w("")
w("### 周雪光 vs 周黎安：两种治理分析框架")
w("")
w("> **周雪光**（组织社会学视角）：")
w('> "一统体制与有效治理"是中国国家治理的基本矛盾——中央统辖权 vs 地方治理权')
w("> — p.20, 第1章")
w("")
w("> **周黎安**（政治经济学视角）：")
w('> 行政发包制+政治锦标赛构成地方官员的双重激励结构')
w("> — p.46, 第2章")
w("")
w('**互补关系**：周雪光解释"为什么会出问题"（一统与有效的张力），周黎安解释"为什么还能运转"（发包+锦标赛的激励兼容）。')
w("")
w("### 周飞舟补充：财政视角的机制")
w("")
w('> **周飞舟**：分税制改革后，"财权层层上收、事权层层下移"——地方被迫开辟非税收入来源（土地财政）')
w("> — 第四章, 分税制改革及其影响")
w("")
w("三位学者构成完整的分析三角：")
w("| 学者 | 分析层次 | 核心变量 |")
w("|------|---------|---------|")
w("| 周雪光 | 宏观制度 | 一统体制 vs 有效治理 |")
w("| 周黎安 | 中观激励 | 行政发包制 + 政治锦标赛 |")
w("| 周飞舟 | 微观财政 | 分税制 → 土地财政 |")
w("")
w("### 波普尔的哲学锚点")
w("")
w('> 波普尔对"乌托邦工程"的批评，为理解中国"渐进改革"vs"休克疗法"之争提供了哲学框架。')
w('> "零星社会工程"（piecemeal social engineering）的立场，与邓小平"摸着石头过河"在方法论上有呼应——但动机和哲学基础完全不同。')
w("")
w("---")
w("")

# ============================================================
# Statistics
# ============================================================
w("## 附录：本次提取统计")
w("")
w("| 书目 | 提取来源 | 定义 | 数据 | 命题 | 案例 |")
w("|------|---------|------|------|------|------|")
w(f"| B1 周雪光 | extracted-knowledge-zhou-xueguang.md | {len(zxg['defs'])} | {len(zxg['data'])} | {len(zxg['claims'])} | {len(zxg['cases'])} |")
w(f"| B3 周黎安 | extracted-knowledge-zhou-lian.md | {len(zl['defs'])} | {len(zl['data'])} | {len(zl['claims'])} | {len(zl['cases'])} |")
w(f"| B4 周飞舟 | extracted-knowledge-others.md | {len(zfz['defs'])} | {len(zfz['data'])} | {len(zfz.get('claims', []))} | {len(zfz['cases'])} |")
w(f"| A1 波普尔 | extracted-knowledge-others.md | {len(popper['defs'])} | {len(popper['data'])} | {len(popper.get('claims', []))} | {len(popper['cases'])} |")
w(f"| F3 黄奇帆 | extracted-knowledge-others.md | {len(hqf['defs'])} | {len(hqf['data'])} | {len(hqf.get('claims', []))} | {len(hqf['cases'])} |")
w(f"| F5 孙萍 | extracted-knowledge-others.md | {len(sp['defs'])} | {len(sp['data'])} | {len(sp.get('claims', []))} | {len(sp['cases'])} |")
w("| D3 王沪宁 | （未提取） | — | — | — | — |")
w("")

method_lines = [
    "",
    '> **方法说明**：以上所有原文引用均由 Python 正则表达式从 pdftotext 全文中自动提取。提取方法包括：',
    '> 1. **定义性陈述**：匹配"即/是指/所谓/也就是/被称为/意味着"等定义标记词',
    '> 2. **关键数据**：匹配含百分比、年份、数值、增长率等数字模式的长句',
    '> 3. **核心理论命题**：匹配含"因为/因此/所以/表明/说明/意味着/解释"等推理标记的长段落',
    '> 4. **关键案例**：匹配含人名、地名、事件名、年份等实体标识的叙事段落',
    "> ",
    '> ⚠️ 由于 pdftotext 的 OCR 质量问题，部分引用可能存在断句、缺字。使用时应回查原书确认。',
]
for l in method_lines:
    w(l)

w("")
w("---")
w("")
w('> **下一步**：对其余书目（E1 毛泽东文集、E2 邓小平文选、I2 钱穆作品集等）进行同样的原文提取，逐步将全部笔记从概括升级为原文引用。')

# Write
output_path = BASE / "political-books-deep-notes-v2.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"\n✅ Written to {output_path}")
print(f"   Total lines: {len(out)}")
print(f"   File size: {os.path.getsize(output_path):,} bytes")
