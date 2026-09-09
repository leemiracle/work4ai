#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为6本EPUB/MOBI创建原文深度笔记
输出: /mnt/c/workspace/essence/analysis/political-books-epub-notes.md
"""
import json
import re
import os

DATA_DIR = '/mnt/c/workspace/essence/data/political-books-extracted'
OUT_FILE = '/mnt/c/workspace/essence/analysis/political-books-epub-notes.md'

FILES = {
    'wanli': 'epub_05314f688e0d76c44aa385c98f502f93.json',
    'mao': 'epub_e077fb766e516aebbf6ad28d9cf81a48.json',
    'deng': 'epub_0695ef24be80eecef2179ca7122c88a9.json',
    'zsi': 'epub_fc25bf25f43b22b0ef1ac62c8642850a.json',
    'sapiens': 'mobi_f124b57a8baef3d0e363c9ee9ebcb01a.json',
    'sociology': 'epub_677b2a39917dfc890ce34c57eb3b159f.json',
}

def load(key):
    with open(os.path.join(DATA_DIR, FILES[key]), encoding='utf-8') as f:
        return json.load(f)

def get_full_text(d):
    """拼接所有section的text"""
    return '\n\n'.join(s['text'] for s in d['full_text'])

def get_body_text(d):
    """拼接正文，排除目录页（含大量 001. 002. 编号条目的section）"""
    parts = []
    for s in d['full_text']:
        t = s['text']
        nums = len(re.findall(r'\n\s*\d{2,3}\.', t))
        # 目录页特征：编号条目密度高（每千字 > 5条）
        density = nums / max(len(t), 1) * 1000
        if density > 5:
            continue
        parts.append(t)
    return '\n\n'.join(parts)

def clean(s, maxlen=None):
    s = s.replace('\n', ' ').strip()
    s = re.sub(r'\s+', ' ', s)
    if maxlen:
        s = s[:maxlen]
    return s

def find_sentences(text, keyword, context=120, maxn=5, minlen=30):
    """在text中找到包含keyword的句子/片段"""
    results = []
    for m in re.finditer(re.escape(keyword), text):
        start = max(0, m.start() - context)
        end = min(len(text), m.end() + context)
        frag = clean(text[start:end])
        # 找句号边界，取较完整句子
        if len(frag) > minlen:
            results.append(frag)
        if len(results) >= maxn:
            break
    return results

def quote(s, src=''):
    s = clean(s)
    if src:
        return f'> "{s}"\n> — {src}\n'
    return f'> "{s}"\n'

# ============================================================
# E1. 万历十五年
# ============================================================
def build_wanli():
    d = load('wanli')
    full = get_full_text(d)
    secs = d['full_text']
    chapters = {s['text'].split('\n')[0].strip(): s for s in secs}

    out = []
    out.append('## E1. 万历十五年（黄仁宇）\n')
    out.append('### 基本信息\n')
    out.append(f"- 字数: {d['total_chars']:,}\n")
    out.append("- 作者: 黄仁宇（Ray Huang），华裔美籍历史学家\n")
    out.append("- 英文原名: *1587, A Year of No Significance: The Ming Dynasty in Decline*（耶鲁大学，1981）\n")
    out.append('- 核心论点: 1587年（万历十五年）看似平淡无事，实则是明代政治制度全面失败、帝国走向衰亡的转折点；根本症结在于道德立国的文官体制无法实现"数目字管理"。\n')

    out.append('\n### 目录结构\n')
    ch_titles = ['第一章　万历皇帝', '第二章　首辅申时行', '第三章　世间已无张居正',
                 '第四章　活着的祖宗', '第五章　海瑞——古怪的模范官僚',
                 '第六章　戚继光——孤独的将领', '第七章　李贽——自相冲突的哲学家']
    for t in ch_titles:
        for s in secs:
            if s['text'].split('\n')[0].strip().startswith(t[:6]):
                out.append(f"- {t}（{len(s['text']):,}字）\n")
                break

    # 核心论点原文
    out.append('\n### 核心论点（原文引用）\n')
    out.append(quote(
        secs[1]['text'][secs[1]['text'].find('万历十五年'):secs[1]['text'].find('万历十五年')+400],
        '自序'))
    # "无关紧要的一年" 标题解读
    qs = find_sentences(full, 'A Year of No Significance', 200, 1)
    if qs:
        out.append(quote(qs[0], '自序'))
    qs = find_sentences(full, '无关紧要', 180, 2)
    for q in qs:
        out.append(quote(q, '全书主题'))
    # 数目字管理
    qs = find_sentences(full, '数目字', 200, 3)
    for q in qs:
        out.append(quote(q, '数目字管理'))

    out.append('\n### 关键概念定义\n')
    out.append('- **数目字管理（mathematical management）**: ')
    qs = find_sentences(full, '数目字', 250, 2)
    if qs:
        out.append(quote(qs[0], '数目字管理'))
    out.append('- **大历史观（macro-history）**: ')
    qs = find_sentences(full, '大历史', 200, 2)
    for q in qs:
        out.append(quote(q, '大历史观'))

    # 六个关键人物
    out.append('\n### 六个关键人物分析（原文引用）\n')
    figures = [
        ('万历皇帝', '第一章', secs[5]),
        ('申时行', '第二章', secs[6]),
        ('张居正', '第三章', secs[7]),
        ('海瑞', '第五章', secs[9]),
        ('戚继光', '第六章', secs[10]),
        ('李贽', '第七章', secs[11]),
    ]
    for name, ch, sec in figures:
        out.append(f'#### {name}（{ch}）\n')
        # 章首摘要
        intro = sec['text'][sec['text'].find(name):sec['text'].find(name)+350] if name in sec['text'] else sec['text'][200:550]
        out.append(quote(intro, ch))
        # 找3条关键句
        qs = find_sentences(sec['text'], name, 200, 3)
        for q in qs:
            out.append(quote(q, ch))
        out.append('')

    # 数目字管理所有出现处
    out.append('### "数目字管理"出现处汇总\n')
    qs = find_sentences(full, '数目字', 200, 8)
    for i, q in enumerate(qs, 1):
        out.append(f'{i}. ' + quote(q, '数目字管理').strip() + '\n')

    # 关键数据
    out.append('\n### 关键数据（原文）\n')
    for kw in ['1587', '一万一千', '两万', '白银', '文官', '武官', '科举']:
        qs = find_sentences(full, kw, 150, 1)
        if qs:
            out.append(quote(qs[0], f'数据·{kw}'))

    # 与钱穆对照
    out.append('\n### 与钱穆《中国历代政治得失》的对照\n')
    out.append('| 维度 | 黄仁宇《万历十五年》 | 钱穆《中国历代政治得失》 |\n')
    out.append('|------|---------------------|------------------------|\n')
    out.append('| 分析单位 | 单一年份（1587）的横截面深描 | 朝代制度的纵向比较（汉唐宋明清） |\n')
    out.append('| 核心病症 | 缺乏数目字管理，道德代替技术 | 制度精神丧失，吏治败坏 |\n')
    out.append('| 皇帝角色 | 被制度囚禁的"牌位"，无力改革 | 制度赋予皇权过重，相权衰落 |\n')
    out.append('| 文官集团 | 以道德名义绑架皇权，垄断权力 | 士人政府理想，反对贵族与军人干政 |\n')
    out.append('| 变革路径 | 需自下而上的数目字管理（法理化） | 恢复制度本意，需"通人"领导 |\n')
    out.append('| 历史观 | 大历史（macro-history），长时段结构 | 文化-制度演进，道德担当 |\n')

    out.append('\n### 与essence项目的关联\n')
    out.append('- 学科映射：`01-natural-sciences/` 历史学 + `04-governance/` 政治制度\n')
    out.append('- thinker（黄仁宇）：大历史观代表，"数目字管理"作为治理现代化的判据\n')
    out.append('- insight：制度的失败往往不在"坏人"而在"系统结构"——与周雪光"一统体制与有效治理矛盾"互参\n')
    out.append('- 跨学科：数目字管理 ↔ 信息论（可计算性）、控制论（反馈精度）\n')

    return ''.join(out)


# ============================================================
# E2. 毛泽东文集
# ============================================================
def build_mao():
    d = load('mao')
    full = get_body_text(d)  # 排除目录页
    secs = d['full_text']

    out = []
    out.append('\n---\n\n## E2. 毛泽东文集（中共中央文献研究室编，共八卷）\n')
    out.append('### 基本信息\n')
    out.append(f"- 字数: {d['total_chars']:,}\n")
    out.append("- 编者: 中共中央文献研究室\n")
    out.append("- 体例: 八卷本文集（区别于《毛泽东选集》四卷），收录1921—1976年间文稿\n")
    out.append("- 体量: 845个独立章节/篇目\n")
    out.append('- 核心地位: 毛泽东思想的原典性文本库，涵盖革命战略、建党、军事、哲学、外交\n')

    out.append('\n### 卷册结构\n')
    # 找各卷标题
    vol_marks = []
    for s in secs:
        fl = s['text'].split('\n')[0].strip()
        if re.match(r'毛泽东文集\s*第[一二三四五六七八]卷', fl):
            vol_marks.append(fl)
    for v in vol_marks:
        out.append(f'- {v}\n')

    # 核心著作10篇
    out.append('\n### 最核心10篇著作（深度分析）\n')
    key_works = [
        ('中国社会各阶级的分析', '阶级分析的方法论起点'),
        ('湖南农民运动考察报告', '农民作为革命主体的发现'),
        ('关于纠正党内的错误思想', '古田会议，党建原则'),
        ('星星之火，可以燎原', '农村包围城市战略的雏形'),
        ('实践论', '认识论：实践→认识→实践'),
        ('矛盾论', '辩证法：主要矛盾与矛盾的主要方面'),
        ('论持久战', '抗日战争三阶段论'),
        ('新民主主义论', '中国革命两步走'),
        ('论十大关系', '1956年探索社会主义建设道路'),
        ('关于正确处理人民内部矛盾的问题', '1957年社会主义社会矛盾理论'),
    ]
    for title, theme in key_works:
        # 找到对应章节
        target = None
        for s in secs:
            fl = s['text'].split('\n')[0].strip()
            if title in fl and len(s['text']) > 500:
                target = s
                break
        out.append(f'#### 《{title}》——{theme}\n')
        if target:
            # 取正文开头一段（跳过标题行）
            lines = target['text'].split('\n')
            body_start = '\n'.join(lines[1:6])
            out.append(quote(body_start, f'《{title}》开篇'))
            # 找关键句
            qs = find_sentences(target['text'], title[:2], 200, 1)
        else:
            qs = find_sentences(full, title, 200, 2)
            for q in qs:
                out.append(quote(q, title))
        out.append('')

    # 关键概念定义
    out.append('\n### 关键概念定义（原文）\n')
    concepts = ['群众路线', '三大法宝', '实事求是', '继续革命', '人民民主专政', '统一战线', '武装斗争']
    for c in concepts:
        out.append(f'- **{c}**: ')
        qs = find_sentences(full, c, 220, 2)
        for q in qs:
            out.append('  ' + quote(q, c).rstrip() + '\n')

    # 与马克思/列宁的关系
    out.append('\n### 与马克思/列宁的关系（原文）\n')
    for kw in ['马克思', '列宁', '马克思主义', '马列主义']:
        qs = find_sentences(full, kw, 200, 1)
        if qs:
            out.append(quote(qs[0], kw))

    out.append('\n### 关键数据与论断（原文）\n')
    for kw in ['一万万', '人口', '根据地', '游击战', '团结', '多数']:
        qs = find_sentences(full, kw, 160, 1)
        if qs:
            out.append(quote(qs[0], kw))

    out.append('\n### 与essence项目的关联\n')
    out.append('- 学科映射：`04-governance/` 革命理论 + `07-methodology/` 辩证法（矛盾论/实践论）\n')
    out.append('- thinker（毛泽东）：实践认识论与主要矛盾分析法的范式\n')
    out.append('- insight："实事求是"是essence项目第一性原理思维的方法论先声\n')
    out.append('- 跨学科：矛盾论 ↔ 系统论（要素/关系的主次）；群众路线 ↔ 复杂适应系统（自下而上涌现）\n')

    return ''.join(out)


# ============================================================
# E3. 邓小平文选
# ============================================================
def build_deng():
    d = load('deng')
    full = get_body_text(d)  # 排除目录页
    secs = d['full_text']

    out = []
    out.append('\n---\n\n## E3. 邓小平文选（第一卷）\n')
    out.append('### 基本信息\n')
    out.append(f"- 字数: {d['total_chars']:,}\n")
    out.append("- 作者: 邓小平\n")
    out.append("- 核心地位: 改革开放总设计师的理论与实践记录\n")
    out.append('- 核心论点: 解放思想，实事求是；发展才是硬道理；摸着石头过河的渐进改革\n')

    out.append('\n### 目录结构（主要篇目）\n')
    # 从目录页提取篇目（取section0，含编号列表）
    toc = secs[0]['text'] if secs else ''
    toc_items = re.findall(r'(\d{2,3})\.\s*([^\n]{4,30})', toc)
    seen = set()
    count = 0
    for num, title in toc_items:
        title = title.strip()
        if title not in seen and len(title) >= 5:
            out.append(f'- {num}. {title}\n')
            seen.add(title)
            count += 1
        if count >= 20:
            break

    # 核心概念定义
    out.append('\n### 关键概念定义（原文）\n')
    concepts = ['改革开放', '一国两制', '四项基本原则', '社会主义市场经济', '小康社会', '发展是硬道理', '解放思想', '三个有利于']
    for c in concepts:
        out.append(f'- **{c}**: ')
        qs = find_sentences(full, c, 220, 2)
        if qs:
            for q in qs:
                out.append('  ' + quote(q, c).rstrip() + '\n')
        else:
            out.append('  （原文未检索到独立定义性陈述）\n')

    # 南巡讲话
    out.append('\n### 南巡讲话（原文段落）\n')
    # 直接定位南巡讲话篇目
    nanxun_idx = full.find('在武昌、深圳、珠海、上海等地的谈话要点')
    if nanxun_idx > 0:
        nanxun = full[nanxun_idx:nanxun_idx+2500]
        out.append(quote(nanxun[:600], '南巡讲话·开篇'))
        # 发展才是硬道理
        idx2 = nanxun.find('发展才是硬道理')
        if idx2 > 0:
            out.append(quote(nanxun[max(0,idx2-300):idx2+200], '南巡讲话·核心论断'))
        # 革命也是解放生产力
        idx3 = nanxun.find('改革也是解放生产力')
        if idx3 > 0:
            out.append(quote(nanxun[max(0,idx3-150):idx3+250], '南巡讲话·改革论'))
    else:
        qs = find_sentences(full, '武昌、深圳、珠海', 300, 2)
        for q in qs:
            out.append(quote(q, '南巡讲话'))
    # 科学技术是第一生产力
    qs = find_sentences(full, '科学技术是第一生产力', 250, 1)
    if qs:
        out.append(quote(qs[0], '南巡讲话·科技论'))

    # 与陈云路线差异
    out.append('\n### 与陈云的路线差异\n')
    out.append('| 维度 | 邓小平路线 | 陈云路线 |\n')
    out.append('|------|-----------|---------|\n')
    out.append('| 改革节奏 | 胆子要大、步子要快（"杀出一条血路"） | 稳步前进、摸着石头过河 |\n')
    out.append('| 经济调控 | 市场化导向，特区先行 | 鸟笼经济，计划为主、市场为辅 |\n')
    out.append('| 速度观 | "发展才是硬道理"，鼓励增长 | 反对经济过热，强调综合平衡 |\n')
    out.append('| 体制观 | 不争论姓社姓资，先试再说 | "摸"中保谨慎，警惕通胀 |\n')
    out.append('| 共识 | 坚持四项基本原则、稳定压倒一切 | 同左 |\n')

    qs = find_sentences(full, '摸着石头过河', 200, 1)
    if qs:
        out.append(quote(qs[0], '渐进改革'))
    qs = find_sentences(full, '稳定压倒一切', 200, 1)
    if qs:
        out.append(quote(qs[0], '稳定论'))

    # 关键数据
    out.append('\n### 关键数据与论断（原文）\n')
    for kw in ['翻两番', '三步走', '一千美元', '八百美元', '小康', '特区']:
        qs = find_sentences(full, kw, 200, 1)
        if qs:
            out.append(quote(qs[0], kw))

    # 补充：经典论断
    out.append('\n### 经典论断（原文）\n')
    for kw in ['不管白猫黑猫', '科学技术是第一生产力', '贫穷不是社会主义', '让一部分人', '杀出一条血路']:
        qs = find_sentences(full, kw, 220, 1)
        if qs:
            out.append(quote(qs[0], kw))

    out.append('\n### 与essence项目的关联\n')
    out.append('- 学科映射：`04-governance/` 改革开放 + `03-economics/` 转型经济\n')
    out.append('- thinker（邓小平）：实用主义政治家，"不管白猫黑猫"的方法论\n')
    out.append('- insight：渐进式改革 vs 休克疗法——essence"反脆弱"主题的中国实践\n')
    out.append('- 跨学科：摸着石头过河 ↔ 控制论（反馈迭代）、演化经济学（制度试错）\n')

    return ''.join(out)


# ============================================================
# E4. 置身事内
# ============================================================
def build_zsi():
    d = load('zsi')
    full = get_full_text(d)
    secs = d['full_text']

    out = []
    out.append('\n---\n\n## E4. 置身事内：中国政府与经济发展（兰小欢）\n')
    out.append('### 基本信息\n')
    out.append(f"- 字数: {d['total_chars']:,}\n")
    out.append("- 作者: 兰小欢，复旦大学经济学院教授\n")
    out.append('- 定位: 复旦经院「毕业课」，中国政府与经济发展入门首选\n')
    out.append('- 核心论点: 理解中国经济必须理解中国政府——政府不仅是监管者，更是深度参与经济活动的"置身事内"者\n')

    out.append('\n### 目录结构（推断章节）\n')
    # 找章节标记
    chap_markers = re.findall(r'(第[一二三四五六七八九十]+章[^\n]{2,30})', full)
    seen = set()
    for cm in chap_markers:
        if cm not in seen:
            out.append(f'- {cm}\n')
            seen.add(cm)
            if len(seen) >= 10:
                break
    if not seen:
        # 备选：找关键主题
        for kw in ['地方政府的权力', '财税与政府行为', '政府投融资', '工业化', '城市化', '债务', '国内国际双循环']:
            out.append(f'- 主题：{kw}\n')

    out.append('\n### 各章/主题核心论点（原文）\n')
    themes = [
        ('地方政府的权力与事务', '政府结构'),
        ('财税与政府行为', '财政'),
        ('政府投融资与债务', '投融资'),
        ('工业化中的政府角色', '产业政策'),
        ('城市化与不平衡', '城市化'),
        ('债务与风险', '债务风险'),
        ('国内国际失衡', '宏观失衡'),
        ('政府与经济发展', '总结'),
    ]
    for theme, tag in themes:
        qs = find_sentences(full, theme.split('的')[0] if '的' in theme else theme[:4], 250, 1)
        if qs:
            out.append(f'#### {theme}\n')
            out.append(quote(qs[0], tag))

    # 关键概念
    out.append('\n### 关键概念（原文）\n')
    concepts = ['土地财政', '分税制', '融资平台', '城投公司', '土地出让金', '转移支付', '营改增', '软预算约束']
    for c in concepts:
        qs = find_sentences(full, c, 220, 1)
        if qs:
            out.append(f'- **{c}**: ' + quote(qs[0], c).rstrip() + '\n')

    # 关键数据
    out.append('\n### 关键数据（原文）\n')
    for kw in ['分税制', '1994', '土地出让', '百分之', 'GDP', '万亿']:
        qs = find_sentences(full, kw, 180, 1)
        if qs:
            out.append(quote(qs[0], f'数据·{kw}'))

    # 入门首选理由
    out.append('\n### 作为"入门首选"的理由\n')
    out.append('1. **政府视角的经济分析**：将政府作为经济主体而非外部监管者，契合中国现实\n')
    out.append('2. **制度与机制并重**：既讲"是什么"（财税/土地/债务），又讲"为什么"（激励机制/央地关系）\n')
    out.append('3. **可读性强**：案例驱动，数据扎实，避免空泛理论\n')
    out.append('4. **衔接前沿**：每章结尾延伸阅读，连接周雪光、周飞舟、陆铭等学者\n')
    out.append('5. **问题导向**：从"政府如何做事"出发，解释增长、失衡与风险\n')

    out.append('\n### 与essence项目的关联\n')
    out.append('- 学科映射：`03-economics/` 政治经济学 + `04-governance/` 央地关系\n')
    out.append('- 与周雪光《制度逻辑》互补：周雪光讲"一统体制与有效治理矛盾"的组织学逻辑，兰小欢讲其经济后果\n')
    out.append('- insight："置身事内"= 政府不是市场的外部变量，而是内生参与者\n')
    out.append('- 跨学科：土地财政 ↔ 制度经济学（激励相容）；融资平台 ↔ 金融摩擦理论\n')

    return ''.join(out)


# ============================================================
# E5. 人类简史
# ============================================================
def build_sapiens():
    d = load('sapiens')
    full = get_full_text(d)
    secs = d['full_text']

    out = []
    out.append('\n---\n\n## E5. 人类简史：从动物到上帝（尤瓦尔·赫拉利）\n')
    out.append('### 基本信息\n')
    out.append(f"- 字数: {d['total_chars']:,}\n")
    out.append("- 作者: 尤瓦尔·赫拉利（Yuval Noah Harari），耶路撒冷希伯来大学历史学家\n")
    out.append("- 副标题: 一部从智人崛起到未来展望的宏大叙事\n")
    out.append('- 核心论点: 智人凭"虚构故事"（fiction）的能力实现了大规模合作，从而统治地球；三大革命（认知/农业/科学）重塑了人类命运\n')

    out.append('\n### 全书结构（四大部分）\n')
    out.append('- 第一部 认知革命（约7万年前）\n')
    out.append('- 第二部 农业革命（约1万年前）\n')
    out.append('- 第三部 人类的融合统一（金钱/帝国/宗教）\n')
    out.append('- 第四部 科学革命（约500年前）\n')

    # 三大革命
    out.append('\n### 三大革命的定义和论证（原文）\n')
    out.append('#### 认知革命\n')
    qs = find_sentences(full, '认知革命', 250, 3)
    for q in qs:
        out.append(quote(q, '认知革命'))
    qs = find_sentences(full, '七万年前', 250, 1)
    if qs:
        out.append(quote(qs[0], '认知革命·时间'))

    out.append('\n#### 农业革命\n')
    qs = find_sentences(full, '农业革命', 250, 3)
    for q in qs:
        out.append(quote(q, '农业革命'))
    qs = find_sentences(full, '一万年前', 200, 1)
    if qs:
        out.append(quote(qs[0], '农业革命·时间'))

    out.append('\n#### 科学革命\n')
    qs = find_sentences(full, '科学革命', 250, 3)
    for q in qs:
        out.append(quote(q, '科学革命'))

    # 虚构故事理论
    out.append('\n### "虚构故事"理论（核心命题）\n')
    qs = find_sentences(full, '虚构', 280, 4)
    for q in qs:
        out.append(quote(q, '虚构故事理论'))
    qs = find_sentences(full, '想象的秩序', 250, 2)
    for q in qs:
        out.append(quote(q, '想象的秩序'))
    qs = find_sentences(full, '大规模合作', 200, 2)
    for q in qs:
        out.append(quote(q, '大规模合作'))

    # 对国家的理解
    out.append('\n### 对"国家"的理解（原文）\n')
    qs = find_sentences(full, '国家', 250, 3)
    for q in qs:
        out.append(quote(q, '国家·虚构实体'))
    qs = find_sentences(full, '想象', 250, 2)
    for q in qs:
        out.append(quote(q, '想象的共同体'))

    # 关键数据
    out.append('\n### 关键数据与论断（原文）\n')
    for kw in ['智人', '尼安德特', '百分之', '一万', '七十亿']:
        qs = find_sentences(full, kw, 180, 1)
        if qs:
            out.append(quote(qs[0], kw))

    out.append('\n### 与essence项目的关联\n')
    out.append('- 学科映射：`02-humanities/` 大历史 + `05-cognition/` 认知科学（虚构能力）\n')
    out.append('- thinker（赫拉利）：大历史叙事代表，"虚构故事"作为人类独特的认知技术\n')
    out.append('- insight："虚构故事"理论可与安德森"想象的共同体"、塞尔"制度性事实"互参\n')
    out.append('- 跨学科：虚构能力 ↔ 语言哲学（言语行为）、演化人类学（邓巴数）\n')
    out.append('- 哲学追问：科学革命让人类获得"能力"却未必获得"幸福"——essence"目的论"反思\n')

    return ''.join(out)


# ============================================================
# E6. 中国社会学经典文库
# ============================================================
def build_sociology():
    d = load('sociology')
    full = get_body_text(d)  # 排除目录页
    secs = d['full_text']

    out = []
    out.append('\n---\n\n## E6. 中国社会学经典文库（费孝通等）\n')
    out.append('### 基本信息\n')
    out.append(f"- 字数: {d['total_chars']:,}\n")
    out.append("- 主编/代表作者: 费孝通（及中国社会学经典文库收录的多种著作）\n")
    out.append("- 体例: 多部中国社会学经典著作的合集\n")
    out.append('- 核心地位: 理解中国社会的"乡土底色"——差序格局、礼俗社会、单位制等本土概念的源头\n')

    # 子书目结构
    out.append('\n### 库内主要著作结构（推断）\n')
    # 找书名/大标题
    book_markers = set()
    for s in secs:
        fl = s['text'].split('\n')[0].strip()
        if 4 <= len(fl) <= 25 and ('乡土' in fl or '江村' in fl or '金翼' in fl or '生育' in fl
            or '中国' in fl or '社会' in fl or '单位' in fl or '村镇' in fl):
            book_markers.add(fl)
    for b in sorted(book_markers)[:15]:
        out.append(f'- {b}\n')

    # 费孝通 差序格局
    out.append('\n### 费孝通"差序格局"的定义（原文）\n')
    qs = find_sentences(full, '差序格局', 300, 5)
    for q in qs:
        out.append(quote(q, '差序格局'))
    qs = find_sentences(full, '差序', 280, 2)
    for q in qs:
        out.append(quote(q, '差序·补充'))
    # 乡土中国
    qs = find_sentences(full, '乡土社会', 250, 2)
    for q in qs:
        out.append(quote(q, '乡土社会'))
    qs = find_sentences(full, '礼俗', 220, 2)
    for q in qs:
        out.append(quote(q, '礼俗社会'))

    # 《金翼》核心案例
    out.append('\n### 《金翼》的核心案例（原文）\n')
    qs = find_sentences(full, '金翼', 300, 4)
    for q in qs:
        out.append(quote(q, '《金翼》'))
    qs = find_sentences(full, '黄村', 250, 1)
    if qs:
        out.append(quote(qs[0], '《金翼》·黄村'))

    # 单位制研究
    out.append('\n### 单位制研究（原文）\n')
    qs = find_sentences(full, '单位制', 300, 3)
    for q in qs:
        out.append(quote(q, '单位制'))
    qs = find_sentences(full, '单位', 250, 2)
    for q in qs:
        out.append(quote(q, '单位·补充'))

    # 其他经典概念
    out.append('\n### 其他经典概念（原文）\n')
    concepts = ['熟人社会', '机械团结', '有机团结', '血缘', '地缘', '面子', '关系']
    for c in concepts:
        qs = find_sentences(full, c, 220, 1)
        if qs:
            out.append(f'- **{c}**: ' + quote(qs[0], c).rstrip() + '\n')

    # 关键数据
    out.append('\n### 关键数据（原文）\n')
    for kw in ['百分之', '调查', '户', '亩', '元']:
        qs = find_sentences(full, kw, 160, 1)
        if qs:
            out.append(quote(qs[0], kw))

    out.append('\n### 与essence项目的关联\n')
    out.append('- 学科映射：`02-humanities/` 社会学 + `04-governance/` 基层治理\n')
    out.append('- thinker（费孝通）：差序格局——理解中国人际关系的本土范式\n')
    out.append('- insight：差序格局（同心圆）vs 团体格局（边界清晰）——essence"组织边界"主题的中西对照\n')
    out.append('- 跨学科：差序格局 ↔ 网络科学（嵌入性/强弱关系）；单位制 ↔ 组织生态学（制度同构）\n')
    out.append('- 与周雪光互参：费孝通提供"乡土底色"，周雪光提供"国家治理逻辑"，二者构成理解中国社会的双层结构\n')

    return ''.join(out)


# ============================================================
# 主程序
# ============================================================
def main():
    header = """# 政治类EPUB/MOBI书目原文深度笔记

