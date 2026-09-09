#!/usr/bin/env python3
"""
政治学知识库 → Anki 闪卡导出脚本

从 knowledge_index.json 提取知识，生成 Anki 可直接导入的 TSV 文件。

卡片类型：
  1. 概念定义卡 (concepts.csv)  — 正面: 概念名 | 背面: 定义+书名+页码
  2. 数据记忆卡 (data.csv)       — 正面: 问题 | 背面: 数据+书名+页码
  3. 命题论证卡 (propositions.csv)— 正面: 命题 | 背面: 原文论证+书名+页码

用法:
  python3 export_anki.py              # 导出全部三类卡
  python3 export_anki.py --concepts   # 仅概念卡
  python3 export_anki.py --data       # 仅数据卡
  python3 export_anki.py --props      # 仅命题卡
  python3 export_anki.py --stats      # 查看统计

Anki 导入说明:
  1. 打开 Anki → 文件 → 导入
  2. 选择对应 .csv 文件
  3. 字段分隔符选 "Tab"
  4. 勾选 "允许在字段中使用 HTML"
  5. 选择目标牌组（如 "政治学::概念"）

CSV 格式（Tab 分隔）:
  正面<TAB>背面<TAB>标签
"""

import json
import re
import os
import sys
import argparse
import csv
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

# ── 路径 ──
SCRIPT_DIR = Path(__file__).parent
INDEX_PATH = SCRIPT_DIR / "knowledge_index.json"
OUTPUT_DIR = SCRIPT_DIR / "anki_cards"

# ── 颜色 ──
class C:
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    CYAN   = '\033[96m'
    BOLD   = '\033[1m'
    DIM    = '\033[2m'
    RESET  = '\033[0m'

def info(msg):  print(f"{C.CYAN}  ℹ{C.RESET}  {msg}")
def ok(msg):    print(f"{C.GREEN}  ✅{C.RESET} {msg}")
def warn(msg):  print(f"{C.YELLOW}  ⚠{C.RESET}  {msg}")
def header(msg): print(f"\n{C.BOLD}{C.CYAN}═══ {msg} ═══{C.RESET}")


# ═══════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════

def load_index():
    """加载知识库 JSON"""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def clean_text(text):
    """清理文本：去除多余空白、截断过长引用"""
    if not text:
        return ""
    # 去除首尾空白
    text = text.strip()
    # 合并连续空白
    text = re.sub(r'\s+', ' ', text)
    # 去除残留的页码标记 [5] 等（保留在原句中间的）
    # text = re.sub(r'\[\d+\]', '', text)
    return text


def format_back(text, book, author="", page=""):
    """格式化卡片背面：原文 + 来源（使用 <br> 换行，兼容 Anki HTML 模式）"""
    parts = [text.strip()]
    source_parts = []
    if author:
        source_parts.append(author)
    if book:
        source_parts.append(f"《{book}》")
    if page:
        source_parts.append(page)
    if source_parts:
        parts.append("— " + " · ".join(source_parts))
    return "<br>".join(parts)


def make_tag(book, author="", theme=""):
    """从书名/作者/主题生成标签"""
    tags = []
    # 作者标签
    if author:
        author_clean = re.sub(r'[^\u4e00-\u9fff\w]', '', author)
        if author_clean:
            tags.append(author_clean)
    # 书名标签（简化）
    if book:
        book_tag = re.sub(r'[^\u4e00-\u9fff\w]', '', book)[:10]
        if book_tag:
            tags.append(book_tag)
    # 主题标签
    if theme:
        theme_tag = re.sub(r'[^\u4e00-\u9fff\w]', '', theme)[:8]
        if theme_tag:
            tags.append(theme_tag)
    return " ".join(tags) if tags else "政治学"


# ═══════════════════════════════════════════════════════════════════
# 卡片生成器
# ═══════════════════════════════════════════════════════════════════

