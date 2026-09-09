#!/usr/bin/env python3
"""
构建可搜索的JSON知识索引 —— 从6个提取文件中解析结构化数据。

解析策略：
- 定义：匹配 "X是指..." "所谓X..." "【即】" "【所谓】" 等
- 命题：匹配带有页码标注的论断段落
- 数据：匹配包含数字+单位的段落
- 案例：匹配含地名/人名的段落
"""

import json
import re
import os
from collections import defaultdict
from datetime import date

ANALYSIS_DIR = "/mnt/c/workspace/essence/analysis"
OUTPUT_PATH = "/mnt/c/workspace/essence/data/political-books-extracted/knowledge_index.json"

# ============================================================
# 书籍元数据映射
# ============================================================
BOOK_MAP = {
    "zhou-xueguang": {"book": "中国国家治理的制度逻辑", "author": "周雪光"},
    "zhou-lian": {"book": "转型中的地方政府", "author": "周黎安"},
    "xi-jinping": {"book": "习近平谈治国理政", "author": "习近平"},
    "others-zhou-feizhou": {"book": "以利为利", "author": "周飞舟"},
    "others-huang-qifan": {"book": "分析与思考", "author": "黄奇帆"},
    "others-sun-ping": {"book": "过渡劳动", "author": "孙萍"},
    "others-popper": {"book": "历史决定论的贫困", "author": "波普尔"},
    "classics-chen-yun": {"book": "陈云文选", "author": "陈云"},
    "classics-qian-mu": {"book": "钱穆国学作品集", "author": "钱穆"},
}

# 概念关键词列表（用于从定义文本中提取概念名）
DEFINITION_PATTERNS = [
    (r'(?:所谓|所谓的)[""\u201c\u2018]?(.+?)[""\u201d\u2019]?(?:是指|指的是|，就是|，即)', '所谓X是指'),
    (r'(.+?)是指(.+)', 'X是指'),
    (r'(.+?)，(?:即|也就是|就是说)(.+)', 'X，即'),
    (r'(.+?)，(?:是指|指的是)(.+)', 'X，是指'),
]

# 跨书概念索引
CROSS_BOOK_CONCEPTS = [
    "权力", "开放", "维稳", "制度", "权威", "改革", "意识形态",
    "社会主义", "资本主义", "主权", "市场经济", "腐败", "党国",
    "数字治理", "全球化", "绩效合法性", "附近", "法治", "人治",
    "有效治理", "共谋", "民主化", "一统体制", "分税制", "民族主义",
    "集体行动", "合法性", "晋升锦标赛", "国家与社会", "社会运动",
    "国家能力", "土地财政", "逆向软预算约束", "运动式治理",
    "行政发包", "官僚制", "数目字管理",
    # 更多核心概念
    "行政发包制", "政治锦标赛", "控制权理论", "共谋现象",
    "运动型治理", "逆向软预算约束", "一统体制与有效治理",
    "卡理斯玛权威", "君主官僚制", "委托方-管理方-代理方",
    "鸟笼经济", "综合平衡", "摸着石头过河", "实事求是",
    "过渡劳动", "平台经济", "放水养鱼", "软预算约束",
]


def clean_text(text):
    """清理文本：去除多余空白、OCR残渣等"""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def truncate(text, max_len=500):
    """截断文本到指定长度"""
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


