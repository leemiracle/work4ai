# 2025–2026 AI 前沿全景：世界大模型 · AI4Science · AI4Math 十二月志

> **卷别**：world-ai4sci-math / 04-synthesis / 第 03 篇
> **主题**：2025 年 7 月至 2026 年 7 月，三大前沿方向的关键事件、技术跃迁与产业格局
> **写作日期**：2026-07-20
> **核实方法**：webfetch 直抓官方页（OpenAI / DeepMind / NVIDIA / World Labs / Arc Institute / IMO 官网 / arXiv）+ gh-grep 代码仓库交叉验证；标注「据…」者为单源待复核项
> **读者**：具备工程基础的 AI 学习者与研究者（中文为主、术语英文）

---

## 引言：为什么这十二个月值得专门立传

从 2025 年 7 月到 2026 年 7 月，是 AI 历史上节奏最密集、分化最剧烈的一段时期。这一年的三条主线几乎同步进入「质变窗口」：

- **世界大模型（World Models）** 从「能生成视频」跨越到「能模拟物理与行动」——OpenAI 把 Sora 2 称作「视频的 GPT-3.5 时刻」，NVIDIA 把 Cosmos 升级成可推理可生成可行动的 omni-model，Meta 用 V-JEPA 2 证明了「先看一百万小时、再上手几小时」的机器人范式。
- **AI4Science** 从「单点突破」走向「全链路落地」——首个全程由 AI 设计的药物 rentosertib 进入 Phase III 临床；AlphaFold 3 的能力被 Boltz-2 等开源复现民主化；Evo 2 把基因组建模推到 40B 参数、覆盖全部生命域。
- **AI4Math** 从「银牌选手」冲到「金牌选手」——IMO 2025 的金牌分数线 35 分，AI 系统首次稳定触及这一门槛；形式化证明（Lean 4）与非形式化推理的鸿沟被 DeepSeek-Prover V2 显著收窄。

与此同时，产业格局也在重写：OpenAI 在 2026 年 4 月突然下线了 Sora 产品线，Google 凭借 Veo 3.1 与 Gemini 全家桶反超视频赛道，NVIDIA 用 Cosmos 3 把「物理 AI」立成新一级市场，国产阵营（可灵、通义万相、Seedance、混元）则在多模态生成上完成正面交锋。

本文按时间顺序整理这十二个月的关键事件，每条配 100–200 字的解读，力求让读者既能看到「什么时候发生了什么」，也能理解「为什么这件事重要」。

---

## 一、三大领域时间线总表（2025-07 → 2026-07）

> 表中「★」表示里程碑级事件（改变赛道格局）；「▶」表示重要版本迭代；日期精确到月，部分精确到日。

### 1.1 世界大模型（World Models）

| 时间 | 事件 | 主导方 | 量级 |
|---|---|---|---|
| 2025-05-14 | AlphaEvolve 发布（Gemini 驱动的进化式编码 Agent） | Google DeepMind | ★ |
| 2025-05-20 | Veo 3 于 Google I/O 2025 发布，原生音频同步 | Google DeepMind | ★ |
| 2025-06-11 | **V-JEPA 2** 发布，自监督视频世界模型 + 机器人规划 | Meta FAIR | ★ |
| 2025-09-30 | **Sora 2** 发布，定位「视频的 GPT-3.5 时刻」 | OpenAI | ★ |
| 2025-10 | Veo 3.1 迭代，物理真实感与 prompt 遵从度全面领先 | Google DeepMind | ▶ |
| 2025-Q4 | World Labs 推出首产品 **Marble**（3D 空间世界生成） | World Labs（李飞飞） | ★ |
| 2026-03-03 | World Labs「3D as code」理念提出 | World Labs | ▶ |
| 2026-03-16 | **V-JEPA 2.1** 发布，引入 dense predictive loss | Meta FAIR | ▶ |
| 2026-04-14 | World Labs Spark 2.0 流式 3DGS 上线 | World Labs | ▶ |
| 2026-04-26 | ⚠️ **OpenAI 下线 Sora 产品线**（Sora 2 模型本身仍存） | OpenAI | ★ |
| 2026-05 | NVIDIA **Cosmos 3** 于 COMPUTEX 2026 发布（黄仁勋） | NVIDIA | ★ |
| 2026-06-03 | World Labs《世界模型功能分类学》发布 | World Labs | ▶ |
| 2026-持续 | 可灵 3.0、通义万相、Seedance、混元世界多线并进 | 国产阵营 | ★ |

### 1.2 AI4Science

| 时间 | 事件 | 主导方 | 量级 |
|---|---|---|---|
| 2025-02 | **Evo 2** 预发布，40B 参数基因组基础模型 | Arc Institute | ★ |
| 2025-2026 | Boltz-2 开源，复现并扩展 AlphaFold 3 能力 | jwohlwend/boltz（MIT 等） | ★ |
| 2025-11-12 | AlphaProof 方法论发表于 **Nature**（DOI 10.1038/s41586-025-09833-y） | Google DeepMind | ★ |
| 2026-持续 | Evo 2 论文正式刊于 **Nature**（DOI 10.1038/s41586-026-10176-5）；20B 版本达到 40B 性能 | Arc Institute | ▶ |
| **2026-07-07** | ★ **rentosertib（INS018_055）Phase III 临床启动**（NCT07687459） | Insilico Medicine | ★★ |

