"""
ETH Zürich Informatik — 研究生补充课程微项目
============================================
覆盖 10 门研究生课程：
1. Advanced Systems Lab — 系统测量
2. Big Data (Systems) — MapReduce/Spark
3. Reliable Distributed Systems (加深) — Raft
4. Security Engineering — 访问控制
5. 3D Vision (Pollefeys) — 相机投影
6. Probabilistic Programming — 推断编译
7. Advanced ML — 核方法
8. Statistical Learning Theory — VC 维
9. Information Theory — 熵 + 编码
10. Causality (加深) — 结构学习
"""
import math
import random


# ============ 1. Advanced Systems Lab ============

def micro_asl_benchmark():
    """系统性能测量 + Roofline 模型"""
    print("\n📋 Advanced Systems Lab: Roofline 模型")
    peak_flops = 10e12  # 10 TFLOP/s
    peak_bw = 100e9     # 100 GB/s
    # 操作强度 (FLOP/Byte)
    for name, oi in [("GEMM", 10), ["SpMV", 0.1], ["stencil", 1]]:
        ridge = peak_flops / peak_bw
        if oi < ridge:
            perf = oi * peak_bw
            bottleneck = "memory"
        else:
            perf = peak_flops
            bottleneck = "compute"
        print(f"   {name:8s} OI={oi:.1f} → {perf/1e9:.1f} GFLOP/s ({bottleneck}-bound)")
    print(f"   Ridge point = {peak_flops/peak_bw:.1f} FLOP/Byte")


# ============ 2. Big Data Systems ============

def micro_bd_mapreduce():
    """MapReduce 词频统计模拟"""
    print("\n📋 Big Data: MapReduce 词频")
    docs = ["eth zurich eth", "informatics zurich", "eth informatics eth"]
    # Map
    mapped = []
    for doc in docs:
        for word in doc.split():
            mapped.append((word, 1))
    # Shuffle (group)
    from collections import defaultdict
    grouped = defaultdict(list)
    for k, v in mapped:
        grouped[k].append(v)
    # Reduce
    result = {k: sum(v) for k, v in grouped.items()}
    for w, c in sorted(result.items(), key=lambda x: -x[1]):
        print(f"     {w}: {c}")


# ============ 3. Reliable Distributed Systems (Raft) ============

def micro_rds_raft_election():
    """Raft 领导者选举模拟"""
    print("\n📋 Reliable Dist (Raft): 领导者选举")
    n = 5
    nodes = [{"id": i, "term": 0, "state": "follower", "votes": 0} for i in range(n)]
    # 节点 0 超时发起选举
    nodes[0]["term"] = 1
    nodes[0]["state"] = "candidate"
    nodes[0]["votes"] = 1  # 自投
    # 请求投票
    for i in range(1, n):
        if random.random() > 0.2:  # 80% 投票
            nodes[i]["term"] = 1
            nodes[0]["votes"] += 1
    majority = n // 2 + 1
    if nodes[0]["votes"] >= majority:
        nodes[0]["state"] = "leader"
        print(f"   n={n}, 节点0 获 {nodes[0]['votes']} 票 (需 {majority})")
        print(f"   → 节点0 当选 leader (term={nodes[0]['term']})")
    else:
        print(f"   选举失败")


# ============ 4. Security Engineering ============

def micro_sec_access_control():
    """访问控制模型 (RBAC)"""
    print("\n📋 Security Engineering: RBAC 访问控制")
    roles = {
        "admin": ["read", "write", "delete"],
        "editor": ["read", "write"],
        "viewer": ["read"],
    }
    users = {"alice": "admin", "bob": "editor", "carol": "viewer"}
    # 检查权限
    for user, role_name in users.items():
        perms = roles[role_name]
        print(f"   {user} ({role_name}): {perms}")

    request = ("bob", "delete")
    role = users[request[0]]
    allowed = request[1] in roles[role]
    print(f"   请求 {request} → {'允许' if allowed else '拒绝'}")


# ============ 5. 3D Vision (Pollefeys) ============

def micro_3dv_camera_projection():
    """相机投影模型 (针孔)"""
    print("\n📋 3D Vision: 针孔相机投影")
    # 3D 点
    P = [1.0, 2.0, 5.0]  # x, y, z
    f = 100.0  # 焦距 (像素)
    # 投影: u = f*X/Z, v = f*Y/Z
    u = f * P[0] / P[2]
    v = f * P[1] / P[2]
    print(f"   3D 点 P={P}, 焦距 f={f}")
    print(f"   投影 (u,v) = ({u:.1f}, {v:.1f})")
    # 深度越远 → 越靠近中心
    P2 = [1.0, 2.0, 10.0]
    u2 = f * P2[0] / P2[2]
    print(f"   P'={P2} → u={u2:.1f} (更靠近光心)")

    # 本质矩阵: x2^T E x1 = 0
    print(f"   本质矩阵 E: 编码相对相机位姿 (5 DOF)")


# ============ 6. Probabilistic Programming ============

