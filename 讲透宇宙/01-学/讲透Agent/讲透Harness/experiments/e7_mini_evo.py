#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E7 —— mini-Evo 外环：harness 配置的贪心搜索与 train/held-out gap（Ch09 核心实验）
====================================================================================
AHE（arXiv:2604.25850）的本地微型版：harness 优化 harness。
AHE 消融实证 harness 超参对模型过拟合（同家族非单调）——本实验复现这个现象的
最小形态：贪心搜索到的"训练集最优配置"在 held-out 上是否仍然最优？

配置空间（harness 超参，模型完全不动）：
  retries  ∈ {0, 1, 2}          —— V 组件：失败重试预算
  feedback ∈ {raw, guided}      —— C 组件：错误回灌样式
    raw     = "上次验证未通过：{err}。请修复。"
    guided  = raw + "先对照测试逐个参数手动演算一遍期望值，再写代码。"

任务池 8 个（train: t1-t4 / held-out: t5-t8）
流程（贪心 hill-climbing，AHE 的"估→提取特征→优化"骨架）：
  baseline=(1, raw) → 扫 retries 轴 {0,1,2} 取最优 → 扫 feedback 轴 {raw,guided} 取最优
  → 终配置 vs baseline 在 held-out 上对决

度量：train 最优配置的 held-out 表现 vs baseline 的 held-out 表现（gap = 过拟合信号）
搜索日志全记录（= AHE 的进化轨迹）

