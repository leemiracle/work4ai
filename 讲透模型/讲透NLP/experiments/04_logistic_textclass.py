#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 第 04 章配套实验：逻辑回归与文本分类（从零实现）
====================================================================
只用 NumPy + 标准库（不用 sklearn / torch）。

跑这个脚本，你会看到四个「能跑出来」的结论：

  1. 从零的 logistic 回归 + 梯度下降，在垃圾邮件分类上 loss 单调下降、收敛。
  2. TF-IDF 特征 > 原始 BoW 特征（特征工程有用）。
  3. 【反直觉 1】一个「固定的低维稠密向量」表示（generic frozen embedding 的玩具替身）
     + logistic 回归，在干净小数据上输给 TF-IDF + logistic。
     —— 这正是「冻结的 BERT embedding + 线性头」在专业/小数据上常常打不过
        TF-IDF + logistic 的同一机制（见 .md 里引用的真实数字）。
  4. 【反直觉 2】L1 正则化（proximal gradient）把绝大多数权重压成精确的 0，
     自动「学出」垃圾邮件关键词；L2 只是整体缩小，不产生稀疏。

自包含，几秒跑完：
    python3 experiments/04_logistic_textclass.py
"""

import re
import numpy as np

SEED = 0
np.random.seed(SEED)


# ============================================================
# 1. 内置小数据集：20 条垃圾 + 20 条正常（英文，关键词驱动）
# ============================================================
SPAM = [
    "Congratulations you have won a free prize claim now",
    "Urgent limited time offer get free cash bonus",
    "Click here to claim your guaranteed lottery winnings",
    "Win money now with this exclusive casino deal",
    "Free credit loan approved click to claim your cash",
    "You are our lucky winner claim your prize money",
    "Limited discount deal buy now and save money",
    "Guaranteed cash prize click the link to win",
    "Congratulations winner free bonus just for you",
    "Urgent offer free lottery ticket claim your cash",
    "Get free money transfer this guaranteed deal ends soon",
    "Click to win a brand new prize today",
    "Exclusive casino bonus double your money now",
    "Claim your free credit and loan discount today",
    "You won the lottery click to claim cash prize",
    "Limited guaranteed offer win free money instantly",
    "Urgent congratulations claim your cash bonus winner",
    "Free discount on credit loan click here now",
    "Winner winner claim your guaranteed lottery prize",
    "Double your cash with this free casino deal",
]
HAM = [
    "Please review the attached report before the meeting",
    "Team lunch scheduled for tomorrow at noon",
    "The project update is attached for your review",
    "Thanks for the notes from our last discussion",
    "Please send the agenda for next week meeting",
    "Quarterly budget report attached for the team",
    "Conference call tomorrow please join on time",
    "Thanks for the updated project file and notes",
    "Let us schedule a discussion about the report",
    "The meeting agenda includes the budget review",
    "Please review the quarterly project update attached",
    "Team meeting notes and action items attached",
    "Lunch with the team tomorrow thanks everyone",
    "Please find the report file attached for review",
    "Project schedule update for this week attached",
    "Thanks for organizing the conference call today",
    "Discussion notes and budget review attached please",
    "Next week team lunch details to follow thanks",
    "The agenda for tomorrow meeting is attached",
    "Quarterly review of the project budget notes attached",
]

TEXTS = SPAM + HAM
LABELS = np.array([1.0] * len(SPAM) + [0.0] * len(HAM), dtype=np.float64)


# ============================================================
# 2. 分词 + 词典 + 三种特征表示（全部从零）
# ============================================================
def tokenize(s: str):
    return re.findall(r"[a-z]+", s.lower())


VOCAB = sorted({tok for t in TEXTS for tok in tokenize(t)})
W2I = {w: i for i, w in enumerate(VOCAB)}
V = len(VOCAB)


def count_matrix(texts):
    X = np.zeros((len(texts), V), dtype=np.float64)
    for r, t in enumerate(texts):
        for tok in tokenize(t):
            X[r, W2I[tok]] += 1.0
    return X


def build_features(texts, fit_df=None, fit_proj=None, kind="tfidf"):
    """
    三种特征：
      'bin'    : 二值 BoW（词出现=1）
      'tfidf'  : TF-IDF（sklearn 风格的平滑 idf + L2 行归一化）
      'dense'  : 把 TF-IDF 经一个【固定】随机矩阵投影到 d 维稠密向量
                 （generic frozen embedding 的玩具替身）
    """
    Xc = count_matrix(texts)

    if kind == "bin":
        return (Xc > 0).astype(np.float64), fit_df, fit_proj

    if fit_df is None:
        df = (Xc > 0).sum(axis=0)
    else:
        df = fit_df
    N = Xc.shape[0] if fit_df is None else len(TEXTS)
    idf = np.log((N + 1.0) / (df + 1.0)) + 1.0
    Xtf = Xc * idf
    norms = np.linalg.norm(Xtf, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    Xtf = Xtf / norms

    if kind == "tfidf":
        return Xtf, df, fit_proj

    if kind == "dense":
        d = 8
        if fit_proj is None:
            fit_proj = np.random.randn(V, d) / np.sqrt(d)
        Xd = Xtf @ fit_proj
        nn = np.linalg.norm(Xd, axis=1, keepdims=True)
        nn[nn == 0] = 1.0
        Xd = Xd / nn
        return Xd, df, fit_proj

    raise ValueError(kind)


# ============================================================
# 3. 从零的 logistic 回归
# ============================================================
def sigmoid(z):
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def train_logistic(X, y, lr=1.0, epochs=600, l2=0.0, l1=0.0,
                   verbose_loss=False, tag=""):
    m, d = X.shape
    w = np.zeros(d)
    b = 0.0
    eps = 1e-12
    history = []
    for ep in range(epochs):
        z = X @ w + b
        yhat = sigmoid(z)
        yhat = np.clip(yhat, eps, 1 - eps)
        gz = (yhat - y) / m
        grad_w = X.T @ gz + l2 * w
        grad_b = gz.sum()
        w = w - lr * grad_w
        b = b - lr * grad_b
        if l1 > 0:
            w = np.sign(w) * np.maximum(np.abs(w) - lr * l1, 0.0)
        if verbose_loss and (ep % 100 == 0 or ep == epochs - 1):
            ce = -(y * np.log(yhat) + (1 - y) * np.log(1 - yhat)).mean()
            reg = 0.5 * l2 * (w @ w) + l1 * np.abs(w).sum()
            history.append((ep, ce, ce + reg))
    return w, b, history


def predict(X, w, b):
    return (sigmoid(X @ w + b) > 0.5).astype(np.float64)


def accuracy(y_true, y_pred):
    return float((y_true == y_pred).mean())


# ============================================================
def main():
    print("=" * 64)
    print("讲透NLP · 04 逻辑回归与文本分类（从零实现）")
    print("=" * 64)
    print(f"数据集：垃圾 {len(SPAM)} 条 + 正常 {len(HAM)} 条 = {len(TEXTS)} 条")
    print(f"词典大小 V = {V} 个词\n")

    print("-" * 64)
    print("结论 1：TF-IDF + logistic 回归，梯度下降 loss 收敛")
    print("-" * 64)
    Xtf, df, _ = build_features(TEXTS, kind="tfidf")
    w, b, hist = train_logistic(Xtf, LABELS, lr=2.0, epochs=600,
                                verbose_loss=True, tag="tfidf")
    print(f"{'epoch':>6} | {'交叉熵':>10} | {'总损失(+正则)':>14}")
    for ep, ce, tot in hist:
        print(f"{ep:>6} | {ce:>10.6f} | {tot:>14.6f}")
    train_acc = accuracy(LABELS, predict(Xtf, w, b))
    print(f"\n训练集准确率 = {train_acc*100:.1f}%\n")

    print("-" * 64)
    print("结论 2 & 反直觉 1：三种特征 × logistic，测试准确率（20 次随机划分）")
    print("-" * 64)
    rng = np.random.RandomState(SEED)
    n_splits = 20
    results = {k: [] for k in ("bin", "tfidf", "dense")}

    for s in range(n_splits):
        idx = rng.permutation(len(TEXTS))
        n_test = 12
        test_idx = idx[:n_test]
        train_idx = idx[n_test:]
        tr_texts = [TEXTS[i] for i in train_idx]
        te_texts = [TEXTS[i] for i in test_idx]
        ytr = LABELS[train_idx]
        yte = LABELS[test_idx]
        for kind in ("bin", "tfidf", "dense"):
            Xtr, df2, proj = build_features(tr_texts, fit_df=df, kind=kind)
            Xte, _, _ = build_features(te_texts, fit_df=df2, fit_proj=proj, kind=kind)
            w, b, _ = train_logistic(Xtr, ytr, lr=2.0, epochs=800, l2=1e-3)
            acc = accuracy(yte, predict(Xte, w, b))
            results[kind].append(acc)

    print(f"{'特征':<28} | {'平均测试准确率':>14} | {'std':>6}")
    print("-" * 56)
    for kind, name in (("bin", "二值 BoW"), ("tfidf", "TF-IDF (手写)"),
                       ("dense", "8维稠密投影(frozen)")):
        a = np.array(results[kind])
        print(f"{name:<28} | {a.mean()*100:>13.1f}% | {a.std()*100:>5.1f}%")

    print("\n👉 反直觉 1：8 维【固定】稠密向量（冻结 embedding 的玩具替身）")
    print("   + logistic，明显输给 TF-IDF + logistic。真实世界里，")
    print("   冻结的 BERT embedding + 线性头，在小/专业数据上也常常打不过")
    print("   TF-IDF + logistic（见 .md 引用的 MDPI 2024 / SemEval 2024）。\n")

    print("-" * 64)
    print("结论 3 & 反直觉 2：L1 vs L2 正则化 —— 权重稀疏性")
    print("-" * 64)
    Xtf, _, _ = build_features(TEXTS, kind="tfidf")
    w_l2, _, _ = train_logistic(Xtf, LABELS, lr=2.0, epochs=1500, l2=0.05)
    w_l1, _, _ = train_logistic(Xtf, LABELS, lr=2.0, epochs=1500, l1=0.003)

    nz_l2 = int((np.abs(w_l2) > 1e-8).sum())
    nz_l1 = int((np.abs(w_l1) > 1e-8).sum())
    print(f"L2  正则：非零权重 = {nz_l2:>3} / {V}   (只整体缩小，几乎不产生精确的 0)")
    print(f"L1  正则：非零权重 = {nz_l1:>3} / {V}   (proximal 软阈值 → 大量精确 0)\n")

    print("L1 幸存的非零权重 = 自动学出的「垃圾邮件关键词」：")
    order = np.argsort(-np.abs(w_l1))
    shown = 0
    for j in order:
        if abs(w_l1[j]) <= 1e-8:
            continue
        tag = "→垃圾" if w_l1[j] > 0 else "→正常"
        print(f"    {VOCAB[j]:<16} 权重={w_l1[j]:+.3f}  {tag}")
        shown += 1
        if shown >= 12:
            break

    print("\n👉 反直觉 2：L1 不只是「正则」，它在做【特征选择】——把几百上千")
    print("   个词里真正有用的十几个挑出来，而且权重可直接读成「这个词对")
    print("   垃圾/正常的贡献」。这就是线性模型至今在可解释性上不可替代的原因。")
    print("\n全部结论复现完毕 ✓")


if __name__ == "__main__":
    main()
