"""
CSC 411 / CSC 511 Machine Learning (University of Toronto)
==========================================================
覆盖主题：
- Linear / Logistic Regression（梯度下降）
- kNN（k-Nearest Neighbors）
- Decision Tree（ID3 信息增益）
- Bagging + Random Forest
- k-Means + EM（Gaussian Mixture Model）

核心教材：
- Hastie, Tibshirani, Friedman "The Elements of Statistical Learning" (2nd ed.)
- Bishop "Pattern Recognition and Machine Learning" (2006)
- Breiman "Random Forests" Machine Learning Journal, 2001
- Dempster, Laird, Rubin "Maximum Likelihood from Incomplete Data via the EM Algorithm" J Royal Stat Soc B, 1977

本文件实现（纯 numpy）：
- 线性回归（解析解 + 梯度下降）
- Logistic 回归（梯度下降 + L2 正则）
- kNN 分类器
- 决策树（信息增益 + 剪枝）
- Random Forest（Bagging + 特征子采样）
- k-Means + GMM（EM 算法）

运行：
    python ml.py
"""
from __future__ import annotations
import numpy as np
import random


# ============ 1. Linear Regression ============

class LinearRegression:
    """
    线性回归：两种解法
    1. 解析解（Normal Equation）: w = (X^T X)^{-1} X^T y
    2. 梯度下降: w ← w - α * X^T (Xw - y) / n
    """

    def __init__(self, method='normal'):
        self.method = method
        self.w = None
        self.b = None

    def fit(self, X, y, lr=0.01, epochs=1000):
        n, d = X.shape
        X_aug = np.hstack([X, np.ones((n, 1))])

        if self.method == 'normal':
            self.w = np.linalg.lstsq(X_aug, y, rcond=None)[0]
        else:
            theta = np.zeros(d + 1)
            for _ in range(epochs):
                pred = X_aug @ theta
                grad = X_aug.T @ (pred - y) / n
                theta -= lr * grad
            self.w = theta

    def predict(self, X):
        n = X.shape[0]
        X_aug = np.hstack([X, np.ones((n, 1))])
        return X_aug @ self.w

    def mse(self, X, y):
        return np.mean((self.predict(X) - y) ** 2)


# ============ 2. Logistic Regression ============

class LogisticRegression:
    """
    Logistic 回归: P(y=1|x) = σ(w^T x + b)
    损失: -[y log(p) + (1-y) log(1-p)] + λ|w|²
    """

    def __init__(self, lr=0.1, epochs=500, l2=0.01):
        self.lr = lr
        self.epochs = epochs
        self.l2 = l2
        self.w = None
        self.b = 0

    @staticmethod
    def _sigmoid(z):
        return 1 / (1 + np.exp(-np.clip(z, -250, 250)))

    def fit(self, X, y):
        n, d = X.shape
        self.w = np.zeros(d)
        self.b = 0
        for _ in range(self.epochs):
            z = X @ self.w + self.b
            p = self._sigmoid(z)
            grad_w = X.T @ (p - y) / n + self.l2 * self.w
            grad_b = np.mean(p - y)
            self.w -= self.lr * grad_w
            self.b -= self.lr * grad_b

    def predict_proba(self, X):
        return self._sigmoid(X @ self.w + self.b)

    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)

    def accuracy(self, X, y):
        return np.mean(self.predict(X) == y)


# ============ 3. kNN ============

class KNN:
    """k-Nearest Neighbors 分类器"""

    def __init__(self, k=3):
        self.k = k

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y

    def predict(self, X):
        predictions = []
        for x in X:
            # 欧氏距离
            dists = np.sqrt(np.sum((self.X_train - x) ** 2, axis=1))
            k_nearest = np.argsort(dists)[:self.k]
            votes = self.y_train[k_nearest]
            pred = np.bincount(votes.astype(int)).argmax()
            predictions.append(pred)
        return np.array(predictions)


# ============ 4. Decision Tree ============

