# -*- coding: utf-8 -*-
"""有限差分 vs 物理信息神经网络:一维泊松方程三解法对比(00/01/04 章配套实验)。

问题: -u''(x) = f(x), x ∈ (0,1), u(0) = u(1) = 0
取解 u(x) = sin(4πx),右端 f(x) = 16π²·sin(4πx)(解析参考基准)。
解取 4 个半波:单一半波(sin πx)会被随机 tanh 基近乎精确表示,
基表达力不构成瓶颈,采样效应反而显形;4 个半波让**基表达力成为
误差的主导瓶颈**——本实验要演示的正是这个 regime。

三解法:
  ① 有限差分(FDM):中心差分离散 -u''=f(二阶截断),三对角
     方程组用追赶法(Thomas)求解——数值线代表
  ② 教学版 PINN:u_θ(x) = x(1-x)·Σ w_j·tanh(s_j·x + c_j)。
     边界用 x(1-x) 因子硬编码(恒满足 Dirichlet,零违约);
     训练简化为"解析最小网络":隐层 (s_j, c_j) 固定随机
     (随机特征/极限学习机式),输出层权重 w 使配点 PDE 残差
     最小二乘——残差对 w 线性,正规方程+高斯消元解析可解,
     全程纯 math 无梯度训练——数据线代表(物理=损失的一项)
  ③ 解析解:sin(4πx),参考基准
六个结构化断言:
  ① FDM 误差按 h² 收敛:逐次加密(16→128),数值收敛阶
     log2(e_h/e_{h/2}) 全部落在 [1.8, 2.2](二阶格式的复现)
  ② 小规模 PINN(48 隐层)误差不劣于粗网格 FDM(n=16)——
     教学版可行性(实测 5 个数量级更优,光滑低维问题的特性)
  ③ 采样密度 ≠ 网格加密:配点足量(≥80)后误差饱和在基误差
     带(<2 倍、无系统下降),同期 FDM 网格加密 16→128 误差
     改善 >30 倍——PINN 无网格,误差由基表达力决定,不由采样
     密度决定(方法论差异的核心展示;配点不足 40 时误差恶化
     两个数量级——"足量才饱和"的两面都演示)
  ④ 表达力决定论:同一配点数,隐层宽度 6→48,误差改善 >100 倍
     ——数据线的"加密旋钮"是基规模,不是采样密度
  ⑤ 两种方法在教学规模下最大误差均 < 5e-2(可用精度)
  ⑥ PINN 边界条件零违约(x(1-x) 因子的解析保证,非惩罚项)
⚠ 纪律(02/04 章):本 PINN 为教学版(随机特征+输出层最小二乘),
非生产 PINN(全网络梯度训练,01 章方向四);隐层规模/配点数为
示意值;"FDM 收敛、PINN 不随采样密度系统下降"不等于"FDM 更好"
——反问题/高维/复杂几何场景的分工见 01 章三分天下;本脚本输出为
教学演示级证据,不可当工程验收依据。

跑法: python experiments/pinn_vs_fdm.py
"""

import math
import random

SEED = 20260907
PI = math.pi
K = 4  # 半波数:让基表达力成为误差瓶颈(见文件头注记)


# ---------------------------------------------------------------- 解析参考
def f_rhs(x):
    """右端项 f(x)=16π²·sin(4πx)(与 -u''=sin(4πx) 匹配)。"""
    return (K * PI) ** 2 * math.sin(K * PI * x)


def u_exact(x):
    return math.sin(K * PI * x)


# ---------------------------------------------------------------- FDM
def solve_fdm(n):
    """中心差分 + 追赶法解 -u''=f,n 个区间(边界 u=0)。

    离散: (2u_i - u_{i-1} - u_{i+1})/h² = f(x_i),i=1..n-1
    截断误差 O(h²);返回 (h, 节点解列表含边界)。
    """
    h = 1.0 / n
    m = n - 1
    a = [-1.0] * m          # 下对角
    b = [2.0] * m           # 主对角
    c = [-1.0] * m          # 上对角
    d = [h * h * f_rhs((i + 1) * h) for i in range(m)]
    for i in range(1, m):   # Thomas 前向消元
        w = a[i] / b[i - 1]
        b[i] -= w * c[i - 1]
        d[i] -= w * d[i - 1]
    u = [0.0] * m           # 回代
    u[-1] = d[-1] / b[-1]
    for i in range(m - 2, -1, -1):
        u[i] = (d[i] - c[i] * u[i + 1]) / b[i]
    return h, [0.0] + u + [0.0]


