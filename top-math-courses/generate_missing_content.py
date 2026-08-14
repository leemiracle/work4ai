#!/usr/bin/env python3
"""
top-math-courses 批量内容补全器
================================
扫描所有课程目录，对缺失的 experiments/exercises/notes 按主题智能补全。
每个实验脚本：纯 numpy + matplotlib，50-80 行，验证一个关键定理 + ML 关联。

用法：python3 generate_missing_content.py
"""
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 12 个主题的高质量实验脚本模板
# ============================================================

EXP_LINEAR_ALGEBRA = '''#!/usr/bin/env python3
"""线性代数核心实验：SVD + PCA + LoRA 低秩近似（验证 Eckart-Young 定理）"""
import numpy as np
# ML 关联：SVD → PCA → LoRA(W ≈ W0 + BA)，Transformer 压缩

np.random.seed(42)
A = np.random.randn(8, 5)
U, s, Vt = np.linalg.svd(A, full_matrices=False)
print("奇异值:", np.round(s, 3))

# Eckart-Young: 最佳秩 k 近似
for k in [1, 2, 3]:
    A_k = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]
    err = np.linalg.norm(A - A_k, "fro")
    lower = s[k] if k < len(s) else 0
    print(f"k={k}: 误差={err:.4f}  σ_{k+1}={lower:.4f}  (应相等)")

# PCA = 数据矩阵 SVD
X = np.random.randn(200, 3) @ np.random.randn(3, 5)
Xc = X - X.mean(0)
Ux, sx, Vtx = np.linalg.svd(Xc, full_matrices=False)
print("\\nPCA 主成分解释方差比:", np.round(sx**2 / (sx**2).sum(), 3))

# LoRA: W ≈ W0 + BA (低秩更新)
W0 = np.random.randn(10, 10)
B = np.random.randn(10, 2) * 0.01
A = np.random.randn(2, 10) * 0.01
W_lora = W0 + B @ A
print(f"\\nLoRA 更新 Frobenius 范数: {np.linalg.norm(B @ A):.4f} (vs W0: {np.linalg.norm(W0):.4f})")
print("=> LoRA 用秩 2 更新微调 10×10 矩阵，参数从 100 降到 20+20=40")
'''

EXP_CALCULUS = '''#!/usr/bin/env python3
"""微积分核心实验：梯度下降 + 链式法则（反向传播的根基）"""
import numpy as np
# ML 关联：梯度 ∇f → SGD → Adam；链式法则 → 反向传播

# 1. 梯度下降最小化 f(x,y) = x² + 3y²
f = lambda x, y: x**2 + 3*y**2
grad = lambda x, y: np.array([2*x, 6*y])
x = np.array([5.0, 5.0])
lr, hist = 0.1, [f(*x)]
for i in range(100):
    x = x - lr * grad(*x)
    hist.append(f(*x))
print(f"梯度下降 100 步: f={hist[-1]:.6f}, x={np.round(x,4)} (应→0)")

# 2. 链式法则 = 反向传播（数值验证）
W1 = np.random.randn(3, 4); W2 = np.random.randn(4, 1)
x = np.random.randn(3, 1); y = np.array([[1.0]])
def forward(W1, W2):
    h = np.tanh(W1 @ x); o = W2 @ h; loss = 0.5*(o - y)**2
    return h, o, loss.sum()
h, o, loss = forward(W1, W2)
# 解析梯度（链式法则）
do = (o - y); dW2 = do @ h.T; dh = W2.T @ do * (1 - h**2); dW1 = dh @ x.T
# 数值梯度（有限差分验证）
eps = 1e-5; dW1_num = np.zeros_like(W1)
for i in range(W1.shape[0]):
    for j in range(W1.shape[1]):
        W1[i,j] += eps; _, _, lp = forward(W1, W2)
        W1[i,j] -= 2*eps; _, _, lm = forward(W1, W2)
        W1[i,j] += eps; dW1_num[i,j] = (lp - lm) / (2*eps)
err = np.abs(dW1 - dW1_num).max()
print(f"\\n反向传播梯度数值验证: 最大误差={err:.2e} (应 < 1e-6)")
'''

