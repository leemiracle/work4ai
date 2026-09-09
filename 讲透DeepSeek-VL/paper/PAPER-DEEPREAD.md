# DeepSeek-VL → DeepSeek-VL2 综合精读：从混合编码器到 MoE 动态切片的演进叙事

> 覆盖论文：arXiv 2403.05525（DeepSeek-VL，2024-03-08 提交，v2 2024-03-11）与 arXiv 2412.10302（DeepSeek-VL2，2024-12-13）。两 ID 均已在 arXiv abs 页核实，标题与本地仓 README 引文完全一致，无勘误。
> 本地代码仓：`~/ai/explore/deepseek-ai/DeepSeek-VL` 与 `DeepSeek-VL2`（VL2 仓内含论文 PDF 原件 `DeepSeek_VL2_paper.pdf`）。
> 注：`work4ai/讲透DeepSeek-VL/deepwiki/` 尚未建（两仓 `.understand-anything/` 仅有 intermediate 残留，无成品图谱），故本文 DeepWiki 对照环节缺席，全部代码引用来自本地源码逐行核对。

---

## 1. 一句话定位

**DeepSeek-VL 是 DeepSeek 系 VL 模型的第一代"务实主义"作品：用 SAM+SigLIP 混合编码器在固定 576 token 预算内吃下 1024 分辨率，用 70% 纯文本配比保住语言能力；9 个月后 DeepSeek-VL2 用动态 tiling（任意宽高比切片）+ DeepSeekMoE/MLA 把"高分辨率"与"低推理成本"同时推向极致——4.5B 激活参数打赢一票 7-8B dense 模型。**

团队背景：均为 DeepSeek-AI（幻方）。VL1 一作 Haoyu Lu 等 15 人（大量实习生贡献）；VL2 一作 Zhiyu Wu/Xiaokang Chen 等 27 人，作者线与 DeepSeek-V2/V3 主线高度重叠（Damai Dai、Huazuo Gao、Zhenda Xie、Chong Ruan），说明 VL2 是把主力 LLM 架构成果（MLA、MoE、auxiliary-loss-free 负载均衡）平移到多模态的系统性动作。两代论文均为技术报告体，无同行评审。

## 2. 动机与痛点：V1 诞生前夜的四个缺陷

VL1 引言直接点名当时开源 VLM 的四个结构性问题，这四个问题恰好定义了 V1→V2 的演进坐标：

1. **算力堆在 SFT 而非预训练**——开源模型把资源花在指令微调刷榜，缺乏大规模 VL 预训练带来的世界知识；
2. **学术数据集拼盘 ≠ 真实体验**——benchmark 分数高但真实用户场景（网页截图、PDF、OCR、图表）体验差；
3. **分辨率天花板**——主流 CLIP 系编码器 336/448 分辨率无法支撑密集 OCR 与小目标识别；且存在 "CLIP-blind pairs" 问题（视觉不同的图被 CLIP 编码成相似向量，Tong et al. 2024 的经典发现）；
4. **多模态训练摧毁语言能力**——长程 VL 训练后 LLM 能力灾难性遗忘，没有机制保语言。

VL2 的动机则是**对 V1 自身的两处扬弃**：混合编码器被钉死在 1024×1024 固定分辨率，遇到极端宽高比（InfographicVQA 长图）或超大分辨率就无能为力；dense LLM 推理成本随规模线性上涨，需要 MoE 稀疏化。此外 V1 完全没有 grounding 能力，VL2 把视觉定位作为新增能力线。

## 3. 核心方法

### 3.1 VL1：混合视觉编码器——语义与细节的双塔合流

**直觉**：SigLIP（384×384，text-aligned）擅长高层语义但有 CLIP-blind 问题且分辨率低；SAM-B（1024×1024，vision-only 自监督，ViTDet 骨干）提供低层细节特征但不带语言对齐。两者互补，一次前向同时拿"语义+细节"。

**数学/张量流程**（论文 §3.1，代码完全对应）：

- SAM-B 路：图像 resize 到 1024×1024 → 特征图 64×64×256 → 插值到 96×96×256 → 两个 stride-2 卷积 → 24×24×1024 → reshape 成 **576×1024**；
- SigLIP-L 路：384×384 → **576×1024**；
- 拼接：`[576, 1024] ⊕ [576, 1024] → [576, 2048]`，GeLU 后过 embedding 层进 LLM。

1024 分辨率被压缩进 **576 个 token**，这是"固定 token 预算"的关键设计——为多轮对话和图文交错留出上下文余量。

