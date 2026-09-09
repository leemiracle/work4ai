#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面解析三份 MD 提取文件 + JSON 知识库，
按"央地关系"专题组织所有相关原文引用。
"""
import json, re, html
from pathlib import Path
from collections import defaultdict, OrderedDict

ROOT = Path('/mnt/c/workspace/essence')
JSON_PATH = ROOT / 'data/political-books-extracted/knowledge_index.json'
OUT_PATH = ROOT / 'analysis/theme-central-local-relations.md'

# ============================================================
# A. 解析 周雪光 MD：核心理论命题段（### 📄 第 XX 页）
# ============================================================
def parse_zhou_xueguang():
    """返回 [{author, book, page, text, section}]"""
    txt = (ROOT/'analysis/extracted-knowledge-zhou-xueguang.md').read_text(encoding='utf-8')
    book = '中国国家治理的制度逻辑'
    author = '周雪光'
    items = []
    # 切出 "核心理论命题" 和 "定义性陈述" 和 "关键数据" 三段
    for sec_name, sec_label in [('二、定义性陈述','定义性陈述'),
                                 ('三、关键数据','关键数据'),
                                 ('四、核心理论命题','核心理论命题'),
                                 ('五、关键案例','关键案例')]:
        # 找该段
        m = re.search(rf'## {re.escape(sec_name)}.*?(?=\n## |\Z)', txt, re.S)
        if not m: continue
        block = m.group(0)
        # 按 "### 📄 第 XX 页" 切分
        parts = re.split(r'### 📄 第 (\d+) 页', block)
        # parts: [pre, pagenum, content, pagenum, content, ...]
        for i in range(1, len(parts)-1, 2):
            page = int(parts[i])
            content = parts[i+1]
            # 每条以 "- " 开头
            for bullet in re.findall(r'- (.+?)(?=\n- |\n### |\Z)', content, re.S):
                t = bullet.strip()
                if len(t) > 15:
                    items.append({'author':author,'book':book,'page':f'p{page}','text':t,'section':sec_label})
    return items

# ============================================================
# B. 解析 周黎安 MD：核心理论命题段（### 命题 N (p.XX)）
# ============================================================
def parse_zhou_lian():
    txt = (ROOT/'analysis/extracted-knowledge-zhou-lian.md').read_text(encoding='utf-8')
    book = '转型中的地方政府'
    author = '周黎安'
    items = []
    for sec_name, sec_label in [('2\. 定义性陈述','定义性陈述'),
                                 ('3\. 关键数据','关键数据'),
                                 ('4\. 核心理论命题','核心理论命题'),
                                 ('5\. 关键案例','关键案例')]:
        m = re.search(rf'## {sec_name}.*?(?=\n## |\Z)', txt, re.S)
        if not m: continue
        block = m.group(0)
        # 格式1: ### 命题 N (p.XX) 触发词：...
        for m2 in re.finditer(r'###\s+(?:命题|定义|数据|案例)\s*\d+\s*\(p\.?(\d+)\)[^\n]*\n+\s*>(.+?)(?=\n###|\Z)', block, re.S):
            page = int(m2.group(1))
            t = m2.group(2).strip()
            if len(t) > 15:
                items.append({'author':author,'book':book,'page':f'p{page}','text':t,'section':sec_label})
        # 格式2: ### 📄 第 XX 页（定义性陈述可能用这种）
        parts = re.split(r'### 📄 第 (\d+) 页', block)
        for i in range(1, len(parts)-1, 2):
            page = int(parts[i])
            content = parts[i+1]
            for bullet in re.findall(r'- (.+?)(?=\n- |\n### |\Z)', content, re.S):
                t = bullet.strip()
                if len(t) > 15:
                    items.append({'author':author,'book':book,'page':f'p{page}','text':t,'section':sec_label})
        # 格式3: 数字编号列表（关键数据段可能用这种）
        for m2 in re.finditer(r'^\d+\.\s*(?:>\s*)?(.+?)(?=\n\d+\.|\n###|\Z)', block, re.S | re.M):
            t = m2.group(1).strip()
            if len(t) > 20 and not t.startswith('**'):
                items.append({'author':author,'book':book,'page':'','text':t,'section':sec_label})
    return items

# ============================================================
# C. 解析 others MD：周飞舟《以利为利》等
# ============================================================
def parse_others():
    txt = (ROOT/'analysis/extracted-knowledge-others.md').read_text(encoding='utf-8')
    items = []
    # 各书段落
    book_ranges = [
        ('以利为利：财政关系与地方政府行为', '周飞舟', '一、周飞舟《以利为利》', '二、黄奇帆'),
        ('分析与思考', '黄奇帆', '二、黄奇帆《分析与思考》', '三、孙萍'),
    ]
    for book, author, start_marker, end_marker in book_ranges:
        m = re.search(rf'## {re.escape(start_marker)}.*?(?=\n## {re.escape(end_marker)}|\Z)', txt, re.S)
        if not m: continue
        block = m.group(0)
        # 各子段 B/C/D/E
        for sub_pat, sub_label in [(r'### B\. 定义性陈述','定义性陈述'),
                                    (r'### C\. 关键数据','关键数据'),
                                    (r'### D\. 核心理论命题.*','核心理论命题'),
                                    (r'### E\. 关键案例.*','关键案例')]:
            ms = re.search(sub_pat + r'.*?(?=\n### [A-Z]\.|\Z)', block, re.S)
            if not ms: continue
            sub_block = ms.group(0)
            # 数字编号列表：1. > text 或 1. text
            for m2 in re.finditer(r'^\s*\d+\.\s*(?:>\s*)?(.+?)(?=\n\s*\d+\.|\n### |\Z)', sub_block, re.S | re.M):
                t = m2.group(1).strip().lstrip('>').strip()
                if len(t) > 15:
                    items.append({'author':author,'book':book,'page':'','text':t,'section':sub_label})
    return items

# ============================================================
# D. 解析 JSON 知识库
# ============================================================
def parse_json_kb():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        KB = json.load(f)
    items = []
    # propositions
    for p in KB['propositions']:
        items.append({'author':guess_author(p.get('book','')),
                      'book':norm_book(p.get('book','')),
                      'page':p.get('page',''),
                      'text':p.get('text',''),
                      'section':'命题','theme':p.get('theme','')})
    # data_points
    for d in KB['data_points']:
        items.append({'author':guess_author(d.get('book','')),
                      'book':norm_book(d.get('book','')),
                      'page':d.get('page',''),
                      'text':d.get('text',''),
                      'section':'数据点'})
    # cases
    for c in KB['cases']:
        items.append({'author':guess_author(c.get('book','')),
                      'book':norm_book(c.get('book','')),
                      'page':c.get('page',''),
                      'text':c.get('summary',''),
                      'section':'案例'})
    # concepts -> 展开 definitions
    for c in KB['concepts']:
        for d in c.get('definitions',[]):
            items.append({'author':guess_author(d.get('book','')),
                          'book':norm_book(d.get('book','')),
                          'page':d.get('page',''),
                          'text':d.get('text',''),
                          'section':'概念定义','concept':c.get('concept','')})
    return items

def norm_book(b):
    m = {
        '中国国家治理的制度逻辑 一个组织学研究': '中国国家治理的制度逻辑',
        '以利为利：财政关系与地方政府行为': '以利为利',
        '分析与思考：黄奇帆的复旦经济课.': '分析与思考',
        '《习近平谈治国理政》第一卷': '习近平谈治国理政·第一卷',
        '《习近平谈治国理政》第二卷': '习近平谈治国理政·第二卷',
        '《习近平谈治国理政》第三卷': '习近平谈治国理政·第三卷',
    }
    return m.get(b, b)

def guess_author(book):
    b = norm_book(book)
    if '中国国家治理的制度逻辑' in b: return '周雪光'
    if '转型中的地方政府' in b: return '周黎安'
    if '以利为利' in b: return '周飞舟'
    if '分析与思考' in b: return '黄奇帆'
    if '习近平' in b: return '习近平'
    if '陈云' in b: return '陈云'
    if '钱穆' in b: return '钱穆'
    if '过渡劳动' in b: return '孙萍'
    if '政治的人生' in b: return '王沪宁'
    return '其他'

# ============================================================
# E. 合并 + 去重 + 关键词过滤
# ============================================================
KW_GROUPS = OrderedDict([
    ('央地总论', ['央地关系','中央与地方','中央—地方','中央-地方','中央和地方','中央地方','上下级政府','上下级']),
    ('集权分权', ['集权','分权','放权','权力下放','权力集中','分权让利','放权让利','权力分配','收放']),
    ('一统体制', ['一统体制','一统','权威体制','一元化','中央权威','一统决策','一统性']),
    ('有效治理', ['有效治理','治理有效性','治理逻辑','治理能力']),
    ('控制权',   ['控制权','实际权威','名义权威','所有权','检查权','考核权','决策权','执行权']),
    ('共谋',     ['共谋','合谋','串谋','基层共谋','上有政策']),
    ('行政发包', ['行政发包','行政分包','发包制','分包制','承包','包干','财政包干','包税','财政大包干','纵向发包']),
    ('锦标赛',   ['晋升锦标赛','锦标赛','晋升竞争','政治锦标赛','经济锦标赛','GDP锦标赛','官场+市场']),
    ('运动式治理',['运动型治理','运动式治理','运动式','政治动员','动员型','专项治理','纠偏']),
    ('土地财政', ['土地财政','土地出让','土地金','土地收入','土地转让','土地开发','以地生财','经营城市','经营土地','土地征用','土地金融']),
    ('分税制',   ['分税制','分税','税制改革','国税地税','国税','地税']),
    ('转移支付', ['转移支付','专项转移','一般性转移','财力转移','专项资金','专项化']),
    ('预算约束', ['预算约束','软约束','财政约束','预算软约束','软预算','财政缺口','财政压力','逆向软预算']),
    ('财税总论', ['财政','税收','税源','财政收入','财政支出','财力','税基','税收分成','收入分成','两个比重']),
])

def hit_groups(text):
    groups = []
    for gname, kws in KW_GROUPS.items():
        for kw in kws:
            if kw in text:
                groups.append(gname)
                break
    return groups

print('Parsing MD files...')
all_items = []
all_items.extend(parse_zhou_xueguang())
all_items.extend(parse_zhou_lian())
all_items.extend(parse_others())
print(f'  MD items: {len(all_items)}')

print('Parsing JSON KB...')
json_items = parse_json_kb()
print(f'  JSON items: {len(json_items)}')

# 合并
combined = all_items + json_items

# 去重（按 text 前80字符 + author + page）
seen = set()
deduped = []
for it in combined:
    key = (it.get('author',''), it.get('page',''), it['text'][:80])
    if key in seen: continue
    seen.add(key)
    deduped.append(it)
print(f'  Combined deduped: {len(deduped)}')

# 关键词命中
for it in deduped:
    it['groups'] = hit_groups(it['text'])

# 保存
cache = ROOT/'analysis/scripts/_central_local_cache'
cache.mkdir(parents=True, exist_ok=True)
(cache/'all_items.json').write_text(
    json.dumps(deduped, ensure_ascii=False, indent=2), encoding='utf-8')

# 统计
from collections import Counter
gcount = Counter()
for it in deduped:
    for g in it['groups']:
        gcount[g] += 1
print('\nHits by group:')
for g in KW_GROUPS:
    print(f'  {g}: {gcount[g]}')

# 按作者统计
acount = Counter(it['author'] for it in deduped)
print('\nBy author:')
for a, c in acount.most_common():
    print(f'  {c:4d}  {a}')

print('\nDONE - all_items.json written')
