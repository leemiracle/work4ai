"""perfagent.actions — 动作面：knob 规格 + typed validation + 执行命令构造。

候选配置 schema：{"threads": int, "affinity": str|None, "impl": "ref"|"cheat_cache"}
  threads   → 统一写入 OMP/OPENBLAS/MKL/NUMEXPR 四个线程 env（SemaTune typed 写入）
  affinity  → taskset -c CPU 列表（第二 knob，E3 用）
  impl      → 负载实现选择（"cheat_cache" 仅红队模式放行）

安全语义：child_env 先**剥离**继承的线程 env——baseline=真默认，candidate=显式设置，
两者对称，不存在"父进程环境泄漏造成的隐性配置"。
"""
import os
import re

THREAD_KEYS = ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
               "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]
NPROC = os.cpu_count() or 1


def expand(aff):
    out = []
    for part in aff.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def validate(cfg, allowed_impls=("ref",)):
    """typed validation：类型/范围/联合约束。不过线的提议不配碰机器（REJECT）。"""
    threads = cfg.get("threads")
    if not isinstance(threads, int) or isinstance(threads, bool):
        return False, "threads must be int"
    if not (1 <= threads <= NPROC):
        return False, f"threads {threads} out of [1,{NPROC}]"
    aff = cfg.get("affinity")
    if aff is not None:
        if not isinstance(aff, str) or not re.fullmatch(r"\d+(-\d+)?(,\d+(-\d+)?)*", aff):
            return False, f"bad affinity {aff!r}"
        cpus = expand(aff)
        if not cpus or max(cpus) >= NPROC:
            return False, "affinity cpus out of range"
        if threads > len(cpus):
            return False, f"threads {threads} > affinity width {len(cpus)} (oversubscribe)"
    impl = cfg.get("impl", "ref")
    if impl not in allowed_impls:
        return False, f"impl {impl!r} not allowed here"
    return True, "ok"


def child_cmd(cfg, runner_path, args):
    cmd = []
    if cfg.get("affinity"):
        cmd += ["taskset", "-c", cfg["affinity"]]
    cmd += [os.environ.get("PERFAGENT_PY", "python3"), runner_path, *args]
    return cmd


def child_env(cfg):
    env = dict(os.environ)
    for k in THREAD_KEYS:            # 剥离继承值（见模块 docstring 的对称语义）
        env.pop(k, None)
    if cfg.get("threads"):
        for k in THREAD_KEYS:
            env[k] = str(cfg["threads"])
    return env
