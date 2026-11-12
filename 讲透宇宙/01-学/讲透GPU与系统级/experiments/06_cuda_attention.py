"""
讲透 CUDA attention kernel —— GPU 编程模型 + numpy 模拟执行
=============================================================
⚠️ 环境无 GPU/CUDA, 本实验用【numpy 模拟】GPU kernel 的执行模型, 让你理解:
  - grid/block/thread 怎么映射到 attention 的计算
  - 共享内存 (shared memory) 怎么用
  - warp (线程束) 的概念
  - 为什么 CUDA kernel 难写但最快

跑法: python3 06_cuda_attention.py
真实 CUDA 代码见 06 文档的代码模板 (需 GPU 编译)。
"""
import numpy as np
import time

np.random.seed(0)

# ============================================================
# 实验 1: GPU 执行模型 —— grid / block / thread
# ============================================================
print("=" * 72)
print("实验 1: GPU 执行模型 (grid / block / thread)")
print("=" * 72)
print("""
GPU 不是"一个大核", 而是成千上万个小核心 (thread)。
CUDA 用三层层级组织它们:

  Grid  → 由多个 Block 组成 (一个 kernel launch 一个 grid)
  Block → 由多个 Thread 组成 (block 内 thread 共享 shared memory, 可同步)
  Thread → 最小执行单元 (有自己的寄存器)

  Warp  → 32 个 thread 的组, GPU 的实际执行单元 (SIMT, 同步执行)
          所有 thread 必须走同一条指令 (if/else 会导致 warp divergence)

  映射到 attention:
    一个 block 处理【一个 query tile】(如 64 个 query)
    block 内的 thread 协作: 算 Q@K^T, softmax, @V
    多个 block 并行处理不同的 query tile → grid 覆盖所有 query
""")

# 模拟: 把 attention 分配到 grid of blocks
N, d = 512, 64          # 512 个 token
BLOCK_M = 64             # 每个 block 处理 64 个 query
NUM_BLOCKS = (N + BLOCK_M - 1) // BLOCK_M   # grid 大小

print(f"任务: attention, N={N}, d={d}")
print(f"配置: BLOCK_M={BLOCK_M} (每 block 64 query), grid = {NUM_BLOCKS} blocks")
print(f"  block 0: query [0:64],   block 1: query [64:128], ...")
print(f"  每个 block 独立并行 (GPU 上真的并行; 这里串行模拟)\n")


# ============================================================
# 实验 2: 模拟一个 block 的执行 (用共享内存 + 遍历 key tiles)
# ============================================================
print("=" * 72)
print("实验 2: 模拟一个 block 的执行 (共享内存 + key tile 遍历)")
print("=" * 72)
print("""
一个 block 的 attention kernel 干什么:
  1. 把自己的 query tile (64×d) 加载到【共享内存】(SRAM, block 内所有 thread 可见)
  2. 遍历所有 key tile:
     - 把 key tile (64×d) 加载到共享内存
     - 算 Q @ K^T (在共享内存/寄存器里, 快)
     - online softmax 更新 (01篇)
  3. 写回结果到 HBM

关键: 中间矩阵 (64×64) 永远在【共享内存/寄存器】, 不写回 HBM → 这就是 FlashAttention 的本质
""")

Q = np.random.randn(N, d).astype(np.float32)
K = np.random.randn(N, d).astype(np.float32)
V = np.random.randn(N, d).astype(np.float32)
scale = d ** -0.5

def naive_attention(Q, K, V):
    scores = Q @ K.T * scale
    m = scores.max(axis=-1, keepdims=True)
    w = np.exp(scores - m); w /= w.sum(axis=-1, keepdims=True)
    return w @ V