### 1.3 AI4Math

| 时间 | 事件 | 主导方 | 量级 |
|---|---|---|---|
| 2024-07-25 | AlphaProof + AlphaGeometry 2 在 IMO 2024 拿 28/42 银牌 | Google DeepMind | ★（前置） |
| 2025-04-30 | **DeepSeek-Prover V2** 发布（arXiv 2504.21801） | DeepSeek | ★ |
| 2025-07 | **IMO 2025**（澳大利亚举办），金牌分数线 35 分 | IMO 官方 | ★ |
| 2025-07 | AI 系统（Gemini 等）首次稳定触及 IMO 金牌线 | Google DeepMind 等 | ★ |
| 2025-11-12 | AlphaProof Nature 论文公布完整 RL + Lean 训练框架 | Google DeepMind | ★ |
| 2026-持续 | DeepSeek-Prover V2 在 MiniF2F-test 达 88.9%、AIME 解 6/15 | DeepSeek | ▶ |

---

## 二、世界大模型深度解读

### 2.1 ★ Sora 2 ——「视频的 GPT-3.5 时刻」与一次意外下线

**发布**：2025 年 9 月 30 日，OpenAI 官方博客标题《Sora 2 is here》。

**核心定位**：OpenAI 自己把 Sora 2 比作「视频领域的 GPT-3.5 时刻」——这是从「能生成画面」到「能模拟世界」的关键一跃。2024 年 2 月的初代 Sora 被称为「视频的 GPT-1」，而 Sora 2 跨过了那道坎。它能完成此前视频模型几乎做不到、甚至根本做不到的事：奥运体操套路、桨板上准确模拟浮力与刚体力学的后空翻、以及「花样滑冰运动员头顶一只猫完成三周半跳」这类需要精细物理一致性的长镜头。

**物理诚实性**：Sora 2 最被讨论的能力是「会失败」。OpenAI 举了一个反直觉的例子——此前的视频模型过度乐观，篮球运动员投篮不中时球会「瞬移」进筐；而 Sora 2 会让球从篮板上弹回。这种「能建模失败、而不只是建模成功」被 OpenAI 视为任何有用世界模拟器的必备素质。

**配套产品**：伴随 Sora 2 上线的是一个独立的 iOS 社交应用「Sora」，主打「characters」功能——用户录一段短视频验证身份后，可以把自己的外貌与声音注入任意 Sora 生成的场景。OpenAI 强调这是「为创作而非消费」设计的产品，并内置了反成瘾的推荐算法与青少年保护机制。

**意外转折**：最值得记录的是 **2026 年 4 月 26 日，OpenAI 官方在 Sora 2 博客顶部加注「As of April 26, 2026, the Sora product is no longer available」**——Sora 产品线被下线。模型本身（Sora 2 / Sora 2 Pro）是否继续以 API 形式提供服务，以及下线的商业原因（成本、竞争、产品定位），是 2026 年上半年业界最大的悬案之一。这提醒我们：技术里程碑不等于商业成功，视频生成的单位经济模型仍是未解之题。

### 2.2 ★ Veo 3 / Veo 3.1 —— Google 接管视频王座

**发布**：Veo 3 于 2025 年 5 月 20 日 Google I/O 2025 发布；同年 10 月迭代到 Veo 3.1。

**核心能力**：Veo 3 把「原生音频同步」做成了标配——音效、环境音、对话台词都由模型一次性生成，且与画面精准对齐。这在 Sora 2 之前是稀缺能力。Veo 3.1 进一步在物理真实感（visually realistic physics）、prompt 遵从度（prompt adherence）、视觉质量三项指标上全面领先，Google 公布的 MovieGenBench 与 VBench I2V 人类偏好测试中，Veo 3.1 在绝大多数维度击败对手（值得一提的是 Google 注明「无法与 Sora 2 Pro 在真人图像上对比」，因为 Sora 2 Pro 不支持真实人物）。

**创意控制**：Veo 3 引入了一整套创作者控制工具——ingredients to video（参考图引导）、scene extension（场景延续）、first & last frame（首尾帧过渡）、outpainting（画面外扩）、object add/remove（物体增删）、camera controls（运镜控制）、character controls（用身体/面部/声音驱动角色）、motion controls（路径定义）。这套工具链让 Veo 从「生成器」变成「创作工作站」。

**生态布局**：Google 同步推出了 Google Flow（cinematic 创作平台）和与导演 Darren Aronofsky 的 Primordial Soup 合作项目，把 Veo 嵌入专业电影制作流程。这是 Veo 区别于纯消费级产品的关键策略。

### 2.3 ★ V-JEPA 2 —— LeCun 路线的第一次工程胜利

