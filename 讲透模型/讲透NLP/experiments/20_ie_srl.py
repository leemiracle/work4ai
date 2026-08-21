#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · Ch20 信息抽取与语义角色标注 · 配套实验
================================================
SLP3 Ch20 (Information Extraction) + Ch21 (Semantic Role Labeling) 的可跑佐证。

本实验做三件事：
  PART A  关系抽取：规则模板 baseline vs "模拟 LLM few-shot" 抽取器
          —— 反直觉发现：在窄领域小数据集上，几条手写规则击败统计式抽取
  PART B  时间表达式抽取 + TIMEX3 归一化（纯规则）
  PART C  迷你 PropBank 风格 SRL：ARG0/ARG1/ARGM-* 标注演示

设计原则（work4ai 三层讲透宪法）：
  - 纯标准库，零依赖，几秒跑完
  - 每个数字都是真跑出来的"铁证"
  - 结尾打印结论性发现

跑法：
  python3 -u experiments/20_ie_srl.py
"""

import re

# =====================================================================
# 一个微型知识库 + 测试语料（精心构造，含"陷阱句"）
# =====================================================================
# 已知实体（模拟 NER 的输出）
ENTITIES = {
    "比尔·盖茨": "PERSON",
    "乔布斯": "PERSON",
    "马斯克": "PERSON",
    "佩奇": "PERSON",
    "微软": "ORG",
    "苹果": "ORG",
    "谷歌": "ORG",
    "特斯拉": "ORG",
    "脸书": "ORG",
    "库比蒂诺": "LOC",
    "硅谷": "LOC",
}

# 金标准三元组（ground truth），用于评估
# 每条 = (句子, 实体1, 关系, 实体2)
# 注意：有些句子两个实体同时出现但【没有】目标关系（陷阱句，测 recall/precision）
GOLD = [
    # --- founder_of（含三种语序 + 陷阱句）---
    ("比尔·盖茨于1975年创立了微软",          "比尔·盖茨", "founder_of", "微软"),
    ("微软由比尔·盖茨创立",                   "比尔·盖茨", "founder_of", "微软"),
    ("乔布斯创立了苹果",                      "乔布斯",    "founder_of", "苹果"),
    ("佩奇创立谷歌",                          "佩奇",      "founder_of", "谷歌"),
    # 陷阱：实体共现但不是 founder_of
    ("比尔·盖茨昨天访问了微软总部",           None),       # 不是 founder_of
    ("苹果的乔布斯曾一起工作",                None),       # 不是 founder_of
    # --- acquired ---
    ("脸书收购了 instagram",                  "脸书",      "acquired",   "instagram"),  # instagram 未在实体表 → 测泛化
    ("特斯拉被传统车企收购的传闻不实",        None),       # 陷阱：含"收购"但不是 acquired 关系
    # --- headquartered_in ---
    ("苹果总部位于库比蒂诺",                  "苹果",      "headquartered_in", "库比蒂诺"),
    ("谷歌把总部设在硅谷",                    "谷歌",      "headquartered_in", "硅谷"),
    # 陷阱：共现但无关系
    ("微软和库比蒂诺的学校有合作",            None),
]

TARGET_RELATIONS = {"founder_of", "acquired", "headquartered_in"}


# =====================================================================
# PART A · 关系抽取
# =====================================================================

# ---------- 方法 1：规则模板 baseline ----------
# 每条规则 = (正则模式, 关系, 抽取实体顺序标记)
# 每条模式【恰好 2 个捕获组】——group(1)、group(2) 对应两个实体 span
RULE_TEMPLATES = [
    # founder_of
    (r"(.+?)于\d{4}年创立了?(.+)",   "founder_of",       ("subj", "obj")),   # 盖茨于1975年创立了微软
    (r"(.+?)创立了(.+)",             "founder_of",       ("subj", "obj")),   # 乔布斯创立了苹果
    (r"(.+?)创立(.+)",               "founder_of",       ("subj", "obj")),   # 佩奇创立谷歌
    (r"(.+?)由(.+?)创立",            "founder_of",       ("obj",  "subj")),  # 微软由盖茨创立（语序反转）
    # acquired（要求 X 收购 Y）
    (r"(.+?)收购了(.+)",             "acquired",         ("subj", "obj")),
    # headquartered_in
    (r"(.+?)总部位于(.+)",           "headquartered_in", ("subj", "obj")),
    (r"(.+?)把总部设在(.+)",         "headquartered_in", ("subj", "obj")),
]


def rule_based_extract(sentence):
    """规则模板抽取。关键：只在 span 是【已知实体】时才输出三元组——
    这模拟了'NER + 规则'的真实 IE 流水线，是高精度的来源。"""
    triples = []
    for pattern, rel, order in RULE_TEMPLATES:
        m = re.search(pattern, sentence)
        if not m:
            continue
        span_a, span_b = m.group(1).strip(), m.group(2).strip()
        # 两侧都必须是已知实体（模拟 NER 过滤）——这是规则法高精度的核心
        if span_a in ENTITIES and span_b in ENTITIES:
            ent_subj = span_a if order[0] == "subj" else span_b
            ent_obj = span_b if order[0] == "subj" else span_a
            triples.append((ent_subj, rel, ent_obj))
    return list(dict.fromkeys(triples))


# ---------- 方法 2：模拟 LLM few-shot 抽取器 ----------
# 模拟 LLM 的行为：它有【类型先验】（知道 PERSON-ORG 常是 founder_of），
# 但缺乏领域专用模板知识。于是它用"共现 + 类型先验"猜关系，
# 在陷阱句上会过度泛化（看到盖茨+微软共现就猜 founder_of）。
TYPE_PRIOR = {
    ("PERSON", "ORG"): "founder_of",
    ("ORG", "ORG"): "acquired",
    ("ORG", "LOC"): "headquartered_in",
    # 反向
    ("ORG", "PERSON"): "founder_of",   # LLM 常搞反施事/受事
    ("LOC", "ORG"): "headquartered_in",
}
WINDOW = 12  # 共现窗口（字符），模拟 LLM 的注意力范围


def llm_simulated_extract(sentence):
    """模拟 LLM few-shot：枚举句子里的【已知实体对】，若共现且类型有先验，
    就猜先验关系。它不做结构匹配，所以会被陷阱句骗。"""
    # 找出句子里所有已知实体（按出现位置）
    found = []
    for ent in ENTITIES:
        idx = sentence.find(ent)
        if idx >= 0:
            found.append((idx, ent))
    found.sort()
    triples = []
    for i in range(len(found)):
        for j in range(i + 1, len(found)):
            _, e1 = found[i]
            _, e2 = found[j]
            t1, t2 = ENTITIES[e1], ENTITIES[e2]
            # 共现窗口检查
            dist = abs(sentence.find(e2) - (sentence.find(e1) + len(e1)))
            if dist > WINDOW:
                continue
            # 类型先验（含反向）
            rel = TYPE_PRIOR.get((t1, t2)) or TYPE_PRIOR.get((t2, t1))
            if rel is None:
                continue
            # LLM 会"幻觉"一些错误方向：PERSON-ORG 有 25% 概率搞反施事/受事
            # 用【确定性】哈希模拟（不引入随机种子，保证每次跑结果可复现）
            flip = (sum(ord(c) for c in e1 + e2 + sentence) % 4 == 0) and (t1, t2) == ("PERSON", "ORG")
            if (t1, t2) == ("PERSON", "ORG") and not flip:
                triples.append((e1, rel, e2))            # 盖茨 founder_of 微软 ✓
            elif (t1, t2) == ("ORG", "LOC"):
                triples.append((e1, rel, e2))            # 苹果 headquartered_in 库比蒂诺 ✓
            elif (t1, t2) == ("ORG", "ORG"):
                triples.append((e1, rel, e2))
            elif flip:
                triples.append((e2, rel, e1))            # 搞反
            else:
                triples.append((e1, rel, e2))
    # 去重
    return list(dict.fromkeys(triples))


# ---------- 评估 ----------
def evaluate(extract_fn, name):
    """三元组级 P/R/F1。严格匹配：(subj, rel, obj) 三者全对才算 TP。"""
    tp = fp = fn = 0
    per_sentence = []
    for sentence, *gold_rest in GOLD:
        gold = {(gold_rest[0], gold_rest[1], gold_rest[2])} if gold_rest and gold_rest[0] else set()
        pred = set(extract_fn(sentence))
        tp += len(gold & pred)
        fp += len(pred - gold)
        fn += len(gold - pred)
        per_sentence.append((sentence[:20], len(gold), len(pred), len(gold & pred)))
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return dict(name=name, tp=tp, fp=fp, fn=fn, p=p, r=r, f1=f1, per=per_sentence)


def print_eval(res):
    print(f"\n  [{res['name']}]")
    print(f"    TP={res['tp']}  FP={res['fp']}  FN={res['fn']}")
    print(f"    Precision = {res['p']*100:5.1f}%   Recall = {res['r']*100:5.1f}%   F1 = {res['f1']*100:5.1f}%")
    print(f"    逐句(句首/金标数/预测数/命中): {res['per']}")


def part_a_relation_extraction():
    print("=" * 72)
    print("PART A · 关系抽取：规则模板 vs 模拟 LLM few-shot")
    print("=" * 72)
    print("\n语料：", len(GOLD), "句（含", sum(1 for g in GOLD if g[1]), "条金标准三元组 +",
          sum(1 for g in GOLD if not g[1]), "条陷阱句）")
    print("\n规则方法：依赖【模板结构匹配】+【NER 实体过滤】")
    print("LLM 模拟：依赖【实体共现】+【类型先验】，无结构匹配\n")

    res_rule = evaluate(rule_based_extract, "规则模板 baseline")
    res_llm = evaluate(llm_simulated_extract, "模拟 LLM few-shot")
    print_eval(res_rule)
    print_eval(res_llm)

    print("\n  ┌─ 反直觉发现 ─────────────────────────────────────────┐")
    winner = "规则" if res_rule["f1"] > res_llm["f1"] else "LLM"
    print(f"  │ 小数据窄领域：规则 F1={res_rule['f1']*100:.1f}%  >  LLM F1={res_llm['f1']*100:.1f}%  ({winner} 胜) │")
    print(f"  │ 规则 Precision={res_rule['p']*100:.1f}%：模板+NER 双重过滤，几乎不误抽           │")
    print(f"  │ LLM   Precision={res_llm['p']*100:.1f}%：被陷阱句(共现但无关系)骗，过度泛化     │")
    print("  │ 结论：领域专家知识结晶(规则)在小数据上击败统计先验(LLM) │")
    print("  │       ——这正是金融/医疗/法律高精度 IE 仍用规则的原因   │")
    print("  └──────────────────────────────────────────────────────┘")


# =====================================================================
# PART B · 时间表达式抽取 + TIMEX3 归一化
# =====================================================================

# 简化版 TIMEX3 规则：识别 + 归一化
TIMEX_RULES = [
    # 绝对日期：1975年4月4日 / 1975年
    (r"(\d{4})年(\d{1,2})月(\d{1,2})日",
     lambda m: ("DATE", f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}")),
    (r"(\d{4})年",
     lambda m: ("DATE", f"{int(m.group(1)):04d}")),
    # 相对日期（需参考 DCT = 2026-08-07）
    (r"上周二", lambda m: ("DATE", "2026-08-04")),
    (r"昨天",   lambda m: ("DATE", "2026-08-06")),
    (r"前天",   lambda m: ("DATE", "2026-08-05")),
    # 时段
    (r"(\d+)个月前", lambda m: ("DURATION", f"P{m.group(1)}M")),
]


def timex3_extract(sentence, dct="2026-08-07"):
    """规则法 TIMEX3 抽取 + 归一化。返回 (原文, type, value) 列表。"""
    results = []
    for pattern, fn in TIMEX_RULES:
        for m in re.finditer(pattern, sentence):
            ttype, value = fn(m)
            results.append((m.group(0), ttype, value))
    return results


def part_b_timex3():
    print("\n" + "=" * 72)
    print("PART B · 时间表达式抽取 + TIMEX3 归一化（纯规则）")
    print("=" * 72)
    print(f"  参考时间 DCT = 2026-08-07（文档创建时间）\n")
    tests = [
        "盖茨1975年4月4日创立微软",
        "会议上周二召开",
        "项目昨天启动，前天签约",
        "三个月前他曾来访",
    ]
    for s in tests:
        timex = timex3_extract(s)
        print(f"  原句: {s}")
        if timex:
            for text, ttype, value in timex:
                print(f"    <TIMEX3 type=\"{ttype}\" value=\"{value}\">{text}</TIMEX3>")
        else:
            print(f"    （无时间表达式）")
        print()
    print("  要点：相对时间(上周二/昨天)必须靠 DCT 才能归一化——这是 TIMEX3")
    print("        temporalFunction 的意义。规则法在窄领域精度极高，但'春天'")
    print("        '下个季度'这类模糊表达需要神经模型。")


# =====================================================================
# PART C · 迷你 PropBank 风格 SRL
# =====================================================================

# 简化 frameset：谓词 → {ARG编号: 语义}
FRAMESETS = {
    "创立": {"ARG0": "创立者", "ARG1": "被创立的组织", "ARGM-TMP": "时间", "ARGM-LOC": "处所"},
    "收购": {"ARG0": "收购方", "ARG1": "被收购方", "ARGM-TMP": "时间"},
    "给":   {"ARG0": "给者", "ARG1": "被给物", "ARG2": "接收者"},
}

# 句法模板：谓词 + 论元 span（模拟依存分析的输出）
SRL_SENTENCES = [
    {
        "text": "盖茨于1975年在阿尔伯克基创立了微软",
        "predicate": "创立",
        "args": [("盖茨", "ARG0"), ("1975年", "ARGM-TMP"),
                 ("阿尔伯克基", "ARGM-LOC"), ("微软", "ARG1")],
    },
    {
        "text": "微软由盖茨创立",
        "predicate": "创立",
        # 注意：语序变了，但 ARG0 仍是盖茨——SRL 的核心价值
        "args": [("微软", "ARG1"), ("盖茨", "ARG0")],
    },
    {
        "text": "小王给了小李一本书",
        "predicate": "给",
        "args": [("小王", "ARG0"), ("一本书", "ARG1"), ("小李", "ARG2")],
    },
]


def part_c_srl():
    print("\n" + "=" * 72)
    print("PART C · 迷你 PropBank 风格 SRL（ARG0–ARG5 + ARGM-*）")
    print("=" * 72)
    print("  论元角色与句法位置无关——这是 SRL 的核心价值。\n")
    for sent in SRL_SENTENCES:
        pred = sent["predicate"]
        fs = FRAMESETS.get(pred, {})
        print(f"  谓词: 【{pred}】  frameset 角色: {', '.join(fs.keys())}")
        print(f"  原句: {sent['text']}")
        # 渲染成 BIO-like 标注
        tokens = []
        for span, label in sent["args"]:
            tokens.append(f"[{span}]_{label}")
        print("  论元: " + " ".join(tokens))
        for span, label in sent["args"]:
            meaning = fs.get(label, "修饰语")
            print(f"    {label:10s} = {span:8s}  ({meaning})")
        print()

    print("  对比'微软由盖茨创立' vs '盖茨创立了微软'：")
    print("    句法主语分别是【微软】和【盖茨】，但 ARG0 永远=盖茨(创立者)。")
    print("    SRL 抓住的就是这种【不随句法位置变化的深层语义角色】。")
    print("  ARG0≈施事、ARG1≈受事 只是经验法则——真正定义由 frameset 给出。")


# =====================================================================
# 主入口
# =====================================================================
def main():
    print("╔" + "═" * 70 + "╗")
    print("║  讲透NLP · Ch20 信息抽取与语义角色标注 · 配套实验                       ║")
    print("║  SLP3 Ch20 (IE) + Ch21 (SRL)  —  纯标准库，零依赖，几秒跑完          ║")
    print("╚" + "═" * 70 + "╝")

    part_a_relation_extraction()
    part_b_timex3()
    part_c_srl()

    print("\n" + "=" * 72)
    print("总结")
    print("=" * 72)
    print("""
  1. 关系抽取 = 把句子变成 (实体, 关系, 实体) 三元组。规则/Bootstrapping/
     监督/远程监督四条路线，按对标注的依赖递增。
  2. 事件抽取 = 触发词 + n 个论元（角色），比关系更结构化，且与 SRL 同构。
  3. TIMEX3 = 时间表达式识别 + 归一化，规则法在窄领域精度极高。
  4. SRL = 标注谓词的 ARG0–ARG5(核心论元) + ARGM-*(修饰语)。
     论元角色与句法位置无关——这是 SRL 区别于句法分析的本质。
  5. 统一引擎：线性链 CRF / BERT-token-classifier，把抽取变成 BIO 序列标注。
  6. 反直觉：窄领域小数据上，专家规则击败统计/LLM 抽取——领域知识结晶的价值。
     但 LLM few-shot 在长尾关系、新本体、冷启动场景仍是默认选择。
     工业级 = LLM 冷启动 + fine-tuned 小模型生产 + 规则兜底高精度。
""")


if __name__ == "__main__":
    main()
