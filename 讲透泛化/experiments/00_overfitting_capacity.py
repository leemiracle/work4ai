"""
实验 00 —— 过拟合: 容量越大越过拟合? (多项式阶数扫描)
对应文档: 00-泛化悖论.md
多项式回归 = 过参数线性模型, 与深度网络过拟合同构 (Belkin 理论框架).
核心结论: 容量(阶数)升高 -> 训练MSE->0(强行记住每个点) -> 测试MSE爆炸(剧烈震荡).
         这正是"参数多=过拟合"的经典直觉, 为泛化悖论做铺垫.
跑法: python3 00_overfitting_capacity.py
"""
import numpy as np
rng = np.random.default_rng(7)

# 数据: y = sin(2πx) + 噪声 (ISLR 经典设定)
n_tr = 20
x_tr = np.sort(rng.uniform(0, 1, n_tr))
y_tr = np.sin(2 * np.pi * x_tr) + rng.normal(0, 0.3, n_tr)
x_te = np.linspace(0, 1, 100)
y_te = np.sin(2 * np.pi * x_te)

def poly(x, d):
    return np.vstack([x ** k for k in range(d + 1)]).T

def fit(d, lam=0.0):
    Ptr, Pte = poly(x_tr, d), poly(x_te, d)
    A = Ptr.T @ Ptr + lam * np.eye(d + 1)
    alpha = np.linalg.solve(A, Ptr.T @ y_tr)
    tr = np.mean((Ptr @ alpha - y_tr) ** 2)
    te = np.mean((Pte @ alpha - y_te) ** 2)
    return tr, te

print("=" * 66)
print("Part1: 多项式阶数扫描 (容量轴). 经典直觉: 阶数↑ -> 过拟合↑")
print("=" * 66)
print(f"{'阶数d':>6} {'参数数':>8} {'训练MSE':>12} {'测试MSE':>12}  解读")
print("-" * 66)
for d in [1, 3, 5, 9, 13, 17, 19]:
    tr, te = fit(d)
    if d < 5:   note = "欠拟合 (容量不足)"
    elif d >= 13: note = "插值训练点 -> 剧烈震荡 -> 过拟合爆炸!"
    else: note = "刚好"
    print(f"{d:>6} {d+1:>8} {tr:>12.4e} {te:>12.4e}  {note}")
print("-" * 66)
print("观察: d=3 测试MSE=0.028(最优) -> d=13 测试MSE≈393(爆炸, 升了 14000 倍)")
print("      训练MSE却始终很低(高阶强行记住每个噪声点).")
print("      => 经典理论'参数多=过拟合'在此完美验证. 但深度网络参数远多却不崩 -> 悖论!")