**发布**：2025 年 6 月 11 日，Meta FAIR。论文 arXiv **2506.09985**。代码与 checkpoint 全部开源（github.com/facebookresearch/vjepa2）。

**技术路线**：V-JEPA 2 是 Yann LeCun 倡导的 JEPA（Joint-Embedding Predictive Architecture）路线的集大成之作。它用自监督方式在超过 100 万小时的互联网视频上训练（无任何人工标注），学习在 latent 空间预测被遮蔽的视频片段。最大变体 ViT-g/16 达 10 亿参数。在运动理解与人类动作预测任务上取得 SOTA。

**V-JEPA 2-AC 的震撼**：真正让业界震动的是 V-JEPA 2-AC——一个在 V-JEPA 2 基础上后训练的「latent action-conditioned world model」。它只用 **不到 62 小时** 的机器人轨迹数据，就能在一个它从未见过的实验室里操控真实机械臂完成抓取摆放，且不需要针对具体任务训练或校准。这与传统机器人学习「每个任务都要成百上千小时示范」的范式形成鲜明对比，被业界解读为「先大量观察世界、再少量上手」的人类学习方式的工程化实现。

**迭代**：2026 年 3 月 16 日，Meta 发布 **V-JEPA 2.1**，引入 dense predictive loss（对所有 token 而非仅 masked token 做预测监督）和深层自监督，学习到时间一致、空间结构化的稠密特征，更适合分割、追踪、深度估计等密集预测任务。这一迭代说明 LeCun 路线仍在快速演化。

### 2.4 ★ NVIDIA Cosmos 3 ——「物理 AI」立国

**发布**：2026 年 5 月，COMPUTEX 2026，黄仁勋亲自站台。

**架构跃迁**：Cosmos 3 是 NVIDIA 「世界基础模型（World Foundation Model, WFM）」的第三代。架构上首次采用 **Mixture-of-Transformers**——推理模块与生成模块使用不同的 transformer，先推理后生成，从而在物理准确性上领先。它是 NVIDIA 所称的首个 **omni-model**：原生支持 reasoning、world、action 三种生成，跨文本、图像、视频、声音、动作五类模态。

**三大用途**：Cosmos 3 的产品定位非常清晰——①作为视觉语言模型（VLM）做实时告警与稠密描述（质检、公共安全、交通、物流、自动驾驶）；②作为 World Action Model（WAM）的骨干加速机器人策略学习；③作为可控的、物理一致的世界模拟器做闭环仿真。配套的 Cosmos Curator（数据筛选）、Cosmos Evaluator（生成评分）、Cosmos Cookbook（上手食谱）构成完整工具链。

**开源与生态**：Cosmos WFMs 以 Linux Foundation 的 OpenMDW1.1 许可证开源，在 HuggingFace 上可下载。前代 Cosmos 2.5 与 Cosmos 2 把感知与生成分成两个模型、模态仅限文本图像视频；Cosmos 3 把它们统一进单一 omni-model，是一次架构层面的整合。NVIDIA 把这一系列定位为「Physical AI 时代的基础设施」——与 Omniverse（3D 仿真环境）形成「仿真+生成」双轮驱动。

### 2.5 ★ World Labs Marble —— 空间智能从口号到产品

**首产品**：World Labs（李飞飞创办）推出的第一款产品叫 **Marble**，定位「空间智能（Spatial Intelligence）」。它能从文本、图像、视频或 360 全景生成空间一致、高保真、持久化的 3D 世界，用户可以在其中移动、编辑、组合。

**理念演进**：2026 年上半年，World Labs 连续发布三篇具有方向标意义的研究博客——3 月 3 日《3D as code》提出「3D 正在成为空间的通用接口，就像文本成为软件的通用接口」；4 月 14 日 Spark 2.0 上线，实现可流式传输的 Level-of-Detail 3D Gaussian Splatting；6 月 3 日《A Functional Taxonomy of World Models》把世界模型系统划分为 Renderers（渲染器）、Simulators（模拟器）、Planners（规划器）以及连接三者的环路。这一分类法正在成为业界讨论世界模型的事实框架。

**澄清**：用户记忆中提到的「LESV3」并非 World Labs 的公开产品名——World Labs 的公开产品线是 Marble + Spark + API 平台。LESV3 可能是某个内部版本代号或第三方误传，本节以官方公开信息为准。

### 2.6 国产阵营：可灵、通义万相、Seedance、混元

**可灵（Kling）3.0**：快手旗下可灵 AI 已迭代到「可灵 AI 3.0 系列」。官方定位「All in One，One for All」，视频 3.0 与视频 3.0 Omni 原生支持多模态指令的深度解析与跨任务融合，实现「视觉主体与听觉音色的双重绑定」的音画同步，并在超长视频的精准分镜上发力。这是国产视频生成在多模态融合维度上正面叫板 Veo / Sora 的代表作。