> 基于6本电子书全文JSON提取的**原文引用**——不是概括，是原文
> 数据来源: `/mnt/c/workspace/essence/data/political-books-extracted/` 下 `epub_*` / `mobi_*` JSON
> 配套: [`political-books-original-text-notes.md`](./political-books-original-text-notes.md)（PDF笔记）
> 提取方法: Python正则从EPUB全文JSON中自动定位关键词与定义性陈述，附原文片段

---

| 编号 | 书名 | 作者 | 字数 |
|------|------|------|------|
| E1 | 万历十五年 | 黄仁宇 | 253,020 |
| E2 | 毛泽东文集 | 毛泽东（中共中央文献研究室编） | 1,855,322 |
| E3 | 邓小平文选 | 邓小平 | 1,232,320 |
| E4 | 置身事内 | 兰小欢 | 210,434 |
| E5 | 人类简史 | 尤瓦尔·赫拉利 | 303,789 |
| E6 | 中国社会学经典文库 | 费孝通 等 | 3,874,570 |

---

"""

    parts = [header]
    print('Building E1 万历十五年...')
    parts.append(build_wanli())
    print('Building E2 毛泽东文集...')
    parts.append(build_mao())
    print('Building E3 邓小平文选...')
    parts.append(build_deng())
    print('Building E4 置身事内...')
    parts.append(build_zsi())
    print('Building E5 人类简史...')
    parts.append(build_sapiens())
    print('Building E6 中国社会学经典文库...')
    parts.append(build_sociology())

    footer = """

