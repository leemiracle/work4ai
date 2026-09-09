#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 theme-central-local-relations.md
从 all_items.json 中精选各专题的原文引用，按文档结构组织。
"""
import json, re
from pathlib import Path
from collections import defaultdict

CACHE = Path('/mnt/c/workspace/essence/analysis/scripts/_central_local_cache')
items = json.loads((CACHE/'all_items.json').read_text(encoding='utf-8'))

def pk(r):
    m = re.search(r'(\d+)', str(r.get('page','')))
    return int(m.group(1)) if m else 9999

def clean(t):
    """清理文本：去掉多余空白"""
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def select(author, groups, min_len=80, max_items=999, must_have=None, sort_by_page=True):
    """筛选条目"""
    out = []
    for r in items:
        if r['author'] != author: continue
        if not any(g in r['groups'] for g in groups): continue
        if len(r['text']) < min_len: continue
        if must_have and must_have not in r['text']: continue
        out.append(r)
    if sort_by_page:
        out.sort(key=pk)
    return out[:max_items]

def select_any(authors, groups, min_len=80, max_items=999, must_have=None):
    out = []
    for r in items:
        if r['author'] not in authors: continue
        if not any(g in r['groups'] for g in groups): continue
        if len(r['text']) < min_len: continue
        if must_have and must_have not in r['text']: continue
        out.append(r)
    out.sort(key=pk)
    return out[:max_items]

def fmt(r):
    """格式化一条引用"""
    t = clean(r['text'])
    page = r.get('page','')
    if page and not page.startswith('p'):
        page = f'p{page}' if page.isdigit() else page
    return f"> **{r['book']}** | {r['author']} | {page}\n>\n> {t}\n"

# ============================================================
# 收集各专题内容
# ============================================================
sections = {}

# --- 周雪光框架 ---
sections['zxg_yitong'] = select('周雪光', ['一统体制','有效治理'], min_len=60)
sections['zxg_control'] = select('周雪光', ['控制权'], min_len=60)
sections['zxg_gongmou'] = select('周雪光', ['共谋'], min_len=60)
sections['zxg_yundong'] = select('周雪光', ['运动式治理'], min_len=60)

# --- 周黎安框架 ---
sections['zla_fabao'] = select('周黎安', ['行政发包'], min_len=80)
sections['zla_jinbiao'] = select('周黎安', ['锦标赛'], min_len=80)

# --- 周飞舟框架 ---
sections['zfz_fiscal'] = select('周飞舟', ['央地总论','分税制','集权分权'], min_len=60)
sections['zfz_transfer'] = select('周飞舟', ['转移支付'], min_len=60)
sections['zfz_budget'] = select('周飞舟', ['预算约束'], min_len=60)

# --- 机制详解 ---
sections['mech_fabao_all'] = select_any(['周黎安','周雪光','周飞舟'], ['行政发包'], min_len=80)
sections['mech_jinbiao_all'] = select_any(['周黎安','周雪光','周飞舟'], ['锦标赛'], min_len=80)
sections['mech_yundong_all'] = select_any(['周雪光','周黎安','周飞舟'], ['运动式治理'], min_len=60)
sections['mech_gongmou_all'] = select_any(['周雪光','周黎安','周飞舟'], ['共谋'], min_len=60)
sections['mech_tudi_all'] = select_any(['周飞舟','周黎安','周雪光','黄奇帆'], ['土地财政'], min_len=60)

# --- 数据 ---
sections['data_all'] = [r for r in items if r['section']=='数据点' and any(g in r['groups'] for g in ['财税总论','分税制','转移支付','土地财政','预算约束','央地总论'])]
# 也从 MD 中提取含数字的关键数据
sections['data_md'] = select_any(['周飞舟','周黎安','周雪光','黄奇帆'], ['财税总论','分税制','转移支付'], min_len=40)
# 过滤只保留含百分比/年份/数值的
sections['data_md'] = [r for r in sections['data_md'] if re.search(r'\d+[.%％]|\d{4}年|亿|万亿', r['text'])]

# --- 历史演变 ---
sections['history'] = select_any(['周飞舟','周黎安','周雪光'], ['集权分权','央地总论'], min_len=60, must_have=None)
# 过滤含年份的
sections['history'] = [r for r in sections['history'] if re.search(r'\d{4}|改革前|统收统支|包干|分税制|大跃进|文革|改革开放', r['text'])]

# 输出统计
for k, v in sections.items():
    print(f'{k}: {len(v)}')

# 保存到 JSON 供生成器使用
(CACHE/'sections.json').write_text(
    json.dumps({k: v for k, v in sections.items()}, ensure_ascii=False, indent=2),
    encoding='utf-8')
print('\n sections.json written')
