#!/usr/bin/env python3
"""
跨书论证链条重建工具
从 knowledge_index.json + 全文 epub/pdf JSON 中搜索关键词，
为5个核心主题提取跨书原文引用，按论证逻辑组织。
"""
import json, re, os, glob
from collections import defaultdict

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 1. 加载知识库 ──────────────────────────────────────────
with open(os.path.join(DATA_DIR, 'knowledge_index.json'), encoding='utf-8') as f:
    KINDEX = json.load(f)

# ── 2. 加载全部全文，建立 book → pages 映射 ────────────────
# book_name → list of {"page"/"loc": str, "text": str}
BOOKS = {}

FILE_BOOK_MAP = {
    # PDF-extracted
    '26cf383bac61.json': '中国国家治理的制度逻辑',
    'e0abe75fbd8d.json': '转型中的地方政府',
    '48c534c19594.json': '习近平谈治国理政·第三卷',
    '06277bb26b53.json': '习近平谈治国理政·第二卷',
    '09fc2812dff9.json': '习近平谈治国理政·第一卷',
    'f3d6472b9789.json': '以利为利',
    'f6033221fa1d.json': '分析与思考',
    'bdf7f491db6b.json': '过渡劳动',
    '231c14cd7e6c.json': '历史决定论的贫困',
    'd04c58fc9b3f.json': '陈云文选·第一卷',
    'b2e287a41416.json': '陈云文选·第二卷',
    '23b66adb7b4d.json': '陈云文选·第三卷',
    '26887183017c.json': '钱穆国学作品集',
    'dd8e3fd4cdd5.json': '政治的人生',
    'f9318869c29c.json': '突围·国门初开的岁月',
    # epub
    'epub_e077fb766e516aebbf6ad28d9cf81a48.json': '毛泽东文集',
    'epub_0695ef24be80eecef2179ca7122c88a9.json': '邓小平文选',
    'epub_677b2a39917dfc890ce34c57eb3b159f.json': '费孝通文集',
    'epub_946db8963df5272299e2408b328f23cd.json': '人地之间',
    'epub_05314f688e0d76c44aa385c98f502f93.json': '万历十五年',
    'epub_fc25bf25f43b22b0ef1ac62c8642850a.json': '置身事内',
    'mobi_f124b57a8baef3d0e363c9ee9ebcb01a.json': '人类简史',
}

for fn, bname in FILE_BOOK_MAP.items():
    fp = os.path.join(DATA_DIR, fn)
    if not os.path.exists(fp):
        continue
    try:
        with open(fp, encoding='utf-8') as f:
            d = json.load(f)
        ft = d.get('full_text', '')
        pages = []
        if isinstance(ft, list):
            for item in ft:
                if isinstance(item, dict):
                    txt = item.get('text', '')
                    if item.get('page'):
                        loc = f"p{item['page']}"
                    elif item.get('file'):
                        loc = item['file'].split('/')[-1].replace('.html','')
                    else:
                        loc = '?'
                    if txt and len(txt.strip()) > 5:
                        pages.append({'loc': loc, 'text': txt})
        elif isinstance(ft, str) and len(ft) > 100:
            pages.append({'loc': 'full', 'text': ft})
        if pages:
            BOOKS[bname] = pages
    except Exception as e:
        print(f'WARN loading {fn}: {e}')

print(f'Loaded {len(BOOKS)} books with full text')

# ── 3. 搜索函数 ────────────────────────────────────────────

def search_kindex(keywords, book_filter=None, entry_types=None):
    """在知识库中搜索关键词，返回匹配条目"""
    results = []
    entry_types = entry_types or ['propositions', 'concepts', 'data_points', 'cases']
    for etype in entry_types:
        items = KINDEX.get(etype, [])
        for item in items:
            text = ''
            book = ''
            if etype == 'concepts':
                for d in item.get('definitions', []):
                    text = d.get('text','')
                    book = d.get('book','')
                    if book_filter and book_filter not in book:
                        continue
                    if any(kw in text for kw in keywords):
                        results.append({
                            'type': 'concept定义',
                            'concept': item.get('concept',''),
                            'book': book,
                            'author': d.get('author',''),
                            'page': d.get('page',''),
                            'text': text.strip(),
                        })
            elif etype == 'cases':
                text = item.get('summary','') + ' ' + item.get('name','')
                book = item.get('book','')
                if book_filter and book_filter not in book:
                    continue
                if any(kw in text for kw in keywords):
                    results.append({
                        'type': '案例',
                        'book': book,
                        'author': item.get('author',''),
                        'page': item.get('page',''),
                        'text': text.strip()[:400],
                    })
            else:
                text = item.get('text','')
                book = item.get('book','')
                if book_filter and book_filter not in book:
                    continue
                if any(kw in text for kw in keywords):
                    results.append({
                        'type': '命题' if etype=='propositions' else '数据',
                        'book': book,
                        'page': item.get('page',''),
                        'text': text.strip(),
                        'theme': item.get('theme',''),
                    })
    return results


