# 讲透公开课 · 03 - AI Infra 源码导读清单

> 姊妹篇：[`01-前沿课实时清单`](./01-前沿课实时清单.md)（AI/ML 课）｜ [`02-数理计算机神课清单`](./02-数理计算机神课清单.md)（数学/物理/CS 课）｜ [`04-全领域学习路径总览`](./04-全领域学习路径总览.md)（路线图）。
>
> 本篇不收"课"，收**全球顶级 AI Infra 开源项目**——每个都给「**仓库入口 + 核心论文 + 关键源码文件 + 阅读顺序 + 和 02 系统课的映射**」。02 教你"OS/分布式/CUDA 为什么这么设计"，本篇告诉你"**这些设计在 vLLM / SGLang / Ray / Triton 里具体是哪几个文件**"。读完能从"会用 API"跨到"能改内核"。
>
> **核对日期**：2026-08-03（**第二轮·GitHub API 全量核 18 项目**，所有 stars/last push 都是当日实抓数据；本轮新发现：SGLang 已扩到 diffusion/VLM/Wan/MiniMax 多模态；verl 2.28w stars 超 OpenRLHF 2 倍；TGI 4 个月未动疑似停滞）
> **图例**：🟢 = 近期高频迭代（周级提交）　🟡 = 稳定维护　🔴 = 维护停滞/已归档
> **收录原则**：① 全球头部 AI 公司在生产用；② 源码完整可读、有论文/技术博客背书；③ 覆盖「推理 / 训练 / 调度 / 算子 / 通信」全栈。

---

## 一、速览表（先看这一张）

> 📊 **stars 排名（2026-08-03 实抓）**：PyTorch 10.2w > vLLM 8.8w > Unsloth 6.9w > DeepSpeed 4.3w ≈ Ray 4.3w > SGLang 3.1w > flash-attention 2.5w > **verl 2.3w（字节 RL 后端，超 OpenRLHF 2 倍）** > Triton 2.0w > Megatron-LM 1.7w > Axolotl 1.2w ≈ xFormers 1.1w ≈ TGI 1.1w > CUTLASS 1.0w > FlashInfer 6.1k > NCCL 4.9k > Slurm 4.2k > KubeRay 2.6k

| # | 项目 | 类别 | Stars | 核心创新 | 状态 |
|---|---|---|---|---|---|
| I1 | **vLLM** | 推理服务 | **88.1k** ⭐ | PagedAttention + 连续 batching；topics 已含 deepseek-v3/kimi/qwen3/gpt-oss/blackwell/tpu | 🟢 周级提交 |
| I2 | **SGLang** | 推理服务 + RL 后端 + **多模态** | **31.2k** ⭐ | RadixAttention + 零开销调度；**topics 已扩到 diffusion/vlm/wan/minimax**（多模态推理引擎） | 🟢 40万+ GPU 在线 |
| I3 | **TGI**（HuggingFace） | 推理服务 | **10.9k** ⭐ | flash-attention + 持续部署 | 🔴 **4 个月未动**（push 2026-03-21）|
| T1 | **Megatron-LM / Megatron-Core** | 训练（TP/PP/DP） | **17.3k** ⭐ | Transformer 并行范式定义者 | 🟢 NVIDIA 维护 |
| T2 | **DeepSpeed** | 训练（ZeRO/PP） | **42.9k** ⭐ | ZeRO-1/2/3 + 卸载到 CPU/NVMe | 🟢 微软维护 |
| T3 | **Unsloth** | 训练（高效微调） | **69.4k** ⭐ | 手写 Triton kernel + 4x LoRA 速度 | 🟢 热门 |
| T4 | **Axolotl** | 训练（微调料） | **12.3k** ⭐ | 配置驱动微调，集成多模型 | 🟢 |
| T5 | **verl / AReaL / Miles** | RL 后端 | **verl 22.8k / AReaL 5.6k** ⭐ | RLHF/GRPO 大规模训练（verl = 字节 HybridFlow，超 OpenRLHF 9.8k 两倍）| 🟢 新生代 |
| D1 | **Ray** | 分布式调度 | **43.4k** ⭐ | Task/Actor/Object 抽象 + AI Libraries | 🟢 Anyscale |
| D2 | **Slurm** | HPC 调度 | **4.2k** ⭐ | HPC 事实标准（训练集群） | 🟡 |
| D3 | **Kubernetes + KubeRay** | 容器调度 | **KubeRay 2.6k** ⭐ | AI workload on K8s | 🟢 |
| K1 | **FlashAttention** | 算子（attention） | **24.6k** ⭐ | IO-aware attention 范式 | 🟢 v3 |
| K2 | **Triton** | 算子（DSL/编译器） | **19.8k** ⭐ | Python 写 GPU kernel，MLIR 后端 | 🟢 2.0 |
| K3 | **CUTLASS** | 算子（GEMM 库） | **10.2k** ⭐ | NVIDIA CUDA GEMM 模板库 + Python DSL | 🟢 NVIDIA |
| K4 | **FlashInfer / xFormers** | 算子（attention 变体） | **FlashInfer 6.1k / xFormers 10.5k** ⭐ | memory-efficient / 长上下文 / JIT 编译 | 🟢 |
| C1 | **NCCL** | 通信（GPU 集合通信） | **4.9k** ⭐ | NVIDIA GPU 集合通信库 | 🟡 标准 |
| C2 | **Gloo** | 通信（CPU 集合通信） | （PyTorch 子模块，无独立 stars）| PyTorch 默认 CPU 后端 | 🟡 |
| U1 | **CUDA Toolkit** | 全栈底座 | （NVIDIA 闭源）| NVIDIA GPU 编程模型 | 🟢 |
| U2 | **PyTorch** | 全栈底座 | **102.2k** ⭐（最大）| eager + torch.compile + FSDP | 🟢 |

