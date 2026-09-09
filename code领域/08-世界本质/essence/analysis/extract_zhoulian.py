#!/usr/bin/env python3
"""
深度知识提取：周黎安《转型中的地方政府：官员激励与治理》
从 full_text JSON 提取 5 类结构化知识。
"""
import json
import re
import os
from collections import defaultdict

SRC = '/mnt/c/workspace/essence/data/political-books-extracted/e0abe75fbd8d.json'
OUT = '/mnt/c/workspace/essence/analysis/extracted-knowledge-zhou-lian.md'

# ---------- 加载 ----------
with open(SRC, encoding='utf-8') as f:
    data = json.load(f)

toc = data['toc']
pages = {p['page']: p['text'] for p in data['full_text']}
N = data['pages']
print(f'加载：{data["filename"]}  页={N}  TOC={len(toc)}  全文段={len(data["full_text"])}')

# ---------- 1. TOC 树 ----------
def infer_level(title):
    """源 TOC 全是 level=1，从标题编号推断层级：
       - '导 论' / 章节名（无数字前缀）= L1
       - 'X.Y ...' (如 1.1, 2.3) = L2
       - 'X.Y.Z ...' (如 1.1.1) = L3
    """
    t = title.strip()
    # 形如 '1.1' '2.3.1'
    if re.match(r'^\d+\.\d+\.\d+', t):
        return 3
    if re.match(r'^\d+\.\d+', t):
        return 2
    # 形如 '第X章' '附录' 也是 L1
    return 1

def toc_tree():
    lines = []
    for _, title, pg in toc:
        lvl = infer_level(title)
        indent = '  ' * (lvl - 1)
        lines.append(f'{indent}- {title}  → p.{pg}')
    return '\n'.join(lines)

# ---------- 工具：以句号切分保留页码 ----------
def iter_sentences():
    """逐页逐句产出 (page, sentence)"""
    for p in sorted(pages.keys()):
        text = pages[p]
        # 切分句子（。！？；换行作为分隔）
        parts = re.split(r'(?<=[。！？；\n])', text)
        for s in parts:
            s = s.strip()
            if len(s) >= 6:
                yield p, s

# 建立句子缓存
SENTS = list(iter_sentences())
print(f'句子总数：{len(SENTS)}')

# ---------- 2. 定义性陈述 ----------
DEF_PATTERNS = [
    # 强定义模式
    r'所谓[^，。\n]{1,40}[,，]?\s*(就是|是指|是指代|是指向)',
    r'[^，。\n：]{1,30}\s*是指[^，。\n]{5,120}',
    r'[^，。\n：]{1,30}\s*指的是?[^，。\n]{5,120}',
    r'所谓[^，。\n]{1,40}',
    r'被(称为|定义|视为|理解为)[^，。\n]{1,80}',
    r'(我们|本书|笔者)?(将|把)?[^，。\n]{0,20}(定义|理解为)[^，。\n]{5,100}',
    r'(本质|核心|关键|主要|基本)(特征|属性|内容|性质|含义)是[^，。\n]{5,100}',
    r'(行政发包制|晋升锦标赛|政治锦标赛|锦标赛|行政逐级发包|属地管理|行政包干|属地化行政发包)[^，。\n]{0,8}(是|指|就是|是指|意味着)[^，。\n]{5,150}',
    r'[^，。\n]{1,20}的(核心|本质|关键)(在于|是)[^，。\n]{5,100}',
    r'可以(定义|概括|理解)[为成][^，。\n]{5,100}',
    r'(简言之|简而言之|具体来说|换言之|也就是说|即)[^，。\n]{5,80}',  # 弱
]

