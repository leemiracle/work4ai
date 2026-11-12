#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E5 —— SELECT 代码化 vs 问模型：把确定性决策从模型手里拿走（Ch06 核心实验）
===========================================================================
E3 发现：账本信息充分，但 0.5B 解析 progress.md 仅 1/3 全对（harness dependence）。
工程对策验证：walkinglabs 设计——SELECT 由 harness 代码执行，不问模型。

三条件（同一账本，崩溃后选下一个任务）：
  ask_model   ：把 progress.md 给模型问"下一个做什么"（E3 复刻，3 reps）
  hybrid      ：模型答 → harness 校验（必须是 pending 且唯一）→ 无效则代码兜底（3 reps）
  code_select ：harness 代码直接读 feature_list 取第一个 pending（0 调用，解析解）

度量：选择正确率 / LLM 调用数 / 是否存在"模型对但被兜底覆盖"与"模型错被兜底救回"

复现：cd 讲透Harness/experiments && timeout 900 python3 e5_select_codify.py
"""
import re
from common import local_qwen, save, fig_save, setup_cn_font

FEATURE_LIST = {           # ground truth 账本（S 组件）
    "add": "done", "rev": "done", "count_vowels": "done",
    "slugify": "pending", "fib": "pending", "fizz": "pending",
}
PENDING_ORDER = [k for k, v in FEATURE_LIST.items() if v == "pending"]
CORRECT_NEXT = PENDING_ORDER[0]                      # slugify
PROGRESS_MD = ("# progress.md\n## 已完成\n- add: done\n- rev: done\n- count_vowels: done\n"
               "\n## 待办\n- slugify（pending）\n- fib（pending）\n- fizz（pending）\n")

def ask_model(rep):
    q = ("你在执行 6 函数任务会话（add/rev/count_vowels/slugify/fib/fizz）。\n"
         "会话中断重启，读回账本：\n---\n" + PROGRESS_MD +
         "---\n下一步应该实现哪个函数？只回答一个函数名。")
    out = local_qwen(q, max_new_tokens=24, temperature=0.3, do_sample=True, seed=11 + rep)
    names = ["count_vowels", "slugify", "add", "rev", "fib", "fizz"]   # 长名优先防前缀误配
    for n in names:
        if n in out:
            return n, out.strip()[:60]
    return None, out.strip()[:60]

def hybrid(rep):
    """模型答 + harness 校验 + 代码兜底——middleware 模式（L2 断言护住 L3）。"""
    choice, raw = ask_model(rep)
    valid = choice in PENDING_ORDER
    final = choice if valid else CORRECT_NEXT      # 兜底 = code_select
    return {"model_choice": choice, "valid": valid, "final": final, "raw": raw}

if __name__ == "__main__":
    print(f"== 正确答案: {CORRECT_NEXT}（pending 顺序 {PENDING_ORDER}）==\n")
    ask_runs, hyb_runs = [], []
    for rep in range(3):
        c, raw = ask_model(rep)
        ask_runs.append(c)
        h = hybrid(rep + 100)                       # 不同 seed，独立采样
        hyb_runs.append(h)
        print(f"  rep{rep}: ask_model={c} | hybrid: model={h['model_choice']} "
              f"valid={h['valid']} final={h['final']}", flush=True)

    acc_ask = sum(c == CORRECT_NEXT for c in ask_runs) / 3
    acc_hyb = sum(h["final"] == CORRECT_NEXT for h in hyb_runs) / 3
    fallback_fired = sum(not h["valid"] for h in hyb_runs)
    summary = {
        "meta": {"model": "Qwen2.5-0.5B (local CPU)", "correct_next": CORRECT_NEXT,
                 "reps": 3, "date": "2026-08-26"},
        "ask_model": {"choices": ask_runs, "acc": acc_ask, "calls": 3},
        "hybrid": {"runs": hyb_runs, "acc": acc_hyb, "calls": 3,
                   "fallback_fired": fallback_fired},
        "code_select": {"acc": 1.0, "calls": 0, "note": "解析解：dict 扫描第一个 pending"},
        "readout": {
            "ask_model 正确率": f"{acc_ask:.0%}（3 次调用）",
            "hybrid 正确率": f"{acc_hyb:.0%}（3 次调用 + 0 成本校验；兜底触发 {fallback_fired}/3）",
            "code_select 正确率": "100%（0 调用，确定性）",
            "结论": "确定性决策代码化是免费的 100%；hybrid 是『模型判断+代码护栏』的一般模式"
                    "（E2 的 L1 护 L3 同构）；纯问模型在弱模型上不可靠",
        },
    }
    save("e5_select_codify", summary)

    setup_cn_font()
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    conds = ["ask_model\n(问模型)", "hybrid\n(模型+校验+兜底)", "code_select\n(纯代码)"]
    accs = [acc_ask, acc_hyb, 1.0]
    calls = [3, 3, 0]
    x = np.arange(3)
    colors = ["#e76f51", "#e9c46a", "#2a9d8f"]
    for i in range(3):
        axes[0].bar(i, accs[i], 0.5, color=colors[i])
        axes[0].text(i, accs[i] + 0.03, f"{accs[i]:.0%}", ha="center", fontsize=10)
    axes[0].set_xticks(x); axes[0].set_xticklabels(conds); axes[0].set_ylim(0, 1.15)
    axes[0].set_ylabel("next 选择正确率"); axes[0].set_title("正确率")
    for i in range(3):
        axes[1].bar(i, calls[i], 0.5, color=colors[i])
        axes[1].text(i, calls[i] + 0.06, str(calls[i]), ha="center", fontsize=10)
    axes[1].set_xticks(x); axes[1].set_xticklabels(conds); axes[1].set_ylim(0, 3.6)
    axes[1].set_ylabel("LLM 调用数"); axes[1].set_title("成本（调用数）")
    fig.suptitle("E5 SELECT 代码化：确定性决策从模型手里拿走（正确率 100% 且零调用）", fontsize=11)
    fig_save(fig, "e5_select_codify")
    print("\n== readout =="); print(summary["readout"])
