#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
multi-lens-batch.py — 多元视角审视（6 视角启发式批处理）

对 312 强制/推荐文档跑 6 个互补视角，产 <原名>.多视角.md：
  1. 第一性原理：假设/推导链
  2. 布鲁姆 6 层：认知层级动词
  3. 图尔敏论证：6 元素完整性
  4. 红队：强论断/反例覆盖
  5. 系统论：反馈环/涌现/杠杆点
  6. 跨学科类比：类比强度

每视角产一段：🤖 启发式扫描 + 作者必答问题。

用法:
  python3 multi-lens-batch.py --dry-run
  python3 multi-lens-batch.py
  python3 multi-lens-batch.py --only "讲透基础模型"
  python3 multi-lens-batch.py --lens first_principles,red_team
"""

from __future__ import annotations
import sys
import re
import pathlib
import argparse
import datetime
import importlib.util

_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("fb", _HERE / "feynman-batch.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
classify = _mod.classify
extract_skeleton = _mod.extract_skeleton


# ============================================================
# 视角 1：第一性原理
# ============================================================

ASSUMPTION_MARKERS = ["假设", "前提", "基于", "根据", "假定", "在...基础上",
                      "建立在", "依赖于", "基于这样", "if", "假设有"]
INFERENCE_MARKERS = ["因此", "所以", "故", "由此", "从而", "推出", "推导",
                     "可得", "证明了", "导致", "表明", "可见"]


def lens_first_principles(text: str) -> dict:
    assumptions = []
    for m in ASSUMPTION_MARKERS:
        for match in re.finditer(re.escape(m), text):
            ctx = text[max(0, match.start()-20): match.start()+60]
            assumptions.append({"marker": m, "context": ctx.strip()[:80]})
    inferences = []
    for m in INFERENCE_MARKERS:
        for match in re.finditer(re.escape(m), text):
            ctx = text[max(0, match.start()-20): match.start()+60]
            inferences.append({"marker": m, "context": ctx.strip()[:80]})

    return {
        "name": "第一性原理（First Principles）",
        "emoji": "🧱",
        "headline": f"显式假设 {len(assumptions)} 处 / 推导连词 {len(inferences)} 处",
        "auto_findings": {
            "assumptions_sample": assumptions[:5],
            "inferences_count": len(inferences),
        },
        "author_questions": [
            "🤖 启发式抓到的'假设'词，是真假设还是修辞性'基于'？逐条确认。",
            "本文的**最底层假设**是什么？能再往下一层吗？（如：NTP 假设语言有规律 → 规律假设世界有结构 → 结构假设...？）",
            f"推导链有 {len(inferences)} 个'因此/所以'——最弱的一环是哪？",
            "如果底层假设不成立，结论还成立吗？给一个反事实场景。",
        ],
    }


# ============================================================
# 视角 2：布鲁姆 6 层
# ============================================================

BLOOM_LEVELS = {
    "记忆": ["记住", "列出", "定义", "识别", "回忆", "命名", "罗列"],
    "理解": ["解释", "总结", "描述", "阐述", "说明", "概括", "转述"],
    "应用": ["应用", "使用", "计算", "演示", "执行", "实现", "操作"],
    "分析": ["比较", "分析", "对比", "区分", "拆解", "分解", "归类"],
    "评价": ["评价", "批判", "辩护", "判断", "评估", "审视", "反思"],
    "创造": ["创造", "设计", "构建", "生成", "提出", "发明", "构建"],
}


def lens_bloom(text: str) -> dict:
    counts = {}
    for level, verbs in BLOOM_LEVELS.items():
        c = sum(len(re.findall(re.escape(v), text)) for v in verbs)
        counts[level] = c
    total = sum(counts.values()) or 1
    dominant = max(counts, key=counts.get)

    return {
        "name": "布鲁姆 6 层（Bloom's Taxonomy）",
        "emoji": "📊",
        "headline": f"动词分布：{'/'.join(f'{k}{v}' for k, v in counts.items())}，主导层 = {dominant}",
        "auto_findings": {
            "counts": counts,
            "dominant": dominant,
            "dominant_pct": round(100 * counts[dominant] / total),
        },
        "author_questions": [
            f"🤖 启发式说主导层是「{dominant}」（{counts[dominant]}次）——这是该文档的合适层级吗？",
            "教程类文档应该**引导读者从记忆→创造**爬升——本文停在分析/评价了吗，还是只描述？",
            "如果你期望读者读完本文能**创造/设计**什么？本文给了足够脚手架吗？",
            "**评价层**动词（批判/反思/判断）出现少 = 文档可能缺批判性——回看费曼 F2 卡壳点。",
        ],
    }


# ============================================================
# 视角 3：图尔敏论证
# ============================================================

TOULMIN_MARKERS = {
    "claim": [r"因此", r"所以", r"结论", r"故", r"可见"],
    "data": [r"实验", r"数据", r"测量", r"观察", r"\d+%", r"\d+\.\d+", r"参数量"],
    "warrant": [r"因为", r"由于", r"根据.{0,10}原理", r"基于.{0,10}规律"],
    "backing": [r"研究表?明", r"理论指?出", r"经典.{0,10}理论", r"\w{2,8}\s*[\(（]\d{4}[\)）]"],
    "qualifier": [r"通常", r"一般", r"在.{0,15}情况下", r"多数", r"大部分"],
    "rebuttal": [r"然而", r"但是", r"尽管", r"反例", r"例外", r"不过"],
}


def lens_toulmin(text: str) -> dict:
    elements = {}
    for elem, patterns in TOULMIN_MARKERS.items():
        c = sum(len(re.findall(p, text)) for p in patterns)
        elements[elem] = c
    missing = [e for e, c in elements.items() if c == 0]

    return {
        "name": "图尔敏论证（Toulmin Model）",
        "emoji": "⚖️",
        "headline": f"6 元素：主张{elements['claim']}/数据{elements['data']}/保证{elements['warrant']}/支撑{elements['backing']}/限定{elements['qualifier']}/反驳{elements['rebuttal']}",
        "auto_findings": {
            "elements": elements,
            "missing": missing,
        },
        "author_questions": [
            f"🤖 启发式说**缺失元素**：{missing if missing else '（看似完整，但需作者确认是否真有）'}",
            "**主张（Claim）**：本文的核心论断用一句话能讲清吗？（看费曼 F1）",
            "**数据（Data）**：每个主张都有具体数字/实验/引用支撑吗？",
            "**反驳（Rebuttal）**：作者主动考虑了反例吗？还是只摆正面证据？这往往是文档最弱的元素。",
            "**限定（Qualifier）**：论断的适用边界清楚吗？还是过度泛化（看红队视角）？",
        ],
    }


# ============================================================
# 视角 4：红队
# ============================================================

REDTEAM_STRONG = ["显然", "必然", "一定", "绝对", "永远", "不可能", "始终", "毫无疑问", "证明"]
REDTEAM_GENERALIZATION = ["所有", "任何", "每", "全部", "从不", "总是"]


def lens_redteam(text: str) -> dict:
    strong_claims = []
    for m in REDTEAM_STRONG:
        for match in re.finditer(re.escape(m), text):
            ctx = text[max(0, match.start()-15): match.start()+50].replace("\n", " ")
            strong_claims.append({"marker": m, "context": ctx.strip()[:70]})
    generalizations = sum(len(re.findall(re.escape(m), text)) for m in REDTEAM_GENERALIZATION)
    rebuttal_count = len(re.findall(r"然而|但是|反例|例外", text))

    return {
        "name": "红队（Red Team）",
        "emoji": "🔴",
        "headline": f"强论断 {len(strong_claims)} 处 / 过度泛化词 {generalizations} / 主动反驳 {rebuttal_count} 处",
        "auto_findings": {
            "strong_claims_sample": strong_claims[:5],
            "generalizations": generalizations,
            "rebuttal_count": rebuttal_count,
        },
        "author_questions": [
            f"🤖 抓到 {len(strong_claims)} 处强论断——**最脆弱的 1 个**是哪个？如果是红队，你怎么攻它？",
            f"过度泛化词（所有/任何/从不）出现 {generalizations} 次——每个都站得住吗？",
            f"主动反驳（然而/反例）只出现 {rebuttal_count} 次——作者**主动考虑反例**了吗？",
            "**红队最想攻的一个论断**：____（用一句话写它的攻击点）",
        ],
    }


# ============================================================
# 视角 5：系统论
# ============================================================

SYSTEMS_FEEDBACK = ["导致", "引起", "反过来", "进而", "从而", "使得", "促使", "反馈"]
SYSTEMS_EMERGENCE = ["涌现", "突现", "整体大于", "不可还原", "整体性质"]
SYSTEMS_LEVERAGE = ["杠杆", "关键点", "干预点", "症结", "突破口", "转折点"]


def lens_systems(text: str) -> dict:
    feedback = sum(len(re.findall(re.escape(m), text)) for m in SYSTEMS_FEEDBACK)
    emergence = sum(len(re.findall(re.escape(m), text)) for m in SYSTEMS_EMERGENCE)
    leverage = sum(len(re.findall(re.escape(m), text)) for m in SYSTEMS_LEVERAGE)

    return {
        "name": "系统论（Systems Thinking）",
        "emoji": "🌀",
        "headline": f"反馈词 {feedback} / 涌现词 {emergence} / 杠杆点词 {leverage}",
        "auto_findings": {
            "feedback": feedback,
            "emergence": emergence,
            "leverage": leverage,
        },
        "author_questions": [
            f"🤖 反馈环词出现 {feedback} 次——本文描述的对象有**反馈环**吗？是正反馈（强化）还是负反馈（平衡）？",
            f"涌现词出现 {emergence} 次——如果有涌现，**微观规则到宏观现象**的桥是什么？（这是最难的）",
            f"杠杆点词出现 {leverage} 次——作者指出了**最有效的干预位置**吗？还是只描述现象？",
            "本文是**线性因果**叙事还是**系统反馈**叙事？前者容易误导。",
        ],
    }


# ============================================================
# 视角 6：跨学科类比
# ============================================================

ANALOGY_MARKERS = ["像", "类似", "如同", "好比", "类似于", "相当于", "可以看作",
                   "analogous", "like", "similar to", "as if"]


def lens_analogy(text: str) -> dict:
    analogies = []
    for m in ANALOGY_MARKERS:
        for match in re.finditer(re.escape(m), text):
            ctx = text[max(0, match.start()-15): match.start()+80].replace("\n", " ")
            analogies.append({"marker": m, "context": ctx.strip()[:90]})
    return {
        "name": "跨学科类比（Cross-Disciplinary Analogy）",
        "emoji": "🌉",
        "headline": f"类比词出现 {len(analogies)} 次",
        "auto_findings": {
            "analogies_sample": analogies[:6],
        },
        "author_questions": [
            f"🤖 抓到 {len(analogies)} 个类比——逐个问：类比对象 Y 在**原领域**有严格定义吗？还是模糊修辞？",
            "**类比失效边界**：每个类比在哪个点上不再成立？（如：把神经网络比作大脑——失效在'反向传播'，大脑没有）",
            "本文**最强的类比**是哪个？**最弱**的（容易误导）是哪个？",
            "如果删掉所有类比，本文的论证还成立吗？还是依赖类比撑场？",
        ],
    }


# ============================================================
# 视角注册表
# ============================================================

LENSES = {
    "first_principles": lens_first_principles,
    "bloom": lens_bloom,
    "toulmin": lens_toulmin,
    "red_team": lens_redteam,
    "systems": lens_systems,
    "analogies": lens_analogy,
}


# ============================================================
# 报告生成
# ============================================================

def gen_multi_lens_report(src_path: pathlib.Path, text: str, rel: str,
                          selected_lenses: list) -> str:
    skeleton = extract_skeleton(text)
    h1 = skeleton["h1"] or src_path.stem

    lines = [
        f"# 多元视角审视 · {h1}",
        "",
        f"> 自动生成 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | 原文 [`{rel}`](../{rel})",
        f"> 视角数：{len(selected_lenses)}（费曼视角见 `<同名>.费曼检验.md`）",
        f">",
        f"> ⚠️ 每个视角分两部分：**🤖 启发式扫描**（自动）+ **作者必答问题**（不可外包）。",
        f"> 启发式只抓表面特征（如术语密度、动词词频），判断质量须作者本人。",
        "",
        "---",
        "",
        "## 视角速览",
        "",
        "| # | 视角 | 自动扫描结论 |",
        "|---|---|---|",
    ]

    results = []
    for i, key in enumerate(selected_lenses, 1):
        fn = LENSES[key]
        r = fn(text)
        results.append(r)
        lines.append(f"| {i} | {r['emoji']} {r['name']} | {r['headline']} |")

    lines += ["", "---", ""]

    for i, r in enumerate(results, 1):
        lines += [
            f"## 视角 {i} · {r['emoji']} {r['name']}",
            "",
            f"**🤖 自动扫描**：{r['headline']}",
            "",
        ]
        # auto findings 详情
        af = r["auto_findings"]
        if "assumptions_sample" in af and af["assumptions_sample"]:
            lines.append("**抓到的'假设'样本（前 5）**：")
            for a in af["assumptions_sample"]:
                lines.append(f"- `{a['marker']}`: {a['context']}")
            lines.append("")
        if "counts" in af:
            lines.append("**布鲁姆动词分布**：")
            for level, c in af["counts"].items():
                bar = "█" * min(c, 20)
                lines.append(f"- {level}: {c}  {bar}")
            lines.append("")
        if "elements" in af:
            lines.append("**图尔敏 6 元素**：")
            elem_label = {"claim": "主张", "data": "数据", "warrant": "保证",
                          "backing": "支撑", "qualifier": "限定", "rebuttal": "反驳"}
            for e, c in af["elements"].items():
                mark = "🟢" if c > 0 else "🔴"
                lines.append(f"- {mark} {elem_label[e]}：{c}")
            if af["missing"]:
                lines.append(f"- ⚠️ **缺失**：{[elem_label[m] for m in af['missing']]}")
            lines.append("")
        if "strong_claims_sample" in af and af["strong_claims_sample"]:
            lines.append("**强论断样本（前 5）**：")
            for s in af["strong_claims_sample"]:
                lines.append(f"- `{s['marker']}`: {s['context']}")
            lines.append("")
        if "analogies_sample" in af and af["analogies_sample"]:
            lines.append("**类比样本（前 6）**：")
            for a in af["analogies_sample"]:
                lines.append(f"- `{a['marker']}`: {a['context']}")
            lines.append("")

        # author questions
        lines.append("**✍️ 作者必答（启发式不能答）**：")
        for q in r["author_questions"]:
            lines.append(f"{q}")
        lines += ["", "---", ""]

    lines += [
        "## 7 视角汇总（含费曼）",
        "",
        "**7 视角清单**：",
        "",
        "- 费曼学习法 → 外行能懂吗？术语偷懒？（见 `.费曼检验.md`）",
        "- 第一性原理 → 拆到公理重推？假设链？",
        "- 布鲁姆 6 层 → 认知层级？停在哪层？",
        "- 图尔敏论证 → 论证 6 元素完整？",
        "- 红队 → 最脆弱论断？反例？",
        "- 系统论 → 反馈环？涌现？杠杆点？",
        "- 跨学科类比 → 类比强度？失效边界？",
        "",
        "**真懂 = 7 视角都过关**。任何一视角不过关 = 该维度的盲区。",
        "",
        "---",
        "_由 `multi-lens-batch.py` 生成。启发式部分自动；判断质量必须作者本人。_",
    ]
    return "\n".join(lines)


# ============================================================
# 主流程
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="只处理某子目录")
    ap.add_argument("--lens", default="",
                    help="逗号分隔视角 key（默认全部）")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    project_root = pathlib.Path(args.root).resolve()
    only = args.only.strip()

    if args.lens:
        selected = [k.strip() for k in args.lens.split(",") if k.strip() in LENSES]
    else:
        selected = list(LENSES.keys())

    # 扫描
    all_mds = []
    for p in project_root.rglob("*.md"):
        rel = p.relative_to(project_root).as_posix()
        if rel.startswith(".git/") or "/.git/" in rel or rel.startswith("费曼学习法/"):
            continue
        if rel.endswith(".费曼检验.md") or rel.endswith(".多视角.md"):
            continue
        if only and not rel.startswith(only):
            continue
        all_mds.append((p, rel))

    print(f"\n🔍 扫描 {len(all_mds)} 文档 | 视角：{', '.join(selected)}")
    print(f"   模式：{'DRY-RUN' if args.dry_run else '生产'}\n")

    produced = 0
    skipped = 0
    failed = 0

    for i, (abs_path, rel) in enumerate(all_mds, 1):
        cls = classify(rel)
        # 只对强制/推荐做（不适用文档不产多视角）
        if cls == "skip":
            continue

        out_path = abs_path.with_name(abs_path.stem + ".多视角.md")
        if out_path.exists() and not args.force:
            skipped += 1
            continue

        try:
            text = abs_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            failed += 1
            continue

        if args.dry_run:
            produced += 1
            continue

        try:
            content = gen_multi_lens_report(abs_path, text, rel, selected)
            out_path.write_text(content, encoding="utf-8")
            produced += 1
        except Exception as e:
            print(f"  ⚠️ {rel}: {e}", file=sys.stderr)
            failed += 1

        if i % 50 == 0:
            print(f"   进度 {i}/{len(all_mds)}")

    print(f"\n{'='*60}")
    print(f"  多视角审视批处理" + ("（DRY-RUN）" if args.dry_run else ""))
    print(f"{'='*60}")
    print(f"  📋 扫描         : {len(all_mds)}")
    print(f"  ✅ 产 .多视角.md : {produced}")
    print(f"  ⏭️ 跳过已存在   : {skipped}")
    print(f"  ❌ 失败         : {failed}")
    print()


if __name__ == "__main__":
    main()