def extract_definitions():
    found = []
    seen = set()
    for pat in DEF_PATTERNS:
        rx = re.compile(pat)
        for p, s in SENTS:
            m = rx.search(s)
            if m and (p, s) not in seen:
                # 过滤过短或纯导航文本
                if len(s) < 12 or '目录' in s[:4]:
                    continue
                # 必须包含中文实质
                if not re.search(r'[\u4e00-\u9fa5]{4,}', s):
                    continue
                found.append((p, s, m.group(0)))
                seen.add((p, s))
    # 去重并按页排序
    found.sort(key=lambda x: (x[0], x[2]))
    return found

# ---------- 3. 关键数据 ----------
DATA_PATTERNS = {
    '百分比':    r'\d+(?:\.\d+)?\s*[％%]',
    '金额':      r'\d+(?:[,，.]\d+)*\s*[亿万万千百十两]+元(?:人民币)?',
    '美元金额':  r'\d+(?:[,，.]\d+)*\s*[亿万千百]?\s*(?:美元|美金|US\$)',
    '年份':      r'(?:1[89]|20)\d{2}\s*年',
    '年份范围':  r'(?:1[89]|20)\d{2}[-—~](?:1[89]|20)\d{2}\s*年?',
    '样本量':    r'\d+\s*(?:个|多)?\s*(?:样本|观察值|样本量|观测值|数据点|案例|案例数|地级市|县级市|县|省份|省|地区|市|企业)',
    '回归系数':  r'[βγρραbkabc](?:值|系数)?\s*[=＝]\s*[-－]?\d+(?:\.\d+)?',
    '显著性':    r'(?:p|sig\.?)\s*[<＜]\s*0?\.\d+',
    't值':       r't\s*值?\s*[=＝]\s*[-－]?\d+(?:\.\d+)?',
    'F值':       r'F\s*(?:值|统计量)?\s*[=＝]\s*\d+(?:\.\d+)?',
    'R平方':     r'R[²2]\s*[=＝]\s*0?\.\d+',
    '排名':      r'(?:排|位列|名列|居)(?:第)?\d+\s*(?:位|名|大)',
    '增长率':    r'\d+(?:\.\d+)?\s*倍',
}

def extract_data():
    found = []
    seen = set()
    for p, s in SENTS:
        for name, pat in DATA_PATTERNS.items():
            for m in re.finditer(pat, s):
                key = (p, s, name)
                if key in seen:
                    continue
                seen.add(key)
                # 去掉过短的导航行
                if len(s) < 10 or re.match(r'^\s*第?\d+\s*页?\s*$', s):
                    continue
                found.append((p, name, m.group(0), s))
    found.sort(key=lambda x: (x[0], x[1]))
    return found

# ---------- 4. 核心理论命题 ----------
PROP_KEYWORDS = [
    '本书提出', '本书认为', '本书将', '本书的核心', '本书的论点',
    '我认为', '笔者提出', '笔者认为', '笔者发现', '我们提出', '我们认为',
    '核心论点', '核心观点', '核心命题', '核心机制', '关键机制', '关键命题',
    '基本观点', '基本判断', '基本命题', '主要论点', '主要观点',
    '理论命题', '理论假说', '理论模型',
    '本书主要', '本书尝试', '本书旨在',
    '需要强调', '重要的一点', '关键在于', '关键的一点',
    '一个重要', '最重要的', '最为重要',
    '提出的(理论|框架|模型|概念|视角|分析)',
    '区别于', '不同于', '与...的关键区别',
]

def extract_propositions():
    found = []
    seen_sent = set()
    # 句号扩展：找命题句后扩展到 300 字
    for p, s in SENTS:
        for kw in PROP_KEYWORDS:
            if kw in s:
                # 扩展：合并相邻 1-2 句
                idx = SENTS.index((p, s))
                ext = s
                total_len = len(s)
                j = idx + 1
                while total_len < 300 and j < len(SENTS) and SENTS[j][0] == p:
                    ext += SENTS[j][1]
                    total_len += len(SENTS[j][1])
                    j += 1
                    if j - idx > 4:
                        break
                ext = ext[:350]
                key = ext[:60]
                if key in seen_sent:
                    break
                seen_sent.add(key)
                found.append((p, kw, ext))
                break
    found.sort(key=lambda x: x[0])
    return found

