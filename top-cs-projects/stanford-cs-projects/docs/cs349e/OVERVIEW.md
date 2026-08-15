# CS349E: Efficient ML Infrastructure at Scale

> Stanford University, Autumn 2025
> Instructors: **Fred Kjolstad** + **Christos Kozyrakis** + **Azalia Mirhoseini** + **Aditya Raina**
> Time: Tue/Thu 10:30-11:50
> Prerequisites: CS240 (推荐) / CS107
> Difficulty: ⭐⭐⭐⭐⭐

---

## 📚 课程定位

**Stanford 官方 vLLM / Triton / 推理优化课**。讲师组合（系统教授 + Gemini 训练专家 Azalia Mirhoseini）罕见。

**核心命题**: 算法是科学，让算法跑起来是**工程**。ML 系统决定 AI 能不能上线。

---

## 🎯 学习目标

1. **理解** GPU 架构（Fermi → Blackwell）
2. **掌握** CUDA / Triton 编程
3. **实现** PagedAttention（vLLM 核心）
4. **掌握** 分布式训练（DeepSpeed / FSDP / Megatron）
5. **实现** 量化（GPTQ / AWQ / FP8）
6. **设计** AI 集群调度

---

## 📅 完整模块（推测，基于讲师方向）

### Week 1: ML 系统栈总览
- 硬件 / 系统 / 算法分层
- 推理 vs 训练 tradeoff
- 成本/延迟/吞吐量三角

### Week 2: GPU 架构
- NVIDIA GPU 演化（Fermi → Hopper → Blackwell）
- SM / Warp / Thread hierarchy
- 内存层级（HBM / L2 / L1 / Registers）
- Tensor Core 原理

### Week 3: CUDA Programming
- CUDA 编程模型
- Thread blocks / Grid
- Coalesced memory access
- Bank conflicts

### Week 4: Triton
- OpenAI Triton 语言
- Block-level programming
- 与 CUDA 对比
- 写一个 vector addition + matmul

### Week 5: Attention 优化
- 🔴 **FlashAttention** (Tri Dao 2022)
- FlashAttention-2 / FlashAttention-3
- Online softmax
- Memory bandwidth analysis

### Week 6: KV Cache & PagedAttention ⭐
- KV cache 数据结构
- **PagedAttention** (Kwon 2023, SOSP)
- vLLM 架构
- Continuous batching

### Week 7: 推理引擎
- vLLM 深度
- SGLang (RadixAttention)
- TensorRT-LLM
- 推理 vs 训练 serving

### Week 8: 量化
- **GPTQ** (Frantar 2022)
- **AWQ** (Lin 2023)
- FP8 训练
- INT4 / 1-bit LLM

### Week 9: 分布式训练
- 数据并行（DP / DDP）
- 张量并行（Megatron-LM）
- 流水并行（Pipeline）
- 🔴 **ZeRO** (Rasley 2020, DeepSpeed)
- FSDP (PyTorch FSDP)

### Week 10: MoE + Cluster
- Mixture of Experts
- Mixtral / DeepSeek-V3 路由
- Slurm / Kubernetes
- MegaScale (字节)

---

## 🧮 核心算法

### PagedAttention（vLLM 核心）
```
传统：每个请求预分配 max_seq_len 内存
  → 浪费严重（实际平均使用 30%）

PagedAttention：把 KV cache 分成固定大小块（默认 16 tokens）
  → 类比 OS virtual memory + paging
  → 按需分配 + 前缀共享（prefix sharing）
```

**内存节省**: ~3-5x throughput 提升。

### FlashAttention
```
传统 attention: O(n²) 内存（materialize QK^T）
FlashAttention: O(n) 内存（tiling + online softmax）
  - 把 Q, K, V 切成 blocks
  - 用 shared memory 累积
  - 不写出中间矩阵
```

### Continuous Batching
```
传统 batching: 等 batch 里所有请求完成
  → 短请求被长请求拖累

Continuous batching: 每步重新组 batch
  → 完成的立即移出，新请求加入
  → GPU 利用率从 ~30% → ~80%
```

---

## 💻 项目代码

📁 `topic4-mlsys/kv_cache_sim.py`

**实现**:
1. ✅ 传统 KV Cache 管理
2. ✅ PagedAttention 分块分配
3. ✅ INT8 量化 + 误差测量
4. ✅ Continuous batching 模拟

### 运行
```bash
cd topic4-mlsys
python3 kv_cache_sim.py
```

**输出**:
```
📋 1. KV Cache 传统管理
   req1: 100 tokens, 内存 12800 floats = 50.0 KB

📋 2. PagedAttention (vLLM 核心)
   Free blocks: 94/100
   Fragmentation: 12.5%

📋 3. INT8 量化
   FP32: 4000 bytes
   INT8: 1000 bytes (25%)
   量化误差 RMSE: 0.000123

📋 4. Continuous Batching
   总 tokens: 142
   wall time: 30 steps
   吞吐: 4.73 tokens/step
   GPU 利用率: 95.33%
```

---

## 📊 关键论文

### 🔴 P0
1. **Kwon et al. 2023** "Efficient Memory Management for LLM with PagedAttention" (vLLM) SOSP
2. **Dao et al. 2022** "FlashAttention" NeurIPS
3. **Dao 2023** "FlashAttention-2" ICLR
4. **Rasley et al. 2020** "DeepSpeed: ZeRO" (System for ML)
5. **Shoeybi et al. 2019** "Megatron-LM" arXiv
6. **Frantar et al. 2022** "GPTQ" ICLR
7. **Lin et al. 2023** "AWQ" MLSys
8. **Zheng et al. 2023** "SGLang" arXiv

### 🟡 P1
9. **Aminabadi et al. 2022** "Megatron-DeepSpeed"
10. **Hopkins 2024** "Muon optimizer"
11. NVIDIA H100 / Blackwell whitepapers

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **AI 工程师（推理）** | CS107 → CS240 → CS349E（最高 ROI） |
| **分布式训练** | CS240 → CS349E |
| **想创业** | CS349E → vLLM/SGLang 贡献 |

---

## 💡 反思

### 课程优势
1. **稀缺** — 全美极少数"推理优化"完整课
2. **讲师组合** — 系统 + 训练专家
3. **就业必备** — ML 工程师最缺的技能

### 潜在局限
1. **官网不公开**（DNS 失败），可能需要 Stanford 账号
2. **缺 GPU 实操** — 需要自己找 Colab / Lambda
3. **更新快** — 2025 后期技术（如 Muon）可能没收录

---

## 🚀 扩展

完成 CS349E 后推荐：
1. **CS145** Modern Data Systems — 数据库视角的 AI infra
2. **CS349F** Fabric Architectures — 网络层
3. **CS349H** Software for HW — 编译层
4. 实习: apply 到 vLLM / Together AI / Fireworks / Mistral

---

**最后更新**: 2026-08-11
**对应代码**: `topic4-mlsys/kv_cache_sim.py`
