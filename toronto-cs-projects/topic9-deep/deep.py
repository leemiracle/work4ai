"""
CSC 413 / CSC 513 Neural Networks & Deep Learning (University of Toronto)
=========================================================================
覆盖主题：
- MLP + 反向传播
- CNN（卷积 + 池化，从零实现）
- RNN + LSTM
- Self-Attention + Transformer Block

核心论文/教材：
- Vaswani et al. "Attention Is All You Need" arXiv:1706.03762
- Hochreiter & Schmidhuber "Long Short-Term Memory" Neural Computation, 1997
- Goodfellow, Bengio, Courville "Deep Learning" (2016, Ch.6-10)

本文件实现（纯 numpy）：
- MLP（前向 + 反向传播，含 SGD/Adam）
- Conv2D + MaxPool（im2col 前向 + col2im 反向传播）
- LSTM 单元（门控机制）
- Self-Attention + Multi-Head + Transformer Encoder Block

运行：
    python deep.py
"""
from __future__ import annotations
import numpy as np


# ============ 1. MLP + Backprop ============

class MLP:
    """
    Multi-Layer Perceptron with Backpropagation
    Forward:  h_l = σ(W_l h_{l-1} + b_l)
    Backward: δ_L = ∇L ⊙ σ'(z_L)
              δ_l = (W_{l+1}^T δ_{l+1}) ⊙ σ'(z_l)
              ∂L/∂W_l = δ_l h_{l-1}^T
    """

    def __init__(self, sizes, lr=0.01):
        self.sizes = sizes
        self.lr = lr
        self.weights = [np.random.randn(n_out, n_in) * np.sqrt(2.0 / n_in)
                        for n_in, n_out in zip(sizes[:-1], sizes[1:])]
        self.biases = [np.zeros((n_out, 1)) for n_out in sizes[1:]]

    @staticmethod
    def _relu(z):
        return np.maximum(0, z)

    @staticmethod
    def _relu_deriv(z):
        return (z > 0).astype(float)

    @staticmethod
    def _softmax(z):
        e = np.exp(z - z.max(axis=0, keepdims=True))
        return e / e.sum(axis=0, keepdims=True)

    def forward(self, X):
        """X: (n_features, n_samples)"""
        activations = [X]
        zs = []
        a = X
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            z = w @ a + b
            zs.append(z)
            if i == len(self.weights) - 1:
                a = self._softmax(z)  # 输出层 softmax
            else:
                a = self._relu(z)
            activations.append(a)
        return activations, zs

    def backward(self, X, y_onehot):
        activations, zs = self.forward(X)
        m = X.shape[1]

        # 输出层梯度（softmax + CE）
        delta = (activations[-1] - y_onehot) / m

        grads_w = [None] * len(self.weights)
        grads_b = [None] * len(self.biases)

        for l in range(len(self.weights) - 1, -1, -1):
            grads_w[l] = delta @ activations[l].T
            grads_b[l] = np.sum(delta, axis=1, keepdims=True)
            if l > 0:
                delta = (self.weights[l].T @ delta) * self._relu_deriv(zs[l - 1])

        # 更新
        for l in range(len(self.weights)):
            self.weights[l] -= self.lr * grads_w[l]
            self.biases[l] -= self.lr * grads_b[l]

    def loss(self, X, y_onehot):
        activations, _ = self.forward(X)
        return -np.mean(np.sum(y_onehot * np.log(activations[-1] + 1e-10), axis=0))

    def predict(self, X):
        activations, _ = self.forward(X)
        return np.argmax(activations[-1], axis=0)


# ============ 2. CNN (Conv2D + MaxPool) ============