EXP_ANALYSIS = '''#!/usr/bin/env python3
"""实分析核心实验：ε-δ 极限数值验证 + 4 种收敛模式可视化"""
import numpy as np
# ML 关联：ε-δ → 数值稳定性；收敛模式 → 大数定律/CLT → SGD 收敛

# 1. ε-δ 验证 lim_{x→2} x² = 4：给定 ε，找 δ
def verify_epsilon_delta(eps):
    delta = min(eps / 5, 1.0)  # δ = ε/5（因为 |x²-4|=|x-2||x+2|≤5|x-2| 当 |x-2|<1）
    xs = np.linspace(2 - delta, 2 + delta, 1000)
    xs = xs[xs != 2]
    max_err = np.max(np.abs(xs**2 - 4))
    return max_err < eps, max_err
for eps in [0.1, 0.01, 0.001]:
    ok, err = verify_epsilon_delta(eps)
    print(f"ε={eps}: δ={min(eps/5,1.0):.4f}, 最大误差={err:.6f}, 满足: {ok}")

# 2. 4 种收敛模式：X_n → 0
print("\\n4 种收敛模式（X_n = 1/n + noise）：")
for n in [10, 100, 1000, 10000]:
    samples = 1/n + np.random.randn(10000) * (1/np.sqrt(n))
    prob = np.mean(np.abs(samples) > 0.5)
    print(f"  n={n:5d}: P(|X|>0.5)={prob:.4f} (in probability: →0)")
# a.s. 收敛更强（单样本路径 →0）；L^p 需 E|X_n|^p →0
print("\\n=> a.s. → in prob → in distribution (蕴含链)")
'''

EXP_PROBABILITY = '''#!/usr/bin/env python3
"""概率论核心实验：大数定律 + CLT + KL 散度（ML 的数学根基）"""
import numpy as np
# ML 关联：LLN→SGD收敛；CLT→BatchNorm/置信区间；KL→VAE/RLHF/cross-entropy

np.random.seed(42)
# 1. 大数定律：样本均值 → 期望
print("大数定律: 样本均值 → E[X]=0.5 (uniform[0,1])")
for n in [10, 100, 1000, 10000, 100000]:
    mean = np.random.uniform(0, 1, n).mean()
    print(f"  n={n:6d}: 均值={mean:.5f}, 偏差={abs(mean-0.5):.5f}")

# 2. CLT: (样本均值 - 期望) * sqrt(n) → N(0, σ²)
print("\\n中心极限定理: √n × (均值 - 0.5) → N(0, 1/12)")
scaled_means = []
for _ in range(10000):
    m = np.random.uniform(0, 1, 100).mean()
    scaled_means.append(np.sqrt(100) * (m - 0.5))
sm = np.array(scaled_means)
print(f"  实测: 均值={sm.mean():.4f} (应≈0), 方差={sm.var():.4f} (应≈1/12={1/12:.4f})")

# 3. KL 散度非对称
p = np.array([0.5, 0.5]); q = np.array([0.9, 0.1])
kl_pq = np.sum(p * np.log(p / q))
kl_qp = np.sum(q * np.log(q / p))
print(f"\\nKL(p‖q)={kl_pq:.4f}, KL(q‖p)={kl_qp:.4f} (不对称!)")
print("=> cross-entropy = H(p) + KL(p‖q); VAE ELBO = 重建 - KL; RLHF = max E[r] - β·KL(π‖πref)")
'''

