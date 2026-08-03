# AI 论文探索之旅 · 谢清池访谈精读（2004 → 2026 全时间线整合版）

> **本文件性质**：参考资料（非教程）。整理自播客「张晓俊商业访谈录」一期论文分享特别节目，并把原文论文时间线（止于 2024 年 DiT）补到 **2026-08-03**。与 work4ai「讲透X」系列互补——讲透系列钻深度，本文档提供**广度的历史脉络与人物关系**。

---

## 元信息

| 项 | 内容 |
|---|---|
| 来源 | 张晓俊商业访谈录（"语言即世界"工作室出品）|
| 嘉宾 | **谢清池**（美团光年之外产品负责人，计算机科班，9 年产品/创业）|
| 录制时间 | 2025 年国庆期间 |
| 嘉宾阅读量 | 2 年业余精读 ~200 篇 AI 论文，精选 30+ 篇串成脉络 |
| 整理日期 | 2026-08-03 |
| 整理者 | ai-mentor（基于访谈实录 + 2024.11–2026.08 公开资料增补）|
| 可信度 | 访谈内容 = 一手口述；2024.11 后内容 = 公开报道/论文/官网，标注日期 |
| 关联项目 | work4ai `讲透Transformer` / `讲透基础模型` / `讲透Agent` 系列 |

---

## 目录

