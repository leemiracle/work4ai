# 讲透 GPU 与系统级

> 从"用 Transformer"到"理解它在 GPU 集群上怎么跑"再到"读懂真实 CUDA/Triton 源码"。硬核系统级深度。
> 环境约束: 纯 CPU (无 GPU/CUDA), 但核心数学与算法全部用 numpy 实跑验证; 真实源码用 zread 精读。
> 配套: `讲透Transformer/` 是前置 (01-15 篇架构与原理)。

---

## 📚 文档导航 (8 篇)

### 系统原理 (CPU 实跑验证)
| 文档 | 主题 | 核心洞察 |
|------|------|---------|
| [01-FlashAttention深度](01-FlashAttention深度.md) | GPU 内存层次 + online softmax + tiling | 快是因读写少, 非算得少 |
| [02-PyTorch内部](02-PyTorch内部.md) | autograd / SDPA 后端 / torch.compile | define-by-run + 融合, 都为减 HBM 读写 |
| [03-推理引擎](03-推理引擎.md) | vLLM PagedAttention / continuous batching | 推理引擎 = OS 思想 + Transformer |
| [04-量化与低精度](04-量化与低精度.md) | FP8 / INT4 / outlier (AWQ) | 难点在 LLM 激活的 outlier |
| [05-并行通信](05-并行通信.md) | all-reduce / all-gather / all-to-all | DP/TP/PP/EP 各用不同通信原语 |

### GPU 编程与源码精读 (理论 + 真实源码)
| 文档 | 主题 | 核心洞察 |
|------|------|---------|
| [06-CUDA-kernel](06-CUDA-kernel.md) | grid/block/warp + 内存层次 + 代码模板 | CUDA = 把计算映射到 grid/block, 数据留 SRAM |
| [07-Triton](07-Triton.md) | block 级编程 + FlashAttention Triton 源码精读 | Triton = block 抽象, 编译器自动处理 thread/warp |
| [08-源码精读综合](08-源码精读综合.md) | CUDA hopper + Triton + vLLM PagedAttention 真实源码 | 三者本质都是 tiling+online softmax, 区别在抽象层 |

---

## 🧪 实验 (全部已实跑验证)

```
experiments/
├── 01_flash_attention.py        # online softmax + tiling (diff ~1e-16 等价)
├── 02_pytorch_internals.py      # 手写 autograd 与 PyTorch 逐位一致
├── 03_inference_engine.py       # 分页 KV Cache + continuous batching (吞吐 2×)
├── 04_quantization.py           # per-channel 误差降 10×, AWQ 降 6×
├── 05_collective_communication.py  # ring all-reduce 通信量省 128×
└── 06_cuda_attention.py         # numpy 模拟 CUDA grid/block 执行 (diff 2e-7)
```
跑法: `cd experiments && python3 0X_xxx.py`

---

## 🎯 贯穿全局的核心思想

**所有 GPU 系统优化, 本质都在打一场仗:**

> **让数据尽量留在快的存储 (SRAM/寄存器), 少搬运到慢的存储 (HBM/网络)。**

| 主题 | 怎么减"搬运" |
|------|------------|
| FlashAttention | 不物化 n×n, tiling 在 SRAM 算 |
| PyTorch compile | 算子融合, 中间值留寄存器 |
| PagedAttention | 分页消除碎片, 减少 KV Cache 浪费 |
| 量化 | 少比特 = 少字节搬运 |
| ring all-reduce | O(N²) 通信降到 O(N) |
| CUDA/Triton kernel | 手动/block 级控制数据放哪 |

---

## 📖 精读的真实源码 (ezyang 风格)

- **Triton FlashAttention**: `Dao-AILab/flash-attention/flash_attn/flash_attn_triton.py` (07 篇逐段精读)
- **CUDA FlashAttention-3**: `Dao-AILab/flash-attention/hopper/` (08 篇, SM90 TMA/GMMA)
- **vLLM PagedAttention**: `vllm-project/vllm/csrc/` (08 篇, 分页 KV + warp shuffle)

---

## 🔗 与 Transformer 项目的关系

```
讲透Transformer/ (前置: 架构与原理, 18篇)
    01 Self-Attention深度 (FlashAttention 是什么)
        ↓ 深入"怎么做到的"
讲透GPU与系统级/ (本项目: 系统实现 + 源码, 8篇)
    01 FlashAttention深度 (tiling + online softmax 数学)
    02-05 系统/工程优化
    06-08 GPU 编程 + 真实源码精读
```

---

## 📌 下一步路径 (有 GPU 后)

本项目 (CPU 可验证 + 源码精读) 完成后:
1. **GPU MODE** (learngpu.com) 从零写 CUDA attention kernel
2. **Triton tutorials** (OpenAI) — 改 FlashAttention Triton 的 BLOCK_M, 跑 benchmark
3. **flash-attention hopper 源码** — 读真实 CUDA SM90 实现
4. **vLLM 源码** — 读 PagedAttention 的真实分页寻址 + continuous batching
5. **贡献开源** — 给 flash-attention / vLLM 提 PR (ezyang 路线)
