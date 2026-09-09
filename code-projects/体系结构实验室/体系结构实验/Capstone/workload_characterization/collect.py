#!/usr/bin/env python3
"""
collect.py — perf stat 输出解析器 + 工作负载刻画报告生成器

用法：
    python3 collect.py data/*.perf > profile_report.md

输入：driver.sh 产生的 *.perf 文件（perf stat 文本输出）
输出：profile_report.md，含数据表 + 自动分析

工作流：
    1. driver.sh 跑各工作负载，输出保存到 data/<workload>_<config>.perf
    2. collect.py 扫描所有 .perf，解析提取关键指标
    3. 生成 markdown 表 + 自动观察 + 优化建议
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PerfRecord:
    name: str           # workload 配置名（如 "gemm_neon", "zstd_3"）
    cycles: int = 0
    instructions: int = 0
    cache_misses: int = 0
    cache_refs: int = 0
    branch_misses: int = 0
    l1d_load_misses: int = 0
    elapsed_sec: float = 0.0
    user_sec: float = 0.0

    @property
    def ipc(self) -> float:
        return self.instructions / self.cycles if self.cycles else 0.0

    @property
    def l1_miss_rate(self) -> float:
        return self.cache_misses / self.cache_refs if self.cache_refs else 0.0

    @property
    def branch_miss_rate(self) -> float:
        # branch-misses 是绝对数；如果没有 branch 总数，只能给绝对值
        return self.branch_misses

    @property
    def cpi(self) -> float:
        return 1.0 / self.ipc if self.ipc else 0.0


# perf stat 输出的字段名 → record 属性
FIELD_MAP = {
    "cycles": "cycles",
    "instructions": "instructions",
    "cache-misses": "cache_misses",
    "cache-references": "cache_refs",
    "branch-misses": "branch_misses",
    "L1-dcache-load-misses": "l1d_load_misses",
}

NUM_RE = re.compile(r"^\s*([\d,]+)\s*(?:<not supported>|<not counted>)?\s+(\S+)\s*")


def parse_perf_output(text: str, name: str) -> PerfRecord:
    """解析 perf stat 文本输出。"""
    rec = PerfRecord(name=name)
    for line in text.splitlines():
        m = NUM_RE.match(line)
        if not m:
            continue
        val_str, event = m.group(1), m.group(2)
        val = int(val_str.replace(",", ""))
        if event in FIELD_MAP:
            setattr(rec, FIELD_MAP[event], val)
        elif event == "seconds" and "time elapsed" in line:
            try:
                rec.elapsed_sec = float(val_str)
            except ValueError:
                pass
    # 时间从最后的 "X.XXXX seconds time elapsed" 抓
    m = re.search(r"([\d.]+)\s+seconds time elapsed", text)
    if m:
        rec.elapsed_sec = float(m.group(1))
    m = re.search(r"([\d.]+)\s+seconds user", text)
    if m:
        rec.user_sec = float(m.group(1))
    return rec


def load_all(data_glob: str) -> List[PerfRecord]:
    records = []
    for path in sorted(glob.glob(data_glob)):
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path) as f:
            text = f.read()
        records.append(parse_perf_output(text, name))
    return records


def fmt_md_table(records: List[PerfRecord]) -> str:
    lines = [
        "| 工作负载 | Cycles (G) | Instr (G) | **IPC** | CPI | "
        "L1 Miss (M) | Miss Rate | Br Miss (M) | 耗时(s) |",
        "|---------|-----------:|----------:|:-------:|----:|"
        "-----------:|----------:|------------:|---------:|",
    ]
    for r in records:
        lines.append(
            f"| `{r.name}` | {r.cycles/1e9:.2f} | {r.instructions/1e9:.2f} | "
            f"**{r.ipc:.2f}** | {r.cpi:.2f} | "
            f"{r.cache_misses/1e6:.1f} | {r.l1_miss_rate*100:.2f}% | "
            f"{r.branch_misses/1e6:.2f} | {r.elapsed_sec:.2f} |"
        )
    return "\n".join(lines)


def fmt_ipc_bar_chart(records: List[PerfRecord]) -> str:
    """ASCII IPC 柱状图，便于在 markdown 里直观比较。"""
    if not records:
        return ""
    max_ipc = max(r.ipc for r in records)
    width = 40
    lines = ["```", f"{'workload':<20} {'IPC':>6}  (max={max_ipc:.2f})"]
    for r in records:
        bar = "█" * int(width * r.ipc / max(max_ipc, 0.01))
        lines.append(f"{r.name:<20} {r.ipc:>6.2f}  {bar}")
    lines.append("```")
    return "\n".join(lines)


def analyze(records: List[PerfRecord]) -> List[str]:
    """自动产出关键观察 + 优化建议。"""
    obs = []
    if not records:
        return obs

    # IPC 排序
    by_ipc = sorted(records, key=lambda r: -r.ipc)
    obs.append(f"- **IPC 最高**：`{by_ipc[0].name}` = {by_ipc[0].ipc:.2f}"
               f"（接近理论 4-wide 峰值 IPC=4 的 {by_ipc[0].ipc/4*100:.0f}%）。")
    obs.append(f"- **IPC 最低**：`{by_ipc[-1].name}` = {by_ipc[-1].ipc:.2f}"
               f"，瓶颈通常是访存或分支密集。")

    # L1 miss
    by_miss = sorted(records, key=lambda r: -r.l1_miss_rate)
    worst = by_miss[0]
    if worst.l1_miss_rate > 0.10:
        obs.append(f"- **L1 miss 率最高**：`{worst.name}` = {worst.l1_miss_rate*100:.2f}%"
                   f"——明显的 cache 不友好模式，建议分块 / 数据布局优化。")
    else:
        obs.append(f"- **L1 miss 率整体健康**（最高 {worst.l1_miss_rate*100:.2f}%），"
                   f"工作负载具有良好的空间 / 时间局部性。")

    # branch
    by_bm = sorted(records, key=lambda r: -r.branch_misses)
    worst_bm = by_bm[0]
    if worst_bm.branch_misses > 50_000_000:
        obs.append(f"- **分支预测失败最多**：`{worst_bm.name}` = "
                   f"{worst_bm.branch_misses/1e6:.0f}M 次，"
                   f"建议重排分支（把 `if (rare) → else` 改为 likely/unlikely 提示）。")

    # Top-Down 推断（基于 IPC + miss）
    obs.append("\n### 基于数据的 Top-Down 推断\n")
    obs.append("| 工作负载 | 推测瓶颈 | 优化方向 |")
    obs.append("|---------|---------|---------|")
    for r in by_ipc:
        if r.ipc < 0.5:
            bottleneck = "Backend Bound（访存）"
            opt = "数据预取 / 分块 / 大页"
        elif r.ipc < 1.0:
            bottleneck = "Backend / Frontend 混合"
            opt = "减小工作集 / 循环展开"
        elif r.ipc < 2.0:
            bottleneck = "依赖链 / 局部 miss"
            opt = "打破依赖链 / 算子融合"
        else:
            bottleneck = "无显著瓶颈"
            opt = "已接近 4-wide 极限"
        obs.append(f"| `{r.name}` | {bottleneck} | {opt} |")
    return obs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("inputs", nargs="+", help=".perf 文件 globs")
    p.add_argument("--output", "-o", default=None)
    args = p.parse_args()

    records = []
    for pattern in args.inputs:
        records.extend(load_all(pattern))

    md = []
    md.append("# Capstone-C: 工作负载刻画报告\n")
    md.append("> 本报告由 `collect.py` 自动生成，所有数据来自 `driver.sh` 跑出的 "
              "`perf stat` 输出。\n")
    md.append(f"**生成时间**：{time.strftime('%Y-%m-%d %H:%M:%S')}  ")
    md.append(f"**工作负载数**：{len(records)}\n")
    md.append("---\n")

    md.append("## 1. 性能指标总览\n")
    md.append(fmt_md_table(records))

    md.append("\n## 2. IPC 可视化\n")
    md.append(fmt_ipc_bar_chart(records))

    md.append("\n---\n")
    md.append("## 3. 自动分析\n")
    for line in analyze(records):
        md.append(line)

    md.append("\n---\n")
    md.append("## 4. 优化建议（详细版见 [`recommendations.md`](./recommendations.md)）\n")
    md.append("- 见 [`recommendations.md`](./recommendations.md) 的 5 条具体可落地建议。")
    md.append("- 见 [`../alpha_21264_study/comparison.md`](../alpha_21264_study/comparison.md) "
              "的微架构上下文对比。\n")

    md.append("## 5. 数据可重现性\n")
    md.append("```bash")
    md.append("# 重跑所有工作负载 + 重新生成本报告")
    md.append("cd Capstone/workload_characterization")
    md.append("./driver.sh            # 重新跑 + 写 data/")
    md.append("python3 collect.py 'data/*.perf' -o profile_report.md")
    md.append("```\n")

    output = "\n".join(md)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
