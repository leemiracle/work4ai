# -*- coding: utf-8 -*-
"""prompts.py — DeepSeek-Prover-V2 官方 prompt 逐字保真 + 分解 prompt 重构

来源核对（2026-08-24）：
  COT / NONCOT —— GitHub README Quick Start 逐字（唯一权威版本）
  DECOMPOSE   —— 论文 §cold-start 描述的重构版（官方未放出全文，标注重构）
"""
import json

# ---- 官方 CoT 模式（复杂定理：先计划后证明）----
COT = """Complete the following Lean 4 code:

```lean4
{statement}
```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.""".strip()

# ---- 官方 non-CoT 模式（简单定理/专家迭代：直接补全）----
NONCOT = """Complete the following Lean 4 code:

```lean4
{statement}
```""".strip()

# ---- 分解 prompt（重构版：给"建筑师"大模型，产出 have 骨架）----
# 论文描述：prompt DeepSeek-V3 把定理分解为高层证明草图并同步形式化为
# Lean 4 子目标序列（have ... := by sorry 骨架）。输出格式约束是我们加的工程化。
DECOMPOSE = """You are a proof architect. Decompose the following Lean 4 theorem into a chain of subgoals.

Instructions:
1. Think about the high-level proof strategy first (natural language, brief).
2. Write the proof as a Lean 4 skeleton: each intermediate step becomes a `have` statement with `sorry` as its proof placeholder.
3. Subgoals must be strictly easier than the original theorem — each one should be provable with 1-3 tactic steps.
4. The final step combines all `have`s to close the main goal.
5. Use only Lean 4 core library (no mathlib imports).

Output ONLY a JSON object:
{{"plan": "<one-paragraph natural language proof plan>",
 "skeleton": "<complete Lean 4 theorem with have-chain and sorry placeholders>"}}

Theorem to decompose:

```lean4
{statement}
```""".strip()

# ---- 子目标证明 prompt（给"瓦工"模型：premises 注入版）----
# 论文机制：子目标表达式从 have 提取替换原目标，前序子目标作为 premises。
SUBGOAL = """Complete the following Lean 4 code:

```lean4
{context}theorem subgoal_{idx} {hypotheses} : {goal} := by
```

The following intermediate results have already been proven and are available as premises:
{premises}

Complete the proof. Output only Lean 4 code.""".strip()


def extract_code(text: str) -> str:
    """提取最后一个 ```lean4/lean 代码块；无块则原样返回（non-CoT 常见）。"""
    import re
    blocks = re.findall(r"```(?:lean4|lean)?\s*\n(.*?)```", text, re.S)
    return blocks[-1].strip() if blocks else text.strip()


def extract_json(text: str) -> dict:
    """提取 LLM 输出中的 JSON 对象（分解模式用）。"""
    import re, json as _j
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in decomposer output")
    return _j.loads(m.group(0))


if __name__ == "__main__":      # 自测：模板渲染
    stmt = "theorem demo : 2 + 2 = 4 := by\n"
    print(NONCOT.format(statement=stmt))
    print("---")
    print(DECOMPOSE.format(statement=stmt)[:200], "...")
