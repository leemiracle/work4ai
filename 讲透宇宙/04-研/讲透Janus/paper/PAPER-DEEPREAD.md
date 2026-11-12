# Janus / Janus-Pro 论文精读

> 论文一：*Janus: Decoupling Visual Encoding for Unified Multimodal Understanding and Generation*，arXiv:2410.13848（2024-10-17，Chengyue Wu 等 11 人，DeepSeek-AI + HKU + PKU）
> 论文二：*Janus-Pro: Unified Multimodal Understanding and Generation with Data and Model Scaling*，arXiv:2501.17811（2025-01-27，Xiaokang Chen 等 8 人，DeepSeek-AI）
> 本地仓：`~/ai/explore/deepseek-ai/Janus`（含 janus_pro_tech_report.pdf、janus/ 与 janusflow/ 两套推理代码）

> **⚠️ ID 勘误**：任务原给的 "2411.07975（Janus-Pro）" 经 arXiv 页核实**并非 Janus-Pro**，而是 **JanusFlow: Harmonizing Autoregression and Rectified Flow**（CVPR 2025，同团队姊妹工作，用整流流替代 VQ token 的生成头）。Janus-Pro 技术报告的正确 ID 是 **2501.17811**（已通过 arXiv 页与 GitHub README bibtex 双重核实）。JanusFlow 不在本次精读范围，只在展望中带一句。

---

## 1. 一句话定位

Janus 是 DeepSeek 的**统一多模态理解与生成**自回归框架，核心主张一句话讲完：**理解与生成对视觉表征的粒度需求根本不同，别共用一个视觉编码器，解耦成两条通路、共用一个 transformer**。以 1.3B 小模型在理解基准上打赢一批 7B-13B 对手、生成基准上打赢 SDXL/DALL-E 2，被广泛视为"解耦路线"的代表性验证。Janus-Pro（2025-01）是同一架构在**训练策略、数据、规模**三轴上的升级版，把 GenEval 从 61% 推到 80%。

命名取自罗马双面神 Janus——两张脸各看一个方向，恰对应"理解要抽象语义、生成要具体细节"这对矛盾在同一模型内的共存。

## 2. 动机与痛点

统一理解+生成模型（区别于"LLM 外挂扩散模型"的 Emu/DreamLLM 类工具调用方案——那不算真统一，生成上限被外部扩散模型锁死）此前的主流做法是**单一视觉编码器通吃两任务**：Chameleon 用 VQ tokenizer 同时做理解和生成的输入编码；Show-o、LWM、VILA-U 同思路（后者用语义 tokenizer）。

痛点是一个表征学冲突：

- **多模态理解**要的是**高维语义**表征——物体类别、属性、可供推理的抽象信息；
- **视觉生成**要的是**低维细节**表征——精细空间结构与纹理，服务于逐 token 重建图像。

把两种表征塞进同一编码器的输出空间，必然互相妥协。后果是统一的模型**理解能力系统性落后**：Chameleon-7B 在 MMMU 仅 22.4、MM-Vet 仅 8.3，Show-o 的 MME 只有 948.4——远低于同量级理解专用模型。Janus 的解法直接了当：编码解耦、处理统一。额外红利是**灵活性**——两路各自换 SOTA 编码器互不牵连（理解侧换 EVA-CLIP/InternViT、生成侧换 MoVQGAN 或扩散 loss），未来加音频/点云/EEG 编码器即插即用。

## 3. 核心方法

### 3.1 架构（Janus 与 Janus-Pro 完全一致）

```
文本 ────────────── LLM tokenizer ──► embedding ─┐
                                                  │
理解图像 ─► SigLIP-Large-Patch16-384 ─► 2D网格flatten成1D ─► understanding adaptor(2层MLP) ─┤
                                                  │        ├──► 统一自回归 Transformer
生成图像 ─► VQ tokenizer(LlamaGen) ─► 离散ID→codebook embedding ─► generation adaptor(2层MLP) ─┘
                                                  │
文本预测：LLM 内置 lm_head │ 图像预测：随机初始化的独立 image head
```

关键数字：VQ tokenizer codebook **16384**、下采样率 **16×**（384×384 图 → 576 个 token）；无任何特殊 attention mask，纯自回归。

### 3.2 训练目标与推理

损失就是标准交叉熵 $\mathcal{L}=-\sum_i \log P_\theta(x_i\mid x_{<i})$——理解任务对文本序列算 loss，生成任务只对图像 token 序列算 loss，不同任务**无加权**（极简哲学）。文生图推理用 classifier-free guidance：训练时以 10% 概率把文本条件替换为 pad token，推理时 $l_g=l_u+s(l_c-l_u)$，默认 $s=5$。

