# LLM 算法知识库 · 谱系 + 应用卡

> 定位：研究/工程速查。每条给"问题→核心思想→关键论文/文档锚点→本项目工具接口"。

## 一、算法谱系（训练侧）

| 阶段 | 核心问题 | 代表方法 | 锚点 |
|---|---|---|---|
| 预训练 | 下一词预测的规模化 | dense/MoE、长上下文扩展（RoPE 外推/ALiBi）| 各技术报告（Qwen/Llama/DeepSeek 系列）|
| SFT | 指令跟随 | 全参 vs LoRA/QLoRA；chat template 就是数据格式合同 | PEFT 文档 |
| 偏好对齐 | 人类偏好注入 | RLHF（PPO）→ DPO（免 reward model）→ GRPO（组相对）| DPO: arXiv:2305.18290（引用前先核实）|
| 推理增强 | 思维链内化 | RLVR（可验证奖励 RL）/过程奖励 PRM/拒绝采样蒸馏 | 讲透NLP Ch09 后训练 |
| 推理时扩展 | 不训模型变聪明 | best-of-N、self-consistency、beam、speculative | — |

**工程红线锚**： tokenizer 是合同（换 tokenizer = 全量重训）；eval 污染是头号事故源。

## 二、应用模式卡

| 模式 | 何时选 | 坑 |
|---|---|---|
| Prompt 工程 | 能力已在模型内 | prompt 过长稀释（手册 04 章）|
| RAG | 知识外置且更新快 | 检索质量是天花板；评测要分检索/生成两段 |
| 微调（LoRA）| 风格/格式/领域术语稳定 | 灾难遗忘（混 5-10% 通用数据）；数据 <500 条慎全参 |
| Agent | 多步+工具+环境 | 六组件缺一不可（手册 03 章）；评测用轨迹不看单轮 |
| 约束解码 | 输出喂机器 | reasoning tax 10-15%（XGrammar 文档）；reasoning 放 schema 外 |

## 三、本项目金字塔 ↔ LLM 工作流

```
L1 lint        代码卫生
L2 单测        数据处理/tokenizer/评测函数的单元
L3 生成冒烟    llm_smoke.py（真加载+真生成+PPL 自检；三级降级诚实标注）
L4 最小评测    llm_eval.py（PPL+重复率；防"模型坏了"级回归）
```

**规模化路径**：L4 之上接正式基准（MMLU/GSM8K 子集/领域自建集），本插件只保证"没坏"，不保证"好"。

## 四、本地环境锚点（2026-08-20 实测）

- 本机：torch 2.10.0+cpu / transformers 5.10.0.dev0 / peft 0.20.0
- 模型库：~/ai/models/Qwen2.5-0.5B-Instruct（冒烟已真跑：中文生成 NLL=4.96）
- HF_ENDPOINT=hf-mirror.com（直连不通）；长任务 setsid nohup 防组杀
- 大模型相关实验的 LoRA 闭环参考：work4ai/xkernel-llm-constraints/scripts/train_lora.py

## 五、研究纪律链接

AGENTS.md 是禁令层；本文件是地图层；论文/技术报告引用**先 webfetch 核实再落盘**（铁律 #2）。
