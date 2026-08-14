"""
CMU SCS — Graduate Course Micro-Projects
================================================
覆盖研究生专题课程 10 门：
- 10-708 PGM advanced (junction tree)
- 11-711 Advanced NLP (mini BERT attention)
- 11-737 Multilingual NLP (subword BPE)
- 15-721 Advanced DB (columnar storage + SIMD)
- 15-749 Distributed Systems (Raft log replication)
- 15-780 Advanced Optimization (interior point)
- 15-826 Multimedia Data Mining (LSH)
- 16-720 Computer Vision grad (bundle adjustment)
- 16-824 Visual Learning (metric learning/triplet loss)
- 17-804 ML Healthcare (federated learning FedAvg)

每个 micro_* 函数实现一个小算法/演示。
"""
from __future__ import annotations
import math
import random
from collections import defaultdict

# ============ 10-708 PGM Advanced: Junction Tree ============

def micro_10_708_junction_tree():
    """Junction tree 消息传递（简化 clique tree）。"""
    print("\n📋 10-708: Junction Tree Message Passing")
    # Chain A-B-C-D → cliques {AB}, {BC}, {CD}
    cliques = [
        {'A','B'},
        {'B','C'},
        {'C','D'},
    ]
    # Potential tables (simplified binary)
    pot_ab = {('a','b'): 0.7, ('a','B'): 0.3, ('A','b'): 0.2, ('A','B'): 0.8}
    # Message passing: marginalize separator
    sep_sets = [{'B'}, {'C'}]
    print(f"   Chain A-B-C-D → cliques: {cliques}")
    print(f"   Separator sets: {sep_sets}")
    # From leaf to root: marginalize → pass belief
    marg_B = {}
    for (a,b), p in pot_ab.items():
        marg_B[b] = marg_B.get(b, 0) + p
    print(f"   Marginal P(B) from clique AB: {marg_B}")
    print("   💡 Junction tree 保证一致的 marginal（Hugin/Shafer-Shenoy）")


# ============ 11-711 Advanced NLP: Mini BERT Attention ============

def micro_11_711_bert_attention():
    """简化 BERT self-attention (2 head)。"""
    print("\n📋 11-711: Mini BERT Self-Attention (2 heads)")
    seq_len, d_model = 4, 8
    d_k = d_model // 2  # 2 heads
    random.seed(42)
    # Random Q, K, V for each head
    def rand_mat(r, c):
        return [[random.gauss(0, 0.5) for _ in range(c)] for _ in range(r)]

    def softmax_row(xs):
        mx = max(xs)
        exps = [math.exp(x-mx) for x in xs]
        s = sum(exps)
        return [e/s for e in exps]

    Q = rand_mat(seq_len, d_k)
    K = rand_mat(seq_len, d_k)
    V = rand_mat(seq_len, d_k)
    # Attention scores
    scores = [[sum(Q[i][d]*K[j][d] for d in range(d_k))/math.sqrt(d_k)
               for j in range(seq_len)] for i in range(seq_len)]
    attn = [softmax_row(row) for row in scores]
    # Output
    output = [[sum(attn[i][j]*V[j][d] for j in range(seq_len)) for d in range(d_k)]
              for i in range(seq_len)]
    print(f"   Seq len={seq_len}, d_model={d_model}, heads=2, d_k={d_k}")
    print(f"   Attention matrix row 0: [{', '.join(f'{v:.3f}' for v in attn[0])}]")
    print(f"   Output[0]: [{', '.join(f'{v:.3f}' for v in output[0])}]")
    print("   💡 Multi-head = 多个 attention 并行 → 捕获不同子空间关系")


# ============ 11-737 Multilingual NLP: BPE ============

def micro_11_737_bpe():
    """Byte-Pair Encoding subword tokenization."""
    print("\n📋 11-737: Byte-Pair Encoding (BPE)")
    word_freqs = {'low': 5, 'lower': 2, 'newest': 6, 'widest': 3}
    # Represent words as char sequences
    splits = {word: list(word) + ['</w>'] for word in word_freqs}

    def get_pairs(splits):
        pairs = defaultdict(int)
        for word, chars in splits.items():
            for i in range(len(chars)-1):
                pairs[(chars[i], chars[i+1])] += word_freqs[word]
        return pairs

    num_merges = 10
    merges = []
    for _ in range(num_merges):
        pairs = get_pairs(splits)
        if not pairs:
            break
        best = max(pairs, key=pairs.get)
        merges.append(best)
        for word in splits:
            chars = splits[word]
            new_chars = []
            i = 0
            while i < len(chars):
                if i < len(chars)-1 and (chars[i], chars[i+1]) == best:
                    new_chars.append(chars[i]+chars[i+1])
                    i += 2
                else:
                    new_chars.append(chars[i])
                    i += 1
            splits[word] = new_chars

    print(f"   Corpus: {word_freqs}")
    print(f"   Learned merges (top 5): {merges[:5]}")
    print(f"   Tokenized 'lowest': {splits.get('lowest', list('lowest'))}")
    print("   💡 BPE 自动学习子词 → 处理 OOV + 多语言共享词表")


