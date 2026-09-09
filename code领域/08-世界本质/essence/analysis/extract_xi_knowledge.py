#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《习近平谈治国理政》三卷深度知识提取
输出: analysis/extracted-knowledge-xi-jinping.md
"""

import json
import re
import os
from collections import defaultdict, OrderedDict

DATA_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"
OUT_FILE = "/mnt/c/workspace/essence/analysis/extracted-knowledge-xi-jinping.md"

# ---- 定位三卷文件 ----
TARGET_KEYWORDS = {
    "第一卷": "习近平谈治国理政",
    "第二卷": "习近平谈治国理政",
    "第三卷": "习近平谈治国理政",
}

def find_files():
    found = {}
    for fn in os.listdir(DATA_DIR):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(DATA_DIR, fn)
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        fname = d.get("filename", "")
        if "习近平谈治国理政" not in fname:
            continue
        for vol in ["第一卷", "第二卷", "第三卷"]:
            if vol in fname and vol not in found:
                found[vol] = (path, d)
    return found

volumes = find_files()
assert len(volumes) == 3, f"Expected 3 volumes, found {list(volumes.keys())}"
print("定位到三卷:")
for vol, (path, d) in volumes.items():
    print(f"  {vol}: {os.path.basename(path)} | {d['pages']}页 | {d['total_chars']}字")

VOL_LABEL = {"第一卷": "第一卷", "第二卷": "第二卷", "第三卷": "第三卷"}

# ============================================================
# 1. 目录提取
# ============================================================

def extract_toc_vol1(d):
    """第一卷: toc字段 [level, title, page]"""
    toc = []
    for item in d.get("toc", []):
        level, title, page = item[0], item[1], item[2]
        toc.append((level, title.strip(), page))
    return toc

def extract_toc_vol3(d):
    """第三卷: toc字段 [level, title, page]"""
    toc = []
    for item in d.get("toc", []):
        level, title, page = item[0], item[1], item[2]
        toc.append((level, title.strip(), page))
    return toc

def extract_toc_vol2(d):
    """第二卷: 从full_text前几页解析目录 (page 4-12)"""
    toc = []
    # 合并目录页文本
    toc_text = ""
    for p in d["full_text"]:
        if 4 <= p["page"] <= 13:
            toc_text += p["text"] + "\n"
    # 按行解析: 专题标题(一~十七开头)为 level 1, 其余为 level 2
    lines = [l.strip() for l in toc_text.split("\n") if l.strip()]
    current_section = None
    # 专题标记
    section_pattern = re.compile(r'^[一二三四五六七八九十]+、')
    for line in lines:
        if line == "目录" or line.startswith("出版说明") or line.startswith("索引"):
            continue
        if section_pattern.match(line):
            current_section = line
            toc.append((1, line, None))
        elif current_section is not None:
            # 文章标题行 (可能带日期或页码)
            # 去掉尾部页码和日期
            cleaned = re.sub(r'\s*\d+\s*$', '', line)
            cleaned = re.sub(r'（\d{4}年\d{1,2}月\d{1,2}日.*?）', '', cleaned).strip()
            if cleaned and len(cleaned) > 2:
                toc.append((2, cleaned, None))
    return toc

print("\n[1/5] 提取目录...")
toc_all = OrderedDict()
toc_all["第一卷"] = extract_toc_vol1(volumes["第一卷"][1])
toc_all["第二卷"] = extract_toc_vol2(volumes["第二卷"][1])
toc_all["第三卷"] = extract_toc_vol3(volumes["第三卷"][1])
for vol, toc in toc_all.items():
    n1 = sum(1 for t in toc if t[0] == 1)
    n2 = sum(1 for t in toc if t[0] == 2)
    print(f"  {vol}: {n1}个专题, {n2}篇文章")

# ============================================================
# 2. 核心概念频率统计
# ============================================================
print("\n[2/5] 统计核心概念频率...")

CONCEPTS = [
    "中国梦", "全面深化改革", "全面从严治党", "依法治国", "新发展理念",
    "人类命运共同体", "共同富裕", "双循环", "科技自立", "国家安全",
    "全过程人民民主", "两个一百年", "百年未有之大变局",
]

# 构建每卷纯文本 (保留page索引)
vol_pages = {}  # vol -> list of (page, text)
vol_fulltext = {}  # vol -> concatenated text
for vol, (path, d) in volumes.items():
    pages = [(p["page"], p["text"]) for p in d["full_text"]]
    vol_pages[vol] = pages
    vol_fulltext[vol] = "".join(t for _, t in pages)

concept_counts = {}  # concept -> {vol: count, total}
for c in CONCEPTS:
    concept_counts[c] = {}
    total = 0
    for vol in ["第一卷", "第二卷", "第三卷"]:
        cnt = vol_fulltext[vol].count(c)
        concept_counts[c][vol] = cnt
        total += cnt
    concept_counts[c]["合计"] = total

for c in CONCEPTS:
    print(f"  {c}: 一{concept_counts[c]['第一卷']} 二{concept_counts[c]['第二卷']} 三{concept_counts[c]['第三卷']} = {concept_counts[c]['合计']}")

# ============================================================
# 3. 关键数据提取
# ============================================================
print("\n[3/5] 提取关键数据...")

# 数据模式: 包含数字+单位/关键词
DATA_PATTERNS = [
    # GDP/经济
    (re.compile(r'.{0,60}(?:GDP|国内生产总值|经济增长|经济总量|经济增速).{0,80}'), "经济/GDP"),
    (re.compile(r'.{0,40}(?:翻一番|翻两番|增长[百分之\d]+|增速).{0,60}'), "经济/GDP"),
    # 贫困
    (re.compile(r'.{0,50}(?:贫困人口|脱贫|贫困县|贫困地区|减贫|消除贫困).{0,80}'), "脱贫"),
    (re.compile(r'.{0,30}全面建成小康社会.{0,80}'), "小康/脱贫"),
    # 军事
    (re.compile(r'.{0,50}(?:国防和军队|强军|军事斗争|军队建设|新时代军事).{0,80}'), "军事"),
    # 外交
    (re.compile(r'.{0,40}(?:一带一路|建交国|伙伴关系|多边|全球治理).{0,80}'), "外交"),
    # 人口/民生
    (re.compile(r'.{0,40}(?:城镇化率|就业|居民收入|人均|中等收入群体|人口).{0,80}'), "民生"),
    # 科技
    (re.compile(r'.{0,40}(?:研发投入|R&D|科技投入|创新驱动|科技强国).{0,80}'), "科技"),
    # 建党/建国周年
    (re.compile(r'.{0,40}(?:建党一百|建国一百|两个一百年|奋斗目标).{0,80}'), "目标"),
]

def has_digit(s):
    return bool(re.search(r'\d', s))

def extract_data_items():
    items = []
    seen = set()
    for vol, pages in vol_pages.items():
        for page, text in pages:
            # 按句分割
            sentences = re.split(r'[。\n！；]', text)
            for sent in sentences:
                sent = sent.strip()
                if len(sent) < 8 or len(sent) > 250:
                    continue
                if not has_digit(sent):
                    continue
                for pattern, cat in DATA_PATTERNS:
                    m = pattern.search(sent)
                    if m:
                        snippet = m.group(0).strip()
                        key = (vol, page, snippet[:50])
                        if key in seen:
                            continue
                        seen.add(key)
                        items.append((cat, vol, page, sent[:200]))
                        break
    return items

data_items = extract_data_items()
print(f"  提取到 {len(data_items)} 条关键数据")
# 按类别统计
data_cats = defaultdict(int)
for cat, vol, page, text in data_items:
    data_cats[cat] += 1
for cat, cnt in sorted(data_cats.items(), key=lambda x: -x[1]):
    print(f"    {cat}: {cnt}")

# ============================================================
# 4. 核心论断提取 (祈使句式)
# ============================================================
print("\n[4/5] 提取核心论断...")

# 主题关键词
THEME_KEYWORDS = {
    "经济": ["经济", "发展", "改革", "市场", "产业", "供给侧", "金融", "贸易", "投资", "创新", "科技", "数字", "高质量", "新常态", "内需", "消费"],
    "政治": ["政治", "制度", "民主", "人大", "政协", "协商", "治理", "法治", "依法", "宪法", "立法", "行政", "监督", "权力"],
    "文化": ["文化", "文明", "价值", "信仰", "思想", "意识", "舆论", "媒体", "网络", "文艺", "哲学", "社会科学", "传统", "中华"],
    "社会": ["民生", "教育", "就业", "医疗", "健康", "社保", "养老", "扶贫", "脱贫", "安全", "治理", "社区", "人口", "住房"],
    "生态": ["生态", "环境", "绿色", "低碳", "污染", "减排", "气候", "自然", "绿水青山", "金山银山", "美丽中国", "碳"],
    "外交": ["外交", "国际", "世界", "全球", "和平", "发展", "合作", "共赢", "命运共同体", "一带一路", "多边", "大国", "周边"],
    "军事": ["军队", "国防", "军事", "强军", "武装", "战士", "官兵", "备战", "打仗", "安全", "主权"],
    "党建": ["党", "党建", "从严", "纪律", "作风", "反腐", "廉洁", "政治建设", "思想建设", "组织建设", "干部", "党员", "领导", "初心", "使命"],
}

def classify_theme(text):
    scores = {}
    for theme, kws in THEME_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in text)
        if score > 0:
            scores[theme] = score
    if not scores:
        return "综合"
    return max(scores, key=scores.get)

# 祈使句式正则
IMPERATIVE_PATTERNS = [
    re.compile(r'(?:^|[。！\n])([^。！\n]{0,10}(?:必须|要|坚持|推动|构建|加快|加强|推进|深化|强化|落实|完善|坚决|始终|牢牢|全面|深入|着力|注重|切实|扎实|统筹|协调|严格|突出|聚焦)[^。！\n]{15,200})[。！]'),
]

def extract_imperatives():
    items = []
    seen = set()
    for vol, pages in vol_pages.items():
        for page, text in pages:
            for pattern in IMPERATIVE_PATTERNS:
                for m in pattern.finditer(text):
                    clause = m.group(1).strip()
                    # 过滤太短或噪音
                    if len(clause) < 20:
                        continue
                    # 必须包含核心动词
                    if not re.search(r'(?:必须|要|坚持|推动|构建|加快|加强|推进|深化|强化|落实|完善|坚决|始终|牢牢|着力|注重|切实|扎实|统筹|严格|突出|聚焦)', clause):
                        continue
                    # 去重 (按前40字)
                    key = clause[:40]
                    if key in seen:
                        continue
                    seen.add(key)
                    theme = classify_theme(clause)
                    items.append((theme, vol, page, clause[:200]))
    return items

imperative_items = extract_imperatives()
print(f"  提取到 {len(imperative_items)} 条核心论断")
imp_themes = defaultdict(int)
for theme, vol, page, text in imperative_items:
    imp_themes[theme] += 1
for theme, cnt in sorted(imp_themes.items(), key=lambda x: -x[1]):
    print(f"    {theme}: {cnt}")

# ============================================================
# 5. 引用经典提取
# ============================================================
print("\n[5/5] 提取引用经典...")

# 引用模式: "马克思说" / "毛泽东同志指出" / "邓小平强调" 等
QUOTE_SOURCES = [
    ("马克思", ["马克思", "马克思主义经典"]),
    ("恩格斯", ["恩格斯"]),
    ("列宁", ["列宁"]),
    ("毛泽东", ["毛泽东", "毛主席"]),
    ("邓小平", ["邓小平"]),
    ("江泽民", ["江泽民"]),
    ("胡锦涛", ["胡锦涛"]),
    # 中华经典
    ("《论语》/孔子", ["孔子", "《论语》"]),
    ("《道德经》/老子", ["老子", "《道德经》", "《老子》"]),
    ("《孟子》", ["孟子", "《孟子》"]),
    ("《荀子》", ["荀子", "《荀子》"]),
    ("《管子》", ["管子", "《管子》"]),
    ("《尚书》", ["《尚书》", "书经"]),
    ("《周易》/《易经》", ["《周易》", "《易经》"]),
    ("《礼记》", ["《礼记》"]),
    ("《大学》", ["《大学》"]),
    ("《中庸》", ["《中庸》"]),
    ("《诗经》", ["《诗经》"]),
    ("《左传》", ["《左传》"]),
    ("《庄子》", ["庄子", "《庄子》"]),
    ("《韩非子》", ["韩非子", "《韩非子》"]),
    ("《孙子兵法》", ["孙子", "《孙子"]),
    ("杜甫", ["杜甫"]),
    ("李白", ["李白"]),
    ("陆游", ["陆游"]),
    ("苏轼", ["苏轼", "苏东坡"]),
    ("王阳明", ["王阳明"]),
    ("顾炎武", ["顾炎武"]),
    ("魏源", ["魏源"]),
    ("林则徐", ["林则徐"]),
    ("《资治通鉴》", ["《资治通鉴》"]),
    ("司马迁/《史记》", ["司马迁", "《史记》"]),
]

# 引用动词: 区分"直接引用"(有说/指出/强调+引号)与"一般提及"
CITATION_VERBS = re.compile(r'(?:说|指出|强调|认为|写道|提出|告诫|曾说|曾指出|的名言|的话|说过|讲过|告诫我们|提醒我们)')
HAS_QUOTE_MARK = re.compile(r'[“”"\']')

def extract_quotes():
    """提取引用，分两级:
       - 'direct': 直接引用 (含引用动词 或 引号) — 高价值
       - 'mention': 一般提及 (仅出现名字) — 低价值，仅计数
    """
    items = []      # direct quotes (会全文展示)
    mention_counts = defaultdict(int)  # source -> 提及次数
    seen = set()
    for vol, pages in vol_pages.items():
        for page, text in pages:
            sentences = re.split(r'(?<=[。！？\n])', text)
            for sent in sentences:
                sent = sent.strip()
                if len(sent) < 6:
                    continue
                for source_name, keywords in QUOTE_SOURCES:
                    matched_kw = None
                    for kw in keywords:
                        if kw in sent:
                            matched_kw = kw
                            break
                    if matched_kw is None:
                        continue
                    # 判定: 是否直接引用
                    is_direct = bool(CITATION_VERBS.search(sent) or HAS_QUOTE_MARK.search(sent))
                    # 排除纯注释/脚注行 (如 "见毛泽东《...》" 算 direct 因为是出处引用)
                    mention_counts[source_name] += 1
                    if is_direct:
                        key = (vol, page, sent[:40])
                        if key in seen:
                            continue
                        seen.add(key)
                        items.append((source_name, matched_kw, vol, page, sent[:200], "direct"))
                    break  # 一个source匹配一次即可
    return items, mention_counts

quote_items, mention_counts = extract_quotes()
n_direct = len(quote_items)
n_mention = sum(mention_counts.values())
print(f"  提取到 {n_direct} 条直接引用 + {n_mention} 次一般提及")
quote_sources = defaultdict(int)
for source, kw, vol, page, text, level in quote_items:
    quote_sources[source] += 1
print("  直接引用分布:")
for source, cnt in sorted(quote_sources.items(), key=lambda x: -x[1]):
    print(f"    {source}: {cnt} (提及共{mention_counts[source]})")

# ============================================================
# 输出 Markdown
# ============================================================
print(f"\n写入 {OUT_FILE} ...")

def fmt_toc(toc, vol):
    lines = []
    for level, title, page in toc:
        indent = "" if level == 1 else "  - "
        pg = f" (p.{page})" if page else ""
        if level == 1:
            lines.append(f"- **{title}**{pg}")
        else:
            lines.append(f"  - {title}{pg}")
    return "\n".join(lines)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("# 《习近平谈治国理政》三卷 · 深度知识提取\n\n")
    f.write("> 自动提取自三卷全文JSON。涵盖目录、概念频率、关键数据、核心论断、引用经典。\n\n")
    f.write("---\n\n")

    # 概览
    f.write("## 概览\n\n")
    f.write("| 卷 | 文件 | 页数 | 字数 |\n")
    f.write("|---|---|---|---|\n")
    for vol in ["第一卷", "第二卷", "第三卷"]:
        path, d = volumes[vol]
        f.write(f"| {vol} | `{os.path.basename(path)}` | {d['pages']} | {d['total_chars']:,} |\n")
    total_chars = sum(volumes[v][1]["total_chars"] for v in ["第一卷","第二卷","第三卷"])
    total_pages = sum(volumes[v][1]["pages"] for v in ["第一卷","第二卷","第三卷"])
    f.write(f"| **合计** | — | **{total_pages}** | **{total_chars:,}** |\n\n")

    # ===== 1. 目录 =====
    f.write("---\n\n## 1. 三卷完整目录\n\n")
    for vol in ["第一卷", "第二卷", "第三卷"]:
        f.write(f"### {vol}\n\n")
        f.write(fmt_toc(toc_all[vol], vol))
        f.write("\n\n")

    # ===== 2. 概念频率 =====
    f.write("---\n\n## 2. 核心概念频率统计\n\n")
    f.write("> 统计13个核心概念在三卷中的出现次数。\n")
    f.write(">\n")
    f.write("> **重要发现**：\"双循环\"\"科技自立\"\"全过程人民民主\"三卷中**零出现**。\n")
    f.write("> 这并非遗漏——这三个概念均在三卷出版后才正式提出（双循环2020.5、科技自立自强2020.10、全过程人民民主2021），\n")
    f.write("> 而第三卷收录截止2020年1月。这本身就是思想演化的关键证据。\n\n")
    f.write("| 概念 | 第一卷 | 第二卷 | 第三卷 | 合计 |\n")
    f.write("|------|-------|-------|-------|------|\n")
    for c in CONCEPTS:
        cc = concept_counts[c]
        f.write(f"| {c} | {cc['第一卷']} | {cc['第二卷']} | {cc['第三卷']} | **{cc['合计']}** |\n")
    f.write("\n")
    # 趋势分析
    f.write("### 概念演化趋势\n\n")
    f.write("| 概念 | 趋势（一→二→三） | 特征 |\n|------|------------------|------|\n")
    for c in CONCEPTS:
        cc = concept_counts[c]
        vals = [cc["第一卷"], cc["第二卷"], cc["第三卷"]]
        if sum(vals) == 0:
            trend = "三卷均未出现"
            feat = "—"
        elif vals[2] > vals[0] and vals[2] > vals[1]:
            trend = "↑ 递增，第三卷最高"
            feat = "新时代强化"
        elif vals[0] > vals[1] and vals[0] > vals[2]:
            trend = "↓ 递减，第一卷最高"
            feat = "早期侧重"
        elif vals[0] == 0 and (vals[1] > 0 or vals[2] > 0):
            trend = f"第二/三卷新增"
            feat = "新提出概念"
        else:
            trend = f"波动"
            feat = "持续关注"
        f.write(f"| {c} | {vals[0]}→{vals[1]}→{vals[2]} {trend} | {feat} |\n")
    f.write("\n")

    # ===== 3. 关键数据 =====
    f.write("---\n\n## 3. 关键数据\n\n")
    f.write("> 含GDP/经济目标、贫困数据、军事目标、外交数据等。每条标注卷号+页码。\n\n")
    by_cat = defaultdict(list)
    for cat, vol, page, text in data_items:
        by_cat[cat].append((vol, page, text))
    for cat in ["经济/GDP", "脱贫", "小康/脱贫", "目标", "民生", "科技", "军事", "外交"]:
        items = by_cat.get(cat, [])
        if not items:
            continue
        f.write(f"### {cat}（{len(items)}条）\n\n")
        # 每类最多展示60条
        for vol, page, text in items[:60]:
            f.write(f"- **{vol} p.{page}**: {text}\n")
        if len(items) > 60:
            f.write(f"- ...（另有 {len(items)-60} 条省略）\n")
        f.write("\n")

    # ===== 4. 核心论断 =====
    f.write("---\n\n## 4. 核心论断（按主题分类）\n\n")
    f.write("> 祈使句式重要论断：\"必须…/要…/坚持…/推动…/构建…\"等。每条标注卷号+页码。\n\n")
    by_theme = defaultdict(list)
    for theme, vol, page, text in imperative_items:
        by_theme[theme].append((vol, page, text))
    theme_order = ["经济", "政治", "文化", "社会", "生态", "外交", "军事", "党建", "综合"]
    for theme in theme_order:
        items = by_theme.get(theme, [])
        if not items:
            continue
        f.write(f"### {theme}（{len(items)}条）\n\n")
        for vol, page, text in items[:80]:
            f.write(f"- **{vol} p.{page}**: {text}\n")
        if len(items) > 80:
            f.write(f"- ...（另有 {len(items)-80} 条省略）\n")
        f.write("\n")

    # ===== 5. 引用经典 =====
    f.write("---\n\n## 5. 引用经典\n\n")
    f.write("> 引用马克思/恩格斯/列宁/毛泽东/邓小平及中华经典的地方。\n")
    f.write("> 分两级：**直接引用**（含引用动词如\"说/指出/强调\"或引号，高价值，全文展示）vs **一般提及**（仅计数）。\n\n")

    # 总览表
    leader_sources = ["马克思", "恩格斯", "列宁", "毛泽东", "邓小平", "江泽民", "胡锦涛"]
    f.write("### 5.0 引用总览\n\n")
    f.write("| 被引用者 | 直接引用 | 一般提及 | 合计 |\n|----------|---------|---------|------|\n")
    all_source_order = [s for s, _ in QUOTE_SOURCES]
    for source in all_source_order:
        d_cnt = quote_sources.get(source, 0)
        m_cnt = mention_counts.get(source, 0)
        if d_cnt == 0 and m_cnt == 0:
            continue
        f.write(f"| {source} | {d_cnt} | {m_cnt} | **{d_cnt + m_cnt}** |\n")
    f.write(f"| **合计** | **{n_direct}** | **{n_mention}** | **{n_direct + n_mention}** |\n\n")

    by_source = defaultdict(list)
    for source, kw, vol, page, text, level in quote_items:
        by_source[source].append((vol, page, kw, text))

    f.write("### 5.1 革命导师与领导人引用（直接引用）\n\n")
    for source in leader_sources:
        items = by_source.get(source, [])
        m_cnt = mention_counts.get(source, 0)
        if not items and m_cnt == 0:
            continue
        f.write(f"#### {source}（直接引用{len(items)}条，一般提及{m_cnt}次）\n\n")
        if not items:
            f.write("—（无直接引用，仅作为思想体系被提及）\n\n")
            continue
        for vol, page, kw, text in items[:50]:
            f.write(f"- **{vol} p.{page}** [匹配:{kw}]: {text}\n")
        if len(items) > 50:
            f.write(f"- ...（另有 {len(items)-50} 条省略）\n")
        f.write("\n")

    f.write("### 5.2 中华经典引用（直接引用）\n\n")
    classic_sources = [s for s, _ in QUOTE_SOURCES if s not in leader_sources]
    for source in classic_sources:
        items = by_source.get(source, [])
        m_cnt = mention_counts.get(source, 0)
        if not items and m_cnt == 0:
            continue
        f.write(f"#### {source}（直接引用{len(items)}条，一般提及{m_cnt}次）\n\n")
        if not items:
            f.write("—（仅被提及）\n\n")
            continue
        for vol, page, kw, text in items[:30]:
            f.write(f"- **{vol} p.{page}** [匹配:{kw}]: {text}\n")
        if len(items) > 30:
            f.write(f"- ...（另有 {len(items)-30} 条省略）\n")
        f.write("\n")

    # 统计摘要
    f.write("---\n\n## 提取统计摘要\n\n")
    f.write("| 类别 | 条数 |\n|------|------|\n")
    f.write(f"| 目录条目 | {sum(len(t) for t in toc_all.values())} |\n")
    f.write(f"| 核心概念 | {len(CONCEPTS)}个（合计出现{sum(concept_counts[c]['合计'] for c in CONCEPTS)}次） |\n")
    f.write(f"| 关键数据 | {len(data_items)}条 |\n")
    f.write(f"| 核心论断 | {len(imperative_items)}条 |\n")
    f.write(f"| 引用经典-直接引用 | {n_direct}条 |\n")
    f.write(f"| 引用经典-一般提及 | {n_mention}次 |\n")
    f.write(f"| **总计（展示条目）** | **{sum(len(t) for t in toc_all.values()) + len(data_items) + len(imperative_items) + n_direct}条（+{len(CONCEPTS)}概念 +{n_mention}提及）** |\n")

print("\n=== 完成 ===")
print(f"输出: {OUT_FILE}")
