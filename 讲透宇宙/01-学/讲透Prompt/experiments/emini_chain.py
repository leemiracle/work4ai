#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-mini 提示链实验：单发大 prompt vs 链式分解（06 章素材）
==================================================================================
任务：从 5 条混合信息文本中抽取结构化 JSON（人名/金额/日期三字段，可能缺省）
  a) single：一次给全部指令+文本，直接输出 JSON
  b) chained：链式三步——①抽取实体 → ②标准化（日期统一 YYYY-MM-DD、金额去"元"）→ ③组装纯 JSON
产出：results/emini_chain.json
"""
from common import glm, save
import json, re, time

TEXTS = [
    "张三于2026年8月15日转账了三千五百元给李四。",
    "会议纪要：王五提出预算 12000，预计下月初（2026-09-03）启动。",
    "赵六报销差旅费 ¥1,842.50，发票日期 2026/7/22。",
    "钱七没有提交任何单据。",
    "孙八将在8月底前归还欠款伍佰元整（2026年8月31日）。",
]
GOLD = [
    {"人名": "张三", "金额": 3500, "日期": "2026-08-15"},
    {"人名": "王五", "金额": 12000, "日期": "2026-09-03"},
    {"人名": "赵六", "金额": 1842.5, "日期": "2026-07-22"},
    None,
    {"人名": "孙八", "金额": 500, "日期": "2026-08-31"},
]

SINGLE = """从下面的文本中抽取信息，输出 JSON（字段：人名、金额、日期；金额转数字，日期统一为YYYY-MM-DD；无信息输出 null）。
只输出 JSON，不要解释。
文本：{t}"""

CH1 = "从文本中抽取涉及的金额和日期（原文形式），没有则输出'无'。文本：{t}"
CH2 = "把下面的金额转成阿拉伯数字，日期转成 YYYY-MM-DD：{raw}"
CH3 = "根据以下信息输出 JSON（字段：人名、金额、日期；无信息为 null），只输出 JSON：{std}\n人名：{name}"

def parse_json(s):
    m = re.search(r"\{.*\}", s or "", re.S)
    if not m: return None
    try: return json.loads(m.group(0))
    except: return None

def field_f1(pred, gold):
    """字段级判分：精确匹配（None 对 None）。返回命中率"""
    if gold is None: return pred is None or (isinstance(pred, dict) and all(v is None for v in pred.values()))
    if not isinstance(pred, dict): return 0.0
    hit = 0
    for k, v in gold.items():
        pv = pred.get(k)
        if isinstance(v, (int, float)) and isinstance(pv, (int, float)):
            hit += abs(pv - v) < 0.01
        else:
            hit += str(pv) == str(v)
    return hit / 3

res = {"single": [], "chained": [], "acc": {}}
for t, g in zip(TEXTS, GOLD):
    # a) single
    r = glm("glm-4-flash", SINGLE.format(t=t), max_tokens=300, temperature=0.1, retries=1)
    f1s = field_f1(parse_json(r["content"]), g)
    res["single"].append({"f1": f1s, "out": r["content"][:120]})
    # b) chained
    r1 = glm("glm-4-flash", CH1.format(t=t), max_tokens=200, temperature=0.1, retries=1)
    r2 = glm("glm-4-flash", CH2.format(raw=r1["content"][:150]), max_tokens=200, temperature=0.1, retries=1)
    name = re.search(r"[\u4e00-\u9fff]{1,3}(?=于|提出|报销|没有|将)", t)
    r3 = glm("glm-4-flash", CH3.format(std=r2["content"][:120], name=name.group(0) if name else "无"),
             max_tokens=200, temperature=0.1, retries=1)
    f1c = field_f1(parse_json(r3["content"]), g)
    res["chained"].append({"f1": f1c, "out": r3["content"][:120]})
    print(f"  {t[:14]}… single={f1s:.2f} chained={f1c:.2f}", flush=True)
    time.sleep(0.2)

res["acc"] = {"single": sum(x["f1"] for x in res["single"]) / len(TEXTS),
              "chained": sum(x["f1"] for x in res["chained"]) / len(TEXTS)}
print(f"== 单发 {res['acc']['single']:.0%} vs 链式 {res['acc']['chained']:.0%}", flush=True)
save("emini_chain", res)
