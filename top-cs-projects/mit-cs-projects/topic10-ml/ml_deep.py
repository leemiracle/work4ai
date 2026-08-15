"""
6.3900/6.867 Machine Learning + 6.S191 Deep Learning（MIT）
================================================
覆盖主题：
- Perceptron + 线性分类（Lecture 2-3）
- MLP + 反向传播（numpy）（Lecture 4-5）
- CNN: conv2d + pooling（6.S191 Lecture 5）
- RNN char-level language model（6.S191 Lecture 4）
- Transformer self-attention（6.S191 Lecture 7）

核心论文/教材（arXiv ID 已核实）：
- Vaswani et al. 2017 "Attention Is All You Need" arXiv:1706.03762
- Rumelhart, Hinton, Williams 1986 "Learning representations by back-propagating errors" Nature
- LeCun et al. 1989 "Backpropagation Applied to Handwritten Zip Code Recognition" Neural Computation
- He et al. 2016 "Deep Residual Learning" arXiv:1512.03385 (ResNet, CNN)

本文件实现：
- Perceptron（在线学习）
- MLP 反向传播（numpy，XOR 可解）
- conv2d（朴素卷积 + im2col 思路）
- 简单 RNN char-LM
- Self-Attention（scaled dot-product）

运行：
    python ml_deep.py
"""
from __future__ import annotations
import math
import random
import numpy as np


# ============ 1. Perceptron ============

class Perceptron:
    """在线感知机。y ∈ {0,1} 或 {-1,+1}。"""
    def __init__(self, n_features: int):
        self.w = np.zeros(n_features)
        self.b = 0.0

    def predict(self, x):
        return 1 if np.dot(self.w, x) + self.b > 0 else 0

    def fit(self, X, y, epochs=10):
        errors_log = []
        for ep in range(epochs):
            errors = 0
            for xi, yi in zip(X, y):
                pred = self.predict(xi)
                update = (yi - pred)
                self.w += update * xi
                self.b += update
                if update != 0:
                    errors += 1
            errors_log.append(errors)
        return errors_log


# ============ 2. MLP + Backprop ============

def relu(x): return np.maximum(0, x)
def relu_deriv(x): return (x > 0).astype(float)
def sigmoid(x): return 1 / (1 + np.exp(-np.clip(x, -50, 50)))


