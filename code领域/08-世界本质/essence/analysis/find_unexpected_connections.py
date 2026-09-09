#!/usr/bin/env python3
"""
意外跨书连接发现器
对20个核心政治概念进行跨书搜索，发现看似无关的书之间的隐性关联。
"""
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

INDEX_PATH = Path(__file__).parent.parent / "data" / "political-books-extracted" / "knowledge_index.json"
OUTPUT_PATH = Path(__file__).parent / "unexpected-connections.md"

# ── 书名标准化（把同书不同写法归并）──
BOOK_ALIASES = {
    "中国国家治理的制度逻辑 一个组织学研究": "中国国家治理的制度逻辑",
    "以利为利：财政关系与地方政府行为": "以利为利",
    "分析与思考：黄奇帆的复旦经济课.": "分析与思考",
    "卡尔·波普尔：历史决定论的贫困": "历史决定论的贫困",
    "中国社会学经典文库": "费孝通·中国社会学经典文库",
    "置身事内 中国政府与经济发展【复旦经院“毕业课”解读经济生活背后的政府角色。罗永浩、刘格菘、张军、周黎安、王烁联袂推荐】": "置身事内",
    "过渡劳动：平台经济下的外卖骑手": "过渡劳动",
    "钱穆国学作品集：《中国历代政治得失》《国史大纲》《中华文化十二讲》《中国历史精神": "钱穆国学作品集",
    "习近平谈治国理政·第一卷": "习近平谈治国理政（三卷）",
    "习近平谈治国理政·第二卷": "习近平谈治国理政（三卷）",
    "习近平谈治国理政·第三卷": "习近平谈治国理政（三卷）",
    "《习近平谈治国理政》第一卷": "习近平谈治国理政（三卷）",
    "《习近平谈治国理政》第二卷": "习近平谈治国理政（三卷）",
    "《习近平谈治国理政》第三卷": "习近平谈治国理政（三卷）",
    "社会与政治运动讲义（第二版）": "赵鼎新·社会与政治运动讲义",
    "突围 国门初开的岁月": "突围·国门初开的岁月",
    "政治的人生": "王沪宁·政治的人生",
    "美国反对美国": "王沪宁·美国反对美国",
}

def norm_book(name: str) -> str:
    if not name:
        return "?"
    return BOOK_ALIASES.get(name, name)

# ── 加载 ──
def load_index():
    with open(INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)

# ── 20 个查询 ──
QUERIES = [
    ("国家", "在不同书中如何定义国家？"),
    ("权力", "谁的权力理论最有洞察？"),
    ("改革", "改革的阻力来自哪里？"),
    ("稳定", "维稳的代价是什么？"),
    ("腐败", "不同书对腐败根源的不同解释"),
    ("土地", "土地在政治经济中的角色"),
    ("官僚", "官僚制的正面与负面"),
    ("群众", "谁是“群众”？不同时代的定义"),
    ("阶级", "阶级分析在今天还有效吗？"),
    ("民主", "不同书对民主的不同理解"),
    ("自由", "积极自由 vs 消极自由"),
    ("平等", "机会平等 vs 结果平等"),
    ("传统", "传统的正面与负面"),
    ("科学", "科学决策的含义"),
    ("效率", "效率与公平的权衡"),
    ("信任", "国家与社会的信任关系"),
    ("信息", "信息不对称对治理的影响"),
    ("边界", "国家-市场-社会的边界"),
    ("危机", "不同书描述的不同危机"),
    ("未来", "对未来的不同预测"),
]

# ── 工具函数 ──

def is_junk_text(text: str) -> bool:
    """判断一段文本是否是目录/页眉/碎片"""
    if not text or len(text.strip()) < 8:
        return True
    # 目录特征
    if re.search(r'\.{5,}|…{2,}|\.{2,}\s*\d+$', text):
        return True
    # 纯数字/页码
    if re.match(r'^[\d\s\-—p\.]+$', text):
        return True
    # 太短的无意义片段
    clean = text.strip()
    if len(clean) < 12:
        return True
    return False