# ============================================================
# 解析器1: 周雪光《中国国家治理的制度逻辑》
# ============================================================
def parse_zhou_xueguang(filepath):
    """解析周雪光文件，格式：### 📄 第 XX 页 后跟 - text"""
    book = "中国国家治理的制度逻辑"
    author = "周雪光"
    concepts = []  # 定义性陈述
    propositions = []  # 核心理论命题
    data_points = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 找到各section的起始位置
    current_section = None
    current_page = None

    # 定义性陈述 section: "## 二、定义性陈述"
    # 关键数据 section: "## 三、关键数据"
    # 核心理论命题 section: "## 四、核心理论命题"

    section_map = {
        "二、定义性陈述": "definitions",
        "三、关键数据": "data",
        "四、核心理论命题": "propositions",
    }

    i = 0
    current_section = None
    current_page = None

    while i < len(lines):
        line = lines[i]

        # 检测section切换
        for key, val in section_map.items():
            if key in line and line.startswith('## '):
                current_section = val
                break

        # 检测页码标题：### 📄 第 XX 页
        page_match = re.match(r'###\s*📄\s*第\s*(\d+)\s*页', line)
        if page_match:
            current_page = f"p{page_match.group(1)}"
            i += 1
            continue

        # 检测条目：以 "- " 开头的行
        if line.startswith('- ') and current_section and current_page:
            text = clean_text(line[2:])
            if len(text) < 5:
                i += 1
                continue

            if current_section == "definitions":
                concepts.append({
                    "book": book, "author": author,
                    "page": current_page, "text": truncate(text, 500),
                    "type": "definition"
                })
            elif current_section == "data":
                data_points.append({
                    "book": book, "page": current_page,
                    "text": truncate(text, 500), "type": "factual",
                    "source_section": "key_data"
                })
            elif current_section == "propositions":
                propositions.append({
                    "book": book, "author": author,
                    "page": current_page, "text": truncate(text, 600),
                    "theme": "国家治理制度逻辑"
                })

        i += 1

    return concepts, propositions, data_points


# ============================================================
# 解析器2: 周黎安《转型中的地方政府》
# ============================================================
def parse_zhou_lian(filepath):
    """解析周黎安文件"""
    book = "转型中的地方政府"
    author = "周黎安"
    concepts = []
    propositions = []
    data_points = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    i = 0

    # Section 2: 定义性陈述 - 表格格式 | # | 页码 | 原文 |
    # Section 3: 关键数据 - 多个子类别
    # Section 4: 核心理论命题 - ### 命题 N (p.XX) 触发词

    current_section = None

    while i < len(lines):
        line = lines[i]

        if "## 2. 定义性陈述" in line:
            current_section = "definitions"
        elif "## 3. 关键数据" in line:
            current_section = "data"
        elif "## 4. 核心理论命题" in line:
            current_section = "propositions"

        # 定义性陈述表格行：| N | p.XX | text |
        if current_section == "definitions":
            table_match = re.match(r'\|\s*\d+\s*\|\s*p\.?(\d+)\s*\|\s*(.+?)\s*\|?\s*$', line)
            if table_match:
                page = f"p{table_match.group(1)}"
                text = clean_text(table_match.group(2))
                if len(text) > 3:
                    concepts.append({
                        "book": book, "author": author,
                        "page": page, "text": truncate(text, 500),
                        "type": "definition"
                    })

        # 核心理论命题：### 命题 N (p.XX) 触发词：`trigger`
        if current_section == "propositions":
            prop_match = re.match(r'###\s*命题\s*\d+\s*\(p\.?(\d+)\)\s*触发词[：:]\s*`(.+?)`', line)
            if prop_match:
                page = f"p{prop_match.group(1)}"
                trigger = prop_match.group(2)
                # 下一个非空行且以 > 开头的是内容
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith('###')):
                    if lines[j].strip().startswith('### 命题'):
                        break
                    j += 1
                if j < len(lines) and lines[j].strip().startswith('>'):
                    text = clean_text(lines[j].strip().lstrip('>'))
                    propositions.append({
                        "book": book, "author": author,
                        "page": page, "text": truncate(text, 600),
                        "trigger": trigger,
                        "theme": "官员激励与治理"
                    })

        # 关键数据子section
        if current_section == "data":
            # 匹配各种数据格式
            # 格式1: | N | p.XX | text | (类似定义的表格)
            data_table_match = re.match(r'\|\s*\d+\s*\|\s*p\.?(\d+)\s*\|\s*(.+?)\s*\|?\s*$', line)
            if data_table_match and '页码' not in line and '原文' not in line:
                page = f"p{data_table_match.group(1)}"
                text = clean_text(data_table_match.group(2))
                if len(text) > 3:
                    data_points.append({
                        "book": book, "page": page,
                        "text": truncate(text, 300), "type": "quantitative"
                    })

        i += 1

    return concepts, propositions, data_points


