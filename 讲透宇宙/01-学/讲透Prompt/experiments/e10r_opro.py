#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E10-R OPRO 复跑：解析器加固 + 纯轨迹驱动（12 章期权 1 + 09 章练习 9）
==================================================================================
E10 的两个教训分开治：
  A) 解析器加固：剥前缀话（"好的，以下是…"）/ 引号 / 多行取首条非空指令行；解析失败重采样 1 次
  B) 元提示删掉"注意否定词"领域提示 → 纯轨迹驱动（人机协同 vs 全自动的控制变量）
问题：修复 A 之后，B 条件下优化器还能到 100% 吗？几轮？
产出：results/e10r_opro.json + e10r_opro.png
"""
from common import glm, save
import re, time

TRAIN = [
    ("没有让我失望，第二次回购了", "正"), ("一点也不好用，客服还态度差", "负"),
    ("价格不算贵，质量对得起价钱", "正"), ("毫无诚意，全是套路", "负"),
    ("比想象中好，充电很快", "正"), ("用了一周就坏了", "负"),
    ("不算难吃，但也就那样", "正"), ("呵，等了两周才发货", "负"),
    ("包装很用心，细节到位", "正"), ("图片和实物差距太大", "负"),
    ("老人也会用，简单", "正"), ("噪音大得没法忍", "负"),
]
TEST = [
    ("没有白等，很满意", "正"), ("一点也不专业", "负"),
    ("这个价位不算亏", "正"), ("完全是敷衍了事", "负"),
    ("响应快，屏幕清晰", "正"), ("两天就闪屏了", "负"),
    ("味道不算差，分量足", "正"), ("物流慢到离谱", "负"),
]
INIT = "判断这条评论是正面还是负面，只输出一个字：正 或 负。"

def execute(instr, text):
    r = glm("glm-4-flash", f"{instr}\n评论：{text}", max_tokens=8, temperature=0.1, retries=1)
    out = r["content"].strip()
    return "正" if "正" in out[:3] else ("负" if "负" in out[:3] else None)

def score(instr, data):
    ok = 0; wrong = []
    for text, label in data:
        p = execute(instr, text)
        if p == label: ok += 1
        else: wrong.append((text, label, p))
    return ok / len(data), wrong

# ---------- A) 解析器加固 ----------
PREFIX_PAT = re.compile(
    r"^(好的|以下是|优化后的|新指令|改进后的|指令)[:：]?\s*|^[「『\"“]|[」』\"”]$")
def robust_parse(raw):
    """剥前缀话→取首条非空行→去引号包裹→长度与合法性检查。失败返回 None。"""
    lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
    for l in lines[:4]:  # 只扫前 4 行，防长篇解释
        l = PREFIX_PAT.sub("", l).strip()
        l = l.strip("「」『』\"'“”").strip()
        # 合法指令：含中文、10-80 字、不是纯解释（含"指令："前缀已剥）
        if 8 <= len(l) <= 80 and re.search(r"[\u4e00-\u9fff]", l) and "```" not in l:
            return l
    return None

META_NOHINT = """你是 prompt 优化专家。改进这条"中文情感分类指令"。
当前指令在 12 条训练评论上的准确率历史：
{history}
部分错误案例（评论 / 正确标签 / 模型输出）：
{wrongs}
初始指令：{init}
请提出一条更好的新指令（简短，不超过 60 字），只输出新指令本身，不要任何解释。
"""

history = []
res = {"meta": {"note": "解析器加固 + 元提示无领域提示（纯轨迹驱动）"}, "curve": [], "parse_fail": 0}
s0, wrong0 = score(INIT, TRAIN)
history.append((INIT, s0))
best = {"instr": INIT, "score": s0}
res["curve"].append({"iter": 0, "instr": INIT, "score": s0})
print(f"  [iter0 基线] {s0:.0%}", flush=True)

for it in range(1, 9):
    hist_txt = "\n".join(f"- 准确率 {s:.0%}：{i}" for i, s in history[-4:])
    wrong_txt = "\n".join(f"- {t} / {l} / 输出:{p}" for t, l, p in (wrong0 or [])[:4]) or "（无错误）"
    instr = None
    for attempt in range(2):  # 解析失败重采样 1 次
        r = glm("glm-4.7", META_NOHINT.format(history=hist_txt, wrongs=wrong_txt, init=INIT),
                max_tokens=200, temperature=0.8 if attempt == 0 else 1.0, retries=1)
        instr = robust_parse(r["content"])
        if instr: break
    if instr is None:
        res["parse_fail"] += 1
        print(f"  [iter{it}] 解析失败×2，沿用历史最优", flush=True)
        continue
    s, wrong0 = score(instr, TRAIN)
    history.append((instr, s))
    res["curve"].append({"iter": it, "instr": instr, "score": s})
    if s > best["score"]: best = {"instr": instr, "score": s}
    print(f"  [iter{it}] {s:.0%} | {instr[:46]}", flush=True)
    time.sleep(0.2)

s_test_init, _ = score(INIT, TEST)
s_test_best, _ = score(best["instr"], TEST)
res["best"] = best
res["test"] = {"baseline": s_test_init, "opro_best": s_test_best}
print(f"== 训练 {history[0][1]:.0%}→{best['score']:.0%} | 留出 基线 {s_test_init:.0%}→最优 {s_test_best:.0%} | 解析失败 {res['parse_fail']} 轮", flush=True)
save("e10r_opro", res)

import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, ax = plt.subplots(figsize=(7, 4))
c = res["curve"]
ax.plot([x["iter"] for x in c], [x["score"] for x in c], "o-", color="#55A868", label="E10-R 纯轨迹+加固解析")
# E10 原版曲线对照（含毒点：5/8 轮解析失败计 0）
e10 = [(0,.92),(1,0),(2,1.0),(3,0),(4,0),(5,1.0),(6,0),(7,0),(8,1.0)]
ax.plot([x for x,_ in e10], [y for _,y in e10], "x--", color="#C44E52", alpha=.6, label="E10 原版（脆解析）")
ax.axhline(.92, ls=":", color="#999")
ax.set_xlabel("优化轮次"); ax.set_ylabel("12条训练集准确率"); ax.legend(); ax.grid(alpha=.3)
ax.set_title("E10-R：修好解析器、撤掉提示，OPRO 还能自己爬到 100% 吗")
plt.tight_layout(); plt.savefig("results/e10r_opro.png", dpi=130)
print("[saved] results/e10r_opro.png")
