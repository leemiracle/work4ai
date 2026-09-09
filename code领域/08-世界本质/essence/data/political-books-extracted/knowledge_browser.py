#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政治类书目知识浏览器（交互式）
==============================
浏览 / 搜索 knowledge_index.json 中的政治学知识库。
纯标准库实现（json / os / re / random / sys），无外部依赖。

用法:
    python3 knowledge_browser.py
"""

import json
import os
import re
import random
import sys
from collections import Counter, defaultdict

# ──────────────────────────────────────────────────────────────
#  颜色（ANSI）
# ──────────────────────────────────────────────────────────────
class C:
    RED      = '\033[91m'
    GREEN    = '\033[92m'
    YELLOW   = '\033[93m'
    BLUE     = '\033[94m'
    MAGENTA  = '\033[35m'
    CYAN     = '\033[96m'
    ORANGE   = '\033[38;5;208m'
    GRAY     = '\033[90m'
    BOLD     = '\033[1m'
    DIM      = '\033[2m'
    RESET    = '\033[0m'
    # 主题分类配色
    THEME_COLORS = {}

def clr(text, color):
    """上色"""
    return f"{color}{text}{C.RESET}"

def hl(text, keyword):
    """高亮关键词（大小写不敏感）"""
    if not keyword:
        return text
    try:
        return re.sub(
            re.escape(keyword),
            clr(keyword, C.RED + C.BOLD),
            text,
            flags=re.IGNORECASE,
        )
    except re.error:
        return text.replace(keyword, clr(keyword, C.RED + C.BOLD))

# 启用 Windows 终端 ANSI 支持（仅 Windows 需要）
if sys.platform.startswith('win'):
    try:
        os.system('')  # 触发 VT100 模式
    except Exception:
        pass

# ──────────────────────────────────────────────────────────────
#  数据加载
# ──────────────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(HERE, 'knowledge_index.json')

def load_index():
    if not os.path.exists(INDEX_PATH):
        print(clr(f"找不到知识库文件: {INDEX_PATH}", C.RED))
        print(clr("请先运行 build_knowledge_index.py 生成知识库。", C.YELLOW))
        sys.exit(1)
    with open(INDEX_PATH, encoding='utf-8') as f:
        return json.load(f)

def load_book_files():
    """扫描所有书目 JSON（非 ocr_ / 非索引），用于按书浏览时取目录。
    返回 {md5_or_name: {'filename','toc','total_chars'}}"""
    books = {}
    for fn in os.listdir(HERE):
        if not fn.endswith('.json'):
            continue
        if fn.startswith('ocr_') or fn == 'knowledge_index.json':
            continue
        path = os.path.join(HERE, fn)
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        books[fn] = {
            'filename': d.get('filename', ''),
            'toc': d.get('toc') or [],
            'total_chars': d.get('total_chars', 0),
        }
    return books

def find_toc_for_book(book_name, book_files):
    """根据知识库中的干净书名，在原始文件里模糊匹配目录。"""
    name = book_name.strip()
    # 直接子串匹配
    candidates = []
    for fn, info in book_files.items():
        full = info['filename'] or fn
        # 清理文件名里的符号便于匹配
        if name in full or name.replace('·', '') in full.replace('·', ''):
            candidates.append(info)
    # 取 toc 非空且字符数最多的
    candidates = [c for c in candidates if c['toc']]
    if candidates:
        return max(candidates, key=lambda x: x['total_chars'])['toc']
    # 退化：关键词匹配
    keys = [k for k in re.split(r'[·《》（）\s]+', name) if len(k) >= 2]
    if keys:
        scored = []
        for fn, info in book_files.items():
            full = (info['filename'] or fn)
            score = sum(1 for k in keys if k in full)
            if score > 0 and info['toc']:
                scored.append((score, info))
        if scored:
            scored.sort(key=lambda x: (-x[0], -x[1]['total_chars']))
            return scored[0][1]['toc']
    return None

# ──────────────────────────────────────────────────────────────
#  主题分类器（把杂乱的 theme / 文本归到 6 大类）
# ──────────────────────────────────────────────────────────────
THEME_CATEGORIES = [
    ('央地关系', C.CYAN, [
        '央地', '中央与地方', '中央地方', '地方官员', '行政发包', '晋升', '官员激励',
        '财政联邦', '分权', '属地', '考核', '目标责任', '锦标赛', '承包', '放权',
        '地方政府', '区域', '乡镇',
    ]),
    ('财政与经济', C.ORANGE, [
        '财政', '经济', 'GDP', '税收', '土地财政', '预算', '收入', '支出', '增长',
        '产业', '金融', '市场', '脱贫', '粮食', '钢产量', '煤', '物价', '货币',
        '外贸', '外汇', '基本建设', '利改税', '包干', '开发区', '招商引资', '小康',
        '民生', '人口就业',
    ]),
    ('合法性与政治', C.MAGENTA, [
        '合法性', '权威', '卡理斯玛', '政治', '党建', '党的', '统治', '意识形态',
        '宣传', '纪律', '领导', '组织', '阶级', '斗争', '专政', '党权', '党员',
        '腐败', '反腐败', '党内', '干部', '路线',
    ]),
    ('国家与社会', C.GREEN, [
        '国家治理', '国家与社会', '运动型', '运动式', '官僚', '官僚体制', '制度逻辑',
        '社会控制', '公民', '群体性', '集体', '过渡劳动', '平台', '浙江村', '社区',
        '社会组织', '治理', '社会',
    ]),
    ('历史演变', C.YELLOW, [
        '历史', '历代', '汉代', '唐代', '宋代', '明代', '清代', '演变', '传统',
        '古代', '封建', '郡县', '科举', '宰相', '皇权', '丞相', '尚书', '制度变迁',
        '陈云', '毛泽东', '邓小平', '小平', '华国锋', '江泽民', '胡耀邦', '改革开放',
        '三中全会', '制度与法术', '选举制度', '兵役', '租庸调',
    ]),
    ('国际关系', C.BLUE, [
        '外交', '国际', '世界', '全球', '外国', '中美', '战争', '贸易战',
        '一带一路', '联合国', '美国', '西方',
    ]),
]

def classify_theme(theme, text=''):
    """把一条记录的 theme + text 归入 6 大类之一。"""
    blob = f"{theme} {text}"
    best, best_score = '其他', 0
    for cat, _color, keys in THEME_CATEGORIES:
        score = sum(1 for k in keys if k in blob)
        if score > best_score:
            best, best_score = cat, score
    return best

CAT_TO_COLOR = {cat: color for cat, color, _ in THEME_CATEGORIES}

# ──────────────────────────────────────────────────────────────
#  显示辅助
# ──────────────────────────────────────────────────────────────
PAGE_SIZE = 8  # 分页每页条数

def pause(msg='按回车继续...'):
    try:
        input(clr(f"\n  {msg}", C.GRAY))
    except (EOFError, KeyboardInterrupt):
        print()

def paginate(items, render, page_size=PAGE_SIZE, keyword=''):
    """分页显示列表。render(item, idx, keyword)->渲染单条。"""
    total = len(items)
    if total == 0:
        return
    start = 0
    while start < total:
        end = min(start + page_size, total)
        print(clr(f"\n  ── 显示 {start+1}-{end} / 共 {total} 条 " + '─' * 30, C.GRAY))
        for i in range(start, end):
            render(items[i], i, keyword)
        if end >= total:
            break
        try:
            ans = input(clr(f"\n  回车=下一页  q=返回菜单 > ", C.GRAY)).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if ans == 'q':
            return
        start = end

def render_proposition(p, idx, keyword=''):
    book = p.get('book', '?')
    author = p.get('author', '')
    page = p.get('page', '')
    theme = p.get('theme', '')
    text = p.get('text', '')
    cat = classify_theme(theme, text)
    cat_color = CAT_TO_COLOR.get(cat, C.GRAY)
    print(f"\n  {clr(f'#{idx+1}', C.YELLOW)} {clr(f'[{cat}]', cat_color)}"
          + (clr(f' {theme}', C.DIM) if theme and theme != cat else ''))
    print(f"  {hl(text, keyword)}")
    print(clr(f"  ——{author}《{book}》{page}", C.GRAY))

def render_data(d, idx, keyword=''):
    book = d.get('book', '?')
    page = d.get('page', '')
    dtype = d.get('type', '')
    text = d.get('text', '')
    print(f"\n  {clr(f'#{idx+1}', C.YELLOW)} {clr(f'[{dtype}]', C.ORANGE)}")
    print(f"  {hl(text, keyword)}")
    print(clr(f"  ——《{book}》{page}", C.GRAY))

def render_case(c, idx, keyword=''):
    name = c.get('name', '?')
    book = c.get('book', '?')
    author = c.get('author', '')
    page = c.get('page', '')
    summary = c.get('summary', '')
    print(f"\n  {clr(f'#{idx+1}', C.YELLOW)} {clr(name, C.BOLD + C.GREEN)}")
    snippet = summary if len(summary) <= 240 else summary[:240] + '…'
    print(f"  {hl(snippet, keyword)}")
    print(clr(f"  ——{author}《{book}》{page}", C.GRAY))

def render_definition(d, idx, keyword=''):
    book = d.get('book', '?')
    author = d.get('author', '')
    page = d.get('page', '')
    text = d.get('text', '')
    print(f"\n  {clr(f'#{idx+1}', C.YELLOW)} {hl(text[:160], keyword)}")
    print(clr(f"  ——{author}《{book}》{page}", C.GRAY))

# ──────────────────────────────────────────────────────────────
#  菜单 1：搜索知识
# ──────────────────────────────────────────────────────────────
TYPE_OPTIONS = {
    '1': ('全部', None),
    '2': ('定义/概念', 'concepts'),
    '3': ('命题/论断', 'propositions'),
    '4': ('数据', 'data_points'),
    '5': ('案例', 'cases'),
}

def menu_search(data):
    print(clr("\n  ╭──────── 搜索知识 ────────╮", C.BLUE + C.BOLD))
    keyword = input(clr("  关键词: ", C.CYAN)).strip()
    if not keyword:
        print(clr("  未输入关键词。", C.YELLOW))
        return
    print(clr("  类型: 1=全部  2=定义  3=命题  4=数据  5=案例", C.GRAY))
    choice = input(clr("  选择 [1]: ", C.CYAN)).strip() or '1'
    label, target = TYPE_OPTIONS.get(choice, ('全部', None))

    print(clr(f"\n  🔍 搜索「{keyword}」（{label}）", C.BOLD + C.BLUE))

    kw = keyword.lower()

    # ---- 概念 ----
    if target in (None, 'concepts'):
        results = []
        for item in data['concepts']:
            if kw in item.get('concept', '').lower():
                results.append(('name', item))
                continue
            for d in item.get('definitions', []):
                if kw in d.get('text', '').lower():
                    results.append(('def', item)); break
            else:
                for m in item.get('mentions', []):
                    if kw in m.get('context', '').lower():
                        results.append(('mention', item)); break
        if results:
            print(clr(f"\n  {'─'*36} 📖 概念/定义 {'─'*36}", C.CYAN))
            for kind, item in results[:6]:
                concept = item['concept']
                print(clr(f"\n  📖 {concept}", C.BOLD + C.CYAN), end='')
                print(clr(f"  [定义:{item.get('def_count',0)} | 提及:{item.get('mention_count',0)}]", C.DIM))
                defs = item.get('definitions', [])
                shown = 0
                for d in defs:
                    t = d.get('text', '')
                    if kw in t.lower() or kw in concept.lower() or shown == 0:
                        book = d.get('book', '?'); author = d.get('author',''); page = d.get('page','')
                        print(f"    {clr('▸', C.GREEN)} {hl(t[:120], keyword)}")
                        print(clr(f"      ——{author}《{book}》{page}", C.GRAY))
                        shown += 1
                        if shown >= 2: break
            print(clr(f"\n  概念结果共 {len(results)} 条（显示前 {min(6,len(results))}）", C.DIM))

    # ---- 命题 ----
    if target in (None, 'propositions'):
        results = [p for p in data['propositions'] if kw in p.get('text', '').lower()]
        if results:
            print(clr(f"\n  {'─'*36} 📝 命题/论断 {'─'*36}", C.MAGENTA))
            paginate(results, render_proposition, keyword=keyword)

    # ---- 数据 ----
    if target in (None, 'data_points'):
        results = [d for d in data['data_points'] if kw in d.get('text', '').lower()]
        if results:
            print(clr(f"\n  {'─'*38} 📉 数据 {'─'*38}", C.ORANGE))
            paginate(results, render_data, keyword=keyword)

    # ---- 案例 ----
    if target in (None, 'cases'):
        results = [c for c in data['cases']
                   if kw in c.get('name', '').lower() or kw in c.get('summary', '').lower()]
        if results:
            print(clr(f"\n  {'─'*38} 📌 案例 {'─'*38}", C.GREEN))
            paginate(results, render_case, keyword=keyword)

    # ---- 跨书（仅全部搜索时附带） ----
    if target is None:
        cross = []
        for item in data.get('cross_book_index', []):
            if kw in item.get('concept', '').lower() or kw in item.get('context', '').lower():
                cross.append(item)
        if cross:
            print(clr(f"\n  {'─'*36} 🔗 跨书对照 {'─'*36}", C.YELLOW))
            grouped = defaultdict(list)
            for r in cross:
                grouped[r['concept']].append(r)
            top = sorted(grouped.items(),
                         key=lambda x: max(e.get('total_books', 0) for e in x[1]), reverse=True)[:5]
            for concept, entries in top:
                total_books = max(e.get('total_books', 0) for e in entries)
                print(f"\n  {clr('🔗', C.YELLOW)} {clr(concept, C.BOLD + C.CYAN)}"
                      + clr(f"  [{total_books} 本书涉及]", C.DIM))
                for e in entries[:3]:
                    print(clr(f"     ·《{e.get('book','?')}》 {e.get('count',0)}次", C.GRAY))

    print(clr(f"\n  {'═'*70}", C.GRAY))

# ──────────────────────────────────────────────────────────────
#  菜单 2：按主题浏览
# ──────────────────────────────────────────────────────────────
def menu_browse_theme(data):
    cats = [c[0] for c in THEME_CATEGORIES] + ['其他']
    print(clr("\n  📂 按主题浏览", C.BOLD + C.CYAN))
    for i, cat in enumerate(cats, 1):
        color = CAT_TO_COLOR.get(cat, C.GRAY)
        print(f"    {i}. {clr(cat, color)}")
    print(clr("    0. 返回", C.GRAY))
    choice = input(clr("\n  选择主题: ", C.CYAN)).strip()
    try:
        idx = int(choice) - 1
    except ValueError:
        print(clr("  无效选择。", C.YELLOW)); return
    if idx < 0 or idx >= len(cats):
        return
    selected = cats[idx]

    # 把命题/数据/案例都按主题归类
    items = []
    for p in data['propositions']:
        if classify_theme(p.get('theme', ''), p.get('text', '')) == selected:
            items.append(('命题', p))
    for d in data['data_points']:
        if classify_theme('', d.get('text', '')) == selected:
            items.append(('数据', d))
    for c in data['cases']:
        if classify_theme('', c.get('summary', '')) == selected:
            items.append(('案例', c))

    color = CAT_TO_COLOR.get(selected, C.GRAY)
    print(clr(f"\n  📂 主题「{selected}」—— 共 {len(items)} 条", C.BOLD + color))
    if not items:
        print(clr("  （该主题暂无条目）", C.DIM))
        return

    # 先给个构成概览
    comp = Counter(t for t, _ in items)
    print(clr("  构成: " + ' | '.join(f"{clr(t, C.BOLD)} {n}" for t, n in comp.items()), C.GRAY))

    def render(item, i, kw=''):
        kind, obj = item
        if kind == '命题':
            render_proposition(obj, i)
        elif kind == '数据':
            render_data(obj, i)
        else:
            render_case(obj, i)

    paginate(items, render)

# ──────────────────────────────────────────────────────────────
#  菜单 3：按书籍浏览
# ──────────────────────────────────────────────────────────────
def collect_book_index(data):
    """聚合每本书的定义/命题/数据/案例。"""
    bi = defaultdict(lambda: {
        'definitions': [], 'propositions': [],
        'data_points': [], 'cases': [],
    })
    for item in data['concepts']:
        for d in item.get('definitions', []):
            book = d.get('book', '?')
            bi[book]['definitions'].append({
                'concept': item.get('concept', ''),
                'text': d.get('text', ''),
                'author': d.get('author', ''),
                'page': d.get('page', ''),
            })
    for p in data['propositions']:
        bi[p.get('book', '?')]['propositions'].append(p)
    for d in data['data_points']:
        bi[d.get('book', '?')]['data_points'].append(d)
    for c in data['cases']:
        bi[c.get('book', '?')]['cases'].append(c)
    return bi

def menu_browse_book(data, book_files):
    bi = collect_book_index(data)
    books = sorted(bi.keys())
    print(clr("\n  📚 按书籍浏览", C.BOLD + C.GREEN))
    for i, b in enumerate(books, 1):
        info = bi[b]
        n = len(info['definitions']) + len(info['propositions']) + \
            len(info['data_points']) + len(info['cases'])
        print(f"    {clr(str(i), C.YELLOW)}. {b}  {clr(f'({n}条)', C.GRAY)}")
    print(clr("    0. 返回", C.GRAY))
    choice = input(clr("\n  选择书籍: ", C.CYAN)).strip()
    try:
        idx = int(choice) - 1
    except ValueError:
        print(clr("  无效选择。", C.YELLOW)); return
    if idx < 0 or idx >= len(books):
        return
    book = books[idx]
    info = bi[book]
    print(clr(f"\n  {'═'*60}", C.GREEN))
    print(clr(f"  📖 《{book}》", C.BOLD + C.GREEN))
    print(clr(f"  定义:{len(info['definitions'])}  命题:{len(info['propositions'])}"
              f"  数据:{len(info['data_points'])}  案例:{len(info['cases'])}", C.GRAY))

    sub = {
        '1': ('目录', None),
        '2': ('核心定义', 'definitions'),
        '3': ('核心命题', 'propositions'),
        '4': ('关键数据', 'data_points'),
        '5': ('关键案例', 'cases'),
        '0': ('返回', None),
    }
    while True:
        print(clr("\n  浏览: 1=目录 2=定义 3=命题 4=数据 5=案例 0=返回", C.GRAY))
        c = input(clr("  选择: ", C.CYAN)).strip()
        if c == '0' or c not in sub:
            break
        label, key = sub[c]

        if key is None:  # 目录
            toc = find_toc_for_book(book, book_files)
            print(clr(f"\n  📑 目录", C.BOLD + C.CYAN))
            if not toc:
                print(clr("  （该书暂无目录信息）", C.DIM))
            else:
                toc_items = toc if isinstance(toc, list) else []
                start = 0
                total = len(toc_items)
                while start < total:
                    end = min(start + PAGE_SIZE * 2, total)
                    for entry in toc_items[start:end]:
                        if isinstance(entry, list) and len(entry) >= 2:
                            level = entry[0]; title = entry[1]
                            page_no = entry[2] if len(entry) >= 3 else ''
                            indent = '    ' * min(level, 3)
                            print(f"  {indent}{clr(title, C.RESET)}"
                                  + (clr(f"  ……{page_no}", C.GRAY) if page_no else ''))
                        elif isinstance(entry, str):
                            print(f"  {entry}")
                    if end >= total:
                        break
                    try:
                        ans = input(clr("  回车=下一页 q=返回 > ", C.GRAY)).strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        print(); break
                    if ans == 'q':
                        break
                    start = end
            continue

        items = info[key]
        print(clr(f"\n  {label}（共 {len(items)} 条）", C.BOLD))
        if not items:
            print(clr("  （无）", C.DIM)); continue

        if key == 'definitions':
            def render_def(d, i, kw=''):
                print(f"\n  {clr(f'#{i+1}', C.YELLOW)} "
                      + clr(f"[{d.get('concept','')}] ", C.CYAN)
                      + hl(d.get('text','')[:160], ''))
                print(clr(f"  ——{d.get('author','')}《{book}》{d.get('page','')}", C.GRAY))
            paginate(items, render_def, page_size=PAGE_SIZE)
        elif key == 'propositions':
            paginate(items, render_proposition, page_size=PAGE_SIZE)
        elif key == 'data_points':
            paginate(items, render_data, page_size=PAGE_SIZE)
        elif key == 'cases':
            paginate(items, render_case, page_size=PAGE_SIZE)

# ──────────────────────────────────────────────────────────────
#  菜单 4：概念对照
# ──────────────────────────────────────────────────────────────
def menu_concept_compare(data):
    print(clr("\n  🔄 概念对照", C.BOLD + C.MAGENTA))
    concept_input = input(clr("  输入概念名（如：权力/合法性/运动型治理）: ", C.CYAN)).strip()
    if not concept_input:
        print(clr("  未输入概念。", C.YELLOW)); return
    kw = concept_input.lower()

    # 匹配概念
    matched = []
    for item in data['concepts']:
        if kw in item.get('concept', '').lower():
            matched.append(item)
    if not matched:
        # 退化：在定义文本里找
        for item in data['concepts']:
            for d in item.get('definitions', []):
                if kw in d.get('text', '').lower():
                    matched.append(item); break

    if not matched:
        print(clr(f"  未找到与「{concept_input}」相关的概念。", C.YELLOW))
        return

    print(clr(f"\n  找到 {len(matched)} 个相关概念", C.DIM))
    for item in matched:
        concept = item['concept']
        defs = item.get('definitions', [])
        print(clr(f"\n  {'━'*60}", C.GRAY))
        print(clr(f"  📖 {concept}", C.BOLD + C.CYAN), end='')
        print(clr(f"  [定义:{item.get('def_count',0)} | 提及:{item.get('mention_count',0)}]", C.DIM))

        if not defs:
            print(clr("  （无定义文本，仅有提及统计）", C.DIM))
            # 显示 mentions
            for m in item.get('mentions', [])[:5]:
                print(clr(f"     ·《{m.get('book','?')}》 提及{m.get('count',0)}次", C.GRAY))
            continue

        # 按书分组定义
        by_book = defaultdict(list)
        for d in defs:
            by_book[d.get('book', '?')].append(d)
        print(clr(f"  在 {clr(str(len(by_book)), C.YELLOW)} 本书/卷中有定义/使用：", C.GREEN))
        for book, dlist in by_book.items():
            author = dlist[0].get('author', '')
            print(clr(f"\n  ▸ 《{book}》{clr(author, C.DIM)}", C.BOLD + C.GREEN))
            for d in dlist[:3]:
                page = d.get('page', '')
                text = d.get('text', '')
                snippet = text if len(text) <= 200 else text[:200] + '…'
                print(f"     {clr(f'[{page}]', C.GRAY)} {hl(snippet, concept_input)}")
            if len(dlist) > 3:
                print(clr(f"     ……还有 {len(dlist)-3} 条", C.DIM))

    pause()

# ──────────────────────────────────────────────────────────────
#  菜单 5：统计总览
# ──────────────────────────────────────────────────────────────
def menu_stats(data):
    meta = data['metadata']
    counts = meta.get('entry_counts', {})

    print(clr("\n  ╔══════════════════════════════════════════════════╗", C.CYAN))
    print(clr("  ║       📊 政治学知识库 — 统计总览                 ║", C.CYAN + C.BOLD))
    print(clr("  ╚══════════════════════════════════════════════════╝", C.CYAN))

    print(clr("\n  📚 来源书籍", C.BOLD))
    for s in meta.get('sources', []):
        print(clr(f"     • {s}", C.GREEN))

    print(clr("\n  📊 条目统计", C.BOLD))
    rows = [
        ('概念定义', counts.get('concepts', len(data.get('concepts', []))), C.CYAN),
        ('理论命题', counts.get('propositions', len(data.get('propositions', []))), C.MAGENTA),
        ('数据点',   counts.get('data_points', len(data.get('data_points', []))), C.ORANGE),
        ('案例',     counts.get('cases', len(data.get('cases', []))), C.GREEN),
        ('跨书对照', counts.get('cross_book_mentions',
                                 len(data.get('cross_book_index', []))), C.YELLOW),
    ]
    total = 0
    for label, n, color in rows:
        print(f"     {clr(label, color):<18s} {clr(str(n), C.BOLD):>6s} 条")
        total += n
    print(clr(f"     {'─'*26}", C.GRAY))
    print(f"     {clr('合计', C.BOLD):<18s} {clr(str(total), C.BOLD):>6s} 条")
    print(clr(f"     总字符数: {meta.get('total_chars', '?')}", C.DIM))

    # 概念频率 TOP20
    print(clr("\n  🔥 被提及最多的概念 Top 20", C.YELLOW))
    concepts = data['concepts']
    top = sorted(concepts, key=lambda x: x.get('mention_count', 0), reverse=True)[:20]
    maxc = top[0].get('mention_count', 1) if top else 1
    for c in top:
        name = c['concept']; mc = c.get('mention_count', 0); dc = c.get('def_count', 0)
        bar = '█' * int(mc / maxc * 25) if maxc else ''
        print(f"     {clr(name, C.CYAN):<16s} 定义:{clr(str(dc), C.GREEN):>3s}"
              f" 提及:{clr(str(mc), C.YELLOW):>5s} {clr(bar, C.GREEN)}")

    # 主题分布（用 6 大类）
    print(clr("\n  📂 主题分布（六大类）", C.MAGENTA))
    cat_counter = Counter()
    for p in data['propositions']:
        cat_counter[classify_theme(p.get('theme', ''), p.get('text', ''))] += 1
    maxcat = cat_counter.most_common(1)[0][1] if cat_counter else 1
    for cat, n in cat_counter.most_common():
        color = CAT_TO_COLOR.get(cat, C.GRAY)
        bar = '█' * int(n / maxcat * 25)
        print(f"     {clr(cat, color):<12s} {clr(str(n), C.YELLOW):>5s} {clr(bar, color)}")

    # 数据类型分布
    print(clr("\n  📉 数据类型分布 Top 12", C.ORANGE))
    dtypes = Counter(d.get('type', '未分类') for d in data['data_points'])
    maxd = dtypes.most_common(1)[0][1] if dtypes else 1
    for dt, n in dtypes.most_common(12):
        bar = '█' * int(n / maxd * 25)
        print(f"     {clr(dt[:18], C.RESET):<20s} {clr(str(n), C.YELLOW):>5s} {clr(bar, C.ORANGE)}")

    # 书籍条目分布
    print(clr("\n  📚 各书条目分布", C.GREEN))
    bi = collect_book_index(data)
    book_stats = []
    for book, info in bi.items():
        n = sum(len(info[k]) for k in ('definitions','propositions','data_points','cases'))
        book_stats.append((book, n))
    for book, n in sorted(book_stats, key=lambda x: -x[1])[:15]:
        print(f"     {clr(book[:34], C.RESET):<36s} {clr(str(n), C.YELLOW):>5s}")

    print(clr(f"\n  📅 知识库创建日期: {meta.get('created', '?')}", C.DIM))
    pause()

# ──────────────────────────────────────────────────────────────
#  菜单 6：随机发现
# ──────────────────────────────────────────────────────────────
def menu_random(data):
    pool = []
    for p in data['propositions']:
        pool.append(('命题', p))
    for d in data['data_points']:
        pool.append(('数据', d))
    for c in data['cases']:
        pool.append(('案例', c))
    if not pool:
        print(clr("  知识库为空。", C.YELLOW)); return

    while True:
        kind, obj = random.choice(pool)
        print(clr(f"\n  🎲 随机发现 —— [{kind}]", C.BOLD + C.YELLOW))
        if kind == '命题':
            render_proposition(obj, 0)
        elif kind == '数据':
            render_data(obj, 0)
        else:
            render_case(obj, 0)
        try:
            ans = input(clr("\n  回车=再来一条  q=返回菜单 > ", C.GRAY)).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(); return
        if ans == 'q':
            return

# ──────────────────────────────────────────────────────────────
#  主循环
# ──────────────────────────────────────────────────────────────
BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║           🏛️  政治类书目知识浏览器                            ║
║           Political Books Knowledge Browser                  ║
╚══════════════════════════════════════════════════════════════╝
"""

