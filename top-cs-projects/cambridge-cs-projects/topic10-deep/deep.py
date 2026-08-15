"""
Part II Deep Learning (Cambridge CST)
=====================================
覆盖主题：
- CNN（卷积 + 池化）
- RNN（字符级语言模型）
- Attention / Transformer block
- Normalizing Flow（MAF）

核心教材：
- Goodfellow, Bengio & Courville 2016 "Deep Learning" MIT Press
- Bishop 2024 "Deep Learning: Foundations and Concepts" Springer

核心论文（真实 arXiv ID）：
- Vaswani et al. 2017 "Attention Is All You Need" arXiv:1706.03762
- He et al. 2015 "Deep Residual Learning" arXiv:1512.03385
- Dinh et al. 2016 "Density Estimation using Real NVP" arXiv:1605.08803
- Papamakarios et al. 2017 "Masked Autoregressive Flow" arXiv:1705.07057

本文件实现：
- 1D 卷积 + 最大池化（纯 Python）
- 简化 RNN cell + 字符级文本生成
- Self-attention + Multi-head attention
- MAF（Masked Autoregressive Flow）前向 + 逆变换

运行：
    python deep.py
"""
from __future__ import annotations
import math
import random


# ================================================================
# 数学工具
# ================================================================

def softmax(vec):
    mx = max(vec)
    exps = [math.exp(v - mx) for v in vec]
    s = sum(exps)
    return [e / s for e in exps]


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x)) if x > -50 else 0.0


# ================================================================
# 1. CNN: 1D 卷积 + 最大池化
# ================================================================

def conv1d(signal, kernel, stride=1):
    """1D 卷积"""
    k = len(kernel)
    out_len = (len(signal) - k) // stride + 1
    return [sum(signal[i*stride + j] * kernel[j] for j in range(k))
            for i in range(out_len)]


def max_pool1d(signal, pool_size=2):
    """1D 最大池化"""
    return [max(signal[i:i+pool_size])
            for i in range(0, len(signal) - len(signal) % pool_size, pool_size)]


def relu_list(lst):
    return [max(0, x) for x in lst]


class SimpleCNN1D:
    """1D CNN 用于时序分类"""

    def __init__(self, kernel1, kernel2, n_classes):
        self.k1 = kernel1
        self.k2 = kernel2
        self.fc_w = [[random.gauss(0, 0.5) for _ in range(n_classes)]
                     for _ in range(8)]  # 简化固定大小
        self.n_classes = n_classes

    def forward(self, signal):
        c1 = relu_list(conv1d(signal, self.k1))
        p1 = max_pool1d(c1)
        c2 = relu_list(conv1d(p1, self.k2))
        p2 = max_pool1d(c2)
        # 全连接（简化）
        logits = [0.0] * self.n_classes
        for i in range(min(len(p2), 8)):
            for j in range(self.n_classes):
                logits[j] += p2[i] * self.fc_w[i][j]
        return softmax(logits), p2


# ================================================================
# 2. RNN: 字符级语言模型
# ================================================================