# ============================================================
# 解析器3: 习近平谈治国理政三卷
# ============================================================
def parse_xi_jinping(filepath):
    """解析习近平谈治国理政"""
    book_base = "习近平谈治国理政"
    author = "习近平"
    concepts = []
    propositions = []
    data_points = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 格式：- **第X卷 p.YY**: text
    # 分别在 "## 3. 关键数据" 和 "## 4. 核心论断" section 下
    # 概念频率统计 section: ## 2. 核心概念频率统计

    current_section = None
    current_topic = None

    i = 0
    while i < len(lines):
        line = lines[i]

        if "## 3. 关键数据" in line:
            current_section = "data"
        elif "## 4. 核心论断" in line:
            current_section = "propositions"
        elif "## 5. 引用经典" in line:
            current_section = "quotes"
        elif line.startswith('### ') and current_section in ("data", "propositions"):
            current_topic = line.replace('###', '').strip()

        # 匹配 - **第X卷 p.YY**: text
        entry_match = re.match(r'-\s*\*\*(.+?)\s*p\.?(\d+)\*\*[：:]\s*(.+)', line)
        if entry_match:
            vol = entry_match.group(1)  # 第一卷/第二卷/第三卷
            page = f"p{entry_match.group(2)}"
            text = clean_text(entry_match.group(3))
            full_book = f"{book_base}·{vol}"

            if current_section == "data":
                data_points.append({
                    "book": full_book, "author": author,
                    "page": page, "text": truncate(text, 400),
                    "type": current_topic or "general",
                    "topic": current_topic
                })
            elif current_section == "propositions":
                propositions.append({
                    "book": full_book, "author": author,
                    "page": page, "text": truncate(text, 400),
                    "theme": current_topic or "综合"
                })

        i += 1

    return concepts, propositions, data_points


# ============================================================
# 解析器4: 政治学著作合集（others）
# ============================================================
def parse_others(filepath):
    """解析周飞舟、黄奇帆、孙萍、波普尔四本书"""
    concepts = []
    propositions = []
    data_points = []
    cases = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 书籍切换：## 一、周飞舟《以利为利》 / ## 二、黄奇帆... 等
    # Section切换：### B. 定义性陈述 / ### C. 关键数据 / ### D. 核心理论命题/论断 / ### E. 关键案例/故事

    book_map_local = {
        "周飞舟": {"book": "以利为利", "author": "周飞舟"},
        "黄奇帆": {"book": "分析与思考", "author": "黄奇帆"},
        "孙萍": {"book": "过渡劳动", "author": "孙萍"},
        "波普尔": {"book": "历史决定论的贫困", "author": "波普尔"},
    }

    current_book = None
    current_author = None
    current_book_name = None
    current_section = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # 检测书切换
        for key, val in book_map_local.items():
            if key in line and line.startswith('## '):
                current_book_name = val["book"]
                current_author = val["author"]
                break

        # 检测section切换
        if "### B. 定义性陈述" in line:
            current_section = "definitions"
        elif "### C. 关键数据" in line:
            current_section = "data"
        elif "### D. 核心理论命题" in line or "### D. 核心理论命题/论断" in line:
            current_section = "propositions"
        elif "### E. 关键案例" in line:
            current_section = "cases"
        elif line.startswith('## ') and '提取统计' not in line and current_book_name:
            current_section = None  # 新书开始，重置

        # 定义性陈述：N. 【标签】text
        if current_section == "definitions":
            def_match = re.match(r'\d+\.\s*【(.+?)】(.+)', line)
            if def_match:
                label = def_match.group(1)
                text = clean_text(def_match.group(2))
                if len(text) > 5 and current_book_name:
                    concepts.append({
                        "book": current_book_name, "author": current_author,
                        "page": "", "text": truncate(text, 500),
                        "type": "definition",
                        "def_marker": label  # 即/所谓/也就是/是指/被称为
                    })

        # 关键数据：N. [类型] 值 \n > 上下文
        if current_section == "data":
            data_match = re.match(r'\d+\.\s*\[(.+?)\]\s*(.+)', line)
            if data_match:
                dtype = data_match.group(1)
                value = clean_text(data_match.group(2))
                # 找下一行的上下文
                context = ""
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('>'):
                    context = clean_text(lines[i + 1].strip().lstrip('>'))
                if current_book_name:
                    data_points.append({
                        "book": current_book_name, "page": "",
                        "type": dtype, "value": value,
                        "context": truncate(context, 400)
                    })

        # 核心理论命题：N. > text
        if current_section == "propositions":
            prop_match = re.match(r'\d+\.\s*>(.+)', line)
            if prop_match:
                text = clean_text(prop_match.group(1))
                if len(text) > 5 and current_book_name:
                    propositions.append({
                        "book": current_book_name, "author": current_author,
                        "page": "", "text": truncate(text, 500),
                        "theme": "理论命题/论断"
                    })

        # 关键案例：N. [标签] \n > text
        if current_section == "cases":
            case_match = re.match(r'\d+\.\s*\[(.+?)\]', line)
            if case_match:
                tags = case_match.group(1)
                # 找下一行的内容
                summary = ""
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('>'):
                    summary = clean_text(lines[i + 1].strip().lstrip('>'))
                if current_book_name and summary:
                    cases.append({
                        "name": tags,
                        "book": current_book_name, "author": current_author,
                        "page": "",
                        "summary": truncate(summary, 500)
                    })

        i += 1

    return concepts, propositions, data_points, cases


