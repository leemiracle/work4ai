# CS349F: Fabric Architectures for AI Systems

> Stanford University | 研究生 | CS349 系列 (主题轮换)
> Instructors: **Balaji Prabhakar** (网络/数据中心专家) + **Mendel Rosenblum** (VMware 创始人)
> Prerequisites: CS144 (网络) + CS240 (分布式) 推荐 / 先修 CS349E
> Difficulty: ⭐⭐⭐⭐⭐ (硬件 + 网络 + 系统三层)

---

## 📚 定位

**"AI 数据中心网络"专题课**。CS349E 讲 GPU 内部 / 推理引擎,CS349F 讲 **GPU 之间怎么连**——支撑 LLM 训练 / 推理的**网络架构层**:InfiniBand、NVLink、Fat-Tree、RDMA、Collective 通信。

讲师组合极强:Prabhakar (拥塞控制权威) + Rosenblum (VMware 创始人,系统视角)。这是 **2024-2025 最稀缺方向**:全球能讲清楚"为什么 GPT-4 训练需要 25000 张 H100 + Fat-Tree + InfiniBand"的人不超过 100 个。

---

## 📅 完整模块(推测,基于讲师方向)

### Week 1: AI 工作负载的网络特征
- 训练通信模式:AllReduce / AllGather / ReduceScatter;推理:KV cache 跨节点传输
- 通信 / 计算 ratio (Amdahl 上界);案例:GPT-4 训练 25k GPU 网络预算

### Week 2: GPU 互联 — NVLink & NVSwitch
- NVLink 1-5 演进 (NVLink 5: 1.8 TB/s);NVSwitch 拓扑;Why NVLink kills PCIe

### Week 3: InfiniBand 基础
- IB vs RoCE vs Cray Slingshot;RDMA 原理 (kernel bypass);IB Verbs API

### Week 4: Topology — Fat-Tree & Beyond
- Clos / Fat-Tree 拓扑数学;oversubscription ratio 设计
- 案例:Meta Grand Teton / NVIDIA DGX SuperPOD;Rail-optimized topology

### Week 5: Collective Communication
- Ring AllReduce (Baidu) vs Tree AllReduce (NCCL default);Recursive Doubling
- 🔴 **NCCL** (NVIDIA Collective Communication Library) 内部机制

### Week 6: 拥塞控制
- TCP-BDP / DCQCN (RoCE) / IRN (InfiniBand, Prabhakar);PFC 与 lossless 网络;Incast 问题

### Week 7: 大规模训练案例研究
- GPT-3/4 / Llama 3 16k GPU 集群架构;Megatron + DeepSpeed 通信模式;故障恢复

### Week 8: 推理集群网络
- KV cache 跨 GPU / 节点共享;Disaggregated inference (DeepSeek);vLLM / SGLang 网络假设

### Week 9-10: 新硬件 / 未来
- Ultra Ethernet Consortium (UEC);Cerebras Wafer-Scale (片内互联);Optical switches (Google Jupiter)
- 共显存 (CXL);Optical I/O (Ayar Labs);Chiplet 与先进封装

---

## 🧮 核心概念

### AllReduce 通信复杂度
- **Ring AllReduce**: bandwidth = $2(N-1)/N \cdot S$,延迟 $2(N-1) \cdot \alpha$
- 关键洞察:**通信量与 N 无关**(只与参数大小 S 有关)

### Fat-Tree 拓扑
```
spine → leaf → ToR → server (含 8 GPU)
```
- $k$-ary Fat-Tree: $\frac{k^3}{4}$ servers;1:1 不超额订阅 = 上行 = 下行带宽

### NCCL Ring vs Tree
- **Ring**: 带宽最优(瓶颈 = 单链路),延迟 ∝ N
- **Tree**: 延迟最优(log N),带宽受限(根节点瓶颈)
- NCCL 混合: 小消息 Tree,大消息 Ring

---

## 💻 项目代码

📁 `topic4-mlsys/` (与 CS349E 同目录)。模拟作业方向:AllReduce 时序模拟 / Fat-Tree 拓扑生成 + 路由 / RDMA vs TCP 延迟对比。NCCL tests: `git clone https://github.com/NVIDIA/nccl-tests; mpirun -np 8 ./all_reduce_perf -b 8 -e 1G -f 2 -g 1`。

---

## 📊 关键论文

### 🔴 P0
1. **Sergeev & Del Balso 2018** "Horovod" — Ring AllReduce 工业实现
2. **NVIDIA NCCL** 官方文档与 paper 系列
3. **Narayanan et al. 2021** "Efficient Large-Scale LLM Training" (Megatron + 3D parallelism)
4. **Lian et al. 2017** "Can Decentralized Algorithms Outperform Centralized?"

### 🟡 P1
5. **Patel et al. 2019** "IRN" (Prabhakar 团队)
6. **Zhu et al. 2019** "DCQCN" (RoCE 拥塞控制)
7. **Meta Engineering Blog** "Building Meta's GenAI Infrastructure" (2024)
8. **Google Jupiter** (Singh et al. 2015)
9. **Ultra Ethernet Consortium** 白皮书 (2024)

---

## 🎯 学习路径

| 角色 | 推荐 |
|------|------|
| **ML infra / training eng** | CS349E → **CS349F (必)** → CS349H |
| **网络工程师转 AI** | CS144 → CS349F (你的甜区) |
| **硬件 / 芯片工程师** | EE373 + CS349F + CS349H |
| **PhD 候选** | CS349F 是 paper idea 富矿 |

---

## 💡 反思

**优势**: 极度稀缺(全球讲 AI 网络的课 < 5 门);讲师背景无敌;就业黄金(NVIDIA / Meta / Google / Anthropic infra 团队都缺)。

**局限**: 不公开(锁在 Stanford 校内);硬件依赖强(没 H100 / IB 集群难实操);迭代快(UEC / CXL 每季度变)。

---

## 🚀 扩展

完成 CS349F 后推荐: **CS349E** (推理引擎) → **CS349H** (编译栈) → **CS240** (分布式理论);实习目标 NVIDIA Networking / Meta Infra / Google Borg / Anthropic Compute。

---

**最后更新**: 2026-08-11
**对应代码**: `topic4-mlsys/` (与 CS349E 共享)
