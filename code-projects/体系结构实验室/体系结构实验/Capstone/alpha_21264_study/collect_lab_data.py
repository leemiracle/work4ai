#!/usr/bin/env python3
"""
collect_lab_data.py — 跑 Lab00-Lab04 反推程序，提取飞腾 D3000M 真机微架构数据

用法：
    python3 collect_lab_data.py > lab_data.json
    python3 collect_lab_data.py --md > lab_data.md

输出会被 Capstone-A 的 comparison.md 引用。
所有数字都是当前机器实测，不是抄 README。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run(cmd: List[str], timeout: int = 60) -> str:
    """跑命令，返回 stdout。失败返回空串并打印 stderr。"""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=ROOT)
        if r.returncode != 0:
            print(f"[warn] {cmd} returned {r.returncode}: {r.stderr[:200]}",
                  file=sys.stderr)
        return r.stdout
    except subprocess.TimeoutExpired:
        print(f"[warn] {cmd} timed out", file=sys.stderr)
        return ""
    except FileNotFoundError:
        print(f"[warn] {cmd[0]} not found", file=sys.stderr)
        return ""


def taskset_cmd(cpu: int, prog: str) -> List[str]:
    return ["taskset", "-c", str(cpu), prog]


# ============================================================================
# 各 Lab 的采集器
# ============================================================================

def collect_arch_probe() -> Dict:
    """Lab00/arch_probe：基础架构信息。"""
    out = run(taskset_cmd(0, "Lab00_测量基础设施/src/arch_probe"))
    data = {"raw_output": out[:5000]}
    # 解析关键字段
    m = re.search(r"part\s+=\s+(\S+)\s+\((\S+)\)", out)
    if m:
        data["part_number"] = m.group(1)
        data["part_name"] = m.group(2)
    m = re.search(r"cores online\s+=\s+(\d+)", out)
    if m: data["cores"] = int(m.group(1))
    m = re.search(r"freq_cur\s+=\s+(\d+)", out)
    if m: data["freq_mhz"] = int(m.group(1)) // 1000
    m = re.search(r"governor\s+=\s+(\S+)", out)
    if m: data["governor"] = m.group(1)
    # cache 信息
    caches = []
    for line in out.splitlines():
        m = re.match(r"\s*L0[^:]*:size=\s*(\d+K)\s+ways=\s*(\d+)\s+line=\s*(\d+)\s+sets=\s*(\d+)\s+\((\w+)\)", line)
        if m:
            caches.append({
                "size": m.group(1), "ways": int(m.group(2)),
                "line": int(m.group(3)), "scope": m.group(5),
            })
    if caches:
        data["caches"] = caches
    return data


def collect_null_loop() -> Dict:
    """Lab00/null_loop：反推 issue width 和 ALU 端口数。"""
    out = run(taskset_cmd(0, "Lab00_测量基础设施/src/null_loop"))
    data = {}
    for variant in ["loop_empty", "loop_volatile", "loop_nop", "loop_add"]:
        m = re.search(rf"{variant}.*IPC=([\d.]+)", out)
        if m:
            data[variant] = {"ipc": float(m.group(1))}
    # 反推：loop_volatile IPC = issue width；loop_add IPC = ALU 端口数
    if "loop_volatile" in data:
        data["issue_width"] = round(data["loop_volatile"]["ipc"])
    if "loop_add" in data:
        data["alu_ports_per_cycle"] = round(data["loop_add"]["ipc"])
    return data


def collect_cache_sizes() -> Dict:
    """Lab03/cache_sizes：实测各级 cache 延迟。"""
    out = run(taskset_cmd(0, "Lab03_存储层次/src/cache_sizes"), timeout=180)
    data = {"levels": []}
    for line in out.splitlines():
        # 形如: 64K   1024   1.61 ns  L1?
        m = re.match(r"\s*(\d+[KM]?)\s+\d+\s+([\d.]+)\s+ns\s+(\w+)\??", line)
        if m:
            data["levels"].append({
                "size": m.group(1),
                "latency_ns": float(m.group(2)),
                "level": m.group(3),
            })
    # 取各级典型延迟
    by_level = {}
    for entry in data["levels"]:
        lvl = entry["level"]
        if lvl not in by_level:
            by_level[lvl] = entry["latency_ns"]
        else:
            by_level[lvl] = min(by_level[lvl], entry["latency_ns"])  # 取最小（最稳定的）
    data["typical_latency_ns"] = by_level
    return data


def collect_rename_capacity() -> Dict:
    """Lab04/rename_capacity：反推寄存器重命名容量。"""
    out = run(taskset_cmd(0, "Lab04_超标量乱序/src/rename_capacity"), timeout=120)
    data = {"curve": []}
    for line in out.splitlines():
        m = re.match(r"\s*(\d+)\s+[\d.]+\s+\d+\s+\d+\s+([\d.]+)", line)
        if m:
            n = int(m.group(1))
            ipc = float(m.group(2))
            data["curve"].append({"n_chains": n, "ipc": ipc})
    # 找 saturate 拐点
    if data["curve"]:
        max_ipc = max(p["ipc"] for p in data["curve"])
        for p in data["curve"]:
            if p["ipc"] >= max_ipc * 0.99:
                data["ipc_saturation_at_n"] = p["n_chains"]
                data["peak_ipc"] = max_ipc
                break
    return data


# ============================================================================
# 汇总
# ============================================================================

def collect_all() -> Dict:
    """跑全部 Lab 反推实验，返回结构化数据。"""
    return {
        "_meta": {
            "collector": "collect_lab_data.py",
            "platform": "Phytium D3000M (FTC862)",
            "note": "所有数字均为本机实测，不是抄 README。",
        },
        "arch": collect_arch_probe(),
        "issue_width": collect_null_loop(),
        "cache_latency": collect_cache_sizes(),
        "rename_capacity": collect_rename_capacity(),
    }


def to_markdown(d: Dict) -> str:
    """转 markdown 表格片段，供 comparison.md 引用。"""
    lines = ["<!-- 由 collect_lab_data.py --md 自动生成，请勿手改 -->\n"]
    arch = d.get("arch", {})
    lines.append(f"- **CPU**：{arch.get('part_name', '?')}，"
                 f"{arch.get('cores', '?')} 核 @ {arch.get('freq_mhz', '?')} MHz，"
                 f"governor={arch.get('governor', '?')}")
    iw = d.get("issue_width", {})
    lines.append(f"- **Issue Width**：{iw.get('issue_width', '?')}-wide "
                 f"(loop_volatile IPC={iw.get('loop_volatile', {}).get('ipc', '?')})")
    lines.append(f"- **ALU 端口**：{iw.get('alu_ports_per_cycle', '?')}/cycle "
                 f"(loop_add IPC={iw.get('loop_add', {}).get('ipc', '?')})")
    cl = d.get("cache_latency", {}).get("typical_latency_ns", {})
    if cl:
        lines.append(f"- **Cache 延迟（实测）**："
                     f"L1={cl.get('L1', '?')}ns / "
                     f"L2={cl.get('L2', '?')}ns / "
                     f"L3={cl.get('L3', '?')}ns / "
                     f"DRAM={cl.get('DRAM', '?')}ns")
    rc = d.get("rename_capacity", {})
    if rc:
        lines.append(f"- **重命名容量拐点**：n={rc.get('ipc_saturation_at_n', '?')} "
                     f"时 IPC saturate 到 {rc.get('peak_ipc', '?'):.3f}")
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--md", action="store_true", help="输出 markdown 而非 JSON")
    args = p.parse_args()
    data = collect_all()
    if args.md:
        print(to_markdown(data))
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