class DecisionTree:
    """
    决策树（ID3 信息增益 IG）
    """

    class Node:
        def __init__(self):
            self.feature = None
            self.threshold = None
            self.left = None
            self.right = None
            self.label = None

    def __init__(self, max_depth=5, min_samples=2):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.root = None

    def _entropy(self, y) -> float:
        if len(y) == 0:
            return 0
        _, counts = np.unique(y, return_counts=True)
        p = counts / len(y)
        return -np.sum(p * np.log2(p + 1e-10))

    def _best_split(self, X, y):
        best_gain = -1
        best_feat, best_thresh = None, None
        n, d = X.shape
        parent_entropy = self._entropy(y)

        for feat in range(d):
            thresholds = np.unique(X[:, feat])
            for thresh in thresholds:
                left_mask = X[:, feat] <= thresh
                right_mask = ~left_mask
                if np.sum(left_mask) < 1 or np.sum(right_mask) < 1:
                    continue
                n_l, n_r = np.sum(left_mask), np.sum(right_mask)
                ig = parent_entropy - (n_l / n) * self._entropy(y[left_mask]) - (n_r / n) * self._entropy(y[right_mask])
                if ig > best_gain:
                    best_gain = ig
                    best_feat, best_thresh = feat, thresh
        return best_feat, best_thresh, best_gain

    def _build(self, X, y, depth):
        node = self.Node()
        if depth >= self.max_depth or len(y) < self.min_samples or self._entropy(y) < 0.01:
            node.label = np.bincount(y.astype(int)).argmax()
            return node

        feat, thresh, gain = self._best_split(X, y)
        if feat is None or gain < 0.01:
            node.label = np.bincount(y.astype(int)).argmax()
            return node

        left_mask = X[:, feat] <= thresh
        node.feature = feat
        node.threshold = thresh
        node.left = self._build(X[left_mask], y[left_mask], depth + 1)
        node.right = self._build(X[~left_mask], y[~left_mask], depth + 1)
        return node

    def fit(self, X, y):
        self.root = self._build(X, y, 0)

    def _predict_one(self, x, node):
        while node.label is None:
            if x[node.feature] <= node.threshold:
                node = node.left
            else:
                node = node.right
        return node.label

    def predict(self, X):
        return np.array([self._predict_one(x, self.root) for x in X])


# ============ 5. Random Forest ============

class RandomForest:
    """
    Random Forest: Bagging + 随机特征子采样
    """

    def __init__(self, n_trees=10, max_depth=5, max_features=None):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.max_features = max_features
        self.trees = []

    def fit(self, X, y):
        n, d = X.shape
        max_feat = self.max_features or int(np.sqrt(d))
        self.trees = []
        for _ in range(self.n_trees):
            # Bootstrap 采样
            indices = np.random.choice(n, n, replace=True)
            feat_indices = np.random.choice(d, max_feat, replace=False)
            tree = DecisionTree(max_depth=self.max_depth)
            tree.fit(X[indices][:, feat_indices], y[indices])
            self.trees.append((tree, feat_indices))

    def predict(self, X):
        predictions = []
        for tree, feat_idx in self.trees:
            predictions.append(tree.predict(X[:, feat_idx]))
        predictions = np.array(predictions)
        # 多数投票
        return np.array([np.bincount(preds.astype(int)).argmax() for preds in predictions.T])


# ============ 6. k-Means ============

class KMeans:
    """
    k-Means 聚类
    """

    def __init__(self, k=3, max_iter=100):
        self.k = k
        self.max_iter = max_iter

    def fit(self, X):
        n = len(X)
        # k-means++ 初始化
        self.centroids = [X[np.random.randint(n)]]
        for _ in range(self.k - 1):
            dists = np.array([min(np.sum((x - c) ** 2) for c in self.centroids) for x in X])
            probs = dists / dists.sum()
            self.centroids.append(X[np.random.choice(n, p=probs)])
        self.centroids = np.array(self.centroids)

        for _ in range(self.max_iter):
            # 分配
            labels = np.array([np.argmin(np.sum((self.centroids - x) ** 2, axis=1)) for x in X])
            # 更新
            new_centroids = np.array([X[labels == k].mean(axis=0) if np.any(labels == k) else self.centroids[k]
                                      for k in range(self.k)])
            if np.allclose(new_centroids, self.centroids):
                break
            self.centroids = new_centroids
        self.labels_ = labels

    def inertia(self, X):
        return sum(np.sum((X[self.labels_ == k] - self.centroids[k]) ** 2)
                   for k in range(self.k))


# ============ 7. GMM via EM ============

class GMM:
    """
    Gaussian Mixture Model via EM Algorithm
    EM Q-function: Q(θ|θ_old) = Σ_n Σ_k γ(z_nk) [log π_k + log N(x_n|μ_k,Σ_k)]
    E-step: γ(z_nk) = π_k N(x_n|μ_k,Σ_k) / Σ_j π_j N(x_n|μ_j,Σ_j)
    M-step: π_k = N_k/N, μ_k = Σ_n γ(z_nk) x_n / N_k, Σ_k = Σ_n γ(z_nk)(x_n-μ_k)(x_n-μ_k)^T / N_k
    """

    def __init__(self, k=2, max_iter=100):
        self.k = k
        self.max_iter = max_iter

    def _gaussian(self, X, mean, cov):
        d = X.shape[1]
        diff = X - mean
        cov_inv = np.linalg.inv(cov + 1e-6 * np.eye(d))
        exponent = -0.5 * np.sum(diff @ cov_inv * diff, axis=1)
        return np.exp(exponent) / np.sqrt(np.linalg.det(cov + 1e-6 * np.eye(d)) * (2 * np.pi) ** d + 1e-10)

    def fit(self, X):
        n, d = X.shape
        # 初始化
        self.means = X[np.random.choice(n, self.k, replace=False)]
        self.covs = [np.eye(d) for _ in range(self.k)]
        self.pis = np.ones(self.k) / self.k

        for _ in range(self.max_iter):
            # E-step
            resp = np.zeros((n, self.k))
            for k in range(self.k):
                resp[:, k] = self.pis[k] * self._gaussian(X, self.means[k], self.covs[k])
            resp_sum = resp.sum(axis=1, keepdims=True) + 1e-10
            resp /= resp_sum

            # M-step
            Nk = resp.sum(axis=0)
            for k in range(self.k):
                self.means[k] = (resp[:, k:k+1] * X).sum(axis=0) / Nk[k]
                diff = X - self.means[k]
                self.covs[k] = (resp[:, k:k+1] * diff).T @ diff / Nk[k] + 1e-6 * np.eye(d)
            self.pis = Nk / n

        self.labels_ = resp.argmax(axis=1)


