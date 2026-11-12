"""perfagent.guard — 裁判层（确定性代码，不是 LLM）。

四级判定 + 怀疑标记（KernelBench eval.py 哲学：怀疑但不断罪）：
  measure_error  子进程跑不起来（含 taskset 缺失/超时）
  invalid        确定性失败（Wafer 案）或指纹不匹配（输出错误/作弊被抓）
  keep / revert  正确性通过后才比快慢；>5× 挂 SUSPICIOUS flag
"""
from workloads import fp_close

SUSPICIOUS = 5.0
KEEP_MARGIN = 1.05      # 5% 噪声带以上才算赢


def judge(res, base, rel=1e-4):
    """容差分层（2026-08-24 bert 教训后 v2 设计）：
      同实现复跑确定性 = det_ok，bitwise 级（runner 内 1e-12，不动）
      跨实现指纹比对   = rel 参数，数值级（默认 1e-4——放过分块/求和顺序差，
                        仍抓住 O(1) 级垃圾输出与作弊）
    bert 实测：threads 3/5/6 在 1e-6 下误报 INVALID（BLAS 分块→LayerNorm/
    softmax 数值放大）；真作弊（cheat 指纹 O(1) 差）在 1e-4 下照抓不误。"""
    if "median_ms" not in res:
        return {"verdict": "measure_error",
                "error": res.get("error", "unknown")[-200:]}
    if not res.get("det_ok", False):
        return {**res, "verdict": "invalid",
                "why": "non-deterministic output (Wafer-style silent failure)"}
    for n, base_fp in base["fps"].items():
        if n not in res["fps"] or not fp_close(res["fps"][n], base_fp, rel):
            return {**res, "verdict": "invalid",
                    "why": f"fingerprint mismatch @nonce {n} (wrong output / cheat caught)"}
    speedup = base["median_ms"] / res["median_ms"]
    verdict = "keep" if speedup >= KEEP_MARGIN else "revert"
    flag = "SUSPICIOUS" if speedup > SUSPICIOUS else ""
    return {**res, "verdict": verdict,
            "speedup": round(speedup, 3), "flag": flag}
