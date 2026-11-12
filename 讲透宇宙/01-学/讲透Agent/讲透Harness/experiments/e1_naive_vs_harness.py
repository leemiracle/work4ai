#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E1 —— 无 harness vs 最小 harness：同模型的可靠性对照（Ch01 核心实验）
=====================================================================
复刻对象：Anthropic 对照实验（无 harness $9/20min 产出不可用 → 全套 harness
$200/6h 产出可玩，walkinglabs 教程转述）的本地微型版——同一颗 Qwen2.5-0.5B：

  Condition A（naive）：一次性要求写完 6 个函数 → 模型自评"是否全部正确"
                       → 我们用真测试 exec 判定真实完成数
  Condition B（harness）：生命周期循环（SELECT→EXECUTE→VERIFY→WRAP UP）
                       逐个任务：生成 → 真测试验证 → 失败则错误回灌重试 1 次 → 记账

度量（幻觉式完成 = false completion 的定义）：
  真实完成率   = exec 测试通过的函数数 / 6
  自称完成     = 模型口头声称的状态
  FCR          = 自称完成 ∧ 真实未完成（naive 组的核心病理）
  harness 的 FCR 恒为 0 —— "测试不过不算完成"（验证即证据）

复现：cd 讲透Harness/experiments && timeout 1500 python3 e1_naive_vs_harness.py
"""
import re, sys, time
from common import local_qwen, save, fig_save, setup_cn_font

# ---------- 任务集（6 个迷你函数，各 2-3 条断言） ----------
TASKS = [
    {"id": "t1", "name": "add",
     "spec": "def add(a, b): 返回 a 与 b 的和",
     "tests": ["add(2,3)==5", "add(-1,1)==0"]},
    {"id": "t2", "name": "rev",
     "spec": "def rev(s): 返回字符串 s 的反转",
     "tests": ["rev('abc')=='cba'", "rev('')==''"]},
    {"id": "t3", "name": "count_vowels",
     "spec": "def count_vowels(s): 返回字符串 s 中元音字母(a/e/i/o/u，不分大小写)的个数",
     "tests": ["count_vowels('hello')==2", "count_vowels('AEIOU')==5"]},
    {"id": "t4", "name": "slugify",
     "spec": "def slugify(s): 把字符串 s 转成 slug——全部小写，空格换成连字符'-'",
     "tests": ["slugify('Hello World')=='hello-world'", "slugify('A B C')=='a-b-c'"]},
    {"id": "t5", "name": "fib",
     "spec": "def fib(n): 返回第 n 个斐波那契数（fib(1)=1, fib(2)=1, fib(3)=2, ...）",
     "tests": ["fib(1)==1", "fib(10)==55"]},
    {"id": "t6", "name": "fizz",
     "spec": "def fizz(n): n 是 3 和 5 的公倍数返回 'FizzBuzz'，只被 3 整除返回 'Fizz'，只被 5 整除返回 'Buzz'，否则返回 str(n)",
     "tests": ["fizz(3)=='Fizz'", "fizz(15)=='FizzBuzz'", "fizz(7)=='7'"]},
]

def extract_code(text):
    """取 ```python 代码块；没有围栏就取全文。"""
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return m[0] if m else text

def run_tests(code, task):
    """真验证（V2 级）：exec + 断言。返回 (passed: bool, err: str)。"""
    try:
        ns = {}
        exec(code, ns)  # 迷你玩具代码，受控沙箱
        for t in task["tests"]:
            assert eval(t, ns), f"断言失败: {t}"
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

# ---------- Condition A：naive 单发 ----------
def naive_run():
    t0 = time.time()
    spec = "\n".join(f"{t['id']}. {t['spec']}" for t in TASKS)
    prompt = (f"请一次性实现下面 {len(TASKS)} 个 Python 函数：\n{spec}\n\n"
              "要求：全部写在一个 ```python 代码块里，只写代码不要解释。")
    out = local_qwen(prompt, max_new_tokens=512, temperature=0.0)
    code = extract_code(out)
    results = {}
    for t in TASKS:
        ok, err = run_tests(code, t)
        results[t["id"]] = {"pass": ok, "err": err[:120]}
    true_pass = sum(r["pass"] for r in results.values())
    # 自评（naive 的完成判定 = 模型说了算）
    self_ask = ("下面是刚生成的代码：\n```python\n" + code[:1500] + "\n```\n"
                "这 6 个函数（add/rev/count_vowels/slugify/fib/fizz）能全部正确通过各自的测试吗？"
                "只回答 ALL_CORRECT 或 HAS_BUG。")
    self_out = local_qwen(self_ask, max_new_tokens=8, temperature=0.0).upper()
    claimed_done = "ALL_CORRECT" in self_out
    calls = 2
    return {"true_pass": true_pass, "per_task": results,
            "claimed_done": claimed_done, "self_say": self_out.strip()[:30],
            "llm_calls": calls, "wall_s": round(time.time() - t0, 1)}

