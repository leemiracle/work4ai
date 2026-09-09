#!/usr/bin/env python3
"""
跨书论证链条重建 — 最终生成脚本
从知识库 + 全文中提取原文，按5个主题的论证逻辑组织，
输出 /mnt/c/workspace/essence/analysis/cross-book-argument-chains.md
"""
import json, re, os
from collections import defaultdict

DATA = '/mnt/c/workspace/essence/data/political-books-extracted'
OUT  = '/mnt/c/workspace/essence/analysis/cross-book-argument-chains.md'

# ═══════════════════════════════════════════════════════════
# 1. 加载全文（带文本归一化）
# ═══════════════════════════════════════════════════════════

def normalize(text):
    """归一化：移除中文字符间的多余空格"""
    t = re.sub(r'(?<=[\u4e00-\u9fff，。、；：！？""''（）《》【】〔〕])\s+(?=[\u4e00-\u9fff，。、；：！？""''（）《》【】〔〕])', '', text)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

FILE_MAP = {
    '26cf383bac61.json': ('中国国家治理的制度逻辑', '周雪光'),
    'e0abe75fbd8d.json': ('转型中的地方政府', '周黎安'),
    '48c534c19594.json': ('习近平谈治国理政·第三卷', '习近平'),
    '06277bb26b53.json': ('习近平谈治国理政·第二卷', '习近平'),
    '09fc2812dff9.json': ('习近平谈治国理政·第一卷', '习近平'),
    'f3d6472b9789.json': ('以利为利', '周飞舟'),
    'f6033221fa1d.json': ('分析与思考', '黄奇帆'),
    'bdf7f491db6b.json': ('过渡劳动', '孙萍'),
    '231c14cd7e6c.json': ('历史决定论的贫困', '波普尔'),
    'd04c58fc9b3f.json': ('陈云文选·第一卷', '陈云'),
    'b2e287a41416.json': ('陈云文选·第二卷', '陈云'),
    '23b66adb7b4d.json': ('陈云文选·第三卷', '陈云'),
    '26887183017c.json': ('钱穆国学作品集', '钱穆'),
    'dd8e3fd4cdd5.json': ('政治的人生', '王沪宁'),
    'f9318869c29c.json': ('突围·国门初开的岁月', '李岚清'),
    'epub_e077fb766e516aebbf6ad28d9cf81a48.json': ('毛泽东文集', '毛泽东'),
    'epub_0695ef24be80eecef2179ca7122c88a9.json': ('邓小平文选', '邓小平'),
    'epub_677b2a39917dfc890ce34c57eb3b159f.json': ('费孝通文集', '费孝通'),
    'epub_05314f688e0d76c44aa385c98f502f93.json': ('万历十五年', '黄仁宇'),
    'epub_fc25bf25f43b22b0ef1ac62c8642850a.json': ('置身事内', '兰小欢'),
    'mobi_f124b57a8baef3d0e363c9ee9ebcb01a.json': ('人类简史', '赫拉利'),
}

BOOKS = {}  # name → [(loc, norm_text)]
for fn, (bname, author) in FILE_MAP.items():
    fp = os.path.join(DATA, fn)
    if not os.path.exists(fp): continue
    try:
        with open(fp, encoding='utf-8') as f:
            d = json.load(f)
        ft = d.get('full_text', [])
        pages = []
        if isinstance(ft, list):
            for item in ft:
                if isinstance(item, dict):
                    raw = item.get('text', '')
                    if not raw or len(raw.strip()) < 10: continue
                    nt = normalize(raw)
                    if item.get('page'):
                        loc = f"p{item['page']}"
                    elif item.get('file'):
                        loc = item['file'].split('/')[-1].replace('.html','').replace('.xhtml','')
                    else:
                        loc = '?'
                    pages.append((loc, nt))
        if pages:
            BOOKS[bname] = pages
    except Exception as e:
        print(f'WARN {fn}: {e}')

print(f'Loaded {len(BOOKS)} books')

# ═══════════════════════════════════════════════════════════
# 2. 加载知识库
# ═══════════════════════════════════════════════════════════
with open(os.path.join(DATA, 'knowledge_index.json'), encoding='utf-8') as f:
    KI = json.load(f)

