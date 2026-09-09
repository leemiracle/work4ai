# DeepSeek-OCR: Contexts Optical Compression — 论文精读

> arXiv:2510.18234（2025-10-21 提交，v1）· Haoran Wei, Yaofeng Sun, Yukun Li · DeepSeek-AI
> 代码/权重：github.com/deepseek-ai/DeepSeek-OCR（本仓即本地对照对象）
> 本文是一手 arXiv HTML 全文精读 + 本地代码对照，无转述损耗。

---

## 1. 一句话定位

**把 OCR 重新定义为"上下文光学压缩（contexts optical compression）"的可行性实验**：证明一个紧凑 VLM 可以从极少量 vision tokens 中解码出 10 倍于其数量的文本信息（10× 压缩下解码精度 ~97%，20× 仍有 ~60%），同时顺手造出一个端到端 SOTA 的实用 OCR 模型。团队背景：一作 Haoran Wei 是 Vary / GOT-OCR2.0 / OneChart / Slow Perception 一作，本文是该团队"OCR 1.0→2.0"路线在 DeepSeek 体系内的延伸——但论文的核心论点已从"更好的 OCR"转向"**用视觉作为 LLM 长上下文的压缩介质**"，这是视角上的关键跃迁。

发表时间线：2025-10-20 开源发布，10-21 挂 arXiv，10-23 进入 vLLM 上游（`vllm.model_executor.models.deepseek_ocr`）。

## 2. 动机与痛点

**LLM 侧的痛点**：LLM 处理长文本的计算代价随序列长度二次增长。作者提出一个反向思路：一页文档渲染成图像后，所需 vision tokens 远少于等价数字文本的 text tokens——**视觉模态本身就是一个高压缩比的文本载体**。于是问题变成：从 LLM-centric 视角重新审视 vision encoder，它能为 LLM 的效率做什么（而不是像传统 VLM 那样问"VQA 能做多好"）。OCR 恰好提供了压缩-解压缩的天然映射与量化指标，成为理想试验台。

**Encoder 侧的痛点**（论文 Figure 2 的三类范式批判）：
- **双塔（Vary 系）**：并行 SAM encoder 扩视觉词表，参数/激活可控，但双路预处理难部署、encoder 流水线并行困难；
- **Tile 切块（InternVL2.0 系）**：激活内存低，但原生分辨率太低（<512²），大图被切得粉碎 → vision tokens 爆炸；
- **原生自适应分辨率（Qwen2-VL/NaViT 系）**：灵活，但大图激活内存爆炸（GPU OOM）、训练需超长序列 packing，长 vision tokens 拖慢 prefill 与生成。

**核心研究问题**：一页 1000 词的文档，解码它最少需要多少个 vision tokens？——"a picture is worth a thousand words" 的定量化。

## 3. 核心方法

### 3.1 总体架构：DeepEncoder + 3B-MoE decoder

DeepSeek-OCR = **DeepEncoder（~380M）** + **DeepSeek3B-MoE-A570M decoder**。decoder 用 DeepSeekMoE：64 routed experts 激活 6 个 + 2 shared experts，约 570M 激活参数——3B 的表达力、500M 的推理成本，专为这种"领域中心（domain-centric）VLM 研究"设计。

### 3.2 DeepEncoder：串行"感知-压缩-知识"三级管线（核心创新 #1）

$$\text{SAM-base (80M, window attention)} \rightarrow \text{16× conv 压缩器} \rightarrow \text{CLIP-large (300M, global attention)}$$

- **前段 SAM-base（patch 16）**：window attention 主导，做高分辨率感知。1024×1024 输入 → 4096 个 patch tokens；因为只有 80M 且以窗口注意力为主，激活量可接受。
- **中段 16× 压缩器**：借鉴 Vary 的 2 层卷积，kernel=3 / stride=2 / padding=1，通道 256→512→1024，空间下采样 2×2=4×4=**16 倍**：4096 tokens → 256 tokens。
- **后段 CLIP-large**：dense global attention 做知识整合；**删掉第一层 patch embedding**（输入已不是图像而是上游 tokens）。

设计哲学：让**便宜的窗口注意力处理多 token**、在进入**昂贵的全局注意力之前完成 token 压缩**——"高分辨率、低激活、少 token、多分辨率、适度参数"五个条件同时满足，这是现有三类 encoder 都做不到的。

**解压缩映射**（论文 Eq. 2，把 OCR 形式化为重建任务）：

$$f_{\text{dec}}:\ \mathbb{R}^{n\times d_{\text{latent}}} \rightarrow \mathbb{R}^{N\times d_{\text{text}}},\quad \hat{\mathbf{X}} = f_{\text{dec}}(\mathbf{Z})\quad \text{where } n \leq N$$

其中 $\mathbf{Z}$ 是压缩后的 latent（vision）tokens，$\hat{\mathbf{X}}$ 是重建的文本表示。论文的关键论断：这个非线性映射 $f_{\text{dec}}$ **紧凑语言模型就能通过 OCR 式训练有效学会**——暗示更大的 LLM 经专项预训练可以更自然地内化该能力。

