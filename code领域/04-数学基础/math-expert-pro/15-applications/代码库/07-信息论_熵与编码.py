"""
信息论：熵、编码与 KL 散度
==========================
数学概念：香农熵 / 交叉熵 / KL 散度 / 霍夫曼编码 / 香农信源编码定理
应用领域：数据压缩 / 机器学习损失函数 / 编码理论
核心思想：熵 H(X) = -Σ p(x) log₂ p(x) 度量分布的不确定性。
         香农信源编码定理：平均编码长度 ≥ H(X)，霍夫曼编码达到最优。
         KL 散度 D_KL(P||Q) = Σ p(x) log(p(x)/q(x)) 度量两个分布的"距离"，
         交叉熵 H(P,Q) = H(P) + D_KL(P||Q)——这就是 ML 分类损失函数的数学根基。
运行方式：python "07-信息论_熵与编码.py"
依赖：numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import heapq

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============ 1. 数学建模：信息论核心量 ============

def shannon_entropy(p, base=2):
    """香农熵 H(X) = -Σ p(x) log p(x)
    p: 概率分布（归一化的非负向量）
    base: 对数底（2=比特，e=奈特）
    返回：熵（比特）
    """
    p = np.asarray(p, dtype=float)
    p = p[p > 0]  # 0 log 0 = 0
    return -np.sum(p * np.log(p) / np.log(base))


def cross_entropy(p, q, base=2):
    """交叉熵 H(P, Q) = -Σ p(x) log q(x)
    含义：用 Q 的编码方案来编码 P 分布的数据，平均需要多少比特
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    mask = (p > 0) & (q > 0)
    return -np.sum(p[mask] * np.log(q[mask]) / np.log(base))


