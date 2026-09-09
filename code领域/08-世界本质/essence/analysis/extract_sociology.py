#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从《中国社会学经典文库》epub JSON 中提取7部著作的核心内容。
输出: sociology-classics-analysis.md
"""
import json, re, os

SRC = '/mnt/c/workspace/essence/data/political-books-extracted/epub_677b2a39917dfc890ce34c57eb3b159f.json'
OUT = '/mnt/c/workspace/essence/analysis/sociology-classics-analysis.md'

with open(SRC, encoding='utf-8') as fh:
    data = json.load(fh)
PAGES = data['full_text']

def book_text(start, end):
    """Concatenate pages [start, end)."""
    parts = []
    for i in range(start, end):
        parts.append(PAGES[i]['text'])
    return '\n\n'.join(parts)

# Book ranges (版权/书名页 boundaries discovered)
BOOKS = {
    'jinyi': {
        'title': '金翼：一个中国家族的史记',
        'author': '林耀华',
        'start': 2, 'end': 28,
        'keywords': ['黄东林','张芬洲','东林','芬洲','金翼','黄村','店铺','关系','家族','宗族',
                     '平衡','命运','人际','亲属','商铺','福州','湖口','风水','坟墓','争吵','合作'],
    },
    'fei': {
        'title': '美好社会与美美与共：费孝通对现时代的思考',
        'author': '费孝通',
        'start': 28, 'end': 61,
        'keywords': ['差序格局','文化自觉','美美与共','美好社会','江村','乡土中国','小城镇',
                     '社区研究','民族','多元一体','志在富民','城乡','现代化','小康社会','基层'],
    },
    'wang': {
        'title': '社会变革与婚姻家庭变动：20世纪30—90年代的冀南农村',
        'author': '王跃生（任务标注为阎云翔，实为王跃生）',
        'start': 61, 'end': 78,
        'keywords': ['婚姻','家庭','冀南','土改','集体化','包产到户','初婚','再婚','父母主婚',
                     '彩礼','分家','核心家庭','宗族','生育','变动','革命','制度'],
    },
    'lu': {
        'title': '陆学艺文萃',
        'author': '陆学艺',
        'start': 78, 'end': 107,
        'keywords': ['三农','农民','阶层','社会分层','中产','包产到户','芦城','农村经济',
                     '社会结构','贫富','城乡','土地','流动','农民工','十大阶层'],
    },
    'he': {
        'title': '乡村治理的社会基础',
        'author': '贺雪峰',
        'start': 107, 'end': 138,
        'keywords': ['村庄','村干部','乡村治理','社会关联','半熟人社会','选举','村庄秩序',
                     '村级','宗族','派系','公共品','村民自治','荆门','理性化','田野'],
    },
    'liyoumei': {
        'title': '组织社会学与决策分析',
        'author': '李友梅',
        'start': 138, 'end': 148,
        'keywords': ['组织','决策','科层','理性','权力','集体行动','组织研究','复杂化',
                     '正式组织','非正式','协调','控制','制度','结构'],
    },
    'danwei': {
        'title': '中国的单位组织：资源、权力与交换',
        'author': '李路路、李汉林',
        'start': 148, 'end': 164,
        'keywords': ['单位','单位制','单位组织','工作单位','资源','权力','交换','依赖',
                     '身份','福利','再分配','单位社会','制度','调查','问卷'],
    },
}

def clean(s):
    """Clean a text snippet for display."""
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def split_sentences(text):
    """Split Chinese text into sentences."""
    # Split on Chinese punctuation, keep delimiters
    parts = re.split(r'(?<=[。！？；])', text)
    return [p.strip() for p in parts if p.strip()]

def find_passages(text, keywords, min_len=30, max_len=400):
    """Find sentences/passages containing keywords."""
    sentences = split_sentences(text)
    seen = set()
    hits = []
    for sent in sentences:
        if len(sent) < min_len or len(sent) > max_len:
            continue
        for kw in keywords:
            if kw in sent:
                key = sent[:40]
                if key not in seen:
                    seen.add(key)
                    hits.append((kw, sent))
                break
    return hits

def find_definitions(text, concept_patterns):
    """Find definitional passages: 'X是...', 'X指...', '所谓X...', 'X，即...'."""
    results = []
    for concept, patterns in concept_patterns.items():
        for pat in patterns:
            for m in re.finditer(pat, text):
                start = max(0, m.start() - 10)
                end = min(len(text), m.end() + 250)
                snippet = clean(text[start:end])
                results.append((concept, snippet))
    return results

# ============ Concept definitions per book ============
CONCEPTS = {
    'jinyi': {
        '平衡/人际关系均衡': [r'平衡[^。]{0,200}', r'均衡[^。]{0,200}'],
        '关系网络': [r'关系网络[^。]{0,200}', r'人际[^。]{0,200}'],
        '家族/宗族': [r'家族[^。]{0,180}', r'宗族[^。]{0,180}'],
        '金翼之家': [r'金翼[^。]{0,180}'],
        '命运与人为': [r'命运[^。]{0,180}', r'人为[^。]{0,180}'],
    },
    'fei': {
        '差序格局': [r'差序格局[^。]{0,220}'],
        '文化自觉': [r'文化自觉[^。]{0,220}'],
        '美美与共': [r'美美与共[^。]{0,200}', r'各美其美[^。]{0,200}'],
        '美好社会': [r'美好社会[^。]{0,200}'],
        '多元一体': [r'多元一体[^。]{0,200}', r'中华民族多元一体[^。]{0,180}'],
        '小城镇': [r'小城镇[^。]{0,180}'],
        '乡土/社区研究': [r'社区研究[^。]{0,180}', r'乡土[^。]{0,150}'],
    },
    'wang': {
        '婚姻变动': [r'婚姻[^。]{0,180}'],
        '家庭结构变动': [r'家庭[^。]{0,180}', r'核心家庭[^。]{0,150}'],
        '父母主婚': [r'父母主婚[^。]{0,180}', r'主婚[^。]{0,150}'],
        '土改对婚姻影响': [r'土改[^。]{0,180}'],
        '集体化': [r'集体化[^。]{0,180}'],
        '分家': [r'分家[^。]{0,180}'],
    },
    'lu': {
        '社会分层/阶层': [r'社会分层[^。]{0,200}', r'阶层[^。]{0,150}'],
        '十大阶层': [r'十大阶层[^。]{0,200}'],
        '三农问题': [r'三农[^。]{0,180}'],
        '包产到户': [r'包产到户[^。]{0,180}'],
        '中产阶层': [r'中产[^。]{0,180}'],
        '社会结构': [r'社会结构[^。]{0,180}'],
    },
    'he': {
        '社会关联': [r'社会关联[^。]{0,220}'],
        '半熟人社会': [r'半熟人社会[^。]{0,220}'],
        '村庄秩序': [r'村庄秩序[^。]{0,200}', r'秩序[^。]{0,150}'],
        '乡村治理': [r'乡村治理[^。]{0,200}'],
        '村庄社会基础': [r'社会基础[^。]{0,180}'],
        '派系/宗族': [r'派系[^。]{0,150}', r'宗族[^。]{0,150}'],
    },
    'liyoumei': {
        '组织研究': [r'组织研究[^。]{0,200}', r'组织社会学[^。]{0,180}'],
        '决策': [r'决策[^。]{0,180}'],
        '科层/官僚制': [r'科层[^。]{0,180}', r'官僚制[^。]{0,180}'],
        '理性化': [r'理性[^。]{0,150}'],
        '集体行动': [r'集体行动[^。]{0,180}'],
        '正式/非正式': [r'正式组织[^。]{0,150}', r'非正式[^。]{0,150}'],
    },
    'danwei': {
        '单位/单位制': [r'单位组织[^。]{0,200}', r'单位制[^。]{0,180}', r'单位社会[^。]{0,180}'],
        '资源与权力交换': [r'权力[^。]{0,120}资源[^。]{0,120}', r'交换[^。]{0,150}'],
        '依赖性': [r'依赖[^。]{0,180}'],
        '再分配': [r'再分配[^。]{0,180}'],
        '身份/福利': [r'福利[^。]{0,150}', r'身份[^。]{0,120}'],
    },
}

# ============ Build analysis ============
out = []
out.append("# 《中国社会学经典文库》七部著作深度分析\n")
out.append("> 数据源：`data/political-books-extracted/epub_677b2a39917dfc890ce34c57eb3b159f.json`\n")
out.append("> 全文库共 387 万字，本分析聚焦任务指定的 7 部著作，以原文引用为主。\n")
out.append("> 提取方法：Python 按书名页/版权页定位每部著作的页范围，再用关键词与定义句式正则检索原文段落。\n\n")

out.append("## 说明：作者更正\n")
out.append("> 任务将第 3 部《社会变革与婚姻家庭变动》标注为阎云翔著。经核验原文书名页，")
out.append('> 该书实为 **王跃生** 著（副标题「20世纪30—90年代的冀南农村」）。')
out.append("> 阎云翔的代表作是《礼物的流动》《私人生活的变革》（写下岬村）。本分析按实际作者处理。\n\n")

out.append("---\n\n")

# Process each book
for idx, (key, bk) in enumerate(BOOKS.items(), 1):
    text = book_text(bk['start'], bk['end'])
    char_count = len(text)
    out.append(f"## 第{idx}部 《{bk['title']}》（{bk['author']}）\n")
    out.append(f"### 基本信息\n")
    out.append(f"- **页范围**：page {bk['start']}–{bk['end']-1}（共 {bk['end']-bk['start']} 页）")
    out.append(f"- **正文字数**：约 {char_count:,} 字\n")

    # --- 核心概念/理论 ---
    out.append("### 核心概念/理论（原文）\n")
    concepts = CONCEPTS.get(key, {})
    def_hits = []
    seen_snip = set()
    for concept, patterns in concepts.items():
        found_for_concept = False
        for pat in patterns:
            for m in re.finditer(pat, text):
                s = max(0, m.start()-5)
                e = min(len(text), m.end()+220)
                snip = clean(text[s:e])
                if snip[:30] in seen_snip:
                    continue
                seen_snip.add(snip[:30])
                def_hits.append((concept, snip))
                found_for_concept = True
                break  # one per pattern
            if found_for_concept:
                break
    for concept, snip in def_hits:
        out.append(f"- **{concept}**：\n  > {snip}\n")

    # --- 核心论点 (search for argumentative sentences) ---
    out.append("### 核心论点（原文）\n")
    # Argument markers: '认为', '指出', '本质上', '关键在于', '重要', '必须', '在于'
    arg_patterns = [
        r'本质[上]?[是就][^。]{20,200}',
        r'关键[在是][^。]{20,200}',
        r'根源[在是][^。]{20,200}',
        r'(?:认为|指出|强调)[^。]{25,200}',
        r'(?:因此|所以|可见|由此)[，,][^。]{25,200}',
        r'(?:重要|核心|根本)[的是][^。]{20,200}',
        r'(?:不是|并非)[^。]{15,}[，,]而[是是][^。]{15,200}',
        r'(?:只有|必须)[^。]{15,200}',
    ]
    arg_hits = []
    seen_arg = set()
    for pat in arg_patterns:
        for m in re.finditer(pat, text):
            s = max(0, m.start()-15)
            e = min(len(text), m.end()+30)
            snip = clean(text[s:e])
            if len(snip) < 35 or len(snip) > 350:
                continue
            if snip[:35] in seen_arg:
                continue
            # require a keyword present
            if not any(kw in snip for kw in bk['keywords']):
                continue
            seen_arg.add(snip[:35])
            arg_hits.append(snip)
        if len(arg_hits) >= 12:
            break
    # dedupe and pick distinct ones
    for snip in arg_hits[:8]:
        out.append(f"> {snip}\n")

    # --- 关键案例/数据 ---
    out.append("### 关键案例/数据（原文）\n")
    data_patterns = [
        r'\d{2,4}[％%][^。]{0,150}',
        r'\d{2,}[\s ]*(?:户|人|个|万|元|亩|岁)[^。]{10,150}',
        r'(?:调查|调查数据|样本|统计|问卷)[^。]{20,180}',
        r'(?:例如|比如|案例|个案|如)[^。]{25,200}',
        r'(?:19\d{2}|20\d{2})年[^。]{15,180}',
    ]
    data_hits = []
    seen_data = set()
    for pat in data_patterns:
        for m in re.finditer(pat, text):
            s = max(0, m.start()-10)
            e = min(len(text), m.end()+20)
            snip = clean(text[s:e])
            if len(snip) < 30 or len(snip) > 280:
                continue
            if snip[:30] in seen_data:
                continue
            seen_data.add(snip[:30])
            data_hits.append(snip)
        if len(data_hits) >= 6:
            break
    for snip in data_hits[:5]:
        out.append(f"> {snip}\n")

    # --- 补充原文引用（确保每部至少15条） ---
    # Collect more distinctive passages via keyword hits
    all_hits = find_passages(text, bk['keywords'], min_len=40, max_len=320)
    existing = set()
    for snip in [d[1] for d in def_hits] + arg_hits + data_hits:
        existing.add(snip[:30])

    out.append("### 更多原文要点（关键词检索）\n")
    extra = []
    for kw, sent in all_hits:
        if sent[:30] in existing:
            continue
        existing.add(sent[:30])
        extra.append((kw, sent))
        if len(extra) >= 8:
            break
    for kw, sent in extra:
        out.append(f"> 〔{kw}〕{sent}\n")

    total_quotes = len(def_hits) + min(len(arg_hits),8) + min(len(data_hits),5) + len(extra)
    out.append(f"\n*本部累计原文引用 {total_quotes} 条。*\n")

    # --- 与essence项目关联 ---
    out.append("### 与 essence 项目关联\n")
    relations = {
        'jinyi': '人际关系均衡论可映射到 essence 的"系统/反馈/稳态"概念簇；'
                 '黄东林-张芬洲家族兴衰是"初始条件敏感+关系网络重构"的案例，'
                 '可纳入 `knowledge-graph/connections.md` 中"社会网络 ⇄ 复杂系统"的连接。',
        'fei': '"差序格局"是理解中国人际结构的底层模型，可对照物理学"引力场/势能"与'
               '信息论"距离度量"；"文化自觉"与 essence 的"第一性原理追问"方法论同构——'
               '都是先认清自身的预设再谈超越。',
        'wang': '婚姻家庭制度随土地制度/政治运动剧变，是"制度突变 ⇒ 结构相变"的'
                '社会学样本，可纳入 `08-cross-cutting/` 的"相变/突变"映射，'
                '对照物理学的相变与生物学的间断平衡。',
        'lu': '社会分层与"十大阶层"是社会结构的纵向切面；"三农"问题可连接到'
              'essence 中"系统层次/涌现"——一个阶层结构的整体性质不可还原为个体。',
        'he': '"半熟人社会""社会关联"是对村庄这一中观系统的刻画，可连接到'
              'essence 的"复杂适应系统"主题；村庄秩序的生成机制是自组织 vs 外部控制的张力。',
        'liyoumei': '组织研究的理性化/科层化主题，可对照 essense 中"控制论/反馈"'
                    '与"信息论"：正式结构是显性规则，非正式网络是隐性信息流。',
        'danwei': '单位制是"资源-权力-交换"的封闭子系统，可对照热力学的"封闭系统/熵"'
                  '与经济学的"再分配 vs 市场"；单位的"依赖性"是社会层面的"路径依赖"。',
    }
    out.append(f"{relations[key]}\n")

    out.append("\n---\n\n")

# Write
result = '\n'.join(out)
with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write(result)

print(f"Written {len(result)} chars to {OUT}")
print(f"Total quotes collected.")

# Stats per book
print("\n=== 引用条数统计 ===")
for key, bk in BOOKS.items():
    text = book_text(bk['start'], bk['end'])
    n_def = sum(len(v) for v in CONCEPTS.get(key,{}).values())
    hits = find_passages(text, bk['keywords'], 40, 320)
    print(f"  {bk['title'][:20]:24s}: {len(hits):3d} keyword hits, concept patterns={n_def}")
