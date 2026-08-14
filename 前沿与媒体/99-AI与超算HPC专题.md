# 前沿与媒体 · 99 - AI 与超算 / HPC 专题（v1.1 长尾）

> 姊妹：[`12-硬件`](./12-AI硬件与算力专题.md)｜ [`40-算力市场`](./40-AI算力市场与集群调度专题.md)。

---

## 一、全球超算 Top500

- **Top500.org**（半年榜）
- **Frontier（ORNL，2022-2024 No.1，1.2 exaFLOPS）**
- **Aurora（Argonne，2024+）**
- **El Capitan（LLNL，2024+）**
- **Fugaku（日本理研）**
- **LUMI（芬兰）**
- **中国：神威·海洋之光（Sunway）/ 天河 / 新一代神威**
- **欧盟 JUPITER（2024 起 AI 加速）**

## 二、AI 工作负载主导 HPC

- **传统 HPC**（CFD / 气象 / 核模拟 / 药物）
- **AI 工作负载**（训练 + 推理）— 占 HPC 越来越多
- **混合**：传统 + AI（如 AlphaFold + 物理）

## 三、HPC + AI 算法栈

| 层 | 工具 |
|---|---|
| **MPI** | 经典消息传递 |
| **OpenMP / CUDA** | 共享内存 / GPU |
| **Slurm / PBS / LSF** | 调度 |
| **NCCL / RCCL** | GPU 集合通信 |
| **PyTorch DDP + Slurm** | ML 集成 |
| **Megatron-LM / DeepSpeed / FSDP** | 大模型训练（已在 [`讲透公开课 03`](../讲透公开课/03-AI%20Infra%20源码导读清单.md)）|

## 四、AI for Science + HPC

- **AlphaFold / Boltz** + HPC（已在 [`15`](./15-AI%20for%20Science%20专题.md)）
- **气候建模 HPC**（已在 [`59`](./59-AI与可持续发展SDG气候专题.md)）
- **核聚变 HPC**
- **分子动力学 + AI**（OpenMM / DeepMD）

## 五、AI 时代 HPC 商业化

- **CoreWeave / Nebius**（已在 [`40`](./40-AI算力市场与集群调度专题.md)）
- **Cray（HPE）** 超算供应商
- **Lenovo / 浪潮 / 曙光 / 联想**（中文超算）
- **国家级算力中心**（中国"东数西算"，已在 [`24`](./24-AI地缘政治与产业政策专题.md)）

## 六、关键会议 / 标准

- **SC（Supercomputing Conference）** — HPC 第一大会
- **ISC（International Supercomputing Conference，德国）**
- **Hot Chips**（芯片架构）
- **TOP500 / Green500 / HPCG**

## 七、维护说明

- **2026-08-03 首版（长尾）**。

---

> 🔗 [`12-硬件`](./12-AI硬件与算力专题.md) ｜ [`40-算力`](./40-AI算力市场与集群调度专题.md) ｜ [`讲透公开课 03`](../讲透公开课/03-AI%20Infra%20源码导读清单.md)
