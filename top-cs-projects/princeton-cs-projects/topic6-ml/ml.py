"""
COS 435 / COS 402 Machine Learning（Princeton）
==================================================
覆盖主题：
- 线性回归（梯度下降 + 正规方程对比）
- 逻辑回归（梯度下降 + sigmoid）
- 感知机（Perceptron learning algorithm）
- kNN（k-Nearest Neighbors）
- 决策树（ID3 / C4.5 信息增益）

核心参考：
- Bishop "Pattern Recognition and Machine Learning" Ch 3-4
- Hastie, Tibshirani, Friedman "The Elements of Statistical Learning" Ch 2-4
- Cover & Hart 1967 "Nearest Neighbor Pattern Classification" IEEE Trans IT
- Quinlan 1986 "Induction of Decision Trees" Machine Learning

本文件实现：
1. 线性回归 (Batch GD)
2. 逻辑回归 (GD + cross-entropy loss)
3. 感知机 (online update)
4. kNN 分类
5. 决策树 (ID3 信息增益)

运行：
    python ml.py
"""
from __future__ import annotations
import math
import random
from collections import Counter


# ================================================================
# 1. Linear Regression (Gradient Descent)
# ================================================================

class LinearRegression:
    """y = w0 + w1*x1 + w2*x2 + ...  via batch gradient descent."""

    def __init__(self, lr: float = 0.01, epochs: int = 1000):
        self.lr = lr
        self.epochs = epochs
        self.weights: list[float] = []

    def fit(self, X: list[list[float]], y: list[float]):
        n = len(X)
        d = len(X[0]) if n > 0 else 0
        # Add bias term
        Xb = [[1.0] + list(row) for row in X]
        self.weights = [0.0] * (d + 1)
        for epoch in range(self.epochs):
            grads = [0.0] * (d + 1)
            for i in range(n):
                pred = sum(w * x for w, x in zip(self.weights, Xb[i]))
                err = pred - y[i]
                for j in range(d + 1):
                    grads[j] += err * Xb[i][j]
            for j in range(d + 1):
                self.weights[j] -= self.lr * grads[j] / n

    def predict(self, X: list[list[float]]) -> list[float]:
        Xb = [[1.0] + list(row) for row in X]
        return [sum(w * x for w, x in zip(self.weights, row)) for row in Xb]


def mse(y_true, y_pred) -> float:
    return sum((a - b) ** 2 for a, b in zip(y_true, y_pred)) / len(y_true)


# ================================================================
# 2. Logistic Regression
# ================================================================

class LogisticRegression:
    """Binary logistic regression with gradient descent."""

    def __init__(self, lr: float = 0.1, epochs: int = 1000):
        self.lr = lr
        self.epochs = epochs
        self.weights: list[float] = []

    @staticmethod
    def _sigmoid(z: float) -> float:
        if z >= 0:
            ez = math.exp(-z)
            return 1.0 / (1.0 + ez)
        ez = math.exp(z)
        return ez / (1.0 + ez)

    def fit(self, X: list[list[float]], y: list[int]):
        n = len(X)
        d = len(X[0]) if n > 0 else 0
        Xb = [[1.0] + list(row) for row in X]
        self.weights = [0.0] * (d + 1)
        for epoch in range(self.epochs):
            grads = [0.0] * (d + 1)
            for i in range(n):
                z = sum(w * x for w, x in zip(self.weights, Xb[i]))
                pred = self._sigmoid(z)
                err = pred - y[i]
                for j in range(d + 1):
                    grads[j] += err * Xb[i][j]
            for j in range(d + 1):
                self.weights[j] -= self.lr * grads[j] / n

    def predict_proba(self, X: list[list[float]]) -> list[float]:
        Xb = [[1.0] + list(row) for row in X]
        return [self._sigmoid(sum(w * x for w, x in zip(self.weights, row)))
                for row in Xb]

    def predict(self, X: list[list[float]]) -> list[int]:
        return [1 if p >= 0.5 else 0 for p in self.predict_proba(X)]


# ================================================================
# 3. Perceptron
# ================================================================

