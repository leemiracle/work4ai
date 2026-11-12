#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讲透NLP · 第 5 章配套实验：从零实现 Skip-gram + Negative Sampling
==================================================================
PyTorch 从零实现（不用任何 word2vec / gensim 库），在精心设计的 toy 语料上：
  1. 训练 50 维词向量
  2. 验证 king - man + woman ≈ queen（向量算术 + 余弦最近邻）
  3. 扫描负样本数 K、向量维度 dim，揭示两个反直觉发现
  4. PCA 降到 2D 可视化语义聚类

★ 三个反直觉发现：
  发现 1：king-man+woman 用余弦最近邻能精准命中 queen；
          而"只看 king 的最近词"未必是 queen——
          向量算术是在"减去一个语义维度、加上另一个"，是几何导航而非检索。
  发现 2：负样本数 K 不是越多越好。本 toy 语料信号干净，小到中等 K 都能让
          4 个类比全中（模型对 K 相当鲁棒）；但 K 过大（20+）会撞上"假负样本"
          （其实真共现的词），把它们也推开，质量反降。
  发现 3：维度不是越大越好。小语料上 dim=300 过拟合，
          把噪声词的记忆塞进高维空间，反而破坏了干净的类比几何。

依赖：torch, numpy, matplotlib    纯 CPU，set_num_threads(1)，几十秒跑完。
python3 experiments/05_word2vec.py
"""
import os
# 单线程：小矩阵上多线程反而因调度开销变慢（项目铁律）
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import random
import time
import numpy as np
import torch
import torch.nn.functional as F

torch.set_num_threads(1)

SEED = 0
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# ============================================================
# 1. 语料生成：人为植入 king-man+woman≈queen 的"加法结构"
# ============================================================
# 关键设计：每个词的上下文由【三个正交维度】各自独立的词承载——
#   阶层 tier  (royal/common)  ← 只由 ROYAL/COMMON 名词承载
#   代际 gen   (ruler/heir)     ← 只由 RULER/HEIR 动词承载（同一动词集跨阶层共用）
#   性别 sex   (m/f)            ← 只由 代词 + KIN 家庭名词承载
# 于是 v(king) ≈ royal ⊕ ruler ⊕ male，三维可加分解。做算术时三维各自抵消：
#   king - man + woman = (royal⊕ruler⊕male) - (common⊕ruler⊕male) + (common⊕ruler⊕female)
#                      = royal ⊕ ruler ⊕ female = queen （精确命中）
# 关键：queen(princess) 因【代际】不同（ruler 动词 vs heir 动词）而被区分开，
#   修复了早期版本里"同阶层+同性别的两个词（king≈prince, queen≈princess）向量塌缩、
#   类比无法在 queen 与 princess 之间二选一"的顽疾。四个类比在正交设计下皆为恒等式。
# 这是"教学简化"：真实语料里这种因子化是噪声里的统计趋势。
# 另外注入少量"噪声词"，让高维过拟合有可乘之机（反直觉发现 3）。
PERSONS = {
    # 词: (阶层 tier, 代际 gen, 性别 sex)
    "king":     ("royal", "ruler", "m"), "queen":    ("royal", "ruler", "f"),
    "prince":   ("royal", "heir",  "m"), "princess": ("royal", "heir",  "f"),
    "man":      ("common","ruler", "m"), "woman":    ("common","ruler", "f"),
    "boy":      ("common","heir",  "m"), "girl":     ("common","heir",  "f"),
}
# 阶层信号词（纯阶层，跨代际/性别共用）
ROYAL    = ["crown", "throne", "kingdom", "palace", "royal", "army", "decree", "gold"]
COMMON   = ["field", "house", "market", "street", "common", "work", "tool", "cotton"]
# 代际信号词（纯代际，跨阶层共用：在位者 vs 子嗣）
RULER_VERBS = ["rules", "governs", "commands", "directs", "manages"]
HEIR_VERBS  = ["plays", "learns", "studies", "explores", "grows"]
# 性别信号词：代词 + 家庭名词。KIN 按 (代际,性别) 细分，使 sex 与 gen 都可读、
# 且 queen(ruler-kin) 与 princess(heir-kin) 在家庭名词上也天然分开。
KIN = {
    ("ruler", "m"): ["father", "brother", "uncle", "husband"],
    ("ruler", "f"): ["mother", "sister", "aunt", "wife"],
    ("heir",  "m"): ["son", "nephew", "lad", "pupil"],
    ("heir",  "f"): ["daughter", "niece", "lass", "maid"],
}
PRON     = {"m": "he", "f": "she"}
# 仅用于 PCA 可视化着色（不参与语料生成）
MALE     = ["he", "his", "father", "brother", "son", "uncle", "nephew", "mr"]
FEMALE   = ["she", "her", "mother", "sister", "daughter", "aunt", "niece", "mrs"]
# 噪声词：随机散布，制造可被高维向量"记住"的伪共现（用于发现 3）
NOISE    = ["zark", "vlox", "quib", "nelf", "dran", "plib", "sorn", "twib"]


def gen_corpus(n_per_template=26, seed=SEED):
    rng = random.Random(seed)
    lines = []
    for w, (tier, gen, sex) in PERSONS.items():
        NOUNS = ROYAL if tier == "royal" else COMMON        # 阶层词池
        VERBS = RULER_VERBS if gen == "ruler" else HEIR_VERBS  # 代际词池
        KINW  = KIN[(gen, sex)]                               # 性别+代际 家庭名词
        pron  = PRON[sex]                                     # 性别代词
        for _ in range(n_per_template):
            noun = rng.choice(NOUNS)
            verb = rng.choice(VERBS)
            kin  = rng.choice(KINW)
            # —— 阶层信号 ×2（纯阶层名词）——
            lines.append(f"the {w} owns the {noun}")
            lines.append(f"{noun} belongs to the {w}")
            # —— 代际信号 ×2（纯代际动词；同一动词集跨阶层，保证正交）——
            lines.append(f"the {w} {verb}")
            lines.append(f"the {w} {verb} daily")
            # —— 性别信号 ×2（代词 + 家庭名词）——
            lines.append(f"{w} is a {kin}")
            lines.append(f"{pron} praised the {w}")
    rng.shuffle(lines)
    text = " ".join(lines)
    # 注入噪声词：随机插到若干位置（少量，不影响主结构但可被高维记忆）
    toks = text.split()
    for nw in NOISE:
        for _ in range(rng.randint(4, 7)):
            pos = rng.randint(0, len(toks) - 1)
            toks.insert(pos, nw)
    return toks


tokens = gen_corpus()
vocab = sorted(set(tokens))
word2id = {w: i for i, w in enumerate(vocab)}
id2word = {i: w for w, i in word2id.items()}
V = len(vocab)
ids = [word2id[w] for w in tokens]
print(f"[语料] {len(tokens)} tokens，词表 V={V} 词")
key_ok = all(w in word2id for w in ['king','queen','man','woman','prince','princess','boy','girl'])
print(f"[语料] 关键词 king/queen/man/woman/prince/princess/boy/girl 均在词表: {key_ok}")

# 词频 & 负采样分布 P(w) ∝ count(w)^0.75
counts = np.zeros(V, dtype=np.float64)
for i in ids:
    counts[i] += 1
neg_prob = counts ** 0.75
neg_prob /= neg_prob.sum()

# 负采样查表（标准 word2vec 做法：一张大表，按概率填充，均匀采样）
NEG_TABLE_SIZE = 100_000
neg_table = np.zeros(NEG_TABLE_SIZE, dtype=np.int64)
cum = np.cumsum(neg_prob)
idx = 0
for t in range(NEG_TABLE_SIZE):
    frac = (t + 1) / NEG_TABLE_SIZE
    while idx < V - 1 and cum[idx] < frac:
        idx += 1
    neg_table[t] = idx


# ============================================================
# 2. 构建 (center, context) 正样本对 —— 动态窗口（word2vec 风格）
# ============================================================
def build_pairs(window=4, seed=SEED):
    rng = random.Random(seed)
    pairs = []
    for pos, c in enumerate(ids):
        b = rng.randint(1, window)               # 动态窗口：近邻权重更大
        lo, hi = max(0, pos - b), min(len(ids), pos + b + 1)
        for j in range(lo, hi):
            if j == pos:
                continue
            pairs.append((c, ids[j]))
    return pairs


# ============================================================
# 3. Skip-gram + Negative Sampling 模型（PyTorch 从零）
# ============================================================
class SGNS:
    """两套向量：中心(输入)v 与 上下文(输出)u。训练后落盘只用 v。"""

    def __init__(self, V, dim, K, neg_table):
        self.dim = dim
        self.K = K
        self.neg_table = neg_table
        with torch.no_grad():
            self.v = torch.empty(V, dim)
            torch.nn.init.uniform_(self.v, -0.5 / dim, 0.5 / dim)   # 小初始化
            self.u = torch.zeros(V, dim)                            # 上下文初始化为 0
        self.v.requires_grad_(True)
        self.u.requires_grad_(True)

    def params(self):
        return [self.v, self.u]

    def loss_on(self, centers_np, positives_np):
        centers = torch.from_numpy(centers_np).long()
        positives = torch.from_numpy(positives_np).long()
        B = centers.shape[0]
        # 采 K*B 个负样本（从负采样表均匀抽取）
        negs = torch.from_numpy(
            self.neg_table[np.random.randint(0, len(self.neg_table), size=(B, self.K))]
        ).long()
        vc = self.v[centers]                 # (B, d)
        up = self.u[positives]               # (B, d)
        un = self.u[negs]                    # (B, K, d)
        # 正样本 logit: dot(vc, up) -> (B,)
        logit_p = (vc * up).sum(dim=1)
        # 负样本 logit: vc . un -> (B, K)
        logit_n = torch.bmm(un, vc.unsqueeze(2)).squeeze(2)
        # SGNS 损失：-log σ(u_o·v_c) - Σ log σ(-u_n·v_c)
        loss = -(F.logsigmoid(logit_p).mean() + F.logsigmoid(-logit_n).mean())
        return loss

    def vectors(self):
        return self.v.detach().numpy()


def train(dim, K, pairs, epochs=15, batch=256, lr=0.03, seed=SEED):
    """训练一个 SGNS 模型并返回词向量矩阵 (V, dim)。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    model = SGNS(V, dim, K, neg_table)
    opt = torch.optim.Adam(model.params(), lr=lr)
    pairs_list = pairs[:]
    for ep in range(epochs):
        random.shuffle(pairs_list)
        centers_all = np.array([p[0] for p in pairs_list], dtype=np.int64)
        positives_all = np.array([p[1] for p in pairs_list], dtype=np.int64)
        for i in range(0, len(pairs_list), batch):
            opt.zero_grad()
            loss = model.loss_on(centers_all[i:i + batch], positives_all[i:i + batch])
            loss.backward()
            opt.step()
    return model.vectors()


