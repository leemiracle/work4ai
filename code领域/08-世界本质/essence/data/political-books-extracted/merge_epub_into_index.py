#!/usr/bin/env python3
"""
将 6 本 EPUB 全文数据合并到已有 knowledge_index.json。

提取策略（基于全文正则匹配）：
- 定义 (definitions):  匹配 "X是指" "X意味着" "所谓X" "X，即" "被称为X" 等
- 命题 (propositions):  匹配 "我认为" "必须" "核心是" "关键在于" "本质上" 等
- 数据 (data_points):   匹配 数字+单位（万亿/亿/万/%/元/人/年等）
- 案例 (cases):         匹配 含地名/人名的叙事段落

合并策略：
- propositions / data_points / cases:  平铺追加到现有列表
- concepts:                            按"概念名"聚合，合并进现有概念结构
- cross_book_index:                    对已知跨书概念统计 EPUB 中出现频次并追加
- metadata:                            更新 total_books(15→21)、total_chars、total_entries
"""

import json
import re
import os
import glob
from collections import defaultdict
from datetime import date

DATA_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"
INDEX_PATH = os.path.join(DATA_DIR, "knowledge_index.json")

# ============================================================
# 每本 EPUB 提取条目上限（避免 JSON 爆炸，全文 7.7M 字符）
# ============================================================
CAP_DEFINITIONS = 120   # 每本
CAP_PROPOSITIONS = 160  # 每本
CAP_DATA_POINTS = 220   # 每本
CAP_CASES = 90          # 每本

# 已知跨书核心概念（与 build_knowledge_index.py 保持一致）
CROSS_BOOK_CONCEPTS = [
    "权力", "开放", "维稳", "制度", "权威", "改革", "意识形态",
    "社会主义", "资本主义", "主权", "市场经济", "腐败", "党国",
    "数字治理", "全球化", "绩效合法性", "附近", "法治", "人治",
    "有效治理", "共谋", "民主化", "一统体制", "分税制", "民族主义",
    "集体行动", "合法性", "晋升锦标赛", "国家与社会", "社会运动",
    "国家能力", "土地财政", "逆向软预算约束", "运动式治理",
    "行政发包", "官僚制", "数目字管理", "实事求是", "过渡劳动",
    "平台经济", "软预算约束", "革命", "阶级", "群众", "路线",
    "土地", "财政", "税收", "增长", "发展", "工业化", "城市化",
]

# ============================================================
# 提取用正则模式
# ============================================================
# 定义：捕获 概念名 + 定义正文
DEF_PATTERNS = [
    # 所谓X，是指/就是/即...
    re.compile(r'(?:所谓|所谓的)[\s""\u201c\u2018「]?([^\u3002\uff0c""\u201d\u2019」，：:!！?？\s]{2,15})[\s""\u201d\u2019」]?(?:是指|指的是|，就是|，即|就是|意味着)'),
    # X是指Y / X意味着Y
    re.compile(r'([^\u3002\uff0c""\u201d\u2019」，：:!！?？\s]{2,15})(?:是指|意味着)(.{8,80})'),
    # X，即Y / X，也就是Y
    re.compile(r'([^\u3002\uff0c""\u201d\u2019」，：:!！?？\s]{2,12})[，,](?:即|也就是|就是说)(.{8,80})'),
    # 被称为X / 称之为X
    re.compile(r'(?:被称为|称之为|称为)[\s""\u201c\u2018「]?([^\u3002\uff0c""\u201d\u2019」，：:!！?？\s]{2,15})'),
    # X的本质是 / X的核心是
    re.compile(r'([^\u3002\uff0c""\u201d\u2019」，：:!！?？\s]{2,12})的(?:本质|核心|关键|基础|前提)是'),
]

