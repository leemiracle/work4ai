"""
MIT EECS 补充课程微项目集 — 杂项（micro_projects.py）
覆盖课程：
- 6.857 Network Security
- 6.859 Algorithmic Game Theory
- 6.S192 CNN (deep learning intro)
- 6.S193 RL (Amini)
- 6.S898 Deep Learning Special Topics
- 6.S977 Hardware Accelerators
- 6.036 ML (old intro)
- 9.660 Computational Cognitive Science
"""
import math
import random


# ============ 6.857 Network Security ============

def mit6_857_tls_handshake():
    """TLS 1.3 握手模拟"""
    print("\n📋 6.857: TLS 1.3 握手")
    steps = [
        ("ClientHello", "C→S", "随机数 + 支持的密码套件"),
        ("ServerHello", "S→C", "随机数 + 选定套件"),
        ("KeyExchange", "S→C", "ECDHE 公钥 + 证书 + 签名"),
        ("Finished", "C→S", "用共享密钥加密的验证"),
        ("Application Data", "C↔S", "加密通信"),
    ]
    for step, direction, desc in steps:
        print(f"  [{direction}] {step}: {desc}")
    print(f"  → TLS 1.3 只需 1-RTT (TLS 1.2 需 2-RTT)")


# ============ 6.859 Algorithmic Game Theory ============

def mit6_859_vickrey_auction():
    """Vickrey 二价拍卖"""
    print("\n📋 6.859: Vickrey (二价) 拍卖")
    # 投标: bidder → bid
    bids = {"Alice": 80, "Bob": 95, "Carol": 60, "Dave": 70}
    winner = max(bids, key=lambda k: bids[k])
    winning_price = sorted(bids.values())[-2]  # 第二高价
    print(f"  投标: {bids}")
    print(f"  赢家: {winner} (出价 ${bids[winner]})")
    print(f"  成交价: ${winning_price} (第二高价)")
    print(f"  → Vickrey 拍卖: 说真话是占优策略 (truthful mechanism)")


# ============ 6.S192 CNN ============

def mit6_s192_convolution_demo():
    """CNN 卷积 + 池化演示"""
    print("\n📋 6.S192: CNN 卷积层")
    image = [
        [1,1,1,0,0],
        [1,1,1,0,0],
        [1,1,1,0,0],
        [0,0,0,1,1],
        [0,0,0,1,1],
    ]
    # 垂直边缘检测核
    kernel = [[-1,0,1],[-2,0,2],[-1,0,1]]
    out = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            val = 0
            for ki in range(3):
                for kj in range(3):
                    val += image[i+ki][j+kj] * kernel[ki][kj]
            out[i][j] = val
    print(f"  输入 5x5 (上半全1下半边缘):")
    for row in image: print(f"    {row}")
    print(f"  垂直边缘核 (Sobel-x):")
    for row in kernel: print(f"    {row}")
    print(f"  卷积输出 3x3:")
    for row in out: print(f"    {row}")


# ============ 6.S193 RL (Amini) ============

def mit6_s193_q_learning():
    """Q-Learning: 网格世界"""
    print("\n📋 6.S193: Q-Learning (GridWorld)")
    # 4x4 网格, 终点在 (3,3), 奖励 -1/步
    random.seed(42)
    Q = {}  # (row,col,action) → value
    actions = [(0,1,'R'),(0,-1,'L'),(1,0,'D'),(-1,0,'U')]
    gamma = 0.9; lr = 0.1; eps = 0.3
    def step(r, c, a):
        dr, dc, _ = actions[a]
        nr, nc = max(0,min(3,r+dr)), max(0,min(3,c+dc))
        reward = 10 if (nr,nc)==(3,3) else -1
        return nr, nc, reward, (nr,nc)==(3,3)
    for ep in range(500):
        r, c = random.randint(0,3), random.randint(0,3)
        for _ in range(50):
            if (r,c)==(3,3): break
            a = random.randint(0,3) if random.random() < eps else max(range(4), key=lambda x: Q.get((r,c,x),0))
            nr, nc, rew, done = step(r,c,a)
            best_next = max(Q.get((nr,nc,x),0) for x in range(4))
            Q[(r,c,a)] = Q.get((r,c,a),0) + lr*(rew + gamma*best_next - Q.get((r,c,a),0))
            r, c = nr, nc
    # 提取最优策略
    print(f"  4x4 网格, 终点=(3,3), 训练 500 episodes")
    print(f"  最优策略:")
    policy_names = ['R','L','D','U']
    for r in range(4):
        row_str = ""
        for c in range(4):
            if (r,c)==(3,3):
                row_str += " G "
            else:
                best_a = max(range(4), key=lambda x: Q.get((r,c,x),0))
                row_str += f" {policy_names[best_a]} "
        print(f"    {row_str}")


# ============ 6.S898 DL Special Topics ============

