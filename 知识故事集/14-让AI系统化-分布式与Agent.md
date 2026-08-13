# 14 · 让 AI 系统化：分布式 + Agent + 世界模型（2018-2026）

> **时间**：2018-2026，8 年
> **核心冲突**：单卡跑不动大模型 / LLM 不会"动手" / LLM 不懂"世界"。
> **嵌入概念**：DDP、FSDP、ZeRO、Tensor Parallel、Agent、世界模型

---

## 🎬 故事

### 2018 · 大模型训练的难题

GPT-2（2019）1.5B 参数。fp32 = 6GB 权重 + 18GB 优化器 + 18GB 梯度 = **42GB 训练显存**。

一张 V100（32GB）装不下。怎么办？

### 路径 A：数据并行（Data Parallel）

最简单的 idea：**多卡各训一份模型**。

```
GPU 0: 模型副本 + 数据 batch 0
GPU 1: 模型副本 + 数据 batch 1
GPU 2: 模型副本 + 数据 batch 2
GPU 3: 模型副本 + 数据 batch 3
```

每张卡 forward + backward，**梯度 all-reduce 同步**。

**DDP**（DistributedDataParallel）：PyTorch 标准。

**问题**：每张卡要装下**整个模型**。175B 装不下。

### 路径 B：模型并行

**Tensor Parallel（TP）**：把每一层的矩阵切到多卡。
```
单 GPU:  Y = X · W（W 是 d×d）
4 GPU TP: Y = X · [W1 | W2 | W3 | W4]，每卡算一部分
```

**Pipeline Parallel（PP）**：把不同层分到不同卡。
```
GPU 0: layer 1-10
GPU 1: layer 11-20
GPU 2: layer 21-30
GPU 3: layer 31-40
```

数据像流水线一样流过。

### 2019 · Megatron-LM

NVIDIA 发 **Megatron-LM**：TP + DP 混合。训 GPT-like 模型。

### 2020 · DeepSpeed ZeRO

Microsoft 发 **DeepSpeed ZeRO**（Zero Redundancy Optimizer）：

**3 阶段**：
- **ZeRO-1**：把优化器状态切到多卡
- **ZeRO-2**：+ 把梯度切到多卡
- **ZeRO-3**：+ 把模型权重切到多卡

**ZeRO-3 训 1T 参数**——比单卡理论极限多 100 倍。

### 2022 · FSDP（PyTorch 原生）

**FSDP**（Fully Sharded Data Parallel）= PyTorch 版的 ZeRO-3。

2022 后 **FSDP 成为 PyTorch 标准**。Llama / Qwen / DeepSeek 都用。

### 训练大模型 = 多种并行组合

2024+ 训 100B+ 模型 = **3D 并行**：
- Data Parallel（DDP / FSDP）
- Tensor Parallel（TP）
- Pipeline Parallel（PP）

加上 **Sequence Parallel** / **Context Parallel**（处理超长上下文）。

**这是大模型训练的工程艺术**——每个 LLM 公司都有自己的"配方"。

### 2023+ · Agent 时代

LLM 训好了，但 LLM 是**只说不做**的。怎么让它**动手**？

**Agent** = LLM + 工具 + 多轮规划。

#### 2023 · 工具调用（Function Calling）

OpenAI / Anthropic / Google 都加 **function calling**——LLM 可以输出 "调用工具 X" 格式。

#### 2023 · ReAct 模式

**ReAct**（Reasoning + Acting）：
1. LLM 思考"我该做什么"
2. 调用工具
3. 看工具结果
4. 继续思考
... 直到完成

#### 2024 · 多 Agent

**CrewAI / AutoGen / LangGraph**：多个 Agent 协作。每个 Agent 有角色（研究员 / 程序员 / 审查员）。

#### 2024 · Devin / Claude Computer Use

**Devin**（Cognition Labs 2024）：号称"第一个 AI 软件工程师"。
**Claude Computer Use**（Anthropic 2024-10）：Claude 可以**直接操作电脑**——鼠标键盘 + 浏览器。

### Agent 的核心难题

但 Agent 仍然有 3 大难题：

1. **可靠性**：LLM 输出不稳定，Agent 经常跑偏
2. **长程规划**：任务超过 20 步就开始迷失
3. **评估**：怎么评估 Agent？

### 2024 · 世界模型（World Model）

**LeCun** 2022 提出 **JEPA**（Joint Embedding Predictive Architecture）：
- 不预测像素，预测**抽象表征**
- 学世界的"内部模型"

LeCun 的 thesis：**LLM 不是 AGI 路径，世界模型才是**。

### 2024 · Sora 作为世界模拟器