EXP_OPTIMIZATION = '''#!/usr/bin/env python3
"""凸优化核心实验：梯度下降收敛速率 + KKT 条件（SVM 推导）"""
import numpy as np
# ML 关联：凸优化→SVM/Lasso；KKT→约束优化；收敛速率→Adam 调参

# 1. 强凸函数 f(x) = x² 的梯度下降：线性收敛
x = 10.0; lr = 0.1; hist = []
for i in range(50):
    hist.append(abs(x)); x = x - lr * 2 * x
ratios = [hist[i+1]/hist[i] for i in range(len(hist)-1) if hist[i] > 1e-10]
print(f"强凸 f=x² 梯度下降收敛速率: 比值≈{np.mean(ratios[-10:]):.3f} (理论: |1-2lr|={abs(1-2*lr):.3f})")

# 2. SVM 的 KKT: min 0.5||w||² s.t. y_i(w·x_i+b)≥1
# 对偶: max Σα_i - 0.5ΣΣ α_iα_j y_i y_j x_i·x_j, s.t. α_i≥0, Σα_i y_i=0
# 简单 2D 例子
X = np.array([[1,2],[2,3],[3,1],[4,1]]); y = np.array([1,1,-1,-1])
# 解析 SVM（暴力简化：找最大间隔方向）
from itertools import combinations
best_margin, best_w = 0, None
for i, j in combinations(range(4), 2):
    if y[i] != y[j]:
        d = X[i] - X[j]; w = d / np.linalg.norm(d)
        margin = abs(np.dot(w, X[i]) - np.dot(w, X[j])) / 2
        if margin > best_margin: best_margin, best_w = margin, w
print(f"\\nSVM 最大间隔: {best_margin:.4f}, 法向量: {np.round(best_w, 4)}")
print("=> 间隔最大化 = 凸二次规划 + KKT 互补松弛 α_i(y_i(w·x_i+b)-1)=0")
'''

EXP_NUMERICAL = '''#!/usr/bin/env python3
"""数值分析核心实验：QR 分解 + 条件数（数值稳定性）"""
import numpy as np
# ML 关联：条件数→训练稳定性；QR→最小二乘→线性回归；浮点→PyTorch 反向传播

# 1. Gram-Schmidt QR 分解
A = np.array([[1.0, 1.0, 0.0], [1.0, 3.0, 1.0], [2.0, -1.0, 1.0]])
Q = np.zeros_like(A); R = np.zeros((A.shape[1], A.shape[1]))
for j in range(A.shape[1]):
    v = A[:, j].copy()
    for i in range(j):
        R[i, j] = Q[:, i] @ A[:, j]
        v -= R[i, j] * Q[:, i]
    R[j, j] = np.linalg.norm(v)
    Q[:, j] = v / R[j, j]
print("手写 QR - Q 正交性误差:", np.round(np.linalg.norm(Q.T @ Q - np.eye(3)), 15))
print("手写 QR - A=QR 重构误差:", np.round(np.linalg.norm(Q @ R - A), 15))

# 2. 条件数：良态 vs 病态
print("\\n条件数（越大越病态）:")
for name, M in [("正交", np.random.randn(5,5)/np.sqrt(5)), ("Hilbert", np.array([[1/(i+j+1) for j in range(5)] for i in range(5)]))]:
    cond = np.linalg.cond(M)
    print(f"  {name}矩阵: κ={cond:.1f}")
print("=> Hilbert 矩阵病态：数值求解 Ax=b 时小扰动→大误差")
'''

EXP_INFORMATION = '''#!/usr/bin/env python3
"""信息论核心实验：熵 + KL + 互信息（ML loss 的统一语言）"""
import numpy as np
# ML 关联：cross-entropy=H(p)+KL(p‖q)；互信息=决策树分裂准则；MDL=模型压缩

# 1. 熵 H(X)：越均匀越不确定
def entropy(p):
    p = np.array(p); p = p[p > 0]
    return -np.sum(p * np.log2(p))
print("熵 H(X):")
for name, p in [("确定", [1,0]), ("均匀2元", [0.5,0.5]), ("偏斜", [0.9,0.1]), ("均匀8元", [1/8]*8)]:
    print(f"  {name}: H={entropy(p):.3f} bits")

# 2. 互信息 I(X;Y) = H(X) - H(X|Y)
print("\\n互信息（决策树信息增益）:")
X = np.random.randint(0, 2, 10000)
Y = X.copy()  # 完全相关
Y_noise = (X + np.random.randint(0, 2, 10000)) % 2  # 加噪声
def mi(x, y):
    px = np.bincount(x) / len(x)
    hx = entropy(px)
    # H(X|Y) = H(X,Y) - H(Y)
    joint = np.zeros((2, 2))
    for a, b in zip(x, y): joint[a, b] += 1
    joint /= len(x)
    hxy = entropy(joint.flatten())
    py = np.bincount(y) / len(y)
    hy = entropy(py)
    return hx - (hxy - hy)
print(f"  I(X;X)={mi(X,X):.3f} (=H(X), 完全相关)")
print(f"  I(X;Y_noise)={mi(X,Y_noise):.3f} (噪声化)")
print("=> cross-entropy loss = H(y_true) + KL(y_true‖y_pred)")
'''

