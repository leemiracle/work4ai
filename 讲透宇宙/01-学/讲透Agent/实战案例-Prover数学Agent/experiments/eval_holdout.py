#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval_holdout.py — 微调前后 pass@k 对比（专家迭代第一轮闭环的裁判端）

用法（容器内）：
  # 基线（serve 着原模型时）
  python3 eval_holdout.py --tag base --api http://127.0.0.1:8177 --model prover
  # 蒸馏后（serve 合并模型时）
  python3 eval_holdout.py --tag distilled --api http://127.0.0.1:8178 --model prover-distill
  # 汇总
  python3 eval_holdout.py --compare base distilled

指标：pass@k（greedy 1 次 + temp0.7 k-1 次，任一 Lean 终验通过即过）
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
NONCOT = """Complete the following Lean 4 code:

```lean4
{statement}
```""" + CORE_HINT


def extract_code(text):
    blocks = re.findall(r"```(?:lean4|lean)?\s*\n(.*?)```", text, re.S)
    return blocks[-1].strip() if blocks else text.strip()


def verify_final(code, timeout=120):
    path = f"/tmp/ev_{int(time.time()*1000)%1000000}.lean"
    with open(path, "w") as f:
        f.write(code + "\n")
    try:
        r = subprocess.run([LEAN, path], capture_output=True, text=True, timeout=timeout)
        out = r.stderr + "\n" + r.stdout
        if "error:" in out:
            m = re.search(r"error:.*", out)
            i = out.rfind("\n", 0, m.start()) + 1
            return False, out[i:i+120].strip()
        if "declaration uses 'sorry'" in out:
            return False, "sorry"
        if r.returncode != 0:
            return False, f"exit {r.returncode}"
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "timeout"
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def chat(base, model, prompt, max_tokens, temperature, seed):
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": prompt}],
                       "temperature": temperature, "max_tokens": max_tokens,
                       "seed": seed}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/v1/chat/completions",
                                 data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]


def run_eval(tag, api, model, problems_path, k, outdir):
    problems = [json.loads(l) for l in open(problems_path) if l.strip()]
    results = []
    for p in problems:
        ok_any, first_proof, tries = False, None, []
        for i in range(k):
            temp = 0.0 if i == 0 else 0.7
            seed = 100 + i
            try:
                text = chat(api, model, NONCOT.format(statement=p["stmt"]),
                            512, temp, seed)
            except Exception as e:
                tries.append({"i": i, "ok": False, "err": f"api: {e}"})
                continue
            code = extract_code(text)
            ok, why = verify_final(code)
            tries.append({"i": i, "ok": ok, "err": "" if ok else why[:100]})
            if ok and not ok_any:
                ok_any, first_proof = True, code
        results.append({"name": p["name"], "level": p["level"],
                        "pass": ok_any, "proof": first_proof, "tries": tries})
        print(f"[{p['name']}] {'PASS' if ok_any else 'fail'}", flush=True)
    path = os.path.join(outdir, f"eval_{tag}.json")
    json.dump(results, open(path, "w"), ensure_ascii=False, indent=1)
    n = sum(r["pass"] for r in results)
    print(f"[{tag}] pass@{k}: {n}/{len(results)}", flush=True)
    return path


def compare(outdir, tags):
    data = {}
    for t in tags:
        path = os.path.join(outdir, f"eval_{t}.json")
        data[t] = {r["name"]: r["pass"] for r in json.load(open(path))}
    names = sorted(set().union(*[set(d) for d in data.values()]))
    print(f"{'problem':<24}" + "".join(f"{t:<12}" for t in tags))
    for n in names:
        row = "".join(("✓    " if d.get(n) else "·    ") for d in [data[t] for t in tags])
        print(f"{n:<24}{row}")
    for t in tags:
        print(f"total {t}: {sum(data[t].values())}/{len(names)}")
    flipped = [n for n in names if len({data[t].get(n) for t in tags}) > 1]
    print(f"翻转题（行为变化）: {flipped if flipped else '无'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="")
    ap.add_argument("--api", default="http://127.0.0.1:8177")
    ap.add_argument("--model", default="prover")
    ap.add_argument("--problems", default="problems_holdout.jsonl")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--outdir", default="/work/distill/out")
    ap.add_argument("--compare", nargs="+", default=[])
    a = ap.parse_args()
    if a.compare:
        compare(a.outdir, a.compare)
    else:
        run_eval(a.tag, a.api, a.model, a.problems, a.k, a.outdir)


if __name__ == "__main__":
    main()
