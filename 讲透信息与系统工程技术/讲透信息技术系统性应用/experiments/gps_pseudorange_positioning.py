# -*- coding: utf-8 -*-
"""
四星伪距 GPS 定位:线性化迭代最小二乘(纯标准库,assert 自验证)
=================================================================
家族:讲透信息与系统工程技术/讲透信息技术系统性应用(GB/T 41330)
配套:04-信息技术系统性应用转代码.md · 走廊②(伪距定位走廊)
      00-体系结构.md §1.2(三球交汇与第四颗星)

内容:
  §A  WGS84 大地坐标(经纬高)→ ECEF 闭式变换(构造档①)
  §B  伪距定位:牛顿式线性化迭代最小二乘
      - 场景1:4 星无噪声 → 4 方程 4 未知数,解到机器精度
      - 场景2:6 星 σ=5 m 伪距噪声 → 三维位置误差 < 100 m(assert)
  §C  ECEF → 本地 ENU(东北天)切平面切换演示(assert)
  附:GDOP 几何精度衰减因子计算

运行:python gps_pseudorange_positioning.py
全部 assert 通过则 exit 0。
"""
import math
import random
import sys

# ---------------- 常量 ----------------
C = 299792458.0                      # 光速 m/s
WGS84_A = 6378137.0                  # 长半轴 m
WGS84_F = 1.0 / 298.257223563        # 扁率
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)  # 第一偏心率平方
SAT_RADIUS = 26560e3                 # GPS 卫星轨道半径(地心距) m
MIN_ELEV_DEG = 20.0                  # 高度角遮蔽


# ---------------- §A 坐标变换:构造档①(闭式) ----------------
def geodetic_to_ecef(lat_deg, lon_deg, h):
    """WGS84 大地坐标 → ECEF(闭式,03 章 §3.2 三套马甲之一)"""
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    s, c = math.sin(lat), math.cos(lat)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * s * s)   # 卯酉圈曲率半径
    return ((n + h) * c * math.cos(lon),
            (n + h) * c * math.sin(lon),
            (n * (1.0 - WGS84_E2) + h) * s)


def enu_basis(lat_deg, lon_deg):
    """某点的 ENU(东/北/天)单位基向量"""
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    sl, cl = math.sin(lat), math.cos(lat)
    so, co = math.sin(lon), math.cos(lon)
    e = (-so, co, 0.0)
    n = (-sl * co, -sl * so, cl)
    u = (cl * co, cl * so, sl)
    return e, n, u


# ---------------- 线性代数(纯标准库,小型够用) ----------------
def solve_linear(A, b):
    """高斯消元(部分主元)解 n×n 线性方程组"""
    n = len(b)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        p = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[p][col]) < 1e-14:
            raise ValueError("奇异雅可比/法方程矩阵")
        M[col], M[p] = M[p], M[col]
        for r in range(col + 1, n):
            f = M[r][col] / M[col][col]
            for k in range(col, n + 1):
                M[r][k] -= f * M[col][k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))
        x[i] = s / M[i][i]
    return x


# ---------------- 卫星场景生成(固定种子,可复现) ----------------
def make_satellites(rng, recv_ecef, lat_deg, lon_deg, n_sat):
    """随机 ECEF 方向 + 固定轨道半径,保留高度角>遮蔽角的卫星"""
    _, _, up = enu_basis(lat_deg, lon_deg)
    sats, trials = [], 0
    while len(sats) < n_sat and trials < 100000:
        trials += 1
        cu = rng.uniform(-1.0, 1.0)                  # 随机球面方向
        phi = rng.uniform(0.0, 2.0 * math.pi)
        sq = math.sqrt(1.0 - cu * cu)
        sat = (SAT_RADIUS * sq * math.cos(phi),
               SAT_RADIUS * sq * math.sin(phi),
               SAT_RADIUS * cu)
        d = [sat[k] - recv_ecef[k] for k in range(3)]
        dist = math.sqrt(sum(v * v for v in d))
        elev = math.degrees(math.asin(sum(d[k] * up[k] for k in range(3)) / dist))
        if elev > MIN_ELEV_DEG:
            sats.append(sat)
    if len(sats) < n_sat:
        raise RuntimeError("可见卫星不足")
    return sats


def simulate_pseudoranges(sats, recv_ecef, clk_bias_m, rng=None, sigma=0.0):
    """伪距 = 真几何距离 + 钟差(米) + 可选高斯噪声"""
    pr = []
    for s in sats:
        d = math.sqrt(sum((s[k] - recv_ecef[k]) ** 2 for k in range(3)))
        noise = rng.gauss(0.0, sigma) if (rng is not None and sigma > 0) else 0.0
        pr.append(d + clk_bias_m + noise)
    return pr


# ---------------- §B 定位解算器:构造档②(迭代) ----------------
def solve_position(sats, pr, x0=(0.0, 0.0, 0.0, 0.0), max_iter=15, tol=1e-4):
    """线性化迭代最小二乘:未知数 (x,y,z,cδt)
    每轮:预测伪距 → 残差 → 雅可比行=[卫星→接收机单位向量, 1] → 解更新量"""
    x = list(x0)
    for it in range(max_iter):
        H, r = [], []
        for i, s in enumerate(sats):
            dx = (x[0] - s[0], x[1] - s[1], x[2] - s[2])
            dist = math.sqrt(sum(v * v for v in dx))
            pred = dist + x[3]
            r.append(pr[i] - pred)
            H.append([dx[0] / dist, dx[1] / dist, dx[2] / dist, 1.0])
        m = len(sats)
        if m == 4:                                   # 恰定:直接解
            dx = solve_linear(H, r)
        else:                                        # 超定:法方程最小二乘
            ATA = [[sum(H[a][i] * H[a][j] for a in range(m)) for j in range(4)]
                   for i in range(4)]
            ATb = [sum(H[a][i] * r[a] for a in range(m)) for i in range(4)]
            dx = solve_linear(ATA, ATb)
        x = [x[k] + dx[k] for k in range(4)]
        if max(abs(v) for v in dx) < tol:
            break
    return x, it + 1