class Conv2D:
    """
    2D 卷积层（im2col 实现，教学用）
    Forward:  Y[b,oc,i,j] = Σ_c Σ_m Σ_n W[oc,c,m,n] X[b,c,i+m,j+n] + b[oc]
    Backward: im2col 重排输入 patches → matmul 算梯度 → col2im 还原输入梯度
    """

    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, lr=0.1):
        self.in_ch = in_channels
        self.out_ch = out_channels
        self.k = kernel_size
        self.stride = stride
        self.lr = lr
        scale = np.sqrt(2.0 / (in_channels * kernel_size ** 2))
        self.W = np.random.randn(out_channels, in_channels, kernel_size, kernel_size) * scale
        self.b = np.zeros(out_channels)

    def _im2col(self, X):
        """X:(batch,C,H,W) → cols:(batch, H_out*W_out, C*k*k)，C-major 展开以匹配 W.reshape"""
        batch, C, H, W = X.shape
        H_out = (H - self.k) // self.stride + 1
        W_out = (W - self.k) // self.stride + 1
        cols = np.zeros((batch, H_out, W_out, C * self.k * self.k))
        for i in range(H_out):
            hs = i * self.stride
            for j in range(W_out):
                ws = j * self.stride
                patch = X[:, :, hs:hs + self.k, ws:ws + self.k]       # (batch,C,k,k)
                cols[:, i, j, :] = patch.reshape(batch, -1)           # C-major flatten
        return cols.reshape(batch, H_out * W_out, C * self.k * self.k), H_out, W_out

    def _col2im(self, dcols):
        """dcols:(batch, H_out*W_out, C*k*k) → dX:(batch,C,H,W)（累加重叠区域）"""
        batch, C, H, W = self._X_shape
        H_out, W_out = self._H_out, self._W_out
        dX = np.zeros((batch, C, H, W))
        dcols_3d = dcols.reshape(batch, H_out, W_out, C, self.k, self.k)
        for i in range(H_out):
            hs = i * self.stride
            for j in range(W_out):
                ws = j * self.stride
                dX[:, :, hs:hs + self.k, ws:ws + self.k] += dcols_3d[:, i, j]
        return dX

    def forward(self, X):
        """X:(batch,in_ch,H,W) → Y:(batch,out_ch,H_out,W_out)"""
        self._X_shape = X.shape
        cols, H_out, W_out = self._im2col(X)
        self._cols = cols
        self._H_out, self._W_out = H_out, W_out
        W_row = self.W.reshape(self.out_ch, -1)               # (out_ch, C*k*k)
        Y = np.matmul(cols, W_row.T) + self.b                # (batch, pos, out_ch)
        Y = Y.transpose(0, 2, 1).reshape(X.shape[0], self.out_ch, H_out, W_out)
        return Y

    def backward(self, dY):
        """dY:(batch,out_ch,H_out,W_out) → dX:(batch,in_ch,H,W)；同时缓存 dW, db"""
        batch = dY.shape[0]
        pos = self._H_out * self._W_out
        dY_flat = dY.transpose(0, 2, 3, 1).reshape(batch, pos, self.out_ch)
        W_row = self.W.reshape(self.out_ch, -1)
        self.dW = np.einsum('bpo,bpi->oi', dY_flat, self._cols).reshape(self.W.shape)
        self.db = dY_flat.sum(axis=(0, 1))
        dcols = np.matmul(dY_flat, W_row)                    # (batch, pos, C*k*k)
        return self._col2im(dcols)

    def update(self, lr=None):
        lr = lr if lr is not None else self.lr
        self.W -= lr * self.dW
        self.b -= lr * self.db


class MaxPool2D:
    """2x2 Max Pooling（forward + backward via argmax mask）"""

    def forward(self, X):
        batch, ch, H, W = X.shape
        self._X_shape = X.shape
        H_out, W_out = H // 2, W // 2
        Y = np.zeros((batch, ch, H_out, W_out))
        self._mask = np.zeros((batch, ch, H, W))
        for b in range(batch):
            for c in range(ch):
                for i in range(H_out):
                    for j in range(W_out):
                        patch = X[b, c, 2 * i:2 * i + 2, 2 * j:2 * j + 2]
                        idx = np.unravel_index(np.argmax(patch), patch.shape)
                        Y[b, c, i, j] = patch[idx]
                        self._mask[b, c, 2 * i + idx[0], 2 * j + idx[1]] = 1.0
        return Y

    def backward(self, dY):
        """dY:(batch,ch,H_out,W_out) → dX:(batch,ch,H,W)；梯度只传给每块的 argmax 位置"""
        batch, ch, H, W = self._X_shape
        H_out, W_out = H // 2, W // 2
        dX = np.zeros(self._X_shape)
        for b in range(batch):
            for c in range(ch):
                for i in range(H_out):
                    for j in range(W_out):
                        dX[b, c, 2 * i:2 * i + 2, 2 * j:2 * j + 2] = (
                            self._mask[b, c, 2 * i:2 * i + 2, 2 * j:2 * j + 2] * dY[b, c, i, j]
                        )
        return dX


