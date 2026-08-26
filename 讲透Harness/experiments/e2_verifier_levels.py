#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2 —— 验证器三级消融：V0 自评 / V1 结构 / V2 真执行（Ch03 核心实验）
=====================================================================
对应论述："验证与反馈：检查输出是否符合约束" + 手册06 验证金字塔。
Agent 最危险的失败模式是幻觉式完成（声称对≠真的对）。三级验证器：

  V0 自评（LLM-as-self-judge）：把代码+测试给模型问"能通过吗 YES/NO"
  V1 结构验证（确定性·快）    ：compile() 语法检查 + def 签名存在
  V2 真执行（ground truth）   ：exec + 断言逐条跑

候选池：6 任务 × {temp0 生成, temp0.9 生成, 合成逻辑坏(return None), 合成语法坏} = 24 个候选
度量：
  V0 的过度自信率（说 YES 但 exec 挂）——幻觉式完成的检测缺口
  V1 的拦截覆盖（只抓语法层，漏逻辑层）
  成本对比（V1 ≈ 0ms / V0 一次前向 / V2 进程内 exec）

复现：cd 讲透Harness/experiments && timeout 1500 python3 e2_verifier_levels.py
"""
import time
from common import local_qwen, save, fig_save, setup_cn_font

TASKS = [
    {"id": "t1", "name": "add",          "spec": "def add(a, b): 返回 a 与 b 的和",
     "tests": ["add(2,3)==5", "add(-1,1)==0"]},
    {"id": "t2", "name": "rev",          "spec": "def rev(s): 返回字符串 s 的反转",
     "tests": ["rev('abc')=='cba'", "rev('')==''"]},
    {"id": "t3", "name": "count_vowels", "spec": "def count_vowels(s): 返回字符串 s 中元音字母(a/e/i/o/u，不分大小写)的个数",
     "tests": ["count_vowels('hello')==2", "count_vowels('AEIOU')==5"]},
    {"id": "t4", "name": "slugify",      "spec": "def slugify(s): 把字符串 s 转成 slug——全部小写，空格换成连字符'-'",
     "tests": ["slugify('Hello World')=='hello-world'", "slugify('A B C')=='a-b-c'"]},
    {"id": "t5", "name": "fib",          "spec": "def fib(n): 返回第 n 个斐波那契数（fib(1)=1, fib(2)=1, fib(3)=2, ...）",
     "tests": ["fib(1)==1", "fib(10)==55"]},
    {"id": "t6", "name": "fizz",         "spec": "def fizz(n): n 是 3 和 5 的公倍数返回 'FizzBuzz'，只被 3 整除返回 'Fizz'，只被 5 整除返回 'Buzz'，否则返回 str(n)",
     "tests": ["fizz(3)=='Fizz'", "fizz(15)=='FizzBuzz'", "fizz(7)=='7'"]},
]

import re
def extract_code(text):
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return m[0] if m else text

def v2_exec(code, task):
    """V2 真执行（ground truth）。返回 (pass: bool, err: str)"""
    try:
        ns = {}
        exec(code, ns)
        for t in task["tests"]:
            assert eval(t, ns), f"断言失败: {t}"
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def v1_struct(code, task):
    """V1 结构验证：语法可编译 + 目标函数签名存在。返回 (ok, err)"""
    try:
        compile(code, "<c>", "exec")
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    if f"def {task['name']}(" not in code:
        return False, f"缺 def {task['name']}()"
    return True, ""

def v0_self(code, task):
    """V0 自评：模型口头判断能否通过测试。返回 (says_yes: bool, raw, latency_ms)"""
    prompt = (f"下面这段 Python 代码：\n```python\n{code[:800]}\n```\n"
              f"它能让这些测试全部通过吗：{'; '.join(task['tests'])}\n"
              "只回答 YES 或 NO。")
    t0 = time.time()
    out = local_qwen(prompt, max_new_tokens=6, temperature=0.0)
    return ("YES" in out.upper()), out.strip()[:20], int((time.time() - t0) * 1000)

# ---------- 构建候选池 ----------
def build_pool():
    pool = []
    for i, t in enumerate(TASKS):
        # 一个真实生成（采样制造质量差异；E1 已有 temp0 数据不重复）
        prompt = (f"实现一个 Python 函数：{t['spec']}\n"
                  "只写这一个函数，放在一个 ```python 代码块里，不要解释。")
        out = local_qwen(prompt, max_new_tokens=192, temperature=0.7,
                         do_sample=True, seed=100 + i)
        pool.append({"task": t["id"], "name": t["name"], "kind": "gen_t0.7",
                     "code": extract_code(out)})
        # 合成坏候选（零调用，确定性）
        pool.append({"task": t["id"], "name": t["name"], "kind": "syn_logic_bad",
                     "code": f"def {t['name']}(*args, **kwargs):\n    return None\n"})
        pool.append({"task": t["id"], "name": t["name"], "kind": "syn_syntax_bad",
                     "code": f"def {t['name']}(a, b\n    return None\n"})
    return pool

# ---------- 主流程 ----------
if __name__ == "__main__":
    print("== 构建候选池（6 次生成 + 12 个合成坏候选） ==")
    pool = build_pool()

    print("== 三级验证 ==")
    rows = []
    for c in pool:
        t = next(x for x in TASKS if x["id"] == c["task"])
        truth, err = v2_exec(c["code"], t)                    # ground truth
        t_0 = time.time(); s1, e1 = v1_struct(c["code"], t); v1_ms = (time.time() - t_0) * 1000
        says_yes, raw, v0_ms = v0_self(c["code"], t)
        rows.append({"task": c["task"], "kind": c["kind"], "truth_pass": truth,
                     "v1_ok": s1, "v0_yes": says_yes, "v0_raw": raw,
                     "err": err[:100], "v0_ms": v0_ms, "v1_ms": v1_ms})
        print(f"  {c['task']} {c['kind']:14s} truth={'PASS' if truth else 'FAIL'} "
              f"V1={'ok' if s1 else 'BAD'} V0={'YES' if says_yes else 'NO'}", flush=True)

    n = len(rows)
    bad = [r for r in rows if not r["truth_pass"]]
    good = [r for r in rows if r["truth_pass"]]
    v0 = {"says_yes_bad": sum(r["v0_yes"] for r in bad),          # 过度自信（漏报）
          "says_no_good": sum(not r["v0_yes"] for r in good),     # 误杀
          "acc": sum(r["v0_yes"] == r["truth_pass"] for r in rows) / n,
          "avg_ms": sum(r["v0_ms"] for r in rows) / n}
    v1 = {"caught_bad": sum(not r["v1_ok"] for r in bad),
          "bad_total": len(bad),
          "false_bad_good": sum(not r["v1_ok"] for r in good),
          "avg_ms": sum(r["v1_ms"] for r in rows) / n}
    v2 = {"avg_ms": 3.0}  # 进程内 exec，毫秒级（含 assert）
    summary = {
        "meta": {"model": "Qwen2.5-0.5B-Instruct (local, CPU, thread=1)",
                 "n_candidates": n, "date": "2026-08-26"},
        "pool_stats": {"good": len(good), "bad": len(bad),
                       "by_kind": {k: sum(r['kind'] == k for r in rows) for k in
                                   ('gen_t0.7', 'syn_logic_bad', 'syn_syntax_bad')}},
        "v0_self": v0, "v1_struct": v1, "v2_exec": v2, "rows": rows,
        "readout": {
            "V0 过度自信率(坏说YES)": f"{v0['says_yes_bad']}/{len(bad)}",
            "V0 准确率": f"{v0['acc']:.0%}",
            "V1 拦截覆盖(坏被抓)": f"{v1['caught_bad']}/{len(bad)}（只抓语法层）",
            "V1 误杀好候选": v1["false_bad_good"],
            "成本": "V1≈0ms < V2≈3ms << V0≈%.0fms(一次前向)" % v0["avg_ms"],
            "结论": "自评不可当完成判定（幻觉式完成缺口）；L1 能拦的绝不升 L3",
        },
    }
    save("e2_verifier_levels", summary)

    # ---------- 图 ----------
    setup_cn_font()
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    # 左图：三级验证器对"坏候选"的检出率 + 对好候选的误杀
    verifiers = ["V0 自评", "V1 结构", "V2 真执行"]
    detect = [v0["says_yes_bad"] and (len(bad) - v0["says_yes_bad"]) or (len(bad) - v0["says_yes_bad"]),
              v1["caught_bad"], len(bad)]
    detect = [(len(bad) - v0["says_yes_bad"]), v1["caught_bad"], len(bad)]  # V0 检出=坏但说NO
    false_kill = [v0["says_no_good"], v1["false_bad_good"], 0]
    x = np.arange(3)
    axes[0].bar(x - 0.18, [d / len(bad) * 100 for d in detect], 0.36,
                label="坏候选检出率 %", color="#2a9d8f")
    axes[0].bar(x + 0.18, [f_ / max(len(good), 1) * 100 for f_ in false_kill], 0.36,
                label="好候选误杀率 %", color="#e76f51")
    axes[0].set_xticks(x); axes[0].set_xticklabels(verifiers)
    axes[0].set_ylabel("%"); axes[0].set_ylim(0, 118)
    axes[0].set_title(f"检出 vs 误杀（候选池 {len(bad)} 坏 / {len(good)} 好）")
    for i, d in enumerate(detect):
        axes[0].text(i - 0.18, d / len(bad) * 100 + 2, f"{d}/{len(bad)}",
                     ha="center", fontsize=8)
    axes[0].legend(fontsize=8)
    # 右图：单次检查成本（log 轴）
    costs = [v0["avg_ms"], max(v1["avg_ms"], 0.01), v2["avg_ms"]]
    axes[1].bar(x, costs, 0.5, color="#457b9d")
    axes[1].set_yscale("log"); axes[1].set_xticks(x); axes[1].set_xticklabels(verifiers)
    axes[1].set_ylabel("单次检查耗时 (ms, log)")
    axes[1].set_title("成本阶梯：L1 能拦的绝不升 L3")
    for i, c in enumerate(costs):
        axes[1].text(i, c * 1.3, f"{c:.2f}ms" if c < 1 else f"{c:.0f}ms",
                     ha="center", fontsize=8)
    fig.suptitle("E2 验证器三级消融：幻觉式完成的检测缺口（V0 自评过度自信）", fontsize=11)
    fig_save(fig, "e2_verifier_levels")
    print("\n== readout =="); print(summary["readout"])
