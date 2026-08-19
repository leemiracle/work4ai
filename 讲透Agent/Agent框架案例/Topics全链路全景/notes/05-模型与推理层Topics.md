# 05 · 模型与推理层 Topics：Inference/Quant（L9）/ 模型本体（L10）/ 横切

> 底座层：模型怎么跑起来（L9）、本体是什么（L10）、贯穿全链的横切关注点。

---

## L9 Inference/Quantization 层——"模型怎么高效跑起来"

### topic:inference（3,836）/ llm-inference（2,926）/ llm-serving（322）/ vllm（2,104）

- **使用背景**：
  - `inference`：通用推理标签（3,836），含传统 ML 推理（历史存量）与 LLM 推理引擎——跨域混杂；
  - `llm-inference`：LLM 特化（2,926），**找推理引擎/吞吐优化用它最准**；
  - `llm-serving`：服务化部署视角（322，小而专——API 网关/OpenAI 兼容层）；
  - `vllm`：**产品名自成 topic**（2,104）——vLLM 生态外围（插件/部署方案/教程），工具成为事实标准后用户自发打标签的典型（同类：`unsloth` 477、`engram` 76）。
- **代表仓**：vllm-project/vllm（89,396★，高吞吐推理事实标准）；sgl-project/sglang（32,076★，第二极）；ggerganov/llama.cpp（~90k★ 量级，8-19 API 限速未实测待核，端侧推理之王）。
- **格局**：vLLM(数据中心) / SGLang(高并发结构化) / llama.cpp(端侧) 三分——分别对应 `vllm`、`llm-inference`、`local-llm` 三个标签的势力范围。

### topic:quantization（2,414）/ speculative-decoding（368）

- **使用背景**：
  - `quantization`：量化（2,414）——GPTQ/AWQ/GGUF 全家，横跨训练（QLoRA 的 Q）与推理（部署瘦身）双场景，**是 L6 与 L9 的界河 topic**；
  - `speculative-decoding`：投机解码（368）——小模型起草+大模型验证的加速范式，推理优化的研究前沿标签。
- **判断**：量化是"部署民主化"的技术底座——与 local-llm(5,389) 呼应：量化让 70B 进单卡、local-llm 让它进家庭实验室。

## L10 模型本体层——"本体是什么"

### topic:llm（116,500）/ large-language-models（6,935）/ transformers（10,738）/ transformer（7,893）

- **使用背景**：
  - `llm`：**全链路最大 topic**（116,500）——已是领域名，一切 LLM 相关都可能打；只适合趋势观测，找项目会被淹没；
  - `large-language-models`：学术全称（6,935），论文与综述偏好；
  - `transformers`/`transformer`：**架构名双形态**（10,738/7,893）——注意 `transformers`（复数）大量指向 HF 库生态（教程/插件/微调方案），`transformer`（单数）更多是架构研究与复现（nanoGPT 血统）。**一字之差，语义分野**——检索 HF 库用法用复数，学架构原理用单数。
- **代表仓**：huggingface/transformers（164,236★，开源模型生态的操作系统）。

### topic:vlm（1,427）/ vision-language-model（1,447）/ multimodal（3,591）/ mllm（333）/ mixture-of-experts（704）/ reasoning-model（9）

- **使用背景**：
  - `vlm` vs `vision-language-model`：缩写与全名几乎等规模（1,427/1,447）——VLM 圈没有形成压倒性偏好，检索要 OR 双查；
  - `multimodal`：多模态大词（3,591），音频/视频/图文混合；
  - `mllm`：多模态 LLM 缩写（333），与 multimodal 部分重叠；
  - `mixture-of-experts`：MoE 架构（704）——DeepSeek-V3/Mixtral/Qwen-MoE 的架构标签，2025 后随开源 MoE 普及而增长；
  - `reasoning-model`：**只有 9 仓**——推理模型（o1/R1 类）是 2025-2026 最热概念之一，但 topic 体系几乎空白：相关项目散在 `chain-of-thought`(514)/`grpo`(522)/`rlvr`(119)。**概念传播速度远快于 topic 习惯形成**。
- **代表仓**：MoonshotAI/Kimi-VL（1,222★ 量级但已停更 2025-07——模型仓的生命周期特征：发版即巅峰，社区版续命）；OpenGVLab/InternVL、QwenLM/Qwen2.5-VL（8-19 限速未实测）。

## 横切关注点

| Topic | 仓数 | 背景与用法 |
|---|---|---|
| `local-llm` | 5,389 | 本地部署运动（llama.cpp/Ollama 生态）——隐私/成本/离线三动机；检索家庭实验室方案 |
| `ai-gateway` | 2,129 | LLM API 网关（路由/限流/多厂商 fallback）——企业统一出口；与 mcp-security 同属治理侧 |
| `llm-framework` | 252 | 开发框架自述标签（被 langchain 等挤压，规模小） |
| `llm-training` | 816 | 训练框架（跨 L6/L7） |
| `open-source-llm` | 75 | 名义热实冷——开源模型散在各模型名 topic（qwen/deepseek）下，不打这个总标签 |

## 底座层的结构性观察

1. **越底层 topic 越老、越大、越混杂**：llm 116k > ai-agents 74k > mcp 64k > rag 41k > prompt-engineering 16k > context-engineering 2.7k——**topic 规模与概念年龄正相关，与检索精度负相关**。用新概念的小 topic 精准检索，用老概念的大 topic 观测大盘。
2. **产品名 topic 化是"事实标准"认证**：vllm 2,104 / unsloth 477——当你工具的名字成为 topic，说明用户在用"基于 X"定义自己的项目。
3. **模型仓与工具仓的 star 逻辑不同**：transformers 164k 是生态积累；模型本体仓 star 快起快落（Kimi-VL 停更即降温）——**底座看工具，前沿看模型**。

## 本层 5W2H 速览（详解见 06 篇）

- **Who**：推理工程师（L9）、模型研究员（L10）、运维（横切 ai-gateway）
- **Why**：算力是硬约束——L9 全部话题都在回答"同预算下更快/更便宜/更小"
- **How much**：llm 116k 一家独大，但实操价值集中在 1k-5k 的工具 topic（llm-inference/quantization/vllm）

## refs
- GitHub Search API 实测 2026-08-19；star 实测同日：vllm 89,396 / transformers 164,236 / sglang 32,076 / Kimi-VL 1,222；llama.cpp、InternVL、Qwen2.5-VL 限速未实测（量级待核）
- 三分格局与 DeepSeek 推理栈：项目内 `../../../讲透DeepSeek/`

*updated: 2026-08-19*
