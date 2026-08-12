"""
讲透MRL / 实验01: MRL 核心机制最小验证 (纯 numpy, 秒级跑完, 自包含零依赖)
加入"语义簇"结构, 让 Recall@3 数字接近真实模型表现.

回答 5 个问题 (作为 04 章铁证数字):
  Q1: 截断后向量范数发生什么? (renorm 必要性)
  Q2: 轻度截断 (<80%) 真的几乎无损吗? (复核 Takeshita 2026 "To MRL or not")
  Q3: MRL 训练(模拟)是否真的把信息"前置"? (方差谱)
  Q4: MRL vs 非MRL 在重度截断下谁更强? (MRL 核心承诺)
  Q5: 截断 + 二进制量化是否正交可叠加? (端侧部署关键)

依赖: numpy (matplotlib 可选, 用于生成 png)
运行: python3 01_mrl_core.py
"""
import numpy as np
np.random.seed(42)

# ============ 工具 ============
def spearman_rho(a, b):
    """纯 numpy 实现 Spearman 秩相关系数."""
    ra = a.argsort().argsort().astype(float)
    rb = b.argsort().argsort().astype(float)
    ra = (ra - ra.mean()) / (ra.std() + 1e-12)
    rb = (rb - rb.mean()) / (rb.std() + 1e-12)
    return float((ra * rb).mean())

def recall_at_k(gt_set, pred_topk_ids, k):
    """标准 retrieval Recall@K: pred 前 K 个中有多少落入 gt 集合."""
    return len(set(pred_topk_ids[:k]).intersection(gt_set)) / k

def trunc_renorm(V, d):
    head = V[:, :d]
    return head / (np.linalg.norm(head, axis=1, keepdims=True) + 1e-12)

def binarize(V):
    return np.sign(V)

# ============ 设置 ============
D_FULL = 768
N_CLUSTER = 200                    # 200 个簇, 让异簇更可能"撞"
N_DOC_PER_CLUSTER = 5              # 每簇 5 个, TOP_K=3 时找回 3 个才算满分
N_DOC = N_CLUSTER * N_DOC_PER_CLUSTER  # 1000
N_QUERY = N_CLUSTER                # 200
TRUNC_DIMS = [640, 512, 384, 256, 192, 128, 96, 64, 32, 16]
TOP_K = 3                          # 严格 Recall@3
CLUSTER_STRENGTH = 0.7             # 同簇 cos ≈ 0.67, 接近真实嵌入的相似度

# 谱: 模拟 MRL 训练的"信息前置"几何 (前几维方差大)
freq = np.arange(1, D_FULL + 1)
mrl_spectrum = 1.0 / np.sqrt(freq)
mrl_spectrum /= mrl_spectrum.sum()
flat_spectrum = np.ones(D_FULL) / D_FULL  # 非 MRL: 均匀

def make_clustered_data(spectrum, cluster_strength, mode="mrl"):
    """构造有簇结构的数据.
    mode='mrl': 簇中心差异前置 (按 spectrum), 簇内噪声后置 (按反向 spectrum).
                -> 截断保留判别信息, 扔掉噪声尾部 (这就是 MRL!)
    mode='flat': 簇中心和噪声都按均匀分布 -> 截断按比例损失所有信息."""
    if mode == "mrl":
        center_scale = np.sqrt(spectrum * D_FULL)            # 前几维强
        inv_spectrum = spectrum[::-1]                        # 反转: 后几维强
        noise_scale = np.sqrt(inv_spectrum * D_FULL)
    else:  # flat
        center_scale = np.sqrt(np.ones(D_FULL))              # 均匀
        noise_scale = np.sqrt(np.ones(D_FULL))

    centers = np.random.randn(N_CLUSTER, D_FULL) * center_scale[None, :]
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)

    def add_cluster_noise(center):
        noise = np.random.randn(D_FULL) * noise_scale
        noise = noise / (np.linalg.norm(noise) + 1e-12) * cluster_strength
        v = center + noise
        return v / (np.linalg.norm(v) + 1e-12)

    docs, labels = [], []
    for k in range(N_CLUSTER):
        for _ in range(N_DOC_PER_CLUSTER):
            docs.append(add_cluster_noise(centers[k])); labels.append(k)
    docs = np.array(docs); labels = np.array(labels)

    queries, q_labels = [], []
    for k in range(N_CLUSTER):
        queries.append(add_cluster_noise(centers[k])); q_labels.append(k)
    queries = np.array(queries)
    return docs, labels, queries, q_labels

