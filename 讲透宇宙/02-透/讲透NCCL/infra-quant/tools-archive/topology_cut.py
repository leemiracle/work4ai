#!/usr/bin/env python3
"""拓扑割集分析：环/树集合通信的有效带宽上界（书 ch06 超节点 + ch07 网络）.

数据搬移五问之"经过哪里"：集合通信的每字节都要过某个链路集合，有效带宽上界 =
瓶颈割集容量 / 该割必须承运的流量。

建模（N 卡，单卡 NVLink 带宽 B_nv、单卡 NIC 带宽 B_nic，G 卡/机）：

1. 机内 NVSwitch 全互联 + 双环（每卡上下行各一份环流量）：
   割（把环切成两半）上，双向环跨割流量由 2 条链路承载（每半各 1 上/下行），
   ring 理想 busbw → min(B_nv, 2×B_nv) 取决于 channel 双向性；多 channel 可
   打满 NVSwitch 全双工。上界：每卡 2B_nv（双 channel 双向）。
2. 跨机 IB rail-optimized 环（每机 2 张 NIC 进出环）：
   机器间割流量 = 整个 all-reduce 的跨机字节 = 2(N-G)/N · M（ring reduce-scatter
   + all-gather 在机间割上各过一次 (N-G)/N·M 每卡）。
   时间下界 = 跨机每机字节 / min(每机 NIC 聚合, NVLink 注入)。
3. 跨机树（机间二分树）：每机 NIC 峰值 = 树根路径上的全量 M → 大消息通常劣于
   ring，但轮次少 → 小消息占优。

incast 检查：树/归约根方向若 (N-1) 流汇入 1 机，该机 NIC 承压 (N-1)/N 系数。

用法：
    python3 topology_cut.py --n 16 --g 8 --bw-nv 450e9 --bw-nic 50e9
"""
import argparse
import json


def analyze(n: int, g: int, bw_nv: float, bw_nic: float, nic_per_node: int,
            msg_bytes: int) -> dict:
    nodes = n // g if g else n
    # ring all-reduce：每卡发送 2(N-1)/N·M，其中跨机部分：reduce-scatter 阶段每卡
    # 需与机外交换 (N-G)/N·M，all-gather 同量 → 每机跨机字节 = G 卡 × 2(N-G)/N·M / G
    # 摊到每卡口径 = 2(N-G)/N·M（与卡数无关，逐卡链路承载）
    per_rank_cross_bytes = 2 * (n - g) / n * msg_bytes
    per_node_nic = nic_per_node * bw_nic
    per_node_nv_inject = g * bw_nv
    node_cross_bytes = per_rank_cross_bytes * g  # 每机总跨机字节
    t_cross_bound = node_cross_bytes / min(per_node_nic, per_node_nv_inject)
    t_intra_bound = 2 * (n - 1) / n * msg_bytes / bw_nv  # 机内 NVLink 环下界（单 channel 口径）
    return dict(
        nodes=nodes, gpus_per_node=g,
        per_rank_cross_bytes=per_rank_cross_bytes,
        per_node_cross_bytes=node_cross_bytes,
        nic_aggregate_bw=per_node_nic, nvlink_inject_bw=per_node_nv_inject,
        bottleneck="nic" if per_node_nic < per_node_nv_inject else "nvlink",
        cross_seconds_bound=t_cross_bound,
        intra_seconds_bound=t_intra_bound,
        allreduce_seconds_bound=max(t_cross_bound, t_intra_bound),
        busbw_bound=msg_bytes / max(t_cross_bound, t_intra_bound),
        # 树 incast：归约流向每机 NIC 的峰值系数
        tree_root_node_peak_factor=nodes - 1,
    )


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, default=16, help="总卡数")
    p.add_argument("--g", type=int, default=8, help="每机卡数（超节点内）")
    p.add_argument("--bw-nv", type=float, default=450e9, help="每卡 NVLink 带宽")
    p.add_argument("--bw-nic", type=float, default=50e9, help="单 NIC 带宽（IB NDR≈50GB/s）")
    p.add_argument("--nic-per-node", type=int, default=8)
    p.add_argument("--bytes", type=int, default=1 << 30)
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    r = analyze(a.n, a.g, a.bw_nv, a.bw_nic, a.nic_per_node, a.bytes)
    if a.format == "json":
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return
    print(f"# 拓扑割集 N={a.n}（{a.n//a.g} 机 × {a.g} 卡）M={a.bytes:,} B")
    print(f"- 每卡跨机字节（ring）: {r['per_rank_cross_bytes']:,.0f} B")
    print(f"- 每机跨机字节: {r['per_node_cross_bytes']:,.0f} B")
    print(f"- 每机 NIC 聚合 {r['nic_aggregate_bw']/1e9:,.0f} GB/s vs NVLink 注入 {r['nvlink_inject_bw']/1e9:,.0f} GB/s → 瓶颈 {r['bottleneck']}")
    print(f"- 跨机时间下界 {r['cross_seconds_bound']*1e3:,.2f} ms；机内环下界 {r['intra_seconds_bound']*1e3:,.2f} ms")
    print(f"- AllReduce 时间下界 {r['allreduce_seconds_bound']*1e3:,.2f} ms → busbw 上界 {r['busbw_bound']/1e9:,.1f} GB/s")
    print(f"- 树根机 NIC 峰值系数 ×{r['tree_root_node_peak_factor']}（incast 风险）")


if __name__ == "__main__":
    main()
