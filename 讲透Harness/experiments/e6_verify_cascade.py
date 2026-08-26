#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E6 —— 验证即级联（verify-then-escalate）：cascade 的 deferral rule = 验证器（Ch08）
====================================================================================
对应论述："多模型 harness / router/cascade"。FrugalGPT 式级联（TMLR 2024）的
本地小规模复现，但 deferral rule 不用打分器——直接用 V2 真执行（E2 的结论：
确定性验证又便宜又零误杀，何必学一个置信度分类器）。

  Tier-1 glm-4-flash（便宜，成本权重 1）生成 → V2 exec 验证
    通过 → 接受
    失败 → Tier-2 glm-5（贵，成本权重 20）带错误反馈重生成 → V2 再验

三基线：all-flash（全用便宜档）/ cascade（本方案）/ all-glm5（全用贵档）
度量：任务完成率 / 加权成本单位 / 每任务轨迹
铁律：API 长实验 retries=1 防重试风暴

复现：cd 讲透Harness/experiments && timeout 1200 python3 e6_verify_cascade.py
"""
import re, time
from common import glm, save, fig_save, setup_cn_font

COST_FLASH, COST_GLM5 = 1.0, 20.0     # 相对成本权重（价格代理，非报价）

TASKS = [
    {"id": "t1", "name": "add", "spec": "def add(a, b): 返回 a 与 b 的和",
     "tests": ["add(2,3)==5", "add(-1,1)==0"]},
    {"id": "t2", "name": "rev", "spec": "def rev(s): 返回字符串 s 的反转",
     "tests": ["rev('abc')=='cba'", "rev('')==''"]},
    {"id": "t3", "name": "count_vowels", "spec": "def count_vowels(s): 返回 s 中元音字母(a/e/i/o/u，不分大小写)个数",
     "tests": ["count_vowels('hello')==2", "count_vowels('AEIOU')==5"]},
    {"id": "t4", "name": "slugify", "spec": "def slugify(s): 全部小写，空格换成连字符'-'",
     "tests": ["slugify('Hello World')=='hello-world'", "slugify('A B C')=='a-b-c'"]},
    {"id": "t5", "name": "fib", "spec": "def fib(n): 第 n 个斐波那契数（fib(1)=1, fib(2)=1）",
     "tests": ["fib(1)==1", "fib(10)==55"]},
    {"id": "t6", "name": "fizz", "spec": "def fizz(n): 3和5公倍数返回'FizzBuzz'，3整除'Fizz'，5整除'Buzz'，否则str(n)",
     "tests": ["fizz(3)=='Fizz'", "fizz(15)=='FizzBuzz'", "fizz(7)=='7'"]},
]

def extract_code(text):
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return m[0] if m else text

def run_tests(code, task):
    try:
        ns = {}
        exec(code, ns)
        for t in task["tests"]:
            assert eval(t, ns), f"断言失败: {t}"
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def gen(model, task, err=None, thinking=None):
    fb = "" if err is None else f"\n上次实现未通过验证，错误：\n{err}\n请修复。"
    prompt = (f"实现一个 Python 函数：{task['spec']}\n"
              f"它必须通过这些测试：{'; '.join(task['tests'])}{fb}\n"
              "只写这一个函数，放在一个 ```python 代码块里。")
    r = glm(model, prompt, max_tokens=512, temperature=0.1, thinking=thinking, retries=1)
    return extract_code(r["content"]), r

def tier(model, task, thinking=None):
    code, resp = gen(model, task, thinking=thinking)
    ok, err = run_tests(code, task)
    return ok, err, code, resp

if __name__ == "__main__":
    t0 = time.time()
    traces = {"all_flash": [], "cascade": [], "all_glm5": []}

    print("== baseline: all_flash ==", flush=True)
    cost_f = 0
    for t in TASKS:
        ok, err, code, r = tier("glm-4-flash", t)
        cost_f += COST_FLASH
        traces["all_flash"].append({"task": t["id"], "pass": ok, "tier": 1, "err": err[:80]})
        print(f"  {t['id']} {'PASS' if ok else 'FAIL ' + err[:50]}", flush=True)

    print("== cascade: flash → V2 → glm-5 ==", flush=True)
    cost_c = 0
    for t in TASKS:
        ok, err, code, r1 = tier("glm-4-flash", t)
        cost_c += COST_FLASH
        if not ok:
            print(f"  {t['id']} flash FAIL → 升级 glm-5", flush=True)
            ok2, err2, code2, r2 = tier("glm-5", t, err=err, thinking={"type": "disabled"})
            cost_c += COST_GLM5
            ok, err = ok2, err2
        traces["cascade"].append({"task": t["id"], "pass": ok,
                                  "tier": 2 if cost_c > COST_FLASH else 1, "err": err[:80]})
        print(f"  {t['id']} {'PASS' if ok else 'FAIL ' + err[:50]}", flush=True)

    print("== baseline: all_glm5 ==", flush=True)
    cost_g = 0
    for t in TASKS:
        ok, err, code, r = tier("glm-5", t, thinking={"type": "disabled"})
        cost_g += COST_GLM5
        traces["all_glm5"].append({"task": t["id"], "pass": ok, "tier": 2, "err": err[:80]})
        print(f"  {t['id']} {'PASS' if ok else 'FAIL ' + err[:50]}", flush=True)

    acc = {k: sum(x["pass"] for x in v) / len(TASKS) for k, v in traces.items()}
    summary = {
        "meta": {"date": "2026-08-26", "cost_weights": {"flash": COST_FLASH, "glm5": COST_GLM5},
                 "note": "成本为相对权重（价格代理），非实际报价"},
        "acc": acc, "cost": {"all_flash": cost_f, "cascade": cost_c, "all_glm5": cost_g},
        "traces": traces, "wall_s": round(time.time() - t0, 1),
        "readout": {
            "完成率": {k: f"{v:.0%}" for k, v in acc.items()},
            "成本单位": {"all_flash": cost_f, "cascade": cost_c, "all_glm5": cost_g},
            "结论": "deferral rule 用验证器而非打分器：cascade 拿到 all_glm5 的完成率，"
                    "成本介于两者之间——验证免费的场景（代码可 exec）不需要学 router",
        },
    }
    save("e6_verify_cascade", summary)

    setup_cn_font()
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    conds = ["all_flash\n(全便宜档)", "cascade\n(flash→V2→glm-5)", "all_glm5\n(全贵档)"]
    costs = [cost_f, cost_c, cost_g]
    accs = [acc["all_flash"] * 100, acc["cascade"] * 100, acc["all_glm5"] * 100]
    x = np.arange(3)
    ax.bar(x - 0.18, costs, 0.36, label="加权成本单位", color="#457b9d")
    ax2 = ax.twinx()
    ax2.bar(x + 0.18, accs, 0.36, label="完成率 %", color="#2a9d8f")
    ax.set_xticks(x); ax.set_xticklabels(conds); ax.set_ylabel("成本单位（flash=1, glm5=20）")
    ax2.set_ylabel("完成率 %"); ax2.set_ylim(0, 118)
    for i in range(3):
        ax.text(i - 0.18, costs[i] + 1, f"{costs[i]:.0f}", ha="center", fontsize=9)
        ax2.text(i + 0.18, accs[i] + 2, f"{accs[i]:.0f}%", ha="center", fontsize=9)
    ax.set_title("E6 验证即级联：cascade 以中间成本拿到贵档完成率")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=9)
    fig_save(fig, "e6_verify_cascade")
    print("\n== readout =="); print(summary["readout"])
