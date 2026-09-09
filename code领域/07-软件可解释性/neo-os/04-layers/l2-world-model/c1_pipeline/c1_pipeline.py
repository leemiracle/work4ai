#!/usr/bin/env python3
"""
Neo-OS · C1 Pipeline · Linux kernel commit 蒸馏
=================================================
命门 V25 在 Linux kernel C commit 上的复现（council C1）。

抽取三元组 (symptom, root_cause, fix)：
  - L1 被动解析：仅从 commit message（subject + body）的启发式
  - L2 agent 主动推理：GLM 读 subject + body，主动构造因果链

对标基准：V25 sglang(Python) 100 样本 L2 ≈ 62%（commit_extraction_report.md）。
预期 kernel(C)：coverage 略低（C kernel 因果更硬、更难抽），但 Fixes: 子集
precision ≥90%（标签提供确定性因果链接）——这是 council C1 的中性预测。

用法：
  python3 c1_pipeline.py test                      # synthetic 自测（验 API）
  python3 c1_pipeline.py run commits.txt --n 100   # 跑真实 commit 小样本
  python3 c1_pipeline.py stats results.jsonl       # 统计 coverage
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error
from collections import Counter

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
API_KEY = os.environ.get("ZHIPU_API_KEY", "")
MODEL = os.environ.get("C1_MODEL", "glm-4-plus")  # glm-4-plus / glm-4.5 / glm-4-long

# ============================================================
# LLM 调用（OpenAI 兼容，重试 2 次）
# ============================================================

def llm(messages, max_tokens=700, temperature=0.1):
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

# ============================================================
# L2 agent 抽取 prompt（对标 V25 的 L2 层）
# ============================================================

L2_PROMPT = """你是 Linux kernel bug 因果分析专家。从下面的 git commit（subject + body），抽取因果三元组与元信息。

Commit:
---
{commit_msg}
---

抽取字段（JSON，缺信息填 null）：
1. "symptom": 用户/系统可观察症状（如 "panic on rmmod", "data corruption under load", "hang under memory pressure"）。commit 常不直接写，需从 root_cause + 修复反推。若完全无线索填 null。
2. "root_cause": 根因机制（如 "use-after-free: cleanup freed buffer before worker finished", "off-by-one: loop should be i<n not i<=n", "missing spin_lock around shared counter"）。
3. "fix": 修复手段（如 "add spin_lock_irqsave around access", "change loop bound to n"）。
4. "category": 从 [INDEX_VAR, LOCK_SYNC, MEM_REF, CONCURRENCY, OFF_BY_ONE, NULL_PTR, RESOURCE_LEAK, LOGIC, INIT_ORDER, OTHER, NOISE] 选一个。NOISE=CI/docs/revert/依赖pin/chore 非真 bug。
5. "confidence": 0.0-1.0 你对此三元组（尤其 root_cause）的置信度。
6. "reasoning": 1-2 句推理（关键证据来自 commit 哪部分）。

