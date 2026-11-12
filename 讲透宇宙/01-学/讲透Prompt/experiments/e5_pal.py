#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E5 PAL 实验：程序辅助提示（Gao et al. 2022, 2211.10435）
==================================================================================
问题：LLM 心算不可靠时，让它"写代码"而不是"写推理"能不能救？
设计：5 道"CoT 心算高风险"题（大数/日期/连续百分比/尾零），两条件对比：
  a) zero-cot ：一步步思考（纯心算）
  b) pal      ：写 Python 代码，沙箱 exec 取 print 结果
答案全部由 Python 运行时计算（不手写金标准）。
沙箱：白名单 builtins + 预载 math/itertools/datetime，禁 import/os/open —— 顺带演示 PAL 的安全边界。
产出：results/e5_pal.json + e5_pal.png
"""
from common import glm, save
import re, io, time, contextlib, math, itertools, datetime

def gold_answers():
    return {}

TASKS = [
    # (id, 题目, 求解函数) —— gold 由本地 Python 算出，杜绝手滑
    ("t1_date", "已知2026年8月26日是星期三。请问2026年10月1日是星期几？请用中文星期几作答。",
     lambda: ["一","二","三","四","五","六","日"][datetime.date(2026,10,1).weekday()]),
    ("t2_big", "123456789 乘以 987654321，乘积的各位数字之和是多少？",
     lambda: sum(int(d) for d in str(123456789 * 987654321))),
    ("t3_pct", "一件商品原价999元，连续三天每天在前一天基础上涨价3.3%。三天后价格是多少元？保留两位小数。",
     lambda: round(999 * 1.033 ** 3, 2)),
    ("t4_perm", "7个人排成一排照相，其中甲、乙、丙三人必须相邻。共有多少种不同排法？",
     lambda: math.factorial(5) * math.factorial(3)),
    ("t5_zero", "100的阶乘（100!）末尾有多少个连续的零？",
     lambda: sum(100 // 5**k for k in range(1, 7))),
]

COT_PROMPT = "{q}\n请一步一步思考，最后单独一行写'答案是：X'。"
PAL_PROMPT = ("请写一段 Python 代码解决下面的问题，用 print 输出最终答案（一个数或字符串）。\n"
              "只能用 math / itertools / datetime 这三个已导入的库，不要 import 其他东西，不要输入函数。\n"
              "只输出一个 ```python 代码块，不要解释。\n问题：{q}")

import builtins as _b
_ALLOWED_MODS = {"math", "itertools", "datetime"}
def _sandbox_import(name, *a, **k):
    if name.partition(".")[0] in _ALLOWED_MODS:
        return _b.__import__(name, *a, **k)
    raise ImportError(f"沙箱禁用 import: {name!r}（仅允许 {sorted(_ALLOWED_MODS)}）")
SANDBOX_BUILTINS = {n: getattr(_b, n) for n in
                    ("abs", "range", "sum", "len", "min", "max", "int", "float", "str",
                     "sorted", "enumerate", "round", "list", "dict", "set", "tuple", "print")}
SANDBOX_BUILTINS["__import__"] = _sandbox_import
SANDBOX_GLOBALS = {"math": math, "itertools": itertools, "datetime": datetime,
                   "__builtins__": SANDBOX_BUILTINS}

def run_pal_code(text):
    """提取 ```python 块（或裸代码）→ 沙箱 exec（白名单 __import__ + 20s alarm 防死循环）→ 捕获 print。"""
    import signal
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    code = m.group(1) if m else text
    buf = io.StringIO()
    def _timeout(signum, frame): raise TimeoutError("沙箱 20s 超时（疑似死循环）")
    old = signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(20)
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, dict(SANDBOX_GLOBALS))
        return buf.getvalue().strip(), None
    except Exception as e:
        return buf.getvalue().strip(), f"{type(e).__name__}: {e}"
    finally:
        signal.alarm(0); signal.signal(signal.SIGALRM, old)

def extract_num(s):
    m = re.findall(r"-?\d+(?:\.\d+)?", s or "")
    return m[-1] if m else None

def weekday_ok(s, gold):
    return gold in (s or "")[-4:]

res = {"meta": {"model": "glm-4-flash"}, "acc": {"zero_cot": 0, "pal": 0}, "detail": []}

for tid, q, goldf in TASKS:
    gold = goldf()
    # a) zero-cot
    r = glm("glm-4-flash", COT_PROMPT.format(q=q), max_tokens=512, temperature=0.1, retries=1)
    cot_out = r["content"]
    cot_pred = None
    if tid == "t1_date":
        cot_ok = weekday_ok(cot_out, str(gold)); cot_pred = cot_out[-4:]
    else:
        cot_pred = extract_num(cot_out.split("答案")[-1])
        try: cot_ok = cot_pred and abs(float(cot_pred) - float(gold)) < 0.01
        except: cot_ok = False
    # b) PAL
    r2 = glm("glm-4-flash", PAL_PROMPT.format(q=q), max_tokens=512, temperature=0.1, retries=1)
    pal_out, pal_err = run_pal_code(r2["content"])
    if tid == "t1_date":
        pal_ok = weekday_ok(pal_out, str(gold)); pal_pred = pal_out[-4:]
    else:
        pal_pred = extract_num(pal_out)
        try: pal_ok = not pal_err and pal_pred and abs(float(pal_pred) - float(gold)) < 0.01
        except: pal_ok = False
    res["acc"]["zero_cot"] += bool(cot_ok); res["acc"]["pal"] += bool(pal_ok)
    res["detail"].append({"id": tid, "q": q[:20], "gold": str(gold),
                          "cot_pred": str(cot_pred)[:20], "cot_ok": bool(cot_ok),
                          "pal_pred": str(pal_pred)[:20], "pal_ok": bool(pal_ok),
                          "pal_err": pal_err})
    print(f"  [{tid}] gold={gold} | CoT {cot_ok}({str(cot_pred)[:12]}) | PAL {pal_ok}({str(pal_pred)[:12]}) {pal_err or ''}", flush=True)
    time.sleep(0.2)

for k in res["acc"]: res["acc"][k] /= len(TASKS)
print(f"== zero-cot {res['acc']['zero_cot']:.0%} vs PAL {res['acc']['pal']:.0%}", flush=True)
save("e5_pal", res)

import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Noto Sans CJK SC"
fig, ax = plt.subplots(figsize=(6.5, 4))
ks = ["zero_cot", "pal"]
ax.bar(["零样本 CoT\n（心算）", "PAL\n（写代码+沙箱执行）"], [res["acc"][k] for k in ks],
       color=["#4C72B0", "#55A868"], width=0.5)
for i, k in enumerate(ks):
    ax.text(i, res["acc"][k] + 0.03, f"{res['acc'][k]:.0%}", ha="center")
ax.set_ylabel("5题准确率"); ax.set_ylim(0, 1.15)
ax.set_title("E5 PAL：把'推理'外包给 Python 解释器"); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.savefig("results/e5_pal.png", dpi=130)
print("[saved] results/e5_pal.png")