class SimpleRNN:
    """
    Vanilla RNN cell:
    h_t = tanh(W_xh · x_t + W_hh · h_{t-1} + b_h)
    y_t = softmax(W_hy · h_t + b_y)
    """

    def __init__(self, vocab_size, hidden_size=16):
        self.V = vocab_size
        self.H = hidden_size
        # 用简单初始化
        def rand_mat(r, c):
            return [[random.gauss(0, 0.5) for _ in range(c)] for _ in range(r)]
        self.W_xh = rand_mat(hidden_size, vocab_size)
        self.W_hh = rand_mat(hidden_size, hidden_size)
        self.W_hy = rand_mat(vocab_size, hidden_size)

    def forward(self, inputs):
        """inputs: list of one-hot vectors. 返回 outputs + 最终 hidden"""
        h = [0.0] * self.H
        outputs = []
        for x in inputs:
            new_h = []
            for i in range(self.H):
                val = sum(self.W_xh[i][j] * x[j] for j in range(self.V))
                val += sum(self.W_hh[i][j] * h[j] for j in range(self.H))
                new_h.append(math.tanh(val))
            h = new_h
            # output
            logits = []
            for k in range(self.V):
                val = sum(self.W_hy[k][j] * h[j] for j in range(self.H))
                logits.append(val)
            outputs.append(softmax(logits))
        return outputs, h

    def generate(self, start_token, length=20):
        """自回归生成"""
        result = [start_token]
        h = [0.0] * self.H
        for _ in range(length):
            x = [0] * self.V
            x[result[-1]] = 1
            new_h = []
            for i in range(self.H):
                val = sum(self.W_xh[i][j] * x[j] for j in range(self.V))
                val += sum(self.W_hh[i][j] * h[j] for j in range(self.H))
                new_h.append(math.tanh(val))
            h = new_h
            logits = []
            for k in range(self.V):
                val = sum(self.W_hy[k][j] * h[j] for j in range(self.H))
                logits.append(val)
            probs = softmax(logits)
            # 采样
            r = random.random()
            cum = 0
            for k, p in enumerate(probs):
                cum += p
                if r < cum:
                    result.append(k)
                    break
            else:
                result.append(len(probs) - 1)
        return result


# ================================================================
# 3. Self-Attention / Transformer Block
# ================================================================

def self_attention(Q, K, V):
    """
    Scaled dot-product attention:
    Attention(Q,K,V) = softmax(Q K^T / √d_k) V
    Q, K, V: [seq_len × d]
    """
    d_k = len(K[0])
    seq = len(Q)
    # Q K^T
    scores = []
    for i in range(seq):
        row = []
        for j in range(seq):
            dot = sum(Q[i][d] * K[j][d] for d in range(d_k))
            row.append(dot / math.sqrt(d_k))
        scores.append(row)
    # softmax per row
    attn = []
    for i in range(seq):
        attn.append(softmax(scores[i]))
    # attn · V
    output = []
    for i in range(seq):
        out_row = []
        for d in range(len(V[0])):
            val = sum(attn[i][j] * V[j][d] for j in range(seq))
            out_row.append(val)
        output.append(out_row)
    return output, attn


def multi_head_attention(Q, K, V, n_heads=2):
    """简化 multi-head：平均各 head 结果"""
    d_model = len(Q[0])
    d_head = d_model // n_heads
    results = []
    for h in range(n_heads):
        Qh = [row[h*d_head:(h+1)*d_head] for row in Q]
        Kh = [row[h*d_head:(h+1)*d_head] for row in K]
        Vh = [row[h*d_head:(h+1)*d_head] for row in V]
        out, _ = self_attention(Qh, Kh, Vh)
        results.append(out)
    # concat heads
    merged = []
    for i in range(len(Q)):
        merged.append([val for h in range(n_heads) for val in results[h][i]])
    return merged


# ================================================================
# 4. Normalizing Flow: Masked Autoregressive Flow (MAF)
# ================================================================

