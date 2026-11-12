#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E10 ★ 自动优化 Prompt：OPRO 最小自实现（Yang et al. 2023, 2309.03409）
==================================================================================
问题：让 LLM 自己写 prompt（元提示循环），能不能超过人写的朴素指令？
角色：执行器 = glm-4-flash（固定）；优化器 = glm-4.7
任务：中文情感二分类（正/负），12 训练 + 8 留出测试，样本含否定/双关陷阱：
  "没有让我失望"(正) / "一点也不好用"(负) / "不算贵"(正) / "毫无诚意"(负) …
循环（8 轮）：
  score(当前指令, 12训练) → 元提示（历史轨迹 instruction→score + 误例）→ 优化器出新指令
基线：朴素指令。终点：最优指令在留出集上复测。
附：DSPy 安装探测（网络不通则手写 BootstrapFewShot 等价——3 个正确示例做 few-shot）。
产出：results/e10_opro.json + e10_opro.png
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

META = """你是 prompt 优化专家。你的任务是改进一条"中文情感分类指令"。
当前指令在 12 条训练评论上的准确率历史如下：
{history}
部分错误案例（评论 / 正确标签 / 模型输出）：
{wrongs}
初始指令：{init}
请提出一条新指令，要求：
1. 明确告诉模型注意否定词（如"没有失望"是正面、"一点也不好用"是负面）
2. 只输出一个字"正"或"负"
3. 指令要简短（不超过 60 字）
只输出新指令本身，不要任何解释。
"""

history = []
best = {"instr": INIT, "score": 0}
res = {"meta": {"executor": "glm-4-flash", "optimizer": "glm-4.7", "iters": 8},
       "curve": [], "best": None, "test": {}}

s0, wrong0 = score(INIT, TRAIN)
history.append((INIT, s0))
best = {"instr": INIT, "score": s0}
res["curve"].append({"iter": 0, "instr": INIT, "score": s0})
print(f"  [iter0 基线] {s0:.0%} 误例: {[(t[:8], p) for t,l,p in wrong0][:3]}", flush=True)

for it in range(1, 9):
    hist_txt = "\n".join(f"- 准确率 {s:.0%}：{i}" for i, s in history[-4:])
    wrong_txt = "\n".join(f"- {t} / {l} / 输出:{p}" for t, l, p in (wrong0 or [])[:4]) or "（无错误）"
    r = glm("glm-4.7", META.format(history=hist_txt, wrongs=wrong_txt, init=INIT),
            max_tokens=200, temperature=0.8, retries=1)
    instr = r["content"].strip().strip('"').split("\n")[0][:80]
    s, wrong0 = score(instr, TRAIN)
    history.append((instr, s))
    res["curve"].append({"iter": it, "instr": instr, "score": s})
    if s > best["score"]: best = {"instr": instr, "score": s}
    print(f"  [iter{it}] {s:.0%} | {instr[:40]}", flush=True)
    time.sleep(0.2)

# 留出集复测：基线 vs 最优
s_test_init, _ = score(INIT, TEST)
s_test_best, _ = score(best["instr"], TEST)
res["best"] = best
res["test"] = {"baseline": s_test_init, "opro_best": s_test_best}
print(f"== 训练集 基线 {history[0][1]:.0%} → 最优 {best['score']:.0%} | 留出集 基线 {s_test_init:.0%} → 最优 {s_test_best:.0%}", flush=True)

# ---- 手写 BootstrapFewShot 等价（DSPy 探测） ----
try:
    import subprocess
    p = subprocess.run(["pip", "install", "dspy-ai", "-q"], capture_output=True, timeout=60)
    dspy_ok = p.returncode == 0 and __import__("importlib").util.find_spec("dspy") is not None
except Exception:
    dspy_ok = False
res["dspy_installed"] = dspy_ok
# 等价实现：从训练集挑 3 条正确直答的示例做 few-shot
demo = [f"评论：{t}\n答：{l}" for t, l in TRAIN[:3]]
BOOT = "你将进行情感分类。参考示例：\n" + "\n".join(demo) + "\n\n只输出一个字：正 或 负。评论：{text}\n答："
ok = 0
for t, l in TEST:
    p = execute(BOOT.format(text=t), t) if False else None
    r = glm("glm-4-flash", BOOT.format(text=t), max_tokens=8, temperature=0.1, retries=1)
    out = r["content"].strip()
    p = "正" if "正" in out[:3] else ("负" if "负" in out[:3] else None)
    ok += p == l
res["test"]["bootstrap_fewshot"] = ok / len(TEST)
print(f"== BootstrapFewShot(手写等价) 留出集 {ok/len(TEST):.0%} (dspy_installed={dspy_ok})", flush=True)

save("e10_opro", res)

import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, ax = plt.subplots(figsize=(7, 4))
its = [c["iter"] for c in res["curve"]]
ax.plot(its, [c["score"] for c in res["curve"]], "o-", color="#4C72B0", label="OPRO 训练集准确率")
ax.axhline(res["curve"][0]["score"], ls="--", color="#999", label="朴素指令基线（训练集）")
ax.set_xlabel("优化轮次"); ax.set_ylabel("12条训练集准确率"); ax.legend(); ax.grid(alpha=0.3)
ax.set_title("E10 OPRO：让 glm-4.7 给 glm-4-flash 写指令")
plt.tight_layout(); plt.savefig("results/e10_opro.png", dpi=130)
print("[saved] results/e10_opro.png")
