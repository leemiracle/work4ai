# -*- coding: utf-8 -*-
"""prover_smoke_api.py — 走 vLLM OpenAI server 的冒烟客户端（HTTP 版）

背景：内网 DCU vLLM offline LLM 类的 detokenize 损坏（Ġ/Ċ 未还原+空格吞失）；
server 模式管线不同（Qwen3-32B 曾在此栈跑通），HTTP content 预期正常。
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:8177/v1/chat/completions"
MODEL = "prover"
LEAN = "/work/lean-4.21.0-linux/bin/lean"
OUT = "/work/prover-smoke"

PROMPT_COT = """Complete the following Lean 4 code:

```lean4
{}
```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.""".strip()

PROMPT_NONCOT = """Complete the following Lean 4 code:

```lean4
{}
```""".strip()

THEOREMS = [
    ("t1-rfl", "theorem smoke_add : 2 + 2 = 4 := by\n"),
    ("t2-have", "theorem smoke_have (a b : Nat) (h : a = b) : a + 0 = b := by\n"),
    ("t3-lemma", "theorem smoke_succ (n : Nat) : n + 1 = Nat.succ n := by\n"),
]


def extract_lean(text):
    blocks = re.findall(r"```(?:lean4|lean)?\s*\n(.*?)```", text, re.S)
    if blocks:
        return blocks[-1].strip()
    return text.strip()


def verify(code, name):
    path = os.path.join(OUT, f"{name}.lean")
    with open(path, "w") as f:
        f.write(code + "\n")
    try:
        r = subprocess.run([LEAN, path], capture_output=True, text=True,
                           timeout=120)
        err = (r.stderr + "\n" + r.stdout).strip()  # lean 4.21 错误走 stdout，必须合并
        sorry = "declaration uses 'sorry'" in err
        return (r.returncode == 0 and not err and not sorry), err[:300], sorry
    except subprocess.TimeoutExpired:
        return False, "lean timeout", False


def chat(prompt, max_tokens):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0, "max_tokens": max_tokens, "seed": 30,
    }).encode()
    req = urllib.request.Request(
        BASE, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]


def main():
    results = []
    for name, stmt in THEOREMS:
        for mode, prompt, maxnew in (("cot", PROMPT_COT, 1024),
                                     ("noncot", PROMPT_NONCOT, 256)):
            t0 = time.time()
            text = chat(prompt.format(stmt), maxnew)
            code = extract_lean(text)
            ok, err, sorry = verify(code, f"{name}-{mode}")
            rec = {"name": name, "mode": mode, "ok": bool(ok),
                   "sorry": bool(sorry), "secs": round(time.time() - t0, 1),
                   "err": err if not ok else "", "code": code[:600],
                   "raw_head": text[:150]}
            results.append(rec)
            print(f"[{name}/{mode}] ok={ok} sorry={sorry} {rec['secs']}s"
                  + (f" err:{err[:140]}" if not ok else ""), flush=True)
    with open(os.path.join(OUT, "smoke_results.json"), "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"[done] {sum(r['ok'] for r in results)}/{len(results)} 通过",
          flush=True)


if __name__ == "__main__":
    main()
