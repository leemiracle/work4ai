#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""glm_apo_finals.py —— 决赛：臂7(RCF) vs 朴素基线，全 16 题配对对跑（并发版）
探索阶段结论（2026-08-17，24 次调用）：臂7 = 角色+CoT+契约 全开 → Q=1.00
用法：python3 glm_apo_finals.py
"""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if (os := __import__('os')) else '.')
from glm_apo import TASKS, call_glm, build_prompt, ARM_NAMES

BEST = 7   # bandit 选出：RCF 全开

def one(i):
    cat, q_text, judge = TASKS[i]
    a1, rt1 = call_glm(q_text, system=build_prompt(BEST) or None)
    a0, rt0 = call_glm(q_text, system=None)
    r1, r0 = judge(a1), judge(a0)
    print(f"  {cat:>4}#{i}: 臂{'✅' if r1 else '❌'}(思{rt1}tk) 基线{'✅' if r0 else '❌'}(思{rt0}tk)"
          + ("  ← 分歧" if r1 != r0 else ""), flush=True)
    return r1, r0

if __name__ == "__main__":
    t0 = time.time()
    print(f"[决赛] {ARM_NAMES[BEST]} vs 朴素空system —— 16 题配对（8 并发）:")
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(one, range(len(TASKS))))
    w1 = sum(r for r, _ in results); w0 = sum(r for _, r in results)
    diff = [i for i, (r1, r0) in enumerate(results) if r1 != r0]
    print(f"\n最优臂 {w1}/16 vs 基线 {w0}/16｜分歧题: {diff or '无'}｜耗时 {time.time()-t0:.0f}s")
    print(f"\n★ 迭代出的最优 system prompt:\n   {build_prompt(BEST)!r}")
