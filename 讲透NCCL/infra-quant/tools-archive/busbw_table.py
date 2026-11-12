#!/usr/bin/env python3
"""algbw ↔ busbw 换算与集合通信带宽上界（nccl-tests 口径 + 书 ch06 环代数）.

定义（nccl-tests）：busbw = 每卡链路实际注入速率 = 每卡发送字节 / 集合时间。
理想环实现下 busbw → 单卡链路带宽 B（100% 利用），故 busbw/B 是实现质量指标。

每卡发送字节（环实现，N 卡，AllReduce 消息 M）：
    AllReduce       2(N-1)/N · M
    ReduceScatter   (N-1)/N · M
    AllGather       (N-1)/N · M
    Broadcast       root 发 (N-1)·M，非 root 收 M → 每卡峰值 (N-1)·M（root 口径）
    AllToAll        每卡发 (N-1)/N · M（M 为总发送量时为 M）

nccl-tests 报表因子（busbw = algbw × factor）：
    AllReduce 2(N-1)/N | AllGather/ReduceScatter N/(N-1) | Broadcast N/(N-1)

用法：
    python3 busbw_table.py --n 8 --bw 450e9          # H100 NVLink 理想 busbw 上界
    python3 busbw_table.py --n 8 --algbw 380e9 --op allreduce   # 实测→利用率
"""
import argparse
import json

# op → (每卡发送字节函数 factor_send(M), nccl-tests algbw→busbw 因子函数)
OPS = {
    "allreduce":       (lambda n: 2 * (n - 1) / n, lambda n: 2 * (n - 1) / n),
    "reducescatter":   (lambda n: (n - 1) / n,     lambda n: n / (n - 1)),
    "allgather":       (lambda n: (n - 1) / n,     lambda n: n / (n - 1)),
    "broadcast":       (lambda n: n - 1,           lambda n: n / (n - 1)),
    "alltoall":        (lambda n: 1.0,             lambda n: (n - 1) / n),
}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--bw", type=float, default=450e9, help="单卡链路带宽（字节/秒）")
    p.add_argument("--op", choices=list(OPS), default="allreduce")
    p.add_argument("--bytes", type=int, default=1 << 30, help="消息大小（带宽渐近区）")
    p.add_argument("--algbw", type=float, default=None, help="实测 algbw，算 busbw 与利用率")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    send_f, report_f = OPS[a.op]
    send = send_f(a.n) * a.bytes
    t_ideal = send / a.bw
    algbw_ideal = a.bytes / t_ideal
    out = dict(n=a.n, op=a.op, link_bw=a.bw, bytes=a.bytes,
               send_bytes_per_rank=send, ideal_seconds=t_ideal,
               ideal_algbw=algbw_ideal, ideal_busbw=a.bw,
               nccl_tests_report_factor=report_f(a.n))
    if a.algbw:
        out["measured_algbw"] = a.algbw
        out["measured_busbw"] = a.algbw * report_f(a.n)
        out["busbw_utilization"] = a.algbw * report_f(a.n) / a.bw
        out["time_overhead_x"] = algbw_ideal / a.algbw
    if a.format == "json":
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"# {a.op} N={a.n} M={a.bytes:,} B 链路 {a.bw/1e9:.0f} GB/s")
    print(f"- 每卡发送 {send:,.0f} B，理想时间 {t_ideal*1e6:,.1f} µs")
    print(f"- 理想 algbw {algbw_ideal/1e9:,.1f} GB/s；busbw 上界 = 链路带宽 {a.bw/1e9:,.1f} GB/s")
    print(f"- nccl-tests 报表因子 ×{report_f(a.n):.4f}")
    if a.algbw:
        print(f"- 实测 algbw {a.algbw/1e9:.1f} → busbw {out['measured_busbw']/1e9:.1f} GB/s，"
              f"链路利用率 {out['busbw_utilization']*100:.1f}%，离上界 {out['time_overhead_x']:.2f}×")


if __name__ == "__main__":
    main()