---

## 二、推理服务层（I1–I3）

### I1. vLLM — 🟢 推理服务事实标准

> **联网核对（2026-08-03）**：`vllm-project/vllm`，88.1k stars / 20.2k forks / **19,460 commits**（极度活跃）。起源 UC Berkeley Sky Computing Lab，现由 2000+ 贡献者维护。

- **仓库**：https://github.com/vllm-project/vllm
- **文档**：https://docs.vllm.ai ｜ **论文**：[Efficient Memory Management for LLM Serving with PagedAttention](https://arxiv.org/abs/2309.06180)（SOSP 2023）
- **核心创新**：
  - **PagedAttention**：把 KV cache 像 OS 虚拟内存一样分页管理，消除显存碎片
  - **Continuous batching**：请求级别动态拼 batch（不是 request-level）
  - **Chunked prefill + prefix caching**：分离 prefill/decode，复用共享前缀
  - **量化全家桶**：FP8 / MXFP4 / NVFP4 / INT4 / GPTQ / AWQ
  - **多种 attention kernel**：FlashAttention / FlashInfer / TRTLLM-GEN / FlashMLA / Triton
  - **Speculative decoding**：n-gram / EAGLE / DFlash
  - **分布式**：tensor / pipeline / data / expert / context parallelism
  - **200+ 模型架构**支持（Llama / Qwen / DeepSeek / GPT-OSS / Mamba / 多模态…）

**源码导读**（按推荐阅读顺序）：
```
vllm/
├── engine/llm_engine.py        ← ① 主引擎，请求生命周期入口
├── core/
│   ├── scheduler.py            ← ② 连续 batching 调度器（核心）
│   └── block_manager.py        ← ③ PagedAttention 的 block 分配
├── attention/
│   └── backends/               ← ④ 各 attention 后端（FlashAttn/Triton…）
├── worker/worker.py            ← ⑤ GPU worker 进程
├── model_executor/models/      ← ⑥ 各模型的实现（学模型架构看这里）
└── csrc/                       ← ⑦ CUDA C++ kernels
```

**阅读路径**：① llm_engine → ② scheduler → ③ block_manager（这三步搞懂 PagedAttention 全貌）→ ④ attention backends（看 attention 怎么被替换）→ ⑥ 选一个简单模型（如 llama）读完整 forward。

**对应「02 系统课」**：`02-C3 6.5840 分布式`（请求调度）+ `02-C4 6.1810 OS`（虚存分页 = PagedAttention 灵感）+ `02-C8 15-213 CSAPP`（内存层级）+ `02-C14 Onur Mutlu 架构`（GPU 内存）。

**一句话**：所有"显存怎么管、请求怎么调度"的工程问题，vLLM 是教科书级实现。

---

### I2. SGLang — 🟢 推理服务 + RL 后端双料王

