#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feynman-fill-f2.py — F2 候选卡壳点自动填充（启发式）

对 feynman-batch.py 产出的 .费曼检验.md 文件，用 6 条启发式自动生成 F2 候选卡壳点：
  1. 逻辑跳跃：「显然/易得/容易看出/略/留作练习」
  2. 绝对化论断：「必然/一定/不可能/本质上就是」+ 结论
  3. 未定义术语：F3 红灯术语高频无解释
  4. 引用代替论证：人名+年份 但 50 字内无"因为/具体来说"
  5. 修辞问句带过：以"？"结尾且后续无回答
  6. 公式无解释：块公式后 30 字内无"其中/表示/含义"

每条候选明确标 🤖 AI 猜测，作者需确认。F1 外行版 / F3 外行翻译 / F4 回炉不填（启发式会出垃圾或伪造历史）。

用法:
  python3 feynman-fill-f2.py --dry-run        # 只统计，不改文件
  python3 feynman-fill-f2.py                  # 填充所有空 F2（跳过已填）
  python3 feynman-fill-f2.py --force          # 强制覆盖（小心：清空作者已填）
"""

from __future__ import annotations
import os
import sys
import re
import pathlib
import argparse
from collections import Counter

# ============================================================
# 6 条启发式
# ============================================================

# 1. 逻辑跳跃信号
LOGIC_LEAP_MARKERS = [
    "显然", "易得", "容易看出", "不难发现", "不难看出", "易证", "同理可证",
    "略去证明", "证明略", "留作练习", "留给读者", "详见", "参见",
    "正如所指出的", "如前所述",
]

# 2. 绝对化论断信号（后跟结论）
ABSOLUTE_MARKERS = [
    "必然", "必定", "一定", "绝对", "永远", "始终", "毫无疑问",
    "本质上就是", "其实就是", "无非是", "不外乎是",
]

# 3. 引用代替论证：人名 + 4 位数字年份
CITATION_PATTERN = re.compile(
    r"([A-Z][a-zé]+\s+(?:et al\.?\s+)?|[\u4e00-\u9fa5]{2,5})\s*[\(（](\d{4})[\)）]"
)

# 4. 引用后展开论证的标志（50 字内出现这些 = 已展开）
CITATION_EXPLAIN = ["因为", "由于", "具体来说", "他的论证", "她的论证", "其论证",
                    "核心观点是", "关键在于", "理由是", "指出", "认为", "主张"]

# 5. 公式后解释的标志
FORMULA_EXPLAIN = ["其中", "这里", "表示", "含义", "代表", "定义为", "即"]

# 6. 黑名单术语（与 feynman-batch.py 同步）—— 用于规则 3
TERM_BLACKLIST_FLAT = []
for domain_terms in [
    ["模型", "训练", "参数", "梯度", "损失函数", "神经网络", "注意力",
     "表征", "嵌入", "微调", "推理", "涌现", "对齐", "幻觉",
     "transformer", "embedding", "RLHF", "RAG", "token", "softmax", "attention"],
    ["向量", "矩阵", "函数", "导数", "概率分布", "收敛", "优化", "正则化"],
    ["波函数", "量子", "希尔伯特空间", "哈密顿量", "纠缠", "诠释"],
    ["认识论", "本体论", "形而上学", "还原论", "工具主义", "范式"],
]:
    TERM_BLACKLIST_FLAT.extend(domain_terms)


def find_section_heading(text: str, keyword: str) -> int:
    """找原文里包含 keyword 的最近 ## 标题，返回其行号。"""
    lines = text.split("\n")
    current_h2 = "开头"
    for i, line in enumerate(lines):
        if line.startswith("## "):
            current_h2 = line.lstrip("# ").strip()
        if keyword in line:
            return current_h2
    return "未知章节"


