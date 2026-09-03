#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E3 —— 状态与失忆：崩溃恢复的三种条件（Ch04 核心实验）
=====================================================
对应论述："状态持久化：将任务状态保存到外部存储，支持中断恢复" +
walkinglabs 最小四文件（progress.md = 任务账本）。

场景：6 任务会话做完 t1-t3 后"崩溃"（上下文全丢）。重启后三种恢复条件：
  A 无账本（no_ledger）  ：新会话直接问"已完成哪些？下一个做什么？"——只能靠猜
  B 截断窗口（truncated） ：只保留崩溃前最后一轮对话（t3 的实现+验证）——部分状态
  C 账本恢复（ledger）   ：注入 progress.md 内容——设计意图：完整恢复

度量：
  done 集recall（{t1,t2,t3} 的精确恢复率）
  next 选择正确率（应为 t4）
  幻觉内容记录（A/B 条件下模型声称完成了什么）

复现：cd 讲透Harness/experiments && timeout 1500 python3 e3_state_amnesia.py
"""
import re
from common import local_qwen, save, fig_save, setup_cn_font

TASKS = [
    {"id": "t1", "name": "add",          "spec": "def add(a, b): 返回 a 与 b 的和"},
    {"id": "t2", "name": "rev",          "spec": "def rev(s): 返回字符串 s 的反转"},
    {"id": "t3", "name": "count_vowels", "spec": "def count_vowels(s): 返回字符串 s 中元音字母(a/e/i/o/u，不分大小写)的个数"},
    {"id": "t4", "name": "slugify",      "spec": "def slugify(s): 把字符串 s 转成 slug——全部小写，空格换成连字符'-'"},
    {"id": "t5", "name": "fib",          "spec": "def fib(n): 返回第 n 个斐波那契数"},
    {"id": "t6", "name": "fizz",         "spec": "def fizz(n): 3和5公倍数返回FizzBuzz等"},
]
ALL_NAMES = [t["name"] for t in TASKS]
DONE = ["t1", "t2", "t3"]           # 崩溃前真实完成
NEXT = "t4"

def extract_code(text):
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return m[0] if m else text

# ---------- Phase 1：真实跑 t1-t3，攒出真账本 ----------
def phase1():
    ledger_lines, last_exchange = [], ""
    for tid in DONE:
        t = next(x for x in TASKS if x["id"] == tid)
        prompt = (f"实现一个 Python 函数：{t['spec']}\n"
                  "只写这一个函数，放在一个 ```python 代码块里，不要解释。")
        out = local_qwen(prompt, max_new_tokens=224, temperature=0.0)
        code = extract_code(out)
        ok = True  # 只为攒账本；E1 已测过完成率，此处不重复验证
        ledger_lines.append(f"- [{tid}] {t['name']}: done（代码已生成）")
        last_exchange = f"用户: {prompt}\n\n助手: ```python\n{code[:300]}\n```"
    progress_md = "# progress.md\n## 已完成\n" + "\n".join(ledger_lines) + \
                  f"\n\n## 下一个\n- [{NEXT}] slugify（pending）\n- t5 fib（pending）\n- t6 fizz（pending）"
    return progress_md, last_exchange

# ---------- Phase 2：三种条件下的恢复问询 ----------
def ask_recover(cond, progress_md, last_exchange, rep):
    q = ("你在执行一个 6 函数任务会话（任务清单：" + "、".join(ALL_NAMES) + "）。\n"
         "会话刚才中断重启。请回答两件事：\n"
         "1. 已完成哪些函数？（只列函数名，逗号分隔）\n"
         "2. 下一步应该实现哪个函数？（只答一个函数名）")
    if cond == "A_no_ledger":
        prompt = q
    elif cond == "B_truncated":
        prompt = ("你在执行一个 6 函数任务会话（任务清单：" + "、".join(ALL_NAMES) + "）。\n"
                  "会话中断重启，只找回了崩溃前最后一轮对话：\n---\n" + last_exchange[:600] +
                  "\n---\n请回答：1. 已完成哪些函数？（只列函数名）2. 下一步应该实现哪个？（只答一个）")
    else:  # C_ledger
        prompt = ("你在执行一个 6 函数任务会话（任务清单：" + "、".join(ALL_NAMES) + "）。\n"
                  "会话中断重启，读回了任务账本 progress.md：\n---\n" + progress_md +
                  "\n---\n请回答：1. 已完成哪些函数？（只列函数名）2. 下一步应该实现哪个？（只答一个）")
    out = local_qwen(prompt, max_new_tokens=64,
                     temperature=0.3, do_sample=True, seed=7 + rep)
    return out.strip()

def parse_done(text):
    """从回答里抠函数名，与 DONE 名集对比。
    v2 修复（meta 教训：解析器也是 harness 的一部分）：
    只从第 1 问的答案段（'2.'/'下一步' 之前）提取已完成；next 单独从第 2 问段提取。
    v1 的 bug：全文找函数名，把第 2 问里的 next 名也算进 done → 高估幻觉。"""
    names = {"add": "t1", "rev": "t2", "count_vowels": "t3",
             "slugify": "t4", "fib": "t5", "fizz": "t6"}
    # 第 1 问段 = 第一个 "2." 或 "下一步" 之前
    seg1 = re.split(r"2[\.、]\s|下一步", text)[0]
    claimed = {names[n] for n in names if n in seg1}
    return claimed

def parse_next(text):
    """第 2 问段（'下一步' 之后）里第一个出现的函数名。"""
    names = ["slugify", "count_vowels", "add", "rev", "fib", "fizz"]
    seg2 = text[text.find("下一步"):] if "下一步" in text else text
    for n in names:
        if n in seg2:
            return n
    return None

if __name__ == "__main__":
    print("== Phase 1: 真实执行 t1-t3 攒账本 ==")
    progress_md, last_exchange = phase1()
    print(progress_md[:200], "...")

    conds = ["A_no_ledger", "B_truncated", "C_ledger"]
    REPS = 3
    results = {c: [] for c in conds}
    print(f"\n== Phase 2: 崩溃恢复 x {REPS} 次重复 ==")
    for rep in range(REPS):
        for c in conds:
            out = ask_recover(c, progress_md, last_exchange, rep)
            claimed = parse_done(out)
            nxt = parse_next(out)
            true_set = set(DONE)
            recall = len(claimed & true_set) / len(true_set)
            exact = claimed == true_set
            halluc = claimed - true_set
            next_ok = nxt == "slugify"
            results[c].append({"raw": out[:160], "claimed_done": sorted(claimed),
                               "next_choice": nxt,
                               "recall": recall, "exact": exact,
                               "hallucinated": sorted(halluc), "next_ok": next_ok})
            print(f"  [{c}] rep{rep} claimed={sorted(claimed)} exact={exact} next={nxt} ok={next_ok}", flush=True)

    summary = {c: {"done_recall_avg": sum(r["recall"] for r in v) / len(v),
                   "exact_match_rate": sum(r["exact"] for r in v) / len(v),
                   "next_correct_rate": sum(r["next_ok"] for r in v) / len(v),
                   "runs": v} for c, v in results.items()}
    summary["meta"] = {"model": "Qwen2.5-0.5B (local CPU)", "true_done": DONE,
                       "true_next": NEXT, "reps": REPS, "date": "2026-08-26"}
    summary["readout"] = {
        "done精确恢复率": {c: f"{summary[c]['exact_match_rate']:.0%}" for c in conds},
        "next选择正确率": {c: f"{summary[c]['next_correct_rate']:.0%}" for c in conds},
        "结论": "无账本=靠猜（幻觉恢复）；账本=确定性恢复——S 组件的价值即中断恢复",
    }
    save("e3_state_amnesia", summary)

    # ---------- 图 ----------
    setup_cn_font()
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    labels = ["A 无账本\n(上下文全丢)", "B 截断窗口\n(只剩最后一轮)", "C 账本恢复\n(progress.md)"]
    exact = [summary[c]["exact_match_rate"] * 100 for c in conds]
    nxt = [summary[c]["next_correct_rate"] * 100 for c in conds]
    x = np.arange(3)
    ax.bar(x - 0.18, exact, 0.36, label="done 集精确恢复率 %", color="#2a9d8f")
    ax.bar(x + 0.18, nxt, 0.36, label="next 选择正确率 %", color="#e9c46a")
    ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0, 118)
    ax.set_ylabel("%")
    ax.set_title("E3 崩溃恢复三条件：账本（S 组件）把恢复从猜变成读")
    for i in range(3):
        ax.text(i - 0.18, exact[i] + 3, f"{exact[i]:.0f}%", ha="center", fontsize=9)
        ax.text(i + 0.18, nxt[i] + 3, f"{nxt[i]:.0f}%", ha="center", fontsize=9)
    ax.legend(fontsize=9)
    fig_save(fig, "e3_state_amnesia")
    print("\n== readout =="); print(summary["readout"])