> **联网核对（2026-08-03）**：`sgl-project/sglang`，31.1k stars / 7.6k forks / **15,991 commits**。**重要**：已成为事实工业标准，**部署在 40 万+ GPU 上**，被 xAI / NVIDIA / AMD / Cursor / LinkedIn / 阿里 / 腾讯采用。由 LMSYS 非营利组织维护。2026 年仍在 day-0 支持新模型（Kimi K3 / GLM5.2 / DeepSeek-V4）。

- **仓库**：https://github.com/sgl-project/sglang
- **文档**：https://docs.sglang.io ｜ **学习材料**：https://github.com/sgl-project/sgl-learning-materials
- **核心创新**：
  - **RadixAttention**：用基数树自动复用任意前缀的 KV cache（比 vLLM 的 prefix cache 更通用）
  - **零开销 CPU 调度器**：Rust + 优化过的 Python，调度开销 < 1%
  - **Prefill-Decode 分离（PD disaggregation）**：把 prefill 和 decode 物理分离到不同 GPU
  - **大规模 EP（Expert Parallelism）**：DeepSeek MoE 在 GB200/GB300 上的工业级部署
  - **Speculative decoding**：DFlash / Spec V2（2026 新一代）
  - **结构化输出**：compressed FSM（JSON decoding 3x faster）
  - **RL 后端**：被 `verl` / `AReaL` / `Miles` / `slime` / `Tunix` 用作 RL rollout
- **硬件**：NVIDIA / AMD / Intel CPU / **Google TPU**（SGLang-Jax）/ Huawei Ascend

**源码导读**：
```
python/sglang/srt/
├── managers/scheduler.py       ← ① 零开销调度器（核心）
├── mem_cache/
│   └── radix_cache.py          ← ② RadixAttention 基数树（核心）
├── model_executor/             ← ③ 模型执行
├── lora/                       ← ④ 多 LoRA batching
├── processors/                 ← ⑤ 结构化输出 / tool calling
└── disaggregation/             ← ⑥ PD 分离（2025-2026 新方向）
rust/
├── sgl-router/                 ← ⑦ Rust 写的负载均衡路由（高性能）
└── ...                         ← ⑧ 性能关键路径用 Rust 重写
proto/sglang/runtime/v1/        ← ⑨ v1 架构（gRPC + 异步）
```

**阅读路径**：② radix_cache（先理解 RadixAttention）→ ① scheduler（看请求怎么过调度器）→ ③ model_executor → ⑥ disaggregation（学最新工程趋势）→ ⑦ sgl-router（Rust 高性能组件）。

**对应「02 系统课」**：`02-C3 6.5840`（调度 + 分布式）+ `02-C7 15-418 并行`（GPU + EP）+ `02-C15 15-440`（大规模部署）。

**一句话**：想搞 RLHF/GRPO 后端、大规模 MoE 推理，SGLang 是 2025-2026 的核心项目；和 vLLM 是**竞争关系**（不是合并），各自演化。

---

### I3. TGI（Text Generation Inference） — 🟡 HuggingFace 出品

- **仓库**：https://github.com/huggingface/text-generation-inference
- **特点**：HF 生态深度集成、Rust 写 router + Python 写 worker、flash-attention 早期采用者
- **现状**：被 vLLM/SGLang 在性能上反超，但 HF Inference Endpoint 仍用，生态稳定
- **阅读价值**：学 Rust + Python 混合系统设计
- **一句话**：HF 生态用户值得读；新项目优先看 vLLM/SGLang。

---

## 三、训练框架层（T1–T5）

### T1. Megatron-LM / Megatron-Core — 🟢 NVIDIA 出品，并行范式定义者

