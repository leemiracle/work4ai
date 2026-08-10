# 102 · HuggingFace 生态全景地图 · 对接 work4ai

> **本文件性质**：HuggingFace GitHub 组织（`github.com/huggingface`）**全部 467 个公开仓库**的系统化梳理——按功能域分类，核心 51 库做「是什么 + 核心 API + 对接 work4ai 哪个系列 + 覆盖状态」卡片，全 467 库列速览附录。
>
> **为什么有这份地图**：work4ai 各讲透系列已**散点引用**了约 10 个 HF 核心库（transformers/peft/trl/diffusers/accelerate/...），但缺一份把整个 HF 生态**分类、对接、标缺口**的全景图。本地图补这个空白——它是「生态/工具」维度的导航，与 [`02-后训练信息源专题`](./02-后训练信息源专题.md) / [`03-模态专题`](./03-模态专题（NLP+Vision+Speech+多模态）.md) / [`56-AI编程语言与生态专题`](./56-AI编程语言与生态专题.md) 并列。
>
> **不做什么**：不讲原理（那是讲透系列的事），不复制库文档（那是官方 docs 的事）。只做**地图 + 对接 + 缺口诊断**。

---

## 一、元信息

| 项 | 内容 |
|---|---|
| **组织** | Hugging Face（`github.com/huggingface`）|
| **公开仓库总数** | **467**（截至 2026-08-10，GitHub API 实测）|
| **数据源** | GitHub REST API `orgs/huggingface/repos`（无认证抓取，已去重）|
| **主导语言** | **Python 230** 个（49%），Rust 31 / TypeScript 29 / Jupyter 40 / Swift 11 / MDX 9 |
| **头部门檻** | 1 万★以上 17 个，1 千★以上 ~60 个 |
| **一句话定位** | HF 不只是「模型仓库」，而是覆盖 **模型框架 / 训练 / 推理 / 数据 / 评测 / Agent / 机器人 / 语音 / 课程 / Hub** 全栈的 ML 生态系统 |
| **抓取日期** | 2026-08-10 |

### 语言分布（top）

| 语言 | 仓库数 | 角色 |
|---|---|---|
| **Python** | 230 | 绝对主导（模型/训练/数据/Agent）|
| Jupyter Notebook | 40 | 课程/教程/notebook |
| 未知 | 58 | MDX 课程 / 文档 / 配置 |
| **Rust** | 31 | 高性能推理（candle/TGI 后端/TEI/hub）|
| TypeScript | 29 | 前端/JS 生态（chat-ui/huggingface.js）|
| JavaScript | 13 | 同上 |
| Swift | 11 | Apple 端（coreml/swift-transformers）|
| MDX | 9 | 课程正文 |
| C++ | 7 | CUDA kernel |
| Shell | 6 | CLI/部署 |

### 功能域分布（按 stars 汇总排序）

| 功能域 | 仓库数 | 合计 stars | 头部仓库 |
|---|---|---|---|
| 核心模型框架 | 52 | 328,754 | transformers 163k |
| 训练/微调 | 26 | 106,916 | open-r1 26k / peft 22k / trl 19k |
| Agent | 18 | 85,018 | agents-course 31k / smolagents 29k |
| 数据/评测 | 28 | 40,442 | datasets 22k |
| 推理/部署/服务 | 14 | 30,292 | text-generation-inference 11k |
| 机器人/具身 | 10 | 26,994 | lerobot 27k |
| 语音/NLP | 6 | 24,527 | speech-to-speech 12k |
| 课程/教程 | 16 | 19,715 | deep-rl-class 5k |
| Hub/CLI/工具 | 27 | 19,412 | huggingface_hub 3.8k |
| 其它/归档 | 270 | 39,363 | nanoVLM 5k / OpenEnv 2.5k |

---

## 二、十大功能域 × 核心库卡片

> **覆盖状态图例**：✅✅ 深度（专章/多文件）｜ ✅ 中（2-3 处）｜ ✅ 浅（1 处提及）｜ ❌ 未提（缺口）
> **统计口径**：`grep -rl -i -w {库名} --include='*.md'` 在 work4ai 下命中文件数（排除 `.费曼检验.md`/`.多视角.md`），实测于 2026-08-10。

### 域 1 · 核心模型框架（52 库，328k★）

> 定义"模型长什么样"的库。transformers 是事实标准，candle 是 Rust 挑战者。

| 仓库 (stars) | 是什么 · 核心 API | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **transformers** (163k) 🐍 | 模型定义框架。`AutoModel.from_pretrained()` / `AutoTokenizer` / `Trainer` | [`讲透Transformer/11-HuggingFace源码对照`](../讲透Transformer/11-HuggingFace源码对照.md)（专章对照 modeling_llama/mixtral/deepseek_v3）、`13-Tokenizer`、[`讲透微调/06-实战`](../讲透微调/06-实战.md)、`讲透NLP/10-BERT` | ✅✅ (29 文件) |
| **pytorch-image-models** (timm) (37k) 🐍 | 最大 PyTorch 视觉 backbone 集（ResNet/ViT/ConvNeXt/Swin...）| 讲透基础模型(CV backbone)、讲透AIfor各学科-计算机视觉 | ❌ **缺口** |
| **diffusers** (34k) 🐍 | 扩散模型工具箱（SD/FLUX/视频/音频）。`DiffusionPipeline.from_pretrained()` | [`讲透生成模型`](../讲透生成模型/)、[`讲透PyTorch/09-生态全景`](../讲透PyTorch/09-PyTorch生态全景.md)、[`07-AI创意生成专题`](./07-AI创意生成专题.md) | ✅ (6) |
| **candle** (21k) 🦀 | Rust 极简 ML 框架（服务器侧推理，无 Python 依赖）| 讲透GPU与系统级(推理引擎对比) | ✅ 浅 (1) |
| **sentence-transformers** (19k) 🐍 | SBERT 嵌入/检索/rerank。`SentenceTransformer('BAAI/bge-small-zh')` | [`讲透RAG/README`](../讲透RAG/README.md)、`讲透NLP/11-RAG`、`讲透Agent/04-记忆机制` | ✅ (3) |
| **transformers.js** (16k) 📜 | 浏览器/Node.js 跑 transformers（ONNX/WASM）| （端侧推理，未来讲透AIfor职业-前端）| ❌ 缺口 |
| **tokenizers** (11k) 🦀 | Rust 写的高速分词器（BPE/Unigram/Word）| [`讲透Transformer/13-Tokenizer`](../讲透Transformer/13-Tokenizer.md)、`讲透PyTorch/09` | ✅✅ (4) |

### 域 2 · 训练/微调（26 库，107k★）

> 从 SFT 到 RL 的全栈。peft+trl+accelerate 是 LoRA/RLHF 的事实三件套。

| 仓库 (stars) | 是什么 · 核心 API | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **open-r1** (26k) 🐍 | DeepSeek-R1 的**全开源复现**（GRPO+verifiable reward）| [`讲透RL/03-RLHF-DPO-GRPO`](../讲透RL/)、讲透微调 | ❌ **重要缺口** |
| **peft** (22k) 🐍 | LoRA/QLoRA/Prefix-Tuning 等。`LoraConfig` / `get_peft_model()` | [`02-后训练信息源专题`](./02-后训练信息源专题.md)（PT-B5 专节）、`讲透微调/06-实战` | ✅✅ (22) |
| **trl** (19k) 🐍 | "post-train foundation models"。`SFTTrainer` / `GRPOTrainer` / `DPOTrainer` | [`02-后训练`](./02-后训练信息源专题.md)（PT-B6 专节 + 2026-08 实时动态）、`讲透微调/06` | ✅✅ (5) |
| **accelerate** (10k) 🐍 | 统一分布式/混合精度/FSDP/DeepSpeed。`Accelerator` | [`讲透PyTorch/09-生态全景`](../讲透PyTorch/09-PyTorch生态全景.md)、`讲透微调/06` | ✅✅ (5) |
| **smol-course** (6.7k) 📓 | "对齐小模型"课程 | 讲透公开课 | ❌ 缺口 |
| **alignment-handbook** (5.6k) 🐍 | 对齐食谱（SFT+DPO 全流程）| 讲透微调(对齐章节) | ✅ 浅 (1) |
| **autotrain-advanced** (4.6k) 🐍 | 一行命令微调。`autotrain llm --train` | [`讲透AIfor职业/11-数据科学家`](../讲透AI%20for%20职业/11-AI%20for%20数据科学家.md) | ✅ 浅 (1) |
| **smollm** (3.9k) 🐍 | SmolLM/SmolVLM 小模型家族全资源 | 讲透基础模型(小模型) | ❌ 缺口 |

### 域 3 · 推理/部署/服务（14 库，30k★）

> 生产级推理引擎。TGI 是 LLM 服务标杆，TEI 是嵌入推理。

| 仓库 (stars) | 是什么 · 核心 API | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **text-generation-inference** (TGI) (11k) 🐍🦀 | LLM 文本生成推理服务（Rust 内核+Python 包装，PagedAttention/连续批处理）| [`讲透公开课/03-AI Infra源码导读`](../讲透公开课/03-AI%20Infra%20源码导读清单.md)、讲透GPU与系统级 | ✅ 浅 (1) |
| **chat-ui** (11k) 🟦 | HuggingChat 开源前端 | （产品参考）| ❌ |
| **text-embeddings-inference** (TEI) (5k) 🦀 | 嵌入模型极速推理（Rust）| 讲透GPU与系统级、讲透RAG(检索侧) | ❌ **缺口** |
| **optimum-quanto** (1.1k) 🐍 | PyTorch 量化后端（int2/int4/int8/float8）| 讲透GPU与系统级(量化章节) | ❌ **重要缺口** |
| **optimum-nvidia** (1k) 🐍 | NVIDIA GPU 优化（TensorRT-LLM 接入）| 讲透GPU与系统级 | ❌ 缺口 |

### 域 4 · 数据/评测（28 库，40k★）

> 数据是新时代石油。datasets 是入口，datatrove 做预处理，lighteval 做评测。

| 仓库 (stars) | 是什么 · 核心 API | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **datasets** (22k) 🐍 | 数据集中心。`load_dataset()` / `Dataset.map()` | 讲透PyTorch/09、讲透NLP | ✅ (2) |
| **datatrove** (3.3k) 🐍 | 平台无关数据处理流水线（预训练数据清洗）| [`讲透数据`](../讲透数据/) | ✅ 浅 (1) |
| **lighteval** (2.5k) 🐍 | LLM 全后端评测工具包 | 讲透数据/评测、ml-experiment | ✅ 浅 (1) |
| **evaluate** (2.5k) 🐍 | 评测指标库（accuracy/BLEU/ROUGE...）| 讲透数据/评测 | ❌ 缺口 |
| **evaluation-guidebook** (2.1k) 📓 | LLM 评测实践+理论（Open LLM Leaderboard 经验）| 讲透数据/评测 | ❌ 缺口 |
| **awesome-papers** (2k) | HF 内部 science day 论文 | （论文参考）| ❌ |

### 域 5 · Agent（18 库，85k★）

> 2025-2026 最热的域。smolagents 是 HF 官方 Agent 库，agents-course 是官方课。

