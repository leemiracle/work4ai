#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cross_distill.py — 第二教师（Qwen2.5-Math-7B-Instruct）交叉验证蒸馏卡断言
容器内跑：python3 cross_distill.py  （需 qwen vllm 已起于 localhost:8001）
输入: cross_claims.jsonl（24 题：18 真 + 6 陷阱）
输出: cross_results.jsonl + stdout 汇总
设计: 每题让 qwen-math 判断真假 + 置信 + 一句话理由；对照卡内 expected。
  - 真题分歧 → 降级候选（★→☆ 待人工复核）
  - 陷阱题判错（说 true）→ 判别力弱，分歧信号打折
"""
import json, re, sys, time, urllib.request

URL = "http://localhost:8001/v1/chat/completions"
MODEL = "qwen2.5-math-7b-instruct"

SYS = "You are a careful mathematician. Judge whether each mathematical claim is TRUE or FALSE. FIRST output exactly one line: FINAL_JSON: {\"verdict\": true|false, \"confidence\": 0.0-1.0, \"reason\": \"<one sentence>\"} — THEN optionally a brief justification (max 3 sentences). Do NOT reason before the FINAL_JSON line."

def ask(claim: str) -> dict:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": f"Claim: {claim}\n\nJudge it now."}],
        "temperature": 0.0, "max_tokens": 1024, "stream": True,
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    chunks = []
    with urllib.request.urlopen(req, timeout=280) as r:
        for line in r:
            line = line.decode("utf-8", "ignore").strip()
            if not line.startswith("data: "): continue
            payload = line[6:]
            if payload == "[DONE]": break
            try:
                d = json.loads(payload)["choices"][0]["delta"]
                if "content" in d and d["content"]: chunks.append(d["content"])
            except Exception:
                pass
    return "".join(chunks)

def parse(text: str) -> dict:
    # 层1: FINAL_JSON（少数服从）
    m = re.findall(r'FINAL_JSON:\s*(\{.*?\})', text, re.S)
    if m:
        try:
            return json.loads(m[-1])
        except Exception:
            pass
    # 层2: qwen-math 天性 \boxed{...} 收尾（True/False/TRUE/False 等）
    b = re.findall(r'\\boxed\{[^}]*\}', text)
    tail = (b[-1] if b else text[-80:]).lower()
    if 'true' in tail and 'false' not in tail:
        return {"verdict": True, "confidence": 0.9, "reason": "boxed:true"}
    if 'false' in tail:
        return {"verdict": False, "confidence": 0.9, "reason": "boxed:false"}
    # 层3: 尾部语义
    t = text[-200:].lower()
    if re.search(r'\bis (definitely )?true\b', t) and not re.search(r'\bis (definitely )?false\b', t):
        return {"verdict": True, "confidence": 0.7, "reason": "tail:true"}
    if re.search(r'\bis (definitely )?false\b', t):
        return {"verdict": False, "confidence": 0.7, "reason": "tail:false"}
    return {"verdict": None, "confidence": 0.0, "reason": f"PARSE_FAIL: {text[-120:]}"}

def main():
    import os
    claims = [json.loads(l) for l in open("cross_claims.jsonl", encoding="utf-8")]
    results = []
    done = set()
    if os.path.exists("cross_results.jsonl"):
        keep = []
        for l in open("cross_results.jsonl", encoding="utf-8"):
            try:
                r = json.loads(l)
                if r["qwen"]["verdict"] is not None:
                    keep.append(r); done.add(r["id"])
            except Exception:
                pass
        results = keep  # 无效记录剔除重判
        print(f"resume: {len(done)} 有效 done（无效记录已剔除）", flush=True)
    todo = [c for c in claims if c["id"] not in done]
    parse_fail = 0
    for c in todo:
        t0 = time.time()
        try:
            v = parse(ask(c["claim"]))
        except Exception as e:
            v = {"verdict": None, "confidence": 0.0, "reason": f"FAIL:{e}"}
        rec = {**c, "qwen": v, "agree": (v["verdict"] == c["expected"]), "sec": round(time.time()-t0, 1)}
        results.append(rec)
        if v["verdict"] is None: parse_fail += 1
        tag = "OK " if rec["agree"] else "DIS"
        print(f'[{tag}] {c["id"]} expected={c["expected"]} qwen={v["verdict"]} conf={v["confidence"]} ({rec["sec"]}s)', flush=True)
        with open("cross_results.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    # 汇总
    trues = [r for r in results if r["expected"]]
    falses = [r for r in results if not r["expected"]]
    ta = sum(r["agree"] for r in trues); fa = sum(r["agree"] for r in falses)
    print(f"\n== 真题(★断言) {ta}/{len(trues)} 一致 | 陷阱题(应判假) {fa}/{len(falses)} 判对 | 解析失败 {parse_fail} ==")
    for r in results:
        if not r["agree"] and r["qwen"]["verdict"] is not None:
            print(f"  分歧: {r['id']} [{r['card']}] expected={r['expected']} qwen={r['qwen']['verdict']}: {r['qwen']['reason'][:100]}")
    print(f"判别力校准: 陷阱全对=强信号；陷阱错≥2=分歧信号打折")

if __name__ == "__main__":
    main()
