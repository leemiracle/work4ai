"""
CS 189 Introduction to Machine Learning — UC Berkeley (Sahai/Hasson)
================================================
覆盖主题：
- 线性回归（normal equation + gradient descent）（Lec 5-7）
- 逻辑回归（Newton-Raphson / IRLS）（Lec 8-10）
- GDA（高斯判别分析）/ 朴素贝叶斯（Lec 11-12）
- 决策树 / 随机森林（Lec 18-19）

核心教材/参考：
- Hastie, Tibshirani, Friedman "The Elements of Statistical Learning" 2nd ed (Springer 2009)
- Bishop "Pattern Recognition and Machine Learning" (Springer 2006), Ch 4-5/7
- Breiman "Random Forests" Machine Learning 45(1) (2001)

本文件实现：
- 线性回归（normal eq + GD 对比）
- 逻辑回归（Newton 法 IRLS）
- GDA（高斯判别分析）
- 决策树（C4.5 信息增益）+ 随机森林

运行：
    python ml_classic.py
"""
from __future__ import annotations
import math
import random


# ============================================================
# 0. 纯 numpy 实现（无 sklearn）
# ============================================================
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ============================================================
# 1. 线性回归（normal equation + GD）
# ============================================================

class LinearRegression:
    """
    正规方程: w = (X^T X)^{-1} X^T y
    GD: w ← w - α * X^T(Xw - y) / n
    """
    def __init__(self):
        self.w = None
        self.b = 0.0

    def fit_normal(self, X, y):
        n = len(y)
        Xb = [[1.0] + list(row) for row in X]
        XtX = _matmul(_transpose(Xb), Xb)
        XtX_inv = _invert(XtX)
        Xty = _matvec(_transpose(Xb), y)
        wsol = _matvec(XtX_inv, Xty)
        self.b = wsol[0]
        self.w = wsol[1:]
        return self

    def fit_gd(self, X, y, lr=0.01, epochs=500):
        n, d = len(X), len(X[0]) if X else 0
        self.w = [0.0] * d
        self.b = 0.0
        for _ in range(epochs):
            grad_w = [0.0] * d
            grad_b = 0.0
            for i in range(n):
                pred = self.b + sum(self.w[j] * X[i][j] for j in range(d))
                err = pred - y[i]
                for j in range(d):
                    grad_w[j] += err * X[i][j] / n
                grad_b += err / n
            for j in range(d):
                self.w[j] -= lr * grad_w[j]
            self.b -= lr * grad_b
        return self

    def predict(self, X):
        return [self.b + sum(self.w[j] * row[j] for j in range(len(row))) for row in X]


def _transpose(A):
    return list(map(list, zip(*A)))

def _matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

def _matvec(A, v):
    return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]