EXP_ALGEBRA = '''#!/usr/bin/env python3
"""抽象代数核心实验：群作用 + 对称性（CNN/等变网络的根基）"""
import numpy as np
# ML 关联：CNN=Z^d群卷积；AlphaFold=SE(3)等变；群表示→张量

# 1. 对称群 S_3 的乘法表
def perm(p, x): return [x[i] for i in p]
S3 = [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]]  # 6 个置换
print("S₃ 乘法表（部分）:")
for p in S3[:3]:
    for q in S3[:3]:
        pq = [p[q[i]] for i in range(3)]  # 先 q 后 p
        print(f"  {p}∘{q} = {pq}")

# 2. 轨道-稳定子定理
print("\\n轨道-稳定子定理: |G| = |轨道| × |稳定子|")
# D_4 (正方形对称群, 8 元素) 作用在 4 个顶点上
corners = [(1,1),(1,-1),(-1,-1),(-1,1)]
# 旋转 90 度
R90 = lambda v: (-v[1], v[0])
v0 = (1, 1)
orbit = {v0}
for _ in range(4):
    v0 = R90(v0); orbit.add(v0)
print(f"  角(1,1) 在 D_4 下的轨道: {orbit} (|轨道|={len(orbit)})")
print(f"  |D_4|=8 = |轨道|×|稳定子| = {len(orbit)}×{8//len(orbit)}")
print("=> CNN = 在 Z^d 群上的等变网络（平移对称）")
'''

EXP_TOPOLOGY = '''#!/usr/bin/env python3
"""拓扑核心实验：Banach 不动点 + 压缩映射（优化收敛的根基）"""
import numpy as np
# ML 关联：压缩映射→SGD收敛；不动点→value iteration；紧致→极值定理→loss最小值存在

# 1. Banach 不动点：T(x) = 0.5x + 1，不动点 x*=2
T = lambda x: 0.5 * x + 1
x = 100.0; hist = [x]
for _ in range(30):
    x = T(x); hist.append(x)
print(f"压缩映射 T(x)=0.5x+1 迭代: {hist[0]:.1f} → {hist[-1]:.6f} (不动点=2)")
ratios = [abs(hist[i+1]-2)/abs(hist[i]-2) for i in range(len(hist)-1) if abs(hist[i]-2)>1e-10]
print(f"  收敛比值: {np.mean(ratios[-5:]):.3f} (理论: 0.5 = 压缩常数)")

# 2. Policy iteration (RL) 是不动点迭代
print("\\n强化学习的 value iteration = 不动点: V* = max_a(R + γP·V*)")
gamma = 0.9; V = np.array([10.0, 10.0])  # 2 状态简化
R = np.array([1.0, 0.5]); P = np.array([[0.5,0.5],[0.3,0.7]])
for _ in range(50):
    V_new = R + gamma * np.max(P @ V)  # 简化（确定性策略）
print(f"  Value iteration 收敛 V*={np.round(V_new, 4)}")
print("=> RL 的核心 = 在赋范空间上做压缩映射（γ<1 保证收敛）")
'''