**Hybrid MLP adaptor**（消融表 10 的赢家）：高/低分辨率特征各过一层独立 MLP 投影（`high_up_proj`/`low_up_proj`，各映射到 `n_embed//2`），embedding 维拼接后再过共享融合 MLP。对照实验显示：序列维拼接（token 翻倍）与三种融合 MLP（hybrid/shared/separate）中，hybrid 平均分最高（55.9）。

**训练策略——模态竞争的治理**（本文最有复用价值的部分）：

- 直接 100% 多模态数据训 LLM → 语言指标雪崩（论文图 4）；根因诊断：多模态语料分布过于简单 + 模态间竞争导致的灾难性遗忘；
- 解法一：**联合训练配比 language:multimodal ≈ 7:3**，语言数据直接复用 DeepSeek-LLM 2T 语料（预训练表里 text-only 占 70%）；
- 解法二：**modality warm-up**——语言数据占比从 1.0 逐步退火到 0.7，避免训练初期失稳；
- 解法三：**modality group training**——按 step 粒度分组（一个 batch 全是文本或全是多模态，不混批），解决"纯文本等图像样本拖后腿"的木桶效应，吞吐 +20% 且不掉分；
- 小模型迭代技巧：1.3B 模型生成式指标噪声大（Schaeffer et al. 2024 的"指标假象"），改用 **Multi-choice PPL 评估**（比对选项位置的困惑度）+ 预训练里掺少量 SFT 数据，才让小模型的消融结论可迁移到 7B。

三阶段流水线：Stage 1 冻结双塔只训 adaptor（消融证明此阶段**数据加量无用**——2K 步 57.5 vs 80K 步 55.6，projector 容量是瓶颈）→ Stage 2 联合预训练（解冻 LLM+adaptor）→ Stage 3 SFT（解冻 SigLIP+adaptor+LLM，SAM-B 仍冻结因显存受限）。

### 3.2 VL1 数据构造 pipeline：真实世界优先

预训练数据六大门类（表 1 配比）：interleaved 图文 13.1%（MMC4/Wikihow/Wikipedia/自建 Epub 教材）、image caption 11.1%（Capsfusion/TaiSu/Detailed Caption）、表格图表 2.1%（Chart2text/Unichart/Ureader/Geo170K/ScienceQA 等 12 源）、Web Code 0.4%（Websight + **自建 plot-to-code**：从 Stack 的 146 万 Jupyter notebook 抽图+前置代码得 200 万对，过滤"单图且代码≥5 行"后留 110 万）、场景文字 OCR 1.2%（ArT/MLT-17/LSVT 等 10 源）、文档 OCR 2.1%（**自建主力**：140 万 arXiv 源码+PDF 用 Nougat 预处理管线渲染成图文对；86 万英文+18 万中文电子书从 Anna's Archive 清洗后 HTML 模板渲染 + K-12 试题百万级）、text-only 70%（DeepSeek-LLM 同款 2T 语料）。

**SFT 数据的方法论核心是 use case taxonomy**：从互联网人工收集 GPT-4V/Gemini 真实测试用例，归纳成 7 大类（Recognition/Conversion/Analysis/Commonsense Reasoning/Logical Reasoning/Evaluation/Multi-graph/Safety）×三级分类树，用 taxonomy 指导每张测试图选配 prompt 构造 in-house SFT 集（占比 10.5%），同一 taxonomy 复用为人工评测集（100 题）。这是"从真实用户场景反推数据构造"的完整闭环，也是 VL1 区别于"学术集拼盘"的立身之本。

### 3.3 VL2：动态 tiling 视觉编码——本文数学重点

**直觉**：与其用一个 1024 大编码器硬吃所有图，不如把高分辨率图切成多个 384 小块（局部 tile）+ 一个 384 全局缩略图（thumbnail），全部喂给**同一个** SigLIP-SO400M-384。局部注意力 ViT 的计算量不随图像总面积二次爆炸，宽高比通过切法自适应。

**候选分辨率集合**（原文公式）：

$$C_R = \{(m\cdot 384,\ n\cdot 384) \mid m,n \in \mathbb{N},\ 1 \le m,n,\ mn \le 9\}$$

即 m×n 网格切块，总块数上限 9（3×3），隐含 token 预算控制。评测 InfographicVQA 等极端长图时放宽到 mn≤18。