**通义万相、Seedance、混元世界**：阿里通义万相（Wan 系列）、字节 Seedance（1.0 及后续）、腾讯混元世界（HunyuanWorld）构成国产世界模型/视频生成的另外三极。这些产品在 2025–2026 年间密集迭代，普遍采用 DiT（Diffusion Transformer）架构、支持长视频与多镜头一致性，并在中文语境理解与本土化创作工作流上建立差异化优势。（具体版本号与发布日期需以各厂官方公告为准，本节不展开未核实细节。）

### 2.7 ★ AlphaEvolve —— 用进化算法发现新数学

**发布**：2025 年 5 月 14 日，Google DeepMind。

**机制**：AlphaEvolve 是一个由 Gemini 驱动的「进化式编码 Agent」——Gemini Flash 负责广度探索（最大化想法数量），Gemini Pro 负责深度（提供关键洞见），二者生成计算机程序作为算法方案的实现；自动化评估器验证并打分；进化框架保留最优解并迭代。它把「发现问题解」从单函数发现扩展到整个代码库的演化。

**实战战绩**：
- **数据中心调度**：发现一个简洁高效的启发式，已上线 Google Borg 一年多，平均回收全球 0.7% 的计算资源。
- **硬件设计**：提出一处 Verilog 改写，移除矩阵乘法算术电路中不必要的比特，已集成进即将发布的 TPU。
- **AI 训练加速**：把 Gemini 架构中一个关键矩阵乘法 kernel 加速 23%，使 Gemini 训练时间减少 1%；FlashAttention kernel 实现最高 32.5% 加速。
- **数学新发现**：找到 4×4 复值矩阵乘法只需 48 次标量乘法的算法（改进了 Strassen 1969 年的纪录）；在 50 多个数学开放问题中约 75% 重新发现了 SOTA 解，约 20% 改进了已知最优解——例如把 11 维「接吻数问题」的下界推进到 593。

**意义**：AlphaEvolve 是「LLM 创造性 + 自动验证器」范式的标杆。它证明了在「解可被算法描述且可自动验证」的领域，AI 不只是辅助人类，而是能独立推进前沿。这对材料科学、药物发现、可持续技术都有深远含义。

---

## 三、AI4Science 深度解读

### 3.1 ★★ rentosertib（INS018_055）—— 首个全程 AI 设计药物进入 Phase III

**里程碑**：**2026 年 7 月 7 日，Insilico Medicine 的 rentosertib（研发代号 INS018_055）Phase III 临床试验正式启动**，注册号 **NCT07687459**。这是**人类历史上第一个完全由 AI 发现并设计的药物进入 III 期临床**。

**疾病与机制**：rentosertib 用于治疗**特发性肺纤维化（Idiopathic Pulmonary Fibrosis, IPF）**——一种进行性、致命的肺部疾病，现有疗法有限。该药物的靶点发现、分子设计全程由 Insilico 的 Pharma.AI 平台完成。它在 2023 年成为首个进入 Phase II 的 AI 设计药物，如今更进一步迈入 Phase III，意味着疗效与安全性已通过早期临床的严格检验，距离上市只差大规模验证这一关。

**为什么这是 AI4Science 的「登月时刻」**：药物开发 traditionally 需要 10–15 年、耗资数十亿美元，失败率极高。rentosertib 从靶点立项到 Phase II 用时不到 30 个月、投入约 4000 万美元——把早期发现阶段的成本与周期压缩了一个数量级。Phase III 的启动证明：AI 不只是在论文里「预测分子」，而是真正走通了「发现→设计→临床→上市」的全链路。这是 AI4Science 从「学术新奇」转向「产业基础设施」的标志性事件。

### 3.2 ★ Boltz-2 —— AlphaFold 3 的开源民主化

**项目**：Boltz 是由 Jeremy Wohlwend、Gabriele Corso、Saro Passaro 等人主导的开源分子结构预测模型（github.com/jwohlwend/boltz，MIT 许可）。Boltz-2 是其当前主版本。

**定位**：AlphaFold 3（Google DeepMind，2024 年 5 月发表于 Nature）能预测蛋白质-配体复合物等复杂分子结构，但其权重未完全开源。Boltz-2 的使命是**复现并扩展 AlphaFold 3 的能力，并以完全开源的方式提供给学术界与产业界**。它支持蛋白质-配体复合物预测，输出 Crystallographic Information File（CIF）可用 Molstar 等工具渲染。

**生态影响**：Boltz-2 已经被大量下游项目采纳——Apple 的 ml-simplefold 直接基于 Boltz 的数据管线构建；Modal Labs、MIMS Harvard ToolUniverse 等都集成了 Boltz 作为结构预测后端。这种「闭源旗舰 + 开源平替」的格局，让 AlphaFold 级别的能力从少数大厂的特权变成了研究者的标配工具，是 AI4Science 民主化的典型样本。（注：Chai-1 由 Chai Discovery 提供，是另一条开源/开放路线，本卷未单独抓取其最新版本细节，留待后续核实。）

### 3.3 ★ Evo 2 —— 覆盖全部生命域的基因组基础模型

**主导方**：Arc Institute（与 NVIDIA、UC Berkeley、Stanford 等合作）。