只输出一个 JSON 对象，不要 markdown 围栏，不要其他文字：
{{"symptom":..., "root_cause":..., "fix":..., "category":..., "confidence":..., "reasoning":...}}"""

def extract_l2(commit_msg):
    raw = llm([{"role": "user", "content": L2_PROMPT.format(commit_msg=commit_msg)}])
    raw = raw.strip()
    # 容错：去 markdown 围栏
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()
    # 容错：找第一个 { 到最后一个 }
    if "{" in raw and "}" in raw:
        raw = raw[raw.index("{"):raw.rindex("}") + 1]
    try:
        return json.loads(raw), None
    except Exception as e:
        return None, f"parse_error: {e}; raw={raw[:150]}"

# ============================================================
# Fixes: 链提取（provenance normative signal，Oracle Review S5）
# ============================================================

def extract_fixes(body):
    """
    从 commit body 提取 Fixes: 链。
    kernel commit 格式：Fixes: <hash> ("<subject>")
    返回 {has_fixes, fixes_hash, normative_signal}。
    Fixes: 是规范性信号——fix 定义「正确」（S5），比 kernel 文档错误模式更去相关。
    """
    if not body:
        return {"has_fixes": False, "fixes_hash": None, "normative_signal": "none"}
    # kernel Fixes: 格式：Fixes: <7-40位hash> ("...")
    match = re.search(r'Fixes:\s*([0-9a-f]{7,40})', body)
    if match:
        return {
            "has_fixes": True,
            "fixes_hash": match.group(1),
            "normative_signal": "strong"  # fix = 描述性→规范性转换（S5）
        }
    return {"has_fixes": False, "fixes_hash": None, "normative_signal": "none"}

# ============================================================
# L1 被动解析（启发式，无 LLM）
# ============================================================

RC_KEYWORDS = ["because", "due to", "caused by", "otherwise", "without this",
               "fixes:", "since", "as ", "leading to", "results in"]
SYMPTOM_KEYWORDS = ["panic", "hang", "crash", "deadlock", "corruption",
                    "oops", "warning", "leak", "race", "regression"]

def extract_l1(subject, body):
    text = (subject + "\n" + body).lower()
    rc_signal = any(k in text for k in RC_KEYWORDS)
    sym_signal = any(k in text for k in SYMPTOM_KEYWORDS)
    has_body = len(body.strip()) > 30
    # L1 可抽取完整三元组的启发式估计：有 root_cause 信号 + 有 fix（subject 通常含 fix）
    return {
        "has_subject": bool(subject.strip()),
        "has_body": has_body,
        "rc_signal": rc_signal,
        "symptom_signal": sym_signal,
        "est_full_triple": rc_signal and len(subject) > 20,
    }

# ============================================================
# 噪声分类（前置过滤 CI/docs/revert）
# ============================================================

NOISE_PATTERNS = ["[ci]", "[docs]", "revert", "pin ", "bump ", "chore",
                  "typo", "whitespace", "format", "merge branch",
                  "update readme", "license"]

def is_noise(subject):
    s = subject.lower()
    return any(p in s for p in NOISE_PATTERNS)

# ============================================================
# commit 解析（从 git log --format="%H%n%s%n%b%n---END---"）
# ============================================================

def parse_commits_file(path):
    """每条 commit 由 hash / subject / body / ---END--- 分隔。"""
    commits = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except FileNotFoundError:
        return commits
    blocks = content.split("---END---")
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        lines = b.split("\n")
        if len(lines) < 2:
            continue
        h = lines[0].strip()
        subject = lines[1].strip() if len(lines) > 1 else ""
        body = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
        if h and subject:
            commits.append({"hash": h, "subject": subject, "body": body})
    return commits

# ============================================================
# 主流程
# ============================================================

def run(commits, n, out_path, sleep=0.3, resume=False):
    results = []
    total = min(n, len(commits)) if n else len(commits)
    noise = 0
    processed = set()
    if resume and os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        processed.add(json.loads(line).get("hash"))
                    except Exception:
                        pass
        print(f"  resume 模式：已处理 {len(processed)} 条，跳过")
    for i, c in enumerate(commits[:total]):
        if c["hash"] in processed:
            continue
        if is_noise(c["subject"]):
            noise += 1
            continue
        commit_msg = f"Subject: {c['subject']}\n\n{c['body']}" if c["body"] else c["subject"]
        l1 = extract_l1(c["subject"], c["body"])
        l2, err = extract_l2(commit_msg)
        fixes_chain = extract_fixes(c["body"])  # provenance normative signal (S5)
        rec = {"hash": c["hash"], "subject": c["subject"], "l1": l1,
               "l2": l2, "fixes_chain": fixes_chain, "error": err}
        results.append(rec)
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{total}] noise={noise} ...", flush=True)
        time.sleep(sleep)
    return results, noise

def stats(jsonl_path):
    """统计 coverage，对标 V25 sglang 报告表格。"""
    records = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    n = len(records)
    if n == 0:
        print("no records"); return
    # L2 指标
    l2_ok = [r for r in records if r.get("l2") and not r.get("error")]
    has_symptom = sum(1 for r in l2_ok if r["l2"].get("symptom"))
    has_rc = sum(1 for r in l2_ok if r["l2"].get("root_cause"))
    has_fix = sum(1 for r in l2_ok if r["l2"].get("fix"))
    full_triple = sum(1 for r in l2_ok
                      if r["l2"].get("symptom") and r["l2"].get("root_cause")
                      and r["l2"].get("fix"))
    cats = Counter(r["l2"].get("category", "?") for r in l2_ok)
    avg_conf = (sum(r["l2"].get("confidence", 0) for r in l2_ok) / len(l2_ok)) if l2_ok else 0
    print(f"=== C1 Pipeline Stats（{jsonl_path}）===")
    print(f"总记录: {n}  |  L2 成功: {len(l2_ok)}  |  parse_error: {n - len(l2_ok)}")
    print(f"\nL2 agent 抽取率（对标 V25 sglang 62%）:")
    print(f"  symptom     : {has_symptom}/{len(l2_ok)} = {100*has_symptom/len(l2_ok):.1f}%")
    print(f"  root_cause  : {has_rc}/{len(l2_ok)} = {100*has_rc/len(l2_ok):.1f}%")
    print(f"  fix         : {has_fix}/{len(l2_ok)} = {100*has_fix/len(l2_ok):.1f}%")
    print(f"  完整三元组  : {full_triple}/{len(l2_ok)} = {100*full_triple/len(l2_ok):.1f}%   ← 核心指标")
    print(f"\n平均置信度: {avg_conf:.2f}")
    print(f"\n类别分布:")
    for cat, cnt in cats.most_common():
        print(f"  {cat:18s}: {cnt:3d} ({100*cnt/len(l2_ok):.0f}%)")
    # 命门对照
    cov = 100 * full_triple / len(l2_ok) if l2_ok else 0
    print(f"\n=== 命门 V25 对照 ===")
    print(f"  悲观线 10%  |  现实线 40%  |  乐观线 70%")
    print(f"  实测: {cov:.1f}%  →  ", end="")
    if cov >= 70: print("🟢 乐观（全力推进）")
    elif cov >= 40: print("🟢 现实-乐观（可推进）")
    elif cov >= 10: print("🟡 悲观上沿（需补充数据）")
    else: print("🔴 悲观（转降级讨论）")

# ============================================================
# CLI
# ============================================================

def selftest():
    """synthetic 自测，验证 API + prompt 工作正常。"""
    test_commits = [
        # 真实风格 kernel bug-fix 1: use-after-free
        """Subject: [PATCH] drm/XYZ: fix use-after-free in hotplug path