### 3.3 三阶段训练（Janus）

| | 训练对象 | 数据 | 步数/lr | 数据配比(理解:文本:生成) |
|---|---|---|---|---|
| Stage I | 仅两个 adaptor + image head（encoders 与 LLM 全冻结） | ShareGPT4V 1.25M 图文对 + ImageNet-1k 1.2M | 10K / 1e-3 cosine | 1:0:1 |
| Stage II | 解冻 LLM，全参数统一预训练 | 纯文本(DeepSeek-LLM 语料)+交错图文(WikiHow/WIT)+caption+表格图表(DeepSeek-VL)+文生图 | 180K / 1e-4 constant | 2:3:5 |
| Stage III | SFT（**除 generation encoder 外**全参） | 指令对话混合 | 24K / 2e-5 | 7:3:10 |

两个继承自 PixArt 的技巧：ImageNet 类别条件数据只在前 120K 步出现（先学像素依赖再学复杂场景）；caption 以 25% 概率只取第一句（练短 prompt 生成）。全程 384×384（理解侧长边缩放短边补灰 RGB(127,127,127)；生成侧短边缩放长边裁剪），sequence packing 提效。训练用 HAI-LLM 框架，16 节点×8 A100-40G 跑 7 天。

### 3.4 Janus-Pro 的三轴升级（架构不动）

1. **训练策略**：Stage I 延长训练让 adaptor 在分类数据上充分收敛；Stage II 采用**早停**（270K 步计划，实际提前停）——直接治好了 Janus"短 prompt 生成差、输出不稳定"的老毛病。
2. **数据扩展**：理解侧 +90M 样本（参考 DeepSeek-VL2 配方：YFCC caption、Docmatix 表格/图表/文档、MEME 理解、中文对话）；生成侧 +**72M 合成美学数据**，使真实:合成 = **1:1**——论文观察到真实网络图噪声大导致生成不稳定，合成数据让收敛更快、美学质量显著提升。
3. **模型规模**：1.5B / 7B 双尺寸（DeepSeek-LLM 1.5B/7B 底座）。更大 LLM 下理解与生成的 loss 收敛速度都显著加快，验证解耦架构的可扩展性。训练成本：1.5B/7B 分别 16/32 节点×8 A100 跑 9/14 天。

## 4. 实验与结果

**Janus（1.3B）多模态理解**：POPE 87.0、MME-P 1338.0、MMBench 69.4、SEED 63.7、VQAv2 77.3、GQA 59.1、MMMU 30.5、MM-Vet 34.3。对比：Show-o（1.3B 统一）MME 仅 948.4、GQA 48.7——Janus 提升 41%/30%；对 7B 理解专用模型 LLaVA-v1.5（POPE 85.9/MMB 64.3/SEED 58.6/MM-Vet 31.1）与 Qwen-VL-Chat-7B 全面反超。

**Janus 文生图**：GenEval 总分 **0.61**（Show-o 0.53、SDXL 0.55、DALL-E 2 0.52、Chameleon-34B 0.39）；细分上 Position 0.46 vs SDXL 0.15——指令跟随是小模型统一架构的意外强项。COCO-30K FID 8.53、MJHQ-30K FID 10.10，均优于 Show-o/LWM。

**消融（本篇论文最核心的证据链，Table 5）**：

| 实验 | 视觉编码 | 任务 | POPE | MMB | COCO-FID |
|---|---|---|---|---|---|
| A | VQ tokenizer 共用 | 理解+生成 | 60.1 | 35.0 | 8.72 |
| B | semantic tokenizer 共用 | 理解+生成 | 82.4 | 52.7 | 7.11 |
| C | semantic tokenizer | 只理解 | 83.9 | 62.1 | - |
| D | **SigLIP + VQ 解耦（Janus）** | 理解+生成 | **87.0** | **69.4** | 8.53 |
| E | SigLIP | 只理解 | 85.9 | 70.6 | - |
| F | VQ | 只生成 | - | - | 8.92 |

三个读数：①A 证明 VQ 编码做理解确实弱；②**B vs C 是 trade-off 的直接实锤**——同一个更强 tokenizer，一旦同时服务生成就把理解从 62.1 拖到 52.7（生成挤占了表征）；③**D vs E/F**：解耦后的统一模型几乎无损地同时拿到两种能力（69.4≈70.6、8.53≈8.92）——统一训练不是问题，表征冲突才是。

