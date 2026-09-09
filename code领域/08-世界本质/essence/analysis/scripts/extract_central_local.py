#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取"央地关系"主题的所有内容
数据源：
  1. knowledge_index.json (concepts/propositions/data_points/cases/cross_book_index)
  2. extracted-knowledge-zhou-xueguang.md
  3. extracted-knowledge-zhou-lian.md
  4. extracted-knowledge-others.md
"""
import json
import re
from pathlib import Path
from collections import defaultdict, OrderedDict

ROOT = Path('/mnt/c/workspace/essence')
JSON_PATH = ROOT / 'data/political-books-extracted/knowledge_index.json'
MD_FILES = {
    'zhou_xueguang': ROOT / 'analysis/extracted-knowledge-zhou-xueguang.md',
    'zhou_lian':     ROOT / 'analysis/extracted-knowledge-zhou-lian.md',
    'others':        ROOT / 'analysis/extracted-knowledge-others.md',
}

# 关键词分组（用于分类）
KW_GROUPS = OrderedDict([
    ('央地总论',  ['央地关系', '中央与地方', '中央—地方', '中央-地方', '中央和地方', '上下级', '上下级政府', '中央地方']),
    ('集权分权',  ['集权', '分权', '放权', '权力下放', '权力集中', '分权让利', '放权让利', '权力分配']),
    ('一统体制',  ['一统体制', '一统', '权威体制', '一元化', '中央权威']),
    ('有效治理',  ['有效治理', '治理有效性', '治理逻辑']),
    ('控制权',    ['控制权', '实际权威', '名义权威', '所有权', '检查权', '考核权']),
    ('共谋',      ['共谋', '合谋', '串谋', '基层共谋']),
    ('行政发包',  ['行政发包', '行政分包', '发包制', '分包制', '承包', '包干', '财政包干', '包税', '财政大包干']),
    ('锦标赛',    ['晋升锦标赛', '锦标赛', '晋升竞争', '政治锦标赛', '经济锦标赛', 'GDP锦标赛']),
    ('运动式治理', ['运动型治理', '运动式治理', '运动式', '政治动员', '动员型', '专项治理']),
    ('土地财政',  ['土地财政', '土地出让', '土地金', '土地收入', '土地转让', '土地开发', '以地生财', '经营城市', '经营土地']),
    ('分税制',    ['分税制', '分税', '税制改革', '国税地税', '国税', '地税']),
    ('转移支付',  ['转移支付', '专项转移', '一般性转移', '财力转移']),
    ('预算约束',  ['预算约束', '软约束', '财政约束', '预算软约束', '软预算', '财政缺口', '财政压力']),
    ('财税总论',  ['财政', '税收', '税源', '财政收入', '财政支出', '财力', '税基', '税收分成', '收入分成']),
])

# 扁平化关键词清单（大集合，用于 JSON 内文搜索）
ALL_KW = []
for kws in KW_GROUPS.values():
    ALL_KW.extend(kws)
# 去重保序
ALL_KW = list(OrderedDict.fromkeys(ALL_KW))

def hit_groups(text):
    """返回 text 命中的关键词组列表"""
    groups = []
    for gname, kws in KW_GROUPS.items():
        for kw in kws:
            if kw in text:
                groups.append(gname)
                break
    return groups

# ============================================================
# 1. 加载 JSON
# ============================================================
print('>> Loading JSON ...')
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    KB = json.load(f)

def item_text(item):
    return ' '.join(str(v) for v in item.values() if isinstance(v, (str, int, float)))

# 在 JSON 各池子里搜索
json_hits = defaultdict(list)   # group -> list[(section, item)]
for section in ['concepts', 'propositions', 'data_points', 'cases', 'cross_book_index']:
    for item in KB[section]:
        text = item_text(item)
        groups = hit_groups(text)
        if groups:
            for g in set(groups):
                json_hits[g].append((section, item))

print('>> JSON hit counts by group:')
for g in KW_GROUPS:
    print(f'   {g}: {len(json_hits[g])}')

# ============================================================
# 2. 加载并切分 markdown 提取文件
# ============================================================
# 每个 md 文件大致结构：以 "## " 或 "### " 或 "- **" 分块
# 我们按"段落块"切分，每个块尽量带上书名/作者/页码

MD_BLOCKS = []   # list of dict {source_file, raw, text}
for fname, fpath in MD_FILES.items():
    raw = fpath.read_text(encoding='utf-8')
    # 按 markdown 块切分：以空行分隔，但保留标题
    # 这里采用更稳妥方式：按行切，每个连续非空行组为一块
    lines = raw.split('\n')
    cur = []
    def flush(buf):
        if buf:
            t = '\n'.join(buf)
            if t.strip():
                MD_BLOCKS.append({'source_file': fname, 'raw': t, 'text': t})
    for ln in lines:
        if ln.strip() == '':
            flush(cur); cur = []
        else:
            cur.append(ln)
    flush(cur)

print(f'>> MD blocks total: {len(MD_BLOCKS)}')

md_hits = defaultdict(list)
for blk in MD_BLOCKS:
    groups = hit_groups(blk['text'])
    if groups:
        for g in set(groups):
            md_hits[g].append(blk)

print('>> MD hit counts by group:')
for g in KW_GROUPS:
    print(f'   {g}: {len(md_hits[g])}')

# ============================================================
# 3. 输出中间结果到 json，便于后续组织文档
# ============================================================
out_dir = ROOT / 'analysis/scripts/_central_local_cache'
out_dir.mkdir(parents=True, exist_ok=True)

# JSON 命中（保留原始 item）
json_export = {}
for g, items in json_hits.items():
    json_export[g] = [{'section': s, 'item': it} for s, it in items]
(out_dir / 'json_hits.json').write_text(
    json.dumps(json_export, ensure_ascii=False, indent=2), encoding='utf-8')

# MD 命中（保留原文块）
md_export = {}
for g, blks in md_hits.items():
    md_export[g] = [{'source_file': b['source_file'], 'text': b['text']} for b in blks]
(out_dir / 'md_hits.json').write_text(
    json.dumps(md_export, ensure_ascii=False, indent=2), encoding='utf-8')

# 汇总：按书统计
book_stat = defaultdict(int)
for s, it in [(s, it) for items in json_hits.values() for s, it in items]:
    book = it.get('book', it.get('name', '?'))
    book_stat[book] += 1
for blk in MD_BLOCKS:
    pass  # md 已在 json 中体现，不重复计

print('\n>> Hits by book (JSON):')
for b, c in sorted(book_stat.items(), key=lambda x: -x[1]):
    print(f'   {c:4d}  {b}')

print('\n>> Cache written to', out_dir)
print('DONE')
