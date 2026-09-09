# 大语言模型核心词典

> 最后更新：2025-03 | 包含历史发展、经典论文、缺陷分析

---

## 📜 历史脉络总览

```
Timeline: 关键节点
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2017   Transformer诞生 - "Attention is All You Need"
  ↓
2018   BERT/GPT-1诞生 - 预训练时代开启
  ↓
2019   GPT-2 - "too dangerous to release" (1.5B参数)
  ↓
2020   GPT-3 - Few-shot learning惊艳世界 (175B)
  ↓
2021   Codex, CLIP - 多模态萌芽
  ↓
2022   ChatGPT - RLHF引爆全球
  ↓
2023   GPT-4, Claude 2, Llama 1 - 多模态+开源革命
  ↓
2024   Claude 3, Llama 3, Gemini 1.5, MoE爆发
  ↓
2025   推理优化、Agent、长上下文成为主流
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 1. 核心架构概念

### Transformer

**费曼解释**：想象你在读一本书，传统的模型像是从左到右逐字读，而Transformer可以同时"看到"整句话，并知道哪些词之间有联系。就像你读"小明喜欢苹果，他觉得它很甜"时，知道"它"指的是苹果。

**历史**：
- 2017年前：RNN/LSTM统治序列建模
- 2017：Google发表 "Attention is All You Need"
- 影响：完全改变了NLP，成为所有现代LLM的基础

**经典论文**：
- "Attention is All You Need" (Vaswani et al., 2017)
  - 核心观点：抛弃RNN/CNN，只用注意力机制
  - 贡献：Self-attention + Positional Encoding
  
**缺陷**：
1. **计算复杂度 O(n²)** - 序列长度平方级增长
2. **内存消耗大** - 长文本处理困难
3. **位置编码不完美** - 外推能力有限
4. **训练不稳定** - 需要careful initialization

**后续改进**：
- Sparse Attention (2018-2019)
- Longformer, BigBird (2020)
- Flash Attention (2022) - 算法优化，不改变复杂度但大幅加速
- Linear Attention (2019-2021)

---

### Self-Attention / Attention Mechanism

**费曼解释**：让每个词"看"所有其他词，决定它们之间的关系强度。就像开会时，你会注意某些人的发言，忽略其他人，根据相关性分配注意力。

**公式直觉**：
```
Attention(Q, K, V) = softmax(QK^T / √d) V
```
- Q (Query): 我要找什么
- K (Key): 每个词的标签
- V (Value): 每个词的内容
- softmax: 归一化权重

**历史发展**：
- 2014：Bahdanau Attention（用于机器翻译）
- 2015：Luong Attention
- 2017：Self-Attention（Transformer核心）

**经典论文**：
- "Neural Machine Translation by Jointly Learning to Align and Translate" (Bahdanau et al., 2014)
- "Effective Approaches to Attention-based Neural Machine Translation" (Luong et al., 2015)

**缺陷**：
1. **O(n²)复杂度** - 双重循环计算
2. **缺乏位置信息** - 需要额外的Positional Encoding
3. **对长距离依赖仍然困难** - 虽然比RNN好，但仍有局限

---

### Multi-Head Attention

**费曼解释**：不是从一个角度看问题，而是从多个角度同时看。就像分析一句话时，既看语法关系、又看语义关系、还看情感关系，最后综合起来。

**为什么需要**：
- 单个attention可能只关注某一方面
- 多个head可以学习不同的"关系模式"

**经典论文**：
- "Attention is All You Need" (2017) - 原始提出

**缺陷**：
1. **参数量大** - head数 × 单head参数
2. **有些head冗余** - 研究发现部分head可剪枝
3. **内存消耗** - 多个head并行计算

**改进**：
- Multi-Query Attention (MQA) - 多个query共享KV
- Grouped Query Attention (GQA) - 分组共享（Llama 2+使用）
- Linear Attention - 降低复杂度

---

### Positional Encoding

**费曼解释**：Transformer本身不知道词的顺序（不像RNN天然有序），需要人为告诉它"这个词在第几个位置"。就像给学生编号，让他们知道自己站哪里。

**历史演进**：
1. **Sinusoidal PE** (2017) - 原始Transformer，正弦函数
2. **Learnable PE** (2018) - BERT使用，可学习
3. **Relative PE** (2018, Shaw et al.) - 相对位置
4. **RoPE** (2021, Rotary PE) - 旋转位置编码，当前主流
5. **ALiBi** (2021) - 不需要训练的位置编码

**经典论文**：
- "Self-Attention with Relative Position Representations" (Shaw et al., 2018)
- "RoFormer: Enhanced Transformer with Rotary Position Embedding" (Su et al., 2021)

**缺陷对比**：

| 方法 | 优点 | 缺点 |
|------|------|------|
| Sinusoidal | 可外推 | 长文本效果差 |
| Learnable | 简单 | 完全无法外推 |
| RoPE | 长文本友好 | 实现稍复杂 |
| ALiBi | 外推极强 | 相对位置信息有限 |

---

## 2. 模型变体架构

### Encoder-Only (BERT系列)

**费曼解释**：像双向阅读理解，同时看前后文。擅长"理解"而不是"生成"。适合分类、抽取、问答等任务。

**代表模型**：
- BERT (2018)
- RoBERTa (2019)
- ALBERT (2019)
- ELECTRA (2020)
- DeBERTa (2020)

**经典论文**：
- "BERT: Pre-training of Deep Bidirectional Transformers" (Devlin et al., 2018)
  - 贡献：Masked LM + Next Sentence Prediction
  - 影响：开启预训练时代

**缺陷**：
1. **不能自然生成文本**
2. **MLM训练低效** - 只预测[MASK]
3. **需要任务特定fine-tuning**

**适用场景**：
- 文本分类
- 命名实体识别
- 问答（抽取式）
- 情感分析

---

### Decoder-Only (GPT系列)

**费曼解释**：单向从左到右生成，像写作文时逐字生成。擅长"生成"而不是"理解"。所有主流LLM（GPT、Claude、Llama）都用这个。

**为什么Decoder-Only成为主流**：
1. 生成能力自然
2. 可扩展性好
3. 训练目标简单（预测下一个token）
4. Scaling laws更清晰

**代表模型**：
- GPT系列 (2018-2023)
- Llama系列 (2023-2024)
- Claude系列
- Mistral系列

**经典论文**：
- "Language Models are Unsupervised Multitask Learners" (GPT-2, Radford et al., 2019)
- "Language Models are Few-Shot Learners" (GPT-3, Brown et al., 2020)

**缺陷**：
1. **单向上下文** - 不能"往后看"
2. **推理需要完整前缀** - 无法并行生成
3. **长文本建模不如双向模型**（某种程度上）

---

### Encoder-Decoder (T5, BART)

**费曼解释**：既有理解部分（Encoder），又有生成部分（Decoder）。像翻译官：先理解原文，再生成译文。

**代表模型**：
- T5 (2019)
- BART (2019)
- mT5 (2020)
- Flan-T5 (2022)

**经典论文**：
- "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (T5, Raffel et al., 2019)

**优势**：
- 适合seq2seq任务（翻译、摘要）
- 理解和生成平衡

**缺陷**：
1. **参数效率低** - 两部分都要训练
2. **纯生成任务不如Decoder-only**
3. **社区支持较少**

**现状**：LLM主流选择Decoder-only

---

### Mixture of Experts (MoE)

**费曼解释**：一个大脑里有多个"专家"，每次只激活相关的专家。就像医院有内科、外科、儿科，病人来了只看对应科室，不是所有医生都出动。

**核心思想**：
- 多个expert networks（前馈网络）
- Router/Gating network决定用哪些expert
- 只激活部分expert（稀疏激活）

**历史**：
- 1991：原始MoE概念（Jacobs et al.）
- 2017：Sparsely-Gated MoE (Eigen et al.)
- 2020：GShard (Google) - 首次大规模应用
- 2021：Switch Transformer (Google) - 万亿参数
- 2022：GLaM (Google)
- 2023：Mixtral 8x7B - 开源MoE标杆
- 2024：DeepSeek-V2, Grok-1

**经典论文**：
- "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer" (Shazeer et al., 2017)
- "Switch Transformers: Scaling to Trillion Parameter Models" (Fedus et al., 2021)
- "Mixture of Experts with Expert Choice Routing" (Zhou et al., 2022)

**优势**：
1. **推理效率高** - 只用部分参数
2. **可扩展性强** - 容易增加expert数量
3. **容量大** - 总参数多但激活少

**缺陷**：
1. **训练不稳定** - expert负载不均
2. **内存占用大** - 所有expert都要加载
3. **路由决策难** - 如何选择expert
4. **微调困难** - expert specialization

**改进方向**：
- Expert Choice Routing（expert主动选token）
- Load balancing loss
- Fine-grained expert segmentation

---

### State Space Models (SSM / Mamba)

**费曼解释**：Transformer看所有历史（O(n²)），SSM像压缩的历史摘要，用固定大小的"状态"记住过去。理论上处理超长序列更高效。

**历史**：
- 2021：S4 (Structured State Space) - Gu et al.
- 2022：H3 - Hungry Hungry Hippos
- 2023：Mamba - 线性时间SSM
- 2024：Mamba-2, Jamba

**经典论文**：
- "Efficiently Modeling Long Sequences with Structured State Spaces" (S4, Gu et al., 2021)
- "Mamba: Linear-Time Sequence Modeling with Selective State Spaces" (Gu & Dao, 2023)

**核心创新**：
- 选择性状态空间 - 根据内容调整状态更新
- 线性复杂度 - O(n) vs Transformer的O(n²)
- 硬件感知算法 - GPU友好

**优势**：
1. **长序列处理高效**
2. **推理内存恒定**
3. **线性复杂度**

**缺陷**：
1. **生态系统不成熟** - 工具链远不如Transformer
2. **预训练数据少** - 大规模验证不足
3. **某些任务表现不如Transformer**
4. **社区接受度待观察**

**现状**：有潜力，但Transformer仍是主流

---

## 3. 训练技术

### Pre-training (预训练)

**费曼解释**：先让模型在海量文本上学习语言的基本规律，像婴儿先学会听懂语言，再去学具体任务。

**目标**：
- Next Token Prediction（最常见）
- Masked Language Modeling（BERT）
- Span Prediction（T5）

**数据规模**：
- GPT-3: 300B tokens
- Llama: 1T+ tokens
- 现代: 多达10T+ tokens

**经典论文**：
- "Improving Language Understanding by Generative Pre-Training" (GPT-1, Radford et al., 2018)
- "BERT: Pre-training of Deep Bidirectional Transformers" (Devlin et al., 2018)

**关键发现**：
- **Scaling Laws** (Kaplan et al., 2020): 性能与参数量、数据量、计算量呈幂律关系
- **Chinchilla Scaling** (Hoffmann et al., 2022): 数据和模型大小应按比例增长

**缺陷**：
1. **数据质量参差不齐**
2. **计算成本极高**（百万美元级别）
3. **存在偏见和有害内容**
4. **知识截止**（训练数据有时效性）

---

### Supervised Fine-Tuning (SFT)

**费曼解释**：用标注好的"指令-回答"对教模型如何听从指令。像学生做题，有标准答案可以对照。

**数据格式**：
```
{
  "instruction": "将下面句子翻译成英文",
  "input": "你好，世界",
  "output": "Hello, world"
}
```

**经典论文**：
- "Training language models to follow instructions with human feedback" (InstructGPT, Ouyang et al., 2022)

**关键点**：
1. **数据质量 > 数量** - 几千条高质量数据比几万条低质量数据效果好
2. **多样性重要** - 覆盖各种任务类型
3. **格式一致** - 统一的prompt模板

**缺陷**：
1. **需要大量标注** - 成本高
2. **分布偏移** - 与预训练数据分布不同
3. **灾难性遗忘** - 可能忘记预训练知识

---

### RLHF (Reinforcement Learning from Human Feedback)

**费曼解释**：人类给模型的回答打分或排序，模型学习"什么样的回答是人类喜欢的"。像老师给作文打分，学生慢慢学会怎么写得更好。

**三步流程**：
1. **SFT** - 先用监督学习训练初始模型
2. **Reward Model** - 训练一个打分模型
3. **PPO** - 用强化学习优化策略

**经典论文**：
- "Training language models to follow instructions with human feedback" (InstructGPT, Ouyang et al., 2022)
- "Learning to Summarize with Human Feedback" (Stiennon et al., 2020)

**历史**：
- 2017：原始RLHF概念（Christiano et al.）
- 2020：首次用于文本摘要
- 2022：InstructGPT/ChatGPT - 引爆LLM应用

**优势**：
1. **对齐人类偏好**
2. **减少有害输出**
3. **提升有用性**

**缺陷**：
1. **训练复杂** - 多阶段训练
2. **奖励模型不准确** - 人类偏好难以建模
3. **Reward Hacking** - 模型学会欺骗奖励模型
4. **标注成本高** - 需要人类标注偏好

---

### DPO (Direct Preference Optimization)

**费曼解释**：RLHF的简化版，不需要训练单独的奖励模型，直接从人类偏好数据学习。跳过中间步骤，更直接。

**核心思想**：
- RLHF: SFT → Reward Model → PPO（三步）
- DPO: SFT → DPO（两步）

**经典论文**：
- "Direct Preference Optimization: Your Language Model is Secretly a Reward Model" (Rafailov et al., 2023)

**公式直觉**：
```
不用显式奖励模型，直接优化策略
利用 Bradley-Terry 偏好模型
```

**优势**：
1. **训练简单** - 少一个阶段
2. **稳定性好** - 不需要PPO的复杂调参
3. **计算高效**

**缺陷**：
1. **理论保证较弱**
2. **可能不如RLHF上限高**
3. **长文本偏好建模困难**

**变体**：
- IPO (Identity Preference Optimization)
- KTO (Kahneman-Tversky Optimization)
- ORPO (Odds Ratio Preference Optimization)

---

### LoRA / QLoRA

**费曼解释**：LoRA = 只调整模型的一小部分"旁路"参数，不动主体。像给机器换几个小零件，而不是重造整台机器。QLoRA = 量化后再用LoRA，资源需求更低。

**LoRA核心**：
- 原始权重 W (d×k) 冻结
- 添加低秩分解 W' = W + AB，A (d×r), B (r×k), r << min(d,k)
- 只训练 A 和 B

**经典论文**：
- "LoRA: Low-Rank Adaptation of Large Language Models" (Hu et al., 2021)
- "QLoRA: Efficient Finetuning of Quantized LLMs" (Dettmers et al., 2023)

**LoRA优势**：
1. **参数高效** - 只训练0.1%-1%的参数
2. **内存友好** - 不需要存储完整梯度
3. **模块化** - 多个LoRA可快速切换

**QLoRA创新**：
1. **4-bit NormalFloat** - 新的量化数据类型
2. **Double Quantization** - 量化常量也量化
3. **Paged Optimizers** - 内存溢出到CPU

**效果**：
- 65B模型：原本需要780GB显存 → QLoRA只需48GB
- 可在单张消费级GPU上微调大模型

**缺陷**：
1. **性能可能不如全参数微调**（某些任务）
2. **低秩假设不总是成立**
3. **超参数选择（秩r）需要实验**

---

## 4. 推理技术

### KV Cache

**费曼解释**：生成第N个token时，第1到N-1个token的计算结果缓存起来，不用重复计算。像做数学题记住中间步骤。

**原理**：
```
生成token 1: 计算 K1, V1
生成token 2: 计算 K2, V2, 用 K1,V1,K2,V2
生成token 3: 计算 K3, V3, 用 K1,V1,K2,V2,K3,V3
...
缓存所有之前的 K,V
```

**优势**：
1. **大幅加速推理** - 避免重复计算
2. **实现简单**

**缺陷**：
1. **内存占用大** - 长文本KV cache可达数GB
2. **随长度线性增长** - 超长文本内存爆炸

**优化方向**：
- **PagedAttention** (vLLM) - 像OS虚拟内存管理
- **Multi-Query Attention (MQA)** - 多个query共享KV
- **Grouped-Query Attention (GQA)** - Llama 2使用
- **KV Cache Compression** - 量化、剪枝

---

### Quantization (量化)

**费曼解释**：减少每个参数的存储精度。原用32位浮点数，改用8位甚至4位整数。像图片压缩，小了但"能用"。

**分类**：

| 类型 | 描述 | 精度损失 | 复杂度 |
|------|------|----------|--------|
| FP32 | 原始精度 | 无 | - |
| FP16/BF16 | 半精度 | 小 | 低 |
| INT8 | 8位整数 | 中 | 低 |
| INT4 | 4位整数 | 较大 | 中 |
| INT3/INT2 | 极低精度 | 大 | 高 |

**方法**：
1. **Post-Training Quantization (PTQ)** - 训练后量化
   - GPTQ (2022)
   - AWQ (2023)
   - GGUF (llama.cpp)
   
2. **Quantization-Aware Training (QAT)** - 训练时考虑量化
   - 更好效果但需要重训练

**经典论文**：
- "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers" (Frantar et al., 2022)
- "AWQ: Activation-aware Weight Quantization for LLM Compression" (Lin et al., 2023)

**GPTQ vs AWQ**：
- GPTQ: 基于Hessian，逐层量化
- AWQ: 考虑激活分布，保护重要权重

**效果**：
- 70B模型：FP16需要140GB → INT4只需35GB
- 推理速度提升2-4x
- 质量损失可接受（多数场景）

**缺陷**：
1. **精度损失** - 困难任务性能下降
2. **硬件支持** - 不是所有GPU都支持低精度
3. **量化过程本身需要资源**

---

### Speculative Decoding (投机解码)

**费曼解释**：用小模型快速"猜"接下来的几个token，大模型验证。猜对了直接用，猜错了重算。像考试时先快速答题，再仔细检查。

**流程**：
```
1. Draft Model (小) 快速生成 K 个token
2. Target Model (大) 并行验证这 K 个token
3. 如果都正确 → 接受，节省时间
4. 如果某处错误 → 拒绝，从该处重新生成
```

**经典论文**：
- "Fast Inference from Transformers via Speculative Decoding" (Leviathan et al., 2023)
- "Speculative Decoding: Exploiting Speculative Execution for Accelerating Transformer Inference" (Xia et al., 2023)

**加速原理**：
- 大模型验证K个token的时间 ≈ 生成1个token的时间
- 如果接受率高，相当于K倍加速

**关键**：
- Draft model要快（小）
- Draft model要准（接受率高）
- Target model要大（质量高）

**效果**：
- 典型加速 2-3x
- 不损失质量（target model保证）

**缺陷**：
1. **需要额外的draft model**
2. **接受率依赖draft model质量**
3. **实现复杂**

---

### Continuous Batching

**费曼解释**：传统batching等所有请求都齐了才开始，continuous batching来了就处理，走了就释放。像公交车，人到齐发车 vs 流水线持续上下客。

**传统 vs Continuous**：

传统：
```
[Request 1] ████████████ (等待)
[Request 2] ████████████ (等待)
             ↑ 都到齐了才开始
