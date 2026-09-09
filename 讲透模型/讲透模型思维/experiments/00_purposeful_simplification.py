"""00_purposeful_simplification — 机理模型 vs 查表模型：简化丢的不是多，而是丢得对

问题：同一份带噪声的阻尼振荡数据，两个模型都能拟合——
  A. 机理模型：y = A*exp(-g*t)*cos(w*t+p)  （4 参数，来自"振荡+阻尼"结构假设）
  B. 查表模型：9 次多项式                    （10 参数，不做任何结构假设）
域内谁拟合得好？域外（外推）谁还活着？

结论：域内两者都贴着噪声底（点数不够时，查表模型连噪声都背不全）；外推立刻爆炸；
      机理模型丢掉"每个点的噪声"，留住"振荡+衰减"的结构——这就是有目的的简化：
      目的（外推预测）决定哪些信息该丢。
"""
import numpy as np

rng = np.random.default_rng(42)

# 真实过程：阻尼振荡（机理假设恰好为真；噪声 = 测量抖动）
t_train = np.linspace(0, 8, 33)            # 训练域 [0, 8]
t_test = np.linspace(8.25, 12, 16)         # 外推域 (8, 12]
A, g, w = 1.0, 0.3, 2.0

def truth(t):
    return A * np.exp(-g * t) * np.cos(w * t)

y_train = truth(t_train) + rng.normal(0, 0.05, t_train.size)
y_test = truth(t_test) + rng.normal(0, 0.05, t_test.size)

def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))

# ---- 模型 A：机理拟合（网格搜 g,w × 线性最小二乘解 A,p）----
best = None
for g_hat in np.arange(0.10, 0.51, 0.01):
    for w_hat in np.arange(1.5, 2.51, 0.01):
        e = np.exp(-g_hat * t_train)
        X = np.column_stack([e * np.cos(w_hat * t_train), e * np.sin(w_hat * t_train)])
        coef, *_ = np.linalg.lstsq(X, y_train, rcond=None)
        r = rmse(X @ coef, y_train)
        if best is None or r < best[0]:
            best = (r, g_hat, w_hat, coef)
_, g_hat, w_hat, coef = best

def mech_predict(t):
    e = np.exp(-g_hat * t)
    X = np.column_stack([e * np.cos(w_hat * t), e * np.sin(w_hat * t)])
    return X @ coef

# ---- 模型 B：9 次多项式（查表/现象模型）----
poly = np.polynomial.Polynomial.fit(t_train, y_train, deg=9)

print(f"[训练域 0-8]   拟合 RMSE：机理 = {rmse(mech_predict(t_train), y_train):.4f}   "
      f"多项式 = {rmse(poly(t_train), y_train):.4f}   <- 域内分不出高下")
print(f"[外推域 8-12]  预测 RMSE：机理 = {rmse(mech_predict(t_test), y_test):.4f}   "
      f"多项式 = {rmse(poly(t_test), y_test):.4f}   <- 外推见真章")
print(f"机理模型找回结构参数：g = {g_hat:.2f}（真值 0.3）  w = {w_hat:.2f}（真值 2.0）")
print("参数量：机理 4  vs  多项式 10 —— 参数少而结构对，胜过参数多而无结构")
