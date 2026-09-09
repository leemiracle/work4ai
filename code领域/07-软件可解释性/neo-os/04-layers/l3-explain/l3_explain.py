#!/usr/bin/env python3
"""
Neo-OS · L3 English Interface（三层讲解 prototype）
=====================================================
把 L2.5 形式化规则翻译成人类可理解的英文解释（降低 CTC）。

继承 work4ai 三层讲透宪法（直觉→数学→代码），Neo-OS L3 = 该方法论的运行时化：
  - Intuition: 1-2 sentence metaphor + why this rule exists
  - Formal statement: Lean4 invariant (the math)
  - Trace evidence: concrete example / violation manifestation (the code)

这是 Neo-OS 四层架构的 L3（英文输出口），对接 L2.5 形式化规则。

用法：
  python3 l3_explain.py                    # 生成所有内置规则的三层讲解
  python3 l3_explain.py ElectionSafety     # 单个规则
"""
import json, os, sys, time, urllib.request

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
API_KEY = os.environ.get("ZHIPU_API_KEY", "")
MODEL = os.environ.get("L3_MODEL", "glm-4-plus")

L3_PROMPT = """You are Neo-OS's L3 English explanation engine. Translate the formal rule below into a three-layer explanation (work4ai 三层讲透 methodology, in English).

Rule name: {name}
Formal anchor: {anchor}
Category: {category}
Lean4 statement:
```lean
{lean4}
```

Generate a three-layer explanation in markdown (English only, no other text):

## Intuition
[1-2 sentence plain-English metaphor + why this rule must hold]

## Formal statement (the math)
[State the Lean4 invariant, then explain what it means mathematically — one paragraph]

## Trace evidence (the code)
[A concrete trace/event example showing the rule in action, OR how a violation would manifest as an observable bug. Be specific to the rule's domain.]

Output only the markdown, English, no preamble."""

# 内置规则（从 L2.5 形式化层来）
RULES = {
    "ElectionSafety": {
        "anchor": "Raft §5.2 / dsyme RE5",
        "category": "DISTRIBUTED CONSENSUS",
        "lean4": """theorem electionSafety (voters : List Nat) (vote : Nat → Option Nat)
    (c1 c2 : Nat)
    (h1 : 2 * votesFor voters vote c1 > voters.length)
    (h2 : 2 * votesFor voters vote c2 > voters.length) :
    c1 = c2
-- votesFor counts how many voters voted for a candidate;
-- vote : voter → Option candidate is single-valued (Option injective).""",
    },
    "committedMono": {
        "anchor": "Raft §5.4.2 / dsyme hcommitted_mono",
        "category": "DISTRIBUTED CONSENSUS",
        "lean4": """theorem Inv_preserved_over_trace :
    ∀ (s : NodeState) (es : List Ev), OK s es → Inv s → Inv (final s es)
-- Inv s := s.commitIndex ≥ 0 ∧ s.lastApplied ≤ s.commitIndex
-- commitIndex only advances (Raft §5.4.2 commit rule).""",
    },
    "spinlockPreempt": {
        "anchor": "Linux Documentation/locking/spinlocks.rst",
        "category": "OS KERNEL (synchronization)",
        "lean4": """theorem Inv_preserved_over_trace :
    ∀ (s : S) (es : List Ev), OK s es → Inv s → Inv (final s es)
-- Inv s := s.preemptCount ≥ 0 ∧ (s.lockHeld = true → s.preemptCount ≥ 1)
-- Holding a spinlock requires preempt_disable (else sleep-holding-lock deadlock).""",
    },
    "logMatchingSingle": {
        "anchor": "Raft §5.4.1 / dsyme LogMatching",
        "category": "DISTRIBUTED CONSENSUS",
        "lean4": """theorem logMatchingSingle (log : List (Nat × Nat)) (i : Nat) (t : Nat) (e1 e2 : Nat)
    (h1 : log.get? i = some (t, e1)) (h2 : log.get? i = some (t, e2)) :
    e1 = e2
-- Same index + same term ⟹ identical entry (Log Matching Property, single-point).""",
    },
}

def llm(prompt, max_tokens=700, temperature=0.3):
    if not API_KEY:
        return "<API_ERROR: ZHIPU_API_KEY unset>"
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
               "max_tokens": max_tokens, "temperature": temperature}
    data = json.dumps(payload).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(API_URL, data=data, headers={
                "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == 2:
                return f"<API_ERROR: {e}>"
            time.sleep(2 ** attempt)

def explain(name):
    info = RULES[name]
    prompt = L3_PROMPT.format(name=name, **info)
    raw = llm(prompt)
    return raw.strip()

def main():
    names = sys.argv[1:] if len(sys.argv) > 1 else list(RULES.keys())
    out = ["# Neo-OS L3 · Three-Layer Explanations (prototype)\n",
           "> Auto-generated from L2.5 formal rules via GLM-4-plus. ",
           "work4ai 三层讲透 methodology (Intuition → Math → Trace).\n"]
    for name in names:
        if name not in RULES:
            print(f"unknown rule: {name}; known: {list(RULES)}"); continue
        print(f"generating {name}...", flush=True)
        expl = explain(name)
        out.append(f"\n---\n\n# {name}\n")
        out.append(f"*Anchor: {RULES[name]['anchor']} · Category: {RULES[name]['category']}*\n")
        out.append(expl)
        out.append("")
        time.sleep(0.5)
    md = "\n".join(out)
    out_path = os.path.join(os.path.dirname(__file__), "explanations.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n→ {out_path}")

if __name__ == "__main__":
    main()
