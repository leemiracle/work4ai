#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E11 ★ 数学领域应用：GSM8K 风格 × prompt 策略矩阵 + Persona 四角色
==================================================================================
问题：在数学这个"硬核查对"领域，哪种 prompt 策略收益最大？Persona 真的有用吗？
设计：
  ① 8 道 GSM8K 风格题（自造，答案全部 Python 验算）× 5 策略 × 2 模型（glm-4-flash / glm-5 thinking off）
     策略：zero-direct / zero-cot / few-cot / PAL(写代码沙箱exec) / persona-老师
  ② Persona 专项：4 角色（普通/数学老师/严谨教授/费曼）× 8 题 × glm-4-flash
     过程质量代理指标：推理行数（含=的行）——对应 Springer 2026 persona 七倍过程性质量的方向
  ③ Lean/Prover prompt：复用 实战案例-Prover数学Agent/prompts.py 的模板（章节展示用，DCU 断点不重跑）
产出：results/e11_math.json + e11_math.png（两面板：策略矩阵条形 + persona 双轴）
"""
from common import glm, save
import re, io, time, contextlib, math
import builtins as _b

# ---------- 8 题（答案 Python 验算） ----------
TASKS = [
    ("q1", "小明买了4支钢笔每支12元，3本笔记本每本8元。他付了100元，应找回多少元？",
     lambda: 100 - (4*12 + 3*8)),
    ("q2", "一个班有42人，男生人数是女生的2倍少3人。女生有多少人？",
     lambda: (42 + 3) // 3),
    ("q3", "一辆车去程60km/h行3小时，回程90km/h。全程平均速度是多少km/h？（保留1位小数）",
     lambda: round(2*60*3*90/(60*3+90*2), 1) if False else round(360*2/(3+240/90), 1)),
    ("q4", "水果店苹果比梨多25%，梨有240千克。苹果和梨一共多少千克？",
     lambda: 240 + 240*1.25),
    ("q5", "一个水龙头每小时漏水0.8升。一个月（30天）漏多少升？",
     lambda: 0.8*24*30),
    ("q6", "某数除以7余3，除以5余2，该数最小是多少？",
     lambda: next(n for n in range(1, 200) if n % 7 == 3 and n % 5 == 2)),
    ("q7", "正方形边长增加2厘米面积增加24平方厘米。原边长是多少厘米？",
     lambda: next(n for n in range(1, 50) if (n+2)**2 - n*n == 24)),
    ("q8", "姐姐的糖果是妹妹的3倍。两人各吃4颗后姐姐是妹妹的4倍。妹妹原有几颗？",
     lambda: next(n for n in range(1, 50) if 3*n - 4 == 4*(n - 4))),
]
# q3 修正验算：去程 60×3=180km，回程 180/90=2h；总 360km/5h=72.0
TASKS[2] = ("q3", "一辆车去程以60km/h行驶3小时到达，然后以90km/h原路返回。全程平均速度是多少km/h？（保留1位小数）",
            lambda: 2*60*3/(3 + 60*3/90))

FEWSHOT_COT = """Q：小刚有10支铅笔，用掉4支，又买了6支。现在有几支？
推理：10-4=6，6+6=12。答案是：12。

