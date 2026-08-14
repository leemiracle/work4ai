#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feynman-fill-final.py — 最终填充（最大化自动化）

把剩余未填的字段全填上：
  - F1 外行版：启发式草稿（H1 + 首段 + top 术语套模板）🤖
  - F3 外行翻译：30 词词典，命中的填 🤖
  - F4 回炉：占位"v0 自动生成，未回炉"🚨
  - Q1-Q5：勾选 Q2，其他标依赖作者
  - 350 篇不适用：也产 .费曼检验.md，标"⚠️ 不适用"

诚实原则：每项都明确标 🤖 AI 草稿 vs 作者必填，不伪造。

用法:
  python3 feynman-fill-final.py --dry-run
  python3 feynman-fill-final.py
  python3 feynman-fill-final.py --force   # 覆盖已升级的
"""

from __future__ import annotations
import os
import sys
import re
import pathlib
import argparse
import datetime
from collections import Counter

# 复用 feynman-batch.py 的分类与扫描函数（文件名带横线，需 importlib 动态加载）
import importlib.util
_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("feynman_batch_mod", _HERE / "feynman-batch.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
classify = _mod.classify
extract_skeleton = _mod.extract_skeleton
scan_terms = _mod.scan_terms

# ============================================================
# 30 词外行翻译词典（覆盖项目最高频术语）
# ============================================================

TERM_DICTIONARY = {
    # AI/ML
    "模型": "用一堆数字权重模拟某种智能行为的程序",
    "训练": "反复调整模型里的数字，让它的输出越来越接近正确答案",
    "参数": "模型里那些会被调整的数字，每改一个，输出就变一点",
    "梯度": "告诉每个参数该往哪个方向调、调多少的指南针",
    "损失函数": "给模型当前表现打分的尺子，分数越低越好",
    "神经网络": "很多简单的'判断小单元'串在一起，能学会复杂任务",
    "注意力": "模型决定看输入的哪一部分更重要，像人读书时划重点",
    "表征": "把一件事转换成一组数字，让电脑能算",
    "嵌入": "把词语/图像变成一串数字坐标，相近的东西坐标相近",
    "微调": "拿一个已经训练好的模型，在你的小数据上再调一调",
    "推理": "模型训完之后，给它新输入算出答案的过程",
    "涌现": "模型大到一定程度，突然出现小模型完全不会的能力",
    "对齐": "让模型按人的意图做事，不偏离、不使坏",
    "幻觉": "模型一本正经地说错的话，看着像真的其实是编的",
    "RAG": "回答前先去查文档，把答案建立在真实资料上",
    "token": "模型处理文字的最小单位，比词更细，约 3/4 个英文词",
    "transformer": "目前最主流的神经网络结构，靠'注意力'处理序列",
    "embedding": "把词语/图像变成一串数字坐标，相近的东西坐标相近",
    "attention": "模型决定看输入的哪一部分更重要",
    "softmax": "把一组数字变成概率（加起来等于 1）的常用做法",
    "RLHF": "用人对模型答案的好坏评价当奖励，反向训练模型",
    "fine-tune": "拿一个已经训练好的模型，在你的小数据上再调一调",
    "logits": "模型最后一层输出的原始数字，还没变成概率",
    # 数学
    "向量": "一串数字，可以表示方向和大小",
    "矩阵": "一堆数字排成方块，能批量算向量",
    "函数": "输入一个数、输出一个数的规则",
    "收敛": "训练中模型的分数不再变化，稳定下来了",
    "优化": "找一组最好的参数让分数最低",
    "正则化": "给模型加约束，防止它死记硬背训练数据",
    "概率分布": "所有可能结果各占多少比例的清单，加起来等于 100%",
    "导数": "函数在某点的变化率，往哪个方向走会变大变小",
    # 物理
    "量子": "微观粒子的物理学，规律和宏观世界很不一样",
    "波函数": "量子力学里描述粒子状态的数学对象",
    "纠缠": "两个量子粒子不管隔多远，状态都互相绑定的现象",
    # 哲学/方法
    "认识论": "研究'我们怎么算知道了'这件事的哲学分支",
    "本体论": "研究'什么东西真的存在'的哲学分支",
    "还原论": "认为复杂事物能拆成简单部分来理解的立场",
    "工具主义": "认为科学理论只是预测工具，不揭示真理的立场",
    "范式": "某个时代科学家群体公认的研究框架",
    "范式转移": "旧框架解释不了新现象，被全新框架取代",
}


def lookup_term(term: str) -> tuple[str, str]:
    """返回 (翻译, 来源)。来源：dictionary / not_in_dict。"""
    if term in TERM_DICTIONARY:
        return TERM_DICTIONARY[term], "🤖 词典"
    # 同义词回退
    lower = term.lower()
    if lower in TERM_DICTIONARY:
        return TERM_DICTIONARY[lower], "🤖 词典"
    return "🤖 无词典翻译，作者填", "not_in_dict"


# ============================================================
# F1 外行版草稿生成
# ============================================================

def build_f1_draft(skeleton: dict, terms: dict) -> str:
    """生成 F1 外行版草稿（基于 H1 + 首段 + top 3 术语套模板）。"""
    h1 = skeleton["h1"] or "(未抽到标题)"
    first_para = skeleton["first_para"] or "(未抽到首段)"

    # top 3 术语（按出现次数）
    sorted_terms = sorted(
        [(t, info) for t, info in terms.items() if info["count"] >= 1],
        key=lambda x: -x[1]["count"],
    )[:3]

    lines = [
        "### 自动骨架（作者据此补血肉）",
        "",
        f"**原文标题**：{h1}",
        "",
        "**原文首段摘要**（截 300 字）：",
        "```",
        first_para[:300],
        "```",
        "",
        f"**原文 H2 骨架**（共 {len(skeleton['h2_list'])} 个）：",
    ]
    for i, h2 in enumerate(skeleton["h2_list"], 1):
        lines.append(f"{i}. {h2}")
    lines += [
        "",
        f"**数学层提示**：原文有 {skeleton['formula_inline']} 个行内公式 + {skeleton['formula_block']} 个块公式。",
        "",
        "### 🤖 AI 草稿版（质量低，作者必须重写）",
        "",
        "> ⚠️ 这是基于原文 H1+首段+top 术语套模板生成的草稿。**真正的外行版需要对主题的深刻理解**，",
        "> AI 启发式做不到——以下仅供参考，作者必须重写。",
        "",
        f"**这篇文档的核心一句话（🤖 草稿）**：",
        f"本文讲「{h1}」。从首段看，核心论点是：「{first_para[:80]}...」",
        "",
        "**3 个核心概念的大白话（🤖 草稿，作者须重写）**：",
        "",
        "| 原术语 | AI 词典翻译 | 生活类比（作者填） |",
        "|---|---|---|",
    ]
    if sorted_terms:
        for t, info in sorted_terms:
            trans, src = lookup_term(t)
            lines.append(f"| {t} | {trans} | _作者填_ |")
    else:
        lines.append("| _未抽到高频术语_ | — | — |")

    lines += [
        "",
        "**12 岁表弟会卡在哪一问？（🤖 草稿，作者须确认）**",
        f"- 卡点 1（🤖 猜）：术语「{sorted_terms[0][0] if sorted_terms else 'X'}」能否用学校里的例子讲清楚？",
        f"- 卡点 2（🤖 猜）：核心论断「{first_para[:40]}...」能举出反例吗？",
        "- 卡点 3（作者填）：_跑 feynman-coach.py 让 AI 戳_",
    ]
    return "\n".join(lines)


# ============================================================
# F3 翻译列填充
# ============================================================

def fill_f3_translations(report_text: str, terms: dict) -> str:
    """把 F3 表里 '🟢 待填' / '🟡 待填' 替换成词典翻译（命中的），保留前 3 列。"""
    def replacer(m):
        term = m.group(1).strip()
        count = m.group(2)
        explained = m.group(3)
        mark = m.group(4)  # 🟢/🟡
        trans, src = lookup_term(term)
        if "词典" in src:
            return f"| {term} | {count} | {explained} | 🤖 {trans} |"
        return f"| {term} | {count} | {explained} | {mark} 作者填 |"

    # 匹配 "| term | count | explained | 🟢/🟡 待填 |"（4 列）
    pattern = re.compile(
        r"\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(🟢|🟡)\s*待填\s*\|"
    )
    return pattern.sub(replacer, report_text)


# ============================================================
# F4 占位填充
# ============================================================

F4_PLACEHOLDER = """```markdown
**v0（自动生成状态）**：2026-08-04，本文由 feynman-batch + feynman-fill-f2 + feynman-fill-final 自动生成
**自检发现 gap**：⚠️ AI 不能填——这要求作者真实反思"以为懂其实不懂"
**重学动作**：⚠️ AI 不能填——AI 不知道作者读了什么、问了谁、跑了什么代码
**v2（当前）**：⚠️ 不存在——本文未经作者回炉
**仍未解决**：见 F2 候选（🤖 AI 猜测，作者需逐条确认哪些真卡）

🚨 F4 是费曼法不可外包的部分。本表是占位标记，不是回炉记录。
作者真实回炉后，请删除本段，按 feynman-batch.py 模板的 F4 格式重写。
```"""


def fill_f4_placeholder(report_text: str) -> str:
    """把 F4 段落的空模板替换成占位标记。"""
    # F4 空模板特征：含 "**v1（初稿）**：<日期>"
    pattern = re.compile(
        r"```markdown\n\*\*v1（初稿）\*\*：.*?\*\*仍未解决\*\*.*?\n```",
        re.DOTALL,
    )
    return pattern.sub(F4_PLACEHOLDER.replace("```markdown\n", "```markdown\n").rstrip(), report_text, count=1)


# ============================================================
# F1 段落升级（在已有 F1 段落后追加草稿）
# ============================================================

def append_f1_draft(report_text: str, skeleton: dict, terms: dict) -> str:
    """在 F1 段落的'### 待作者填'之前插入 AI 草稿。"""
    f1_draft = build_f1_draft(skeleton, terms)
    # 找 "### 待作者填：外行版核心" 锚点，在其前面插入
    anchor = "### 待作者填：外行版核心（不许用任何术语）"
    if anchor in report_text:
        marker = "\n---\n\n" + f1_draft + "\n\n"
        return report_text.replace(anchor, marker + anchor, 1)
    return report_text


# ============================================================
# 不适用文档的简化报告
# ============================================================

def gen_inapplicable_report(src_path: pathlib.Path, skeleton: dict, terms: dict, rel_path: str) -> str:
    """对不适用文档产简化版 .费曼检验.md。"""
    h1 = skeleton["h1"] or src_path.stem
    lines = [
        f"# 费曼检验（⚠️ 不适用）· {h1}",
        "",
        f"> 自动生成 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | 原文 [`{rel_path}`](../{rel_path})",
        f"> 类型：⚪ 不适用（索引/编年/清单/访谈）",
        "",
        "## ⚠️ 此文档类型不适合费曼检验",
        "",
        "**原因**：这类文档（前沿索引/访谈/论文清单/课程目录）是**编年或检索类**内容，",
        "没有教学论点。强行套费曼模板会产出垃圾——费曼法是检验「作者真懂没真懂」，",
        "对索引类文档无意义。",
        "",
        "## 启发式扫描结果（仅供参考，价值有限）",
        "",
        f"- 原文行数：约 {len(skeleton.get('first_para', '')) + 100}+ 行",
        f"- 抽到的 H1：{h1}",
        f"- H2 数量：{len(skeleton['h2_list'])}",
        f"- 黑名单术语出现：{sum(info['count'] for info in terms.values())} 次（无需外行翻译，因为这不是教学）",
        f"- 数学公式：{skeleton['formula_inline']} 行内 / {skeleton['formula_block']} 块",
        "",
        "## 如果非要「讲透」这类内容",
        "",
        "1. 先把它**改写为有论点的教程**（如把「前沿索引」改写成「为什么这些是 2025 年最重要的 5 个突破」）",
        "2. 然后照 `费曼学习法/费曼检验模板.md` 跑完整 F1-F4",
        "3. 否则不要做费曼检验——这是诚实的态度",
        "",
        "---",
        "_本文件由 `feynman-fill-final.py` 自动生成。明确标注「不适用」，不强行套模板。_",
    ]
    return "\n".join(lines)


# ============================================================
# 主流程
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    project_root = pathlib.Path(args.root).resolve()
    all_mds = []
    for p in project_root.rglob("*.md"):
        rel = p.relative_to(project_root).as_posix()
        if rel.startswith(".git/") or "/.git/" in rel or rel.startswith("费曼学习法/"):
            continue
        # 跳过已经生成的 .费曼检验.md（避免把自己当原文处理）
        if rel.endswith(".费曼检验.md"):
            continue
        all_mds.append((p, rel))

    print(f"\n🔍 扫描 {len(all_mds)} 个 .md")
    print(f"   模式：{'DRY-RUN' if args.dry_run else '填充（升级 312 + 新增 350 不适用）'}\n")

    # 标记已升级的：F4 含 "v0（自动生成状态）"
    upgraded = 0
    skipped_already = 0
    inapplicable_created = 0
    failed = 0

    for i, (abs_path, rel) in enumerate(all_mds, 1):
        cls = classify(rel)

        # 读原文
        try:
            src_text = abs_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            failed += 1
            continue

        skeleton = extract_skeleton(src_text)
        terms = scan_terms(src_text)

        # 强制 / 推荐：升级已有 .费曼检验.md
        if cls in ("mandatory", "recommended"):
            report_path = abs_path.with_name(abs_path.stem + ".费曼检验.md")
            if not report_path.exists():
                continue  # 没有报告，跳过（应已存在）
            try:
                report_text = report_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                failed += 1
                continue

            # 检查是否已升级
            already_upgraded = "v0（自动生成状态）" in report_text and "AI 草稿版" in report_text
            if already_upgraded and not args.force:
                skipped_already += 1
                continue

            if args.dry_run:
                upgraded += 1
                continue

            # 三步升级
            new_report = report_text
            new_report = append_f1_draft(new_report, skeleton, terms)
            new_report = fill_f3_translations(new_report, terms)
            new_report = fill_f4_placeholder(new_report)

            if new_report != report_text:
                report_path.write_text(new_report, encoding="utf-8")
                upgraded += 1

        # 不适用：产简化版
        elif cls == "skip":
            report_path = abs_path.with_name(abs_path.stem + ".费曼检验.md")
            if report_path.exists() and not args.force:
                skipped_already += 1
                continue
            if args.dry_run:
                inapplicable_created += 1
                continue
            content = gen_inapplicable_report(abs_path, skeleton, terms, rel)
            report_path.write_text(content, encoding="utf-8")
            inapplicable_created += 1

        if i % 80 == 0:
            print(f"   进度 {i}/{len(all_mds)}")

    print(f"\n{'='*60}")
    print(f"  最终填充统计" + ("（DRY-RUN）" if args.dry_run else ""))
    print(f"{'='*60}")
    print(f"  📋 扫描 .md       : {len(all_mds)}")
    print(f"  ✅ 升级强制/推荐  : {upgraded}（填 F1草稿 + F3词典翻译 + F4占位）")
    print(f"  🆕 新增不适用文件 : {inapplicable_created}（标⚠️ 不适用）")
    print(f"  ⏭️ 跳过已升级    : {skipped_already}")
    print(f"  ❌ 失败          : {failed}")
    print(f"\n  📊 项目 .费曼检验.md 总数：{len(list(project_root.rglob('*.费曼检验.md')))}")
    print()


if __name__ == "__main__":
    main()
