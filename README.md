# work4ai · AI 学习知识库总览

> 一套用「直觉 → 数学 → 代码跑通 → 不足 → 应用」范式写的 AI 讲透系列。从神经网络地基到大模型全栈，每个主题都往**底层和本质**钻，配可运行实验。不是广度综述，是深度讲透。

---

## 19 个「讲透」系列 + 总纲

> 现状（2026-08-03 实盘核对）：13 个有完整内容、16 个讲透系列已开篇（含博士级试点 + 思想史 + 博士地基）+ **讲透AIfor各学科 20 个学科开篇**（物理/化学/生物/材料/天文/地球气候/芯片设计/经济金融/法学/哲学/数学/统计学/机器人/心理学/政治学/历史学/语言学/教育/能源/农业）。**总计 36 个讲透系列 + 20 个 AIfor 各学科子系列**。

### A. 已完整（12 个）✅

| 系列 | 讲什么 | 篇数 |
|---|---|---|
| **讲透激活函数** | 神经网络地基：非线性 → ReLU → 家族 → 量化 → SwiGLU | 7+实验 |
| **讲透反向传播** | 反传本质 → VJP 统一视角 → 手算 MLP → 计算图 → 故障 | 9+README |
| **讲透基础模型** | NTP 第一性原理 → 注意力 → 规模律 → 涌现 → 对齐 → 部署 | 7+数学+实验 |
| **讲透Transformer** | 全景 → Self-Attention → 位置编码 → 变体 → MoE → 推理优化 | 10 |
| **讲透微调** | LoRA 第一性原理 → 数学 → PEFT → QLoRA → 数据 → 失败 → 实战 | 7+实验 |
| **讲透Prompt** | 条件概率 → ICL → CoT → 结构化输出 → 上下文工程 | 5+实验 |
| **讲透RAG** | 为什么需要 → 检索数学 → 工程 → 高级架构 → 评估 | 5+实验 |
| **讲透PyTorch** | Tensor → Autograd → nn.Module → 训练循环 → AMP → torch.compile → 生态 | 10 |
| **讲透GPU与系统级** | FlashAttention → PyTorch 内部 → 推理引擎 → 量化 → 并行通信 → CUDA → Triton | 8+实验 |
| **讲透复用权重** | 迁移学习 → 预训练范式 → PEFT → 蒸馏 → 持续学习 → LoRA 深水区 | 10 |
| **讲透泛化** | 泛化悖论 → 隐式正则 → 平坦极小值 → 双层下降 → 归纳偏置 | 6+练习+实验 |
| **讲透生成模型** | 统一视角 → AR → VAE → GAN → Flow → Diffusion → Score/SDE | 9+README |
| **讲透AI应用全景** | 应用视角：AI4Science/AI4Math/AI4Code/Medicine/创意/企业/**AI for AI** 七大领域 | 8（README+00+01-07）|

### B. 待补全（16 个，已开篇）🟡

| 系列 | 现状 |
|---|---|
| **讲透Agent** | `00` + `01-经典范式对比`（在写）|
| **讲透优化器** | 仅 `00-优化器全景.md`（236 行全景已写），待补各优化器深挖 |
| **讲透损失函数** | 仅 `00-损失函数全景.md`，待补各 loss 深挖 |
| **讲透KV Cache** | `00` + `01` + README（推理优化核心），待补 02-07（PagedAttention/RadixAttention/MLA/量化/分层）|
| **讲透RL**（新）| README + `00`(MDP) + `01`(DQN) + `02`(PPO) + `03`(RLHF/DPO/GRPO)，LLM 对齐核心 |
| **讲透分布式AI系统**（新）| README + `00`(显存账) + `01`(DDP/FSDP) + `02`(ZeRO) + `03`(TP/PP)，大模型训练工程 |
| **讲透可解释性**（新）| README + `00`(为什么 AI 是黑箱)，三条路径 + mechanistic interpretability，配套 07 第⑥层 |
| **讲透数据**（新）| README + `00`(数据是新的代码) + `03`(Model Collapse 数学证明)，数据墙/Chinchilla/合成数据，配套 07 第③层 |
| **讲透科学的现代性**（新）| README + `00`(总览) + `01`(第五范式) + `02`(可重复性危机) + `03`(科学哲学)，三视角合一 |
| **讲透世界模型**（新·博士级试点）| README + `00`(四派统一框架) + **advanced/ 4 篇**（论文清单+JEPA数学+Sora批判+10博士方向），首批博士级 + 研究前沿级试点 |
| **讲透AI历史**（新·思想史）| README + `00`(思想史方法论) + **advanced/00**(必读书单+30 篇论文) + **advanced/01**(范式转移库恩分析) |
| **讲透统计学习理论**（新·博士地基）| README + `00`——scaling law/双层下降的数学根基 |
| **讲透概率图模型**（新·博士地基）| README + `00`——VAE/扩散的理论祖父 |
| **讲透因果推断**（新·博士地基）| README + `00`——Pearl do-calculus + Rubin 反事实 |
| **讲透符号主义**（新·博士地基）| README + `00`——GOFAI + Neurosymbolic + AlphaProof |
| **讲透优化理论**（新·博士地基）| README + `00`——Adam 收敛性 + 非凸优化理论 |

### C. 总纲

| 系列 | 讲什么 | 状态 |
|---|---|---|
| **横向打通** | AI 能力获取决策框架（微调/RAG/Prompt/Agent 何时用谁）| ✅ |

---

## 参考资料（非教程类）

非教程的**公开课清单、信息源、访谈整理**等，与讲透系列互补——讲透钻深度，这里提供**广度的脉络、人物、历史、前沿**。可作为讲透系列章节的背景阅读与延伸。

按"如何使用"分四块（每一块都和讲透系列交叉验证）：

### 1. 系统学：[`讲透公开课/`](讲透公开课/)（按课表走）

| 文件 | 类型 | 收录范围 |
|------|------|---------|
| [`讲透公开课/01-前沿课实时清单.md`](讲透公开课/01-前沿课实时清单.md) | **AI/ML/DL 神课清单**（10 门）| Karpathy Zero-to-Hero / CS224n Winter 2026 / CS231n / MIT 6.S191 / 李宏毅 / DLSys Fall 2025 / CS285 Spring 2026 / fast.ai / 等。2026-07-31 全量联网核对。 |
| [`讲透公开课/02-数理计算机神课清单.md`](讲透公开课/02-数理计算机神课清单.md) | **数学/物理/CS 神课清单**（30+ 门）| Strang 18.06 / Stat 110 / Lewin 物理 / David Tong 笔记 / Preskill 量子 / MIT 6.5840 / 6.1810 / CMU 15-445 / CSAPP 等。2026-08-03 核对。 |
| [`讲透公开课/03-AI Infra 源码导读清单.md`](<讲透公开课/03-AI Infra 源码导读清单.md>) | **AI Infra 开源项目源码导读**（20+ 项目）| vLLM / SGLang / Ray / Triton / Megatron / DeepSpeed / FlashAttention / CUTLASS / NCCL 等。每个给仓库+论文+关键源码文件+阅读路径。2026-08-03 联网核对。 |
| [`讲透公开课/04-全领域学习路径总览.md`](讲透公开课/04-全领域学习路径总览.md) | **路线图**（7 条路径 + 5 档时间预算）| 把 01/02/03 + 14 个讲透系列编排成按目标/按时间的路径，含自我诊断。 |

### 2. 日常跟前沿：[`前沿与媒体/`](前沿与媒体/)（保持手感）

**入口**：从 [`前沿与媒体/00-角色 × 专题推荐矩阵.md`](前沿与媒体/00-角色%20×%20专题推荐矩阵.md) 开始，按你的角色选 3 份精读。

| 文件 | 类型 | 收录范围 |
|------|------|---------|
| [`前沿与媒体/00-角色 × 专题推荐矩阵.md`](前沿与媒体/00-角色%20×%20专题推荐矩阵.md) | **导航入口** | 13 个角色 × 12 份专题的推荐矩阵 + 时间预算 + 痛点反查。第一次来从这里开始。 |
| [`前沿与媒体/01-AI顶级信息源实时清单.md`](前沿与媒体/01-AI顶级信息源实时清单.md) | **AI 顶级信息源清单**（9 大类 80+ 条）| 论文聚合（arXiv/HF Papers/AK）/ 顶级播客（Lex/Dwarkesh/MLST/Latent Space）/ 个人博客（Karpathy/Lilian Weng/Raschka）/ 机构 blog / Newsletter / 社区 / 中文资源 / AI Safety / 评测榜单。2026-08-03 二轮核对（联网实抓 50+ URL）。 |
| [`前沿与媒体/02-后训练信息源专题.md`](前沿与媒体/02-后训练信息源专题.md) | **后训练垂直专题**（8 大类 30+ 条）| 综述博客（Nathan Lambert/Lilian Weng/Raschke）/ 代码库（TRL/PEFT/Axolotl/Unsloth/LLaMA-Factory/OpenRLHF/open-instruct）/ 数据集（UltraFeedback/HH-RLHF/Magpie/Tülu mix）/ 评测（RewardBench/AlpacaEval/LightEval）/ 关键论文（InstructGPT/CAI/DPO/KTO/GRPO/DeepSeek-R1）。2026-08-03 首版核对。 |
| [`前沿与媒体/03-模态专题（NLP+Vision+Speech+多模态）.md`](前沿与媒体/03-模态专题（NLP+Vision+Speech+多模态）.md) | **模态垂直专题**（4 大模态 60+ 条）| NLP（Transformers/HanLP/spaCy/ACL）/ Vision（OpenCV/YOLO26/Detectron2/CLIP/SAM/CVPR）/ Speech（Whisper/FunASR/ESPnet/Bark/Interspeech）/ 多模态（CLIP/LLaVA/SAM/BLIP）。2026-08-03 首版（NLP/Vision 全核，Speech 部分待补）。 |
| [`前沿与媒体/04-Document AI 与文档智能专题.md`](前沿与媒体/04-Document%20AI%20与文档智能专题.md) | **Document AI 垂直专题**（30+ 条）| 解析器（GROBID/Marker/Nougat/MinerU/Docling/Unstructured）/ 商业服务（LlamaParse/Mathpix/Azure DI）/ 经典论文（LayoutLM/Donut/Nougat/DocOwl）/ 中文场景（PaddleOCR/MinerU/Pix2Text）。2026-08-03 首版。 |
| [`前沿与媒体/05-AI研究工作流与学术工具专题.md`](前沿与媒体/05-AI研究工作流与学术工具专题.md) | **AI 研究工具专题**（30+ 条）| 发现（Consensus 2.5亿论文/Elicit/Connected Papers/SciSpace/ResearchRabbit）/ 阅读（Claude/GPT/Kimi/ChatPDF）/ 管理（Zotero 全平台）/ 写作（Claude+Overleaf/Grammarly/Writefull）/ 中文专属（Kimi 长上下文）。2026-08-03 首版（7 个工具全部实抓活跃）。 |
| [`前沿与媒体/06-AI编程工具专题.md`](前沿与媒体/06-AI编程工具专题.md) | **AI 编程专题**（IDE/Agent/模型/评测）| Cursor / Windsurf / Claude Code（**Anthropic 2026-08 Sonnet 5/Opus 5/Fable 5**）/ OpenHands / Cline / Aider / Devin + 评测（SWE-Bench / LiveCodeBench）+ 中文（通义灵码 / DeepSeek-Coder）。2026-08-03 首版。 |
| [`前沿与媒体/07-AI创意生成专题.md`](前沿与媒体/07-AI创意生成专题.md) | **创意生成专题**（图/视频/音乐/3D）| Midjourney / Flux / Stable Diffusion / ComfyUI + Sora / Veo / **Runway（已定位世界模型）** / Wan / Kling + Suno / Udio / MusicGen + Point-E / Shap-E / TripoSR。2026-08-03 首版。 |
| [`前沿与媒体/08-AIAgent框架与工具调用专题.md`](前沿与媒体/08-AIAgent框架与工具调用专题.md) | **Agent 框架专题**（框架/协议/平台/评测）| LangGraph / AutoGen / CrewAI / LlamaIndex / Agno / Pydantic AI / Smolagents + **MCP（事实标准）** / Function Calling / Anthropic "Building Effective Agents" + 评测（SWE-Bench / WebArena / GAIA / τ-bench）+ 中文（Manus / MetaGPT / Coze / AutoGLM）。2026-08-03 首版。 |
| [`前沿与媒体/09-AI商业产品与ToC应用专题.md`](前沿与媒体/09-AI商业产品与ToC应用专题.md) | **AI 商业产品地图**（通用/垂直/办公/搜索/API）| ChatGPT / **Claude（Sonnet 5/Opus 5/Fable 5）** / Gemini / Copilot / Grok / Perplexity + 豆包 / Kimi / 通义 / 文心 / DeepSeek / 智谱清言 + 垂直（Notion AI / Glean / Julius）+ API（OpenRouter / Together / SiliconFlow）。2026-08-03 首版。 |
| [`前沿与媒体/10-AI评测与基准大合集.md`](前沿与媒体/10-AI评测与基准大合集.md) | **AI 评测大合集**（8 个能力维度）| 通用（LMSYS/OpenCompass **GPT-5.4 SOTA**/Open LLM/SuperCLUE/Artificial Analysis/Scale SEAL）+ 代码（SWE-Bench **SWE-agent-LM-32B 开源 SOTA**/HumanEval/LiveCodeBench）+ Agent（WebArena/GAIA/τ-bench/MLE-Bench）+ 多模态（MMMU/MMBench）+ 推理/数学（GPQA/AIME/MATH）+ 长上下文（LongBench/RULER）+ 中文（C-Eval/CMMLU）+ 安全（HarmBench/AdvBench/TruthfulQA）。2026-08-03 首版。 |
| [`前沿与媒体/11-AI政策、伦理与Safety专题.md`](前沿与媒体/11-AI政策、伦理与Safety专题.md) | **政策/Safety 深化**（4 层 60+ 条）| 法规（**EU AI Act 实抓**/NIST AI RMF/UK AISI/中国生成式 AI 办法）+ 标准（ISO 42001/NIST AI RMF/OECD/UNESCO）+ 研究机构（Anthropic Alignment/Redwood/Apollo/CAIS/MIRI）+ 关键论文（Constitutional AI/Sleeper Agents/Sycophancy/Superposition）+ 伦理（公平/偏见/隐私/版权）+ 国际峰会（Bletchley/Frontier Model Forum）+ 中文治理（信通院/清华 I-AIGC/薛澜）。2026-08-03 首版。 |
| [`前沿与媒体/12-AI硬件与算力专题.md`](前沿与媒体/12-AI硬件与算力专题.md) | **AI 硬件上游**（4 层 50+ 条）| 芯片（**NVIDIA H100/B200/Vera Rubin** / AMD MI300X / Google TPU / Intel Gaudi / **Groq LPU** / Cerebras WSE / Tenstorrent / SambaNova / 华为昇腾 / 寒武纪 / 摩尔线程）+ HBM（SK Hynix / Samsung / Micron）+ 晶圆厂（TSMC / Samsung / Intel / SMIC）+ 数据中心（CoreWeave / Nebius / Stargate 5000亿）+ 能源 + 关键人物（**Jensen Huang / Jim Keller / Lisa Su / Dylan Patel**）。2026-08-03 首版。 |
| [`前沿与媒体/13-AI学术圈与PhD招聘专题.md`](前沿与媒体/13-AI学术圈与PhD招聘专题.md) | **AI 学术生态**（4 层 40+ 条）| 北美顶级（**MIT CSAIL / Stanford HAI / Berkeley BAIR / CMU RI** 实抓活跃 / Princeton NLP / UW / NYU / Toronto / MILA / ETH）+ 中国（**上海 AI Lab / BAAI / 清华交叉信息院** 实抓）+ PhD 申请时间线 + 选校 Tier + 奖学金（NSF GRFP / CSC / Anthropic Doctoral Fellowship）+ Frontier Labs 实习（OpenAI Residency / Anthropic / DeepMind / FAIR / MSR）+ 签证（F1/O-1/EB-1A/Global Talent/Tech.Pass）。2026-08-03 首版。 |
| [`前沿与媒体/14-AI军事与国防专题.md`](前沿与媒体/14-AI军事与国防专题.md) | **AI 军事化**（5 层 50+ 条）| 公司（**Palantir/Anduril（实抓 Thunder/Ghost）/Scale AI Defense/Shield AI/Helsing**）+ 应用场景（ISR/决策/自主武器/网络太空）+ 各国战略（美 Replicator / 中 / 俄 / 乌实战 / 以 Lavender）+ 关键事件（Project Maven / 纳卡 / 俄乌战 / 加沙）+ 伦理（CCW LAWS / 人在回路）+ 中文（国防科大 / CETC / 大疆）。2026-08-03 首版。 |
| [`前沿与媒体/15-AI for Science 专题.md`](前沿与媒体/15-AI%20for%20Science%20专题.md) | **AI for Science**（4 象限 40+ 条）| 生物化学（**AlphaFold 2/3 + 2024 诺奖** / ESM 4.2k / DeepChem 6.9k / RoseTTAFold / Boltz-2）+ 材料化学（GNoME / MACE / PySCF 1.6k / OpenMM 1.9k / DeePMD）+ 数学推理（AlphaProof / AlphaGeometry 2 / Lean / AlphaEvolve）+ 物理（DeepMind AI 飞控 / 聚变 / GraphCast 天气）。2026-08-03 首版。 |
| [`前沿与媒体/16-AI重点行业（医疗+金融+法律+教育）.md`](前沿与媒体/16-AI重点行业（医疗+金融+法律+教育）.md) | **AI + 重点行业**（4 大行业 60+ 条）| 医疗（Hippocratic AI / OpenEvidence / Med-PaLM / Paige / 腾讯觅影）+ 金融（BloombergGPT / FinGPT / Kensho / 蚂蚁 ChatANT）+ 法律（**Harvey 实抓 "Purpose built agents"** / Casetext/CoCounsel / EvenUp / LexisNexis / 法小通）+ 教育（Khanmigo / Duolingo Max / Speak / 松鼠 AI）+ 其他（政务/房产/制造/农业/零售）。2026-08-03 首版。 |
| [`前沿与媒体/17-AI芯片设计与电子研发专题.md`](前沿与媒体/17-AI芯片设计与电子研发专题.md) | **AI 芯片设计 / EDA**（流程 + 工具）| 里程碑（**AlphaChip 用在 TPU v5/v6 设计** / ChipNeMo）+ 开源（**OpenROAD 2.9k ⭐** / Yosys / OpenROAD-flow-scripts / Sky130 PDK）+ 商业三巨头（**Synopsys（实抓）/ Cadence（实抓"physics-based AI"）/ Siemens EDA**）+ LLM 写 Verilog（VerilogEval / RTLCoder / ChipNeMo）+ 中文（华大九天 / 概伦 / 芯和）。2026-08-03 首版。 |
| [`前沿与媒体/18-AI自动驾驶与具身机器人专题.md`](前沿与媒体/18-AI自动驾驶与具身机器人专题.md) | **自动驾驶 + 具身机器人**（共享技术栈 60+ 条）| 自驾（Tesla FSD / Waymo / Cruise / **comma.ai 6.33w ⭐ / Apollo 2.68w ⭐ / Carla 1.42w ⭐** / Wayve / Nuro + 中国百度/小马/文远/Momenta/华为 ADS/小鹏 XNGP/蔚来/理想/小米）+ 人形机器人（**Figure / Tesla Optimus / 1X / Agility Digit / Boston Dynamics / Unitree / 智元 / Galbot**）+ 模型（RT-2 / Aloha / OpenVLA / Octo / **Pi π0** / NVIDIA GR00T）。2026-08-03 首版。 |
| [`前沿与媒体/19-AI网络安全与对抗专题.md`](前沿与媒体/19-AI网络安全与对抗专题.md) | **网络安全 + AI 双向战场**（攻击 + 防御 60+ 条）| 防御公司（CrowdStrike / Microsoft Copilot for Security / Google Mandiant / Wiz / SentinelOne Purple / Darktrace / Palo Alto XSIAM / Splunk + 中文奇安信/深信服/绿盟/360）+ 攻击（WormGPT/FraudGPT/2024 香港 Arup 2 亿 Deepfake 骗案）+ 开源（**Zeek 7.8k ⭐ / Suricata 6.5k ⭐ / Security Onion 4.8k ⭐**）+ AI 应用安全（Prompt Injection / OWASP LLM Top 10 / MITRE ATLAS）+ 会议（DEF CON / Black Hat / DARPA AIxCC）。2026-08-03 首版。 |
| [`前沿与媒体/20-AI艺术与创意社区专题.md`](前沿与媒体/20-AI艺术与创意社区专题.md) | **AI 艺术社区**（实操向 60+ 条）| Civitai（**实抓** models/images/videos/3D/comics/challenges 全栈）/ HF Spaces（"AI App Directory"）/ Krea（**实抓** Realtime Image+Video）/ Lexica / Leonardo / Midjourney Explore + 视频（Pika/Runway）+ 音乐（Suno/Udio）+ 写作（Character.ai/NovelAI）+ 比赛（Colorado State Fair/Civitai Challenges）+ 版权争议（Jason Allen 2022/Karla Ortiz 诉 SD/NYT 诉 OpenAI）+ 关键人物（Refik Anadol/Mario Klingemann/Beeple）。2026-08-03 首版。 |
| [`前沿与媒体/21-AI哲学、意识与认知科学专题.md`](前沿与媒体/21-AI哲学、意识与认知科学专题.md) | **AI 哲学 + 意识**（思辨向 60+ 条）| 5 大追问（强 AI/意识/理解/超智/模拟）+ 哲学家（**David Chalmers 实抓 NYU**/**Nick Bostrom 实抓 2026-08 "superintelligence not very far off" + Deep Utopia 中译**/Dennett 已逝/Searle 已逝/Churchland/Andy Clark/Schneider/Shanahan）+ 5 大意识理论（Hard Problem/IIT/GWT/HOT/Predictive Processing）+ Anthropic Consciousness 报告 + 强 AI 论战 + 10 本必读书 + 7 篇关键论文 + Sean Carroll/Lex Fridman 播客。2026-08-03 首版。 |
| [`前沿与媒体/22-AI历史与人物传记专题.md`](前沿与媒体/22-AI历史与人物传记专题.md) | **AI 史 + 人物**（知识向 80+ 条）| 七幕史（1943 黎明 → 1956 达特茅斯 → 1974/1987 两次寒冬 → 2012 AlexNet → 2022 ChatGPT → 2026 当前）+ 完整年表（30+ 关键节点）+ 群像（**三巨头 Hinton/LeCun/Bengio** + Ilya Sutskever / Karpathy / Vaswani / Altman / Amodei / Hassabis + RL 派 Silver/Schulman/Levine + 中国李飞飞/唐杰/黄铁军/梁文锋 + 哲学家）+ 经典书（AIMA/Deep Learning/Alignment Problem/Genius Makers/Deep Utopia）+ 纪录片（AlphaGo/Coded Bias/Social Dilemma/Her/Ex Machina）+ 7 大争论史。2026-08-03 首版。 |
| [`前沿与媒体/23-AI教育与学习路径专题.md`](前沿与媒体/23-AI教育与学习路径专题.md) | **AI 教育**（3 场景 50+ 条）| 用 AI 学（**Khanmigo 实抓** / Duolingo Max / Speak / Photomath / Wolfram / 中文作业帮/学而思）+ 用 AI 教（MagicSchool / Century / Squirrel AI / Khanmigo for Teachers / Turnitin AI）+ 学 AI（**DeepLearning.AI 实抓** / fast.ai / Coursera / 3B1B / Karpathy Zero to Hero / MIT RAISE / AI4K12）+ UNESCO 指南 + Sal Khan《Brave New Words》。2026-08-03 首版。 |
| [`前沿与媒体/24-AI地缘政治与产业政策专题.md`](前沿与媒体/24-AI地缘政治与产业政策专题.md) | **AI 大国博弈**（各国战略 60+ 条）| 美国（**BIS 出口管制实抓** / CHIPS Act / NAII / EO 14110）+ 中国（**新一代 AI 规划 / 生成式 AI 办法 / 算法备案 / 东数西算 / 新质生产力**）+ 欧盟（AI Act / GDPR / GAIA-X）+ 英国（**UK AISI 实抓** / Bletchley）+ 日韩印新阿以俄 + Chip War（TSMC 全球扩张 / ASML EUV 禁运 / SMIC 7nm 突破）+ Chris Miller《Chip War》+ Jeffrey Ding《ChinAI》。2026-08-03 首版。 |
| [`前沿与媒体/25-AI隐私与生物特征专题.md`](前沿与媒体/25-AI隐私与生物特征专题.md) | **AI 隐私 + 生物特征**（矛与盾 50+ 条）| 识别（**Clearview AI 300 亿人脸** / 商汤 / 旷视 / AI 四小龙 / PimEyes / AWS Rekognition）+ 反识别（CV Dazzle）+ 语音克隆（ElevenLabs / 拜登假语音 / 香港 Arup 案 / 斯嘉丽 vs OpenAI Sky）+ Deepfake（政治/色情/广告）+ 检测（Sensity / C2PA / SynthID）+ 数据投毒（**Glaze/Nightshade/PhotoGuard**）+ 隐私机器学习（差分隐私/联邦/同态/MPC/TEE）+ 全球法（GDPR/CCPA/PIPL/BIPA/HIPAA/COPPA）+ Zuboff/Buolamwini/O'Neil/EFF。2026-08-03 首版。 |
| [`前沿与媒体/26-AI游戏与互动娱乐专题.md`](前沿与媒体/26-AI游戏与互动娱乐专题.md) | **AI + 游戏**（3 场景 50+ 条）| AI 玩（深蓝 1997 / **AlphaGo 2016** / AlphaStar / OpenAI Five / Pluribus / MuZero / CICERO / **SIMA** / World Mini）+ AI 设计（AI Dungeon / GameNGen 重构 Doom / Genesis / 资产生成 Scenario）+ AI NPC（**Inworld 实抓 Realtime TTS-2** / Convai / NVIDIA ACE / Ubisoft NEO / Stanford Generative Agents / Voyager）+ 棋类（Stockfish NNUE / KataGo / Pluribus）+ Unity ML-Agents / Unreal / Roblox / GDC / AIIDE。2026-08-03 首版。 |
| [`前沿与媒体/27-AI + 实体产业（制造+物流+能源+农业+建筑）.md`](前沿与媒体/27-AI%20+%20实体产业（制造+物流+能源+农业+建筑）.md) | **AI + 实体产业**（5 个重资产行业 50+ 条）| 制造（**西门子 Xcelerator/Industrial Copilot + NVIDIA Omniverse 数字孪生** + Bosch/Augury/Samsara/海康/三一/海尔卡奥斯）+ 物流（FedEx/UPS/DHL/**Flexport 实抓** / Maersk/Locus/Symbotic + 顺丰/菜鸟/京东物流/满帮）+ 能源（国家电网/BP/Shell/Tesla Energy/Climate Trace/Pachama）+ 农业（**John Deere See & Spray** + Bayer/Carbon Robotics 激光除草/极飞/大疆农业）+ 建筑（Autodesk Revit+Forma / Bentley / Trimble / Procore / 广联达）。2026-08-03 首版。 |
| [`前沿与媒体/28-AI + 消费服务（零售+电商+旅游+餐饮+媒体+广告）.md`](前沿与媒体/28-AI%20+%20消费服务（零售+电商+旅游+餐饮+媒体+广告）.md) | **AI + 消费服务**（6 大行业 60+ 条）| 零售/电商（Amazon Rufus + Just Walk Out / 阿里万相台 / JD 言犀 / 拼多多 Temu / Shopify Magic / Stripe）+ 旅游（**Booking/Expedia/Airbnb/Hopper** / Trip.com）+ 餐饮（McDonald's Drive-Thru/Starbucks Deep Brew/美团/海底捞）+ 媒体（NYT/WaPo/FT/Bloomberg + 字节/快手/B 站/小红书）+ 广告（Google P-Max / Meta Advantage+ / 字节巨量引擎 / **Adobe GenStudio 实抓** / Jasper / Copy.ai）。2026-08-03 首版。 |
| [`前沿与媒体/29-AI + 专业服务（保险+HR+设计+体育+政务+非营利+电信）.md`](前沿与媒体/29-AI%20+%20专业服务（保险+HR+设计+体育+政务+非营利+电信）.md) | **AI + 专业服务**（7 个行业 40+ 条）| 保险（Lemonade / Tractable / Shift / 平安）+ HR（LinkedIn / Workday / HireVue / Eightfold / 北森 / Moka）+ 设计（**Adobe Sensei 实抓** / Figma AI / Canva Magic）+ 体育（Second Spectrum / Catapult / Hudl）+ 政务（Palantir Foundry / 一网通办 / Microsoft Gov / AWS GovCloud）+ 非营利（GiveDirectly / Open Philanthropy）+ 电信（中国移动 / AT&T / 华为 + 5G AI）。2026-08-03 首版。 |
| [`前沿与媒体/30-AI金融科技深化专题.md`](前沿与媒体/30-AI金融科技深化专题.md) | **金融深化**（5 大场景 40+ 条）| 量化（Renaissance/Citadel/Two Sigma/**幻方（DeepSeek 母公司！）**/九坤/明汯 + Crypto 量化 Wintermute/Jump）+ 反欺诈/AML（Sift/Riskified/Feedzai/蚂蚁 AlphaRisk/腾讯天御）+ 信贷（Upstart/Zest AI/芝麻信用/微众）+ 支付（Stripe/Adyen/Visa/支付宝/微信）+ 加密（Chainlink/Binance/SingularityNET/Numerai）+ Jim Simons / 梁文锋。2026-08-03 首版。 |
| [`前沿与媒体/31-AI与Web3区块链专题.md`](前沿与媒体/31-AI与Web3区块链专题.md) | **AI × Web3**（4 大交叉 30+ 条）| 去中心化算力（Render/Akash/Fetch.ai/io.net/Gensyn/Ritual）+ 数据市场（Ocean/Filecoin/Arweave）+ AI Agent + DAO（**SingularityNET Ben Goertzel**/Fetch.ai/Autonolas/Numerai）+ AI NFT（Botto DAO）+ 监管（SEC）+ Ben Goertzel/Humayun Sheikh/Vitalik 评论。2026-08-03 首版。 |
| [`前沿与媒体/32-AI心理健康与心理治疗专题.md`](前沿与媒体/32-AI心理健康与心理治疗专题.md) | **心理 AI**（光谱 30+ 条）| 自助/CBT（Woebot/Wysa/Tess/Headspace AI）+ AI 伴侣（**Replika**/Character.ai/Pi）+ 国内（心岛日记/简单心理 AI）+ 技术（LLM 情感识别/CBT 脚本/语音生物标记/VR 暴露）+ 伦理（依赖/幻觉/数据隐私/**意大利禁 Replika**/比利时男子自杀事件）+ Alison Darcy/Eugenia Kuyda。2026-08-03 首版。 |
| [`前沿与媒体/33-AI翻译与多语言专题.md`](前沿与媒体/33-AI翻译与多语言专题.md) | **翻译 + 多语言**（4 代史 30+ 条）| 商业（**DeepL/Google/Azure/百度/有道/Yandex**）+ LLM 翻译（GPT-4/Claude/Gemini）+ CAT 工具（Trados/MemoQ/Smartcat/Crowdin）+ 开源（Meta **NLLB-200**/SeamlessM4T/OpenNMT/Argos）+ 多语言 LLM（Cohere Aya/Qwen/DeepSeek）+ 场景（学术/跨境/本地化/字幕/同传/低资源保护）。2026-08-03 首版。 |
| [`前沿与媒体/34-AI开源生态（HF与ModelScope）专题.md`](前沿与媒体/34-AI开源生态（HF与ModelScope）专题.md) | **AI 开源生态**（4 层 40+ 条）| Hugging Face（Hub/Datasets/Spaces/Transformers/PEFT/TRL/Courses）+ **旗舰开源模型**（Llama 3.5/4/Mistral/Qwen 3.5/**DeepSeek R1**/Phi/Gemma/Kimi K3/GLM-4.5）+ ModelScope 魔搭（阿里）+ 推理服务（Replicate/Together/Fireworks/Modal/**OpenRouter**/SiliconFlow/DeepInfra）+ 数据集 Hub（HF/Kaggle/LAISON/Common Crawl）+ Agent 市场（Coze/GPT Store/Poe）。2026-08-03 首版。 |
| [`前沿与媒体/35-AI创业投资生态专题.md`](前沿与媒体/35-AI创业投资生态专题.md) | **AI 创投**（5 层 50+ 条）| VC（**a16z/Sequoia/Founders Fund/Khosla**/Thrive/YC + 红杉中国/HongShan/启明/真格/高瓴 + PIF/SoftBank/NVIDIA）+ 孵化器（YC/Anthropic Startup Fund/a16z Startup School/奇绩创坛/NVIDIA Inception）+ 独角兽 2024-2026（**OpenAI $500B/Anthropic $60B/xAI $80B/Databricks $62B/Scale $14B/Perplexity $9B/Cohere $5B/Mistral $6B/Figure $2.6B/Harvey $3B/Anysphere Cursor $10B+** + 中国智谱/Kimi/MiniMax/阶跃/百川/DeepSeek）+ 薪资（顶级研究员 $1-10M）+ 必读（YC Library/**Paul Graham**/Sam Altman Essays/a16z Future/Stratechery/The Information/The Generalist）。2026-08-03 首版。 |
| [`前沿与媒体/36-AI数据标注与RLHF数据专题.md`](前沿与媒体/36-AI数据标注与RLHF数据专题.md) | **数据标注**（4 波 30+ 条）| 顶级公司（**Scale AI $14B**/Surge AI/Labelbox/Snorkel/Appen/Invisible/Remotasks + 中文龙猫/海天瑞声/数据堂）+ RLHF 数据（UltraFeedback/HH-RLHF/ShareGPT/OpenAssistant/Magpie）+ 自托管工具（Label Studio/CVAT/Doccano/Prodigy/Argilla）+ 合成数据（Gretel/Mostly AI/Tonic）+ 伦理（非洲/菲律宾 $1-2/时血汗 + COPPA）。2026-08-03 首版。 |
| [`前沿与媒体/37-AI MLOps与工程化专题.md`](前沿与媒体/37-AI%20MLOps与工程化专题.md) | **MLOps 全流程**（7 阶段 50+ 条）| 实验追踪（**W&B 事实标准**/MLflow/Comet/Neptune/Aim）+ 特征存储（Feast/Tecton/DVC）+ 编排（Kubeflow/Airflow/Prefect/Dagster/Metaflow/Flyte）+ 部署（BentoML/Seldon/KServe/Triton）+ 监控（Evidently/Arize/Fiddler/WhyLabs）+ 商业平台（Databricks/SageMaker/Vertex AI/Azure ML）+ **LLMOps 新分支**（LangSmith/Langfuse/Helicone/Portkey/Braintrust）。2026-08-03 首版。 |
| [`前沿与媒体/38-AI量子计算专题.md`](前沿与媒体/38-AI量子计算专题.md) | **量子 × AI**（3 路线 40+ 条）| 平台（IBM Quantum+Qiskit/Google Sycamore+Willow/Azure Quantum/AWS Braket/IonQ/Quantinuum/Rigetti/PsiQuantum + 中国中科大九章/祖冲之）+ QML（**PennyLane 事实标准**/Qiskit ML/TF Quantum/Cirq）+ AI for Quantum（DeepMind 2024 RL 解码 Surface Code）+ 关键人物（**Preskill/Neven/潘建伟/Scott Aaronson**）+ Nielsen-Chuang 教材。2026-08-03 首版。 |
| [`前沿与媒体/39-AI数学与形式化专题.md`](前沿与媒体/39-AI数学与形式化专题.md) | **AI + 数学形式化**（30+ 条）| 系统（**Lean 4 + Mathlib 当前最热**/Coq/Isabelle/HOL Light/Agda）+ ATP（AlphaProof IMO 银牌/AlphaGeometry 2/Lean Copilot/LeanDojo/COPRA/LLEMMA/DeepSeek-Prover）+ 数据集（MINIF2F/ProofNet/Lean-Workbook）+ 关键事件（**Scholze Liquid Tensor/Terence Tao 用 Lean/AlphaProof 2024**）+ Terence Tao/Scholze/Kevin Buzzard/Leo de Moura。2026-08-03 首版。 |
| [`前沿与媒体/40-AI算力市场与集群调度专题.md`](前沿与媒体/40-AI算力市场与集群调度专题.md) | **算力市场**（4 级 40+ 条）| GPU 云（**CoreWeave NASDAQ:CRWV**/Lambda/Nebius/Together/Fireworks/Replicate/Modal/RunPod/Vast.ai/Crusoe + 中文阿里云/火山引擎）+ 调度（Slurm/Kubernetes+Volcano/Ray/SkyPilot/Run:AI 被 NVIDIA 收购）+ GPU 期货 + 成本表（H100 $1.5-5/时，B200 $5-15/时）+ 关键源（**SemiAnalysis Dylan Patel**）。2026-08-03 首版。 |
| [`前沿与媒体/41-AI玩具与儿童产品专题.md`](前沿与媒体/41-AI玩具与儿童产品专题.md) | **AI 玩具 / 儿童**（2 类 30+ 条）| 教育/陪伴硬件（**Moxie（破产复活）/Moflin/Anki Vector/Mattel+OpenAI/字节豆包玩具/Disney**）+ 软件教育（Duolingo Kids/Khanmigo Kids/Lingokids）+ 伦理（COPPA/GDPR-K/依恋风险/发展影响/Moxie 破产断云变废铁事件）+ Paolo Pirjanian。2026-08-03 首版。 |