复现：cd 讲透Harness/experiments && timeout 1400 python3 e7_mini_evo.py
"""
import re, time
from common import local_qwen, save, fig_save, setup_cn_font

TASKS = [
    {"id": "t1", "name": "add", "spec": "def add(a, b): 返回 a 与 b 的和",
     "tests": ["add(2,3)==5", "add(-1,1)==0"]},
    {"id": "t2", "name": "rev", "spec": "def rev(s): 返回字符串 s 的反转",
     "tests": ["rev('abc')=='cba'", "rev('')==''"]},
    {"id": "t3", "name": "count_vowels", "spec": "def count_vowels(s): 返回 s 中元音(a/e/i/o/u，不分大小写)个数",
     "tests": ["count_vowels('hello')==2", "count_vowels('AEIOU')==5"]},
    {"id": "t4", "name": "slugify", "spec": "def slugify(s): 全部小写，空格换成连字符'-'",
     "tests": ["slugify('Hello World')=='hello-world'", "slugify('A B C')=='a-b-c'"]},
    {"id": "t5", "name": "fib", "spec": "def fib(n): 第 n 个斐波那契数（fib(1)=1, fib(2)=1）",
     "tests": ["fib(1)==1", "fib(10)==55"]},
    {"id": "t6", "name": "fizz", "spec": "def fizz(n): 3和5公倍数'FizzBuzz'，3整除'Fizz'，5整除'Buzz'，否则str(n)",
     "tests": ["fizz(3)=='Fizz'", "fizz(15)=='FizzBuzz'", "fizz(7)=='7'"]},
    {"id": "t7", "name": "is_pal", "spec": "def is_pal(s): 字符串 s 是否回文（正读反读相同）",
     "tests": ["is_pal('racecar')==True", "is_pal('ab')==False"]},
    {"id": "t8", "name": "uniq_sorted", "spec": "def uniq_sorted(lst): 去重并升序排序，返回新列表",
     "tests": ["uniq_sorted([3,1,3,2])==[1,2,3]", "uniq_sorted([])==[]"]},
]
TRAIN, HELDOUT = TASKS[:4], TASKS[4:]

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

def fb_text(style, err):
    base = f"\n上次验证未通过：{err}\n请修复。"
    if style == "raw":
        return base
    return base + "\n先对照测试逐个参数手动演算一遍期望值，再写代码。"

def eval_config(retries, fb_style, tasks, tag=""):
    """一个 harness 配置在一组任务上的成绩（模型/温度/seed 全不动）。"""
    passed, calls = 0, 0
    per = {}
    for t in tasks:
        err, ok = None, False
        for attempt in range(1 + retries):
            fb = "" if err is None else fb_text(fb_style, err)
            prompt = (f"实现一个 Python 函数：{t['spec']}\n"
                      f"它必须通过这些测试：{'; '.join(t['tests'])}{fb}\n"
                      "只写这一个函数，放在一个 ```python 代码块里。")
            out = local_qwen(prompt, max_new_tokens=176, temperature=0.0)
            calls += 1
            ok, err = run_tests(extract_code(out), t)
            if ok:
                break
        passed += ok
        per[t["id"]] = ok
    score = passed / len(tasks)
    print(f"  [{tag}] retries={retries} fb={fb_style:6s} → {passed}/{len(tasks)} "
          f"({calls} calls)", flush=True)
    return {"retries": retries, "fb": fb_style, "score": score, "calls": calls, "per": per}

if __name__ == "__main__":
    t0 = time.time()
    search_log = []

    print("== Phase 1: 贪心搜索（train t1-t4）==", flush=True)
    base = eval_config(1, "raw", TRAIN, "baseline")
    search_log.append({"step": "baseline", "cfg": (1, "raw"), "score": base["score"]})

    best_r, best_s = base["retries"], base["score"]
    for r in (0, 2):                                  # 1 已由 baseline 覆盖
        c = eval_config(r, "raw", TRAIN, f"scan-retries")
        search_log.append({"step": "scan-retries", "cfg": (r, "raw"), "score": c["score"]})
        if c["score"] > best_s:
            best_r, best_s = r, c["score"]

    best_fb, best_s2 = "raw", best_s
    for fb in ("guided",):                            # raw 已覆盖
        c = eval_config(best_r, fb, TRAIN, "scan-feedback")
        search_log.append({"step": "scan-feedback", "cfg": (best_r, fb), "score": c["score"]})
        if c["score"] > best_s2:
            best_fb, best_s2 = fb, c["score"]

    chosen = (best_r, best_fb)
    print(f"\n== 终配置: {chosen}（train {best_s2:.0%}）==\n", flush=True)

    print("== Phase 2: held-out 对决（t5-t8）==", flush=True)
    chosen_ho = eval_config(*chosen, HELDOUT, "chosen-heldout")
    base_ho = eval_config(1, "raw", HELDOUT, "baseline-heldout")

    gap = chosen_ho["score"] - base_ho["score"]
    summary = {
        "meta": {"model": "Qwen2.5-0.5B (local CPU, temp=0, seed 固定)",
                 "note": "贪心搜索与 held-out 用同模型同 seed——差异全部来自 harness 配置",
                 "date": "2026-08-26"},
        "search_log": search_log, "chosen_cfg": chosen,
        "train": {"baseline": base["score"], "chosen": best_s2},
        "heldout": {"baseline": base_ho["score"], "chosen": chosen_ho["score"]},
        "gap": gap,
        "readout": {
            "train": f"baseline {base['score']:.0%} → chosen {best_s2:.0%}",
            "heldout": f"baseline {base_ho['score']:.0%} vs chosen {chosen_ho['score']:.0%}（gap {gap:+.0%}）",
            "结论": ("gap ≤ 0 ⇒ 搜索收益不迁移 = AHE『harness 超参对模型/任务过拟合』的本地证据；"
                     "gap > 0 ⇒ 本任务族上配置可迁移（样本极小，诚实标注噪声）"),
            "对照": "AHE 同家族非单调（medium+2.3/high+7.3/xhigh+2.3，2604.25850）",
        },
        "wall_s": round(time.time() - t0, 1),
    }
    save("e7_mini_evo", summary)

    setup_cn_font()
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    # 左：搜索轨迹
    steps = [f"{s['step']}\n{tuple(s['cfg'])}" for s in search_log]
    scores = [s["score"] * 100 for s in search_log]
    axes[0].plot(range(len(scores)), scores, "o-", color="#457b9d")
    for i, s in enumerate(scores):
        axes[0].text(i, s + 3, f"{s:.0f}", ha="center", fontsize=8)
    axes[0].set_xticks(range(len(steps))); axes[0].set_xticklabels(steps, fontsize=7)
    axes[0].set_ylabel("train 得分 %"); axes[0].set_ylim(0, 118)
    axes[0].set_title("贪心搜索轨迹（AHE 外环微型版）")
    # 右：train vs heldout
    x = np.arange(2)
    axes[1].bar(x - 0.18, [base["score"] * 100, base_ho["score"] * 100], 0.36,
                label="baseline (1, raw)", color="#999")
    axes[1].bar(x + 0.18, [best_s2 * 100, chosen_ho["score"] * 100], 0.36,
                label=f"chosen {tuple(chosen)}", color="#2a9d8f")
    axes[1].set_xticks(x); axes[1].set_xticklabels(["train (t1-t4)", "held-out (t5-t8)"])
    axes[1].set_ylim(0, 118); axes[1].set_ylabel("得分 %")
    axes[1].set_title(f"train→held-out gap = {gap:+.0%}（过拟合信号）")
    axes[1].legend(fontsize=8)
    fig.suptitle("E7 mini-Evo：harness 配置搜索的收益是否迁移（AHE 2604.25850 本地版）", fontsize=11)
    fig_save(fig, "e7_mini_evo")
    print("\n== readout =="); print(summary["readout"])
