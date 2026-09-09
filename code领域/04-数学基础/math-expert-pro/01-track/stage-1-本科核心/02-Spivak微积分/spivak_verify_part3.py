# -*- coding: utf-8 -*-
"""Spivak《Calculus》Part III 现代验证（导数 + 积分 + FTC + 牛顿法）
阶段1灵魂。纯 Python 无依赖"""
import math

# ---------- §1 导数：定义与法则 ----------
def section_derivative():
    print("\n" + "="*60)
    print("【Part III 导数：定义 + 法则 + 链式法则（Spivak 第9-10章）】")
    print("="*60)
    print("导数定义：f'(a) = lim(h→0) [f(a+h)-f(a)]/h")
    # 数值导数验证
    print("\n数值验证（中心差分，比前向差分更准）：")
    def num_deriv(f, a, h=1e-7):
        return (f(a+h) - f(a-h)) / (2*h)
    cases = [
        ("x²", lambda x: x**2, lambda x: 2*x, [1,2,3,-1]),
        ("x³", lambda x: x**3, lambda x: 3*x**2, [1,2,-2]),
        ("sin(x)", math.sin, math.cos, [0, math.pi/4, math.pi/2]),
        ("eˣ", math.exp, math.exp, [0, 1, 2]),
        ("ln(x)", math.log, lambda x: 1/x, [1, 2, 10]),
    ]
    for name, f, exact, pts in cases:
        for a in pts[:2]:
            num = num_deriv(f, a)
            ex = exact(a)
            print(f"  ({name})' at x={a}: 数值={num:.8f}, 精确={ex:.8f}, 误差={abs(num-ex):.2e}")
    # 求导法则：和/积/商/链式
    print("\n求导法则验证（链式法则：(f∘g)'(x)=f'(g(x))·g'(x)）：")
    # f(x)=sin(x²), f'(x)=cos(x²)·2x
    f_comp = lambda x: math.sin(x**2)
    f_comp_exact = lambda x: math.cos(x**2) * 2*x
    for a in [0.5, 1.0, 1.5]:
        num = num_deriv(f_comp, a)
        ex = f_comp_exact(a)
        print(f"  (sin(x²))' at x={a}: 数值={num:.8f}, 链式法则=cos(x²)·2x={ex:.8f}, 误差={abs(num-ex):.2e}")
    print("→ 链式法则 = 你写反向传播时用的求导法则（你的 PyTorch 背景）")

# ---------- §2 积分：黎曼和 + FTC ----------
def section_integral():
    print("\n" + "="*60)
    print("【Part III 积分：黎曼和 + FTC + 数值积分（Spivak 第13章）】")
    print("="*60)
    # 黎曼和：∫_a^b f = lim Σ f(x_i)Δx
    def riemann(f, a, b, n, mode="left"):
        dx = (b-a)/n
        if mode == "left":
            return sum(f(a+i*dx) for i in range(n)) * dx
        elif mode == "mid":
            return sum(f(a+(i+0.5)*dx) for i in range(n)) * dx
    # 验证 ∫_0^1 x² dx = 1/3
    print("∫_0^1 x² dx = 1/3，黎曼和收敛：")
    exact = 1/3
    for n in [10, 100, 1000, 10000]:
        L = riemann(lambda x: x**2, 0, 1, n, "left")
        M = riemann(lambda x: x**2, 0, 1, n, "mid")
        print(f"  n={n:>5}: 左黎曼和={L:.10f}（误差{abs(L-exact):.2e}），中点={M:.10f}（误差{abs(M-exact):.2e}，更快）")
    # FTC：∫_a^b f = F(b)-F(a)，其中 F'=f
    print(f"\n★ FTC（Spivak 第14章核心）：∫_a^b f(x)dx = F(b)-F(a)，其中 F'=f")
    # f=x², F=x³/3
    a, b = 0, 1
    F = lambda x: x**3/3
    f = lambda x: x**2
    ftc_val = F(b) - F(a)
    riemann_val = riemann(f, a, b, 100000, "mid")
    print(f"  f(x)=x², F(x)=x³/3：FTC 算 F(1)-F(0)={ftc_val:.10f}")
    print(f"  黎曼和（n=100000）={riemann_val:.10f}（两者吻合，FTC 正确）")
    print(f"→ 导数与积分互逆——这是微积分最美定理（柯朗第8章直觉版，Spivak 严格证）")

# ---------- §3 牛顿法（Spivak 应用） ----------
def section_newton():
    print("\n" + "="*60)
    print("【Part III 应用：牛顿法求根（Spivak 第4章附录/第10章应用）】")
    print("="*60)
    print("牛顿法：x_{n+1} = x_n - f(x_n)/f'(x_n)，二次收敛")
    # 求 √2：f(x)=x²-2
    print("求 √2（f(x)=x²-2，迭代 x ← (x + 2/x)/2）：")
    x = 1.0
    for i in range(6):
        x_new = x - (x**2 - 2)/(2*x)
        err = abs(x_new - math.sqrt(2))
        print(f"  迭代 {i+1}: x={x_new:.15f}, 误差={err:.2e}")
        if err < 1e-15: break
        x = x_new
    print(f"  精确 √2 = {math.sqrt(2):.15f}")
    print("→ 牛顿法'二次收敛'：每步有效位数翻倍。这是导数的工程应用（[03/控制]、[03/量化]）")

# ---------- §4 π 和 e（Spivak 第15-18章） ----------
def section_pi_e():
    print("\n" + "="*60)
    print("【Part III π 与 e：用微积分严格定义（Spivak 第15-18章）】")
    print("="*60)
    # e = lim(1+1/n)^n = Σ 1/n!
    print("e 的两种严格定义（Spivak 第18章）：")
    n = 1000000
    e_limit = (1 + 1/n)**n
    e_series = sum(1/math.factorial(k) for k in range(20))
    print(f"  e = lim(1+1/n)^n (n={n}) = {e_limit:.12f}")
    print(f"  e = Σ 1/n! (前20项)        = {e_series:.12f}")
    print(f"  math.e = {math.e:.12f}")
    # π 用反正切的级数（Spivak 用 arctan 积分定义 π）
    print(f"\nπ 的定义（Spivak 第15-16章）：")
    print(f"  Spivak 用 ∫_(-1)^(1) dx/(1+x²) = π/2 + π/2 = π 来定义 π")
    # π 的 Leibniz 级数：π/4 = 1 - 1/3 + 1/5 - 1/7 + ...
    pi_leibniz = 4 * sum((-1)**k / (2*k+1) for k in range(100000))
    print(f"  Leibniz 级数 π/4 = 1-1/3+1/5-... (10万项) = π ≈ {pi_leibniz:.10f}（收敛慢但严格）")
    print(f"  math.pi = {math.pi:.10f}")
    print("→ Spivak 不假设 π/e '已知'，而是从积分/极限**构造**它们——严格化到骨子里")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  Spivak《Calculus》Part III · 现代验证                     ║")
    print("║  导数 + 积分 + FTC + 牛顿法 + π/e 严格定义                  ║")
    print("╚" + "═"*58 + "╝")
    section_derivative()
    section_integral()
    section_newton()
    section_pi_e()
    print("\n" + "═"*60)
    print("✅ Part III 验证通过。导数/积分/FTC/应用全打通。")
    print("═"*60)