### 3. 中文深度：[`访谈及其他/`](访谈及其他/)（人物与脉络）

| 文件 | 类型 | 来源 |
|------|------|------|
| [`访谈及其他/AI论文探索之旅-谢清池访谈精读.md`](访谈及其他/AI论文探索之旅-谢清池访谈精读.md) | 访谈整理 + 论文脉络（2004→2026 全时间线，含术语纠错表）| 张小珺商业访谈录·谢清池（2025 国庆录制）|
| [`访谈及其他/张小珺商业访谈录-AI访谈索引.md`](访谈及其他/张小珺商业访谈录-AI访谈索引.md) | **33 集精选索引**：嘉宾/OUTLINE/官方文字版链接/核心要点/work4ai 对接（不下载音频，走官方文字版渠道）| 张小珺商业访谈录全系列 |

详见 [`访谈及其他/README.md`](访谈及其他/README.md)。

### 三块怎么配合

```
系统学（公开课）        ← 想跟一门完整课，从入门到前沿
  │
日常跟（前沿与媒体）     ← 每周/每日 30 分钟到 2 小时的"信息摄入"
  │
中文深度（访谈及其他）   ← 理解人物/历史/产业脉络
  │
讲透系列              ← 把单个概念往底层钻透
```

**铁律**：讲透系列是"主食"，三块参考资料是"配菜/维生素"——配菜吃得再好，没主食也长不出肌肉。