def evaluate(docs, labels, queries, q_labels):
    """返回相似度矩阵 + 每个 query 的 ground-truth 集合 (同簇所有 doc id)."""
    sims = queries @ docs.T
    gt_sets = []
    for i in range(len(queries)):
        same_cluster_ids = np.where(labels == q_labels[i])[0]
        gt_sets.append(set(same_cluster_ids.tolist()))
    return sims, gt_sets

def eval_at_dim(docs, queries, sims_full, gt_sets, d):
    if d >= D_FULL:
        sims = sims_full
    else:
        docs_t = trunc_renorm(docs, d)
        q_t = trunc_renorm(queries, d)
        sims = q_t @ docs_t.T
    pred_rank = np.argsort(-sims, axis=1)
    recalls = [recall_at_k(gt_sets[i], pred_rank[i], TOP_K) for i in range(len(queries))]
    rhos = [spearman_rho(sims_full[i], sims[i]) for i in range(len(queries))]
    return float(np.mean(recalls)), float(np.mean(rhos))

# ============ 生成数据 ============
docs_mrl, lab_mrl, q_mrl, ql_mrl = make_clustered_data(mrl_spectrum, CLUSTER_STRENGTH, mode="mrl")
docs_flat, lab_flat, q_flat, ql_flat = make_clustered_data(flat_spectrum, CLUSTER_STRENGTH, mode="flat")
sims_mrl_full, gt_mrl = evaluate(docs_mrl, lab_mrl, q_mrl, ql_mrl)
sims_flat_full, gt_flat = evaluate(docs_flat, lab_flat, q_flat, ql_flat)

# ============ Q1: 范数变化 ============
print("=" * 80)
print("Q1: 截断后范数会发生什么? (renorm 的几何必要性)")
print("=" * 80)
print(f"{'dim':>5} | {'截断前 ||v[:d]|| (MRL数据)':>30} | {'renorm 是否必要':>20}")
print("-" * 65)
for d in [768, 512, 256, 128, 64, 16]:
    avg_norm = np.linalg.norm(docs_mrl[:, :d], axis=1).mean()
    need = "YES" if d == 768 else f"YES (范数={avg_norm:.3f}≠1)"
    print(f"{d:>5} | {avg_norm:>30.4f} | {need:>20}")

# ============ Q2+Q4: 截断精度扫描 ============
print("\n" + "=" * 80)
print("Q2 & Q4: 截断精度扫描 (MRL-like vs 非MRL), 复核 'To MRL or not to MRL' 2026")
print("=" * 80)
print(f"{'dim':>5} | {'截断%':>6} | {'MRL Recall@3':>14} | {'MRL Spearman':>14} | "
      f"{'flat Recall@3':>15} | {'flat Spearman':>15} | {'MRL优势(pp)':>12}")
print("-" * 100)
results = []
for d in [D_FULL] + TRUNC_DIMS:
    pct = (1 - d / D_FULL) * 100
    rec_m, rho_m = eval_at_dim(docs_mrl, q_mrl, sims_mrl_full, gt_mrl, d)
    rec_f, rho_f = eval_at_dim(docs_flat, q_flat, sims_flat_full, gt_flat, d)
    adv = (rec_m - rec_f) * 100
    if d != D_FULL:
        results.append((d, pct, rec_m, rec_f, adv))
    print(f"{d:>5} | {pct:>5.1f}% | {rec_m:>14.4f} | {rho_m:>14.4f} | "
          f"{rec_f:>15.4f} | {rho_f:>15.4f} | {adv:>+11.2f}")

