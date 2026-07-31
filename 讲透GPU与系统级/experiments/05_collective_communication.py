"""
讲透并行通信 —— all-reduce / all-gather / all-to-all
=====================================================
大模型训练/推理的通信基础 (14 篇的深化)。本实验在 CPU 上模拟:
  实验1: ring all-reduce 算法 (步数 = 2(N-1), 每卡数据量 = 2(N-1)/N × size)
  实验2: 三大集体通信 (all-reduce / all-gather / all-to-all) 的语义
  实验3: DP/TP/PP 各自的通信模式与通信量

核心洞察: 分布式训练的瓶颈常常是【通信】, 不是计算。
跑法: python3 05_collective_communication.py
"""
import numpy as np

# ============================================================
# 实验 1: ring all-reduce —— DP 的核心通信原语
# ============================================================
print("=" * 72)
print("实验 1: ring all-reduce (数据并行的梯度同步)")
print("=" * 72)
print("""
all-reduce: 让所有 N 张卡都拿到【所有卡梯度的和】, 是数据并行的核心。
朴素做法: 每张卡把自己的梯度发给其他所有卡 → O(N²) 通信, 爆炸。
ring all-reduce: 把卡排成环, 分两阶段传递 → O(N) 通信, 最优!
  阶段1 (scatter-reduce): N-1 步, 每步每卡传 1/N 数据给下一卡, 累加
  阶段2 (all-gather):    N-1 步, 每步传 1/N 数据, 让所有卡拿到完整结果
  总步数 = 2(N-1), 每卡总发送量 = 2(N-1)/N × size  (几乎 = 2× size, 与 N 无关!)
""")

def ring_all_reduce(gpu_tensors):
    """模拟 ring all-reduce (numpy), 返回每卡最终结果"""
    N = len(gpu_tensors)
    size = len(gpu_tensors[0])
    chunk = size // N
    # 复制, 模拟两阶段
    bufs = [t.copy() for t in gpu_tensors]
    # 阶段1: scatter-reduce (N-1 步)
    for step in range(N - 1):
        new_bufs = [b.copy() for b in bufs]
        for i in range(N):
            send_chunk = (i + step) % N
            recv_chunk = (i + step + 1) % N
            # 卡 i 的 chunk send_chunk 累加到 卡 (i+1) 的同 chunk
            nxt = (i + 1) % N
            new_bufs[nxt][recv_chunk*chunk:(recv_chunk+1)*chunk] += bufs[i][send_chunk*chunk:(send_chunk+1)*chunk]
        bufs = new_bufs
    # 阶段2: all-gather (N-1 步)
    for step in range(N - 1):
        new_bufs = [b.copy() for b in bufs]
        for i in range(N):
            send_chunk = (i + step - (N-1) + 1) % N   # 错位传播
            nxt = (i + 1) % N
            new_bufs[nxt][send_chunk*chunk:(send_chunk+1)*chunk] = bufs[i][send_chunk*chunk:(send_chunk+1)*chunk]
        bufs = new_bufs
    return bufs

# 测试
N = 4; size = 16
np.random.seed(0)
gpu_tensors = [np.random.randn(size) for _ in range(N)]
result = ring_all_reduce(gpu_tensors)
true_sum = sum(gpu_tensors)   # 真实总和
print(f"测试: {N} 卡, 每卡 {size} 元素")
print(f"卡0 最终结果: {np.round(result[0][:4], 3)}")
print(f"真实总和:      {np.round(true_sum[:4], 3)}")
print(f"所有卡结果一致? {all(np.allclose(result[0], r) for r in result)}  ✓")
print(f"与真实和一致? {np.allclose(result[0], true_sum)}  ✓")
print(f"\n通信量分析 (N 卡, 数据 size 字节):")
print(f"  朴素 all-to-all: 每卡发 (N-1)×size, 总 O(N²×size)")
print(f"  ring all-reduce: 每卡发 2(N-1)/N × size ≈ 2×size, 总 O(N×size)  (省 N/2×)")
for nt in [4, 8, 32, 256]:
    ratio = nt / 2
    print(f"    N={nt:>3}: ring 比朴素省 {ratio:>3}× 通信量\n" if nt == 256 else "", end="")

print("\n")

# ============================================================
# 实验 2: 三大集体通信的语义
# ============================================================
print("=" * 72)
print("实验 2: 三大集体通信 (collective communication)")
print("=" * 72)

