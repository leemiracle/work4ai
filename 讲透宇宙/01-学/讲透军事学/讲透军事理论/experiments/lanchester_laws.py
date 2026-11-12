# -*- coding: utf-8 -*-
"""
lanchester_laws.py — 兰彻斯特平方律 vs 线性律:集中兵力的数学表达

对应章:04-军事理论转代码(走廊①:假设宇宙内的推演——"算得准"档)
      /03-可构造与结构(✨美之时刻④:平方律=集中兵力的数学表达;
       L2 模型库:两律的分岔与各自的假设宇宙)
      /02-语言特征(§五:算学方言的机器化——编译的是方言,不是格言)
GB/T 83010 军事理论 · 家族层实验(纯标准库,RK4 数值积分,assert 自验证)

背景(兰彻斯特 1916《Aircraft in Warfare》第 5 章"集中原则"):
  平方律(现代作战/直接瞄准火力): dx/dt = -b*y, dy/dt = -a*x
    ——每一方损耗率正比于【对方】兵力数;等效能时守恒量 x²-y²
  线性律(古代方阵/一对一交战/面杀伤): dx/dt = -k*x*y, dy/dt = -k*x*y
    ——损耗率正比于双方兵力【乘积】(交战只发生在接触线上);
     等效能时守恒量 x-y

想定:蓝方 x0=1000(优势), 红方 y0=800(劣势), 等单位效能。
三组对照,每组都是一条军事理论的机器版:
  场景 1 终局与交换比 —— 平方律:红全灭时蓝剩约 600(交换比 2:1);
       线性律:蓝剩约 200(交换比 1:1)。劣势方在线性律下交换更划算。
  场景 2 固定作战时限的生存率 —— 同初始损耗率标定后,劣势方
       在线性律下任意同时刻存量更高(本实验断言的核心命题)。
  场景 3 集中 vs 分兵 —— 红方 800 合兵 vs 分两个 400 批次投入:
       平方律宇宙里分兵被各个击破(蓝终局 600 → 825,红利送对手);
       线性律宇宙里分兵【无惩罚】(守恒量 x-y 对分批免疫)。
       ⇒ "集中兵力"不是公理,是平方律宇宙的地方性定律。

运行:python lanchester_laws.py   (全部 assert 通过即 exit 0)
"""

import math

# ---------- 1. 数值积分:RK4 ----------

def integrate(rhs, x0, y0, dt, t_max, floor=2.0):
    """从 (x0,y0) 积到 t_max 或劣势方 y < floor(战斗终局截断)。
    返回 (x, y, t, traj),traj 为 [(t,x,y)] 轨迹(供定时取样)。"""
    t, x, y = 0.0, float(x0), float(y0)
    traj = [(t, x, y)]
    n_steps = int(t_max / dt)
    for _ in range(n_steps):
        if y <= floor:
            break
        k1x, k1y = rhs(x, y)
        k2x, k2y = rhs(x + 0.5 * dt * k1x, y + 0.5 * dt * k1y)
        k3x, k3y = rhs(x + 0.5 * dt * k2x, y + 0.5 * dt * k2y)
        k4x, k4y = rhs(x + dt * k3x, y + dt * k3y)
        x += dt * (k1x + 2 * k2x + 2 * k3x + k4x) / 6.0
        y += dt * (k1y + 2 * k2y + 2 * k3y + k4y) / 6.0
        t += dt
        traj.append((t, x, y))
    return x, y, t, traj


def square_rhs(a, b):
    """平方律:蓝损耗∝红军兵力,红损耗∝蓝军兵力。"""
    def f(x, y):
        return (-b * y, -a * x)
    return f

def linear_rhs(k):
    """线性律(等效能一对一):双方损耗率同为 k*x*y。"""
    def f(x, y):
        return (-k * x * y, -k * x * y)
    return f

def sample_at(traj, t_query):
    """轨迹在 t_query 时刻的最近取样点。"""
    best = min(traj, key=lambda p: abs(p[0] - t_query))
    return best[1], best[2]


# ---------- 参数:蓝 1000(优势)vs 红 800(劣势),等效能 ----------
X0, Y0 = 1000.0, 800.0
A = B = 0.001                    # 平方律效能:t=0 时红方损耗率 = A*X0 = 1.0/单位时间
K = 1.0 / (X0 * Y0)              # 线性律标定:t=0 时红方损耗率 = K*X0*Y0 = 1.0/单位时间
                                 # —— 同初始损耗率:两律对比的公平标定(配对实验)

# =====================================================================
# 场景 1:终局与交换比 —— 两律给劣势方完全不同的生死算法
# =====================================================================

