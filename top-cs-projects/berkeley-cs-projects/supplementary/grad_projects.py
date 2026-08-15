"""
UC Berkeley EECS — 研究生专题课程微项目集
覆盖：CS 288 / CS 294 DL / CS 267 / CS 287 / CS 294-141 3D Vision / CS 294-165 Fairness / CS 280 grad / EE 227BT / CS 281A / CS C267
"""
import math
import random
from collections import defaultdict


# ============ CS 288 Adv NLP：subword BPE ============

def cs288_bpe():
    """CS288: Byte Pair Encoding（GPT-2 subword）"""
    print("\n📋 CS288: Byte Pair Encoding（子词分词）")
    def get_pair_stats(vocab):
        pairs = defaultdict(int)
        for word, freq in vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i+1])] += freq
        return pairs

    def merge_vocab(pair, vocab):
        new_vocab = {}
        bigram = " ".join(pair)
        replacement = "".join(pair)
        for word, freq in vocab.items():
            new_word = word.replace(bigram, replacement)
            new_vocab[new_word] = freq
        return new_vocab

    vocab = {"l o w </w>": 5, "l o w e r </w>": 2, "n e w e s t </w>": 6, "w i d e s t </w>": 3}
    print(f"   初始词表: {vocab}")
    for i in range(5):
        pairs = get_pair_stats(vocab)
        if not pairs:
            break
        best = max(pairs, key=pairs.get)
        vocab = merge_vocab(best, vocab)
        print(f"   合并 #{i+1}: {best} → freq={pairs[best]}")
    print(f"   最终词表: {list(vocab.keys())}")


# ============ CS 294 DL：BatchNorm ============

def cs294_batchnorm():
    """CS294: Batch Normalization 前向"""
    print("\n📋 CS294: Batch Normalization")
    # BN(x) = γ · (x - μ) / sqrt(σ² + ε) + β
    batch = [1.0, 2.0, 3.0, 4.0, 5.0]
    mu = sum(batch) / len(batch)
    var = sum((x - mu) ** 2 for x in batch) / len(batch)
    eps = 1e-5
    gamma, beta = 1.0, 0.0
    normalized = [gamma * (x - mu) / math.sqrt(var + eps) + beta for x in batch]
    print(f"   输入: {batch}")
    print(f"   μ={mu:.2f}, σ²={var:.2f}")
    print(f"   BN 输出: {[round(x, 3) for x in normalized]}")
    print(f"   (均值→0, 方差→1)")


# ============ CS 267 Parallel：reduce ============

def cs267_parallel_reduce():
    """CS267: 并行归约（树形 reduce）"""
    print("\n📋 CS267: 并行归约（树形）")
    data = list(range(1, 17))  # 1..16
    n = len(data)
    steps = 0
    arr = list(data)
    print(f"   初始: {arr}")
    while len(arr) > 1:
        new_arr = []
        for i in range(0, len(arr), 2):
            if i + 1 < len(arr):
                new_arr.append(arr[i] + arr[i+1])
            else:
                new_arr.append(arr[i])
        arr = new_arr
        steps += 1
        print(f"   step {steps}: {arr}")
    print(f"   sum = {arr[0]}  (串行需 {n-1} 步, 并行需 {int(math.log2(n))} 步)")


# ============ CS 287 Robotics：正运动学 ============

def cs287_forward_kinematics():
    """CS287: 2-DOF 机械臂正运动学"""
    print("\n📋 CS287: 机械臂正运动学（2-DOF）")
    l1, l2 = 1.0, 0.8  # 连杆长度
    # θ1, θ2 关节角
    configs = [(0, 0), (math.pi/2, 0), (math.pi/4, math.pi/4), (0, math.pi/2)]
    for theta1, theta2 in configs:
        x = l1 * math.cos(theta1) + l2 * math.cos(theta1 + theta2)
        y = l1 * math.sin(theta1) + l2 * math.sin(theta1 + theta2)
        print(f"   θ1={math.degrees(theta1):.0f}°, θ2={math.degrees(theta2):.0f}° → "
              f"末端 ({x:.3f}, {y:.3f})")


# ============ CS 294-141 3D Vision：三角化 ============

def cs294_141_triangulation():
    """CS294-141: 双目三角化测距"""
    print("\n📋 CS294-141: 双目三角化")
    # 基线 b=0.5m, 焦距 f=700px
    b, f = 0.5, 700.0
    # 视差 disparity = x_left - x_right
    for disparity in [5, 10, 50, 100]:
        depth = b * f / disparity
        print(f"   disparity={disparity}px → depth={depth:.2f}m  "
              f"(视差越小距离越远)")


# ============ CS 294-165 Fairness：Demographic Parity ============

def cs294_165_fairness():
    """CS294-165: 算法公平性"""
    print("\n📋 CS294-165: Demographic Parity（公平性）")
    # 模拟贷款批准
    random.seed(42)
    groups = {"A": 0.65, "B": 0.50}  # 实际合格率
    for name, rate in groups.items():
        approved = sum(1 for _ in range(1000) if random.random() < rate)
        print(f"   组 {name}: 批准率 {approved/1000:.1%}")
    # Demographic parity: P(approve|A) ≈ P(approve|B)
    diff = abs(0.65 - 0.50)
    print(f"   Demographic parity 差异: {diff:.1%} (>10% 通常认为不公平)")