# 命题触发词
PROP_TRIGGERS = [
    "我认为", "笔者认为", "我们必须", "必须", "应当", "应该",
    "核心是", "关键在于", "关键在于", "本质上是", "从根本上",
    "最重要", "归根到底", "归根结底", "总之", "由此可见",
    "可以得出", "结论是", "说明了", "证明了", "这意味着",
    "必然", "一定", "只有…才", "之所以…是因为",
]
PROP_TRIGGERS_RE = re.compile(r'(?:我认为|笔者认为|我主张|在我看来|我们必须|必须指出|应当看到|核心是|关键在于|本质上[是]|从根本上[说讲]|归根到底|归根结底|由此[可见]|结论是|这意味[着]|证明了|必然要|只有.{1,20}才)')

# 数据：数字 + 单位
DATA_UNIT_RE = re.compile(
    r'[\u3000-\u9fff\w]{0,18}?\d+(?:\.\d+)?\s*(?:万亿|千亿|百亿|十亿|亿|千万|百万|万|千|%'
    r'|％|美元|元|人民币|公斤|吨|亩|公顷|平方公里|平方千米|人|名|岁|年|个月|天|小时|度|个百分点)'
)
# 严格数字+单位（用于 data_points）
STRICT_DATA_RE = re.compile(
    r'(\d+(?:\.\d+)?)\s*(万亿|千亿|百亿|十亿|亿|千万|百万|万|千|%|％|美元|元|人民币|吨|亩|公顷|平方公里|平方千米|岁|个百分点|个百|分点)'
)

# 中国地名（省级 + 常见城市，用于案例识别）
PLACE_NAMES = [
    "北京", "上海", "天津", "重庆", "广州", "深圳", "杭州", "南京", "武汉",
    "成都", "西安", "沈阳", "大连", "青岛", "济南", "苏州", "无锡", "宁波",
    "温州", "福州", "厦门", "长沙", "郑州", "合肥", "南昌", "昆明", "贵阳",
    "兰州", "太原", "石家庄", "哈尔滨", "长春", "南宁", "海口", "银川", "西宁",
    "乌鲁木齐", "拉萨", "呼和浩特", "香港", "澳门", "台湾", "珠三角", "长三角",
    "广东", "江苏", "浙江", "山东", "河南", "四川", "湖北", "湖南", "河北",
    "福建", "安徽", "江西", "陕西", "辽宁", "吉林", "黑龙江", "广西", "云南",
    "贵州", "甘肃", "青海", "宁夏", "新疆", "西藏", "内蒙古", "海南", "山西",
    "小岗村", "华西村", "深圳特区", "浦东",
]
PLACE_RE = re.compile('|'.join(re.escape(p) for p in PLACE_NAMES))

# ============================================================
# 工具函数
# ============================================================