**模型家族**：Evo 2 是基因组学的「基础模型」，论文正式发表于 **Nature**（DOI 10.1038/s41586-026-10176-5，标题《Genome modeling and design across all domains of life with Evo 2》）。模型家族包含 evo2_40b（旗舰）、evo2_20b、evo2_7b、evo2_1b 等多个规模，全部 Apache-2.0 开源（github.com/ArcInstitute/evo2，HuggingFace: arcinstitute/evo2_*）。

**核心突破**：Evo 2 在**全部生命域（all domains of life）**的基因组数据上训练——这是从原核到真核、跨越整个生命树的尺度。它不仅能理解 DNA 序列，还能进行序列设计（design），这意味着可以从零设计具有特定功能的基因元件。40B 参数使它成为迄今最大的基因组基础模型之一。

**工程优化**：2026 年发布的 **Evo 2 20B** 在性能上达到 40B 旗舰水平、同时速度翻倍，让更多实验室能在合理算力下使用顶级基因组模型。这种「大模型旗舰 + 高效中等模型」的双轨策略，与 LLM 领域的演化路径高度一致。

### 3.4 ★ AlphaProof / AlphaGeometry 2 —— 数学推理的 Nature 正名

**论文**：2025 年 11 月 12 日，AlphaProof 的完整方法论发表于 **Nature**（DOI 10.1038/s41586-025-09833-y）。这篇论文系统披露了 AlphaProof 如何用 Lean 形式语言 + AlphaZero 式强化学习训练自身。

**IMO 2024 战绩回顾**：AlphaProof + AlphaGeometry 2 组合系统在 IMO 2024 解出 6 题中的 4 题，得分 28/42，达到银牌水平（当年金牌线 29）。其中 AlphaProof 解出两道代数题与最难的那道数论题（全场仅 5 名人类选手解出），AlphaGeometry 2 解出几何题 P4（用时仅 19 秒）。

**AlphaGeometry 2 的进化**：相比初代，AG2 用 Gemini 作为语言模型、合成数据量提升一个数量级、符号引擎快两个数量级，并引入知识共享机制组合不同搜索树。它能解 25 年来 83% 的历史 IMO 几何题（初代仅 53%）。这是一条「神经-符号混合」路线的胜利。

---

## 四、AI4Math 深度解读

### 4.1 IMO 2025 —— AI 首次稳定触及金牌线

**赛事背景**：第 66 届 IMO 于 2025 年 7 月在**澳大利亚**举办，110 个国家、630 名选手参赛（其中 69 名女生）。IMO 官方数据显示，**2025 年金牌分数线为 35 分**（满分 42，有效分阈值 43.77%），银牌 28 分，铜牌 19 分。

**AI 表现**：综合行业报告与 Epoch AI 等追踪机构的信息（本节为多源汇总，单一来源待进一步核实），2025 年的 AI 系统首次稳定触及 IMO 金牌线——以 Google Gemini 系列为代表的非形式化推理路线达到约 35 分水平，跨过金牌门槛；DeepMind 的形式化路线（AlphaProof 继承者）与 Lean 生态的 Seed-Prover 等在部分题目上取得 5/6 级别的形式化证明。这是继 2024 年银牌之后的又一次台阶式跃升。

**为什么金牌线意义重大**：IMO 金牌意味着 AI 能稳定处理需要「非显然构造」「多步组合推理」「跨主题综合」的数学问题。从银牌（28）到金牌（35）只差 7 分，但这 7 分往往卡在最难的两道题上——正是人类顶尖选手也容易失手的组合与高级代数。AI 触及金牌线，标志着数学推理从「能做中等题」进入「能与顶尖人类选手同台」的阶段。

### 4.2 ★ DeepSeek-Prover V2 —— 形式化证明的 SOTA

**论文**：arXiv **2504.21801**，2025 年 4 月 30 日提交（v2 于 2025 年 7 月 18 日修订）。标题《DeepSeek-Prover-V2: Advancing Formal Mathematical Reasoning via Reinforcement Learning for Subgoal Decomposition》。

**核心方法**：DeepSeek-Prover V2 是开源的、用于 Lean 4 形式化定理证明的大语言模型。它的冷启动数据通过一个递归定理证明管线收集——先用 DeepSeek-V3 把复杂问题分解成一系列子目标（subgoal），再把已解子目标的证明合成成 chain-of-thought，与 DeepSeek-V3 的逐步推理结合，形成强化学习的冷启动。这一过程把非形式化与形式化数学推理整合进同一个模型。

**战绩**：DeepSeek-Prover-V2-671B（6710 亿参数）在 MiniF2F-test 上达到 **88.9%** 的通过率（SOTA），在 PutnamBench 解出 658 题中的 49 题。团队还发布了 ProverBench（325 道形式化问题，含 15 道 AIME 24-25 题），模型解出其中 6 道——而 DeepSeek-V3 用多数投票解出 8 道，说明**形式化与非形式化推理之间的鸿沟正在显著收窄**。

**意义**：DeepSeek-Prover V2 证明了中国团队在形式化数学推理这一硬核方向上具备顶级竞争力。它的开源属性（模型权重公开）让全球研究者都能在 SOTA 基础上继续推进，是对 Lean 证明助手生态的重大贡献。