### 3.3 多分辨率支持（核心创新 #2：让"压缩比"成为可调变量）

要测"N 个 text token 最少要多少 vision token"，模型必须支持可变 token 数。方案是**位置编码动态插值 + 多模式同训**：

| 模式 | 分辨率 | vision tokens | 处理方式 |
|---|---|---|---|
| Tiny | 512×512 | 64 | resize |
| Small | 640×640 | 100 | resize |
| Base | 1024×1024 | 256 | padding |
| Large | 1280×1280 | 400 | padding |
| Gundam | n×640² + 1×1024² | n×100+256 | resize+padding |
| Gundam-M | n×1024² + 1×1280² | n×256+400 | 续训获得 |

padding 模式下**有效 token 数**（论文 Eq. 1）：

$$N_{valid}=\left\lceil N_{actual}\times\left[1-\frac{\max(w,h)-\min(w,h)}{\max(w,h)}\right]\right\rceil$$

Gundam 动态模式的 tiling 是"二次窗口注意力"，进一步压激活；因原生分辨率较大，tiles 数控制在 2-9，不会碎片化。Gundam-M 因分辨率过大、与其它模式混训拖慢全局速度，改为在训好的模型上用 6M 数据继续训练（负载均衡考虑）。

### 3.4 数据引擎

- **OCR 1.0（文档+场景）**：30M 页 PDF、约 100 语言（中英 25M）；coarse 标注（fitz 直接抽取）+ fine 标注（中英各 2M 页，PP-DocLayout/MinerU/GOT-OCR2.0 造检测-识别交错数据，坐标归一 1000 bins）；小语种用"模型飞轮"（layout 泛化 + 训 GOT-OCR2.0 标 patch）造 600K；3M Word 数据补公式与 HTML 表格；场景 OCR 中英各 10M（LAION/Wukong + PaddleOCR 标注）。
- **OCR 2.0（人工图像）**：chart 10M（pyecharts/matplotlib 渲染，标签用 HTML 表格而非 OneChart 字典——省 token）；化学式 5M（PubChem SMILES + RDKit）；平面几何 1M（Slow Perception，perception-ruler=4，加平移不变增广）。
- **配比**：OCR 70% / 通用视觉 20% / 纯文本 10%（8192 长度）。通用视觉数据（DeepSeek-VL2 式 caption/detection/grounding）只为保留通用视觉接口；纯文本保语言能力。**注意：无 SFT 阶段，模型不是 chatbot，能力需 completion prompt 激活。**

### 3.5 训练管线（刻意保持简单）

两阶段：①独立训 DeepEncoder（接一个紧凑 LM 做 next-token prediction；全 OCR 数据 + 100M LAION 通用数据，2 epochs，bs 1280，lr 5e-5，seq 4096）；②训完整 DeepSeek-OCR（HAI-LLM 平台，PP=4：**PP0 放 SAM+压缩器并冻结**（当 vision tokenizer），**PP1 放 CLIP 可训练**（当输入 embedding 层），PP2/PP3 各放 LM 6 层；20 节点×8 A100-40G，DP 40，GBS 640，lr 3e-5；纯文本 90B tokens/day、多模态 70B tokens/day）。

## 4. 实验与结果

### 4.1 视觉-文本压缩研究（Fox 基准，论文的主科学结论）

取 Fox 英文文档 600-1300 text tokens 共 100 页，用无布局 prompt（`<image>\nFree OCR.`）：

| Text tokens | 64 vision tokens | 100 vision tokens |
|---|---|---|
| 区间 | 精度 / 压缩比 | 精度 / 压缩比 |
| 600-700 | 96.5% / 10.5× | 98.5% / 6.7× |
| 900-1000 | 85.9% / 15.1× | 96.8% / 9.7× |
| 1200-1300 | 59.1% / 19.7× | 87.1% / 12.6× |

**结论：压缩比 <10× 时解码精度 ~97%；10-12× 时 ~90%；~20× 时仍 ~60%**（且因输出格式与 GT 不完全匹配，实际精度更高）。超过 10× 后退化的两个候选解释：长文档布局更复杂；长文本在 512/640 分辨率下变模糊——作者把后者重新诠释为"**遗忘机制的特性而非缺陷**"。

### 4.2 OmniDocBench 实战（edit distance，越低越好）

| 模式 | tokens | 英文 overall | 中文 overall |
|---|---|---|---|
| Small | **100** | 0.221 | 0.284 |
| Base | 256(182 有效) | 0.137 | 0.240 |
| Gundam | 795 | **0.127** | 0.181 |
| Gundam-M†200dpi | 1853 | **0.123** | 0.157 |
| GOT-OCR2.0 | 256 | 0.287 | 0.411 |
| MinerU2.0 | 6790 | 0.133 | 0.238 |
| Gemini2.5-Pro | - | 0.148 | 0.212 |