**最优切法选择**：对原图 (H,W)，先按"长边对齐、保宽高比"缩放到每个候选分辨率（论文脚注 1），计算 padding 面积，选 padding 最小者。**代码实证**（`processing_deepseek_vl_v2.py::select_best_resolution`）与论文表述是对偶形式：代码按"最大化 effective_resolution（缩放后有效像素数），平手时最小化 wasted_resolution（候选画布−有效像素）"排序——数学上等价于最小化浪费/padding，但实现了两级裁决的精确语义。选中 $(m_i\cdot 384,\ n_i\cdot 384)$ 后切成 $m_i \times n_i$ 个局部 tile + 1 个全局缩略图，共 $1 + m_i n_i$ 张 384×384 过 SigLIP，每块出 27×27=729 个 1152 维 embedding。

**token 数推导**（论文公式 + 代码逐项核对）：2×2 pixel-shuffle 式压缩把每块 729 → 196 token（代码实证：`downsample_mlp_gelu` 分支，27 为奇数先 pad 到 28×28，`F.unfold(kernel=2, stride=2)` 做 space-to-depth 得 4×1152 通道再 Linear 降维；`h = math.ceil((384//14)/2) = ceil(13.5) = 14`）。序列布局：

- 全局块：14×14 网格，每行尾插 1 个 `<tile_newline>` → 14×15 = **210**；
- 局部块拼成 2D 大图（代码 `rearrange('(th tw) (h w) d -> (th h) (tw w) d')`）：形状 $(n_i\cdot 14,\ m_i\cdot 14)$，每行尾插 newline → $m_i\cdot 14 \times (n_i\cdot 14 + 1)$；
- 全局与局部之间插 1 个 `<view_separator>`。

**总 token 数**：$T = 210 + 1 + m_i\cdot 14 \times (n_i\cdot 14 + 1)$。极限情形（m=n=3）约 3.5K token；1×1 时 631 token——动态预算随宽高比伸缩，这正是标题里 "dynamic" 的含义。多图（>2 张）场景禁用 tiling 退回固定 384（论文明示；代码以 `cropping: bool` 参数控制，处理逻辑在 `tokenize_with_image` 里显式分支）。行尾 newline 的作用是给 LLM 提供 2D 空间结构的显式切分行号——继承自 ViPLlava/InternVL 一脉的 tile 系语言设计。

### 3.4 VL2：DeepSeekMoE + MLA 语言底座

三个变体的 LLM 底座分别取自 DeepSeekMoE 3B/16B/27B：Tiny 用多头注意力（MHA），Small/Base 用 **MLA（rank=512）**——KV cache 压缩进潜向量，推理吞吐显著提升。专家配置：routed experts 64/64/72 + shared experts 2 + top-6 路由；路由函数 Tiny/Small 用 Softmax，Base 用 **Sigmoid + 全局 bias 修正项**（即 DeepSeek-V3 论文的 auxiliary-loss-free 负载均衡，aux loss 权重也从 0.001 降到 0.0001）。三档部署门槛：3B/16B/27B 分别跑进 10GB/40GB/80GB 单卡。

训练侧的 MoE 工程细节：视觉编码器作为流水线第一段计算特性与 LLM 块不同，需细粒度切层做 PP 负载均衡；**动态分辨率导致各 rank 图像 tile 数不均，需跨数据并行 rank 做 tile 负载均衡**；纯文本 batch 与含图 batch 走两套流水线策略按需切换。

### 3.5 VL2 数据管线升级

- **配比反转**：VL1 是 text 70% : VL 30%，VL2 反转为 **VL 70% : text 30%**（text 仍取自基 LLM 预训练语料）——因为底座 MoE 已在纯文本上充分预训练，VL2 阶段的重心移到多模态；预训练总量约 800B token。
- **caption 重打标管线**：开源 caption 质量方差大（简短/错配/幻觉），自建 captioner 以 OCR hints + 元信息（地理位置/相机参数）+ 原 caption 为 prompt 重新生成（PixelProse 式策略），再用 DeepSeek Chat 按写作质量打分过滤——大规模标注的重复病用"LLM 质量分"兜底。
- **grounding 数据**（V1 完全没有的能力线）：格式 `Locate <|ref|><query><|/ref|>` → `<|ref|>query<|/ref|><|det|>[[x1,y1,x2,y2],...]<|/det|>`，坐标归一化到 0-999（代码 `processing_deepseek_vl_v2.py` L178-187 注册 5 个特殊 token `<|ref|>/<|/ref|>/<|det|>/<|/det|>/<|grounding|>` 完全对应）；另造负样本（查询目标不在图内）和 in-context grounding（参考图红框物体在另一图找同类）。
- **grounded conversation**：`<|grounding|>` 前缀触发"带框描述"，如 "Two <|ref|>dogs<|/ref|><|det|>[[...]]<|/det|> are running"。
- SFT 侧的精细化：中文混英文病（Tiny 专属）→ 自建中文 QA 集；推理链数据对 Tiny 反而有害（**小模型配简洁回复更好**）；OCR/表格 QA 全部用原图+OCR 信息重生成答案。