def clean(text):
    """压缩空白、去首尾"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def trunc(text, n=400):
    if len(text) > n:
        return text[:n] + "…"
    return text

def _pages_to_text(full_text):
    """把 full_text（可能是 list[dict]、list[str] 或 str）统一转成纯文本"""
    if isinstance(full_text, str):
        return full_text
    if isinstance(full_text, list):
        parts = []
        for p in full_text:
            if isinstance(p, dict):
                parts.append(p.get("text", ""))
            elif isinstance(p, str):
                parts.append(p)
        return "\n".join(parts)
    return str(full_text)


def split_paragraphs(full_text):
    """把多页全文拼起来，按段落切分"""
    text = _pages_to_text(full_text)
    # 按换行 + 句号切块
    paras = re.split(r'[\n\r]+', text)
    out = []
    for p in paras:
        p = clean(p)
        if len(p) >= 12:  # 过短段落丢弃
            out.append(p)
    return out

def is_noise_concept(name):
    if not name or len(name) < 2 or len(name) > 12:
        return True
    if name.isdigit():
        return True
    NOISE = {
        "当然", "但是", "实际上", "事实上", "换言之", "简言之", "也就是", "所谓",
        "这里", "特别", "特征", "效应", "服务", "绩效", "监督", "类似", "反复",
        "交换", "情况", "第二", "第一", "第三", "这个", "那个", "他们", "我们",
        "这些", "那些", "这种", "那种", "这样", "那样", "什么", "怎么", "为什么",
        "因为", "所以", "如果", "虽然", "尽管", "而且", "并且", "或者", "以及",
        "已经", "正在", "将要", "可以", "能够", "应该", "必须", "一定", "必然",
        "可能", "也许", "大概", "似乎", "好像", "其中", "其他", "另外", "此外",
        "同时", "当时", "后来", "之前", "之后", "之间", "当中", "上面", "下面",
        "前面", "后面", "里面", "外面", "左边", "右边", "旁边", "附近", "中间",
    }
    return name in NOISE

# ============================================================
# 提取器
# ============================================================

def extract_definitions(paras, book, author):
    """提取定义性陈述，返回 (concept_name, definition_text) 列表"""
    results = []
    seen = set()
    for para in paras:
        if len(para) > 300:
            continue
        for pat in DEF_PATTERNS:
            m = pat.search(para)
            if m:
                concept = m.group(1).strip().strip('""\u201c\u201d\u2018\u2019「」【】（）()')
                if is_noise_concept(concept):
                    continue
                key = concept
                if key in seen:
                    continue
                seen.add(key)
                results.append({
                    "concept": concept,
                    "book": book, "author": author, "page": "",
                    "text": trunc(para, 400),
                    "type": "definition",
                })
                if len(results) >= CAP_DEFINITIONS:
                    return results
                break
    return results

def extract_propositions(paras, book, author, theme=""):
    """提取命题/论断"""
    results = []
    seen = set()
    for para in paras:
        if not (20 <= len(para) <= 350):
            continue
        if PROP_TRIGGERS_RE.search(para):
            key = para[:60]
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "book": book, "author": author, "page": "",
                "text": trunc(para, 450),
                "theme": theme or "核心论断",
            })
            if len(results) >= CAP_PROPOSITIONS:
                return results
    return results

def extract_data_points(paras, book, theme=""):
    """提取数据点（数字+单位）"""
    results = []
    seen = set()
    for para in paras:
        if not (10 <= len(para) <= 400):
            continue
        if STRICT_DATA_RE.search(para):
            key = para[:50]
            if key in seen:
                continue
            seen.add(key)
            # 分类
            if '%' in para or '％' in para or '百分' in para:
                dtype = "percentage"
            elif any(u in para for u in ['万亿', '亿', '万', '元', '美元']):
                dtype = "fiscal"
            elif '年' in para:
                dtype = "temporal"
            elif any(u in para for u in ['人', '名', '口', '岁']):
                dtype = "population"
            else:
                dtype = "quantitative"
            results.append({
                "book": book, "page": "",
                "text": trunc(para, 300),
                "type": dtype,
                "source_section": "epub_fulltext",
            })
            if len(results) >= CAP_DATA_POINTS:
                return results
    return results

def extract_cases(paras, book, author):
    """提取案例（含地名/人名的叙事段落）"""
    results = []
    seen = set()
    for para in paras:
        if not (40 <= len(para) <= 400):
            continue
        if PLACE_RE.search(para):
            # 提取命中的地名作为标签
            hit_places = PLACE_RE.findall(para)
            tag = "、".join(dict.fromkeys(hit_places))[:20]  # 去重保序
            key = para[:50]
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "name": tag,
                "book": book, "author": author, "page": "",
                "summary": trunc(para, 400),
            })
            if len(results) >= CAP_CASES:
                return results
    return results

def count_concept(text, concept):
    """统计概念在全文中的出现次数"""
    return text.count(concept)

def extract_cross_book(full_text_str, book, concept):
    """为单个概念提取在单本书中的频次与上下文"""
    cnt = full_text_str.count(concept)
    if cnt == 0:
        return None
    # 找一个上下文片段
    idx = full_text_str.find(concept)
    start = max(0, idx - 40)
    end = min(len(full_text_str), idx + len(concept) + 80)
    context = clean(full_text_str[start:end])
    return {
        "concept": concept,
        "keyword": concept,
        "book": book,
        "count": cnt,
        "context": trunc(context, 200),
        "total_books": 1,  # 后面统一更新
    }

# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 64)
    print("合并 6 本 EPUB 全文到 knowledge_index.json")
    print("=" * 64)

    # 1. 加载现有索引
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        index = json.load(f)

    orig_counts = {
        "concepts": len(index["concepts"]),
        "propositions": len(index["propositions"]),
        "data_points": len(index["data_points"]),
        "cases": len(index["cases"]),
        "cross_book_index": len(index["cross_book_index"]),
    }
    orig_total_chars = index["metadata"]["total_chars"]
    print(f"\n[原索引] 概念={orig_counts['concepts']} 命题={orig_counts['propositions']} "
          f"数据={orig_counts['data_points']} 案例={orig_counts['cases']} "
          f"跨书={orig_counts['cross_book_index']}")
    print(f"[原索引] total_chars={orig_total_chars:,}  total_books={index['metadata']['total_books']}")

    # 2. 收集 EPUB 文件（排除 mobi，按任务 +6 EPUB，total_books 15→21）
    epub_files = sorted(glob.glob(os.path.join(DATA_DIR, "epub_*.json")))
    print(f"\n发现 {len(epub_files)} 个 EPUB 文件:")
    for fp in epub_files:
        with open(fp, 'r', encoding='utf-8') as f:
            d = json.load(f)
        print(f"  · {d['title'][:24]:24s} | {d['author'][:10]:10s} | {d['total_chars']:>8,} 字符")

    # 3. 逐本提取
    new_defs = []        # (concept, entry)
    new_propositions = []
    new_data_points = []
    new_cases = []
    new_cross = []
    epub_total_chars = 0
    new_sources = []

    # 用于概念聚合：concept_name -> list of definition entries
    concept_def_map = defaultdict(list)

    for fp in epub_files:
        with open(fp, 'r', encoding='utf-8') as f:
            d = json.load(f)
        title = d["title"]
        author = d["author"]
        book = title  # 用完整标题
        epub_total_chars += d["total_chars"]
        new_sources.append(f"{author}《{title}》")

        paras = split_paragraphs(d["full_text"])
        full_str = _pages_to_text(d["full_text"])

        defs = extract_definitions(paras, book, author)
        props = extract_propositions(paras, book, author, theme=title[:12])
        data = extract_data_points(paras, book)
        cases = extract_cases(paras, book, author)

        for dd in defs:
            concept_def_map[dd["concept"]].append(dd)

        new_propositions.extend(props)
        new_data_points.extend(data)
        new_cases.extend(cases)

        # 跨书概念频次
        for concept in CROSS_BOOK_CONCEPTS:
            cb = extract_cross_book(full_str, book, concept)
            if cb:
                new_cross.append(cb)

        print(f"\n  [{title[:20]}] 定义={len(defs):>3} 命题={len(props):>3} "
              f"数据={len(data):>3} 案例={len(cases):>3}")

    print(f"\n[EPUB 合计字符] {epub_total_chars:,}")

    # 4. 合并到现有索引

    # 4a. 概念聚合：合并进现有 concepts 结构
    #    现有 concepts 是 list of {concept, definitions[], mentions[], def_count, mention_count}
    existing_concept_map = {c["concept"]: c for c in index["concepts"]}
    new_concept_count = 0
    merged_concept_count = 0
    for cname, defs in concept_def_map.items():
        if cname in existing_concept_map:
            # 追加定义（去重）
            ec = existing_concept_map[cname]
            existing_texts = {d["text"][:40] for d in ec["definitions"]}
            for dd in defs:
                if dd["text"][:40] not in existing_texts:
                    ec["definitions"].append({
                        "book": dd["book"], "author": dd["author"],
                        "page": dd["page"], "text": dd["text"],
                    })
                    existing_texts.add(dd["text"][:40])
            ec["definitions"] = ec["definitions"][:15]  # 上限
            ec["def_count"] = len(ec["definitions"])
            merged_concept_count += 1
        else:
            # 新概念
            index["concepts"].append({
                "concept": cname,
                "definitions": [
                    {"book": d["book"], "author": d["author"],
                     "page": d["page"], "text": d["text"]} for d in defs[:8]
                ],
                "mentions": [],
                "def_count": min(len(defs), 8),
                "mention_count": 0,
            })
            new_concept_count += 1
            existing_concept_map[cname] = index["concepts"][-1]

    # 4b. 平铺追加
    index["propositions"].extend(new_propositions)
    index["data_points"].extend(new_data_points)
    index["cases"].extend(new_cases)

    # 4c. 跨书索引追加，并更新 total_books 字段（这些概念现在跨更多书）
    index["cross_book_index"].extend(new_cross)

    # 5. 更新 metadata
    old_books = index["metadata"]["total_books"]
    new_total_chars = orig_total_chars + epub_total_chars
    new_counts = {
        "concepts": len(index["concepts"]),
        "propositions": len(index["propositions"]),
        "data_points": len(index["data_points"]),
        "cases": len(index["cases"]),
        "cross_book_mentions": len(index["cross_book_index"]),
    }
    total_entries = (new_counts["concepts"] + new_counts["propositions"]
                     + new_counts["data_points"] + new_counts["cases"])

    index["metadata"]["total_books"] = old_books + len(epub_files)
    index["metadata"]["total_chars"] = new_total_chars
    index["metadata"]["total_entries"] = total_entries
    index["metadata"]["updated"] = str(date.today())
    # 追加新来源
    for s in new_sources:
        if s not in index["metadata"]["sources"]:
            index["metadata"]["sources"].append(s)
    index["metadata"]["entry_counts"] = new_counts
    index["metadata"]["entry_counts"]["cross_book_mentions"] = len(index["cross_book_index"])

    # 6. 保存
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    new_size = os.path.getsize(INDEX_PATH)

    # 7. 报告
    print("\n" + "=" * 64)
    print("合并完成")
    print("=" * 64)
    print(f"\n【新增条目】")
    print(f"  概念:   新建 {new_concept_count} 个 / 合并进已有 {merged_concept_count} 个")
    print(f"  命题:   +{len(new_propositions)}")
    print(f"  数据:   +{len(new_data_points)}")
    print(f"  案例:   +{len(new_cases)}")
    print(f"  跨书:   +{len(new_cross)}")

    added_entries = (new_concept_count + len(new_propositions)
                     + len(new_data_points) + len(new_cases))

    print(f"\n【总条目数】")
    print(f"  概念 (concepts):       {orig_counts['concepts']:>5} -> {new_counts['concepts']:>5}")
    print(f"  命题 (propositions):   {orig_counts['propositions']:>5} -> {new_counts['propositions']:>5}")
    print(f"  数据 (data_points):    {orig_counts['data_points']:>5} -> {new_counts['data_points']:>5}")
    print(f"  案例 (cases):          {orig_counts['cases']:>5} -> {new_counts['cases']:>5}")
    print(f"  跨书 (cross_book):     {orig_counts['cross_book_index']:>5} -> {new_counts['cross_book_mentions']:>5}")
    print(f"  ------------------------------")
    print(f"  total_entries:         {index['metadata'].get('total_entries',0):>5}  (新增约 {added_entries})")

    print(f"\n【统计更新】")
    print(f"  total_books:  {old_books} -> {index['metadata']['total_books']}  (+{len(epub_files)} EPUB)")
    print(f"  total_chars:  {orig_total_chars:,} -> {new_total_chars:,}  (+{epub_total_chars:,})")

    print(f"\n【文件】")
    print(f"  knowledge_index.json   = {new_size:,} bytes ({new_size/1024/1024:.2f} MB)")
    print(f"  knowledge_index_v1.json = {os.path.getsize(INDEX_PATH.replace('knowledge_index.json','knowledge_index_v1.json')):,} bytes (备份)")


if __name__ == "__main__":
    main()
