#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feynman-batch.py — 费曼检验批处理（对整个项目跑）

把整个 work4ai 项目的所有 .md 自动过一遍费曼检验：
- 自动分类：强制 F1-F4 / 推荐 F1+F3 / 不适用
- 强制/推荐类：在每个原文旁产 <原名>.费曼检验.md
  · F1 外行复述：抽骨架（标题/首段/H2/公式），留作者填血肉
  · F2 作者自曝：空表 + 红字（AI 不可代填——费曼法灵魂）
  · F3 术语黑名单：全自动扫描，启发式判定红灯（高频但无解释）
  · F4 回炉记录：空表 + 红字
- 不适用类：跳过，记录到 _index.md
- 产全局 _index.md（进度仪表盘）+ _红灯术语总清单.md（项目级 top 术语）

用法:
  python3 feynman-batch.py --dry-run                # 只看分类统计，不产文件
  python3 feynman-batch.py                          # 正式跑（跳过已存在的）
  python3 feynman-batch.py --force                  # 覆盖已存在的（小心：会清空你填的 F2/F4）
  python3 feynman-batch.py --root /path/to/work4ai  # 指定项目根
  python3 feynman-batch.py --only "讲透基础模型"     # 只处理某子目录

底线（不可移除）:
- 不改原文一字（只产旁置 .费曼检验.md）
- F2/F4 永远留空——AI 代写自曝 = 伪造费曼
- 不适用文档不强行套模板
"""

from __future__ import annotations
import os
import sys
import re
import json
import time
import datetime
import pathlib
import argparse
from collections import Counter, defaultdict

# ============================================================
# 术语黑名单（与 feynman-coach.py 共享，按领域分组）
# ============================================================

TERM_BLACKLIST = {
    "ai/ML": ["模型", "训练", "参数", "梯度", "损失函数", "神经网络", "注意力",
              "表征", "嵌入", "微调", "推理", "涌现", "对齐", "幻觉",
              "transformer", "embedding", "fine-tune", "RLHF", "RAG", "token",
              "softmax", "attention", "encoder", "decoder", "logits", "pooling"],
    "数学": ["向量", "矩阵", "函数", "导数", "积分", "概率分布", "梯度",
            "收敛", "优化", "正则化", "manifold", "tensor", "jacobian",
            "hessian", "正定", "范数", " inner product "],
    "物理": ["波函数", "量子", "希尔伯特空间", "哈密顿量", "波粒二象性",
            "纠缠", "诠释", "张量", "算符", "态矢量"],
    "哲学/方法": ["认识论", "本体论", "形而上学", "先验", "后验",
                "还原论", "工具主义", "实在论", "范式", "范式转移"],
}

# 展平成 (term, domain) 列表，长术语优先匹配
ALL_TERMS = []
for domain, terms in TERM_BLACKLIST.items():
    for t in terms:
        ALL_TERMS.append((t.strip(), domain))
ALL_TERMS.sort(key=lambda x: -len(x[0]))  # 长的先匹配，避免"梯度"被"梯度下降"截断

# ============================================================
# 分类规则
# ============================================================

def classify(rel_path: str) -> str:
    """返回 'mandatory' / 'recommended' / 'skip'。rel_path 是相对项目根的路径。"""
    p = rel_path.replace("\\", "/")
    pl = p.lower()

    # --- 不适用目录 ---
    if p.startswith("前沿与媒体/"):
        return "skip"  # 索引类，无教学论点
    if p.startswith("访谈及其他/"):
        return "skip"  # 访谈非教程
    if p.startswith("费曼学习法/"):
        return "skip"  # 本工具自身
    if p.startswith("讲透公开课/"):
        return "skip"  # 课程索引

    # --- 不适用文件名模式 ---
    base = pathlib.Path(p).name
    SKIP_PATTERNS = [
        "论文清单", "早期经典与历史", "最新前沿", "2024-2026",
        "00-角色", "00-AI顶级信息源", "README.md",  # 索引/课程列表
    ]
    # README 单独处理：如果是讲透系列或学科根 README，是"目录索引"→ skip；
    # 但项目根 README 也是索引。统一 skip README（除非 --include-readme）
    if base.lower() == "readme.md":
        return "skip"
    for pat in SKIP_PATTERNS:
        if pat in base:
            return "skip"

    # --- 推荐 F1+F3：职业系列（先于强制规则，避免被 "讲透XXX" 误吸）---
    if p.startswith("讲透AI for 职业/"):
        return "recommended"

    # --- 强制 F1-F4：讲透系列核心 + 学科 00/本质 ---
    # 讲透XXX/ 下的 00-/01-/02-/03- 等编号深度文件
    if re.match(r"^讲透[^/]+/\d+-", p):
        return "mandatory"
    # 讲透XXX/本质探索.md / 灵魂.md 等
    if re.match(r"^讲透[^/]+/(本质探索|灵魂|核心|总纲)", p):
        return "mandatory"
    # 学科目录下的 00-*是什么.md / 本质探索.md
    if re.match(r"^讲透AIfor各学科/[^/]+/(00-[^/]*是什么|本质探索)\.md$", p):
        return "mandatory"
    # 学科目录下的 01-XX深挖.md 等
    if re.match(r"^讲透AIfor各学科/[^/]+/\d+-[^/]*深挖", p):
        return "mandatory"
    # 学科/advanced/ 下的 01/02/03 深度文件（非论文清单）
    if re.match(r"^讲透AIfor各学科/[^/]+/advanced/[123]-", p):
        return "mandatory"
    # 横向打通/多角色审查 等根目录有论点的文件
    if base in ("横向打通-能力获取决策框架.md", "多角色审查报告.md"):
        return "mandatory"

    # --- 兜底 ---
    return "skip"


# （职业系列已上移到强制规则之前，避免被误吸为 mandatory）


# ============================================================
# F3：术语扫描 + 红灯判定
# ============================================================

# 术语后 N 字内出现这些词 = "有解释"
EXPLAIN_HINTS = ["即", "也就是", "指的是", "意思是", "即指", "（", "(", "—", ":", "：", "，即", "，也就是"]

def scan_terms(text: str) -> dict:
    """扫描文本里的黑名单术语，返回 {term: {count, domain, has_explain, red}}。"""
    results = {}
    for term, domain in ALL_TERMS:
        # 找所有出现位置
        positions = []
        start = 0
        while True:
            idx = text.find(term, start)
            if idx < 0:
                break
            positions.append(idx)
            start = idx + len(term)
        if not positions:
            continue

        # 检查每个位置：后 30 字内是否有解释提示
        explained_count = 0
        for pos in positions:
            window = text[pos + len(term): pos + len(term) + 30]
            if any(hint in window for hint in EXPLAIN_HINTS):
                explained_count += 1

        count = len(positions)
        has_explain = explained_count > 0
        # 红灯：高频（≥3 次）且无任何解释
        red = (count >= 3 and explained_count == 0)

        results[term] = {
            "count": count,
            "domain": domain,
            "explained": explained_count,
            "red": red,
        }
    return results


# ============================================================
# F1：骨架抽取
# ============================================================

def extract_skeleton(text: str) -> dict:
    """从原文抽 F1 骨架（标题/首段/H2 列表/公式数）。"""
    lines = text.split("\n")

    # H1
    h1 = ""
    for line in lines:
        if line.startswith("# "):
            h1 = line.lstrip("# ").strip()
            break

    # 第一段实质性内容（跳过引用块/空行）
    first_para_lines = []
    in_blockquote = False
    for line in lines:
        s = line.strip()
        if s.startswith(">"):
            in_blockquote = True
            continue
        if in_blockquote and not s:
            in_blockquote = False
            continue
        if not in_blockquote and s and not s.startswith("#") and not s.startswith("---"):
            first_para_lines.append(s)
            if len(first_para_lines) >= 2 and len(" ".join(first_para_lines)) > 80:
                break
    first_para = " ".join(first_para_lines)[:300]

    # H2 列表
    h2_list = [line.lstrip("# ").strip() for line in lines if line.startswith("## ")]

    # 公式数量
    formula_inline = len(re.findall(r"\$[^$]+\$", text))
    formula_block = len(re.findall(r"\$\$", text)) // 2

    return {
        "h1": h1,
        "first_para": first_para,
        "h2_list": h2_list[:10],  # 最多 10 个
        "formula_inline": formula_inline,
        "formula_block": formula_block,
    }


# ============================================================
# 生成 .费曼检验.md
# ============================================================

def gen_mandatory_report(src_path: pathlib.Path, skeleton: dict, terms: dict, rel_path: str) -> str:
    """强制类：F1 骨架 + F2 空 + F3 自动 + F4 空。"""
    h1 = skeleton["h1"] or src_path.stem
    red_terms = [(t, info) for t, info in terms.items() if info["red"]]
    other_terms = [(t, info) for t, info in terms.items() if not info["red"] and info["count"] >= 1]
    # 按频次排序
    red_terms.sort(key=lambda x: -x[1]["count"])
    other_terms.sort(key=lambda x: -x[1]["count"])

    lines = [
        f"# 费曼检验 · {h1}",
        f"",
        f"> **自动生成**：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} 由 `feynman-batch.py` 产出。",
        f"> **原文**：[`{rel_path}`](../{rel_path})",
        f"> **类型**：🔴 强制 F1-F4（核心论点文档）",
        f">",
        f"> ⚠️ **F2 / F4 是空表，必须作者本人填**。AI 代写 = 伪造费曼。",
        f">   F1（骨架）和 F3（术语扫描）已自动产出，作者补全 F1 血肉 + 填 F2/F4。",
        f"",
        f"---",
        f"",
        f"## F1 · 外行复述版（12 岁小孩版）🟡 待补",
        f"",
        f"### 自动骨架（作者据此补血肉）",
        f"",
        f"**原文标题**：{h1}",
        f"",
        f"**原文首段摘要**（截 300 字）：",
        f"```",
        f"{skeleton['first_para'] or '（未抽到，可能原文格式特殊）'}",
        f"```",
        f"",
        f"**原文 H2 骨架**（共 {len(skeleton['h2_list'])} 个）：",
    ]
    for i, h2 in enumerate(skeleton["h2_list"], 1):
        lines.append(f"{i}. {h2}")
    lines += [
        f"",
        f"**数学层提示**：原文有 {skeleton['formula_inline']} 个行内公式 + {skeleton['formula_block']} 个块公式。",
        f"",
        f"### 待作者填：外行版核心（不许用任何术语）",
        f"",
        f"```markdown",
        f"**这篇文档的核心一句话**：<1 句话，无术语>",
        f"",
        f"**3 个核心概念的大白话**：",
        f"| 原术语 | 大白话 | 生活类比 |",
        f"|---|---|---|",
        f"| XXX | \"…\" | 例：菜谱/电话簿 |",
        f"",
        f"**12 岁表弟会卡在哪一问？**",
        f"- 卡点 1：…",
        f"```",
        f"",
        f"---",
        f"",
        f"## F2 · 卡壳点清单（作者自曝）🔴 必填",
        f"",
        f"> 🚨 **AI 不可代填**。这是费曼法的灵魂——作者自己暴露写这篇时**没真懂**的地方。",
        f"> 挖不出 ≥1 个卡壳点本身就是 🔴（你在自欺）。",
        f"",
        f"| # | 哪段/论断 | 卡在哪 | 当时怎么绕过 | 真懂吗 |",
        f"|---|---|---|---|---|",
        f"| 1 | _（你填）_ | _（你填）_ | _（你填）_ | 🔴/🟡/🟢 |",
        f"",
        f"**最难回答的 1 个追问**（外行问会哑口无言的）：",
        f"> _（你填。提示：跑 `python3 费曼学习法/feynman-coach.py \"{h1}\"` 让 AI 帮你戳出来）_",
        f"",
        f"---",
        f"",
        f"## F3 · 术语黑名单 {'🔴 '+str(len(red_terms))+' 红灯' if red_terms else '🟢'}（自动）",
        f"",
        f"> 自动扫描结果。🚨 红灯 = 高频（≥3 次）且**无任何解释**的术语，可能掩盖理解空洞。",
        f"",
    ]
    if red_terms:
        lines += [
            f"### 🚨 红灯术语（高频无解释，必须补外行翻译或删段）",
            f"",
            f"| 术语 | 出现次数 | 领域 | 给得出外行翻译吗 |",
            f"|---|---|---|---|",
        ]
        for t, info in red_terms[:20]:
            lines.append(f"| **{t}** | {info['count']} | {info['domain']} | 🔴 待作者填 |")
        lines.append(f"")
    if other_terms:
        lines += [
            f"### 其他出现的黑名单术语（已用但可能有解释）",
            f"",
            f"| 术语 | 出现 | 有解释次数 | 外行翻译 |",
            f"|---|---|---|---|",
        ]
        for t, info in other_terms[:30]:
            mark = "🟢" if info["explained"] else "🟡"
            lines.append(f"| {t} | {info['count']} | {info['explained']} | {mark} 待填 |")
        lines.append(f"")
    if not red_terms and not other_terms:
        lines += [f"_本文未检测到黑名单术语（可能是纯思想/方法论类文档）。_", f""]

    lines += [
        f"---",
        f"",
        f"## F4 · 回炉记录 🔴 必填",
        f"",
        f"> 🚨 **AI 不可代填**。首次写成无回炉 = 🟡（要么真懂罕见，要么跳过自检大概率）。",
        f"",
        f"```markdown",
        f"**v1（初稿）**：<日期>，卡壳点 ___ 个",
        f"**自检发现最大 gap**：<我以我懂其实不懂的事>",
        f"**重学动作**：<读了什么/问了谁/跑了什么代码>",
        f"**v2（当前）**：<日期>，原卡点解决情况：___",
        f"**仍未解决**（移入 advanced/）：<问题>",
        f"```",
        f"",
        f"---",
        f"",
        f"## 发布前自检 5 问",
        f"",
        f"- [ ] Q1：3 句大白话讲核心（无术语）",
        f"- [ ] Q2：列出 ≥1 个卡壳点",
        f"- [ ] Q3：每个术语有外行翻译（看 F3 红灯）",
        f"- [ ] Q4：举出一个反例 / 让本文论断失效的场景",
        f"- [ ] Q5：预测 12 岁连环追问 5 个为什么你会哑在哪",
        f"",
        f"---",
        f"",
        f"_本文件由 `feynman-batch.py` 自动生成。F1 骨架 + F3 术语扫描由脚本负责；_",
        f"_F2 / F4 / F1 血肉 / Q1-Q5 必须作者本人填——这是费曼法不可外包的部分。_",
    ]
    return "\n".join(lines)


def gen_recommended_report(src_path: pathlib.Path, skeleton: dict, terms: dict, rel_path: str) -> str:
    """推荐类：简版（只 F1 骨架 + F3 术语）。"""
    h1 = skeleton["h1"] or src_path.stem
    red_terms = [(t, info) for t, info in terms.items() if info["red"]]
    red_terms.sort(key=lambda x: -x[1]["count"])

    lines = [
        f"# 费曼检验（简版）· {h1}",
        f"",
        f"> 自动生成 {datetime.datetime.now().strftime('%Y-%m-%d %H:%MD')} | 原文 [`{rel_path}`](../{rel_path}) | 类型：🟡 推荐 F1+F3",
        f"",
        f"## F1 外行复述（待补）",
        f"",
        f"**原文核心一句话**：<作者填，1 句无术语>",
        f"",
        f"**H2 骨架**：{'; '.join(skeleton['h2_list'][:5]) or '（无）'}",
        f"",
        f"## F3 术语红灯 {'🔴 '+str(len(red_terms)) if red_terms else '🟢 无'}",
        f"",
    ]
    if red_terms:
        lines.append("| 术语 | 出现 | 领域 |")
        lines.append("|---|---|---|")
        for t, info in red_terms[:15]:
            lines.append(f"| **{t}** | {info['count']} | {info['domain']} |")
    else:
        lines.append("_无高频无解释术语。_")
    lines += [
        "",
        "## F2/F4（推荐但不强制）",
        "",
        "如要深做，复制完整模板：`费曼学习法/费曼检验模板.md`。",
    ]
    return "\n".join(lines)


# ============================================================
# 全局索引生成
# ============================================================

def gen_index(report_root: pathlib.Path, stats: dict, all_red_terms: Counter,
              skipped_paths: list, project_root: pathlib.Path) -> None:
    """生成 _index.md 仪表盘 + _红灯术语总清单.md。"""
    total = stats["total"]
    mandatory = stats["mandatory"]
    recommended = stats["recommended"]
    skip = stats["skip"]
    produced = stats["produced"]
    skipped_existing = stats["skipped_existing"]

    # 仪表盘
    lines = [
        "# 费曼检验 · 全项目仪表盘",
        "",
        f"> 生成于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 项目根：`{project_root}`",
        "",
        "## 总览",
        "",
        "| 指标 | 数量 |",
        "|---|---|",
        f"| 扫描 .md 总数 | **{total}** |",
        f"| 🔴 强制 F1-F4（已产报告） | **{produced['mandatory']}** / {mandatory} |",
        f"| 🟡 推荐 F1+F3（已产简版） | **{produced['recommended']}** / {recommended} |",
        f"| ⏭️ 跳过已存在（保留作者已填）| {skipped_existing} |",
        f"| ⚪ 不适用（索引/清单/访谈）| {skip} |",
        "",
        "## 分类规则回顾",
        "",
        "| 类型 | 范围 | 处理 |",
        "|---|---|---|",
        "| 🔴 强制 | 讲透系列编号文件 / 学科 00-是什么 / 本质探索 / 横向打通 | F1 骨架+F3 自动+F2/F4 空表 |",
        "| 🟡 推荐 | 讲透 AI for 职业 | F1 骨架+F3 简版 |",
        "| ⚪ 不适用 | 前沿与媒体/访谈/论文清单/README/课程索引 | 跳过，记录本表 |",
        "",
        "## 项目级 Top 红灯术语（高频无解释，跨文档）",
        "",
        "> 这些术语在最多文档里被滥用 = 项目级学习清单。",
        "",
        "| 术语 | 出现在多少文档 | 累计频次 | 领域 |",
        "|---|---|---|---|",
    ]
    for term, doc_count in all_red_terms.most_common(30):
        # 找领域
        domain = next((d for t, d in ALL_TERMS if t == term), "?")
        lines.append(f"| **{term}** | {doc_count} 篇 | — | {domain} |")

    lines += [
        "",
        "## 下一步（作者必读）",
        "",
        "1. **F2/F4 必须作者本人填**——AI 代写 = 伪造费曼。这是不可外包的。",
        "2. **跑陪练脚本帮你戳 F2**：`python3 费曼学习法/feynman-coach.py \"<主题>\" --rounds 3`",
        "3. **优先处理 Top 红灯术语**：上表前 10 个 = 项目最该补课的概念。",
        "4. **每个 .费曼检验.md 的 F1 骨架需作者补血肉**——脚本只抽了标题/首段，外行版必须重写。",
        "5. **完成 5 问自检后**才能认为该文档通过费曼检验。",
        "",
        "## 跳过的文档清单（不适用，共 " + str(skip) + " 篇）",
        "",
        "<details><summary>展开查看</summary>",
        "",
    ]
    for p in skipped_paths[:200]:
        lines.append(f"- `{p}`")
    if len(skipped_paths) > 200:
        lines.append(f"- _... 还有 {len(skipped_paths) - 200} 篇_")
    lines += ["", "</details>", ""]
    (report_root / "_index.md").write_text("\n".join(lines), encoding="utf-8")


# ============================================================
# 主流程
# ============================================================

def main():
    ap = argparse.ArgumentParser(description="费曼检验批处理")
    ap.add_argument("--root", default=".", help="项目根（默认当前目录）")
    ap.add_argument("--dry-run", action="store_true", help="只统计分类，不产文件")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的 .费曼检验.md（小心：会清空你填的 F2/F4）")
    ap.add_argument("--only", default="", help="只处理某子目录，如 '讲透基础模型'")
    args = ap.parse_args()

    project_root = pathlib.Path(args.root).resolve()
    if not (project_root / "README.md").exists():
        print(f"⚠️ {project_root} 不像项目根（找不到 README.md）", file=sys.stderr)
        return

    only = args.only.strip()

    # 收集所有 .md（排除 .费曼检验.md 自身，避免嵌套）
    all_mds = []
    for p in project_root.rglob("*.md"):
        rel = p.relative_to(project_root).as_posix()
        if rel.startswith(".git/") or "/.git/" in rel or rel.startswith("费曼学习法/"):
            continue
        if rel.endswith(".费曼检验.md"):
            continue  # 避免把自己当原文处理（嵌套）
        if only and not rel.startswith(only):
            continue
        all_mds.append((p, rel))

    print(f"\n📂 扫描 {project_root}")
    print(f"   共 {len(all_mds)} 个 .md 文件\n")

    # 分类
    stats = {
        "total": len(all_mds),
        "mandatory": 0, "recommended": 0, "skip": 0,
        "produced": {"mandatory": 0, "recommended": 0},
        "skipped_existing": 0,
    }
    all_red_terms = Counter()  # term -> 出现在多少文档
    skipped_paths = []

    report_root = project_root / "费曼学习法" / "检验报告"
    if not args.dry_run:
        report_root.mkdir(parents=True, exist_ok=True)

    for i, (abs_path, rel) in enumerate(all_mds, 1):
        cls = classify(rel)
        stats[cls] += 1

        if cls == "skip":
            skipped_paths.append(rel)
            continue

        if args.dry_run:
            continue

        # 读原文
        try:
            text = abs_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"  ⚠️ 读失败 {rel}: {e}", file=sys.stderr)
            continue

        # 抽骨架 + 术语
        skeleton = extract_skeleton(text)
        terms = scan_terms(text)

        # 累计红灯术语
        for t, info in terms.items():
            if info["red"]:
                all_red_terms[t] += 1

        # 目标文件（旁置）
        out_path = abs_path.with_suffix(".md.费曼检验.md")  # 原文.md → 原文.md.费曼检验.md
        # 更优雅：原文.md → 原文.费曼检验.md
        out_path = abs_path.with_name(abs_path.stem + ".费曼检验.md")

        if out_path.exists() and not args.force:
            stats["skipped_existing"] += 1
            continue

        # 生成
        if cls == "mandatory":
            content = gen_mandatory_report(abs_path, skeleton, terms, rel)
        else:
            content = gen_recommended_report(abs_path, skeleton, terms, rel)

        out_path.write_text(content, encoding="utf-8")
        stats["produced"][cls] += 1

        if i % 30 == 0:
            print(f"   进度 {i}/{len(all_mds)}")

    # 输出统计
    print(f"\n{'='*60}")
    print(f"  分类统计" + ("（DRY-RUN，未产文件）" if args.dry_run else ""))
    print(f"{'='*60}")
    print(f"  📋 扫描总数      : {stats['total']}")
    print(f"  🔴 强制 F1-F4    : {stats['mandatory']}")
    print(f"  🟡 推荐 F1+F3    : {stats['recommended']}")
    print(f"  ⚪ 不适用        : {stats['skip']}")
    if not args.dry_run:
        print(f"  ✅ 已产强制报告  : {stats['produced']['mandatory']}")
        print(f"  ✅ 已产推荐简版  : {stats['produced']['recommended']}")
        print(f"  ⏭️ 跳过已存在   : {stats['skipped_existing']}（保留作者已填的 F2/F4）")

    if not args.dry_run:
        gen_index(report_root, stats, all_red_terms, skipped_paths, project_root)
        print(f"\n  📊 仪表盘：{report_root / '_index.md'}")
        print(f"  📊 共处理 {stats['produced']['mandatory'] + stats['produced']['recommended']} 篇\n")


if __name__ == "__main__":
    main()
