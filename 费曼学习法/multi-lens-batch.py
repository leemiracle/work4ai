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
from multiprocessing import Pool, cpu_count
from collections import Counter

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
# 视角 7：Paul-Elder 思维标准（8 元素）
# ============================================================

PE_STANDARDS = {
    "清晰": ["明确", "即指", "就是指", "例子", "比如"],
    "准确": ["精确", "测量", "数据点", "具体值"],
    "精确": ["恰好", "正好", "等于", "±", "误差"],
    "相关": ["相关", "联系", "有关", "涉及"],
    "深度": ["因为", "由于", "原因", "本质", "为什么"],
    "广度": ["另一方面", "不同视角", "其他观点", "从.{0,5}看"],
    "逻辑": ["因此", "故", "推导", "推出", "所以"],
    "公平": ["然而", "但是", "反例", "尽管", "批评"],
}


def lens_paul_elder(text: str) -> dict:
    counts = {k: sum(len(re.findall(p, text)) for p in vs) for k, vs in PE_STANDARDS.items()}
    weak = [k for k, v in counts.items() if v == 0]
    return {
        "name": "Paul-Elder 思维标准（8 元素）",
        "emoji": "🎯",
        "headline": f"8 标准覆盖 {sum(1 for v in counts.values() if v > 0)}/8，弱项 = {weak or '无明显'}",
        "auto_findings": {
            "summary": [f"{k}: {v} 次" for k, v in counts.items()]
                       + ([f"⚠️ 弱项: {', '.join(weak)}"] if weak else []),
        },
        "author_questions": [
            f"🤖 启发式说弱项是 {weak or '无明显弱项'}——作者复核每项是否真弱",
            "**清晰度**：每个核心概念都有例子吗？",
            "**深度**：是描述表面还是追问'为什么'？",
            "**广度**：考虑了不同视角吗？还是单一立场？",
            "**公平性**：公平对待反方观点吗？还是 strawman？",
        ],
    }


# ============================================================
# 视角 8：Popper 可证伪性
# ============================================================

def lens_popper(text: str) -> dict:
    soft = ["可能", "也许", "似乎", "大致", "或许", "大约", "看起来"]
    soft_count = sum(len(re.findall(re.escape(s), text)) for s in soft)
    hard_pred = len(re.findall(r"\d+\.?\d*\s*[%％]", text))
    specific_cond = len(re.findall(r"如果.{0,30}则|当.{0,20}时|若.{0,20}则", text))
    return {
        "name": "Popper 可证伪性",
        "emoji": "🔬",
        "headline": f"软论断词 {soft_count} / 具体百分比 {hard_pred} / 条件预测 {specific_cond}",
        "auto_findings": {
            "summary": [
                f"软论断（可能/也许/似乎）: {soft_count} 次",
                f"具体百分比/数字: {hard_pred} 次",
                f"条件预测（如果X则Y）: {specific_cond} 次",
            ],
        },
        "author_questions": [
            "🤖 软论断多 = 不可证伪——本文的核心论断能被实验证伪吗？",
            "把每个论断改写成'如果 X 则 Y'——能改写的才算科学论断",
            "**最不可证伪的论断**：____（写出来，问'什么证据能让你改变想法'）",
            "答不出'什么证据能证伪' = 这个论断是修辞不是科学",
        ],
    }


# ============================================================
# 视角 9：DIKW 层级
# ============================================================

DIKW_MARKERS = {
    "Data": [r"测量", r"数据", r"数字", r"记录"],
    "Information": [r"关系", r"相关", r"连接", r"关联", r"映射"],
    "Knowledge": [r"模式", r"规律", r"原理", r"理论", r"解释"],
    "Wisdom": [r"判断", r"应用", r"伦理", r"意义", r"应该", r"价值"],
}


def lens_dikw(text: str) -> dict:
    counts = {k: sum(len(re.findall(p, text)) for p in vs) for k, vs in DIKW_MARKERS.items()}
    total = sum(counts.values()) or 1
    dominant = max(counts, key=counts.get)
    return {
        "name": "DIKW 层级（Data/Information/Knowledge/Wisdom）",
        "emoji": "🔺",
        "headline": f"D{counts['Data']}/I{counts['Information']}/K{counts['Knowledge']}/W{counts['Wisdom']}，主导 = {dominant}",
        "auto_findings": {
            "summary": [f"{k}: {v}（{round(100*v/total)}%）" for k, v in counts.items()],
        },
        "author_questions": [
            f"🤖 主导层是 {dominant}——本文停在数据罗列还是到了智慧/判断？",
            "**升级问题**：停在 Data 能否抽 Information？停在 Knowledge 能否到 Wisdom？",
            "**Wisdom 层**：本文有讨论'应该怎样'（伦理/价值）吗？",
        ],
    }