## 4. 实验与结果

**VL1-7B vs 同代 7B**（表 5 摘录）：MMBench 73.2 / MMC 72.8 / SEED 70.4 / OCRBench 456 / POPE 88.1 / MMMU 36.6——除 MMMU 外全面领先 LLaVA-Next-7B（67.4/60.0/70.2/-/86.5/35.8）与 CogVLM（63.7/53.8/68.8/34.7）。1.3B 小模型在 tiny 档无对手（MMB 64.6 超 MobileVLM 2.7B 的 59.6）。

**VL1 语言能力保持**（表 7，vs DeepSeek-LLM-7B-Chat）：HellaSwag 68.4 vs 68.5（持平）、MMLU 52.4 vs 49.4（反超）、AGIEval 27.8 vs 19.3（反超）、**GSM8K 55.0 vs 63.0（降 8 分）**——作者坦承 7B 容量下模态竞争仍在，数学是最先被牺牲的能力。

**VL2 的代际跨越**（vs VL1-7B）：OCRBench 811 vs 456（+78%）、DocVQA 93.3、ChartQA 86.0、InfoVQA 78.1、TextVQA 84.2——OCR/文档类全面接近 GPT-4o（736/92.8/85.7/79.2/77.4）。通用档：MMStar 61.3、MMMU 51.1、MME 2253、MMBench-en 83.1、MathVista 62.8，均以 4.5B 激活参数压过 InternVL2-8B/Qwen2-VL-7B 档（如 MMBench 83.1 vs 81.7/83.0，MMStar 61.3 vs 61.5/60.7）。**grounding 新能力**：RefCOCO val 95.1/testA 96.7/testB 92.7，RefCOCO+ val 91.2，超过专门化的 Ferret-v2-7B（92.8/94.7/88.7）与 Qwen2-VL-7B（91.7/93.6/87.3）；Small（2.8B 激活）的 RefCOCO 93.9/95.3/91.3 也已是同档最强。

**消融结论沉淀**（VL1）：adaptor 预热阶段数据不加量；三阶段缺一不可（去 Stage1 或去 Stage2 都掉分）；encoder 消融（训练 loss 视角）证明加 SAM 显著降 loss；adaptor 设计里 hybrid MLP + embedding 维拼接最优。

## 5. 局限与后续

**VL1 自认**：7B 容量导致 GSM8K 退化（模态竞争未根治）；结论章预告 "scale up + MoE"（正是 VL2）。**VL2 自认**：上下文窗口只容几张图，多图交互受限；模糊图像/未见物体鲁棒性不足；感知强推理弱（论文原话 "excels in visual perception... aim to strengthen its reasoning"）。

**社区与后续演进**：VL2 的 OCR/文档能力线后来独立放大成 DeepSeek-OCR（2025，contexts 光学压缩路线）；感知-推理分线思想走向 Janus/Janus-Pro 的理解-生成解耦；动态 tiling 已成 2025 年开源 VLM 事实标准（Qwen2.5-VL 原生动态分辨率、InternVL2.5 动态 tile 均为同族方案）。值得注意的工程遗产：select_best_resolution 的 effective/wasted 两级裁决、tile 行尾 newline 的 2D 结构编码、多图退化固定分辨率策略，被后续多个仓库直接复用。

## 6. 与代码的对照（论文概念 → 本仓实现）

