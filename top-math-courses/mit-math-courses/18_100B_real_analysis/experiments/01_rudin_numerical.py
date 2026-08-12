"""
MIT 18.100B · 实验01: Rudin 实分析的数值验证
依赖: numpy, matplotlib
运行: python3 01_rudin_numerical.py

验证:
  1. 完备性: Cauchy 序列在 R 中收敛
  2. 紧致集上连续函数取最值 (Weierstrass 极值定理)
  3. Taylor 展开的收敛速度
  4. Stone-Weierstrass 定理: 多项式逼近连续函数 (Bernstein 多项式)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ============================================================
# 实验 1: Cauchy 序列收敛
# ============================================================
print("=" * 60)
print("实验 1: Cauchy 序列在 R 中收敛")
print("=" * 60)

# 构造 Cauchy 序列: s_n = sum_{k=1}^n 1/(k(k+1))
# 这个序列收敛到 1 (telescoping series)
def cauchy_seq(n):
    k = np.arange(1, n+1)
    return np.cumsum(1.0 / (k * (k + 1)))

N = 1000
s = cauchy_seq(N)
print(f"序列 s_1000 = {s[-1]:.10f} (真值=1)")
print(f"|s_1000 - 1| = {abs(s[-1] - 1):.2e}")

# 验证 Cauchy 性质: |s_n - s_m| -> 0
for gap in [100, 50, 10, 1]:
    diffs = np.abs(s[gap:] - s[:-gap])
    print(f"  |s_n - s_{{n-{gap}}}| max = {diffs.max():.2e}")

# ============================================================
# 实验 2: 紧致集上连续函数取最值
# ============================================================
print("\n" + "=" * 60)
print("实验 2: 紧致集 [0,1] 上连续函数取最值")
print("=" * 60)

# f(x) = sin(5x) * exp(-x) 在 [0,1] 上
x = np.linspace(0, 1, 10000)
f = np.sin(5 * x) * np.exp(-x)

max_idx = f.argmax()
min_idx = f.argmin()
print(f"f 在 [0,1] 上的最大值 = {f[max_idx]:.6f} (x={x[max_idx]:.4f})")
print(f"f 在 [0,1] 上的最小值 = {f[min_idx]:.6f} (x={x[min_idx]:.4f})")
print(f"结论: 连续 + 紧致 → 最值存在 ✓")

# 对比: 非紧致集 (0,1) 上 f(x) = 1/x 无最大值
print("\n对比: f(x)=1/x 在 (0,1) 上无最大值（非紧致）")
print(f"  f(0.001) = {1/0.001:.1f}, f(0.0001) = {1/0.0001:.1f} → 趋向无穷")

# ============================================================
# 实验 3: Taylor 展开收敛速度
# ============================================================
print("\n" + "=" * 60)
print("实验 3: Taylor 展开收敛速度 (e^x 在 x=1)")
print("=" * 60)

x0 = 1.0
true_val = np.exp(x0)
print(f"真值 e^1 = {true_val:.10f}\n")

for n in range(1, 21):
    taylor = sum(x0**k / np.math.factorial(k) for k in range(n+1))
    error = abs(taylor - true_val)
    remainder_bound = np.exp(x0) * x0**(n+1) / np.math.factorial(n+1)  # Taylor 余项上界
    print(f"  n={n:2d}: Taylor = {taylor:.10f}, 误差 = {error:.2e}, "
          f"余项上界 = {remainder_bound:.2e}")

# ============================================================
# 实验 4: Stone-Weierstrass 定理 (Bernstein 多项式逼近)
# ============================================================
print("\n" + "=" * 60)
print("实验 4: Stone-Weierstrass 定理 (Bernstein 多项式)")
print("=" * 60)

# 目标函数: f(x) = |x - 0.5| (连续但不可微)
def target_f(x):
    return np.abs(x - 0.5)

def bernstein(f, n, x):
    """n 阶 Bernstein 多项式逼近 f 在 x 处的值"""
    from math import comb
    k = np.arange(n + 1)
    return sum(f(ki / n) * comb(n, ki) * x**ki * (1 - x)**(n - ki) 
               for ki, k_val in enumerate(k))

x_fine = np.linspace(0, 1, 500)
f_true = target_f(x_fine)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 左图: 不同 n 的 Bernstein 逼近
axes[0].plot(x_fine, f_true, "k-", linewidth=2, label="$f(x) = |x - 0.5|$")
for n in [5, 10, 20, 50]:
    approx = np.array([bernstein(target_f, n, xi) for xi in x_fine])
    error = np.max(np.abs(approx - f_true))
    axes[0].plot(x_fine, approx, "--", label=f"Bernstein n={n} (误差={error:.4f})")
    print(f"  Bernstein n={n:2d}: 一致逼近误差 = {error:.6f}")

axes[0].set_xlabel("x")
axes[0].set_ylabel("y")
axes[0].set_title("Stone-Weierstrass: 多项式逼近连续函数")
axes[0].legend()
axes[0].grid(alpha=0.3)

# 右图: 误差随 n 衰减
ns = [5, 10, 20, 50, 100, 200]
errors = []
for n in ns:
    approx = np.array([bernstein(target_f, n, xi) for xi in x_fine])
    errors.append(np.max(np.abs(approx - f_true)))

axes[1].semilogy(ns, errors, "ro-", linewidth=2)
axes[1].set_xlabel("Bernstein 多项式阶数 n")
axes[1].set_ylabel("一致逼近误差 (log)")
axes[1].set_title(f"误差衰减率 ~ $O(1/\\sqrt{{n}})$")
axes[1].grid(alpha=0.3)

# 参考线 O(1/sqrt(n))
ref = 0.5 / np.sqrt(np.array(ns))
axes[1].semilogy(ns, ref, "b--", alpha=0.5, label="$0.5/\\sqrt{n}$")
axes[1].legend()

plt.tight_layout()
plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
print(f"\n图表已保存: {__file__.replace('.py', '.png')}")
print("\n结论: 多项式可以一致逼近任何连续函数 (Stone-Weierstrass 定理)")
print("ML 关联: 这就是 Universal Approximation Theorem 的数学根源")
