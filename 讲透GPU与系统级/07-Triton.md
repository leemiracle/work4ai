# 07 Triton：block 级 GPU 编程 + FlashAttention 源码精读

> Triton (OpenAI) 是介于 CUDA 和 PyTorch 之间的 GPU kernel 语言——**block 级抽象**, 不用手写 thread/warp/共享内存, 但仍比 PyTorch 快得多。
> 本文精读 `Dao-AILab/flash-attention` 的真实 Triton 实现 `flash_attn/flash_attn_triton.py`。
> 核心洞察: **Triton 让你用 block 思维写 kernel, 编译器自动处理 thread/warp/共享内存**。

---

## 一、Triton vs CUDA vs PyTorch

| | PyTorch | **Triton** | CUDA |
|---|---------|---------|------|
| 抽象层 | 算子级 | **block 级** | thread 级 |
| 要管什么 | 几乎不用 | block 大小、循环 | thread/warp/shared memory/sync |
| 性能 | 慢 | 接近 CUDA | 最快 |
| 开发速度 | 快 | 中 | 慢 |

**Triton 的关键**: 你写"一个 block 干什么", Triton 编译器自动把它展开成成千上万个 thread + 共享内存 + 同步。你不用碰 `__syncthreads()`、`__shared__`、warp divergence 这些 CUDA 噩梦。

---

## 二、FlashAttention 的 Triton 源码精读 (`_fwd_kernel`)

来源: `flash_attn/flash_attn_triton.py` (真实生产代码)。逐段解读:

### 1. 装饰器: JIT + 自动调优
```python
@triton.jit                          # ★ 编译成 GPU kernel
def _fwd_kernel(Q, K, V, Bias, Out, Lse, TMP, softmax_scale, ...,
                BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):  # block 大小是编译期常量
```
- `@triton.jit`: 把 Python 函数编译成 GPU kernel
- `BLOCK_M: tl.constexpr`: block 大小是**编译期常量** (Triton 会为每个 BLOCK 组合重新编译)
- `@triton.autotune`: 自动尝试不同 BLOCK_M/BLOCK_N/num_warps 组合, 选最快的

### 2. block 索引 (相当于 CUDA blockIdx)
```python
start_m = tl.program_id(0)           # ★ 相当于 blockIdx.x: 哪个 query tile
off_hb = tl.program_id(1)            # batch * head 的合并索引
off_b = off_hb // nheads
off_h = off_hb % nheads
```
> `tl.program_id(0)` = CUDA 的 `blockIdx.x`。一个 program instance = 一个 block。

### 3. block 内偏移
```python
offs_m = start_m * BLOCK_M + tl.arange(0, BLOCK_M)    # 这个 block 处理的 query 行
offs_n = tl.arange(0, BLOCK_N)                         # key 列的 block 内偏移
offs_d = tl.arange(0, BLOCK_HEADDIM)                   # head 维度
```
> `tl.arange(0, BLOCK_M)` 创建 block 内的索引向量。整个 block 的数据用这些索引寻址。

### 4. 显式加载 (HBM → SRAM)
```python
q_ptrs = Q + off_b*stride_qb + off_h*stride_qh + (offs_m[:,None]*stride_qm + offs_d[None,:])
q = tl.load(q_ptrs)                  # ★ 显式从 HBM 加载到 block (SRAM), q 全程留在 SRAM
```
> `tl.load` = CUDA 的全局内存→共享内存加载。**显式控制数据搬运** (连接 01/06 篇: 把热数据搬进 SRAM)。