def search_fulltext(book_name, keywords, context_chars=200):
    """在指定书的全文中搜索关键词，返回带上下文的段落"""
    results = []
    pages = BOOKS.get(book_name, [])
    for pg in pages:
        text = pg['text']
        loc = pg['loc']
        for kw in keywords:
            idx = text.find(kw)
            while idx != -1:
                start = max(0, idx - context_chars)
                end = min(len(text), idx + len(kw) + context_chars)
                snippet = text[start:end].replace('\n', ' ').strip()
                # Clean up extra spaces
                snippet = re.sub(r'\s+', ' ', snippet)
                results.append({
                    'book': book_name,
                    'loc': loc,
                    'keyword': kw,
                    'text': snippet,
                })
                idx = text.find(kw, idx + 1)
    return results


def search_fulltext_multi(book_names, keywords, context_chars=250, max_per_book=8):
    """在多本书中搜索，每个关键词组每本书最多返回 max_per_book 条"""
    all_results = []
    for bname in book_names:
        hits = search_fulltext(bname, keywords, context_chars)
        # Deduplicate by location
        seen_loc = set()
        unique = []
        for h in hits:
            key = (h['loc'], h['keyword'])
            if key not in seen_loc:
                seen_loc.add(key)
                unique.append(h)
        all_results.extend(unique[:max_per_book])
    return all_results


# ── 4. 五大主题搜索 ────────────────────────────────────────

THEME_SEARCHES = {}

