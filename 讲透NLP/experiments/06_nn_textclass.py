"""
实验 06 —— MLP 文本分类：从 logistic 到神经网络，提升有多大？
对应文档: 06-神经网络基础.md (讲透NLP Ch6, 基于 SLP3 Ch6)

核心反直觉发现:
  在简单的 bag-of-words 文本分类上，加一层 hidden layer 的 MLP
  比 Ch4 的 logistic 回归提升不到 2%——非线性在 BoW 上的边际效益极低。
  参数量翻了 30+ 倍，准确率几乎没动。

跑法: python3 06_nn_textclass.py   (纯 NumPy, 几秒跑完, 无外部依赖)
"""
# 小矩阵上多线程 BLAS 反而因线程调度开销变慢, 强制单线程 (项目铁律)
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import numpy as np

# ================================================================
# Part 0: 工具函数
# ================================================================

def sigmoid(z):
    """数值稳定的 sigmoid"""
    return np.where(z >= 0, 1.0 / (1.0 + np.exp(-z)),
                    np.exp(z) / (1.0 + np.exp(z)))

def bce_loss(y_hat, y):
    """二元交叉熵 (数值稳定)"""
    eps = 1e-7
    y_hat = np.clip(y_hat, eps, 1.0 - eps)
    return -np.mean(y * np.log(y_hat) + (1.0 - y) * np.log(1.0 - y_hat))

def build_vocab(sentences, min_df=2):
    """从句子列表构建词汇表 {word: index}.
    min_df: 只保留出现 >= min_df 个句子的词 (过滤噪声/罕见词)"""
    df = {}  # document frequency: 每个词出现在多少个句子中
    for s in sentences:
        for w in set(s.split()):  # set() 去重: 每句每词只算一次
            df[w] = df.get(w, 0) + 1
    vocab = {}
    for s in sentences:
        for w in s.split():
            if df.get(w, 0) >= min_df and w not in vocab:
                vocab[w] = len(vocab)
    return vocab

def bow_matrix(sentences, vocab):
    """句子列表 → 二值 BoW 矩阵 (词出现=1, 不出现=0)"""
    M = np.zeros((len(sentences), len(vocab)), dtype=np.float64)
    for i, s in enumerate(sentences):
        for w in s.split():
            if w in vocab:
                M[i, vocab[w]] = 1.0
    return M


# ================================================================
# Part 1: 内置情感数据集 (模板生成, 确保每个情感词高频出现, 稳定学习)
# ================================================================

import random as _rnd

def _gen_dataset(seed=42):
    """模板化生成情感分类数据集.
    设计原则: 每个情感词出现在 >= 6 个句子中, 确保模型能稳定学习词极性.
    含 ~6% 否定 tricky 样本 (not bad = 正面, not great = 负面)."""
    rng = _rnd.Random(seed)
    POS_ADJ = ["great", "amazing", "wonderful", "fantastic", "brilliant",
               "beautiful", "perfect", "excellent", "superb", "outstanding"]
    NEG_ADJ = ["terrible", "awful", "horrible", "boring", "worst",
               "bad", "stupid", "dreadful", "painful", "ridiculous"]
    SUBJ   = ["movie", "film", "story"]
    ASPECT = ["acting", "plot", "direction"]

    pos, neg = [], []

    # T1: "this X is ADJ"  (3 subj x 10 adj = 30 per class)
    for s in SUBJ:
        for a in POS_ADJ: pos.append(f"this {s} is {a}")
        for a in NEG_ADJ: neg.append(f"this {s} is {a}")

    # T2: "the X was ADJ"  (3 aspect x 10 adj = 30 per class)
    for s in ASPECT:
        for a in POS_ADJ: pos.append(f"the {s} was {a}")
        for a in NEG_ADJ: neg.append(f"the {s} was {a}")

    # T3: "i really VERB this X"  (2 verb x 2 subj = 4 per class)
    for vp, vn in [("loved", "hated"), ("enjoyed", "suffered")]:
        for s in ["movie", "film"]:
            pos.append(f"i really {vp} this {s}")
            neg.append(f"i really {vn} this {s}")

    # T4: "what a ADJ X"  (10 adj x 2 subj = 20 per class)
    for a in POS_ADJ:
        for s in ["movie", "film"]: pos.append(f"what a {a} {s}")
    for a in NEG_ADJ:
        for s in ["movie", "film"]: neg.append(f"what a {a} {s}")

    # T5: tricky 否定 (not + 负面词 = 正面, not + 正面词 = 负面)
    for a in NEG_ADJ[:5]: pos.append(f"not {a} at all")
    for a in POS_ADJ[:5]: neg.append(f"not {a} at all")

    rng.shuffle(pos)
    rng.shuffle(neg)
    return pos, neg