MENU = (
    ("1", "搜索知识（关键词）", C.BLUE),
    ("2", "按主题浏览", C.CYAN),
    ("3", "按书籍浏览", C.GREEN),
    ("4", "概念对照", C.MAGENTA),
    ("5", "统计总览", C.YELLOW),
    ("6", "随机发现", C.ORANGE),
    ("0", "退出", C.GRAY),
)

def main():
    print(clr(BANNER, C.CYAN + C.BOLD))
    data = load_index()
    book_files = load_book_files()

    meta = data['metadata']
    print(clr(f"  已加载: {meta.get('total_books','?')} 本书 · "
              f"{meta.get('total_entries','?')} 条知识", C.DIM))
    print(clr(f"  知识库: {INDEX_PATH}", C.GRAY))

    while True:
        print(clr("\n  ┌──────── 主菜单 ────────┐", C.BOLD))
        for key, label, color in MENU:
            print(f"  │  {clr(key, C.YELLOW)}. {clr(label, color)}")
        print(clr("  └────────────────────────┘", C.BOLD))
        try:
            choice = input(clr("  请选择 > ", C.CYAN)).strip()
        except (EOFError, KeyboardInterrupt):
            print(clr("\n  再见！👋", C.GRAY)); break

        if choice == '1':
            menu_search(data)
        elif choice == '2':
            menu_browse_theme(data)
        elif choice == '3':
            menu_browse_book(data, book_files)
        elif choice == '4':
            menu_concept_compare(data)
        elif choice == '5':
            menu_stats(data)
        elif choice == '6':
            menu_random(data)
        elif choice == '0':
            print(clr("\n  再见！👋  愿你在追问本质的路上不断深入。", C.GREEN))
            break
        else:
            print(clr("  无效选择，请重新输入。", C.YELLOW))

if __name__ == '__main__':
    main()