# 分析性词汇族
ANALYTIC_WORDS = [
    "因为", "所以", "由于", "本质", "根源", "在于", "意味着", "实质", "关键", "核心",
    "悖论", "矛盾", "困境", "张力", "代价", "后果", "反过来", "事实上", "恰恰",
    "取决于", "源于", "导致", "反映", "揭示", "其实质", "其根源", "深层",
]
CONTRAST_WORDS = ["而", "却", "反之", "相反", "并非", "不是", "而是", "看似", "实则", "然而"]

def keyword_density(text: str, keyword: str) -> float:
    """关键词密度 = 出现次数 / (字数/50)。>1 说明关键词是焦点"""
    cnt = text.count(keyword)
    L = max(len(text), 1)
    return cnt / (L / 50.0)

def quality_score(text: str, keyword: str) -> float:
    """评估一段引用的质量分。惩罚「顺带提及」的长文。"""
    score = 0.0
    if is_junk_text(text):
        return -1.0
    L = len(text)
    # 关键词密度：核心判据。密度低说明只是顺带提及
    dens = keyword_density(text, keyword)
    if dens < 0.3 and L > 120:
        # 长文里关键词只出现一次且不密集 → 大概率是顺带提及
        score -= 1.5
    elif dens >= 1.0:
        score += 1.5
    elif dens >= 0.5:
        score += 0.8
    # 长度适中加分（30-180字最优）
    if 30 <= L <= 180:
        score += 2.0
    elif 20 <= L <= 280:
        score += 1.0
    else:
        score += 0.1
    # 关键词出现次数（适度加分）
    cnt = text.count(keyword)
    if 1 <= cnt <= 3:
        score += 1.2
    elif cnt > 3:
        score += 0.4
    # 句子完整性（含标点）
    if re.search(r'[。！？；：]', text):
        score += 1.0
    # 含分析性词汇加分（每个 +0.35，封顶）
    aw = sum(1 for w in ANALYTIC_WORDS if w in text)
    score += min(aw * 0.35, 1.6)
    # 含对比/因果结构
    cw = sum(1 for w in CONTRAST_WORDS if w in text)
    score += min(cw * 0.3, 0.9)
    # 含定义性句式（"X是…"、"X指…"、"X意味着…"）强加分
    if re.search(rf'{keyword}[^。]{{0,12}}(是|指|为|意味着|在于|实质上|本质上)', text):
        score += 1.5
    # 演讲/口号/套话惩罚
    if re.search(r'同志们|希望大家|做出更多|做出更大|贡献|捍卫我们|党中央|号召', text) and dens < 0.8:
        score -= 1.0
    return score

def collect_all_hits(data, keyword):
    """对单个关键词，从所有类型条目中收集命中"""
    kw = keyword.lower()
    hits = []  # list of dict: {text, book, author, page, type, score}

    # 1. 概念定义
    for c in data["concepts"]:
        cname = c.get("concept", "")
        # 概念名匹配
        name_hit = keyword in cname
        for d in c.get("definitions", []):
            text = d.get("text", "")
            if name_hit or kw in text.lower():
                if not is_junk_text(text):
                    hits.append({
                        "text": text,
                        "book": norm_book(d.get("book", "")),
                        "author": d.get("author", ""),
                        "page": d.get("page", ""),
                        "type": "定义",
                        "concept": cname,
                        "score": quality_score(text, keyword) + (1.0 if name_hit else 0),
                    })
        # mentions
        for m in c.get("mentions", []):
            ctx = m.get("context", "")
            if kw in ctx.lower() or name_hit:
                if not is_junk_text(ctx):
                    hits.append({
                        "text": ctx,
                        "book": norm_book(m.get("book", "")),
                        "author": "",
                        "page": m.get("page", ""),
                        "type": "提及",
                        "concept": cname,
                        "score": quality_score(ctx, keyword) * 0.6,
                    })

    # 2. 命题
    for p in data["propositions"]:
        text = p.get("text", "")
        if kw in text.lower():
            if not is_junk_text(text):
                hits.append({
                    "text": text,
                    "book": norm_book(p.get("book", "")),
                    "author": p.get("author", ""),
                    "page": p.get("page", ""),
                    "type": "命题",
                    "concept": "",
                    "score": quality_score(text, keyword) + 0.5,
                    "theme": p.get("theme", ""),
                })

    # 3. 数据
    for d in data["data_points"]:
        text = d.get("text", "")
        if kw in text.lower():
            if not is_junk_text(text):
                hits.append({
                    "text": text,
                    "book": norm_book(d.get("book", "")),
                    "author": "",
                    "page": d.get("page", ""),
                    "type": "数据",
                    "concept": "",
                    "score": quality_score(text, keyword) + 0.3,
                })

    # 4. 案例
    for c in data["cases"]:
        for field in ("name", "summary"):
            text = c.get(field, "")
            if kw in text.lower():
                if not is_junk_text(text):
                    hits.append({
                        "text": text,
                        "book": norm_book(c.get("book", "")),
                        "author": c.get("author", ""),
                        "page": c.get("page", ""),
                        "type": "案例",
                        "concept": "",
                        "score": quality_score(text, keyword) + 0.4,
                    })
                    break

    # 5. 跨书索引
    for cb in data["cross_book_index"]:
        concept = cb.get("concept", "")
        ctx = cb.get("context", "")
        if keyword in concept or kw in ctx.lower():
            if not is_junk_text(ctx):
                hits.append({
                    "text": ctx,
                    "book": norm_book(cb.get("book", "")),
                    "author": "",
                    "page": "",
                    "type": "跨书",
                    "concept": concept,
                    "score": quality_score(ctx, keyword) * 0.7,
                    "total_books": cb.get("total_books", 0),
                })

    return hits

