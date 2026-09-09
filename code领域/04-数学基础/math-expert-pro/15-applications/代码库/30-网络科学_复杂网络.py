"""网络科学：复杂网络与社区发现
================================
数学概念：图论 / 随机图 / 小世界 / 无标度 / 模块度 / 社区发现 / 谱聚类
应用领域：社交网络 / 生物网络 / 推荐系统 / 流行病 / 交通 / 神经科学
核心思想：网络科学 = 图论 + 统计物理——研究真实世界网络的结构与动力学。
  ER 随机图：每条边以概率 p 独立存在
  小世界(Watts-Strogatz)：高聚类+短路径（六度分隔）
  无标度(Barabási-Albert)：度分布 P(k)~k^{-γ}（幂律，hub节点）
  模块度 Q：衡量社区划分质量（Q>0.3=有社区结构）
  谱聚类：用拉普拉斯矩阵的特征向量做聚类
运行方式：python "30-网络科学_复杂网络.py"
依赖：numpy, matplotlib"""
import numpy as np, matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

def er_random_graph(n, p, seed=42):
    rng = np.random.RandomState(seed)
    A = (rng.rand(n, n) < p).astype(float)
    A = np.triu(A, 1); A = A + A.T
    return A

def watts_strogatz(n, k, p, seed=42):
    rng = np.random.RandomState(seed)
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(1, k//2+1):
            A[i, (i+j)%n] = A[(i+j)%n, i] = 1
    # 重连
    for i in range(n):
        for j in range(1, k//2+1):
            if rng.rand() < p:
                old = (i+j)%n
                A[i, old] = A[old, i] = 0
                new = rng.choice([x for x in range(n) if x != i and A[i,x]==0])
                A[i, new] = A[new, i] = 1
    return A

def barabasi_albert(n, m, seed=42):
    rng = np.random.RandomState(seed)
    A = np.zeros((n, n))
    for i in range(m):  # 初始完全图
        for j in range(i): A[i,j] = A[j,i] = 1
    for i in range(m, n):
        degrees = A[:i].sum(axis=1)
        total = degrees.sum()
        targets = rng.choice(i, m, replace=False, p=degrees/total)
        for t in targets: A[i,t] = A[t,i] = 1
    return A

def modularity(A, communities):
    m = A.sum() / 2
    Q = 0
    for i in range(len(A)):
        for j in range(len(A)):
            if communities[i] == communities[j]:
                k_i = A[i].sum(); k_j = A[j].sum()
                Q += (A[i,j] - k_i*k_j/(2*m))
    return Q / (2*m)

def spectral_clustering(A, k):
    """谱聚类：用拉普拉斯矩阵的前 k 个特征向量。"""
    D = np.diag(A.sum(axis=1))
    L = D - A  # 图拉普拉斯矩阵
    eigvals, eigvecs = np.linalg.eigh(L)
    # 用前 k 个（跳过第一个）特征向量做 k-means
    features = eigvecs[:, 1:k+1]
    # 简单 k-means
    centroids = features[np.random.choice(len(features), k, replace=False)]
    for _ in range(50):
        dists = np.linalg.norm(features[:, None] - centroids[None, :], axis=2)
        labels = np.argmin(dists, axis=1)
        for j in range(k):
            if np.sum(labels == j) > 0:
                centroids[j] = features[labels == j].mean(axis=0)
    return labels

def main():
    np.random.seed(42)
    N = 100
    print("="*60); print("实验 1：三种经典网络模型"); print("="*60)
    ER = er_random_graph(N, 0.05)
    WS = watts_strogatz(N, 6, 0.1)
    BA = barabasi_albert(N, 3)
    for name, A in [("ER随机图", ER), ("WS小世界", WS), ("BA无标度", BA)]:
        degrees = A.sum(axis=1)
        n_edges = int(A.sum()/2)
        avg_deg = degrees.mean()
        max_deg = degrees.max()
        print(f"  {name}: {n_edges}边, 平均度={avg_deg:.1f}, 最大度={max_deg}")

    print("\n"+"="*60); print("实验 2：度分布——无标度网络的标志"); print("="*60)
    for name, A in [("ER(均匀)", ER), ("BA(幂律)", BA)]:
        degrees = A.sum(axis=1)
        max_d = int(degrees.max()) + 1
        hist = np.bincount(degrees.astype(int), minlength=max_d)
        nonzero = hist > 0
        print(f"\n  {name} 度分布:")
        for d in range(min(8, max_d)):
            if hist[d] > 0: print(f"    度={d}: {hist[d]}节点 ({hist[d]/N:.0%})")

    print("\n"+"="*60); print("实验 3：社区发现——谱聚类"); print("="*60)
    # 构造有社区结构的网络（两个稠密子图+稀疏连接）
    A_comm = np.zeros((N, N))
    # 社区1: 前50个节点
    for i in range(50):
        for j in range(i+1, 50):
            if np.random.rand() < 0.3: A_comm[i,j] = A_comm[j,i] = 1
    # 社区2: 后50个节点
    for i in range(50, N):
        for j in range(i+1, N):
            if np.random.rand() < 0.3: A_comm[i,j] = A_comm[j,i] = 1
    # 跨社区稀疏连接
    for _ in range(5):
        i, j = np.random.randint(0, 50), np.random.randint(50, N)
        A_comm[i,j] = A_comm[j,i] = 1

    labels = spectral_clustering(A_comm, 2)
    true_labels = np.array([0]*50 + [1]*50)
    accuracy = max(np.mean(labels == true_labels), np.mean(labels != true_labels))
    Q = modularity(A_comm, labels)
    print(f"谱聚类准确率: {accuracy:.1%}")
    print(f"模块度 Q = {Q:.4f} {'✓ 有社区结构' if Q > 0.3 else '弱社区结构'}")

    print("\n"+"="*60); print("实验 4：网络科学应用"); print("="*60)
    apps = [("社交网络", "Facebook/Twitter好友关系"),
            ("生物网络", "蛋白质相互作用/神经网络"),
            ("互联网", "网页链接/路由器拓扑"),
            ("流行病", "SIR模型在网络上传播"),
            ("推荐系统", "用户-物品二部图"),
            ("区块链", "交易网络/信任传播")]
    for app, desc in apps: print(f"  {app:<12} → {desc}")

    # 可视化
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    for idx, (name, A) in enumerate([("ER随机图", ER), ("WS小世界", WS), ("BA无标度", BA)]):
        ax = axes[0, idx]
        rng = np.random.RandomState(idx)
        pos = rng.randn(N, 2)
        for i in range(N):
            neighbors = np.where(A[i] > 0)[0]
            for j in neighbors:
                if j > i:
                    ax.plot([pos[i,0], pos[j,0]], [pos[i,1], pos[j,1]], 'b-', alpha=0.1, lw=0.5)
        degrees = A.sum(axis=1)
        ax.scatter(pos[:,0], pos[:,1], c=degrees, s=degrees*10+20, cmap='YlOrRd', zorder=5)
        ax.set_title(f'{name}\n(平均度={degrees.mean():.1f})')
        ax.set_aspect('equal'); ax.axis('off')

    ax = axes[1,0]
    deg_BA = np.sort(BA.sum(axis=1))[::-1]
    deg_ER = np.sort(ER.sum(axis=1))[::-1]
    ax.semilogy(range(N), deg_BA, 'b-', lw=2, label='BA无标度(幂律)')
    ax.semilogy(range(N), deg_ER, 'r-', lw=2, label='ER随机(均匀)')
    ax.set_xlabel('排名'); ax.set_ylabel('度（对数）')
    ax.set_title('度分布排序：BA有hub，ER均匀'); ax.legend(); ax.grid(alpha=0.3)
    ax = axes[1,1]
    clabels = ['社区1' if l==0 else '社区2' for l in labels]
    colors = ['steelblue' if l==0 else 'coral' for l in labels]
    rng2 = np.random.RandomState(5)
    pos_comm = rng2.randn(N, 2)
    pos_comm[:50, 0] -= 3; pos_comm[50:, 0] += 3  # 分离两个社区
    for i in range(N):
        neighbors = np.where(A_comm[i] > 0)[0]
        for j in neighbors:
            if j > i: ax.plot([pos_comm[i,0],pos_comm[j,0]], [pos_comm[i,1],pos_comm[j,1]], 'gray', alpha=0.1, lw=0.5)
    ax.scatter(pos_comm[:,0], pos_comm[:,1], c=colors, s=50, zorder=5)
    ax.set_title(f'社区发现(Q={Q:.3f}, 准确率={accuracy:.0%})'); ax.set_aspect('equal'); ax.axis('off')
    ax = axes[1,2]
    D_comm = np.diag(A_comm.sum(axis=1))
    L_comm = D_comm - A_comm
    eigvals_comm = np.linalg.eigvalsh(L_comm)
    ax.bar(range(10), eigvals_comm[:10], color='steelblue')
    ax.set_xlabel('特征值编号'); ax.set_ylabel('特征值')
    ax.set_title('拉普拉斯特征值（前两个接近0=两个社区）'); ax.grid(alpha=0.3)
    plt.tight_layout(); plt.savefig("30-网络科学_结果.png", dpi=120)
    print(f"\n[结果] 图像已保存: 30-网络科学_结果.png")
    print("\n[总结] 1. 网络科学=图论+统计物理")
    print("2. 三模型:ER(随机)/WS(小世界)/BA(无标度)")
    print("3. 社区发现:模块度Q+谱聚类(拉普拉斯特征值)")
    print("4. 无标度网络有hub节点→鲁棒但脆弱(目标攻击)")

if __name__ == "__main__": main()