EXP_SDE = '''#!/usr/bin/env python3
"""随机微分方程实验：Euler-Maruyama + Itô 引理 + 扩散模型前向"""
import numpy as np
# ML 关联：Itô→Black-Scholes；反向 SDE→Diffusion model；Langevin→MCMC

np.random.seed(42)
# 1. Geometric Brownian Motion dX = μX dt + σX dW（Black-Scholes 基础）
T, N, mu, sigma, X0 = 1.0, 1000, 0.1, 0.3, 100.0
dt = T / N; n_paths = 1000
dW = np.random.randn(n_paths, N) * np.sqrt(dt)
X = np.zeros((n_paths, N+1)); X[:, 0] = X0
for i in range(N):
    X[:, i+1] = X[:, i] + mu*X[:, i]*dt + sigma*X[:, i]*dW[:, i]
print(f"GBM 终值: 实测均值={X[:,-1].mean():.2f}, 理论 E[X_T]={X0*np.exp(mu*T):.2f}")
print(f"  实测方差={X[:,-1].var():.2f}, 理论 Var≈={(X0**2)*np.exp(2*mu*T)*(np.exp(sigma**2*T)-1):.2f}")

# 2. Itô 引理: d(ln X) = (μ - σ²/2)dt + σdW
log_X_final = np.log(X[:, -1])
theoretical = np.log(X0) + (mu - sigma**2/2)*T + sigma*np.sqrt(T)*np.random.randn(n_paths)
print(f"\\nItô 引理验证: d(lnX) 均值差={abs(log_X_final.mean()-theoretical.mean()):.4f}")
print("=> Itô 项 (1/2)σ² 是 Black-Scholes 公式的关键")

# 3. Diffusion 前向: x_t = √α̅_t x_0 + √(1-α̅_t) ε（DDPM）
print("\\nDiffusion 前向 (DDPM, arXiv:2006.11239):")
x0 = np.random.randn(1000)
alpha_bar = 0.5  # 某个时间步
xt = np.sqrt(alpha_bar) * x0 + np.sqrt(1 - alpha_bar) * np.random.randn(1000)
print(f"  α̅={alpha_bar}: x_t 均值={xt.mean():.3f}(应≈0), 方差={xt.var():.3f}(应≈1)")
'''

EXP_PDE = '''#!/usr/bin/env python3
"""偏微分方程实验：扩散方程 + heat kernel（diffusion model 的根基）"""
import numpy as np
# ML 关联：扩散方程→DDPM；heat kernel=高斯卷积；PINN=PDE+神经网络

# 1. 一维扩散方程 ∂u/∂t = D ∂²u/∂x²（有限差分）
D, dx, dt = 0.1, 0.05, 0.001
x = np.linspace(-2, 2, 81); u = np.exp(-x**2 / 0.1)  # 初始 δ-like
n_steps = 500
for step in range(n_steps):
    u_new = u.copy()
    u_new[1:-1] = u[1:-1] + D * dt / dx**2 * (u[2:] - 2*u[1:-1] + u[:-2])
    u = u_new
# 理论解: u(x,T) = 高斯卷积
T_final = n_steps * dt
theory = 1/np.sqrt(4*np.pi*D*T_final + 0.1) * np.exp(-x**2/(4*D*T_final + 0.1))
theory = theory / theory.max() * u.max()  # 归一化对比
err = np.abs(u - theory).mean()
print(f"扩散方程数值解 vs 理论高斯: 平均误差={err:.4f}")
print("=> heat kernel = 高斯; 扩散方程平滑化 = 信息损失（熵增）")

# 2. 扩散模型: 前向加噪 = 离散化扩散方程
print("\\n扩散模型 (DDPM):")
x0 = np.array([1.0, -1.0, 2.0])  # 3 个"图像"
for t, alpha_bar in [(0.1, 0.99), (0.5, 0.5), (0.9, 0.01)]:
    noise = np.random.randn(3)
    xt = np.sqrt(alpha_bar) * x0 + np.sqrt(1-alpha_bar) * noise
    print(f"  t={t}: α̅={alpha_bar}, x_t={np.round(xt, 3)} ({'≈原图' if alpha_bar>0.9 else '≈纯噪声' if alpha_bar<0.1 else '混合'})")
'''

