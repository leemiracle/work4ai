# -*- coding: utf-8 -*-
"""物理知情最小二乘：PINN 的裸核（去 N 版）。

04 章 · 转代码 配套实验。numpy。

问题: −u″ = f 于 [0,1]，u(0)=u(1)=0。取精确解 u=sin(πx) ⟹ f=π²sin(πx)。
方法: 基函数 φₖ(x)=x(1−x)xᵏ（边界条件编码进基），配点最小二乘
      min_θ Σᵢ ‖Σₖ cₖ φₖ″(xᵢ) + f(xᵢ)‖²
导数手推（自动微分的替身——PINN 里这步由 autodiff 代劳）。

跑法: python3 -u experiments/04_physics_informed.py
"""
import numpy as np


def basis(k):
    """返回 (φₖ, φₖ″) 的向量化函数。φₖ = x(1−x)xᵏ。"""
    def phi(x):
        return x ** (k + 1) - x ** (k + 2)
    def phi2(x):
        # 手推二阶导：(k+1)k x^{k-1} − (k+2)(k+1) x^{k}（k=0 首项为零，避开 0**-1）
        first = (k + 1) * k * x ** (k - 1) if k >= 1 else np.zeros_like(x)
        return first - (k + 2) * (k + 1) * x ** k
    return phi, phi2


def solve(K, npts=201):
    x = np.linspace(0, 1, npts)
    f = np.pi ** 2 * np.sin(np.pi * x)
    A = np.column_stack([basis(k)[1](x) for k in range(K)])   # 残差矩阵
    c, *_ = np.linalg.lstsq(A, -f, rcond=None)                # Σcₖφₖ″ = −f
    u_hat = sum(c[k] * basis(k)[0](x) for k in range(K))
    u_exact = np.sin(np.pi * x)
    err = np.max(np.abs(u_hat - u_exact))
    return x, c, err


def main():
    print("=" * 62)
    print("物理知情最小二乘（PINN 裸核）：−u″ = π²sin(πx)")
    print("=" * 62)
    print("基: φₖ=x(1−x)xᵏ（边界条件 u(0)=u(1)=0 编码进基）")
    print("最小二乘: min Σᵢ‖Σₖcₖφₖ″(xᵢ)+f(xᵢ)‖²  ← '物理'就是这行残差")
    print()
    prev = None
    for K in (2, 3, 4, 5, 6, 8):
        x, c, err = solve(K)
        rate = f"（误差比 {prev/err:.1f}×）" if prev else ""
        print(f"  基数 K={K}: 最大误差 {err:.2e} {rate}")
        prev = err
    print()
    _, c, _ = solve(4)
    print("K=4 的系数（对 sin(πx) 的多项式逼近系数）:")
    print("  " + ", ".join(f"{v:+.4f}" for v in c))
    print()
    print("对照 PINN（把基换成神经网络）:")
    print("  · 相同点：都是'残差平方和'当损失，边界/物理写进目标函数")
    print("  · 不同点：神经网络基免手选、可扩高维；代价是谱偏差+非凸+无误差界")
    print("  · 裸核的意义：先看清'PDE→目标函数'这一步——N 是后加的 💡")


if __name__ == "__main__":
    main()
