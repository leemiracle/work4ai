#!/usr/bin/env python3
"""
政治学概念-论点数据库构建脚本 v2
基于模式匹配而非硬编码行位置
"""

import re
import os
from collections import defaultdict, OrderedDict

ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(ANALYSIS_DIR, "political-knowledge-database.md")

definitions = []
propositions = []
data_records = []
cases = []

def clean_ws(text):
    """Remove all whitespace from text for compact representation."""
    return re.sub(r'\s+', '', text.strip())

def truncate(text, max_len=300):
    if len(text) <= max_len:
        return text
    return text[:max_len] + '…'

def source_ref(rec):
    parts = [rec['source_book']]
    if rec.get('volume'):
        parts.append(rec['volume'])
    if rec.get('page'):
        parts.append(rec['page'])
    return ' '.join(parts)


# ============================================================
# PARSER 1: zhou-xueguang.md
# ============================================================
def parse_zhou_xueguang(filepath):
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()
    
    current_type = None
    current_page = None
    
    for line in lines:
        # Detect main sections
        if '定义性陈述' in line and line.startswith('##'):
            current_type = 'definition'
            current_page = None
            continue
        elif '关键数据' in line and line.startswith('##'):
            current_type = 'data'
            current_page = None
            continue
        elif '核心理论命题' in line and line.startswith('##'):
            current_type = 'proposition'
            current_page = None
            continue
        elif '关键案例' in line and line.startswith('##'):
            current_type = 'case'
            current_page = None
            continue
        elif line.startswith('## ') and current_type:
            # New main section that isn't one we care about
            current_type = None
            current_page = None
            continue
        
        # Detect page markers
        page_m = re.match(r'###\s*📄\s*第\s*(\d+)\s*页', line)
        if page_m:
            current_page = page_m.group(1)
            continue
        
        # Parse bullet items
        if current_type and current_page:
            if line.startswith('- '):
                raw = line[2:].strip()
                c = clean_ws(raw)
                if len(c) < 5:
                    continue
                rec = {
                    'type': current_type,
                    'source_book': '中国国家治理的制度逻辑',
                    'source_author': '周雪光',
                    'page': f'p.{current_page}',
                    'volume': None,
                    'text': c,
                }
                if current_type == 'definition':
                    definitions.append(rec)
                elif current_type == 'data':
                    data_records.append(rec)
                elif current_type == 'proposition':
                    propositions.append(rec)
                elif current_type == 'case':
                    cases.append(rec)


# ============================================================
# PARSER 2: zhou-lian.md
# ============================================================
def parse_zhou_lian(filepath):
    with open(filepath, encoding='utf-8') as f:
        text = f.read()
    
    current_type = None
    
    # Parse table-based sections (definitions, data, cases)
    # Definitions: ## 2. 定义性陈述 → table rows
    # Data: ## 3. 关键数据 → table rows  
    # Cases: ## 5. 关键案例 → table rows
    
    for line in text.split('\n'):
        if '定义性陈述' in line and line.startswith('##'):
            current_type = 'definition'
            continue
        elif '关键数据' in line and line.startswith('## 3'):
            current_type = 'data'
            continue
        elif '核心理论命题' in line and line.startswith('##'):
            current_type = None  # propositions are handled separately
            continue
        elif '关键案例' in line and line.startswith('## 5'):
            current_type = 'case'
            continue
        elif line.startswith('## ') and '提取统计' not in line:
            if current_type in ('definition', 'data', 'case'):
                # Check if it's a new content section
                if not any(kw in line for kw in ['定义性陈述', '关键数据', '关键案例']):
                    current_type = None
    
    # Re-parse with proper approach: split by sections
    sections = re.split(r'^## ', text, flags=re.M)
    
    for section in sections:
        if section.startswith('2.') or '定义性陈述' in section[:30]:
            for m in re.finditer(r'\|\s*\d+\s*\|\s*(p\.\d+)\s*\|\s*(.+?)\s*\|', section):
                raw = m.group(2).strip()
                c = clean_ws(raw)
                if len(c) < 5:
                    continue
                definitions.append({
                    'type': 'definition',
                    'source_book': '转型中的地方政府',
                    'source_author': '周黎安',
                    'page': m.group(1).strip(),
                    'volume': None,
                    'text': c,
                })
        
        elif section.startswith('3.') or ('关键数据' in section[:30]):
            for m in re.finditer(r'\|\s*\d+\s*\|\s*(p\.\d+)\s*\|\s*(.+?)\s*\|', section):
                raw = m.group(2).strip()
                c = clean_ws(raw)
                if len(c) < 5:
                    continue
                data_records.append({
                    'type': 'data',
                    'source_book': '转型中的地方政府',
                    'source_author': '周黎安',
                    'page': m.group(1).strip(),
                    'volume': None,
                    'text': c,
                })
        
        elif section.startswith('4.') or '核心理论命题' in section[:30]:
            # Propositions: ### 命题 N (p.X) 触发词:`word` → > text
            for m in re.finditer(r'命题\s*\d+\s*\(p\.(\d+)\).*?\n+>\s*(.+?)(?=\n###|\n##|\Z)', section, re.S):
                page = m.group(1).strip()
                raw = m.group(2).strip()
                c = clean_ws(raw)
                if len(c) < 10:
                    continue
                propositions.append({
                    'type': 'proposition',
                    'source_book': '转型中的地方政府',
                    'source_author': '周黎安',
                    'page': f'p.{page}',
                    'volume': None,
                    'text': c,
                })
        
        elif section.startswith('5.') or '关键案例' in section[:30]:
            for m in re.finditer(r'\|\s*\d+\s*\|\s*(p\.\d+)\s*\|\s*(.+?)\s*\|', section):
                raw = m.group(2).strip()
                c = clean_ws(raw)
                if len(c) < 5:
                    continue
                cases.append({
                    'type': 'case',
                    'source_book': '转型中的地方政府',
                    'source_author': '周黎安',
                    'page': m.group(1).strip(),
                    'volume': None,
                    'text': c,
                })


