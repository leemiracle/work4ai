# AI知识词典（2024-2025版）

## 目录
1. [基础概念](#基础概念)
2. [模型架构](#模型架构)
3. [训练技术](#训练技术)
4. [提示工程](#提示工程)
5. [推理技术](#推理技术)
6. [应用领域](#应用领域)
7. [工具与框架](#工具与框架)
8. [评估与基准](#评估与基准)
9. [前沿技术](#前沿技术)
10. [伦理与安全](#伦理与安全)

---

## 基础概念

### LLM (Large Language Model)
**费曼解释**：想象一个读过互联网上几乎所有文字的超大图书管理员，能根据你给的提示生成连贯的文本。就像鹦鹉学舌，但学会了语言的模式和规律。

### Transformer
**费曼解释**：一种革命性的神经网络架构，通过"注意力机制"让模型知道哪些词之间有关系。就像阅读时，你会同时关注句子中相互关联的词。

### Attention Mechanism
**费曼解释**：让模型"知道该看哪里"的机制。就像你看"苹果很好吃，它很甜"时，知道"它"指代的是苹果。

### Token
**费曼解释**：文本的最小单位，可以是一个字、一个词或一部分词。模型不是逐字处理，而是按token处理。例如"hello"可能是1个token，"人工智能"可能是2-3个token。

### Embedding
**费曼解释**：把文字变成一串数字向量，让计算机能理解词的含义。相似含义的词在数字空间里距离更近，就像地图上相近地点距离更近。

### Context Window
**费曼解释**：模型一次能"记住"和处理的文本长度。就像人的工作记忆容量有限，模型也有它的记忆窗口。

### Parameters
**费曼解释**：模型的"脑细胞连接数"。70B参数意味着模型有700亿个可调整的参数，参数越多通常能力越强，但也更耗资源。

### Temperature
**费曼解释**：控制输出随机性的参数。0度像严格的教科书，总是最确定的回答；高温像创意作家，输出更多样和随机。

### Top-p / Nucleus Sampling
**费曼解释**：从最可能的一堆候选词中随机选，而不是从所有词中选。就像考试时从你最有把握的几个答案中选，而不是瞎猜。

---

## 模型架构

### GPT (Generative Pre-trained Transformer)
**费曼解释**：OpenAI开创的"预测下一个词"模型架构。通过海量文本预训练，学会了语言的模式。

### BERT (Bidirectional Encoder Representations from Transformers)
**费曼解释**：同时看前后文的模型，擅长"理解"而不是"生成"。像仔细阅读理解文章，而不是写文章。

### MoE (Mixture of Experts)
**费曼解释**：一个大脑里有多个"专家"，每次只激活相关的专家。就像医院有各科医生，看病时只找对应科室。

### Sparse Attention
**费曼解释**：不需要关注所有词，只关注重要的。就像开会时不听所有人发言，只听相关的部分。

### Multi-Head Attention
**费曼解释**：同时从多个角度理解关系。就像分析一句话时，既看语法、又看语义、还看情感。

### RoPE (Rotary Position Embedding)
**费曼解释**：用旋转的方式表示位置信息。比传统方法更好地让模型理解词的相对位置。

### Grouped Query Attention (GQA)
**费曼解释**：多个查询头共享键值，减少计算量。像多个学生共享一本参考书，省资源。

### Sliding Window Attention
**费曼解释**：只关注附近的一定范围内的词。像读书时眼睛一次只看一页或一段。

### Flash Attention
**费曼解释**：一种高效的注意力计算方法，通过巧妙的重排计算顺序，大幅减少内存访问，让训练和推理更快。

---

## 训练技术

### Pre-training (预训练)
**费曼解释**：先让模型在海量数据上学习语言的基础规律。像婴儿先学说话，掌握语言基本功。

### SFT (Supervised Fine-Tuning)
**费曼解释**：用标注好的数据教模型特定任务。像学生做有标准答案的练习题。

### RLHF (Reinforcement Learning from Human Feedback)
**费曼解释**：人类给模型的回答打分，模型学习什么是"好回答"。像老师给作文打分，学生慢慢学会怎么写更好。

### DPO (Direct Preference Optimization)
**费曼解释**：简化版的RLHF，直接从人类偏好数据学习，不需要训练奖励模型。更直接高效。

### PPO (Proximal Policy Optimization)
**费曼解释**：一种强化学习算法，让模型改进时不偏离太远。像调整设置时小步快跑，不会一步改太多。

### LoRA (Low-Rank Adaptation)
**费曼解释**：只调整模型的一小部分参数就能适应新任务。像只换几个齿轮就让机器适应新功能。

### QLoRA (Quantized LoRA)
**费曼解释**：先用4位量化压缩模型，再应用LoRA微调。在有限资源下微调大模型的黑科技。

### Fine-tuning (微调)
**费曼解释**：在预训练基础上，用专门数据训练模型适应特定任务。像通用人才接受专业培训。

### Instruction Tuning
**费曼解释**：用"指令-回答"对训练模型，让它学会听从指令。像训练员工按标准流程工作。

### Constitutional AI
**费曼解释**：给模型一套"宪法"原则，让它自我批评和改进，减少有害输出。

### Curriculum Learning
**费曼解释**：从简单到复杂逐步学习。像小学生先学加减，再学乘除。

### Continual Learning
**费曼解释**：持续学习新知识而不忘旧知识。挑战在于如何避免"灾难性遗忘"。

---

## 提示工程

### Prompt Engineering
**费曼解释**：设计输入文本的艺术，让模型输出你想要的结果。像学会如何提问才能得到好答案。

### Chain of Thought (CoT)
**费曼解释**：让模型"一步步思考"，展示推理过程。像数学题要求写出解题步骤，不只是答案。

### Zero-shot
**费曼解释**：不给示例，直接让模型完成任务。测试模型泛化能力。

### Few-shot
**费曼解释**：给几个示例，让模型模仿。像给模板让学生照着做。

### Role-playing
**费曼解释**：让模型扮演特定角色。例如"你是一位经验丰富的Python程序员..."

### Prompt Injection
**费曼解释**：恶意输入试图覆盖原始指令。像黑客试图欺骗系统。

### System Prompt
**费曼解释**：预先设定的背景指令，定义模型的行为方式和约束条件。

### Context Stuffing
**费曼解释**：尽可能往上下文窗口塞相关信息。在有限空间内提供最多有用信息。

### RAG (Retrieval-Augmented Generation)
**费曼解释**：先从知识库检索相关信息，再让模型结合检索结果生成回答。像考试时允许查阅资料。

### Tool Use / Function Calling
**费曼解释**：让模型调用外部工具（计算器、搜索引擎、API等）。给模型"手脚"，不只动嘴。

---

## 推理技术

### KV Cache
**费曼解释**：缓存之前计算的结果，避免重复计算。像算长算式时记住中间结果。

### Speculative Decoding
**费曼解释**：用小模型快速"猜"接下来的内容，大模型验证。猜对了就省时间。

### Quantization (量化)
**费曼解释**：减少每个参数的存储位数（如从16位到4位），用精度换速度和内存。像压缩图片，小了但能用。

### Distillation (蒸馏)
**费曼解释**：让小模型学习大模型的知识。大模型当老师，小模型当学生。

### Pruning (剪枝)
**费曼解释**：删除模型中不重要的连接。像修剪树枝，去掉多余部分让树更健康。

### Continuous Batching
**费曼解释**：动态批处理，不等所有请求都齐了才开始处理。提高服务效率。

### Paged Attention
**费曼解释**：像操作系统的虚拟内存一样管理KV缓存，更高效利用内存。

### Tensor Parallelism
**费曼解释**：把一个矩阵运算拆到多个GPU上并行计算。人多力量大。

### Pipeline Parallelism
**费曼解释**：把模型分成几段，不同GPU处理不同层。像流水线生产。

### vLLM
**费曼解释**：一种高效的大模型推理引擎，通过PagedAttention技术大幅提升吞吐量。

---

## 应用领域

### Chatbot / Conversational AI
**费曼解释**：能进行对话的AI系统。从客服机器人到智能助手。

### Code Generation
**费曼解释**：让AI写代码。GitHub Copilot就是例子，理解需求生成代码。

### Translation
**费曼解释**：机器翻译。将一种语言自动转换为另一种语言。

### Summarization
**费曼解释**：自动总结长文本的核心内容。像学生写摘要。

### Sentiment Analysis
**费曼解释**：分析文本的情感倾向（正面、负面、中性）。

### Question Answering
**费曼解释**：给定文档，回答相关问题。像智能阅读理解助手。

### Text Classification
**费曼解释**：自动给文本分类。例如垃圾邮件检测、新闻分类。

### Named Entity Recognition (NER)
**费曼解释**：识别文本中的人名、地名、机构名等实体。

### Image Generation (多模态)
**费曼解释**：AI生成图片。如DALL-E、Midjourney、Stable Diffusion。

### Multimodal AI
**费曼解释**：能同时处理文字、图片、音频、视频等多种类型信息的AI。

### Agent
**费曼解释**：有自主能力的AI，能规划任务、使用工具、执行复杂操作。不只是回答问题，而是解决问题。

---

## 工具与框架

### PyTorch
**费曼解释**：Meta开发的深度学习框架，灵活且流行。研究人员的最爱。

### TensorFlow
**费曼解释**：Google开发的深度学习框架，生产环境广泛使用。

### JAX
**费曼解释**：Google开发的高性能数值计算框架，能自动并行和加速。

### Hugging Face
**费曼解释**：AI界的GitHub，分享模型和数据集的平台。开源AI的中心。

### LangChain
**费曼解释**：帮助构建LLM应用的框架，提供各种工具和组件。

### LlamaIndex
**费曼解释**：专门用于构建RAG系统的框架，连接LLM和你的数据。

### Ollama
**费曼解释**：本地运行大模型的工具，简单易用。

### vLLM
**费曼解释**：高性能推理引擎，优化吞吐量和延迟。

### DeepSpeed
**费曼解释**：微软的深度学习优化库，支持大规模分布式训练。

### Accelerate
**费曼解释**：Hugging Face的库，简化多GPU和混合精度训练。

### PEFT
**费曼解释**：参数高效微调库，包含LoRA等方法。

### Transformers
**费曼解释**：Hugging Face的核心库，提供各种预训练模型。

### Safetensors
**费曼解释**：安全的模型存储格式，避免pickle格式的安全风险。

---

## 评估与基准

### Perplexity
**费曼解释**：衡量模型对文本的"困惑度"。越低越好，说明模型预测越准确。

### BLEU Score
**费曼解释**：评估机器翻译质量，比较生成文本和参考文本的相似度。

### ROUGE
**费曼解释**：评估摘要和生成文本的指标，看重叠度。

### MMLU (Massive Multitask Language Understanding)
**费曼解释**：综合测试模型在各种学科的知识和理解能力。

### HellaSwag
**费曼解释**：测试常识推理能力，让模型完成日常场景描述。

### HumanEval
**费曼解释**：测试代码生成能力，给函数描述让模型实现。

### GSM8K
**费曼解释**：小学数学应用题数据集，测试多步推理能力。

### TruthfulQA
**费曼解释**：测试模型是否会生成常见误区和错误信息。

### C-Eval / CMMLU
**费曼解释**：中文综合能力测试基准。

### Chatbot Arena
**费曼解释**：让用户blind test对比不同模型，排名最真实。

### MT-Bench
**费曼解释**：用GPT-4给模型的对话能力打分。

---

## 前沿技术

### Mamba / State Space Models (SSM)
**费曼解释**：Transformer的挑战者，序列长度线性复杂度。理论上比Transformer处理超长文本更高效。

### Long Context Models
**费曼解释**：支持超长上下文的模型（如128K tokens）。能处理整本书的输入。

### Multimodal LLMs (GPT-4V, Gemini, Claude 3)
**费曼解释**：能看懂图片、听懂音频的大模型。不只是文本，全方位理解。

### Vision Language Models (VLM)
**费曼解释**：结合视觉和语言的模型，能理解图片内容并用文字描述或回答。

### Diffusion Models
**费曼解释**：通过"去噪"过程生成图像的模型。从纯噪声一步步还原出清晰图像。

### Flow Matching
**费曼解释**：生成模型的新范式，比扩散更直接高效。像走直线而不是弯路。

### Neural Architecture Search (NAS)
**费曼解释**：让AI自动设计AI架构。机器设计机器。

### Mixture of Depths (MoD)
**费曼解释**：不是所有层都需要对所有token计算，动态选择计算深度。更聪明的资源分配。

### Test-Time Training (TTT)
**费曼解释**：推理时还继续学习调整。灵活适应具体任务。

### Diffusion Language Models
**费曼解释**：用扩散模型的思路生成文本，而不是传统的自回归。

### World Models
**费曼解释**：模型学会理解世界的运作规律，预测物理现象和因果关系。

### Chain-of-Verification
**费曼解释**：模型先给出答案，再自我验证每一步，减少幻觉。

### Tree of Thoughts
**费曼解释**：不只一条思路，而是探索多条可能的推理路径，选最优。

### Self-Consistency
**费曼解释**：同一问题多次采样，选最一致的答案。少数服从多数。

---

## 模型系列与版本

### GPT Series (OpenAI)
- **GPT-3**: 175B参数，展示了few-shot能力
- **GPT-3.5**: ChatGPT的初始版本
- **GPT-4**: 多模态，大幅提升推理能力
- **GPT-4o**: 更快更便宜的多模态模型
- **GPT-4 Turbo**: 更快版本，128K上下文

### Claude Series (Anthropic)
- **Claude 1**: 初代，擅长长文本
- **Claude 2**: 100K上下文，更强推理
- **Claude 3 (Haiku/Sonnet/Opus)**: 多尺寸选择
- **Claude 3.5 Sonnet**: 性能与速度的最佳平衡

### Llama Series (Meta)
- **Llama 1**: 开源模型的开创者
- **Llama 2**: 商用友好，性能大幅提升
- **Llama 3**: 最新一代，多个尺寸(8B/70B/405B)

### Gemini Series (Google)
- **Gemini 1.0**: 原生多模态
- **Gemini 1.5 Pro**: 百万token上下文
- **Gemini Ultra**: 最强版本

### Mistral Series
- **Mistral 7B**: 小而强大
- **Mixtral 8x7B**: MoE架构，高效
- **Mistral Large**: 挑战GPT-4

### Qwen Series (阿里通义)
- **Qwen-7B/14B/72B**: 多尺寸
- **Qwen-VL**: 视觉语言版本
- **Qwen-2**: 新一代

### Yi Series (零一万物)
- **Yi-6B/34B**: 双语模型

### Baichuan (百川)
- **Baichuan 2**: 开源双语模型

### GLM / ChatGLM (智谱)
- **GLM-4**: 多模态，长上下文
- **ChatGLM3**: 对话优化版本

### DeepSeek
- **DeepSeek-V2**: MoE架构，高性价比
- **DeepSeek Coder**: 代码专精

---

## 伦理与安全

### AI Alignment
**费曼解释**：让AI的行为符合人类价值观和意图。确保AI做我们真正想让它做的事。

### Hallucination
**费曼解释**：模型"一本正经地胡说八道"。自信地给出错误信息。

### Bias and Fairness
**费曼解释**：模型可能继承或放大训练数据中的偏见。需要检测和缓解。

### Safety Training
**费曼解释**：专门训练让模型拒绝有害请求，不输出危险内容。

### Red Teaming
**费曼解释**：让攻击者尝试攻破模型，发现安全漏洞。像军事演习。

### RLHF vs RLAIF
**费曼解释**：RLHF用人类反馈，RLAIF用AI反馈训练，更可扩展。

### Interpretability / Explainability
**费曼解释**：理解模型为什么做出某个决策。打开黑盒。

### Jailbreaking
**费曼解释**：通过特殊提示绕过模型的安全限制。安全研究的重点。

### Poisoning Attacks
**费曼解释**：污染训练数据，让模型学到错误的东西。

### Privacy in LLMs
**费曼解释**：确保模型不泄露训练数据中的隐私信息。

### Responsible AI
**费曼解释**：负责任地开发和部署AI，考虑社会影响。

---

## 量化与优化

### FP16 / BF16
**费曼解释**：16位浮点数格式。BF16更适合深度学习，精度范围更广。

### INT8 / INT4
**费曼解释**：8位或4位整数。更激进的量化，内存占用更小。

### GPTQ
**费曼解释**：一种训练后量化方法，专门为GPT类模型设计。

### AWQ (Activation-aware Weight Quantization)
**费曼解释**：考虑激活分布的量化方法，保持重要权重精度。

### GGUF
**费曼解释**：llama.cpp使用的模型格式，支持各种量化级别。

### EXL2
**费曼解释**：ExLlamaV2的量化格式，追求极致的推理速度。

### Mixed Precision Training
**费曼解释**：训练时混合使用不同精度，平衡速度和精度。

### Gradient Checkpointing
**费曼解释**：以计算换内存，不存储所有中间结果，需要时重新计算。

---

## 数据与数据集

### Pre-training Data
**费曼解释**：预训练用的海量文本，通常来自互联网(Common Crawl)、书籍、代码等。

### Instruction Data
**费曼解释**：指令-回答对，用于SFT训练。

### Preference Data
**费曼解释**：比较两个回答哪个更好的数据，用于RLHF/DPO。

### Synthetic Data
**费曼解释**：AI生成的数据，用来训练AI。GPT-4生成数据训练小模型。

### Data Contamination
**费曼解释**：测试数据混入训练数据，导致评估结果虚高。

### Deduplication
**费曼解释**：去除重复数据，提高数据质量和训练效率。

### Data Cleaning
**费曼解释**：清理低质量、有毒、错误的数据。

### Pile
**费曼解释**：一个大规模、多样化的开源预训练数据集。

### C4
**费曼解释**：Colossal Clean Crawled Corpus，清理过的网页数据。

### SlimPajama
**费曼解释**：Pile数据集的清理版本。

---

## 部署与生产

### Model Serving
**费曼解释**：部署模型供实际使用，处理API请求。

### API Rate Limiting
**费曼解释**：限制API调用频率，防止滥用。

### Latency vs Throughput
**费曼解释**：延迟(单个请求响应时间)vs吞吐量(单位时间处理请求数)。需要权衡。

### Batching
**费曼解释**：把多个请求打包一起处理，提高效率。

### Caching
**费曼解释**：缓存常见查询的结果，减少重复计算。

### Load Balancing
**费曼解释**：把请求分配到多个服务器，避免单点过载。

### A/B Testing
**费曼解释**：对比不同模型或配置的效果，数据驱动决策。

### Model Versioning
**费曼解释**：管理不同版本的模型，支持回滚和对比。

### Monitoring
**费曼解释**：监控模型在生产环境的表现，及时发现异常。

---

## 高级概念

### Emergent Abilities
**费曼解释**：模型规模大到一定程度突然出现的新能力，小模型没有。

### Scaling Laws
**费曼解释**：模型性能与规模、数据量、计算量之间的数学关系。

### Chinchilla Scaling
**费曼解释**：指出很多模型训练不足，给定计算预算，数据和模型大小应该按比例缩放。

### Grokking
**费曼解释**：模型在长时间过拟合后突然"顿悟"，泛化能力突然提升。

### In-context Learning
**费曼解释**：模型从提示中的示例学习新任务，不更新参数。

### Retrieval Augmented Generation (RAG)
**费曼解释**：结合检索和生成，先找相关信息再生成答案。

### Agentic Behavior
**费曼解释**：模型展现自主性，能规划、执行、反思的复杂行为。

### Tool Learning
**费曼解释**：模型学会使用外部工具(计算器、搜索引擎、代码解释器等)。

### Multi-Agent Systems
**费曼解释**：多个AI agent协作完成任务，各有分工。

### Constitutional AI
**费曼解释**：Anthropic提出的训练方法，通过自我批评改进，遵循"宪法"原则。

### Sparse vs Dense Models
**费曼解释**：稀疏模型(如MoE)只激活部分参数，稠密模型每次全激活。

---

## 最新趋势（2024-2025）

### Small Language Models (SLMs)
**费曼解释**：小而精的模型(1B-8B)，在边缘设备上运行，隐私友好。

### Efficient Inference
**费曼解释**：各种让推理更快更便宜的技术：投机解码、量化、缓存优化等。

### Long Context & RAG结合
**费曼解释**：超长上下文不意味着不需要RAG，两者互补。

### Multimodal Everything
**费曼解释**：所有模型都在变成多模态，文字、图像、音频、视频统一处理。

### Code as Reasoning
**费曼解释**：让模型写代码来辅助推理，Python解释器成为标配工具。

### AI Agents
**费曼解释**：从Chatbot到Agent，AI能执行复杂任务流程，使用工具，自主规划。

### Open Source Renaissance
**费曼解释**：开源模型(Llama, Mistral, Qwen等)快速追赶闭源模型。

### Mixture of Experts (MoE)普及
**费曼解释**：Mixtral、DeepSeek等证明MoE是高效架构，更多模型采用。

### Safety & Alignment研究
**费曼解释**：如何让模型更安全、更可控、更符合人类价值观。

### Model Merging
**费曼解释**：合并多个微调模型，无需训练就能获得组合能力。

---

## 实用资源

### 模型仓库
- **Hugging Face Hub**: https://huggingface.co/models
- **ModelScope**: https://modelscope.cn (国内)

### 数据集
- **Hugging Face Datasets**: https://huggingface.co/datasets
- **Papers with Code**: https://paperswithcode.com/datasets

### 论文追踪
- **arXiv**: https://arxiv.org (cs.CL, cs.LG)
- **Hugging Face Papers**: https://huggingface.co/papers

### 社区
- **r/LocalLLaMA**: Reddit社区
- **Hugging Face Discord**
- **AI相关的Twitter/X**

### 学习资源
- **Andrej Karpathy的YouTube课程**
- **斯坦福CS224N (NLP)**
- **Fast.ai课程**
- **Hugging Face NLP Course**

---

## 快速参考表

| 术语 | 简单解释 |
|------|----------|
| LLM | 大语言模型 |
| Prompt | 输入给模型的指令 |
| Token | 文本最小处理单位 |
| Context Window | 上下文长度限制 |
| Temperature | 输出随机性参数 |
| Fine-tuning | 微调模型 |
| RAG | 检索增强生成 |
| CoT | 链式思考 |
| Zero-shot | 零样本学习 |
| Few-shot | 少样本学习 |
| SFT | 监督微调 |
| RLHF | 人类反馈强化学习 |
| DPO | 直接偏好优化 |
| LoRA | 低秩适配微调 |
| Quantization | 模型量化 |
| KV Cache | 键值缓存 |
| MoE | 混合专家模型 |
| Hallucination | 幻觉/胡说 |
| Embedding | 向量嵌入 |
| Agent | 智能体 |

---

*本词典持续更新中，最后更新：2025年3月*