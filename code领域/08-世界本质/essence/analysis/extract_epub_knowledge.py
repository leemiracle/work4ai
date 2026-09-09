#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度知识提取：从6本EPUB/MOBI全文JSON中提取5类知识。
输出: extracted-knowledge-epubs-deep.md
"""

import json, re, os, glob
from collections import defaultdict

DATA_DIR = '/mnt/c/workspace/essence/data/political-books-extracted'
OUT_FILE = '/mnt/c/workspace/essence/analysis/extracted-knowledge-epubs-deep.md'

# ─── 书籍映射 ───
BOOK_FILES = {
    'wanli':     ('epub_05314f688e0d76c44aa385c98f502f93.json', '万历十五年', '黄仁宇'),
    'sociology': ('epub_677b2a39917dfc890ce34c57eb3b159f.json', '中国社会学经典文库', '费孝通 等'),
    'mao':       ('epub_e077fb766e516aebbf6ad28d9cf81a48.json', '毛泽东文集', '毛泽东'),
    'deng':      ('epub_0695ef24be80eecef2179ca7122c88a9.json', '邓小平文选', '邓小平'),
    'zhishen':   ('epub_fc25bf25f43b22b0ef1ac62c8642850a.json', '置身事内', '兰小欢'),
    'sapiens':   ('mobi_f124b57a8baef3d0e363c9ee9ebcb01a.json', '人类简史', '尤瓦尔·赫拉利'),
}

# ─── 正则模式 ───

# 1. 定义性陈述
DEF_PATTERNS = [
    r'所谓[^，。；\n]{2,30}(?:是指|就是|指的是|意味着|即是|乃)',
    r'[^，。；\n：]{2,20}是指[^。\n]{5,120}',
    r'[^，。；\n：]{2,20}，(?:即|也就是)(?:指)?[^。\n]{5,100}',
    r'(?:定义|概念)(?:为|是|：)[^。\n]{5,120}',
    r'(?:所谓|一般所说的)(?:的)?[^，。；\n]{2,30}(?:，|，其)?(?:就是|是指|指的是)',
    r'「[^」]{2,20}」(?:是指|就是|指的是|意味着)',
    r'"[^"]{2,20}"(?:是指|就是|指的是|意味着)',
    r'称之为[^。\n]{3,40}',
    r'简而言之[^。\n]{5,80}',
]
DEF_REGEX = re.compile('|'.join(f'(?:{p})' for p in DEF_PATTERNS))

# 2. 核心命题/论断
PROP_PATTERNS = [
    r'(?:我认为|笔者认为|本书认为|本书提出|作者认为)[^。\n]{5,150}',
    r'(?:核心(?:问题|观点|论点|结论|思想)?)(?:在于|是|就是)[^。\n]{5,120}',
    r'(?:关键(?:问题|在于|是|因素)?)(?:在于|是)[^。\n]{5,120}',
    r'(?:归根结底|归根到底|说到底)[^。\n]{5,120}',
    r'(?:本质上|实质上|根本上)(?:是|来说)[^。\n]{5,120}',
    r'(?:最重要(?:的)?|最根本(?:的)?|最关键(?:的)?)(?:是|在于)[^。\n]{5,120}',
    r'(?:必须|务必|一定要)[^。\n]{5,100}',
    r'(?:总之|总而言之|综上)[^。\n]{5,120}',
    r'(?:由此可(?:以)?见|由此得出|结论是)[^。\n]{5,120}',
    r'(?:问题(?:的)?(?:关键|核心|实质|根本))(?:在于|是)[^。\n]{5,100}',
    r'(?:原因(?:在于|是|有))[^。\n]{5,100}',
    r'(?:目的(?:在于|是|就是为了))[^。\n]{5,100}',
]
PROP_REGEX = re.compile('|'.join(f'(?:{p})' for p in PROP_PATTERNS))

# 3. 关键数据（支持阿拉伯数字和中文数字）
CN_NUM = r'[一二三四五六七八九十百千万亿零〇点两]'
DATA_PATTERNS = [
    r'\d+(?:\.\d+)?%',                       # 阿拉伯百分比
    r'百分之(?:[一二三四五六七八九十百千万亿零〇点两\d]+(?:\.\d+)?)',  # 中文百分比
    r'(?:约|大约|超过|近|将近)?\d+(?:\.\d+)?(?:万|亿|百万|千万|千亿|万亿)(?:元|美元|人|吨|亩|公里|个|次|场|年)?',  # 阿拉伯大数字
    f'(?:{CN_NUM}+){{2,}}(?:万|亿)(?:元|美元|人|吨|亩|个|次|名|位)',   # 中文大数字
    r'\d{3,4}(?:年|年度)',                   # 阿拉伯年份
    r'一九[〇一二三四五六七八九]{2}年|二〇[〇一二三四五六七八九]{2}年',  # 中文年份
    r'第[一二三四五六七八九十百千]+(?:次|届|个|批|阶段|时期|步|个五年)',  # 序数
    r'\d+(?:多)?(?:个|种|类|项|条|本|篇|部|省|市|县|区|村|人|名|位)',  # 计数
]
DATA_REGEX = re.compile('|'.join(f'(?:{p})' for p in DATA_PATTERNS))

# 章节标题（更严格，避免误匹配正文）
CHAPTER_REGEX = re.compile(
    r'^(?:'
    r'第[一二三四五六七八九十百零〇]+[章节回篇编卷]\s*[^\n]{0,50}'
    r'|前言\b[^\n]{0,30}'
    r'|后记\b[^\n]{0,30}'
    r'|序(?:言|论)?\b[^\n]{0,30}'
    r'|附录\b[^\n]{0,40}'
    r'|结语\b[^\n]{0,30}'
    r'|引言\b[^\n]{0,30}'
    r'|导论\b[^\n]{0,30}'
    r'|绪论\b[^\n]{0,30}'
    r')$',
    re.MULTILINE
)

# 文章编号格式（用于毛选/邓选等以编号排列的文章）
ARTICLE_NUM_REGEX = re.compile(r'^\d{3}\.[^\n]{4,60}$', re.MULTILINE)


def load_book(key):
    """加载一本书的full_text，返回 (title, author, pages) where pages is list of (idx, file, text)"""
    fname, title, author = BOOK_FILES[key]
    path = os.path.join(DATA_DIR, fname)
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    pages = []
    for i, p in enumerate(data.get('full_text', [])):
        if isinstance(p, dict):
            pages.append((i, p.get('file', f'page{i}'), p.get('text', '')))
    return data.get('title', title), author, pages


def split_sentences(text):
    """将文本按句子分割"""
    # 先按换行分段
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    sentences = []
    for para in paragraphs:
        # 按句号、问号、感叹号分句
        parts = re.split(r'(?<=[。！？；])', para)
        for part in parts:
            part = part.strip()
            if len(part) >= 8:  # 太短的不提取
                sentences.append(part)
    return sentences


def extract_definitions(pages, limit=80):
    """提取定义性陈述"""
    results = []
    seen = set()
    for idx, fname, text in pages:
        sentences = split_sentences(text)
        for sent in sentences:
            if len(results) >= limit:
                return results
            matches = DEF_REGEX.findall(sent)
            if matches:
                key = sent[:50]
                if key not in seen and len(sent) <= 200:
                    seen.add(key)
                    results.append((sent.strip(), f'[{fname}]'))
    return results


def extract_propositions(pages, limit=80):
    """提取核心命题"""
    results = []
    seen = set()
    for idx, fname, text in pages:
        sentences = split_sentences(text)
        for sent in sentences:
            if len(results) >= limit:
                return results
            matches = PROP_REGEX.findall(sent)
            if matches:
                key = sent[:50]
                if key not in seen and len(sent) <= 250:
                    seen.add(key)
                    results.append((sent.strip(), f'[{fname}]'))
    return results


def extract_data_points(pages, limit=80):
    """提取关键数据"""
    results = []
    seen = set()
    for idx, fname, text in pages:
        sentences = split_sentences(text)
        for sent in sentences:
            if len(results) >= limit:
                return results
            matches = DATA_REGEX.findall(sent)
            # 过滤：只保留有百分比、大数字或年份的句子
            significant = [m for m in matches if '%' in m or '百分之' in m or '亿' in m or '万' in m
                           or re.search(r'\d{4}年', m) or re.search(r'[一九二][〇一二三四五六七八九]{2}年', m)]
            if significant and len(sent) <= 250:
                key = sent[:50]
                if key not in seen:
                    seen.add(key)
                    # 高亮数据
                    display = sent.strip()
                    results.append((display, f'[{fname}]'))
    return results


def extract_cases(pages, keywords, limit=40):
    """提取含特定关键词的案例段落"""
    results = []
    seen = set()
    for idx, fname, text in pages:
        paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 30]
        for para in paragraphs:
            if len(results) >= limit:
                return results
            for kw in keywords:
                if kw in para and len(para) <= 300:
                    key = para[:60]
                    if key not in seen:
                        seen.add(key)
                        results.append((para.strip(), f'[{fname}]', kw))
                        break
    return results


def extract_toc(pages):
    """提取目录结构"""
    toc = []
    seen_titles = set()
    for idx, fname, text in pages:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if CHAPTER_REGEX.match(line) and line not in seen_titles:
                seen_titles.add(line)
                toc.append((line, f'[{fname}]'))
            # 文章编号格式（如 "001.动员新兵..."）
            elif ARTICLE_NUM_REGEX.match(line) and line not in seen_titles:
                seen_titles.add(line)
                toc.append((line, f'[{fname}]'))
    # 也尝试从目录页提取
    for idx, fname, text in pages:
        if '目录' in text[:20] or '目 录' in text[:20]:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 3 and len(line) < 60 and line not in seen_titles:
                    # 尝试匹配章节模式
                    if re.match(r'第[一二三四五六七八九十百零〇]+[章节回篇]', line) or \
                       re.match(r'\d{3}\.', line) or \
                       line.startswith('前言') or line.startswith('后记') or \
                       line.startswith('附录') or line.startswith('结语'):
                        seen_titles.add(line)
                        toc.append((line, f'[{fname}]'))
    return toc


def extract_concept_mentions(pages, concepts, limit_per_concept=10):
    """提取特定概念出现的上下文"""
    results = {}
    for concept in concepts:
        mentions = []
        for idx, fname, text in pages:
            start = 0
            while True:
                pos = text.find(concept, start)
                if pos == -1:
                    break
                # 提取上下文（前后各取100字）
                ctx_start = max(0, pos - 80)
                ctx_end = min(len(text), pos + len(concept) + 120)
                context = text[ctx_start:ctx_end].replace('\n', ' ').strip()
                if len(context) > 20:
                    mentions.append((context, f'[{fname}]'))
                start = pos + len(concept)
                if len(mentions) >= limit_per_concept:
                    break
            if len(mentions) >= limit_per_concept:
                break
        results[concept] = mentions
    return results


def extract_keyword_paragraphs(pages, keywords, limit=60):
    """提取含特定关键词的段落（更宽松）"""
    results = []
    seen = set()
    for idx, fname, text in pages:
        paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 40]
        for para in paragraphs:
            if len(results) >= limit:
                return results
            for kw in keywords:
                if kw in para and len(para) <= 350:
                    key = para[:50]
                    if key not in seen:
                        seen.add(key)
                        results.append((para.strip(), f'[{fname}]', kw))
                        break
    return results


# ═══════════════════════════════════════════════════════
#  各书专用提取
# ═══════════════════════════════════════════════════════

def extract_wanli(pages):
    """万历十五年专用提取"""
    concepts = ['数目字管理', '大历史', '潜水艇三明治', '潜水艇夹肉面包', '道德代替管理',
                '以道德代替法律', '宏观历史', '大历史观']
    people = ['万历', '张居正', '申时行', '海瑞', '戚继光', '李贽']
    
    person_paras = extract_keyword_paragraphs(pages, people, limit=30)
    concept_mentions = extract_concept_mentions(pages, concepts, limit_per_concept=5)
    
    return {
        'concepts': concept_mentions,
        'people': person_paras,
    }


def extract_mao(pages):
    """毛泽东文集专用提取"""
    # 特定著作
    works = ['中国社会各阶级的分析', '实践论', '矛盾论', '新民主主义论', '论人民民主专政',
             '论持久战', '湖南农民运动考察报告', '星星之火', '井冈山的斗争']
    # 核心概念
    concepts = ['群众路线', '三大法宝', '实事求是', '人民民主专政', '新民主主义',
                '统一战线', '武装斗争', '党的建设', '主要矛盾', '次要矛盾',
                '矛盾的主要方面', '实践是检验真理', '调查研究', '为人民服务',
                '独立自主', '自力更生']
    
    work_paras = extract_keyword_paragraphs(pages, works, limit=25)
    concept_mentions = extract_concept_mentions(pages, concepts, limit_per_concept=4)
    
    return {
        'works': work_paras,
        'concepts': concept_mentions,
    }


def extract_deng(pages):
    """邓小平文选专用提取"""
    concepts = ['改革开放', '一国两制', '四项基本原则', '摸着石头过河', '发展是硬道理',
                '社会主义市场经济', '社会主义初级阶段', '三个有利于', '科学技术是第一生产力',
                '两手抓', '共同富裕', '让一部分人先富起来', '解放思想', '实事求是',
                '南方谈话', '南巡']
    
    concept_mentions = extract_concept_mentions(pages, concepts, limit_per_concept=5)
    
    # 提取1992年南巡讲话相关
    south_tour = extract_keyword_paragraphs(pages, ['一九九二', '1992', '南方', '南巡', '武昌', '深圳', '珠海', '上海'], limit=20)
    
    # 市场经济论述
    market = extract_keyword_paragraphs(pages, ['市场经济', '计划经济', '市场与计划', '计划和市场'], limit=20)
    
    return {
        'concepts': concept_mentions,
        'south_tour': south_tour,
        'market': market,
    }


def extract_zhishen(pages):
    """置身事内专用提取"""
    concepts = ['地方政府竞争', '土地财政', '产业政策', '财政分权', '分税制',
                '属地管理', '事权', '财权', '转移支付', '融资平台', '城投',
                '土地出让', '预算外收入', '招商引资', '激励相容', '外部性',
                '规模经济', '纵向竞争', '横向竞争']
    
    concept_mentions = extract_concept_mentions(pages, concepts, limit_per_concept=4)
    
    # 每章核心论点（从章节开头提取）
    chapter_points = []
    for idx, fname, text in pages:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_s = line.strip()
            if re.match(r'第[一二三四五六七八九十]+章', line_s):
                # 取后面几段作为核心论点
                remaining = '\n'.join(lines[i:i+5])
                chapter_points.append((line_s, remaining[:400].replace('\n', ' '), f'[{fname}]'))
    
    return {
        'concepts': concept_mentions,
        'chapter_points': chapter_points,
    }


def extract_sapiens(pages):
    """人类简史专用提取"""
    concepts = ['认知革命', '农业革命', '科学革命', '虚构故事', '想象的秩序',
                '集体虚构', '想象的现实', '八卦理论', '吉尔伽美什',
                '泛灵论', '多神教', '一神教', '人文主义']
    
    concept_mentions = extract_concept_mentions(pages, concepts, limit_per_concept=5)
    
    # 三大革命的定义
    revolutions = extract_keyword_paragraphs(pages, ['认知革命', '农业革命', '科学革命'], limit=15)
    
    # 金钱/国家/宗教作为虚构
    fictions = extract_keyword_paragraphs(pages, ['金钱', '货币', '国家', '帝国', '宗教', '公司'], limit=20)
    
    return {
        'concepts': concept_mentions,
        'revolutions': revolutions,
        'fictions': fictions,
    }


def extract_sociology(pages):
    """中国社会学经典文库专用提取（选择性）"""
    concepts = ['差序格局', '江村经济', '乡土中国', '单位制', '单位组织',
                '乡村治理', '熟人社会', '礼俗社会', '法理社会', '血缘',
                '地缘', '团体格局', '道德体系', '社会结构']
    
    concept_mentions = extract_concept_mentions(pages, concepts, limit_per_concept=5)
    
    # 金翼相关
    jinyi = extract_keyword_paragraphs(pages, ['金翼', '黄村', '东林', '芬洲'], limit=15)
    
    # 单位制论述
    danwei = extract_keyword_paragraphs(pages, ['单位制', '单位组织', '单位社会', '体制内'], limit=15)
    
    # 乡村治理
    rural = extract_keyword_paragraphs(pages, ['乡村治理', '村民自治', '宗族', '乡绅'], limit=15)
    
    return {
        'concepts': concept_mentions,
        'jinyi': jinyi,
        'danwei': danwei,
        'rural': rural,
    }


# ═══════════════════════════════════════════════════════
#  Markdown 生成
# ═══════════════════════════════════════════════════════

def esc(s, maxlen=300):
    """清理文本用于markdown"""
    s = s.replace('\n', ' ').replace('\r', '').strip()
    s = re.sub(r'\s{2,}', ' ', s)
    if len(s) > maxlen:
        s = s[:maxlen] + '…'
    return s


def write_book_section(f, key, title, author, pages):
    """写一本书的提取结果"""
    char_count = sum(len(t) for _, _, t in pages)
    
    f.write(f'\n---\n\n')
    f.write(f'## {title}\n\n')
    f.write(f'**作者**：{author}  \n')
    f.write(f'**总字数**：{char_count:,}  \n')
    f.write(f'**页/文件数**：{len(pages)}  \n\n')
    
    counts = {}
    
    # 1. 定义性陈述
    defs = extract_definitions(pages, limit=80)
    counts['定义性陈述'] = len(defs)
    f.write(f'### 1. 定义性陈述（{len(defs)}条）\n\n')
    for i, (sent, ref) in enumerate(defs, 1):
        f.write(f'{i}. {esc(sent)} {ref}\n')
    f.write('\n')
    
    # 2. 核心命题
    props = extract_propositions(pages, limit=80)
    counts['核心命题'] = len(props)
    f.write(f'### 2. 核心命题/论断（{len(props)}条）\n\n')
    for i, (sent, ref) in enumerate(props, 1):
        f.write(f'{i}. {esc(sent)} {ref}\n')
    f.write('\n')
    
    # 3. 关键数据
    data = extract_data_points(pages, limit=80)
    counts['关键数据'] = len(data)
    f.write(f'### 3. 关键数据（{len(data)}条）\n\n')
    for i, (sent, ref) in enumerate(data, 1):
        f.write(f'{i}. {esc(sent)} {ref}\n')
    f.write('\n')
    
    # 4. 目录结构
    toc = extract_toc(pages)
    # 毛泽东文集：每页是一篇文章，提取文章标题
    if key == 'mao' and len(toc) < 20:
        toc = []
        seen_titles = set()
        for idx, fname, text in pages:
            if 'chapter' not in fname:
                continue
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if lines:
                title = lines[0]
                # 过滤掉目录/出版说明等
                if title in ('目录', '出版说明', 'bookcover') or title.startswith('毛泽东文集'):
                    continue
                title_clean = re.sub(r'\[\d+\]', '', title).strip()
                if title_clean and title_clean not in seen_titles and len(title_clean) > 2:
                    seen_titles.add(title_clean)
                    toc.append((title_clean, f'[{fname}]'))
    counts['目录章节'] = len(toc)
    f.write(f'### 4. 目录结构（{len(toc)}条）\n\n')
    for i, (title_s, ref) in enumerate(toc[:80], 1):
        f.write(f'{i}. {esc(title_s, 80)} {ref}\n')
    if len(toc) > 80:
        f.write(f'   ...（共{len(toc)}条，此处省略）\n')
    f.write('\n')
    
    # 5. 专用提取
    f.write(f'### 5. 本书专属深度提取\n\n')
    
    if key == 'wanli':
        special = extract_wanli(pages)
        # 核心概念
        f.write(f'#### 5.1 核心概念出现\n\n')
        for concept, mentions in special['concepts'].items():
            if mentions:
                f.write(f'**「{concept}」** ({len(mentions)}处)\n\n')
                for i, (ctx, ref) in enumerate(mentions[:3], 1):
                    f.write(f'   - {esc(ctx, 250)} {ref}\n')
                f.write('\n')
        # 人物论述
        f.write(f'#### 5.2 关键人物论述\n\n')
        for para, ref, kw in special['people'][:20]:
            f.write(f'- **[{kw}]** {esc(para, 250)} {ref}\n')
        f.write('\n')
        counts['人物论述'] = len(special['people'])
    
    elif key == 'mao':
        special = extract_mao(pages)
        f.write(f'#### 5.1 核心著作段落\n\n')
        for para, ref, kw in special['works'][:15]:
            f.write(f'- **[{kw}]** {esc(para, 250)} {ref}\n')
        f.write('\n')
        f.write(f'#### 5.2 核心概念定义与论述\n\n')
        for concept, mentions in special['concepts'].items():
            if mentions:
                f.write(f'**「{concept}」** ({len(mentions)}处)\n\n')
                for ctx, ref in mentions[:3]:
                    f.write(f'   - {esc(ctx, 250)} {ref}\n')
                f.write('\n')
        counts['著作段落'] = len(special['works'])
    
    elif key == 'deng':
        special = extract_deng(pages)
        f.write(f'#### 5.1 核心概念定义与使用\n\n')
        for concept, mentions in special['concepts'].items():
            if mentions:
                f.write(f'**「{concept}」** ({len(mentions)}处)\n\n')
                for ctx, ref in mentions[:3]:
                    f.write(f'   - {esc(ctx, 250)} {ref}\n')
                f.write('\n')
        f.write(f'#### 5.2 南巡讲话相关\n\n')
        for para, ref, kw in special['south_tour'][:10]:
            f.write(f'- **[{kw}]** {esc(para, 250)} {ref}\n')
        f.write('\n')
        f.write(f'#### 5.3 市场经济与社会主义\n\n')
        for para, ref, kw in special['market'][:10]:
            f.write(f'- **[{kw}]** {esc(para, 250)} {ref}\n')
        f.write('\n')
        counts['南巡段落'] = len(special['south_tour'])
    
    elif key == 'zhishen':
        special = extract_zhishen(pages)
        f.write(f'#### 5.1 核心概念定义与数据\n\n')
        for concept, mentions in special['concepts'].items():
            if mentions:
                f.write(f'**「{concept}」** ({len(mentions)}处)\n\n')
                for ctx, ref in mentions[:3]:
                    f.write(f'   - {esc(ctx, 250)} {ref}\n')
                f.write('\n')
        f.write(f'#### 5.2 各章核心论点\n\n')
        for ch_title, ch_content, ref in special['chapter_points'][:15]:
            f.write(f'- **{esc(ch_title, 60)}**：{esc(ch_content, 250)} {ref}\n')
        f.write('\n')
        counts['章节论点'] = len(special['chapter_points'])
    
    elif key == 'sapiens':
        special = extract_sapiens(pages)
        f.write(f'#### 5.1 三大革命定义与论证\n\n')
        for para, ref, kw in special['revolutions'][:10]:
            f.write(f'- **[{kw}]** {esc(para, 250)} {ref}\n')
        f.write('\n')
        f.write(f'#### 5.2 核心概念\n\n')
        for concept, mentions in special['concepts'].items():
            if mentions:
                f.write(f'**「{concept}」** ({len(mentions)}处)\n\n')
                for ctx, ref in mentions[:3]:
                    f.write(f'   - {esc(ctx, 250)} {ref}\n')
                f.write('\n')
        f.write(f'#### 5.3 集体虚构：金钱/国家/宗教\n\n')
        for para, ref, kw in special['fictions'][:10]:
            f.write(f'- **[{kw}]** {esc(para, 250)} {ref}\n')
        f.write('\n')
        counts['革命论述'] = len(special['revolutions'])
    
    elif key == 'sociology':
        special = extract_sociology(pages)
        f.write(f'#### 5.1 核心概念\n\n')
        for concept, mentions in special['concepts'].items():
            if mentions:
                f.write(f'**「{concept}」** ({len(mentions)}处)\n\n')
                for ctx, ref in mentions[:3]:
                    f.write(f'   - {esc(ctx, 250)} {ref}\n')
                f.write('\n')
        f.write(f'#### 5.2 《金翼》核心案例\n\n')
        for para, ref, kw in special['jinyi'][:10]:
            f.write(f'- **[{kw}]** {esc(para, 250)} {ref}\n')
        f.write('\n')
        f.write(f'#### 5.3 单位制论述\n\n')
        for para, ref, kw in special['danwei'][:10]:
            f.write(f'- **[{kw}]** {esc(para, 250)} {ref}\n')
        f.write('\n')
        f.write(f'#### 5.4 乡村治理\n\n')
        for para, ref, kw in special['rural'][:10]:
            f.write(f'- **[{kw}]** {esc(para, 250)} {ref}\n')
        f.write('\n')
        counts['金翼案例'] = len(special['jinyi'])
    
    return counts


def main():
    all_counts = {}
    
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write('# 6本EPUB深度知识提取报告\n\n')
        f.write(f'> 自动提取 · 5类知识 × 6本书\n')
        f.write(f'> 数据源：`/data/political-books-extracted/` 下的 epub_/mobi_ JSON\n')
        f.write(f'> 引用格式：[text/part00XX.html] 为HTML文件序号\n\n')
        f.write('---\n\n')
        
        f.write('## 目录\n\n')
        for i, (key, (_, title, author)) in enumerate(BOOK_FILES.items(), 1):
            f.write(f'{i}. [{title}（{author}）](#{i}-{key})\n')
        f.write('\n')
        
        for i, (key, (_, title, author)) in enumerate(BOOK_FILES.items(), 1):
            print(f'  Processing: {title} ({key})...')
            book_title, book_author, pages = load_book(key)
            f.write(f'<a id="{i}-{key}"></a>\n')
            counts = write_book_section(f, key, title, author, pages)
            all_counts[key] = (title, counts)
            print(f'    Done: {counts}')
        
        # 总结表
        f.write('\n---\n\n')
        f.write('## 提取统计汇总\n\n')
        f.write('| 书名 | 定义性陈述 | 核心命题 | 关键数据 | 目录章节 | 专属提取 |\n')
        f.write('|------|----------|---------|---------|---------|---------|\n')
        for key, (_, title, _) in BOOK_FILES.items():
            if key in all_counts:
                _, c = all_counts[key]
                special_count = sum(v for k, v in c.items() if k not in ['定义性陈述', '核心命题', '关键数据', '目录章节'])
                f.write(f'| {title} | {c.get("定义性陈述",0)} | {c.get("核心命题",0)} | {c.get("关键数据",0)} | {c.get("目录章节",0)} | {special_count} |\n')
        f.write('\n')
    
    print(f'\n✅ 输出完成: {OUT_FILE}')
    print(f'   文件大小: {os.path.getsize(OUT_FILE) / 1024:.1f} KB')


if __name__ == '__main__':
    main()
