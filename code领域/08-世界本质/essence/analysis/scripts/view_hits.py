#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看各作者/各主题的命中内容，按作者+页码排序，去重"""
import json
from pathlib import Path
from collections import defaultdict

CACHE = Path('/mnt/c/workspace/essence/analysis/scripts/_central_local_cache')
json_hits = json.loads((CACHE/'json_hits.json').read_text(encoding='utf-8'))
md_hits  = json.loads((CACHE/'md_hits.json').read_text(encoding='utf-8'))

# 书名归一化
def norm_book(b):
    if not b: return '?'
    b = str(b)
    m = {
        '中国国家治理的制度逻辑 一个组织学研究': '中国国家治理的制度逻辑',
        '以利为利：财政关系与地方政府行为': '以利为利',
        '分析与思考：黄奇帆的复旦经济课.': '分析与思考',
        '《习近平谈治国理政》第一卷': '习近平谈治国理政·第一卷',
        '《习近平谈治国理政》第二卷': '习近平谈治国理政·第二卷',
        '《习近平谈治国理政》第三卷': '习近平谈治国理政·第三卷',
    }
    return m.get(b, b)

def author_of(book):
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
    return '?'

def page_key(p):
    """页码排序：抽取数字"""
    import re
    m = re.search(r'(\d+)', str(p))
    return int(m.group(1)) if m else 0

# 把 json_hits 重新组织成 (author, book, page, text, group, section)
flat = []
for g, items in json_hits.items():
    for rec in items:
        it = rec['item']
        sec = rec['section']
        book = norm_book(it.get('book', it.get('name','')))
        author = author_of(book)
        page = it.get('page','')
        # 取文本：propositions/data_points 有 text；concepts 取 definitions 或 mentions；cases 取 summary
        text = ''
        if sec == 'concepts':
            # 展开为多条
            defs = it.get('definitions', [])
            ms = it.get('mentions', [])
            for d in defs:
                flat.append((author, norm_book(d.get('book',book)), d.get('page',page),
                             d.get('text',''), g, 'concept-def', it.get('concept','')))
            for m in ms:
                flat.append((author, norm_book(m.get('book',book)), m.get('page',page),
                             m.get('text',''), g, 'concept-mention', it.get('concept','')))
            continue
        elif sec == 'cases':
            text = it.get('summary','') or it.get('text','')
        else:
            text = it.get('text','')
        if text:
            flat.append((author, book, page, text, g, sec, ''))

# 去重 (author,book,page,text)
seen = set()
dedup = []
for row in flat:
    k = (row[0],row[1],row[2],row[3][:80])
    if k in seen: continue
    seen.add(k)
    dedup.append(row)

print(f'Total dedup rows: {len(dedup)}')

# 按作者统计
by_author = defaultdict(int)
for r in dedup:
    by_author[r[0]] += 1
print('\nBy author:')
for a,c in sorted(by_author.items(), key=lambda x:-x[1]):
    print(f'  {c:4d}  {a}')

# 保存为可查询格式
(CACHE/'flat_hits.json').write_text(
    json.dumps([{'author':r[0],'book':r[1],'page':r[2],'text':r[3],
                 'group':r[4],'section':r[5],'concept':r[6]} for r in dedup],
               ensure_ascii=False, indent=2), encoding='utf-8')
print('\nWrote flat_hits.json')
