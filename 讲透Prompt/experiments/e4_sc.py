#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E4 Self-Consistency 实验：采样多条推理路径 + 多数投票（Wang et al. 2022, 2203.11171 据指南）
==================================================================================
问题：CoT 采样一次会错，采样 9 条投票能纠多少错？
设计：6 道难题（鸡兔同笼/相遇/工程/利润——E3 的题 glm-4-flash zero-cot 已 100%，测不出差异）
  每题：greedy 基线 1 次 + temperature=0.8 采样 9 次（zero-cot prompt）
  统计：前缀多数投票 n=1/3/5/9 的准确率（n=1 即单次采样，与 greedy 对照）
产出：results/e4_sc.json + e4_sc.png（acc-n 曲线 + 每题票型分布）
"""
from common import glm, save
import re, time
from collections import Counter

TASKS = [  # (题目, 答案) —— 全部 Python 验算过
    ("笼子里有鸡和兔共35个头，94只脚。鸡有多少只？", 23),
    ("甲乙两地相距360千米，快车每小时行60千米，慢车每小时行40千米，两车同时相向而行，几小时后相遇？", 3.6),
    ("一项工程甲队单独做12天完成，乙队单独做24天完成，两队合作需要几天完成？", 8),
    ("某商品进价100元，商家先加价50%标价，又打8折出售。每件利润是多少元？", 20),
    ("一个数加上它的50%正好是27，这个数是多少？", 18),
    ("今年父子年龄和是40岁，4年后父亲年龄恰好是儿子的3倍。儿子今年多少岁？", 8),
]

PROMPT = "{q}\n请一步一步思考，推理过程写在前面，最后单独一行写'答案是：X'。"

def parse_answer(out):
    m = re.findall(r"答案[是为：:]*\s*(-?\d+(?:\.\d+)?)", out)
    if m: return m[-1]
    nums = re.findall(r"-?\d+(?:\.\d+)?", out)
    return nums[-1] if nums else None

def to_f(p):
    try: return float(p)
    except: return None

def vote(preds, gold):
    """前缀多数投票：对每个 n 取前 n 个预测的众数（数值容差 1e-6）。返回 {n: bool}"""
    vals = [to_f(p) for p in preds]
    vals = [round(v, 6) if v is not None else None for v in vals]
    out = {}
    for n in (1, 3, 5, 9):
        c = Counter(v for v in vals[:n] if v is not None)
        if not c: out[n] = False; continue
        top, cnt = c.most_common(1)[0]
        out[n] = abs(top - gold) < 1e-6 and cnt >= (n // 2 + 1)  # 严格多数且正确
    return out, vals

res = {"meta": {"model": "glm-4-flash", "sampling": "T=0.8, 9条/题", "tasks": len(TASKS)},
       "greedy_acc": 0, "sc_acc": {1: 0, 3: 0, 5: 0, 9: 0}, "detail": []}

for q, gold in TASKS:
    # greedy 基线
    r = glm("glm-4-flash", PROMPT.format(q=q), max_tokens=512, temperature=0.1)
    g_ok = abs((to_f(parse_answer(r["content"])) or -999) - gold) < 1e-6
    res["greedy_acc"] += g_ok
    # 9 路采样
    preds = []
    for i in range(9):
        r = glm("glm-4-flash", PROMPT.format(q=q), max_tokens=512, temperature=0.8)
        preds.append(parse_answer(r["content"]))
        time.sleep(0.1)
    sc, vals = vote(preds, gold)
    for n in (1, 3, 5, 9): res["sc_acc"][n] += sc[n]
    res["detail"].append({"q": q[:18], "gold": gold, "greedy": g_ok,
                          "votes": dict(Counter(v for v in vals if v is not None)), "sc": sc})
    print(f"  [{time.strftime('%H:%M:%S')}] {q[:14]}… gold={gold} greedy={g_ok} "
          f"票型={dict(Counter(v for v in vals if v is not None))} sc9={sc[9]}", flush=True)

res["greedy_acc"] /= len(TASKS)
for n in (1, 3, 5, 9): res["sc_acc"][n] /= len(TASKS)
print(f"== greedy(T=0.1) {res['greedy_acc']:.0%} | SC: n=1 {res['sc_acc'][1]:.0%} / "
      f"n=3 {res['sc_acc'][3]:.0%} / n=5 {res['sc_acc'][5]:.0%} / n=9 {res['sc_acc'][9]:.0%}", flush=True)
save("e4_sc", res)

# ---- 可视化 ----
import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, ax = plt.subplots(figsize=(7, 4.2))
ns = [1, 3, 5, 9]
ax.plot(ns, [res["sc_acc"][n] for n in ns], "o-", color="#4C72B0", label="Self-Consistency（多数投票）")
ax.axhline(res["greedy_acc"], ls="--", color="#C44E52", label=f"greedy 单次（T=0.1）={res['greedy_acc']:.0%}")
ax.set_xticks(ns); ax.set_xlabel("采样条数 n（投票人数）"); ax.set_ylabel("6题准确率")
ax.set_ylim(0, 1.1); ax.legend(); ax.grid(alpha=0.3)
ax.set_title("E4 Self-Consistency：9 条采样路径能纠多少错？")
plt.tight_layout(); plt.savefig("results/e4_sc.png", dpi=130)
print("[saved] results/e4_sc.png")
