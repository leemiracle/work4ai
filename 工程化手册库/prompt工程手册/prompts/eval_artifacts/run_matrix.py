#!/usr/bin/env python3
"""自带矩阵 runner：glm-4.7 / glm-5.3（thinking disabled，直连 zhipu coding 端点）。
- 黄金集：config_v2_flash.yaml 的 tests（与 promptfoo 跑 flash 的完全同一份）
- 评分：score.js 逻辑的 Python 精确移植（组间AND/组内ANY + 空集罚分 + leak/forbidden）
- 输出：promptfoo 兼容 results/v2_<model>.json
- 自校验：用 flash 已有 promptfoo 结果的 raw output 跑 Python 评分器，与 JS 判定对比
"""
import json, os, re, time, yaml, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

KEY = open("/tmp/opencode/zhipu_key").read().strip()
BASE = "https://open.bigmodel.cn/api/coding/paas/v4"
ART = "~/ai/work4ai/工程化手册库/prompt工程手册/prompts/eval_artifacts"

# ---------- 载入 ----------
cfg = yaml.safe_load(open(f"{ART}/config_v2_flash.yaml"))
tests = cfg["tests"]
variants = {os.path.basename(p["id"].replace("file://", "")): p for p in cfg["prompts"]}
var_files = {k: json.load(open(f"{ART}/variants/{k}")) for k in ["additive_orig.json", "additive_slim.json", "fact_v1.json"]}

def render(msgs, vars_):
    out = []
    for m in msgs:
        c = m["content"]
        for k, v in vars_.items():
            c = c.replace("{{" + k + "}}", str(v))
        out.append({"role": m["role"], "content": c})
    return out

# ---------- 评分器（score.js 的精确移植） ----------
def score_output(output, vars_):
    text = str(output)
    try:
        expected = json.loads(vars_.get("expected_facts") or "[]")
    except Exception:
        expected = []
    m = re.search(r"\{[\s\S]*\}", text)
    parsed = None
    if m:
        try: parsed = json.loads(m.group(0))
        except Exception: parsed = None
    if parsed is None:
        return False, 0.0, "JSON parse failed: " + text[:100]
    items = parsed.get("memory") or parsed.get("facts") or []
    texts = [x if isinstance(x, str) else (x or {}).get("text", "") for x in (items if isinstance(items, list) else [])]
    texts = [t for t in texts if t and t.strip()]
    joined = " \n ".join(texts).lower()
    for key in ["leak_markers", "forbidden_markers"]:
        mk = vars_.get(key)
        if mk:
            try:
                hit = next(x for x in json.loads(mk) if str(x).lower() in text.lower())
                return False, 0.0, f"{key.upper()} HIT: '{hit}'"
            except StopIteration: pass
            except Exception: pass
    if len(expected) == 0:
        if texts:
            return False, 0.0, "Expected empty, got " + str(len(texts)) + ": " + " | ".join(texts[:2])[:150]
        return True, 1.0, "correctly empty"
    hit, missing = 0, []
    for grp in expected:
        kws = grp if isinstance(grp, list) else [grp]
        if any(str(kw).lower() in joined for kw in kws): hit += 1
        else: missing.append("[" + "|".join(map(str, kws)) + "]")
    s = hit / len(expected)
    return s >= 0.8, s, f"recall {hit}/{len(expected)}" + (" MISS " + ";".join(missing)[:200] if missing else "") + f"; n={len(texts)}"

# ---------- 自校验：flash promptfoo 结果 × Python 评分器 ----------
def self_validate():
    R = json.load(open(f"{ART}/results/v2_flash.json"))["results"]
    agree = disagree = 0
    for r in R["results"]:
        ok, s, reason = score_output((r.get("response") or {}).get("output"), r["vars"])
        js_pass = bool(r.get("success"))
        if ok == js_pass: agree += 1
        else:
            disagree += 1
            if disagree <= 3:
                print(f"  DISAGREE: {r['testCase']['description']} py={ok} js={js_pass} :: {reason[:80]}")
    print(f"[self-validate] agree={agree} disagree={disagree}")
    return disagree <= 3  # 允许个别边界，>3 视为移植有误

# ---------- API 调用 ----------
lock = threading.Lock()
def call_api(messages, model):
    body = {"model": model, "messages": messages, "temperature": 0, "max_tokens": 2048,
            "thinking": {"type": "disabled"}}
    last_err = None
    for attempt in range(3):
        req = urllib.request.Request(f"{BASE}/chat/completions", data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.load(r)
            msg = resp["choices"][0]["message"]
            usage = resp.get("usage", {})
            return msg.get("content", ""), (time.time()-t0)*1000, {
                "prompt": usage.get("prompt_tokens", 0), "completion": usage.get("completion_tokens", 0),
                "total": usage.get("total_tokens", 0), "cached": 0}
        except Exception as e:
            last_err = e; time.sleep(3 * (attempt + 1))
    raise last_err

def run_model(model, out_name):
    prompts_meta = [{"id": p["id"], "label": p.get("label", p["id"])} for p in cfg["prompts"]]
    results = [None] * (len(tests) * 3)
    def work(ti, vi):
        vfname = ["additive_orig.json", "additive_slim.json", "fact_v1.json"][vi]
        test = tests[ti]
        msgs = render(var_files[vfname], test["vars"])
        try:
            out, lat, tok = call_api(msgs, model)
            ok, s, reason = score_output(out, test["vars"])
            return {"promptId": f"file://variants/{vfname}", "promptIdx": vi, "testIdx": ti,
                    "testCase": test, "vars": test["vars"], "success": ok, "score": s,
                    "latencyMs": round(lat), "tokenUsage": tok, "response": {"output": out},
                    "gradingResult": {"pass": ok, "score": s, "reason": reason}}
        except Exception as e:
            return {"promptId": f"file://variants/{vfname}", "promptIdx": vi, "testIdx": ti,
                    "testCase": test, "vars": test["vars"], "success": False, "score": 0,
                    "latencyMs": 0, "tokenUsage": {"prompt":0,"completion":0,"total":0,"cached":0},
                    "response": {"output": ""}, "gradingResult": {"pass": False, "score": 0,
                    "reason": "API_ERROR: " + str(e)[:120]}, "failureReason": "error"}
    jobs = [(ti, vi) for ti in range(len(tests)) for vi in range(3)]
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(work, ti, vi): (ti, vi) for ti, vi in jobs}
        done = 0
        for f in as_completed(futs):
            ti, vi = futs[f]
            results[ti * 3 + vi] = f.result()
            done += 1
            if done % 60 == 0: print(f"  {model}: {done}/{len(jobs)}")
    doc = {"results": {"prompts": prompts_meta, "results": [r for r in results if r]}}
    out_path = f"{ART}/results/{out_name}"
    json.dump(doc, open(out_path, "w"), ensure_ascii=False)
    npass = sum(1 for r in doc["results"]["results"] if r["success"])
    nerr = sum(1 for r in doc["results"]["results"] if r.get("failureReason") == "error")
    print(f"[{model}] {npass}/{len(results)} pass, {nerr} api-errors -> {out_path}")

if __name__ == "__main__":
    import sys
    if not self_validate():
        print("SELF-VALIDATION FAILED — scorer port mismatch, abort"); sys.exit(1)
    for model, out in [("glm-4.7", "v2_47.json"), ("glm-5.3", "v2_53.json")]:
        t0 = time.time()
        run_model(model, out)
        print(f"  took {(time.time()-t0)/60:.1f} min")