# ============================================================
# 视角 10：因果 vs 相关（Pearl）
# ============================================================

def lens_causality(text: str) -> dict:
    causal = sum(len(re.findall(p, text)) for p in [r"导致", r"引起", r"造成", r"使得", r"促使"])
    corr = sum(len(re.findall(p, text)) for p in [r"相关", r"有关", r"联系到"])
    inter = len(re.findall(r"随机对照|RCT|do\(|干预|反事实|实验组", text))
    return {
        "name": "因果 vs 相关（Pearl）",
        "emoji": "🔗",
        "headline": f"因果声明 {causal} / 相关声明 {corr} / 干预讨论 {inter}",
        "auto_findings": {
            "summary": [
                f"因果动词（导致/引起）: {causal} 次",
                f"相关动词（相关/有关）: {corr} 次",
                f"干预讨论（RCT/do/反事实）: {inter} 次",
            ],
        },
        "author_questions": [
            f"🤖 因果声明 {causal} 处但干预讨论只 {inter}——多数'导致'是观察相关冒充因果",
            "每个'X 导致 Y'问：有 RCT/自然实验吗？还是观察相关？",
            "**最强因果论断**：____（写出来，问'反事实是什么'）",
            "Pearl do-calculus：do(X) vs see(X) 区分清楚了吗？",
        ],
    }


# ============================================================
# 视角 11：机制可解释性
# ============================================================

def lens_mechinterp(text: str) -> dict:
    why = len(re.findall(r"为什么|为何|何以", text))
    how = len(re.findall(r"如何|怎么|怎样", text))
    mech = sum(len(re.findall(p, text)) for p in [r"机制", r"原理", r"电路", r"特征", r"探测", r"归因"])
    blackbox = len(re.findall(r"黑箱|黑盒|black\s*box|不可解释|不透明", text))
    return {
        "name": "机制可解释性",
        "emoji": "🔍",
        "headline": f"'为什么' {why} / '如何' {how} / 机制词 {mech} / 黑箱讨论 {blackbox}",
        "auto_findings": {
            "summary": [
                f"'为什么'类追问: {why} 次",
                f"'如何'类描述: {how} 次",
                f"机制词（机制/原理/电路/特征）: {mech} 次",
                f"黑箱讨论: {blackbox} 次",
            ],
        },
        "author_questions": [
            "🤖 机制词密度反映'解释力'——本文是预测性（黑箱）还是解释性（机制）？",
            "**最强黑箱声明**：'模型能 X 但不知道为什么'——作者讨论了吗？",
            "**电路/特征层面**：本文有没有分解到具体机制？",
        ],
    }


# ============================================================
# 视角 12：Cynefin 框架（4 问题域）
# ============================================================

def lens_cynefin(text: str) -> dict:
    simple = len(re.findall(r"最佳实践|SOP|标准流程|规范|protocol", text))
    complicated = len(re.findall(r"专家分析|建模分析|良好实践", text))
    complex_ = len(re.findall(r"涌现|probe|复杂适应|不可预测|非线性", text))
    chaotic = len(re.findall(r"危机|紧急|混沌|chaos|act.sense", text))
    return {
        "name": "Cynefin 框架（4 问题域）",
        "emoji": "🌐",
        "headline": f"简单 {simple} / 繁杂 {complicated} / 复杂 {complex_} / 混沌 {chaotic}",
        "auto_findings": {
            "summary": [
                f"简单域（最佳实践）: {simple}",
                f"繁杂域（专家分析）: {complicated}",
                f"复杂域（涌现/Probe）: {complex_}",
                f"混沌域（危机）: {chaotic}",
            ],
        },
        "author_questions": [
            "🤖 本文处理的问题在哪个域？方法匹配吗？",
            "**常见错误**：用简单域方法（SOP）处理复杂域问题——本文犯了吗？",
            "**AI 主题**：训练是繁杂域，部署是复杂域，对齐是混沌域——本文区分了吗？",
        ],
    }


# ============================================================
# 视角 13：MECE（互斥穷尽）
# ============================================================