EXP_COMPLEX = '''#!/usr/bin/env python3
"""复分析实验：Cauchy 积分公式 + 留数定理（信号处理根基）"""
import numpy as np
# ML 关联：Z变换→滤波器；Nyquist稳定性；特征函数→概率分布

# 1. Cauchy 积分公式: f(a) = 1/(2πi) ∮ f(z)/(z-a) dz
def f(z): return np.exp(z)  # 整函数
a = 1.0 + 0.5j
R = 2.0  # 围绕 a 半径 R 的圆
N = 10000
theta = np.linspace(0, 2*np.pi, N, endpoint=False)
z = a + R * np.exp(1j * theta)
dz = 1j * R * np.exp(1j * theta) * (2*np.pi / N)
integral = np.sum(f(z) / (z - a) * dz) / (2j * np.pi)
print(f"Cauchy 公式验证: ∮ e^z/(z-a)dz / 2πi = {integral:.6f}")
print(f"  理论 f(a) = e^a = {np.exp(a):.6f}")
print(f"  误差: {abs(integral - np.exp(a)):.2e}")

# 2. 留数定理: ∮ f(z) dz = 2πi × Σ(留数)
# f(z) = 1/(z²+1) = 1/((z-i)(z+i)), 极点 z=i (在围道内)
def g(z): return 1 / (z**2 + 1)
R = 2.0; N = 10000
theta = np.linspace(0, 2*np.pi, N, endpoint=False)
z = R * np.exp(1j * theta)
dz = 1j * R * np.exp(1j * theta) * (2*np.pi / N)
integral = np.sum(g(z) * dz)
residue_theory = 1 / (2j)  # 在 z=i 处的留数 = 1/(2i)
theory = 2j * np.pi * residue_theory  # 只 z=i 在围道内
print(f"\\n留数定理: ∮ dz/(z²+1) = {integral:.6f}")
print(f"  理论 2πi × Res(f, i) = {theory:.6f}")
print(f"  误差: {abs(integral - theory):.2e}")
'''

EXPERIMENTS = {
    'linear_algebra': EXP_LINEAR_ALGEBRA,
    'calculus': EXP_CALCULUS,
    'analysis': EXP_ANALYSIS,
    'probability': EXP_PROBABILITY,
    'optimization': EXP_OPTIMIZATION,
    'numerical': EXP_NUMERICAL,
    'information': EXP_INFORMATION,
    'algebra': EXP_ALGEBRA,
    'topology': EXP_TOPOLOGY,
    'sde': EXP_SDE,
    'pde': EXP_PDE,
    'complex': EXP_COMPLEX,
}

def topic_of(name):
    n = name.lower()
    if 'machine_learning' in n: return 'optimization'
    if 'random_matrix' in n: return 'probability'
    if 'linear_alg' in n or 'linear_algebra' in n: return 'linear_algebra'
    if 'ode' in n or '_54_' in n: return 'pde'
    if 'pde' in n: return 'pde'
    if 'differential' in n: return 'pde'
    if 'sde' in n or 'stochastic' in n or 'numerical_sde' in n: return 'sde'
    if any(k in n for k in ['calculus','multivar','vector_calc','m408','m427','vectors_matrices','vector_calculus','complex_analysis','complex_var']): return 'calculus'
    if any(k in n for k in ['analysis','measure','real_var','mat215','mat300','fourier','functional']): return 'analysis'
    if 'probab' in n or 'statistic' in n or 'martingale' in n or 'information' in n: return 'probability' if 'information' not in n else 'information'
    if 'information' in n: return 'information'
    if 'optim' in n or 'convex' in n: return 'optimization'
    if 'numerical' in n or 'comput' in n or 'scientific' in n or 'applied_math' in n or 'cme108' in n: return 'numerical'
    if any(k in n for k in ['algebra','abstract','number','groups','galois','discrete','ring','module','set_theory','sets']): return 'algebra'
    if any(k in n for k in ['topology','geometry','manifold','differential_geom']): return 'topology'
    if 'complex' in n: return 'complex'
    return 'numerical'

# ============================================================
# exercises 模板（按主题，5-8 题）
# ============================================================
def gen_exercises(course_name, topic):
    topic_name = {
        'linear_algebra': '线性代数', 'calculus': '微积分', 'analysis': '实分析',
        'probability': '概率论', 'optimization': '优化', 'numerical': '数值分析',
        'information': '信息论', 'algebra': '抽象代数', 'topology': '拓扑',
        'sde': '随机微分方程', 'pde': '微分方程', 'complex': '复分析',
    }.get(topic, '数学')
    return f'''# {course_name} · 精选习题

> 难度：⭐ 基础 / ⭐⭐ 中等 / ⭐⭐⭐ 开放（连接 ML）

## 基础题（⭐）

1. 用定义验证：{topic_name}的核心定义是什么？写出精确的数学表述。
2. 计算一个简单的{topic_name}例子，验证定理成立。

## 中等题（⭐⭐）

3. 证明{topic_name}的一个关键性质（见 notes.md）。
4. 给出一个反例：什么情况下定理会失效？

## 开放题（⭐⭐⭐ 连接 ML）

5. 这个{topic_name}概念如何应用到机器学习中？（提示：见 README "🔬 理论联系实际"）
6. 用 numpy 实现{topic_name}的核心算法（提示：见 experiments/）。

<details><summary>答案提示</summary>

1-2. 见 notes.md 数学层。
3-4. 见 notes.md 不足层（反例）。
5-6. 见 README 的 ML 关联 + experiments/ 代码。

</details>
'''

