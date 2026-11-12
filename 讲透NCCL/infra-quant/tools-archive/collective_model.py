#!/usr/bin/env python3
"""集合通信时间模型：ring vs tree（蒸馏自《深入理解 AI Infra》ch06/ch07）.

公式出处（书 calculations/src/infra_calc/topics/{ring,tree}_collective.py 实测核对）：

Ring AllReduce（N 卡、消息 M B、单卡链路带宽 B、每轮启动延迟 α）:
    轮次 R      = 2(N-1)                 # reduce_scatter N-1 轮 + all_gather N-1 轮
    chunk       = M/N
    每卡发送    = 2(N-1)/N · M           # 每轮 1 个 chunk，共 2(N-1) 轮
    时间        = 2(N-1)·α + 2(N-1)/N · M/B
    环上每卡链路速率（busbw 口径）= 每卡发送字节 / 时间

Tree（binomial reduce + 逆序 broadcast，书 declared algorithm；NCCL 实际用
double-tree 半轮错开，见报告对照）:
    轮次        = 2·ceil(log2 N)，每边携带全量 M，每层是 barrier
    关键路径时间 = 2·ceil(log2 N)·α + ceil(log2 N) · M/B
    根侧卡峰值发送 = ceil(log2 N) · M

交叉点：消息小于 S* 时 tree 赢（轮次少、α 占优），大于 S* 时 ring 赢。
    近似 S* ≈ α·B · N·log2(N)/(N - log2(N))（由两模型时间相等解出，见 cross()）。

用法示例：
    python3 collective_model.py --n 8 --bytes 33554432 --bw 50e9 --alpha-us 2
    python3 collective_model.py --sweep            # 扫消息规模画交叉表
"""
import argparse
import json
import math


def ring_model(n: int, msg_bytes: int, bw: float, alpha: float) -> dict:
    rounds = 2 * (n - 1)
    chunk = msg_bytes / n
    send_per_rank = rounds * chunk
    t = rounds * alpha + send_per_rank / bw
    return dict(algo="ring", rounds=rounds, chunk_bytes=chunk,
                send_bytes_per_rank=send_per_rank, seconds=t,
                busbw=send_per_rank / t, startup_seconds=rounds * alpha,
                bandwidth_seconds=send_per_rank / bw)


def tree_model(n: int, msg_bytes: int, bw: float, alpha: float) -> dict:
    depth = math.ceil(math.log2(n))
    rounds = 2 * depth
    t = rounds * alpha + depth * msg_bytes / bw
    return dict(algo="binomial-tree", rounds=rounds, depth=depth,
                send_bytes_per_rank_max=depth * msg_bytes, seconds=t,
                busbw=msg_bytes / t, startup_seconds=rounds * alpha,
                bandwidth_seconds=depth * msg_bytes / bw)


def cross(n: int, bw: float, alpha: float) -> float:
    """ring/tree 等时消息规模 S*（忽略带宽时延重叠，一阶近似）。

    2(N-1)α + 2(N-1)/N·S/B = 2dα + d·S/B,  d=ceil(log2 N)
    => S* = 2B(N-1-d)α·N / (dN - 2(N-1))   （分母>0 即 ring 每卡字节更省时才有交点）
    """
    d = math.ceil(math.log2(n))
    denom = d * n - 2 * (n - 1)
    if denom <= 0:
        return float("inf")  # tree 在该 N 下不可能被 ring 追上（带宽项也占优）
    return 2 * bw * (n - 1 - d) * alpha * n / denom


def sweep(n: int, bw: float, alpha: float) -> list:
    rows = []
    for k in range(10, 31):  # 1KB .. 1GB
        m = 2 ** k
        r, t = ring_model(n, m, bw, alpha), tree_model(n, m, bw, alpha)
        rows.append(dict(msg_bytes=m, ring_us=r["seconds"] * 1e6,
                         tree_us=t["seconds"] * 1e6,
                         winner="tree" if t["seconds"] < r["seconds"] else "ring"))
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, default=8, help="参与卡数")
    p.add_argument("--bytes", type=int, default=33_554_432, help="消息字节数（AllReduce 语义）")
    p.add_argument("--bw", type=float, default=50e9, help="每卡链路带宽 B（字节/秒）")
    p.add_argument("--alpha-us", type=float, default=2.0, help="每轮启动延迟 α（微秒）")
    p.add_argument("--sweep", action="store_true", help="扫描 1KB-1GB 输出交叉表")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    alpha = a.alpha_us * 1e-6
    out = dict(n=a.n, msg_bytes=a.bytes, bw=a.bw, alpha_s=alpha,
               ring=ring_model(a.n, a.bytes, a.bw, alpha),
               tree=tree_model(a.n, a.bytes, a.bw, alpha),
               crossover_bytes=cross(a.n, a.bw, alpha))
    if a.sweep:
        out["sweep"] = sweep(a.n, a.bw, alpha)
    if a.format == "json":
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    r, t, c = out["ring"], out["tree"], out["crossover_bytes"]
    lines = [f"# ring vs tree (N={a.n}, M={a.bytes:,} B, B={a.bw/1e9:.0f} GB/s, α={a.alpha_us} µs)",
             "", "| 模型 | 轮次 | 每卡发送 | 时间 | busbw |", "| --- | ---: | ---: | ---: | ---: |",
             f"| ring | {r['rounds']} | {r['send_bytes_per_rank']:,.0f} B | {r['seconds']*1e6:,.1f} µs | {r['busbw']/1e9:.1f} GB/s |",
             f"| tree | {t['rounds']} | {t['send_bytes_per_rank_max']:,.0f} B(峰值) | {t['seconds']*1e6:,.1f} µs | {t['busbw']/1e9:.1f} GB/s |",
             "", f"交叉点 S* ≈ {c:,.0f} B" + ("（tree 恒优）" if c == float('inf') else ""),
             f"该规模胜者: {'tree' if t['seconds'] < r['seconds'] else 'ring'}"]
    if a.sweep:
        lines += ["", "| 消息 | ring µs | tree µs | 胜者 |", "| ---: | ---: | ---: | --- |"]
        lines += [f"| 2^{int(math.log2(s['msg_bytes']))} ({s['msg_bytes']:,} B) | {s['ring_us']:,.2f} | {s['tree_us']:,.2f} | {s['winner']} |"
                  for s in out["sweep"]]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