| 论文概念 | 仓库 | 文件 / 类 / 函数 | 备注 |
|---|---|---|---|
| 混合视觉编码器（SAM+SigLIP） | VL | `deepseek_vl/models/clip_encoder.py::HybridVisionTower` | `vision_tower_high`(SAM-B)+`vision_tower_low`(SigLIP-L) 双塔，各自 LayerNorm；SAM 塔仅 `downsamples`/`neck` 参数可训 |
| 1024→576 token 压缩 | VL | `clip_encoder.py` + `sam.py` | 64×64×256 插值 96×96×256，双 stride-2 卷积到 24×24×1024 |
| Hybrid MLP adaptor | VL | `deepseek_vl/models/projector.py::MlpProjector`（`projector_type="low_high_hybrid_split_mlp_gelu"`） | `high_up_proj`/`low_up_proj` 各投影到 `n_embed//2` 再 concat——消融表 10 最优架构的逐字实现 |
| 长宽比保真预处理 | VL | `deepseek_vl/models/image_processing_vlm.py::ImageGenerator.resize` | min_size 兜底的比例缩放+pad 到 1024 |
| 候选分辨率集合 C_R | VL2 | `processing_deepseek_vl_v2.py` L150（`candidate_resolutions` 构造，image_size=384） | mn≤9 |
| 最优切法（min padding） | VL2 | `processing_deepseek_vl_v2.py::select_best_resolution`（L34-52） | 实现为 max effective_resolution + 平手 min wasted 的对偶形式 |
| tile 切分与缩略图 | VL2 | `tokenize_with_image` 内 `ImageOps.pad` 全局 384 + `local_view.crop` 循环切 tile | `images_spatial_crop` 记录 [宽块数, 高块数] |
| pixel shuffle 729→196 | VL2 | `modeling_deepseek_vl_v2.py::MlpProjector`（`downsample_mlp_gelu` 分支 + `token_pooling` 分支） | 实为 pad 到 28×28 后 `F.unfold(k=2,s=2)` space-to-depth + Linear，非严格 PixelShuffle 算子 |
| 2D 序列布局与 newline | VL2 | `modeling_deepseek_vl_v2.py::prepare_inputs_embeds`（L410-454） | `rearrange('(th tw) (h w) d -> (th h) (tw w) d')` 拼 2D 大图、行尾 `image_newline`、`view_seperator`、`global_view_pos` head/tail 可配 |
| token 数公式 T=210+1+… | VL2 | `tokenize_with_image` L573-577 | `h=w=ceil((384//14)/2)=14`，逐项与论文公式吻合 |
| grounding 特殊 token | VL2 | `processing_deepseek_vl_v2.py` L178-187 | `<|ref|>/<|/ref|>/<|det|>/<|/det|>/<|grounding|>` 五 token 注册 |
| 多图禁用动态 tiling | VL2 | `tokenize_with_image(cropping: bool)` 参数 | 论文 ">2 图禁用" 的代码出口 |
| MLA 注意力 | VL2 | `deepseek_vl2/models/modeling_deepseek.py`（DeepseekV2 模型族） | rank=512（Small/Base） |
| MoE 路由+bias 修正 | VL2 | `modeling_deepseek.py`（routed experts/top_k/`e_score_correction_bias`） | Sigmoid 路由仅 Base 档 |
| 视觉编码器 LR 缩放 | VL2 | 训练配置（论文表 2 Visual Encoder LR multiplier=0.1） | 推理仓不含训练代码，属论文侧信息 |

## 7. 学习路径

**前置知识**：ViT/SigLIP 的 sigmoid 对比学习（理解 CLIP-blind pairs 才懂为什么要 SAM）、SAM 的 ViTDet 编码器、LLaVA 三阶段范式（VL1/VL2 的流水线直接继承它）、DeepSeekMoE 与 MLA（读 VL2 前必读 arXiv 2401.06066 与 DeepSeek-V2 报告）。

**精读顺序**：① VL1 §2 数据构造（先建立"真实世界数据"的品味）→ ② VL1 §3.1-3.2（混合编码器 + 模态竞争治理，本文最可迁移的方法论）→ ③ VL2 §2（动态 tiling，边读边在纸上推 token 公式）→ ④ VL2 §3-4（数据管线与 MoE 训练细节）→ ⑤ 两文实验表对照着读，体会 9 个月的代际差。

**复现建议**（按投入递增）：a) 单跑 `DeepSeek-VL2/inference.py`（Tiny 档 10GB 单卡可跑，改 `cropping=False` 对比固定分辨率输出差异）；b) 用 PIL 手写 `select_best_resolution` + tile 切分，对任意长图（如网页截图）算出 token 数，验证 T 公式——本仓代码即参考答案；c) 读 `prepare_inputs_embeds` 的 `rearrange` 段，画出 (th tw)(h w) → (th h)(tw w) 的索引重排示意图，这是理解 2D tile 语义的关键一步；d) 有多卡条件时可复现 VL1 的 modality 配比消融（1B 档即可观察语言指标雪崩现象）。

**一句收束**：V1 的遗产是"数据品味 + 模态治理"，V2 的遗产是"分辨率经济学（tile 数学的预算化）+ 架构杠杆（MoE/MLA）"——两代合起来就是 DeepSeek 系 VLM 的完整世界观：多模态能力是预算约束下的工程分配问题，而非单纯堆参数。