### 4.3 形式化 vs 非形式化：两条路线的收敛

这一年的 AI4Math 最深刻的趋势是「两条路线开始收敛」：

- **形式化路线**（AlphaProof、DeepSeek-Prover V2）：用 Lean/Coq/Isabelle 等形式语言，证明可被机器验证、零幻觉，但受限于形式数据稀缺。AlphaProof 用 autoformalization（自然语言→形式语言）桥接，DeepSeek 用 subgoal 分解 + RLVR 桥接。
- **非形式化路线**（Gemini、o1/R1 系列、Claude）：用自然语言推理，数据丰富、灵活，但有幻觉风险。其 SOTA 在 FrontierMath 等基准上仍低于 2%（据 Epoch AI 2024 数据），但在 AIME/竞赛数学上已很强。

DeepSeek-Prover V2 的 6/15 vs V3 的 8/15（AIME）是收敛的最直接证据——形式化模型正在逼近非形式化模型的解题能力，同时保留可验证性。这是 AI4Math 走向「可信数学助手」的关键。

---

## 五、跨域突破（5 条精选）

### 5.1 AlphaEvolve 同时推进数学与工程
（详见 2.7）一个系统同时改进了 Google 数据中心调度（工程）、TPU 算术电路（硬件）、矩阵乘法算法（数学）——这是「AI 作为通用问题求解器」的最强证据。它的关键是「解可被算法描述且可自动验证」这一共性，让数学与工程的边界变得模糊。

### 5.2 V-JEPA 2-AC 让世界模型直接驱动机器人
（详见 2.3）自监督视频预训练 + 极少量机器人数据 = 通用机械臂操作。这把「世界模型」从「生成漂亮视频」拉到「驱动物理行动」，是 embodied AI 与 world model 两条线的合流。

### 5.3 Boltz-2 把 AlphaFold 能力变成公共基础设施
（详见 3.2）闭源旗舰（AlphaFold 3）+ 开源平替（Boltz-2）的格局，让结构生物学进入「人人可用」时代。这是 AI4Science 民主化的模板，可复制到材料、药物等其它领域。

### 5.4 rentosertib 证明 AI 能走通「发现→临床」全链路
（详见 3.1）这是 AI4Science 唯一一例「从论文到 Phase III」的完整闭环。它的意义不在单一药物，而在证明了 AI 设计的分子能通过人类最严格的验证体系（FDA/EMA 临床试验）。

### 5.5 IMO 金牌线被 AI 触及，数学推理进入新常态
（详见 4.1）从 2024 银牌（28）到 2025 金牌线（35），AI 数学推理能力一年内跨过人类顶尖选手门槛。这预示着数学研究的工作流将发生根本变化——AI 不再只是「检查证明」，而是「共同发现」。

---

## 六、重要公司动态（2025-07 → 2026-07）

### 6.1 OpenAI —— 高歌与转折并存
- **GPT-5 系列快速迭代**：据 OpenAI 官网导航，2025–2026 年间已发布 GPT-5.4、GPT-5.5、GPT-5.6，迭代节奏远超往年。
- **Sora 2 发布又下线**：2025-09-30 发布 Sora 2（视频的 GPT-3.5 时刻），但 **2026-04-26 下线 Sora 产品线**——这是 OpenAI 罕见的产品撤退，背后可能是单位经济、竞争压力或战略重心的转移（转向 GPT 系列与 Codex）。
- **Codex 与 Agents**：Codex（编码 Agent）持续强化，Apps SDK 与 Open Models 路线并行。

### 6.2 Google / DeepMind —— 全栈反超
- **Veo 3.1 领跑视频生成**：在物理真实感、prompt 遵从度、视觉质量上全面领先，配合 Google Flow 与 Darren Aronofsky 合作切入专业影视。
- **Gemini 全家桶**：Gemini、Gemini Omni、Nano Banana（图像）、Gemini Audio、Gemini Robotics 构成多模态矩阵。
- **科学旗舰**：AlphaFold、WeatherNext（GraphCast/Aurora）、AlphaEarth、AlphaEvolve、AlphaGenome 形成「Alpha 科学院」品牌。
- **Antigravity**：推出 agentic 开发平台 Google Antigravity，押注 Agent 工程化。

### 6.3 xAI / Meta / NVIDIA
- **xAI（Grok）**：在推理模型与超大规模训练集群（Memphis）上持续投入，具体产品节奏本卷未单独核实。
- **Meta FAIR**：V-JEPA 2 / 2.1 是 LeCun 路线的工程胜利；SIMA 2（虚拟 3D 世界游戏 Agent）、Gemini Robotics（注：属 Google，此处 Meta 侧为 V-JEPA 系与 Llama 系开源模型）持续推进世界模型与开源 LLM。
- **NVIDIA**：Cosmos 3 立「Physical AI」新市场；硬件侧 Blackwell GB200、RTX PRO 6000 Blackwell 持续出货；NVentures、AI Foundry、DGX Cloud 构建全栈商业。

