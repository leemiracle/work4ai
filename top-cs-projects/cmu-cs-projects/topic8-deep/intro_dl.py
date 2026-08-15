"""
10-315 / 11-667 Introduction to Deep Learning (CMU)
================================================
覆盖主题（对应 lecture）：
- MLP + Backpropagation (numpy from scratch)
- CNN forward pass (conv2d + maxpool)
- Simple RNN (sequential processing)
- Mini Self-Attention (scaled dot-product)

核心教材/论文：
- "Rumelhart Hinton Williams 1986 Nature" — backpropagation
- Vaswani et al. "Attention Is All You Need" arXiv:1706.03762 (NeurIPS 2017)
- LeCun et al. "Gradient-Based Learning Applied to Document Recognition" 1998 IEEE Proc
- "Goodfellow Bengio Courville Deep Learning" 2016 MIT Press

本文件实现：
- MLP with manual backprop (forward, backward, SGD)
- Conv2d + MaxPool forward (nested loops, no library)
- Vanilla RNN forward pass
- Scaled dot-product self-attention

运行：
    python3 intro_dl.py
"""
from __future__ import annotations
import math
import random

# ============ 1. MLP + Backprop (pure Python) ============

def mat_vec(W, x):  # W[m][n] * x[n] → m
    return [sum(W[i][j]*x[j] for j in range(len(x))) for i in range(len(W))]

def relu(x):
    return [max(0, v) for v in x]

def relu_grad(x):
    return [1.0 if v > 0 else 0.0 for v in x]

def softmax(xs):
    mx = max(xs)
    exps = [math.exp(x - mx) for x in xs]
    s = sum(exps)
    return [e/s for e in exps]

class MLP:
    """2-layer MLP: input → hidden(ReLU) → output(softmax)."""

    def __init__(self, n_in, n_hid, n_out):
        self.W1 = [[random.gauss(0, 0.5) for _ in range(n_in)] for _ in range(n_hid)]
        self.b1 = [0.0]*n_hid
        self.W2 = [[random.gauss(0, 0.5) for _ in range(n_hid)] for _ in range(n_out)]
        self.b2 = [0.0]*n_out

    def forward(self, x):
        self.x = x
        self.z1 = mat_vec(self.W1, x)
        self.z1 = [z+b for z,b in zip(self.z1, self.b1)]
        self.a1 = relu(self.z1)
        self.z2 = mat_vec(self.W2, self.a1)
        self.z2 = [z+b for z,b in zip(self.z2, self.b2)]
        self.a2 = softmax(self.z2)
        return self.a2

    def backward(self, y_true, lr=0.1):
        """Backprop with cross-entropy loss."""
        # dL/dz2 = softmax_output - one_hot
        dz2 = [a - t for a, t in zip(self.a2, y_true)]
        # dL/dW2, dL/db2
        dW2 = [[dz2[i]*self.a1[j] for j in range(len(self.a1))] for i in range(len(dz2))]
        db2 = dz2
        # dL/da1
        da1 = [sum(self.W2[i][j]*dz2[i] for i in range(len(dz2))) for j in range(len(self.a1))]
        # dL/dz1 = da1 * relu'
        dz1 = [da1[j]*relu_grad(self.z1)[j] for j in range(len(self.a1))]
        # dL/dW1, dL/db1
        dW1 = [[dz1[i]*self.x[j] for j in range(len(self.x))] for i in range(len(dz1))]
        db1 = dz1
        # update
        for i in range(len(self.W2)):
            for j in range(len(self.W2[i])):
                self.W2[i][j] -= lr * dW2[i][j]
            self.b2[i] -= lr * db2[i]
        for i in range(len(self.W1)):
            for j in range(len(self.W1[i])):
                self.W1[i][j] -= lr * dW1[i][j]
            self.b1[i] -= lr * db1[i]

    def loss(self, y_true):
        return -sum(t * math.log(max(p, 1e-10)) for t, p in zip(y_true, self.a2))


# ============ 2. CNN Forward Pass ============

def conv2d(image, kernel, stride=1):
    """2D convolution (cross-correlation). image & kernel are 2D lists."""
    ih, iw = len(image), len(image[0])
    kh, kw = len(kernel), len(kernel[0])
    oh = (ih - kh) // stride + 1
    ow = (iw - kw) // stride + 1
    output = [[0.0]*ow for _ in range(oh)]
    for i in range(oh):
        for j in range(ow):
            val = 0.0
            for ki in range(kh):
                for kj in range(kw):
                    val += image[i*stride+ki][j*stride+kj] * kernel[ki][kj]
            output[i][j] = val
    return output

def maxpool2d(image, pool_size=2, stride=2):
    ih, iw = len(image), len(image[0])
    oh = (ih - pool_size) // stride + 1
    ow = (iw - pool_size) // stride + 1
    output = [[0.0]*ow for _ in range(oh)]
    for i in range(oh):
        for j in range(ow):
            mx = -math.inf
            for pi in range(pool_size):
                for pj in range(pool_size):
                    mx = max(mx, image[i*stride+pi][j*stride+pj])
            output[i][j] = mx
    return output


# ============ 3. Simple RNN Forward ============

def rnn_forward(inputs, W_xh, W_hh, b_h, h0=None):
    """
    Vanilla RNN forward: h_t = tanh(W_xh @ x_t + W_hh @ h_{t-1} + b_h)
    inputs: list of vectors. Returns hidden states.
    """
    n_hid = len(W_hh)
    if h0 is None:
        h0 = [0.0]*n_hid
    h = h0
    hidden_states = []
    for x in inputs:
        # W_xh @ x + W_hh @ h + b
        new_h = []
        for i in range(n_hid):
            val = b_h[i]
            val += sum(W_xh[i][j]*x[j] for j in range(len(x)))
            val += sum(W_hh[i][j]*h[j] for j in range(n_hid))
            new_h.append(math.tanh(val))
        h = new_h
        hidden_states.append(h)
    return hidden_states