# ============================================================
# PARSER 3: xi-jinping.md
# ============================================================
def parse_xi_jinping(filepath):
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()
    
    current_section = None
    current_category = None
    
    for line in lines:
        stripped = line.strip()
        
        # Detect main sections
        if '## 3. 关键数据' in line or '关键数据' in line and stripped.startswith('##'):
            current_section = 'data'
            current_category = None
            continue
        elif '核心论断' in line and stripped.startswith('##'):
            current_section = 'proposition'
            current_category = None
            continue
        elif stripped.startswith('## ') and current_section:
            if not any(kw in line for kw in ['关键数据', '核心论断']):
                current_section = None
                current_category = None
            continue
        
        if not current_section:
            continue
        
        # Detect category
        cat_m = re.match(r'###\s*(.+?)（(\d+)条）', stripped)
        if cat_m:
            current_category = cat_m.group(1).strip()
            continue
        
        # Parse items: - **第X卷 p.Y**: text
        item_m = re.match(r'-\s*\*\*(.+?)\s*p\.(\d+)\*\*[：:]\s*(.+)', stripped)
        if item_m and current_section:
            vol = item_m.group(1).strip()
            page = item_m.group(2).strip()
            raw = item_m.group(3).strip()
            c = clean_ws(raw)
            if len(c) < 5:
                continue
            rec = {
                'type': current_section,
                'source_book': '习近平谈治国理政',
                'source_author': '习近平',
                'page': f'p.{page}',
                'volume': vol,
                'text': c,
                'theme': current_category,
            }
            if current_section == 'data':
                data_records.append(rec)
            elif current_section == 'proposition':
                propositions.append(rec)


# ============================================================
# PARSER 4: others.md
# ============================================================
def parse_others(filepath):
    with open(filepath, encoding='utf-8') as f:
        text = f.read()
    
    # Split by major book sections
    book_sections = re.split(r'^## [一二三四五六]、', text, flags=re.M)
    
    book_info = {
        1: ("周飞舟", "以利为利"),
        2: ("黄奇帆", "分析与思考"),
        3: ("孙萍", "过渡劳动"),
        4: ("波普尔", "历史决定论的贫困"),
    }
    
    for idx, section in enumerate(book_sections):
        if idx == 0:
            continue  # preamble
        if idx not in book_info:
            continue
        
        author, book = book_info[idx]
        
        # Split by subsections (### A. / ### B. / etc.)
        sub_sections = re.split(r'^### ([A-Z])\.\s*', section, flags=re.M)
        
        for j in range(1, len(sub_sections), 2):
            letter = sub_sections[j]
            content = sub_sections[j+1] if j+1 < len(sub_sections) else ""
            
            # Determine subsection type from header
            header = content.split('\n')[0].strip() if content else ""
            
            if '定义' in header:
                # Parse: N. 【keyword】text
                for m in re.finditer(r'\d+\.\s*【(.+?)】(.+)', content):
                    keyword = m.group(1).strip()
                    raw = m.group(2).strip()
                    c = clean_ws(raw)
                    if len(c) < 5:
                        continue
                    definitions.append({
                        'type': 'definition',
                        'source_book': book,
                        'source_author': author,
                        'page': None,
                        'volume': None,
                        'text': c,
                        'definition_marker': keyword,
                    })
            
            elif '关键数据' in header or '数据' in header:
                # Parse: N. [tag] value → > text
                lines_list = content.split('\n')
                for li in range(len(lines_list)):
                    line = lines_list[li]
                    m = re.match(r'\d+\.\s*\[(.+?)\]\s*(.+)', line.strip())
                    if m:
                        tag = m.group(1).strip()
                        val = m.group(2).strip()
                        # Check next line for > quote
                        quote = ""
                        if li + 1 < len(lines_list) and lines_list[li+1].strip().startswith('>'):
                            quote = lines_list[li+1].strip().lstrip('>').strip()
                        c = clean_ws(quote if quote else val)
                        if len(c) < 5:
                            continue
                        data_records.append({
                            'type': 'data',
                            'source_book': book,
                            'source_author': author,
                            'page': None,
                            'volume': None,
                            'text': c,
                            'data_tag': tag,
                        })
            
            elif any(kw in header for kw in ['核心', '理论', '论断', '命题', '观点']):
                # Parse propositions
                for m in re.finditer(r'\d+\.\s*(.+?)(?=\n\d+\.|\n###|\n##|\Z)', content, re.S):
                    raw = m.group(1).strip()
                    c = clean_ws(raw)
                    if len(c) < 15:
                        continue
                    # Skip if it looks like a table header
                    if c.startswith('|') or c.startswith('-'):
                        continue
                    propositions.append({
                        'type': 'proposition',
                        'source_book': book,
                        'source_author': author,
                        'page': None,
                        'volume': None,
                        'text': c,
                    })
            
            elif any(kw in header for kw in ['案例', '故事']):
                for m in re.finditer(r'\d+\.\s*(.+?)(?=\n\d+\.|\n###|\n##|\Z)', content, re.S):
                    raw = m.group(1).strip()
                    c = clean_ws(raw)
                    if len(c) < 10:
                        continue
                    if c.startswith('|') or c.startswith('-'):
                        continue
                    cases.append({
                        'type': 'case',
                        'source_book': book,
                        'source_author': author,
                        'page': None,
                        'volume': None,
                        'text': c,
                    })