class Perceptron:
    """Classic perceptron: online mistake-driven learning."""

    def __init__(self, lr: float = 1.0, epochs: int = 100):
        self.lr = lr
        self.epochs = epochs
        self.weights: list[float] = []
        self.mistakes = 0

    def fit(self, X: list[list[float]], y: list[int]):
        n = len(X)
        d = len(X[0]) if n > 0 else 0
        Xb = [[1.0] + list(row) for row in X]
        self.weights = [0.0] * (d + 1)
        self.mistakes = 0
        for epoch in range(self.epochs):
            errors = 0
            for i in range(n):
                score = sum(w * x for w, x in zip(self.weights, Xb[i]))
                pred = 1 if score > 0 else -1
                # Convert y from {0,1} to {-1,1}
                yi = 1 if y[i] == 1 else -1
                if pred != yi:
                    for j in range(d + 1):
                        self.weights[j] += self.lr * yi * Xb[i][j]
                    errors += 1
                    self.mistakes += 1
            if errors == 0:
                break

    def predict(self, X: list[list[float]]) -> list[int]:
        Xb = [[1.0] + list(row) for row in X]
        return [1 if sum(w * x for w, x in zip(self.weights, row)) > 0 else 0
                for row in Xb]


# ================================================================
# 4. kNN
# ================================================================

def euclidean(a, b) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


class KNN:
    """k-Nearest Neighbors with majority vote."""

    def __init__(self, k: int = 3, distance=euclidean):
        self.k = k
        self.distance = distance
        self.X = []
        self.y = []

    def fit(self, X, y):
        self.X = X
        self.y = y

    def predict_one(self, x) -> int:
        dists = [(self.distance(x, xi), yi) for xi, yi in zip(self.X, self.y)]
        dists.sort(key=lambda t: t[0])
        neighbors = [yi for _, yi in dists[:self.k]]
        return Counter(neighbors).most_common(1)[0][0]

    def predict(self, X) -> list[int]:
        return [self.predict_one(x) for x in X]


# ================================================================
# 5. Decision Tree (ID3)
# ================================================================

class DecisionNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, label=None):
        self.feature = feature      # split feature index
        self.threshold = threshold   # split threshold
        self.left = left
        self.right = right
        self.label = label           # leaf label