# ---------- 5. 关键案例 ----------
# 地名：省、市、县、区、镇、村；事件：地名+动词
PLACE_SUFFIX = r'(?:省|市|县|区|镇|乡|村|旗|盟|地区|自治)'
# 常见具体地名（避免误判）
KNOWN_PLACES = r'(?:浙江|江苏|广东|山东|河南|四川|安徽|福建|湖南|湖北|江西|山西|陕西|河北|辽宁|吉林|黑龙江|云南|贵州|甘肃|青海|海南|台湾|内蒙古|广西|西藏|宁夏|新疆|北京|上海|天津|重庆|深圳|广州|苏州|温州|泉州|东莞|佛山|中山|珠海|汕头|厦门|宁波|杭州|南京|无锡|常州|南通|徐州|济南|青岛|潍坊|烟台|威海|日照|临沂|郑州|洛阳|武汉|长沙|成都|西安|太原|合肥|南昌|昆明|贵阳|兰州|西宁|海口|哈尔滨|长春|沈阳|大连|鞍山|抚顺|本溪|包头|银川|乌鲁木齐|拉萨|南宁|呼和浩特|香港|澳门|佛山|江门|湛江|茂名|肇庆|梅州|汕尾|河源|清远|潮州|揭阳|云浮|阳江|韶关|惠州|三水|南海|顺德|番禺|增城|从化|昆山|张家港|江阴|常熟|吴江|太仓|宜兴|义乌|慈溪|余姚|奉化|宁海|象山|桐乡|海宁|平湖|海盐|嘉善|富阳|临安|建德|桐庐|淳安|诸暨|嵊州|新昌|上虞|余杭|萧山|绍兴|台州|丽水|衢州|舟山|金华|永康|东阳|磐安|武义|浦江|兰溪)'

CASE_TRIGGERS = [
    r'{}'.format(KNOWN_PLACES) + r'{1,3}' + PLACE_SUFFIX,
    r'(?:案例|典型|典型例子|典型代表|例如|比如|譬如|实例|一个例子|以.{1,15}为例)',
    r'19[789]\d\s*年.{0,30}(?:改革|试点|事件|事故|案件|爆发|发生)',
    r'(?:安徽小岗村|家庭联产承包|大包干|苏南模式|温州模式|浙江现象|珠三角|长三角)',
    r'(?:于|在|到)\s*' + KNOWN_PLACES + PLACE_SUFFIX + r'[^，。\n]{5,80}',
]

def extract_cases():
    found = []
    seen = set()
    for p, s in SENTS:
        matched_kws = []
        for pat in CASE_TRIGGERS:
            if re.search(pat, s):
                matched_kws.append(pat[:30])
        if matched_kws and (p, s) not in seen:
            # 过滤过短
            if len(s) < 15:
                continue
            seen.add((p, s))
            # 摘要：取前 120 字
            summary = s[:200] + ('...' if len(s) > 200 else '')
            found.append((p, summary))
    found.sort(key=lambda x: x[0])
    return found

# ---------- 执行 ----------
print('正在提取 5 类知识...')
toc_md = toc_tree()
defs = extract_definitions()
print(f'  定义性陈述: {len(defs)}')
datas = extract_data()
print(f'  关键数据:   {len(datas)}')
props = extract_propositions()
print(f'  理论命题:   {len(props)}')
cases = extract_cases()
print(f'  关键案例:   {len(cases)}')

# ---------- 输出 markdown ----------
def md_escape(t):
    return t.replace('|', '\\|').replace('\n', ' ').strip()

out = []
out.append('# 周黎安《转型中的地方政府：官员激励与治理》— 深度知识提取\n')
out.append(f'> 源文件：`{data["filename"]}`  \n> 总页数：{N}  全文字符数：{data["total_chars"]:,}  TOC 条目：{len(toc)}\n')
out.append(f'> 提取方式：Python 正则自动扫描 full_text（{len(SENTS)} 句）  \n> 生成时间：2026-07-13\n')
out.append('\n---\n')