# ============================================================
# PARSER 5: classics.md
# ============================================================
def parse_classics(filepath):
    with open(filepath, encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')
    
    # Detect major book boundaries
    # "# 第一部分" = 陈云, "# 第二部分" = 钱穆, "# 第三部分" = 李岚清
    current_book = None
    current_author = None
    current_section = None
    current_concept = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Major book section markers (# 第X部分)
        if stripped.startswith('# 第一部分') or '陈云' in stripped and stripped.startswith('# '):
            current_book = "陈云文选"
            current_author = "陈云"
            current_section = None
            i += 1
            continue
        if stripped.startswith('# 第二部分') or ('钱穆' in stripped and stripped.startswith('# ')):
            current_book = "中国历代政治得失"
            current_author = "钱穆"
            current_section = None
            i += 1
            continue
        if stripped.startswith('# 第三部分') or ('李岚清' in stripped and stripped.startswith('# ')):
            current_book = "突围：国门初开的岁月"
            current_author = "李岚清"
            current_section = None
            i += 1
            continue
        
        # Section detection
        if stripped.startswith('## '):
            if '核心概念' in stripped and '出现处' in stripped:
                current_section = 'concept'
                current_concept = None
            elif '核心论断' in stripped:
                current_section = 'qianmu_prop'
            elif '定义性陈述' in stripped:
                current_section = 'qianmu_def'
            elif '经济工作具体数据' in stripped or ('经济工作' in stripped and '数据' in stripped):
                current_section = 'chenyun_data'
                current_concept = None
                current_book = "陈云文选"
                current_author = "陈云"
            elif '关于党建' in stripped:
                current_section = 'chenyun_party'
                current_book = "陈云文选"
                current_author = "陈云"
            elif '意见差异' in stripped or '陈云与毛泽东' in stripped:
                current_section = 'chenyun_interaction'
                current_book = "陈云文选"
                current_author = "陈云"
            elif '改革开放决策' in stripped:
                current_section = 'lilanqing_case'
                current_book = "突围：国门初开的岁月"
                current_author = "李岚清"
            elif '经济特区' in stripped and ('数据' in stripped or '外资' in stripped):
                current_section = 'lilanqing_data'
                current_book = "突围：国门初开的岁月"
                current_author = "李岚清"
            elif '关键人物互动' in stripped:
                current_section = 'lilanqing_interaction'
                current_book = "突围：国门初开的岁月"
                current_author = "李岚清"
            elif '中国专制论' in stripped:
                current_section = 'qianmu_critique'
            elif '完整目录' in stripped or 'TOC' in stripped:
                current_section = None  # skip TOC
            else:
                current_section = None
            i += 1
            continue
        
        # Sub-section (###)
        if stripped.startswith('### '):
            concept_m = re.match(r'###\s*概念[：:]\s*[「「](.+?)[」」]', stripped)
            cat_m = re.match(r'###\s*类别[：:]\s*[「「](.+?)[」」]', stripped)
            if concept_m:
                current_concept = concept_m.group(1).strip()
            elif cat_m:
                current_concept = cat_m.group(1).strip()
            i += 1
            continue
        
        # ---- Parse items based on section ----
        # Format A: - **p.X（第Y卷）· 命中「word」**: → next line > quote  (陈云 concept + party)
        # Format B: - **p.X ·「word」**: → next line > quote  (李岚清)
        # Format C: - text → next line > quote  (钱穆)
        
        if current_section and stripped.startswith('- '):
            quote = ""
            if i + 1 < len(lines) and lines[i+1].strip().startswith('>'):
                quote = lines[i+1].strip().lstrip('>').strip()
            
            # Format A: chen yun
            m_a = re.match(r'-\s*\*\*p\.(\d+)（第(.+?)卷）.*?[「「].*?[」」]\*\*[：:]?\s*$', stripped)
            # Format B: li lanqing  
            m_b = re.match(r'-\s*\*\*p\.(\d+)\s*·\s*[「「](.+?)[」」]\*\*[：:]?\s*$', stripped)
            # Format C: qian mu
            m_c = not m_a and not m_b
            
            if quote and len(clean_ws(quote)) > 10:
                c = clean_ws(quote)
                
                if current_section in ('concept', 'chenyun_party'):
                    page = f'p.{m_a.group(1)}' if m_a else 'p.?'
                    vol = m_a.group(2) if m_a else None
                    rec_type = 'definition' if current_section == 'concept' else 'proposition'
                    rec = {
                        'type': rec_type,
                        'source_book': '陈云文选',
                        'source_author': '陈云',
                        'page': page,
                        'volume': vol,
                        'text': c,
                    }
                    if current_concept:
                        rec['concept_tags'] = [current_concept]
                    if rec_type == 'definition':
                        definitions.append(rec)
                    else:
                        propositions.append(rec)
                    i += 2
                    continue
                
                elif current_section == 'chenyun_data':
                    page = f'p.{m_a.group(1)}' if m_a else 'p.?'
                    vol = m_a.group(2) if m_a else None
                    data_records.append({
                        'type': 'data',
                        'source_book': '陈云文选',
                        'source_author': '陈云',
                        'page': page,
                        'volume': vol,
                        'text': c,
                        'data_tag': current_concept,
                    })
                    i += 2
                    continue
                
                elif current_section == 'qianmu_prop':
                    propositions.append({
                        'type': 'proposition',
                        'source_book': '中国历代政治得失',
                        'source_author': '钱穆',
                        'page': None,
                        'volume': None,
                        'text': c,
                    })
                    i += 2
                    continue
                
                elif current_section == 'qianmu_def':
                    definitions.append({
                        'type': 'definition',
                        'source_book': '中国历代政治得失',
                        'source_author': '钱穆',
                        'page': None,
                        'volume': None,
                        'text': c,
                    })
                    i += 2
                    continue
                
                elif current_section == 'qianmu_critique':
                    propositions.append({
                        'type': 'proposition',
                        'source_book': '中国历代政治得失',
                        'source_author': '钱穆',
                        'page': None,
                        'volume': None,
                        'text': c,
                        'theme': '历史演变',
                    })
                    i += 2
                    continue
                
                elif current_section == 'lilanqing_case':
                    page = f'p.{m_b.group(1)}' if m_b else 'p.?'
                    tag = m_b.group(2) if m_b else None
                    cases.append({
                        'type': 'case',
                        'source_book': '突围：国门初开的岁月',
                        'source_author': '李岚清',
                        'page': page,
                        'volume': None,
                        'text': c,
                        'concept_tags': [tag] if tag else [],
                    })
                    i += 2
                    continue
                
                elif current_section == 'lilanqing_data':
                    page = f'p.{m_b.group(1)}' if m_b else 'p.?'
                    data_records.append({
                        'type': 'data',
                        'source_book': '突围：国门初开的岁月',
                        'source_author': '李岚清',
                        'page': page,
                        'volume': None,
                        'text': c,
                    })
                    i += 2
                    continue
                
                elif current_section == 'lilanqing_interaction':
                    page = f'p.{m_b.group(1)}' if m_b else 'p.?'
                    tag = m_b.group(2) if m_b else None
                    cases.append({
                        'type': 'case',
                        'source_book': '突围：国门初开的岁月',
                        'source_author': '李岚清',
                        'page': page,
                        'volume': None,
                        'text': c,
                        'concept_tags': [tag] if tag else [],
                    })
                    i += 2
                    continue
                
                elif current_section == 'chenyun_interaction':
                    page = f'p.{m_a.group(1)}' if m_a else 'p.?'
                    vol = m_a.group(2) if m_a else None
                    cases.append({
                        'type': 'case',
                        'source_book': '陈云文选',
                        'source_author': '陈云',
                        'page': page,
                        'volume': vol,
                        'text': c,
                    })
                    i += 2
                    continue
        
        i += 1


# ============================================================
# THEME CLASSIFICATION
# ============================================================
THEME_KEYWORDS = {
    '国家治理结构': ['治理', '官僚', '体制', '集权', '分权', '一统', '发包', '控制权', '锦标赛', '晋升', '考核', '行政', '干部', '人事', '组织', '决策', '权力'],
    '财政与经济': ['财政', '税收', 'GDP', '经济', '预算', '土地', '金融', '货币', '增长', '收入', '支出', '分税', '包干', '转移支付', '债务', '产业', '市场', '投资', '消费', '贸易'],
    '合法性与政治': ['合法性', '权威', '卡理斯玛', '教化', '意识形态', '绩效', '稳定', '维稳', '信仰', '共识', '党', '执政', '领导', '纪律', '反腐败'],
    '国家与社会': ['社会', '民众', '集体', '村庄', '选举', '运动', '维权', '上访', '公共', '公民', '群众', '社区', '平台', '劳动', '骑手'],
    '历史演变': ['历史', '帝国', '王朝', '明清', '古代', '改革', '开放', '革命', '计划经济', '传统', '变迁', '汉代', '唐代', '宋代', '封建'],
    '国际关系': ['外交', '国际', '世界', '全球', '美国', '苏联', '贸易战', '一带一路', '开放', '主权', '战争', '外国', '西方', '东亚'],
}

def classify_theme(text):
    scores = defaultdict(int)
    for theme, keywords in THEME_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[theme] += 1
    if scores:
        return max(scores, key=scores.get)
    return '其他'

CORE_CONCEPTS = [
    '合法性', '运动式治理', '运动型治理', '行政发包制', '晋升锦标赛', '土地财政',
    '绩效合法性', '一统体制', '有效治理', '官僚制', '国家与社会',
    '改革', '共谋', '逆向软预算约束', '控制权', '软预算约束',
    '卡理斯玛', '属地管理', '集权', '分权', '意识形态',
    '社会主义', '市场经济', '腐败', '权力', '权威',
    '政治锦标赛', '发包制', '锦标赛', '维稳',
]

def detect_concepts(text):
    found = []
    for concept in CORE_CONCEPTS:
        if concept in text:
            found.append(concept)
    return found


# ============================================================
# OUTPUT GENERATION
# ============================================================

def generate_output():
    # Enrich records
    for rec in propositions:
        if not rec.get('theme'):
            rec['theme'] = classify_theme(rec['text'])
        rec['concept_tags'] = detect_concepts(rec['text'])
    
    for rec in definitions:
        rec['concept_tags'] = detect_concepts(rec['text'])
    
    for rec in data_records:
        if not rec.get('theme'):
            rec['theme'] = classify_theme(rec['text'])
    
    for rec in cases:
        rec['concept_tags'] = detect_concepts(rec['text'])
        if not rec.get('theme'):
            rec['theme'] = classify_theme(rec['text'])
    
    # Build concept dictionary
    concept_defs = defaultdict(list)
    for rec in definitions:
        for tag in rec.get('concept_tags', []):
            concept_defs[tag].append(rec)
        # Also detect concept in first 50 chars
        for concept in CORE_CONCEPTS:
            if concept in rec['text'][:80]:
                concept_defs[concept].append(rec)
    
    # Also search propositions and cases for concepts
    for rec in propositions + cases:
        for tag in rec.get('concept_tags', []):
            concept_defs[tag].append(rec)
    
    lines = []
    
    lines.append("# 政治学概念-论点数据库")
    lines.append("")
    lines.append("> **整合自 10 本政治学/政治经济学著作的知识提取结果**")
    lines.append("> 涵盖周雪光、周黎安、习近平、周飞舟、黄奇帆、孙萍、波普尔、陈云、钱穆、李岚清等著作")
    lines.append("")
    total = len(definitions) + len(propositions) + len(data_records) + len(cases)
    lines.append(f"> **统计**：定义 {len(definitions)} 条 | 论点 {len(propositions)} 条 | 数据 {len(data_records)} 条 | 案例 {len(cases)} 条 | 合计 {total} 条")
    lines.append(f"> **生成日期**：2026-07-13")
    lines.append(f"> **生成方法**：Python 脚本解析 6 个知识提取 Markdown 文件，自动分类、去重、整合")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # ============================================================
    # PART 1: 统一概念词典
    # ============================================================
    lines.append("# 第一部分：统一概念词典")
    lines.append("")
    lines.append("> 按概念出现频次降序排列。每个概念收录不同书中的定义与引用。")
    lines.append("")
    
    # Deduplicate and sort
    sorted_concepts = sorted(concept_defs.items(), key=lambda x: (-len(x[1]), x[0]))
    
    for concept, recs in sorted_concepts:
        if len(recs) < 2:  # Only show concepts with 2+ mentions
            continue
        
        # Deduplicate
        seen = set()
        unique_recs = []
        for r in recs:
            key = (r.get('source_book'), r.get('page'), r['text'][:60])
            if key not in seen:
                seen.add(key)
                unique_recs.append(r)
        
        if len(unique_recs) < 2:
            continue
        
        lines.append(f"## {concept}")
        
        # Count by book
        by_book = defaultdict(int)
        for r in unique_recs:
            by_book[r.get('source_book', '?')] += 1
        
        book_summary = '、'.join(f"{book}({cnt})" for book, cnt in sorted(by_book.items(), key=lambda x: -x[1])[:5])
        lines.append(f"> 共 {len(unique_recs)} 处引用 | 主要来源：{book_summary}")
        lines.append("")
        
        # Group by (author, book)
        grouped = defaultdict(list)
        for r in unique_recs:
            grouped[(r.get('source_author', '?'), r.get('source_book', '?'))].append(r)
        
        for (author, book), book_recs in sorted(grouped.items(), key=lambda x: -len(x[1])):
            # Select best entries per book (longest ones are usually most informative)
            book_recs_sorted = sorted(book_recs, key=lambda r: -len(r['text']))
            for r in book_recs_sorted[:3]:
                ref = source_ref(r)
                lines.append(f"- **{author}《{book}》{r.get('page') or ''}**：{truncate(r['text'], 250)}")
        
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # ============================================================
    # PART 2: 论点数据库
    # ============================================================
    lines.append("# 第二部分：论点数据库")
    lines.append("")
    lines.append("> 按主题分类。每个论点标注出处+页码+原文摘录（≤300字）。")
    lines.append("")
    
    themed_props = defaultdict(list)
    for rec in propositions:
        themed_props[rec.get('theme', '其他')].append(rec)
    
    theme_order = ['国家治理结构', '财政与经济', '合法性与政治', '国家与社会', '历史演变', '国际关系', '其他']
    
    for theme in theme_order:
        recs = themed_props.get(theme, [])
        if not recs:
            continue
        
        # Sort by source
        recs.sort(key=lambda r: (r.get('source_book', ''), r.get('page', '') or ''))
        
        # Balance across sources
        source_counts = defaultdict(int)
        max_per_source = 40
        selected = []
        for r in recs:
            if source_counts[r.get('source_book', '?')] < max_per_source:
                selected.append(r)
                source_counts[r.get('source_book', '?')] += 1
        
        lines.append(f"## {theme}（{len(recs)} 条，展示 {len(selected)} 条）")
        lines.append("")
        
        current_book = None
        for r in selected:
            book = r.get('source_book', '?')
            author = r.get('source_author', '?')
            if book != current_book:
                current_book = book
                lines.append(f"### {author}《{book}》")
                lines.append("")
            
            ref = source_ref(r)
            tags = r.get('concept_tags', [])
            tag_str = f" `[{', '.join(tags[:3])}]`" if tags else ""
            lines.append(f"- **{ref}**{tag_str}")
            lines.append(f"  > {truncate(r['text'], 300)}")
            lines.append("")
        
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # ============================================================
    # PART 3: 数据库
    # ============================================================
    lines.append("# 第三部分：关键数据库")
    lines.append("")
    lines.append("> 按类型分类的关键数据。")
    lines.append("")
    
    data_types = {
        '经济数据（GDP/财政/贸易）': ['GDP', '经济', '增长', '财政', '税收', '收入', '支出', '万亿', '亿元', '债务', '金融', '贸易', '投资', '消费', '利润', '产业', '百分', '杠杆'],
        '人口与社会数据': ['人口', '贫困', '就业', '人均', '劳动力', '城镇', '农村', '居民', '脱贫', '可支配'],
        '制度与行政数据': ['行政', '区划', '公务员', '编制', '干部', '官员', '政府机关', '机构', '编制', '级别'],
        '历史经济数据（粮食/钢/财政）': ['195', '196', '197', '粮食', '钢', '统购', '公粮', '产量', '斤', '亿斤', '斤粮', '征购', '收购'],
    }
    
    def classify_data(text):
        for dtype, keywords in data_types.items():
            for kw in keywords:
                if kw in text:
                    return dtype
        return '其他数据'
    
    typed_data = defaultdict(list)
    for rec in data_records:
        dtype = classify_data(rec['text'])
        typed_data[dtype].append(rec)
    
    for dtype in list(data_types.keys()) + ['其他数据']:
        recs = typed_data.get(dtype, [])
        if not recs:
            continue
        
        recs.sort(key=lambda r: (r.get('source_book', ''), r.get('page', '') or ''))
        
        source_counts = defaultdict(int)
        max_per_source = 35
        selected = []
        for r in recs:
            if source_counts[r.get('source_book', '?')] < max_per_source:
                selected.append(r)
                source_counts[r.get('source_book', '?')] += 1
        
        lines.append(f"## {dtype}（{len(recs)} 条，展示 {len(selected)} 条）")
        lines.append("")
        
        current_book = None
        for r in selected:
            book = r.get('source_book', '?')
            author = r.get('source_author', '?')
            if book != current_book:
                current_book = book
                lines.append(f"### {author}《{book}》")
                lines.append("")
            
            ref = source_ref(r)
            lines.append(f"- **{ref}**：{truncate(r['text'], 200)}")
        
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # ============================================================
    # PART 4: 案例库
    # ============================================================
    lines.append("# 第四部分：案例库")
    lines.append("")
    lines.append("> 按类型分类的关键案例。")
    lines.append("")
    
    case_types = {
        '历史案例': ['大跃进', '文革', '革命', '公社', '统购', '计划经济', '古代', '帝国', '朝代', '历史', '传统', '封建', '汉代', '唐代', '清代', '明朝', '清朝'],
        '田野案例': ['浙江', '外卖', '骑手', '村庄', '县', '镇', '巴东', '田野', '基层', '环保', '污染', '访谈', '平台', '算法'],
        '比较案例': ['美国', '苏联', '日本', '韩国', '英国', '国际', '比较', '欧洲', '东亚', '西方', '世界'],
        '改革案例': ['改革', '开放', '特区', '深圳', '浦东', '分税', '包干', '土地', '市场', '私营', '外资', '引进'],
    }
    
    def classify_case(text):
        for ctype, keywords in case_types.items():
            for kw in keywords:
                if kw in text:
                    return ctype
        return '其他案例'
    
    typed_cases = defaultdict(list)
    for rec in cases:
        ctype = classify_case(rec['text'])
        typed_cases[ctype].append(rec)
    
    for ctype in list(case_types.keys()) + ['其他案例']:
        recs = typed_cases.get(ctype, [])
        if not recs:
            continue
        
        recs.sort(key=lambda r: (r.get('source_book', ''), r.get('page', '') or ''))
        
        source_counts = defaultdict(int)
        max_per_source = 30
        selected = []
        for r in recs:
            if source_counts[r.get('source_book', '?')] < max_per_source:
                selected.append(r)
                source_counts[r.get('source_book', '?')] += 1
        
        lines.append(f"## {ctype}（{len(recs)} 条，展示 {len(selected)} 条）")
        lines.append("")
        
        current_book = None
        for r in selected:
            book = r.get('source_book', '?')
            author = r.get('source_author', '?')
            if book != current_book:
                current_book = book
                lines.append(f"### {author}《{book}》")
                lines.append("")
            
            ref = source_ref(r)
            tags = r.get('concept_tags', [])
            tag_str = f" `[{', '.join(tags[:2])}]`" if tags else ""
            lines.append(f"- **{ref}**{tag_str}：{truncate(r['text'], 200)}")
        
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # ============================================================
    # PART 5: 跨书概念对照表
    # ============================================================
    lines.append("# 第五部分：跨书概念对照表（10个核心概念深度对照）")
    lines.append("")
    lines.append("> 以下10个核心概念在不同著作中的定义、使用方式与评价对比。")
    lines.append("")
    
    DEEP_CONCEPTS = [
        ('合法性', ['合法性', '权威', '支配', '韦伯', '法理', '传统型', '卡理斯玛']),
        ('运动式治理', ['运动', '动员', '纠偏', '常规与动员', '运动型', '运动式']),
        ('行政发包制', ['发包', '承包', '属地', '逐级发包', '发包制']),
        ('晋升锦标赛', ['锦标赛', '晋升', '官场', '竞争', '绩效', '政治锦标赛']),
        ('土地财政', ['土地', '财政', '以地生财', '土地金融', '土地收入']),
        ('绩效合法性', ['绩效', '经济增长', '稳定', '合法性', '经济表现']),
        ('一统体制vs有效治理', ['一统体制', '有效治理', '矛盾', '统辖', '一统决策']),
        ('官僚制', ['官僚', '科层', '韦伯', '理性', '规则', '程序']),
        ('国家与社会', ['国家与社会', '市民社会', '社会', '民众', '公共', '国家—社会']),
        ('改革', ['改革', '开放', '转型', '制度变迁', '改革开放']),
    ]
    
    for concept_name, search_terms in DEEP_CONCEPTS:
        lines.append(f"## 「{concept_name}」")
        lines.append("")
        
        # Collect ALL relevant records
        all_relevant = []
        for rec in definitions + propositions + data_records + cases:
            if any(term in rec['text'] for term in search_terms):
                all_relevant.append(rec)
        
        # Deduplicate
        seen = set()
        relevant = []
        for r in all_relevant:
            key = (r.get('source_book'), r.get('page'), r['text'][:80])
            if key not in seen:
                seen.add(key)
                relevant.append(r)
        
        if not relevant:
            lines.append("*（未找到充足跨书材料）*")
            lines.append("")
            continue
        
        # Group by book
        by_book = defaultdict(list)
        for r in relevant:
            by_book[(r.get('source_author', '?'), r.get('source_book', '?'))].append(r)
        
        # Summary table
        lines.append("### 出现分布")
        lines.append("")
        lines.append("| 著者 | 书名 | 相关条目 |")
        lines.append("|------|------|---------|")
        for (author, book), recs in sorted(by_book.items(), key=lambda x: -len(x[1])):
            lines.append(f"| {author} | {book} | {len(recs)} |")
        lines.append("")
        
        # Detailed entries per book
        lines.append("### 各书引用")
        lines.append("")
        
        for (author, book), recs in sorted(by_book.items(), key=lambda x: -len(x[1])):
            lines.append(f"#### {author}《{book}》（{len(recs)}条）")
            lines.append("")
            
            type_order = [('definition', '定义'), ('proposition', '论点'), ('data', '数据'), ('case', '案例')]
            for type_key, type_label in type_order:
                type_recs = [r for r in recs if r['type'] == type_key]
                if type_recs:
                    # Sort by length descending (most informative first)
                    type_recs.sort(key=lambda r: -len(r['text']))
                    lines.append(f"**{type_label}（{len(type_recs)}条）：**")
                    lines.append("")
                    for r in type_recs[:5]:
                        ref = source_ref(r)
                        lines.append(f"- {ref}：{truncate(r['text'], 250)}")
                    if len(type_recs) > 5:
                        lines.append(f"- *…另有 {len(type_recs)-5} 条*")
                    lines.append("")
        
        # Cross-book synthesis
        lines.append("### 跨书比较要点")
        lines.append("")
        
        book_set = set(r.get('source_book', '') for r in relevant)
        author_set = set(r.get('source_author', '') for r in relevant)
        
        notes = []
        
        if '中国国家治理的制度逻辑' in book_set and '转型中的地方政府' in book_set:
            notes.append('**周雪光 vs 周黎安**：周雪光从宏观制度逻辑与历史脉络分析（韦伯理论视角），揭示结构性张力；周黎安从微观激励与组织经济学切入，关注官员行为动机。两者互补：前者解释「为什么」，后者解释「怎么做」。')
        
        if '中国国家治理的制度逻辑' in book_set and '习近平谈治国理政' in book_set:
            notes.append("**周雪光 vs 习近平**：周雪光以学术视角揭示治理矛盾与运动式治理的制度根源；习近平从执政者视角呈现政策应对与治理现代化路径。学术分析揭示张力，执政论述呈现解决方案。")
        
        if '转型中的地方政府' in book_set and '以利为利' in book_set:
            notes.append("**周黎安 vs 周飞舟**：周黎安从官员晋升激励出发（政治锦标赛），周飞舟从财政体制切入（分税制/土地财政）。前者关注政治激励，后者关注财政约束，共同解释地方政府行为。")
        
        if '中国国家治理的制度逻辑' in book_set and '中国历代政治得失' in book_set:
            notes.append("**周雪光 vs 钱穆**：周雪光以现代组织学分析当代治理逻辑，钱穆从中国政治史传统提供历史纵深。当代现象可在历史中找到制度原型。")
        
        if '陈云文选' in book_set:
            notes.append("**陈云的历史维度**：陈云的实践论述提供了该概念在计划经济时代的制度原型与操作细节，是理解当代治理的历史锚点。")
        
        if '分析与思考' in book_set:
            notes.append("**黄奇帆的实务视角**：从经济政策操作者角度补充该概念的具体政策含义与改革路径。")
        
        if '过渡劳动' in book_set:
            notes.append("**孙萍的数字时代视角**：展示该概念在平台经济与数字劳动中的新形态与新张力。")
        
        if '突围' in book_set:
            notes.append("**李岚清的决策记录**：提供改革开放初期该概念在高层决策中的实际运用证据。")
        
        if '历史决定论的贫困' in book_set:
            notes.append("**波普尔的哲学视角**：从科学哲学角度批判历史决定论，为该政治学概念提供认识论参照。")
        
        if not notes:
            notes.append("该概念主要集中在特定著作中，跨书比较材料有限。")
        
        for note in notes[:5]:
            lines.append(f"- {note}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # ============================================================
    # APPENDIX
    # ============================================================
    lines.append("# 附录：统计概览")
    lines.append("")
    
    lines.append("## 各书贡献统计")
    lines.append("")
    lines.append("| 著者 | 书名 | 定义 | 论点 | 数据 | 案例 | 合计 |")
    lines.append("|------|------|------|------|------|------|------|")
    
    all_books = OrderedDict()
    for rec in definitions + propositions + data_records + cases:
        key = (rec.get('source_author', '?'), rec.get('source_book', '?'))
        if key not in all_books:
            all_books[key] = {'definition': 0, 'proposition': 0, 'data': 0, 'case': 0}
        all_books[key][rec['type']] += 1
    
    for (author, book), counts in sorted(all_books.items(), key=lambda x: -sum(x[1].values())):
        total = sum(counts.values())
        lines.append(f"| {author} | {book} | {counts['definition']} | {counts['proposition']} | {counts['data']} | {counts['case']} | {total} |")
    
    lines.append("")
    
    # Top concepts
    lines.append("## 核心概念频率（按出现频次排序）")
    lines.append("")
    lines.append("| 概念 | 条目总数 | 涉及书目数 |")
    lines.append("|------|---------|-----------|")
    
    for concept, recs in sorted_concepts[:25]:
        if len(recs) < 3:
            continue
        books = set(r.get('source_book', '') for r in recs)
        lines.append(f"| {concept} | {len(recs)} | {len(books)} |")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 本数据库由 Python 脚本 (`build_knowledge_database.py`) 自动解析6个知识提取文件生成。")
    lines.append("> 由于提取源文件中部分条目为OCR/文本截取，原文可能存在截断或格式问题。")
    lines.append(f"> 最后更新：2026-07-13")
    lines.append("")
    
    return '\n'.join(lines)


def main():
    print("=" * 60)
    print("政治学概念-论点数据库构建 v2")
    print("=" * 60)
    
    files = [
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-zhou-xueguang.md"),
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-zhou-lian.md"),
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-xi-jinping.md"),
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-others.md"),
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-classics.md"),
    ]
    
    print("\n[1/3] 解析文件...")
    
    b = len(definitions)
    parse_zhou_xueguang(files[0])
    print(f"  ✓ 周雪光：+{len(definitions)-b}定义 +{len([r for r in data_records if r['source_book']=='中国国家治理的制度逻辑'])}数据")
    
    b = len(definitions)
    bp = len(propositions)
    bd = len(data_records)
    bc = len(cases)
    parse_zhou_lian(files[1])
    print(f"  ✓ 周黎安：+{len(definitions)-b}定义 +{len(propositions)-bp}论点 +{len(data_records)-bd}数据 +{len(cases)-bc}案例")
    
    bp = len(propositions)
    bd = len(data_records)
    parse_xi_jinping(files[2])
    print(f"  ✓ 习近平：+{len(propositions)-bp}论点 +{len(data_records)-bd}数据")
    
    b = len(definitions)
    bd = len(data_records)
    bp = len(propositions)
    bc = len(cases)
    parse_others(files[3])
    print(f"  ✓ 周飞舟/黄奇帆/孙萍/波普尔：+{len(definitions)-b}定义 +{len(data_records)-bd}数据 +{len(propositions)-bp}论点 +{len(cases)-bc}案例")
    
    b = len(definitions)
    bd = len(data_records)
    bp = len(propositions)
    bc = len(cases)
    parse_classics(files[4])
    print(f"  ✓ 陈云/钱穆/李岚清：+{len(definitions)-b}定义 +{len(data_records)-bd}数据 +{len(propositions)-bp}论点 +{len(cases)-bc}案例")
    
    total = len(definitions)+len(propositions)+len(data_records)+len(cases)
    print(f"\n[2/3] 汇总：定义{len(definitions)} | 论点{len(propositions)} | 数据{len(data_records)} | 案例{len(cases)} | 合计{total}")
    
    # Show per-book breakdown
    book_stats = defaultdict(lambda: defaultdict(int))
    for rec in definitions + propositions + data_records + cases:
        book_stats[rec.get('source_book', '?')][rec['type']] += 1
    for book, counts in sorted(book_stats.items(), key=lambda x: -sum(x[1].values())):
        t = sum(counts.values())
        print(f"    {book}: {t} (定义{counts['definition']}+论点{counts['proposition']}+数据{counts['data']}+案例{counts['case']})")
    
    print(f"\n[3/3] 生成数据库...")
    output = generate_output()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output)
    
    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"\n✅ 输出: {OUTPUT_FILE}")
    print(f"   大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"   行数: {len(output.splitlines()):,}")


if __name__ == '__main__':
    main()
