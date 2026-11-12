# 04 · 训练层 Topics：微调/PEFT（L6）/ 对齐（L7）/ 数据与评测（L8）

> 这是"模型怎么变成你的"三步：适配（L6）→ 对齐（L7）→ 喂什么数据/怎么验货（L8）。与项目内 `../../../讲透模型宇宙/` Part IV（18 建/19 调改）方法论呼应。

---

## L6 Fine-Tuning/PEFT 层——"用你的数据适配模型"

### topic:fine-tuning（4,863）/ llm-finetuning（171）/ instruction-tuning（301）/ llm-training（816）

- **使用背景**：
  - `fine-tuning`：通用微调总标签（4,863）——模型适配工具/教程/行业方案。**Kimi 报告此处错 67 倍**（报 72），实测纠正后此层规模其实是 PEFT 级别；
  - `llm-finetuning`（171）与 `llm-training`（816）：LLM 特化名，框架类仓库偏好（LLaMA-Factory 官方标签群）；
  - `instruction-tuning`：学术血统标签（Alpaca/ShareGPT 衍生数据集与教程）。
- **代表仓**：unslothai/unsloth（73,656★，消费级 GPU 微调加速的事实标准，`unsloth` 自成 topic 477 仓）；hiyouga/LLaMA-Factory（~70k★ 量级，8-19 API 限速未实测待核，一站式微调 UI）。

### topic:lora（4,997）/ qlora（1,073）/ peft（1,110）

- **使用背景**：
  - `lora`：低秩适配——PEFT 的代名词级标签。4,997 仓横跨方法实现/适配器分发/应用方案；2023 QLoRA 论文后爆发，2025-2026 是**消费级微调民主化**的基础设施标签；
  - `qlora`：4-bit 量化+LoRA 组合（1,073）——单卡微调大模型的标配路径；
  - `peft`：**既是方法类名也是 HF 库名**——1,110 仓大部分是 huggingface/peft（21,559★）的生态外围（教程/适配器/集成）。
- **三者关系**：peft(方法族) ⊃ lora(最流行成员) ⊃ qlora(量化变体)——检索时 `peft OR lora` 覆盖，`qlora` 找极端省显存方案。
- **判断**：L6 的真实门槛不在方法（PEFT 已傻瓜化）而在数据（L8）与评估（L8）——topics 规模也印证：synthetic-data 2,419 + llm-evaluation 3,935 与 lora 4,997 同量级。

## L7 Alignment 层——"让模型行为符合偏好"

### topic:rlhf（778）/ dpo（441）/ grpo（522）/ rlvr（119）/ alignment（1,387）

- **使用背景**：
  - `rlhf`：人类反馈强化学习——对齐的经典标签（778），InstructGPT 血统；检索对齐综述/传统 RLHF 管线用；
  - `dpo`：直接偏好优化（441）——无 reward model 的简化路线，2024 起微调侧最常用；
  - `grpo`：DeepSeek-R1 带火的组相对策略优化（522）——**推理模型训练的方法标签**，2025 年增长最快；
  - `rlvr`：可验证奖励 RL（119 仓，概念热 topic 冷）——数学/代码等可验证域的 RL，R1/o1 路线的学术名；
  - `alignment`：大词（1,387），含 AI 安全/价值对齐的学术讨论，与上述方法标签部分重叠。
- **代表仓**：huggingface/trl（19,107★，SFT/DPO/PPO/GRPO 全家桶，实践派入口）；PKU-Alignment/align-anything（4,666★，全模态对齐）。
- **方法演进 vs topic 稳定**：RLHF(2022)→DPO(2023)→GRPO(2024-25)→RLVR，四个标签并存不替换——**对齐圈用 topic 表达方法阵营**，检索特定方法直接用方法名，比 `alignment` 大词准。

## L8 Data/Eval 层——"喂什么、怎么验货"

### topic:benchmark（10,860）/ llm-evaluation（3,935）/ evals（1,395）

- **使用背景**：
  - `benchmark`：万仓级（10,860）但**高度跨域**——AI benchmark 与传统性能 benchmark（JS 基准/数据库基准）混居，检索 LLM 评测需组合 `llm-evaluation`（3,935，纯度高：OpenCompass/lm-eval-harness 生态）；
  - `evals`：OpenAI evals 血统的标签（1,395），评测集格式与 harness。
- **视角**：L8 是唯一横跨全链路的层——L1 prompt 评测（promptfoo）、L4 agent 评测（microsoft/skills 的 eval CI）、L6 微调效果、L9 推理质量，全部回到"怎么验货"。

### topic:synthetic-data（2,419）/ data-centric-ai（111）

- **使用背景**：`synthetic-data`：合成数据生成（2,419）——2025-2026 训练数据枯竭叙事下的**最热增长点**（distilabel/easy-dataset 一类"用 LLM 造 LLM 训练数据"工具）；`data-centric-ai`：Andrew Ng 数据中心 AI 旗号（111 仓，叫好不叫座的典型——理念先行、工具散落）。
- **判断**：合成数据是 L6-L7 的燃料供应商——微调民主化（L6）× 合成数据（L8）× 消费级硬件（unsloth）构成 2026 "人人可微调"的三件套。

## 训练三层的 5W2H 速览（详解见 06 篇）

- **Who**：算法工程师（L6/L7 主力）、数据工程师（L8）、评测平台团队
- **Why**：权重不满足你 → L6 改权重；行为不合意 → L7 对齐；数据/质量是根因 → L8
- **When**：先 RAG/skills（零训练）不达标 → 才上 LoRA（L6）→ 效果好但行为怪 → DPO/GRPO（L7）——**训练是最后手段**，成本阶梯见 06 篇 How much
- **How much**：lora 4,997 / fine-tuning 4,863 / llm-evaluation 3,935 / synthetic-data 2,419——方法层规模相当，无超级 topic（对比 L3/L4 的 64k/74k）——**训练是专业深水区，不是大众活动**

## refs
- GitHub Search API 实测 2026-08-19；star 实测同日：unsloth 73,656 / peft 21,559 / trl 19,107 / align-anything 4,666 / dspy(L1) 37,401；LLaMA-Factory 限速未实测（~70k★ 量级待核）
- 方法演进：RLHF(InstructGPT 2022)→DPO(2023)→GRPO(DeepSeek-R1 2024-25)；项目内 `../../../讲透模型宇宙/` Part IV

*updated: 2026-08-19*