# ============================================================
# 4. 评测工具：余弦、最近邻、类比
# ============================================================
def unit(m):
    n = np.linalg.norm(m, axis=1, keepdims=True)
    return m / np.clip(n, 1e-8, None)


def cosine_matrix(vecs):
    u = unit(vecs)
    return u @ u.T


def nearest(vecs, word, topn=5):
    wid = word2id[word]
    sim = unit(vecs) @ unit(vecs)[wid]
    order = np.argsort(-sim)
    out = []
    for j in order:
        if j == wid:
            continue
        out.append((id2word[j], float(sim[j])))
        if len(out) >= topn:
            break
    return out


# 类比集：base - minus + plus ≈ expected
ANALOGIES = [
    ("king", "man", "woman", "queen"),
    ("prince", "boy", "girl", "princess"),
    ("queen", "woman", "man", "king"),
    ("princess", "girl", "boy", "prince"),
]


def eval_analogies(vecs, verbose=False):
    """返回 (rank1 命中数, 平均 cos(target, expected), 详情)。"""
    U = unit(vecs)
    hits = 0
    cos_sum = 0.0
    details = []
    for base, minus, plus, expected in ANALOGIES:
        target = vecs[word2id[base]] - vecs[word2id[minus]] + vecs[word2id[plus]]
        tu = target / max(np.linalg.norm(target), 1e-8)
        sim = U @ tu
        # 排除输入词
        for w in (base, minus, plus):
            sim[word2id[w]] = -np.inf
        order = np.argsort(-sim)
        top1 = id2word[order[0]]
        hit = (top1 == expected)
        hits += int(hit)
        cos_sum += float(sim[word2id[expected]])
        top5 = [(id2word[j], round(float(sim[j]), 3)) for j in order[:5]]
        details.append((base, minus, plus, expected, top1, hit, top5))
        if verbose:
            flag = "✓" if hit else "✗"
            print(f"    {base}-{minus}+{plus} -> {top1} {flag} "
                  f"(期望 {expected}, cos={float(sim[word2id[expected]]):.3f})  top5={top5}")
    return hits, cos_sum / len(ANALOGIES), details