def top_quotes_by_diverse_books(hits, n=3):
    """选出 top N 引用，但尽量来自不同书"""
    # 先过滤掉低质量
    good = [h for h in hits if h["score"] > 0]
    good.sort(key=lambda x: x["score"], reverse=True)
    selected = []
    used_books = set()
    used_texts = set()
    for h in good:
        key = h["text"][:40]
        if key in used_texts:
            continue
        # 优先选不同书
        if h["book"] in used_books and len(selected) < n:
            # 只有当不同书用完才允许同书
            continue
        selected.append(h)
        used_books.add(h["book"])
        used_texts.add(key)
        if len(selected) >= n:
            break
    # 如果还不够，放宽限制
    if len(selected) < n:
        for h in good:
            key = h["text"][:40]
            if key in used_texts:
                continue
            selected.append(h)
            used_texts.add(key)
            if len(selected) >= n:
                break
    return selected[:n]

def book_distribution(hits):
    """统计每本书命中数"""
    c = Counter(h["book"] for h in hits)
    return c

# ── 主分析 ──

def analyze_one(data, keyword, question):
    hits = collect_all_hits(data, keyword)
    dist = book_distribution(hits)
    top_q = top_quotes_by_diverse_books(hits, n=3)

    # 找跨书索引中涉及该书最多的概念
    cross_concepts = []
    for cb in data["cross_book_index"]:
        if keyword in cb.get("concept", "") or keyword in cb.get("keyword", ""):
            cross_concepts.append(cb)
    # 按涉及书数排序
    cross_concepts.sort(key=lambda x: x.get("total_books", 0), reverse=True)

    return {
        "keyword": keyword,
        "question": question,
        "total_hits": len(hits),
        "book_dist": dist,
        "top_quotes": top_q,
        "cross_concepts": cross_concepts[:5],
    }