def detect_logic_leaps(text: str) -> list[dict]:
    """规则 1：逻辑跳跃。"""
    findings = []
    lines = text.split("\n")
    current_h2 = "开头"
    for line in lines:
        if line.startswith("## "):
            current_h2 = line.lstrip("# ").strip()
            continue
        if line.startswith("#"):  # 跳过 H1/H3
            continue
        for marker in LOGIC_LEAP_MARKERS:
            if marker in line:
                # 抽上下文（前后 30 字）
                idx = line.find(marker)
                ctx = line[max(0, idx-20): idx+len(marker)+30].strip()
                findings.append({
                    "type": "logic_leap",
                    "section": current_h2,
                    "marker": marker,
                    "context": ctx[:80],
                    "guess": f"出现「{marker}」——可能跳步/略证，AI 猜测作者没真推导",
                })
                break  # 一行只报一次
    return findings


def detect_absolute_claims(text: str) -> list[dict]:
    """规则 2：绝对化论断。"""
    findings = []
    lines = text.split("\n")
    current_h2 = "开头"
    for line in lines:
        if line.startswith("## "):
            current_h2 = line.lstrip("# ").strip()
            continue
        if line.startswith("#"):
            continue
        for marker in ABSOLUTE_MARKERS:
            if marker in line:
                idx = line.find(marker)
                ctx = line[max(0, idx-15): idx+len(marker)+40].strip()
                # 过滤：太短的行（可能只是举例）
                if len(line.strip()) < 15:
                    continue
                findings.append({
                    "type": "absolute",
                    "section": current_h2,
                    "marker": marker,
                    "context": ctx[:80],
                    "guess": f"绝对化论断「{marker}...」——AI 猜测缺乏论证或反例考虑",
                })
                break
    return findings


def detect_undefined_terms(text: str) -> list[dict]:
    """规则 3：未定义黑名单术语（高频无解释）。"""
    findings = []
    EXPLAIN_HINTS = ["即", "也就是", "指的是", "意思是", "（", "(", "—", ": "]
    for term in TERM_BLACKLIST_FLAT:
        positions = []
        start = 0
        while True:
            idx = text.find(term, start)
            if idx < 0:
                break
            positions.append(idx)
            start = idx + len(term)
        if len(positions) < 3:
            continue
        explained = sum(
            1 for pos in positions
            if any(h in text[pos+len(term): pos+len(term)+30] for h in EXPLAIN_HINTS)
        )
        if explained == 0:
            findings.append({
                "type": "undefined_term",
                "section": "全文",
                "marker": term,
                "context": f"出现 {len(positions)} 次，0 次解释",
                "guess": f"术语「{term}」高频（{len(positions)}次）完全无解释——AI 猜测在掩盖理解空洞（见 F3）",
            })
    return findings[:5]  # 最多 5 个，避免淹没


def detect_citation_without_argument(text: str) -> list[dict]:
    """规则 4：引用代替论证。"""
    findings = []
    lines = text.split("\n")
    current_h2 = "开头"
    for line in lines:
        if line.startswith("## "):
            current_h2 = line.lstrip("# ").strip()
            continue
        if line.startswith("#"):
            continue
        for m in CITATION_PATTERN.finditer(line):
            citation = m.group(0)
            idx = m.end()
            # 看后续 50 字
            window = line[idx: idx+50]
            if not any(ex in window for ex in CITATION_EXPLAIN):
                ctx = line[max(0, m.start()-10): idx+30].strip()
                findings.append({
                    "type": "citation",
                    "section": current_h2,
                    "marker": citation,
                    "context": ctx[:80],
                    "guess": f"引用「{citation}」但未展开论证——AI 猜测是引用撑场面",
                })
                break  # 一行一次
    return findings