def kl_divergence(p, q, base=2):
    """KL 散度 D_KL(P||Q) = Σ p(x) log(p(x)/q(x))
    性质：≥0（Gibbs 不等式），=0 当且仅当 P=Q；不对称（非距离度量）
    关系：H(P,Q) = H(P) + D_KL(P||Q)
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    mask = (p > 0) & (q > 0)
    return np.sum(p[mask] * np.log(p[mask] / q[mask]) / np.log(base))


def huffman_code(probs):
    """霍夫曼编码：给定概率分布，返回最优前缀码。
    最优性：平均编码长度 ≤ H(X) + 1（香农信源编码定理的达界）
    """
    n = len(probs)
    if n == 1:
        return {0: '0'}
    # 用堆维护当前森林，每个节点 = (概率, 序号, 编码字典)
    heap = [(probs[i], i, {i: ''}) for i in range(n)]
    heapq.heapify(heap)
    while len(heap) > 1:
        p1, _, codes1 = heapq.heappop(heap)
        p2, _, codes2 = heapq.heappop(heap)
        merged = {}
        for k, v in codes1.items():
            merged[k] = '0' + v
        for k, v in codes2.items():
            merged[k] = '1' + v
        heapq.heappush(heap, (p1 + p2, min(heap[0][1] if heap else 0, -1), merged))
    _, _, final_codes = heap[0]
    return final_codes


def avg_code_length(probs, codes):
    """平均编码长度 = Σ p(x) × len(code(x))"""
    return sum(probs[i] * len(codes[i]) for i in range(len(probs)))


# ============ 2. 实验与可视化 ============

def main():
    np.random.seed(42)

    # ---- 实验 1：不同分布的熵 ----
    print("=" * 60)
    print("实验 1：不同分布的香农熵")
    print("=" * 60)

    distributions = {
        "均匀分布 (8 符号)": np.ones(8) / 8,
        "偏斜分布": np.array([0.4, 0.2, 0.15, 0.1, 0.08, 0.04, 0.02, 0.01]),
        "高度集中": np.array([0.9, 0.05, 0.02, 0.01, 0.01, 0.005, 0.003, 0.002]),
        "二值均匀": np.array([0.5, 0.5]),
    }

    print(f"{'分布':<20} {'熵 H(X) (bits)':<18} {'最大熵':<10} {'效率':<10}")
    print("-" * 60)
    entropies = {}
    for name, p in distributions.items():
        H = shannon_entropy(p)
        H_max = np.log2(len(p))
        eff = H / H_max if H_max > 0 else 1.0
        entropies[name] = (H, H_max, eff)
        print(f"{name:<20} {H:<18.4f} {H_max:<10.4f} {eff:<10.2%}")

    print("\n[解读] 均匀分布熵最大（最不确定）；越集中熵越小。")
    print("       均匀分布的熵 = log₂(n) = 最大熵。")

    # ---- 实验 2：霍夫曼编码 vs 熵 ----
    print("\n" + "=" * 60)
    print("实验 2：霍夫曼编码 vs 香农下界")
    print("=" * 60)

    p = distributions["偏斜分布"]
    H = shannon_entropy(p)
    codes = huffman_code(p)
    L_avg = avg_code_length(p, codes)
    L_uniform = np.ceil(np.log2(len(p)))  # 等长编码

    print(f"\n分布: {p}")
    print(f"香农熵 H(X) = {H:.4f} bits（理论下界）")
    print(f"霍夫曼平均编码长度 = {L_avg:.4f} bits（最优前缀码）")
    print(f"等长编码长度 = {L_uniform:.0f} bits（不利用概率）")
    print(f"霍夫曼 vs 熵差距 = {L_avg - H:.4f} bits（≤1，信源编码定理保证）")
    print(f"霍夫曼 vs 等长节省 = {(1 - L_avg/L_uniform)*100:.1f}%")

    print("\n编码表:")
    for i in range(len(p)):
        print(f"  符号 {i}: P={p[i]:.3f}  编码={codes[i]:<8} 长度={len(codes[i])}")

    print("\n[解读] 霍夫曼编码让高频符号用短码、低频用长码，")
    print("       平均长度逼近香农熵下界。这是所有压缩算法的理论根基。")

    # ---- 实验 3：KL 散度与交叉熵 ----
    print("\n" + "=" * 60)
    print("实验 3：KL 散度与交叉熵（ML 损失函数的数学根基）")
    print("=" * 60)

    P = np.array([0.7, 0.2, 0.1])  # 真实分布
    Q_candidates = [
        ("Q=P (完美匹配)", np.array([0.7, 0.2, 0.1])),
        ("Q 接近 P", np.array([0.6, 0.3, 0.1])),
        ("Q 偏离 P", np.array([0.5, 0.4, 0.1])),
        ("Q 均匀", np.array([1/3, 1/3, 1/3])),
        ("Q 严重偏离", np.array([0.1, 0.2, 0.7])),
    ]

    H_P = shannon_entropy(P)
    print(f"\n真实分布 P = {P}, H(P) = {H_P:.4f} bits")
    print(f"\n{'Q 分布':<20} {'H(P,Q) 交叉熵':<16} {'D_KL(P||Q)':<14} {'= H(P)+KL?':<12}")
    print("-" * 65)
    kl_values = []
    ce_values = []
    for name, Q in Q_candidates:
        CE = cross_entropy(P, Q)
        KL = kl_divergence(P, Q)
        check = np.isclose(CE, H_P + KL)
        kl_values.append(KL)
        ce_values.append(CE)
        print(f"{name:<20} {CE:<16.4f} {KL:<14.4f} {'✓' if check else '✗':<12}")

    print("\n[解读] 交叉熵 H(P,Q) = H(P) + D_KL(P||Q)")
    print("       当 Q=P 时，KL=0，交叉熵 = 熵（最小值）")
    print("       Q 越偏离 P，KL 越大，交叉熵越大")
    print("       ★ ML 分类用交叉熵损失 = 最小化 KL散度 = 让模型分布 Q 逼近真实 P")

    # ---- 实验 4：二元分布的熵函数 ----
    print("\n" + "=" * 60)
    print("实验 4：二元熵函数 H(p) = -p log₂ p - (1-p) log₂(1-p)")
    print("=" * 60)
    ps = np.linspace(0.001, 0.999, 100)
    H_binary = [-p * np.log2(p) - (1-p) * np.log2(1-p) for p in ps]
    p_max = 0.5
    H_max_binary = 1.0
    print(f"最大熵在 p=0.5: H(0.5) = {H_max_binary:.4f} bits")
    print(f"p=0.1: H(0.1) = {-0.1*np.log2(0.1) - 0.9*np.log2(0.9):.4f} bits")
    print(f"p=0.01: H(0.01) = {-0.01*np.log2(0.01) - 0.99*np.log2(0.99):.4f} bits")
    print("[解读] p=0.5 时最不确定（熵=1）；p→0 或 1 时几乎确定（熵→0）。")

    # ============ 3. 可视化 ============
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # 图 1：不同分布的熵
    ax = axes[0, 0]
    names = list(entropies.keys())
    H_vals = [entropies[n][0] for n in names]
    Hmax_vals = [entropies[n][1] for n in names]
    x = np.arange(len(names))
    ax.bar(x - 0.2, H_vals, 0.4, label='熵 H(X)', color='steelblue')
    ax.bar(x + 0.2, Hmax_vals, 0.4, label='最大熵 log₂n', color='orange', alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([n[:8] for n in names], rotation=15, fontsize=9)
    ax.set_ylabel('熵 (bits)')
    ax.set_title('不同分布的香农熵 vs 最大熵')
    ax.legend()
    ax.grid(alpha=0.3)

    # 图 2：霍夫曼编码长度对比
    ax = axes[0, 1]
    methods = ['香农熵\n(下界)', '霍夫曼\n(最优)', '等长编码\n(不压缩)']
    lengths = [H, L_avg, L_uniform]
    colors = ['green', 'steelblue', 'red']
    ax.bar(methods, lengths, color=colors, alpha=0.8)
    ax.set_ylabel('平均编码长度 (bits/符号)')
    ax.set_title('霍夫曼编码 vs 理论下界')
    for i, v in enumerate(lengths):
        ax.text(i, v + 0.05, f'{v:.3f}', ha='center', fontweight='bold')
    ax.grid(alpha=0.3, axis='y')

    # 图 3：KL 散度随 Q 偏离 P 的变化
    ax = axes[1, 0]
    labels = [name for name, _ in Q_candidates]
    ax.bar(range(len(labels)), kl_values, color='coral', alpha=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([l[:10] for l in labels], rotation=15, fontsize=9)
    ax.set_ylabel('D_KL(P||Q) (bits)')
    ax.set_title('KL 散度：Q 越偏离 P，KL 越大')
    ax.axhline(0, color='black', lw=0.5)
    ax.grid(alpha=0.3, axis='y')

    # 图 4：二元熵函数
    ax = axes[1, 1]
    ax.plot(ps, H_binary, 'b-', lw=2)
    ax.axhline(1.0, color='r', ls='--', alpha=0.5, label='最大熵 = 1 bit')
    ax.axvline(0.5, color='gray', ls=':', alpha=0.5)
    ax.plot(0.5, 1.0, 'ro', markersize=10)
    ax.annotate('p=0.5, H=1 (最大不确定)', xy=(0.5, 1.0), xytext=(0.15, 0.85),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, color='red')
    ax.set_xlabel('p (伯努利参数)')
    ax.set_ylabel('H(p) (bits)')
    ax.set_title('二元熵函数：不确定性 vs 概率')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("07-信息论_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 07-信息论_结果.png")

    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    print("1. 熵 H(X) 度量不确定性：均匀分布最大，越集中越小")
    print("2. 霍夫曼编码逼近香农下界：平均长度 ≤ H(X)+1")
    print("3. KL 散度 D_KL(P||Q)≥0：度量分布距离，=0 当且仅当 P=Q")
    print("4. 交叉熵 = 熵 + KL：ML 分类的损失函数就是交叉熵")
    print("   → 最小化交叉熵损失 = 让模型 Q 逼近真值 P")
    print("5. 二元熵在 p=0.5 最大（1 bit），p→0/1 时趋于 0")
    print("\n[解读] 信息论是连接'压缩'与'机器学习'的数学桥梁——")
    print("       同一个 KL 散度，在压缩里是'编码冗余'，在 ML 里是'损失函数'。")


if __name__ == "__main__":
    main()