def demo_cnn():
    print("\n📋 2. CNN (Conv2D + MaxPool)")
    rng = np.random.RandomState(42)
    # 模拟一张 8x8 图像，1 通道
    X = rng.randn(1, 1, 8, 8)

    conv = Conv2D(in_channels=1, out_channels=4, kernel_size=3)
    Y_conv = conv.forward(X)
    print(f"   输入: {X.shape}")
    print(f"   Conv2D(1→4, k=3): {Y_conv.shape}")

    pool = MaxPool2D()
    Y_pool = pool.forward(Y_conv)
    print(f"   MaxPool2D(2x2):   {Y_pool.shape}")

    # 边缘检测演示
    print(f"\n   边缘检测演示（Sobel-like kernel）:")
    edge_filter = Conv2D(1, 1, kernel_size=3)
    edge_filter.W[0, 0] = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    edge_filter.b[0] = 0

    # 创建有边缘的图像
    test_img = np.zeros((1, 1, 6, 6))
    test_img[0, 0, :, 3:] = 1.0  # 左暗右亮，垂直边缘
    edge_output = edge_filter.forward(test_img)
    print(f"   输入图: 左半=0, 右半=1, 大小 {test_img.shape}")
    print(f"   Sobel输出 (中间列):")
    for row in edge_output[0, 0, :, :]:
        print(f"     {''.join(f'{v:6.1f}' for v in row)}")
    print(f"   → 边缘在第3列附近响应最大（垂直边缘）")

    # Conv2D + MaxPool 反向传播验证
    print(f"\n   Conv2D + MaxPool 反向传播验证（im2col + col2im）:")
    conv_tr = Conv2D(in_channels=1, out_channels=2, kernel_size=3, lr=0.5)
    X_tr = rng.randn(2, 1, 6, 6)
    target = rng.randn(2, 2, 4, 4)  # conv(1→2, k=3): 6×6 → 4×4

    def _mse(a, t):
        return 0.5 * np.mean((a - t) ** 2)

    losses_conv = []
    for step in range(60):
        Y = conv_tr.forward(X_tr)
        dY = (Y - target) / Y.size           # dMSE/dY
        conv_tr.backward(dY)                  # im2col → dW, db, dX(col2im)
        conv_tr.update()
        losses_conv.append(_mse(Y, target))
    print(f"   Conv2D 训练 60 步: MSE {losses_conv[0]:.4f} → {losses_conv[-1]:.4f}"
          f"（梯度正确则 loss 下降）")

    # MaxPool backward 验证：梯度只传给每块 argmax 位置
    pool_tr = MaxPool2D()
    Xp = np.array([[[[1., 0., 3., 0.], [0., 0., 0., 0.]]]])  # 1×1×2×2: max@0, max@2
    Yp = pool_tr.forward(Xp)
    dXp = pool_tr.backward(np.ones_like(Yp))
    nonzero = np.where(dXp[0, 0].ravel() != 0)[0].tolist()
    print(f"   MaxPool backward: 梯度位置 → {nonzero}（应=[0, 2]，即两个 max 位置）")


# ============ 3. LSTM ============

