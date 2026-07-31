"""
实验 01 —— 双层下降 (Double Descent): 过参数化反而泛化更好
对应文档: 03-双层下降.md
Belkin et al. 2019 里程碑现象. 高维随机特征模型稳定复现.
核心结论: 容量轴上测试误差是"双降"而非经典U型:
          欠拟合 -> 临界插值(峰值) -> 过参数化(测试误差反降!)
诚实注记: 1D 低维 + 纯插值数值上严重震荡(难复现); 高维随机特征 + 微正则更稳.
跑法: python3 01_double_descent.py
"""
import numpy as np
rng = np.random.default_rng(2024)

# 高维输入 d=20, 用 teacher(随机浅网络)生成标签
d = 20
n_tr, n_te = 60, 300
X_tr = rng.standard_normal((n_tr, d))
X_te = rng.standard_normal((n_te, d))

# teacher: 固定随机浅网络 -> 平滑真函数
W_t = rng.standard_normal((d, 80)) * 0.5
H_tr = np.maximum(X_tr @ W_t, 0); H_te = np.maximum(X_te @ W_t, 0)
w_out = rng.standard_normal(80) * 0.3
y_tr = H_tr @ w_out + rng.normal(0, 0.1, n_tr)   # 训练带微噪
y_te = H_te @ w_out                                # 测试无噪

def rff_features(X, N, gamma=0.5):
    """随机傅里叶特征 (近似高斯核)"""
    W = rng.standard_normal((d, N)) * np.sqrt(2 * gamma)
    b = rng.uniform(0, 2 * np.pi, N)
    return np.sqrt(2.0 / N) * np.cos(X @ W + b)

def fit_eval(N, lam=1e-8):
    Phi_tr = rff_features(X_tr, N)      # (n_tr, N)
    Phi_te = rff_features(X_te, N)
    A = Phi_tr.T @ Phi_tr + lam * np.eye(N)
    alpha = np.linalg.solve(A, Phi_tr.T @ y_tr)
    tr = np.mean((Phi_tr @ alpha - y_tr) ** 2)
    te = np.mean((Phi_te @ alpha - y_te) ** 2)
    return tr, te

print("=" * 70)
print(f"双层下降: 高维随机傅里叶特征, 扫描特征数 N (训练样本 n={n_tr}, d={d})")
print("=" * 70)
print(f"{'特征数N':>9} {'参数比 N/n':>11} {'训练MSE':>12} {'测试MSE':>12}  区域")
print("-" * 70)
widths = [5, 15, 30, 50, 58, 60, 62, 70, 100, 200, 500, 1000, 3000]
peak_te, peak_N = 0, 0
results = []
for N in widths:
    tr, te = fit_eval(N)
    results.append((N, tr, te))
    if te > peak_te: peak_te, peak_N = te, N
    if N < n_tr: zone = "欠参数(欠拟合)"
    elif abs(N - n_tr) <= 5: zone = "★临界插值(N≈n, 峰值区)"
    elif N < 4 * n_tr: zone = "记号态(过拟合最惨)"
    else: zone = "过参数区(N>>n, 反而降!)"
    print(f"{N:>9} {N/n_tr:>11.2f} {tr:>12.4e} {te:>12.4e}  {zone}")

print("-" * 70)
over = [(N, te) for N, _, te in results if N >= 5 * n_tr]
if over:
    best_over = min(over, key=lambda r: r[1])
    print(f"\n★ 测试误差峰值: N={peak_N} (MSE={peak_te:.3f})")
    print(f"★ 过参数区最佳: N={best_over[0]} (MSE={best_over[1]:.3f}, 参数是样本的 {best_over[0]//n_tr}倍)")
    if best_over[1] < peak_te:
        print(f"  -> 参数从 {peak_N} 涨到 {best_over[0]}, 测试误差反降 {peak_te/best_over[1]:.1f} 倍!")
        print("  => 这就是双层下降: 过了临界点, 更多参数让'最小范数插值解'更平滑 -> 泛化更好")
    else:
        print(f"  -> 过参数区未明显优于峰值(数值/设定敏感). 双层下降是经验现象, 非普适定理.")
print("\n诚实注记: 1D 低维 + 纯插值(λ=0)会数值爆炸(我已试过). 高维+微正则(λ=1e-8)才稳.")
print("          这本身说明双层下降对设定敏感——它是经验规律, 不是对所有情况成立的定理.")
