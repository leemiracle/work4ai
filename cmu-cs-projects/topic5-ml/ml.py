"""
10-701 Introduction to Machine Learning (CMU)
================================================
覆盖主题（对应 lecture）：
- Supervised: Logistic Regression (GD), Gaussian Discriminant Analysis (GDA)
- Unsupervised: EM for GMM (Gaussian Mixture Model)
- Trees: ID3 Decision Tree (信息增益)

核心教材/论文：
- "Mitchell 1997 Machine Learning" McGraw-Hill (ID3, Ch 3)
- "Hastie Tibshirani Friedman ESL" 2nd ed (GDA, GMM/EM Ch 8)
- "Dempster Laird Rubin 1977 J Royal Stat Soc B" — EM algorithm
- Ng "CS229 Lecture Notes" Stanford (GDA, logistic regression)

本文件实现：
- Binary logistic regression (gradient descent)
- Multi-class GDA (shared covariance → linear boundary)
- EM for GMM (1D, full E-M steps)
- ID3 decision tree (entropy + information gain)

运行：
    python3 ml.py
"""
from __future__ import annotations
import math
import random
from collections import Counter

# ============ 1. Logistic Regression ============

def sigmoid(z):
    if z >= 0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    ez = math.exp(z)
    return ez / (1.0 + ez)

class LogisticRegression:
    """Binary logistic regression with gradient descent."""

    def __init__(self, lr=0.1, epochs=500):
        self.lr = lr
        self.epochs = epochs
        self.w = None
        self.b = 0.0

    def fit(self, X, y):
        n, d = len(X), len(X[0])
        self.w = [0.0] * d
        self.b = 0.0
        for epoch in range(self.epochs):
            gw = [0.0] * d
            gb = 0.0
            for xi, yi in zip(X, y):
                z = sum(wj * xj for wj, xj in zip(self.w, xi)) + self.b
                p = sigmoid(z)
                err = p - yi
                for j in range(d):
                    gw[j] += err * xi[j]
                gb += err
            for j in range(d):
                self.w[j] -= self.lr * gw[j] / n
            self.b -= self.lr * gb / n

    def predict_proba(self, x):
        z = sum(wj * xj for wj, xj in zip(self.w, x)) + self.b
        return sigmoid(z)

    def predict(self, x):
        return 1 if self.predict_proba(x) >= 0.5 else 0


# ============ 2. Gaussian Discriminant Analysis ============

def mean_vec(X):
    n, d = len(X), len(X[0])
    return [sum(x[j] for x in X) / n for j in range(d)]

def cov_matrix(X, mu):
    n, d = len(X), len(X[0])
    cov = [[0.0]*d for _ in range(d)]
    for x in X:
        for i in range(d):
            for j in range(d):
                cov[i][j] += (x[i]-mu[i]) * (x[j]-mu[j])
    return [[c/n for c in row] for row in cov]

class GDA:
    """Multi-class GDA with shared covariance (linear decision boundary)."""

    def fit(self, X, y):
        classes = sorted(set(y))
        self.classes = classes
        self.means = {}
        self.priors = {}
        all_X = {c: [] for c in classes}
        for xi, yi in zip(X, y):
            all_X[yi].append(xi)
        d = len(X[0])
        # shared covariance
        total_cov = [[0.0]*d for _ in range(d)]
        n_total = len(X)
        for c in classes:
            Xc = all_X[c]
            self.means[c] = mean_vec(Xc)
            self.priors[c] = len(Xc) / n_total
            mu_c = self.means[c]
            cov_c = cov_matrix(Xc, mu_c)
            for i in range(d):
                for j in range(d):
                    total_cov[i][j] += cov_c[i][j] * len(Xc) / n_total
        self.sigma = total_cov
        self.sigma_inv = _invert_2x2(total_cov) if d == 2 else None

    def predict(self, x):
        if self.sigma_inv:
            best_c, best_score = None, -math.inf
            for c in self.classes:
                mu = self.means[c]
                diff = [x[i] - mu[i] for i in range(len(x))]
                # quadratic form diff^T Σ^-1 diff
                quad = sum(self.sigma_inv[i][j] * diff[i] * diff[j]
                           for i in range(len(diff)) for j in range(len(diff)))
                score = -0.5*quad + math.log(self.priors[c])
                if score > best_score:
                    best_score, best_c = score, c
            return best_c
        return self.classes[0]