def scenario_1():
    print("== 场景 1:终局与交换比(蓝 1000 vs 红 800,等效能)==")
    xs, ys, ts, _ = integrate(square_rhs(A, B), X0, Y0, dt=0.5, t_max=6000.0)
    print("  平方律:红全灭(t=%.0f)时蓝剩 %.1f" % (ts, xs))
    assert abs(xs - math.sqrt(X0 ** 2 - Y0 ** 2)) < 3.0, \
        "平方律终局应为 sqrt(1000^2-800^2)=600(解析守恒量 x^2-y^2)"
    print("  解析对照:x^2-y^2 守恒 ⇒ 终局 %.1f  OK" % math.sqrt(X0 ** 2 - Y0 ** 2))

    xl, yl, tl, traj_l = integrate(linear_rhs(K), X0, Y0, dt=5.0, t_max=60000.0)
    print("  线性律:红全灭(t=%.0f)时蓝剩 %.1f" % (tl, xl))
    assert abs(xl - (X0 - Y0)) < 3.0, \
        "线性律终局应为 1000-800=200(解析守恒量 x-y)"
    assert all(abs((x - y) - (X0 - Y0)) < 0.5 for _, x, y in traj_l[::200]), \
        "线性律全程守恒量 x-y=200 应保持"

    # 交换比:劣势方红每损失 1 人,换来蓝方多少损失
    ex_sq = (X0 - xs) / Y0       # 平方律:400/800 = 0.5
    ex_ln = (X0 - xl) / Y0       # 线性律:800/800 = 1.0
    print("  劣势方交换比:平方律 %.2f(1 换 0.5) vs 线性律 %.2f(1 换 1)"
          % (ex_sq, ex_ln))
    assert ex_ln > ex_sq, "劣势方在线性律下交换更划算"
    print("  —— 同样的兵力对比,交战律决定劣势方的生死算法 OK")


# =====================================================================
# 场景 2:固定作战时限的生存率 —— 本实验的核心断言
#          同(等初始损耗率标定的)兵力劣势方,在线性律下生存率更高
# =====================================================================

def scenario_2():
    print("== 场景 2:作战时限 T=300 时劣势方(红)存量对比 ==")
    _, _, _, traj_sq = integrate(square_rhs(A, B), X0, Y0, dt=0.5, t_max=2000.0)
    _, _, _, traj_ln = integrate(linear_rhs(K), X0, Y0, dt=5.0, t_max=2000.0)
    T = 300.0
    _, y_sq = sample_at(traj_sq, T)
    _, y_ln = sample_at(traj_ln, T)
    # 平方律解析对照:y(T) = (u0*e^{-aT} - v0*e^{aT})/2, u=x+y, v=x-y
    u = (X0 + Y0) * math.exp(-A * T)
    v = (X0 - Y0) * math.exp(A * T)
    y_sq_analytic = (u - v) / 2.0
    print("  T=%d 时红方存量:平方律 %.1f(解析 %.1f) vs 线性律 %.1f"
          % (T, y_sq, y_sq_analytic, y_ln))
    assert abs(y_sq - y_sq_analytic) < 5.0, "平方律数值应贴住解析解"
    assert y_ln > y_sq + 20.0, \
        "核心命题:同兵力劣势方在线性律下生存率更高(同时刻存量更大)"
    print("  —— 核心命题 OK:线性律 %.0f > 平方律 %.0f" % (y_ln, y_sq))
    print("  (平方律放大数量优势;线性律不放大——劣势方的活路在交战律里)")


# =====================================================================
# 场景 3:集中 vs 分兵 —— "集中兵力的数学表达"与它的适用边界
# =====================================================================

def scenario_3():
    print("== 场景 3:红方 800 合兵 vs 分两个 400 批次投入 ==")
    # 平方律·合兵:1000 vs 800 一波
    xb_united, _, _, _ = integrate(square_rhs(A, B), X0, Y0, dt=0.5, t_max=6000.0)
    # 平方律·分兵:先 1000 vs 400,残部再战下一批 400(各个击破)
    x_mid, _, _, _ = integrate(square_rhs(A, B), X0, 400.0, dt=0.5, t_max=6000.0)
    xb_split, _, _, _ = integrate(square_rhs(A, B), x_mid, 400.0, dt=0.5, t_max=6000.0)
    print("  平方律:蓝终局 合兵 %.1f vs 分兵 %.1f(中间态 %.1f)"
          % (xb_united, xb_split, x_mid))
    assert xb_split > xb_united + 100.0, \
        "平方律宇宙:劣势方分兵被各个击破,优势方赢得更轻松(600→825)"
    print("  —— 红方合兵能换蓝 400;分批只换约 %.0f:分兵的账单 OK"
          % (X0 - xb_split))

    # 线性律·合兵
    xl_united, _, _, _ = integrate(linear_rhs(K), X0, Y0, dt=5.0, t_max=60000.0)
    # 线性律·分兵
    x_mid_l, _, _, _ = integrate(linear_rhs(K), X0, 400.0, dt=5.0, t_max=60000.0)
    xl_split, _, _, _ = integrate(linear_rhs(K), x_mid_l, 400.0, dt=5.0, t_max=60000.0)
    print("  线性律:蓝终局 合兵 %.1f vs 分兵 %.1f" % (xl_united, xl_split))
    assert abs(xl_split - xl_united) < 2.0, \
        "线性律宇宙:守恒量 x-y 对分批免疫——分兵无惩罚"
    print("  —— 分兵免疫 OK:'集中兵力'是平方律宇宙的地方性定律,")
    print("     不是普适公理(知道律的边界与知道律本身同等重要)")


def main():
    scenario_1()
    scenario_2()
    scenario_3()
    print()
    print("全部断言通过:兰彻斯特两律对比自验证成功 (exit 0)")


if __name__ == "__main__":
    main()
