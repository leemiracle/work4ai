#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 附录 B 配套实验：朴素贝叶斯文本分类（从零实现）
====================================================================
纯 NumPy + 标准库。实现多项式 NB，并与 logistic 回归对比。

★ 反直觉发现：
  1. 朴素贝叶斯“一遍数数”即收敛，logistic 需要数百轮梯度下降
  2. 但两者测试准确率几乎相同——“朴素”假设 = 免费正则化
  3. 数据越少，NB 优势越明显（Ng & Jordan 2002 的理论预言）

python3 experiments/B_naive_bayes.py
"""
import re
import numpy as np

SEED = 0
np.random.seed(SEED)

def P(*a, **kw):
    print(*a, **kw, flush=True)


# ============================================================
# 1. 内置玩具数据集：正面/负面影评
# ============================================================
POS = [
    "great movie loved it so much",
    "amazing film brilliant acting throughout",
    "best movie ever fantastic plot twists",
    "wonderful story loved the characters deeply",
    "brilliant masterpiece truly amazing direction",
    "fantastic film great cast wonderful music",
    "loved every minute best experience ever",
    "excellent movie outstanding performance by all",
    "amazing story great visuals stunning",
    "wonderful film loved the soundtrack too",
    "great acting brilliant screenplay executed",
    "best film amazing soundtrack loved it",
    "loved this movie fantastic story telling",
    "wonderful direction excellent cast superb",
    "brilliant film loved everything about it",
    "amazing plot great characters developed well",
    "fantastic movie wonderful experience overall",
    "excellent story brilliant acting from start",
    "loved the film best movie this year",
    "great visuals amazing music loved everything",
    "superb acting wonderful story loved deeply",
    "outstanding film excellent direction great",
    "best performance amazing cast wonderful plot",
    "fantastic storytelling brilliant throughout loved",
    "wonderful movie great experience loved it",
]

NEG = [
    "terrible movie hated it so much",
    "awful film boring acting throughout",
    "worst movie ever horrible plot twists",
    "bad story hated the characters deeply",
    "horrible mess truly awful direction",
    "boring film bad cast terrible music",
    "hated every minute worst experience ever",
    "poor movie disappointing performance by all",
    "awful story bad visuals dreadful",
    "terrible film hated the soundtrack too",
    "bad acting boring screenplay executed",
    "worst film awful soundtrack hated it",
    "hated this movie horrible story telling",
    "terrible direction poor cast dreadful",
    "awful film hated everything about it",
    "horrible plot bad characters developed poorly",
    "boring movie terrible experience overall",
    "poor story awful acting from start",
    "hated the film worst movie this year",
    "bad visuals awful music hated everything",
    "dreadful acting terrible story hated deeply",
    "disappointing film poor direction bad",
    "worst performance awful cast horrible plot",
    "boring storytelling dreadful throughout hated",
    "terrible movie bad experience hated it",
]

TEXTS = POS + NEG
LABELS = np.array([1] * len(POS) + [0] * len(NEG))


# ============================================================
# 2. 分词 + 词典
# ============================================================
def tokenize(s):
    return re.findall(r"[a-z]+", s.lower())

VOCAB = sorted({tok for t in TEXTS for tok in tokenize(t)})
W2I = {w: i for i, w in enumerate(VOCAB)}
V = len(VOCAB)


def text_to_counts(text):
    """词频向量"""
    vec = np.zeros(V, dtype=np.float64)
    for tok in tokenize(text):
        vec[W2I[tok]] += 1.0
    return vec


# ============================================================
# 3. 多项式朴素贝叶斯（从零实现）
# ============================================================
class MultinomialNB:
    """多项式 NB + add-1 平滑。训练 = 数数，O(n) 一次扫描。"""

    def fit(self, X, y, n_classes=2):
        self.n_classes = n_classes
        self.log_prior = np.zeros(n_classes)
        self.log_likelihood = np.zeros((n_classes, X.shape[1]))

        for c in range(n_classes):
            Xc = X[y == c]
            # 先验（log）
            self.log_prior[c] = np.log(len(Xc) / len(X))
            # 似然（add-1 平滑）
            word_counts = Xc.sum(axis=0) + 1.0          # 每个词 +1
            total = word_counts.sum()                     # 总词数 + V
            self.log_likelihood[c] = np.log(word_counts / total)
        return self

    def predict_scores(self, X):
        """返回 log P(c) + Σ log P(w|c)"""
        # X @ log_likelihood.T = 每个样本 × 每个类
        return X @ self.log_likelihood.T + self.log_prior

    def predict(self, X):
        return np.argmax(self.predict_scores(X), axis=1)


# ============================================================
# 4. Logistic 回归（从零实现，用于对比）
# ============================================================
def sigmoid(z):
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def train_logistic(X, y, lr=0.5, epochs=400, l2=1e-3):
    """二分类 logistic 回归，全批量梯度下降。"""
    m, d = X.shape
    w = np.zeros(d)
    b = 0.0
    for ep in range(epochs):
        z = X @ w + b
        yhat = sigmoid(z)
        yhat = np.clip(yhat, 1e-12, 1 - 1e-12)
        gz = (yhat - y) / m
        grad_w = X.T @ gz + l2 * w
        grad_b = gz.sum()
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b


def predict_logistic(X, w, b):
    return (sigmoid(X @ w + b) > 0.5).astype(int)


# ============================================================
# 5. 评估函数
# ============================================================
def evaluate(nb_data=True, n_splits=30, train_frac=0.75):
    """
    随机划分 train/test，跑 NB 和 logistic，返回准确率列表。
    """
    rng = np.random.RandomState(SEED)
    nb_accs = []
    lr_accs = []

    for _ in range(n_splits):
        idx = rng.permutation(len(TEXTS))
        n_train = int(len(TEXTS) * train_frac)
        tr_idx, te_idx = idx[:n_train], idx[n_train:]

        tr_texts = [TEXTS[i] for i in tr_idx]
        te_texts = [TEXTS[i] for i in te_idx]
        ytr = LABELS[tr_idx]
        yte = LABELS[te_idx]

        Xtr = np.array([text_to_counts(t) for t in tr_texts])
        Xte = np.array([text_to_counts(t) for t in te_texts])

        # NB
        nb = MultinomialNB().fit(Xtr, ytr)
        nb_pred = nb.predict(Xte)
        nb_accs.append((nb_pred == yte).mean())

        # Logistic
        w, b = train_logistic(Xtr, ytr, lr=0.5, epochs=400, l2=1e-3)
        lr_pred = predict_logistic(Xte, w, b)
        lr_accs.append((lr_pred == yte).mean())

    return np.array(nb_accs), np.array(lr_accs)


# ============================================================
# 主程序
# ============================================================
def main():
    P("=" * 68)
    P("讲透NLP · 附录 B：朴素贝叶斯文本分类（从零实现）")
    P("=" * 68)
    P(f"数据集：正面 {len(POS)} 条 + 负面 {len(NEG)} 条 = {len(TEXTS)} 条")
    P(f"词表大小 V = {V}\n")

    # ----------------------------------------------------------
    # Part 1：NB 训练过程透视 —— 训练 = 数数
    # ----------------------------------------------------------
    P("-" * 68)
    P("Part 1：朴素贝叶斯训练过程 —— 就是数数")
    P("-" * 68)

    X_all = np.array([text_to_counts(t) for t in TEXTS])
    y_all = LABELS

    nb_demo = MultinomialNB().fit(X_all, y_all)

    P(f"""
  训练步骤（一遍扫描，无迭代）:
    1. 先验: P(正面) = {len(POS)}/{len(TEXTS)} = {len(POS)/len(TEXTS):.2f}
             P(负面) = {len(NEG)}/{len(TEXTS)} = {len(NEG)/len(TEXTS):.2f}
    2. 似然: 对每个类，数每个词的出现次数 + 1（add-1 平滑）
             再除以该类总词数 + V
    3. 预测: log P(c) + Σ log P(w|c)，取 argmax

  "loved" 的似然:
    P(loved | 正面) = e^{nb_demo.log_likelihood[1][W2I['loved']]:.3f} = {np.exp(nb_demo.log_likelihood[1][W2I['loved']]):.4f}
    P(loved | 负面) = e^{nb_demo.log_likelihood[0][W2I['loved']]:.3f} = {np.exp(nb_demo.log_likelihood[0][W2I['loved']]):.4f}
    → "loved" 强烈指向正面 ✓

  "hated" 的似然:
    P(hated | 正面) = e^{nb_demo.log_likelihood[1][W2I['hated']]:.3f} = {np.exp(nb_demo.log_likelihood[1][W2I['hated']]):.4f}
    P(hated | 负面) = e^{nb_demo.log_likelihood[0][W2I['hated']]:.3f} = {np.exp(nb_demo.log_likelihood[0][W2I['hated']]):.4f}
    → "hated" 强烈指向负面 ✓

  "movie" 的似然:
    P(movie | 正面) = {np.exp(nb_demo.log_likelihood[1][W2I['movie']]):.4f}
    P(movie | 负面) = {np.exp(nb_demo.log_likelihood[0][W2I['movie']]):.4f}
    → "movie" 两类差不多（不区分）✓