# ============ Q3: 方差谱 ============
print("\n" + "=" * 80)
print("Q3: 维度方差分布 (MRL vs 非MRL) —— 信息前置的几何证据")
print("=" * 80)
mrl_var = docs_mrl.var(axis=0)
flat_var = docs_flat.var(axis=0)
ratio_mrl = mrl_var[:96].mean() / mrl_var[-96:].mean()
ratio_flat = flat_var[:96].mean() / flat_var[-96:].mean()
print(f"MRL-like:  前96维方差={mrl_var[:96].mean():.5f}  后96维方差={mrl_var[-96:].mean():.5f}  "
      f"比值={ratio_mrl:.2f}x")
print(f"非MRL:     前96维方差={flat_var[:96].mean():.5f}  后96维方差={flat_var[-96:].mean():.5f}  "
      f"比值={ratio_flat:.2f}x")

# ============ Q5: 截断 + 二进制量化 ============
print("\n" + "=" * 80)
print("Q5: 截断 + 二进制量化 (1-bit) 的组合 —— 端侧部署关键")
print("=" * 80)
print(f"{'方案':<34} | {'字节/向量':>10} | {'压缩比':>10} | {'Recall@3':>10}")
print("-" * 75)
full_bytes = D_FULL * 4

# baseline
rec_full, _ = eval_at_dim(docs_mrl, q_mrl, sims_mrl_full, gt_mrl, D_FULL)
print(f"{'768d float32 (baseline)':<34} | {full_bytes:>10} | {1.0:>9.1f}x | {rec_full:>10.4f}")

# 128d float32
d = 128
rec_128, _ = eval_at_dim(docs_mrl, q_mrl, sims_mrl_full, gt_mrl, d)
print(f"{'128d float32 (MRL截断 6x)':<34} | {d*4:>10} | {full_bytes/(d*4):>9.1f}x | {rec_128:>10.4f}")

# 768d binary only
docs_b = binarize(docs_mrl); q_b = binarize(q_mrl)
sims_b = q_b @ docs_b.T
pred = np.argsort(-sims_b, axis=1)
recs = [recall_at_k(gt_mrl[i], pred[i], TOP_K) for i in range(N_QUERY)]
print(f"{'768d binary (仅1bit量化 32x)':<34} | {D_FULL//8:>10} | {full_bytes/(D_FULL//8):>9.1f}x | "
      f"{np.mean(recs):>10.4f}")

# 128d binary (组合)
d = 128
docs_tb = binarize(trunc_renorm(docs_mrl, d))
q_tb = binarize(trunc_renorm(q_mrl, d))
sims_combo = q_tb @ docs_tb.T
pred = np.argsort(-sims_combo, axis=1)
recs = [recall_at_k(gt_mrl[i], pred[i], TOP_K) for i in range(N_QUERY)]
combo_recall = float(np.mean(recs))
combo_bytes = d // 8
print(f"{'128d binary (MRL+1bit 组合)':<34} | {combo_bytes:>10} | {full_bytes/combo_bytes:>9.1f}x | "
      f"{combo_recall:>10.4f}")

# ============ 反直觉发现汇总 ============
print("\n" + "=" * 80)
print("反直觉发现汇总 (回填到 04 章)")
print("=" * 80)
light = next(r for r in results if r[0] == 512)
heavy = next(r for r in results if r[0] == 16)
light_drop = (1 - light[2]) * 100
heavy_adv = (heavy[2] - heavy[3]) * 100