def gdop(sats, x):
    """GDOP = sqrt(trace((HᵀH)⁻¹)):几何税(03 章 §3.3)"""
    m = len(sats)
    H = []
    for s in sats:
        dx = (x[0] - s[0], x[1] - s[1], x[2] - s[2])
        dist = math.sqrt(sum(v * v for v in dx))
        H.append([dx[0] / dist, dx[1] / dist, dx[2] / dist, 1.0])
    ATA = [[sum(H[a][i] * H[a][j] for a in range(m)) for j in range(4)]
           for i in range(4)]
    Q = [solve_linear(ATA, [1.0 if i == j else 0.0 for j in range(4)])
         for i in range(4)]                          # 逐列求逆
    return math.sqrt(sum(Q[i][i] for i in range(4)))


# ---------------- 主流程 ----------------
def main():
    print("=" * 64)
    print("四星伪距 GPS 定位 · 线性化迭代最小二乘(GB/T 41330 家族实验)")
    print("=" * 64)

    # 真值:北京,椭球高 50 m;接收机钟差真值 85000 m(≈0.283 ms)
    LAT, LON, H = 39.9042, 116.4074, 50.0
    CLK_TRUE = 85000.0
    recv = geodetic_to_ecef(LAT, LON, H)

    print(f"\n[§A] 大地坐标→ECEF(闭式): ({LAT}, {LON}, {H}m) ->")
    print(f"     x={recv[0]:.3f}  y={recv[1]:.3f}  z={recv[2]:.3f}")
    r0 = geodetic_to_ecef(0.0, 0.0, 0.0)
    assert abs(r0[2] - 0.0) < 1e-6 and abs(math.hypot(r0[0], r0[1]) - WGS84_A) < 1e-6

    rng = random.Random(42)
    sats = make_satellites(rng, recv, LAT, LON, 6)

    # 场景 1:恰好 4 星,无噪声 → 4 方程 4 未知数,精确解
    pr4 = simulate_pseudoranges(sats[:4], recv, CLK_TRUE)
    sol4, it4 = solve_position(sats[:4], pr4)
    err4 = math.sqrt(sum((sol4[k] - recv[k]) ** 2 for k in range(3)))
    clk_err4 = abs(sol4[3] - CLK_TRUE)
    print(f"\n[§B-1] 4 星无噪声: {it4} 轮收敛")
    print(f"     三维位置误差 = {err4:.2e} m   钟差误差 = {clk_err4:.2e} m")
    print(f"     (第四颗星不是冗余,是买钟——钟差 85000 m 同时被解出)")
    assert err4 < 1e-3 and clk_err4 < 1e-3, "无噪声恰定解应达机器精度"

    # 场景 2:6 星,σ=5 m 伪距噪声 → 最小二乘均摊,误差<100 m
    rng_n = random.Random(7)
    pr6 = simulate_pseudoranges(sats, recv, CLK_TRUE, rng=rng_n, sigma=5.0)
    sol6, it6 = solve_position(sats, pr6)
    err6 = math.sqrt(sum((sol6[k] - recv[k]) ** 2 for k in range(3)))
    clk_err6 = abs(sol6[3] - CLK_TRUE)
    g = gdop(sats, sol6)
    print(f"\n[§B-2] 6 星 σ=5 m 噪声: {it6} 轮收敛,GDOP={g:.2f}")
    print(f"     三维位置误差 = {err6:.2f} m   钟差误差 = {clk_err6:.2f} m")
    print(f"     (误差≈测距噪声×几何税 GDOP;加星=降税)")
    assert err6 < 100.0, f"噪声场景三维位置误差应<100 m,实测 {err6:.2f} m"
    assert clk_err6 < 100.0

    # §C ECEF → 本地 ENU 切平面:构造档①
    e, n, u = enu_basis(LAT, LON)
    nearby = geodetic_to_ecef(LAT + 0.01, LON + 0.01, H)
    d = [nearby[k] - recv[k] for k in range(3)]
    E = sum(d[k] * e[k] for k in range(3))
    N = sum(d[k] * n[k] for k in range(3))
    U = sum(d[k] * u[k] for k in range(3))
    print(f"\n[§C] 本地点 (+0.01°lat, +0.01°lon) 的 ECEF 位移 → ENU:")
    print(f"     E={E:.1f} m  N={N:.1f} m  U={U:.2f} m")
    print(f"     (经度方向 1°≈85.5 km·cos 因子,纬度方向 1°≈111 km)")
    assert 1100.0 < N < 1120.0, "0.01° 纬距应约 1111 m"
    assert 845.0 < E < 865.0, "北京纬度 0.01° 经距应约 855 m"
    assert abs(U) < 5.0, "同椭球高的邻近点天向分量应近零"

    # 反直觉演示:钟即尺
    print(f"\n[附] 钟变成尺:1 ms 钟误差 = {C * 1e-3 / 1000:.1f} km, "
          f"1 ns = {C * 1e-9:.3f} m —— 接收机钟差必须当第四未知数解掉")

    print("\n" + "=" * 64)
    print("ALL TESTS PASSED (exit 0)")
    sys.exit(0)


if __name__ == "__main__":
    main()
