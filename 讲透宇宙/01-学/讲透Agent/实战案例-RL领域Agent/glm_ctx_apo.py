#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
glm_ctx_apo.py —— rl_agent v3 CtxPolicy 的真模型版：context 技术还能在最优 prompt 上加多少分？
===============================================================================================
背景：GLM-APO（v1）已迭代出最优 RCF system（16/16）。本实验问下一层问题：
     在最优 prompt 之上，手册 06/12 的 context 技术（few-shot / bookend / 分隔符）还有增益吗？
设计（对照 toy Ctx-APO，手册 11 方案对决的又一活体）：
     底座固定 = RCF 最优 system；变异对象 = user 侧 context 结构（4 臂）
     臂0 base   : RCF 原样（对照）
     臂1 shot   : + 同类 1 条 few-shot（教格式，不同内容 ← 手册 02 S 要素）
     臂2 bookend: 任务后重申关键约束（lost-in-middle 对策 ← 手册 06）
     臂3 split  : ### 分隔 任务/输出要求（防注入+结构化 ← 手册 02 分隔符）
题集：16 题中 6 题精选（每类≥1 + v1 已知脆弱题 math#2 9.8vs9.11 / know#12 / know#15）
预算：4 臂 × 6 题 = 24 次调用（coding-plan 套餐内 glm-5）
测量：对错 + reasoning_tokens（context 是否影响推理预算分配 ← v1 发现③）
跑法：python3 glm_ctx_apo.py [--dry]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glm_apo import call_glm, TASKS, DRY   # 复用调用器/题集/判分器（单一事实源）

RCF = "你是严谨的算法工程师，精准第一。 先一步步推理，再给出最终答案。 严格遵循输出要求：不多不少，只输出要求的内容。"

# 6 题精选（索引对应 glm_apo.TASKS）：每类≥1 + v1 脆弱题优先
PICK = [2, 3, 4, 8, 12, 15]     # math 9.8vs9.11 / math 1..100 / json 抽取 / code 回文 / know 注意力 / know RLVR

FEWSHOT = {
    2:  "例：计算 7×8，只输出最终数字。答：56",
    3:  "例：2+4+6 等于多少？只输出数字。答：12",
    4:  "例：把「王五，40 岁，住上海」抽成 JSON。答：{\"name\":\"王五\",\"age\":40,\"city\":\"上海\"}",
    8:  "例：写函数 double(x) 返回两倍，最后 print(double(21))。答：输出 42",
    # 12/15 知识题不给例（防泄露答案模式——诚实标注）
}
def wrap(arm, idx, task):
    if arm == 0: return task
    if arm == 1:
        ex = FEWSHOT.get(idx)
        return f"{ex}\n\n{task}" if ex else task
    if arm == 2: return f"{task}\n\n（重申：严格遵循输出要求，不多不少，只输出要求的内容。）"
    if arm == 3: return f"### 任务\n{task}\n\n### 输出要求\n只输出要求的内容，不多不少。"
CTX_NAMES = ["ctx0/base", "ctx1/+shot", "ctx2/+bookend", "ctx3/+split"]

def run():
    print("=" * 66)
    print(f"GLM-CtxAPO：context 臂 × glm-5 × RLVR 6 题｜底座=RCF 最优｜24 次预算")
    print("=" * 66)
    R = {a: [] for a in range(4)}          # (idx, reward, reasoning_tokens)
    for idx in PICK:                        # 题外循环（同题 4 臂连跑 → 配对可比）
        cat, q_text, judge = TASKS[idx]
        for a in range(4):
            ans, rt = call_glm(wrap(a, idx, q_text), system=RCF)
            r = 1.0 if judge(ans) else 0.0
            R[a].append((idx, r, rt))
            print(f"  {cat:>4}#{idx} {CTX_NAMES[a]:>13} → {'✅' if r else '❌'} (思考{rt}tk)", flush=True)
    print()
    for a in range(4):
        rs = [r for _, r, _ in R[a]]; rts = [rt for _, _, rt in R[a]]
        print(f"  [合计] {CTX_NAMES[a]:>13}: {sum(rs):.0f}/6  平均思考token {sum(rts)//max(len(rts),1)}")
    print("\n[配对] 与 base 的逐题分歧:")
    diff = 0
    for j, idx in enumerate(PICK):
        row = {a: R[a][j][1] for a in range(4)}
        if len(set(row.values())) > 1:
            diff += 1
            print(f"  题#{idx}({TASKS[idx][0]}): " + " ".join(f"{CTX_NAMES[a]}={'✅' if v else '❌'}" for a, v in row.items()))
    if not diff: print("  无（4 臂全一致）")
    print("[预算] 实际调用 24 次")
    return R

if __name__ == "__main__":
    if DRY:
        print("[dry] wrap 变换自检:")
        for a in range(4): print(f"  {CTX_NAMES[a]}: {wrap(a, 2, '测试任务')[:70]!r}")
    else:
        run()
