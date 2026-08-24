"""perfagent.sensors — 感知层：拓扑探测 + 可选 perf stat 遥测。"""
import os
import re
import subprocess

NPROC = os.cpu_count() or 1


def topology():
    """物理核数/SMT 检测（/proc/cpuinfo 的 (physical id, core id) 去重）。失败则保守假设无 SMT。"""
    pairs, cur = set(), {}
    try:
        for line in open("/proc/cpuinfo"):
            line = line.strip()
            if not line:
                if cur.get("core id") is not None:
                    pairs.add((cur.get("physical id"), cur.get("core id")))
                cur = {}
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                cur[k.strip()] = v.strip()
        if cur.get("core id") is not None:
            pairs.add((cur.get("physical id"), cur.get("core id")))
    except Exception:
        pass
    phys = len(pairs) or NPROC
    return {"nproc": NPROC, "physical_cores": phys, "smt": NPROC > phys}


def perf_stat_cmd(cmd, env, events=("cycles", "instructions")):
    """可选遥测：perf stat 包裹子进程命令。权限不足/无 perf → 返回 None（优雅降级）。
    注意：包裹的是整个子进程（含 numpy import），IPC 是粗粒度信号，仅作辅助诊断。"""
    if subprocess.run(["which", "perf"], capture_output=True).returncode != 0:
        return None
    full = ["perf", "stat", "-x,", "-e", ",".join(events), "--"] + cmd
    try:
        r = subprocess.run(full, capture_output=True, text=True, env=env, timeout=600)
        vals = {}
        for line in r.stderr.splitlines():
            # -x, 格式：value,,event,time,...（event 在第 3 字段）
            parts = line.split(",")
            if len(parts) >= 3:
                for ev in ("cycles", "instructions"):
                    if parts[2] == ev:
                        try:
                            vals[ev] = float(parts[0].replace(",", ""))
                        except ValueError:
                            pass
        if "cycles" in vals and "instructions" in vals and vals["cycles"] > 0:
            return {"ipc": round(vals["instructions"] / vals["cycles"], 3)}
    except Exception:
        pass
    return None
