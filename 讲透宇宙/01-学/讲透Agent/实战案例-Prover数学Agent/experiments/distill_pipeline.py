#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""distill_pipeline.py — DeepSeek-Prover-V2 逆向蒸馏数据流水线（批量版）

规律映射（README §一 + Needle 2 借法）：
  Needle generate-data（从工具 schema 合成 JSONL 微调数据）
    → 本流水线从"题库 + 分解"合成 Lean 证明 JSONL 微调数据
  R1 分解降跨度：CoT 自分解 → have 骨架 → 逐 sorry 填充（前序已证 have 天然成为上下文 premises）
  R2 ZPD 策展：只收「e2e 全失败 ∧ 分解后子目标全解 ∧ 终验通过」的问题为蒸馏数据
  R4 子目标课程：分解出的 have 链即难度降级的课程序列
  R5 专家迭代：Lean 验证器二值把关；wins/traps 库落盘积累
  R8 双模式 prompt：e2e 先 non-CoT 后 CoT；分解用 CoT 变体
  R10 诚实边界：architect=7B 自分解（论文用 671B）——self-distillation 变体，弱化预期；
     premises 经上下文注入而非显式假设（论文机制未单独消融，工程取实用版）

用法（csmath 容器内）：
  python3 distill_pipeline.py --problems problems_core.jsonl --out /work/distill/out
  python3 distill_pipeline.py ... --resume        # 断点续跑（默认开）

产物（OUT 目录）：
  precheck.json   题库语句编译预检（语句本身必须合法）
  e2e.jsonl       端到端尝试记录（每 problem 聚合一行）
  distill.jsonl   ★ZPD 蒸馏数据（SFT 就绪：messages 格式 + plan 字段可消融）
  wins.jsonl      全部成功证明（e2e 路线 + subgoal 路线）
  traps.jsonl     失败档案（子目标错误信息——R7 尾部技能富矿的原料）
  progress.json   每 problem 状态机（resume 依据）
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

# ---------------------------------------------------------------- 常量
LEAN = os.environ.get("PROVER_LEAN", "/work/lean-4.21.0-linux/bin/lean")
CORE_HINT = "\nUse only the Lean 4 core library (no Mathlib imports, no `norm_num`/`ring`)."

NONCOT = """Complete the following Lean 4 code:

```lean4
{statement}
```""" + CORE_HINT

COT = """Complete the following Lean 4 code:

```lean4
{statement}
```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.""" + CORE_HINT

DECOMPOSE = """You are a proof architect. Decompose the following Lean 4 theorem into a chain of easier subgoals.

Instructions:
1. Write the proof as a Lean 4 skeleton: each intermediate step is a `have` statement whose proof is exactly `sorry`.
2. Each subgoal must be strictly easier than the original — provable in 1-3 tactic steps.
3. The final step combines all `have`s to close the main goal.
4. Use only Lean 4 core library. No Mathlib, no `norm_num`/`ring`.
5. Output ONLY one ```lean4 code block containing the complete theorem with the have-chain. No explanation.

Theorem to decompose:

```lean4
{statement}
```""".strip()

FILL = """Complete the following Lean 4 code. The proof already has a `have`-chain skeleton.
Fill in ONLY the FIRST `sorry` (replace it with a real tactic proof). Keep every other `sorry` unchanged.
Use only Lean 4 core library. Output ONLY the complete Lean 4 code, no explanation.

```lean4
{code}
```""".strip()


def extract_code(text: str) -> str:
    """提取 Lean 代码：优先最后一个 ```lean4 块；无块时从首个 theorem/import 行截取，
    去掉模型爱加的 markdown 头（# 标题）与尾注（非代码行）。"""
    blocks = re.findall(r"```(?:lean4|lean)?\s*\n(.*?)```", text, re.S)
    if blocks:
        return blocks[-1].strip()
    m = re.search(r"^(theorem|import|lemma|example)\b.*$", text, re.M)
    if not m:
        s = re.search(r"\b(theorem|import|lemma|example)\b", text)
        if not s:
            return text.strip()
        code = text[s.start():]
    else:
        code = text[m.start():]
    code = code.split("```")[0]                    # 尾部闭合 fence 截断
    lines = []
    for ln in code.split("\n"):                    # 去掉尾部非代码行（markdown 残留）
        if ln.strip().startswith(("#", "*", "-", "This ", "Note ", "Here ")):
            break
        lines.append(ln)
    return "\n".join(lines).strip()


