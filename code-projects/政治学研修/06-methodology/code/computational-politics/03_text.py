#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""计算政治学代码 3：文本即数据（text-as-data）
演示：政治文本词频分析、两阵营词汇差异（极化的代理测量）
纯 Python 标准库。运行：python3 03_text.py
说明：真实研究会用 jieba/LLM，本示例用最简分词展示原理。
"""
import re
from collections import Counter

# 两段政治文本（简短示例：左翼 vs 右翼话语）
left_text = """
我们要公平 平等 福利 再分配 公平 保护工人 平等 公平
福利 再分配 教育 医疗 保护 弱者 平等 公平 民生
"""
right_text = """
我们要自由 市场 减税 自由 市场 竞争 自由 安全 秩序
市场 传统 减税 效率 自由 企业 创新 竞争 责任
"""

def tokenize(t):
    # 中文按空格/标点分词（示例）；真实用 jieba
    return [w for w in re.split(r'[\s，。、；：！？""''（）()]+', t.strip()) if w]

lw = tokenize(left_text)
rw = tokenize(right_text)
lc, rc = Counter(lw), Counter(rw)

print("=" * 55)
print("1. 词频：两阵营各自的高频词")
print("=" * 55)
print(f"  左翼 top5: {lc.most_common(5)}")
print(f"  右翼 top5: {rc.most_common(5)}\n")

print("=" * 55)
print("2. 独有词（只在一方出现 = 立场信号词）")
print("=" * 55)
left_only = sorted({w for w in lc if rc.get(w, 0) == 0})
right_only = sorted({w for w in rc if lc.get(w, 0) == 0})
shared = sorted({w for w in lc if rc.get(w, 0) > 0})
print(f"  左翼独有: {left_only}")
print(f"  右翼独有: {right_only}")
print(f"  双方共享: {shared}\n")

print("=" * 55)
print("3. 极化指数（独有词占比 = 话语隔离程度）")
print("=" * 55)
all_words = set(lc) | set(rc)
exclusive = set(left_only) | set(right_only)
polarization = len(exclusive) / len(all_words)
print(f"  总词种: {len(all_words)}；独有词: {len(exclusive)}")
print(f"  极化指数 = {polarization:.2f}（越接近1，两阵营话语越不重叠）")
print("  → 真实研究里，这可量化媒体/政党的话语极化（呼应")
print("    [02 民主倒退](../../../papers/前沿-民主倒退与竞争性威权.md) 的极化议题）")