# 1. TOC
out.append('\n## 1. 完整目录树（来自 TOC）\n')
out.append(f'共 {len(toc)} 条。\n\n')
out.append('```\n')
for _, title, pg in toc:
    lvl = infer_level(title)
    indent = '  ' * (lvl - 1)
    out.append(f'{indent}{title}  ... p.{pg}\n')
out.append('```\n')

# 2. 定义性陈述
out.append('\n---\n\n## 2. 定义性陈述\n')
out.append(f'共提取 **{len(defs)}** 条。\n\n')
out.append('| # | 页码 | 原文 |')
out.append('\n|---|------|------|\n')
for i, (p, s, matched) in enumerate(defs, 1):
    out.append(f'| {i} | p.{p} | {md_escape(s)} |\n')

# 3. 关键数据
out.append('\n---\n\n## 3. 关键数据\n')
out.append(f'共提取 **{len(datas)}** 条。\n\n')
# 按类型分组
by_type = defaultdict(list)
for p, name, m, s in datas:
    by_type[name].append((p, m, s))

for name in ['百分比', '金额', '美元金额', '样本量', '回归系数', 'R平方', 't值', 'F值', '显著性', '年份范围', '年份', '增长率', '排名']:
    items = by_type.get(name, [])
    if not items:
        continue
    out.append(f'\n### 3.{list(by_type.keys()).index(name)+1 if name in by_type else 0} {name}（{len(items)} 条）\n\n')
    out.append('| # | 页码 | 数值 | 原文上下文 |')
    out.append('\n|---|------|------|-----------|\n')
    for i, (p, m, s) in enumerate(items, 1):
        out.append(f'| {i} | p.{p} | `{m}` | {md_escape(s)} |\n')

# 4. 理论命题
out.append('\n---\n\n## 4. 核心理论命题\n')
out.append(f'共提取 **{len(props)}** 条（每条扩展至约 300 字）。\n\n')
for i, (p, kw, ext) in enumerate(props, 1):
    out.append(f'\n### 命题 {i}  (p.{p})  触发词：`{kw}`\n\n')
    out.append(f'> {md_escape(ext)}\n')

# 5. 关键案例
out.append('\n---\n\n## 5. 关键案例\n')
out.append(f'共提取 **{len(cases)}** 条。\n\n')
out.append('| # | 页码 | 摘要 |')
out.append('\n|---|------|------|\n')
for i, (p, summary) in enumerate(cases, 1):
    out.append(f'| {i} | p.{p} | {md_escape(summary)} |\n')

out.append('\n---\n\n## 提取统计\n')
out.append('| 类别 | 条数 |\n|------|------|')
out.append(f'\n| 1. 目录树 | {len(toc)} |')
out.append(f'\n| 2. 定义性陈述 | {len(defs)} |')
out.append(f'\n| 3. 关键数据 | {len(datas)} |')
out.append(f'\n| 4. 核心理论命题 | {len(props)} |')
out.append(f'\n| 5. 关键案例 | {len(cases)} |')
out.append(f'\n| **合计** | **{len(toc)+len(defs)+len(datas)+len(props)+len(cases)}** |\n')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(''.join(out))

size = os.path.getsize(OUT)
print(f'\n✓ 已写入：{OUT}')
print(f'  文件大小：{size:,} bytes ({size/1024:.1f} KB)')
print(f'\n=== 提取统计 ===')
print(f'  1. 目录树:       {len(toc)}')
print(f'  2. 定义性陈述:   {len(defs)}')
print(f'  3. 关键数据:     {len(datas)}')
print(f'  4. 核心理论命题: {len(props)}')
print(f'  5. 关键案例:     {len(cases)}')
print(f'  合计:            {len(toc)+len(defs)+len(datas)+len(props)+len(cases)}')