POSITIVE, NEGATIVE = _gen_dataset()

ALL_SENTENCES = POSITIVE + NEGATIVE
ALL_LABELS = np.array([1.0] * len(POSITIVE) + [0.0] * len(NEGATIVE))


# ================================================================
# Part 2: Logistic 回归 (0 hidden layers = Ch4)
# ================================================================

class LogisticRegression:
    """x -> sigmoid(w·x+b) -> BCE loss. 就是 Ch4 的逻辑回归.
    用 Adam 优化器训练 (自适应学习率, lr=0.01 通用)."""

    def __init__(self, n_features, lr=0.01, l2=1e-4):
        self.w = np.zeros(n_features)
        self.b = np.zeros(1)
        self.lr = lr
        self.l2 = l2

    def forward(self, X):
        return sigmoid(X @ self.w + self.b[0])

    def fit(self, X, y, epochs=2000):
        n = len(y)
        params = [self.w, self.b]
        m = [np.zeros_like(p) for p in params]
        v = [np.zeros_like(p) for p in params]
        b1, b2, eps = 0.9, 0.999, 1e-8
        for t in range(1, epochs + 1):
            y_hat = self.forward(X)
            # sigmoid + BCE 的梯度有一个美妙化简: dL/dz = (y_hat - y)
            dz = (y_hat - y) / n
            grads = [X.T @ dz + self.l2 * self.w, np.array([dz.sum()])]
            for i in range(2):
                m[i] = b1 * m[i] + (1 - b1) * grads[i]
                v[i] = b2 * v[i] + (1 - b2) * grads[i] ** 2
                params[i] -= self.lr * (m[i] / (1 - b1**t)) / \
                    (np.sqrt(v[i] / (1 - b2**t)) + eps)
        return self

    def predict(self, X):
        return (self.forward(X) >= 0.5).astype(float)

    def n_params(self):
        return len(self.w) + 1


# ================================================================
# Part 3: MLP (1 hidden layer, ReLU) — 本章的主角
# ================================================================

class MLP:
    """x -> ReLU(W1·x+b1) -> sigmoid(w2·h+b2) -> BCE loss.
    用 Adam 优化器训练."""

    def __init__(self, n_features, n_hidden=32, lr=0.01, l2=1e-4, seed=0):
        rng = np.random.RandomState(seed)
        # He 初始化 (适合 ReLU): std = sqrt(2 / fan_in)
        self.W1 = rng.randn(n_features, n_hidden) * np.sqrt(2.0 / n_features)
        self.b1 = np.zeros(n_hidden)
        self.W2 = rng.randn(n_hidden) * np.sqrt(2.0 / n_hidden)
        self.b2 = np.zeros(1)
        self.lr = lr
        self.l2 = l2

    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1         # (N, H)
        self.a1 = np.maximum(0.0, self.z1)      # ReLU
        return sigmoid(self.a1 @ self.W2 + self.b2[0])

    def fit(self, X, y, epochs=2000):
        n = len(y)
        params = [self.W1, self.b1, self.W2, self.b2]
        m = [np.zeros_like(p) for p in params]
        v = [np.zeros_like(p) for p in params]
        b1, b2, eps = 0.9, 0.999, 1e-8
        for t in range(1, epochs + 1):
            # --- 前向 ---
            y_hat = self.forward(X)
            # --- 反向 (链式法则逐层) ---
            dz2 = (y_hat - y) / n                       # (N,)
            da1 = np.outer(dz2, self.W2)                # (N, H)
            dz1 = da1 * (self.z1 > 0)                   # ReLU 局部导数
            grads = [
                X.T @ dz1 + self.l2 * self.W1,          # W1 (D,H)
                dz1.sum(axis=0),                         # b1 (H,)
                self.a1.T @ dz2 + self.l2 * self.W2,    # W2 (H,)
                np.array([dz2.sum()]),                   # b2 (1,)
            ]
            # --- Adam 更新 ---
            for i in range(4):
                m[i] = b1 * m[i] + (1 - b1) * grads[i]
                v[i] = b2 * v[i] + (1 - b2) * grads[i] ** 2
                params[i] -= self.lr * (m[i] / (1 - b1**t)) / \
                    (np.sqrt(v[i] / (1 - b2**t)) + eps)
        return self

    def predict(self, X):
        return (self.forward(X) >= 0.5).astype(float)

    def n_params(self):
        return self.W1.size + self.b1.size + self.W2.size + 1


