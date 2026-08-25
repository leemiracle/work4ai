#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E3 CoT 实验：思维链四条件对比（指南 techniques/cot + Kojima zero-shot CoT 的实证）
==================================================================================
问题：CoT 到底何时有效？"让我们一步步思考"这种零样本咒语有效吗？
设计（4 条件 × 2 模型 × 10 题）：
  a) zero-direct ：零样本，只要求答案
  b) zero-cot   ：零样本 + "请一步一步思考，最后给出'答案是X'"
  c) few-direct ：少样本，示例只给答案（无推理）
  d) few-cot    ：少样本，示例含完整推理链（指南 odd-numbers 格式）
模型：Qwen2.5-0.5B(本地) / glm-4-flash(API)
题目：指南经典题（奇数和/妹妹年龄）+ 8 道自造可验算算术应用题
产出：results/e3_cot.json + e3_cot.png
"""
from common import local_qwen, glm, save
import re, time

TASKS = [  # (题目, 答案)
    ("这组数中的奇数加起来是偶数：15、32、5、13、82、7、1。对还是错？", "错"),
    ("当我6岁时，我的妹妹是我年龄的一半。现在我70岁了，妹妹多大？", "67"),
    ("小明有12个苹果，送给小红5个，又买了3个。现在有几个苹果？", "10"),
    ("一本书240页，第一天读了全书的1/4，第二天读了40页。还剩多少页？", "140"),
    ("商店上午卖出15件衣服，下午卖出的是上午的2倍。全天共卖多少件？", "45"),
    ("小李有78元，买书花了23元，后来又挣了15元。现在有多少元？", "70"),
    ("火车3小时行驶240千米。照此速度，5小时行驶多少千米？", "400"),
    ("一块长方形菜地长8米宽3米，面积是多少平方米？", "24"),
    ("盘子里有60颗糖，分给同学一半，自己又吃了10颗。还剩多少颗？", "20"),
    ("一件衣服原价120元，先打八折再用券减10元，最终多少钱？", "86"),
]

FEWSHOT_COT = """这组数中的奇数加起来是偶数：4、8、9、15、12、2、1。
推理：奇数是9、15、1，相加9+15+1=25。25是奇数。所以"加起来是偶数"不成立。
答案是：错。

Q：小刚有10支铅笔，用掉4支，又买了6支。现在有几支？
推理：10-4=6，6+6=12。答案是：12。

"""
FEWSHOT_DIRECT = """这组数中的奇数加起来是偶数：4、8、9、15、12、2、1。
答案是：错。

Q：小刚有10支铅笔，用掉4支，又买了6支。现在有几支？
答案是：12。

"""

def parse_answer(out):
    out = out.strip()
    m = re.findall(r"答案[是为：:]*\s*(\d+|对|错|True|False)", out)
    if m: return m[-1]
    if re.search(r"(对还是错)", ""): pass
    nums = re.findall(r"-?\d+(?:\.\d+)?", out)
    if "还是错" in out or "对还是错" in out: return None
    return nums[-1] if nums else None

def correct(pred, gold):
    if pred is None: return False
    p, g = str(pred), str(gold)
    if g in ("对", "错"):
        return p == g or (g == "对" and p.lower() == "true") or (g == "错" and p.lower() == "false")
    try: return abs(float(p) - float(g)) < 1e-6
    except: return False

def build(cond, q):
    if cond == "zero-direct":
        return f"{q}\n只输出最终答案（数字或对/错），不要解释。"
    if cond == "zero-cot":
        return f"{q}\n请一步一步思考，推理过程写在前面，最后单独一行写'答案是：X'。"
    if cond == "few-direct":
        return FEWSHOT_DIRECT + f"Q：{q}\n答案是："
    if cond == "few-cot":
        return FEWSHOT_COT + f"Q：{q}\n推理："

CONDS = ["zero-direct", "zero-cot", "few-direct", "few-cot"]
res = {"meta": {"tasks": len(TASKS)}, "acc": {}, "errors": {}}

for cond in CONDS:
    acc_l = acc_g = 0; errs = []
    for q, gold in TASKS:
        # 本地
        out_l = local_qwen(build(cond, q), max_new_tokens=256 if "cot" in cond else 16,
                           temperature=0.0)
        pl = parse_answer(out_l); ok_l = correct(pl, gold); acc_l += ok_l
        if not ok_l: errs.append(("qwen", q[:14], gold, pl, out_l[-60:].replace("\n", " ")))
        # API
        r = glm("glm-4-flash", build(cond, q),
                max_tokens=512 if "cot" in cond else 16, temperature=0.1)
        pg = parse_answer(r["content"]); ok_g = correct(pg, gold); acc_g += ok_g
        if not ok_g: errs.append(("glm", q[:14], gold, pg, r["content"][-60:].replace("\n", " ")))
        time.sleep(0.2)
    res["acc"][cond] = {"qwen": acc_l / len(TASKS), "glm4flash": acc_g / len(TASKS)}
    res["errors"][cond] = errs[:6]
    print(f"  {cond:12s}: Qwen-0.5B {acc_l/len(TASKS):.0%} | glm-4-flash {acc_g/len(TASKS):.0%}")

save("e3_cot", res)

# ---- 可视化 ----
import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, ax = plt.subplots(figsize=(7.5, 4))
x = range(len(CONDS)); w = 0.35
ax.bar([i - w/2 for i in x], [res["acc"][c]["qwen"] for c in CONDS], w, label="Qwen2.5-0.5B", color="#4C72B0")
ax.bar([i + w/2 for i in x], [res["acc"][c]["glm4flash"] for c in CONDS], w, label="glm-4-flash", color="#55A868")
ax.set_xticks(list(x)); ax.set_xticklabels(["零样本\n直答", "零样本\n+一步步思考", "少样本\n直答", "少样本\nCoT"])
ax.set_ylabel("10题准确率"); ax.set_ylim(0, 1.1); ax.legend()
ax.set_title("E3 CoT 四条件对比：思维链何时有效？"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig("results/e3_cot.png", dpi=130)
print("[saved] results/e3_cot.png")
