#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""magent_run.py — 多 Agent 协作拓扑对比实验（13 节点 C500 / vllm / Prover-V2-7B）

实验设计（对应多 Agent 分类框架）：
  T1 manager  管理者模式（层级拓扑，消息传递）：Manager 出计划 → Solver 证明 → lean 验证 → 失败回灌 replan（≤3 轮）
  T2 debate   对等辩论（peer 拓扑，广播共享）：3 独立采样 → 互看修订 1 轮 → 3 候选全验证 pass@any
  T3 indep    去中心化独立并行（无通信基线）：8 独立采样全验证 pass@8
  T2b role    角色偏置微实验（信息不对称，6 题）：3 persona（minimalist/structuralist/skeptic）

等预算：每题每拓扑 LLM 调用 ≤8。全程轨迹 JSONL 落盘（每事件 flush，断点安全）。
验证器：容器内 lean 4.21（core 语法无 Mathlib）——rc==0 ∧ 无 error ∧ 无 sorry。
"""
import json, os, re, subprocess, sys, time, hashlib
from concurrent.futures import ThreadPoolExecutor

API = "http://localhost:8000/v1/chat/completions"
MODEL = "deepseek-prover"
LEAN = "/mnt/200/lwz/aiz-work/csmath/lean-4.21.0-linux/bin/lean"
OUT_DIR = "/root/luowz/work/magent"
TRACES = os.path.join(OUT_DIR, "traces.jsonl")
SUMMARY = os.path.join(OUT_DIR, "summary.json")
RUN = time.strftime("magent-%m%d-%H%M")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---- 题目（12 题：L1×3 + L2×4 + L3×5，取自 problems_core.jsonl）----
PROBS = [
    ("e1_add_zero", 1, "theorem e1_add_zero (n : Nat) : n + 0 = n := by "),
    ("e5_le_refl",  1, "theorem e5_le_refl (n : Nat) : n \u2264 n := by "),
    ("e6_sub_zero", 1, "theorem e6_sub_zero (n : Nat) : n - 0 = n := by "),
    ("m1_double",   2, "theorem m1_double (n : Nat) : 2 * n = n + n := by "),
    ("m3_succ_le",  2, "theorem m3_succ_le (n : Nat) : n \u2264 n + 1 := by "),
    ("m5_append_nil", 2, "theorem m5_append_nil (l : List Nat) : l ++ [] = l := by "),
    ("m7_sub_self", 2, "theorem m7_sub_self (n : Nat) : n - n = 0 := by "),
    ("h2_mul_comm", 3, "theorem h2_mul_comm (n m : Nat) : n * m = m * n := by "),
    ("h4_exists_succ", 3, "theorem h4_exists_succ (n : Nat) (h : n \u2260 0) : \u2203 m, n = m + 1 := by "),
    ("h6_map_len",  3, "theorem h6_map_len (l : List Nat) : (l.map (fun x => x + 1)).length = l.length := by "),
    ("h8_distrib",  3, "theorem h8_distrib (a b : Nat) : 2 * (a + b) = 2 * a + 2 * b := by "),
    ("h9_le_trans", 3, "theorem h9_le_trans (a b c : Nat) (h1 : a \u2264 b) (h2 : b \u2264 c) : a \u2264 c := by "),
]
ROLE_PROBS = [p for p in PROBS if p[1] >= 2][:6]  # T2b 用 6 道中高难题

# ---- prompt 模板（沿用官方双模式，debate/role 为工程化扩展）----
COT = """Complete the following Lean 4 code:

```lean4
{stmt}
```

Before producing the Lean 4 code, provide a brief proof plan (2-3 sentences), then the complete proof."""
NONCOT = """Complete the following Lean 4 code:

```lean4
{stmt}
```"""
REPLAN = """You are the proof manager. Your previous plan failed Lean verification.

Theorem:
```lean4
{stmt}
```

Your plan was: {plan}
The attempted proof was: {proof}
Lean error: {err}

Produce a NEW brief proof plan (different strategy), then the complete corrected proof."""
DEBATE_REVISE = """You are prover {aid} in a team of 3 provers working on:

```lean4
{stmt}
```

Your first attempt: {own}
Prover {bid} attempt: {other1}
Prover {cid} attempt: {other2}

Review all three. Produce your final best proof. Output only Lean 4 code."""
PERSONAS = {
    "minimalist": "Prefer the shortest possible proof using simp, omega, decide, or simp_arith if they work.",
    "structuralist": "Prefer explicit structural proofs using induction and rw of the defining equations.",
    "skeptic": "First double-check the statement is provable as stated, then prove it with extra care on each rewrite step.",
}
ROLE_PROMPT = """{persona}

Complete the following Lean 4 code:

```lean4
{stmt}
```"""


def extract_code(t):
    blocks = re.findall(r"```(?:lean4|lean)?\s*\n(.*?)```", t, re.S)
    return blocks[-1].strip() if blocks else t.strip()


def norm_proof(code):
    """归一化：去注释/空白/空行，小写 tactic——用于去重与趋同度量。"""
    c = re.sub(r"--[^\n]*", "", code)
    c = re.sub(r"\s+", " ", c).strip().lower()
    return c


def llm(messages, t=1.0, max_tok=512, retries=2):
    import requests
    for i in range(retries + 1):
        try:
            r = requests.post(API, json={
                "model": MODEL, "messages": messages,
                "temperature": t, "top_p": 0.95,
                "max_tokens": max_tok, "seed": None,
            }, timeout=180)
            r.raise_for_status()
            j = r.json()
            u = j["usage"]
            return j["choices"][0]["message"]["content"], u["prompt_tokens"], u["completion_tokens"]
        except Exception as e:
            if i == retries:
                return f"__API_ERR__ {e}", 0, 0
            time.sleep(3)


def verify(code, timeout=60):
    path = f"/tmp/ma_{int(time.time()*1000)%10**8}.lean"
    with open(path, "w") as f:
        f.write(code + "\n")
    try:
        r = subprocess.run([LEAN, path], capture_output=True, text=True, timeout=timeout)
        out = (r.stderr + "\n" + r.stdout).strip()
        if "declaration uses 'sorry'" in out:
            return False, "sorry"
        if "error:" in out:
            return False, out[:160].replace("\n", " ")
        if r.returncode != 0:
            return False, (out or f"exit {r.returncode}")[:160]
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "lean timeout"
    finally:
        try: os.remove(path)
        except OSError: pass


# ---------------------------------------------------------------- 轨迹
F = None
COUNTER = {"n": 0, "ptok": 0, "ctok": 0}

def _init_out():
    global F
    os.makedirs(OUT_DIR, exist_ok=True)
    F = open(TRACES, "a", buffering=1)

def ev(topo, prob, lvl, agent, call_idx, prompt, output, pt, ct, lat, vok=None, vreason="", extra=None):
    code = extract_code(output) if "__API_ERR__" not in output else output
    e = {"run": RUN, "topology": topo, "prob": prob, "level": lvl, "agent": agent,
         "call_idx": call_idx, "prompt": prompt[-1200:], "output": output[-2000:],
         "out_norm": norm_proof(code) if code else "",
         "prompt_toks": pt, "completion_toks": ct, "latency_s": round(lat, 2),
         "verify_ok": vok, "verify_reason": vreason, "ts": time.time()}
    if extra: e.update(extra)
    F.write(json.dumps(e, ensure_ascii=False) + "\n")
    COUNTER["n"] += 1; COUNTER["ptok"] += pt; COUNTER["ctok"] += ct
    return e


# ---------------------------------------------------------------- 拓扑实现
def t1_manager(name, lvl, stmt):
    """管理者模式：plan→solve→verify→replan 循环，成功即停（自适应预算）"""
    t0 = time.time(); calls = 0; solved = False; first_err = ""
    msg = [{"role": "user", "content": COT.format(stmt=stmt)}]
    ta = time.time(); plan_out, pt, ct = llm(msg, t=0.6, max_tok=1024); calls += 1
    ev("manager", name, lvl, "manager-plan", calls, msg[0]["content"], plan_out, pt, ct, time.time()-ta)
    plan = plan_out[:600]
    for rnd in range(1, 4):
        msg = [{"role": "user", "content": NONCOT.format(stmt=stmt)}]
        ta = time.time(); out, pt, ct = llm(msg, t=0.8); calls += 1
        e = ev("manager", name, lvl, "solver", calls, msg[0]["content"], out, pt, ct, time.time()-ta,
               extra={"round": rnd, "plan": plan[:300]})
        ok, reason = verify(extract_code(out))
        e["verify_ok"], e["verify_reason"] = ok, reason; F.write(json.dumps(e, ensure_ascii=False) + "\n")
        if rnd == 1: first_err = reason
        if ok:
            solved = True; break
        ta = time.time()
        msg = [{"role": "user", "content": REPLAN.format(stmt=stmt, plan=plan, proof=extract_code(out), err=reason)}]
        plan_out, pt, ct = llm(msg, t=0.6, max_tok=1024); calls += 1
        ev("manager", name, lvl, "manager-replan", calls, msg[0]["content"], plan_out, pt, ct, time.time()-ta,
           extra={"round": rnd})
        plan = plan_out[:600]
    return {"topology": "manager", "prob": name, "level": lvl, "solved": solved,
            "calls": calls, "wall_s": round(time.time()-t0, 1), "first_error": first_err[:120]}


def _batch(messages_list, t, max_tok=512):
    with ThreadPoolExecutor(4) as ex:
        return list(ex.map(lambda m: llm(m, t=t, max_tok=max_tok), messages_list))


def t2_debate(name, lvl, stmt, role_bias=None):
    """对等辩论：3 独立 → 互看修订 → pass@any。role_bias=T2b persona 字典"""
    t0 = time.time(); tag = "debate" if not role_bias else "role"
    msgs = []
    for i in range(3):
        c = (ROLE_PROMPT.format(persona=list(role_bias.values())[i], stmt=stmt)
             if role_bias else NONCOT.format(stmt=stmt))
        msgs.append([{"role": "user", "content": c}])
    res = _batch(msgs, t=1.0); calls = 3
    agents = list((role_bias or {"A": 0, "B": 0, "C": 0}).keys())
    ta = 0.0  # 并行批次内不记单次延迟，由总墙钟覆盖
    v1 = []
    for i, (out, pt, ct) in enumerate(res):
        e = ev(tag, name, lvl, f"solver-{agents[i]}", calls - 2 + i, msgs[i][0]["content"], out, pt, ct, ta)
        v1.append(e)
    ok1 = [verify(extract_code(ex_["output"])) for ex_ in v1]
    for e, (o, r) in zip(v1, ok1):
        e["verify_ok"], e["verify_reason"] = o, r; F.write(json.dumps(e, ensure_ascii=False) + "\n")
    # 修订轮
    rmsgs = []
    for i in range(3):
        others = [v1[j]["output"][:500] for j in range(3) if j != i]
        c = DEBATE_REVISE.format(aid=agents[i], stmt=stmt, own=v1[i]["output"][:500],
                                 bid=agents[(i+1) % 3], other1=others[0],
                                 cid=agents[(i+2) % 3], other2=others[1])
        rmsgs.append([{"role": "user", "content": c}])
    rres = _batch(rmsgs, t=0.8); calls += 3
    solved = False; n_identical_self = 0; n_follow_first = 0
    for i, (out, pt, ct) in enumerate(rres):
        e = ev(tag, name, lvl, f"revised-{agents[i]}", calls - 2 + i, rmsgs[i][0]["content"], out, pt, ct, 0)
        ok, r = verify(extract_code(out))
        e["verify_ok"], e["verify_reason"] = ok, r; F.write(json.dumps(e, ensure_ascii=False) + "\n")
        solved = solved or ok
        if norm_proof(extract_code(out)) == v1[i]["out_norm"]: n_identical_self += 1
        if norm_proof(extract_code(out)) == v1[0]["out_norm"]: n_follow_first += 1
    solved_any = solved or any(o for o, _ in ok1)
    return {"topology": tag, "prob": name, "level": lvl, "solved": solved_any,
            "solved_round1": any(o for o, _ in ok1),
            "calls": calls, "wall_s": round(time.time()-t0, 1),
            "identical_to_self": n_identical_self, "follow_first_agent": n_follow_first}


def t3_indep(name, lvl, stmt, n=8):
    """独立并行基线：8 采样 pass@8 + 多样性度量"""
    t0 = time.time()
    msgs = [[{"role": "user", "content": NONCOT.format(stmt=stmt)}]] * n
    res = _batch(msgs, t=1.0); calls = n
    norms, solved, first_ok_idx = [], False, -1
    for i, (out, pt, ct) in enumerate(res):
        e = ev("indep", name, lvl, "solo", i + 1, msgs[0][0]["content"], out, pt, ct, 0)
        ok, r = verify(extract_code(out))
        e["verify_ok"], e["verify_reason"] = ok, r; F.write(json.dumps(e, ensure_ascii=False) + "\n")
        norms.append(e["out_norm"])
        if ok and first_ok_idx < 0: first_ok_idx = i + 1
        solved = solved or ok
    uniq = len(set(norms))
    return {"topology": "indep", "prob": name, "level": lvl, "solved": solved,
            "pass_at_1": first_ok_idx == 1, "unique_proofs": uniq, "n_samples": n,
            "calls": calls, "wall_s": round(time.time()-t0, 1)}


def main():
    _init_out()
    results = []
    T0 = time.time()
    print(f"[{RUN}] start: 12 probs x (manager/debate/indep) + 6 probs role-bias", flush=True)
    for name, lvl, stmt in PROBS:
        print(f"== {name} (L{lvl}) ==", flush=True)
        for runner in (t1_manager, lambda n, l, s: t2_debate(n, l, s),
                       lambda n, l, s: t3_indep(n, l, s)):
            r = runner(name, lvl, stmt)
            results.append(r)
            print(f"  {r['topology']:<8} solved={r['solved']} calls={r['calls']} "
                  f"wall={r['wall_s']}s", flush=True)
    print("== T2b role bias (6 probs) ==", flush=True)
    for name, lvl, stmt in ROLE_PROBS:
        r = t2_debate(name, lvl, stmt, role_bias=PERSONAS)
        results.append(r)
        print(f"  {name} role solved={r['solved']} r1={r['solved_round1']} "
              f"identical_self={r['identical_to_self']} follow_first={r['follow_first_agent']}", flush=True)
    summary = {"run": RUN, "total_events": COUNTER["n"], "total_prompt_toks": COUNTER["ptok"],
               "total_completion_toks": COUNTER["ctok"], "wall_s": round(time.time()-T0, 1),
               "results": results}
    with open(SUMMARY, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, ensure_ascii=False), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