- **仓库**：https://github.com/NVIDIA/Megatron-LM （应用层）｜ https://github.com/NVIDIA/Megatron-Core （核心库）
- **论文**（必读）：
  - [Megatron-LM](https://arxiv.org/abs/1909.08053)（TP，2019）
  - [Efficient Large-Scale Language Model Training](https://arxiv.org/abs/2104.04473)（PP + interleaved）
  - [Sequence Parallelism](https://arxiv.org/abs/2205.05198)
- **核心**：**Tensor Parallel（TP）/ Pipeline Parallel（PP）/ Data Parallel（DP）/ Sequence Parallel（SP）的工业级实现范式**。所有大模型训练框架（DeepSpeed/FSDP/数百个 LLM 训练脚本）都参考 Megatron。
- **源码关键文件**：
  ```
  megatron/core/
  ├── tensor_parallel/        ← ① TP（column-parallel / row-parallel）
  ├── pipeline_parallel/      ← ② PP（含 interleaved schedule）
  ├── transformer/            ← ③ Transformer 层（并行版本）
  ├── parallel_state.py       ← ④ 全局并行拓扑
  ├── datasets/               ← ⑤ 数据并行加载
  └── optimizers/             ← ⑥ 分布式优化器
  ```
- **对应「02 系统课」**：`02-C3 6.5840 分布式` + `02-C7 15-418 并行` + `02-C9 6.172 性能`。
- **一句话**：想理解"10K GPU 训练万亿参数"的工程，Megatron 是绕不开的原典。

### T2. DeepSpeed — 🟢 微软出品，ZeRO 的发明者

- **仓库**：https://github.com/microsoft/DeepSpeed
- **论文**（必读）：[ZeRO: Memory Optimizations Toward Training Trillion Parameter Models](https://arxiv.org/abs/1910.02054)（SC 2020）
- **核心**：
  - **ZeRO-1/2/3**：把 optimizer state / gradient / parameter 分散到所有 GPU，渐进消除冗余
  - **ZeRO-Offload / ZeRO-Infinity**：卸载到 CPU 内存 / NVMe
  - **Pipeline Parallelism**（PipeDream-Flush）
  - **MoE 训练**、**LongContext**（Sequence360K）、**QLoRA 训练**
- **源码关键文件**：
  ```
  deepspeed/runtime/
  ├── engine.py               ← ① 主引擎
  ├── zero/                   ← ② ZeRO-1/2/3 实现（核心）
  │   ├── stage1.py / stage2.py / stage3.py
  │   └── offload/            ← ③ 卸载到 CPU/NVMe
  ├── pipe/                   ← ④ Pipeline Parallelism
  ├── activation_checkpointing/
  └── ...
  ```
- **对应「02 系统课」**：`02-C3 6.5840` + `02-C4 6.1810 OS`（内存层级 + 卸载）+ `02-C7 15-418`。
- **一句话**：显存不够想训大模型，DeepSpeed ZeRO 是默认答案；想理解"训练显存怎么算"，读 ZeRO 论文。

### T3. Unsloth — 🟢 高效微调加速器

- **仓库**：https://github.com/unslothai/unsloth
- **核心**：手写 **Triton kernel** + 算子融合 + 手动 autograd，**比 HF Trainer 快 2-5x，省 60%+ 显存**，单卡 LoRA 微调的事实标准
- **特点**：低门槛（一行代码）、支持 Llama / Qwen / Mistral / Gemma / DeepSeek 全家
- **阅读价值**：学"如何手写 Triton kernel 加速训练"——比 FlashAttention 简单，是入门 Triton 的好材料
- **对应「02 系统课」**：`02-K2 Triton` + `讲透微调`。
- **一句话**：想做 LoRA 微调、又想榨干单卡性能，Unsloth 是首选。

### T4. Axolotl — 🟢 配置驱动微调料

- **仓库**：https://github.com/axolotl-ai-cloud/axolotl
- **核心**：YAML 配置 → 一行命令完成预训练 / 微调（LoRA/QLoRA/全参/DPO/GRPO）
- **价值**：把 Unsloth/DeepSpeed/PEFT 包装成易用工具，是中小团队微调首选
- **一句话**：不想研究底层框架、想快速微调，用 Axolotl。

### T5. verl / AReaL / Miles — 🟢 RL 后端新生代

- **verl**（火山引擎）：https://github.com/volcengine/verl —— 字节 / 火山出品，国产 RLHF/GRPO 训练框架
- **AReaL**（蚂蚁）：https://github.com/inclusionAI/AReaL
- **Miles**（RadixArk）：和 SGLang 深度协作
- **共同特点**：用 SGLang/vLLM 做 rollout，**异步** RL 训练（actor/learner/reward 解耦）
- **价值**：DeepSeek-R1 / Kimi 这一代 reasoning 模型的训练后端，是 2025-2026 最热方向
- **对应**：`01-CS285 Spring 2026 LLM RL` + `讲透微调`（RLHF/DPO/GRPO 部分）。
- **一句话**：想做下一个 reasoning 模型，verl + SGLang 是工业级 RL 训练栈。

---

## 四、分布式调度层（D1–D3）

### D1. Ray — 🟢 分布式 AI 计算引擎

> **联网核对（2026-08-03）**：`ray-project/ray`，43.4k stars / 7.9k forks / **31,231 commits**（极度活跃）。由 Anyscale 维护。

- **仓库**：https://github.com/ray-project/ray
- **文档**：https://docs.ray.io ｜ **论文**：[Ray](https://arxiv.org/abs/1712.05889)（OSDI 2018）
- **核心抽象**：
  - **Task**：无状态函数，集群里执行
  - **Actor**：有状态 worker 进程
  - **Object**：跨进程共享的不可变对象（Object Store）
- **AI Libraries**：
  - **Ray Data**：分布式数据集
  - **Ray Train**：分布式训练
  - **Ray Tune**：超参搜索
  - **RLlib**：分布式 RL（生产级）
  - **Ray Serve**：模型服务
- **源码关键文件**：
  ```
  src/ray/
  ├── raylet/                  ← ① C++ 写的核心调度器（raylet）
  ├── core_worker/             ← ② worker 进程核心
  └── ...
  python/ray/
  ├── serve/                   ← ③ Ray Serve（生产服务）
  ├── train/                   ← ④ 分布式训练
  ├── tune/                    ← ⑤ 超参搜索
  └── rllib/                   ← ⑥ RLlib（大型 RL 库）
  ```
- **阅读路径**：先看 Ray Core（task/actor/object 抽象）→ 再看 Serve/Train 选一个深入。
- **对应「02 系统课」**：`02-C3 6.5840 分布式`（task/actor 抽象）+ `02-C4 6.1810 OS`（进程/对象）+ `02-C15 15-440`。
- **一句话**：从笔记本到集群"同一份代码"，Ray 是 AI 时代的 Spark。

### D2. Slurm — 🟡 HPC 调度事实标准

- **官网**：https://slurm.schedmd.com/
- **核心**：HPC 集群作业调度，几乎所有 GPU 训练集群（超算/学术/大厂内部）都跑 Slurm
- **学习要点**：会写 `sbatch` 脚本、会 `salloc` / `srun` / `sinfo` / `squeue` / `scancel`
- **对应「讲透」系列**：未来 `讲透分布式AI系统` 的运维层
- **一句话**：搞大模型训练，Slurm 是和 Kubernetes 平行的另一半世界（HPC 圈用 Slurm，云原生圈用 K8s）。

### D3. Kubernetes + KubeRay — 🟢 云原生 AI

- **K8s**：https://kubernetes.io/
- **KubeRay**：https://github.com/ray-project/kuberay —— 在 K8s 上跑 Ray
- **其他 AI on K8s**：Volcano（批调度）、Kueue（队列）、NVIDIA GPU Operator
- **一句话**：云厂商（AWS/GCP/Azure/阿里云）的托管 AI 训练，多半是 K8s + GPU Operator + KubeRay 这套。

---

## 五、底层算子层（K1–K4）

### K1. FlashAttention — 🟢 IO-aware attention 范式

- **仓库**：https://github.com/Dao-AILab/flash-attention
- **论文**（必读三连）：
  - [FlashAttention: Fast and Memory-Efficient Exact Attention](https://arxiv.org/abs/2205.14135)（NeurIPS 2022）
  - [FlashAttention-2: Faster Attention with Better Parallelism](https://arxiv.org/abs/2307.08691)（2023）
  - [FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision](https://arxiv.org/abs/2407.08608)（2024，H100 专用）
- **核心思想**：**attention 慢不是算力不够，是 IO 浪费**——通过 tiling + recomputation 把 HBM 读写降到最小
- **源码关键文件**：
  ```
  csrc/flash_attn/             ← CUDA C++ kernels（CUTLASS 模板）
  flash_attn/                  ← Python 接口
  ```
- **对应「02 系统课」**：`02-C7 15-418 并行`（GPU 内存层级）+ `02-C8 15-213 CSAPP`（缓存）+ `02-C9 6.172 性能` + `讲透注意力`。
- **一句话**：FlashAttention 论文是 2022 年后所有 attention 优化的源头，必读。

### K2. Triton — 🟢 Python 写 GPU kernel

> **联网核对（2026-08-03）**：**重要发现**——已从 `openai/triton` **迁移到 `triton-lang/triton`**（社区化治理）。19.8k stars / 3.1k forks / 6,640 commits。**Version 2.0 已发布**，后端改用 **MLIR** 重写。Triton Conference 2025 在 Microsoft Silicon Valley 举办（一年一度）。

- **仓库**：https://github.com/triton-lang/triton ｜ **文档**：https://triton-lang.org
- **论文**：[Triton: An Intermediate Language and Compiler for Tiled Neural Network Computations](https://www.eecs.harvard.edu/~htk/publication/2019-mapl-tillet-kung-cox.pdf)（MAPL 2019）
- **核心**：用 Python（`@triton.jit`）写 GPU kernel，性能接近手写 CUDA，但生产力高 10x。FlashAttention v2、vLLM、PyTorch 2.0 `torch.compile` 都用它。
- **学习资源**：
  - [Triton Puzzles](https://github.com/srush/Triton-Puzzles)（无需 GPU，纯 interpreter 跑，强烈推荐入门）
  - Triton Conference 2023/2024/2025 全套录像 YouTube
- **源码关键文件**：
  ```
  python/triton/
  ├── runtime/jit.py          ← ① @triton.jit 装饰器（入口）
  ├── language/               ← ② tl DSL（tl.dot / tl.load / tl.store…）
  └── tools/
  lib/
  ├── Dialect/Triton/         ← ③ MLIR dialect（2.0 后端核心）
  ├── Dialect/TritonGPU/
  └── Conversion/             ← ④ IR 转换 pass
  include/triton/             ← ⑤ C++ 头文件
  ```
- **阅读路径**：先做 Triton Puzzles 建立直觉 → 读 `python/triton/language/`（看 tl DSL）→ 读官方 tutorial → 看 FlashAttention 的 Triton 实现版本。
- **对应「02 系统课」**：`02-C7 15-418 并行` + `02-C8 15-213 CSAPP`（缓存/tiling）+ `讲透GPU与系统级` + `讲透优化器`。
- **一句话**：2025 年想给 AI 写高性能 kernel，Triton 是唯一选择（CUDA 太底层，PyTorch 太高）。

### K3. CUTLASS — 🟢 NVIDIA CUDA GEMM 模板库

- **仓库**：https://github.com/NVIDIA/cutlass
- **核心**：NVIDIA 官方的高性能 GEMM 模板库，C++ 模板元编程极致，是 cuBLAS / TensorRT / FlashAttention 的底层
- **学习难度**：高（C++ 模板 + CUDA + GPU 架构）
- **价值**：想榨干 H100/B100 的 Tensor Core，必须懂 CUTLASS
- **对应「02 系统课」**：`02-C7 15-418 并行` + `02-C9 6.172 性能` + `02-C14 Onur Mutlu 架构`。
- **一句话**：CUTLASS 是 CUDA 编程的"研究生教材"，不读它写不出顶级 GEMM。

### K4. FlashInfer / xFormers — 🟢 attention 变体工具箱

- **FlashInfer**（MLC）：https://github.com/flashinfer-ai/flashinfer —— 长上下文 / KV cache 优化 / batch attention
- **xFormers**（Meta）：https://github.com/facebookresearch/xformers —— memory-efficient attention + 各类变体
- **价值**：当 FlashAttention 不够用（长上下文 / 稀疏 attention / 共享 KV），用这俩
- **对应**：`讲透注意力` + `讲透KV Cache`。
- **一句话**：FlashAttention 是基础，FlashInfer/xFormers 是补充。

---

## 六、通信层（C1–C2）

### C1. NCCL — 🟡 NVIDIA GPU 集合通信库

- **官网**：https://github.com/NVIDIA/nccl
- **核心**：NVIDIA GPU 集合通信（AllReduce / AllGather / Broadcast / ReduceScatter）的事实标准，PyTorch / Megatron / DeepSpeed 全用它
- **关键算法**：Ring AllReduce（树 + 环混合）、NVLink + InfiniBand 感知
- **学习难度**：高（C + CUDA + 网络拓扑）
- **对应「02 系统课」**：`02-C3 6.5840 分布式` + `02-C6 CS144 网络` + `02-C7 15-418 并行`。
- **一句话**：所有"多卡训练通信怎么走"的问题，根在 NCCL。

### C2. Gloo — 🟡 PyTorch 默认 CPU 后端

- **仓库**：https://github.com/facebookincubator/gloo
- **核心**：Facebook 出的 CPU 集合通信库，PyTorch 默认后端（CPU 训练 / 多机协调）
- **价值**：调试分布式训练的好工具，但 GPU 训练用 NCCL
- **一句话**：CPU 分布式用 Gloo，GPU 分布式用 NCCL。

---

## 七、全栈底座（U1–U2）

### U1. CUDA Toolkit — 🟢 NVIDIA GPU 编程模型

- **官网**：https://developer.nvidia.com/cuda-toolkit
- **学习**：
  - 《Programming Massively Parallel Processors》（PMPP，第 4 版 2022）—— CUDA 教材 No.1
  - NVIDIA 官方 CUDA C++ Programming Guide
  - NVIDIA 的 [CUDA Lecture Series](https://www.youtube.com/playlist?list=PLGs0VKk2DiYw74-Io1Lp4TuYf3wxY_xL_)（YouTube）
- **核心概念**：grid/block/thread → shared memory → warp → coalesced access → Tensor Core
- **对应「02 系统课」**：`02-C7 15-418 并行` + `02-C14 Onur Mutlu 架构` + `讲透GPU与系统级`。
- **一句话**：所有 GPU 编程（Triton/CUTLASS/cuDNN）下面都是 CUDA，不懂 CUDA 走不远。

### U2. PyTorch — 🟢 深度学习框架事实标准

- **仓库**：https://github.com/pytorch/pytorch
- **核心**：
  - **eager mode**：动态图（易用）
  - **torch.compile**（PyTorch 2.0+）：JIT 编译，用 Triton 生成 kernel
  - **FSDP**（Fully Sharded Data Parallel）：原生 ZeRO-3 等价物
  - **DTensor / DeviceMesh**（2024+）：新一代分布式抽象
  - **Custom Extensions**：`torch.utils.cpp_extension` 加载 C++/CUDA
- **源码关键文件**：
  ```
  torch/
  ├── _dynamo/                ← ① torch.compile 的 Python 部分
  ├── inductor/               ← ② codegen（生成 Triton kernel）
  ├── distributed/            ← ③ 分布式（DDP/FSDP/RPC）
  │   ├── fsdp/
  │   └── device_mesh/        ← ④ DTensor / DeviceMesh（新）
  ├── nn/                     ← ⑤ 模块定义
  ├── autograd/               ← ⑥ 自动微分
  └── csrc/                   ← ⑦ C++ 核心
  ```
- **对应「讲透」系列**：`讲透PyTorch` + `讲透反向传播`（autograd）+ `讲透优化器`。
- **一句话**：所有训练框架（Megatron/DeepSpeed/Unsloth）都建在 PyTorch 之上，不懂 PyTorch 内部就改不动上层。

---

## 八、源码阅读方法论（怎么真的读进去）

> 公开课（02）让你"懂概念"，开源项目（03）让你"会工程"——但读源码和读书完全不同。下面是验证过的方法论。

### 1. **从入口倒推**（最高效）
不要从 `main.py` 顺着读，而是问自己：**"我运行 `python -m vllm.entrypoints.openai.api_server`，第一个请求进来后，发生了什么？"** 然后从 API endpoint → engine → scheduler → worker 倒着追。

### 2. **绑定一篇论文**
读 vLLM 必须先读 PagedAttention 论文，读 SGLang 必须先读 RadixAttention 论文。论文给你"地图"，源码是"实地"，没地图会迷路。

### 3. **配 `02 系统课`一起读**
| 想读的项目 | 必看 02 的课 |
|----------|-----------|
| vLLM scheduler / block_manager | 02-C3 6.5840 + 02-C4 6.1810 OS |
| SGLang radix_cache | 02-M1 Strang 18.06（树结构）+ 02-C3 6.5840 |
| Megatron TP/PP | 02-C3 6.5840 + 02-C7 15-418 |
| DeepSpeed ZeRO | 02-C4 6.1810 OS（内存） + 02-C3 6.5840 |
| FlashAttention | 02-C7 15-418 + 02-C8 15-213 CSAPP |
| Triton | 02-C7 15-418 + 02-C9 6.172 性能 |
| Ray | 02-C3 6.5840 + 02-C15 15-440 |
| NCCL | 02-C3 6.5840 + 02-C6 CS144 |

### 4. **改一个最小 patch**
读完不等于会，**提一个最小 PR** 才是真懂。建议从「修文档 / 修 typo / 加测试」开始，进到「加一个 config 选项」，最后「改一个 kernel」。每个项目都有 `good first issue` 标签。

### 5. **跑 benchmark + 看 trace**
用 `nvidia-smi` + `py-spy` + `nsight systems` 跑一遍，看时间花在哪。**性能 profile 是源码阅读的最好向导**——哪慢就去看哪。

---

## 九、维护说明

- **下次重核对建议**：AI Infra 迭代极快，建议**每 3 个月**核对一次 stars/commits/重大版本（vLLM/SGLang 周级提交，Triton 季度发版）。
- **易变项**：
  - vLLM / SGLang：几乎每周都有新特性，本清单只标"核心创新"，新特性看官方 blog
  - Triton：2.0 后端在持续重写，MLIR dialect 可能有调整
  - 训练框架：verl/AReaL/Miles 是 2025-2026 新生代，格局未稳
- **本清单口径**：只收"全球头部 AI 公司生产在用"的项目；个人玩具 / 已废弃（如早期的 DeepSpeed-MII / 有些 fork）不收。
- **核对日志**：
  - **2026-08-03（第二轮·GitHub API 全量核 18 项目）**：用本地 firecrawl self-host + GitHub API（`api.github.com/repos/...`）批量核所有 18 项目的 stars/last push/topics。**关键发现**：
    - **排名**（按 stars）：PyTorch 10.2w > vLLM 8.8w > Unsloth 6.9w > DeepSpeed 4.3w ≈ Ray 4.3w > SGLang 3.1w > flash-attention 2.5w > **verl 2.3w** > Triton 2.0w > Megatron-LM 1.7w > Axolotl 1.2w ≈ xFormers 1.1w ≈ TGI 1.1w > CUTLASS 1.0w > FlashInfer 6.1k > NCCL 4.9k > Slurm 4.2k > KubeRay 2.6k。
    - **🆕 SGLang 多模态化**：topics 已含 `diffusion / vlm / wan / minimax`，从纯 LLM 推理引擎扩到**多模态推理引擎**。
    - **🆕 vLLM 全模型/全硬件覆盖**：topics 含 `deepseek-v3 / kimi / qwen3 / gpt-oss / blackwell / tpu`。
    - **🔴 TGI 疑似停滞**：最后 push 是 **2026-03-21**（4 个多月未动），可能被 vLLM/SGLang 边缘化，状态从 🟡 降为 🔴。
    - **🆕 verl（字节 HybridFlow）22.8k stars**——**超过 OpenRLHF(9.8k) 2 倍**，是 2025–2026 RL 后端实际上的"开源一哥"。
    - **🆕 AReaL 5.6k stars**（inclusionAI），自我描述 "RL Bridge for **LLM-based Agent** Applications"——RL + Agent 桥接框架，对应 02 后训练专题里"Agentic RL 趋势"。
    - 所有项目 last push 都是 2026-08-03 当天或前 2 周内（除 TGI 4 个月、xFormers 7月中），整体生态极活跃。
  - 2026-08-03（首版·四大件核对）：实抓 vLLM（88.1k stars/19460 commits）/ SGLang（31.1k stars/15991 commits，40万+ GPU）/ Ray（43.4k stars/31231 commits）/ Triton（**已迁到 triton-lang 组织**，19.8k stars，2.0 用 MLIR 重写）。其他基于稳定知识。

---

📌 **下一步**

1. **挑一个项目深入**：告诉我你的目标（推理加速 / 训练框架 / RL 后端 / 算子开发），我帮你选一个项目 + 配 02 的系统课 + 给出"7 天读完核心源码"的具体路径。
2. **想做实战**？我可以帮你写一个最小可跑的 demo（比如用 vLLM 跑本地模型 + 加自定义 attention kernel）。
3. **核对更新**？某个项目出了大版本（如 Triton 3.0 / SGLang v2），告诉我，我刷新本清单。
4. **回到学习主线**？继续看 01/02 的课，或者开始本仓库的「讲透 XXX」系列精读。