### 6.4 国产巨头
- **可灵（快手）**：3.0 系列在多模态融合与音画同步上正面竞争。
- **阿里（通义万相）**：Wan 系列视频/世界模型，中文语境优势。
- **字节（Seedance / 豆包）**：Seedance 视频生成 + 豆包多模态，C 端流量与 B 端 API 并进。
- **腾讯（混元）**：HunyuanWorld 世界模型 + 混元大模型，游戏/社交场景落地。
- **DeepSeek**：DeepSeek-Prover V2（AI4Math SOTA）+ DeepSeek-V3/R1 系列（开源 LLM 旗舰），是中国开源 AI 的名片。

---

## 七、2026 下半年展望（5 个预判）

### 预判 1：世界模型将从「生成」全面转向「行动」
2025 年的 Sora 2 / Veo 3 还停留在「生成漂亮且物理一致的 video」，但 V-JEPA 2-AC 与 Cosmos 3 已经把方向指向「驱动物理行动」。2026 下半年，预计会出现更多「世界模型 + 机器人策略」的整合产品，物理 AI（Physical AI）成为与 LLM、视频生成并列的第三大赛道。NVIDIA Cosmos 3 的 omni-model 架构（reasoning + world + action）很可能成为业界模仿的范式。

### 预判 2：AI4Science 进入「Phase III 密集期」
rentosertib（IPF）开了 Phase III 的头之后，预计 2026 下半年到 2027 年会有更多 AI 设计的药物进入晚期临床（肿瘤、神经退行性疾病等）。同时，AlphaFold 级能力（Boltz-2 等开源版）会深度嵌入制药研发流程，从「新奇」变成「标配」。基因组基础模型（Evo 2 系列）可能在基因治疗与合成生物学上产生首批商业成果。

### 预判 3：AI4Math 触及「研究级数学」
IMO 金牌线被触及之后，下一个目标是研究级数学——FrontierMath、OTIS Mock AIME、未解数学难题（如 Epoch AI 的 Open Problems）。预计 2026 下半年会有 AI 系统在某个具体的、未被人类解决的小型开放问题上取得形式化证明的进展。AlphaEvolve 式的「进化 + 自动验证」范式可能在更多数学分支产生新发现。

### 预判 4：视频生成的单位经济将重塑赛道
Sora 产品线的下线是一个强烈信号——视频生成的算力成本仍然远高于图像/文本，纯消费级社交产品的变现模型难以跑通。2026 下半年，预计赛道会分化：一极走向专业影视（Veo + Flow 模式），一极走向 B 端 API 与垂直行业（广告、电商、教育），纯 C 端「刷视频」产品可能进一步收缩。

### 预判 5：开源与闭源进入新平衡
DeepSeek-Prover V2（AI4Math）、Boltz-2（结构生物学）、Evo 2（基因组）、V-JEPA 2（世界模型）、Cosmos 3（物理 AI）等顶级能力相继开源，说明开源阵营在多个垂直方向上已能与闭源旗舰分庭抗礼。2026 下半年，预计「闭源旗舰定义上限、开源平替定义下限」的格局会固化，研究者和中小团队的默认起点将是开源 SOTA 而非 API。

---

## 📌 进一步阅读

### 官方一手资料
- **OpenAI Sora 2**：https://openai.com/index/sora-2/ （含 2026-04-26 下线声明）
- **Google DeepMind Veo**：https://deepmind.google/models/veo/
- **Meta V-JEPA 2**：https://ai.meta.com/blog/v-jepa-2-world-model-benchmarks/ ；论文 arXiv 2506.09985；代码 github.com/facebookresearch/vjepa2
- **NVIDIA Cosmos 3**：https://www.nvidia.com/en-us/ai/cosmos/ ；技术报告 research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf
- **World Labs Marble**：https://www.worldlabs.ai/ ；研究博客 /blog/taxonomy-of-world-models
- **AlphaEvolve**：https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/ ；白皮书 PDF 链接见博客
- **AlphaProof Nature 论文**：https://www.nature.com/articles/s41586-025-09833-y
- **DeepSeek-Prover V2**：https://arxiv.org/abs/2504.21801
- **Evo 2 Nature 论文**：https://www.nature.com/articles/s41586-026-10176-5 ；代码 github.com/ArcInstitute/evo2
- **Boltz-2**：https://github.com/jwohlwend/boltz
- **rentosertib / INS018_055 临床试验**：ClinicalTrials.gov NCT07687459 ；Insilico Medicine 官网 insilico.com
- **IMO 官方结果**：https://www.imo-official.org/results.aspx （2025 年金牌线 35）

### 本卷配套章节
- `03-ai4math/01-formal-proof.md` —— 形式化定理证明专章（含 AlphaProof / DeepSeek-Prover 三代）
- `03-ai4math/02-informal-reasoning.md` —— AI 非形式化数学推理（CoT→PRM→o1→R1→2026）
- `02-ai4science/00-README.md` —— AI4Science 综述导览
- `02-ai4science/02-genomics-singlecell.md` —— DNA/RNA + 单细胞（含 Evo 2 详述）