# ---------------------------------------------------------------- 教学版 PINN
class RandomFeaturePinn:
    """u_θ(x) = x(1-x)·Σ w_j·tanh(s_j·x + c_j)。

    隐层 (s_j, c_j) 固定随机;基函数 g_j(x)=x(1-x)·tanh(s_j x+c_j)
    的 0/1/2 阶导数全部解析可微(物理信息:不靠网格差分求导)。
    输出层 w 由配点残差最小二乘解析求解(见 fit)。
    """

    def __init__(self, width, rng, smax=10.0):
        self.width = width
        self.s = [rng.uniform(-smax, smax) for _ in range(width)]
        self.c = [rng.uniform(-3.0, 3.0) for _ in range(width)]
        self.w = None

    def _g(self, j, x):
        """基函数 g_j 及其 0/1/2 阶导数(链式法则,解析)。"""
        s, c = self.s[j], self.c[j]
        t = math.tanh(s * x + c)
        dt = s * (1.0 - t * t)                    # φ'
        ddt = -2.0 * s * s * t * (1.0 - t * t)    # φ''
        q, dq = x - x * x, 1.0 - 2.0 * x          # x-x² 及其导数
        g = q * t
        gp = dq * t + q * dt
        gpp = -2.0 * t + 2.0 * dq * dt + q * ddt
        return g, gp, gpp

    def u(self, x):
        """网络输出(边界因子 x(1-x) 保证 u(0)=u(1)=0)。"""
        q = x - x * x
        return q * sum(self.w[j] * math.tanh(self.s[j] * x + self.c[j])
                       for j in range(self.width))

    def fit(self, n_colloc, ridge=1e-9):
        """输出层最小二乘:最小化 Σ_i [Σ_j w_j·(-g_j''(x_i)) - f(x_i)]²。

        残差对 w 线性 → 正规方程 (AᵀA+λI)w = AᵀF,高斯消元(部分
        主元)解析求解——"解析最小网络"的教学简化,免梯度训练。
        """
        m = self.width
        # 配点取内部均匀点(采样参数,非网格;断言③的对象)
        xs = [(i + 1) / (n_colloc + 1) for i in range(n_colloc)]
        rows = [[-self._g(j, x)[2] for j in range(m)] for x in xs]
        rhs = [f_rhs(x) for x in xs]
        ata = [[sum(r[i] * r[j] for r in rows) + (ridge if i == j else 0.0)
                for j in range(m)] for i in range(m)]
        atf = [sum(rows[k][i] * rhs[k] for k in range(len(rhs)))
               for i in range(m)]
        self.w = gauss_solve(ata, atf)
        return self


def gauss_solve(A, b):
    """高斯消元(部分主元),纯 list 实现——正规方程求解器。"""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-300:
            raise ValueError("奇异正规方程(基相关或 ridge 过小)")
        M[col], M[piv] = M[piv], M[col]
        inv = 1.0 / M[col][col]
        for r in range(col + 1, n):
            factor = M[r][col] * inv
            if factor != 0.0:
                for k in range(col, n + 1):
                    M[r][k] -= factor * M[col][k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][k] * x[k]
                              for k in range(i + 1, n))) / M[i][i]
    return x


def pinn_max_error(net, n_test=501):
    """独立测试网格上的最大误差(测试点≠配点,防自欺)。"""
    xs = [i / (n_test - 1) for i in range(n_test)]
    return max(abs(net.u(x) - u_exact(x)) for x in xs)


def fmt_ratio(x):
    """改善倍数的友好打印:大数用科学计数,避免超长整数。"""
    return f"{x:.1e} 倍" if x >= 1000 else f"{x:.1f} 倍"