---

## 推荐学习路径

```
讲透激活函数 (地基: 非线性)
    │
讲透基础模型 (造能力: 预训练)
    │
    ├─ 讲透微调 (调能力: 后训练)
    │
    └─ 推理时 (用能力):
          ├─ 讲透RAG (注知识)
          ├─ 讲透Prompt (控输出)
          └─ 讲透Agent (待做: 自主规划)
    │
横向打通 (总纲: 决策框架, 串起以上所有)
```

**新手**：按 激活函数 → 基础模型 → 微调 → RAG → Prompt → 横向打通 顺序。
**有基础**：直接看感兴趣的系列，每系列内独立。

---

## 每个系列的「第一性原理」入口

每个系列都从一个**最该问却最常被跳过**的问题切入：

| 系列 | 第一性问题 | 答案核心 |
|---|---|---|
| 激活函数 | 为什么没有非线性, 再深网络也等价单层线性? | 多层线性=单层线性, 非线性才有表达力 |
| 基础模型 | 预测下一个词这么无聊的目标, 凭什么练出智能? | 预测=压缩=理解 (Kolmogorov) |
| 微调 | LoRA 凭什么用 1% 参数逼近全参数微调? | 微调的ΔW是低秩的 (本征维度) |
| RAG | LLM 这么强, 为什么还需要接外部知识? | 知识是参数化的(幻觉/过时/私有) |
| Prompt | 改几个字 prompt, 凭什么输出天差地别? | Prompt是P(输出\|输入)的条件 |