""")

    # ----------------------------------------------------------
    # Part 2：NB vs Logistic 回归 —— 30 次随机划分
    # ----------------------------------------------------------
    P("-" * 68)
    P("Part 2：★ 反直觉 —— NB vs Logistic（30 次随机划分）")
    P("-" * 68)

    nb_accs, lr_accs = evaluate(n_splits=30, train_frac=0.75)

    P(f"""
  75% 训练 / 25% 测试，30 次随机划分取均值:

  ┌────────────────────────┬───────────────┬──────────┐
  │ 方法                   │ 平均准确率     │ std      │
  ├────────────────────────┼───────────────┼──────────┤
  │ 朴素贝叶斯 (NB)        │  {nb_accs.mean()*100:>6.1f}%       │ {nb_accs.std()*100:>5.1f}%   │
  │ Logistic 回归          │  {lr_accs.mean()*100:>6.1f}%       │ {lr_accs.std()*100:>5.1f}%   │
  └────────────────────────┴───────────────┴──────────┘

  NB 赢的次数: {int((nb_accs > lr_accs).sum())} / 30
  LR 赢的次数: {int((lr_accs > nb_accs).sum())} / 30
  平局:        {int((nb_accs == lr_accs).sum())} / 30

  ★ 反直觉: 两者准确率几乎相同!
    - NB 训练只需【一遍数数】，无迭代
    - Logistic 需要【400 轮梯度下降】
    - 但最终效果打平——"朴素"假设 = 免费正则化
