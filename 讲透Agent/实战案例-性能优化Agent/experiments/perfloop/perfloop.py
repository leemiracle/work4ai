#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perfloop — CPU 性能调优裸 loop（讲透Agent/实战案例-性能优化Agent/03 实验代码）

闭环：propose → validate → apply → measure → guard → keep/revert → win/trap 记忆
零第三方依赖（仅 numpy）。~240 行，对应 README §2.3 的 SemaTune/LumOS 式最小闭环。

设计对照（每一段都能映射到头部项目的做法）：
  - 失败四级分类          ← KernelBench eval.py 五重裁判（compile/run/correct/fast 分开记）
  - 正确性前置于性能      ← KernelBench eval.py:610
  - 子进程隔离测量        ← SOL-ExecBench 子进程隔离（防状态泄漏）
  - 输出确定性检查        ← Wafer 104× 假加速案的防法（同输入跑两遍必须一致）
  - 统计指纹比对          ← 抓"垃圾输出恰好蒙混"（全零/NaN 一眼假）
  - typed validation     ← SemaTune：LLM/搜索提议先过类型+范围+联合约束校验
  - excessive speedup    ← KernelBench eval.py:691 的怀疑阈值（CPU 场景取 5×）
  - win/trap 库          ← KernelBlaster optimization_database.json 模式
  - proposer 插槽        ← 易变/不变分离：grid（零依赖）| llm（OpenAI 兼容 API）

用法：
  python3 perfloop.py                          # grid proposer（默认，零依赖）
  python3 perfloop.py --proposer llm           # LLM 提议（需 env，见 LLMProposer）
  python3 perfloop.py --iters-large 3 --iters-small 30   # 调测量预算