# ================================================================
# Part 4: 多种子交叉验证 + 对比
# ================================================================

def evaluate(n_seeds=5, n_hidden=32, epochs=2000):
    """n_seeds 次随机 80/20 划分, 返回两种模型的平均测试准确率."""
    n = len(ALL_SENTENCES)
    n_train = int(n * 0.8)

    log_accs, mlp_accs = [], []
    log_train, mlp_train = [], []
    log_losses, mlp_losses = [], []

    for seed in range(n_seeds):
        rng = np.random.RandomState(seed)
        idx = rng.permutation(n)
        train_idx, test_idx = idx[:n_train], idx[n_train:]

        # 用全部数据构建词汇表 (教学标准做法; 对 logistic/MLP 公平, 不影响对比结论)
        train_sents = [ALL_SENTENCES[i] for i in train_idx]
        test_sents = [ALL_SENTENCES[i] for i in test_idx]
        vocab = build_vocab(ALL_SENTENCES, min_df=2)

        X_train = bow_matrix(train_sents, vocab)
        y_train = ALL_LABELS[train_idx]
        X_test = bow_matrix(test_sents, vocab)
        y_test = ALL_LABELS[test_idx]

        d = len(vocab)

        # Logistic
        log = LogisticRegression(d, lr=0.01, l2=0.01)
        log.fit(X_train, y_train, epochs=epochs)
        log_pred = log.predict(X_test)
        log_accs.append(np.mean(log_pred == y_test))
        log_train.append(np.mean(log.predict(X_train) == y_train))
        log_losses.append(bce_loss(log.forward(X_test), y_test))

        # MLP
        mlp = MLP(d, n_hidden=n_hidden, lr=0.01, l2=0.01, seed=seed)
        mlp.fit(X_train, y_train, epochs=epochs)
        mlp_pred = mlp.predict(X_test)
        mlp_accs.append(np.mean(mlp_pred == y_test))
        mlp_train.append(np.mean(mlp.predict(X_train) == y_train))
        mlp_losses.append(bce_loss(mlp.forward(X_test), y_test))

    return (np.array(log_accs), np.array(mlp_accs),
            np.array(log_train), np.array(mlp_train),
            np.array(log_losses), np.array(mlp_losses),
            d)