# ============================================================
# 解析器5: 经典著作（陈云文选 + 钱穆国学）
# ============================================================
def parse_classics(filepath):
    """解析陈云文选和钱穆国学作品集"""
    concepts = []
    propositions = []
    data_points = []
    cases = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 第一部分：陈云文选
    # 第二部分：钱穆国学作品集
    current_part = None
    current_section = None
    current_concept = None
    current_category = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # 检测部分切换
        if "第一部分：陈云文选" in line:
            current_part = "chen-yun"
        elif "第二部分：钱穆国学作品集" in line:
            current_part = "qian-mu"

        if current_part == "chen-yun":
            book = "陈云文选"
            author = "陈云"

            # 概念出现处：### 概念：「X」
            concept_match = re.match(r'###\s*概念[：:]\s*[「「](.+?)[」」]', line)
            if concept_match:
                current_concept = concept_match.group(1)
                current_section = "concept"

            # 经济数据类别：### 类别：「X」
            cat_match = re.match(r'###\s*类别[：:]\s*[「「](.+?)[」」]', line)
            if cat_match:
                current_category = cat_match.group(1)
                current_section = "econ-data"

            # 党建论述
            if "## 四、关于党建" in line:
                current_section = "party-building"
            elif "## 五、陈云与毛泽东" in line:
                current_section = "interaction"

            # 条目格式变体：
            #   - **p.XX（卷）· 命中「Y」**：          (概念出现处)
            #   - **p.XX（卷）·「Y」**：                (党建论述)
            #   - **p.XX（卷）·「Y」** 提取数字：...     (经济数据)
            entry_match = re.match(r'-\s*\*\*p\.?(\d+)（(第.卷)）[·・]\s*(?:命中)?[「「](.+?)[」」]\*\*(.+)', line)
            if entry_match and current_section:
                page = f"p{entry_match.group(1)}"
                vol = entry_match.group(2)
                tag = entry_match.group(3)
                full_book = f"{book}·{vol}"

                # 找下一行的引用内容
                text = ""
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('>'):
                    text = clean_text(lines[i + 1].strip().lstrip('>'))

                if not text:
                    i += 1
                    continue

                if current_section == "concept":
                    concepts.append({
                        "book": full_book, "author": author,
                        "page": page, "text": truncate(text, 500),
                        "type": "concept_mention",
                        "concept": current_concept,
                        "hit_keyword": tag
                    })
                elif current_section == "econ-data":
                    # 提取数字
                    data_points.append({
                        "book": full_book, "author": author,
                        "page": page, "text": truncate(text, 400),
                        "type": current_category or "economic",
                        "category": current_category
                    })
                elif current_section == "party-building":
                    propositions.append({
                        "book": full_book, "author": author,
                        "page": page, "text": truncate(text, 500),
                        "theme": f"党建·{tag}"
                    })
                elif current_section == "interaction":
                    propositions.append({
                        "book": full_book, "author": author,
                        "page": page, "text": truncate(text, 500),
                        "theme": f"陈云与毛邓互动·{tag}"
                    })

        elif current_part == "qian-mu":
            book = "钱穆国学作品集"
            author = "钱穆"

            # 《中国历代政治得失》核心论断
            if "《中国历代政治得失》核心论断" in line:
                current_section = "qianmu-propositions"

            # 朝代小节：### 汉代政治制度核心判断
            dynasty_match = re.match(r'###\s*(.+?)政治制度核心判断', line)
            if dynasty_match:
                current_dynasty = dynasty_match.group(1)

            # 条目：- **p.XX ·「朝代/主题」**：
            if current_section == "qianmu-propositions":
                entry_match = re.match(r'-\s*\*\*p\.?(\d+)\s*[·・]\s*[「「](.+?)[」」]\*\*[：:]', line)
                if entry_match:
                    page = f"p{entry_match.group(1)}"
                    tag = entry_match.group(2)
                    text = ""
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith('>'):
                        text = clean_text(lines[i + 1].strip().lstrip('>'))
                    if text:
                        propositions.append({
                            "book": book, "author": author,
                            "page": page, "text": truncate(text, 500),
                            "theme": f"历代政治得失·{tag}"
                        })

        i += 1

    return concepts, propositions, data_points, cases