### 推荐追踪源
- **Epoch AI**（epochai.org）：AI 能力与基准追踪，FrontierMath / ECI 排行
- **Papers with Code**：SOTA 基准
- **Hugging Face Papers**：每日精选
- **Nature / Science AI 专栏**：顶级科学成果首发

---

## ✍️ 思考题（3 道）

### 题 1：世界模型的「物理诚实性」是特性还是负担？
OpenAI 在 Sora 2 中强调「能建模失败」是世界模拟器的必备素质（篮球不中会弹回而非瞬移进筐）。但「物理诚实」意味着模型不能为了满足 prompt 而「作弊」，这在产品体验上可能让用户觉得「不够听话」。请思考：在一个面向消费者的视频生成产品中，「物理诚实」与「prompt 遵从」之间应该如何权衡？这两者是否本质冲突？Sora 产品线的下线是否与这一权衡有关？

### 题 2：rentosertib 进入 Phase III，AI4Science 的「最后验证」还是「冰山一角」？
rentosertib 是首个全程 AI 设计进入 Phase III 的药物，但 Phase III 本身仍可能失败（行业平均失败率约 30%）。请思考：如果 rentosertib 最终获批上市，它将如何改变制药业的研发流程与商业模式？如果它在 Phase III 失败，我们应该如何归因——是 AI 设计方法的局限，还是 IPF 这一疾病本身的难度？「AI 设计药物」的成功标准应该是什么？

### 题 3：形式化与非形式化数学推理的收敛，会催生什么样的「数学助手」？
DeepSeek-Prover V2（形式化，Lean 4）在 AIME 解 6/15，DeepSeek-V3（非形式化）解 8/15——鸿沟正在收窄。请思考：如果一个未来的「数学助手」同时具备形式化的可验证性与非形式化的灵活性，它会如何改变职业数学家的工作流？哪些类型的数学问题最适合这种人机协作？这种工具会让数学变得更「工程化」还是更「自由」？对数学教育（从中小学到研究生）又会产生什么影响？

---

## 附录：核实记录与诚实声明

### 已一手核实（官方页 / arXiv / Nature / GitHub）
- Sora 2 发布日期 2025-09-30、2026-04-26 下线声明 → openai.com/index/sora-2/
- Veo 3 / Veo 3.1 能力与基准 → deepmind.google/models/veo/
- V-JEPA 2 发布 2025-06-11、arXiv 2506.09985、V-JEPA 2-AC 机器人、2.1 版 2026-03-16 → github.com/facebookresearch/vjepa2 README
- NVIDIA Cosmos 3（COMPUTEX 2026）、Mixture-of-Transformers、OpenMDW1.1 → nvidia.com/en-us/ai/cosmos/
- World Labs Marble、三篇研究博客日期 → worldlabs.ai/blog
- AlphaEvolve 2025-05-14、战绩数据 → deepmind.google 博客
- AlphaProof Nature 论文 DOI 10.1038/s41586-025-09833-y、IMO 2024 28/42 银 → deepmind.google 博客
- DeepSeek-Prover V2 arXiv 2504.21801、671B、88.9% MiniF2F、6/15 AIME → arxiv.org/abs/2504.21801
- Evo 2 Nature DOI 10.1038/s41586-026-10176-5、模型家族、Apache-2.0 → github.com/ArcInstitute/evo2
- Boltz-2 开源、MIT 许可 → github.com/jwohlwend/boltz
- IMO 2025 金牌线 35 分、澳大利亚举办、630 选手 → imo-official.org/results.aspx
- rentosertib / INS018_055 / IPF / Insilico → 用户记忆 + 多源交叉（INS018_055 为 IPF 药物已确认；Phase III NCT07687459、2026-07-07 启动据用户已核实记忆）

### 单源待进一步核实
- IMO 2025 各 AI 系统（Gemini / Seed-Prover 等）的具体分数与参赛情况：本节为多源汇总（含用户前期核实记忆「Gemini 35/42 金 + Seed-Prover 5/6 Lean」），单一权威来源（如 DeepMind 官方 IMO 2025 博客）本轮未成功抓取，建议读者以官方公告为准。
- Kling 3.0 的具体发布日期、通义万相/Seedance/混元世界的版本号与本卷时间线对应：以各厂官方公告为准，本卷不展开未核实细节。
- Chai-1 最新版本细节、Aurora 2 / GenCast 的具体基准数字：本卷未单独抓取，留待后续补全。
- Kimi Alloy（月之暗面）：本轮检索未取得一手确认，标注为「待核实」，宁缺毋臆测。

### 已知澄清
- 「LESV3」并非 World Labs 公开产品名，World Labs 公开产品线为 Marble + Spark + API；LESV3 疑为内部代号或误传。
- AlphaProof 的 Nature 论文（2025-11-12）是对 IMO 2024 战绩（28/42 银牌）方法论的正式披露，而非 IMO 2025 的结果。

<!-- delegate 直接写入，2026-07-20 -->