def generate_concept_cards(data, min_per_concept=1, max_per_concept=2):
    """
    类型1: 概念定义卡
    从 concepts 数组提取，每个概念选取最佳定义。
    正面: 概念名
    背面: 定义（原文引用+书名+页码）
    """
    cards = []
    concepts = data.get('concepts', [])

    for item in concepts:
        concept_name = item.get('concept', '').strip()
        if not concept_name or len(concept_name) < 2:
            continue

        definitions = item.get('definitions', [])
        if not definitions:
            continue

        # 按文本质量排序：优先选择长度适中（30-200字）且含实质内容的定义
        def quality_score(d):
            text = d.get('text', '')
            length = len(text)
            # 太短没信息量，太长可能不完整
            if length < 10:
                return -100
            score = 0
            # 长度评分：30-150 字最优
            if 30 <= length <= 150:
                score += 50
            elif 20 <= length <= 250:
                score += 30
            elif length >= 10:
                score += 10
            # 含定义性词汇加分
            for kw in ['是指', '是指', '称为', '叫做', '定义为', '概念', '本质', '核心', '指的', '是一种', '是一个']:
                if kw in text:
                    score += 20
                    break
            return score

        sorted_defs = sorted(definitions, key=quality_score, reverse=True)

        # 每个概念取 1-3 个最佳定义（来自不同书）
        seen_books = set()
        count = 0
        for d in sorted_defs:
            if count >= max_per_concept:
                break
            text = clean_text(d.get('text', ''))
            if len(text) < 10:
                continue
            book = d.get('book', '')
            # 同一本书只取一条，避免重复
            if book in seen_books:
                continue
            seen_books.add(book)

            author = d.get('author', '')
            page = d.get('page', '')

            front = concept_name
            back = format_back(text, book, author, page)
            tag = make_tag(book, author) + " 概念"

            cards.append((front, back, tag))
            count += 1

    return cards


def generate_data_cards(data, min_cards=100):
    """
    类型2: 数据记忆卡
    从 data_points 提取含数字/百分比/年份的条目。
    正面: 问题（基于数据内容生成）
    背面: 数据原文+书名+页码
    """
    cards = []
    data_points = data.get('data_points', [])

    # 数值模式检测
    number_pattern = re.compile(
        r'\d+[%％]|\d+\.\d+%|\d{4}年|\d+亿|\d+万|\d+,\d{3}|\d+元|\d+倍|\d+个|\d+次'
    )

    seen_texts = set()  # 去重

    for dp in data_points:
        text = clean_text(dp.get('text', ''))
        if len(text) < 15:
            continue

        # 必须包含数值
        if not number_pattern.search(text):
            continue

        # 去重（基于前30字）
        dedup_key = text[:30]
        if dedup_key in seen_texts:
            continue

        book = dp.get('book', '')
        page = dp.get('page', '')
        dp_type = dp.get('type', '')

        # ── 生成问题（正面）──
        question = generate_data_question(text, book, dp_type)

        # ── 生成答案（背面）──
        back = format_back(text, book, "", page)

        # 标签
        tag_parts = ["数据"]
        if dp_type:
            tag_parts.append(dp_type)
        tag = make_tag(book) + " " + " ".join(tag_parts)

        cards.append((question, back, tag))
        seen_texts.add(dedup_key)

    return cards


def generate_data_question(text, book, dp_type):
    """根据数据文本内容智能生成问题"""
    # 提取关键数值
    percentages = re.findall(r'(\d+\.?\d*)\s*[%％]', text)
    years = re.findall(r'(\d{4})\s*年', text)
    amounts = re.findall(r'(\d+\.?\d*)\s*(亿|万亿|百万|万|千)', text)
    multiples = re.findall(r'(\d+\.?\d*)\s*倍', text)

    # 基于文本前半段生成问题
    # 截取前30-50字作为问题语境
    snippet = text[:50]
    if len(text) > 50:
        # 在逗号/句号处截断
        for i, ch in enumerate(snippet):
            if ch in '，。；！？、' and i > 20:
                snippet = snippet[:i]
                break

    # 根据数据类型生成不同问题模板
    if percentages:
        pct = percentages[0]
        return f"填空：{snippet}…（关键百分比数据）"

    if years and amounts:
        yr = years[0]
        return f"填空：{snippet}…（{yr}年数据）"

    if amounts:
        return f"填空：{snippet}…（关键数值）"

    if multiples:
        return f"填空：{snippet}…（倍数关系）"

    if years:
        yr = years[0]
        return f"填空：{snippet}…（{yr}年相关）"

    # 默认：提取核心事实
    return f"回忆：{snippet}…（来源：《{book}》）"