# ============================================================
# 解析器6: 跨书概念对照
# ============================================================
def parse_cross_book(filepath):
    """解析跨书主题对照文件，提取概念索引"""
    cross_concepts = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 格式：### 「概念」— 出现在 N 本书中
    # 然后：| 书名 | 出现次数 | 上下文摘录 |

    current_concept = None
    current_keyword = None
    current_book_count = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        concept_match = re.match(r'###\s*[「「](.+?)[」」]\s*[—-]\s*出现在\s*(\d+)\s*本书中', line)
        if concept_match:
            current_concept = concept_match.group(1)
            current_book_count = int(concept_match.group(2))

        # 关键词行：**关键词**: xxx, xxx
        if current_concept and line.startswith('**关键词**'):
            kw_match = re.match(r'\*\*关键词\*\*[：:]\s*(.+)', line)
            if kw_match:
                current_keyword = kw_match.group(1).strip()

        # 表格行：| 书名 | 出现次数 | 上下文摘录 |
        if current_concept and line.startswith('|') and '---' not in line and '书名' not in line:
            parts = line.split('|')
            if len(parts) >= 4:
                book_name = parts[1].strip()
                count_str = parts[2].strip()
                context = parts[3].strip() if len(parts) > 3 else ""

                # 清理书名（去掉.pdf等后缀）
                book_clean = re.sub(r'\s*\(.*?\)', '', book_name).strip()
                book_clean = book_clean.replace('.pdf', '').replace('.pd', '').strip()

                try:
                    count = int(count_str)
                except ValueError:
                    count = 0

                cross_concepts.append({
                    "concept": current_concept,
                    "keyword": current_keyword or current_concept,
                    "book": book_clean,
                    "count": count,
                    "context": truncate(context, 300),
                    "total_books": current_book_count
                })

        i += 1

    return cross_concepts