| 仓库 (stars) | 是什么 · 核心 API | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **agents-course** (31k) 📓 | HF 官方 Agent 课程（ReAct/CodeAgent/MCP）| [`讲透Agent`](../讲透Agent/)、讲透公开课 | ❌ **重要缺口** |
| **smolagents** (29k) 🐍 | "用代码思考"的极简 Agent 库。`CodeAgent` / `ToolCallingAgent` | [`讲透Agent/02-工具调用工程 §5.5`](../讲透Agent/02-工具调用工程.md)（code action 专节）| ✅✅ (深度) |
| **skills** (11k) 🐍 | 给 Agent 装上 HF 生态能力 | 讲透Agent(工具调用) | ✅ 浅 (2) |
| **ml-intern** (11k) 🐍 | 开源 ML 工程师 Agent（读论文/训模型/发布）| 讲透Agent(AutoML agent 案例) | ❌ 缺口 |
| **tau** (2.3k) 🐍 | Pi 极简 coding agent 的 Python 移植 | 讲透Agent(代码 agent) | ❌ |
| **OpenEnv** (2.5k) 🐍 | RL 后训练环境接口（TRL 配套）| 讲透RL(Agentic RL)、讲透Agent | ❌ 缺口 |

### 域 6 · 课程/教程（16 库，20k★）

> HF 是少数把"课程"当一等公民的开源组织。

| 仓库 (stars) | 是什么 | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **deep-rl-class** (5k) 📓 | HF 深度强化学习课 | [`讲透RL`](../讲透RL/)、讲透公开课 | ❌ **缺口** |
| **notebooks** (4.6k) 📓 | HF 库官方 notebook 集 | 讲透公开课 | ❌ |
| **diffusion-models-class** (4.4k) 📓 | 扩散模型课 | [`讲透生成模型`](../讲透生成模型/)、讲透公开课 | ❌ 缺口 |
| **cookbook** (2.7k) 📓 | 开源 AI cookbook（RAG/agent/评估）| 讲透RAG/讲透Agent | ❌ |
| **mcp-course** (910) 📓 | Model Context Protocol 课 | [`讲透Agent`](../讲透Agent/)（MCP 章节）| ❌ 缺口 |

### 域 7 · 机器人/具身（10 库，27k★）

> lerobot 一库独大，是 HF 在具身智能的押注。

| 仓库 (stars) | 是什么 · 核心 API | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **lerobot** (27k) 🐍 | 端到端机器人学习。`LeRobotDataset` / ACT/Diffusion Policy/π0 复现 | 未来**讲透具身**（核心案例）| ❌ **重要缺口** |
| lerobot-humanoid 系列 (238) | 人形机器人数据/硬件/模型 | 未来讲透具身 | ❌ |

### 域 8 · 嵌入/检索/RAG（含 setfit）

| 仓库 (stars) | 是什么 · 核心 API | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **sentence-transformers** (19k) | （见域 1）SBERT 嵌入/检索 | 讲透RAG、讲透NLP/11 | ✅ (3) |
| **setfit** (2.8k) 📓 | Sentence Transformer 少样本学习 | 讲透微调(few-shot)、讲透NLP | ❌ 缺口 |

### 域 9 · 语音/NLP（6 库，25k★）

| 仓库 (stars) | 是什么 · 核心 API | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **speech-to-speech** (12k) 🐍 | 本地语音 Agent（开源模型）| （语音 agent）| ✅ 浅 (1) |
| **parler-tts** (5.6k) 🐍 | 高质量 TTS 训练+推理 | 讲透生成模型(语音) | ❌ 缺口 |
| **distil-whisper** (4.1k) 🐍 | Whisper 蒸馏（6x 快/50% 小/WER−1%）| 讲透复用权重(蒸馏案例) | ❌ **缺口** |
| **neuralcoref** (2.9k) 🐍 | spaCy 神经共指消解 | [`讲透NLP/22-情感与共指消解`](../讲透NLP/22-情感与共指消解.md) | ❌ 缺口 |

### 域 10 · Hub/CLI/工具（27 库，19k★）

> huggingface_hub 是所有人都在用却很少单独讨论的底层库。

| 仓库 (stars) | 是什么 · 核心 API | 对接 work4ai | 覆盖 |
|---|---|---|---|
| **huggingface_hub** (3.8k) 🐍 | Hub 官方 CLI + Python 客户端。`hf download/upload` / `snapshot_download()` | （几乎所有讲透系列的底座，但未单独讲）| ❌ **缺口** |
| **blog** (3.5k) 📓 | HF 官方博客（rlhf/dpo/zph 等名篇）| [`02-后训练`](./02-后训练信息源专题.md)（已引 rlhf/dpo-trl）| ✅ 间接 |
| **knockknock** (2.8k) 🐍 | 训练结束通知（2 行代码接微信/Slack）| （工程小工具）| ❌ |
| **huggingface.js** (2.5k) 🟦 | JS 用 HF | （JS 生态）| ❌ |
| **llm-vscode** / **llm.nvim** (1.3k/1.2k) | LLM 辅助开发（VSCode/Neovim）| （开发工具）| ❌ |

---

## 三、work4ai × HuggingFace 覆盖热力图

> 按覆盖深度排序。读法：**绿色 = 已对接，红色 = 缺口**。

| HF 核心库 | stars | 覆盖深度 | 主要对接的 work4ai 系列 |
|---|---:|:---:|---|
| transformers | 163k | ✅✅ 深度 | 讲透Transformer(专章)/讲透微调/讲透NLP/讲透PyTorch |
| peft | 22k | ✅✅ 深度 | 前沿02-后训练(专节)/讲透微调 |
| tokenizers | 11k | ✅✅ 深度 | 讲透Transformer/13/讲透PyTorch/09 |
| trl | 19k | ✅✅ 深度 | 前沿02-后训练(专节+实时动态)/讲透微调 |
| accelerate | 10k | ✅✅ 深度 | 讲透PyTorch/09/讲透微调/06 |
| diffusers | 34k | ✅ 中 | 讲透生成模型/讲透PyTorch/09/前沿07 |
| sentence-transformers | 19k | ✅ 中 | 讲透RAG/讲透NLP/11/讲透Agent/04 |
| datasets | 22k | ✅ 中 | 讲透PyTorch/09/讲透NLP |
| skills | 11k | ✅ 浅 | 讲透Agent |
| smolagents | 29k | ✅✅ 深度 | 讲透Agent/02 §5.5（code action 专节）|
| candle | 21k | ✅ 浅 | （讲透GPU，可补）|
| datatrove | 3.3k | ✅ 浅 | 讲透数据 |
| lighteval | 2.5k | ✅ 浅 | 讲透数据/评测 |
| alignment-handbook | 5.6k | ✅ 浅 | 讲透微调 |
| autotrain-advanced | 4.6k | ✅ 浅 | 讲透AIfor职业/11 |
| text-generation-inference | 11k | ✅ 浅 | 讲透公开课/03 |
| speech-to-speech | 12k | ✅ 浅 | — |
| **lerobot** | **27k** | ❌ 未提 | 未来讲透具身 |
| **open-r1** | **26k** | ❌ 未提 | 讲透RL/讲透微调 |
| **agents-course** | **31k** | ❌ 未提 | 讲透Agent/讲透公开课 |
| **pytorch-image-models** | **37k** | ❌ 未提 | 讲透基础模型(CV) |
| **transformers.js** | **16k** | ❌ 未提 | 端侧推理 |
| **huggingface_hub** | 3.8k | ❌ 未提 | （全系列底座，竟未单独讲）|
| **text-embeddings-inference** | 5k | ❌ 未提 | 讲透GPU/讲透RAG |
| **optimum-quanto** | 1.1k | ❌ 未提 | 讲透GPU(量化) |
| **deep-rl-class** | 5k | ❌ 未提 | 讲透RL/讲透公开课 |
| **evaluate** | 2.5k | ❌ 未提 | 讲透数据/评测 |
| **setfit** | 2.8k | ❌ 未提 | 讲透微调(few-shot) |
| **distil-whisper** | 4.1k | ❌ 未提 | 讲透复用权重(蒸馏) |
| **ml-intern** | 11k | ❌ 未提 | 讲透Agent(AutoML) |
| **parler-tts** | 5.6k | ❌ 未提 | 讲透生成模型(语音) |
| **neuralcoref** | 2.9k | ❌ 未提 | 讲透NLP/22 |
| **mcp-course** | 910 | ❌ 未提 | 讲透Agent(MCP) |
| **diffusion-models-class** | 4.4k | ❌ 未提 | 讲透生成模型 |

**覆盖率统计**：核心 34 库中，✅✅深度 6 个（含 2026-08-10 新增 smolagents）/ ✅中 3 个 / ✅浅 8 个 = **已覆盖 17 个（50%）**；❌未提 17 个（50%）。

---

## 四、补强清单（work4ai 当前缺口，按价值排序）

> 这些是 **HF 高星核心库 × work4ai 尚未对接** 的空白，按"对接价值 × 实现难度"排序。

### 🔴 P0（高星 + 强对接价值，强烈建议补）

| 缺口库 | stars | 该补在哪 | 为什么重要 |
|---|---:|---|---|
| **lerobot** | 27k | 未来**讲透具身** | HF 在具身智能的旗舰，端到端机器人学习事实标准；work4ai 完全空白 |
| **open-r1** | 26k | [`讲透RL/03`](../讲透RL/) + 讲透微调 | DeepSeek-R1 全开源复现，GRPO+verifiable reward 的最佳实战参考；讲透RL 不能没有它 |
| **agents-course** | 31k | [`讲透Agent`](../讲透Agent/) + 讲透公开课 | HF 官方 Agent 课（ReAct/CodeAgent/MCP 全覆盖），stars 比 smolagents 还高；讲透Agent 应作为权威延伸 |
| **smolagents**（深化）| 29k | [`讲透Agent/02 §5.5`](../讲透Agent/02-工具调用工程.md) | ✅ **已完成（2026-08-10）**：在 02 篇新增 §5.5「范式跃迁：从 JSON Tool-Call 到 Code Action」专节（直觉/机制/论文证据 2402.01030+2411.01747/CodeAgent vs ToolCallingAgent 对比/选型表），横评表加 Action 形态行，总结升级为五维度 |
| **optimum-quanto** | 1.1k | [`讲透GPU与系统级`](../讲透GPU与系统级/) | HF 官方量化库（int2/4/8/fp8），讲透GPU 量化章节缺它；量化是小模型看不出损失的典型场景（见用户记忆铁律10）|

### 🟡 P1（中星 + 有对接点，建议补）

| 缺口库 | stars | 该补在哪 | 理由 |
|---|---:|---|---|
| **pytorch-image-models** (timm) | 37k | 讲透基础模型(CV backbone) | 最大视觉 backbone 集，CV 章节缺它 |
| **transformers.js** | 16k | 端侧/前端 AI | 浏览器跑 ML 的代表，AIfor职业-前端可接 |
| **deep-rl-class** | 5k | 讲透RL/讲透公开课 | HF 官方 RL 课，讲透RL 的天然配套 |
| **text-embeddings-inference** | 5k | 讲透GPU/讲透RAG | Rust 嵌入推理引擎，检索侧生产级 |
| **diffusion-models-class** | 4.4k | 讲透生成模型/讲透公开课 | HF 官方扩散课 |
| **distil-whisper** | 4.1k | 讲透复用权重(蒸馏) | 蒸馏的教科书案例（6x 快/50% 小/WER−1%）|
| **evaluate** | 2.5k | 讲透数据/评测 | 评测指标库，ml-experiment 配套 |
| **setfit** | 2.8k | 讲透微调(few-shot) | 少样本学习代表 |
| **mcp-course** | 910 | 讲透Agent(MCP) | MCP 协议官方课 |
| **huggingface_hub** | 3.8k | 全系列底座 | `hf` CLI / `snapshot_download`，所有人都在用却没单独讲，可在讲透PyTorch/09 加一节 |