### 5. 核心循环: 遍历 key tile + online softmax
```python
m_i = full([BLOCK_M], -inf)          # online softmax 状态 (寄存器)
lse_i = full([BLOCK_M], -inf)        # log-sum-exp (代替 l, 数值稳定)
acc_o = zeros([BLOCK_M, BLOCK_HEADDIM])

for start_n in range(0, end_n, BLOCK_N):     # ★ key tile 循环
    k = tl.load(k_ptrs + start_n*stride_kn)  # 加载 key tile 到 SRAM
    qk = tl.dot(q, k, trans_b=True)          # ★ Q@K^T, 自动用 tensor core!
    if IS_CAUSAL:
        qk += tl.where(offs_m[:,None] >= (start_n+offs_n)[None,:], 0, -inf)  # causal mask

    # online softmax (01 篇的算法, 在 Triton 里)
    m_ij = maximum(tl.max(qk, 1) * softmax_scale, lse_i)
    p = tl.exp(qk * softmax_scale - m_ij[:,None])
    l_ij = tl.sum(p, 1)

    # 更新输出累加器 (rescale 旧的 + 加新的)
    acc_o = acc_o * tl.exp(m_i - m_ij)[:,None]    # rescale 旧贡献
    v = tl.load(v_ptrs + start_n*stride_vn)        # 加载 value tile
    acc_o += tl.dot(p, v)                           # 加新贡献

    m_i = m_ij
    lse_i = m_ij + tl.log(l_ij)                     # 数值稳定的 log-sum-exp
```
> 这就是 01 篇的 online softmax + tiling, 用 Triton 写出来。**`tl.dot` 自动用 tensor core**, `tl.load` 控制内存搬运。

### 6. 写回结果
```python
acc_o = acc_o * tl.exp(m_i - lse_i)[:,None]   # 最终归一化
tl.store(out_ptrs, acc_o)                       # ★ 写回 HBM
```

---

## 三、Triton 让你省了什么 (对比 06 篇 CUDA)

| CUDA 要手写 | Triton 自动处理 |
|------------|----------------|
| `__shared__` 共享内存声明 | 自动分配 (你用 block 级变量) |
| `__syncthreads()` 同步 | 自动插入 |
| thread 索引 (threadIdx) | 不存在 (你只写 block 级) |
| warp divergence | 编译器优化 |
| `tl.dot` 的 tile 分块 | 自动 (你写一个 `dot`, 它分块) |

**代价**: 你失去对寄存器/共享内存的精确控制, 极限性能略低于手写 CUDA。但对 95% 的 kernel, Triton 已经足够快。

---

## 四、autotune: 自动选最优配置

```python
@triton.autotune(
    configs=[
        triton.Config({"BLOCK_M": 128, "BLOCK_N": 128}, num_warps=8, num_stages=1),
        triton.Config({"BLOCK_M": 128, "BLOCK_N": 128, "SEQUENCE_PARALLEL": True}, num_warps=8),
    ],
    key=["CACHE_KEY_SEQLEN_Q", "CACHE_KEY_SEQLEN_K", ...]
)
```
> Triton 自动尝试不同 block 大小/warp 数/流水线级数, 选最快的。CUDA 要手动调, Triton 一行搞定。这是 Triton 对生产环境的大杀器。

---

## 五、源码里的工程细节 (真实代码的"坑")

读真实源码能看到课本没有的工程现实:
- **大量 `EVEN_M`/`EVEN_N` 分支**: 处理序列长度不是 block 整数倍时的边界 (mask)
- **`tl.debug_barrier()`**: 显式同步, 防 race condition (Triton 编译器的 bug)
- **`TMP` scratchpad**: 绕过编译器 bug 的临时缓冲
- **`eviction_policy="evict_last"`**: LRU 缓存提示

> 真实 kernel 比教学版复杂得多——大量边界处理、编译器 bug 绕路、性能调优。这就是为什么 ezyang 风格的源码精读有价值 (看真实代码, 不是玩具)。

---

## 六、Triton 生态

- **PyTorch 2.0 `torch.compile`**: Inductor 后端用 Triton 生成 kernel (02 篇)
- **vLLM / SGLang**: 部分 kernel 用 Triton
- **DeepSeek FlashMLA**: 主体是 CUDA, 但有 Triton 参考
- **学习**: OpenAI Triton tutorials (06-fused-attention.py 是本文源码基础)

---

## 参考文献
- Tillet et al. 2019, *Triton: An Intermediate Language and Compiler for Tiled Neural Network Computputations*
- OpenAI Triton tutorials: github.com/openai/triton (06-fused-attention.py)
- Dao-AILab/flash-attention `flash_attn/flash_attn_triton.py` (本文精读对象)