```

Continuous：
```
[Request 1] ████████
[Request 2]   ████████████
[Request 3]     ██████████
             ↑ 来了就处理
```

**实现**：
- Orca (2022) - 首次提出
- vLLM - 工程实现标杆

**经典论文**：
- "Orca: A Distributed Serving System for Transformer-Based Generative Models" (Yu et al., 2022)

**优势**：
1. **吞吐量大幅提升**（2-10x）
2. **延迟降低**
3. **资源利用率高**

---

### PagedAttention (vLLM)

**费曼解释**：把KV cache像操作系统管理内存一样管理，按"页"分配。内存碎片化问题解决，利用率大幅提升。

**核心思想**：
- KV cache分成固定大小的block（类似内存页）
- 按需分配，不需要连续内存
- 支持sharing（相同prefix的请求共享）

**经典论文**：
- "Efficient Memory Management for Large Language Model Serving with PagedAttention" (vLLM, Kwon et al., 2023)

**优势**：
1. **内存利用率接近100%**
2. **支持超长文本**
3. **吞吐量提升2-4x**

**缺陷**：
1. **实现复杂**
2. **block大小需要调优**

---

## 5. 核心参数与概念

### Temperature

**费曼解释**：控制输出的"创造性"。0度 = 最确定的选择（总是选概率最高的），高温 = 更随机、更有创意。

**公式**：
```
prob = softmax(logits / temperature)
```
- T=1: 原始分布
- T<1: 更尖锐，更确定
- T>1: 更平滑，更随机

**使用场景**：
- 代码生成：T=0-0.3（确定性任务）
- 创意写作：T=0.7-1.0（多样性任务）
- 头脑风暴：T>1（探索性任务）

**缺陷**：
- 温度不是万能的，高温度可能导致幻觉加剧

---

### Top-p (Nucleus Sampling)

**费曼解释**：不从所有词中选，只从累积概率达到p的最可能的词中选。比如p=0.9，就只考虑前90%概率的词。

**与Top-k对比**：
- Top-k: 固定选前k个词
- Top-p: 动态选择，累积概率达到p

**推荐配置**：
- Top-p: 0.9-0.95
- 配合Temperature使用

---

### Context Window / Context Length

**费曼解释**：模型一次能处理的文本长度上限。像人的工作记忆，只能同时"记住"这么多内容。

**历史演进**：
```
2018  BERT:      512 tokens
2019  GPT-2:     1024 tokens
2020  GPT-3:     2048 tokens
2022  GPT-3.5:   4096 tokens
2023  Claude 2:  100K tokens
2024  Gemini 1.5: 1M+ tokens
```

**扩展技术**：
- ALiBi位置编码
- RoPE外推
- 长文本微调
- 滑动窗口

**注意**：
- 长上下文 ≠ 长期记忆
- 中间内容可能被"遗忘"（Lost in the Middle现象）

---

### Token与Tokenization

**费曼解释**：模型不直接看文字，而是看"token"（词片）。"Hello world"可能是[15496, 995]两个token。

**常见Tokenizer**：
1. **BPE** (Byte Pair Encoding) - GPT系列
2. **WordPiece** - BERT
3. **Unigram** - T5, SentencePiece
4. **Byte-level BPE** - GPT-2+

**影响**：
- Token数量影响成本（API按token收费）
- 不同语言tokenization效率不同（中文可能1字=1-2 token，英文1词≈1-2 token）

**经典论文**：
- "Neural Machine Translation of Rare Words with Subword Units" (Sennrich et al., 2015)

---

## 6. 评估与基准

### Perplexity (困惑度)

**费曼解释**：衡量模型对文本的"惊讶程度"。越低越好，说明模型预测越准确。

**公式**：
```
PPL = exp(average negative log-likelihood)
```

**直觉**：
- PPL = 10: 模型每次像从10个等可能选项中选
- PPL = 100: 模型很困惑，像从100个选项中猜

**缺陷**：
- 不直接反映下游任务性能
- 不同tokenizer不可比

---

### MMLU (Massive Multitask Language Understanding)

**费曼解释**：综合考试，覆盖57个学科，从初等数学到专业法律。测试模型的知识广度。

**经典论文**：
- "Measuring Massive Multitask Language Understanding" (Hendrycks et al., 2021)

**评分**：
- GPT-4: ~86%
- Claude 3 Opus: ~86.8%
- Llama 3 70B: ~82%

---

### HumanEval (代码生成)

**费曼解释**：给164道Python编程题，让模型实现函数，用单元测试验证正确性。

**经典论文**：
- "Evaluating Large Language Models Trained on Code" (Chen et al., 2021)

**指标**：pass@k
- pass@1: 一次生成即通过
- pass@10: 生成10次，至少1次通过

---

### Chatbot Arena (Elo Rating)

**费曼解释**：盲测平台，用户同时问两个模型问题，选择更好的。像国际象棋Elo积分。

**特点**：
- 人类真实偏好
- 持续更新
- 覆盖主流模型

**排名（2024参考）**：
1. GPT-4 Turbo
2. Claude 3.5 Sonnet
3. Gemini 1.5 Pro
4. Llama 3 70B

---

## 🔬 研究前沿

### Scaling Laws

**费曼解释**：模型性能随规模（参数、数据、计算）的可预测增长规律。像物理定律，可以预测"多大模型能达到什么效果"。

**经典论文**：
- "Scaling Laws for Neural Language Models" (Kaplan et al., 2020)
- "Training Compute-Optimal Large Language Models" (Chinchilla, Hoffmann et al., 2022)

**核心发现**：
1. 性能与参数、数据、计算呈幂律关系
2. Chinchilla: 给定计算预算，参数量和数据量应等比例增长
3. 小模型+更多数据 > 大模型+少数据（计算相等时）

**争议**：
- Llama挑战了Chinchilla（过训练有益）
- 推理时计算 vs 训练时计算（新scaling维度）

---

### Emergent Abilities (涌现能力)

**费曼解释**：模型大到一定程度突然出现的新能力，小模型完全没有。像量变引起质变。

**经典论文**：
- "Emergent Abilities of Large Language Models" (Wei et al., 2022)

**例子**：
- 思维链推理 (CoT)
- 指令遵循
- 上下文学习

**争议**：
- 是否真的"涌现"？
- 可能是评估指标问题（科学界有争议）

---

## 📚 必读论文清单

### 奠基之作
1. "Attention is All You Need" (2017) - Transformer
2. "BERT" (2018) - 预训练时代开启
3. "Language Models are Few-Shot Learners" (GPT-3, 2020)
4. "Training language models to follow instructions with human feedback" (InstructGPT, 2022)

### 优化与加速
5. "FlashAttention" (2022)
6. "QLoRA" (2023)
7. "vLLM: Easy, Fast, and Cheap LLM Serving" (2023)

### 对齐与安全
8. "Constitutional AI" (2022)
9. "Direct Preference Optimization" (2023)

### 新架构
10. "Mamba" (2023)
11. "Mixtral of Experts" (2023)

---

## 🔗 下一步

- [主流模型大全](./MODEL_ENCYCLOPEDIA.md) - 各公司模型详细对比
- [AI Agent深度指南](./AI_AGENT_GUIDE.md) - Agent系统设计
- [AI应用开发实战](./AI_APP_DEVELOPMENT.md) - RAG、Prompt工程、部署

---

*词典持续更新中 | 反馈请提Issue*