def generate_proposition_cards(data, min_cards=100):
    """
    类型3: 命题论证卡
    从 propositions 提取含实质论证内容的条目。
    正面: 命题（基于文本提炼的问题）
    背面: 原文论证+书名+页码
    """
    cards = []
    propositions = data.get('propositions', [])

    # 也从 cases 中提取部分作为命题卡
    cases = data.get('cases', [])

    seen_texts = set()

    # ── 处理 propositions ──
    for prop in propositions:
        text = clean_text(prop.get('text', ''))
        if len(text) < 30:  # 太短的跳过
            continue

        # 去重
        dedup_key = text[:40]
        if dedup_key in seen_texts:
            continue

        book = prop.get('book', '')
        author = prop.get('author', '')
        page = prop.get('page', '')
        theme = prop.get('theme', '')

        # ── 生成命题问题（正面）──
        question = generate_proposition_question(text, author, theme, book)

        # ── 生成论证（背面）──
        back = format_back(text, book, author, page)

        # 标签
        tag = make_tag(book, author, theme) + " 命题"

        cards.append((question, back, tag))
        seen_texts.add(dedup_key)

    # ── 处理 cases（案例也是命题论证的好材料）──
    for case in cases:
        text = clean_text(case.get('summary', ''))
        if len(text) < 50:
            continue

        dedup_key = text[:40]
        if dedup_key in seen_texts:
            continue

        book = case.get('book', '')
        author = case.get('author', '')
        page = case.get('page', '')
        name = case.get('name', '')

        question = f"案例：{name}（《{book}》）"
        back = format_back(text, book, author, page)
        tag = make_tag(book, author) + " 案例"

        cards.append((question, back, tag))
        seen_texts.add(dedup_key)

    return cards


def generate_proposition_question(text, author, theme, book):
    """根据命题文本生成问题"""
    # 如果有主题，用主题提问
    if theme and len(theme) > 2:
        # 截取文本核心部分
        core = text[:40]
        if len(text) > 40:
            for i, ch in enumerate(core):
                if ch in '，。；！？' and i > 15:
                    core = core[:i]
                    break
        return f"关于「{theme}」：{core}…？"

    # 如果有作者，用作者提问
    if author:
        core = text[:35]
        if len(text) > 35:
            for i, ch in enumerate(core):
                if ch in '，。；！？' and i > 12:
                    core = core[:i]
                    break
        return f"{author}提出：{core}…？"

    # 默认：提取前半段作为问题
    core = text[:40]
    if len(text) > 40:
        for i, ch in enumerate(core):
            if ch in '，。；！？' and i > 15:
                core = core[:i]
                break
    return f"论证：{core}…？（《{book}》）"


# ═══════════════════════════════════════════════════════════════════
# 导出函数
# ═══════════════════════════════════════════════════════════════════

def write_tsv(cards, filepath):
    """写入 TSV 文件（Anki 直接导入格式）"""
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for front, back, tag in cards:
            writer.writerow([front, back, tag])
    return len(cards)


def export_concepts(data):
    """导出概念定义卡"""
    header("导出概念定义卡")
    cards = generate_concept_cards(data)
    filepath = OUTPUT_DIR / "concepts.csv"
    count = write_tsv(cards, filepath)
    ok(f"概念卡: {count} 张 → {filepath.name}")

    # 展示样例
    if cards:
        warn("样例:")
        for front, back, tag in cards[:3]:
            print(f"    正面: {front[:40]}")
            back_first_line = back.split('\n')[0]
            print(f"    背面: {back_first_line[:60]}...")
            print(f"    标签: {tag}")
            print()

    return count


def export_data_cards(data):
    """导出数据记忆卡"""
    header("导出数据记忆卡")
    cards = generate_data_cards(data)
    filepath = OUTPUT_DIR / "data.csv"
    count = write_tsv(cards, filepath)
    ok(f"数据卡: {count} 张 → {filepath.name}")

    if cards:
        warn("样例:")
        for front, back, tag in cards[:3]:
            print(f"    正面: {front[:50]}")
            back_first_line = back.split('\n')[0]
            print(f"    背面: {back_first_line[:60]}...")
            print(f"    标签: {tag}")
            print()

    return count


