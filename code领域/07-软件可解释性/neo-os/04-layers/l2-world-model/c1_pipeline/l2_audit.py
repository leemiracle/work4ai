#!/usr/bin/env python3
"""
Neo-OS · L2 语义审计 · 量化「编译通过但语义错」的比例（R5§6 命门实证）
=====================================================================
48/48 编译率已知（语法），本脚本审计语义正确率：
  对每个蒸馏出的 Lean4 不变式，GLM 对比原始 commit，判断是否正确编码了 bug 因果。

⚠️ GLM 审计 GLM 有自相关偏差（倾向于说自己生成的是对的），
   结果是语义正确率的**上界估计**（真实人工审计可能更低）。

用法：
  python3 l2_audit.py ../data/l2_distilled_rules_48.lean ../data/c1_50_results.jsonl --n 10
"""
import argparse, json, os, re, sys, time, urllib.request

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
API_KEY = os.environ.get("ZHIPU_API_KEY", "")
MODEL = os.environ.get("C1_MODEL", "glm-4-plus")

AUDIT_PROMPT = """你是 kernel 安全审计专家。判断下面的 Lean4 不变式是否正确编码了 kernel bug 的因果规则。

## bug 原始信息
- subject: {subject}
- root_cause: {root_cause}
- fix: {fix}
- category: {category}

## 从 bug 蒸馏出的 Lean4 不变式
```lean
{lean_code}
```

## 审计标准
- **correct**: 不变式正确捕捉了 bug 的核心因果机制（root_cause → 被阻止）
- **partial**: 捕捉了部分因果，但漏掉关键方面（如只查上界不查下界）
- **wrong**: 不变式与 bug 的因果无关，或编码了错误的方向

只输出一个 JSON（不要 markdown 围栏）：
{{"verdict": "correct|partial|wrong", "captures_core": true/false, "missing": "...", "reasoning": "1-2句"}}"""


def llm(messages, max_tokens=400, temperature=0.2):
    if not API_KEY:
        return '{"verdict": "wrong", "reasoning": "API unset"}'
    payload = {"model": MODEL, "messages": messages,
               "max_tokens": max_tokens, "temperature": temperature}
    data = json.dumps(payload).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(API_URL, data=data, headers={
                "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == 2:
                return f'{{"verdict": "wrong", "reasoning": "API error: {e}"}}'
            time.sleep(2 ** attempt)
    return '{"verdict": "wrong"}'


def parse_distilled_lean(path):
    """解析 l2_distilled_rules_48.lean，返回 [{namespace, source_hash, lean_code}]"""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    rules = []
    # 匹配 namespace Rule_xxxx ... end Rule_xxxx
    for m in re.finditer(
        r'namespace (Rule_[0-9a-f]+)\n(.*?)end \1', content, re.DOTALL):
        ns = m.group(1)
        body = m.group(2)
        # 提取来源 hash（注释里的完整 hash）
        hash_match = re.search(r'来源:\s*([0-9a-f]+)', body)
        source_hash = hash_match.group(1) if hash_match else ""
        rules.append({"namespace": ns, "source_hash": source_hash, "lean_code": body.strip()})
    return rules


def load_originals(jsonl_path):
    """按 hash 索引原始 commit 信息"""
    originals = {}
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                originals[r.get("hash", "")] = r
    return originals


def audit_one(rule, original):
    """审计一个规则。返回 verdict dict。"""
    l2 = original.get("l2", {}) if original else {}
    prompt = AUDIT_PROMPT.format(
        subject=original.get("subject", "") if original else "?",
        root_cause=l2.get("root_cause", ""),
        fix=l2.get("fix", ""),
        category=l2.get("category", ""),
        lean_code=rule["lean_code"][:500],
    )
    raw = llm([{"role": "user", "content": prompt}])
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        raw = raw.rsplit("```", 1)[0]
    if "{" in raw and "}" in raw:
        raw = raw[raw.index("{"):raw.rindex("}") + 1]
    try:
        return json.loads(raw)
    except Exception:
        return {"verdict": "parse_error", "reasoning": raw[:100]}


def main():
    ap = argparse.ArgumentParser(description="L2 语义审计")
    ap.add_argument("lean_file", help="蒸馏出的 Lean4 文件")
    ap.add_argument("jsonl_file", help="C1 原始 jsonl")
    ap.add_argument("--n", type=int, default=10, help="审计几个")
    args = ap.parse_args()

    rules = parse_distilled_lean(args.lean_file)
    originals = load_originals(args.jsonl_file)
    rules = rules[:args.n]
    print(f"=== L2 语义审计：{len(rules)} 个规则（GLM 审计 GLM，上界估计）===\n")

    verdicts = {"correct": 0, "partial": 0, "wrong": 0, "parse_error": 0}
    details = []
    for i, rule in enumerate(rules):
        original = originals.get(rule["source_hash"], {})
        subject = original.get("subject", "?")[:50]
        print(f"[{i+1}/{len(rules)}] {rule['source_hash'][:8]}: {subject}")
        v = audit_one(rule, original)
        verdict = v.get("verdict", "parse_error")
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        print(f"  → {verdict}: {v.get('reasoning', '')[:100]}")
        details.append({"hash": rule["source_hash"], "subject": subject, **v})
        time.sleep(0.3)

    # 统计
    total = len(rules)
    correct = verdicts.get("correct", 0)
    partial = verdicts.get("partial", 0)
    wrong = verdicts.get("wrong", 0)
    print(f"\n=== 语义审计结果（N={total}）===")
    print(f"  ✅ correct: {correct} ({100*correct/total:.0f}%)")
    print(f"  🟡 partial: {partial} ({100*partial/total:.0f}%)")
    print(f"  🟥 wrong:   {wrong} ({100*wrong/total:.0f}%)")
    semantic_ok = correct + partial  # partial 算"部分正确"
    print(f"\n  编译率: 100%（48/48 lake build 通过）")
    print(f"  语义正确率（correct+partial，上界）: {100*semantic_ok/total:.0f}%")
    print(f"  语义错误率（wrong）: {100*wrong/total:.0f}%")
    print(f"\n  ⚠️ GLM 审计 GLM 有自相关偏差，真实人工审计可能更低")
    print(f"  这是 R5§6 命门（编译≠语义正确）的初步量化")


if __name__ == "__main__":
    main()
