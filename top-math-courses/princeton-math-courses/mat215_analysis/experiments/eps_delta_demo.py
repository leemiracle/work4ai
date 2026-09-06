"""
import math
Princeton MAT 215 · 实验: ε-δ 极限的数值验证
依赖: numpy, matplotlib
运行: python3 eps_delta_demo.py

验证:
  1. ε-δ 博弈: 给定 ε, 找到 δ, 验证 |f(x)-L| < ε
  2. 完备性: Cauchy 序列在 R 中收敛
  3. 极值定理: 紧致集上连续函数取最值
  4. Taylor 展开: sigmoid 的多项式逼近
  5. 一致收敛 vs 逐点收敛: x^n 的反例
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ============================================================
# 实验 1: ε-δ 博弈
# ============================================================
print("=" * 70)
print("实验 1: ε-δ 博弈 — 验证 lim_{x->a} f(x) = L")
print("=" * 70)

# 例 1: lim_{x->2} x^2 = 4
print("\n例 1: lim_{x->2} x^2 = 4")
print("  策略: |x^2-4| = |x-2|·|x+2|, 当 |x-2|<1 时 |x+2|<5")
print("  所以取 δ = min(1, ε/5)")
a, L = 2.0, 4.0
for eps in [1e-1, 1e-3, 1e-6, 1e-9, 1e-12]:
    delta = min(1.0, eps / 5.0)
    x = a + delta / 2  # 取边界内最坏情况
    err = abs(x**2 - L)
    ok = "✓" if err < eps else "✗"
    print(f"  ε={eps:.0e} → δ={delta:.2e} → x={x:.10f} → |x²-4|={err:.2e} {ok}")

# 例 2: lim_{x->0} sin(x)/x = 1
print("\n例 2: lim_{x->0} sin(x)/x = 1")
print("  策略: sin(x)/x ≈ 1 - x²/6, 所以 |sin(x)/x - 1| ≈ x²/6")
print("  要 < ε, 取 δ = sqrt(6ε)")
for eps in [1e-1, 1e-3, 1e-6, 1e-9]:
    delta = np.sqrt(6 * eps)
    x = delta / 2
    err = abs(np.sin(x) / x - 1.0)
    ok = "✓" if err < eps else "✗"
    print(f"  ε={eps:.0e} → δ={delta:.4e} → x={x:.4e} → |sin(x)/x - 1|={err:.2e} {ok}")

# ============================================================
# 实验 2: 完备性 — Cauchy 序列收敛
# ============================================================
print("\n" + "=" * 70)
print("实验 2: 完备性 — Cauchy 序列在 R 中收敛")
print("=" * 70)

# 三个 Cauchy 序列
print("\n序列 1: s_n = sum_{k=1}^n 1/(k(k+1)) → 1 (telescoping)")
s1 = np.cumsum([1.0/(k*(k+1)) for k in range(1, 10001)])
print(f"  s_10000 = {s1[-1]:.12f}, |s-1| = {abs(s1[-1]-1):.2e}")

print("\n序列 2: s_n = (1+1/n)^n → e")
s2 = np.array([(1+1/n)**n for n in range(1, 10001)])
print(f"  s_10000 = {s2[-1]:.10f}, e = {np.e:.10f}, |s-e| = {abs(s2[-1]-np.e):.2e}")

print("\n序列 3: s_n = sum_{k=0}^n 1/k! → e")
s3 = np.cumsum([1.0/math.factorial(k) for k in range(170)])
print(f"  s_169 = {s3[-1]:.12f}, |s-e| = {abs(s3[-1]-np.e):.2e}")

# Cauchy 检验
print("\nCauchy 检验 (序列 1):")
for gap in [1000, 100, 10, 1]:
    diffs = np.abs(s1[gap:] - s1[:-gap])
    print(f"  max|s_n - s_{{n-{gap}}}| = {diffs.max():.2e}")

# ============================================================
# 实验 3: 极值定理
# ============================================================
print("\n" + "=" * 70)
print("实验 3: 极值定理 — 紧致集上连续函数取最值")
print("=" * 70)

x = np.linspace(0, 1, 100000)

# 函数 1: 多项式
f1 = x**3 - 1.5*x**2 + 0.5*x + 0.3*np.sin(10*x)
print(f"\nf(x) = x³ - 1.5x² + 0.5x + 0.3sin(10x) on [0,1]:")
print(f"  max = {f1.max():.6f} at x = {x[f1.argmax()]:.6f}")
print(f"  min = {f1.min():.6f} at x = {x[f1.argmin()]:.6f}")

# 对比: 非紧致集
print(f"\n对比: f(x) = 1/x on (0,1] (非紧致):")
print(f"  无最大值 (f(0.0001) = {1/0.0001:.0f} → ∞)")
print(f"  最小值 = 1 at x = 1 (碰巧闭端点)")

# ============================================================
# 实验 4: Taylor 展开 — sigmoid
# ============================================================
print("\n" + "=" * 70)
print("实验 4: Taylor 展开 — sigmoid(x) ≈ 1/2 + x/4 - x³/48 + x⁵/480")
print("=" * 70)

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

# Taylor 系数 at x=0: sigmoid(0)=1/2, σ'(0)=σ(1-σ)=1/4
# σ''(0) = σ'(1-2σ) = 1/4·(1-1) = 0
# σ'''(0) = σ'[(1-2σ)² - 2σ'] 需要计算
coeffs = {0: 0.5, 1: 0.25, 3: -1/48, 5: 1/480}

def taylor_sig(x, order):
    result = np.zeros_like(x, dtype=float)
    for k, c in coeffs.items():
        if k <= order:
            result += c * x**k
    return result

x_vals = np.array([0.01, 0.1, 0.5, 1.0, 2.0, 3.0])
print(f"\n{'x':>6} | {'sigmoid':>10} | {'Taylor(1)':>12} | {'Taylor(3)':>12} | {'Taylor(5)':>12}")
print("-" * 65)
for xv in x_vals:
    true = sigmoid(xv)
    t1 = taylor_sig(np.array([xv]), 1)[0]
    t3 = taylor_sig(np.array([xv]), 3)[0]
    t5 = taylor_sig(np.array([xv]), 5)[0]
    print(f"{xv:6.2f} | {true:10.6f} | {t1:10.6f}({abs(true-t1):.1e}) | {t3:10.6f}({abs(true-t3):.1e}) | {t5:10.6f}({abs(true-t5):.1e})")

# ============================================================
# 实验 5: 一致收敛 vs 逐点收敛
# ============================================================
print("\n" + "=" * 70)
print("实验 5: 一致收敛 vs 逐点收敛 — f_n(x) = x^n on [0,1]")
print("=" * 70)
print("逐点极限: f(x) = 0 for x<1, f(1) = 1")
print("一致收敛? 检查 sup|x^n - f(x)|:")
x = np.linspace(0, 1, 10000)
for n in [1, 5, 10, 50, 100]:
    fn = x**n
    f = (x >= 1).astype(float)
    sup_err = np.max(np.abs(fn - f))
    print(f"  n={n:3d}: sup|x^n - f| = {sup_err:.6f} {'→ 0 ✓' if sup_err < 0.01 else '↛ 0 ✗'}")
print("结论: 不一致收敛! (sup 误差不趋于 0)")
print("原因: 极限 f 不连续, 但 x^n 连续 → 矛盾")
print("ML 关联: 训练/验证 gap = 不一致收敛的体现")

# ============================================================
# 绘图
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# 子图 1: ε-δ 博弈
x = np.linspace(1.9, 2.1, 1000)
axes[0,0].plot(x, x**2, "b-", linewidth=2)
axes[0,0].axhline(y=4, color="k", linestyle="--", alpha=0.3)
axes[0,0].axvline(x=2, color="k", linestyle="--", alpha=0.3)
eps = 0.05
delta = eps / 5
axes[0,0].axvspan(2-delta, 2+delta, alpha=0.2, color="green", label=f"δ={delta:.3f}")
axes[0,0].axhspan(4-eps, 4+eps, alpha=0.1, color="red", label=f"ε={eps}")
axes[0,0].set_title("ε-δ: lim x² = 4")
axes[0,0].legend(fontsize=8)
axes[0,0].grid(alpha=0.3)

# 子图 2: Cauchy 序列收敛
ns = np.arange(1, 1001)
s1 = np.cumsum([1.0/(k*(k+1)) for k in range(1, 1001)])
axes[0,1].plot(ns, s1, "b-", linewidth=1)
axes[0,1].axhline(y=1, color="r", linestyle="--", label="limit = 1")
axes[0,1].set_title("Cauchy seq: Σ1/(k(k+1)) → 1")
axes[0,1].set_xlabel("n")
axes[0,1].legend()
axes[0,1].grid(alpha=0.3)

# 子图 3: 极值定理
x = np.linspace(0, 1, 10000)
f1 = x**3 - 1.5*x**2 + 0.5*x + 0.3*np.sin(10*x)
axes[0,2].plot(x, f1, "b-", linewidth=2)
axes[0,2].plot(x[f1.argmax()], f1.max(), "ro", markersize=10, label=f"max={f1.max():.3f}")
axes[0,2].plot(x[f1.argmin()], f1.min(), "go", markersize=10, label=f"min={f1.min():.3f}")
axes[0,2].set_title("Extreme Value Thm on [0,1]")
axes[0,2].legend()
axes[0,2].grid(alpha=0.3)

# 子图 4: Taylor 展开 sigmoid
x = np.linspace(-3, 3, 500)
axes[1,0].plot(x, sigmoid(x), "k-", linewidth=2, label="sigmoid")
axes[1,0].plot(x, taylor_sig(x, 1), "r--", label="Taylor(1)")
axes[1,0].plot(x, taylor_sig(x, 3), "g--", label="Taylor(3)")
axes[1,0].plot(x, taylor_sig(x, 5), "b--", label="Taylor(5)")
axes[1,0].set_title("Taylor expansion of sigmoid")
axes[1,0].legend(fontsize=8)
axes[1,0].grid(alpha=0.3)

# 子图 5: x^n 逐点 vs 一致收敛
x = np.linspace(0, 1, 500)
for n in [1, 2, 5, 10, 50]:
    axes[1,1].plot(x, x**n, label=f"n={n}")
axes[1,1].set_title("x^n: pointwise but NOT uniform")
axes[1,1].legend(fontsize=8)
axes[1,1].grid(alpha=0.3)

# 子图 6: 收敛速度对比
axes[1,2].set_title("Convergence speed comparison")
ns = np.arange(1, 100)
# s1 的收敛速度 ~ 1/n
err1 = np.abs(np.cumsum([1.0/(k*(k+1)) for k in range(1, 100)]) - 1)
# e 的收敛速度 ~ factorial
err2 = np.abs([(1+1/n)**n - np.e for n in ns])
axes[1,2].semilogy(ns, err1, "b-", label="Σ1/(k(k+1)) ~ O(1/n)")
axes[1,2].semilogy(ns, err2, "r-", label="(1+1/n)^n ~ O(1/n)")
axes[1,2].legend(fontsize=8)
axes[1,2].grid(alpha=0.3)

plt.suptitle("Princeton MAT 215: ε-δ and Analysis Demos", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
plt.close()

print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
print("\n=== 总结 ===")
print("1. ε-δ 极限: 'no matter how small ε, I can find δ'")
print("2. 完备性: Cauchy 列在 R 中一定收敛 (Q 中不行)")
print("3. 极值定理: 紧致集 + 连续 = 最值存在 (loss 最小值的理论保证)")
print("4. Taylor 展开: 用导数信息局部克隆函数 (优化的基础)")
print("5. 一致收敛 ≠ 逐点收敛: 泛化 gap 的数学本质")