class MADE_Layer:
    """
    Masked Autoregressive Flow 单层 (Papamakarios et al. 2017, arXiv:1705.07057)

    核心：每维的 affine 参数 μ_i 和 α_i 是 x_{<i} 的函数（而非常数）。
    下三角掩码保证 u_i 仅依赖 x_{<i}：
      μ_i(x_{<i}) = Σ_{j<i} W_μ[i][j] · x_j + b_μ[i]
      α_i(x_{<i}) = exp(Σ_{j<i} W_α[i][j] · x_j + b_α[i])   (恒正)
      u_i = (x_i − μ_i) / α_i
      log|det J| = −Σ_i log α_i   (Jacobian 下三角, 对角元素 = 1/α_i)

    forward (密度评估): 所有 u_i 可并行计算 → 快
    inverse (采样): x_i 依赖 x_{<i}, 必须逐维串行 → 慢 (这是 MAF 的代价)
    """

    def __init__(self, n_dims):
        self.n = n_dims
        # 下三角掩码权重 (j < i 才非零) → u_i 仅依赖 x_{<i}
        self.W_mu = [[random.gauss(0, 0.1) if j < i else 0.0
                      for j in range(n_dims)] for i in range(n_dims)]
        self.W_alpha = [[random.gauss(0, 0.1) if j < i else 0.0
                         for j in range(n_dims)] for i in range(n_dims)]
        self.b_mu = [0.0] * n_dims
        self.b_alpha = [0.0] * n_dims

    def forward(self, x):
        """x → u (密度评估用). 返回 (u, log|det du/dx|). 全部并行。"""
        mu = [sum(self.W_mu[i][j] * x[j] for j in range(i)) + self.b_mu[i]
              for i in range(self.n)]
        alpha = [math.exp(sum(self.W_alpha[i][j] * x[j] for j in range(i))
                          + self.b_alpha[i])
                 for i in range(self.n)]
        u = [(x[i] - mu[i]) / alpha[i] for i in range(self.n)]
        log_det = -sum(math.log(alpha[i]) for i in range(self.n))
        return u, log_det

    def inverse(self, u):
        """u → x (采样用). 逐维串行: x_i 依赖已计算的 x_{<i}."""
        x = [0.0] * self.n
        for i in range(self.n):
            mu = sum(self.W_mu[i][j] * x[j] for j in range(i)) + self.b_mu[i]
            alpha = math.exp(sum(self.W_alpha[i][j] * x[j] for j in range(i))
                             + self.b_alpha[i])
            x[i] = u[i] * alpha + mu
        return x