def ki_search(keywords, books=None, types=None, limit=5):
    """在知识库中搜索"""
    types = types or ['propositions','concepts','data_points','cases']
    results = []
    for etype in types:
        for item in KI.get(etype, []):
            if etype == 'concepts':
                for d in item.get('definitions', []):
                    txt = d.get('text','')
                    bk = d.get('book','')
                    if books and not any(b in bk for b in books): continue
                    if any(kw in txt for kw in keywords):
                        results.append({
                            'type':'定义','book':bk,'author':d.get('author',''),
                            'page':d.get('page',''),'text':txt.strip()[:400],
                            'concept':item.get('concept','')
                        })
            else:
                txt = item.get('text', item.get('summary',''))
                bk = item.get('book','')
                if books and not any(b in bk for b in books): continue
                if any(kw in txt for kw in keywords):
                    lbl = {'propositions':'命题','data_points':'数据','cases':'案例'}[etype]
                    results.append({
                        'type':lbl,'book':bk,'page':item.get('page',''),
                        'text':txt.strip()[:400],
                        'concept': item.get('name','') if etype=='cases' else ''
                    })
    return results[:limit]

# ═══════════════════════════════════════════════════════════
# 3. 全文搜索（归一化后）
# ═══════════════════════════════════════════════════════════

def ft_search(book_names, keywords, ctx=250, max_hits=6, min_dist=80):
    """在全文中搜索关键词，返回去重后的上下文段落"""
    results = []
    for bn in book_names:
        if bn not in BOOKS: continue
        seen_positions = []
        for loc, text in BOOKS[bn]:
            for kw in keywords:
                idx = text.find(kw)
                while idx != -1:
                    # Distance check to avoid overlapping
                    if all(abs(idx - sp) > min_dist for sp in seen_positions):
                        seen_positions.append(idx)
                        start = max(0, idx - ctx)
                        end = min(len(text), idx + len(kw) + ctx)
                        snippet = text[start:end].strip()
                        results.append({
                            'book': bn, 'loc': loc, 'kw': kw, 'text': snippet
                        })
                        if len([r for r in results if r['book']==bn]) >= max_hits:
                            break
                    idx = text.find(kw, idx + len(kw))
                if len([r for r in results if r['book']==bn]) >= max_hits:
                    break
            if len([r for r in results if r['book']==bn]) >= max_hits:
                break
    return results


def best(results, n=3):
    """选出最有信息量的n条（优先较长且包含更多关键词的）"""
    if not results: return []
    scored = []
    for i, r in enumerate(results):
        score = len(r['text'])
        scored.append((score, -i, r))  # -i for stable sort
    scored.sort(reverse=True)
    return [r for _, _, r in scored[:n]]


def cite(r):
    """格式化引用"""
    book = r.get('book','')
    loc = r.get('loc', r.get('page',''))
    text = r.get('text','').strip()
    loc_str = f" {loc}" if loc else ""
    return f"> **[{book}{loc_str}]**　{text}"


# ═══════════════════════════════════════════════════════════
# 4. 生成 Markdown
# ═══════════════════════════════════════════════════════════

md = []
md.append("# 跨书论证链条重建——五个核心主题")
md.append("")
md.append("> 本文档从 21 本政治学著作的全文与结构化知识库中提取原文引用，")
md.append("> 按论证逻辑（前提→推理→结论→反驳→补充）组织成五条跨书论证链条。")
md.append(f"> 数据源：`knowledge_index.json`（{KI['metadata']['total_entries']}条）+ 全文 JSON（{len(BOOKS)}本）。")
md.append(">")
md.append("> **逻辑关系标记**：`→前提` `→推理` `→转折(但是)` `→结论` `→反驳` `→补充`")
md.append("")

# ── 主题1 ─────────────────────────────────────────────────
md.append("---")
md.append("")
md.append("## 主题一：央地关系的演变——从毛泽东到习近平")
md.append("")
md.append("**论证骨架：**")
md.append("```")
md.append("毛泽东《论十大关系》(1956) → 发挥中央和地方两个积极性")
md.append("  ↓ →但是")
md.append("邓小平 → 放权让利 → 财政包干制（权力过于集中是弊端）")
md.append("  ↓ →但是")
md.append("1994分税制 → 中央财权集中 → 地方财政困境")
md.append("  ↓ →因此")
md.append("周飞舟 → 土地财政是地方在分税制后的自救")
md.append("  ↓ →理论提升")
md.append("周雪光 → 一统体制 vs 有效治理 = 基本矛盾")
md.append("  ↓ →激励机制")
md.append("周黎安 → 行政发包制 + 晋升锦标赛 = 行为逻辑")
md.append("  ↓ →新阶段")
md.append("习近平 → 国家治理体系和治理能力现代化")
md.append("```")
md.append("")

# --- 1a. 毛泽东 ---
md.append('### 环节① 毛泽东《论十大关系》(1956)——"发挥两个积极性"')
md.append("**【逻辑角色：起点/前提】** 中央与地方关系是中国治理的基本张力，毛泽东首次系统论述。")
md.append("")