三个里程碑：**100 tokens 超 GOT-OCR2.0（256 tokens）；<800 tokens 超 MinerU2.0（6790 tokens）；Gundam-M 1853 tokens 达到端到端 SOTA 梯队**。分文档类型（Table 4）：slides 64 tokens 即可（0.116）、book/report 100 tokens 够；**newspaper（4000-5000 text tokens）必须 Gundam/Gundam-M**（0.94→0.122/0.099）——这正好从应用侧印证了 10× 压缩边界。生产效率：单 A100-40G 200k+ pages/day，20 节点 33M pages/day（可直接当 LLM/VLM 预训练数据工厂）。

### 4.3 定性能力

deep parsing（二次调用解析文档内嵌图表/几何/化学式→SMILES/自然图 dense caption）、~100 语言多语识别、受限的通用视觉理解——全部统一在一个 prompt 体系下。

## 5. 局限与后续（论文自认 + 演进）

- **自认局限**：OCR 不足以完全验证"真正的上下文光学压缩"——尚未做 digital-optical 文本交错预训练与大海捞针测试；>10× 退化机制未定论；early-stage。
- **作者勾画的方向**：多轮对话中把 k 轮以前的历史文本渲染成图（10× 压缩）；更老的历史逐级降分辨率 → token 数递减、文字渐糊，**用光学压缩模拟人类遗忘曲线**（Figure 13，"近期高保真、远期自然衰减"的记忆结构）。这个构想直接呼应了摘要里"memory forgetting mechanisms in LLMs"的研究价值主张。
- **实际后续**：3 个月后 DeepSeek-OCR 2（arXiv:2601.20552，见姊妹篇）升级 encoder 为 causal flow 架构，OmniDocBench v1.5 91.09，证实该路线的可扩展性。

## 6. 与代码的对照（论文概念 → 本仓实现）

| 论文概念 | 本仓位置（DeepSeek-OCR-master/） |
|---|---|
| SAM-base 感知段（window attention） | `DeepSeek-OCR-vllm/deepencoder/sam_vary_sdpa.py`：`ImageEncoderViT`（`window_size` 参数、`global_attn_indexes`、`window_partition/unpartition`） |
| 16× conv 压缩器（2×Conv2d k3s2p1, 256→1024） | `sam_vary_sdpa.py` L166-167：`self.net_2 = nn.Conv2d(256, 512, 3, 2, 1)`、`self.net_3 = nn.Conv2d(512, 1024, 3, 2, 1)`，`forward` 里 `conv2_output→conv3_output` 串联 |
| CLIP-large 知识段（去 patch embed） | `deepencoder/clip_sdpa.py`：`CLIPVisionEmbeddings` 等全套（`forward(x)` 直接吃 token 序列而非 `pixel_values`） |
| projector/维度对齐 | `deepencoder/build_linear.py`：`MlpProjector` |
| 多分辨率模式（Tiny~Gundam） | `run_dpsk_ocr.py` 调用 `model.infer(..., base_size=1024, image_size=640, crop_mode=True, test_compress=True)`——`test_compress` 即压缩实验开关 |
| prompts（布局/自由/rec/通用） | README "Prompts examples"：`<|grounding|>Convert the document to markdown.` 等 |
| 解码端防重复（生产稳定性） | vLLM 上游 `NGramPerReqLogitsProcessor`（ngram_size=30, window=90, whitelist `<td></td>`） |
| PDF 批量生产（200k pages/day） | `DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py` + `config.py` |

**DeepWiki 佐证**（work4ai/讲透DeepSeek-OCR/deepwiki/，10 页）：`1-deepseek-ocr-overview.md` 与 `3.2.2-pdf-document-processing.md` 的管线描述与论文 §3.5 训练-部署细节一致，可交叉参考。

## 7. 学习路径

1. **前置**：ViT 与 window attention（Swin/SAM）→ CLIP 双塔对比学习 → Vary（双塔扩词表）与 GOT-OCR2.0（OCR 2.0 概念）——本文的直接前身。
2. **精读顺序**：§1 问题定义（compression ratio = text tokens / vision tokens）→ §3.2 DeepEncoder → Table 2 压缩主实验 → §5 Discussion（遗忘机制构想，本文思想浓度最高的一节）。
3. **复现建议**：模型只有 3B-MoE（激活 570M），单 A100-40G 可跑——先用 `run_dpsk_ocr.py` 复现 Tiny/Small 模式在自选文档上的精度，再按 Table 2 自己测不同压缩比；进阶可验证"历史渲染成图+逐级降采样"的遗忘模拟是否真的省 token 不丢关键信息。
4. **延伸阅读**：DeepSeek-OCR 2（2601.20552）看 encoder 范式如何被"LLM 化"重构；Context Cascade Compression（2511.15244）是纯文本侧的对照路线。

---

*写于 2026-09-05；一手来源 arXiv HTML v1 + 本仓 76fda72 检出代码。*