def lens_mece(text: str) -> dict:
    lists = len(re.findall(r"(?:[一二三四五六七八九十]+|[1234567890]+)[、.]\s*\S", text))
    not_exh = len(re.findall(r"等等|之类|以及其他|等等等", text))
    return {
        "name": "MECE（互斥穷尽）",
        "emoji": "🔀",
        "headline": f"分类项 {lists} / 不穷尽信号 {not_exh}",
        "auto_findings": {
            "summary": [
                f"分类列表项: {lists}",
                f"'等等/之类'（不穷尽信号）: {not_exh}",
            ],
        },
        "author_questions": [
            f"🤖 抓到 {lists} 个分类项——逐个问：互斥吗？穷尽吗？",
            f"'等等/之类'出现 {not_exh} 次——作者是否在逃避穷尽性？",
            "**最强分类**：本文最重要的一个分类，能严格证明互斥穷尽吗？",
        ],
    }


# ============================================================
# 视角 14：黄金圈（Sinek Why/How/What）
# ============================================================

def lens_golden_circle(text: str) -> dict:
    lines = text.split("\n")
    intro = " ".join(lines[:30])
    why = len(re.findall(r"为什么|为何|为了|目的|意义|动机", intro))
    how = len(re.findall(r"如何|方法|步骤|怎么做", intro))
    what = len(re.findall(r"是什么|定义|内容|清单|包括", intro))
    return {
        "name": "黄金圈（Sinek Why/How/What）",
        "emoji": "🟡",
        "headline": f"开头 30 行：Why {why} / How {how} / What {what}",
        "auto_findings": {
            "summary": [
                f"开头 Why 词（动机）: {why}",
                f"开头 How 词（方法）: {how}",
                f"开头 What 词（内容）: {what}",
            ],
        },
        "author_questions": [
            "🤖 本文是从 Why（为什么讨论这个）还是 What（定义/列表）开始？",
            "**Sinek 论点**：好文档应从 Why 开始——本文符合吗？",
            "如果从 What 开始：能否把 Why 提到开头？",
        ],
    }


# ============================================================
# 视角 15：认知负荷（Sweller）
# ============================================================

def lens_cognitive_load(text: str) -> dict:
    lines = text.split("\n")
    h_levels = [len([l for l in lines if l.startswith("#" * i + " ")]) for i in range(1, 5)]
    avg_line_len = sum(len(l) for l in lines) / max(len(lines), 1)
    formula_density = len(re.findall(r"\$\$", text)) // 2
    long_lists = len([l for l in lines if re.match(r"^\s*[\-\*\+]\s", l)])
    max_depth = max((i for i, c in enumerate(h_levels, 1) if c > 0), default=0)
    return {
        "name": "认知负荷（Sweller）",
        "emoji": "🧩",
        "headline": f"嵌套深度 {max_depth} / 平均行长 {avg_line_len:.0f} / 块公式 {formula_density}",
        "auto_findings": {
            "summary": [
                f"标题层级 H1/H2/H3/H4: {h_levels}",
                f"平均行长: {avg_line_len:.0f} 字",
                f"块公式: {formula_density}",
                f"列表项: {long_lists}",
            ],
        },
        "author_questions": [
            f"🤖 嵌套深度 = {max_depth} 层——超过 3 层认知负荷高",
            f"平均行长 {avg_line_len:.0f}——超过 100 字建议拆句",
            "公式密度高 = 内在负荷高，需要更多解释",
        ],
    }


# ============================================================
# 视角 16：不确定性与校准
# ============================================================

