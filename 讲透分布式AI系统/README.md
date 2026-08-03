# 讲透分布式 AI 系统

> 单卡装不下大模型——Llama-70B 训练要 ~840GB 显存（权重+梯度+optimizer state），H100 单卡只有 80GB。**分布式不是"锦上添花"，是"训练大模型的物理必需"**。本系列从显存账讲到 ZeRO/TP/PP，把"万亿参数怎么在万卡上训起来"的工程钻透。
>
> 配套：[`讲透公开课/02-6.5840 Spring 2026`](../讲透公开课/02-数理计算机神课清单.md)（分布式系统地基，Raft lab）+ [`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 Megatron/DeepSpeed/Ray

---

## 篇目

| # | 标题 | 状态 | 核心 |
|---|------|------|------|
| **00** | [为什么大模型必须分布式](./00-为什么必须分布式.md) | ✅ | 显存账、单卡瓶颈、四范式总览、通信代价 |
| **01** | 数据并行 DDP / FSDP | ✅ | DDP 原理、FSDP=ZeRO-3 的 PyTorch 原生版 |
| **02** | ZeRO 三阶段（DeepSpeed）| ✅ | 分 optimizer/gradient/parameter 的渐进消除冗余 |
| **03** | Tensor / Pipeline Parallel（Megatron）| ✅ | 层内切矩阵（TP）、层间切模型（PP）、interleaved |
| 04 | Ray 分布式调度 | 🟡 | Task/Actor/Object + Ray Train |
| 05 | 推理分布式（vLLM/SGLang TP+EP）| 🟡 | 配 [`讲透KV Cache`](../讲透KV Cache/) |
| 06 | 通信优化（NCCL / 计算通信重叠）| 🟡 | Ring AllReduce、NVLink/IB 拓扑 |

---

## 怎么用

- **想懂大模型怎么训**：00 → 01 → 02 → 03（数据并行 + ZeRO + 模型并行三主线）
- **想搞 AI Infra**：全部 + 配 [`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>)
- **想用 PyTorch FSDP 微调**：00 + 01（FSDP 是最实用的）
- **想读 Megatron 源码**：03 + 配 03 的 T1 条目

---

## 配套

- 课：[`讲透公开课/02-C3 6.5840`](../讲透公开课/02-数理计算机神课清单.md)（Raft lab，分布式地基）
- 系统：[`讲透公开课/02-C7 15-418`](../讲透公开课/02-数理计算机神课清单.md)（并行）+ [`讲透GPU与系统级`](../讲透GPU与系统级/)
- 源码：[`讲透公开课/03`](<../讲透公开课/03-AI Infra 源码导读清单.md>) 的 T1 Megatron / T2 DeepSpeed / D1 Ray