---

## 统一的方法论（贯穿所有系列）

1. **原理优先于 API**：先讲为什么，再讲怎么调库。
2. **每个结论都有可运行代码佐证**：不凭记忆，数字都是跑出来的。
3. **批判性**：每篇有「局限/争议」，不把漂亮理论当教条。
4. **离散 vs 连续分水岭**：从 MSE/回归跨到 CE/分类必须翻的坎，反复强调。
5. **诚实标注实验边界**：教学版 toy 实验的局限（vs 真实 LLM 规模）都写明。

---

## 环境

- 小模型实验（激活函数/基础模型/微调/Prompt 原理）：纯 CPU + torch/numpy，已全部跑通。
- RAG 实验：TF-IDF + sklearn（无 sentence-transformers/GPU），跑通检索原理。
- 真实大模型实验：需 GPU + 模型权重，本机暂无，各系列给出可移植代码骨架。

---

## 怎么跑

```bash
cd /data/usershare/ai/work4ai
for d in 讲透激活函数 讲透基础模型 讲透微调 讲透RAG 讲透Prompt; do
  echo "##### $d #####"
  ls $d/experiments/*.py 2>/dev/null | head -3
done
# 任选一个实验跑:
python3 -u 讲透基础模型/experiments/00_why_ntp.py
```

---

## 下一步（可选）

- **补全 6 个早期待补全系列**：讲透Agent / 讲透优化器 / 讲透损失函数 / 讲透KV Cache / 讲透RL / 讲透分布式AI系统（都已有 00 开篇，接着写即可）
- **续写本轮 3 个新系列**：讲透可解释性（→ mechanistic + SAE）/ 讲透数据（→ Model Collapse + 合成数据工程）/ 讲透科学的现代性（4 篇已完整，可深挖某个视角）
- **任一系列深挖特定篇**（如基础模型实战、微调在 GPU 上真跑）
- **走 `讲透公开课/04` 的个性化路径**：做"五、自我诊断"，根据现状挑下一段路

> 🔗 **新加的 3 个系列是 `讲透AI应用全景/07-AI for AI` 的三向深挖**：
> - 数据 → 07 第③层（AI 训练 AI）
> - 可解释性 → 07 第⑥层（AI 理解 AI）
> - 科学的现代性 → 07 元反思层（"AI 发现算理解吗"）