class LSTMCell:
    """
    LSTM Cell:
    Gates:
      f_t = σ(W_f [h_{t-1}, x_t] + b_f)  (forget gate)
      i_t = σ(W_i [h_{t-1}, x_t] + b_i)  (input gate)
      g_t = tanh(W_g [h_{t-1}, x_t] + b_g) (candidate)
      o_t = σ(W_o [h_{t-1}, x_t] + b_o)  (output gate)

    State update:
      C_t = f_t ⊙ C_{t-1} + i_t ⊙ g_t
      h_t = o_t ⊙ tanh(C_t)
    """

    def __init__(self, input_size, hidden_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        concat_size = input_size + hidden_size
        scale = np.sqrt(2.0 / concat_size)

        self.W_f = np.random.randn(hidden_size, concat_size) * scale
        self.b_f = np.zeros((hidden_size, 1))
        self.W_i = np.random.randn(hidden_size, concat_size) * scale
        self.b_i = np.zeros((hidden_size, 1))
        self.W_g = np.random.randn(hidden_size, concat_size) * scale
        self.b_g = np.zeros((hidden_size, 1))
        self.W_o = np.random.randn(hidden_size, concat_size) * scale
        self.b_o = np.zeros((hidden_size, 1))

    @staticmethod
    def _sigmoid(z):
        return 1 / (1 + np.exp(-np.clip(z, -250, 250)))

    def forward(self, x_seq):
        """
        x_seq: (seq_len, input_size, 1)
        returns: outputs (list of h_t)
        """
        h = np.zeros((self.hidden_size, 1))
        C = np.zeros((self.hidden_size, 1))
        outputs = []
        gate_stats = {'f': [], 'i': [], 'o': []}

        for x in x_seq:
            concat = np.vstack([h, x])

            f = self._sigmoid(self.W_f @ concat + self.b_f)
            i = self._sigmoid(self.W_i @ concat + self.b_i)
            g = np.tanh(self.W_g @ concat + self.b_g)
            o = self._sigmoid(self.W_o @ concat + self.b_o)

            C = f * C + i * g
            h = o * np.tanh(C)
            outputs.append(h.copy())

            gate_stats['f'].append(np.mean(f))
            gate_stats['i'].append(np.mean(i))
            gate_stats['o'].append(np.mean(o))

        return outputs, gate_stats


def demo_lstm():
    print("\n📋 3. LSTM Cell")
    lstm = LSTMCell(input_size=4, hidden_size=8)
    # 序列输入
    seq_len = 10
    x_seq = [np.random.randn(4, 1) * 0.5 for _ in range(seq_len)]
    outputs, gates = lstm.forward(x_seq)

    print(f"   序列长度: {seq_len}, 输入维度: 4, 隐藏维度: 8")
    print(f"\n   门控激活均值（揭示 LSTM 记忆机制）:")
    print(f"   {'t':>3} {'forget':>8} {'input':>8} {'output':>8} {'h_norm':>8}")
    for t in range(seq_len):
        h_norm = np.linalg.norm(outputs[t])
        print(f"   {t:3d} {gates['f'][t]:8.3f} {gates['i'][t]:8.3f} "
              f"{gates['o'][t]:8.3f} {h_norm:8.3f}")

    print(f"\n   反直觉发现：随机初始化时 forget gate 均值≈0.5")
    print(f"   → 工程惯例：LSTM 偏置 forget gate 初始化为 +1（强制早期保留记忆）")


# ============ 4. Self-Attention + Transformer ============

class SelfAttention:
    """
    Scaled Dot-Product Attention:
    Attention(Q,K,V) = softmax(QK^T / √d_k) V

    Multi-Head: head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
               MultiHead = Concat(head_1,...,head_h) W^O
    """

    def __init__(self, d_model=64, n_heads=4):
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        scale = np.sqrt(2.0 / d_model)

        self.W_q = [np.random.randn(d_model, self.d_k) * scale for _ in range(n_heads)]
        self.W_k = [np.random.randn(d_model, self.d_k) * scale for _ in range(n_heads)]
        self.W_v = [np.random.randn(d_model, self.d_k) * scale for _ in range(n_heads)]
        self.W_o = np.random.randn(n_heads * self.d_k, d_model) * scale

    @staticmethod
    def _softmax(x, axis=-1):
        e = np.exp(x - x.max(axis=axis, keepdims=True))
        return e / e.sum(axis=axis, keepdims=True)

    def forward(self, X):
        """X: (seq_len, d_model)"""
        seq_len = X.shape[0]
        head_outputs = []

        for h in range(self.n_heads):
            Q = X @ self.W_q[h]  # (seq_len, d_k)
            K = X @ self.W_k[h]
            V = X @ self.W_v[h]

            # Scaled dot-product attention
            scores = Q @ K.T / np.sqrt(self.d_k)  # (seq_len, seq_len)
            attn_weights = self._softmax(scores, axis=-1)
            head_output = attn_weights @ V  # (seq_len, d_k)
            head_outputs.append(head_output)

        # Concat all heads
        multi_head = np.hstack(head_outputs)  # (seq_len, n_heads * d_k)
        output = multi_head @ self.W_o  # (seq_len, d_model)
        return output, attn_weights


class TransformerEncoderBlock:
    """
    Transformer Encoder Block:
    1. Multi-Head Self-Attention
    2. Add & Norm (residual + layer norm)
    3. Feed-Forward (2 linear layers + ReLU)
    4. Add & Norm
    """

    def __init__(self, d_model=64, n_heads=4, d_ff=128):
        self.attn = SelfAttention(d_model, n_heads)

        # FFN: Linear(d_model→d_ff) → ReLU → Linear(d_ff→d_model)
        self.W1 = np.random.randn(d_model, d_ff) * np.sqrt(2.0 / d_model)
        self.b1 = np.zeros(d_ff)
        self.W2 = np.random.randn(d_ff, d_model) * np.sqrt(2.0 / d_ff)
        self.b2 = np.zeros(d_model)

    @staticmethod
    def _layer_norm(X, eps=1e-6):
        mean = X.mean(axis=-1, keepdims=True)
        var = X.var(axis=-1, keepdims=True)
        return (X - mean) / np.sqrt(var + eps)

    def forward(self, X):
        # 1. Self-Attention + Residual + LayerNorm
        attn_out, weights = self.attn.forward(X)
        X = self._layer_norm(X + attn_out)

        # 2. FFN + Residual + LayerNorm
        ffn_out = np.maximum(0, X @ self.W1 + self.b1) @ self.W2 + self.b2
        X = self._layer_norm(X + ffn_out)
        return X, weights


def demo_transformer():
    print("\n📋 4. Self-Attention + Transformer Block")
    seq_len, d_model = 8, 32
    X = np.random.randn(seq_len, d_model)

    # Single-head attention pattern
    attn = SelfAttention(d_model, n_heads=1)
    _, weights = attn.forward(X)

    print(f"   输入: seq_len={seq_len}, d_model={d_model}")
    print(f"\n   Attention 权重矩阵（单头，{seq_len}x{seq_len}）:")
    # ASCII 可视化
    for i in range(min(seq_len, 6)):
        row = weights[i]
        bar = ''.join('█' if w > 0.2 else '▓' if w > 0.15 else '▒' if w > 0.1 else '·' for w in row)
        print(f"   pos {i}: {bar}")

    entropy = -(weights * np.log2(weights + 1e-10)).sum(axis=1).mean()
    max_entropy = np.log2(seq_len)
    ratio = entropy / max_entropy
    print(f"\n   → 每行 sum={weights[0].sum():.4f}（softmax 归一化）")
    print(f"   → 权重熵: {entropy:.3f} bits（统一 log2，单位一致）")
    print(f"   （最大熵 = log2({seq_len}) = {max_entropy:.3f} bits，占比 {ratio:.1%}）")

    # Multi-head Transformer block
    block = TransformerEncoderBlock(d_model=32, n_heads=4, d_ff=64)
    output, _ = block.forward(X)
    print(f"\n   Transformer Block 输出: {output.shape}")
    print(f"   输出均值: {output.mean():.4f}, 标准差: {output.std():.4f}")
    print(f"   （LayerNorm 使每行零均值单位方差）")

    print(f"\n   反直觉发现：")
    print(f"   随机初始化 attention 并非均匀——熵仅占 max 的 {ratio:.1%}（已显著 peaked）")
    print(f"   原因：scores = QK^T/√d_k = Σ^d_k q_i·k_i，累积 d_k={attn.d_k} 个随机项")
    print(f"   使某些 (query,key) 对天然偏大 → softmax 放大为高权重（熵降低）")
    print(f"   → 训练会进一步锐化这种 peaked（注意力集中于语义相关 token）")


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 413/513: Neural Networks & Deep Learning Demo")
    print("=" * 60)

    np.random.seed(42)

    # 1. MLP
    print("\n📋 1. MLP + Backprop（MNIST 风格分类）")
    # 合成数据：3 类，2D 特征
    rng = np.random.RandomState(42)
    n_per = 50
    centers = [(2, 2), (-2, 2), (0, -2)]
    X_list, y_list = [], []
    for cls, center in enumerate(centers):
        X_list.append(rng.randn(n_per, 2) + center)
        y_list.append(np.full(n_per, cls))
    X = np.vstack(X_list).T  # (2, 150)
    y = np.hstack(y_list)
    y_onehot = np.zeros((3, len(y)))
    y_onehot[y, np.arange(len(y))] = 1.0

    mlp = MLP([2, 16, 3], lr=0.1)
    initial_loss = mlp.loss(X, y_onehot)
    for epoch in range(200):
        mlp.backward(X, y_onehot)
    final_loss = mlp.loss(X, y_onehot)
    preds = mlp.predict(X)
    acc = np.mean(preds == y)
    print(f"   初始 loss: {initial_loss:.4f}")
    print(f"   训练后 loss: {final_loss:.4f}")
    print(f"   训练准确率: {acc:.1%}")

    # 2. CNN
    demo_cnn()

    # 3. LSTM
    demo_lstm()

    # 4. Transformer
    demo_transformer()

    print("\n✅ CSC 413/513 完成！")
    print("💡 覆盖：MLP+反向传播 + CNN(Conv+Pool) + LSTM门控 + Transformer注意力")
    print("   核心公式：Attention(Q,K,V) = softmax(QK^T/√d_k)V")


if __name__ == "__main__":
    demo()