hits = ft_search(['毛泽东文集'], ['十大关系','中央和地方的关系','两个积极性','发挥中央和地方'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→前提` {cite(r)}")
    md.append("")

# Search for the specific passage about 中央和地方关系 in 十大关系
hits2 = ft_search(['毛泽东文集'], ['处理好中央和地方', '发挥两个积极性', '两个积极性'], max_hits=6)
for r in best(hits2, 2):
    if '十大关系' in r['text'] or '积极性' in r['text']:
        md.append(f"- `→前提` {cite(r)}")
        md.append("")

# Mao on power decentralization
hits3 = ft_search(['毛泽东文集'], ['大权独揽','小权分散','应当在巩固中央统一领导的前提下'], max_hits=4)
for r in best(hits3, 2):
    md.append(f"- `→补充` {cite(r)}")
    md.append("")

# --- 1b. 邓小平 ---
md.append('### 环节② 邓小平——放权让利，"权力过于集中"是弊端')
md.append("**【逻辑角色：推理/转折(但是)】** 毛泽东提出两个积极性，但权力实际仍高度集中；邓小平将放权作为改革突破口。")
md.append("")

hits = ft_search(['邓小平文选'], ['权力过于集中','权力下放','放权','下放权力'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

hits2 = ft_search(['邓小平文选'], ['太集中','统得太死','过分集中'], max_hits=5)
for r in best(hits2, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# Deng on fiscal reform
hits3 = ft_search(['邓小平文选'], ['财政体制','体制改革','包干'], max_hits=5)
for r in best(hits3, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# --- 1c. 周飞舟 ---
md.append("### 环节③ 周飞舟——分税制后土地财政是地方自救")
md.append("**【逻辑角色：推理/转折(但是)】** 1994年分税制集中财权→地方财政困难→以土地出让金弥补，催生土地财政。")
md.append("")

hits = ft_search(['以利为利'], ['分税制','分税制改革'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

hits2 = ft_search(['以利为利'], ['土地财政','土地出让','土地出让金'], max_hits=6)
for r in best(hits2, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

ki = ki_search(['分税制','土地财政','事权','财权'], books=['以利为利'])
for r in ki[:3]:
    md.append(f'- `→补充[{r["type"]}]` {cite(r)}')
    md.append("")

# --- 1d. 周雪光 ---
md.append("### 环节④ 周雪光——一统体制 vs 有效治理：基本矛盾")
md.append("**【逻辑角色：推理/理论提升】** 上述具体制度变迁背后，存在一统体制与有效治理之间的结构性矛盾。")
md.append("")

hits = ft_search(['中国国家治理的制度逻辑'], ['一统体制','有效治理','基本矛盾','中央管辖权'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

hits2 = ft_search(['中国国家治理的制度逻辑'], ['运动型治理','运动式治理','变通','共谋'], max_hits=6)
for r in best(hits2, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

ki = ki_search(['一统体制','有效治理','运动型治理','变通'], books=['中国国家治理'])
for r in ki[:3]:
    md.append(f'- `→补充[{r["type"]}]` {cite(r)}')
    md.append("")

# --- 1e. 周黎安 ---
md.append("### 环节⑤ 周黎安——行政发包制 + 晋升锦标赛")
md.append("**【逻辑角色：推理/激励机制】** 为什么地方政府在压力下仍然高效运转？因为行政发包制和晋升锦标赛提供了强激励。")
md.append("")

hits = ft_search(['转型中的地方政府'], ['行政发包制'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

hits2 = ft_search(['转型中的地方政府'], ['晋升锦标赛','锦标赛','政治锦标赛'], max_hits=6)
for r in best(hits2, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

ki = ki_search(['行政发包制','晋升锦标赛','锦标赛'], books=['转型中的地方政府'])
for r in ki[:3]:
    md.append(f'- `→补充[{r["type"]}]` {cite(r)}')
    md.append("")

# --- 1f. 习近平 ---
md.append("### 环节⑥ 习近平——国家治理体系和治理能力现代化")
md.append("**【逻辑角色：结论/新阶段】** 在央地矛盾的历史积累上，提出系统性的治理现代化方案。")
md.append("")

hits = ft_search(['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
                 ['国家治理体系','治理能力现代化','治理体系和'], max_hits=10)
for r in best(hits, 4):
    md.append(f"- `→结论` {cite(r)}")
    md.append("")

hits2 = ft_search(['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
                  ['财税体制','财政体制','中央和地方'], max_hits=6)
for r in best(hits2, 2):
    md.append(f"- `→补充` {cite(r)}")
    md.append("")

# --- 1g. 兰小欢 ---
md.append("### 环节⑦ 兰小欢《置身事内》——综合视角")
md.append("**【逻辑角色：补充/案例】** 从经济学视角综述分税制—土地财政—地方债务的完整链条。")
md.append("")

hits = ft_search(['置身事内'], ['分税制','土地财政','地方债务'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→补充` {cite(r)}")
    md.append("")


# ── 主题2 ─────────────────────────────────────────────────
md.append("---")
md.append("")
md.append("## 主题二：市场与计划——从陈云到黄奇帆")
md.append("")
md.append("**论证骨架：**")
md.append("```")
md.append('陈云 → "鸟笼经济"：计划经济为主，市场调节为辅')
md.append("  ↓ →但是")
md.append('邓小平 → "社会主义也可以搞市场经济"——突破意识形态禁区')
md.append("  ↓ →因此")
md.append("加入WTO → 全面融入全球市场")
md.append("  ↓ →发展")
md.append('习近平 → "市场在资源配置中起决定性作用"')
md.append("  ↓ →新形态")
md.append("黄奇帆 → 金融供给侧结构性改革——市场的新形态")
md.append("```")
md.append("")

# --- 2a. 陈云 ---
md.append('### 环节① 陈云——"鸟笼经济"：计划为主，市场为辅')
md.append("**【逻辑角色：起点/前提】** 陈云提出中国经济的经典框架：计划经济是笼子，市场调节是鸟。")
md.append("")

hits = ft_search(['陈云文选·第三卷'], ['鸟','笼子','鸟和笼子'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→前提` {cite(r)}")
    md.append("")

hits2 = ft_search(['陈云文选·第一卷','陈云文选·第二卷','陈云文选·第三卷'],
                  ['计划经济为主','市场调节为辅','计划为主'], max_hits=8)
for r in best(hits2, 3):
    md.append(f"- `→前提` {cite(r)}")
    md.append("")

# Chen Yun on comprehensive balance
hits3 = ft_search(['陈云文选·第一卷','陈云文选·第二卷','陈云文选·第三卷'],
                  ['综合平衡','按比例','财政平衡'], max_hits=5)
for r in best(hits3, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# --- 2b. 邓小平 ---
md.append('### 环节② 邓小平——"社会主义也可以搞市场经济"')
md.append("**【逻辑角色：推理/转折(但是)】** 邓小平突破了陈云的框架，将市场经济从资本主义标签中解放出来。")
md.append("")

hits = ft_search(['邓小平文选'], ['市场经济','社会主义也可以搞市场经济','计划和市场','计划经济和市场经济'], max_hits=8)
for r in best(hits, 4):
    md.append(f"- `→转折` {cite(r)}")
    md.append("")

hits2 = ft_search(['邓小平文选'], ['市场','计划','手段','不是目的'], max_hits=5)
for r in best(hits2, 2):
    if '市场' in r['text'] and '计划' in r['text']:
        md.append(f"- `→推理` {cite(r)}")
        md.append("")

# --- 2c. 入世 ---
md.append("### 环节③ 加入WTO——全面市场化")
md.append("**【逻辑角色：推理/案例】** 入世标志着中国全面融入全球市场经济体系。")
md.append("")

hits = ft_search(['突围·国门初开的岁月'], ['世贸','WTO','入世','对外开放','经济特区','特区'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# --- 2d. 习近平 ---
md.append('### 环节④ 习近平——市场在资源配置中起"决定性作用"')
md.append('**【逻辑角色：推理/发展】** 从"基础性作用"到"决定性作用"，市场化进一步深化。')
md.append("")

hits = ft_search(['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
                 ['市场在资源配置中','决定性作用','更好发挥政府作用'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→发展` {cite(r)}")
    md.append("")

# --- 2e. 黄奇帆 ---
md.append("### 环节⑤ 黄奇帆——供给侧结构性改革：市场的新形态")
md.append("**【逻辑角色：结论/新形态】** 从总量调控转向结构性调控，金融供给侧改革是市场经济的新阶段。")
md.append("")

hits = ft_search(['分析与思考'], ['供给侧','供给侧改革','供给侧结构性'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→结论` {cite(r)}")
    md.append("")

hits2 = ft_search(['分析与思考'], ['金融','要素配置','市场机制'], max_hits=5)
for r in best(hits2, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

ki = ki_search(['供给侧','金融改革','要素配置'], books=['分析与思考'])
for r in ki[:2]:
    md.append(f'- `→补充[{r["type"]}]` {cite(r)}')
    md.append("")

# --- 2f. 兰小欢 ---
md.append("### 环节⑥ 兰小欢——政府与市场的交织")
md.append("**【逻辑角色：补充/案例】** 政府不是市场的对立面，而是嵌入市场内部的参与者。")
md.append("")

hits = ft_search(['置身事内'], ['市场经济','政府与市场','产业政策','政府干预'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→补充` {cite(r)}")
    md.append("")


# ── 主题3 ─────────────────────────────────────────────────
md.append("---")
md.append("")
md.append("## 主题三：合法性——从毛泽东到习近平")
md.append("")
md.append("**论证骨架：**")
md.append("```")
md.append("毛泽东 → 革命合法性 + 阶级斗争 + 群众路线")
md.append("  ↓ →转向")
md.append('邓小平 → 绩效合法性："发展是硬道理""三个有利于"')
md.append("  ↓ →强化")
md.append("习近平 → 民族复兴 + 国家安全 + 以人民为中心")
md.append("  ↓ →理论对照")
md.append("周雪光 → 权威类型的分析：卡理斯玛→法理权威的张力")
md.append("  ↓ →哲学反驳")
md.append('波普尔 → 反历史决定论：不能以"历史规律"证成合法性')
md.append("```")
md.append("")

# --- 3a. 毛泽东 ---
md.append("### 环节① 毛泽东——革命合法性与阶级斗争")
md.append("**【逻辑角色：起点/前提】** 毛泽东时代的合法性建立在革命胜利和阶级斗争之上。")
md.append("")

hits = ft_search(['毛泽东文集'], ['阶级斗争','人民民主专政','革命','继续革命','无产阶级专政'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→前提` {cite(r)}")
    md.append("")

hits2 = ft_search(['毛泽东文集'], ['群众路线','为人民服务','依靠群众','人民，只有人民'], max_hits=6)
for r in best(hits2, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# --- 3b. 邓小平 ---
md.append('### 环节② 邓小平——绩效合法性："发展是硬道理"')
md.append("**【逻辑角色：推理/转向】** 邓小平将合法性基础从阶级斗争转向经济发展。")
md.append("")

hits = ft_search(['邓小平文选'], ['发展是硬道理','发展才是硬道理','三个有利于','以经济建设为中心'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→转向` {cite(r)}")
    md.append("")

hits2 = ft_search(['邓小平文选'], ['生产力','发展生产力','解放生产力'], max_hits=5)
for r in best(hits2, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

hits3 = ft_search(['邓小平文选'], ['稳定压倒一切','四项基本原则'], max_hits=5)
for r in best(hits3, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# --- 3c. 习近平 ---
md.append("### 环节③ 习近平——民族复兴 + 国家安全 + 以人民为中心")
md.append("**【逻辑角色：推理/强化】** 在绩效合法性之上叠加民族复兴叙事和国家安全框架，构成复合合法性。")
md.append("")

hits = ft_search(['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
                 ['民族复兴','伟大复兴','中国梦','中华民族伟大'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→强化` {cite(r)}")
    md.append("")

hits2 = ft_search(['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
                  ['国家安全','总体国家安全观','安全观'], max_hits=6)
for r in best(hits2, 2):
    md.append(f"- `→强化` {cite(r)}")
    md.append("")

hits3 = ft_search(['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
                  ['以人民为中心','不忘初心','人民至上'], max_hits=6)
for r in best(hits3, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# --- 3d. 周雪光 ---
md.append("### 环节④ 周雪光——权威类型与合法性基础")
md.append("**【逻辑角色：理论对照】** 从韦伯式权威类型学分析中国治理的合法性结构。")
md.append("")

hits = ft_search(['中国国家治理的制度逻辑'], ['合法性','权威','卡理斯玛','法理权威','传统型权威'], max_hits=8)
for r in best(hits, 4):
    md.append(f"- `→理论对照` {cite(r)}")
    md.append("")

ki = ki_search(['合法性','权威','卡理斯玛'], books=['中国国家治理'])
for r in ki[:3]:
    md.append(f'- `→补充[{r["type"]}]` {cite(r)}')
    md.append("")

# --- 3e. 波普尔 ---
md.append('### 环节⑤ 波普尔——反对历史决定论：不能以"历史规律"证成合法性')
md.append('**【逻辑角色：反驳/哲学】** 波普尔论证历史不可预测，任何以"历史必然性"为合法性辩护的理论都是谬误。')
md.append("")

hits = ft_search(['历史决定论的贫困'], ['历史决定论','不能预测','预测','规律'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→反驳` {cite(r)}")
    md.append("")

hits2 = ft_search(['历史决定论的贫困'], ['零星','渐进','社会工程','乌托邦','整体主义'], max_hits=6)
for r in best(hits2, 3):
    md.append(f"- `→反驳` {cite(r)}")
    md.append("")

ki = ki_search(['历史决定论','预测','乌托邦','零星'], books=['历史决定论'])
for r in ki[:3]:
    md.append(f'- `→补充[{r["type"]}]` {cite(r)}')
    md.append("")

# --- 3f. 王沪宁 ---
md.append("### 环节⑥ 王沪宁——政治发展与社会制度化")
md.append("**【逻辑角色：补充】** 政治的核心不在于合法性叙事本身，而在于制度化水平。")
md.append("")

hits = ft_search(['政治的人生'], ['合法性','政治发展','制度化','权威'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→补充` {cite(r)}")
    md.append("")


# ── 主题4 ─────────────────────────────────────────────────
md.append("---")
md.append("")
md.append("## 主题四：国家与社会——从秦晖到孙萍")
md.append("")
md.append("**论证骨架：**")
md.append("```")
md.append('秦晖 → "大共同体本位"：国家压倒一切社会自治（注：秦晖《田园诗与狂想曲》为扫描版，')
md.append("         此处以周雪光、费孝通的平行论证替代）")
md.append("  ↓ →文化深层结构")
md.append('费孝通 → 差序格局：社会关系的基本模式（替代孙隆基"他律导向"维度）')
md.append("  ↓ →历史延伸")
md.append("周雪光 → 官僚体制不断延伸，国家权力渗透社会")
md.append("  ↓ →当代案例")
md.append('孙萍 → 算法控制是"国家—社会"张力在数字时代的新形态')
md.append("  ↓ →哲学对照")
md.append('赫拉利 → 国家本身是"想象的秩序"——一种集体虚构')
md.append("```")
md.append("")
md.append("> **注**：秦晖《田园诗与狂想曲》、孙隆基《中国文化的深层结构》、项飙《浙江村》为扫描版PDF（无文本层），")
md.append("> 本文以知识库中的跨书引用 + 周雪光/费孝通的平行论证重建其论证位置。")
md.append("")

# --- 4a. 秦晖（替代论证）---
md.append('### 环节① 秦晖（替代论证）——"大共同体本位"：国家压倒社会')
md.append('**【逻辑角色：起点/前提】** 秦晖论证中国社会的核心特征不是"个人主义"或"集体主义"，而是"大共同体本位"——国家凌驾于一切社会自治之上。')
md.append("")
md.append("> **秦晖《田园诗与狂想曲》（扫描版，无文本层）核心论点摘要：**")
md.append('> - 中国社会的根本问题不是"农民的私有权"不发达，而是"大共同体"（国家）对个人的压制')
md.append('> - 与西方"小共同体"（领主、教会、行会）先于民族国家不同，中国从秦统一起就是"大共同体"压倒一切')
md.append('> - 宗族、乡绅等"小共同体"在中国历史上始终被皇权压制，无法成为抵御国家的中间层')
md.append('> - "大共同体本位"是中国与西方"个人主义社会"的本质差异所在')
md.append("")
md.append("> **跨书印证——周雪光对国家渗透的论证：**")
md.append("")

hits = ft_search(['中国国家治理的制度逻辑'], ['国家与社会','社会空间','社会自主性','社会群体'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→前提(平行)` {cite(r)}")
    md.append("")

# --- 4b. 费孝通 ---
md.append("### 环节② 费孝通——差序格局：社会关系的基本模式")
md.append('**【逻辑角色：推理/文化深层结构】** 费孝通的"差序格局"揭示了为什么中国社会难以形成抵御国家的自治组织——社会关系以自我为中心向外推演，而非横向结社。')
md.append("")

hits = ft_search(['费孝通文集'], ['差序格局'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

hits2 = ft_search(['费孝通文集'], ['团体格局','西洋社会','社会组织','结社'], max_hits=6)
for r in best(hits2, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

hits3 = ft_search(['费孝通文集'], ['乡土社会','熟人社会','礼治秩序'], max_hits=5)
for r in best(hits3, 2):
    md.append(f"- `→补充` {cite(r)}")
    md.append("")

# --- 4c. 周雪光 ---
md.append("### 环节③ 周雪光——官僚体制的延伸与国家权力渗透")
md.append("**【逻辑角色：推理/历史延伸】** 国家通过官僚体制不断渗透社会，挤压社会自治空间。")
md.append("")

hits = ft_search(['中国国家治理的制度逻辑'], ['官僚体制','官僚制','专断权力','国家权力','渗透'], max_hits=8)
for r in best(hits, 4):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# --- 4d. 孙萍 ---
md.append('### 环节④ 孙萍——算法控制是"国家—社会"张力的数字时代新形态')
md.append("**【逻辑角色：当代/案例】** 平台经济中，算法取代了传统官僚体制，成为控制劳动者的新型权力。")
md.append("")

hits = ft_search(['过渡劳动'], ['算法','算法管理'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→案例` {cite(r)}")
    md.append("")

hits2 = ft_search(['过渡劳动'], ['平台','骑手','外卖','劳动控制'], max_hits=6)
for r in best(hits2, 3):
    md.append(f"- `→案例` {cite(r)}")
    md.append("")

hits3 = ft_search(['过渡劳动'], ['自由','控制','弹性','不稳定'], max_hits=5)
for r in best(hits3, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

ki = ki_search(['算法','平台','骑手','劳动控制'], books=['过渡劳动'])
for r in ki[:3]:
    md.append(f'- `→补充[{r["type"]}]` {cite(r)}')
    md.append("")

# --- 4e. 赫拉利 ---
md.append('### 环节⑤ 赫拉利——国家本身是"想象的秩序"')
md.append('**【逻辑角色：反驳/哲学对照】** 从认知革命视角，国家、法律、货币都是大规模人类协作所必需的"共同想象的虚构"。')
md.append("")

hits = ft_search(['人类简史'], ['虚构','想象的','集体想象','想象的秩序'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→反驳` {cite(r)}")
    md.append("")

hits2 = ft_search(['人类简史'], ['帝国','国家','秩序','信任','想象的现实'], max_hits=6)
for r in best(hits2, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# --- 4f. 习近平 ---
md.append("### 环节⑥ 习近平——社会治理与基层管控")
md.append("**【逻辑角色：补充/官方视角】** 从国家视角看，社会治理现代化是提高管控能力而非释放社会自治。")
md.append("")

hits = ft_search(['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
                 ['社会治理','基层治理','网格化','共建共治'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→补充` {cite(r)}")
    md.append("")


# ── 主题5 ─────────────────────────────────────────────────
md.append("---")
md.append("")
md.append("## 主题五：传统与现代——从钱穆到黄仁宇")
md.append("")
md.append("**论证骨架：**")
md.append("```")
md.append('钱穆 → 传统政治有其内在合理性——需以"温情与敬意"理解')
md.append("  ↓ →对照")
md.append('黄仁宇 → 传统社会缺"数目字管理"——这是结构性失败')
md.append("  ↓ →延续")
md.append("毛泽东 → 打破旧制度——革命建国")
md.append("  ↓ →延续")
md.append("邓小平 → 改革开放——面向现代化")
md.append("  ↓ →新阶段")
md.append("习近平 → 文化自信 + 创造性转化——传统的再利用")
md.append("```")
md.append("")

# --- 5a. 钱穆 ---
md.append("### 环节① 钱穆——传统政治有内在合理性")
md.append('**【逻辑角色：起点/前提】** 钱穆反对以现代标准否定传统，主张以"温情与敬意"理解历史制度的内在逻辑。')
md.append("")

hits = ft_search(['钱穆国学作品集'], ['温情与敬意','温情','历史意见','时代意见'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→前提` {cite(r)}")
    md.append("")

hits2 = ft_search(['钱穆国学作品集'], ['历代政治','政治得失','皇权','相权','宰相','三省六部'], max_hits=8)
for r in best(hits2, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

hits3 = ft_search(['钱穆国学作品集'], ['士人','科举','考试制度','士大夫'], max_hits=6)
for r in best(hits3, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

ki = ki_search(['温情','政治得失','皇权','宰相','科举'], books=['钱穆'])
for r in ki[:3]:
    md.append(f'- `→补充[{r["type"]}]` {cite(r)}')
    md.append("")

# --- 5b. 黄仁宇 ---
md.append('### 环节② 黄仁宇——缺"数目字管理"：结构性失败')
md.append("**【逻辑角色：推理/对照】** 传统政治的困境不在于道德，而在于缺乏数目字管理能力——无法在技术上实现大规模精细治理。")
md.append("")

hits = ft_search(['万历十五年'], ['数目字管理','数目字','以道德代替法律','道德'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→对照` {cite(r)}")
    md.append("")

hits2 = ft_search(['万历十五年'], ['大历史','潜流','文官集团','官僚','停滞'], max_hits=6)
for r in best(hits2, 3):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

ki = ki_search(['数目字','道德','大历史','文官'], books=['万历十五年'])
for r in ki[:3]:
    md.append(f'- `→补充[{r["type"]}]` {cite(r)}')
    md.append("")

# --- 5c. 毛泽东 ---
md.append("### 环节③ 毛泽东——打破旧制度：革命建国")
md.append("**【逻辑角色：推理/延续】** 毛泽东彻底否定传统制度，以革命方式重建国家。")
md.append("")

hits = ft_search(['毛泽东文集'], ['旧制度','封建','推翻','破除','新民主主义'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→延续` {cite(r)}")
    md.append("")

hits2 = ft_search(['毛泽东文集'], ['革命','建国','新中国','人民民主专政','建立新中国'], max_hits=5)
for r in best(hits2, 2):
    md.append(f"- `→推理` {cite(r)}")
    md.append("")

# --- 5d. 邓小平 ---
md.append("### 环节④ 邓小平——改革开放：面向现代化")
md.append('**【逻辑角色：推理/延续】** 邓小平将"现代化"确立为国家目标，通过改革开放实现。')
md.append("")

hits = ft_search(['邓小平文选'], ['现代化','面向现代化','科学技术','改革开放'], max_hits=8)
for r in best(hits, 3):
    md.append(f"- `→延续` {cite(r)}")
    md.append("")

# --- 5e. 习近平 ---
md.append("### 环节⑤ 习近平——文化自信 + 创造性转化")
md.append('**【逻辑角色：结论/新阶段】** 习近平重新评价传统：不再否定，而是"创造性转化、创新性发展"，将传统作为合法性资源。')
md.append("")

hits = ft_search(['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
                 ['文化自信','创造性转化','创新性发展','传统文化','中华优秀'], max_hits=8)
for r in best(hits, 4):
    md.append(f"- `→结论` {cite(r)}")
    md.append("")

# --- 5f. 周雪光 ---
md.append("### 环节⑥ 周雪光——历史演变与制度路径依赖")
md.append("**【逻辑角色：补充/理论】** 治理制度有强大的历史延续性和路径依赖。")
md.append("")

hits = ft_search(['中国国家治理的制度逻辑'], ['历史','传统','路径','制度演变','延续性','中华帝国'], max_hits=6)
for r in best(hits, 3):
    md.append(f"- `→补充` {cite(r)}")
    md.append("")


# ── 总结 ───────────────────────────────────────────────────
md.append("---")
md.append("")
md.append("## 附录：方法论说明")
md.append("")
md.append("### 数据来源")
md.append(f"- `knowledge_index.json`：{KI['metadata']['total_entries']} 条结构化知识条目")
md.append(f"  - 概念定义：{KI['metadata']['entry_counts']['concepts']} 条")
md.append(f"  - 理论命题：{KI['metadata']['entry_counts']['propositions']} 条")
md.append(f"  - 关键数据：{KI['metadata']['entry_counts']['data_points']} 条")
md.append(f"  - 案例：{KI['metadata']['entry_counts']['cases']} 条")
md.append(f"- 全文 JSON：{len(BOOKS)} 本（含PDF文本层 + epub全文）")
md.append("")
md.append("### 搜索方法")
md.append("1. 对每个论证环节定义关键词组（3-6个关键词）")
md.append("2. 在对应作者的全文中做关键词搜索，提取前后250字的上下文")
md.append("3. 对文本进行归一化（移除PDF文本层中中文字符间的多余空格）")
md.append("4. 在知识库中补充搜索定义/命题/数据/案例")
md.append("5. 按论证逻辑角色（前提/推理/转折/结论/反驳/补充）组织引用")
md.append("")
md.append("### 局限性")
md.append("- 秦晖《田园诗与狂想曲》、孙隆基《中国文化的深层结构》、项飙《浙江村》、赵鼎新《社会与政治运动讲义》为扫描版PDF（无文本层），其论证以摘要形式补充")
md.append("- 搜索基于关键词匹配，可能遗漏不含关键词但语义相关的重要段落")
md.append('- 全文引用的"页码"对PDF为页号，对epub为章节文件名')
md.append("- 每个环节的引用数量受关键词命中率和文本长度限制，已尽量选取信息量最大的段落")
md.append("")

# ── 写入文件 ───────────────────────────────────────────────
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))

# 统计
total_quotes = sum(1 for line in md if line.strip().startswith('- `→'))
print(f'\n✓ 写入 {OUT}')
print(f'  总引用条数：~{total_quotes}')
print(f'  5个主题，每个主题4-7个论证环节')