---

## 跨书主题连接

### 治理逻辑的三个层次
| 层次 | 代表文本 | 核心命题 |
|------|---------|---------|
| 历史结构 | 万历十五年 | 道德立国 vs 数目字管理 |
| 革命与建国 | 毛泽东文集 | 实事求是、群众路线、主要矛盾 |
| 改革与发展 | 邓小平文选 / 置身事内 | 摸着石头过河、土地财政、央地激励 |
| 社会底色 | 中国社会学经典文库 | 差序格局、乡土社会、单位制 |
| 普世参照 | 人类简史 | 虚构故事与大规模合作 |

### essence项目的 thinker 网络
- **黄仁宇** — 大历史观、数目字管理（治理现代化的判据）
- **毛泽东** — 实践认识论、主要矛盾分析（方法论范式）
- **邓小平** — 实用主义、渐进改革（反脆弱的中国实践）
- **兰小欢** — 政府作为经济内生参与者（政治经济学入门）
- **赫拉利** — 虚构故事理论（认知-合作-权力的演化）
- **费孝通** — 差序格局、乡土中国（理解中国社会的本土范式）

### 方法论映射
- 第一性原理：毛泽东"实事求是" ↔ essence追问本质
- 系统思维：周雪光"一统体制与有效治理矛盾" ↔ 黄仁宇"制度全面失败"
- 跨学科：数目字管理（历史）↔ 可计算性（信息论）↔ 反馈精度（控制论）

> 生成时间: 自动提取 | 提取脚本: `generate_epub_notes.py`
"""
    parts.append(footer)

    content = ''.join(parts)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'\n✓ 已写入 {OUT_FILE}')
    print(f'  总字数: {len(content):,}')

    # 统计每书引用数
    for tag in ['E1.', 'E2.', 'E3.', 'E4.', 'E5.', 'E6.']:
        sec_start = content.find('## ' + tag)
        sec_end = content.find('\n---\n', sec_start + 10)
        if sec_end < 0:
            sec_end = len(content)
        sec = content[sec_start:sec_end]
        qcount = sec.count('> "')
        print(f'  {tag}: 约 {qcount} 条原文引用')

if __name__ == '__main__':
    main()
