#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E9 ★ 模型适配实验：同一个 prompt，四种模型配置怎么吃
==================================================================================
问题：prompt 技巧是模型的函数——few-shot 救谁、CoT 咒语在 thinking 模型上是否负作用？
配置（4）：glm-4-flash / glm-4.7 / glm-5(thinking 默认开) / glm-5(thinking off)
风格（3）：zero-direct / zero-cot（+"一步步思考"）/ few-cot（带推理链示例）
任务（6）：
  3 道推理题（鸡兔同笼/工程合作/父子年龄）+ 3 道指令遵循题（恰好10字/全大写/拼音排序）
  指令遵循题对准 2505.11423（reasoning 伤指令跟随）与 Google Cloud
  "thinking 模型删掉手写 step-by-step" 的建议。
产出：results/e9_adapt.json + e9_adapt.png（热力图：配置×风格 双列——推理acc/IF acc）
"""
from common import glm, save
import re, time

REASON_TASKS = [
    ("笼子里有鸡和兔共35个头，94只脚。鸡有多少只？", "23"),
    ("一项工程甲队单独做12天完成，乙队单独做24天完成，两队合作需要几天完成？", "8"),
    ("今年父子年龄和是40岁，4年后父亲年龄恰好是儿子的3倍。儿子今年多少岁？", "8"),
]
IF_TASKS = [
    ("if10", "用恰好10个汉字介绍长城，不要标点。"),
    ("ifupper", "把下面的英文改成全部大写字母输出：the weather is nice today"),
    ("iforder", "把 覆盆子、菠萝、苹果、木瓜 按拼音首字母排序，用顿号分隔，只输出结果。"),
]

FEWSHOT_COT = """Q：小刚有10支铅笔，用掉4支，又买了6支。现在有几支？
推理：10-4=6，6+6=12。答案是：12。

"""

def build_reason(style, q):
    if style == "zero-direct":
        return f"{q}\n只输出最终答案数字，不要解释。"
    if style == "zero-cot":
        return f"{q}\n请一步一步思考，最后单独一行写'答案是：X'。"
    return FEWSHOT_COT + f"Q：{q}\n推理："

def check_reason(out, gold):
    m = re.findall(r"-?\d+(?:\.\d+)?", out or "")
    return bool(m) and abs(float(m[-1]) - float(gold)) < 1e-6

PINYIN = {"覆盆子": "f", "菠萝": "b", "苹果": "p", "木瓜": "m"}  # 正确序: b<f<m<p → 菠萝、覆盆子、木瓜、苹果
def check_if(tid, out):
    out = (out or "").strip()
    last = [l for l in out.splitlines() if l.strip()][-1] if out else ""  # 取末行判答案
    if tid == "if10":
        cjk = re.findall(r"[\u4e00-\u9fff]", last)
        return len(cjk) == 10
    if tid == "ifupper":
        return "THE WEATHER IS NICE TODAY" in last.upper() and last == last.upper()
    if tid == "iforder":
        seq = re.sub(r"[^覆盆子菠萝苹果木瓜、]", "", last)
        return seq in ("菠萝、覆盆子、木瓜、苹果", "菠萝,覆盆子,木瓜,苹果")
    return False

CONFIGS = [
    ("glm-4-flash", None),
    ("glm-4.7", None),
    ("glm-5", "think_on"),      # 默认 thinking
    ("glm-5", "think_off"),
]
STYLES = ["zero-direct", "zero-cot", "few-cot"]

res = {"meta": {}, "matrix": {}, "latency": {}}
for model, tag in CONFIGS:
    key = f"{model}" + (f"[{tag}]" if tag else "")
    thinking = {"type": "disabled"} if tag == "think_off" else None
    print(f"== {key}", flush=True)
    res["matrix"][key] = {}; res["latency"][key] = []
    for style in STYLES:
        r_ok = if_ok = 0; r_tok = 0
        for q, gold in REASON_TASKS:
            r = glm(model, build_reason(style, q), max_tokens=1024, temperature=0.1, thinking=thinking, retries=1)
            r_ok += check_reason(r["content"], gold); r_tok += r["reasoning_tokens"]
            res["latency"][key].append(r["latency_ms"])
        for tid, q in IF_TASKS:
            instr = q if style == "zero-direct" else (
                f"{q}\n请一步一步思考后再作答。" if style == "zero-cot" else f"{q}\n（参考做法：先分析要求，再严格按格式输出）")
            r = glm(model, instr, max_tokens=1024, temperature=0.1, thinking=thinking, retries=1)
            ok = check_if(tid, r["content"])
            if_ok += ok
            res["matrix"][key].setdefault("if_detail", {}).setdefault(style, {})[tid] = \
                {"ok": ok, "out": r["content"][-80:]}
        res["matrix"][key][style] = {"reason_acc": r_ok / 3, "if_acc": if_ok / 3,
                                     "avg_reasoning_tokens": r_tok // 3}
        print(f"  {style:12s} 推理 {r_ok}/3 | 指令遵循 {if_ok}/3", flush=True)
        time.sleep(0.2)

save("e9_adapt", res)

# ---- 热力图 ----
import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["font.family"] = "Noto Sans CJK SC"
keys = list(res["matrix"])
fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
for ax, metric, title in [(axes[0], "reason_acc", "推理题（3题）"), (axes[1], "if_acc", "指令遵循题（3题）")]:
    M = np.array([[res["matrix"][k][s][metric] for s in STYLES] for k in keys])
    im = ax.imshow(M, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(STYLES))); ax.set_xticklabels(["zero-direct", "zero-cot", "few-cot"], fontsize=9)
    ax.set_yticks(range(len(keys))); ax.set_yticklabels(keys, fontsize=9)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{M[i,j]:.0%}", ha="center", va="center", fontsize=9)
    ax.set_title(title)
plt.suptitle("E9 模型适配：同一个 prompt，四种配置怎么吃", y=1.02)
plt.tight_layout(); plt.savefig("results/e9_adapt.png", dpi=130, bbox_inches="tight")
print("[saved] results/e9_adapt.png")
