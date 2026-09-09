#!/usr/bin/env python3
"""
roofline_d3000m.py — 飞腾 D3000M Roofline 模型生成器

性能建模专家的核心工具。给定硬件参数 + 应用算术强度，画出 Roofline：
    Attainable GFLOPS = min(Peak Compute, Bandwidth × Arithmetic Intensity)

用法：
    python3 roofline_d3000m.py             # 生成 roofline.png
    python3 roofline_d3000m.py --no-plot   # 只输出数据

对应 Expert_09_Performance_Model/README.md。
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass


# ============================================================================
# 飞腾 D3000M 实测/数据手册参数
# ============================================================================

@dataclass
class CPUSpec:
    name: str
    frequency_ghz: float
    cores: int
    # 峰值算力（per core, GFLOPS/GOPS）
    peak_fp32_per_core: float
    peak_fp16_per_core: float
    peak_int8_per_core: float
    # 带宽（GB/s）
    bw_l1_per_core: float
    bw_l2_per_core: float
    bw_l3_total: float
    bw_dram_total: float


D3000M = CPUSpec(
    name="飞腾 D3000M (FTC862)",
    frequency_ghz=2.5,
    cores=8,
    # Lab05 实测：FP32 NEON 9.45 GFLOPS/核
    peak_fp32_per_core=9.45,
    # Lab01 实测：FP16 SIMD 比 FP32 快 3.81×，理论 2× SIMD 宽度，实际 ~17
    peak_fp16_per_core=17.0,
    # UDOT 实测 int8：~304 GOPS / 8 核 = ~38 GOPS/核（来自 int8_gemm_udot 实测）
    peak_int8_per_core=38.0,
    bw_l1_per_core=80,       # 估算
    bw_l2_per_core=40,
    bw_l3_total=120,
    bw_dram_total=80,        # DDR4-3200 × 4 ch = 102 GB/s 理论，实测 ~80
)


# ============================================================================
# Roofline 计算
# ============================================================================

def roofline(peak_gflops: float, bandwidth_gbps: float,
             arithmetic_intensity: float) -> float:
    """返回给定算术强度下的可达 GFLOPS。"""
    return min(peak_gflops, bandwidth_gbps * arithmetic_intensity)


def ridge_point(peak_gflops: float, bandwidth_gbps: float) -> float:
    """Ridge point：算力 bound 和带宽 bound 的交点。"""
    return peak_gflops / bandwidth_gbps


# ============================================================================
# 典型算子的算术强度
# ============================================================================

WORKLOADS = [
    # (name, AI, GFLOPS 实测/推测, color, marker)
    ("SpMV",              0.25, 0.4,   "black",   "v"),
    ("Conv 3x3 (small)",  3.0,  2.5,   "blue",    "s"),
    ("Attention (decode)",5.0,  3.0,   "green",   "D"),
    ("GEMM (32³)",       16.0,  4.5,   "orange",  "^"),
    ("GEMM (512³)",     341.0,  9.2,   "red",     "o"),   # Lab05 实测
    ("LLM Prefill",     100.0,  6.0,   "magenta", "P"),
]


# ============================================================================
# 输出
# ============================================================================

def print_summary(spec: CPUSpec) -> None:
    """打印 CPU 参数 + 各带宽 ridge point。"""
    peak_total_fp32 = spec.peak_fp32_per_core * spec.cores
    print(f"=== {spec.name} Roofline 参数 ===")
    print(f"频率: {spec.frequency_ghz} GHz × {spec.cores} 核")
    print(f"峰值算力:")
    print(f"  FP32 (per core / total): {spec.peak_fp32_per_core} / "
          f"{peak_total_fp32:.1f} GFLOPS")
    print(f"  FP16 (per core):         {spec.peak_fp16_per_core} GFLOPS")
    print(f"  INT8 (per core):         {spec.peak_int8_per_core} GOPS")
    print()
    print(f"带宽:")
    print(f"  L1 (per core):  {spec.bw_l1_per_core} GB/s")
    print(f"  L2 (per core):  {spec.bw_l2_per_core} GB/s")
    print(f"  L3 (total):     {spec.bw_l3_total} GB/s")
    print(f"  DRAM (total):   {spec.bw_dram_total} GB/s")
    print()
    print(f"Ridge points (算力/带宽 = 算术强度):")
    for name, bw_total in [("L1 (per core)", spec.bw_l1_per_core),
                     ("L2 (per core)", spec.bw_l2_per_core),
                     ("L3 (per core)", spec.bw_l3_total / spec.cores),
                     ("DRAM (per core)", spec.bw_dram_total / spec.cores)]:
        rp = ridge_point(spec.peak_fp32_per_core, bw_total)
        print(f"  {name:18s}: {rp:6.2f} FLOP/byte")
    print()
    print(f"=== 典型算子预测性能 ===")
    print(f"{'算子':<22} {'AI':>10} {'L2 bound':>10} {'DRAM bound':>11} {'Predicted':>10}")
    for name, ai, _, _, _ in WORKLOADS:
        # per-core bound
        l2_bound = roofline(spec.peak_fp32_per_core, spec.bw_l2_per_core, ai)
        dram_bound = roofline(spec.peak_fp32_per_core, spec.bw_dram_total / spec.cores, ai)
        predicted = min(l2_bound, dram_bound)
        print(f"{name:<22} {ai:>10.2f} {l2_bound:>10.2f} {dram_bound:>11.2f} "
              f"{predicted:>10.2f}")


def plot_roofline(spec: CPUSpec, output: str) -> None:
    """用 matplotlib 画 Roofline 图。"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("[warn] matplotlib 不可用，跳过画图")
        return

    ai = np.logspace(-2, 4, 500)   # 算术强度 0.01 - 10000 FLOP/byte

    fig, ax = plt.subplots(figsize=(11, 7))

    # 各带宽线（斜率 = 带宽，截止于 peak）
    peak_per_core = spec.peak_fp32_per_core
    for name, bw, color, ls in [
        ("L1 per core", spec.bw_l1_per_core, "tab:green", "--"),
        ("L2 per core", spec.bw_l2_per_core, "tab:blue",  "--"),
        ("L3 total / core", spec.bw_l3_total / spec.cores, "tab:orange", "--"),
        ("DRAM per core", spec.bw_dram_total / spec.cores, "tab:red",  "-"),
    ]:
        bound = np.minimum(bw * ai, peak_per_core)
        ax.plot(ai, bound, color=color, linestyle=ls, label=f"{name} ({bw:.0f} GB/s)")

    # 峰值算力水平线
    ax.axhline(peak_per_core, color="black", linestyle=":",
               label=f"Peak FP32 {peak_per_core:.1f} GFLOPS/核")

    # 算子散点
    for name, ai_op, perf_real, color, marker in WORKLOADS:
        ax.scatter([ai_op], [perf_real], s=120, c=color, marker=marker,
                   edgecolors="black", zorder=5, label=name)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Arithmetic Intensity (FLOP/byte)", fontsize=12)
    ax.set_ylabel("Attainable Performance (GFLOPS/核)", fontsize=12)
    ax.set_title(f"{spec.name} Roofline Model\n"
                 f"({spec.frequency_ghz} GHz × {spec.cores} 核, "
                 f"peak FP32 {peak_per_core:.1f} GFLOPS/核)",
                 fontsize=13)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="lower right", fontsize=9, ncol=2)
    ax.set_xlim(0.01, 10000)
    ax.set_ylim(0.05, 50)

    plt.tight_layout()
    plt.savefig(output, dpi=120, bbox_inches="tight")
    print(f"\nRoofline 图已保存: {output}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", "-o", default="roofline_d3000m.png")
    p.add_argument("--no-plot", action="store_true")
    args = p.parse_args()

    print_summary(D3000M)
    if not args.no_plot:
        plot_roofline(D3000M, args.output)


if __name__ == "__main__":
    main()