def _invert_2x2(m):
    a, b = m[0]
    c, d = m[1]
    det = a*d - b*c
    if abs(det) < 1e-10:
        return [[1e6, 0],[0, 1e6]]
    return [[d/det, -b/det], [-c/det, a/det]]


# ============ 3. EM for GMM (1D) ============

def em_gmm_1d(data, k=2, epochs=50):
    """EM for 1D Gaussian Mixture Model."""
    n = len(data)
    # init
    means = [data[random.randint(0, n-1)] for _ in range(k)]
    variances = [1.0] * k
    weights = [1.0/k] * k

    log_likes = []
    for epoch in range(epochs):
        # E-step: responsibilities
        resp = [[0.0]*k for _ in range(n)]
        for i in range(n):
            total = 0.0
            for j in range(k):
                resp[i][j] = weights[j] * _gaussian_1d(data[i], means[j], variances[j])
                total += resp[i][j]
            for j in range(k):
                resp[i][j] /= max(total, 1e-300)

        # M-step
        Nk = [sum(resp[i][j] for i in range(n)) for j in range(k)]
        for j in range(k):
            means[j] = sum(resp[i][j]*data[i] for i in range(n)) / max(Nk[j], 1e-10)
            variances[j] = sum(resp[i][j]*(data[i]-means[j])**2 for i in range(n)) / max(Nk[j], 1e-10)
            weights[j] = Nk[j] / n

        ll = sum(math.log(max(sum(weights[j]*_gaussian_1d(data[i], means[j], variances[j])
                             for j in range(k)), 1e-300)) for i in range(n))
        log_likes.append(ll)

    return means, variances, weights, log_likes

def _gaussian_1d(x, mu, var):
    return 1.0/math.sqrt(2*math.pi*max(var,1e-10)) * math.exp(-(x-mu)**2/(2*max(var,1e-10)))


# ============ 4. ID3 Decision Tree ============

def entropy(labels):
    total = len(labels)
    if total == 0:
        return 0
    counts = Counter(labels)
    return -sum((c/total)*math.log2(c/total) for c in counts.values())

def info_gain(X_col, y, split_val=None):
    """For discrete features: split on feature value."""
    total_e = entropy(y)
    values = set(X_col)
    weighted = 0.0
    n = len(y)
    for v in values:
        subset_y = [y[i] for i in range(n) if X_col[i] == v]
        weighted += len(subset_y)/n * entropy(subset_y)
    return total_e - weighted

class ID3Node:
    def __init__(self):
        self.label = None    # if leaf
        self.feature = None  # split feature index
        self.children = {}

def id3(X, y, features, depth=0, max_depth=5):
    node = ID3Node()
    # pure node
    if len(set(y)) == 1:
        node.label = y[0]
        return node
    if not features or depth >= max_depth:
        node.label = Counter(y).most_common(1)[0][0]
        return node

    # pick best feature
    best_f, best_ig = None, -1
    for f in features:
        col = [row[f] for row in X]
        ig = info_gain(col, y)
        if ig > best_ig:
            best_ig, best_f = ig, f

    node.feature = best_f
    remaining = [f for f in features if f != best_f]
    col = [row[best_f] for row in X]
    for v in set(col):
        idx = [i for i in range(len(X)) if col[i] == v]
        X_v = [X[i] for i in idx]
        y_v = [y[i] for i in idx]
        node.children[v] = id3(X_v, y_v, remaining, depth+1, max_depth)
    return node

def id3_predict(node, x):
    while node.label is None:
        v = x[node.feature]
        if v not in node.children:
            return None
        node = node.children[v]
    return node.label


# ============ Demo ============

