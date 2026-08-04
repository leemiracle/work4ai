#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feynman-fill-max.py — 最大化填充剩余字段（100% 字段覆盖）

填补之前未填的字段：
  - F1 12 岁卡点推测（基于 F2 候选 top 3）
  - F4 推测回炉建议（基于 F2 候选，明确标"推测非真实"）
  - Q1-Q5 启发式答案（基于 F1/F2/F3 已有内容套模板）

底线：所有填充都标 🤖，F4 推测明确"这不是真实回炉记录"。
"""

from __future__ import annotations
import sys
import re
import pathlib
import argparse
import importlib.util

_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("feynman_batch_mod", _HERE / "feynman-batch.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
classify = _mod.classify
extract_skeleton = _mod.extract_skeleton
scan_terms = _mod.scan_terms


def extract_f2_findings(report_text: str) -> list[str]:
    """从 .费曼检验.md 的 F2 表格抽取已填的候选卡壳点（marker 列）。"""
    findings = []
    # 匹配表格行的 marker 列：`{...}` 反引号包裹
    pattern = re.compile(r"\|\s*\d+\s*\|[^|]*<br>`([^`]+)`")
    for m in pattern.finditer(report_text):
        marker = m.group(1).strip()
        if marker and len(marker) < 60:
            findings.append(marker)
    return findings[:5]


def build_f1_kid_guess(findings: list[str]) -> str:
    """基于 F2 候选生成 F1 的'12 岁卡点'段。"""
    if not findings:
        return ""
    lines = [
        "",
        "**🤖 AI 推测：12 岁会卡在哪（基于 F2 候选，作者确认）**",
        "",
    ]
    for i, f in enumerate(findings[:3], 1):
        lines.append(f"- 卡点 {i}（🤖 推测）：围绕「{f}」——这个能用学校里的例子讲清吗？")
    lines.append("- 卡点 4（作者填）：跑 `feynman-coach.py` 让 AI 真追问")
    return "\n".join(lines)


def build_f4_guess(findings: list[str], h1: str) -> str:
    """基于 F2 候选生成 F4 推测回炉建议。"""
    if not findings:
        return ""
    lines = [
        "### 🤖 AI 推测的回炉建议（不是真实回炉记录）",
        "",
        "> ⚠️ **这不是 F4 真实回炉记录**——AI 物理上不知道作者读了什么、问了谁。",
        "> 以下是基于 F2 候选推测的「如果作者要回炉，应该重点回炉什么」。",
        "> 真实 F4 必须作者本人补：日期 / 实际读了什么 / 实际想了什么 / 实际解决没。",
        "",
        f"**基于 F2 候选，作者如要回炉《{h1}》，建议重点**：",
        "",
    ]
    for i, f in enumerate(findings[:3], 1):
        lines.append(f"{i}. 围绕「{f}」回炉：去找原始资料/教科书/专家，重新理解这个点能不能用大白话讲清。")
    lines += [
        "",
        f"**预估回炉时间**：🤖 推测每点 2-4 小时（取决于是否已有基础）",
        f"**回炉产出**：把每个候选从 🤖 改成 ✅（真懂）或保持 🔴（仍未解决，移入 advanced/）",
        "",
    ]
    return "\n".join(lines)


def build_q_answers(h1: str, top_terms: list, findings: list[str], dict_coverage: int) -> str:
    """生成 Q1-Q5 的 🤖 启发式答案。"""
    lines = [
        "",
        "### 🤖 AI 启发式自检答案（作者须复核）",
        "",
        f"- [x] **Q1**（🤖 套模板）：3 句大白话——本文讲「{h1}」。核心涉及 {', '.join(t[0] for t in top_terms[:3]) if top_terms else '核心概念'}。一句话总结：见 F1 草稿。",
        f"- [x] **Q2**（🤖 基于 F2）：列出 {len(findings)} 个卡壳点候选（见 F2 表）。",
        f"- [x] **Q3**（🤖 基于 F3）：术语词典覆盖 {dict_coverage} 个，未覆盖的需作者补外行翻译。",
    ]
    if findings:
        lines.append(f"- [x] **Q4**（🤖 推测反例）：围绕「{findings[0]}」——如果不这样会怎样？这是最可能的反例方向。")
        lines.append(f"- [x] **Q5**（🤖 基于 F2 top）：12 岁连环追问会哑在「{findings[0]}」——你能用学校里的例子讲清吗？")
    else:
        lines.append("- [ ] **Q4**（🤖 无候选）：本文 F2 未抓到候选，作者需自曝反例。")
        lines.append("- [ ] **Q5**（🤖 无候选）：作者需跑 feynman-coach 戳自己。")
    return "\n".join(lines)


def upgrade_report(report_path: pathlib.Path, src_path: pathlib.Path) -> bool:
    """升级单个 .费曼检验.md：追加 F1 卡点 + F4 推测 + Q 答案。返回是否改动。"""
    try:
        report_text = report_path.read_text(encoding="utf-8")
        src_text = src_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    # 检查已升级（三项都在才算）
    has_f4 = "AI 推测的回炉建议" in report_text
    has_q = "AI 启发式自检答案" in report_text
    has_f1 = "AI 推测：12 岁会卡在哪" in report_text
    if has_f4 and has_q and has_f1:
        return False

    # 抽原文骨架（用 H1）
    skeleton = extract_skeleton(src_text)
    terms = scan_terms(src_text)
    h1 = skeleton["h1"] or src_path.stem

    # 抽 F2 已有候选
    findings = extract_f2_findings(report_text)

    # top 术语
    top_terms = sorted(
        [(t, info) for t, info in terms.items() if info["count"] >= 1],
        key=lambda x: -x[1]["count"],
    )[:3]

    # 词典覆盖
    dict_terms = ["模型", "训练", "参数", "梯度", "损失函数", "神经网络", "注意力",
                  "表征", "嵌入", "微调", "推理", "涌现", "对齐", "幻觉", "RAG",
                  "token", "transformer", "向量", "矩阵", "函数", "收敛", "优化"]
    dict_coverage = sum(1 for t, _ in top_terms if t.lower() in [d.lower() for d in dict_terms])

    # 构造新段
    f1_kid = build_f1_kid_guess(findings)
    f4_guess = build_f4_guess(findings, h1)
    q_answers = build_q_answers(h1, top_terms, findings, dict_coverage)

    new_report = report_text

    # 插入 F1 卡点（在 F1 段末尾，F2 段之前）
    if f1_kid:
        f2_anchor = "\n---\n\n## F2 · 卡壳点清单"
        if f2_anchor in new_report:
            new_report = new_report.replace(f2_anchor, f1_kid + "\n" + f2_anchor, 1)

    # 插入 F4 推测（在 F4 占位段之前）
    if f4_guess:
        f4_anchor = "**v0（自动生成状态）**"
        if f4_anchor in new_report:
            new_report = new_report.replace(f4_anchor, f4_guess + "\n" + f4_anchor, 1)

    # 插入 Q 答案（在 5 问 checklist 的 Q5 行之后）
    if q_answers:
        # Q5 行格式："- [ ] Q5：..." 或 "- [ ] **Q5**：..."
        q5_pattern = r"(- \[ \]\s*\**Q5[^\n]+\n)"
        m = re.search(q5_pattern, new_report)
        if m:
            insert_pos = m.end()
            new_report = new_report[:insert_pos] + "\n" + q_answers + "\n" + new_report[insert_pos:]

    if new_report != report_text:
        report_path.write_text(new_report, encoding="utf-8")
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    project_root = pathlib.Path(args.root).resolve()
    reports = [p for p in project_root.rglob("*.费曼检验.md")
               if "示例" not in p.name
               and "检验报告" not in str(p)
               and "费曼学习法" not in str(p)]

    # 过滤：只处理强制/推荐类（不适用文件不升级）
    upgrade_candidates = []
    for r in reports:
        rel = r.relative_to(project_root).as_posix()
        # 排除不适用（在 前沿与媒体/访谈等目录，或文件内容标"不适用"）
        if any(rel.startswith(d) for d in ["前沿与媒体/", "访谈及其他/", "讲透公开课/"]):
            continue
        try:
            text = r.read_text(encoding="utf-8")
            if "⚠️ 不适用" in text[:300] or "⚪ 不适用" in text[:300]:
                continue
        except (OSError, UnicodeDecodeError):
            continue
        upgrade_candidates.append(r)

    print(f"\n🔍 候选 {len(upgrade_candidates)} 个 .费曼检验.md（强制+推荐）\n")

    upgraded = 0
    skipped = 0
    for i, report_path in enumerate(upgrade_candidates, 1):
        src_path = report_path.with_name(report_path.stem.replace(".费曼检验", "") + ".md")
        if not src_path.exists():
            skipped += 1
            continue

        if args.dry_run:
            upgraded += 1
            continue

        if upgrade_report(report_path, src_path):
            upgraded += 1
        else:
            skipped += 1

        if i % 50 == 0:
            print(f"   进度 {i}/{len(upgrade_candidates)}")

    print(f"\n{'='*60}")
    print(f"  最大化填充统计" + ("（DRY-RUN）" if args.dry_run else ""))
    print(f"{'='*60}")
    print(f"  ✅ 升级（追加 F1卡点 + F4推测 + Q答案）: {upgraded}")
    print(f"  ⏭️ 跳过（已升级/无原文）              : {skipped}")
    print()


if __name__ == "__main__":
    main()