# ============================================================
# 概念聚合：将定义合并为可搜索的概念索引
# ============================================================
def build_concept_index(all_definitions, cross_concepts):
    """
    将所有定义性陈述按概念名聚合，同时整合跨书概念索引。
    使用已知概念词表进行智能匹配。
    """
    # 核心概念词表（从跨书分析中提取的高频政治学概念）
    KNOWN_CONCEPTS = [
        # 治理制度类
        "行政发包制", "行政发包", "政治锦标赛", "锦标赛体制", "控制权理论", "控制权",
        "共谋现象", "共谋行为", "共谋",
        "运动型治理", "运动型治理机制", "运动式治理", "逆向软预算约束",
        "一统体制", "有效治理", "一统体制与有效治理",
        "卡理斯玛权威", "君主官僚制", "委托方", "管理方", "代理方",
        "晋升锦标赛", "压力型体制", "数目字管理", "属地化管理", "属地化",
        "条块关系", "条条", "块块", "垂直管理",
        "党政双重权威", "政治教化", "礼仪化",
        # 财政经济类
        "分税制", "财政包干制", "土地财政", "软预算约束", "预算外资金",
        "转移支付", "两个比重", "统收统支", "总额分成", "固定比例分成",
        "吃饭财政", "三保", "放水养鱼", "鸟笼经济", "计划与市场", "市场调节", "综合平衡",
        "摸着石头过河", "计划经济", "市场经济", "供给侧改革", "去杠杆",
        "地票", "资本置换", "经济性分权", "供给侧结构性改革",
        # 政治权力类
        "合法性", "绩效合法性", "权威", "权力", "专制", "集权", "分权",
        "党国", "国家能力", "国家与社会", "维稳", "意识形态",
        "民主化", "法治", "人治", "腐败", "改革", "开放",
        # 社会类
        "集体行动", "社会运动", "过渡劳动", "平台经济", "不稳定劳动",
        "数字治理", "全球化", "附近", "悬浮",
        # 思想理论类
        "实事求是", "社会主义", "资本主义", "民族主义", "主权",
        "历史决定论", "乌托邦", "渐进工程", "整体主义", "批判理性主义",
        # 干部管理类
        "59岁现象", "35岁现象", "神仙下凡", "干部交流", "目标责任制",
        "责任状", "层层加码", "拼凑应对", "逆向软预算",
        # 陈云特有
        "鸟笼经济", "综合平衡", "唯实", "执政党的党风",
        "听取不同意见", "国情",
        # 钱穆特有
        "士人政府", "相权", "皇权", "察举", "科举", "府兵制",
        "两税制", "三公九卿", "十三曹",
        # 其他重要概念
        "剩余控制权", "剩余索取权", "不完全契约", "交易费用",
        "效率工资", "资产专用性", "机会主义",
        "财政联邦主义", "可信承诺", "激励兼容",
        "政商关系", "官商关系", "地方国家公司主义",
        "锦标赛体制", "政治商业周期", "土地批租",
        "乡财县管", "省直管县", "二八分成",
        "物资本位制", "汇兑本位制", "布雷顿森林体系",
        "脱嵌", "算法管理", "情感劳动",
    ]

    concept_map = defaultdict(lambda: {"definitions": [], "mentions": []})

    # Phase 1: 从跨书概念索引建立基础概念
    for cc in cross_concepts:
        concept_name = cc["concept"]
        concept_map[concept_name]["mentions"].append({
            "book": cc["book"], "page": "",
            "context": cc["context"],
            "count": cc["count"]
        })

    # Phase 2: 将定义性陈述匹配到已知概念
    for d in all_definitions:
        text = d.get("text", "")
        book = d.get("book", "")
        author = d.get("author", "")
        page = d.get("page", "")

        matched = False
        # 尝试匹配已知概念词
        for concept in KNOWN_CONCEPTS:
            if concept in text:
                concept_map[concept]["definitions"].append({
                    "book": book, "author": author,
                    "page": page, "text": d["text"]
                })
                matched = True
                break  # 每个定义只归入第一个匹配的概念

        if not matched:
            # 尝试用正则提取概念名
            concept_name = extract_concept_name(text, d.get("def_marker", ""))
            if concept_name and is_valid_concept_name(concept_name):
                concept_map[concept_name]["definitions"].append({
                    "book": book, "author": author,
                    "page": page, "text": d["text"]
                })
            # 未匹配的定义不创建独立概念条目，但保留在 all_definitions 中

    # 构建最终列表
    result = []
    for name, data in concept_map.items():
        if data["definitions"] or data["mentions"]:
            result.append({
                "concept": name,
                "definitions": data["definitions"][:10],
                "mentions": data["mentions"][:15],
                "def_count": len(data["definitions"]),
                "mention_count": len(data["mentions"])
            })

    # 按覆盖度排序
    result.sort(key=lambda x: (x["def_count"] + x["mention_count"]), reverse=True)
    return result


