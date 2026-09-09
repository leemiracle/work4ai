#!/usr/bin/env python3
"""
Neo-OS · L2 蒸馏初版 · commit 三元组 → Lean4 不变式
=====================================================
把 C1 pipeline 抽取的 (symptom, root_cause, fix) 三元组，
用 GLM 转成 Lean4 不变式陈述（基于 SpinlockPreempt 框架）。

这是 Neo-OS L2→L2.5 接口的首次实证：
  trace → C1 三元组 → L2 蒸馏（本脚本）→ Lean4 规则候选 → lake build 验证

R5 调研：从系统 trace 端到端生成 Lean4 因果规则，无成熟竞品（蓝海）。

用法：
  python3 l2_distill.py ../data/c1_50_results.jsonl --n 5
"""
import argparse, json, os, re, sys, time, urllib.request

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
API_KEY = os.environ.get("ZHIPU_API_KEY", "")
MODEL = os.environ.get("C1_MODEL", "glm-4-plus")

L2_DISTILL_PROMPT = """你是 Lean4 形式化专家，专长 OS/系统软件不变式。从下面的 kernel bug 因果三元组，提取一个 Lean4 不变式陈述。

## bug 三元组
- subject: {subject}
- root_cause: {root_cause}
- fix: {fix}
- category: {category}

## 参考：Neo-OS SpinlockPreempt 的框架
```lean
structure S where
  preemptCount : Nat
  lockHeld     : Bool
  deadlocked   : Bool

inductive Ev where
  | lockAcquire | lockRelease | preemptDisable | preemptEnable | tick | schedule

def step (e : Ev) (s : S) : S := ...
def safe (e : Ev) (s : S) : Prop := ...
def Inv (s : S) : Prop := s.preemptCount ≥ 0 ∧ (s.lockHeld = true → s.preemptCount ≥ 1) ∧ s.deadlocked = false
```

## 你的任务
从这个 bug 的因果机制，提取**一个** Lean4 不变式陈述（def 或 theorem），编码这个 bug 的核心因果规则。

要求：
1. 只输出一个 Lean4 代码块（```lean ... ```）
2. 不变式要捕捉 bug 的**因果本质**（如 UAF → 引用计数非负；race → 操作原子性；OBOE → 边界检查）
3. **structure 名必须唯一**（含 bug 主题关键词，如 S_vhost_iotlb，不要用通用的 S）
4. 给出不变式 + 一个简短的解释（1-2 行注释）

例如，对于 use-after-free，可能的不变式：
```lean
-- UAF: 引用计数 > 0 时对象不可释放
def Inv_noUAF (s : S) : Prop := s.refcount > 0 → s.freed = false
```
"""


def llm(messages, max_tokens=800, temperature=0.3):
    if not API_KEY:
        return "<API_ERROR: ZHIPU_API_KEY unset>"
    payload = {"model": MODEL, "messages": messages,
               "max_tokens": max_tokens, "temperature": temperature}
    data = json.dumps(payload).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(API_URL, data=data, headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read())["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == 2:
                return f"<API_ERROR: {e}>"
            time.sleep(2 ** attempt)
    return ""


def distill_rule(triple):
    """把一个三元组转成 Lean4 不变式候选。"""
    prompt = L2_DISTILL_PROMPT.format(
        subject=triple.get("subject", ""),
        root_cause=triple.get("l2", {}).get("root_cause", ""),
        fix=triple.get("l2", {}).get("fix", ""),
        category=triple.get("l2", {}).get("category", ""),
    )
    raw = llm([{"role": "user", "content": prompt}])
    # 提取 ```lean ... ``` 代码块
    match = re.search(r'```lean?\n(.*?)```', raw, re.DOTALL)
    lean_code = match.group(1).strip() if match else raw.strip()
    return lean_code, raw


def load_triples(jsonl_path, n=None, categories=None):
    """从 c1_pipeline 的 jsonl 加载三元组。可按 category 过滤。"""
    triples = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if categories:
                cat = r.get("l2", {}).get("category", "")
                if cat not in categories:
                    continue
            triples.append(r)
    return triples[:n] if n else triples


def main():
    ap = argparse.ArgumentParser(description="L2 蒸馏：commit 三元组 → Lean4 不变式")
    ap.add_argument("input", help="c1_pipeline 输出的 jsonl")
    ap.add_argument("--n", type=int, default=5, help="蒸馏几个三元组")
    ap.add_argument("--out", default="../data/l2_distilled_rules.lean",
                    help="输出的 Lean4 文件（所有蒸馏的不变式）")
    ap.add_argument("--categories", default=None,
                    help="按 category 过滤（逗号分隔，如 MEM_REF,CONCURRENCY）")
    args = ap.parse_args()

    cats = args.categories.split(",") if args.categories else None
    triples = load_triples(args.input, args.n, cats)
    print(f"=== L2 蒸馏：{len(triples)} 个三元组 → Lean4 不变式 ===\n")

    all_rules = []
    for i, t in enumerate(triples):
        subject = t.get("subject", "")[:60]
        cat = t.get("l2", {}).get("category", "?")
        print(f"[{i+1}/{len(triples)}] {cat}: {subject}")
        lean_code, raw = distill_rule(t)
        print(f"  → {lean_code[:120]}...")
        all_rules.append({
            "hash": t.get("hash", ""),
            "subject": t.get("subject", ""),
            "category": cat,
            "lean4_rule": lean_code,
        })
        time.sleep(0.5)

    # 生成合并的 Lean4 文件（每规则独立 namespace，避免 structure 名冲突）
    print(f"\n=== 写入 {args.out} ===")
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("/- L2 蒸馏：commit 三元组 → Lean4 不变式（GLM-4-plus 生成，未验证）-/\n\n")
        for r in all_rules:
            ns = "Rule_" + r['hash'][:8]
            f.write(f"namespace {ns}\n\n")
            f.write(f"/- 来源: {r['hash'][:12]} ({r['category']})\n   {r['subject']}\n   -/\n")
            f.write(r["lean4_rule"])
            f.write(f"\n\nend {ns}\n\n")

    print(f"完成：{len(all_rules)} 个 Lean4 不变式候选")
    print(f"⚠️ 这些是 GLM 生成的候选，需 lake build 验证 + 人工审计")


if __name__ == "__main__":
    main()