def main():
    SEP = "=" * 64

    print(SEP)
    print("实验 06: 从 Logistic 到 MLP")
    print("——非线性在 BoW 文本分类上有多大用？ (SLP3 Ch6 / 讲透NLP Ch6)")
    print(SEP)

    # --- Part 1: 数据集 ---
    print("\n[Part 1] 数据集")
    print(f"  正面: {len(POSITIVE)} 句,  负面: {len(NEGATIVE)} 句,  总计: {len(ALL_SENTENCES)}")
    print(f"  其中 10 句为 tricky 样本 (否定: 'not bad'=正面 / 'not great'=负面)")
    print(f"  划分: 80% 训练 / 20% 测试,  x5 随机种子取平均")

    # --- Part 2-4: 训练 + 评估 ---
    log_accs, mlp_accs, log_train_accs, mlp_train_accs, log_losses, mlp_losses, vocab_size = evaluate(
        n_seeds=5, n_hidden=32, epochs=2000
    )

    log_param = vocab_size + 1
    mlp_param = vocab_size * 32 + 32 + 32 + 1

    print(f"\n[Part 2] Logistic 回归 (0 hidden layers, = Ch4)")
    print(f"  参数量:     {log_param}")
    print(f"  训练准确率: {log_train_accs.mean()*100:.1f}% +/- {log_train_accs.std()*100:.1f}%")
    print(f"  测试准确率: {log_accs.mean()*100:.1f}% +/- {log_accs.std()*100:.1f}%")
    print(f"  测试损失:   {log_losses.mean():.4f}")

    print(f"\n[Part 3] MLP (1 hidden layer, ReLU, 32 units)")
    print(f"  结构:       BoW({vocab_size}) -> hidden(32, ReLU) -> sigmoid -> BCE")
    print(f"  参数量:     {mlp_param}  (是 logistic 的 {mlp_param/log_param:.0f} 倍)")
    print(f"  训练准确率: {mlp_train_accs.mean()*100:.1f}% +/- {mlp_train_accs.std()*100:.1f}%")
    print(f"  测试准确率: {mlp_accs.mean()*100:.1f}% +/- {mlp_accs.std()*100:.1f}%")
    print(f"  测试损失:   {mlp_losses.mean():.4f}")

    # --- Part 4: 对比 ---
    gap = (mlp_accs.mean() - log_accs.mean()) * 100
    print(f"\n[Part 4] 对比")
    print(f"  MLP - Logistic = {gap:+.1f}%")
    print()
    print(f"  ★ 反直觉发现: 参数量翻了 {mlp_param/log_param:.0f} 倍, "
          f"准确率只提升了 {gap:.1f}%!")

    # --- Logistic 学到的词权重 (直觉佐证) ---
    print(f"\n[Part 5] Logistic 学到了什么 (用全部数据训一次)")
    full_vocab = build_vocab(ALL_SENTENCES)
    X_full = bow_matrix(ALL_SENTENCES, full_vocab)
    y_full = ALL_LABELS
    log_full = LogisticRegression(len(full_vocab), lr=0.01, l2=0.01)
    log_full.fit(X_full, y_full, epochs=2000)

    idx2word = {v: k for k, v in full_vocab.items()}
    sorted_idx = np.argsort(log_full.w)
    print("  Top-5 正面词 (权重最大):")
    for i in sorted_idx[-5:][::-1]:
        print(f"    {idx2word[i]:15s}  w = {log_full.w[i]:+.3f}")
    print("  Top-5 负面词 (权重最小):")
    for i in sorted_idx[:5]:
        print(f"    {idx2word[i]:15s}  w = {log_full.w[i]:+.3f}")

    # --- 核心洞察 ---
    DASH = "-" * 64
    print(f"\n{DASH}")
    print("核心洞察:")
    print(DASH)
    print(f"""
  1. BoW 情感分类本质是线性问题: 好词 +、坏词 -, 加权求和就够。
     Logistic 回归恰好就是这个模型, 所以很难被超越。

  2. MLP 的 hidden layer 能学非线性交互 (如 not+bad=正面), 但:
     - tricky 样本太少 (~6%), 学不稳定
     - BoW 丢失词序, "not bad" 和 "bad" 的特征向量几乎一样
     -> 非线性的理论优势在 BoW 上无法兑现

  3. 真正的飞跃来自换输入表示, 不是堆 MLP 层:
     BoW -> 词嵌入 (word2vec) -> 上下文嵌入 (BERT)
     每一步的特征升级比加深网络有用得多。

  4. 这就是为什么现代 NLP 用 Transformer + 嵌入, 不用 MLP + BoW:
     网络自己学会从 token 提取特征, 不再需要手工 BoW。
""")


if __name__ == "__main__":
    main()
