#!/usr/bin/env python3
"""提取邓小平文选12篇核心篇章的完整文本"""

import json
import re

DATA = '/mnt/c/workspace/essence/data/political-books-extracted/epub_0695ef24be80eecef2179ca7122c88a9.json'

d = json.load(open(DATA))
ft = d['full_text']  # list of {file, text}

# Build a page index: find article boundaries
# Each article page starts with "邓小平文选（二/三）" then article number + title
vol2_start = None
vol3_start = None
for i, p in enumerate(ft):
    if '邓小平文选（二）' in p['text'] and '第二卷' in p['text']:
        vol2_start = i
    if '邓小平文选（三）' in p['text'] and '第三卷' in p['text']:
        vol3_start = i

print(f"Vol2 starts at page {vol2_start}, Vol3 starts at page {vol3_start}")

# Find all article starts in vol2 and vol3
# Article pages have pattern: number.title at start (after header line)
def find_article_starts():
    """Return dict: (vol, article_num) -> page_index"""
    starts = {}
    for i in range(vol2_start, len(ft)):
        text = ft[i]['text']
        # Skip TOC pages (they have many numbered items)
        if text.count('\n') > 5 and '001.' in text:
            continue
        # Match article header: starts with number like "023." or "23."
        # The article starts after "邓小平文选（X）\n\n"
        lines = text.strip().split('\n')
        for line_idx, line in enumerate(lines[:5]):
            line = line.strip()
            m = re.match(r'^(\d{1,3})\.(.+)', line)
            if m:
                num = int(m.group(1))
                title = m.group(2).strip()
                # Check if next line looks like a date
                if line_idx + 1 < len(lines):
                    next_line = lines[line_idx + 1].strip()
                    if re.search(r'一九|年', next_line) or len(next_line) < 5:
                        vol = 2 if i < vol3_start else 3
                        starts[(vol, num)] = (i, title)
                        break
    return starts

starts = find_article_starts()
print(f"\nFound {len(starts)} article starts")

# Define the 12 key works to extract
KEY_WORKS = {
    'w1': {'vol': 2, 'num': 23, 'title': '解放思想，实事求是，团结一致向前看', 'date': '1978.12.13'},
    'w2': {'vol': 2, 'num': 26, 'title': '坚持四项基本原则', 'date': '1979.3.30'},
    'w3': {'vol': 2, 'num': 39, 'title': '对起草《关于建国以来党的若干历史问题的决议》的意见', 'date': '1980-1981'},
    'w4': {'vol': 2, 'num': 56, 'title': '党和国家领导制度的改革', 'date': '1980.8.18'},
    'w5': {'vol': 3, 'num': 22, 'title': '建设有中国特色的社会主义', 'date': '1984.6.30'},
    'w6': {'vol': 3, 'num': 21, 'title': '一个国家，两种制度', 'date': '1984.6'},
    'w7': {'vol': 3, 'num': 119, 'title': '在武昌、深圳、珠海、上海等地的谈话要点（南巡讲话）', 'date': '1992.1-2'},
    'w8': {'vol': 3, 'num': 89, 'title': '科学技术是第一生产力', 'date': '1988.9'},
    'w9': {'vol': 3, 'num': 93, 'title': '压倒一切的是稳定', 'date': '1989.2'},
    'w10': {'vol': 3, 'num': 117, 'title': '视察上海时的谈话', 'date': '1991.1-2'},
    'w11': {'vol': 3, 'num': 88, 'title': '总结历史是为了开辟未来', 'date': '1988.9'},
    'w12a': {'vol': 2, 'num': 34, 'title': '社会主义也可以搞市场经济', 'date': '1979.11'},
    'w12b': {'vol': 3, 'num': 48, 'title': '社会主义和市场经济不存在根本矛盾', 'date': '1985.10'},
    'w12c': {'vol': 3, 'num': 66, 'title': '计划和市场都是发展生产力的方法', 'date': '1987.2'},
}

# For each key work, find its text range and extract
def get_sorted_starts(vol):
    """Get sorted list of (num, page) for a volume"""
    items = [(num, info[0]) for (v, num), info in starts.items() if v == vol]
    return sorted(items)

vol2_sorted = get_sorted_starts(2)
vol3_sorted = get_sorted_starts(3)

def extract_work(vol, num):
    """Extract full text of an article"""
    sorted_list = vol2_sorted if vol == 2 else vol3_sorted
    # Find start
    start_idx = None
    start_page = None
    for idx, (n, p) in enumerate(sorted_list):
        if n == num:
            start_idx = idx
            start_page = p
            break
    if start_idx is None:
        return None, None, None
    
    # Find end = start of next article
    if start_idx + 1 < len(sorted_list):
        end_page = sorted_list[start_idx + 1][1]
    else:
        end_page = len(ft)
    
    # Extract text
    texts = []
    for i in range(start_page, end_page):
        texts.append(ft[i]['text'])
    
    full = '\n'.join(texts)
    # Clean: remove repeated "邓小平文选（X）" headers
    full = re.sub(r'邓小平文选（[二三二]）\n*', '', full)
    
    return full, start_page, end_page

# Extract all works and save
works_data = {}
for key, info in KEY_WORKS.items():
    text, sp, ep = extract_work(info['vol'], info['num'])
    if text:
        works_data[key] = {**info, 'text': text, 'start_page': sp, 'end_page': ep, 'char_count': len(text)}
        print(f"[{key}] {info['title']}: pages {sp}-{ep}, {len(text)} chars")
    else:
        print(f"[{key}] {info['title']}: NOT FOUND!")

# Save extracted texts
json.dump(works_data, open('/tmp/deng_works_extracted.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\nSaved {len(works_data)} works to /tmp/deng_works_extracted.json")
