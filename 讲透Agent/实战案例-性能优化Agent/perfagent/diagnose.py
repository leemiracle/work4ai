"""perfagent.diagnose — 诊断层：线程伸缩探针 → 工作负载画像卡（roofline-lite）。

诚实声明：这是**经验探针分类**（实测 1/2/4/物理核 的伸缩曲线），不是 SOLAR 式解析
roofline。它的定位是给提议器提供决策上下文（SemaTune 的 decision context /
KernelAgent 的 roofline 分类的零成本等价物）。
"""


def classify(probe_ms):
    """probe_ms: {threads: median_ms}。返回 (class, best_threads)。"""
    best_t = min(probe_ms, key=probe_ms.get)
    one = probe_ms.get(1)
    # thread-adverse：4 线程比 1 线程还慢 30% 以上（同步开销主导）
    four = probe_ms.get(4) or probe_ms.get(max(probe_ms))
    if four and one and four > 1.3 * one:
        cls = "thread-adverse"
    elif one and one / probe_ms[best_t] >= 2.5:
        cls = "compute-scaling"
    elif one and one / probe_ms[best_t] >= 1.5:
        cls = "partial-scaling"
    else:
        cls = "flat"          # memory/latency bound：加线程无益
    return cls, best_t


def build_card(name, spec, baseline_ms, probe_ms, ipc=None):
    cls, best_t = classify(probe_ms)
    flops = spec.get("flops", 0)
    return {
        "name": name,
        "kind": spec["kind"],
        "intensity_Mflop_per_rep": round(flops / 1e6, 1),
        "baseline_ms": round(baseline_ms, 3),
        "probe_ms": {str(t): round(m, 3) for t, m in probe_ms.items()},
        "scaling_class": cls,
        "probe_best_threads": best_t,
        "ipc_coarse": ipc,
    }