def detect_rhetorical_questions(text: str) -> list[dict]:
    """规则 5：修辞问句带过（问号结尾且后续无回答）。"""
    findings = []
    lines = text.split("\n")
    current_h2 = "开头"
    for i, line in enumerate(lines):
        if line.startswith("## "):
            current_h2 = line.lstrip("# ").strip()
            continue
        if line.startswith("#"):
            continue
        s = line.strip()
        # 问句：含 "？" 或 "?" 结尾，且含中文问词
        if ("？" in s or s.endswith("?")) and any(w in s for w in ["吗", "呢", "为什么", "如何", "怎么", "是什么"]):
            # 看后续 2 行是否有"答：/答案是/实际上/答案是"
            following = " ".join(lines[i+1: i+3])
            if not any(ans in following for ans in ["答案是", "实际上", "原因是", "因为", "答：", "解："]):
                if len(s) < 100:  # 太长的可能是讨论
                    findings.append({
                        "type": "rhetorical",
                        "section": current_h2,
                        "marker": s[:40] + ("..." if len(s) > 40 else ""),
                        "context": s[:80],
                        "guess": "修辞问句带过——AI 猜测把问题甩给读者，作者自己没回答",
                    })
    return findings[:3]  # 最多 3 个


def detect_formulas_without_explanation(text: str) -> list[dict]:
    """规则 6：块公式后无解释。"""
    findings = []
    # 找 $$...$$ 块
    blocks = list(re.finditer(r"\$\$(.+?)\$\$", text, re.DOTALL))
    lines = text.split("\n")
    # 重建位置到行映射（粗略）
    for m in blocks:
        end = m.end()
        after = text[end: end+50]
        if not any(ex in after for ex in FORMULA_EXPLAIN):
            # 找所在 H2
            pos = m.start()
            current_h2 = "未知"
            char_count = 0
            for line in lines:
                if line.startswith("## "):
                    current_h2 = line.lstrip("# ").strip()
                char_count += len(line) + 1
                if char_count > pos:
                    break
            formula_preview = m.group(0)[:40].replace("\n", " ")
            findings.append({
                "type": "formula",
                "section": current_h2,
                "marker": formula_preview + "...",
                "context": formula_preview,
                "guess": "公式后无「其中/表示/含义」解释——AI 猜测作者会算但讲不清含义",
            })
    return findings[:3]


def run_all_heuristics(text: str) -> list[dict]:
    """对原文跑 6 条启发式，合并去重，返回候选卡壳点列表。"""
    findings = []
    findings += detect_logic_leaps(text)
    findings += detect_absolute_claims(text)
    findings += detect_undefined_terms(text)
    findings += detect_citation_without_argument(text)
    findings += detect_rhetorical_questions(text)
    findings += detect_formulas_without_explanation(text)
    # 截断到合理数量（每篇最多 12 条候选）
    return findings[:12]


# ============================================================
# F2 段落重写
# ============================================================

EMPTY_F2_MARKER = "_（你填）_"  # batch.py 产出的空表标志


def is_f2_empty(report_text: str) -> bool:
    """检测 .费曼检验.md 的 F2 是否还是空模板。"""
    return EMPTY_F2_MARKER in report_text


def build_f2_table(findings: list[dict]) -> str:
    """把启发式 findings 转成 F2 表格内容。"""
    if not findings:
        return (
            "| # | 哪段/论断 | 卡在哪（🤖 AI 猜测） | 当时怎么绕过（🤖 猜） | 真懂吗（作者填） |\n"
            "|---|---|---|---|---|\n"
            "| - | _启发式未抓到候选，作者需自曝_ | — | — | 🔴/🟡/🟢 |\n"
        )

    type_label = {
        "logic_leap": "逻辑跳跃",
        "absolute": "绝对化",
        "undefined_term": "未定义术语",
        "citation": "引用代证",
        "rhetorical": "修辞带过",
        "formula": "公式无解",
    }
    rows = ["| # | 哪段/论断 | 卡在哪（🤖 AI 猜测） | 当时怎么绕过（🤖 猜） | 真懂吗（作者填） |",
            "|---|---|---|---|---|"]
    for i, f in enumerate(findings, 1):
        ctx = f["context"].replace("|", "\\|").replace("\n", " ")[:60]
        guess = f["guess"].replace("|", "\\|")[:80]
        label = type_label.get(f["type"], f["type"])
        rows.append(f"| {i} | §{f['section']}<br>`{f['marker'][:30]}` | [{label}] {guess} | 原文：「{ctx}」 | 🔴/🟡/🟢 _待作者确认_ |")
    return "\n".join(rows) + "\n"


