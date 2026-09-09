"""
凸优化：支持向量机与拉格朗日对偶
================================
数学概念：凸优化 / 拉格朗日对偶 / KKT 条件 / 支持向量机 / 核方法
应用领域：机器学习 / 分类 / 模式识别
核心思想：SVM 寻找最大间隔超平面 w^T x + b = 0。
  原始问题：min ½||w||²  s.t. yᵢ(w^T xᵢ + b) ≥ 1
  拉格朗日对偶：max Σαᵢ - ½ΣΣαᵢαⱼyᵢyⱼxᵢ^T xⱼ  s.t. αᵢ ≥ 0, Σαᵢyᵢ = 0
  KKT 条件：αᵢ[yᵢ(w^T xᵢ + b) - 1] = 0（互补松弛）
  核技巧：K(xᵢ,xⱼ) = φ(xᵢ)^T φ(xⱼ)，隐式映射到高维空间
运行方式：python "13-凸优化_SVM对偶.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. SVM 从零实现（SMO 简化版）============

class SVM:
    """支持向量机（软间隔，对偶形式）。
    用简化版 SMO（Sequential Minimal Optimization）求解对偶问题。
    """

    def __init__(self, C=1.0, kernel='linear', gamma=0.5, max_iter=200, tol=1e-3):
        self.C = C          # 正则化参数（越大越拟合训练数据）
        self.kernel = kernel
        self.gamma = gamma   # RBF 核参数
        self.max_iter = max_iter
        self.tol = tol
        self.alpha = None
        self.b = 0.0
        self.X = None
        self.y = None

    def _kernel(self, x1, x2):
        """核函数：线性核 K(x₁,x₂)=x₁ᵀx₂ 或 RBF 核 K=e^(-γ||x₁-x₂||²)"""
        if self.kernel == 'linear':
            return np.dot(x1, x2)
        elif self.kernel == 'rbf':
            diff = x1 - x2
            return np.exp(-self.gamma * np.dot(diff, diff))

    def _kernel_matrix(self, X):
        """计算完整核矩阵（预计算加速）。"""
        n = len(X)
        K = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                K[i, j] = self._kernel(X[i], X[j])
        return K

    def fit(self, X, y):
        """SMO 简化版训练。
        核心循环：选两个 α 同时优化（因为约束 Σαᵢyᵢ=0 需要至少两个同时变）。
        """
        n = len(X)
        self.X = X
        self.y = y.astype(float)
        self.alpha = np.zeros(n)
        self.b = 0.0

        K = self._kernel_matrix(X)

        for _ in range(self.max_iter):
            num_changed = 0
            for i in range(n):
                # E_i = f(x_i) - y_i（预测误差）
                f_i = np.sum(self.alpha * self.y * K[i]) + self.b
                E_i = f_i - self.y[i]

                # KKT 条件违反检查
                if (self.y[i] * E_i < -self.tol and self.alpha[i] < self.C) or \
                   (self.y[i] * E_i > self.tol and self.alpha[i] > 0):
                    # 随机选第二个 j
                    j = np.random.choice([x for x in range(n) if x != i])
                    f_j = np.sum(self.alpha * self.y * K[j]) + self.b
                    E_j = f_j - self.y[j]

                    # 保存旧值
                    alpha_i_old = self.alpha[i]
                    alpha_j_old = self.alpha[j]

                    # 计算 L 和 H（约束边界）
                    if self.y[i] != self.y[j]:
                        L = max(0, self.alpha[j] - self.alpha[i])
                        H = min(self.C, self.C + self.alpha[j] - self.alpha[i])
                    else:
                        L = max(0, self.alpha[i] + self.alpha[j] - self.C)
                        H = min(self.C, self.alpha[i] + self.alpha[j])

                    if L == H:
                        continue

                    # η = 2K(i,j) - K(i,i) - K(j,j)
                    eta = 2 * K[i, j] - K[i, i] - K[j, j]
                    if eta >= 0:
                        continue

                    # 更新 α_j
                    self.alpha[j] -= self.y[j] * (E_i - E_j) / eta
                    self.alpha[j] = np.clip(self.alpha[j], L, H)

                    if abs(self.alpha[j] - alpha_j_old) < 1e-5:
                        continue

                    # 更新 α_i（保持 Σαᵢyᵢ=0）
                    self.alpha[i] += self.y[i] * self.y[j] * (alpha_j_old - self.alpha[j])

                    # 更新 b
                    b1 = self.b - E_i - self.y[i] * (self.alpha[i] - alpha_i_old) * K[i, i] \
                         - self.y[j] * (self.alpha[j] - alpha_j_old) * K[i, j]
                    b2 = self.b - E_j - self.y[i] * (self.alpha[i] - alpha_i_old) * K[i, j] \
                         - self.y[j] * (self.alpha[j] - alpha_j_old) * K[j, j]

                    if 0 < self.alpha[i] < self.C:
                        self.b = b1
                    elif 0 < self.alpha[j] < self.C:
                        self.b = b2
                    else:
                        self.b = (b1 + b2) / 2

                    num_changed += 1

            if num_changed == 0:
                break

        # 保存支持向量
        self.sv_indices = np.where(self.alpha > 1e-7)[0]
        return self

    def predict(self, X_test):
        """预测。f(x) = ΣαᵢyᵢK(xᵢ,x) + b"""
        predictions = []
        for x in X_test:
            s = 0
            for i in self.sv_indices:
                s += self.alpha[i] * self.y[i] * self._kernel(self.X[i], x)
            predictions.append(s + self.b)
        return np.sign(predictions)

    def decision_function(self, X_test):
        """决策函数值（到超平面的距离）。"""
        return self.predict(X_test)


# ============ 2. 数据生成 ============

def make_linearly_separable(n=50, seed=42):
    """生成线性可分数据。"""
    rng = np.random.RandomState(seed)
    X1 = rng.randn(n // 2, 2) + [2, 2]
    X2 = rng.randn(n // 2, 2) + [-2, -2]
    X = np.vstack([X1, X2])
    y = np.array([1] * (n // 2) + [-1] * (n // 2))
    return X, y

def make_nonlinear(n=100, seed=42):
    """生成非线性可分数据（需要核技巧）。"""
    rng = np.random.RandomState(seed)
    r = rng.uniform(1.5, 4, n // 2)
    theta = rng.uniform(0, 2 * np.pi, n // 2)
    X1 = np.c_[r * np.cos(theta), r * np.sin(theta)]  # 外圈

    r2 = rng.uniform(0, 1, n // 2)
    theta2 = rng.uniform(0, 2 * np.pi, n // 2)
    X2 = np.c_[r2 * np.cos(theta2), r2 * np.sin(theta2)]  # 内圈

    X = np.vstack([X1, X2])
    y = np.array([1] * (n // 2) + [-1] * (n // 2))
    return X, y


# ============ 3. 实验 ============

def main():
    np.random.seed(42)

    # ---- 实验 1：线性可分 SVM（最大间隔）----
    print("=" * 60)
    print("实验 1：线性可分 SVM（最大间隔超平面）")
    print("=" * 60)

    X, y = make_linearly_separable(50)
    svm_linear = SVM(C=1.0, kernel='linear', max_iter=200)
    svm_linear.fit(X, y)

    # 提取 w 和支持向量
    w = np.sum(svm_linear.alpha[i] * svm_linear.y[i] * svm_linear.X[i]
               for i in svm_linear.sv_indices)
    n_sv = len(svm_linear.sv_indices)
    margin = 2 / np.linalg.norm(w)

    # 准确率
    y_pred = svm_linear.predict(X)
    accuracy = np.mean(y_pred == y)

    print(f"训练数据: 50 个样本（2 类各 25 个）")
    print(f"支持向量数: {n_sv} / 50")
    print(f"权重 w = {w}")
    print(f"偏置 b = {svm_linear.b:.4f}")
    print(f"间隔宽度 = 2/||w|| = {margin:.4f}")
    print(f"训练准确率: {accuracy:.2%}")
    print(f"\n[解读] 只有支持向量（α>0）决定分类边界。")
    print(f"       间隔最大化 = 泛化能力的数学保证（VC 维理论）。")

    # ---- 实验 2：正则化参数 C 的影响 ----
    print("\n" + "=" * 60)
    print("实验 2：正则化参数 C 对决策边界的影响")
    print("=" * 60)

    # 加入噪声使数据不完全可分
    X_noisy = np.vstack([X, [[0.5, 0.5], [0, 1], [-0.5, -0.5], [1, 0]]])
    y_noisy = np.array(list(y) + [-1, -1, 1, 1])

    print(f"{'C':<8} {'支持向量数':<12} {'训练准确率':<12} {'间隔宽度':<12} {'行为'}")
    print("-" * 60)
    for C in [0.01, 0.1, 1.0, 10, 100]:
        svm = SVM(C=C, kernel='linear', max_iter=200)
        svm.fit(X_noisy, y_noisy)
        w = np.sum(svm.alpha[i] * svm.y[i] * svm.X[i]
                   for i in svm.sv_indices)
        y_pred = svm.predict(X_noisy)
        acc = np.mean(y_pred == y_noisy)
        mg = 2 / np.linalg.norm(w) if np.linalg.norm(w) > 0 else 0
        behavior = "大间隔(欠拟合)" if C < 0.1 else "平衡" if C < 10 else "小间隔(过拟合)"
        print(f"{C:<8.2f} {len(svm.sv_indices):<12} {acc:<12.2%} {mg:<12.4f} {behavior}")

    print(f"\n[解读] C 小→大间隔→允许误分类→抗噪但可能欠拟合")
    print(f"       C 大→小间隔→严格分类→可能过拟合")
    print(f"       C 是偏差-方差权衡的核心旋钮。")

    # ---- 实验 3：核技巧（非线性分类）----
    print("\n" + "=" * 60)
    print("实验 3：核技巧——线性 SVM vs RBF 核 SVM")
    print("=" * 60)

    X_nl, y_nl = make_nonlinear(100)

    # 线性核（必然失败）
    svm_lin = SVM(C=1.0, kernel='linear', max_iter=200)
    svm_lin.fit(X_nl, y_nl)
    acc_lin = np.mean(svm_lin.predict(X_nl) == y_nl)

    # RBF 核（能处理非线性）
    svm_rbf = SVM(C=1.0, kernel='rbf', gamma=0.5, max_iter=200)
    svm_rbf.fit(X_nl, y_nl)
    acc_rbf = np.mean(svm_rbf.predict(X_nl) == y_nl)

    print(f"非线性数据: 100 个样本（内圈 vs 外圈）")
    print(f"线性核 SVM 准确率: {acc_lin:.2%}（{'失败——数据非线性可分' if acc_lin < 0.7 else '成功'}）")
    print(f"RBF 核 SVM 准确率: {acc_rbf:.2%}（{'成功——核技巧映射到高维' if acc_rbf > 0.9 else '部分成功'}）")
    print(f"RBF 支持向量数: {len(svm_rbf.sv_indices)} / 100")
    print(f"\n[解读] 核技巧 K(xᵢ,xⱼ)=φ(xᵢ)ᵀφ(xⱼ) 隐式映射到高维空间。")
    print(f"       RBF 核 = 无限维映射（Mercer 定理）。")
    print(f"       不需要显式计算 φ——'kernel trick' 的精妙之处。")

    # ============ 4. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # 图 1：线性 SVM 决策边界 + 间隔 + 支持向量
    ax = axes[0, 0]
    ax.scatter(X[y == 1][:, 0], X[y == 1][:, 1], c='blue', s=50, label='类别 +1')
    ax.scatter(X[y == -1][:, 0], X[y == -1][:, 1], c='red', s=50, label='类别 -1')
    # 支持向量高亮
    sv_X = X[svm_linear.sv_indices]
    ax.scatter(sv_X[:, 0], sv_X[:, 1], s=150, facecolors='none',
               edgecolors='green', linewidths=2, label=f'支持向量({n_sv}个)')
    # 决策边界 + 间隔
    xx = np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 100)
    yy = -(w[0] * xx + svm_linear.b) / w[1]
    ax.plot(xx, yy, 'k-', lw=2, label='决策边界')
    ax.plot(xx, -(w[0] * xx + svm_linear.b + 1) / w[1], 'k--', alpha=0.5)
    ax.plot(xx, -(w[0] * xx + svm_linear.b - 1) / w[1], 'k--', alpha=0.5)
    ax.fill_between(xx, -(w[0] * xx + svm_linear.b + 1) / w[1],
                    -(w[0] * xx + svm_linear.b - 1) / w[1], alpha=0.1, color='green',
                    label=f'间隔={margin:.2f}')
    ax.set_title(f'线性 SVM：最大间隔分类（准确率={accuracy:.0%}）')
    ax.legend(fontsize=8)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)

    # 图 2：C 的影响
    ax = axes[0, 1]
    ax.scatter(X_noisy[y_noisy == 1][:, 0], X_noisy[y_noisy == 1][:, 1], c='blue', s=30)
    ax.scatter(X_noisy[y_noisy == -1][:, 0], X_noisy[y_noisy == -1][:, 1], c='red', s=30)
    colors = ['green', 'orange', 'purple', 'brown', 'black']
    for idx, C in enumerate([0.01, 0.1, 1.0, 10, 100]):
        svm = SVM(C=C, kernel='linear', max_iter=200)
        svm.fit(X_noisy, y_noisy)
        w = np.sum(svm.alpha[i] * svm.y[i] * svm.X[i]
                   for i in svm.sv_indices)
        if np.linalg.norm(w) > 0:
            yy = -(w[0] * xx + svm.b) / w[1]
            ax.plot(xx, yy, color=colors[idx], lw=1.5, label=f'C={C}')
    ax.set_title('正则化参数 C 对决策边界的影响')
    ax.legend(fontsize=8)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)

    # 图 3：RBF 核决策边界
    ax = axes[1, 0]
    # 网格决策函数
    x_min, x_max = X_nl[:, 0].min() - 0.5, X_nl[:, 0].max() + 0.5
    y_min, y_max = X_nl[:, 1].min() - 0.5, X_nl[:, 1].max() + 0.5
    xx_grid, yy_grid = np.meshgrid(np.linspace(x_min, x_max, 100),
                                    np.linspace(y_min, y_max, 100))
    Z = svm_rbf.predict(np.c_[xx_grid.ravel(), yy_grid.ravel()])
    Z = Z.reshape(xx_grid.shape)
    ax.contourf(xx_grid, yy_grid, Z, alpha=0.3, cmap='coolwarm')
    ax.scatter(X_nl[y_nl == 1][:, 0], X_nl[y_nl == 1][:, 1], c='blue', s=30, label='+1')
    ax.scatter(X_nl[y_nl == -1][:, 0], X_nl[y_nl == -1][:, 1], c='red', s=30, label='-1')
    sv_X = X_nl[svm_rbf.sv_indices]
    ax.scatter(sv_X[:, 0], sv_X[:, 1], s=100, facecolors='none',
               edgecolors='green', linewidths=1.5, label=f'支持向量({len(svm_rbf.sv_indices)}个)')
    ax.set_title(f'RBF 核 SVM：非线性分类（准确率={acc_rbf:.0%}）')
    ax.legend(fontsize=8)

    # 图 4：α 值分布（支持向量识别）
    ax = axes[1, 1]
    alphas = svm_rbf.alpha
    colors_alpha = ['green' if a > 1e-7 else 'gray' for a in alphas]
    ax.bar(range(len(alphas)), alphas, color=colors_alpha, alpha=0.7)
    ax.axhline(svm_rbf.C, color='red', ls='--', label=f'C={svm_rbf.C}（上界）')
    ax.set_xlabel('样本索引')
    ax.set_ylabel('α（拉格朗日乘子）')
    ax.set_title(f'对偶变量 α 分布（绿色=支持向量，{len(svm_rbf.sv_indices)}/100）')
    ax.legend()

    plt.tight_layout()
    plt.savefig("13-SVM_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 13-SVM_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. SVM = 最大间隔分类 = 凸优化问题（唯一全局最优）")
    print("2. 对偶形式：只依赖支持向量（稀疏性），天然引入核技巧")
    print("3. KKT 条件：αᵢ[yᵢ(w^T xᵢ + b) - 1] = 0（互补松弛）")
    print("4. 正则化 C：偏差-方差权衡的核心旋钮")
    print("5. 核技巧：隐式高维映射，不显式计算 φ（Mercer 定理）")
    print("\n[解读] SVM 是凸优化+线性代数+对偶理论的完美结合——")
    print("       数学优美（全局最优解）+ 实用强大（核技巧）。")
    print("       这也是理解深度学习优化理论的基础。")


if __name__ == "__main__":
    main()