def export_proposition_cards(data):
    """导出命题论证卡"""
    header("导出命题论证卡")
    cards = generate_proposition_cards(data)
    filepath = OUTPUT_DIR / "propositions.csv"
    count = write_tsv(cards, filepath)
    ok(f"命题卡: {count} 张 → {filepath.name}")

    if cards:
        warn("样例:")
        for front, back, tag in cards[:3]:
            print(f"    正面: {front[:50]}")
            back_first_line = back.split('\n')[0]
            print(f"    背面: {back_first_line[:60]}...")
            print(f"    标签: {tag}")
            print()

    return count


# ═══════════════════════════════════════════════════════════════════
# 统计
# ═══════════════════════════════════════════════════════════════════

def show_stats(data):
    """显示知识库统计信息"""
    header("知识库统计")

    meta = data.get('metadata', {})
    print(f"  总条目: {meta.get('total_entries', 'N/A')}")
    print(f"  来源书籍: {meta.get('total_books', 'N/A')} 本")
    print(f"  总字数: {meta.get('total_chars', 'N/A'):,}")
    print()

    counts = meta.get('entry_counts', {})
    print(f"  {'类别':<20} {'数量':>8}")
    print(f"  {'─'*20} {'─'*8}")
    for cat, cnt in counts.items():
        print(f"  {cat:<20} {cnt:>8}")

    print()
    header("卡片预估")
    concept_cards = generate_concept_cards(data)
    data_cards = generate_data_cards(data)
    prop_cards = generate_proposition_cards(data)
    print(f"  概念卡（预估）: {len(concept_cards)}")
    print(f"  数据卡（预估）: {len(data_cards)}")
    print(f"  命题卡（预估）: {len(prop_cards)}")
    print(f"  {'─'*20} {'─'*8}")
    print(f"  总计:            {len(concept_cards) + len(data_cards) + len(prop_cards)}")


# ═══════════════════════════════════════════════════════════════════
# 主函数
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='政治学知识库 → Anki 闪卡导出',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 export_anki.py              # 导出全部三类卡
  python3 export_anki.py --concepts   # 仅概念卡
  python3 export_anki.py --data       # 仅数据卡
  python3 export_anki.py --props      # 仅命题卡
  python3 export_anki.py --stats      # 查看统计

Anki 导入说明:
  1. 打开 Anki → 文件 → 导入
  2. 选择对应 .csv 文件
  3. 字段分隔符选 "Tab"
  4. 勾选 "允许在字段中使用 HTML"
        """
    )
    parser.add_argument('--concepts', action='store_true', help='仅导出概念定义卡')
    parser.add_argument('--data', action='store_true', help='仅导出数据记忆卡')
    parser.add_argument('--props', action='store_true', help='仅导出命题论证卡')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    args = parser.parse_args()

    # 加载知识库
    header("加载知识库")
    info(f"读取: {INDEX_PATH.name}")
    data = load_index()
    ok(f"加载完成: {data['metadata']['total_entries']} 条知识")

    # 仅统计
    if args.stats:
        show_stats(data)
        return

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    ok(f"输出目录: {OUTPUT_DIR}")

    # 决定导出哪些
    export_all = not (args.concepts or args.data or args.props)

    total = 0

    if export_all or args.concepts:
        total += export_concepts(data)

    if export_all or args.data:
        total += export_data_cards(data)

    if export_all or args.props:
        total += export_proposition_cards(data)

    # 总结
    header("导出完成")
    ok(f"总计: {total} 张闪卡")
    info(f"输出目录: {OUTPUT_DIR}")
    print()
    warn("Anki 导入步骤:")
    print("    1. 打开 Anki → 文件 → 导入")
    print("    2. 选择对应的 .csv 文件")
    print("    3. 字段分隔符选 'Tab'")
    print("    4. 勾选 '允许在字段中使用 HTML'")
    print("    5. 目标牌组建议: 政治学::概念 / 政治学::数据 / 政治学::命题")


if __name__ == '__main__':
    main()