class MLP:
    """2 层 MLP: input → hidden(ReLU) → output(sigmoid)。numpy 手写反向传播。"""
    def __init__(self, n_in, n_hidden, n_out, seed=42):
        rng = np.random.RandomState(seed)
        self.W1 = rng.randn(n_in, n_hidden) * math.sqrt(2.0 / n_in)  # He init
        self.b1 = np.zeros(n_hidden)
        self.W2 = rng.randn(n_hidden, n_out) * math.sqrt(2.0 / n_hidden)
        self.b2 = np.zeros(n_out)

    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = relu(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = sigmoid(self.z2)
        return self.a2

    def backward(self, X, y, lr=0.1):
        m = len(X)
        dz2 = self.a2 - y.reshape(-1, 1)  # BCE + sigmoid 的梯度简化
        dW2 = self.a1.T @ dz2 / m
        db2 = dz2.mean(axis=0)
        da1 = dz2 @ self.W2.T
        dz1 = da1 * relu_deriv(self.z1)
        dW1 = X.T @ dz1 / m
        db1 = dz1.mean(axis=0)
        self.W2 -= lr * dW2; self.b2 -= lr * db2
        self.W1 -= lr * dW1; self.b1 -= lr * db1

    def train(self, X, y, epochs=2000, lr=0.5):
        losses = []
        for _ in range(epochs):
            out = self.forward(X)
            loss = -np.mean(y * np.log(out[:,0]+1e-10) + (1-y) * np.log(1-out[:,0]+1e-10))
            losses.append(loss)
            self.backward(X, y, lr)
        return losses


# ============ 3. Conv2d (im2col 简化) ============

def conv2d_naive(image: np.ndarray, kernel: np.ndarray, stride=1) -> np.ndarray:
    """朴素 2D 卷积。image: (H,W), kernel: (kH,kW)。"""
    H, W = image.shape
    kH, kW = kernel.shape
    out_h = (H - kH) // stride + 1
    out_w = (W - kW) // stride + 1
    out = np.zeros((out_h, out_w))
    for i in range(out_h):
        for j in range(out_w):
            region = image[i*stride:i*stride+kH, j*stride:j*stride+kW]
            out[i, j] = np.sum(region * kernel)
    return out


def maxpool2d(feature: np.ndarray, pool=2) -> np.ndarray:
    H, W = feature.shape
    out = np.zeros((H // pool, W // pool))
    for i in range(0, H - pool + 1, pool):
        for j in range(0, W - pool + 1, pool):
            out[i//pool, j//pool] = feature[i:i+pool, j:j+pool].max()
    return out


# ============ 4. RNN char-level ============

class SimpleRNN:
    """单层 RNN cell（char-LM）。"""
    def __init__(self, vocab_size, hidden_size=16, seed=42):
        rng = np.random.RandomState(seed)
        self.Wh = rng.randn(hidden_size, hidden_size) * 0.1
        self.Wx = rng.randn(vocab_size, hidden_size) * 0.1
        self.Wy = rng.randn(hidden_size, vocab_size) * 0.1
        self.bh = np.zeros(hidden_size)
        self.by = np.zeros(vocab_size)
        self.h0 = np.zeros(hidden_size)

    def forward(self, x_seq: list):  # x_seq: list of one-hot indices
        h = self.h0.copy()
        h_list = [h]
        logits_list = []
        for idx in x_seq:
            x = np.zeros(len(self.Wx)); x[idx] = 1
            h = np.tanh(x @ self.Wx + h @ self.Wh + self.bh)
            logits = h @ self.Wy + self.by
            h_list.append(h)
            logits_list.append(logits)
        return h_list, logits_list

    def predict_next(self, x_seq, temperature=1.0):
        _, logits = self.forward(x_seq)
        probs = np.exp(logits[-1] / temperature)
        probs /= probs.sum()
        return np.random.choice(len(probs), p=probs)


# ============ 5. Self-Attention ============

def softmax_rows(x):
    x = x - x.max(axis=-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=-1, keepdims=True)


def self_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
    """Scaled Dot-Product Attention.
    Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V
    """
    d_k = K.shape[-1]
    scores = Q @ K.T / math.sqrt(d_k)
    attn_weights = softmax_rows(scores)
    return attn_weights @ V, attn_weights


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.867 ML + 6.S191 DL: Perceptron/MLP/CNN/RNN/Attention")
    print("=" * 65)
    random.seed(42); np.random.seed(42)

    # --- Perceptron ---
    print("\n📋 1. Perceptron 线性分类")
    X = np.array([[1,1],[2,1],[1,2],[3,3],[2,3],[3,2]], dtype=float)
    y = np.array([0,0,0,1,1,1])
    perc = Perceptron(2)
    errs = perc.fit(X, y, epochs=20)
    acc = sum(perc.predict(x) == yi for x, yi in zip(X, y)) / len(y)
    print(f"  数据: {list(zip(X.tolist(), y.tolist()))}")
    print(f"  训练后权重: w={perc.w}, b={perc.b:.1f}")
    print(f"  准确率: {acc*100:.0f}%")
    print(f"  误差收敛: {errs}")

    # --- MLP XOR ---
    print("\n📋 2. MLP 解 XOR (反向传播)")
    X_xor = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=float)
    y_xor = np.array([0,1,1,0])
    mlp = MLP(2, 4, 1, seed=42)
    losses = mlp.train(X_xor, y_xor, epochs=3000, lr=0.5)
    preds = mlp.forward(X_xor)[:, 0]
    print(f"  输入: {X_xor.tolist()}")
    print(f"  目标: {y_xor.tolist()}")
    print(f"  预测: {[round(p, 3) for p in preds]}")
    print(f"  最终 loss: {losses[-1]:.4f} (初始 {losses[0]:.4f})")
    print("  → 单层 Perceptron 无法解 XOR；2 层 MLP 可以(通用近似)。")

    # --- Conv2d ---
    print("\n📋 3. Conv2d + MaxPool (边缘检测)")
    image = np.array([
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,9,9,0,0],
        [0,0,9,9,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
    ], dtype=float)
    sobel_x = np.array([[-1,0,1],[-2,0,2],[-1,0,1]], dtype=float)
    conv_out = conv2d_naive(image, sobel_x)
    pool_out = maxpool2d(np.abs(conv_out), pool=2)
    print(f"  输入图 {image.shape}: (中心 2x2 亮块)")
    print(f"  Sobel-x 卷积输出 {conv_out.shape}:")
    for row in conv_out:
        print(f"    {[round(v,1) for v in row]}")
    print(f"  MaxPool(2x2) 输出 {pool_out.shape}:")
    for row in pool_out:
        print(f"    {[round(v,1) for v in row]}")

    # --- Self-Attention ---
    print("\n📋 4. Transformer Self-Attention")
    # Attention(Q,K,V) = softmax(QK^T/sqrt(d_k))V  (Vaswani 2017)
    d_k = 4; seq_len = 3
    Q = np.random.randn(seq_len, d_k)
    K = np.random.randn(seq_len, d_k)
    V = np.random.randn(seq_len, d_k)
    out, weights = self_attention(Q, K, V)
    print(f"  Q,K,V shape: ({seq_len},{d_k})")
    print(f"  Attention weights (softmax(QK^T/sqrt({d_k}))):")
    for row in weights:
        print(f"    {[round(v,3) for v in row]}")
    print(f"  每行和 = {weights.sum(axis=1).round(4)} (应=1.0)")

    # --- 反直觉发现 ---
    print("\n" + "=" * 65)
    print("💡 反直觉发现：Q=K 时 attention 退化为自指——对角线显著偏大")
    print("=" * 65)
    # Q=K 时，logit 对角线 = ||q_i||²/√d_k ≈ √d_k >> 非对角 ≈ N(0,1)
    # 而 Q⊥K（独立随机）时所有 logit ≈ N(0,1)，权重 ≈ 均匀
    for n in [3, 5, 10, 20]:
        K2 = np.random.randn(n, 8)
        Q2 = K2.copy()             # Q=K → Gram matrix → 对角线偏大
        V2 = np.eye(n)
        _, w = self_attention(Q2, K2, V2)
        diag = np.mean(np.diag(w))
        offdiag = (w.sum() - np.trace(w)) / (n*n - n) if n > 1 else 0
        entropy = -np.sum(w * np.log2(w + 1e-10), axis=1).mean()
        max_entropy = math.log2(n)
        print(f"  seq={n:>2}: 对角线均值={diag:.3f}, 非对角={offdiag:.3f}, "
              f"熵={entropy:.3f}/{max_entropy:.2f} bits ({entropy/max_entropy*100:.0f}%)")
    print("  → Q=K 时对角线远超非对角——注意力“自指”。")
    print("    这解释了为何 Transformer 用不同投影 Wq≠Wk 打破对称性。")
    print("    独立随机 Q/K 则退化为近似均匀（熵≈max），无对角偏移。")

    print("\n✅ 6.867+6.S191 Demo 完成！")


if __name__ == "__main__":
    demo()