### 🟢 P2（低优先，有需再补）

neuralcoref（讲透NLP/22 共指）、parler-tts（讲透生成模型 语音）、ml-intern（讲透Agent AutoML 案例）、chat-ui（产品参考）、knockknock（工程小工具）。

---

## 五、怎么用这份地图

1. **学某个 HF 库** → 先看本地图找到它属于哪个域 + 对接哪个讲透系列 → 去对应讲透系列读原理 → 回官方 docs 调 API。
2. **诊断 work4ai 覆盖** → 看热力图红色行 → 决定下一篇补哪个缺口。
3. **选型** → 同域多库对比（如推理域 TGI vs TEI vs optimum-quanto 各管什么）。

---

## 六、附录：全 467 仓库分类速览表

> 一行一个，按功能域分组，域内按 stars 降序。满足"所有内容"广度要求。`stars` 为 2026-08-10 GitHub API 实测值。

<!-- ALL_467_START -->

#### 核心模型框架（52 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 163507 | [`transformers`](https://github.com/huggingface/transformers) | Python | 🤗 Transformers: the model-definition framework for state-of-the-art ma |
| 37058 | [`pytorch-image-models`](https://github.com/huggingface/pytorch-image-models) | Python | The largest collection of PyTorch image encoders / backbones. Includin |
| 34272 | [`diffusers`](https://github.com/huggingface/diffusers) | Python | 🤗 Diffusers: State-of-the-art diffusion models for image, video, and a |
| 20874 | [`candle`](https://github.com/huggingface/candle) | Rust | Minimalist ML framework for Rust |
| 18982 | [`sentence-transformers`](https://github.com/huggingface/sentence-transformers) | Python | State-of-the-Art Embeddings, Retrieval, and Reranking |
| 16239 | [`transformers.js`](https://github.com/huggingface/transformers.js) | JavaScript | State-of-the-art Machine Learning for the web. Run 🤗 Transformers dire |
| 10955 | [`tokenizers`](https://github.com/huggingface/tokenizers) | Rust | 💥 Fast State-of-the-Art Tokenizers optimized for Research and Producti |
| 4117 | [`course`](https://github.com/huggingface/course) | MDX | The Hugging Face course on Transformers |
| 3456 | [`optimum`](https://github.com/huggingface/optimum) | Python | 🚀 Accelerate inference and training of 🤗 Transformers, Diffusers, TIMM |
| 2778 | [`setfit`](https://github.com/huggingface/setfit) | Jupyter Notebook | Efficient few-shot learning with Sentence Transformers |
| 2756 | [`swift-coreml-diffusers`](https://github.com/huggingface/swift-coreml-diffusers) | Swift | Swift app demonstrating Core ML Stable Diffusion |
| 2079 | [`transformers.js-examples`](https://github.com/huggingface/transformers.js-examples) | JavaScript | A collection of 🤗 Transformers.js demos and example applications |
| 1682 | [`swift-coreml-transformers`](https://github.com/huggingface/swift-coreml-transformers) | Swift | Swift Core ML 3 implementations of GPT-2, DistilGPT-2, BERT, and Disti |
| 1652 | [`gsplat.js`](https://github.com/huggingface/gsplat.js) | TypeScript | JavaScript Gaussian Splatting library. |
| 1522 | [`pytorch-openai-transformer-lm`](https://github.com/huggingface/pytorch-openai-transformer-lm) | Python | 🐥A PyTorch implementation of OpenAI's finetuned transformer language m |
| 1350 | [`swift-transformers`](https://github.com/huggingface/swift-transformers) | Swift | Swift Package to implement a transformers-like API in Swift |
| 1038 | [`pytorch-pretrained-BigGAN`](https://github.com/huggingface/pytorch-pretrained-BigGAN) | Python | 🦋A PyTorch implementation of BigGAN with pretrained weights and conver |
| 768 | [`ratchet`](https://github.com/huggingface/ratchet) | Rust | A cross-platform browser ML framework. |
| 596 | [`swift-chat`](https://github.com/huggingface/swift-chat) | Swift | Mac app to demonstrate swift-transformers |
| 566 | [`transformers-bloom-inference`](https://github.com/huggingface/transformers-bloom-inference) | Python | Fast Inference Solutions for BLOOM |
| 512 | [`audio-transformers-course`](https://github.com/huggingface/audio-transformers-course) | MDX | The Hugging Face Course on Transformers for Audio |
| 421 | [`tflite-android-transformers`](https://github.com/huggingface/tflite-android-transformers) | Java | DistilBERT / GPT-2 for on-device inference thanks to TensorFlow Lite w |
| 339 | [`optimum-benchmark`](https://github.com/huggingface/optimum-benchmark) | Python | 🏋️ A unified multi-backend utility for benchmarking Transformers, Timm |
| 212 | [`optimum-habana`](https://github.com/huggingface/optimum-habana) | Python | Easy and lightning fast training of 🤗 Transformers on Habana Gaudi pro |
| 200 | [`sharp-transformers`](https://github.com/huggingface/sharp-transformers) | C# | A Unity plugin for using Transformers models in Unity. |
| 135 | [`optimum-tpu`](https://github.com/huggingface/optimum-tpu) | Python | Google TPU optimizations for transformers models |
| 131 | [`transformers-research-projects`](https://github.com/huggingface/transformers-research-projects) | Python | Research projects built on top of Transformers |
| 96 | [`huggingface-inference-toolkit`](https://github.com/huggingface/huggingface-inference-toolkit) | Python | Hugging Face Inference Toolkit used to serve transformers, sentence-tr |
| 87 | [`optimum-graphcore`](https://github.com/huggingface/optimum-graphcore) | Python | Blazing fast training of 🤗 Transformers on Graphcore IPUs |
| 70 | [`image_gen_aux`](https://github.com/huggingface/image_gen_aux) | Python | Set of auxiliary tools to use with image and video generation libaries |
| 54 | [`tokenizers.js`](https://github.com/huggingface/tokenizers.js) | TypeScript | 🤗 Tokenizers.js: A pure JS/TS implementation of today's most used toke |
| 51 | [`transformers-to-mlx`](https://github.com/huggingface/transformers-to-mlx) | Python | Agent Skill to help convert transformer LLMs to mlx-lm |
| 37 | [`transformers_bloom_parallel`](https://github.com/huggingface/transformers_bloom_parallel) | Python | Techniques used to run BLOOM at inference in parallel |
| 23 | [`spm_precompiled`](https://github.com/huggingface/spm_precompiled) | Rust | Highly specialized crate to parse and use `google/sentencepiece` 's pr |
| 17 | [`transformers.js-benchmarking`](https://github.com/huggingface/transformers.js-benchmarking) | JavaScript |  |
| 14 | [`model-evaluator`](https://github.com/huggingface/model-evaluator) | Python | Evaluate Transformers from the Hub 🔥 |
| 14 | [`lor-e`](https://github.com/huggingface/lor-e) | Rust | Issue bot for transformers |
| 13 | [`candle-cublaslt`](https://github.com/huggingface/candle-cublaslt) | Rust |  |
| 12 | [`diffusers_all`](https://github.com/huggingface/diffusers_all) | - |  |
| 12 | [`candle-paged-attention`](https://github.com/huggingface/candle-paged-attention) | Cuda |  |
| 11 | [`candle-rotary`](https://github.com/huggingface/candle-rotary) | Rust |  |
| 9 | [`candle-flash-attn-v1`](https://github.com/huggingface/candle-flash-attn-v1) | C++ |  |
| 9 | [`hf-rocm-benchmark`](https://github.com/huggingface/hf-rocm-benchmark) | Python | A reproducible benchmark of Text Generation Inference and Transformers |
| 6 | [`hf-serve`](https://github.com/huggingface/hf-serve) | Python | Experimental Hugging Face API for Transformers, Diffusers and Sentence |
| 5 | [`candle-silu`](https://github.com/huggingface/candle-silu) | Rust |  |
| 5 | [`transformers-mlinter`](https://github.com/huggingface/transformers-mlinter) | Python | Lint modeling, modular, and configuration files for structural convent |
| 4 | [`candle-layer-norm`](https://github.com/huggingface/candle-layer-norm) | Cuda |  |
| 3 | [`candle_wax`](https://github.com/huggingface/candle_wax) | Rust | A testing ground for candle storage generics. |
| 2 | [`candle-extensions`](https://github.com/huggingface/candle-extensions) | C++ |  |
| 1 | [`transformers-test-ci`](https://github.com/huggingface/transformers-test-ci) | Python |  |
| 1 | [`transformers-ci`](https://github.com/huggingface/transformers-ci) | Python | CI tools for Transformers |
| 1 | [`transformers-pr-agent`](https://github.com/huggingface/transformers-pr-agent) | Python | 🤗 Transformers: the model-definition framework for state-of-the-art ma |

#### 训练/微调（26 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 26431 | [`open-r1`](https://github.com/huggingface/open-r1) | Python | Fully open reproduction of DeepSeek-R1 |
| 21524 | [`peft`](https://github.com/huggingface/peft) | Python | 🤗 PEFT: State-of-the-art Parameter-Efficient Fine-Tuning. |
| 19030 | [`trl`](https://github.com/huggingface/trl) | Python | Train transformer language models with reinforcement learning. |
| 9807 | [`accelerate`](https://github.com/huggingface/accelerate) | Python | 🚀 A simple way to launch, train, and use PyTorch models on almost any  |
| 6726 | [`smol-course`](https://github.com/huggingface/smol-course) | Jupyter Notebook | A course on aligning smol models. |
| 5656 | [`alignment-handbook`](https://github.com/huggingface/alignment-handbook) | Python | Robust recipes to align language models with human and AI preferences |
| 4599 | [`autotrain-advanced`](https://github.com/huggingface/autotrain-advanced) | Python | 🤗 AutoTrain Advanced |
| 3867 | [`smollm`](https://github.com/huggingface/smollm) | Python | Everything about the SmolLM and SmolVLM family of models |
| 2779 | [`nanotron`](https://github.com/huggingface/nanotron) | Python | Minimalistic large language model 3D-parallelism training |
| 2275 | [`picotron`](https://github.com/huggingface/picotron) | Python | Minimalistic 4D-parallelism distributed training framework for educati |
| 1755 | [`transfer-learning-conv-ai`](https://github.com/huggingface/transfer-learning-conv-ai) | Python | 🦄 State-of-the-Art Conversational AI with Transfer Learning |
| 1359 | [`finetrainers`](https://github.com/huggingface/finetrainers) | Python | Scalable and memory-optimized training of diffusion models |
| 611 | [`optimum-intel`](https://github.com/huggingface/optimum-intel) | Jupyter Notebook | 🤗 Optimum Intel: Accelerate inference with Intel optimization tools |
| 255 | [`picotron_tutorial`](https://github.com/huggingface/picotron_tutorial) | Python |  |
| 72 | [`trl-jobs`](https://github.com/huggingface/trl-jobs) | Python | Train LLM on Hugging Face infra |
| 52 | [`trl-tuto`](https://github.com/huggingface/trl-tuto) | Jupyter Notebook |  |
| 27 | [`optimum-furiosa`](https://github.com/huggingface/optimum-furiosa) | Jupyter Notebook | Accelerated inference of 🤗 models using FuriosaAI NPU chips. |
| 20 | [`accelerate-wip`](https://github.com/huggingface/accelerate-wip) | Python | 🚀 A simple way to train and use PyTorch models with multi-GPU, TPU, mi |
| 20 | [`ember`](https://github.com/huggingface/ember) | Python | ANE accelerated embedding models! |
| 19 | [`Megatron-LM`](https://github.com/huggingface/Megatron-LM) | Python | Ongoing research training transformer models at scale |
| 15 | [`peft-pytorch-conference`](https://github.com/huggingface/peft-pytorch-conference) | Jupyter Notebook | Code for the examples presented in the talk "Training a Llama in your  |
| 9 | [`Megatron-LM-Carbon`](https://github.com/huggingface/Megatron-LM-Carbon) | Python |  |
| 4 | [`autotrain-advanced-api`](https://github.com/huggingface/autotrain-advanced-api) | Dockerfile |  |
| 4 | [`autotrain-example-datasets`](https://github.com/huggingface/autotrain-example-datasets) | - |  |
| 0 | [`prime-rl`](https://github.com/huggingface/prime-rl) | - | Async RL Training at Scale |
| 0 | [`nemo-rl`](https://github.com/huggingface/nemo-rl) | - | Scalable toolkit for efficient model reinforcement |

#### 推理/部署/服务（14 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 10886 | [`text-generation-inference`](https://github.com/huggingface/text-generation-inference) | Python | Large Language Model Text Generation Inference |
| 10878 | [`chat-ui`](https://github.com/huggingface/chat-ui) | TypeScript | The open source codebase powering HuggingChat |
| 4988 | [`text-embeddings-inference`](https://github.com/huggingface/text-embeddings-inference) | Rust | A blazing fast inference solution for text embeddings models |
| 1054 | [`optimum-quanto`](https://github.com/huggingface/optimum-quanto) | Python | A pytorch quantization backend for optimum |
| 1037 | [`optimum-nvidia`](https://github.com/huggingface/optimum-nvidia) | Python |  |
| 756 | [`nfsserve`](https://github.com/huggingface/nfsserve) | Rust | A Rust NFS Server implementation |
| 267 | [`optimum-neuron`](https://github.com/huggingface/optimum-neuron) | Jupyter Notebook | Training and inference on AWS Trainium and Inferentia chips. |
| 160 | [`optimum-onnx`](https://github.com/huggingface/optimum-onnx) | Python | 🤗 Optimum ONNX: Export your model to ONNX and run inference with ONNX  |
| 135 | [`optimum-executorch`](https://github.com/huggingface/optimum-executorch) | Python | 🤗 Optimum ExecuTorch |
| 100 | [`optimum-amd`](https://github.com/huggingface/optimum-amd) | Jupyter Notebook | AMD related optimizations for transformer models |
| 22 | [`chat-ui-android`](https://github.com/huggingface/chat-ui-android) | Kotlin |  |
| 3 | [`fuser`](https://github.com/huggingface/fuser) | Rust |  |
| 3 | [`endpoints-custom-routers`](https://github.com/huggingface/endpoints-custom-routers) | Go | custom routers compatible with HF endpoints custom router feature impl |
| 3 | [`aokit`](https://github.com/huggingface/aokit) | Python | Lightweight ahead-of-time compilation toolkit for PyTorch. Used heavil |

#### 数据/评测（28 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 21826 | [`datasets`](https://github.com/huggingface/datasets) | Python | 🤗 The largest hub of ready-to-use datasets for AI models with fast, ea |
| 3255 | [`datatrove`](https://github.com/huggingface/datatrove) | Python | Freeing data processing from scripting madness by providing a set of p |
| 2511 | [`lighteval`](https://github.com/huggingface/lighteval) | Python | Lighteval is your all-in-one toolkit for evaluating LLMs across multip |
| 2475 | [`evaluate`](https://github.com/huggingface/evaluate) | Python | 🤗 Evaluate: A library for easily evaluating machine learning models an |
| 2136 | [`evaluation-guidebook`](https://github.com/huggingface/evaluation-guidebook) | Jupyter Notebook | Sharing both practical insights and theoretical knowledge about LLM ev |
| 2049 | [`awesome-papers`](https://github.com/huggingface/awesome-papers) | - | Papers & presentation materials from Hugging Face's internal science d |
| 1638 | [`aisheets`](https://github.com/huggingface/aisheets) | TypeScript | Build, enrich, and transform datasets using AI models with no code |
| 1132 | [`search-and-learn`](https://github.com/huggingface/search-and-learn) | Python | Recipes to scale inference-time compute of open models |
| 895 | [`dataset-viewer`](https://github.com/huggingface/dataset-viewer) | Python | Backend that powers the dataset viewer on Hugging Face dataset pages t |
| 724 | [`upskill`](https://github.com/huggingface/upskill) | Python | Generate and evaluate agent skills for code agents like Claude Code, O |
| 609 | [`text-clustering`](https://github.com/huggingface/text-clustering) | Python | Easily embed, cluster and semantically label text datasets |
| 275 | [`data-is-better-together`](https://github.com/huggingface/data-is-better-together) | Jupyter Notebook | Let's build better datasets, together! |
| 179 | [`olm-datasets`](https://github.com/huggingface/olm-datasets) | Python | Pipeline for pulling and processing online language model pretraining  |
| 163 | [`chug`](https://github.com/huggingface/chug) | Python | Minimal sharded dataset loaders, decoders, and utils for multi-modal d |
| 116 | [`lerobot-dataset-visualizer`](https://github.com/huggingface/lerobot-dataset-visualizer) | TypeScript | Web application for visualizing robotics datasets in LeRobot format |
| 87 | [`datasets-viewer`](https://github.com/huggingface/datasets-viewer) | Python | Viewer for the 🤗 datasets library. |
| 81 | [`video-dataset-scripts`](https://github.com/huggingface/video-dataset-scripts) | Python | Collection of scripts to build small-scale datasets for fine-tuning vi |
| 75 | [`data-measurements-tool`](https://github.com/huggingface/data-measurements-tool) | Python | Developing tools to automatically analyze datasets |
| 63 | [`personas`](https://github.com/huggingface/personas) | - | Datasets for Deep learning Personas |
| 37 | [`lerobot-annotate`](https://github.com/huggingface/lerobot-annotate) | Python | Lightweight web UI for annotating LeRobot datasets |
| 30 | [`faceberg`](https://github.com/huggingface/faceberg) | Python | Expose HuggingFace datasets as Apache Iceberg tables |
| 27 | [`pyspark_huggingface`](https://github.com/huggingface/pyspark_huggingface) | Python | PySpark custom data source for Hugging Face Datasets |
| 23 | [`datasets-tagging`](https://github.com/huggingface/datasets-tagging) | Python | A Streamlit app to add structured tags to a dataset card |
| 14 | [`community-evals`](https://github.com/huggingface/community-evals) | Python | A repository for tooling for the community to evaluate open source mod |
| 11 | [`datasets-course`](https://github.com/huggingface/datasets-course) | MDX | A course on building and sharing AI datasets |
| 6 | [`data-measurements`](https://github.com/huggingface/data-measurements) | Python | Developing tools to automatically analyze datasets |
| 3 | [`videodatasetsrecipe`](https://github.com/huggingface/videodatasetsrecipe) | Python |  |
| 2 | [`meta-agents-research-environments`](https://github.com/huggingface/meta-agents-research-environments) | Python | Meta Agents Research Environments is a comprehensive platform designed |

#### Agent（18 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 30818 | [`agents-course`](https://github.com/huggingface/agents-course) | MDX | This repository contains the Hugging Face Agents Course. |
| 28735 | [`smolagents`](https://github.com/huggingface/smolagents) | Python | 🤗 smolagents: a barebones library for agents that think in code. |
| 10906 | [`skills`](https://github.com/huggingface/skills) | Python | Give your agents the power of the Hugging Face ecosystem |
| 10727 | [`ml-intern`](https://github.com/huggingface/ml-intern) | Python | 🤗 ml-intern: an open-source ML engineer that reads papers, trains mode |
| 2256 | [`tau`](https://github.com/huggingface/tau) | Python | A Python port of Pi’s minimalist coding agent. |
| 910 | [`meshgen`](https://github.com/huggingface/meshgen) | Python | Use AI Agents directly in Blender. |
| 429 | [`hf-agents`](https://github.com/huggingface/hf-agents) | Shell | HF CLI extension to run local coding agent powered by llmfit and llama |
| 78 | [`context-course`](https://github.com/huggingface/context-course) | Python | A course on context engineering with code agents. |
| 47 | [`serge`](https://github.com/huggingface/serge) | Python | Reviews pull requests with any OpenAI-compatible LLM |
| 41 | [`agent-collabs`](https://github.com/huggingface/agent-collabs) | Python | Quickly setup the infrastructure to run a collaborative autoresearch p |
| 21 | [`is-it-agentic-enough`](https://github.com/huggingface/is-it-agentic-enough) | Python |  |
| 20 | [`physics-intern-skills`](https://github.com/huggingface/physics-intern-skills) | Shell | Agentic framework for physics |
| 7 | [`mlclaw`](https://github.com/huggingface/mlclaw) | TypeScript | ML Claw: deploy OpenClaw agents on Hugging Face |
| 7 | [`agent-manager`](https://github.com/huggingface/agent-manager) | JavaScript |  |
| 6 | [`swarm-sweeper`](https://github.com/huggingface/swarm-sweeper) | Python |  |
| 5 | [`agentcap`](https://github.com/huggingface/agentcap) | Rust | A framework to capture, analyse and export agentic sessions |
| 3 | [`research-agent`](https://github.com/huggingface/research-agent) | Python |  |
| 2 | [`hf-skills`](https://github.com/huggingface/hf-skills) | Python | Simple CLI Skill Installer/Updater for Hugging Face Skills |

#### 课程/教程（16 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 4981 | [`deep-rl-class`](https://github.com/huggingface/deep-rl-class) | MDX | This repo contains the Hugging Face Deep Reinforcement Learning Course |
| 4593 | [`notebooks`](https://github.com/huggingface/notebooks) | Jupyter Notebook | Notebooks using the Hugging Face libraries 🤗 |
| 4351 | [`diffusion-models-class`](https://github.com/huggingface/diffusion-models-class) | Jupyter Notebook | Materials for the Hugging Face Diffusion Models Course |
| 2706 | [`cookbook`](https://github.com/huggingface/cookbook) | Jupyter Notebook | Open-source AI cookbook |
| 910 | [`mcp-course`](https://github.com/huggingface/mcp-course) | MDX |  |
| 865 | [`computer-vision-course`](https://github.com/huggingface/computer-vision-course) | Jupyter Notebook | This repo is the homebase of a community driven course on Computer Vis |
| 506 | [`gpt-oss-recipes`](https://github.com/huggingface/gpt-oss-recipes) | Jupyter Notebook | Collection of scripts and notebooks for OpenAI's latest GPT OSS models |
| 179 | [`ml-for-3d-course`](https://github.com/huggingface/ml-for-3d-course) | MDX |  |
| 146 | [`robotics-course`](https://github.com/huggingface/robotics-course) | MDX | A course on robotics by Hugging Face using LeRobot. |
| 115 | [`making-games-with-ai-course`](https://github.com/huggingface/making-games-with-ai-course) | MDX | This repository contains the ML For Games Course |
| 94 | [`segment-anything-2`](https://github.com/huggingface/segment-anything-2) | Jupyter Notebook | The repository provides code for running inference with the Meta Segme |
| 88 | [`openenv-course`](https://github.com/huggingface/openenv-course) | Jupyter Notebook |  |
| 74 | [`jupyter-agent`](https://github.com/huggingface/jupyter-agent) | Python | Training LLMs to reason and analyze data with notebooks |
| 49 | [`post-training-takehome`](https://github.com/huggingface/post-training-takehome) | - | Hugging Face's take home challenge for post-training internships, now  |
| 38 | [`101-course`](https://github.com/huggingface/101-course) | - | A course on Hugging Face land |
| 20 | [`llm-course`](https://github.com/huggingface/llm-course) | - | A course on building Large Language Models |

#### 机器人/具身（10 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 26525 | [`lerobot`](https://github.com/huggingface/lerobot) | Python | 🤗 LeRobot: Making AI for Robotics more accessible with end-to-end lear |
| 238 | [`lerobot-humanoid`](https://github.com/huggingface/lerobot-humanoid) | - |  |
| 146 | [`leLab`](https://github.com/huggingface/leLab) | TypeScript | 🤗 LeLab: A web UI interface on top of LeRobot |
| 32 | [`lerobot-humanoid-hardware`](https://github.com/huggingface/lerobot-humanoid-hardware) | Python |  |
| 23 | [`lerobot-libero`](https://github.com/huggingface/lerobot-libero) | Jupyter Notebook | A fork of the official LIBERO benchmark, extended for Hugging Face’s L |
| 8 | [`lerobot-humanoid-model`](https://github.com/huggingface/lerobot-humanoid-model) | Python |  |
| 8 | [`lerobot-humanoid-runtime`](https://github.com/huggingface/lerobot-humanoid-runtime) | Python |  |
| 6 | [`lerobot-humanoid-design`](https://github.com/huggingface/lerobot-humanoid-design) | Python | Design and co-design of the next LeRobot humanoid. |
| 6 | [`lerobot-humanoid-identification`](https://github.com/huggingface/lerobot-humanoid-identification) | Python | how to identify lreobot humanoid |
| 2 | [`arxiv-robotics-sustainability-classification`](https://github.com/huggingface/arxiv-robotics-sustainability-classification) | Python | Automated pipeline for classifying ArXiv robotics papers with respect  |

#### 嵌入/检索/RAG（0 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|

#### 语音/NLP（6 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 11901 | [`speech-to-speech`](https://github.com/huggingface/speech-to-speech) | Python | Build local voice agents with open-source models |
| 5587 | [`parler-tts`](https://github.com/huggingface/parler-tts) | Python | Inference and training library for high-quality TTS models. |
| 4102 | [`distil-whisper`](https://github.com/huggingface/distil-whisper) | Python | Distilled variant of Whisper for speech recognition. 6x faster, 50% sm |
| 2894 | [`neuralcoref`](https://github.com/huggingface/neuralcoref) | C | ✨Fast Coreference Resolution in spaCy with Neural Networks |
| 35 | [`neuralcoref-viz`](https://github.com/huggingface/neuralcoref-viz) | TypeScript | ✨ Web interface for NeuralCoref coreference resolution |
| 8 | [`neuralcoref-models`](https://github.com/huggingface/neuralcoref-models) | - | ✨ Models for the NeuralCoref coreference resolution module |

#### Hub/CLI/工具（27 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 3792 | [`huggingface_hub`](https://github.com/huggingface/huggingface_hub) | Python | The official CLI and Python client for the Hugging Face Hub. |
| 3494 | [`blog`](https://github.com/huggingface/blog) | Jupyter Notebook | Public repo for HF blog posts |
| 2826 | [`knockknock`](https://github.com/huggingface/knockknock) | Python | 🚪✊Knock Knock: Get notified when your training ends with only two addi |
| 2487 | [`huggingface.js`](https://github.com/huggingface/huggingface.js) | TypeScript | Use Hugging Face with JavaScript |
| 1313 | [`llm-vscode`](https://github.com/huggingface/llm-vscode) | TypeScript | LLM powered development for VSCode |
| 1186 | [`llm.nvim`](https://github.com/huggingface/llm.nvim) | Lua | LLM powered development for Neovim |
| 1089 | [`awesome-huggingface`](https://github.com/huggingface/awesome-huggingface) | - | 🤗 A list of wonderful open-source projects & applications integrated w |
| 879 | [`llm-ls`](https://github.com/huggingface/llm-ls) | Rust | LSP server leveraging LLMs for code completion (and more?) |
| 777 | [`hf-mount`](https://github.com/huggingface/hf-mount) | Rust | Mount Hugging Face Buckets and repos as local filesystems. No download |
| 555 | [`xet-core`](https://github.com/huggingface/xet-core) | Rust | xet client tech, used in huggingface_hub |
| 321 | [`hf-hub`](https://github.com/huggingface/hf-hub) | Rust | Rust client for the huggingface hub aiming for minimal subset of featu |
| 272 | [`hf-mcp-server`](https://github.com/huggingface/hf-mcp-server) | TypeScript | Hugging Face MCP Server |
| 159 | [`hf-sandbox`](https://github.com/huggingface/hf-sandbox) | Python | Modal-style sandbox API on top of Hugging Face Jobs |
| 39 | [`hf-discover`](https://github.com/huggingface/hf-discover) | Python | Agentic Resource Discovery Client/Server |
| 35 | [`rlhf-interface`](https://github.com/huggingface/rlhf-interface) | Python |  |
| 29 | [`hf-nix`](https://github.com/huggingface/hf-nix) | Nix |  |
| 27 | [`hf-endpoints-documentation`](https://github.com/huggingface/hf-endpoints-documentation) | JavaScript |  |
| 26 | [`hf-endpoints-emulator`](https://github.com/huggingface/hf-endpoints-emulator) | Python | Local emulator for Hugging Face Inference Endpoints customer handlers |
| 25 | [`huggingface_hub_rust`](https://github.com/huggingface/huggingface_hub_rust) | Rust | Comprehensive Hugging Face Hub Library for rust |
| 24 | [`hf-rocm-kernels`](https://github.com/huggingface/hf-rocm-kernels) | Python |  |
| 16 | [`hf-claude`](https://github.com/huggingface/hf-claude) | Shell | Launch Claude Code with Hugging Face Inference Providers |
| 13 | [`widgets-server`](https://github.com/huggingface/widgets-server) | TypeScript | Public helpers for huggingface.co. Now lives in https://github.com/hug |
| 12 | [`hf-csi-driver`](https://github.com/huggingface/hf-csi-driver) | Go | CSI driver for mounting HuggingFace Buckets and Repos as FUSE filesyst |
| 8 | [`hf-workflows`](https://github.com/huggingface/hf-workflows) | - |  |
| 4 | [`hf-inference`](https://github.com/huggingface/hf-inference) | Python | CLI extension for `hf` to run inference with Hugging Face Inference Pr |
| 2 | [`hf-jobs-action`](https://github.com/huggingface/hf-jobs-action) | JavaScript |  |
| 2 | [`hf-image`](https://github.com/huggingface/hf-image) | Python | Fast, Xet-native push/pull for the Hugging Face container registry (cr |

#### 其它/归档（270 个）
| stars | 仓库 | 语言 | 简介 |
|---|---|---|---|
| 4982 | [`nanoVLM`](https://github.com/huggingface/nanoVLM) | Python | The simplest, fastest repository for training/finetuning small-sized V |
| 2490 | [`OpenEnv`](https://github.com/huggingface/OpenEnv) | Python | An interface library for RL post training with environments. |
| 1961 | [`chat-macOS`](https://github.com/huggingface/chat-macOS) | Swift | Making the community's best AI chat models available to everyone. |
| 1419 | [`Mongoku`](https://github.com/huggingface/Mongoku) | Svelte | 🔥The Web-scale GUI for MongoDB |
| 1195 | [`hmtl`](https://github.com/huggingface/hmtl) | Python | 🌊HMTL: Hierarchical Multi-Task Learning - A State-of-the-Art neural ne |
| 1173 | [`Math-Verify`](https://github.com/huggingface/Math-Verify) | Python |  |
| 921 | [`torchMoji`](https://github.com/huggingface/torchMoji) | Python | 😇A pyTorch implementation of the DeepMoji model: state-of-the-art deep |
| 917 | [`AnyLanguageModel`](https://github.com/huggingface/AnyLanguageModel) | Swift | An API-compatible, drop-in replacement for Apple's Foundation Models f |
| 724 | [`naacl_transfer_learning_tutorial`](https://github.com/huggingface/naacl_transfer_learning_tutorial) | Python | Repository of code for the tutorial on Transfer Learning in NLP held a |
| 723 | [`kernels`](https://github.com/huggingface/kernels) | Python | Build compute kernels and load them from the Hub. |
| 711 | [`huggingface-llama-recipes`](https://github.com/huggingface/huggingface-llama-recipes) | Jupyter Notebook |  |
| 698 | [`exporters`](https://github.com/huggingface/exporters) | Python | Export Hugging Face models to Core ML and TensorFlow Lite |
| 582 | [`hub-docs`](https://github.com/huggingface/hub-docs) | Handlebars | Docs of the Hugging Face Hub |
| 578 | [`hf_transfer`](https://github.com/huggingface/hf_transfer) | Rust |  |
| 573 | [`cosmopedia`](https://github.com/huggingface/cosmopedia) | Python |  |
| 566 | [`llm_training_handbook`](https://github.com/huggingface/llm_training_handbook) | Python | An open collection of methodologies to help with successful training o |
| 551 | [`pytorch_block_sparse`](https://github.com/huggingface/pytorch_block_sparse) | C++ | Fast Block Sparse Matrices for Pytorch |
| 504 | [`large_language_model_training_playbook`](https://github.com/huggingface/large_language_model_training_playbook) | Python | An open collection of implementation tips, tricks and resources for tr |
| 497 | [`controlnet_aux`](https://github.com/huggingface/controlnet_aux) | Python |  |
| 489 | [`Repo2RLEnv`](https://github.com/huggingface/Repo2RLEnv) | Python | Convert any Repo into an RL Environment |
| 465 | [`node-question-answering`](https://github.com/huggingface/node-question-answering) | TypeScript | Fast and production-ready question answering in Node.js |
| 455 | [`yourbench`](https://github.com/huggingface/yourbench) | HTML | 🤗 Benchmark Large Language Models Reliably On Your Data |
| 455 | [`screenenv`](https://github.com/huggingface/screenenv) | Python | A powerful Python library for creating and managing isolated desktop e |
| 427 | [`community-events`](https://github.com/huggingface/community-events) | Jupyter Notebook | Place where folks can contribute to 🤗 community events |
| 413 | [`sam2-studio`](https://github.com/huggingface/sam2-studio) | Swift |  |
| 409 | [`nn_pruning`](https://github.com/huggingface/nn_pruning) | Jupyter Notebook | Prune a model while finetuning or training. |
| 402 | [`gpu-fryer`](https://github.com/huggingface/gpu-fryer) | Rust | Where GPUs get cooked 👩‍🍳🔥 |
| 400 | [`dataspeech`](https://github.com/huggingface/dataspeech) | Python |  |
| 389 | [`education-toolkit`](https://github.com/huggingface/education-toolkit) | Jupyter Notebook | Educational materials for universities |
| 385 | [`nanowhale`](https://github.com/huggingface/nanowhale) | Python |  |
| 384 | [`local-gemma`](https://github.com/huggingface/local-gemma) | Python | Gemma 2 optimized for your local machine. |
| 360 | [`unity-api`](https://github.com/huggingface/unity-api) | C# |  |
| 359 | [`open-muse`](https://github.com/huggingface/open-muse) | Python | Open reproduction of MUSE for fast text2image generation. |
| 358 | [`speechbox`](https://github.com/huggingface/speechbox) | Python |  |
| 347 | [`ai-deadlines`](https://github.com/huggingface/ai-deadlines) | TypeScript | ⏰ AI conference deadline countdowns |
| 345 | [`datablations`](https://github.com/huggingface/datablations) | Jupyter Notebook | Scaling Data-Constrained Language Models |
| 337 | [`100-times-faster-nlp`](https://github.com/huggingface/100-times-faster-nlp) | HTML | 🚀100 Times Faster Natural Language Processing in Python - iPython note |
| 328 | [`diarizers`](https://github.com/huggingface/diarizers) | Python |  |
| 304 | [`huggingface-gemma-recipes`](https://github.com/huggingface/huggingface-gemma-recipes) | Jupyter Notebook | Inference, Fine Tuning and many more recipes with Gemma family of mode |
| 291 | [`llm-swarm`](https://github.com/huggingface/llm-swarm) | Python | Manage scalable open LLM inference endpoints in Slurm clusters |
| 265 | [`coreml-examples`](https://github.com/huggingface/coreml-examples) | Jupyter Notebook | Swift Core ML Examples |
| 257 | [`fineweb-2`](https://github.com/huggingface/fineweb-2) | Python |  |
| 250 | [`instruction-tuned-sd`](https://github.com/huggingface/instruction-tuned-sd) | Python | Code for instruction-tuning Stable Diffusion. |
| 235 | [`open_asr_leaderboard`](https://github.com/huggingface/open_asr_leaderboard) | Python |  |
| 235 | [`diffusion-fast`](https://github.com/huggingface/diffusion-fast) | Python | Faster generation with text-to-image diffusion models. |
| 235 | [`responses.js`](https://github.com/huggingface/responses.js) | TypeScript | A lightweight express.js server implementing OpenAI’s Responses API, b |
| 230 | [`gym-hil`](https://github.com/huggingface/gym-hil) | Python | Human in the loop Reinforcement Learning suite |
| 217 | [`OBELICS`](https://github.com/huggingface/OBELICS) | Python | Code used for the creation of OBELICS, an open, massive and curated co |
| 214 | [`gym-aloha`](https://github.com/huggingface/gym-aloha) | Python | A gym environment for ALOHA |
| 213 | [`kernel-builder`](https://github.com/huggingface/kernel-builder) | Nix | 👷 Build compute kernels |
| 213 | [`large-scale-image-deduplication`](https://github.com/huggingface/large-scale-image-deduplication) | Python |  |
| 205 | [`carbon`](https://github.com/huggingface/carbon) | Python | The home of Carbon Genomic Foundation Model 🧬 |
| 196 | [`VLAb`](https://github.com/huggingface/VLAb) | Python |  |
| 195 | [`simulate`](https://github.com/huggingface/simulate) | Python | 🎢 Creating and sharing simulation environments for embodied and synthe |
| 194 | [`gym-pusht`](https://github.com/huggingface/gym-pusht) | Python | A gym environment for PushT |
| 189 | [`HuggingSnap`](https://github.com/huggingface/HuggingSnap) | Swift | SmolVLM2 Demo |
| 188 | [`finepdfs`](https://github.com/huggingface/finepdfs) | Python | Codebase for FinePDFs |
| 186 | [`jat`](https://github.com/huggingface/jat) | Python | General multi-task deep RL Agent |
| 182 | [`frp`](https://github.com/huggingface/frp) | Go | FRP Fork |
| 182 | [`Google-Cloud-Containers`](https://github.com/huggingface/Google-Cloud-Containers) | Dockerfile | Hugging Face Deep Learning Containers (DLCs) for Google Cloud |
| 175 | [`api-inference-community`](https://github.com/huggingface/api-inference-community) | Python |  |
| 172 | [`flux-fast`](https://github.com/huggingface/flux-fast) | Python | Making Flux go brrr on GPUs. |
| 169 | [`swift-huggingface`](https://github.com/huggingface/swift-huggingface) | Swift | A Swift client for Hugging Face Hub and Inference Providers APIs |
| 168 | [`inference-benchmarker`](https://github.com/huggingface/inference-benchmarker) | Rust | Inference server benchmarking tool |
| 151 | [`workshops`](https://github.com/huggingface/workshops) | Jupyter Notebook | Materials for workshops on the Hugging Face ecosystem |
| 145 | [`screensuite`](https://github.com/huggingface/screensuite) | Python | ScreenSuite - The most comprehensive benchmarking suite for GUI Agents |
| 140 | [`doc-builder`](https://github.com/huggingface/doc-builder) | Python | The package used to build the documentation of our Hugging Face repos |
| 137 | [`smol2operator`](https://github.com/huggingface/smol2operator) | Python |  |
| 136 | [`kernels-community`](https://github.com/huggingface/kernels-community) | C++ | Kernel sources for https://huggingface.co/kernels-community |
| 132 | [`swift-jinja`](https://github.com/huggingface/swift-jinja) | Swift | A minimalistic Swift implementation of the Jinja templating engine, sp |
| 124 | [`competitions`](https://github.com/huggingface/competitions) | Python |  |
| 122 | [`visual-blocks-custom-components`](https://github.com/huggingface/visual-blocks-custom-components) | TypeScript | Custom Hugging Face Nodes for Google Visual Blocks for ML |
| 102 | [`fineVideo`](https://github.com/huggingface/fineVideo) | Python |  |
| 100 | [`cadgenbench`](https://github.com/huggingface/cadgenbench) | Python | A benchmark for AI-driven CAD generation and editing |
| 98 | [`olm-training`](https://github.com/huggingface/olm-training) | Python | Repo for training MLMs, CLMs, or T5-type models on the OLM pretraining |
| 97 | [`huggingface_sb3`](https://github.com/huggingface/huggingface_sb3) | Jupyter Notebook | Additional code for Stable-baselines3 to load and upload models from t |
| 93 | [`huggingface-vscode-chat`](https://github.com/huggingface/huggingface-vscode-chat) | TypeScript | A VSCode extension to use Hugging Face Inference Providers in Copilot  |
| 89 | [`amused`](https://github.com/huggingface/amused) | Python |  |
| 88 | [`tune`](https://github.com/huggingface/tune) | Python |  |
| 87 | [`fuego`](https://github.com/huggingface/fuego) | Python | [WIP] A 🔥 interface for running code in the cloud |
| 85 | [`llm-intellij`](https://github.com/huggingface/llm-intellij) | Kotlin | LLM powered development for IntelliJ |
| 83 | [`block_movement_pruning`](https://github.com/huggingface/block_movement_pruning) | Python | Block Sparse movement pruning |
| 82 | [`pi-llama`](https://github.com/huggingface/pi-llama) | TypeScript | Pi coding agent extension: llama.cpp provider with dynamic model + con |
| 76 | [`hfapi`](https://github.com/huggingface/hfapi) | Python | Simple Python client for the Hugging Face Inference API |
| 76 | [`gym-xarm`](https://github.com/huggingface/gym-xarm) | Python | A gym environment for xArm |
| 72 | [`paper-style-guide`](https://github.com/huggingface/paper-style-guide) | - |  |
| 72 | [`grout`](https://github.com/huggingface/grout) | Rust | Testbed for LLM inference with cutile-rs. |
| 70 | [`disaggregators`](https://github.com/huggingface/disaggregators) | Python | 🤗 Disaggregators: Curated data labelers for in-depth analysis. |
| 66 | [`bloom-jax-inference`](https://github.com/huggingface/bloom-jax-inference) | Python |  |
| 66 | [`ai-blueprint`](https://github.com/huggingface/ai-blueprint) | Jupyter Notebook | A blueprint for AI development, focusing on applied examples of RAG, i |
| 65 | [`that_is_good_data`](https://github.com/huggingface/that_is_good_data) | - |  |
| 60 | [`hffs`](https://github.com/huggingface/hffs) | Python | **ARCHIVED** Filesystem interface to 🤗 Hub |
| 59 | [`m4-logs`](https://github.com/huggingface/m4-logs) | - | M4 experiment logbook |
| 52 | [`discord-bots`](https://github.com/huggingface/discord-bots) | Python |  |
| 50 | [`zapier`](https://github.com/huggingface/zapier) | JavaScript | Hugging Face's Zapier Integration 🤗⚡️ |
| 49 | [`ml-agents`](https://github.com/huggingface/ml-agents) | C# | Unity Machine Learning Agents Toolkit |
| 49 | [`inference-playground`](https://github.com/huggingface/inference-playground) | Svelte |  |
| 46 | [`physics-intern`](https://github.com/huggingface/physics-intern) | Python | An agentic framework for solving scientific research problems |
| 42 | [`latex2sympy2_extended`](https://github.com/huggingface/latex2sympy2_extended) | Python | Parse LaTeX math expressions |
| 42 | [`ioi`](https://github.com/huggingface/ioi) | Python |  |
| 41 | [`adversarialnlp`](https://github.com/huggingface/adversarialnlp) | Python | A generic library for crafting adversarial NLP examples - WIP |
| 40 | [`bert-syntax`](https://github.com/huggingface/bert-syntax) | Python | Assessing syntactic abilities of BERT |
| 40 | [`AIEnergyScore`](https://github.com/huggingface/AIEnergyScore) | Python | AI Energy Score: Initiative to establish comparable energy efficiency  |
| 40 | [`gym-genesis`](https://github.com/huggingface/gym-genesis) | Python | A gym environment for GENESIS |
| 37 | [`lm-evaluation-harness`](https://github.com/huggingface/lm-evaluation-harness) | Python | A framework for few-shot evaluation of language models. |
| 37 | [`hub-tutorials`](https://github.com/huggingface/hub-tutorials) | Jupyter Notebook |  |
| 34 | [`tgi-gaudi`](https://github.com/huggingface/tgi-gaudi) | Python | Large Language Model Text Generation Inference on Habana Gaudi |
| 32 | [`lora-fast`](https://github.com/huggingface/lora-fast) | Python | Minimal repository to demonstrate fast LoRA inference with Flux family |
| 32 | [`pwc-cli`](https://github.com/huggingface/pwc-cli) | Python | A Command-Line Interface (CLI) and Skill to interact with Papers with  |
| 30 | [`model_card`](https://github.com/huggingface/model_card) | - |  |
| 30 | [`swift-xet`](https://github.com/huggingface/swift-xet) | Swift | A Swift implementation of the Xet protocol |
| 29 | [`rasa_hmtl`](https://github.com/huggingface/rasa_hmtl) | Python | RASA wrapper for HMTL: Hierarchical Multi-Task Learning |
| 27 | [`dataset-dedupe-estimator`](https://github.com/huggingface/dataset-dedupe-estimator) | Jupyter Notebook | parquet dedupe estimator |
| 27 | [`wikirace-llms`](https://github.com/huggingface/wikirace-llms) | TypeScript |  |
| 27 | [`finephrase`](https://github.com/huggingface/finephrase) | Python | Synthetic pretraining data by rephrasing the web |
| 26 | [`xlnet`](https://github.com/huggingface/xlnet) | Python | XLNet: Generalized Autoregressive Pretraining for Language Understandi |
| 26 | [`movie-shot-categorizer`](https://github.com/huggingface/movie-shot-categorizer) | Jupyter Notebook | Fine-tune of Florence-2 for shot categorization. |
| 25 | [`pyo3-special-method-derive`](https://github.com/huggingface/pyo3-special-method-derive) | Rust | Automatically derive Python dunder methods for your Rust code |
| 24 | [`pixparse`](https://github.com/huggingface/pixparse) | Python | Pixel Parsing. A reproduction of OCR-free end-to-end document understa |
| 24 | [`docmatix`](https://github.com/huggingface/docmatix) | Python | A huge dataset for Document Visual Question Answering |
| 23 | [`leaderboards`](https://github.com/huggingface/leaderboards) | - |  |
| 22 | [`hub-sync`](https://github.com/huggingface/hub-sync) | - | A GitHub Action that syncs your GitHub repository to Hugging Face Hub  |
| 21 | [`tailscale-action`](https://github.com/huggingface/tailscale-action) | - | Github action to connect to tailscale |
| 20 | [`distill-bloom-deepspeed`](https://github.com/huggingface/distill-bloom-deepspeed) | Python | Teacher - student distillation using DeepSpeed |
| 20 | [`gaia`](https://github.com/huggingface/gaia) | Jupyter Notebook | Hugging Face and Pyserini interoperability |
| 20 | [`semver-release-action`](https://github.com/huggingface/semver-release-action) | JavaScript |  |
| 20 | [`dedupe_estimator`](https://github.com/huggingface/dedupe_estimator) | C++ | Chunk Dedupe Estimation |
| 18 | [`hf_benchmarks`](https://github.com/huggingface/hf_benchmarks) | Python | A starter kit for evaluating benchmarks on the 🤗 Hub |
| 17 | [`inference-providers-starter-app`](https://github.com/huggingface/inference-providers-starter-app) | TypeScript |  |
| 16 | [`ethics-scripts`](https://github.com/huggingface/ethics-scripts) | Python |  |
| 16 | [`ml-agents-patch`](https://github.com/huggingface/ml-agents-patch) | C# | The Unity Machine Learning Agents Toolkit (ML-Agents) is an open-sourc |
| 16 | [`Huggy`](https://github.com/huggingface/Huggy) | - | Huggy is a Unity ML-Agents environment showcasing a dog mastering stic |
| 16 | [`prettier-plugin-vertical-align`](https://github.com/huggingface/prettier-plugin-vertical-align) | TypeScript | Align object properties and interface members vertically for JS/TS cod |
| 16 | [`Microsoft-Azure`](https://github.com/huggingface/Microsoft-Azure) | Makefile | Hugging Face on Microsoft Azure (documentation, examples and more) |
| 16 | [`gpu-mode-openenv`](https://github.com/huggingface/gpu-mode-openenv) | - | A repo of resource for the GPU Mode talk on OpenEnv. |
| 15 | [`hugs-docs`](https://github.com/huggingface/hugs-docs) | - | Official Documentation for HUGS |
| 15 | [`feel`](https://github.com/huggingface/feel) | Python |  |
| 15 | [`Qwen2.5-Coder`](https://github.com/huggingface/Qwen2.5-Coder) | - | Qwen2.5-Coder is the code version of Qwen2.5, the large language model |
| 14 | [`snapchat-lens-api`](https://github.com/huggingface/snapchat-lens-api) | - | Type definitions for Snapchat Lenses scripting |
| 14 | [`Unity-WebGL-template-for-Hugging-Face-Spaces`](https://github.com/huggingface/Unity-WebGL-template-for-Hugging-Face-Spaces) | - | Unity WebGL template for Hugging Face Spaces |
| 14 | [`faq`](https://github.com/huggingface/faq) | - | FAQ about Hugging Face and Open Source |
| 14 | [`funes`](https://github.com/huggingface/funes) | Rust | Durable, searchable memory of your past agent sessions. |
| 13 | [`FastChat`](https://github.com/huggingface/FastChat) | Python | An open platform for training, serving, and evaluating large language  |
| 12 | [`ethics-education`](https://github.com/huggingface/ethics-education) | - | AI Ethics educational material 🤗 |
| 12 | [`hfendpoints`](https://github.com/huggingface/hfendpoints) | Rust | SDK for creating Hugging Face Inference Endpoints deployments |
| 12 | [`trending-deploy`](https://github.com/huggingface/trending-deploy) | Python |  |
| 12 | [`jobs-actions`](https://github.com/huggingface/jobs-actions) | Python | Run GitHub Actions on Hugging Face Jobs |
| 11 | [`efficient_scripts`](https://github.com/huggingface/efficient_scripts) | Python |  |
| 11 | [`gguf-jinja-analysis`](https://github.com/huggingface/gguf-jinja-analysis) | Rust |  |
| 11 | [`dell-ai`](https://github.com/huggingface/dell-ai) | Python | The official Python SDK and CLI for the Dell Enterprise Hub |
| 11 | [`chat-template-playground`](https://github.com/huggingface/chat-template-playground) | TypeScript | Chat Template Playground for testing & debugging |
| 10 | [`awd-lstm-lm`](https://github.com/huggingface/awd-lstm-lm) | Python |  |
| 10 | [`roots-search-tool`](https://github.com/huggingface/roots-search-tool) | Jupyter Notebook | Scripts supporting the development and serving the Roots Search Tool - |
| 10 | [`khipu_workshop`](https://github.com/huggingface/khipu_workshop) | Jupyter Notebook |  |
| 10 | [`tei-gaudi`](https://github.com/huggingface/tei-gaudi) | Rust | A blazing fast inference solution for text embeddings models |
| 10 | [`ultravox`](https://github.com/huggingface/ultravox) | Python | A fast multimodal LLM for real-time voice |
| 10 | [`hugex`](https://github.com/huggingface/hugex) | TypeScript | Coding agent user interface |
| 10 | [`paperswithcode-feedback`](https://github.com/huggingface/paperswithcode-feedback) | - | A repository to let people list feedback on paperswithcode. |
| 10 | [`AIFS-single-2.0-on-all-GPUs`](https://github.com/huggingface/AIFS-single-2.0-on-all-GPUs) | Jupyter Notebook | Patch and tutorial to run AIFS single 2.0 using Hugging Face jobs or l |
| 9 | [`gym-games`](https://github.com/huggingface/gym-games) | - | A gym version of various games for reinforcenment learning. |
| 9 | [`autogptq-index`](https://github.com/huggingface/autogptq-index) | HTML | A GitHub Pages hosting AutoGPTQ wheels |
| 9 | [`environments`](https://github.com/huggingface/environments) | Python |  |
| 9 | [`finetranslations`](https://github.com/huggingface/finetranslations) | Python | Source code for the FineTranslations dataset |
| 9 | [`sandbox-server`](https://github.com/huggingface/sandbox-server) | Rust | Static in-sandbox server for 'hf sandbox' — command exec, file transfe |
| 8 | [`diff2html`](https://github.com/huggingface/diff2html) | TypeScript | Pretty diff to html javascript library (diff2html) |
| 8 | [`allennlp`](https://github.com/huggingface/allennlp) | Python | An open-source NLP research library, built on PyTorch. |
| 8 | [`flappy-bird-gym`](https://github.com/huggingface/flappy-bird-gym) | Python | An OpenAI Gym environment for the Flappy Bird game |
| 8 | [`Qwen2.5-Math`](https://github.com/huggingface/Qwen2.5-Math) | Python | A series of math-specific large language models of our Qwen2 series. |
| 8 | [`hugs-helm-chart`](https://github.com/huggingface/hugs-helm-chart) | Smarty | Official Helm Chart for HUGS |
| 7 | [`rl-baselines3-zoo-update`](https://github.com/huggingface/rl-baselines3-zoo-update) | Python | A training framework for Stable Baselines3 reinforcement learning agen |
| 7 | [`mlintern-plugin`](https://github.com/huggingface/mlintern-plugin) | JavaScript |  |
| 7 | [`moon-ide`](https://github.com/huggingface/moon-ide) | Rust | IDE for moon team |
| 6 | [`collaborative-training-auth`](https://github.com/huggingface/collaborative-training-auth) | Python | Collaborative Hub Training Authentication API server-side machinery |
| 6 | [`helm-common`](https://github.com/huggingface/helm-common) | Mustache | Common chart for our helm charts |
| 6 | [`llm-perf-backend`](https://github.com/huggingface/llm-perf-backend) | Python | Backend for the llm-perf leaderboard space |
| 5 | [`s3prl`](https://github.com/huggingface/s3prl) | - | Self-Supervised Speech Pre-training and Representation Learning Toolki |
| 5 | [`tensorboard`](https://github.com/huggingface/tensorboard) | - | TensorFlow's Visualization Toolkit |
| 5 | [`stable-baselines3`](https://github.com/huggingface/stable-baselines3) | Python | PyTorch version of Stable Baselines, reliable implementations of reinf |
| 5 | [`helm-publish-action`](https://github.com/huggingface/helm-publish-action) | - | Github Action to simplify Helm Chart publish into a registry |
| 5 | [`python-readability`](https://github.com/huggingface/python-readability) | Python | fast python port of arc90's readability tool, updated to match latest  |
| 5 | [`Unity-MLAgents-LoadFromHub-Assets`](https://github.com/huggingface/Unity-MLAgents-LoadFromHub-Assets) | - | Unity scripts and UI for easily loading models from the Hugging Face H |
| 5 | [`bench_cluster`](https://github.com/huggingface/bench_cluster) | Python |  |
| 5 | [`tau2-bench`](https://github.com/huggingface/tau2-bench) | Python | τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environme |
| 5 | [`mcp-bench`](https://github.com/huggingface/mcp-bench) | Python | MCP-Bench: Benchmarking Tool-Using LLM Agents with Complex Real-World  |
| 5 | [`security-workflows`](https://github.com/huggingface/security-workflows) | - | Centralized security workflows: CodeQL analysis, Octoscan, and permiss |
| 5 | [`vllm-xet-loader`](https://github.com/huggingface/vllm-xet-loader) | Python | vLLM zero-copy model loader via xet CAS |
| 4 | [`neural-compressor`](https://github.com/huggingface/neural-compressor) | Python | Intel® Neural Compressor (formerly known as Intel® Low Precision Optim |
| 4 | [`huggingface-sagemaker-snowflake-example`](https://github.com/huggingface/huggingface-sagemaker-snowflake-example) | Python |  |
| 4 | [`ML-Agents-Training-Executables`](https://github.com/huggingface/ML-Agents-Training-Executables) | - | This repo contains the Unity ML-Agents environments' executables for W |
| 4 | [`alpaca_eval`](https://github.com/huggingface/alpaca_eval) | Jupyter Notebook | An automatic evaluator for instruction-following language models. Huma |
| 4 | [`llm-awq`](https://github.com/huggingface/llm-awq) | - | AWQ: Activation-aware Weight Quantization for LLM Compression and Acce |
| 4 | [`llm-academy`](https://github.com/huggingface/llm-academy) | Jupyter Notebook | LLM Academy |
| 4 | [`MixEval`](https://github.com/huggingface/MixEval) | - | The official evaluation suite and dynamic data release for MixEval. |
| 4 | [`how-to-release-on-the-hub`](https://github.com/huggingface/how-to-release-on-the-hub) | - |  |
| 4 | [`dell-helm-chart`](https://github.com/huggingface/dell-helm-chart) | Go Template | Helm Chart for the Dell Enterprise Hub |
| 4 | [`rocm-nix`](https://github.com/huggingface/rocm-nix) | Nix | ROCm overlay for TGI and kernel-builder |
| 4 | [`mergekit`](https://github.com/huggingface/mergekit) | Python | Tools for merging pretrained large language models. |
| 4 | [`gorilla`](https://github.com/huggingface/gorilla) | Python | Gorilla: Training and Evaluating LLMs for Function Calls (Tool Calls) |
| 4 | [`boomtitan`](https://github.com/huggingface/boomtitan) | Python | fork of torchtitan for the boom project |
| 4 | [`pr-search-cli`](https://github.com/huggingface/pr-search-cli) | Python | CLI for accessing PR Similarity Search for Agent PR management |
| 3 | [`doc-build-dev`](https://github.com/huggingface/doc-build-dev) | - |  |
| 3 | [`Snowball-Target`](https://github.com/huggingface/Snowball-Target) | - | Snowball Target is a Unity ML-Agents environment where you need to tra |
| 3 | [`VLMEvalKit`](https://github.com/huggingface/VLMEvalKit) | Python | Open-source evaluation toolkit of large vision-language models (LVLMs) |
| 3 | [`AgentLite`](https://github.com/huggingface/AgentLite) | - |  |
| 3 | [`ai-hardware-leaderboard`](https://github.com/huggingface/ai-hardware-leaderboard) | Python |  |
| 3 | [`prime`](https://github.com/huggingface/prime) | Python | prime is a framework for efficient, globally distributed training of A |
| 3 | [`kernels-benchmarks`](https://github.com/huggingface/kernels-benchmarks) | Python | Benchmarks for the HuggingFace Kernel Community kernels |
| 3 | [`PipelineRL`](https://github.com/huggingface/PipelineRL) | Python | A scalable asynchronous reinforcement learning implementation with in- |
| 3 | [`deep-learning-containers`](https://github.com/huggingface/deep-learning-containers) | Python | One stop shop for running AI/ML on AWS. |
| 3 | [`inspect_evals`](https://github.com/huggingface/inspect_evals) | Python | Collection of evals for Inspect AI |
| 3 | [`kernel-builder-job`](https://github.com/huggingface/kernel-builder-job) | JavaScript |  |
| 3 | [`physics-intern-claude-plugin`](https://github.com/huggingface/physics-intern-claude-plugin) | Python | Claude Code plugin to bootstrap a PhysicsIntern research workspace |
| 3 | [`pi-local-router`](https://github.com/huggingface/pi-local-router) | Python | Pi extension for routing between llama.cpp and Hugging Face Inference  |
| 2 | [`rl-baselines3-zoo`](https://github.com/huggingface/rl-baselines3-zoo) | Python | A training framework for Stable Baselines3 reinforcement learning agen |
| 2 | [`RL-model-card-template`](https://github.com/huggingface/RL-model-card-template) | - | Model card template |
| 2 | [`amazon-eks-ami`](https://github.com/huggingface/amazon-eks-ami) | Shell | Packer configuration for building a custom EKS AMI |
| 2 | [`ViZDoom`](https://github.com/huggingface/ViZDoom) | C++ | Doom-based AI Research Platform for Reinforcement Learning from Raw Vi |
| 2 | [`huggingface_tianshou`](https://github.com/huggingface/huggingface_tianshou) | - | Additional code for Tianshou to load and upload models from the Hub. |
| 2 | [`dana`](https://github.com/huggingface/dana) | JavaScript | Test/benchmark regression and comparison system with dashboard |
| 2 | [`quicktype`](https://github.com/huggingface/quicktype) | TypeScript | Generate types and converters from JSON, Schema, and GraphQL |
| 2 | [`lmms-eval`](https://github.com/huggingface/lmms-eval) | Python | Accelerating the development of large multimodal models (LMMs) with lm |
| 2 | [`arena-hard`](https://github.com/huggingface/arena-hard) | - | Arena-Hard benchmark |
| 2 | [`ms-build-mi300`](https://github.com/huggingface/ms-build-mi300) | Jupyter Notebook |  |
| 2 | [`scheduler-plugins`](https://github.com/huggingface/scheduler-plugins) | Go | Repository for out-of-tree scheduler plugins based on scheduler framew |
| 2 | [`distribution-v2`](https://github.com/huggingface/distribution-v2) | - |  |
| 2 | [`duc`](https://github.com/huggingface/duc) | - | Dude, where are my bytes: Duc, a library and suite of tools for inspec |
| 2 | [`action-check-commits`](https://github.com/huggingface/action-check-commits) | TypeScript | A simple GitHub action that checks the list of commits in a pull-reque |
| 2 | [`WebShop`](https://github.com/huggingface/WebShop) | Python | [NeurIPS 2022] 🛒WebShop: Towards Scalable Real-World Web Interaction w |
| 2 | [`temp-tailscale-action`](https://github.com/huggingface/temp-tailscale-action) | - |  |
| 2 | [`metadata-sniffer`](https://github.com/huggingface/metadata-sniffer) | Python |  |
| 2 | [`torchtitan`](https://github.com/huggingface/torchtitan) | Python | A PyTorch native platform for training generative AI models |
| 2 | [`LIBERO`](https://github.com/huggingface/LIBERO) | Jupyter Notebook | Benchmarking Knowledge Transfer in Lifelong Robot Learning |
| 2 | [`pipeline-rl-cmu`](https://github.com/huggingface/pipeline-rl-cmu) | Python |  |
| 2 | [`publish-to-the-kernel-hub-action`](https://github.com/huggingface/publish-to-the-kernel-hub-action) | TypeScript |  |
| 2 | [`labbench2`](https://github.com/huggingface/labbench2) | Python | labbench2 |
| 2 | [`physics-intern-opencode-plugin`](https://github.com/huggingface/physics-intern-opencode-plugin) | Python | Installer for Physics Intern inside Opencode |
| 1 | [`flax_bert`](https://github.com/huggingface/flax_bert) | Python |  |
| 1 | [`clamd-client`](https://github.com/huggingface/clamd-client) | Rust | Rust async tokio client for clamd. Works with a tcp socket or with the |
| 1 | [`test_gh_secret`](https://github.com/huggingface/test_gh_secret) | - | dummy repo testing github workflow secrets |
| 1 | [`hub-js-utils`](https://github.com/huggingface/hub-js-utils) | JavaScript |  |
| 1 | [`prometheus-slurm-exporter`](https://github.com/huggingface/prometheus-slurm-exporter) | - | Prometheus exporter for performance metrics from Slurm. |
| 1 | [`Auth0-Social-Connection`](https://github.com/huggingface/Auth0-Social-Connection) | JavaScript |  |
| 1 | [`hugs-gcp-marketplace`](https://github.com/huggingface/hugs-gcp-marketplace) | - | Asses and details for HUGS on GCP |
| 1 | [`ProcessBench`](https://github.com/huggingface/ProcessBench) | Python |  |
| 1 | [`vllm-dca`](https://github.com/huggingface/vllm-dca) | - | A high-throughput and memory-efficient inference and serving engine fo |
| 1 | [`better-auth`](https://github.com/huggingface/better-auth) | TypeScript | The most comprehensive authentication framework for TypeScript |
| 1 | [`arena-hard-auto`](https://github.com/huggingface/arena-hard-auto) | - | Arena-Hard-Auto: An automatic LLM benchmark. |
| 1 | [`egl_probe`](https://github.com/huggingface/egl_probe) | C | A helpful module for listing available GPUs for EGL rendering. |
| 1 | [`DeepEP`](https://github.com/huggingface/DeepEP) | - | DeepEP: an efficient expert-parallel communication library |
| 1 | [`containerd`](https://github.com/huggingface/containerd) | - | An open and reliable container runtime |
| 1 | [`demo-storage-buckets`](https://github.com/huggingface/demo-storage-buckets) | Shell | Demo scripts for Storage Buckets presentations |
| 1 | [`Automodel`](https://github.com/huggingface/Automodel) | Python | 🚀 Pytorch Distributed native training library for LLMs/VLMs with OOTB  |
| 1 | [`hlh-server`](https://github.com/huggingface/hlh-server) | Python |  |
| 1 | [`deny-actions-registry`](https://github.com/huggingface/deny-actions-registry) | Shell | Org-wide GitHub Actions denylist + reusable validation workflow |
| 1 | [`kernels-test`](https://github.com/huggingface/kernels-test) | Python | Sources for test kernels at https://huggingface.co/kernels-test |
| 1 | [`sagemaker-python-sdk`](https://github.com/huggingface/sagemaker-python-sdk) | Python | A library for training and deploying machine learning models on Amazon |
| 1 | [`physics-intern-codex-plugin`](https://github.com/huggingface/physics-intern-codex-plugin) | Python | A Codex plugin for Physics Intern |
| 1 | [`space-demo-kit`](https://github.com/huggingface/space-demo-kit) | HTML | Render polished Gradio-style demo videos for Hugging Face Spaces |
| 1 | [`tokbench`](https://github.com/huggingface/tokbench) | Rust |  |
| 0 | [`test-actions`](https://github.com/huggingface/test-actions) | - |  |
| 0 | [`slurm-mail`](https://github.com/huggingface/slurm-mail) | Python | Slurm-Mail is a drop in replacement for Slurm's e-mails to give users  |
| 0 | [`bitsandbytes_testing`](https://github.com/huggingface/bitsandbytes_testing) | Python | Fork of bitsandbytes used for testing purpose |
| 0 | [`TensorRT-LLM`](https://github.com/huggingface/TensorRT-LLM) | C++ | TensorRT-LLM provides users with an easy-to-use Python API to define L |
| 0 | [`Multi-IF`](https://github.com/huggingface/Multi-IF) | - | The evaluation code for MultiIF multi-turn and multi-lingual instructi |
| 0 | [`new-model-addition-cwm`](https://github.com/huggingface/new-model-addition-cwm) | Python |  |
| 0 | [`homebrew-tap`](https://github.com/huggingface/homebrew-tap) | Ruby | The homebrew tap of Hugging Face tools |
| 0 | [`slime`](https://github.com/huggingface/slime) | - | slime is an LLM post-training framework for RL Scaling. |
| 0 | [`AReaL`](https://github.com/huggingface/AReaL) | Python | Lightning-Fast RL for LLM Reasoning and Agents. Made Simple & Flexible |
| 0 | [`cuda-toolkit`](https://github.com/huggingface/cuda-toolkit) | TypeScript | GitHub Action to install CUDA |
| 0 | [`migrate-to-kernel-repo-tool`](https://github.com/huggingface/migrate-to-kernel-repo-tool) | Python | A small cli tool to migrate a kernels in model type repo to kernel typ |

---

**附录数据源**：GitHub API `orgs/huggingface/repos`（2026-08-10 抓取，467 个公开仓库去重）｜ **分类规则**：基于 name+description 关键词正则，边界库可能跨域（如 sentence-transformers 同时属"模型框架"与"嵌入/检索"）｜ **维护**：HF 每月新增仓库，可设 `schedule_job` 月度刷新。