def is_valid_concept_name(name):
    """判断提取的概念名是否有效"""
    if not name or len(name) < 2 or len(name) > 12:
        return False
    # 排除包含标点的
    if any(c in name for c in '，。、；：！？""''「」【】（）()[]{}...—·- '):
        return False
    # 排除纯数字
    if name.isdigit():
        return False
    # 排除常见噪音词
    NOISE_WORDS = {
        "当然", "但是", "实际上", "事实上", "换言之", "简言之",
        "也就是", "所谓", "这里", "特别", "特征", "体制",
        "效应", "服务", "绩效", "监督", "类似", "反复",
        "交换", "情况", "第二", "第一", "第三", "法币",
        "净地", "二国营", "析框架", "包干", "包干制",
    }
    if name in NOISE_WORDS:
        return False
    return True


def extract_concept_name(text, marker=""):
    """从定义文本中尝试提取概念名"""
    # 基于标记词的模式
    patterns = [
        (r'所谓(?:的)?[""\u201c\u2018「]?([^""\u201d\u2019」，]{2,15})[""\u201d\u2019」]?(?:是指|指的是|，就是|，即|就是)', None),
        (r'(.{2,15})是指(.+)', None),
        (r'(.{2,15})，即(.+)', None),
        (r'(.{2,15})，也就是(.+)', None),
        (r'被称为[""\u201c\u2018「]?([^""\u201d\u2019」，]{2,15})', None),
        (r'概念[是为](.+?)(?:的|，)', None),
    ]

    for pattern, _ in patterns:
        m = re.search(pattern, text)
        if m:
            name = m.group(1).strip()
            # 过滤掉太短或太长的
            if 2 <= len(name) <= 20:
                return name

    return None