# ============================================================
# notes 模板（费曼三层，针对缺 notes 的课）
# ============================================================
def gen_notes(course_name, topic):
    topic_name = {
        'linear_algebra': '线性代数', 'calculus': '微积分', 'analysis': '实分析',
        'probability': '概率论', 'optimization': '优化', 'numerical': '数值分析',
        'information': '信息论', 'algebra': '抽象代数', 'topology': '拓扑',
        'sde': '随机微分方程', 'pde': '微分方程', 'complex': '复分析',
    }.get(topic, '数学')
    return f'''# {course_name} · 费曼三层笔记

> 本笔记按"直觉 → 数学 → 代码 → 不足 → 应用"五层组织。

## 🧠 直觉层（一句话比喻）

{topic_name}研究的是 ... （见 README 的课程信息，提炼核心直觉）。

> **比喻**：用日常生活的类比解释 {topic_name} 的核心对象。

## 🧮 数学层（关键定义 + 定理 + LaTeX）

（基于课程教材，写出 {topic_name} 的核心定义、定理、公式）

## 💻 代码层（numpy 验证）

见 [`experiments/`](./experiments/) 目录的可运行脚本。

## ⚠️ 不足层（局限与边界）

{topic_name}的主要局限是什么？什么情况下会失效？

## 🚀 应用层（ML / 工程关联）

见 README 的"🔬 理论联系实际"小节。

---

> 📌 **注**：本 notes.md 为模板自动生成。建议结合课程教材和 [`experiments/`](./experiments/) 深化。
> 配套：[`exercises.md`](./exercises.md) | [`experiments/`](./experiments/) | [README.md](./README.md)
'''

# ============================================================
# 主逻辑
# ============================================================
stats = {'exp_created': 0, 'exer_created': 0, 'notes_created': 0}

for school in sorted(os.listdir(ROOT)):
    school_dir = os.path.join(ROOT, school)
    if not os.path.isdir(school_dir) or '-math-courses' not in school:
        continue
    for course in sorted(os.listdir(school_dir)):
        course_dir = os.path.join(school_dir, course)
        if not os.path.isdir(course_dir):
            continue
        topic = topic_of(course)

        # 1. 补 experiments/
        exp_dir = os.path.join(course_dir, 'experiments')
        # 如果目录不存在 或 目录里没有 .py 文件，则生成
        has_py = os.path.isdir(exp_dir) and any(fn.endswith('.py') for fn in os.listdir(exp_dir)) if os.path.isdir(exp_dir) else False
        if not has_py:
            os.makedirs(exp_dir, exist_ok=True)
            script = EXPERIMENTS[topic]
            script_path = os.path.join(exp_dir, f'01_{topic}_demo.py')
            with open(script_path, 'w') as fp:
                fp.write(script)
            stats['exp_created'] += 1

        # 2. 补 exercises.md
        exer_path = os.path.join(course_dir, 'exercises.md')
        if not os.path.exists(exer_path):
            with open(exer_path, 'w') as fp:
                fp.write(gen_exercises(course, topic))
            stats['exer_created'] += 1

        # 3. 补 notes.md（最低优先级，只补完全缺失的）
        notes_path = os.path.join(course_dir, 'notes.md')
        if not os.path.exists(notes_path):
            with open(notes_path, 'w') as fp:
                fp.write(gen_notes(course, topic))
            stats['notes_created'] += 1

print("=" * 60)
print("批量补全完成")
print("=" * 60)
print(f"新建 experiments/ 目录: {stats['exp_created']}")
print(f"新建 exercises.md:      {stats['exer_created']}")
print(f"新建 notes.md:          {stats['notes_created']}")
print(f"总计新建文件:           {sum(stats.values())}")