# 模拟 GPU kernel: grid of blocks, 每个块用共享内存
def simulate_cuda_attention(Q, K, V, BLOCK_M=64, BLOCK_N=64):
    """模拟 CUDA kernel 的执行: grid of blocks, 每块处理一个 query tile"""
    N, d = Q.shape
    scale = d ** -0.5
    O = np.zeros_like(Q)
    shared_mem_usage = 0   # 统计共享内存使用 (模拟)
    hbm_reads = 0          # 统计 HBM 读取

    # === GRID: 多个 block 并行 (这里串行模拟) ===
    for block_idx in range((N + BLOCK_M - 1) // BLOCK_M):
        q_start = block_idx * BLOCK_M
        q_end = min(q_start + BLOCK_M, N)
        bm = q_end - q_start

        # --- block 开始: 加载 query tile 到【共享内存】 ---
        Q_smem = Q[q_start:q_end].copy()   # 模拟 load 到 shared memory
        shared_mem_usage += Q_smem.nbytes
        hbm_reads += Q_smem.nbytes

        # online softmax 状态 (在寄存器, 每个 query 一份)
        m_running = np.full(bm, -np.inf)
        l_running = np.zeros(bm)
        O_running = np.zeros((bm, d))

        # --- block 内: 遍历所有 key tile ---
        for k_start in range(0, N, BLOCK_N):
            k_end = min(k_start + BLOCK_N, N)
            # 加载 key/value tile 到【共享内存】
            K_smem = K[k_start:k_end].copy()
            V_smem = V[k_start:k_end].copy()
            shared_mem_usage += K_smem.nbytes + V_smem.nbytes
            hbm_reads += K_smem.nbytes + V_smem.nbytes

            # 在共享内存/寄存器里算 (不写回 HBM!)
            scores = Q_smem @ K_smem.T * scale    # bm × BLOCK_N, 留在 SRAM
            m_block = scores.max(axis=-1)
            P = np.exp(scores - np.maximum(m_running, m_block)[:, None])
            # online 合并 (01 篇)
            m_new = np.maximum(m_running, m_block)
            alpha = np.exp(m_running - m_new)
            beta = np.exp(m_block - m_new)
            l_running = l_running * alpha + P.sum(axis=-1)
            O_running = O_running * alpha[:, None] + P @ V_smem
            m_running = m_new

        # --- block 结束: 写回结果到 HBM ---
        O[q_start:q_end] = O_running / l_running[:, None]
    return O, shared_mem_usage, hbm_reads

O_naive = naive_attention(Q, K, V)
O_cuda, smem, hbm_r = simulate_cuda_attention(Q, K, V, BLOCK_M=64, BLOCK_N=64)

print(f"验证: CUDA 模拟 vs naive 最大差异: {np.abs(O_naive - O_cuda).max():.2e}  (严格等价!)")
print(f"\n共享内存 (SRAM) 使用: {smem/1024:.0f} KB (block 内复用, 极快)")
print(f"HBM 读取: {hbm_r/1024:.0f} KB (读 Q,K,V, 写 O)")
print(f"中间 scores 矩阵 (64×64): 永远在共享内存, 不写 HBM! ← 这就是 FlashAttention 的核心\n")


# ============================================================
# 实验 3: warp divergence (分支惩罚)
# ============================================================
print("=" * 72)
print("实验 3: warp divergence —— 为什么 if/else 在 GPU 上要小心")
print("=" * 72)
print("""
Warp = 32 个 thread 同步执行【同一条指令】(SIMT)。
如果 if 把 warp 内的 thread 分成两半:
  → 两半【串行】执行 (先走 if 分支, 再走 else), 浪费一半算力
  → 这叫 warp divergence
""")

# 模拟: 32 个 thread, 一半走 if 一半走 else
n_threads = 32
# 无 divergence: 所有 thread 同操作
data = np.random.randn(10000, 32)
t = time.time()
for _ in range(100): result = data * 2          # 所有 thread 同指令
t_no_div = time.time() - t

# 有 divergence: 一半 thread 乘 2, 一半乘 3 (模拟 if/else)
t = time.time()
for _ in range(100):
    result = np.where(data > 0, data * 2, data * 3)   # 条件分支
t_div = time.time() - t

print(f"无 divergence (所有 thread 同 op): {t_no_div*1000:.1f} ms")
print(f"有 divergence (if/else 分支):      {t_div*1000:.1f} ms  → 慢 {t_div/t_no_div:.1f}×")
print(f"  ==> GPU kernel 里尽量避免 warp 内的分支 (或让分支按 warp 对齐)\n")


# ============================================================
# 实验 4: 内存层次综合 (连接 01 篇)
# ============================================================
print("=" * 72)
print("实验 4: GPU 内存层次 —— kernel 编程的核心约束")
print("=" * 72)

print("""
┌─────────────────────────────────────────────────────────────┐
│  层级          容量        延迟       谁能访问              │
├─────────────────────────────────────────────────────────────┤
│  寄存器        ~256KB/SM   1 cycle   每个 thread 私有       │
│  共享内存 SRAM ~228MB      ~30 cycle block 内 thread 共享   │
│  L1/L2 cache   ~50MB       ~200 cycle  自动管理            │
│  HBM (显存)    ~80GB       ~400 cycle 所有 block, 慢       │
└─────────────────────────────────────────────────────────────┘
""")
print("写 CUDA kernel 的核心技能: 把热数据尽量留在【寄存器/共享内存】, 少碰 HBM。")
print("这就是 FlashAttention (01篇) / torch.compile 算子融合 (02篇) 的共同原理。")
print("CUDA 难写 = 你要手动管理这些层级; CUDA 快 = 你能精确控制数据放哪。\n")

print("=" * 72)
print("全部实验完成! 核心: CUDA kernel = 把计算映射到 grid/block, 把数据留在 SRAM")
print("真实 CUDA 代码 (需 GPU 编译) 见 06 文档的代码模板")
print("=" * 72)