def replace_f2_section(report_text: str, new_table: str) -> str:
    """把 .费曼检验.md 里的 F2 表格段落替换成新的。"""
    # F2 段落结构：
    # ## F2 · 卡壳点清单...
    # > 🚨 ...警告
    # 
    # | # | 哪段/论断...
    # |---|...
    # | 1 | _（你填）_ ...
    #
    # **最难回答的 1 个追问**...

    # 找 F2 表格块（从 "| # |" 开始到空行/下一个非表格行）
    pattern = re.compile(
        r"(## F2 · 卡壳点清单.*?\n(?:[^\n]*\n)*?)"
        r"(\| # \|.*?\n(?:\|[^\n]*\n)+)",
        re.DOTALL,
    )
    m = pattern.search(report_text)
    if not m:
        return report_text  # 找不到，不动

    header_block = m.group(1)
    # 替换表格
    new_block = header_block + new_table
    return report_text[: m.start(2)] + new_table + report_text[m.end(2):]


# ============================================================
# 主流程
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="项目根")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="强制覆盖（含作者已填）")
    args = ap.parse_args()

    project_root = pathlib.Path(args.root).resolve()
    reports = list(project_root.rglob("*.费曼检验.md"))
    # 排除示范文件（物理那篇是手工填的）
    reports = [r for r in reports if "示例" not in r.name and "检验报告" not in str(r)]

    print(f"\n🔍 找到 {len(reports)} 个 .费曼检验.md 文件")
    print(f"   模式：{'DRY-RUN' if args.dry_run else '填充（跳过已填）' if not args.force else '强制覆盖'}\n")

    filled = 0
    skipped_filled = 0
    skipped_no_finding = 0
    total_findings = 0
    findings_per_doc = Counter()

    for i, report_path in enumerate(reports, 1):
        rel = report_path.relative_to(project_root).as_posix()
        try:
            report_text = report_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        if not args.force and not is_f2_empty(report_text):
            skipped_filled += 1
            continue

        # 找原文
        src_path = report_path.with_name(report_path.stem.replace(".费曼检验", "") + ".md")
        if not src_path.exists():
            continue
        try:
            src_text = src_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # 跑启发式
        findings = run_all_heuristics(src_text)
        total_findings += len(findings)
        findings_per_doc[len(findings)] += 1

        if not findings:
            skipped_no_finding += 1
            continue

        if args.dry_run:
            filled += 1
            continue

        # 生成新表 + 替换
        new_table = build_f2_table(findings)
        new_report = replace_f2_section(report_text, new_table)
        if new_report != report_text:
            report_path.write_text(new_report, encoding="utf-8")
            filled += 1

        if i % 50 == 0:
            print(f"   进度 {i}/{len(reports)}")

    # 统计
    print(f"\n{'='*60}")
    print(f"  F2 候选填充统计" + ("（DRY-RUN）" if args.dry_run else ""))
    print(f"{'='*60}")
    print(f"  📋 扫描 .费曼检验.md : {len(reports)}")
    print(f"  ✅ 填充 F2 候选     : {filled}")
    print(f"  ⏭️ 跳过（作者已填） : {skipped_filled}")
    print(f"  ⚠️ 启发式未抓到    : {skipped_no_finding}")
    print(f"  📊 共生成候选卡壳点 : {total_findings}（平均 {total_findings/max(filled,1):.1f} 条/篇）")
    print(f"\n  分布：")
    for n in sorted(findings_per_doc.keys(), reverse=True):
        c = findings_per_doc[n]
        bar = "█" * min(n, 12)
        print(f"    {n:2d} 条候选: {c:3d} 篇  {bar}")
    print()


if __name__ == "__main__":
    main()