def mit6_s898_diffusion_concept():
    """扩散模型概念：前向加噪"""
    print("\n📋 6.S898: 扩散模型 (DDPM 前向)")
    # DDPM (Ho et al. 2020 arXiv:2006.11239)
    # x_t = sqrt(α_bar_t) * x_0 + sqrt(1-α_bar_t) * ε
    x0 = 1.0  # 原始数据点
    betas = [0.01 * t for t in range(1, 11)]  # 噪声调度
    alphas = [1 - b for b in betas]
    alpha_bars = []
    cum = 1.0
    for a in alphas:
        cum *= a; alpha_bars.append(cum)
    print(f"  原始数据 x_0 = {x0}")
    print(f"  {'t':>3}{'β_t':>8}{'ᾱ_t':>8}{'x_t (1 sample)':>14}")
    random.seed(42)
    for t in range(10):
        eps = random.gauss(0, 1)
        xt = math.sqrt(alpha_bars[t]) * x0 + math.sqrt(1 - alpha_bars[t]) * eps
        print(f"  {t+1:>3}{betas[t]:>8.3f}{alpha_bars[t]:>8.3f}{xt:>14.3f}")
    print(f"  → t 增大, x_t 趋近纯噪声 N(0,1)")


# ============ 6.S977 Hardware Accelerators ============

def mit6_s977_tpu_systolic():
    """TPU 脉动阵列概念"""
    print("\n📋 6.S977: TPU 脉动阵列 (Systolic Array)")
    # 2x2 脉动阵列做矩阵乘法
    A = [[1, 2], [3, 4]]  # 2x2
    B = [[5, 6], [7, 8]]  # 2x2
    # 结果 C = A @ B
    C = [[0]*2 for _ in range(2)]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                C[i][j] += A[i][k] * B[k][j]
    print(f"  A = {A}, B = {B}")
    print(f"  C = A@B = {C}")
    print(f"  → 脉动阵列: 每个 PE 做一次 MAC, 数据像心脏跳动一样流过")
    print(f"    TPU v1: 256x256 阵列 = 65536 MAC/cycle")


# ============ 6.036 ML (old intro) ============

def mit6_036_kmeans():
    """K-Means 聚类"""
    print("\n📋 6.036: K-Means 聚类")
    random.seed(42)
    points = []
    for _ in range(10): points.append((random.gauss(0,1), random.gauss(0,1)))
    for _ in range(10): points.append((random.gauss(5,1), random.gauss(5,1)))
    # K-Means with k=2
    k = 2
    centroids = [points[0], points[10]]
    for iteration in range(20):
        clusters = [[], []]
        for p in points:
            dists = [math.sqrt((p[0]-c[0])**2+(p[1]-c[1])**2) for c in centroids]
            clusters[dists.index(min(dists))].append(p)
        new_centroids = []
        for cl in clusters:
            cx = sum(p[0] for p in cl)/len(cl) if cl else 0
            cy = sum(p[1] for p in cl)/len(cl) if cl else 0
            new_centroids.append((cx, cy))
        if new_centroids == centroids:
            break
        centroids = new_centroids
    print(f"  20 点 (2 簇), k=2")
    print(f"  最终质心: {[(round(c[0],2), round(c[1],2)) for c in centroids]}")
    print(f"  簇大小: {[len(c) for c in clusters]}")


# ============ 9.660 Computational Cognitive Science ============

def mit9_660_act_r_architecture():
    """ACT-R 认知架构"""
    print("\n📋 9.660: ACT-R 认知架构")
    modules = [
        ("declarative", "陈述性记忆 (事实)"),
        ("procedural", "程序性记忆 (产生式规则)"),
        ("visual", "视觉模块"),
        ("manual", "运动模块"),
        ("imaginal", "问题表征"),
        ("goal", "目标栈"),
    ]
    print("  ACT-R 模块:")
    for name, desc in modules:
        print(f"    {name}: {desc}")
    # 记忆的激活量公式
    # B_i = ln(Σ t_j^(-d)) + Σ W_j * S_ji
    # 演示: 过去3次回忆时间 [1, 5, 20] 分钟前, decay d=0.5
    times = [1, 5, 20]  # minutes ago
    d = 0.5
    base_activation = math.log(sum(t ** (-d) for t in times))
    print(f"\n  记忆激活 (3次回忆在 1/5/20 分钟前, d={d}):")
    print(f"    B = ln({sum(t**(-d) for t in times):.3f}) = {base_activation:.3f}")
    print(f"  → 回忆越频繁、越近期, 激活量越高")


# ============ 主入口 ============

def run_micro():
    print("=" * 65)
    print("🎓 MIT EECS 杂项补充课程微项目")
    print("=" * 65)
    mit6_857_tls_handshake()
    mit6_859_vickrey_auction()
    mit6_s192_convolution_demo()
    mit6_s193_q_learning()
    mit6_s898_diffusion_concept()
    mit6_s977_tpu_systolic()
    mit6_036_kmeans()
    mit9_660_act_r_architecture()
    print("\n" + "=" * 65)
    print("✅ 杂项补充课程完成！")
    print("=" * 65)


if __name__ == "__main__":
    run_micro()