def render_report(results, data):
    """渲染 markdown"""
    lines = []
    def w(s=""):
        lines.append(s)

    w("# 意外的跨书连接：20 个政治概念的隐性对话")
    w("")
    w(f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    w("> 数据源：`data/political-books-extracted/knowledge_index.json`  ")
    w(f"> 知识库覆盖 {data['metadata']['total_books']} 本书，{data['metadata']['total_entries']} 条目")
    w("")
    w("---")
    w("")
    w("## 阅读指南")
    w("")
    w("这份报告对 20 个政治学核心概念做了跨书搜索。对每个概念，我们：")
    w("1. 统计哪些书涉及它（分布）；")
    w("2. 选出 **3 条跨书的高质量原文引用**（优先来自不同书）；")
    w("3. 标注 **意外连接** —— 看似无关的书在某个概念上形成的隐性对话。")
    w("")
    w("洞察的标准：含因果/对比/悖论结构、指向“本质/根源/矛盾”、不是目录碎片。")
    w("")
    w("---")
    w()

    # 总览矩阵
    w("## 概念 × 书籍 覆盖矩阵（概览）")
    w("")
    all_books_seen = set()
    for r in results:
        for b in r["book_dist"]:
            all_books_seen.add(b)
    # 只保留出现频次较高的书
    book_total = Counter()
    for r in results:
        book_total.update(r["book_dist"])
    main_books = [b for b, _ in book_total.most_common(18)]

    header = "| 概念 | " + " | ".join(b.replace("|", "/")[:8] for b in main_books) + " | 总计 |"
    sep = "|" + "---|" * (len(main_books) + 2)
    w(header)
    w(sep)
    for r in results:
        row = f"| **{r['keyword']}** | "
        cells = []
        for b in main_books:
            cnt = r["book_dist"].get(b, 0)
            cells.append(str(cnt) if cnt > 0 else "·")
        row += " | ".join(cells) + f" | {r['total_hits']} |"
        w(row)
    w("")
    w("---")
    w()

    # 每个查询的详细分析
    for i, r in enumerate(results, 1):
        kw = r["keyword"]
        w(f"## {i:02d}. 「{kw}」 — {r['question']}")
        w("")

        # 分布
        top_books = r["book_dist"].most_common(10)
        total = r["total_hits"]
        w(f"**搜索结果**：共 {total} 条命中，涉及 {len(r['book_dist'])} 本书。")
        w("")
        if top_books:
            w("<details><summary>📊 各书命中分布（点击展开）</summary>")
            w("")
            w("| 书 | 命中数 | 占比 |")
            w("|---|---:|---:|")
            for b, c in top_books:
                pct = c / total * 100 if total else 0
                w(f"| {b} | {c} | {pct:.0f}% |")
            w("")
            w("</details>")
            w("")

        # Top 3 引用
        w("### 最有洞察的 3 条原文引用")
        w("")
        if not r["top_quotes"]:
            w("（本概念在结构化条目中较少，见下方跨书分析。）")
        else:
            for j, q in enumerate(r["top_quotes"], 1):
                text = q["text"].strip()
                # 清理
                text = re.sub(r'\s+', ' ', text)
                if len(text) > 280:
                    text = text[:280] + "…"
                book = q["book"]
                author = q.get("author", "")
                page = q.get("page", "")
                qtype = q["type"]
                concept = q.get("concept", "")
                theme = q.get("theme", "")
                tag = f"**{qtype}**"
                if concept:
                    tag += f" · 概念「{concept}」"
                if theme:
                    tag += f" · 主题「{theme}」"
                src = book
                if author:
                    src = f"{author}《{book}》"
                else:
                    src = f"《{book}》"
                if page:
                    src += f" {page}"
                w(f"**{j}.** {tag}")
                w("")
                w(f"> {text}")
                w("")
                w(f"*—— {src}*")
                w("")
        w("")

        # 意外连接 — 自动推断
        w("### 意外连接")
        w("")
        connection = infer_unexpected_connections(r, data)
        for c in connection:
            w(f"- {c}")
        w("")
        w("---")
        w()

    # ── 综合洞察 ──
    w("## 综合洞察：最意外的跨书发现")
    w("")
    w("把 20 个概念放在一起看，浮现出几条贯穿性的发现：")
    w("")
    syn = build_synthesis(results, data)
    for s in syn:
        w(s)
    w("")

    return "\n".join(lines)

def build_synthesis(results, data):
    """跨所有查询的综合洞察"""
    items = []

    # 1. 哪些"书对"在最多概念上同时出现（最强的隐性连接）
    pair_concepts = defaultdict(set)
    for r in results:
        books = [b for b, c in r["book_dist"].items() if c >= 2]
        for i in range(len(books)):
            for j in range(i + 1, len(books)):
                b1, b2 = sorted([books[i], books[j]])
                t1, _ = tradition_of(b1)
                t2, _ = tradition_of(b2)
                # 只统计跨传统的配对
                if t1 != t2:
                    pair_concepts[(b1, b2)].add(r["keyword"])
    # 排序：共同概念数最多的书对
    top_pairs = sorted(pair_concepts.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    items.append("**连接最密的「跨传统书对」**（在最多概念上同时出现）：")
    items.append("")
    for (b1, b2), concepts in top_pairs:
        t1, _ = tradition_of(b1)
        t2, _ = tradition_of(b2)
        items.append(
            f"  - 《{b1}》（{t1}）↔ 《{b2}》（{t2}）："
            f"在 **{len(concepts)}** 个概念上共鸣"
            f"—— {'、'.join(sorted(concepts))}"
        )
    items.append("")

    # 2. 哪本书是最大的"概念枢纽"（涉及最多概念）
    book_concepts = defaultdict(set)
    for r in results:
        for b, c in r["book_dist"].items():
            if c >= 1:
                book_concepts[b].add(r["keyword"])
    top_hubs = sorted(book_concepts.items(), key=lambda x: len(x[1]), reverse=True)[:6]
    items.append("**概念覆盖最广的书**（涉及最多核心概念）：")
    items.append("")
    for b, concepts in top_hubs:
        t, desc = tradition_of(b)
        items.append(
            f"  - 《{b}》（{t}）：覆盖 **{len(concepts)}/20** 概念"
            f"—— {desc}"
        )
    items.append("")

    # 3. 哪些概念是"跨传统共识"（涉及传统数最多，排除"其他"）
    concept_traditions = {}
    for r in results:
        trads = set()
        for b in r["book_dist"]:
            t, _ = tradition_of(b)
            if t != "其他":
                trads.add(t)
        concept_traditions[r["keyword"]] = trads
    most_spanning = sorted(concept_traditions.items(), key=lambda x: len(x[1]), reverse=True)[:6]
    items.append("**跨传统最广的概念**（被最多不同传统的书讨论）：")
    items.append("")
    for kw, trads in most_spanning:
        items.append(
            f"  - 「{kw}」：覆盖 **{len(trads)}** 个传统"
            f"（{'、'.join(sorted(trads))}）——"
            f"这是真正的「最大公约数」概念，每个传统都绕不开它。"
        )
    items.append("")

    # 4. 最"孤立"的概念（集中在少数传统）
    genuinely_narrow = [(kw, trads) for kw, trads in concept_traditions.items() if len(trads) <= 4]
    genuinely_narrow.sort(key=lambda x: len(x[1]))
    if genuinely_narrow:
        items.append("**最「单一视角」的概念**（≤4 个传统）——这些概念的知识库存在盲区：")
        items.append("")
        for kw, trads in genuinely_narrow:
            items.append(
                f"  - 「{kw}」：仅 {len(trads)} 个传统"
                f"（{'、'.join(sorted(trads))}）——"
                f"缺少古典史学/西方理论等视角的对照，值得补充阅读。"
            )
        items.append("")
    else:
        items.append("**无单一视角概念**：所有 20 个概念都至少被 5 个传统讨论，知识库的视角覆盖较均衡。")
        items.append("")

    return items

# ── 书的"传统/流派"分类，用于发现跨传统的意外对话 ──
BOOK_TRADITION = {
    # 古典 / 传统史学
    "钱穆国学作品集": ("古典史学", "从中国历代政治得失看制度演变的连续性"),
    "万历十五年（经典版）": ("古典史学", "以微观切片揭示宏观制度僵化"),
    "费孝通·中国社会学经典文库": ("本土社会学", "从乡土基层看中国社会结构"),
    # 革命经典 / 官方话语
    "毛泽东文集（全集，共八卷）": ("革命经典", "阶级斗争与群众路线的政治实践"),
    "邓小平文选 第一卷": ("革命经典", "改革开放的实用主义路线"),
    "陈云文选·第一卷": ("革命经典", "计划经济与综合平衡的治理观"),
    "陈云文选·第二卷": ("革命经典", "计划经济与综合平衡的治理观"),
    "陈云文选·第三卷": ("革命经典", "计划经济与综合平衡的治理观"),
    "习近平谈治国理政（三卷）": ("当代官方", "新时代国家治理的顶层设计话语"),
    "突围·国门初开的岁月": ("当代官方", "改革开放前夜的决策内幕"),
    # 当代中国实证研究
    "中国国家治理的制度逻辑": ("当代实证", "从组织学拆解国家治理的中央-地方张力"),
    "转型中的地方政府": ("当代实证", "行政发包与晋升竞争的激励结构"),
    "以利为利": ("当代实证", "财政关系如何塑造地方政府行为"),
    "置身事内": ("当代实证", "政府作为经济主体的微观机制"),
    "分析与思考": ("当代实证", "从政策操盘手视角看经济结构"),
    "过渡劳动": ("当代实证", "平台经济下劳动者的脆弱性"),
    "人地之间：中国增长模式下的城乡土地改革": ("当代实证", "城乡土地制度改革的实证分析"),
    "赵鼎新·社会与政治运动讲义": ("当代实证", "社会运动的机制与国家回应"),
    # 西方理论
    "历史决定论的贫困": ("西方理论", "对历史规律论/整体工程论的哲学批判"),
    "王沪宁·政治的人生": ("西方理论", "比较政治学的日记体思考"),
    "王沪宁·美国反对美国": ("西方理论", "从美国内部看现代性的悖论"),
}

def tradition_of(book):
    return BOOK_TRADITION.get(book, ("其他", ""))

# 传统之间的"对话距离"——距离越大，连接越意外
TRADITION_DISTANCE = {
    ("古典史学", "革命经典"): 4,
    ("古典史学", "当代官方"): 4,
    ("古典史学", "西方理论"): 5,
    ("古典史学", "当代实证"): 3,
    ("本土社会学", "西方理论"): 4,
    ("本土社会学", "当代实证"): 2,
    ("革命经典", "当代实证"): 3,
    ("革命经典", "西方理论"): 5,
    ("当代官方", "西方理论"): 4,
    ("当代官方", "古典史学"): 4,
    ("当代实证", "西方理论"): 3,
}

def dialogue_distance(b1, b2):
    t1, _ = tradition_of(b1)
    t2, _ = tradition_of(b2)
    if t1 == t2:
        return 1
    return TRADITION_DISTANCE.get((t1, t2), TRADITION_DISTANCE.get((t2, t1), 2))

def tradition_closing(t1, t2, kw):
    """根据两个传统的具体组合，给出不同的收尾观察。"""
    pair = tuple(sorted([t1, t2]))
    pair_rev = (pair[1], pair[0])
    closings = {
        ("古典史学", "革命经典"):
            f"古典史家看到的是「{kw}」在两千年制度中的惯性，革命经典要打破的正是这种惯性——同一概念，一个是诊断，一个是处方。",
        ("古典史学", "当代官方"):
            f"历代政治得失的总结，与当代顶层设计的话语，在「{kw}」上形成跨越千年的回响：哪些是老问题的新包装？",
        ("古典史学", "西方理论"):
            f"中国历史的内在逻辑与西方理论的抽象框架，在「{kw}」上互相检验——西方概念能否解释中国经验？",
        ("古典史学", "当代实证"):
            f"古典史学的宏观判断与当代实证的微观机制，在「{kw}」上互为表里：历史给出现律，实证给出因果。",
        ("本土社会学", "西方理论"):
            f"费孝通式的乡土洞察与西方理论的普世主张，在「{kw}」上形成「地方性知识 vs 普遍规律」的张力。",
        ("本土社会学", "当代实证"):
            f"乡土社会的底色与当代治理的表层，在「{kw}」上连续——理解今日中国，绕不开基层社会的逻辑。",
        ("革命经典", "当代实证"):
            f"革命经典的宏大叙事与当代实证的机制拆解，在「{kw}」上形成「应然 vs 实然」的对照。",
        ("革命经典", "西方理论"):
            f"中国革命的政治直觉与西方学院的理论批判，在「{kw}」上殊途同归或针锋相对——一个从实践中提炼，一个从逻辑中推演。",
        ("当代官方", "西方理论"):
            f"官方话语的实践逻辑与西方理论的批判视角，在「{kw}」上构成「治理经验 vs 规范判断」的对话。",
        ("当代实证", "西方理论"):
            f"当代实证揭示的中国机制与西方理论提供的分析工具，在「{kw}」上形成「经验发现 vs 理论预设」的互补。",
    }
    return closings.get(pair, closings.get(pair_rev, f"两种传统在「{kw}」上形成隐性对话。"))

def infer_unexpected_connections(r, data):
    """发现真正意外的跨书连接：找对话距离最远的书对，并给出具体观察。"""
    conns = []
    kw = r["keyword"]
    dist = r["book_dist"]

    books_here = [b for b, _ in dist.most_common(15)]
    if len(books_here) < 2:
        conns.append(f"「{kw}」主要集中在单一来源，跨书对话较少。")
        return conns

    # ① 找"对话距离"最远的书对（最意外的连接）
    pairs = []
    for i in range(len(books_here)):
        for j in range(i + 1, len(books_here)):
            b1, b2 = books_here[i], books_here[j]
            d = dialogue_distance(b1, b2)
            # 距离 × 双方命中数（保证不只是远，也要有实质讨论）
            weight = d * (dist[b1] + dist[b2]) ** 0.5
            pairs.append((weight, d, b1, b2))
    pairs.sort(reverse=True)

    shown_pairs = set()
    pair_count = 0
    for weight, d, b1, b2 in pairs:
        if pair_count >= 2:
            break
        key = tuple(sorted([b1, b2]))
        if key in shown_pairs:
            continue
        if d < 3:  # 只报距离≥3的（足够意外）
            continue
        shown_pairs.add(key)
        t1, desc1 = tradition_of(b1)
        t2, desc2 = tradition_of(b2)
        conns.append(
            f"**{t1} ↔ {t2}**（对话距离 {d}/5）："
            f"《{b1}》（{desc1}，{dist[b1]}次）与《{b2}》（{desc2}，{dist[b2]}次）"
            f"都聚焦「{kw}」。{tradition_closing(t1, t2, kw)}"
        )
        pair_count += 1

    # ② 跨书索引：本概念被多少不同传统的书讨论（去重）
    seen_cross = set()
    if r["cross_concepts"]:
        for cc in r["cross_concepts"][:3]:
            concept = cc.get("concept", "")
            tb = cc.get("total_books", 0)
            ck = (concept, tb)
            if ck in seen_cross or tb < 4:
                continue
            seen_cross.add(ck)
            book = norm_book(cc.get("book", ""))
            t, _ = tradition_of(book)
            conns.append(
                f"**跨学派共识**：「{concept}」在 {tb} 本书中被讨论"
                f"（含「{t}」传统），说明它不是某一派的专利，而是跨传统的共同问题意识。"
            )

    # ③ 定义对照：同一概念在不同传统的书里如何被界定
    exact_defs = []
    for c in data["concepts"]:
        if c.get("concept", "") == kw:
            for d in c.get("definitions", []):
                txt = d.get("text", "")
                if not is_junk_text(txt) and len(txt) > 15:
                    b = norm_book(d.get("book", ""))
                    t, _ = tradition_of(b)
                    exact_defs.append((t, b, txt[:50]))
    if len(exact_defs) >= 2:
        traditions = {t for t, _, _ in exact_defs}
        if len(traditions) >= 2:
            sample = "；".join(f"「{t}」《{b}》：『{t2}…』" for t, b, t2 in exact_defs[:3])
            conns.append(
                f"**定义分岔**：同一个「{kw}」，不同传统给出了不同界定——{sample}。"
                f"这种分歧本身就是理解该概念的关键。"
            )

    # ④ 兜底：若以上都没产出，给一个基于 top quotes 的观察
    if not conns and r["top_quotes"]:
        qs = r["top_quotes"]
        traditions_q = {tradition_of(q["book"])[0] for q in qs}
        if len(traditions_q) >= 2:
            conns.append(
                f"**多视角**：top 引用分别来自 {len(traditions_q)} 个传统"
                f"（{'、'.join(traditions_q)}），显示「{kw}」是一个跨传统的交叉概念。"
            )
    if not conns:
        conns.append(f"「{kw}」在知识库中的跨传统对话较少，可尝试扩展检索词。")

    return conns[:4]

# ── 主 ──
def main():
    data = load_index()
    results = [analyze_one(data, kw, q) for kw, q in QUERIES]
    md = render_report(results, data)
    OUTPUT_PATH.write_text(md, encoding="utf-8")
    print(f"✅ 已生成: {OUTPUT_PATH}")
    print(f"   {len(results)} 个查询，{sum(r['total_hits'] for r in results)} 条总命中")
    # 简短预览
    for r in results:
        print(f"   - 「{r['keyword']}」: {r['total_hits']} 命中, "
              f"{len(r['book_dist'])} 本书, top quotes {len(r['top_quotes'])}")

if __name__ == "__main__":
    main()