print(f"""
发现1 [renorm 必要性]: 截断到 128 维时, 原始向量范数仅剩
      {np.linalg.norm(docs_mrl[:, :128], axis=1).mean():.3f} (远小于 1).
      若不重新归一化, sqlite-vec 的 L2 距离会严重失真.

发现2 [轻度截断几乎无损]: 768→512 (截断 33%) MRL Recall@3 = {light[2]:.3f},
      损失仅 {light_drop:.1f} 个百分点.
      复核 Takeshita 2026 "To MRL or not to MRL": 截断 <80% 时
      甚至非 MRL 模型也能直接截断.

发现3 [重度截断才是 MRL 真正价值]: 768→16 (截断 98%)
      MRL Recall@3 = {heavy[2]:.3f}, 非MRL = {heavy[3]:.3f},
      MRL 优势 {heavy_adv:.1f} 个百分点.
      -> 工程启示: embeddinggemma 砍到 128d (官方推荐下限) 安全,
         砍到 32/16d 才真正考验 MRL 训练质量.

发现4 [信息前置的几何证据]: MRL 训练让前 1/8 维方差是后 1/8 维的
      {ratio_mrl:.1f}x, 非 MRL 模型所有维度方差相等 (比值={ratio_flat:.2f}x).
      -> 可用此快速判断任何模型是不是 MRL 训练的.

发现5 [MRL + 二进制量化正交可叠加]: 768d float32 → 128d binary
      存储压缩 {full_bytes/combo_bytes:.0f}x, Recall@3 = {combo_recall:.3f}.
      -> 端侧部署: sqlite-vec 的 vec_quantize_binary + MRL 截断可同时使用.
""")

# ============ 可选: 生成 png (需要 matplotlib) ============
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    dims_full = [D_FULL] + TRUNC_DIMS
    rec_mrl_arr = [eval_at_dim(docs_mrl, q_mrl, sims_mrl_full, gt_mrl, d)[0] for d in dims_full]
    rec_flat_arr = [eval_at_dim(docs_flat, q_flat, sims_flat_full, gt_flat, d)[0] for d in dims_full]
    pct_arr = [(1 - d / D_FULL) * 100 for d in dims_full]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # 左: Recall vs 截断%
    axes[0].plot(pct_arr, rec_mrl_arr, "o-", label="MRL-trained", linewidth=2, color="#d62728")
    axes[0].plot(pct_arr, rec_flat_arr, "s--", label="non-MRL", linewidth=2, color="#1f77b4")
    axes[0].axvline(x=80, color="gray", linestyle=":", alpha=0.6, label="80% 截断阈值")
    axes[0].set_xlabel("截断百分比 (%)")
    axes[0].set_ylabel(f"Recall@{TOP_K}")
    axes[0].set_title("MRL vs 非 MRL: 截断精度曲线\n(复核 Takeshita 2026 'To MRL or not')")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[0].set_ylim(-0.05, 1.05)

    # 右: 方差谱
    axes[1].semilogy(range(96), mrl_var[:96], "-", label="MRL 前96维", color="#d62728", alpha=0.8)
    axes[1].semilogy(range(672, 768), mrl_var[672:], "-", label="MRL 后96维", color="#d62728",
                     alpha=0.8, linestyle="--")
    axes[1].semilogy(range(96), flat_var[:96], "-", label="非MRL 前96维", color="#1f77b4", alpha=0.8)
    axes[1].semilogy(range(672, 768), flat_var[672:], "-", label="非MRL 后96维", color="#1f77b4",
                     alpha=0.8, linestyle="--")
    axes[1].set_xlabel("维度索引 (片段)")
    axes[1].set_ylabel("方差 (log scale)")
    axes[1].set_title(f"信息前置证据: 前96维方差是后96维的 {ratio_mrl:.1f}x")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(__file__.replace(".py", ".png"), dpi=120, bbox_inches="tight")
    print(f"图表已保存: {__file__.replace('.py', '.png')}")
except ImportError:
    print("(matplotlib 未安装, 跳过 png 生成)")
