"""
实验 02 —— 隐式正则: 优化器本身就在正则 (无需任何显式约束)
对应文档: 01-隐式正则.md
设计: 归一化特征空间 (每列除以自身范数), 让闭式与GD同尺度、同数值稳定, 公平对比.
核心结论:
  1. 闭式最小二乘(λ=0) = 全局解, 一步到位 -> 过拟合 (测试MSE高)
  2. 梯度下降(GD)渐进优化, 早期测试MSE低(隐式正则), 后期才趋近闭式过拟合解
  3. => 训练过程本身就是正则: 早停 + 优化器偏好 = 免费正则化
  注: 归一化空间下 Pte_n@w 直接等于原始尺度预测, 故测试MSE与实验00/03同尺度可比.
跑法: python3 02_implicit_regularization.py
"""
import numpy as np
rng = np.random.default_rng(7)

n_tr = 20
x_tr = np.sort(rng.uniform(0, 1, n_tr))
y_tr = np.sin(2 * np.pi * x_tr) + rng.normal(0, 0.3, n_tr)
x_te = np.linspace(0, 1, 100)
y_te = np.sin(2 * np.pi * x_te)

D = 9    # 用 d=9 (条件数远低于d=15, 闭式数值稳定; 实验00 证其稳定过拟合, 测试MSE≈6)
def poly(x): return np.vstack([x ** k for k in range(D + 1)]).T
Ptr_raw, Pte_raw = poly(x_tr), poly(x_te)
# 归一化每列 (进一步改善条件数, 与实验00/03 同 y 尺度)
col_norm = np.linalg.norm(Ptr_raw, axis=0)
col_norm = np.where(col_norm < 1e-12, 1.0, col_norm)
Ptr = Ptr_raw / col_norm
Pte = Pte_raw / col_norm     # 归一化空间下 Pte@w = 原始尺度预测

def tr_mse(w): return np.mean((Ptr @ w - y_tr) ** 2)
def te_mse(w): return np.mean((Pte @ w - y_te) ** 2)

# 闭式最小二乘 (λ=0) = 全局解 (归一化后数值稳定)
w_closed, *_ = np.linalg.lstsq(Ptr, y_tr, rcond=None)
closed_te = te_mse(w_closed)

print("=" * 66)
print("隐式正则: 过参数多项式 d=9 (归一化特征, 与实验00/03 同 y 尺度)")
print("=" * 66)
print(f"闭式最小二乘(λ=0): 训练MSE={tr_mse(w_closed):.2e}  测试MSE={closed_te:.4f}")
print(f"  -> 一步到位的全局解, 高阶项全用上 -> 过拟合 (实验00 同设定给≈6)\n")

# GD 从 w=0 训练, 跟踪测试MSE
w = np.zeros(D + 1)
lr = 0.3
print("梯度下降(GD)从零初始化, 跟踪测试MSE随步数:")
print(f"{'步数':>8} {'训练MSE':>12} {'测试MSE':>12}  解读")
print("-" * 66)
checkpoints = {50, 200, 1000, 5000, 20000, 80000}
best_te, best_step = 1e9, 0
for step in range(1, 80001):
    grad = Ptr.T @ (Ptr @ w - y_tr) / n_tr
    w -= lr * grad
    if step in checkpoints:
        tm, em = tr_mse(w), te_mse(w)
        if em < best_te: best_te, best_step = em, step
        if step <= 1000: note = "早期: 隐式正则(高阶还没学) -> 泛化好"
        elif em < closed_te * 0.3: note = "中期: 接近最优泛化"
        else: note = "后期: 高阶学上 -> 趋近过拟合闭式解"
        print(f"{step:>8} {tm:>12.4e} {em:>12.4f}  {note}")
print("-" * 66)
print(f"\n★ GD 最优: 步数={best_step}, 测试MSE={best_te:.4f}")
print(f"  vs 闭式(λ=0) 测试MSE={closed_te:.4f}: GD 隐式正则降了 {closed_te/max(best_te,1e-9):.1f} 倍!")
print(f"  vs 实验03 最优岭正则(λ=1e-6, MSE=0.038): GD 无需手调λ 即达相近泛化!")
print()
print("核心洞察 (为何深度网络'裸奔'也能泛化):")
print("  - 过参数模型有无数解能拟合训练数据")
print("  - GD 不随机挑解: 训练早期停在'简单解', 高阶/复杂成分学得慢")
print("  - 所以 GD 轨迹 + 早停 = 免费、自动的正则化")
print("  - SGD/Adam 在深度学习里既是优化器又是正则器 (双重身份)")
print("  - 这就是没有 weight decay 的大网络也能泛化的根本原因之一")