The driver accessed a freed buffer in the hotplug worker because
cleanup() freed it before the worker finished.

Fixes: abc12345 ("drm/XYZ: add hotplug support")
Signed-off-by: Foo Bar <foo@kernel.org>""",
        # 真实风格 2: off-by-one
        """Subject: [PATCH] net: fix off-by-one in skb queue loop

The loop used i <= n instead of i < n, causing a one-byte
over-read past the array boundary under high load.

Reported-by: regression in v6.1
Fixes: def67890 ("net: rewrite skb queue")
Signed-off-by: Bar Baz <bar@kernel.org>""",
        # 噪声
        """Subject: [docs] update README typo

fix typo in readme""",
    ]
    print(f"=== C1 Pipeline self-test (model={MODEL}) ===\n")
    for i, c in enumerate(test_commits):
        noise = is_noise(c.split("\n")[0].replace("Subject: ", ""))
        print(f"--- commit {i+1} (noise={noise}) ---")
        if noise:
            print("  → skipped (noise filter)\n"); continue
        l1 = extract_l1(c.split("\n")[0].replace("Subject: ", ""),
                        "\n".join(c.split("\n")[1:]))
        l2, err = extract_l2(c)
        print(f"L1: {l1}")
        if err: print(f"L2 error: {err}")
        else: print(f"L2: {json.dumps(l2, indent=2, ensure_ascii=False)}")
        print()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Neo-OS C1 kernel commit 蒸馏 pipeline")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("test", help="synthetic 自测")
    pr = sub.add_parser("run", help="跑真实 commit")
    pr.add_argument("input"); pr.add_argument("--n", type=int, default=100)
    pr.add_argument("--out", default="../data/c1_results.jsonl")
    pr.add_argument("--resume", action="store_true", help="续跑模式（skip 已处理 hash）")
    st = sub.add_parser("stats", help="统计 coverage")
    st.add_argument("jsonl")
    args = ap.parse_args()

    if args.cmd == "test":
        selftest()
    elif args.cmd == "run":
        commits = parse_commits_file(args.input)
        print(f"解析到 {len(commits)} 条 commit，跑前 {args.n} 条 → {args.out}")
        if not args.resume and os.path.exists(args.out):
            os.remove(args.out)
        run(commits, args.n, args.out, resume=args.resume)
        print(f"\n完成，结果在 {args.out}")
        stats(args.out)
    elif args.cmd == "stats":
        stats(args.jsonl)