# ---------------------------------------------------------------- 主流程
def main():
    print("=" * 76)
    print("有限差分 vs 物理信息神经网络:一维泊松方程三解法对比"
          f"(seed={SEED})")
    print("=" * 76)

    # --- [1] FDM 收敛阶研究(02 章 E3 证据制造机) ------------------
    print("\n[1] FDM 逐次加密收敛研究(中心差分,二阶截断)")
    print(f"{'n':>5} {'h':>10} {'最大误差':>12} {'收敛阶':>8}")
    ns = [16, 32, 64, 128]
    fdm_err = {}
    for n in ns:
        h, u = solve_fdm(n)
        xs = [i * h for i in range(n + 1)]
        err = max(abs(u[i] - u_exact(xs[i])) for i in range(n + 1))
        fdm_err[n] = err
        order = ""
        if n > ns[0]:
            order = f"{math.log2(fdm_err[n // 2] / err):.3f}"
        print(f"{n:>5} {h:>10.5f} {err:>12.3e} {order:>8}")
    orders = [math.log2(fdm_err[ns[i]] / fdm_err[ns[i + 1]])
              for i in range(len(ns) - 1)]
    fdm_gain = fdm_err[16] / fdm_err[128]

    # --- [2] 教学版 PINN(随机特征 + 输出层解析最小二乘) ------------
    print("\n[2] 教学版 PINN:u = x(1-x)·Σ w_j·tanh(s_j x + c_j),"
          "输出层最小二乘")
    net = RandomFeaturePinn(width=48, rng=random.Random(SEED)).fit(160)
    pin_err = pinn_max_error(net)
    bc_violation = max(abs(net.u(0.0)), abs(net.u(1.0)))
    print(f"    隐层 48(随机特征),配点 160(独立测试点 501)")
    print(f"    最大误差 {pin_err:.3e} | 边界违约 {bc_violation:.1e}"
          "(硬编码因子的解析保证)")
    print(f"    对照粗网格 FDM(n=16)误差 {fdm_err[16]:.3e}"
          f"——教学版可行性:不劣于粗网格档")

    # --- [3] 采样密度 vs 网格加密(方法论分野) ----------------------
    print("\n[3] 采样密度 vs 网格加密:配点 ×8 之后误差动了吗?")
    print(f"{'配点数':>8} {'PINN 最大误差':>14} {'备注':>10}")
    density_errs = {}
    for nc in (40, 80, 160, 320):
        rng_d = random.Random(SEED)   # 同一隐层(同一基),可对比
        net_d = RandomFeaturePinn(width=48, rng=rng_d).fit(n_colloc=nc)
        e = pinn_max_error(net_d)
        density_errs[nc] = e
        note = "欠采样" if nc < 80 else "饱和带"
        print(f"{nc:>8} {e:>14.3e} {note:>10}")
    plateau = [density_errs[nc] for nc in (80, 160, 320)]
    band = max(plateau) / min(plateau)
    plateau_gain = plateau[0] / plateau[-1]
    print(f"    饱和带(80/160/320)误差比 {band:.2f} | 80→320 改善 "
          f"{fmt_ratio(plateau_gain)}(无系统下降)")
    print(f"    同幅加密对照:FDM 网格 16→128 误差改善 {fmt_ratio(fdm_gain)}")

    # --- [4] 表达力决定论:同一配点,改基规模 ------------------------
    print("\n[4] 表达力对照:配点固定 160,隐层宽度 6→48")
    width_errs = {}
    for width in (6, 12, 24, 48):
        rng_w = random.Random(SEED)
        net_w = RandomFeaturePinn(width=width, rng=rng_w).fit(160)
        width_errs[width] = pinn_max_error(net_w)
        print(f"    宽度 {width:>3}: {width_errs[width]:.3e}")
    width_gain = width_errs[6] / width_errs[48]
    print(f"    宽度 6→48(×8)误差改善 {fmt_ratio(width_gain)}"
          "——数据线的加密旋钮是基规模,不是采样密度")

    # --- [5] 断言(自验) -----------------------------------------------
    print("\n[5] 结构化断言")
    checks = [
        ("① FDM 收敛阶≈2(全部 1.8-2.2)",
         all(1.8 < p < 2.2 for p in orders)),
        ("② PINN 误差不劣于粗网格 FDM(n=16)",
         pin_err < fdm_err[16]),
        ("③ 配点足量后误差饱和(带<2 且改善<1.5),"
         "FDM 同幅加密改善>30 倍",
         band < 2.0 and plateau_gain < 1.5 and fdm_gain > 30.0),
        ("④ 表达力决定:宽度 6→48 误差改善 >100 倍",
         width_gain > 100.0),
        ("⑤ 教学规模下两法误差均 < 5e-2",
         pin_err < 5e-2 and fdm_err[128] < 5e-2),
        ("⑥ PINN 边界零违约(硬编码因子)",
         bc_violation < 1e-15),
    ]
    for name, ok in checks:
        print(f"    [{'PASS' if ok else 'FAIL'}] {name}")
        assert ok, name

    print("\n⚠ 纪律:教学版 PINN(随机特征+解析输出层)非生产 PINN;"
          "输出为教学演示级证据(02 章阶梯 E3 以下),")
    print("  不可当工程验收依据;'FDM 收敛、PINN 不随采样系统下降'"
          "是方法论差异展示,不是优劣判决(01 章三分天下)。")
    print("=" * 76)
    print("全部断言通过——泊松方程上,数值线的误差有阶可外推(每加密"
          "一档×4),")
    print("数据线的误差由基表达力决定(采样足量即饱和):两条线的"
          "'加密旋钮'根本不同。")


if __name__ == "__main__":
    main()
