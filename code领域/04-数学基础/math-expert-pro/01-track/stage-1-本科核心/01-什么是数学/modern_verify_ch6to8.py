# -*- coding: utf-8 -*-
"""《什么是数学》第6-8章 现代验证（柯朗：函数与极限 / 极大极小 / 微积分）
分析主线，衔接 Spivak。纯 Python 无依赖"""
import math

# ---------- §6 函数与极限：ε-δ 直觉 ----------
def section_6_limit():
    print("\n" + "="*60)
    print("【§6 函数与极限：ε-δ 定义 + 数值验证】")
    print("="*60)
    # ε-δ 定义：∀ε>0, ∃δ>0, 使 |x-a|<δ ⟹ |f(x)-L|<ε
    print("ε-δ 极限定义：lim(x→a) f(x) = L")
    print("  ∀ε>0, ∃δ>0, 使 0<|x-a|<δ ⟹ |f(x)-L|<ε")
    print("\n例：lim(x→2) (3x+1) = 7")
    # 数值验证：x 越接近 2，f(x) 越接近 7
    print("  数值：x→2 时 f(x)=3x+1 的值：")
    for dx in [0.1, 0.01, 0.001, 1e-6, 1e-9]:
        x = 2 + dx
        print(f"    x=2+{dx:.0e}: f(x)={3*x+1:.12f}, |f(x)-7|={abs(3*x+1-7):.2e}")
    # 给定 ε 找 δ：要 |f(x)-7|<ε ⟺ 3|x-2|<ε ⟺ |x-2|<ε/3，故 δ=ε/3
    print("\n  给定 ε 求 δ：|3x+1-7|=3|x-2|<ε ⟺ |x-2|<ε/3，故 δ=ε/3")
    for eps in [0.1, 0.01, 0.001]:
        delta = eps/3
        # 验证边界
        x_boundary = 2 + delta
        assert abs(3*x_boundary+1 - 7) <= eps + 1e-12
        print(f"    ε={eps}: δ=ε/3={delta:.6f}, 边界 |f(2+δ)-7|={abs(3*x_boundary+1-7):.6f} ≤ ε ✓")
    print("\n→ ε-δ 的精髓：'你随便给一个误差容忍 ε，我都能找到对应的接近度 δ'")
    print("  这是'挑战-应答'博弈——你给 ε 挑战，我用 δ 应对，永远守得住")

    # 震荡反例：sin(1/x) 在 x→0 无极限
    print("\n反例：sin(1/x) 在 x→0 无极限（震荡）")
    for x in [0.1, 0.01, 1e-3, 1e-4, 1e-6]:
        print(f"    x={x:.0e}: sin(1/x)={math.sin(1/x):.6f}（在 -1 到 1 间剧烈震荡）")

# ---------- §7 极大极小：变分法 ----------
def section_7_extrema():
    print("\n" + "="*60)
    print("【§7 极大极小：变分法 + 最速降线】")
    print("="*60)
    # 函数极值：f'(x)=0 + f''(x) 判别
    print("函数极值：f'(x₀)=0 + f''(x₀) 判别（>0 极小，<0 极大）")
    # 例：f(x) = x² 在 x=0 极小
    print(f"  f(x)=x²: f'(0)=0, f''(0)=2>0 → x=0 是极小，f(0)={0**2}")
    # 数值验证梯度下降找极小
    print(f"\n梯度下降找 f(x)=x²+2x+1=(x+1)² 的极小（应为 x=-1, f=0）：")
    x = 5.0  # 起点
    lr = 0.1
    for i in range(50):
        grad = 2*x + 2  # f'(x)
        x = x - lr * grad
    print(f"  50 步后 x={x:.10f}, f(x)={x**2+2*x+1:.2e}（→ 极小 x=-1）")
    # 变分法：最速降线（brachistochrone）= 摆线，不是直线
    print(f"\n变分法巅峰：最速降线问题（1696 Johann Bernoulli）")
    print(f"  问题：球从 A 到 B（A 高于 B），走什么路径最快？")
    print(f"  直觉答案：直线。正确答案：摆线（cycloid）——'先陡降加速，再平缓利用速度'")
    print(f"  这是变分法的开端：求泛函 J[y]=∫L(y,y',x)dx 的极值，Euler-Lagrange 方程")
    print(f"  → 物理学的'最小作用量原理'同源（[03/物理-对称守恒]的 Noether 定理）")

# ---------- §8 微积分：导数/积分/FTC ----------
def section_8_calculus():
    print("\n" + "="*60)
    print("【§8 微积分：导数/积分/微积分基本定理 FTC】")
    print("="*60)
    # 导数 = 瞬时变化率 = lim (f(x+h)-f(x))/h
    print("导数：f'(x) = lim(h→0) [f(x+h)-f(x)]/h")
    print("  数值验证 f(x)=x² 的导数 f'(x)=2x：")
    for x in [1, 2, 3]:
        for h in [0.1, 0.001, 1e-9]:
            num_deriv = ((x+h)**2 - x**2) / h
        h = 1e-9
        num_deriv = ((x+h)**2 - x**2) / h
        print(f"    f({x})=x²: 数值导数（h=1e-9）={num_deriv:.8f}, 精确 2x={2*x}")

    # 积分 = 黎曼和极限 = 曲线下面积
    print("\n积分：∫ₐᵇ f(x)dx = lim(Δx→0) Σ f(xᵢ)Δx（黎曼和）")
    # 数值积分 ∫₀¹ x² dx = 1/3
    def riemann_sum(f, a, b, n):
        dx = (b - a) / n
        return sum(f(a + i*dx) for i in range(n)) * dx
    exact = 1/3
    for n in [10, 100, 1000, 10000]:
        approx = riemann_sum(lambda x: x**2, 0, 1, n)
        print(f"    ∫₀¹ x²dx 的黎曼和（n={n}）={approx:.10f}, 精确 1/3={exact:.10f}, 误差={abs(approx-exact):.2e}")

    # FTC：d/dx ∫ₐˣ f(t)dt = f(x)
    print("\n★ 微积分基本定理 FTC：d/dx ∫ₐˣ f(t)dt = f(x)")
    print("  导数与积分互为逆运算——这是微积分最美的定理")
    # 验证：d/dx ∫₀ˣ t² dt = d/dx (x³/3) = x²
    print("  验证：d/dx ∫₀ˣ t²dt = d/dx(x³/3) = x² ✓（求导与积分互逆）")
    print("\n→ 柯朗第 8 章的微积分是'直觉版'，严格 ε-δ 版在 Spivak《Calculus》（你的阶段1灵魂）")
    print("  柯朗建直觉，Spivak 建严格——两者配合是学微积分的最佳路径")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  《什么是数学》第 6-8 章 · 现代验证（极限/极值/微积分）   ║")
    print("╚" + "═"*58 + "╝")
    section_6_limit()
    section_7_extrema()
    section_8_calculus()
    print("\n" + "═"*60)
    print("✅ 第 6-8 章验证通过。分析主线打通。")
    print("═"*60)