# ============================================================
# 数据点分类
# ============================================================
def classify_data_point(text):
    """根据文本内容推断数据类型"""
    if any(kw in text for kw in ['%', '百分', '%']):
        return "percentage"
    if any(kw in text for kw in ['万亿', '亿', '万', '元', '美元', '刀']):
        return "fiscal"
    if any(kw in text for kw in ['年', '年代']):
        return "temporal"
    if any(kw in text for kw in ['人', '名', '口']):
        return "population"
    if re.search(r'\d+', text):
        return "quantitative"
    return "general"


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 60)
    print("构建政治学书籍知识索引 JSON")
    print("=" * 60)

    all_definitions = []
    all_propositions = []
    all_data_points = []
    all_cases = []

    # 1. 周雪光
    print("\n[1/6] 解析周雪光《中国国家治理的制度逻辑》...")
    fp = os.path.join(ANALYSIS_DIR, "extracted-knowledge-zhou-xueguang.md")
    defs, props, data = parse_zhou_xueguang(fp)
    all_definitions.extend(defs)
    all_propositions.extend(props)
    all_data_points.extend(data)
    print(f"  定义: {len(defs)} | 命题: {len(props)} | 数据: {len(data)}")

    # 2. 周黎安
    print("\n[2/6] 解析周黎安《转型中的地方政府》...")
    fp = os.path.join(ANALYSIS_DIR, "extracted-knowledge-zhou-lian.md")
    defs, props, data = parse_zhou_lian(fp)
    all_definitions.extend(defs)
    all_propositions.extend(props)
    all_data_points.extend(data)
    print(f"  定义: {len(defs)} | 命题: {len(props)} | 数据: {len(data)}")

    # 3. 习近平
    print("\n[3/6] 解析《习近平谈治国理政》三卷...")
    fp = os.path.join(ANALYSIS_DIR, "extracted-knowledge-xi-jinping.md")
    defs, props, data = parse_xi_jinping(fp)
    all_definitions.extend(defs)
    all_propositions.extend(props)
    all_data_points.extend(data)
    print(f"  命题: {len(props)} | 数据: {len(data)}")

    # 4. 政治学合集
    print("\n[4/6] 解析政治学著作合集（周飞舟/黄奇帆/孙萍/波普尔）...")
    fp = os.path.join(ANALYSIS_DIR, "extracted-knowledge-others.md")
    defs, props, data, cases = parse_others(fp)
    all_definitions.extend(defs)
    all_propositions.extend(props)
    all_data_points.extend(data)
    all_cases.extend(cases)
    print(f"  定义: {len(defs)} | 命题: {len(props)} | 数据: {len(data)} | 案例: {len(cases)}")

    # 5. 经典著作
    print("\n[5/6] 解析经典著作（陈云文选/钱穆国学）...")
    fp = os.path.join(ANALYSIS_DIR, "extracted-knowledge-classics.md")
    defs, props, data, cases = parse_classics(fp)
    all_definitions.extend(defs)
    all_propositions.extend(props)
    all_data_points.extend(data)
    all_cases.extend(cases)
    print(f"  定义/概念: {len(defs)} | 命题: {len(props)} | 数据: {len(data)} | 案例: {len(cases)}")

    # 6. 跨书概念对照
    print("\n[6/6] 解析跨书概念对照...")
    fp = os.path.join(ANALYSIS_DIR, "political-books-cross-book-analysis.md")
    cross_concepts = parse_cross_book(fp)
    print(f"  跨书概念条目: {len(cross_concepts)}")

    # 为数据点添加分类
    for dp in all_data_points:
        if "type" not in dp or dp["type"] in ("general", "factual"):
            dp["type"] = classify_data_point(dp.get("text", ""))

    # 构建概念索引
    print("\n构建概念聚合索引...")
    concepts = build_concept_index(all_definitions, cross_concepts)

    # 计算总字符数
    total_chars = 0
    for fp in [
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-zhou-xueguang.md"),
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-zhou-lian.md"),
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-xi-jinping.md"),
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-others.md"),
        os.path.join(ANALYSIS_DIR, "extracted-knowledge-classics.md"),
        os.path.join(ANALYSIS_DIR, "political-books-cross-book-analysis.md"),
    ]:
        with open(fp, 'r', encoding='utf-8') as f:
            total_chars += len(f.read())

    # 构建最终JSON
    total_entries = len(concepts) + len(all_propositions) + len(all_data_points) + len(all_cases)

    knowledge_index = {
        "metadata": {
            "total_books": 15,
            "total_chars": total_chars,
            "total_entries": total_entries,
            "created": str(date.today()),
            "sources": [
                "周雪光《中国国家治理的制度逻辑》",
                "周黎安《转型中的地方政府》",
                "习近平谈治国理政（三卷）",
                "周飞舟《以利为利》",
                "黄奇帆《分析与思考》",
                "孙萍《过渡劳动》",
                "波普尔《历史决定论的贫困》",
                "陈云文选（三卷）",
                "钱穆国学作品集（7部）",
            ],
            "entry_counts": {
                "concepts": len(concepts),
                "propositions": len(all_propositions),
                "data_points": len(all_data_points),
                "cases": len(all_cases),
                "cross_book_mentions": len(cross_concepts),
            }
        },
        "concepts": concepts,
        "propositions": all_propositions,
        "data_points": all_data_points,
        "cases": all_cases,
        "cross_book_index": cross_concepts[:500],  # 限制数量
    }

    # 写入文件
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(knowledge_index, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(OUTPUT_PATH)

    print("\n" + "=" * 60)
    print("构建完成！")
    print("=" * 60)
    print(f"输出文件: {OUTPUT_PATH}")
    print(f"文件大小: {file_size / 1024:.1f} KB ({file_size / 1024 / 1024:.2f} MB)")
    print(f"\n各类条目数:")
    print(f"  概念 (concepts):       {len(concepts):>6}")
    print(f"  命题 (propositions):   {len(all_propositions):>6}")
    print(f"  数据 (data_points):    {len(all_data_points):>6}")
    print(f"  案例 (cases):          {len(all_cases):>6}")
    print(f"  跨书索引 (cross_book): {len(cross_concepts):>6}")
    print(f"  总条目数:              {total_entries:>6}")
    print(f"\n源文件总字符数: {total_chars:,}")


if __name__ == "__main__":
    main()
