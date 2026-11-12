#!/usr/bin/env python3
"""NCCL 源码结构量化扫描：模块行数 / 算法协议枚举 / packet 常量 / 成本模型定位.

配合《深入理解 AI Infra》ch06/ch07 模型使用（aib-cluster-network-analysis 等 skill）。
输出：JSON（--format json）或 Markdown 报告。定位锚点带 文件:行号，可直接复核。

用法：
    python3 nccl_structure_scan.py --repo /usr-data/data2/kylin/nccl
"""
import argparse
import json
import re
from pathlib import Path


def file_lines(p: Path) -> int:
    try:
        return len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
    except OSError:
        return 0


def subsystem_stats(repo: Path) -> list[dict]:
    groups = {
        "graph/topo/tuning": ["src/graph", "src/tuning"],
        "device kernels": ["src/device"],
        "transports": ["src/transport"],
        "collectives api": ["src/collectives.cc", "src/group.cc", "src/channel.cc",
                            "src/enqueue", "src/scheduler"],
        "proxy/bootstrap/init": ["src/proxy.cc", "src/bootstrap.cc", "src/init.cc",
                                 "src/allocator.cc", "src/mem_manager.cc", "src/register"],
        "rma/ce/mnnvl/ras": ["src/rma", "src/ce_coll.cc", "src/mnnvl.cc", "src/ras",
                             "src/cft_dev_runtime.cc"],
        "include/plugin/os/misc": ["src/include", "src/plugin", "src/os", "src/misc",
                                   "src/param", "src/gdr.cc", "src/enhcompat.cc",
                                   "src/sym_kernels.cc", "src/dev_runtime*"],
    }
    out = []
    for name, paths in groups.items():
        total, files = 0, 0
        for sub in paths:
            p = repo / sub
            if p.is_file():
                total += file_lines(p); files += 1
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.suffix in (".cc", ".cu", ".cuh", ".h", ".cpp", ".c", ".in", ".py", ".cmake"):
                        total += file_lines(f); files += 1
        out.append(dict(subsystem=name, files=files, lines=total))
    # Pyright 显式收窄：int 字段直接构造
    return [{"subsystem": str(r["subsystem"]), "files": int(r["files"]),
             "lines": int(r["lines"])} for r in out]


def find_anchors(repo: Path) -> list[dict]:
    """grep 一批关键符号 → (主题, 文件:行, 代码片段)。"""
    targets = [
        ("LL128 行定义", r"#define NCCL_LL128_LINESIZE", "src/include/device.h"),
        ("LL128 数据元素", r"#define NCCL_LL128_DATAELEMS", "src/include/device.h"),
        ("LL128 每线程元素", r"#define NCCL_LL128_ELEMS_PER_THREAD", "src/include/device.h"),
        ("LL flag 轮转", r"#define NCCL_LL_FLAG_MAX", "src/include/device.h"),
        ("协议 buffSize 分派", r"proto == NCCL_PROTO_LL\s*\?", "src/include/device.h"),
        ("算法内联分派", r"int algo1 = algo == NCCL_ALGO_RING", "src/include/device.h"),
        ("成本模型", r"latency|time.*=", "src/tuning/cost_model.cc"),
        ("ring 调优", r"ncclTopoGetAlgoTime|time \+=", "src/tuning/ring.cc"),
        ("tree 调优", r"ncclTopoGetAlgoTime|time \+=", "src/tuning/tree.cc"),
        ("nvls 调优", r"time", "src/tuning/nvls.cc"),
        ("通道搜索", r"NCCL_TOPO_.*HERUISTIC|searchInit", "src/graph/search.cc"),
    ]
    anchors = []
    for topic, pat, relf in targets:
        f = repo / relf
        if not f.exists():
            # graph/search.cc 在 v2.32 可能移位，做一次仓内定位
            cands = list(repo.rglob(Path(relf).name))
            if not cands:
                continue
            f = cands[0]
        rx = re.compile(pat)
        try:
            for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
                if rx.search(line):
                    anchors.append(dict(topic=topic, anchor=f"{f.relative_to(repo)}:{i}",
                                        code=line.strip()[:120]))
                    break
        except OSError:
            continue
    return anchors