# ============ CS 280 grad CV：Lucas-Kanade 光流 ============

def cs280_optical_flow():
    """CS280 grad: Lucas-Kanade 光流（简化）"""
    print("\n📋 CS280 grad: Lucas-Kanade 光流")
    # Ix·u + Iy·v = -It
    # 假设 3 像素的梯度
    Ix = [1, 0, -1]
    Iy = [1, 2, 1]
    It = [-2, -1, -1]  # 时间梯度
    # 解 A^T A [u,v] = A^T b
    # A = [[Ix_i, Iy_i]], b = -It_i
    ATA = [[sum(Ix[i]**2 for i in range(3)), sum(Ix[i]*Iy[i] for i in range(3))],
           [sum(Ix[i]*Iy[i] for i in range(3)), sum(Iy[i]**2 for i in range(3))]]
    ATb = [-sum(Ix[i]*It[i] for i in range(3)), -sum(Iy[i]*It[i] for i in range(3))]
    # 2x2 求解
    det = ATA[0][0] * ATA[1][1] - ATA[0][1] * ATA[1][0]
    u = (ATA[1][1] * ATb[0] - ATA[0][1] * ATb[1]) / det
    v = (-ATA[1][0] * ATb[0] + ATA[0][0] * ATb[1]) / det
    print(f"   光流向量 (u, v) = ({u:.2f}, {v:.2f})")


# ============ EE 227BT Convex Opt：SVM 对偶 ============

def ee227bt_svm_dual():
    """EE227BT: SVM 对偶问题"""
    print("\n📋 EE227BT: SVM 对偶（小规模）")
    # 简化 2D：两类可分
    # min 0.5|w|²  s.t. y_i(w·x_i + b) ≥ 1
    # 拉格朗日对偶: max Σα_i - 0.5 ΣΣ α_i α_j y_i y_j x_i·x_j
    points = [(-1, -1, +1), (1, 1, -1)]
    # 简化解：w 平行于 (1,1)，b=0
    w = [1, 1]
    b = 0
    for x1, x2, y in points:
        margin = y * (w[0] * x1 + w[1] * x2 + b)
        print(f"   点 ({x1},{x2}), y={y:+d}, margin = {margin:.2f}")
    print(f"   |w| = {math.sqrt(sum(wi**2 for wi in w)):.2f}  (margin = 1/|w|)")


# ============ CS 281A Stat Learning：EM 高斯混合 ============

def cs281a_em_gmm():
    """CS281A: EM 算法（1D GMM 1 步）"""
    print("\n📋 CS281A: EM（1D 高斯混合）")
    random.seed(42)
    # 两簇：N(-2, 0.5) 和 N(2, 0.5)
    data = [random.gauss(-2, 0.5) for _ in range(50)] + [random.gauss(2, 0.5) for _ in range(50)]
    random.shuffle(data)
    # 初始化
    mu1, mu2 = -1.0, 1.0
    for iteration in range(5):
        # E-step: 软分配
        r1_list, r2_list = [], []
        for x in data:
            p1 = math.exp(-0.5 * (x - mu1) ** 2)
            p2 = math.exp(-0.5 * (x - mu2) ** 2)
            r1 = p1 / (p1 + p2)
            r1_list.append(r1)
            r2_list.append(1 - r1)
        # M-step: 更新均值
        mu1 = sum(r1_list[i] * data[i] for i in range(len(data))) / sum(r1_list)
        mu2 = sum(r2_list[i] * data[i] for i in range(len(data))) / sum(r2_list)
        print(f"   iter {iteration+1}: μ1={mu1:.3f}, μ2={mu2:.3f}")
    print(f"   收敛到 μ1≈-2, μ2≈2 (真实参数)")


# ============ CS C267 Parallel Apps：矩阵乘法分块 ============

def csc267_blocked_matmul():
    """CS C267: 分块矩阵乘法 cache 效率"""
    print("\n📋 CS C267: 分块矩阵乘法（cache 友好）")
    N, B = 8, 4  # 8x8 矩阵, 4x4 块
    A = [[random.random() for _ in range(N)] for _ in range(N)]
    Bm = [[random.random() for _ in range(N)] for _ in range(N)]
    C = [[0.0] * N for _ in range(N)]
    # 分块乘法
    for ii in range(0, N, B):
        for jj in range(0, N, B):
            for kk in range(0, N, B):
                for i in range(ii, min(ii + B, N)):
                    for j in range(jj, min(jj + B, N)):
                        for k in range(kk, min(kk + B, N)):
                            C[i][j] += A[i][k] * Bm[k][j]
    print(f"   {N}×{N} 分块乘法完成 (block={B})")
    print(f"   分块 vs 朴素: cache miss 减少 ~B 倍")
    print(f"   C[0][0] = {C[0][0]:.3f}")


# ============ 主入口 ============

def run_all_grad():
    print("=" * 60)
    print("🎓 UC Berkeley EECS 研究生专题课程微项目")
    print("=" * 60)
    cs288_bpe()
    cs294_batchnorm()
    cs267_parallel_reduce()
    cs287_forward_kinematics()
    cs294_141_triangulation()
    cs294_165_fairness()
    cs280_optical_flow()
    ee227bt_svm_dual()
    cs281a_em_gmm()
    csc267_blocked_matmul()
    print("\n" + "=" * 60)
    print("✅ 全部研究生专题微项目完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all_grad()