# ============ 15-721 Advanced DB: Columnar + SIMD ============

def micro_15_721_columnar():
    """列存 vs 行存扫描对比。"""
    print("\n📋 15-721: Columnar vs Row Store")
    # Simulate: SELECT SUM(col3) FROM table
    n_rows = 1000
    n_cols = 10
    # Row store: must read all columns
    row_bytes = n_rows * n_cols * 4
    # Column store: only read col3
    col_bytes = n_rows * 1 * 4
    print(f"   Table: {n_rows} rows × {n_cols} columns (4 bytes each)")
    print(f"   Query: SELECT SUM(col3)")
    print(f"   Row store I/O:   {row_bytes:,} bytes (read all columns)")
    print(f"   Column store I/O: {col_bytes:,} bytes (read only col3)")
    print(f"   Speedup: {row_bytes/col_bytes:.0f}x")
    print("   💡 列存 + SIMD 向量化 = 分析查询的核心优化 (OLAP)")


# ============ 15-749 Distributed Systems: Raft Log ============

def micro_15_749_raft_log():
    """Raft 日志复制模拟。"""
    print("\n📋 15-749: Raft Log Replication")
    leader_log = [1, 1, 1, 0, 1]  # committed entries
    followers = [
        [1, 1, 1, 0, 1],     # up-to-date
        [1, 1, 1, 0],         # missing last
        [1, 1, 1, 0, 1, 1],  # extra uncommitted
    ]
    commit_idx = len(leader_log) - 1
    print(f"   Leader log:  {leader_log} (commitIdx={commit_idx})")
    for i, f in enumerate(followers):
        match = sum(1 for j in range(min(len(f), len(leader_log))) if f[j] == leader_log[j])
        print(f"   Follower {i}: {f} (matchIndex={match-1})")
    # Majority commit
    majority = len(followers) // 2 + 1
    replicated = sum(1 for f in followers if len(f) > commit_idx - 1)
    print(f"   Replicated on {replicated}/{len(followers)} followers (majority={majority})")
    print("   💡 Raft: entry committed when majority replicates (Ongaro 2014)")


# ============ 15-780 Advanced Optimization: Interior Point ============

def micro_15_780_interior_point():
    """简化内点法：带约束的二次优化。"""
    print("\n📋 15-780: Interior Point Method (barrier)")
    # Minimize x² + y² subject to x + y ≥ 1
    # Barrier: minimize x² + y² - t*ln(x+y-1)
    x, y = 0.5, 0.5  # feasible interior start
    t = 1.0
    for outer in range(5):
        t *= 10  # increase barrier weight
        for _ in range(50):
            constraint = x + y - 1
            if constraint <= 0.001:
                constraint = 0.001
            # gradient of barrier objective
            gx = 2*x - t/constraint
            gy = 2*y - t/constraint
            x -= 0.001 * gx
            y -= 0.001 * gy
    print(f"   Minimize x²+y² s.t. x+y≥1")
    print(f"   Interior point solution: x={x:.4f}, y={y:.4f}")
    print(f"   Expected: x=0.5, y=0.5 (symmetric optimum on constraint)")
    print("   💡 内点法用 log-barrier 跟踪中心路径 → 多项式时间收敛")


# ============ 15-826 Multimedia: LSH ============

def micro_15_826_lsh():
    """Locality-Sensitive Hashing (SimHash)。"""
    print("\n📋 15-826: Locality-Sensitive Hashing (SimHash)")
    def simhash(features, n_bits=16):
        v = [0] * n_bits
        for feat, weight in features.items():
            h = hash(feat) & ((1 << n_bits) - 1)
            for i in range(n_bits):
                if h & (1 << i):
                    v[i] += weight
                else:
                    v[i] -= weight
        return tuple(1 if x > 0 else 0 for x in v)

    def hamming(a, b):
        return sum(1 for x, y in zip(a, b) if x != y)

    doc1 = simhash({'cat':1, 'dog':1, 'pet':1, 'animal':1})
    doc2 = simhash({'cat':1, 'dog':1, 'pet':1, 'fur':1})
    doc3 = simhash({'python':1, 'java':1, 'code':1, 'program':1})
    print(f"   Doc1 (pets): {doc1}")
    print(f"   Doc2 (pets): {doc2}")
    print(f"   Doc3 (code): {doc3}")
    print(f"   Hamming(Doc1,Doc2) = {hamming(doc1, doc2)} (similar)")
    print(f"   Hamming(Doc1,Doc3) = {hamming(doc1, doc3)} (different)")
    print("   💡 LSH: 相似文档 hash 到相近桶 → 近邻搜索 O(1) per band")