def extract_constants(repo: Path) -> dict[str, object]:
    dev = (repo / "src/include/device.h").read_text(errors="ignore")

    def defint(name, text):
        m = re.search(rf"#define\s+{name}\s+\(?(.+?)\)?\s*(?:$|/)", text, re.M)
        return m.group(1).strip() if m else None
    ll128_line = defint("NCCL_LL128_LINESIZE", dev)
    ll128_dataelems = defint("NCCL_LL128_DATAELEMS", dev)
    ll128_lineelems = defint("NCCL_LL128_LINEELEMS", dev)
    eff_ll128 = None
    if ll128_dataelems and ll128_lineelems:
        try:
            eff_ll128 = int(ll128_dataelems.strip("()").split("/")[-1].strip() or ll128_dataelems)
            # DATAELEMS = LINEELEMS-1 形如 (NCCL_LL128_LINESIZE / sizeof(uint64_t)) - 1
            m = re.search(r"LINESIZE\s*/\s*sizeof\(uint64_t\)\s*\)\s*-\s*1", dev)
            eff_ll128 = 15 / 16 if m else None
        except (ValueError, ZeroDivisionError):
            eff_ll128 = None
    return dict(
        ll128_linesize=ll128_line, ll128_dataelems=ll128_dataelems,
        ll128_efficiency=eff_ll128,  # 15/16 = 0.9375
        ll_flag_max=defint("NCCL_LL_FLAG_MAX", dev),
        ll_efficiency="2/3 (8B data + 4B flag, 经典 LL 包)",
        simple_max_threads=defint("NCCL_SIMPLE_MAX_NTHREADS", dev),
        ll128_max_threads=defint("NCCL_LL128_MAX_NTHREADS", dev),
        ll128_elems_per_thread=defint("NCCL_LL128_ELEMS_PER_THREAD", dev),
    )


def count_symbols(repo: Path) -> dict[str, object]:
    api = (repo / "src/nccl.h.in").read_text(errors="ignore")
    n_pub = len(re.findall(r"^ncclResult_t\s+nccl\w+", api, re.M))
    algs = sorted(set(re.findall(r"NCCL_ALGO_(\w+)", (repo / "src/include/device.h").read_text(errors="ignore"))))
    protos = sorted(set(re.findall(r"NCCL_PROTO_(\w+)", (repo / "src/include/device.h").read_text(errors="ignore"))))
    return dict(public_api_functions=n_pub, algorithms=algs, protocols=protos)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo", default=".", help="NCCL 仓路径")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    repo = Path(a.repo).resolve()
    out: dict[str, object] = dict(repo=str(repo),
               subsystems=subsystem_stats(repo),
               constants=extract_constants(repo),
               symbols=count_symbols(repo),
               anchors=find_anchors(repo))
    if a.format == "json":
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"# NCCL 结构扫描：{repo.name}")
    print("\n## 子系统行数\n")
    print("| 子系统 | 文件数 | 行数 |", "| --- | ---: | ---: |")
    subs = out["subsystems"]
    for r in subs:
        print(f"| {r['subsystem']} | {int(r['files'])} | {int(r['lines']):,} |")
    total = sum(int(r["lines"]) for r in subs)
    print(f"| 合计 | {sum(int(r['files']) for r in subs)} | {total:,} |")
    c = out["constants"]; s = out["symbols"]
    print(f"\n## 协议常量\n- LL128: {c['ll128_linesize']}B 行, DATAELEMS={c['ll128_dataelems']}, "
          f"效率 {c['ll128_efficiency']}, ELEMS_PER_THREAD={c['ll128_elems_per_thread']}")
    print(f"- LL: flag_max={c['ll_flag_max']}, 效率 {c['ll_efficiency']}")
    print(f"- 算法族: {', '.join(s['algorithms'])}")
    print(f"- 协议族: {', '.join(s['protocols'])}")
    print(f"- 公开 API 函数: {s['public_api_functions']}")
    print("\n## 关键锚点\n")
    for anc in out["anchors"]:
        print(f"- **{anc['topic']}** `{anc['anchor']}`")


if __name__ == "__main__":
    main()