# ---------------------------------------------------------------- 验证器（R5 守门员）
def run_lean(code: str, timeout: int = 120):
    path = f"/tmp/dp_{int(time.time()*1000)%1000000}.lean"
    with open(path, "w") as f:
        f.write(code + "\n")
    try:
        r = subprocess.run([LEAN, path], capture_output=True, text=True, timeout=timeout)
        out = (r.stderr + "\n" + r.stdout)
        return r.returncode, out
    except subprocess.TimeoutExpired:
        return None, "lean timeout"
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def count_sorry(out: str) -> int:
    return len(re.findall(r"declaration uses 'sorry'", out))


def has_error(out: str) -> str:
    m = re.search(r"error:.*", out)
    if m:
        i = out.rfind("\n", 0, m.start()) + 1
        return out[i:i + 180].strip()
    return ""


def verify_final(code: str):
    """终验：exit 0 ∧ 无 error ∧ 无 sorry（'能编译'≠'证完了'）。"""
    rc, out = run_lean(code)
    if out == "lean timeout":
        return False, "lean timeout"
    if has_error(out):
        return False, has_error(out)
    if count_sorry(out) > 0:
        return False, "contains sorry"
    if rc != 0:
        return False, f"exit {rc}"
    return True, ""


def verify_step(code: str):
    """步验：无 error 即可（允许剩余 sorry）。返回 (ok, err, n_sorry)。"""
    rc, out = run_lean(code)
    if out == "lean timeout":
        return False, "lean timeout", 0
    e = has_error(out)
    if e:
        return False, e, 0
    if rc not in (0, None):
        return False, f"exit {rc}", 0
    return True, "", count_sorry(out)