class DecisionTree:
    """ID3 decision tree with information gain (C4.5-style continuous splits)."""

    def __init__(self, max_depth: int = 5, min_samples: int = 2):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.root = None

    def fit(self, X, y):
        self.root = self._build(X, y, depth=0)

    def _entropy(self, labels) -> float:
        if not labels:
            return 0.0
        counts = Counter(labels)
        n = len(labels)
        return -sum((c / n) * math.log2(c / n) for c in counts.values())

    def _build(self, X, y, depth):
        # Leaf conditions
        if len(set(y)) == 1:
            return DecisionNode(label=y[0])
        if depth >= self.max_depth or len(y) < self.min_samples:
            return DecisionNode(label=Counter(y).most_common(1)[0][0])

        best_gain = -1
        best_feat, best_thresh = 0, 0.0
        base_entropy = self._entropy(y)

        for feat in range(len(X[0])):
            values = sorted(set(row[feat] for row in X))
            for i in range(len(values) - 1):
                thresh = (values[i] + values[i + 1]) / 2
                left_y = [y[j] for j in range(len(y)) if X[j][feat] <= thresh]
                right_y = [y[j] for j in range(len(y)) if X[j][feat] > thresh]
                if not left_y or not right_y:
                    continue
                n = len(y)
                ig = base_entropy - (len(left_y) / n * self._entropy(left_y) +
                                     len(right_y) / n * self._entropy(right_y))
                if ig > best_gain:
                    best_gain = ig
                    best_feat = feat
                    best_thresh = thresh

        if best_gain <= 0:
            return DecisionNode(label=Counter(y).most_common(1)[0][0])

        left_idx = [j for j in range(len(y)) if X[j][best_feat] <= best_thresh]
        right_idx = [j for j in range(len(y)) if X[j][best_feat] > best_thresh]
        left = self._build([X[j] for j in left_idx], [y[j] for j in left_idx], depth + 1)
        right = self._build([X[j] for j in right_idx], [y[j] for j in right_idx], depth + 1)
        return DecisionNode(feature=best_feat, threshold=best_thresh,
                            left=left, right=right)

    def predict_one(self, x) -> int:
        node = self.root
        while node.label is None:
            if x[node.feature] <= node.threshold:
                node = node.left
            else:
                node = node.right
        return node.label

    def predict(self, X) -> list[int]:
        return [self.predict_one(x) for x in X]


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 435/402: Machine Learning Demo")
    print("=" * 60)
    random.seed(42)

    # --- 1. Linear Regression ---
    print("\n📋 1. 线性回归 (梯度下降)")
    # y = 3x + 2 + noise
    X_lin = [[random.uniform(0, 10)] for _ in range(100)]
    y_lin = [3.0 * x[0] + 2.0 + random.gauss(0, 0.5) for x in X_lin]
    lr_model = LinearRegression(lr=0.01, epochs=500)
    lr_model.fit(X_lin, y_lin)
    print(f"   真实: y = 3x + 2")
    print(f"   学到: y = {lr_model.weights[1]:.2f}x + {lr_model.weights[0]:.2f}")
    mse_val = mse(y_lin, lr_model.predict(X_lin))
    print(f"   MSE: {mse_val:.4f}")

    # --- 2. Logistic Regression ---
    print("\n📋 2. 逻辑回归 (二分类)")
    # Two clusters
    X_cls = [[random.gauss(-2, 1), random.gauss(-2, 1)] for _ in range(50)] + \
            [[random.gauss(2, 1), random.gauss(2, 1)] for _ in range(50)]
    y_cls = [0] * 50 + [1] * 50
    log_model = LogisticRegression(lr=0.1, epochs=1000)
    log_model.fit(X_cls, y_cls)
    preds = log_model.predict(X_cls)
    acc = sum(p == t for p, t in zip(preds, y_cls)) / len(y_cls)
    print(f"   训练准确率: {acc:.1%}")

    # --- 3. Perceptron ---
    print("\n📋 3. 感知机")
    perc = Perceptron(lr=1.0, epochs=100)
    perc.fit(X_cls, y_cls)
    preds = perc.predict(X_cls)
    acc = sum(p == t for p, t in zip(preds, y_cls)) / len(y_cls)
    print(f"   总错误次数: {perc.mistakes}")
    print(f"   训练准确率: {acc:.1%}")

    # --- 4. kNN ---
    print("\n📋 4. kNN")
    # 3-class data
    X_3cls = []
    y_3cls = []
    centers = [(0, 0), (5, 0), (2.5, 5)]
    for ci, (cx, cy) in enumerate(centers):
        for _ in range(30):
            X_3cls.append([cx + random.gauss(0, 1), cy + random.gauss(0, 1)])
            y_3cls.append(ci)
    # Split
    split = int(0.8 * len(X_3cls))
    indices = list(range(len(X_3cls)))
    random.shuffle(indices)
    train_idx, test_idx = indices[:split], indices[split:]
    X_train = [X_3cls[i] for i in train_idx]
    y_train = [y_3cls[i] for i in train_idx]
    X_test = [X_3cls[i] for i in test_idx]
    y_test = [y_3cls[i] for i in test_idx]

    for k in [1, 3, 5, 7]:
        knn = KNN(k=k)
        knn.fit(X_train, y_train)
        preds = knn.predict(X_test)
        acc = sum(p == t for p, t in zip(preds, y_test)) / len(y_test)
        print(f"   k={k}: 测试准确率 {acc:.1%}")

    # --- 5. Decision Tree ---
    print("\n📋 5. 决策树 (ID3)")
    dt = DecisionTree(max_depth=5)
    dt.fit(X_train, y_train)
    preds = dt.predict(X_test)
    acc = sum(p == t for p, t in zip(preds, y_test)) / len(y_test)
    print(f"   测试准确率: {acc:.1%}")
    print(f"   根节点分裂: feature={dt.root.feature}, threshold={dt.root.threshold:.2f}")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    # k=1 vs k=7
    knn1 = KNN(k=1); knn1.fit(X_train, y_train)
    knn7 = KNN(k=7); knn7.fit(X_train, y_train)
    acc1 = sum(p == t for p, t in zip(knn1.predict(X_test), y_test)) / len(y_test)
    acc7 = sum(p == t for p, t in zip(knn7.predict(X_test), y_test)) / len(y_test)
    # Training accuracy
    acc1_train = sum(p == t for p, t in zip(knn1.predict(X_train), y_train)) / len(y_train)
    acc7_train = sum(p == t for p, t in zip(knn7.predict(X_train), y_train)) / len(y_train)
    print(f"   k=1: 训练 {acc1_train:.1%}, 测试 {acc1:.1%}")
    print(f"   k=7: 训练 {acc7_train:.1%}, 测试 {acc7:.1%}")
    print(f"   → k=1 训练集几乎 100%（过拟合），k=7 泛化更好")
    print(f"   → 这就是 bias-variance tradeoff 的直观体现")

    print("\n✅ COS 435/402 Demo 完成！")


if __name__ == "__main__":
    demo()
