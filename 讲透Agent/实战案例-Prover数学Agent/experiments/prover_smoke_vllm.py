# -*- coding: utf-8 -*-
"""prover_smoke_vllm.py — DeepSeek-Prover-V2-7B × 海光 DCU × vLLM 最小闭环

闭环 = 官方 prompt（CoT/non-CoT）→ vLLM 生成 → 提取 Lean → lean 4.21 验证
vLLM 0.23.1 rocm633（海光定制）绕开 transformers 5.12 DynamicCache 崩溃。
"""
import json
import os
import re
import subprocess
import time

from vllm import LLM, SamplingParams

MODEL = "/work/models/DeepSeek-Prover-V2-7B"
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
    return blocks[-1].strip() if blocks else text.strip()


def verify(code, name):
    path = os.path.join(OUT, f"{name}.lean")
    with open(path, "w") as f:
        f.write(code + "\n")
    try:
        r = subprocess.run([LEAN, path], capture_output=True, text=True,
                           timeout=120)
        err = r.stderr.strip()
        sorry = "declaration uses 'sorry'" in err
        return (r.returncode == 0 and not err and not sorry), \
            err[:300], sorry
    except subprocess.TimeoutExpired:
        return False, "lean timeout", False


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    llm = LLM(model=MODEL, dtype="bfloat16", max_model_len=8192,
              gpu_memory_utilization=0.85, trust_remote_code=True)
    print(f"[vllm] loaded {time.time()-t0:.0f}s", flush=True)
    tok = llm.get_tokenizer()

    # 批量构造两模式全部请求（vLLM 连续批处理，一次跑完）
    reqs, meta = [], []
    for name, stmt in THEOREMS:
        for mode, prompt, maxnew in (("cot", PROMPT_COT, 1024),
                                     ("noncot", PROMPT_NONCOT, 256)):
            text = tok.apply_chat_template(
                [{"role": "user", "content": prompt.format(stmt)}],
                tokenize=False, add_generation_prompt=True)
            reqs.append(text)
            meta.append((name, mode, maxnew))

    results = []
    pending = list(zip(reqs, meta))
    # 按各自 max_tokens 分组采样
    outs = []
    for maxnew in (1024, 256):
        group = [(t, m) for t, m in pending if m[2] == maxnew]
        sp = SamplingParams(temperature=0.0, max_tokens=maxnew, seed=30)
        batch = llm.generate([t for t, _ in group], sp)
        outs.extend(zip([m for _, m in group], batch))

    for (name, mode, _), o in outs:
        # 海光 vLLM 的 detokenize 异常（Ġ/Ċ 未还原）→ 手动 decode token_ids
        text = tok.decode(o.outputs[0].token_ids, skip_special_tokens=True)
        code = extract_lean(text)
        ok, err, sorry = verify(code, f"{name}-{mode}")
        rec = {"name": name, "mode": mode, "ok": bool(ok),
               "sorry": bool(sorry), "n_tok": len(o.outputs[0].token_ids),
               "err": err if not ok else "", "code": code[:600]}
        results.append(rec)
        print(f"[{name}/{mode}] ok={ok} sorry={sorry} "
              f"{rec['n_tok']}tok" + (f" err:{err[:120]}" if not ok else ""),
              flush=True)
    with open(os.path.join(OUT, "smoke_results.json"), "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"[done] {sum(r['ok'] for r in results)}/{len(results)} 通过",
          flush=True)


if __name__ == "__main__":
    main()