OpenAI Sora（2024-02）：
- 生成 1 分钟视频
- **学到了世界物理规律**（球弹起 / 玻璃碎 / 光影）
- OpenAI 称之为 "data-driven physical world simulator"

**意义**：视频生成 = **世界模型的早期形态**。

### 2024+ · World Models 路线

- **Genie**（DeepMind 2024）：可玩的游戏世界模型
- **Genie 2**（DeepMind 2024-12）：3D 世界模型
- **Sora**（OpenAI）
- **Dreamer V3**（Hafner）：RL + 世界模型

**世界模型是 AGI 的下一步候选**——但理论还不成熟。

---

## 🧠 核心概念

- **DDP**（DistributedDataParallel）：每卡装整个模型，并行训数据。
- **FSDP**（Fully Sharded Data Parallel）：ZeRO-3 思想，每卡只装一部分模型。
- **TP**（Tensor Parallel）：层内矩阵切到多卡。
- **PP**（Pipeline Parallel）：层间切到多卡。
- **ZeRO**（Microsoft DeepSpeed）：3 阶段优化器/梯度/权重切分。
- **Agent**：LLM + 工具 + 多轮规划。
- **ReAct**：Reasoning + Acting 模式。
- **Function Calling**：LLM 输出结构化工具调用。
- **世界模型**：学世界的内部模型。AGI 候选路径。

## 🎨 类比

- **DDP** = 4 个厨师**做同一道菜的不同份**——每个厨师有自己的厨房和全套菜谱
- **TP** = 4 个厨师**一起做一道菜**——每人负责切不同食材
- **PP** = 流水线**4 道工序**——菜从工序 1 流到工序 4
- **ZeRO / FSDP** = 4 个厨师**共用一套厨房工具**——每人保管一部分（不重复）
- **3D 并行** = 同时用 DDP + TP + PP——所有方法混用
- **Agent** = 一个有 LLM 大脑 + 工具双手的实习生
- **ReAct** = 实习生"想一步做一步"的工作方式
- **多 Agent** = 一个团队，各司其职
- **世界模型** = LLM 之外，AI 还要学**模拟世界的能力**

## 💡 反直觉发现

1. **大模型训练是工程艺术，不是算法**：每个 LLM 公司的"训练配方"都是秘密。**算力 + 工程决定一切**。

2. **ZeRO-3 让模型显存少 100 倍**：经典数据并行浪费 4N 倍冗余。ZeRO 切分所有冗余。

3. **Agent 仍然不可靠**：2024 Devin demo 是预录的。**生产 Agent 仍然容易跑偏**。

4. **世界模型路线还没赢**：LeCun JEPA 还没出大产品。LLM 路线仍在主流。**但 AGI 可能需要世界模型**。

5. **Claude Computer Use 是新范式**：2024-10 后，AI 可以直接操作电脑。**未来 5 年的 agent 形态可能基于此**。

6. **视频生成 ≠ 世界模型**：Sora 学到了"看起来对"的物理，但**不理解因果**。**真世界模型要能预测干预后果**。

## 🛠️ 我该深挖什么

### work4ai 系列
- [`../讲透分布式AI系统/`](../讲透分布式AI系统/)：DDP / FSDP / ZeRO / TP
- [`../讲透GPU与系统级/`](../讲透GPU与系统级/)：CUDA / FlashAttention / NCCL
- [`../讲透Agent/`](../讲透Agent/)：Agent 框架 / ReAct / 多 Agent
- [`../讲透世界模型/`](../讲透世界模型/)：JEPA / Sora / Dreamer（博士级）
- [`../讲透形式化验证/`](../讲透形式化验证/)：seL4 → Lean4（与 Agent / 系统结合）

### 必读
- **Shoeybi et al. 2019 "Megatron-LM"**
- **Rajbhandari et al. 2020 "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models"**
- **Yao et al. 2022 "ReAct: Synergizing Reasoning and Acting"**
- **LeCun 2022 "A Path Towards Autonomous Machine Intelligence"**（JEPA）

### 实验
```python
# 1. 用 PyTorch DDP 在 2 张 GPU 训一个小模型
# 2. 用 transformers + accelerate 跑 FSDP
# 3. 用 LangChain / LangGraph 搭一个 ReAct agent
# 4. 跑 Dreamer V3 on Atari（学世界模型基础）
```

---

## 🔗 下一篇

下一篇：[**15 · 你的下一步：成为顶级专家**（2026-2033）](15-你的下一步-成为顶级专家.md)——终章，整合前 14 个故事 + 你的英雄之旅。

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**单 LLM → 多 GPU 训练 → Agent → 世界模型。这是 AGI 路径上未完成的故事。**