class MAF:
    """Masked Autoregressive Flow (stack of MADE layers)"""

    def __init__(self, n_dims, n_layers=3):
        self.layers = [MADE_Layer(n_dims) for _ in range(n_layers)]

    def log_prob(self, x):
        """log p(x) = log p(u) + Σ log|det|"""
        u = list(x)
        total_log_det = 0.0
        for layer in self.layers:
            u, log_det = layer.forward(u)
            total_log_det += log_det
        # 基础分布: N(0, I)
        log_base = sum(-0.5 * ui**2 - 0.5 * math.log(2 * math.pi) for ui in u)
        return log_base + total_log_det

    def sample(self):
        """从 N(0,I) 采样 → inverse flow"""
        n_dims = self.layers[0].n
        u = [random.gauss(0, 1) for _ in range(n_dims)]
        x = u
        for layer in reversed(self.layers):
            x = layer.inverse(x)
        return x


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part II Deep Learning — Demo")
    print("=" * 64)
    random.seed(42)

    # 1. CNN
    print("\n📋 1. 1D CNN（边缘检测信号）")
    signal = [0]*5 + [10]*5 + [0]*5 + [10]*5 + [0]*5  # 方波信号
    edge_kernel = [1, -1]
    edges = conv1d(signal, edge_kernel)
    pooled = max_pool1d(relu_list(edges))
    print(f"   信号: {signal}")
    print(f"   卷积 [1,-1]: {[int(e) for e in edges]}")
    print(f"   ReLU+池化: {[int(p) for p in pooled]}")
    print(f"   → 卷积提取了「跳变」位置")

    cnn = SimpleCNN1D([0.5, -0.5], [0.3, 0.3, -0.6], n_classes=3)
    probs, feat = cnn.forward(signal)
    print(f"   CNN 分类概率: {[f'{p:.3f}' for p in probs]}")

    # 2. RNN
    print("\n📋 2. RNN 字符级语言模型")
    vocab = list("abc ")
    vocab_idx = {c: i for i, c in enumerate(vocab)}
    rnn = SimpleRNN(vocab_size=len(vocab), hidden_size=8)
    inputs = [[1 if j == vocab_idx[c] else 0 for j in range(len(vocab))]
              for c in "abcab"]
    outputs, _ = rnn.forward(inputs)
    print(f"   输入: 'abcab'")
    print(f"   每步输出概率（第一个字符预测）: "
          f"{[round(max(o),3) for o in outputs[:3]]}")
    generated = rnn.generate(vocab_idx['a'], length=10)
    gen_str = ''.join(vocab[i] for i in generated)
    print(f"   生成（随机权重）: '{gen_str}'")
    print(f"   → 未训练的 RNN 输出随机，但展示了自回归生成机制")

    # 3. Attention
    print("\n📋 3. Self-Attention（Attention Is All You Need, arXiv:1706.03762）")
    # 3 词序列，4 维
    Q = [[1,0,0,0],[0,1,0,0],[1,1,0,0]]
    K = Q
    V = [[1,0],[0,1],[1,1]]
    out, attn = self_attention(Q, K, V)
    print(f"   Q=K=[[1,0,0,0],[0,1,0,0],[1,1,0,0]], V=[[1,0],[0,1],[1,1]]")
    print(f"   Attention weights:")
    for i, row in enumerate(attn):
        bar = " ".join(f"{v:.3f}" for v in row)
        print(f"     pos{i}: [{bar}]")
    print(f"   Output: {[[round(x,3) for x in r] for r in out]}")
    print(f"   → 第3个词 attend 到自己和前两个（[1,1] = 前两者之和）")

    # Multi-head
    mha = multi_head_attention([[1,0,1,1],[0,1,1,0]], [[1,0,1,1],[0,1,1,0]],
                               [[1,1],[2,2]], n_heads=2)
    print(f"   Multi-head (2 heads) output: {[[round(x,3) for x in r] for r in mha]}")

    # 4. Normalizing Flow
    print("\n📋 4. Normalizing Flow (MAF, arXiv:1705.07057)")
    maf = MAF(n_dims=4, n_layers=3)
    x_test = [1.0, 0.5, -0.3, 0.8]
    log_p = maf.log_prob(x_test)
    print(f"   x = {x_test}")
    print(f"   log p(x) = {log_p:.4f}")

    # 验证 1: 3 层 MAF 不塌缩为对角仿射 (≠ 等效单层)
    maf_1 = MAF(n_dims=4, n_layers=1)
    maf_1.layers = [maf.layers[0]]  # 只取第 1 层
    u_3layer, _ = maf.layers[0].forward(x_test)
    u_3layer, _ = maf.layers[1].forward(u_3layer)
    u_3layer, _ = maf.layers[2].forward(u_3layer)
    u_1layer, _ = maf.layers[0].forward(x_test)
    collapse = all(abs(a - b) < 1e-9 for a, b in zip(u_3layer, u_1layer))
    print(f"   3层 forward == 1层 forward? {collapse}  → {'❌ 塌缩' if collapse else '✅ 不塌缩（每层 μ/α 依赖 x_{<i}，叠加有实质效果）'}")

    # 验证 2: inverse(forward(x)) ≈ x (可逆性)
    u_check, _ = maf.layers[0].forward(x_test)
    u_check, _ = maf.layers[1].forward(u_check)
    u_check, _ = maf.layers[2].forward(u_check)
    x_recon = u_check
    for layer in reversed(maf.layers):
        x_recon = layer.inverse(x_recon)
    max_err = max(abs(a - b) for a, b in zip(x_test, x_recon))
    print(f"   inverse(forward(x)) 最大误差 = {max_err:.2e}  → {'✅ 可逆' if max_err < 1e-9 else '❌ 不可逆'}")

    samples = [maf.sample() for _ in range(100)]
    means = [sum(s[i] for s in samples)/len(samples) for i in range(4)]
    print(f"   100 次采样的均值: {[round(m,3) for m in means]}")
    print(f"   log p(均值样本) = {maf.log_prob(means):.4f}")
    print(f"   → Flow 把简单 N(0,I) 变换为复杂分布，且 log-likelihood 可计算")

    print("\n✅ Deep Learning 完成！")
    print("\n💡 反直觉发现：")
    print("   - 卷积核 [1,-1] 就是离散导数（边缘 = 信号突变处）")
    print("   - Attention 公式 softmax(QK^T/√d_k)V 中 √d_k 防止点积过大→梯度消失")
    print("   - Normalizing Flow 可以精确计算 log-likelihood（GAN 不能）")
    print("   - MAF 采样是 O(n) 串行（自回归），但 log-likelihood 是 O(1) 并行")


if __name__ == "__main__":
    demo()