def micro_pp_inference():
    """概率编程：贝叶斯推断模拟"""
    print("\n📋 Probabilistic Programming: 贝叶斯推断")
    # 抛硬币：观察 7 正 3 反，推断 θ
    alpha, beta = 1, 1  # Beta 先验
    heads, tails = 7, 3
    # 后验 Beta(alpha+heads, beta+tails)
    post_a = alpha + heads
    post_b = beta + tails
    # 后验均值
    mean = post_a / (post_a + post_b)
    print(f"   先验: Beta({alpha},{beta}), 观察: {heads}H {tails}T")
    print(f"   后验: Beta({post_a},{post_b})")
    print(f"   后验均值 (θ估计) = {mean:.3f}")
    print(f"   MLE = {heads/(heads+tails):.3f} (无先验)")


# ============ 7. Advanced ML (核方法) ============

def micro_ml_kernel():
    """核技巧 + SVM 对偶"""
    print("\n📋 Advanced ML: 核技巧")
    def linear_kernel(x1, x2):
        return sum(a * b for a, b in zip(x1, x2))
    def rbf_kernel(x1, x2, gamma=0.5):
        return math.exp(-gamma * sum((a - b)**2 for a, b in zip(x1, x2)))

    x1, x2 = [1, 2, 3], [4, 5, 6]
    print(f"   x1={x1}, x2={x2}")
    print(f"   线性核 K = {linear_kernel(x1, x2):.2f}")
    print(f"   RBF核   K = {rbf_kernel(x1, x2):.4f}")
    print(f"   → 核技巧: 在高维空间计算内积，不显式映射 φ(x)")


# ============ 8. Statistical Learning Theory ============

def micro_slt_vc_dimension():
    """VC 维 + 样本复杂度"""
    print("\n📋 Statistical Learning Theory: VC 维")
    # 样本复杂度: m ≥ (1/ε)(4 log(2/δ) + 8d log(13/ε))
    for model, d in [("线性分类器", 3), ("区间", 2), ("正弦", float('inf'))]:
        eps, delta = 0.05, 0.05
        if d == float('inf'):
            m = "∞"
        else:
            m = int((1/eps) * (4 * math.log(2/delta) + 8 * d * math.log(13/eps)))
        print(f"   {model:12s} VC维={d}, ε={eps}: 需 ≥{m} 样本")
    print(f"   → VC维越高，所需样本越多（过拟合风险越大）")


# ============ 9. Information Theory ============

def micro_it_entropy():
    """熵 + 霍夫曼编码"""
    print("\n📋 Information Theory: 熵 + 编码")
    def entropy(probs):
        return -sum(p * math.log2(p) for p in probs if p > 0)

    # 公平硬币
    print(f"   公平硬币 H = {entropy([0.5, 0.5]):.3f} bits")
    # 不公平
    print(f"   偏硬币 H = {entropy([0.9, 0.1]):.3f} bits")
    # 英文字母频率（近似）
    letter_freq = [0.12, 0.09, 0.08, 0.07, 0.07, 0.06, 0.06, 0.05, 0.05,
                   0.04, 0.03, 0.03, 0.02, 0.02, 0.02, 0.01]
    s = sum(letter_freq)
    letter_freq = [p / s for p in letter_freq]
    H = entropy(letter_freq)
    print(f"   16 字母熵 = {H:.2f} bits (固定编码=4 bits)")
    print(f"   → 霍夫曼编码平均 < 4 bits, 接近 H")


# ============ 10. Causality (加深) ============

def micro_causal_structural():
    """结构因果模型 + 干预"""
    print("\n📋 Causality (加深): 结构学习")
    # 简单 SCM: X = N_x, Y = 2X + N_y
    random.seed(42)
    n = 1000
    Nx = [random.gauss(0, 1) for _ in range(n)]
    X = list(Nx)
    Y = [2 * xi + random.gauss(0, 0.5) for xi in X]

    # 观察 vs 干预
    mean_obs = sum(Y) / n
    # do(X=0): 干预后
    Y_do = [2 * 0 + random.gauss(0, 0.5) for _ in range(n)]
    mean_do = sum(Y_do) / n
    print(f"   模型: X=N_x, Y=2X+N_y")
    print(f"   E[Y|观察] = {mean_obs:.3f}")
    print(f"   E[Y|do(X=0)] = {mean_do:.3f}")
    print(f"   → 干移除了 X 的自然变异，纯因果效应")


# ============ 主入口 ============

def run_all():
    print("=" * 60)
    print("🎓 ETH Zürich 研究生补充课程微项目")
    print("=" * 60)

    micro_asl_benchmark()
    micro_bd_mapreduce()
    micro_rds_raft_election()
    micro_sec_access_control()
    micro_3dv_camera_projection()
    micro_pp_inference()
    micro_ml_kernel()
    micro_slt_vc_dimension()
    micro_it_entropy()
    micro_causal_structural()

    print("\n" + "=" * 60)
    print("✅ 全部研究生补充课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    run_all()
