#!/usr/bin/env python3
"""小消息协议模型：LL / LL128 / Simple 有效带宽与协议选择（书 ch07 带宽时延积思路）.

模型：协议 = 有效载荷效率 eff × 线速，加上协议各自的同步/等待开销。
    LL128: 每 128B 行携带 120B 数据（NCCL 源码 NCCL_LL128_DATA_SZ/ LINE_SZ 比值），
           flag 内嵌于行，发送侧须等上一行 ACK 才能继续（在途上限 = 2 行），
           延迟低、线速 ~93.75%，但要求对齐且带宽高时受 credit 往返限制。
    LL:    数据按 8B 粒度 + 4B flag（NCCL LL_DATA_SZ/FLAG_SZ），效率 ~66.7%，
           每 flag 读写依赖顺序可见性，CPU/GPU 端易成瓶颈——线速低但小消息延迟最小。
    Simple: 全额线速，但每 chunk 需 wait/sync 握手（批量 flag），启动开销大；
            大消息专用。

交叉点估算（一阶）：
    小消息 → 延迟项主导 → LL 赢（握手最轻）
    中消息 → 带宽项主导但 credit 限制未触发 → LL128 赢
    大消息 → 纯线速 → Simple 赢
本工具按 t_proto(M) = latency_proto + M / (eff_proto × B) 建模，交叉点 =
    M* = (latency_a − latency_b) / (1/(eff_b·B) − 1/(eff_a·B))

注意：eff/latency 默认值是通用锚点；分析真实实现（如 NCCL）时请用
nccl_structure_scan.py 从源码提取常量后通过参数喂入，不要照搬默认。

用法：
    python3 protocol_crossover.py --bw 25e9
    python3 protocol_crossover.py --bw 25e9 --eff-ll 0.5 --eff-ll128 0.9375
"""
import argparse
import json


def proto_time(m: float, bw: float, eff: float, latency: float) -> float:
    return latency + m / (eff * bw)


def crossover(p1: dict, p2: dict) -> float:
    """t1(M)=lat1+M/(e1·B), t2 同理 → 等时点 M*（t1 快于 t2 的区段在其一侧）。"""
    denom = (1 / (p1["eff"] * p1["bw"]) - 1 / (p2["eff"] * p2["bw"]))
    if denom == 0:
        return float("inf")
    return (p2["latency"] - p1["latency"]) / denom


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bw", type=float, default=25e9, help="单通道线速 B（字节/秒）")
    p.add_argument("--eff-ll", type=float, default=0.667, help="LL 有效载荷效率（8B/12B）")
    p.add_argument("--eff-ll128", type=float, default=0.9375, help="LL128 效率（120B/128B）")
    p.add_argument("--eff-simple", type=float, default=1.0, help="Simple 效率")
    p.add_argument("--lat-ll-us", type=float, default=1.0, help="LL 每步延迟（µs）")
    p.add_argument("--lat-ll128-us", type=float, default=1.5, help="LL128 每步延迟（µs）")
    p.add_argument("--lat-simple-us", type=float, default=5.0, help="Simple 同步延迟（µs）")
    p.add_argument("--bytes", type=int, default=None, help="给定消息大小算三协议耗时")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    protos: list[dict[str, float]] = [
        dict(eff=a.eff_ll, bw=a.bw, latency=a.lat_ll_us * 1e-6),
        dict(eff=a.eff_ll128, bw=a.bw, latency=a.lat_ll128_us * 1e-6),
        dict(eff=a.eff_simple, bw=a.bw, latency=a.lat_simple_us * 1e-6),
    ]
    names = ["LL", "LL128", "Simple"]
    x_ll_ll128 = crossover(protos[0], protos[1])
    x_ll128_simple = crossover(protos[1], protos[2])
    out = dict(bw=a.bw, protos=[{k: v for k, v in p_.items()} for p_ in protos],
               crossover_ll_ll128_bytes=x_ll_ll128,
               crossover_ll128_simple_bytes=x_ll128_simple)
    if a.bytes:
        out["at_bytes"] = {name: proto_time(a.bytes, p_["bw"], p_["eff"], p_["latency"])
                           for name, p_ in zip(names, protos)}
    if a.format == "json":
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"# 协议模型（线速 {a.bw/1e9:.1f} GB/s）\n")
    print("| 协议 | 效率 | 有效带宽 | 每步延迟 |")
    print("| --- | ---: | ---: | ---: |")
    for name, p_ in zip(names, protos):
        print(f"| {name} | {p_['eff']:.3f} | {p_['eff']*a.bw/1e9:.2f} GB/s | {p_['latency']*1e6:.1f} µs |")
    print(f"\n交叉点 LL×LL128 ≈ {x_ll_ll128:,.0f} B；LL128×Simple ≈ {x_ll128_simple:,.0f} B")
    if a.bytes:
        print(f"\nM={a.bytes:,} B 时：")
        for k, v in out["at_bytes"].items():
            print(f"  {k}: {v*1e6:,.2f} µs")


if __name__ == "__main__":
    main()