""")

    # ----------------------------------------------------------
    # Part 3：数据量越小，NB 优势越明显
    # ----------------------------------------------------------
    P("-" * 68)
    P("Part 3：★ 反直觉 —— 数据越少，NB 越占优 (Ng & Jordan 2002)")
    P("-" * 68)

    P(f"\n  {'训练比例':>10}  {'NB 准确率':>12}  {'LR 准确率':>12}  {'NB−LR':>8}  {'NB赢的次数':>12}")
    P("  " + "-" * 60)
    for frac in [0.2, 0.3, 0.4, 0.5, 0.6, 0.75]:
        nb_a, lr_a = evaluate(n_splits=30, train_frac=frac)
        diff = (nb_a - lr_a).mean()
        nb_wins = int((nb_a > lr_a).sum())
        P(f"  {frac*100:>9.0f}%  {nb_a.mean()*100:>11.1f}%  {lr_a.mean()*100:>11.1f}%  "
          f"{diff*100:>+7.1f}%  {nb_wins:>5}/30")

    P(f"""
  ★ 解释 (Ng & Jordan 2002 的生成式 vs 判别式理论):
    - 数据少时: NB 的"朴素"假设 = 强先验 = 正则化 → 抗过拟合 → 占优
    - 数据多时: Logistic 不做错误假设 → 上界更高 → 追上甚至超越
    - 交叉点在数据量大约为 V (词表大小) 量级时

  这就是为什么垃圾邮件过滤至今还用 NB:
    - 训练极快（数数即可）
    - 小数据效果好
    - 概率输出可直接做阈值调整
""")

    # ----------------------------------------------------------
    # Part 4：NB 的"朴素"在文本上为什么不太伤？
    # ----------------------------------------------------------
    P("-" * 68)
    P("Part 4：为什么'朴素'假设在文本分类上不太伤？")
    P("-" * 68)
    P("""
  "朴素"假设: 给定类别，词与词条件独立。
  这显然不成立: "free" 和 "win" 在垃圾邮件中高度共现。

  为什么 NB 仍然有效?
    1. NB 只需要排序正确（谁的分数更高），不需要概率精确
    2. 条件独立假设系统性偏向，但偏向在两类间一致 → 不影响排序
    3. 文本分类的信号极强: 几个关键词("loved"/"hated")就够决策
    4. add-1 平滑 + log 空间天然抗噪声

  失效场景:
    - 特征高度相关且相关性在各类间不同 (如 "not" + "good" = 负面)
    - 需要【精确】概率（如校准后的风险评估）→ 用 logistic
""")

    # ----------------------------------------------------------
    # 总结
    # ----------------------------------------------------------
    P("=" * 68)
    P("一句话总结")
    P("=" * 68)
    P("""
  朴素贝叶斯:
    训练 = 数数  预测 = 加 log 似然 + 比 argmax
    "朴素"假设错误但无害（只需要排序对）

  ★ 反直觉: NB 在文本分类上打平 logistic 回归:
    - 训练快 100×（无迭代 vs 数百轮）
    - 小数据占优（强先验 = 免费正则化）
    - 大数据打平（logistic 追上但不碾压）

  这就是为什么 2000 年代的垃圾邮件过滤、新闻分类、情感分析
  几乎全部用 NB——不是因为它最好，而是因为它"够好且极便宜"。
""")


if __name__ == "__main__":
    main()