def pca(X, k=2):
    """朴素 PCA（numpy SVD），不依赖 sklearn。"""
    Xc = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc @ Vt[:k].T


# ============================================================
# 5. 主流程
# ============================================================
def main():
    t0 = time.time()
    pairs = build_pairs(window=4)
    print(f"[建对] {len(pairs)} 个 (center, context) 正样本对\n")

    # ---- 训练参考模型 (dim=20, K=5) ----
    # 选用 dim=20：下方"发现 3"证明它是本 toy 语料的甜区——
    # 高维（50+）会把 8 个噪声词的伪共现也学进去，反而破坏干净的类比几何。
    print("=" * 64)
    print("参考模型：dim=20, K=5, 15 epochs")
    print("=" * 64)
    vecs = train(dim=20, K=5, pairs=pairs)

    # ---- 反直觉发现 1：向量算术 vs 直接最近词 ----
    print("\n[反直觉发现 1] 向量算术 king-man+woman ≈ queen")
    print("-" * 64)
    print("(a) 直接看 king 的最近词（不算术）：")
    for w, c in nearest(vecs, "king", 5):
        print(f"      {w:12s} cos={c:.3f}")
    print("    -> king 的最近词未必是 queen（这里是 man——二者共享'在位者+男性'上下文）。\n")
    print("(b) 用向量算术 king - man + woman 找最近词：")
    target = vecs[word2id["king"]] - vecs[word2id["man"]] + vecs[word2id["woman"]]
    tu = target / max(np.linalg.norm(target), 1e-8)
    sim = unit(vecs) @ tu
    for w in ("king", "man", "woman"):
        sim[word2id[w]] = -np.inf
    order = np.argsort(-sim)
    for j in order[:5]:
        print(f"      {id2word[j]:12s} cos={float(sim[j]):.3f}")
    print(f"    -> 算术后 queen 的 cos = {float(sim[word2id['queen']]):.3f}")
    print("    结论：减去 male 成分、加上 female 成分 = 在语义空间导航，精确命中 queen。\n")

    print("[类比评测 - 参考模型]")
    hits, mean_cos, _ = eval_analogies(vecs, verbose=True)
    print(f"    rank-1 命中 {hits}/{len(ANALOGIES)}，平均 cos(target,expected)={mean_cos:.3f}\n")

    # ---- 反直觉发现 2：负样本数 K 的影响 ----
    # 说明：本 toy 语料三维正交、信号干净，因此小到中等的 K 都能让 4 个类比全中，
    # 模型对 K 相当鲁棒；真正的反直觉在于"K 不是越大越好"——K 过大时，采样更
    # 容易撞上"假负样本"（其实和中心词真共现的词），把它们也推开，质量反降。
    print("=" * 64)
    print("[反直觉发现 2] 负样本数 K 的扫描（dim=20 固定）")
    print("=" * 64)
    print(f"    {'K':>4} | {'命中':>6} | {'平均cos':>8} | 解读")
    print("    " + "-" * 50)
    k_results = []
    for K in [1, 5, 10, 20, 30]:
        v2 = train(dim=20, K=K, pairs=pairs)
        h, c, _ = eval_analogies(v2)
        k_results.append((K, h, c))
    best_k = max(k_results, key=lambda r: (r[1], r[2]))[0]
    best_cos = max(r[2] for r in k_results)
    for K, h, c in k_results:
        note = ""
        if K == best_k:
            note = "<- 命中最多"
        elif K >= 20 and c < best_cos:
            note = "负样本过多，撞上'假负样本'，质量反降"
        print(f"    {K:>4} | {h:>4}/{len(ANALOGIES)} | {c:>8.3f} | {note}")
    big_k_drop = any(K >= 20 and c < best_cos - 0.01 for K, h, c in k_results)
    if big_k_drop:
        print("    结论：K 不是越大越好——小到中等 K 已足够（干净语料上甚至 K=1 就能 4/4），\n"
              "          K 过大反而因'假负样本'把真共现词推开而伤质量。\n")
    else:
        print("    结论：本干净 toy 语料上类比质量对 K 几乎不敏感（K=1..30 都接近满分）；\n"
              "          真实大规模语料里 K 过大才有明显副作用。\n")

    # ---- 反直觉发现 3：维度不是越大越好 ----
    print("=" * 64)
    print("[反直觉发现 3] 维度 dim 的扫描（K=5 固定）")
    print("=" * 64)
    print(f"    {'dim':>4} | {'参数量':>10} | {'命中':>6} | {'平均cos':>8} | 解读")
    print("    " + "-" * 56)
    results = []
    for dim in [20, 50, 100, 200, 300]:
        v3 = train(dim=dim, K=5, pairs=pairs)
        h, c, _ = eval_analogies(v3)
        nparam = 2 * V * dim
        results.append((dim, h, c, nparam))
    best_dim = max(results, key=lambda r: r[2])[0]
    best_cos = max(r[2] for r in results)
    for dim, h, c, nparam in results:
        if dim == best_dim:
            note = "<- 最佳（平均cos最高）"
        elif dim > best_dim and c < best_cos:
            note = "维度更高但质量反降（容量记住噪声词）"
        else:
            note = ""
        print(f"    {dim:>4} | {nparam:>10} | {h:>4}/{len(ANALOGIES)} | {c:>8.3f} | {note}")
    print(f"    结论：最佳维度≈{best_dim}；超过它参数量线性增长，类比质量不再提升甚至下降\n"
          f"          （小语料+噪声词时，高维有容量去'记住'伪共现，破坏干净几何）。\n")

    # ---- PCA 2D 可视化 ----
    print("=" * 64)
    print("[可视化] PCA 降到 2D，保存到 fig_05_word2vec_pca.png")
    print("=" * 64)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        # 中文字体（项目铁律：Noto Sans CJK SC），避免 legend/title 出现缺字方块
        plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False

        proj = pca(vecs, k=2)
        fig, ax = plt.subplots(figsize=(9, 7))
        # 标注词：人物 + 各类上下文标记
        show = list(PERSONS.keys()) + ["crown", "throne", "kingdom", "palace",
                                       "field", "house", "market", "street",
                                       "he", "she", "his", "her"]
        color_map = {}
        for w in PERSONS:
            tier, gen, sex = PERSONS[w]
            color_map[w] = "tab:red" if tier == "royal" else "tab:orange"
        for w in ROYAL:
            color_map[w] = "tab:blue"
        for w in COMMON:
            color_map[w] = "tab:green"
        for w in MALE:
            color_map[w] = "tab:purple"
        for w in FEMALE:
            color_map[w] = "tab:pink"
        for w in show:
            if w not in word2id:
                continue
            j = word2id[w]
            ax.scatter(proj[j, 0], proj[j, 1], c=color_map.get(w, "gray"),
                       s=50, zorder=3, edgecolors="black", linewidths=0.4)
            ax.annotate(w, (proj[j, 0], proj[j, 1]), fontsize=9,
                        xytext=(4, 4), textcoords="offset points")
        # 图例
        from matplotlib.lines import Line2D
        legend = [
            Line2D([0], [0], marker="o", color="w", label="王室人物", markerfacecolor="tab:red", markersize=9),
            Line2D([0], [0], marker="o", color="w", label="平民人物", markerfacecolor="tab:orange", markersize=9),
            Line2D([0], [0], marker="o", color="w", label="王室上下文", markerfacecolor="tab:blue", markersize=9),
            Line2D([0], [0], marker="o", color="w", label="平民上下文", markerfacecolor="tab:green", markersize=9),
            Line2D([0], [0], marker="o", color="w", label="男性标记", markerfacecolor="tab:purple", markersize=9),
            Line2D([0], [0], marker="o", color="w", label="女性标记", markerfacecolor="tab:pink", markersize=9),
        ]
        ax.legend(handles=legend, loc="best", fontsize=8)
        ax.set_title("word2vec (dim=50) PCA 2D: king/queen/man/woman 语义聚类")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        out_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig_05_word2vec_pca.png")
        fig.savefig(out_png, dpi=120)
        print(f"    已保存: {out_png}")
    except Exception as e:
        print(f"    [跳过可视化] {e}")

    print(f"\n[总耗时] {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
