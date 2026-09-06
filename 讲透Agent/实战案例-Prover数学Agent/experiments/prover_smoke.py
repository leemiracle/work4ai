# -*- coding: utf-8 -*-
"""prover_smoke.py — DeepSeek-Prover-V2-7B 在海光 DCU 上的最小闭环冒烟

闭环 = 官方 prompt（CoT/non-CoT 双模式）→ 生成 → 提取 Lean 代码 → lean 4.21 验证
测试定理：核心库可证（单文件 lean 无 mathlib；mathlib lake 项目属正式 harness 下一步）
"""
import json
import os
import re
import subprocess
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "/work/models/DeepSeek-Prover-V2-7B"
LEAN = "/work/lean-4.21.0-linux/bin/lean"
OUT = "/work/prover-smoke"

# ---- 官方 prompt（GitHub README Quick Start 逐字保真）----
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

# 由易到难：rfl 单步 → have 子目标结构 → 需要引理调用
THEOREMS = [
    ("t1-rfl", "theorem smoke_add : 2 + 2 = 4 := by\n"),
    ("t2-have", "theorem smoke_have (a b : Nat) (h : a = b) : a + 0 = b := by\n"),
    ("t3-lemma", "theorem smoke_succ (n : Nat) : n + 1 = Nat.succ n := by\n"),
]


def extract_lean(text):
    """提取最后一个 ```lean4/lean 代码块；无块则原样返回（non-CoT 常见）。"""
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
        # lean 无输出=验证通过；sorry 会出 warning 但 exit 0——显式拒 sorry
        has_sorry = "declaration uses 'sorry'" in err
        return (r.returncode == 0 and not err), err[:300], has_sorry
    except subprocess.TimeoutExpired:
        return False, "lean timeout", False


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    print(f"[load] torch={torch.__version__} cuda={torch.cuda.is_available()} "
          f"dev={torch.cuda.get_device_name(0) if torch.cuda.is_available() else '?'}",
          flush=True)
    tok = AutoTokenizer.from_pretrained(MODEL)
    # 海光 DCU 兼容链：SDPA→eager（cache_utils 在 DTK 上 cat 维度崩）
    try:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL, dtype=torch.bfloat16, trust_remote_code=True,
            attn_implementation="eager", device_map="auto")
        print("[load] attn=eager bf16", flush=True)
    except Exception as e:
        print(f"[load] eager 失败 {e} → 降级 fp32", flush=True)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL, dtype=torch.float32, trust_remote_code=True,
            attn_implementation="eager", device_map="auto")
    model.eval()
    print(f"[load] done in {time.time()-t0:.0f}s", flush=True)

    results = []
    for name, stmt in THEOREMS:
        for mode, prompt, maxnew in (
                ("cot", PROMPT_COT, 1024), ("noncot", PROMPT_NONCOT, 256)):
            t1 = time.time()
            chat = [{"role": "user", "content": prompt.format(stmt)}]
            # transformers 5.12 坑：apply_chat_template(tokenize=True) 返回 BatchEncoding
            enc = tok.apply_chat_template(
                chat, tokenize=True, add_generation_prompt=True,
                return_tensors="pt")
            ids = enc["input_ids"].to(model.device) \
                if hasattr(enc, "keys") else enc.to(model.device)
            attn = enc.get("attention_mask")
            attn = attn.to(model.device) if attn is not None else None
            torch.manual_seed(30)      # 官方示例种子
            with torch.no_grad():
                out = model.generate(
                    ids,
                    **({"attention_mask": attn} if attn is not None else {}),
                    max_new_tokens=maxnew, do_sample=False,
                    pad_token_id=tok.eos_token_id)
            text = tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
            code = extract_lean(text)
            ok, err, sorry = verify(code, f"{name}-{mode}")
            rec = {"name": name, "mode": mode, "ok": bool(ok and not sorry),
                   "sorry": bool(sorry), "gen_s": round(time.time()-t1, 1),
                   "n_out": int(out.shape[1] - ids.shape[1]),
                   "err": err if not ok else "",
                   "code": code[:500]}
            results.append(rec)
            print(f"[{name}/{mode}] ok={rec['ok']} sorry={sorry} "
                  f"{rec['gen_s']}s {rec['n_out']}tok", flush=True)
            if not ok:
                print(f"  err: {err[:160]}", flush=True)
    with open(os.path.join(OUT, "smoke_results.json"), "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    n_ok = sum(r["ok"] for r in results)
    print(f"[done] {n_ok}/{len(results)} 通过 → {OUT}/smoke_results.json",
          flush=True)


if __name__ == "__main__":
    main()