def _invert(M):
    """Gauss-Jordan 求逆"""
    n = len(M)
    aug = [list(M[i]) + [1.0 if j == i else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        aug[col], aug[pivot] = aug[pivot], aug[col]
        pv = aug[col][col]
        aug[col] = [x / pv for x in aug[col]]
        for r in range(n):
            if r != col and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [aug[r][k] - factor * aug[col][k] for k in range(2 * n)]
    return [row[n:] for row in aug]


# ============================================================
# 2. 逻辑回归 + Newton-Raphson（IRLS）
# ============================================================

class LogisticRegression:
    """
    P(y=1|x) = σ(w·x + b)
    MLE: min -Σ[y log σ + (1-y) log(1-σ)]
    Newton: w ← w - H^{-1} ∇L
    H = X^T diag(s(1-s)) X （Hessian，s = σ(Xw)）
    """
    def __init__(self):
        self.w = None
        self.b = 0.0

    @staticmethod
    def _sigmoid(z):
        if z >= 0:
            ez = math.exp(-z)
            return 1.0 / (1.0 + ez)
        ez = math.exp(z)
        return ez / (1.0 + ez)

    def fit(self, X, y, epochs=20):
        """
        Newton-Raphson (IRLS): w ← w - H^{-1} ∇L
        H = X^T diag(s(1-s)) X （Hessian，s = σ(Xw)）
        含 bias 列的增广设计矩阵；加 λI 正则保证 Hessian 可逆。
        IRLS 二阶收敛，通常 ≤10 步即收敛。
        """
        n, d = len(X), len(X[0]) if X else 0
        # 增广：bias 作为第 0 列
        Xb = [[1.0] + list(row) for row in X]
        m = d + 1
        w_full = [0.0] * m
        for _ in range(epochs):
            # 线性预测 + sigmoid
            z = [sum(Xb[i][j] * w_full[j] for j in range(m)) for i in range(n)]
            s = [self._sigmoid(zi) for zi in z]
            # 梯度 grad = Xb^T (s - y) / n
            grad = [sum(Xb[i][j] * (s[i] - y[i]) for i in range(n)) / n
                    for j in range(m)]
            # Hessian H[j][k] = Σ_i Xb[i][j] · s_i(1-s_i) · Xb[i][k] / n
            S = [s[i] * (1 - s[i]) for i in range(n)]
            H = [[sum(Xb[i][j] * S[i] * Xb[i][k] for i in range(n)) / n
                  for k in range(m)] for j in range(m)]
            # 加微小正则保证可逆
            for j in range(m):
                H[j][j] += 1e-8
            # Newton 步: w ← w - H^{-1} grad
            H_inv = _invert(H)
            delta = _matvec(H_inv, grad)
            w_full = [w_full[j] - delta[j] for j in range(m)]
        self.b = w_full[0]
        self.w = w_full[1:]
        return self

    def predict_proba(self, X):
        return [self._sigmoid(self.b + sum(self.w[j]*row[j] for j in range(len(row)))) for row in X]

    def predict(self, X, threshold=0.5):
        return [1 if p > threshold else 0 for p in self.predict_proba(X)]


# ============================================================
# 3. GDA 高斯判别分析（Bishop §4.2）
# ============================================================

class GDA:
    """
    假设 P(x|y=k) ~ N(μ_k, Σ)
    判别：argmax_k P(y=k) P(x|y=k)
    """
    def fit(self, X, y):
        self.classes = sorted(set(y))
        self.means = {}
        self.cov = None
        n, d = len(X), len(X[0])
        # Mean per class
        for c in self.classes:
            Xc = [X[i] for i in range(n) if y[i] == c]
            self.means[c] = [sum(row[j] for row in Xc) / len(Xc) for j in range(d)]
        # Shared covariance
        diff_sum = [[0.0]*d for _ in range(d)]
        for i in range(n):
            mu = self.means[y[i]]
            for a in range(d):
                for b in range(d):
                    diff_sum[a][b] += (X[i][a] - mu[a]) * (X[i][b] - mu[b])
        self.cov = [[diff_sum[a][b] / n for b in range(d)] for a in range(d)]
        self.cov_inv = _invert(self.cov)
        self.priors = {c: sum(1 for yi in y if yi == c) / n for c in self.classes}
        return self

    def predict(self, X):
        preds = []
        for x in X:
            best_c, best_ll = None, -math.inf
            for c in self.classes:
                mu = self.means[c]
                diff = [x[j] - mu[j] for j in range(len(x))]
                # Mahalanobis distance
                quad = sum(self.cov_inv[a][b] * diff[a] * diff[b]
                           for a in range(len(x)) for b in range(len(x)))
                ll = -0.5 * quad + math.log(self.priors[c] + 1e-10)
                if ll > best_ll:
                    best_ll, best_c = ll, c
            preds.append(best_c)
        return preds


# ============================================================
# 4. 决策树 + 随机森林（Breiman 2001）
# ============================================================

class DecisionTree:
    """CART with Gini impurity"""
    def __init__(self, max_depth=5, min_samples=2, feature_subset=None):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.feature_subset = feature_subset
        self.tree = None

    def _gini(self, labels):
        if not labels:
            return 0
        counts = {}
        for l in labels:
            counts[l] = counts.get(l, 0) + 1
        n = len(labels)
        return 1 - sum((c / n) ** 2 for c in counts.values())

    def _best_split(self, X, y, indices):
        n_features = len(X[0])
        features = range(n_features)
        if self.feature_subset:
            features = random.sample(range(n_features), min(self.feature_subset, n_features))
        best_gain, best = 0, None
        parent_gini = self._gini([y[i] for i in indices])
        for f in features:
            thresholds = set(X[i][f] for i in indices)
            for t in thresholds:
                left = [i for i in indices if X[i][f] <= t]
                right = [i for i in indices if X[i][f] > t]
                if len(left) < self.min_samples or len(right) < self.min_samples:
                    continue
                n = len(indices)
                child_gini = (len(left)*self._gini([y[i] for i in left]) +
                              len(right)*self._gini([y[i] for i in right])) / n
                gain = parent_gini - child_gini
                if gain > best_gain:
                    best_gain = gain
                    best = (f, t, left, right)
        return best

    def _build(self, X, y, indices, depth):
        labels = [y[i] for i in indices]
        if depth >= self.max_depth or len(set(labels)) == 1 or len(indices) < self.min_samples:
            counts = {}
            for l in labels:
                counts[l] = counts.get(l, 0) + 1
            return {"leaf": max(counts, key=counts.get)}
        split = self._best_split(X, y, indices)
        if not split:
            counts = {}
            for l in labels:
                counts[l] = counts.get(l, 0) + 1
            return {"leaf": max(counts, key=counts.get)}
        f, t, left, right = split
        return {"feature": f, "threshold": t,
                "left": self._build(X, y, left, depth + 1),
                "right": self._build(X, y, right, depth + 1)}

    def fit(self, X, y):
        self.tree = self._build(X, y, list(range(len(y))), 0)
        return self

    def _predict_one(self, x):
        node = self.tree
        while "leaf" not in node:
            if x[node["feature"]] <= node["threshold"]:
                node = node["left"]
            else:
                node = node["right"]
        return node["leaf"]

    def predict(self, X):
        return [self._predict_one(x) for x in X]


class RandomForest:
    """Breiman 2001: bootstrap + feature subsampling"""
    def __init__(self, n_trees=20, max_depth=5, feature_subset=2):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.feature_subset = feature_subset
        self.trees = []

    def fit(self, X, y):
        n = len(y)
        for _ in range(self.n_trees):
            indices = [random.randrange(n) for _ in range(n)]  # bootstrap
            tree = DecisionTree(self.max_depth, feature_subset=self.feature_subset)
            Xb = [X[i] for i in indices]
            yb = [y[i] for i in indices]
            tree.fit(Xb, yb)
            self.trees.append(tree)
        return self

    def predict(self, X):
        all_preds = [[t._predict_one(x) for t in self.trees] for x in X]
        preds = []
        for ps in all_preds:
            counts = {}
            for p in ps:
                counts[p] = counts.get(p, 0) + 1
            preds.append(max(counts, key=counts.get))
        return preds


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("CS 189 Machine Learning Demo")
    print("=" * 60)
    random.seed(42)

    # 1. Linear Regression
    print("\n📋 1. 线性回归（normal eq vs GD）")
    # y = 2x1 + 3x2 + 1 + noise
    X = [[random.gauss(0, 1), random.gauss(0, 1)] for _ in range(100)]
    y = [2*x[0] + 3*x[1] + 1 + random.gauss(0, 0.1) for x in X]
    lr_normal = LinearRegression().fit_normal(X, y)
    lr_gd = LinearRegression().fit_gd(X, y, lr=0.05, epochs=500)
    print(f"   真实: w=[2, 3], b=1")
    print(f"   Normal: w=[{lr_normal.w[0]:.3f}, {lr_normal.w[1]:.3f}], b={lr_normal.b:.3f}")
    print(f"   GD:     w=[{lr_gd.w[0]:.3f}, {lr_gd.w[1]:.3f}], b={lr_gd.b:.3f}")

    # 2. Logistic Regression
    print("\n📋 2. 逻辑回归（分类）")
    X2 = [[random.gauss(-1, 0.5), random.gauss(-1, 0.5)] for _ in range(50)] + \
         [[random.gauss(1, 0.5), random.gauss(1, 0.5)] for _ in range(50)]
    y2 = [0]*50 + [1]*50
    logr = LogisticRegression().fit(X2, y2, epochs=200)
    preds = logr.predict(X2)
    acc = sum(p == t for p, t in zip(preds, y2)) / len(y2)
    print(f"   准确率: {acc:.1%}")

    # 3. GDA
    print("\n📋 3. GDA 高斯判别分析")
    gda = GDA().fit(X2, y2)
    preds_gda = gda.predict(X2)
    acc_gda = sum(p == t for p, t in zip(preds_gda, y2)) / len(y2)
    print(f"   准确率: {acc_gda:.1%}")

    # 4. Decision Tree vs Random Forest
    print("\n📋 4. 决策树 vs 随机森林")
    # XOR-like: nonlinear
    X3 = [[random.uniform(-1, 1), random.uniform(-1, 1)] for _ in range(200)]
    y3 = [1 if (x[0] > 0) != (x[1] > 0) else 0 for x in X3]  # XOR
    # 加少量噪声
    for i in random.sample(range(200), 20):
        y3[i] = 1 - y3[i]

    dt = DecisionTree(max_depth=6).fit(X3, y3)
    preds_dt = dt.predict(X3)
    acc_dt = sum(p == t for p, t in zip(preds_dt, y3)) / len(y3)
    print(f"   决策树训练准确率: {acc_dt:.1%}")

    rf = RandomForest(n_trees=30, max_depth=6, feature_subset=1).fit(X3, y3)
    preds_rf = rf.predict(X3)
    acc_rf = sum(p == t for p, t in zip(preds_rf, y3)) / len(y3)
    print(f"   随机森林(30 trees)训练准确率: {acc_rf:.1%}")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print("   在 XOR 数据上，线性逻辑回归准确率应该 ~50%（XOR 线性不可分）。")
    lr_xor = LogisticRegression().fit(X3, y3, epochs=200)
    preds_xor = lr_xor.predict(X3)
    acc_xor = sum(p == t for p, t in zip(preds_xor, y3)) / len(y3)
    print(f"   逻辑回归在 XOR: {acc_xor:.1%}（几乎随机！）")
    print(f"   决策树在 XOR:   {acc_dt:.1%}（能拟合非线性边界）")
    print()
    print("   关键教训：'没有免费的午餐'——线性模型假设数据线性可分，")
    print("   XOR 这种异或数据需要非线性模型（树/核SVM/神经网络）。")
    print("   选模型 = 选归纳偏置（inductive bias）。")


if __name__ == "__main__":
    demo()
