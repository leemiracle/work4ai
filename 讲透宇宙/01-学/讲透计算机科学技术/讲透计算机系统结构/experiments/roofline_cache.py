# -*- coding: utf-8 -*-
"""
roofline_cache.py —— 三堵墙的数值显形(讲透计算机系统结构 家族实验)

对应章:00(存储金字塔)/03(Amdahl)/04(roofline 三堵墙)
做什么:
  [1] 流式访存带宽实测 -> 你的环境的"墙 1"高度(GB/s)
  [2] roofline 定位:两个 kernel(纯流式 vs 中等算术强度)在地图上的坐标
  [3] 缓存行效应:同行(64B 内) vs 跨行访问的计数差 —— 金字塔的收费账单
  [4] Amdahl 上界:串行占比 f 封死加速比(渐近线显形)
断言:全部内置,跑通即验证。纯 numpy+标准库,无平台特定依赖。
"""
import time
import numpy as np

N = 1 << 22  # 4M 元素 * 8B = 32MB,确保远超典型 L2/L3,落在 DRAM 档


def wall1_stream_bandwidth():
    """[1] 流式读:测 DRAM 带宽(SAXPY 风格:读 x,y 写 y)。"""
    x = np.random.rand(N)
    y = np.random.rand(N)
    a = 2.5
    y.sum()  # 预热(页表/缓存冷启动)
    t0 = time.perf_counter()
    y[:] = a * x + y  # 读 2*N*8B + 写 N*8B
    t = time.perf_counter() - t0
    bytes_moved = 3 * N * 8
    gb_s = bytes_moved / t / 1e9
    print(f"[1] 流式带宽(SAXPY): {gb_s:7.1f} GB/s   (移动 {bytes_moved/1e6:.0f} MB / {t*1e3:.1f} ms)")
    return gb_s


def roofline_position(gb_s, peak_gflops=200.0):
    """[2] roofline:算术强度(FLOP/Byte)决定天花板 min(峰值, 带宽×强度)。"""
    kernels = [
        ("SAXPY(流式)", 2 / 8 / 3 * 1 / 1),   # 2 FLOP / 24B(读x,y写y) ≈ 0.083
        ("axpy 原地", 2 / (2 * 8)),           # 2 FLOP / 16B = 0.125
        ("点积", 2 / (2 * 8)),                # 2 FLOP / 16B = 0.125(读2写0..近似)
        ("GEMM 分块后", 8.0),                  # 分块良好时可达两位数
    ]
    ridge = peak_gflops / gb_s  # 屋脊点:强度超过它才吃得满峰值
    print(f"[2] roofline(假设峰值 {peak_gflops:.0f} GFLOP/s,实测带宽 {gb_s:.1f} GB/s):")
    print(f"    屋脊点强度 = {ridge:.3f} FLOP/Byte —— 低于它,一切 kernel 都活在访存墙上")
    for name, ai in kernels:
        attainable = min(peak_gflops, gb_s * ai)
        where = "访存墙(带宽限制)" if gb_s * ai < peak_gflops else "峰值平台"
        print(f"    {name:<10} 强度 {ai:6.3f} -> 可达 {attainable:7.1f} GFLOP/s  [{where}]")
    assert gb_s * 0.083 < peak_gflops, "断言:SAXPY 必在访存墙上(强度<屋脊点)"
    return ridge


def cache_line_effect():
    """[3] 缓存行:按行收费——跳行只消费 1/8 的字节,时间却几乎不变。"""
    stride = 64 // 8  # 一个 double=8B,一行 8 个 double
    n = 1 << 20       # n 行
    arr = np.random.rand(n * stride)
    arr.sum()  # 预热
    # 模式 A:全量求和(消费 8N 个字节,每行 8/8)
    t0 = time.perf_counter()
    s_a = float(arr.sum())
    ta = time.perf_counter() - t0
    # 模式 B:每行只取 1 个(消费 N 个字节=1/8,但缓存仍按整行搬运)
    t0 = time.perf_counter()
    s_b = float(arr[::stride].sum())
    tb = time.perf_counter() - t0
    ratio = tb / ta * 100
    print(f"[3] 缓存行:全量 8N 字节 {ta*1e3:6.1f} ms vs 只用 1/8 字节 {tb*1e3:6.1f} ms(={ratio:.0f}% 时间)")
    print(f"    -> 金字塔按『行(64B)』收费不按『字节』:跳行访问把 7/8 带宽扔进水里")
    assert s_a > 0 and s_b > 0 and 0.3 < tb / ta <= 1.5, "断言:1/8 数据量耗时仍在全量的 30%-150%(按行收费)"
    return ta, tb


def amdahl_curve():
    """[4] Amdahl:串行占比 f 与加速上界 1/(f+(1-f)/N)。"""
    print("[4] Amdahl 上界 S(f,N)=1/(f+(1-f)/N):")
    for f in (0.01, 0.05, 0.20):
        for nn in (16, 1024, 10**9):
            s = 1.0 / (f + (1 - f) / nn)
            if nn == 10**9:
                s_inf = 1.0 / f
                print(f"    串行 {f*100:>4.0f}%  |  16 核 {1.0/(f+(1-f)/16):6.1f}x | 1024 核 {1.0/(f+(1-f)/1024):6.1f}x | ∞核 {s_inf:6.1f}x")
        assert abs(1.0 / (f + (1 - f) / 10**9) - 1.0 / f) < 1e-3, "断言:∞核渐近线=1/f"
    print("    -> 渐近线 1/f:串行 1% 就是 100 倍的天花板,与核数无关(Amdahl 1967)")


if __name__ == "__main__":
    print(__doc__.split("\n")[1])
    gb = wall1_stream_bandwidth()
    roofline_position(gb)
    cache_line_effect()
    amdahl_curve()
    print("\n[ALL ASSERTS PASSED] 三堵墙数值显形:带宽墙高度、屋脊点、缓存行账单、Amdahl 渐近线。")
    print("带走一句(04 章):先测算术强度,再谈优化——roofline 之下,一切优化都是搬运学。")