N = 4
print(f"\n【all-reduce】 所有卡拿到【元素级求和】 (DP 同步梯度)")
tensors = [np.array([1,2,3,4]) * (i+1) for i in range(N)]
print(f"  输入: 卡0={tensors[0]}, 卡1={tensors[1]}, ...")
print(f"  输出(所有卡): {sum(tensors)}")

print(f"\n【all-gather】 所有卡拿到【所有卡数据的拼接】 (TP 收集分片结果)")
parts = [np.array([i*10, i*10+1]) for i in range(N)]
print(f"  输入: 卡0={parts[0]}, 卡1={parts[1]}, ...")
print(f"  输出(所有卡): {np.concatenate(parts)}  (拼接, 不求和)")

print(f"\n【all-to-all】 每卡把自己的数据【分发】给所有卡 (EP 专家路由)")
# 每卡有 N 块, 第 j 块发给卡 j
data = [np.arange(N) + i*10 for i in range(N)]   # 卡i: [i*10, i*10+1, ..., i*10+N-1]
print(f"  输入: 卡0={data[0]}, 卡1={data[1]}, ...")
# all-to-all: 卡i 的第j块 → 卡j 的第i块
result = np.zeros((N, N), dtype=int)
for i in range(N):
    for j in range(N):
        result[j][i] = data[i][j]
print(f"  输出: 卡0={result[0]}, 卡1={result[1]}, ...  (转置式分发)")
print(f"\n  ==> all-reduce (求和) 用于 DP, all-gather (拼接) 用于 TP, all-to-all (分发) 用于 EP/MoE\n")


# ============================================================
# 实验 3: DP / TP / PP 的通信模式与通信量
# ============================================================
print("=" * 72)
print("实验 3: DP / TP / PP 各自的通信模式")
print("=" * 72)

# 假设: 模型参数 P, 层数 L, hidden d, batch B, seq T
P = 70e9; L = 80; d = 8192; B = 8; T = 2048; bytes_per = 2  # FP16

print(f"模型规模: {P/1e9:.0f}B 参数, {L} 层, batch={B}, seq={T}\n")

print("【数据并行 DP】 每步通信")
dp_comm = P * bytes_per * 2  # all-reduce 梯度 (约 2× 参数量)
print(f"  通信量 ≈ {dp_comm/1e9:.1f} GB/步 (all-reduce 梯度, ring)")
print(f"  频率: 每训练步一次")
print(f"  瓶颈: 大模型时梯度 all-reduce 很重\n")

print("【张量并行 TP】 每层通信 (2 次 all-reduce)")
tp_comm_per_layer = B * T * d * bytes_per * 2  # attention 前 + FFN 前
tp_comm_total = tp_comm_per_layer * L * 2     # 每层 2 次
print(f"  每层 all-reduce ≈ {tp_comm_per_layer/1e6:.1f} MB")
print(f"  全模型 {L} 层 ≈ {tp_comm_total/1e9:.2f} GB/前向")
print(f"  频率: 每层每前向都通信 → 必须 NVLink (节点内高速)")
print(f"  瓶颈: 通信频繁, 只适合节点内\n")

print("【流水线并行 PP】 层边界点对点通信")
pp_comm = B * T * d * bytes_per  # 每个层边界传激活
pp_comm_total = pp_comm * (1)  # PP 切成 stage, 每个 stage 边界传一次
print(f"  每个 stage 边界 ≈ {pp_comm/1e6:.1f} MB")
print(f"  频率: 每 stage 一次前向 + 一次反向")
print(f"  瓶颈: 气泡 (bubble) 导致闲置; 通信小但延迟敏感\n")

print("【专家并行 EP】 all-to-all (MoE 路由)")
n_experts = 256
ep_comm = B * T * d * bytes_per  # all-to-all
print(f"  每个 MoE 层 all-to-all ≈ {ep_comm/1e6:.1f} MB")
print(f"  频率: 每个 MoE 层 (DeepSeek-V3 有 {n_experts} 专家)")
print(f"  瓶颈: all-to-all 通信是 MoE 训练主要开销\n")

print("=" * 72)
print("核心洞察:")
print("  - DP: all-reduce 梯度 (每步, 大通信量)")
print("  - TP: all-reduce 激活 (每层, 频繁, 需 NVLink)")
print("  - PP: 点对点激活 (层边界, 有气泡)")
print("  - EP: all-to-all (MoE 路由, 主要开销)")
print("  现代训练 = DP×TP×PP×EP 多维并行, 通信调度是系统工程核心")
print("=" * 72)