- [一、嘉宾与访谈背景](#一嘉宾与访谈背景)
- [二、三个核心视角（访谈灵魂）](#二三个核心视角访谈灵魂)
- [三、用 AI 学 AI 的工具箱 + 学习路书](#三用-ai-学-ai-的工具箱--学习路书)
- [四、四大板块论文精读（2004 → 2026）](#四四大板块论文精读2004--2026)
  - [4.1 模型范式变迁](#41-模型范式变迁)
  - [4.2 Infra 与数据变迁](#42-infra-与数据变迁)
  - [4.3 语言模型发展](#43-语言模型发展)
  - [4.4 多模态与世界模型](#44-多模态与世界模型)
- [五、元洞察提炼](#五元洞察提炼)
- [六、术语纠错表（增值）](#六术语纠错表增值)
- [七、与 work4ai 项目的对接](#七与-work4ai-项目的对接)
- [📌 进一步阅读与练习](#-进一步阅读与练习)

---

## 一、嘉宾与访谈背景

**谢清池**：大学本硕读计算机，毕业后去豆瓣做产品（做过"阿尔法城"社区探索，期间系统研读城市规划大师 Jan Gehl 论著），中间 9 年创业（To C + 消费）。2022 年 ChatGPT 来潮后，意识到"对产品经理而言，**产品=在给定边界里求最优解**，而 AI 时代的边界正在剧变"，于是从 2022–2023 起系统读论文，目标是"**通过原理了解这个新世界的边界**，并掌握 3–5 年不变的知识"。

**为什么互联网时代 PM 不读论文、AI 时代必须读**：互联网/移动互联网本质是"成熟技术的应用"，技术论文稀缺；AI 仍处技术早期，**必须通过论文才能 follow 演进、感知边界**。

---

## 二、三个核心视角（访谈灵魂）

谢清池强调：读论文最难的不是单点看不懂，而是**"不知道作者为什么要这么做"**。他用三个视角破解：

| 视角 | 回答的问题 |
|------|-----------|
| **历史视角**（编年体+纪传体）| 那个时代碰到什么挑战？作者为什么这么做？对后续路线影响？ |
| **范式变迁视角** | 旧范式（手工特征/SMT/RNN/CNN/GAN）碰到什么危机？哪个支线崛起夺走主流？ |
| **人物视角** | 这些科学家如何登场？如何在工业界延续影响？（一张"封神演义"人物网）|

**底层主线**：深度学习发展 = **算力(芯片+Infra) × 数据 × 模型结构** 四要素随时间共同演进；Richard Sutton 的 *The Bitter Lesson* 是贯穿全文的"第一性原理"。

---

## 三、用 AI 学 AI 的工具箱 + 学习路书

### 工具
| 工具 | 用途 |
|------|------|
| **沉浸式翻译**（浏览器插件） | 解决英文阅读障碍；视频字幕也能译 |
| **ChatGPT / Claude / 豆包** | 身边最好的老师，多模型交叉验证可分辨差距 |
| **Claude Artifacts** | 让 AI 把原理做成可视化网页 |
| **DeepL 浏览器** | 边看论文边划词提问 |

### 视频路书（按谢清池推荐度）
1. **吴恩达** 机器学习/AI 课程
2. **李宏毅**《生成式 AI 时代下的机器学习》2025 版（B 站有授权连载）
3. **Andrej Karpathy** YouTube（教育向，质量极高）
4. **李沐** 论文精读系列（B 站，每篇看 2–3 遍）
5. **3Blue1Brown**（数学/物理/神经网络可视化，GitHub 开源了可视化库）
6. **汪木头学科学**（B 站，学习方法分享）
7. **周喵喵**（B 站，华为昇腾工程师，GPU/Infra 深度内容）

### 书籍路书
1. **《一站式 LLM 底层技术原理入门指南》**（飞书文档，深入浅出）
2. **《动手学深度学习》** PyTorch 版（开源，李沐是作者之一，配套中文讲解视频）
3. **《深度学习中的数学》**（概率论补课）
4. **《深度学习革命》**（余凯作序，讲 Hinton/Ilya/Alex 公司拍卖故事）

### 学习方法论（嘉宾亲历）
- **平台期 2–3 个月**：早期读论文云里雾里、看睡着（"只有考研时有过这经验"），度过之后享受第一手信息快感。
- **从"是什么"到"为什么"**：单点读懂不难，难在不知道作者为何这么做——所以串联历史脉络。
- **读懂论文的回报**：能直接看研究员分享视频、和最聪明头脑对话；**能预判模型节奏、"心安理得地等"**（如客服模型等千问 3 而非手工 SFT）。

---

## 四、四大板块论文精读（2004 → 2026）

> **时间线总览**（mermaid）：
>
> ```mermaid
> timeline
>     title AI 大事件（2004 → 2026.08）
>     2004 : Brook for GPU (CUDA 前身)
>     2012 : AlexNet (深度学习开端)
>     2014 : Seq2Seq + Attention / GAN / 双流网络
>     2015 : ResNet / 知识蒸馏 / Diffusion 诞生
>     2017 : Transformer / AlphaGo Zero / 现代 MoE
>     2018 : GPT-1 vs BERT (信仰之战)
>     2019 : GPT-2 / Scaling Laws
>     2020 : GPT-3 / DDPM / ViT
>     2021 : CLIP / LoRA 前身
>     2022 : CoT / ReAct / Stable Diffusion / InstructGPT
>     2023 : Mamba
>     2024 : DeepSeek-V3/R1 / Sora / Genie 2 / GPT-4o / o1
>     2025 : Llama 4 / Qwen3 / Kimi K2 / Veo 3 / Sora 2
>     2026 : DeepSeek V4 / Nemotron 3 / Claude Opus 5 / GPT-5.6
> ```

### 4.1 模型范式变迁

#### 速览表（2004 → 2026）

| 年份 | 论文/模型 | 作者（含八卦）| 核心贡献 |
|------|----------|-------------|---------|
| 2004 | **Brook for GPU** | Ian Buck（CUDA 创始成员，至今 NVIDIA CUDA VP）+ Pat Hanrahan（2019 图灵奖/Pixar 创始员工/Tableau 创始人，被 Salesforce 157 亿美金收购）| GPU 抽象为流处理器，发明 stream/kernel/reduce 框架，**CUDA 前身** |
| 2012 | **AlexNet** | Alex Krizhevsky（Infra 达人，搞定 CUDA）+ Ilya Sutskever + Geoffrey Hinton | **首次同时 scale 数据+算力+模型**（0.06B），ImageNet top1 领先 10+ 点，开启深度学习时代 |
| 2014 | **Sequence to Sequence** | Ilya + Quoc Le（现 Gemini 后训练负责人）+ Aäron van den Oord（现 Google 预训练负责人）| 用 LSTM 复兴 Encoder-Decoder，解决"变长→变长"序列问题 |
| 2014 | **Bahdanau Attention** | Dzmitry Bahdanau + Yoshua Bengio | 首次提出注意力机制，缓解隐藏状态瓶颈，为 Transformer 埋伏笔 |
| 2015 | **Distilling the Knowledge**（知识蒸馏）| Hinton + Oriol Vinyals + Jeff Dean | 教师-学生范式，软标签传递概率分布 |
| 2015 | **ResNet**（残差网络）| 何恺明（现 MIT 教授）+ 张翔宇（阶跃星辰首席科学家）+ 任少卿（蔚来自动驾驶）+ 孙剑（已故，原旷视首席科学家），均出自微软亚研院 | 引入残差连接，**引用量近 30 万（高于 Transformer）**，至今所有网络（含 Diffusion/Transformer）都用残差 |
| 2017 | **Attention is All You Need**（Transformer）| 8 位 Google 作者，**Noam Shazeer** 最知名（工程+算法双强，后创 Character.AI）| 只要 Attention 不要 RNN，**抽中"硬件彩票"**，奠定至今未变的主导架构 |
| 2017 | **AlphaGo Zero** | DeepMind，含 Karen Simonyan（后 Inflection/微软 AI 负责人）| 纯 RL、零人类先验，36 小时超李世石版；启发 o1/R1-Zero 的 **test-time scaling** |
| 2017 | **现代 MoE** | Noam Shazeer 等 | 容量 ×1000、计算成本几乎不变 |
| 2022 | **Chain of Thought** | Jason Wei（达特茅斯本科）+ Denny Zhou（现 Gemini reasoning 负责人）| "let's think step by step"激发潜在能力，**预训练→后训练迁移的引爆点** |
| 2021 | **LoRA** | Edward Hu（Bengio 学生，后入 OpenAI）| 低秩旁路 Δ 矩阵，等效全量微调，零额外延迟 |
| 2022 | **ReAct** | 姚顺雨 Shunyu Yao（清华姚班，97 年生）| Reasoning + Acting 交替，**Agent 范式奠基** |
| —— | **The Bitter Lesson**（Sutton, 2019，文章非论文）| Richard Sutton | 利用算力的通用方法（search+learning）长期必胜手工特征；**OpenAI 的"圣经"** |
| **2023.12** | **Mamba**（Gu & Dao）| Albert Gu + Tri Dao | 首个中小规模匹敌 Transformer 的 SSM，**选择性状态空间**；推理 O(1)/步 |
| **2024.05** | **Mamba-2 / SSD**（Dao & Gu）| Tri Dao + Albert Gu | 证明 SSM 与 attention 是同一半可分矩阵的两种收缩→核心层快 2-8× |
| **2024.03** | **Jamba**（AI21）| AI21 Labs | 首个生产级 **Transformer-Mamba-MoE 混合**，256K 上下文，KV cache 小 10× |
| **2024.09** | **OpenAI o1** | OpenAI（Noam Brown 等）| **test-time scaling 引爆点**——AlphaGo Zero 的 MCTS 思想搬进 LLM |
| **2025 多篇** | **test-time scaling 理论化**（NeurIPS 2025）| 多机构 | "Does Thinking More Help?" 揭示 **overthinking 反效应**；parallel thinking 比 sequential 高 22% |
| **2026.03** | **Mamba-3** | 见 Sebastian Raschka 2026 论文清单（arXiv:2603.15569）| SSM 序列建模新迭代 |
| **2026.04** | **Nemotron 3 Super**（NVIDIA, arXiv:2604.12374）| NVIDIA | **hybrid Mamba-Attention MoE + LatentMoE + MTP**，120B/12B，吞吐 7.5× Qwen3.5-122B |
| **2026.05** | **Gated DeltaNet-2**（arXiv:2605.22791）| —— | 解耦 erase/write 的线性 attention，Qwen3.6 采用 |
| **2026.03** | **Sparse Feature Attention + FlashSFA**（arXiv:2603.22300）| Xie et al. | **特征维度稀疏**（正交于 token 稀疏），2.5× 加速、KV cache -50% |

#### 重点论文展开

**🟢 AlexNet (2012) / 范式变迁引爆点**
- **关键背景**：ImageNet 比赛**第三届只剩 6 支队伍**（第一届 13 支），眼看办不下去。余凯/NEC 用手工特征已做到极致；Yann LeCun 提神经网络的论文甚至被拒。
- **Ilya 原话**：问题出在"深度网络需要更多数据+算力+模型规模"——AlexNet **同时 scale 三者**。
- **0.06B 参数**今天看很小，但比当时最大网络大一个数量级，于是有了 Google 拍卖公司（余凯参与）、Hinton+Ilya+Alex 入 Google Brain 的故事。

**🟢 ResNet (2015) / 让 scale 真正 work**
- **反直觉**：2015 年人们发现网络深到 100+ 层反而**退化**（不是过拟合，是退化）——"scale 会自动变好"在当时并不成立。
- **解法**：学 F(x) 改成学 F(x)+x 的残差，等价于只学"增量"，类似后来 LoRA 只学 Δ。

**🟢 Transformer (2017) / 抽中硬件彩票**
- **Noam 名言**（解释为何模型有效）："**我们不提供任何解释——如果 work，归为神的仁慈。**" → 揭示当时对神经网络的理解仍是"托勒密观星"阶段。
- **配套机制**：位置编码（RoPE 后由**苏剑林**改进）、mask、多头注意力。
- **结果**：建模能力强 + 适配 GPU → 可在数据/算力上 scale → 大力出奇迹成为可能。**自此主流架构几乎未变**。

**🟢 AlphaGo Zero (2017) / 启发两个时代**
- **对旧 AlphaGo 的两点批判**：① 依赖人类棋谱（上限被锁死）② 注入"气/眼"等手工特征。
- **贡献一**：纯 RL 从零训，更少卡 + 36 小时超李世石版。
- **贡献二**：每步 1600 次 MCTS 搜索 → **test-time scaling** 思想源头 → 启发 Noam Brown 做 o1、DeepSeek 做 R1-Zero。
- **Sutton 的延伸批评**：当前 LLM 仍在"语料库学习"，类似早期 AlphaGo 在人类棋谱上学习，**并非真正 RL**。

**🟢 现代 MoE (2017) / 成本优先的架构选择**
- **路线选择对照**：DeepSeek 成本优先→选 MoE；OpenAI GPT-4 起转 MoE；**Llama 转 MoE 失败、MiniMax 训了 3 次才成**——MoE 至今仍难训。

**🟢 CoT (2022) / 定义时代问题**
- **影响**：① AI 重心从预训练→后训练 ② 输入工程化：prompt engineering → context engineering ③ 直接催生 thinking 模型。
- **谢清池的方法论评价**：Jason Wei 属于"**定义时代重要问题**"型研究员——论文难度≈博文，但引用量在 R1/o1 后暴涨。

**🟢 DeepSeek-R1 (2025.01) / 开源版的"o1 时刻"**
- **R1-Zero 的震撼**：直接在 V3-Base 上跑 GRPO，**不掺任何 SFT**，AIME pass@1 从 15.6% → 71.0%（cons@64 达 86.7% 匹配 o1-0912）。模型自然涌现自我验证、反思、生成长 CoT 等行为。
- **意义**：首个开源验证"纯 RL 即可激发推理"，R1 论文（arXiv:2501.12948）+ 开源 1.5B–70B 蒸馏模型，把"thinking 范式"民主化。
- **历史呼应**：这是 AlphaGo Zero 路线在 LLM 上的首次大规模开源兑现。

**🟢 The Bitter Lesson / 全文的"宪法"**
- **两条核心教训**：
  1. 利用算力的通用方法（**search + learning**）长期必胜；手工特征"短期有效且令研究者满足，长期陷入平台期"。
  2. 心智内容极其复杂、不可简化——停止寻找捷径，只内置"能发现复杂性的元方法"。
- **工业界平衡术**：Claude Code 的 system prompt 仍写"6 位数以上请用 Python"——典型手工特征，因为模型当前还不够强；但 GPT/Claude 能力正逼近 Cursor 的工程化路径。
- **谢清池的实践指导**：**"心安理得地等"**——读懂论文后能预判模型节奏，知道某问题 5-6 个月后模型会自己解决，就不必手工 SFT。

**🟢 2024–2026 架构主旋律：Hybrid + MoE + 长上下文**
- **Transformer 主导地位首次被结构性挑战**——不是被替换，而是被"hybrid 化"：Mamba-2/Gated DeltaNet-2 处理长上下文省内存，少量 attention 层做"全局锚点"。
- **谢清池"等模型"预言成真**：上下文 1M-2M 成标配，DeepSeek NSA/SFA 把 reading 成本降一个量级，混合架构让 KV cache 不再膨胀。
- **硬件彩票二次开奖**：长上下文 + agent 把 KV cache 成本推到台前，**SSM/线性 attention 因"固定大小状态"再次被选中**——历史重演。

---

### 4.2 Infra 与数据变迁

#### 速览表

| 年份 | 论文/工作 | 作者 | 核心贡献 |
|------|----------|------|---------|
| 2019 | **ZeRO**（DeepSpeed 第三代）| 微软（李沐早期参与的参数服务器为第一代）| 优化数据并行，消除内存冗余，可训练模型规模 ∝ 集群总显存；支撑 OpenAI 早期 GPT-3 训练 |
| 2020 | **Scaling Laws**（OpenAI + DeepMind Chinchilla 两篇）| Jared Kaplan 等 / Hoffmann 等 | loss 与 compute/data/params 呈**对数线性**幂律 → 可用小模型实验预测大模型效果；DeepMind 主张"参数与数据等比 scale"，OpenAI 偏向"参数优先→导致训练不足" |
| 2021 | **LAION-5B** | Christoph Schuhmann（德国高中物理+计算机老师）+ 开源社区 | 50 亿图文对，**多模态版 ImageNet**，Diffusion 训练基石；NSFW 标注策略（**关键洞察：去掉人体结构数据，模型会丧失对人体结构的理解**）|
| 2023 | **RefinedWeb** | TII（Falcon 团队）| 仅靠 Common Crawl 精洗就能超过人工策展语料，**破解"数据墙"新范式** |
| 2024 | **MegaScale**（字节）| 字节 | **首篇公开的万卡单 job 训练论文**；建可观察系统做监控/归因/故障自愈 |
| **2025** | **Native Sparse Attention (NSA)** | DeepSeek | 硬件友好稀疏注意力，长上下文推理成本降一个量级 |
| **2026.02** | **ERNIE 5.0 弹性训练** | 百度 | 一次预训练同时产出多深度/宽度/稀疏度子模型 |
| **2026.04** | **LatentMoE**（Nemotron 3 Super）| NVIDIA | token 先压到潜空间再路由，accuracy/FLOP 与 accuracy/parameter 双优 |
| **2026.04** | **NVFP4 预训练**（Nemotron 3 Super）| NVIDIA | 首次在 **FP4** 下稳定预训练万亿级模型 |

#### 关键洞察

- **Scaling Law 的真正用途**：不是炫技，而是**用小模型预测大模型**，避免"训 3 个月开盲盒"。
- **loss 炸了 = 回 checkpoint 重训**：Llama 训练每 2 小时炸 1 次；DeepSeek 训 2 个月不炸 = 工程能力强。
- **算法-Infra co-design 典范**：DeepSeek-V2/V3 的张量并行度**精确贴着 H800 带宽上限设计**（切 4 卡），实现计算与通信零等待。当前主流训练 MFU 仅 ~50%，理论空间巨大。
- **数据墙并非绝境**：合成数据（特别是 RL 可验证领域：数学/代码）成为破墙主路径——DeepSeek R1 的成功本质是**用 RL 自生成可验证推理数据**。

---

### 4.3 语言模型发展

#### 速览表（含 2024–2026 三极分化）

| 年份 | 论文/模型 | 作者 | 核心贡献 |
|------|----------|------|---------|
| 2013 | **Word2Vec** | Tomas Mikolov + Jeff Dean | 首次将单词向量化、且语义连续（king−man+woman≈queen）；现代 embedding 雏形 |
| 2016 | **GNMT**（Google 神经机器翻译）| 吴永辉（现字节 Seed 预训练负责人）+ Quoc Le + Aäron + Jeff Dean | 神经网络翻译首次工业级部署，集成 ResNet/Encoder-Decoder/Attention/低精度——**工程集大成** |
| 2018 | **GPT-1** | Alec Radford 等 | **无监督预训练 + 监督微调**范式；Decoder-only + next-token prediction；0.1B/5GB BooksCorpus |
| 2018 | **BERT** | Google | 双向完形填空，**发布即屠榜**，GPT-1 被锤 |
| 2019 | **GPT-2** | OpenAI | 数据 + Reddit 爬取 WebText，10× scale；首次提出 **zero-shot** 概念；OpenAI 改组为有限盈利、微软注资 10 亿 |
| 2020 | **GPT-3** | 31 位作者（vs GPT-1/2 的 6-8 位）| 100× scale 到 175B、Common Crawl；**上下文学习（in-context learning）** 成为主范式 |
| 2022 | **InstructGPT** | Long Ouyang 欧阳龙 + John Schulman 等 | **RLHF**（SFT + reward model + PPO），1.3B 经对齐后超越 175B GPT-3；现代"助手"形态起点 |
| 2024 | **Tülu 3** | Allen Institute for AI (AI2)，Nathan Lambert 一作 | 公开**完整 posttrain 配方**（数据+代码+权重）|
| **2024.12** | **DeepSeek-V3** | DeepSeek | **MLA + 无辅助损失 MoE + MTP**；671B/37B，2 月训完不炸 |
| **2025.01** | **DeepSeek-R1 / R1-Zero**（arXiv:2501.12948）| DeepSeek | **首个开源验证纯 RL（GRPO）激发推理**，开源 1.5B-70B 蒸馏 |
| **2025.04** | **Llama 4 Scout/Maverick** | Meta | Scout **10M 上下文**（78× 同行），Maverick MMLU 85.5% |
| **2025.05** | **Qwen3 + GSPO** | 阿里 | **thinking/non-thinking 切换**；用 **GSPO**（非 GRPO）训练，避免长度偏置 |
| **2025.07** | **Kimi K2** | Moonshot AI | 1T 参数，**首次生产级用 Muon 优化器**替代 AdamW，loss 曲线异常平滑 |
| **2025.07** | **GLM-4.5 / slime RL** | Z.ai（智谱）| **agent-native MoE**，BFCL 工具调用 77.8% 超 Kimi K2/DeepSeek-R1 |
| **2026.04** | **DeepSeek V4-Pro** | DeepSeek | 1.6T/49B，1M 上下文，MIT 许可；SWE-Bench Verified **80.6%**、GPQA **90.1%**、Codeforces 3206 |
| **2026.04** | **Kimi K2.6** | Moonshot AI | SWE-Bench Pro **58.6%** 开源第一；agentic 长链强项 |
| **2026.07** | **Kimi K3**（传闻）| Moonshot AI | 传 2.8T MoE，原生视觉，1M 上下文 |
| **2026.07** | **Qwen 3.6 / 3.7 Flash** | 阿里 | Apache 2.0 最宽松，200+ 语言，Qwen Code agent 套件成熟 |

#### 重头戏：GPT vs BERT 的"信仰之战" → 2026 终章

1. **2018 GPT-1 出来立刻被 BERT 锤**：BERT 双向、参数小、效果强、刷榜。
2. **历史若停在此刻就没 OpenAI 了**——BERT 主导了 GPT-3 之前的整个 NLP。
3. **OpenAI 的信仰**：哪怕 GPT-1 作者本人（姚顺雨的导师）也不坚信，但 Ilya/Sam 坚持。
4. **本质差异**：
   - **BERT** = 简单任务（完形填空）专家，建模语言本身。
   - **GPT 的 next-token prediction** = "**大型隐式多任务学习**"，被迫学通用规律（同时预测数学 token、地理 token、轨迹 token → 学到天体运动规律）。开放性更强，但需更多数据+规模才显现。
5. **GPT-2 的两个动作**：模型 ×10、数据多样性（Reddit 高赞）→ **zero-shot 涌现**。
6. **GPT-2→GPT-3 之间的组织信号**：OpenAI 砍掉魔方/游戏 RL 团队、改组为有限盈利、拿微软 10 亿、作者数从 6→31——**这是有意识的 all-in，不是偶然**。
7. **InstructGPT 是 ChatGPT 的真正序幕**。

> **2026 闭幕词**：**Decoder-only next-token prediction 彻底统一江湖**，连 BERT 派的 embedding 角色也在被 decoder 模型侵蚀。**MoE 成为开源标配**（Llama 4 转 MoE 失败后，2026 几乎所有新开源大模型都是 MoE）。

#### 2026 闭源三极分化定型

| 厂商 | 旗舰 | 战略定位 |
|------|------|---------|
| **OpenAI** | GPT-5.6 **Sol/Terra/Luna** 分层（2026.07.09 GA）+ ChatGPT Work + Codex | "**执行平台**"——拆解任务跨模型/工具运行 |
| **Anthropic** | Claude **Opus 5**（2026.07.24）/Fable 5/Mythos 5 | "**判断角色**"——长任务、低崩溃、自我验证；Opus 5 半价 Fable 5，Frontier-Bench SOTA |
| **Google** | Gemini 3.5 Pro（2026.05，2M 上下文 + Deep Think）/3.6 **Flash 主线** | "**廉价量产**"——多模态、广覆盖、单位成本最低 |

**三大趋同**：① 全部押注 **agents**（不再卖"最聪明模型"）② 全部 **reasoning effort 分级**（low→max 5 档）③ 基准**饱和**——GPQA/MMLU 差距 3-5%，差异化转移到 post-training/工具/产品集成。

#### 2026 开源三强座次

| 模型 | 总参/激活 | 上下文 | 强项 | 许可证 |
|------|----------|--------|------|--------|
| **DeepSeek V4-Pro** | 1.6T / 49B | 1M | SWE-Bench 80.6%、GPQA 90.1% | MIT |
| **Kimi K2.6 / K3** | 1T / ~32B（K3 传 2.8T）| 256K-1M | SWE-Bench Pro 58.6% 开源第一、原生视觉、agentic | Modified MIT |
| **Qwen 3.6 / 3.7** | 235B / 22B | 256K-262K | 200+ 语言、Apache 2.0 最宽松、Qwen Code | Apache 2.0 |

> **"开源落后 2-3 年"叙事彻底破产**：DeepSeek V4-Pro 在 SWE-Bench/GPQA 与 GPT-5.5/Claude Fable 5 差距≤5%。中国实验室（DeepSeek/Kimi/Qwen）包揽开源前五。

---

### 4.4 多模态与世界模型

#### 速览表（2004–2026）

| 年份 | 论文 | 作者 | 核心贡献 |
|------|------|------|---------|
| 2014 | **Deep Video** | Andrej Karpathy（李飞飞博士生，后 OpenAI 创始成员、特斯拉 AI 总监）+ 李飞飞 | 100 万 YouTube 视频数据集；**效果仅比单帧提升 1.6 个点**——失败但奠基 |
| 2014 | **Two-Stream Networks**（双流网络）| Karen Simonyan（牛津，后 AlphaGo Zero/Inflection/微软 AI 负责人）| 引入**光流**作为运动信息原方法，首次视频理解超手工特征——**视频领域 AlexNet 时刻** |
| 2014 | **GAN** | Ian Goodfellow + Bengio | 生成器-判别器博弈，主导图像生成 5-6 年；缺点：训练不稳定、易崩 |
| 2015 | **Diffusion**（雏形）| Jascha Sohl-Dickstein（伯克利神经科学博士，原物理/火星探测器背景）| 从物理扩散过程获灵感；**被冷落 5 年**，自嘲"最不知名的扩散发明者" |
| 2020 | **DDPM** | Jonathan Ho（后创 Edify）+ Pieter Abbeel | 改"预测图像"为"预测噪声"+ 用 U-Net → **效果追平 GAN 且训练稳定** |
| 2020 | **ViT**（An Image is Worth 16×16 Words）| Google，含 Jakob Uszkoreit 顾问 | 把图像切 16×16 patch **强行序列化**，直接套 Transformer；"模型不能适应数据，就让数据适应模型" |
| 2021 | **CLIP** | Alec Radford + Ilya | 4 亿图文对**对比学习**，首次把文字与图像映射到同一空间；zero-shot 分类超 ImageNet 模型 |
| 2022 | **Stable Diffusion** | Stability AI | ① **引入潜空间**（像素压缩到 128×128）→ 计算量降 2 个量级且效果反而更好（"压缩产生智能"）② **交叉注意力**注入 CLIP 文本条件 → 真正的文生图 |
| 2022 | **DiT**（Scalable Diffusion Models with Transformers）| 谢赛宁（NYU→Meta AI）+ William Peebles（后 Sora 团队）| 把 U-Net 换成 Transformer，享受 Transformer scaling 优势；**Sora 猜测的核心技术之一** |
| **2024.02** | **Sora 技术报告**（Brooks et al. "Video Generation Models as World Simulators"）| OpenAI | DiT 在视频上的胜利，提出"视频模型=世界模拟器" |
| **2024.05** | **GPT-4o** | OpenAI | **omni-modal** 实时端到端（语音/图像/文本同入同出，~300ms 响应），打破 ASR→LLM→TTS pipeline |
| **2024.12** | **Genie 2** | Google DeepMind | **交互式世界模型**：单图生成可玩 3D 环境，autoregressive latent diffusion |
| **2025 mid** | **Veo 3** / **Genie 3** | Google DeepMind | Veo 3：物理模拟+原生音频；Genie 3：20-24 FPS 实时交互世界模型 |
| **2025.12** | **Sora 2** | OpenAI | 电影级 1080p + 同步音频 |
| **2026.02** | **ERNIE 5.0** | 百度 | 文/图/音/视频**从零联合训练**，Next-Group-of-Tokens 统一目标，超稀疏 MoE（激活<3%）|
| **2026.03** | **Qwen 3.5-Omni** | 阿里 | 真正 omnimodal 流式（文本/图/音/视频一条流）|

#### 2026 视频/世界模型四派共识

| 派别 | 代表 | 特点 |
|------|------|------|
| **生成式视频** | Sora 2、Veo 3.1、Kling 2、Hailuo 02 | 文生视频；电影/广告 |
| **物理 AI 世界模型** | NVIDIA Cosmos、V-JEPA 2（Meta）| 为机器人/AV 生成物理合理数据 |
| **交互式世界模型** | Genie 3、Decart Oasis、World Labs（李飞飞）| 单图→可玩 3D 环境 |
| **潜空间规划型** | DreamerV3、JEPA 家族、MuZero | RL + 机器人 |

#### 关键洞察
- **融合时机（early vs late fusion）**：从 2014 Deep Video 到今天阶跃星辰都在讨论，**人类是早融合（提"特朗普"即激活图像参数）→ 理论天花板更高但更难训**，10 年未收敛。
- **"压缩产生智能"再下一城**：Genie 3 用潜空间自回归扩散，Veo 3 靠物理模拟取胜——潜空间 + 物理先验成为视频模型共识。
- **谢清池预判兑现**：原文说"自回归可能再度超越 Diffusion 成为主流图像生成范式"——2026 ERNIE 5.0、自回归视频模型已在落地。

---

## 五、元洞察提炼

### A. 关于技术演进
1. **The Hardware Lottery**（硬件彩票）：算法能否主导，取决于是否适配当时主流硬件（GPU 并行）。RNN 没抽中，CNN 抽中一半，Transformer 完美抽中。
2. **支线变主线**：深度学习/GPT/Diffusion 都曾是支线，被边缘化多年——范式变迁的常态。
3. **大模型 = 偶然中的必然**：GPT-1/2 偶然，GPT-3 是有意识 all-in（拿钱、改组织、砍方向、组团队）。

### B. 关于人物
1. **多数盛产期在年轻**（无历史包袱，姚顺雨读博就有 GPT 可用）。
2. **"定义问题"型研究员影响力 ≈ "解决问题"型**：Jason Wei/姚顺雨论文难度≈博文，但定义了时代问题；Noam 这种"工程+算法双强+深耕写代码"的"老师傅"是少数稀缺品。
3. **湾区 vs 伦敦文化冲突**：硅谷偏 Infra/工程，伦敦偏算法/模型结构——Gemini 整合不顺的根源（"双子星没有双子"）。
4. **趋势：全栈 builder**。硅谷只有"软件工程师/硬件工程师"，国内细分 PM/前端/后端/算法；AI 时代回归端到端负责的 builder。

### C. 关于学习方法（与 work4ai 项目直接相关）
1. **平台期 2-3 个月**：早期读论文云里雾里、看睡着，度过之后享受第一手信息。
2. **从"是什么"到"为什么"**：单点读懂不难，难在不知道作者为何这么做——所以串联历史脉络。
3. **AI 学 AI**：沉浸式翻译、多模型交叉验证、Claude Artifacts 可视化、Deepl 划词。
4. **读懂论文的回报**：能直接看研究员分享视频、和最聪明头脑对话；能预判模型节奏、**"心安理得地等"**。

### D. 关于行业判断
1. **Scaling Law 乐观**：数据未真枯竭、test-time computing 空间大、合成数据可行——还没碰到明显天花板。
2. **OpenAI 在做下一代操作系统**：通过 MCP 把物理世界 API 接入，用参数（而非确定性软件）调度 GPU 算力。
3. **超级个体/小团队趋势**：Telegram 40 人服务 10 亿用户；但美团这类重商业模式仍需大量人——**和技术+商业模式双因素相关**。
4. **对个人建议三层**：① 多用 AI（用得好已稀缺）② 学编程+工程能力（做 builder 而非细分职能）③ 读论文（AI 是长周期浪潮，懂原理才能长期跟住）。

### E. 关于架构（2026 新共识）
1. **Transformer 不会被替换，会被 hybrid 化**：Mamba-2/Gated DeltaNet-2 + 少量 attention 锚点 + MoE = 2026 主流配方。
2. **硬件彩票二次开奖**：长上下文 + agent 把 KV cache 成本推到台前，SSM/线性 attention 再次被选中。
3. **稀疏性正交化**：token 稀疏（MoE）+ 特征稀疏（SFA）+ 静态稀疏（STEM）三轴可叠加。

### F. 关于推理（test-time scaling 的成熟）
1. **"想得久 = 更好"被证伪**：overthinking 是真实反效应，parallel thinking > sequential。
2. **reasoning effort 商品化**：5 档分级成 API 标配，"high" 常优于 "max"——**算力边际收益不再单调**。
3. **闭源-开源差距已压到 3-5%**（GPQA 90%+ 都在开源可达范围）。

### G. 关于产业（2026 H1 格局）
1. **闭源三极分化定型**：选型从"谁最聪明"变成"按工种路由"（执行/判断/量产）。
2. **开源已逼近闭源**，**中国实验室主导开源前沿**（DeepSeek/Kimi/Qwen 包揽前五），MIT/Apache 2.0 许可证成竞争武器。
3. **超级个体/小团队工具链成熟**：reasoning 分级 + agent harness（Claude Code、Cursor、Qwen Code）让端到端 builder 可行——**谢清池的预测兑现**。

---

## 六、术语纠错表（增值）

> 访谈实录为语音转写，存在大量同音错字与技术术语误识。下表为整理者根据上下文 + 技术常识核实后的纠错清单（节选 ~40 处），可用于公开版转写校对。

| 转录原文 | 正确术语 | 说明 |
|---------|---------|------|
| 全球风暴 / 圈 late | GNMT（Google Neural Machine Translation）| Google 2016 神经机器翻译系统 |
| 柬埔寨 | Gemini | Google 大模型 |
| 憨藏 / 憨藏自己写代码 | 深耕 | "硅谷工程师深耕写代码" |
| 见面 / 元宝 / 建明 | （AI 助手，结合上下文是豆包/Kimi）| —— |
| 永辉 | 吴永辉 | 字节 Seed 预训练负责人 |
| 加斯卡 | Jascha Sohl-Dickstein | Diffusion 雏形发明者 |
| Karen / 噶兰 | Karen Simonyan | 双流网络/AlphaGo Zero 作者 |
| 俄坤山 / Enoch | （Sora 团队成员，含 William Peebles）| —— |
| 说话 / 索软 / 索软小哥 | Sora | OpenAI 视频模型 |
| 控制（模型）说 | 控制力差 | 指早期 Diffusion 文生图控制力差 |
| 底 p / 底球 / 底分析波动 | DALL-E | OpenAI 文生图模型 |
| 识蒸馏 / 退售 | 知识蒸馏 | —— |
| Encode Decode | Encoder-Decoder | —— |
| 长短记忆网络 | LSTM | —— |
| 残差，隐藏 | 残差连接 | —— |
| 硬件彩票 | The Hardware Lottery | 一篇论文 |
| 余凯老师 → 应为余凯（无误）| —— | —— |
| 李菲飞 / 李菲飞老师 | 李飞飞 | ImageNet 主导者 |
| 国际内 | 国内 | —— |
| Allen 人究智能研究所 | Allen Institute for AI (AI2) | Tülu 3 出品方 |
| Tulu / Tula | Tülu 3 | AI2 的开源 posttrain 模型家族 |
| Llama 色论文 | Llama 3 论文 | —— |
| 萤火虫，二号 | 萤火虫 2 号 | DeepSeek 早期集群 |
| 阶月 / 翔宇 | 阶跃星辰 / 张翔宇 | —— |
| 扩力 | Quoc Le | Google Brain 创始成员 |
| Oracle（与 Quoc Le 并列）| Aäron van den Oord | —— |
| 黄昏冲 / Don't Teach Incentive Wise | "Don't Teach, Incentivize"（韩国研究员分享标题）| —— |
| 江苏曼中枢 | John Schulman | PPO 作者 |
| 欧阳剑 | （欧阳龙的弟弟，论文 contractor）| —— |
| 何俊贤 | —— | DeepSeek 论文讲解者（音译待核）|
| 吸收注意力 | Native Sparse Attention (NSA) | DeepSeek 稀疏注意力 |
| 助力机制 | 注意力机制 | —— |
| 自主力 | 自注意力（self-attention）| —— |
| 一吃上 | B 站 | —— |
| 卡巴西 | （Anthropic 某研究员人名音译）| 待核 |

---

## 七、与 work4ai 项目的对接

本文件作为**参考资料**，与讲透系列互补。具体对接点：

| 本文档章节 | 对接的讲透系列 | 建议用法 |
|-----------|---------------|---------|
| 4.1 Transformer / 4.3 GPT vs BERT | `讲透Transformer` / `讲透基础模型` | 提供历史脉络与人物背景，章节开头作"为什么学这个"引子 |
| 4.1 ResNet / LoRA | `讲透复用权重` / `讲透微调` | 提供"残差思想贯穿 ResNet→LoRA"的主线 |
| 4.1 CoT / ReAct / 4.3 InstructGPT | `讲透Prompt` / `讲透Agent` | 提供"上下文工程"演化时间线 |
| 4.2 Scaling Law / ZeRO / MegaScale | `讲透GPU与系统级` | 提供"算法-Infra co-design"案例 |
| 4.4 Diffusion / Stable Diffusion / DiT | `讲透生成模型` | 提供三大范式（似然/隐式/分数）演化的工业界印证 |
| 二、三 学习方法 | 全系列通用 | 章节结尾"📌下一步"可引用 |

---

## 📌 进一步阅读与练习

### 进一步阅读（2026 H1 推荐补充）
- **Sebastian Raschka《LLM Research Papers: The 2026 List (January to May)》**（magazine.sebastianraschka.com, 2026-06-06）——2026 论文逐月清单，本文件 4.1 架构部分的主要来源
- **DeepSeek-R1 论文**（arXiv:2501.12948）——开源 thinking 范式的源头
- **DeepSeek-V3 / V4 技术报告**（GitHub: deepseek-ai/DeepSeek-V3, DeepSeek-V4-Flash）——MLA + 无辅助损失 MoE 工程圣经
- **Nemotron 3 Super 技术报告**（arXiv:2604.12374）——2026 hybrid Mamba-Attn MoE 生产级实现
- **The Bitter Lesson 原文**（Richard Sutton, 2019）——全文不到 2 页，本文件板块一的"宪法"

### 练习（对接讲透系列）
1. **Transformer 章节**：对照本文 4.1 Noam 名言"归为神的仁慈"，写一段"我们当前对 Transformer 的理解边界在哪"——培养批判性视角。
2. **基础模型章节**：把 GPT-1→GPT-3 的"组织信号"（作者数 6→31、改组、拿融资、砍方向）画成决策树，回答"如果当时你是 OpenAI 决策者，会在哪一步 all-in"。
3. **生成模型章节**：用本文 4.4 的"压缩产生智能"洞察，在 `讲透生成模型` 的 VAE 实验里加一个"压缩维度 vs 重构质量"的消融，验证潜空间压缩的反直觉收益。
4. **Agent 章节**：对照本文 ReAct (2022) → CoT (2022) → o1 (2024) → R1 (2025) 路线，画出"推理-行动"范式从学术到工业的转移图。

---

**最后更新**：2026-08-03
**维护建议**：本文件可作"活清单"维护，每季度追加新论文（用 `schedule_job` 月度前沿检索自动更新候选）。
