"""
实验 03 —— 正则化手段 zoo: 怎么把过拟合拉回泛化
对应文档: 04-架构归纳偏置与显式正则.md
核心结论: 岭回归(=L2权重衰减)把高阶多项式从过拟合(测试MSE=17.8)拉回泛化(0.038, 降470倍).
         λ太小=过拟合, λ太大=欠拟合, 中间最优(bias-variance权衡).
         深度网络的 weight decay/dropout/数据增强/early-stop 都是同一思想.
跑法: python3 03_regularization_zoo.py
"""
import numpy as np
rng = np.random.default_rng(7)

n_tr = 20
x_tr = np.sort(rng.uniform(0, 1, n_tr))
y_tr = np.sin(2 * np.pi * x_tr) + rng.normal(0, 0.3, n_tr)
x_te = np.linspace(0, 1, 100)
y_te = np.sin(2 * np.pi * x_te)

def poly(x, d):
    return np.vstack([x ** k for k in range(d + 1)]).T

def fit(d, lam):
    Ptr, Pte = poly(x_tr, d), poly(x_te, d)
    A = Ptr.T @ Ptr + lam * np.eye(d + 1)
    alpha = np.linalg.solve(A, Ptr.T @ y_tr)
    tr = np.mean((Ptr @ alpha - y_tr) ** 2)
    te = np.mean((Pte @ alpha - y_te) ** 2)
    return tr, te

print("=" * 66)
print("固定高阶 d=15 (过拟合), 扫描岭正则强度 λ")
print("岭回归 ≡ L2 权重衰减 (深度网络的 weight decay)")
print("=" * 66)
print(f"{'岭 λ':>12} {'训练MSE':>12} {'测试MSE':>12}  解读")
print("-" * 66)
best_te, best_lam = 1e9, 0
for lam in [0, 1e-10, 1e-6, 1e-3, 1e-1, 1, 100]:
    tr, te = fit(15, lam)
    if lam == 0: note = "无正则: 严重过拟合"
    elif te < 0.1: note = "<<< 正则化救场: 测试误差大降!"
    elif lam >= 10: note = "过强正则: 又欠拟合了 (bias 太大)"
    else: note = ""
    if te < best_te: best_te, best_lam = te, lam
    print(f"{lam:>12.0e} {tr:>12.4e} {te:>12.4e}  {note}")
print("-" * 66)
print(f"最优 λ={best_lam:.0e}, 测试MSE={best_te:.4f}")
print(f"相比无正则(17.8), 降了 {17.8/best_te:.0f} 倍!")
print()
print("深度网络对应手段 (同一思想):")
print("  岭回归 λ    <-> weight decay (L2) / L1")
print("  降阶 d      <-> 缩小网络/剪枝/架构选择")
print("  加噪声数据  <-> 数据增强")
print("  早停        <-> early stopping (在过拟合前停下)")
print("  随机丢弃    <-> dropout")
print("=> 正则化 = 人为缩小有效假设空间, 让模型倾向'平滑/简单'解 -> 泛化")
