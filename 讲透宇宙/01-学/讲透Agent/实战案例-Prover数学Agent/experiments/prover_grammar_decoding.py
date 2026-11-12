#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prover_grammar_decoding.py — 语法约束解码实验（Needle 2 思路 × Lean 证明）

背景（Needle 2 借法之三）：
  Needle 2 从工具 schema 编译 grammar，解码时只算合法 token，结构 token 跳过 98% 词表投影。
  该收益的前提是：输出空间封闭（JSON 工具调用语法封闭）。
  Lean 证明是**半开放空间**（tactic 组合无界）——强约束可能反伤证明通过率。

假设（本实验要量化）：
  H1: regex 轻约束（强制 ```lean4 块包裹）→ 提取成功率↑、结构 token 浪费↓、通过率不变
  H2: 强 grammar 约束（证明骨架 BNF）→ 通过率↓（证明多样性被截断）
  => 量化"约束收益 ∝ 输出空间封闭度"

用法（csmath 容器内，vLLM 已在 :8177）：
  python3 prover_grammar_decoding.py --problems problems_core.jsonl --out /work/distill/grammar_exp
  python3 prover_grammar_decoding.py --mode regex          # 只跑轻约束
"""
import argparse
import json
import os
import re
import subprocess
import time
import urllib.request

LEAN = os.environ.get("PROVER_LEAN", "/work/lean-4.21.0-linux/bin/lean")
CORE_HINT = "\nUse only the Lean 4 core library (no Mathlib imports, no `norm_num`/`ring`)."
API = "http://127.0.0.1:8177"
MODEL = "prover"

PROMPT = """Complete the following Lean 4 code:

```lean4
{statement}
```
Output ONLY one ```lean4 code block with the complete theorem proof, no explanation.""" + CORE_HINT

# ---------------------------------------------------------------- 约束定义
# L1 regex：强制输出形如 ```lean4\n...\n``` 的单一代码块（结构保证，内容自由）
REGEX = r"```lean4\n[^\x00]*?\n```"

# L2 grammar：简化证明骨架 BNF（GBNF EBNF 语法）。tactic 词表受限集。
# 注意：这是刻意保守的骨架约束——H2 预期它伤害通过率，用作反面对照。
GRAMMAR = r"""root ::= proof
proof ::= "```lean4\n" stmt "\n```"
stmt ::= "theorem " name " " binders ": " prop " := by" "\n  " tactic+
name ::= [a-zA-Z_] [a-zA-Z0-9_']*
binders ::= [^\n:]*
prop ::= [^\n]*
tactic ::= tactic-line ("\n  " tactic-line)*
tactic-line ::= simp-tactic | exact-tactic | rw-tactic | ind-tactic | other-tactic
simp-tactic ::= "simp" [" [" simp-args "]"]
simp-args ::= [a-zA-Z0-9_ ,'↑←]*
exact-tactic ::= "exact " term
rw-tactic ::= "rw" [" [" rw-args "]"] [" at " name]
rw-args ::= [a-zA-Z0-9_ ,'←]*
ind-tactic ::= "induction " term " with" [^\n]*
other-tactic ::= "refl" | "rfl" | "trivial" | "constructor" | "decide" | "omega" | "repeat " tactic-line | "apply " term
term ::= [^\n]+
"""


def chat(prompt, mode, max_tokens=1024, temperature=0.0, seed=1):
    """mode: free | regex | grammar。新版 vLLM 用 structured_outputs；旧版退 guided_*。"""
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature, "max_tokens": max_tokens, "seed": seed}
    if mode == "regex":
        body["structured_outputs"] = {"regex": REGEX}
    elif mode == "grammar":
        body["structured_outputs"] = {"grammar": GRAMMAR}
    req = urllib.request.Request(API + "/v1/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            d = json.loads(r.read())
        return d["choices"][0]["message"]["content"], d["usage"]["completion_tokens"], None
    except urllib.error.HTTPError as e:
        # 兼容旧版 API 名：guided_regex / guided_grammar
        err = e.read().decode()[:200]
        if "structured_outputs" in err or " guided" not in err:
            try:
                alt = dict(body)
                if mode == "regex":
                    alt.pop("structured_outputs", None); alt["guided_regex"] = REGEX
                elif mode == "grammar":
                    alt.pop("structured_outputs", None); alt["guided_grammar"] = GRAMMAR
                req2 = urllib.request.Request(API + "/v1/chat/completions",
                                               data=json.dumps(alt).encode(),
                                               headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req2, timeout=600) as r2:
                    d = json.loads(r2.read())
                return d["choices"][0]["message"]["content"], d["usage"]["completion_tokens"], "fallback_guided"
            except Exception as e2:
                return None, 0, f"alt-fail: {str(e2)[:150]}"
        return None, 0, f"http {e.code}: {err}"


def extract_code(text):
    blocks = re.findall(r"```(?:lean4|lean)?\s*\n(.*?)```", text or "", re.S)
    if blocks:
        return blocks[-1].strip(), True
    return (text or "").strip(), False   # 无块——regex 模式下不应发生


def run_lean(code, timeout=120):
    path = f"/tmp/gd_{int(time.time()*1000)%1000000}.lean"
    with open(path, "w") as f:
        f.write(code + "\n")
    try:
        r = subprocess.run([LEAN, path], capture_output=True, text=True, timeout=timeout)
        out = r.stderr + "\n" + r.stdout
        return r.returncode, out
    except subprocess.TimeoutExpired:
        return None, "lean timeout"
    finally:
        try: os.remove(path)
        except OSError: pass


def verify(code):
    rc, out = run_lean(code)
    if out == "lean timeout": return False, "timeout"
    if re.search(r"error:", out): return False, re.search(r"error:.*", out).group()[:100]
    if "declaration uses 'sorry'" in out: return False, "sorry"
    if rc not in (0, None): return False, f"exit {rc}"
    return True, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problems", default="problems_core.jsonl")
    ap.add_argument("--out", default="/work/distill/grammar_exp")
    ap.add_argument("--mode", default="all", choices=["all", "free", "regex", "grammar"])
    ap.add_argument("--limit", type=int, default=6)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    problems = [json.loads(l) for l in open(a.problems) if l.strip()][:a.limit]
    modes = ["free", "regex", "grammar"] if a.mode == "all" else [a.mode]

    results = []
    for p in problems:
        for mode in modes:
            t0 = time.time()
            text, ntok, warn = chat(PROMPT.format(statement=p["stmt"]), mode)
            if text is None:
                results.append({"name": p["name"], "mode": mode, "api_err": warn})
                print(f"[{p['name']}/{mode}] API FAIL: {warn}", flush=True)
                continue
            code, had_block = extract_code(text)
            ok, why = verify(code)
            rec = {"name": p["name"], "mode": mode, "ok": ok, "err": "" if ok else why,
                   "had_code_block": had_block, "completion_tokens": ntok,
                   "warn": warn, "secs": round(time.time()-t0, 1)}
            results.append(rec)
            print(f"[{p['name']}/{mode}] ok={ok} tokens={ntok} block={had_block} "
                  f"{rec['secs']}s {'WARN:'+str(warn) if warn else ''}", flush=True)
            with open(os.path.join(a.out, "results.jsonl"), "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 汇总
    print("\n===== summary =====")
    for mode in modes:
        rs = [r for r in results if r.get("mode") == mode and "api_err" not in r]
        if not rs: continue
        n = len(rs)
        ok = sum(1 for r in rs if r["ok"])
        blk = sum(1 for r in rs if r["had_code_block"])
        tok = sum(r["completion_tokens"] for r in rs) / n
        print(f"{mode:8s}: pass {ok}/{n}  block_rate {blk}/{n}  avg_tokens {tok:.0f}")
    print("H1 检验: regex 的 block_rate 应=100% 且 pass 不低于 free")
    print("H2 检验: grammar 的 pass 预期 < free（半开放空间被强约束截断）")


if __name__ == "__main__":
    main()
