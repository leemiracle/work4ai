# -*- coding: utf-8 -*-
"""
stress_performance_inverted_u.py — 应激-绩效倒U(耶克斯-多德森)数值演示

对应章:04-军事心理学转代码(走廊①)/00-体系结构(暗线:剂量思维)/
      02-语言特征(第二栏:定律的措辞如何塑造直觉)
GB/T 83020 军事心理学 · 家族层实验(纯标准库,assert 自验证)

做什么:把 1908 年 Yerkes-Dodson 的两条经验规律写成可计算模型:

    P(A; tau) = A * exp(-beta(tau) * A)
      A   = 唤醒水平(应激剂量,越大越"上头")
      tau = 任务复杂度(0, 1]
      beta = 0.4 + 1.2*tau:任务越复杂,衰减率越大

  规律一(倒U)  :绩效随唤醒先升后降,峰值在 A* = 1/beta
  规律二(难度交互):任务越复杂,最优唤醒越低(简单任务吃得起高唤醒);
                    同样的过度唤醒,复杂任务蒙受的相对损失远大于简单任务

数字是定律的化身,不是实验数据:原始研究是小鼠电击-辨别学习
(Yerkes & Dodson 1908, J. Comp. Neurol. Psychol.),这里只是把
教科书曲线参数化——引用倒U时应带上"难度×强度交互"这个原始限定。

运行:python stress_performance_inverted_u.py   (全部 assert 通过即 exit 0)
"""

import math

AROUSAL_GRID = [i * 0.1 for i in range(1, 61)]  # A ∈ (0.1 .. 6.0],步长0.1


def beta(tau):
    """任务复杂度 → 衰减率;tau 越大 beta 越大,最优唤醒 1/beta 越低"""
    assert 0.0 < tau <= 1.0
    return 0.4 + 1.2 * tau


def performance(A, tau):
    """倒U曲线:绩效 = 唤醒 × exp(-β·唤醒)"""
    b = beta(tau)
    return A * math.exp(-b * A)


def peak_arousal_analytic(tau):
    """解析峰值位置:对 A·e^{-βA} 求导为零 → A* = 1/β"""
    return 1.0 / beta(tau)


def peak_arousal_numeric(tau):
    """数值峰值位置:网格搜索(模拟'实测曲线找峰')"""
    best_A, best_P = None, -1.0
    for A in AROUSAL_GRID:
        P = performance(A, tau)
        if P > best_P:
            best_A, best_P = A, P
    return best_A


def relative_overload_loss(tau, A_over=2.5):
    """过度唤醒的相对损失:1 - P(A_over)/P(A*) —— 同样的'上头',
    复杂任务掉下去的比例有多大"""
    p_star = performance(peak_arousal_analytic(tau), tau)
    p_over = performance(A_over, tau)
    return 1.0 - p_over / p_star


# ---------- 演示 1:难度交互——最优唤醒随复杂度左移 ----------

def demo_peak_shift():
    print("[1] 任务复杂度 tau → 最优唤醒 A*(解析 / 数值)")
    for tau in (0.1, 0.3, 0.5, 0.7, 0.9):
        pa, pn = peak_arousal_analytic(tau), peak_arousal_numeric(tau)
        print("    tau=%.1f   A* = %5.2f (解析)   %5.2f (数值)" % (tau, pa, pn))
        # 数值峰与解析峰一致(网格分辨率 0.1 → 容差 0.051)
        assert abs(pa - pn) <= 0.051, (tau, pa, pn)
    # 规律二:复杂任务的最优唤醒严格低于简单任务(左移)
    assert peak_arousal_analytic(0.9) < peak_arousal_analytic(0.1)
    assert peak_arousal_analytic(0.9) < peak_arousal_analytic(0.5)
    assert peak_arousal_analytic(0.5) < peak_arousal_analytic(0.1)


# ---------- 演示 2:倒U——先升后降且单峰 ----------

def demo_inverted_u():
    print("[2] 倒U形状检验(tau=0.5):绩效曲线先升后降、单峰")
    tau = 0.5
    Ps = [performance(A, tau) for A in AROUSAL_GRID]
    i_star = Ps.index(max(Ps))
    print("    A 从 %.1f → %.1f:P %.3f → %.3f → %.3f(峰值在 A=%.1f)"
          % (AROUSAL_GRID[0], AROUSAL_GRID[-1], Ps[0], max(Ps), Ps[-1],
             AROUSAL_GRID[i_star]))
    # 单峰:峰前严格上升,峰后严格下降
    assert all(Ps[i] < Ps[i + 1] for i in range(i_star))
    assert all(Ps[i] > Ps[i + 1] for i in range(i_star, len(Ps) - 1))
    # 唤醒不足同样有害(低唤醒端趋近于零绩效)
    assert performance(0.1, tau) < performance(1.0, tau) * 0.5


# ---------- 演示 3:过度唤醒的相对损失——难度×强度交互 ----------

def demo_overload_loss():
    print("[3] 同样的过度唤醒(A=2.5)对不同任务造成的相对损失:")
    for tau in (0.1, 0.3, 0.5, 0.7, 0.9):
        loss = relative_overload_loss(tau)
        print("    tau=%.1f   相对损失 = %5.1f%%" % (tau, 100.0 * loss))
    # 1908 年原始命题的化身:复杂任务在高强度下受害远甚于简单任务
    assert relative_overload_loss(0.1) < 0.10   # 简单任务:轻微损失
    assert relative_overload_loss(0.9) > 0.50   # 复杂任务:过半损失
    assert relative_overload_loss(0.9) > relative_overload_loss(0.1)


def main():
    print("=" * 62)
    print("应激-绩效倒U数值演示(Yerkes-Dodson 1908 的参数化转世)")
    print("=" * 62)
    demo_peak_shift()
    demo_inverted_u()
    demo_overload_loss()
    print("-" * 62)
    print("全部 assert 通过:倒U(先升后降/单峰)成立;")
    print("最优唤醒随任务复杂度左移;过度唤醒对复杂任务更致命。")
    print("提示:P(A;tau)=A·e^(-βA) 是命题化身,非实验数据拟合。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