"""

PERSONAS = {
    "普通": "",
    "数学老师": "你是一位耐心的数学老师，请像板书一样一步步演算，每步一行，最后写'答案是：X'。",
    "严谨教授": "你是一位严谨的数学教授，请先列出已知量与未知量，再列式求解，逐步推导，最后写'答案是：X'。",
    "费曼": "请像费曼一样，先用大白话解释这道题在问什么，再一步步算，最后写'答案是：X'。",
}

PAL_PROMPT = ("请写一段 Python 代码解决下面的数学题并 print 最终答案。\n"
              "只能用 math 库，不要 import 其他东西。只输出一个 ```python 代码块。\n题目：{q}")

_SANDBOX = {n: getattr(_b, n) for n in ("abs","range","sum","len","min","max","int","float","str","sorted","round","print")}
_allowed = {"math"}
def _imp(name, *a, **k):
    if name.partition(".")[0] in _allowed: return _b.__import__(name, *a, **k)
    raise ImportError(f"沙箱禁用 import: {name}")
_SANDBOX["__import__"] = _imp

def run_pal(text):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    code = m.group(1) if m else text
    code = re.sub(r"^\s*import\s+math\s*$", "", code, flags=re.M)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, {"math": math, "__builtins__": dict(_SANDBOX), "__import__": _imp})
        return buf.getvalue().strip(), None
    except Exception as e:
        return buf.getvalue().strip(), f"{type(e).__name__}"

def num_ok(out, gold):
    m = re.findall(r"-?\d+(?:\.\d+)?", str(out) or "")
    if not m: return False
    try: return abs(float(m[-1]) - float(gold)) < 0.06
    except: return False

MODELS = [("glm-4-flash", None), ("glm-5", {"type": "disabled"})]
STRATS = ["zero-direct", "zero-cot", "few-cot", "pal", "persona-老师"]

def build(strat, q):
    if strat == "zero-direct": return f"{q}\n只输出最终答案数字。"
    if strat == "zero-cot": return f"{q}\n请一步一步思考，最后写'答案是：X'。"
    if strat == "few-cot": return FEWSHOT_COT + f"Q：{q}\n推理："
    if strat == "pal": return PAL_PROMPT.format(q=q)
    return PERSONAS["数学老师"] + "\n题目：" + q

res = {"meta": {"tasks": 8}, "matrix": {}, "persona": {}, "pal_errors": []}

# ① 策略 × 模型矩阵
for model, thinking in MODELS:
    key = model + ("[think_off]" if thinking else "")
    res["matrix"][key] = {}
    print(f"== {key}", flush=True)
    for strat in STRATS:
        ok = 0
        for tid, q, gf in TASKS:
            gold = gf()
            r = glm(model, build(strat, q), max_tokens=1024, temperature=0.1, thinking=thinking, retries=1)
            if strat == "pal":
                out, err = run_pal(r["content"])
                if err: res["pal_errors"].append((tid, err))
            else:
                out = r["content"]
            ok += num_ok(out, gold)
        res["matrix"][key][strat] = ok / len(TASKS)
        print(f"  {strat:14s} {ok}/8", flush=True)
        time.sleep(0.1)

# ② Persona 专项（glm-4-flash）
print("== Persona 专项", flush=True)
for pname, prefix in PERSONAS.items():
    ok = 0; steps = 0
    for tid, q, gf in TASKS:
        gold = gf()
        instr = (prefix + "\n题目：" + q) if prefix else (q + "\n请一步步思考，最后写'答案是：X'。")
        r = glm("glm-4-flash", instr, max_tokens=1024, temperature=0.1, retries=1)
        out = r["content"]
        ok += num_ok(out, gold)
        steps += len([l for l in out.splitlines() if "=" in l])
    res["persona"][pname] = {"acc": ok / len(TASKS), "avg_steps": steps / len(TASKS)}
    print(f"  [{pname}] acc {ok}/8 平均推理行 {steps/len(TASKS):.1f}", flush=True)

save("e11_math", res)

# ---- 可视化 ----
import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.2))
keys = list(res["matrix"]); strats = STRATS
x = np.arange(len(strats)); w = 0.35
for i, k in enumerate(keys):
    axes[0].bar(x + (i-0.5)*w, [res["matrix"][k][s] for s in strats], w, label=k)
axes[0].set_xticks(x); axes[0].set_xticklabels([s.replace("-", "\n") for s in strats], fontsize=8)
axes[0].set_ylabel("8题准确率"); axes[0].legend(fontsize=8); axes[0].set_ylim(0, 1.1)
axes[0].set_title("① 策略矩阵：哪种 prompt 在数学上收益最大")
pn = list(res["persona"])
acc = [res["persona"][p]["acc"] for p in pn]
stp = [res["persona"][p]["avg_steps"] for p in pn]
ax2 = axes[1]; ax2.bar(pn, acc, color="#4C72B0", width=0.5)
for i, v in enumerate(acc): ax2.text(i, v+0.02, f"{v:.0%}", ha="center")
ax2.set_ylim(0, 1.1); ax2.set_ylabel("准确率", color="#4C72B0")
ax3 = ax2.twinx(); ax3.plot(pn, stp, "o-", color="#C44E52"); ax3.set_ylabel("平均推理行数", color="#C44E52")
ax2.set_title("② Persona 四角色：准确率 vs 过程量（glm-4-flash）")
plt.tight_layout(); plt.savefig("results/e11_math.png", dpi=130)
print("[saved] results/e11_math.png")