# ============ 16-720 CV grad: Bundle Adjustment ============

def micro_16_720_bundle_adjustment():
    """简化 bundle adjustment：优化 1D 位姿 + 路标。"""
    print("\n📋 16-720: Bundle Adjustment (simplified)")
    # 3 camera poses, 2 landmarks, observations
    poses = [0.0, 2.0, 4.0]
    landmarks = [5.0, -1.0]
    # Observations (pose_idx, lm_idx, measured_distance)
    obs = [(0,0,5.0), (1,0,3.0), (2,0,1.0), (0,1,1.0), (1,1,3.0)]
    # Reprojection error
    total_err = 0
    for pi, li, meas in obs:
        pred = abs(landmarks[li] - poses[pi])
        total_err += (pred - meas)**2
    print(f"   3 poses, 2 landmarks, 5 observations")
    print(f"   Total reprojection error (before): {total_err:.4f}")
    # One Gauss-Newton step on landmark 0
    # d(err)/d(lm0) = 2*(lm0-pose - meas) for each obs
    grad = sum(2*(landmarks[li] - poses[pi] - meas) for pi,li,meas in obs if li==0)
    landmarks[0] -= 0.1 * grad
    total_err2 = sum((abs(landmarks[li]-poses[pi])-meas)**2 for pi,li,meas in obs)
    print(f"   After 1 GN step: error = {total_err2:.4f}")
    print("   💡 BA 联合优化 poses + landmarks → SLAM/SfM 核心")


# ============ 16-824 Visual Learning: Metric Learning ============

def micro_16_824_triplet_loss():
    """Triplet loss 演示。"""
    print("\n📋 16-824: Triplet Loss (Metric Learning)")
    anchor =    [1.0, 0.0, 0.0]
    positive =  [0.9, 0.1, 0.0]  # same class
    negative =  [0.0, 1.0, 0.0]  # different class

    def dist(a, b):
        return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

    d_pos = dist(anchor, positive)
    d_neg = dist(anchor, negative)
    margin = 0.5
    triplet_loss = max(0, d_pos - d_neg + margin)
    print(f"   Anchor:   {anchor}")
    print(f"   Positive: {positive} (same class)")
    print(f"   Negative: {negative} (diff class)")
    print(f"   d(anchor, pos) = {d_pos:.3f}")
    print(f"   d(anchor, neg) = {d_neg:.3f}")
    print(f"   Triplet loss (margin={margin}): {triplet_loss:.3f}")
    print("   💡 目标: max(0, d_pos - d_neg + margin) → 拉 close 正例, 推远负例")


# ============ 17-804 ML Healthcare: Federated Learning ============

def micro_17_804_fedavg():
    """FedAvg 联邦学习模拟。"""
    print("\n📋 17-804: Federated Learning (FedAvg)")
    # 3 hospitals, each has local model weights
    hospitals = {
        'H1': [0.4, 0.5, 0.1],
        'H2': [0.3, 0.6, 0.2],
        'H3': [0.5, 0.4, 0.3],
    }
    n_samples = {'H1': 100, 'H2': 200, 'H3': 150}
    total_n = sum(n_samples.values())
    # FedAvg: weighted average by sample count
    global_model = [0.0]*3
    for h in hospitals:
        weight = n_samples[h] / total_n
        for i in range(3):
            global_model[i] += weight * hospitals[h][i]
    print(f"   3 hospitals, local models:")
    for h in hospitals:
        print(f"     {h} (n={n_samples[h]}): {hospitals[h]}")
    print(f"   FedAvg global model: {[round(x,3) for x in global_model]}")
    print("   💡 FedAvg: 原始数据不出本地 → 隐私保护 (McMahan 2017)")


# ============ 主入口 ============

def run_all():
    print("=" * 60)
    print("🎓 CMU SCS — Graduate Micro-Projects")
    print("=" * 60)
    random.seed(42)
    micro_10_708_junction_tree()
    micro_11_711_bert_attention()
    micro_11_737_bpe()
    micro_15_721_columnar()
    micro_15_749_raft_log()
    micro_15_780_interior_point()
    micro_15_826_lsh()
    micro_16_720_bundle_adjustment()
    micro_16_824_triplet_loss()
    micro_17_804_fedavg()
    print("\n" + "=" * 60)
    print("✅ 全部研究生微项目完成！(10 门课程)")
    print("=" * 60)

if __name__ == "__main__":
    run_all()