**Janus-Pro-7B**：MMBench **79.2**（Janus 69.4、TokenFlow-XL-13B、MetaMorph 75.2 之下无一合手）；GenEval **0.80**（SD3-Medium 0.74、DALL-E 3 0.67）；DPG-Bench **84.19** 全场第一——1.3B 时代的"生成小胜"到 7B 变成对专用扩散模型的全面超越。

## 5. 局限与后续

论文自认局限（Janus-Pro §4）：①输入分辨率锁 384×384，OCR 等细粒度理解任务吃亏；②生成侧低分辨率 + VQ tokenizer 重建损失，语义丰富但细节不足（小人脸欠细节）。加分辨率是显式出路。

后续演进三条线：①**JanusFlow**（arXiv:2411.07975，CVPR 2025）——生成头从"离散 VQ token 自回归"换成**整流流（rectified flow）**，证明 flow 可以直接嵌进 LLM 框架无需复杂架构改动，配合解耦编码器与表征对齐两策略；②社区蒸馏/加速（Janus-Pro 的 grpo/sift 变体众多）；③DeepSeek 内部这条线最终汇入 VL 系列与更晚的统一模型实践。行业影响：解耦编码已成统一模型标配设计（后继众多统一模型皆引 Janus 为据），"understanding encoder 自由升级 + generation encoder 自由升级"的工程红利被广泛继承。

## 6. 与代码的对照（论文 → 本仓文件）

| 论文概念 | 仓内位置 | 说明 |
|---|---|---|
| 统一模型主体 | `janus/models/modeling_vlm.py` → `MultiModalityCausalLM` | 六件套组装：`vision_model`（SigLIP）+ `aligner`（understanding adaptor）+ `gen_vision_model`（VQ）+ `gen_aligner`（generation adaptor）+ `gen_head`（image head）+ `language_model`（DeepSeek-LLM）；`vision_head` 类即论文"随机初始化图像预测头" |
| SigLIP 理解编码器 | `janus/models/siglip_vit.py`、`clip_encoder.py` | SigLIP-Large-Patch16-384 |
| VQ 生成编码器 | `janus/models/vq_model.py` | LlamaGen tokenizer（codebook 16384/16×下采样） |
| 2 层 MLP adaptor | `janus/models/projector.py` | 两路 adaptor 同结构 |
| 特征序列拼接 | `janus/models/processing_vlm.py`、`image_processing_vlm.py` | 多模态特征序列组装 + 384 边缘填充/裁剪预处理 |
| 多模态理解推理 | `inference.py`、`interactivechat.py` | chat 模板在 `janus/utils/conversation.py` |
| 文生图推理（CFG=5） | `generation_inference.py` | 论文 §3.4 CFG 公式实现 |
| Janus-Pro 演示 | `demo/app_januspro.py` | Pro 模型加载路径 |
| JanusFlow 变体 | `janus/janusflow/`（含 `uvit.py`） | 整流流生成头（姊妹论文，非本篇主角） |

注意仓库 README 只给模型卡不重述训练细节；训练代码未开源，本仓是**推理仓**——精读复现训练需自行按论文超参表（Table 1/2）搭建，或参考第三方复现（如 ModelScope Janus 训练教程）。

## 7. 学习路径

**前置**：①LLaVA 范式（ViT+adaptor+LLM 的理解侧标准结构）；②VQ-VAE/LlamaGen（离散图像 token 与 codebook）；③SigLIP（sigmoid 对比损失）；④CFG（classifier-free guidance）概念；⑤多模态基准体系（POPE/MME/MMBench/GenEval 各测什么）。

**精读顺序**：Figure 1（双面神动机图）→ §1 粒度冲突论述 → Figure 2 架构 → Table 5 消融（本文最精华，B vs C vs D 的对照链）→ Janus-Pro §2 三轴升级 → 两篇的限制章节（对照读可看出"数据换血（合成美学 1:1）是 Pro 最大杠杆"这一隐含结论）。

**复现建议**：①门槛最低：本仓 `inference.py`/`generation_inference.py` 跑 Janus-Pro-1B（消费级显卡可跑，bf16 下 ~3GB）；②图像侧想看细节：读 `vq_model.py` 对照 codebook/下采样率与论文数字；③想动手练统一训练：用 OpenDataLab/ModelScope 的 Janus 复现教程，小规模复刻 Stage I（adaptor 对齐）即可感受"冻结底座训 adaptor"的成本优势；④生成质量评估跑 GenEval 官方工具链，Position/Color 子项最能暴露模型指令跟随短板。

**延伸阅读**：Chameleon（被对比的共用编码器路线）、Show-o、VILA-U（semantic tokenizer 路线）、Transfusion（扩散损失路线）、LlamaGen（VQ tokenizer 出处）、DeepSeek-VL2（Pro 数据配方的来源）。