def lens_calibration(text: str) -> dict:
    hedging = sum(len(re.findall(p, text)) for p in [r"可能", r"大约", r"估计", r"似乎", r"或许", r"约"])
    confident = sum(len(re.findall(p, text)) for p in [r"必然", r"一定", r"绝对", r"毫无疑问", r"证明"])
    ci = len(re.findall(r"\d+\s*[%％]|置信区间|CI|p\s*[<>=]", text))
    ratio = hedging / max(confident, 1)
    return {
        "name": "不确定性与校准",
        "emoji": "📉",
        "headline": f"Hedging {hedging} / 自信词 {confident} / 比 {ratio:.1f}:1 / 置信数字 {ci}",
        "auto_findings": {
            "summary": [
                f"含糊词（可能/大约）: {hedging}",
                f"自信词（必然/一定）: {confident}",
                f"hedging:confident 比: {ratio:.1f}:1",
                f"具体置信度（%/CI/p<）: {ci}",
            ],
        },
        "author_questions": [
            f"🤖 hedging:confident = {ratio:.1f}:1（>3:1 过度含糊，<0.5:1 过度自信）",
            "好文档应该 hedging 适度 + 有具体置信度数字——本文有吗？",
            "**过度自信论断**：哪个最该加'约/大概'？",
            "**过度含糊论断**：哪个最该给具体数字？",
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
    "paul_elder": lens_paul_elder,
    "popper": lens_popper,
    "dikw": lens_dikw,
    "causality": lens_causality,
    "mechinterp": lens_mechinterp,
    "cynefin": lens_cynefin,
    "mece": lens_mece,
    "golden_circle": lens_golden_circle,
    "cognitive_load": lens_cognitive_load,
    "calibration": lens_calibration,
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
        # 通用 summary 兜底（新 10 视角用 summary 字段）
        if "summary" in af:
            lines.append("**自动统计**：")
            for s in af["summary"]:
                lines.append(f"- {s}")
            lines.append("")

        # author questions
        lines.append("**✍️ 作者必答（启发式不能答）**：")
        for q in r["author_questions"]:
            lines.append(f"{q}")
        lines += ["", "---", ""]

    lines += [
        "## 17 视角汇总（含费曼）",
        "",
        "**17 视角清单**：",
        "",
        "**核心 7 视角**：",
        "- 费曼学习法 → 外行能懂吗？术语偷懒？（见 `.费曼检验.md`）",
        "- 第一性原理 → 拆到公理重推？假设链？",
        "- 布鲁姆 6 层 → 认知层级？停在哪层？",
        "- 图尔敏论证 → 论证 6 元素完整？",
        "- 红队 → 最脆弱论断？反例？",
        "- 系统论 → 反馈环？涌现？杠杆点？",
        "- 跨学科类比 → 类比强度？失效边界？",
        "",
        "**扩展 10 视角**：",
        "- Paul-Elder 8 标准 → 清晰/准确/深度/广度/逻辑/公平？",
        "- Popper 可证伪 → 论断能被实验证伪吗？",
        "- DIKW 层级 → 停在 Data 还是到 Wisdom？",
        "- 因果 vs 相关 → '导致'有 RCT 支撑吗？",
        "- 机制可解释性 → 黑箱还是机制？",
        "- Cynefin 框架 → 问题在简单/繁杂/复杂/混沌哪域？",
        "- MECE → 分类互斥穷尽吗？",
        "- 黄金圈 → 从 Why 还是 What 开始？",
        "- 认知负荷 → 嵌套深度/行长/公式密度？",
        "- 不确定性校准 → hedging/confident 比例？",
        "",
        "**真懂 = 17 视角都过关**。任何一视角不过关 = 该维度的盲区。",
        "",
        "---",
        "_由 `multi-lens-batch.py` 生成。启发式部分自动；判断质量必须作者本人。_",
    ]
    return "\n".join(lines)


# ============================================================
# 主流程
# ============================================================

def _worker(task):
    """并行 worker：处理单个文档。返回 status 字符串。Linux fork 模式可继承全局函数。"""
    abs_path_str, rel, selected, force, dry_run = task
    abs_path = pathlib.Path(abs_path_str)
    cls = classify(rel)
    if cls == "skip":
        return "skip"
    out_path = abs_path.with_name(abs_path.stem + ".多视角.md")
    if out_path.exists() and not force:
        return "skipped"
    try:
        text = abs_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "failed"
    if dry_run:
        return "produced"
    try:
        content = gen_multi_lens_report(abs_path, text, rel, selected)
        out_path.write_text(content, encoding="utf-8")
        return "produced"
    except Exception:
        return "failed"


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

    # 准备并行任务（加大并行度）
    tasks = [(str(p), rel, selected, args.force, args.dry_run) for p, rel in all_mds]
    n_proc = min(cpu_count(), 16)
    print(f"   并行度: {n_proc} 进程（{len(tasks)} 任务）\n")

    results = []
    with Pool(n_proc) as pool:
        for i, result in enumerate(pool.imap_unordered(_worker, tasks), 1):
            results.append(result)
            if i % 100 == 0:
                print(f"   进度 {i}/{len(tasks)}")

    stats = Counter(results)
    produced = stats.get("produced", 0)
    skipped = stats.get("skipped", 0)
    failed = stats.get("failed", 0)

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