# ============ Synthetic Data ============

def make_classification(n=200, n_features=2, seed=42):
    rng = np.random.RandomState(seed)
    n_per = n // 2
    X1 = rng.randn(n_per, n_features) + np.array([2, 2])
    X2 = rng.randn(n_per, n_features) + np.array([-2, -2])
    X = np.vstack([X1, X2])
    y = np.array([0] * n_per + [1] * n_per)
    return X, y


def make_blobs(n=150, seed=42):
    rng = np.random.RandomState(seed)
    centers = [(0, 0), (5, 5), (0, 5)]
    X = np.vstack([rng.randn(n // 3, 2) + c for c in centers])
    return X


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 411/511: Machine Learning Demo")
    print("=" * 60)

    np.random.seed(42)
    X, y = make_classification(200)

    # 1. Linear Regression
    print("\n📋 1. Linear Regression")
    X_reg = np.random.randn(100, 1) * 3
    y_reg = 2.5 * X_reg.ravel() + 1.0 + np.random.randn(100) * 0.5
    for method in ['normal', 'gd']:
        lr = LinearRegression(method=method)
        lr.fit(X_reg, y_reg, lr=0.01, epochs=500)
        print(f"   {method:8s}: w={lr.w[0]:.3f}, b={lr.w[1]:.3f}, MSE={lr.mse(X_reg, y_reg):.4f}")

    # 2. Logistic Regression
    print("\n📋 2. Logistic Regression")
    logr = LogisticRegression(lr=0.1, epochs=300)
    logr.fit(X, y)
    print(f"   accuracy = {logr.accuracy(X, y):.1%}")
    print(f"   w = [{logr.w[0]:.3f}, {logr.w[1]:.3f}], b = {logr.b:.3f}")

    # 3. kNN
    print("\n📋 3. kNN")
    for k in [1, 3, 5, 7]:
        knn = KNN(k=k)
        knn.fit(X, y)
        acc = np.mean(knn.predict(X) == y)
        print(f"   k={k}: accuracy = {acc:.1%}")

    # 4. Decision Tree
    print("\n📋 4. Decision Tree")
    dt = DecisionTree(max_depth=5)
    dt.fit(X, y)
    acc_dt = np.mean(dt.predict(X) == y)
    print(f"   单棵树 accuracy = {acc_dt:.1%}")

    # 5. Random Forest
    print("\n📋 5. Random Forest")
    for nt in [1, 5, 10, 20]:
        rf = RandomForest(n_trees=nt, max_depth=5)
        rf.fit(X, y)
        acc_rf = np.mean(rf.predict(X) == y)
        print(f"   {nt:2d} 棵树: accuracy = {acc_rf:.1%}")

    # 6. k-Means
    print("\n📋 6. k-Means 聚类")
    X_cluster = make_blobs(150)
    km = KMeans(k=3)
    km.fit(X_cluster)
    print(f"   Inertia = {km.inertia(X_cluster):.2f}")
    counts = np.bincount(km.labels_)
    print(f"   簇大小: {counts}")

    # 7. GMM via EM
    print("\n📋 7. GMM via EM Algorithm")
    gmm = GMM(k=2, max_iter=50)
    gmm.fit(X)
    counts_gmm = np.bincount(gmm.labels_)
    print(f"   GMM 簇大小: {counts_gmm}")
    print(f"   混合权重 π: {gmm.pis}")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    print("   1. kNN k=1 training accuracy=100%（过拟合），但测试集会下降")
    print("   2. Random Forest 1棵 vs 20棵：方差降低，但偏差不变")
    print("   3. EM 对初始化敏感（非凸优化），可能收敛到局部最优")
    print("   4. k-Means 假设球形簇，对椭圆簇失败 → GMM 更通用")

    print("\n✅ CSC 411/511 完成！")
    print("💡 覆盖：线性/Logistic回归 + kNN + 决策树 + Random Forest + k-Means + GMM-EM")


if __name__ == "__main__":
    demo()
