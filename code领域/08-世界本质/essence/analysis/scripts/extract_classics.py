#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5本著作全文JSON深度知识提取
- 陈云文选3卷 (合并)
- 钱穆国学作品集 (167.9万字)
- 李岚清《突围》

输出: /mnt/c/workspace/essence/analysis/extracted-knowledge-classics.md
"""
import json
import re
import os
from pathlib import Path
from collections import defaultdict, OrderedDict

DATA_DIR = Path('/mnt/c/workspace/essence/data/political-books-extracted')
OUT_FILE = Path('/mnt/c/workspace/essence/analysis/extracted-knowledge-classics.md')

# 文件映射
FILES = {
    'chen1': 'd04c58fc9b3f.json',   # 陈云文选 第一卷
    'chen2': 'b2e287a41416.json',   # 陈云文选 第二卷
    'chen3': '23b66adb7b4d.json',   # 陈云文选 第三卷
    'qian':  '26887183017c.json',   # 钱穆
    'tuwei': 'f9318869c29c.json',   # 突围
}

# 全局统计
STATS = defaultdict(int)


def load_book(key):
    """加载一本书的JSON数据"""
    p = DATA_DIR / FILES[key]
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def normalize(text):
    """规范化文本：CJK PDF特性——每字独占一行带尾随空格。
    必须去掉换行 AND 所有空格，才能让"综 合 平 衡"→"综合平衡"可搜。"""
    if not text:
        return ''
    # 去掉换行
    t = text.replace('\n', '').replace('\r', '')
    # 去掉所有空格（CJK文本不含词间空格，阿拉伯数字也是逐字排版）
    t = t.replace(' ', '').replace('\t', '')
    return t


def build_page_index(book):
    """构建页面索引：list of (page_num, normalized_text)"""
    pages = []
    for p in book['full_text']:
        pages.append({
            'page': p['page'],
            'raw': p['text'],
            'norm': normalize(p['text'])
        })
    return pages


def find_context(norm_text, keyword, ctx_chars=200, max_hits_per_page=2):
    """在规范化文本中查找关键词，返回 (start, end, context) 列表"""
    hits = []
    start = 0
    while True:
        idx = norm_text.find(keyword, start)
        if idx == -1:
            break
        s = max(0, idx - ctx_chars)
        e = min(len(norm_text), idx + len(keyword) + ctx_chars)
        ctx = norm_text[s:e]
        hits.append((s, e, ctx))
        start = idx + len(keyword)
        if len(hits) >= max_hits_per_page:
            break
    return hits


def is_toc_or_meta(norm_text):
    """检测是否是目录页/版权页/扉页等元数据页"""
    if len(norm_text) < 50:
        return True
    # 目录页特征：前100字内出现"目录"或"contents"
    head = norm_text[:100]
    if '目录' in head or 'contents' in head.lower():
        return True
    # 版权页特征
    if 'ISBN' in norm_text or '出版发行' in norm_text[:50]:
        return True
    # 扉页特征：极短且含书名
    if len(norm_text) < 150 and ('出版社' in norm_text):
        return True
    # TOC特征2：大量"（XXXX年X月X日）"+页码范围模式
    date_page_patterns = len(re.findall(r'年.{0,3}月.{0,3}日.*?\d{2,3}[—\-–]\d{2,3}', norm_text))
    if date_page_patterns >= 3:
        return True
    # TOC特征3：连续多个标题+页码对（如 "标题文字１２３"）
    toc_entries = len(re.findall(r'[\u4e00-\u9fff]{4,}[\d]{2,3}', norm_text))
    if toc_entries >= 5:
        return True
    return False


def search_all(pages, keywords, ctx_chars=200, max_per_page=2, limit=40):
    """在所有页面搜索关键词（任一匹配），返回 [{page, keyword, context, ...extra}]"""
    results = []
    seen_ctx = set()  # 去重：相同上下文只保留一条
    for pg in pages:
        # 跳过目录/版权/扉页
        if is_toc_or_meta(pg['norm']):
            continue
        for kw in keywords:
            hits = find_context(pg['norm'], kw, ctx_chars, max_per_page)
            for s, e, ctx in hits:
                # 去重key: 关键词 + 上下文前40字
                dk = (kw, ctx[:40])
                if dk in seen_ctx:
                    continue
                seen_ctx.add(dk)
                entry = {
                    'page': pg['page'],
                    'keyword': kw,
                    'context': ctx.strip()
                }
                # 保留页面对象中的额外字段（如 vol）
                for extra_k in ('vol', 'book'):
                    if extra_k in pg:
                        entry[extra_k] = pg[extra_k]
                results.append(entry)
                if len(results) >= limit:
                    return results
    return results


def search_phrase(pages, phrases, ctx_chars=250, limit=30):
    """搜索短语（更精准），每个phrase是完整字符串"""
    results = []
    seen = set()
    for pg in pages:
        for ph in phrases:
            idx = pg['norm'].find(ph)
            while idx != -1 and len([r for r in results if r['phrase'] == ph]) < limit:
                s = max(0, idx - ctx_chars)
                e = min(len(pg['norm']), idx + len(ph) + ctx_chars)
                ctx = pg['norm'][s:e].strip()
                dk = (ph, ctx[:50])
                if dk not in seen:
                    seen.add(dk)
                    results.append({
                        'page': pg['page'],
                        'phrase': ph,
                        'context': ctx
                    })
                idx = pg['norm'].find(ph, idx + len(ph))
    return results


def extract_numbers(text):
    """从文本中提取数字+单位组合（支持全角数字和中文数字）"""
    # 先把全角数字转为半角
    fw_map = str.maketrans('０１２３４５６７８９．', '0123456789.')
    t = text.translate(fw_map)
    results = []
    # 模式1：阿拉伯数字 + 中文单位
    pat1 = r'(\d+(?:\.\d+)?)\s*(亿|万|千|百)?\s*(吨|斤|公斤|千瓦|度|元|美元|亿元|万元|两|担|石|匹|台|套|辆|架|人|名|个|件|条|座|处|所|间|平方公里|公里|米|亩|顷|年|月|日|次|回|遍|分|秒|时|点|起|桩|批|类|种|项|篇|部|册|卷|届|期|轮|场|段|期)'
    for m in re.finditer(pat1, t):
        results.append(m.group(0).strip())
    # 模式2：纯阿拉伯数字（≥3位数，可能是产量/金额）
    for m in re.finditer(r'(?<![\d.])(\d{3,})(?![\d.])', t):
        results.append(m.group(0))
    # 模式3：中文数字 + 单位
    pat3 = r'([一二三四五六七八九十百千万亿两零〇]+[百千万亿]?)\s*(吨|斤|公斤|元|美元|人|名|个|件|条|座|年|月|日|亩|顷|分|万|亿)'
    for m in re.finditer(pat3, text):  # 用原文（含中文数字）
        results.append(m.group(0).strip())
    return results[:10]  # 限制数量


def md_header(text, level=2):
    return '#' * level + ' ' + text


def toc_to_markdown(toc, indent_char='  '):
    """TOC转markdown列表"""
    lines = []
    for entry in toc:
        if isinstance(entry, list) and len(entry) >= 3:
            level, title, page = entry[0], entry[1], entry[2]
            prefix = indent_char * (level - 1) + '- '
            if page and page > 0:
                lines.append(f'{prefix}{title.strip()} (p.{page})')
            else:
                lines.append(f'{prefix}{title.strip()}')
    return '\n'.join(lines)


# ============================================================
# 陈云文选 3卷 处理
# ============================================================
def process_chen_yun():
    out = []
    out.append(md_header('第一部分：陈云文选（三卷合集）', 1))
    out.append('')
    out.append('> 来源：陈云文选第一卷（786158字/454页）+ 第二卷（651050字/381页）+ 第三卷（706208字/435页），合计214万字。')
    out.append('')

    books = {k: load_book(k) for k in ['chen1', 'chen2', 'chen3']}
    vol_names = {'chen1': '第一卷', 'chen2': '第二卷', 'chen3': '第三卷'}

    # 1. 三卷完整目录
    out.append(md_header('一、三卷完整目录', 2))
    out.append('')
    for k in ['chen1', 'chen2', 'chen3']:
        b = books[k]
        out.append(md_header(f'陈云文选 {vol_names[k]}（{len(b["toc"])}条）', 3))
        out.append('')
        out.append(toc_to_markdown(b['toc']))
        out.append('')
        STATS[f'chen_toc_{k}'] = len(b['toc'])

    # 构建所有页面索引
    all_pages = []
    for k in ['chen1', 'chen2', 'chen3']:
        for pg in build_page_index(books[k]):
            pg['vol'] = vol_names[k]
            all_pages.append(pg)
    STATS['chen_total_pages'] = len(all_pages)

    # 2. 核心概念出现处
    out.append(md_header('二、核心概念出现处（页码+200字上下文）', 2))
    out.append('')

    concepts = {
        '鸟笼经济/计划与市场': ['鸟笼', '笼子', '笼中', '鸟和笼', '笼里', '笼内', '搞活', '活而不乱', '管而不死', '计划为主', '市场调节', '大计划', '小自由', '计划经济', '市场经济'],
        '综合平衡': ['综合平衡', '财政平衡', '信贷平衡', '物资平衡', '外汇平衡', '收支平衡', '四大平衡'],
        '摸着石头过河': ['摸着石头', '摸石过河', '石头过河', '摸着走', '试点', '试验', '稳步前进', '稳扎稳打'],
        '唯实/思想方法': ['不唯上', '不唯书', '只唯实', '交换、比较、反复', '交换，比较，反复', '全面、比较、反复', '交换比较反复'],
        '执政党的党风': ['执政党的党风', '党风问题', '党风', '关系到', '生死存亡'],
        '听取不同意见': ['不同意见', '反对意见', '反面意见', '多谋善断'],
        '国情/实事求是': ['国情', '实事求是', '从实际出发', '调查研究'],
    }

    for concept, keywords in concepts.items():
        out.append(md_header(f'概念：「{concept}」', 3))
        out.append('')
        results = search_all(all_pages, keywords, ctx_chars=200, max_per_page=1, limit=20)
        if not results:
            out.append('*未在文选中找到明确匹配（该概念可能以其他表述出现）。*')
            out.append('')
            continue
        for r in results:
            STATS['chen_concept_hits'] += 1
            out.append(f'- **p.{r["page"]}（{r.get("vol","")}）· 命中「{r["keyword"]}」**：')
            out.append(f'  > {r["context"]}')
            out.append('')
        out.append('')

    # 3. 经济工作具体数据
    out.append(md_header('三、经济工作具体数据（粮食/钢/财政等）', 2))
    out.append('')

    econ_keywords = {
        '粮食产量': ['粮食产量', '粮食总产', '粮食生产', '粮食征购', '粮食统购', '粮食征', '征购粮', '商品粮', '万斤粮', '亿斤粮'],
        '钢产量': ['钢产量', '钢铁产量', '产钢', '炼钢', '大炼钢铁', '钢的产量', '万吨钢', '吨钢'],
        '煤产量': ['煤产量', '煤炭产量', '原煤', '产煤'],
        '财政数据': ['财政收入', '财政支出', '财政赤字', '财政结余', '预算', '决算', '税收', '税收收入'],
        '基本建设': ['基本建设', '基建投资', '建设投资', '基建规模'],
        '物价与货币': ['物价', '通货膨胀', '货币发行', '钞票发行', '人民币发行', '币值'],
        '外贸外汇': ['外汇', '进出口', '对外贸易', '出口', '进口', '贸易额'],
        '人口就业': ['人口', '就业', '失业', '劳动力'],
    }

    for cat, keywords in econ_keywords.items():
        out.append(md_header(f'类别：「{cat}」', 3))
        out.append('')
        results = search_all(all_pages, keywords, ctx_chars=220, max_per_page=1, limit=18)
        for r in results:
            STATS['chen_econ_hits'] += 1
            # 提取该上下文中的数字
            nums = extract_numbers(r['context'])
            nums_str = '；'.join(nums[:8]) if nums else '（无数值）'
            out.append(f'- **p.{r["page"]}（{r.get("vol","")}）·「{r["keyword"]}」** 提取数字：{nums_str}')
            out.append(f'  > {r["context"]}')
            out.append('')
        if not results:
            out.append('*未找到。*')
            out.append('')

    # 4. 党建论述
    out.append(md_header('四、关于党建的论述（300字原文+页码）', 2))
    out.append('')
    party_keywords = [
        '执政党', '党的建设', '党性问题', '党性原则', '党风问题', '党内民主',
        '党的纪律', '民主集中制', '批评与自我批评', '党内斗争',
        '领导干部', '提拔干部', '干部政策', '中青年干部', '老干部',
        '纪检', '纪律检查', '纪检委', '党风建设', '党群关系',
        '党的领导', '党的组织', '党的团结', '党的路线',
    ]
    results = search_all(all_pages, party_keywords, ctx_chars=300, max_per_page=1, limit=80)
    for r in results:
        STATS['chen_party_hits'] += 1
        out.append(f'- **p.{r["page"]}（{r.get("vol","")}）·「{r["keyword"]}」**：')
        out.append(f'  > {r["context"]}')
        out.append('')

    # 5. 陈云与毛泽东/邓小平意见差异
    out.append(md_header('五、陈云与毛泽东/邓小平意见差异/互动的段落', 2))
    out.append('')

    # 精准搜索
    diff_phrases = [
        '毛主席', '毛泽东同志', '毛泽东',
        '小平同志', '邓小平',
        '不同意', '不同意见', '我有不同看法', '保留意见', '我保留',
        '纠偏', '纠左', '纠正', '调整',
        '反冒进', '冒进', '大跃进',
        '包产到户', '分田到户', '责任制',
        '七千人大会', '庐山会议', '八届', '十一届三中全会',
    ]
    results = search_all(all_pages, diff_phrases, ctx_chars=280, max_per_page=1, limit=80)
    for r in results:
        STATS['chen_diff_hits'] += 1
        out.append(f'- **p.{r["page"]}（{r.get("vol","")}）·「{r["keyword"]}」**：')
        out.append(f'  > {r["context"]}')
        out.append('')

    return '\n'.join(out)


# ============================================================
# 钱穆 处理
# ============================================================
def process_qian_mu():
    out = []
    out.append('')
    out.append(md_header('第二部分：钱穆国学作品集（167.9万字）', 1))
    out.append('')
    out.append('> 来源：钱穆国学作品集（含《中国历代政治得失》《国史大纲》《中华文化十二讲》《中国历史精神》《中国思想史》《人生十论》等），502条TOC，1460页。')
    out.append('')

    book = load_book('qian')
    pages = build_page_index(book)
    STATS['qian_total_pages'] = len(pages)

    # 1. 完整目录结构
    out.append(md_header('一、完整目录（502条，标注著作名称）', 2))
    out.append('')

    # 识别著作分界：钱穆集是多部书合集，TOC顶层应该是各书名
    # 通过TOC分析+书名识别
    known_works = [
        '中国历代政治得失', '国史大纲', '中华文化十二讲', '中国历史精神',
        '中国思想史', '人生十论', '中国文化精神', '民族与文化',
        '中国文化史导论', '政学私言', '国史新论', '文化与教育',
        '湖上闲思录', '中国学术通义', '现代中国学术论衡', '八十忆双亲',
        '师友杂忆', '庄子纂笺', '论语新解', '孔子传', '朱子学提纲',
        '宋明理学概述', '阳明学述要', '中国近三百年学术史', '国学概论',
        '中国史学发微', '中国史学名著', '史记地名考',
    ]

    current_work = None
    toc_lines = []
    work_page_ranges = {}  # work -> [start_page]
    for entry in book['toc']:
        if not (isinstance(entry, list) and len(entry) >= 3):
            continue
        level, title, page = entry[0], entry[1].strip(), entry[2]
        # 规范化标题以匹配
        title_norm = title.replace(' ', '')
        # 检测是否是已知著作名
        is_work = False
        for w in known_works:
            w_norm = w.replace(' ', '')
            if w_norm in title_norm and len(title_norm) <= len(w_norm) + 8:
                current_work = w
                toc_lines.append(f'\n### 📖 《{w}》（起 p.{page}）\n')
                work_page_ranges.setdefault(w, []).append(page)
                is_work = True
                break
        if not is_work:
            prefix = '  ' * (level - 1) + '- '
            if page and page > 0:
                toc_lines.append(f'{prefix}{title} (p.{page})')
            else:
                toc_lines.append(f'{prefix}{title}')

    out.append('\n'.join(toc_lines))
    out.append('')
    STATS['qian_toc'] = len(book['toc'])

    # 2. 重点：《中国历代政治得失》的所有论断
    out.append(md_header('二、《中国历代政治得失》核心论断（按朝代）', 2))
    out.append('')
    out.append('> 此书约在 p.3-p.90 区间（按TOC推断）。提取各朝代核心制度判断。')
    out.append('')

    dynasties = {
        '汉代': ['汉代', '汉制', '汉武帝', '汉光武', '汉室', '汉朝', '汉家'],
        '唐代': ['唐代', '唐制', '唐太宗', '唐玄宗', '唐室', '唐朝'],
        '宋代': ['宋代', '宋制', '宋太祖', '宋室', '宋朝'],
        '明代': ['明代', '明制', '明太祖', '明室', '明朝', '朱元璋'],
        '清代': ['清代', '清制', '清室', '清朝', '满清', '康熙', '雍正', '乾隆'],
    }

    # 限制在前120页（历代政治得失的范围）
    zhanmu_pages = [pg for pg in pages if pg['page'] <= 130]

    for dyn, kws in dynasties.items():
        out.append(md_header(f'{dyn}政治制度核心判断', 3))
        out.append('')
        results = search_all(zhanmu_pages, kws, ctx_chars=250, max_per_page=1, limit=20)
        for r in results:
            STATS['qian_dynasty_hits'] += 1
            out.append(f'- **p.{r["page"]} ·「{r["keyword"]}」**：')
            out.append(f'  > {r["context"]}')
            out.append('')
        if not results:
            out.append('*（前130页未匹配）*')
            out.append('')

    # 3. 定义性陈述：士人政府/科举/相权/制度vs法术
    out.append(md_header('三、关键概念定义性陈述', 2))
    out.append('')

    concept_phrases = {
        '士人政府': ['士人政府', '士人', '士大夫', '士大夫政治', '士人政治'],
        '科举/考试制度': ['科举', '考试制度', '选举制度', '察举', '九品中正', '进士', '科举制'],
        '相权/皇权': ['相权', '宰相', '丞相', '皇权', '君权', '相权与皇权', '相权限制', '君相'],
        '制度 vs 法术': ['制度', '法术', '制度与法术', '制度vs法术', '政治制度', '制度之背后', '制度的本原'],
        '内阁/六部': ['内阁', '六部', '尚书', '中书省', '门下省', '尚书省', '三省六部'],
        '地方制度': ['地方制度', '地方政府', '郡县', '州县', '行省', '封建', '郡县制'],
        '兵役/田制/税制': ['兵役', '府兵', '募兵', '租庸调', '两税法', '一条鞭法', '摊丁入亩', '井田'],
    }

    for concept, kws in concept_phrases.items():
        out.append(md_header(f'概念：「{concept}」', 3))
        out.append('')
        # 重点在前130页
        results = search_all(zhanmu_pages, kws, ctx_chars=280, max_per_page=1, limit=18)
        if not results:
            # 扩展到全书
            results = search_all(pages, kws, ctx_chars=280, max_per_page=1, limit=10)
        for r in results:
            STATS['qian_concept_hits'] += 1
            out.append(f'- **p.{r["page"]} ·「{r["keyword"]}」**：')
            out.append(f'  > {r["context"]}')
            out.append('')
        if not results:
            out.append('*未匹配。*')
            out.append('')

    # 4. "专制论"批判
    out.append(md_header('四、对「中国专制论」的批判段落', 2))
    out.append('')
    out.append('> 钱穆反对将中国传统政治简单定性为"专制"，此节提取相关论辩。')
    out.append('')
    autocracy_kws = [
        '专制', '君主专制', '独裁', '暴君', '暴政',
        '不是专制', '非专制', '不可一概', '不可一概而论',
        '黑暗', '黑暗专制', '愚民',
        '皇室', '皇室与政府', '皇室政府',
        '传统政治', '传统政制', '传统制度',
    ]
    results = search_all(pages, autocracy_kws, ctx_chars=280, max_per_page=1, limit=50)
    for r in results:
        STATS['qian_autocracy_hits'] += 1
        out.append(f'- **p.{r["page"]} ·「{r["keyword"]}」**：')
        out.append(f'  > {r["context"]}')
        out.append('')

    return '\n'.join(out)


# ============================================================
# 李岚清《突围》处理
# ============================================================
def process_li_lanqing():
    out = []
    out.append('')
    out.append(md_header('第三部分：李岚清《突围——国门初开的岁月》（31.2万字）', 1))
    out.append('')
    out.append('> 来源：李岚清著，中央文献出版社，399页，48条TOC。回忆1979-1984年中国对外开放初期决策与执行。')
    out.append('')

    book = load_book('tuwei')
    pages = build_page_index(book)
    STATS['tuwei_total_pages'] = len(pages)

    # 1. 目录
    out.append(md_header('一、完整目录', 2))
    out.append('')
    out.append(toc_to_markdown(book['toc']))
    out.append('')
    STATS['tuwei_toc'] = len(book['toc'])

    # 2. 改革开放决策过程回忆
    out.append(md_header('二、改革开放决策过程回忆（300字+页码）', 2))
    out.append('')
    decision_kws = [
        '决策', '作出决定', '决定开放', '中央决定', '党中央决定',
        '十一届三中全会', '三中全会', '工作会议', '中央工作会议',
        '邓小平', '小平同志', '小平',
        '思想解放', '真理标准', '解放思想',
        '改革开放', '对外开放', '开放政策', '基本国策',
        '试办', '试办特区', '先行先试',
        '谷牧', '国务院', '国务院特区办',
    ]
    results = search_all(pages, decision_kws, ctx_chars=300, max_per_page=1, limit=50)
    for r in results:
        STATS['tuwei_decision_hits'] += 1
        out.append(f'- **p.{r["page"]} ·「{r["keyword"]}」**：')
        out.append(f'  > {r["context"]}')
        out.append('')

    # 3. 经济特区/外资/WTO数据
    out.append(md_header('三、经济特区/外资/外经贸具体数据', 2))
    out.append('')

    data_cats = {
        '经济特区': ['经济特区', '深圳', '珠海', '汕头', '厦门', '海南', '特区', '十四个开放城市', '沿海开放', '开发区', '保税区'],
        '外资/FDI': ['外资', '外商', '外商投资', '合资', '合资企业', '外资企业', '外资引进', '利用外资', '引进外资', '直接投资', 'FDI', '外资项目', '三资企业'],
        '外贸数据': ['进出口', '出口额', '进口额', '贸易额', '外贸', '对外贸易', '出口创汇', '创汇'],
        '外汇储备': ['外汇储备', '外汇', '外汇收入', '外汇支出', '结汇'],
        'WTO/关贸总协定': ['WTO', '世界贸易组织', '关贸总协定', 'GATT', '复关', '入世', '加入WTO'],
        '外债/贷款': ['外债', '外国政府贷款', '世界银行', '国际货币基金', 'IMF', '日元贷款', '优惠贷款'],
    }
    for cat, kws in data_cats.items():
        out.append(md_header(f'类别：「{cat}」', 3))
        out.append('')
        results = search_all(pages, kws, ctx_chars=240, max_per_page=1, limit=20)
        for r in results:
            STATS['tuwei_data_hits'] += 1
            nums = extract_numbers(r['context'])
            nums_str = '；'.join(nums[:8]) if nums else '（无数值）'
            out.append(f'- **p.{r["page"]} ·「{r["keyword"]}」** 提取数字：{nums_str}')
            out.append(f'  > {r["context"]}')
            out.append('')
        if not results:
            out.append('*未匹配。*')
            out.append('')

    # 4. 关键人物互动
    out.append(md_header('四、关键人物互动（邓小平/江泽民/朱镕基等）', 2))
    out.append('')
    figures = {
        '邓小平': ['邓小平', '小平同志', '小平'],
        '江泽民': ['江泽民', '江总书记', '泽民同志'],
        '朱镕基': ['朱镕基', '朱总理', '镕基同志', '朱鎔基'],
        '李先念': ['李先念', '先念同志'],
        '陈云': ['陈云', '陈云同志'],
        '胡耀邦': ['胡耀邦', '耀邦同志'],
        '赵紫阳': ['赵紫阳', '紫阳同志'],
        '谷牧': ['谷牧', '谷牧同志'],
        '其他领导人': ['华国锋', '胡启立', '姚依林', '田纪云', '薄一波', '万里'],
    }
    for fig, kws in figures.items():
        results = search_all(pages, kws, ctx_chars=250, max_per_page=1, limit=15)
        if not results:
            continue
        out.append(md_header(f'人物：「{fig}」', 3))
        out.append('')
        for r in results:
            STATS['tuwei_figure_hits'] += 1
            out.append(f'- **p.{r["page"]} ·「{r["keyword"]}」**：')
            out.append(f'  > {r["context"]}')
            out.append('')

    return '\n'.join(out)


# ============================================================
# 主函数
# ============================================================
def main():
    print('>>> 加载并处理5本著作...')

    parts = []

    # 头部
    header = []
    header.append('# 5本经典著作全文深度知识提取')
    header.append('')
    header.append('> **数据源**：`data/political-books-extracted/` 下5本著作全文JSON（合计约413万字）')
    header.append('>')
    header.append('> **著作清单**：')
    header.append('> 1. 陈云文选（第一卷）— 786,158字 / 454页 / 60条TOC')
    header.append('> 2. 陈云文选（第二卷）— 651,050字 / 381页 / 57条TOC')
    header.append('> 3. 陈云文选（第三卷）— 706,208字 / 435页 / 88条TOC')
    header.append('> 4. 钱穆国学作品集 — 1,678,823字 / 1460页 / 502条TOC（含《中国历代政治得失》等6+部）')
    header.append('> 5. 李岚清《突围——国门初开的岁月》— 312,327字 / 399页 / 48条TOC')
    header.append('>')
    header.append('> **生成时间**：' + str(__import__('datetime').datetime.now()))
    header.append('')
    parts.append('\n'.join(header))

    # 1. 陈云
    print('  [1/3] 处理陈云文选三卷...')
    parts.append(process_chen_yun())

    # 2. 钱穆
    print('  [2/3] 处理钱穆国学作品集...')
    parts.append(process_qian_mu())

    # 3. 李岚清
    print('  [3/3] 处理李岚清《突围》...')
    parts.append(process_li_lanqing())

    # 统计附录
    stats_md = []
    stats_md.append('')
    stats_md.append(md_header('附录：提取统计', 1))
    stats_md.append('')
    stats_md.append('| 类别 | 提取条数 |')
    stats_md.append('|------|---------|')
    for k in sorted(STATS.keys()):
        stats_md.append(f'| {k} | {STATS[k]} |')
    stats_md.append('')
    total = sum(v for k, v in STATS.items() if 'toc' not in k and 'pages' not in k)
    stats_md.append(f'**知识条目总计**：{total} 条')
    stats_md.append('')
    parts.append('\n'.join(stats_md))

    # 写入文件
    print(f'>>> 写入 {OUT_FILE} ...')
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))

    size_kb = OUT_FILE.stat().st_size / 1024
    print(f'>>> 完成。文件大小：{size_kb:.1f} KB')
    print()
    print('=== 提取统计 ===')
    for k in sorted(STATS.keys()):
        print(f'  {k}: {STATS[k]}')
    print(f'  知识条目总计: {total}')


if __name__ == '__main__':
    main()
