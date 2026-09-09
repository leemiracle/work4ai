#!/usr/bin/env python3
"""
政治学知识库搜索脚本
搜索 knowledge_index.json 中的概念、命题、数据、案例
支持关键词搜索、类型过滤、跨书对照、统计

用法:
  python3 search_knowledge.py "行政发包制"
  python3 search_knowledge.py "土地财政" --type definition
  python3 search_knowledge.py "运动式治理" --type proposition
  python3 search_knowledge.py "GDP" --type data
  python3 search_knowledge.py "浙江村" --type case
  python3 search_knowledge.py "合法性" --cross-book
  python3 search_knowledge.py --stats
  python3 search_knowledge.py "财政" --book "以利为利"
  python3 search_knowledge.py "权力" --cross-book --top 5
"""

import json
import sys
import os
import argparse
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

# ── 颜色 ──
class C:
    HEADER  = '\033[95m'
    BLUE    = '\033[94m'
    CYAN    = '\033[96m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    RESET   = '\033[0m'
    # 额外颜色
    ORANGE  = '\033[38;5;208m'
    MAGENTA = '\033[35m'
    GRAY    = '\033[90m'

def colorize(text, color, enabled=True):
    if not enabled:
        return text
    return f"{color}{text}{C.RESET}"

# ── 加载知识库 ──
def load_index():
    index_path = Path(__file__).parent / "knowledge_index.json"
    if not index_path.exists():
        print(colorize(f"错误: 找不到 {index_path}", C.RED))
        sys.exit(1)
    with open(index_path, encoding='utf-8') as f:
        return json.load(f)

# ── 类型映射 ──
TYPE_MAP = {
    'definition': 'concepts',
    'concept': 'concepts',
    'concepts': 'concepts',
    '定义': 'concepts',
    '概念': 'concepts',
    'proposition': 'propositions',
    'propositions': 'propositions',
    '命题': 'propositions',
    '论断': 'propositions',
    'data': 'data_points',
    'data_points': 'data_points',
    '数据': 'data_points',
    'case': 'cases',
    'cases': 'cases',
    '案例': 'cases',
}

# ── 搜索函数 ──

def search_concepts(data, keyword, limit=20):
    """搜索概念定义"""
    results = []
    for item in data['concepts']:
        concept = item.get('concept', '')
        # 概念名匹配
        if keyword.lower() in concept.lower():
            results.append(('name_match', item))
            continue
        # 定义文本匹配
        for d in item.get('definitions', []):
            if keyword.lower() in d.get('text', '').lower():
                results.append(('def_match', item))
                break
        else:
            # mentions 匹配
            for m in item.get('mentions', []):
                if keyword.lower() in m.get('context', '').lower():
                    results.append(('mention_match', item))
                    break
    return results[:limit]

def search_propositions(data, keyword, limit=30):
    """搜索命题"""
    results = []
    for p in data['propositions']:
        text = p.get('text', '')
        if keyword.lower() in text.lower():
            results.append(p)
    return results[:limit]

def search_data_points(data, keyword, limit=30):
    """搜索数据"""
    results = []
    for d in data['data_points']:
        text = d.get('text', '')
        if keyword.lower() in text.lower():
            results.append(d)
    return results[:limit]

def search_cases(data, keyword, limit=20):
    """搜索案例"""
    results = []
    for c in data['cases']:
        name = c.get('name', '')
        summary = c.get('summary', '')
        if keyword.lower() in name.lower() or keyword.lower() in summary.lower():
            results.append(c)
    return results[:limit]

def search_cross_book(data, keyword, top_n=10):
    """跨书对照搜索"""
    results = []
    for item in data['cross_book_index']:
        concept = item.get('concept', '')
        context = item.get('context', '')
        if keyword.lower() in concept.lower() or keyword.lower() in context.lower():
            results.append(item)
    
    # 按概念分组
    grouped = defaultdict(list)
    for r in results:
        grouped[r['concept']].append(r)
    
    # 按涉及书数排序
    sorted_concepts = sorted(grouped.items(), 
                           key=lambda x: max(item.get('total_books', 0) for item in x[1]),
                           reverse=True)
    return sorted_concepts[:top_n]

# ── 显示函数 ──

def display_concepts(results, keyword):
    """显示概念搜索结果"""
    if not results:
        print(colorize(f"  未找到包含「{keyword}」的概念", C.YELLOW))
        return
    
    for match_type, item in results:
        concept = item['concept']
        print()
        print(colorize(f"{'━'*80}", C.GRAY))
        print(colorize(f"  📖 概念: {concept}", C.BOLD + C.CYAN), end='')
        print(colorize(f"  [定义:{item.get('def_count',0)} | 提及:{item.get('mention_count',0)}]", C.DIM))
        
        # 显示定义
        defs = item.get('definitions', [])
        if defs:
            shown = 0
            for d in defs:
                text = d.get('text', '')
                if keyword.lower() in text.lower() or keyword.lower() in concept.lower() or shown == 0:
                    book = d.get('book', '?')
                    author = d.get('author', '')
                    page = d.get('page', '')
                    print(f"    {colorize('▸', C.GREEN)} {colorize(text[:120], C.RESET)}")
                    print(f"      {colorize(f'——{author}《{book}》{page}', C.GRAY)}")
                    shown += 1
                    if shown >= 3:
                        break
        
        # 显示提及
        mentions = item.get('mentions', [])
        if mentions and match_type == 'mention_match':
            print(colorize(f"    📎 出现在 {len(mentions)} 本书/卷中:", C.DIM))
            for m in mentions[:3]:
                book = m.get('book', '?')
                count = m.get('count', 0)
                print(colorize(f"       {book} ({count}次)", C.GRAY))

def display_propositions(results, keyword):
    """显示命题"""
    if not results:
        print(colorize(f"  未找到包含「{keyword}」的命题", C.YELLOW))
        return
    
    for i, p in enumerate(results, 1):
        book = p.get('book', '?')
        author = p.get('author', '')
        page = p.get('page', '')
        theme = p.get('theme', '')
        text = p.get('text', '')
        
        print()
        print(colorize(f"{'━'*80}", C.GRAY))
        print(f"  {colorize(f'#{i}', C.YELLOW)} ", end='')
        if theme:
            print(colorize(f"[{theme}] ", C.MAGENTA), end='')
        print()
        print(f"  {highlight_keyword(text, keyword)}")
        print(colorize(f"  ——{author}《{book}》{page}", C.GRAY))

def display_data_points(results, keyword):
    """显示数据"""
    if not results:
        print(colorize(f"  未找到包含「{keyword}」的数据", C.YELLOW))
        return
    
    for i, d in enumerate(results, 1):
        book = d.get('book', '?')
        page = d.get('page', '')
        dtype = d.get('type', '')
        text = d.get('text', '')
        
        print()
        print(colorize(f"{'━'*80}", C.GRAY))
        print(f"  {colorize(f'#{i}', C.YELLOW)} ", end='')
        if dtype:
            print(colorize(f"[{dtype}] ", C.ORANGE), end='')
        print()
        print(f"  {highlight_keyword(text, keyword)}")
        print(colorize(f"  ——《{book}》{page}", C.GRAY))

def display_cases(results, keyword):
    """显示案例"""
    if not results:
        print(colorize(f"  未找到包含「{keyword}」的案例", C.YELLOW))
        return
    
    for i, c in enumerate(results, 1):
        name = c.get('name', '?')
        book = c.get('book', '?')
        author = c.get('author', '')
        page = c.get('page', '')
        summary = c.get('summary', '')
        
        print()
        print(colorize(f"{'━'*80}", C.GRAY))
        print(f"  {colorize(f'#{i}', C.YELLOW)} {colorize(f'📌 {name}', C.BOLD + C.GREEN)}")
        print(f"  {highlight_keyword(summary[:200], keyword)}")
        print(colorize(f"  ——{author}《{book}》{page}", C.GRAY))

def display_cross_book(grouped_results, keyword):
    """显示跨书对照"""
    if not grouped_results:
        print(colorize(f"  未找到「{keyword}」的跨书对照", C.YELLOW))
        return
    
    for concept, entries in grouped_results:
        books = [(e.get('book','?'), e.get('count',0)) for e in entries]
        total_books = max((e.get('total_books', 0) for e in entries), default=0)
        
        print()
        print(colorize(f"{'━'*80}", C.GRAY))
        print(f"  {colorize('🔗', C.MAGENTA)} {colorize(concept, C.BOLD + C.CYAN)}", end='')
        print(colorize(f"  [{colorize(str(total_books), C.YELLOW)} 本书涉及]", C.DIM))
        
        for book, count in books:
            bar = '█' * min(count // 10, 30) if count > 0 else ''
            print(f"    {colorize(f'{book}', C.RESET)}")
            print(f"    {colorize(f'{count}次 ', C.YELLOW)}{colorize(bar, C.GREEN)}")
        
        # 显示一段上下文
        if entries:
            ctx = entries[0].get('context', '')[:150]
            if ctx:
                print(colorize(f"    📎 上下文: {ctx}...", C.GRAY))

def highlight_keyword(text, keyword):
    """高亮关键词"""
    if not keyword:
        return text
    # 简单替换（避免正则复杂度）
    result = text.replace(keyword, colorize(keyword, C.RED + C.BOLD))
    return result

# ── 统计函数 ──

def show_stats(data):
    """显示统计信息"""
    meta = data['metadata']
    
    print()
    print(colorize("╔══════════════════════════════════════════════════════════════╗", C.CYAN))
    print(colorize("║          📊 政治学知识库 — 统计总览                            ║", C.CYAN + C.BOLD))
    print(colorize("╚══════════════════════════════════════════════════════════════╝", C.CYAN))
    
    print()
    print(colorize("  📚 来源书籍:", C.BOLD))
    for s in meta['sources']:
        print(colorize(f"     • {s}", C.GREEN))
    
    print()
    print(colorize("  📊 条目统计:", C.BOLD))
    counts = meta['entry_counts']
    total = meta['total_entries']
    print(f"     {colorize('概念定义', C.CYAN):20s} {counts['concepts']:>6d} 条")
    print(f"     {colorize('理论命题', C.MAGENTA):20s} {counts['propositions']:>6d} 条")
    print(f"     {colorize('数据点', C.ORANGE):20s} {counts['data_points']:>6d} 条")
    print(f"     {colorize('案例', C.GREEN):20s} {counts['cases']:>6d} 条")
    print(f"     {colorize('跨书对照', C.YELLOW):20s} {counts['cross_book_mentions']:>6d} 条")
    print(f"     {colorize('─'*20, C.GRAY)}")
    print(f"     {colorize('合计', C.BOLD):20s} {total:>6d} 条")
    print(f"     {colorize('总字符数', C.DIM):20s} {meta['total_chars']:>6d}")
    
    # 各类型详细分布
    print()
    print(colorize("  📈 各类型详细分布:", C.BOLD))
    
    # 概念 top 20
    concepts = data['concepts']
    top_concepts = sorted(concepts, key=lambda x: x.get('mention_count', 0), reverse=True)[:20]
    print()
    print(colorize("  🔥 被提及最多的概念 Top 20:", C.YELLOW))
    max_count = top_concepts[0].get('mention_count', 1) if top_concepts else 1
    for c in top_concepts:
        name = c['concept']
        mc = c.get('mention_count', 0)
        dc = c.get('def_count', 0)
        bar_len = int(mc / max_count * 25) if max_count > 0 else 0
        bar = '█' * bar_len
        print(f"     {colorize(name, C.CYAN):16s} 定义:{colorize(str(dc), C.GREEN):>3s} 提及:{colorize(str(mc), C.YELLOW):>5s} {colorize(bar, C.GREEN)}")
    
    # 命题主题分布
    print()
    themes = Counter(p.get('theme', '未分类') for p in data['propositions'])
    print(colorize("  📝 命题主题分布 Top 15:", C.MAGENTA))
    for theme, count in themes.most_common(15):
        bar_len = int(count / themes.most_common(1)[0][1] * 25)
        bar = '█' * bar_len
        print(f"     {colorize(theme[:20], C.RESET):22s} {colorize(str(count), C.YELLOW):>5s} {colorize(bar, C.MAGENTA)}")
    
    # 数据类型分布
    print()
    dtypes = Counter(d.get('type', '未分类') for d in data['data_points'])
    print(colorize("  📉 数据类型分布:", C.ORANGE))
    for dtype, count in dtypes.most_common(15):
        bar_len = int(count / dtypes.most_common(1)[0][1] * 25) if dtypes.most_common(1)[0][1] > 0 else 0
        bar = '█' * bar_len
        print(f"     {colorize(dtype[:20], C.RESET):22s} {colorize(str(count), C.YELLOW):>5s} {colorize(bar, C.ORANGE)}")
    
    # 案例来源分布
    print()
    case_books = Counter(c.get('book', '?') for c in data['cases'])
    print(colorize("  📌 案例来源分布:", C.GREEN))
    for book, count in case_books.most_common(10):
        print(f"     {colorize(book[:30], C.RESET):32s} {colorize(str(count), C.YELLOW):>5s}")
    
    # 跨书对照 top
    print()
    cross = data['cross_book_index']
    cross_by_concept = defaultdict(list)
    for c in cross:
        cross_by_concept[c['concept']].append(c)
    top_cross = sorted(cross_by_concept.items(), 
                      key=lambda x: sum(item.get('count',0) for item in x[1]), reverse=True)[:15]
    print(colorize("  🔗 跨书覆盖最广的概念 Top 15:", C.YELLOW))
    for concept, entries in top_cross:
        book_count = len(entries)
        total_count = sum(e.get('count', 0) for e in entries)
        print(f"     {colorize(concept, C.CYAN):16s} {colorize(f'{book_count}本书', C.GREEN):>8s} 总计{colorize(str(total_count), C.YELLOW)}次")
    
    print()
    print(colorize(f"  📅 创建日期: {meta.get('created', '?')}", C.DIM))
    print()

# ── 按书过滤 ──

def filter_by_book(results, book_keyword):
    """按书名过滤"""
    filtered = []
    for item in results:
        item_book = ''
        if isinstance(item, dict):
            item_book = item.get('book', '')
        elif isinstance(item, tuple):
            # concept search results
            match_type, data = item
            for d in data.get('definitions', []):
                if book_keyword.lower() in d.get('book', '').lower():
                    filtered.append(item)
                    break
            continue
        if book_keyword.lower() in item_book.lower():
            filtered.append(item)
    return filtered

# ── 主函数 ──

def main():
    parser = argparse.ArgumentParser(
        description='政治学知识库搜索',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "行政发包制"
  %(prog)s "土地财政" --type definition
  %(prog)s "运动式治理" --type proposition
  %(prog)s "GDP" --type data
  %(prog)s "浙江村" --type case
  %(prog)s "合法性" --cross-book
  %(prog)s --stats
  %(prog)s "财政" --book "以利为利"
  %(prog)s "权力" --cross-book --top 5
"""
    )
    parser.add_argument('keyword', nargs='?', default='', help='搜索关键词')
    parser.add_argument('--type', '-t', dest='search_type', 
                       choices=['definition', 'proposition', 'data', 'case', 'all'],
                       default='all', help='搜索类型')
    parser.add_argument('--cross-book', '-c', action='store_true', help='跨书对照模式')
    parser.add_argument('--book', '-b', default='', help='按书名过滤')
    parser.add_argument('--top', '-n', type=int, default=10, help='显示条数上限')
    parser.add_argument('--stats', '-s', action='store_true', help='显示统计信息')
    parser.add_argument('--no-color', action='store_true', help='禁用颜色')
    
    args = parser.parse_args()
    
    # 禁用颜色
    if args.no_color:
        global C
        for attr in dir(C):
            if not attr.startswith('_'):
                setattr(C, attr, '')
    
    # 统计模式
    if args.stats:
        data = load_index()
        show_stats(data)
        return
    
    # 需要关键词
    if not args.keyword:
        parser.print_help()
        return
    
    data = load_index()
    keyword = args.keyword
    
    # 跨书模式
    if args.cross_book:
        print()
        print(colorize(f"  🔗 跨书对照搜索: 「{keyword}」", C.BOLD + C.MAGENTA))
        results = search_cross_book(data, keyword, top_n=args.top)
        display_cross_book(results, keyword)
        return
    
    # 按类型搜索
    target = TYPE_MAP.get(args.search_type, None)
    
    if target and target != 'concepts':
        # 指定类型
        print()
        type_labels = {
            'propositions': ('📝', '命题/论断', C.MAGENTA),
            'data_points': ('📉', '数据', C.ORANGE),
            'cases': ('📌', '案例', C.GREEN),
            'concepts': ('📖', '概念/定义', C.CYAN),
        }
        icon, label, color = type_labels.get(target, ('📄', target, C.RESET))
        print(colorize(f"  {icon} {label}搜索: 「{keyword}」", C.BOLD + color))
        
        if target == 'propositions':
            results = search_propositions(data, keyword, limit=99999)
        elif target == 'data_points':
            results = search_data_points(data, keyword, limit=99999)
        elif target == 'cases':
            results = search_cases(data, keyword, limit=99999)
        elif target == 'concepts':
            results = search_concepts(data, keyword, limit=99999)
        
        # 按书过滤（在限制数量之前过滤）
        if args.book:
            if target in ('propositions', 'data_points', 'cases'):
                results = filter_by_book(results, args.book)
        
        # 显示
        if target == 'propositions':
            display_propositions(results[:args.top], keyword)
        elif target == 'data_points':
            display_data_points(results[:args.top], keyword)
        elif target == 'cases':
            display_cases(results[:args.top], keyword)
        elif target == 'concepts':
            display_concepts(results[:args.top], keyword)
        
        print()
        total = len(results)
        print(colorize(f"  找到 {total} 条结果" + (f"，显示前 {min(args.top, total)} 条" if total > args.top else ""), C.DIM))
    
    else:
        # 全部类型搜索
        print()
        print(colorize(f"  🔍 全文搜索: 「{keyword}」", C.BOLD + C.BLUE))
        
        # 概念
        concept_results = search_concepts(data, keyword, limit=5)
        if concept_results:
            print()
            print(colorize(f"  {'─'*40} 📖 概念/定义 {'─'*40}", C.CYAN))
            display_concepts(concept_results, keyword)
        
        # 命题
        prop_results = search_propositions(data, keyword, limit=args.top * 2)
        if args.book:
            prop_results = filter_by_book(prop_results, args.book)
        if prop_results:
            print()
            print(colorize(f"  {'─'*40} 📝 命题/论断 {'─'*40}", C.MAGENTA))
            display_propositions(prop_results[:args.top], keyword)
        
        # 数据
        data_results = search_data_points(data, keyword, limit=args.top * 2)
        if args.book:
            data_results = filter_by_book(data_results, args.book)
        if data_results:
            print()
            print(colorize(f"  {'─'*40} 📉 数据 {'─'*40}", C.ORANGE))
            display_data_points(data_results[:args.top], keyword)
        
        # 案例
        case_results = search_cases(data, keyword, limit=5)
        if case_results:
            print()
            print(colorize(f"  {'─'*40} 📌 案例 {'─'*40}", C.GREEN))
            display_cases(case_results[:5], keyword)
        
        # 跨书
        cross_results = search_cross_book(data, keyword, top_n=5)
        if cross_results:
            print()
            print(colorize(f"  {'─'*40} 🔗 跨书对照 {'─'*40}", C.YELLOW))
            display_cross_book(cross_results, keyword)
        
        # 总结
        print()
        print(colorize(f"  {'═'*80}", C.GRAY))
        total = len(concept_results) + len(prop_results) + len(data_results) + len(case_results)
        print(colorize(f"  合计: 概念{len(concept_results)} | 命题{len(prop_results)} | 数据{len(data_results)} | 案例{len(case_results)} | 跨书{len(cross_results)}", C.DIM))
    
    print()

if __name__ == '__main__':
    main()