# ---------- Condition B：最小 harness 生命周期 ----------
def harness_run(max_retries=1):
    t0 = time.time()
    feature_list = {t["id"]: "pending" for t in TASKS}   # S：任务账本
    progress = []                                        # S：证据账本
    calls = 0
    for t in TASKS:                                      # SELECT：逐个取 pending
        done, err = False, ""
        for attempt in range(1 + max_retries):           # EXECUTE + VERIFY + 失败回灌
            fb = "" if attempt == 0 else f"\n上次实现未通过验证，错误信息：\n{err}\n请修复。"
            prompt = (f"实现一个 Python 函数：{t['spec']}\n"
                      f"它必须通过这些测试：{'; '.join(t['tests'])}{fb}\n"
                      "只写这一个函数，放在一个 ```python 代码块里，不要解释。")
            out = local_qwen(prompt, max_new_tokens=224, temperature=0.0)
            calls += 1
            done, err = run_tests(extract_code(out), t)
            if done:
                break
        feature_list[t["id"]] = "done" if done else "failed"   # WRAP UP：记账
        progress.append({"id": t["id"], "pass": done,
                         "evidence": "tests green" if done else err[:120],
                         "attempts": attempt + 1})
    true_pass = sum(p["pass"] for p in progress)
    return {"true_pass": true_pass, "feature_list": feature_list, "progress": progress,
            "claimed_done": true_pass == len(TASKS),   # 验证即证据：账本即真相
            "llm_calls": calls, "wall_s": round(time.time() - t0, 1)}

# ---------- 主流程 ----------
if __name__ == "__main__":
    print("== Condition A: naive =="); A = naive_run();  print(A["true_pass"], "passed; claimed:", A["claimed_done"])
    print("== Condition B: harness =="); B = harness_run(); print(B["true_pass"], "passed;", B["llm_calls"], "calls")

    A["fcr"] = A["claimed_done"] and A["true_pass"] < len(TASKS)   # 幻觉式完成
    B["fcr"] = False                                               # 验证即证据 ⇒ 结构性为 0
    summary = {
        "meta": {"model": "Qwen2.5-0.5B-Instruct (local, CPU, thread=1, temp=0)",
                 "n_tasks": len(TASKS), "date": "2026-08-26"},
        "naive": A, "harness": B,
        "readout": {
            "真实完成数 naive→harness": f"{A['true_pass']}→{B['true_pass']}",
            "完成判定 naive": "模型自评(口头)" if A["claimed_done"] else "模型自评(口头，自称有bug)",
            "幻觉式完成 FCR naive": A["fcr"],
            "幻觉式完成 FCR harness": "结构性 0（测试不过不算完成）",
            "调用次数 naive→harness": f"{A['llm_calls']}→{B['llm_calls']}",
        },
    }
    save("e1_naive_vs_harness", summary)

    # ---------- 图 ----------
    setup_cn_font()
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    x = np.arange(2)
    labels = ["naive\n(无harness)", "harness\n(生命周期+真验证)"]
    # 左图：真实 vs 自称
    axes[0].bar(x - 0.18, [A["true_pass"], B["true_pass"]], 0.36, label="真实完成数(测试exec)", color="#2a9d8f")
    claimed = [len(TASKS) if A["claimed_done"] else 0, len(TASKS) if B["claimed_done"] else 0]
    axes[0].bar(x + 0.18, claimed, 0.36, label="自称完成数(口头)", color="#e9c46a")
    axes[0].set_xticks(x); axes[0].set_xticklabels(labels)
    axes[0].set_ylabel("函数数 / 6"); axes[0].set_ylim(0, 6.8)
    axes[0].set_title("真实 vs 自称：幻觉式完成缺口" + ("（naive 出现 FCR！）" if A["fcr"] else ""))
    if A["fcr"]:
        axes[0].annotate("幻觉式完成：\n自称6/6 实际%d/6" % A["true_pass"],
                         xy=(0.18, 6), xytext=(0.5, 6.3), fontsize=9, color="#d62828",
                         arrowprops=dict(arrowstyle="->", color="#d62828"))
    axes[0].legend(fontsize=8)
    # 右图：FCR 与调用成本
    fcr = [100.0 if A["fcr"] else 0.0, 0.0]
    axes2 = axes[1].twinx()
    axes[1].bar(x, [A["llm_calls"], B["llm_calls"]], 0.5, color="#457b9d", label="LLM调用数")
    axes[1].set_ylabel("LLM 调用数（成本）"); axes[1].set_xticks(x); axes[1].set_xticklabels(labels)
    axes2.bar(x + 0.0, fcr, 0.18, color="#d62828", label="FCR %")
    axes2.set_ylabel("幻觉式完成率 FCR (%)", color="#d62828"); axes2.set_ylim(0, 120)
    axes[1].set_title("成本与可靠性：harness 用 %.1f× 调用买回可靠性" % (B["llm_calls"] / max(A["llm_calls"], 1)))
    h1, l1 = axes[1].get_legend_handles_labels(); h2, l2 = axes2.get_legend_handles_labels()
    axes[1].legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
    fig.suptitle("E1 同一颗 Qwen2.5-0.5B：无 harness vs 最小 harness（Agent = Model + Harness）", fontsize=11)
    fig_save(fig, "e1_naive_vs_harness")
    print("\n== readout =="); print(summary["readout"])