# ━━ 主题1：央地关系 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THEME_SEARCHES['t1'] = {
    'title': '央地关系的演变——从毛泽东到习近平',
    'groups': [
        {
            'label': '毛泽东《论十大关系》——中央和地方的关系',
            'role': '起点/前提',
            'books': ['毛泽东文集'],
            'keywords': ['十大关系', '中央和地方', '两个积极性', '发挥地方'],
        },
        {
            'label': '毛泽东——大权独揽/权力下放',
            'role': '补充',
            'books': ['毛泽东文集'],
            'keywords': ['大权独揽', '权力下放', '下放', '条块'],
        },
        {
            'label': '邓小平——放权让利/权力下放',
            'role': '推理/延续',
            'books': ['邓小平文选'],
            'keywords': ['放权让利', '权力下放', '权力过于集中', '下放权力'],
        },
        {
            'label': '邓小平——财政包干/改革体制',
            'role': '推理',
            'books': ['邓小平文选'],
            'keywords': ['财政体制', '包干', '分灶吃饭', '改革体制'],
        },
        {
            'label': '周飞舟——分税制与土地财政',
            'role': '推理/转折',
            'books': ['以利为利'],
            'keywords': ['分税制', '土地财政', '土地出让', '财政困境', '事权', '财权'],
        },
        {
            'label': '周飞舟——中央集中/地方竞争',
            'role': '推理',
            'books': ['以利为利'],
            'keywords': ['中央集中', '财权上收', '地方政府行为', '竞争'],
        },
        {
            'label': '周雪光——一统体制vs有效治理',
            'role': '推理/理论提升',
            'books': ['中国国家治理的制度逻辑'],
            'keywords': ['一统体制', '有效治理', '基本矛盾', '治理悖论', '中央管辖权'],
        },
        {
            'label': '周雪光——运动式治理/变通',
            'role': '推理',
            'books': ['中国国家治理的制度逻辑'],
            'keywords': ['运动型治理', '运动式治理', '变通', '共谋', '地方性'],
        },
        {
            'label': '周黎安——行政发包制',
            'role': '推理/理论框架',
            'books': ['转型中的地方政府'],
            'keywords': ['行政发包制', '发包', '属地管理', '承包'],
        },
        {
            'label': '周黎安——晋升锦标赛',
            'role': '推理/激励机制',
            'books': ['转型中的地方政府'],
            'keywords': ['晋升锦标赛', '锦标赛', '政治锦标赛', 'GDP考核', '激励'],
        },
        {
            'label': '周黎安——M型/U型/财政分权',
            'role': '补充',
            'books': ['转型中的地方政府'],
            'keywords': ['分权', '财政包干', '分税制', 'M型', '条块关系'],
        },
        {
            'label': '习近平——国家治理体系和治理能力现代化',
            'role': '结论/新阶段',
            'books': ['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
            'keywords': ['国家治理体系', '治理能力现代化', '治理体系和', '中央和地方'],
        },
        {
            'label': '习近平——财权事权/体制改革',
            'role': '补充',
            'books': ['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
            'keywords': ['财权', '事权', '财税体制', '财政体制'],
        },
        {
            'label': '兰小欢——置身事内/政府与经济',
            'role': '补充/案例',
            'books': ['置身事内'],
            'keywords': ['分税制', '土地财政', '地方债务', '财政'],
        },
    ],
}

# ━━ 主题2：市场与计划 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THEME_SEARCHES['t2'] = {
    'title': '市场与计划——从陈云到黄奇帆',
    'groups': [
        {
            'label': '陈云——鸟笼经济/计划为主',
            'role': '起点/前提',
            'books': ['陈云文选·第一卷','陈云文选·第二卷','陈云文选·第三卷'],
            'keywords': ['鸟笼', '计划经济为主', '市场调节为辅', '计划为主', '鸟和笼子'],
        },
        {
            'label': '陈云——计划与市场的关系',
            'role': '推理',
            'books': ['陈云文选·第一卷','陈云文选·第二卷','陈云文选·第三卷'],
            'keywords': ['计划和市场', '计划与市场', '综合平衡', '按比例', '宏观控制'],
        },
        {
            'label': '陈云——市场调节/搞活经济',
            'role': '推理',
            'books': ['陈云文选·第一卷','陈云文选·第二卷','陈云文选·第三卷'],
            'keywords': ['市场调节', '自由市场', '价值规律', '商品经济'],
        },
        {
            'label': '邓小平——社会主义市场经济',
            'role': '推理/转折',
            'books': ['邓小平文选'],
            'keywords': ['社会主义也可以搞市场经济', '市场经济', '计划和市场', '计划经济和市场经济'],
        },
        {
            'label': '邓小平——改革开放/解放思想',
            'role': '推理',
            'books': ['邓小平文选'],
            'keywords': ['改革开放', '解放思想', '实事求是', '摸着石头'],
        },
        {
            'label': '李岚清——入世/国门初开',
            'role': '推理/案例',
            'books': ['突围·国门初开的岁月'],
            'keywords': ['世贸组织', 'WTO', '入世', '对外开放', '特区'],
        },
        {
            'label': '黄奇帆——供给侧改革/金融',
            'role': '结论/新形态',
            'books': ['分析与思考'],
            'keywords': ['供给侧', '供给侧改革', '供给侧结构性', '金融改革'],
        },
        {
            'label': '黄奇帆——市场经济/要素配置',
            'role': '推理',
            'books': ['分析与思考'],
            'keywords': ['要素配置', '市场机制', '市场经济', '宏观调控'],
        },
        {
            'label': '兰小欢——政府与经济发展',
            'role': '补充/案例',
            'books': ['置身事内'],
            'keywords': ['市场经济', '政府与市场', '产业政策', '宏观调控'],
        },
        {
            'label': '习近平——市场在资源配置中起决定性作用',
            'role': '推理/发展',
            'books': ['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
            'keywords': ['市场在资源配置中', '决定性作用', '市场作用', '更好发挥政府作用'],
        },
    ],
}

# ━━ 主题3：合法性 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THEME_SEARCHES['t3'] = {
    'title': '合法性——从毛泽东到习近平',
    'groups': [
        {
            'label': '毛泽东——革命合法性/阶级斗争',
            'role': '起点/前提',
            'books': ['毛泽东文集'],
            'keywords': ['阶级斗争', '革命', '人民民主专政', '继续革命', '造反'],
        },
        {
            'label': '毛泽东——人民/群众路线',
            'role': '推理',
            'books': ['毛泽东文集'],
            'keywords': ['群众路线', '为人民服务', '人民，只有人民', '依靠群众'],
        },
        {
            'label': '邓小平——发展是硬道理/绩效',
            'role': '推理/转向',
            'books': ['邓小平文选'],
            'keywords': ['发展是硬道理', '发展才是硬道理', '以经济建设为中心', '三个有利于', '生产力'],
        },
        {
            'label': '邓小平——稳定压倒一切/四项基本原则',
            'role': '推理',
            'books': ['邓小平文选'],
            'keywords': ['稳定压倒一切', '四项基本原则', '坚持四项', '压倒一切'],
        },
        {
            'label': '习近平——民族复兴/中国梦',
            'role': '推理/强化',
            'books': ['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
            'keywords': ['民族复兴', '伟大复兴', '中国梦', '中华民族伟大'],
        },
        {
            'label': '习近平——国家安全/总体国家安全观',
            'role': '推理/强化',
            'books': ['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
            'keywords': ['国家安全', '总体国家安全观', '安全观', '政治安全'],
        },
        {
            'label': '习近平——以人民为中心/不忘初心',
            'role': '推理',
            'books': ['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
            'keywords': ['以人民为中心', '不忘初心', '牢记使命', '人民至上'],
        },
        {
            'label': '周雪光——权威类型/合法性基础',
            'role': '补充/理论',
            'books': ['中国国家治理的制度逻辑'],
            'keywords': ['合法性', '权威', '卡理斯玛', '法理权威', '传统型权威', '合法性基础'],
        },
        {
            'label': '波普尔——历史决定论的贫困',
            'role': '反驳/对照',
            'books': ['历史决定论的贫困'],
            'keywords': ['历史决定论', '预测', '不能预测', '规律', '乌托邦', '渐进'],
        },
        {
            'label': '波普尔——反乌托邦/零星社会工程',
            'role': '推理/反驳',
            'books': ['历史决定论的贫困'],
            'keywords': ['零星', '渐进工程', '社会工程', '乌托邦工程', '整体主义'],
        },
        {
            'label': '王沪宁——政治的逻辑/合法性',
            'role': '补充',
            'books': ['政治的人生'],
            'keywords': ['合法性', '政治发展', '制度化', '权威'],
        },
    ],
}

# ━━ 主题4：国家与社会 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THEME_SEARCHES['t4'] = {
    'title': '国家与社会——从秦晖到孙萍',
    'groups': [
        {
            'label': '周雪光——国家与社会关系',
            'role': '理论框架',
            'books': ['中国国家治理的制度逻辑'],
            'keywords': ['国家与社会', '社会空间', '社会自主性', '社会群体', '官僚体制'],
        },
        {
            'label': '周雪光——官僚体制的延伸',
            'role': '推理',
            'books': ['中国国家治理的制度逻辑'],
            'keywords': ['官僚体制', '官僚制', '专断权力', '国家权力', '渗透'],
        },
        {
            'label': '费孝通——差序格局/乡土社会',
            'role': '补充/文化根源',
            'books': ['费孝通文集'],
            'keywords': ['差序格局', '乡土社会', '熟人社会', '礼治', '无讼'],
        },
        {
            'label': '孙萍——平台劳动/算法控制',
            'role': '当代/案例',
            'books': ['过渡劳动'],
            'keywords': ['算法', '平台', '外卖', '骑手', '算法管理', '数字'],
        },
        {
            'label': '孙萍——劳动控制/过渡劳动',
            'role': '推理',
            'books': ['过渡劳动'],
            'keywords': ['劳动控制', '过渡劳动', '弹性', '不稳定', '自由与控制'],
        },
        {
            'label': '赫拉利——虚构故事/集体想象',
            'role': '反驳/对照',
            'books': ['人类简史'],
            'keywords': ['虚构', '想象的', '集体想象', '想象的秩序', '故事'],
        },
        {
            'label': '赫拉利——国家/帝国/货币',
            'role': '推理',
            'books': ['人类简史'],
            'keywords': ['帝国', '国家', '货币', '秩序', '信任', '想象的现实'],
        },
        {
            'label': '习近平——社会治理/基层',
            'role': '补充/官方视角',
            'books': ['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
            'keywords': ['社会治理', '基层治理', '社会管理', '网格化', '共建共治'],
        },
        {
            'label': '兰小欢——政府与社会/土地财政',
            'role': '补充',
            'books': ['置身事内'],
            'keywords': ['土地', '征地', '拆迁', '农民', '城乡'],
        },
    ],
}

# ━━ 主题5：传统与现代 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THEME_SEARCHES['t5'] = {
    'title': '传统与现代——从钱穆到黄仁宇',
    'groups': [
        {
            'label': '钱穆——温情与敬意/传统政治',
            'role': '起点/前提',
            'books': ['钱穆国学作品集'],
            'keywords': ['温情与敬意', '温情', '历史意见', '时代意见', '制度精神'],
        },
        {
            'label': '钱穆——中国历代政治得失',
            'role': '推理',
            'books': ['钱穆国学作品集'],
            'keywords': ['历代政治', '政治得失', '皇权', '相权', '宰相', '三省六部'],
        },
        {
            'label': '钱穆——士人政治/考试制度',
            'role': '推理',
            'books': ['钱穆国学作品集'],
            'keywords': ['士人', '科举', '考试制度', '选举', '士大夫'],
        },
        {
            'label': '黄仁宇——数目字管理',
            'role': '推理/对照',
            'books': ['万历十五年'],
            'keywords': ['数目字管理', '数目字', '以道德代替法律', '道德'],
        },
        {
            'label': '黄仁宇——大历史观/结构',
            'role': '推理',
            'books': ['万历十五年'],
            'keywords': ['大历史', '结构', '潜流', '官僚', '文官集团', '停滞'],
        },
        {
            'label': '毛泽东——打破旧制度/革命建国',
            'role': '推理/延续',
            'books': ['毛泽东文集'],
            'keywords': ['旧制度', '封建', '革命', '推翻', '破除', '新民主主义'],
        },
        {
            'label': '邓小平——改革开放/现代化',
            'role': '推理/延续',
            'books': ['邓小平文选'],
            'keywords': ['现代化', '改革开放', '面向现代化', '面向世界', '科学技术'],
        },
        {
            'label': '习近平——文化自信/创造性转化',
            'role': '结论/新阶段',
            'books': ['习近平谈治国理政·第一卷','习近平谈治国理政·第二卷','习近平谈治国理政·第三卷'],
            'keywords': ['文化自信', '创造性转化', '创新性发展', '传统文化', '中华优秀'],
        },
        {
            'label': '周雪光——历史演变/路径依赖',
            'role': '补充/理论',
            'books': ['中国国家治理的制度逻辑'],
            'keywords': ['历史', '传统', '路径', '制度演变', '延续性'],
        },
    ],
}


# ── 5. 执行搜索 ────────────────────────────────────────────
import sys

def run_all_searches(output_file):
    output = {}
    for theme_id, theme in THEME_SEARCHES.items():
        print(f'\n=== {theme["title"]} ===')
        theme_result = {
            'title': theme['title'],
            'groups': []
        }
        for grp in theme['groups']:
            # Search knowledge index
            kindex_hits = search_kindex(grp['keywords'], max_per_book=5) if False else []
            # Search full text
            fulltext_hits = search_fulltext_multi(
                grp['books'], grp['keywords'],
                context_chars=280, max_per_book=10
            )
            # Also search knowledge index
            ki = search_kindex(grp['keywords'])
            # Filter to relevant books
            ki_filtered = [k for k in ki if any(b in k.get('book','') for b in grp['books'])]

            print(f'  [{grp["role"]}] {grp["label"]}: {len(fulltext_hits)} fulltext + {len(ki_filtered)} kindex')

            theme_result['groups'].append({
                'label': grp['label'],
                'role': grp['role'],
                'keywords': grp['keywords'],
                'books': grp['books'],
                'fulltext_hits': fulltext_hits,
                'kindex_hits': ki_filtered[:5],
            })
        output[theme_id] = theme_result

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'\n✓ Saved to {output_file}')
    return output


if __name__ == '__main__':
    out = os.path.join(DATA_DIR, 'argument_chain_raw.json')
    run_all_searches(out)