# ---------------------------------------------------------------- API 客户端
class Client:
    def __init__(self, base, model):
        self.base = base.rstrip("/")
        self.model = model

    def wait_up(self, max_wait=1200):
        t0 = time.time()
        while time.time() - t0 < max_wait:
            try:
                with urllib.request.urlopen(self.base + "/v1/models", timeout=5) as r:
                    if r.status == 200:
                        print("[api] server up", flush=True)
                        return True
            except Exception:
                pass
            time.sleep(10)
        return False

    def chat(self, prompt, max_tokens, temperature, seed=None):
        body = {"model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature, "max_tokens": max_tokens}
        if seed is not None:
            body["seed"] = seed
        req = urllib.request.Request(
            self.base + "/v1/chat/completions", data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"})
        last = None
        for attempt in range(5):                  # server 重启窗口 ~75s 内自动扛过
            try:
                with urllib.request.urlopen(req, timeout=600) as resp:
                    return json.loads(resp.read())["choices"][0]["message"]["content"]
            except Exception as e:
                last = e
                time.sleep(min(5 * (attempt + 1), 40))
        raise RuntimeError(f"api failed: {last}")


# ---------------------------------------------------------------- 状态与落盘
class Store:
    def __init__(self, outdir):
        self.out = outdir
        os.makedirs(outdir, exist_ok=True)
        self.progress_path = os.path.join(outdir, "progress.json")
        self.progress = {}
        if os.path.exists(self.progress_path):
            self.progress = json.load(open(self.progress_path))

    def st(self, name):
        return self.progress.get(name, {"stage": "init"})

    def set(self, name, **kw):
        self.progress.setdefault(name, {}).update(kw)
        with open(self.progress_path, "w") as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=1)

    def append(self, fname, rec):
        with open(os.path.join(self.out, fname), "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- 各阶段
def precheck(problems, store):
    """题库预检：语句本身必须编译（只有 sorry warning）。坏题丢弃并记录。"""
    pc_path = os.path.join(store.out, "precheck.json")
    if os.path.exists(pc_path):
        kept = [p for p in json.load(open(pc_path))["kept"]]
        return kept
    kept, dropped = [], []
    for p in problems:
        rc, out = run_lean(p["stmt"] + "  sorry\n")
        e = has_error(out)
        if e or rc not in (0, None):
            dropped.append({"name": p["name"], "err": e or f"exit {rc}"})
            print(f"[precheck] DROP {p['name']}: {e[:80]}")
        else:
            kept.append(p)
    json.dump({"kept": kept, "dropped": dropped}, open(pc_path, "w"), ensure_ascii=False, indent=1)
    print(f"[precheck] kept {len(kept)} / dropped {len(dropped)}", flush=True)
    return kept


def stage_e2e(p, cli, store, k_noncot=4):
    """Stage 0：端到端。non-CoT×k（temp .7 不同 seed）+ CoT×1。任一通过即 e2e-solved。"""
    attempts = []
    for mode, maxnew in (("noncot", 512), ("cot", 1536)):
        n = k_noncot if mode == "noncot" else 1
        for i in range(n):
            seed = i + 1
            temp = 0.0 if (mode == "cot" or i == 0) else 0.7
            try:
                text = cli.chat((NONCOT if mode == "noncot" else COT).format(statement=p["stmt"]),
                                maxnew, temp, seed)
            except RuntimeError as e:
                attempts.append({"mode": mode, "seed": seed, "ok": False, "err": str(e)[:120]})
                continue
            code = extract_code(text)
            ok, why = verify_final(code)
            attempts.append({"mode": mode, "seed": seed, "ok": ok,
                             "err": "" if ok else why[:140], "code": code if ok else code[:200]})
            if ok:
                return True, attempts, code, mode
    return False, attempts, None, None


def stage_decompose(p, cli):
    """Stage 1：7B 自分解（R10 注：论文用 671B 建筑师，此处 self-distill 变体）。"""
    for temp, seed in ((0.0, 7), (0.7, 8)):
        try:
            text = cli.chat(DECOMPOSE.format(statement=p["stmt"]), 1024, temp, seed)
        except RuntimeError:
            continue
        sk = extract_code(text)
        if "sorry" not in sk or "theorem" not in sk:
            continue
        ok, err, ns = verify_step(sk)
        if ok and 1 <= ns <= 8:            # 骨架编译通过 ∧ sorry 数合理
            return sk, ns
    return None, 0


def stage_fill(p, cli, store, skeleton):
    """Stage 2：逐 sorry 填充（R1：前序已证 have 在上下文=premises 注入）。
    每轮让模型只填第一个 sorry；接受条件=无 error ∧ sorry 数下降。"""
    code = skeleton
    n0 = code.count("sorry")
    subgoal_recs = []
    for round_ in range(n0 * 3 + 2):        # 安全上限
        cur = code.count("sorry")
        if cur == 0:
            break
        got = False
        for temp, seed in ((0.0, 11), (0.7, 12), (1.0, 13)):
            try:
                text = cli.chat(FILL.format(code=code), 1024, temp, seed)
            except RuntimeError:
                continue
            cand = extract_code(text)
            if "theorem" not in cand:
                continue
            ok, err, ns = verify_step(cand)
            if ok and ns < cur:
                subgoal_recs.append({"round": round_, "temp": temp,
                                     "sorries_left": ns, "delta": cur - ns})
                code = cand
                store.append("traps_clean.jsonl", {}) if False else None
                got = True
                break
            elif not ok:
                subgoal_recs.append({"round": round_, "temp": temp, "err": err[:140]})
        if not got:
            return None, subgoal_recs       # 卡死 → 失败
    return (code if code.count("sorry") == 0 else None), subgoal_recs


def run(problems_path, out, base, model, resume, limit):
    cli = Client(base, model)
    if not cli.wait_up():
        sys.exit("[fatal] vLLM server 未就绪")
    store = Store(out)
    problems = [json.loads(l) for l in open(problems_path) if l.strip()]
    problems = precheck(problems, store)
    if limit:
        problems = problems[:limit]

    for p in problems:
        name = p["name"]
        st = store.st(name)
        if resume and st.get("stage") in ("done", "failed"):
            continue
        t0 = time.time()
        # ---- Stage 0 e2e（若全程 api 不可达：等 server 复活重试一轮，绝不落死标记）
        api_dead = False
        for round_ in range(2):
            solved, attempts, proof, mode = stage_e2e(p, cli, store)
            api_dead = (not solved and attempts
                        and all(str(a.get("err", "")).startswith("api") for a in attempts))
            if not api_dead:
                break
            print(f"[{name}] api unreachable — waiting for server, retry e2e", flush=True)
            if not cli.wait_up(600):
                break
        if api_dead and not solved:
            store.set(name, stage="init")          # 交还 resume 重试
            print(f"[{name}] api down, deferred", flush=True)
            continue
        store.append("e2e.jsonl", {"name": name, "level": p["level"],
                                   "solved": solved, "attempts": [
                                       {k: v for k, v in a.items() if k != "code"}
                                       for a in attempts]})
        if solved:
            store.append("wins.jsonl", {"name": name, "route": f"e2e-{mode}",
                                        "proof": proof, "secs": round(time.time() - t0, 1)})
            store.set(name, stage="done", route=f"e2e-{mode}")
            print(f"[{name}] e2e SOLVED ({mode}) {time.time()-t0:.0f}s", flush=True)
            continue
        # ---- Stage 1 decompose
        sk, ns = stage_decompose(p, cli)
        if sk is None:
            ok_up = cli.wait_up(300)
            if ok_up:                              # server 曾挂导致分解失败 → 重试一次
                sk, ns = stage_decompose(p, cli)
        if sk is None:
            store.append("traps.jsonl", {"name": name, "where": "decompose",
                                         "level": p["level"]})
            store.set(name, stage="failed", where="decompose")
            print(f"[{name}] decompose FAILED", flush=True)
            continue
        # ---- Stage 2 fill
        filled, recs = stage_fill(p, cli, store, sk)
        if filled is None:
            store.append("traps.jsonl", {"name": name, "where": "subgoal",
                                         "level": p["level"], "detail": recs[-3:]})
            store.set(name, stage="failed", where="subgoal")
            print(f"[{name}] subgoal STUCK ({time.time()-t0:.0f}s)", flush=True)
            continue
        # ---- Stage 3 终验
        ok, why = verify_final(filled)
        if not ok:
            store.append("traps.jsonl", {"name": name, "where": "final", "err": why[:140]})
            store.set(name, stage="failed", where="final")
            print(f"[{name}] final verify FAILED: {why[:80]}", flush=True)
            continue
        # ---- Stage 4 ZPD 入库（R2：e2e 失败 ∧ 分解路线成功 → 蒸馏数据）
        rec = {"name": name, "level": p["level"], "statement": p["stmt"],
               "skeleton": sk, "proof": filled,
               "n_subgoals": ns, "subgoal_trace": recs,
               "e2e_attempts": len(attempts),
               "messages": [
                   {"role": "user", "content": NONCOT.format(statement=p["stmt"])},
                   {"role": "assistant", "content": f"```lean4\n{filled}\n```"}],
               "secs": round(time.time() - t0, 1)}
        store.append("distill.jsonl", rec)
        store.append("wins.jsonl", {"name": name, "route": "subgoal", "proof": filled,
                                    "secs": rec["secs"]})
        store.set(name, stage="done", route="subgoal")
        print(f"[{name}] ★DISTILL ({ns} subgoals, {time.time()-t0:.0f}s)", flush=True)

    # ---- 汇总
    n_distill = sum(1 for s in store.progress.values() if s.get("route") == "subgoal")
    n_e2e = sum(1 for s in store.progress.values() if str(s.get("route", "")).startswith("e2e"))
    n_fail = sum(1 for s in store.progress.values() if s.get("stage") == "failed")
    print(f"\n[summary] distill={n_distill} e2e-solved={n_e2e} failed={n_fail}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problems", default="problems_core.jsonl")
    ap.add_argument("--out", default="/work/distill/out")
    ap.add_argument("--api", default="http://127.0.0.1:8177")
    ap.add_argument("--model", default="prover")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-resume", dest="resume", action="store_false")
    a = ap.parse_args()
    run(a.problems, a.out, a.api, a.model, a.resume, a.limit)


if __name__ == "__main__":
    main()