def demo():
    print("=" * 60)
    print("10-701 Intro ML: LogReg, GDA, GMM-EM, ID3")
    print("=" * 60)
    random.seed(42)

    # --- 1. Logistic Regression ---
    print("\n📋 1. Logistic Regression")
    # XOR-like data (linearly inseparable — logistic will struggle)
    X_lin = [[0,0],[0,1],[1,0],[1,1]]*25
    y_lin = [0,0,0,1]*25  # AND function
    lr = LogisticRegression(lr=0.5, epochs=300)
    lr.fit(X_lin, y_lin)
    correct = sum(1 for xi,yi in zip(X_lin,y_lin) if lr.predict(xi)==yi)
    print(f"   AND function: accuracy = {correct}/{len(y_lin)} = {correct/len(y_lin):.1%}")
    print(f"   weights = [{lr.w[0]:.3f}, {lr.w[1]:.3f}], bias = {lr.b:.3f}")

    # --- 2. GDA ---
    print("\n📋 2. Gaussian Discriminant Analysis (3 classes)")
    def gen_2d(cx, cy, n):
        return [[cx+random.gauss(0,0.5), cy+random.gauss(0,0.5)] for _ in range(n)]
    X3 = gen_2d(0,0,30) + gen_2d(5,5,30) + gen_2d(0,5,30)
    y3 = [0]*30 + [1]*30 + [2]*30
    gda = GDA(); gda.fit(X3, y3)
    correct = sum(1 for xi,yi in zip(X3,y3) if gda.predict(xi)==yi)
    print(f"   3-class GDA accuracy: {correct}/{len(y3)} = {correct/len(y3):.1%}")
    print(f"   means = {{0: {gda.means[0]}}}")

    # --- 3. EM for GMM ---
    print("\n📋 3. EM for Gaussian Mixture Model (1D)")
    data = ([random.gauss(-3, 0.8) for _ in range(100)] +
            [random.gauss(3, 0.8) for _ in range(100)])
    random.shuffle(data)
    means, vars, weights, lls = em_gmm_1d(data, k=2, epochs=30)
    print(f"   True means: [-3, 3]")
    print(f"   EM recovered means: {sorted(means)}")
    print(f"   Log-likelihood: epoch 1 = {lls[0]:.1f} → epoch 30 = {lls[-1]:.1f}")
    print(f"   💡 EM 单调递增 log-likelihood（保证收敛到局部最优，非全局）")

    # --- 4. ID3 ---
    print("\n📋 4. ID3 Decision Tree")
    # Classic "play tennis" dataset
    X_t = [
        ['Sunny','Hot','High','Weak'],['Sunny','Hot','High','Strong'],
        ['Overcast','Hot','High','Weak'],['Rain','Mild','High','Weak'],
        ['Rain','Cool','Normal','Weak'],['Rain','Cool','Normal','Strong'],
        ['Overcast','Cool','Normal','Strong'],['Sunny','Mild','High','Weak'],
        ['Sunny','Cool','Normal','Weak'],['Rain','Mild','Normal','Weak'],
        ['Sunny','Mild','Normal','Strong'],['Overcast','Mild','High','Strong'],
        ['Overcast','Hot','Normal','Weak'],['Rain','Mild','High','Strong'],
    ]
    y_t = ['No','No','Yes','Yes','Yes','No','Yes','No',
           'Yes','Yes','Yes','Yes','Yes','No']
    tree = id3(X_t, y_t, features=[0,1,2,3])
    correct = sum(1 for xi,yi in zip(X_t,y_t) if id3_predict(tree,xi)==yi)
    print(f"   Play Tennis: training accuracy = {correct}/{len(y_t)}")
    print(f"   Root split feature: {tree.feature} (0=Outlook)")
    print(f"   💡 ID3 用信息增益，偏向多值特征（C4.5 改用 gain ratio 修正）")

    print("\n✅ 10-701 Intro ML 完成！")
    print("   覆盖：Logistic Regression / GDA / EM-GMM / ID3")


if __name__ == "__main__":
    demo()
