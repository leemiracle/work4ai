# 06 CUDA attention kernel：GPU 编程模型 + 代码模板

> 从"用 PyTorch"到"写 CUDA kernel"的跨越。环境无 GPU, 本文用【numpy 模拟 + 代码模板】, 让你理解 CUDA kernel 的结构。真编译需 nvcc + GPU。
> 配套实验: `experiments/06_cuda_attention.py` (numpy 模拟 grid/block 执行)
> 核心洞察: **CUDA kernel = 把计算映射到 grid/block, 把热数据留在 SRAM (共享内存)**。

---

## 一、CUDA 编程模型: grid / block / thread / warp

GPU 不是"一个大核", 而是成千上万个小核心 (thread)。CUDA 用三层层级组织:

```
Grid  → 多个 Block (一个 kernel launch 一个 grid)
Block → 多个 Thread (block 内共享 shared memory, 可同步)
Thread → 最小执行单元 (有自己的寄存器)
Warp  → 32 thread 的组, GPU 实际执行单元 (SIMT, 同步同指令)
```

### 映射到 attention
- 一个 **block** 处理一个 **query tile** (如 64 个 query)
- block 内的 thread 协作算 `Q@K^T`, softmax, `@V`
- 多个 block 并行处理不同 query tile → **grid 覆盖所有 query**

**实验1**: N=512, BLOCK_M=64 → grid=8 blocks, block0 处理 query[0:64], ...

---

## 二、GPU 内存层次 (kernel 编程的核心约束)

| 层级 | 容量 | 延迟 | 访问 |
|------|------|------|------|
| **寄存器** | ~256KB/SM | 1 cycle | thread 私有 |
| **共享内存 SRAM** | ~228MB | ~30 cycle | block 内共享 |
| L1/L2 cache | ~50MB | ~200 cycle | 自动 |
| **HBM (显存)** | ~80GB | ~400 cycle | 所有 block, 慢 |

> **写 CUDA kernel 的核心技能: 把热数据留在寄存器/共享内存, 少碰 HBM。** 这是 FlashAttention (01) / compile 融合 (02) 的共同原理。

---

## 三、模拟一个 block 的执行 (实验2)

```
1. 加载 query tile (64×d) 到【共享内存】
2. 遍历所有 key tile:
   - 加载 key/value tile 到共享内存
   - 算 Q@K^T (在共享内存, 快)
   - online softmax 更新 (01篇)
   - 【中间 scores 矩阵永不写回 HBM!】
3. 写回结果 O 到 HBM
```

**实验2 实测**: numpy 模拟的"CUDA kernel" vs naive attention, **差异 2.09e-07** (严格等价)。中间 64×64 scores 矩阵全程在共享内存。

---

## 四、Warp divergence (实验3): 为什么 GPU 怕 if/else

Warp = 32 thread 同步执行**同一条指令** (SIMT)。若 `if` 把 warp 分两半 → 两半**串行**执行, 浪费算力。

**实验3 实测**: 无 divergence 21ms vs 有 divergence 110ms → **慢 5.2×**。

> 写 kernel 要避免 warp 内分支, 或让分支按 warp 边界对齐。

---

## 五、教学版 CUDA kernel 代码模板 (需 nvcc + GPU 编译)

```c
// 简化版 FlashAttention forward kernel (教学, 非生产)
// 真实实现见 github.com/Dao-AILab/flash-attention (hopper/ 目录)
__global__ void flash_attn_fwd_kernel(
    const float* __restrict__ Q,   // [N, d] in HBM
    const float* __restrict__ K,
    const float* __restrict__ V,
    float* __restrict__ O,          // [N, d] output
    int N, int d, float scale) {

    int q_block = blockIdx.x;       // ★ 每个 block 处理一个 query tile
    int tid = threadIdx.x;          // block 内 thread id

    // ★ 共享内存: block 内所有 thread 可见, ~30 cycle (HBM 的 1/13)
    __shared__ float Q_smem[BLOCK_M][d];
    __shared__ float K_smem[BLOCK_N][d];
    __shared__ float V_smem[BLOCK_N][d];

    // 1. 协作加载 Q tile 到共享内存
    for (int i = tid; i < BLOCK_M; i += blockDim.x)
        for (int j = 0; j < d; j++)
            Q_smem[i][j] = Q[(q_block*BLOCK_M + i)*d + j];
    __syncthreads();                // ★ 同步: 等 block 内所有 thread 加载完

    // online softmax 状态 (在寄存器, 每个 thread 一份)
    float m = -INFINITY, l = 0.0f;
    float acc[d] = {0};             // 累积输出

    // 2. 遍历所有 key tile
    for (int kb = 0; kb < N / BLOCK_N; kb++) {
        // 加载 K, V tile 到共享内存
        load_tile(K, K_smem, kb); load_tile(V, V_smem, kb);
        __syncthreads();

        // 算 scores = Q_smem @ K_smem^T * scale  (在共享内存!)
        // online softmax 更新 (01 篇的算法, 在寄存器)
        // m_new = max(m, m_block); l, acc 更新...
        __syncthreads();
    }

    // 3. 归一化并写回 O 到 HBM
    for (int j = 0; j < d; j++)
        O[(q_block*BLOCK_M + tid)*d + j] = acc[j] / l;
}
```

**关键点**:
- `__shared__` 声明共享内存 (block 内共享, 快)
- `__syncthreads()` 同步 block 内所有 thread
- `__restrict__` 帮编译器优化 (无别名)
- 中间矩阵 `Q@K^T` 永远在共享内存, **不写 HBM**

---

## 六、为什么 CUDA 难写但最快

| | CUDA | Triton (07篇) | PyTorch |
|---|------|------|---------|
| 抽象层次 | 最低 (手管内存) | 中 (block 级) | 最高 (自动) |
| 性能 | 最快 (精确控制) | 接近 CUDA | 最慢 |
| 开发难度 | 极高 | 中 | 低 |
| 适用 | 极致优化 (FlashAttn) | 大多数 kernel | 业务代码 |

> CUDA 难 = 你要手动管理寄存器/共享内存/同步/warp; CUDA 快 = 你能精确控制数据放哪。FlashAttention 的极致性能来自 CUDA 对内存层次的精确利用。

---

## 七、学习路径 (有 GPU 后)

1. **CUDA C++ 基础**: vector add → matrix mul → reduction (GPU MODE 课程)
2. **shared memory**: tiled matrix multiplication
3. **attention kernel**: 按本文模板, 实现 FlashAttention forward
4. **进阶**: warp shuffle, tensor core (wmma), TMA (H100), CUTLASS

---

## 参考文献
- NVIDIA, *CUDA C++ Programming Guide* (grid/block/warp 官方文档)
- Kirk & Hwu, *Programming Massively Parallel Processors* (CUDA 教材)
- GPU MODE: learngpu.com (从零写 kernel 的社区课程)
- Dao-AILab/flash-attention `hopper/` 目录 (真实 CUDA 实现, 主题3精读)