"""
import argparse
import itertools
import json
import os
import statistics
import subprocess
import sys
import time
import urllib.request

# ---------------------------------------------------------------- 动作面（knob 规格）
# typed validation 的数据源：每个 knob 声明 (类型, 最小, 最大)；联合约束另加规则
KNOB_SPEC = {
    "OMP_NUM_THREADS": (int, 1, 8),
    "OPENBLAS_NUM_THREADS": (int, 1, 8),
}
MAX_CPUS = os.cpu_count() or 1
SUSPICION_THRESHOLD = 5.0   # 比 baseline 快 5× 以上：先怀疑测量，再相信魔法
WORKLOADS = [               # 双负载：预期得出相反结论（调优结论依赖负载）
    {"name": "matmul-256", "size": 256, "iters_key": "iters_small"},
    {"name": "matmul-2048", "size": 2048, "iters_key": "iters_large"},
]

def validate(cfg: dict):
    """typed validation：类型、范围、联合约束。不过线的提议不配碰机器（REJECT）。"""
    for k, v in cfg.items():
        if k not in KNOB_SPEC:
            return False, f"unknown knob {k}"
        typ, lo, hi = KNOB_SPEC[k]
        if not isinstance(v, int) or isinstance(v, bool):
            return False, f"{k} must be int, got {type(v).__name__}"
        if not (lo <= v <= min(hi, MAX_CPUS)):
            return False, f"{k}={v} out of [{lo},{min(hi, MAX_CPUS)}]"
    if "OMP_NUM_THREADS" in cfg and "OPENBLAS_NUM_THREADS" in cfg \
       and cfg["OMP_NUM_THREADS"] != cfg["OPENBLAS_NUM_THREADS"]:
        return False, "joint constraint: OMP != OPENBLAS threads (avoid mixed pools)"
    return True, "ok"

# ---------------------------------------------------------------- 测量（子进程隔离）
def _fingerprint(a):
    """统计指纹：sum/mean/max/fro-norm。抗浮点非确定性，抓垃圾输出（全零/NaN）。"""
    import numpy as np
    a = np.asarray(a)
    return [float(x) for x in (a.sum(), a.mean(), a.max(), float((a * a).sum() ** 0.5))]

def _fp_close(fp1, fp2, rel=1e-6):
    return all(abs(x - y) <= rel * max(1.0, abs(x)) for x, y in zip(fp1, fp2))

def child_main(size: int, iters: int):
    """子进程：warmup → 计时 iterations 次取中位 → 确定性检查（首末两次指纹必须一致）。"""
    import numpy as np
    rng = np.random.default_rng(42)
    a = rng.standard_normal((size, size)).astype(np.float64)
    b = rng.standard_normal((size, size)).astype(np.float64)
    out = a @ b                      # warmup（含 BLAS 线程池初始化）
    fp_first = _fingerprint(out)
    times = []
    for _ in range(iters):
        t0 = time.perf_counter()
        out = a @ b
        times.append((time.perf_counter() - t0) * 1000.0)
    fp_last = _fingerprint(out)
    print(json.dumps({
        "median_ms": statistics.median(times),
        "all_times_ms": [round(t, 3) for t in times],
        "fp_first": fp_first, "fp_last": fp_last,
        "deterministic": _fp_close(fp_first, fp_last, rel=1e-12),
    }))

def measure(cfg: dict, workload: dict, iters: int, timeout: int = 300) -> dict:
    """apply+measure 事务：只构造传给子进程的 env（不碰系统状态），失败自动'回滚'。"""
    env = dict(os.environ)
    for k, v in cfg.items():
        env[str(k)] = str(v)
    try:
        r = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--child",
             str(workload["size"]), str(iters)],
            capture_output=True, text=True, env=env, timeout=timeout)
        if r.returncode != 0:
            return {"verdict": "measure_error", "error": r.stderr.strip()[-300:]}
        return json.loads(r.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return {"verdict": "measure_error", "error": "timeout"}

# ---------------------------------------------------------------- guard（确定性代码，不是 LLM）
def guard(result: dict, baseline: dict) -> dict:
    """四级失败分类学 + 正确性前置 + 怀疑阈值。LLM/搜索器永远不拥有 keep 的宣布权。"""
    if result.get("verdict") == "measure_error":
        return {**result, "verdict": "measure_error"}                # 1) 跑不起来
    if not result.get("deterministic", False):
        return {**result, "verdict": "invalid",
                "why": "non-deterministic output (Wafer-style silent failure)"}  # 2) 输出抖动
    if not _fp_close(result["fp_first"], baseline["fp_first"]):
        return {**result, "verdict": "invalid",
                "why": "fingerprint mismatch (wrong output)"}        # 3) 不正确 → 不许谈快
    speedup = baseline["median_ms"] / result["median_ms"]            # 4) 正确了才比快慢
    verdict = "keep" if speedup > 1.05 else "revert"                 # 5% 噪声带以上才算赢
    flag = "SUSPICIOUS" if speedup > SUSPICION_THRESHOLD else ""     # 怀疑但不断罪
    return {**result, "verdict": verdict, "speedup": round(speedup, 3), "flag": flag}

# ---------------------------------------------------------------- proposer（易变插槽）
def grid_proposer(seen: set):
    """零依赖基线：全网格扫描（跳过历史已测）。LLM proposer 的对照组。"""
    for t in range(1, MAX_CPUS + 1):
        cfg = {"OMP_NUM_THREADS": t, "OPENBLAS_NUM_THREADS": t}
        key = json.dumps(cfg, sort_keys=True)
        if key not in seen:
            yield cfg

class LLMProposer:
    """插槽：OpenAI 兼容 API。env: PERFLOOP_LLM_BASE_URL / _API_KEY / _MODEL。
    输入=遥测+历史 win/trap（SemaTune 决策上下文），输出=knob 提议（仍要过 validate+guard）。"""
    def __init__(self):
        self.base = os.environ.get("PERFLOOP_LLM_BASE_URL", "").rstrip("/")
        self.key = os.environ.get("PERFLOOP_LLM_API_KEY", "")
        self.model = os.environ.get("PERFLOOP_LLM_MODEL", "glm-5.3")
        if not (self.base and self.key):
            sys.exit("[perfloop] LLM proposer 需要 PERFLOOP_LLM_BASE_URL/_API_KEY；或用 --proposer grid")

    def __call__(self, telemetry: str):
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是 CPU 性能调优专家。只输出 JSON："
                 '{"OMP_NUM_THREADS": int, "OPENBLAS_NUM_THREADS": int}，不要解释。'},
                {"role": "user", "content": telemetry},
            ],
            "temperature": 0.2,
        }).encode()
        req = urllib.request.Request(
            self.base + "/chat/completions", data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.key}"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            txt = json.loads(resp.read())["choices"][0]["message"]["content"]
        return json.loads(txt[txt.index("{"): txt.rindex("}") + 1])

# ---------------------------------------------------------------- 主循环
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proposer", choices=["grid", "llm"], default="grid")
    ap.add_argument("--iters-small", type=int, default=30)
    ap.add_argument("--iters-large", type=int, default=5)
    ap.add_argument("--child", action="store_true", help=argparse.SUPPRESS)  # 子进程入口
    args, extra = ap.parse_known_args()
    if args.child:                                          # 用法: perfloop.py --child SIZE ITERS
        child_main(int(extra[0]), int(extra[1]))
        return

    here = os.path.dirname(os.path.abspath(__file__))
    hist_path = os.path.join(here, "results.jsonl")          # win/trap 库（跨 session warm-start）
    history, seen = [], set()
    if os.path.exists(hist_path):
        with open(hist_path) as f:
            history = [json.loads(l) for l in f if l.strip()]
        seen = {json.dumps(h["cfg"], sort_keys=True) for h in history if not h.get("baseline")}

    iters_map = {"iters_small": args.iters_small, "iters_large": args.iters_large}
    print(f"[perfloop] cpus={MAX_CPUS} proposer={args.proposer} history={len(history)} 条")

    # 基准配置 = 全默认（不动 knob）。每个负载先量基准 + 记指纹
    baselines = {}
    for w in WORKLOADS:
        r = measure({}, w, iters_map[w["iters_key"]])       # 空 cfg = 继承当前环境
        assert "median_ms" in r, f"baseline failed: {r}"
        baselines[w["name"]] = r
        print(f"[baseline] {w['name']}: {r['median_ms']:.1f} ms (threads=default)")

    proposer = LLMProposer() if args.proposer == "llm" else None
    telemetry = json.dumps({n: round(b["median_ms"], 2) for n, b in baselines.items()} |
                           {"history": [(h["cfg"], h.get("verdict"), h.get("speedup")) for h in history[-10:]]},
                           ensure_ascii=False)
    candidates = []
    if proposer:  # LLM 模式：提议 K 个候选
        for _ in range(min(MAX_CPUS, 8)):
            try:
                candidates.append(proposer(telemetry))
            except Exception as e:
                print(f"[proposer] LLM 调用失败: {e}")
                break
    else:
        candidates = grid_proposer(seen)

    log = open(os.path.join(here, "run.log"), "a")
    for cfg in candidates:
        ok, why = validate(cfg)                              # ① typed validation（REJECT 在这）
        if not ok:
            print(f"[REJECT] {cfg} — {why}"); continue
        key = json.dumps(cfg, sort_keys=True)
        if key in seen:
            print(f"[SKIP]   {cfg} 已测过（win/trap 库命中）"); continue
        row = {"ts": time.strftime("%F %T"), "cfg": cfg}
        for w in WORKLOADS:                                  # ② apply+measure（事务式）
            res = measure(cfg, w, iters_map[w["iters_key"]])
            judged = guard(res, baselines[w["name"]])        # ③ guard 四级判定
            row[w["name"]] = {k: v for k, v in judged.items() if k != "all_times_ms"}
            tag = judged.get("verdict", "?")
            sp = judged.get("speedup", "")
            print(f"[{tag.upper():6s}] threads={cfg['OMP_NUM_THREADS']} {w['name']}: "
                  f"{judged.get('median_ms', -1):.1f} ms  speedup={sp}"
                  + (f"  ⚠{judged['flag']}" if judged.get("flag") else "")
                  + (f"  ({judged.get('why')})" if judged.get("why") else ""))
        with open(hist_path, "a") as f:                      # ④ 追加进 win/trap 库
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        log.write(json.dumps(row, ensure_ascii=False) + "\n")
        seen.add(key)
    log.close()

    # 摘要：每个负载的最佳配置（keep 中最快者）
    all_rows = [json.loads(l) for l in open(hist_path) if l.strip()]
    print("\n===== 摘要（keep 中最优）=====")
    for w in WORKLOADS:
        best = min((h for h in all_rows
                    if w["name"] in h and h[w["name"]].get("verdict") == "keep"),
                   key=lambda h: h[w["name"]]["median_ms"], default=None)
        if best:
            print(f"{w['name']}: threads={best['cfg']['OMP_NUM_THREADS']} "
                  f"{best[w['name']]['median_ms']:.1f} ms (x{best[w['name']]['speedup']})")
        else:
            print(f"{w['name']}: 无 keep 配置")

if __name__ == "__main__":
    main()
