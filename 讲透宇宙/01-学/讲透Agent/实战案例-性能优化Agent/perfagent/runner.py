"""perfagent.runner — 子进程隔离测量（一次调用 = 正确性 + 确定性 + 计时）。

防线设计（对应 SOL-ExecBench 沙箱）：
  1) 双 nonce 随机输入指纹 —— 正确性必须在两组不同输入上成立（防单输入碰运气）
  2) 同输入复跑确定性 —— Wafer 假加速案防法（输出必须 bitwise 级一致）
  3) 计时输入扰动三档 —— 防状态缓存作弊的军备竞赛阶梯：
       0 = 恒定输入（漏洞模式，红队对照）
       1 = 逐 rep 内容扰动（防内容键缓存；指针键可绕过）
       2 = 逐 rep 输入对象轮换（copy 生成新指针+新内容；内容键与指针键全防
           ——对应 SOL-ExecBench 的 ShiftingMemoryPool 思路）

调用：python3 runner.py WORKLOAD SAMPLES INNER IMPL PERTURB(0|1|2)
输出：stdout 最后一行 JSON。
"""
import json
import statistics
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workloads import SPECS, gen, run_op, fingerprint, stable_seed, fp_close

NONCES = (101, 202)   # 正确性 nonce（跨进程确定）
TIMING_SEED = 303     # 计时输入基种子（与正确性 nonce 区分）


def main():
    w, samples, inner, impl, perturb = (
        sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
        sys.argv[4], int(sys.argv[5]))
    spec = SPECS[w]
    cache = {} if impl.startswith("cheat") else None

    # 1) 正确性：双 nonce 指纹
    fps = {}
    for nonce in NONCES:
        fps[nonce] = fingerprint(
            run_op(spec, gen(spec, stable_seed(w, nonce)), impl, cache))

    # 2) 确定性：nonce-101 输入复跑
    fp_det = fingerprint(
        run_op(spec, gen(spec, stable_seed(w, NONCES[0])), impl, cache))
    det_ok = fp_close(fps[NONCES[0]], fp_det, 1e-12)

    # 3) 计时：三档扰动（见模块 docstring）
    t_inputs = gen(spec, stable_seed(w, TIMING_SEED))
    times, counter = [], 0
    for _s in range(samples):
        for _i in range(inner):
            counter += 1
            call_inputs = t_inputs
            if perturb == 1:
                t_inputs[0].flat[0] = float(counter)          # 内容变，指针不变
            elif perturb == 2:
                fresh = t_inputs[0].copy()                    # 新对象：新指针
                fresh.flat[0] = (float(counter) if fresh.dtype.kind == "f"
                                 else counter % max(2, int(fresh.flat[0]) + 2))
                call_inputs = [fresh, *t_inputs[1:]]          # 内容也变
            t0 = time.perf_counter()
            run_op(spec, call_inputs, impl, cache)
            times.append((time.perf_counter() - t0) * 1000.0)
    st = sorted(times)
    print(json.dumps({
        "median_ms": statistics.median(times),
        "p10_ms": st[max(0, len(st) // 10)],
        "p90_ms": st[min(len(st) - 1, len(st) * 9 // 10)],
        "fps": {str(n): f for n, f in fps.items()},
        "det_ok": det_ok,
    }))


if __name__ == "__main__":
    main()