# ============ 4. Self-Attention ============

def scaled_dot_product_attention(Q, K, V):
    """
    Attention(Q,K,V) = softmax(Q·K^T / sqrt(d_k)) · V
    Q,K,V: [seq_len, d_k] (list of lists)
    """
    seq_len = len(Q)
    d_k = len(Q[0])
    # scores = Q @ K^T / sqrt(d_k)
    scores = [[0.0]*seq_len for _ in range(seq_len)]
    for i in range(seq_len):
        for j in range(seq_len):
            scores[i][j] = sum(Q[i][d]*K[j][d] for d in range(d_k)) / math.sqrt(d_k)
    # softmax per row
    attn = [[0.0]*seq_len for _ in range(seq_len)]
    for i in range(seq_len):
        mx = max(scores[i])
        exps = [math.exp(s - mx) for s in scores[i]]
        s = sum(exps)
        attn[i] = [e/s for e in exps]
    # output = attn @ V
    d_v = len(V[0])
    output = [[0.0]*d_v for _ in range(seq_len)]
    for i in range(seq_len):
        for d in range(d_v):
            output[i][d] = sum(attn[i][j]*V[j][d] for j in range(seq_len))
    return output, attn


# ============ Demo ============

def demo():
    print("=" * 60)
    print("10-315/11-667 Intro DL: MLP, CNN, RNN, Attention")
    print("=" * 60)
    random.seed(42)

    # --- 1. MLP ---
    print("\n📋 1. MLP + Backpropagation")
    mlp = MLP(n_in=4, n_hid=8, n_out=3)
    # Toy dataset: classify input patterns
    X = [[0,0,0,1],[0,1,0,0],[1,0,0,0],[1,1,1,0],[0,0,1,1],[1,1,0,1]]
    Y = [[1,0,0],[0,1,0],[1,0,0],[0,0,1],[0,1,0],[0,0,1]]
    losses = []
    for epoch in range(100):
        total_loss = 0
        for x, y in zip(X, Y):
            mlp.forward(x)
            mlp.backward(y, lr=0.5)
            total_loss += mlp.loss(y)
        losses.append(total_loss/len(X))
    # test
    correct = 0
    for x, y in zip(X, Y):
        pred = mlp.forward(x)
        if pred.index(max(pred)) == y.index(max(y)):
            correct += 1
    print(f"   MLP (4→8→3): accuracy = {correct}/{len(X)}")
    print(f"   Loss: epoch 1 = {losses[0]:.3f} → epoch 100 = {losses[-1]:.3f}")

    # --- 2. CNN ---
    print("\n📋 2. CNN Forward Pass (Conv2d + MaxPool)")
    # Edge detection on 6x6 "image"
    image = [
        [0,0,0,1,1,1],[0,0,0,1,1,1],[0,0,0,1,1,1],
        [0,0,0,1,1,1],[0,0,0,1,1,1],[0,0,0,1,1,1],
    ]
    edge_kernel = [[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]  # Laplacian
    conv_out = conv2d(image, edge_kernel)
    pool_out = maxpool2d(conv_out)
    print(f"   Image: 6×6 (left=0, right=1)")
    print(f"   Conv output: {len(conv_out)}×{len(conv_out[0])} (3×3 Laplacian kernel)")
    print(f"   Pool output: {len(pool_out)}×{len(pool_out[0])}")
    print(f"   Conv center row: [{', '.join(f'{v:6.0f}' for v in conv_out[1])}]")
    print(f"   💡 边缘检测器在 0→1 边界处响应最大（卷积核学习边缘）")

    # --- 3. RNN ---
    print("\n📋 3. Simple RNN Forward")
    W_xh = [[0.5, -0.3],[0.1, 0.8]]
    W_hh = [[0.9, -0.1],[0.2, 0.7]]
    b_h = [0.0, 0.0]
    # Sequence of 2D inputs
    inputs = [[1,0],[0,1],[1,1],[0,0],[1,0]]
    hidden_states = rnn_forward(inputs, W_xh, W_hh, b_h)
    print(f"   Input sequence (len={len(inputs)}, dim=2)")
    print(f"   Final hidden state: [{hidden_states[-1][0]:.4f}, {hidden_states[-1][1]:.4f}]")
    print(f"   Hidden norms over time: {[math.sqrt(sum(h*h for h in hs)) for hs in hidden_states]}")
    print(f"   💡 RNN 隐状态是所有历史输入的压缩（但长序列会梯度消失/爆炸）")

    # --- 4. Self-Attention ---
    print("\n📋 4. Scaled Dot-Product Self-Attention")
    # 3 tokens, 4-dim
    Q = [[1,0,0,0],[0,1,0,0],[1,1,0,0]]
    K = [[1,0,0,0],[0,1,0,0],[0,0,1,0]]
    V = [[1,0],[0,1],[1,1]]
    output, attn = scaled_dot_product_attention(Q, K, V)
    print(f"   Attention weights matrix (3×3):")
    for row in attn:
        print(f"     [{', '.join(f'{v:.3f}' for v in row)}]")
    print(f"   Output[0] = [{output[0][0]:.3f}, {output[0][1]:.3f}]")
    print(f"   💡 注意力是凸组合（行和=1），Q[0]=[1,0,0,0] 主要关注 K[0]→V[0]")

    print("\n✅ 10-315/11-667 Intro DL 完成！")
    print("   覆盖：MLP+Backprop / Conv2d+MaxPool / RNN / Self-Attention")


if __name__ == "__main__":
    demo()
