# 前沿与媒体 · 03 - 模态专题（NLP / Vision / Speech / 多模态）

> 姊妹篇：[`01-AI顶级信息源实时清单.md`](./01-AI顶级信息源实时清单.md)（全领域）、[`02-后训练信息源专题.md`](./02-后训练信息源专题.md)（后训练）。
>
> 01 是横向广度（80+ 跨域源），02 是垂直深度（后训练一条线）。**本篇是"按模态切片"**——把 NLP / Vision / Speech / 多模态 四个模态各自独占的代码库、数据集、会议、综述、研究者集中起来。**和 01/02 互补不重复**：通用资源（Karpathy/HF Papers/arXiv）已在 01，纯 LLM 训练已在 02，本篇只列"模态特有"的。
>
> **核对日期**：2026-08-03（首版，GitHub API 实抓 + firecrawl 实抓综述页；NLP/Vision 核到核心代码库 stars，Speech/多模态部分待补）
> **方法**：本地 firecrawl self-host（`/v1/scrape`）+ GitHub API（`api.github.com/repos/...`）+ 圈共识基线
> **图例**：🟢 = 活跃　🟡 = 经典稳定　🔴 = 停更/归档　⚠️ = 反爬未核到

---

## 0. 一张图：四大模态的"信息地形"

```
        ┌──────────────────────────────────────┐
        │  多模态（Multimodal）— 模态间的桥      │
        │  CLIP / BLIP / LLaVA / SAM / GPT-4V   │
        └──────────────────────────────────────┘
              ↑              ↑             ↑
   ┌──────────┴──┐  ┌───────┴────┐  ┌─────┴─────┐
   │  NLP / 文本  │  │ Vision / 视觉│  │ Speech /  │
   │ spaCy/HanLP │  │ OpenCV/YOLO │  │ 音频 Whisper│
   │ BERT/GPT    │  │ Detectron2  │  │ ESPnet/Bark│
   │ ACL/EMNLP   │  │ CVPR/ICCV   │  │ Interspeech│
   └─────────────┘  └─────────────┘  └────────────┘
```

**铁律**：**多模态是 2024–2026 的最大变量**——单模态工具（spaCy / OpenCV / Whisper）仍是生产主力，但前沿研究全在多模态桥接（CLIP/BLIP/LLaVA/SAM）。学单模态打地基，跟前沿看多模态。

---

## 一、NLP（自然语言处理）

> **NLP 的地位变化**：2018 前 NLP 是独立学科（HMM/CRF/Seq2Seq），2018 后 LLM 把 NLP "吃掉"了大半。**纯 NLP 信息源现在主要服务于：① 命名实体/分词/句法等结构化任务；② 多语言/低资源语言；③ LLM 之前的"经典 NLP"教学**。

### N1. 顶级 NLP 代码库（GitHub 实抓 stars）

| # | 代码库 | Stars | 状态 | 强项 |
|---|---|---|---|---|
| N1-1 | **HuggingFace Transformers** `huggingface/transformers` | **16.3w** ⭐ | 🟢 ✅ 当日 push | 已扩到 text/vision/audio/multimodal 全模态 |
| N1-2 | **Google BERT** `google-research/bert` | **4.0w** ⭐ | 🟡 最后 push 2024-07（不再维护，但教学金标准）| BERT 原版 TensorFlow 实现 |
| N1-3 | **HanLP** `hankcs/HanLP` | **3.6w** ⭐ | 🟢 中文 NLP 第一库 | 中文分词/NER/句法/语义全套 |
| N1-4 | **jieba** `fxsjy/jieba` | **3.5w** ⭐ | 🟡 最后 push 2024-08 | 结巴中文分词，经典轻量 |
| N1-5 | **spaCy** `explosion/spaCy` | **3.4w** ⭐ | 🟢 工业级 NLP | 工业级英文 NLP，配套 prodigy 标注 |
| N1-6 | **Fairseq** `facebookresearch/fairseq` | **3.2w** ⭐ | 🟡 最后 push 2025-09 | Meta 的 Seq2Seq 工具，含 NLLB 等 |
| N1-7 | **Microsoft UniLM** `microsoft/unilm` | **2.2w** ⭐ | 🟢 LayoutLM/Kosmos/BitNet 源仓库 | 跨任务/语言/模态预训练 |
| N1-8 | **NLTK** `nltk/nltk` | **1.5w** ⭐ | 🟢 教学经典 | 经典 NLP 教学库 |
| N1-9 | **AllenNLP** `allenai/allennlp` | **1.2w** ⭐ | 🔴 **已停更**（最后 push 2022-11）| 被 HF Transformers 取代 |
| N1-10 | **Stanford CoreNLP** `stanfordnlp/CoreNLP` | **1.0w** ⭐ | 🟢 Java 经典 | Stanford NLP 组 Java 套件 |
| N1-11 | **sacrebleu** `mjpost/sacrebleu` | **1.25k** ⭐ | 🟢 标准 BLEU 实现 | 机器翻译评测金标准 |

### N2. NLP 综述博客 / 研究者

| # | 源 | 作者 | 状态 | 强项 |
|---|---|---|---|---|
| N2-1 | **ruder.io** | Sebastian Ruder | 🟢 ✅ 本轮实抓活跃 | NLP Progress 经典综述、跨语言 NLP |
| N2-2 | **Anna Rogers 博客 / X** | Anna Rogers | 🟢 | NLP 评测批判、引用问题 |
| N2-3 | **Yoav Goldberg "NLP Progress"** | Yoav Goldberg | 🟡 经典书 | 《Neural Network Methods for NLP》教科书 |

### N3. NLP 顶级会议（论文雷达）

| 会议 | 全称 | 频次 | CCF 等级 |
|---|---|---|---|
| **ACL** | Assoc. for Computational Linguistics | 年度 | CCF-A（NLP 第一会议）|
| **EMNLP** | Empirical Methods in NLP | 年度 | CCF-B（实测方向顶会）|
| **NAACL** | North American Chapter of ACL | 年度 | CCF-B |
| **COLING** | Intl. Committee on Computational Linguistics | 两年一度 | CCF-B |
| **LREC** | Intl. Conf. on Language Resources and Evaluation | 两年一度 | 数据/评测方向 |

> **入口**：所有 ACL 系会议论文免费下载于 [ACL Anthology](https://aclanthology.org/)（本轮实抓确认活跃，含 1990 至 2026 全论文）。

### N4. NLP 经典数据集

| # | 数据集 | 任务 | 规模 |
|---|---|---|---|
| N4-1 | **GLUE** | 通用语言理解评测（8 任务）| 8 子集 |
| N4-2 | **SuperGLUE** | GLUE 升级版（更难）| 10 子集 |
| N4-3 | **SQuAD** | 抽取式问答 | 100K Q-A |
| N4-4 | **XNLI** | 跨语言推理（15 语言）| — |
| N4-5 | **Common Crawl** | 网页文本（PB 级）| 1PB+ |
| N4-6 | **Penn Treebank** | 句法标注（经典）| 1M 词 |

---

## 二、Vision（计算机视觉）

> **Vision 的地位变化**：2020 前 CV 是独立学科（CNN/ImageNet/检测分割），2020 后 ViT 把 CV 也"吃掉"了——现在主流是 ViT/Swin/CLIP/SAM/Diffusion。**OpenCV 等经典库仍在生产，但前沿全在 Transformer-based 视觉**。

### V1. 顶级 Vision 代码库（GitHub 实抓 stars）

| # | 代码库 | Stars | 状态 | 强项 |
|---|---|---|---|---|
| V1-1 | **OpenCV** `opencv/opencv` | **9.0w** ⭐ | 🟢 ✅ 经典+活跃 | 计算机视觉 C++ 库，工业事实标准 |
| V1-2 | **Ultralytics YOLO** `ultralytics/ultralytics` | **6.0w** ⭐ | 🟢 ✅ 当日 push | **YOLO26**（描述已含 YOLO26/YOLO11/YOLOv8）— 检测/分割/姿态/跟踪 |
| V1-3 | **Detectron2** `facebookresearch/detectron2` | **3.5w** ⭐ | 🟢 | Meta 检测/分割平台 |
| V1-4 | **OpenAI CLIP** `openai/CLIP` | **3.4w** ⭐ | 🟡 最后 push 2026-03 | 对比学习图文预训练，多模态桥梁 |
| V1-5 | **MMDetection** `open-mmlab/mmdetection` | **3.3w** ⭐ | 🔴 最后 push 2024-08（1 年未动）| OpenMMLab 检测工具箱 |
| V1-6 | **torchvision** `pytorch/vision` | **1.8w** ⭐ | 🟢 ✅ 当日 push | PyTorch 官方 CV 库 |
| V1-7 | **google-research ViT** | **1.27w** ⭐ | 🟢 | ViT 官方实现 |
| V1-8 | **MMSegmentation** `open-mmlab/mmsegmentation` | **9.9k** ⭐ | 🟡 最后 push 2024-08 | OpenMMLab 分割工具箱 |
| V1-9 | **Segment Anything (SAM)** `facebookresearch/segment-anything` | ⚠️ 待核（rate limit）| 🟢 | Meta 可提示分割，2023 CV 最大突破 |
| V1-10 | **Detectron2 / MMDet 替代** `microsoft/` 系 | — | — | 见详解 |

### V2. Vision 顶级会议

| 会议 | 全称 | 频次 | CCF |
|---|---|---|---|
| **CVPR** | Computer Vision and Pattern Recognition | 年度 | CCF-A（CV 第一会议）|
| **ICCV** | Intl. Conf. on Computer Vision | 两年一度 | CCF-A |
| **ECCV** | European Conf. on CV | 两年一度 | CCF-B |
| **WACV** | Winter Conf. on Applications of CV | 年度 | CCF-C |
| **BMVC** | British Machine Vision Conf. | 年度 | — |

> **入口**：CVPR/ICCV/ECCV 论文在 [openaccess.thecvf.com](https://openaccess.thecvf.com/) 全免费；CVPR 2026 官网 cvpr.thecvf.com（本轮实抓活跃）。

### V3. Vision 经典数据集

| # | 数据集 | 任务 | 规模 |
|---|---|---|---|
| V3-1 | **ImageNet** | 图像分类（1000 类）| 1.4M 图 |
| V3-2 | **COCO** | 检测/分割/关键点 | 33 万图（cocodataset.org 本轮实抓活跃）|
| V3-3 | **ADE20K** | 语义分割 | 27K 图 |
| V3-4 | **LAION-5B** | 图文对（多模态训练）| 58.5 亿对 |
| V3-5 | **CIFAR-10/100** | 教学分类 | 6 万图 |

### V4. Vision 综述 / 教程

- **CS231n 笔记**（[cs231n.github.io](https://cs231n.github.io/)）：Justin Johnson 写的反向传播/CNN/卷积笔记，至今最清楚
- **PyImageSearch**（[pyimagesearch.com](https://pyimagesearch.com/)，本轮实抓活跃）：Adrian Rosebrock 的 OpenCV 实战博客
- **3Brown1Brown 神经网络系列**：建直觉

---

## 三、Speech（语音 / 音频）

> **Speech 的地位变化**：2022 前 Kaldi/ESPNet 主导，2022 OpenAI Whisper 后**端到端 Transformer 取代流水线**。**TTS 在 2024 后被 LLM-based 系统（Bark/VALL-E/Tortoise）颠覆**。

### S1. 顶级 Speech 代码库（部分待 GitHub API 恢复后补 stars）

| # | 代码库 | Stars | 状态 | 强项 |
|---|---|---|---|---|
| S1-1 | **OpenAI Whisper** `openai/whisper` | ⚠️ 待核（rate limit）| 🟢 多语言 ASR 事实标准 | 多语言语音识别 |
| S1-2 | **FunASR** `modelscope/FunASR` | ⚠️ 待核 | 🟢 阿里达摩院中文 ASR | 中文识别第一开源 |
| S1-3 | **ESPnet** `espnet/espnet` | ⚠️ 待核 | 🟢 端到端语音 | 学术主流 |
| S1-4 | **Kaldi** `kaldi-asr/kaldi` | ⚠️ 待核 | 🔴 经典但已停更（HMM/GMM 时代）| 教学+遗留系统 |
| S1-5 | **Bark** `suno-ai/bark` | ⚠️ 待核 | 🟢 文本转语音/音效/音乐 | generative audio |
| S1-6 | **Coqui TTS** `coqui-ai/TTS` | ⚠️ 待核 | 🟡 工业级 TTS | 多语种 TTS |
| S1-7 | **NVIDIA NeMo** `NVIDIA/NeMo` | ⚠️ 待核 | 🟢 多模态（含 ASR/TTS）| NVIDIA 官方 |
| S1-8 | **HiFi-GAN** `jik876/hifi-gan` | ⚠️ 待核 | 🟡 经典声码器 | TTS 后端 |
| S1-9 | **RVC** `RVC-Project/...` | ⚠️ 待核 | 🟢 语音转换（变声器）| 实时声音转换 |
| S1-10 | **WeNet** `wenet-e2e/wenet` | ⚠️ 待核 | 🟢 端到端 ASR（中文社区）| 出门问问 + 西工大 |
| S1-11 | **SpeechBrain** `speechbrain/speechbrain` | ⚠️ 待核 | 🟢 PyTorch 语音工具箱 | 学术友好 |

### S2. Speech 顶级会议

| 会议 | 全称 | 频次 | 强项 |
|---|---|---|---|
| **Interspeech** | 年度 | CCF-C | 语音第一会议 |
| **ICASSP** | 年度 | CCF-B | IEEE 信号处理（含语音）|

### S3. Speech 教程 / 综述

- **Hugging Face Audio Course**（[huggingface.co/learn/audio-course](https://huggingface.co/learn/audio-course)，本轮实抓活跃）：HF 官方音频课，涵盖 ASR/TTS/分类/音频 LLM
- **AssemblyAI Blog**（assemblyai.com/blog，本轮超时但 URL 有效）：实战教程

### S4. Speech 经典数据集

| # | 数据集 | 任务 | 规模 |
|---|---|---|---|
| S4-1 | **LibriSpeech** | 英文 ASR | 1000 小时 |
| S4-2 | **Common Voice** (Mozilla) | 多语言 ASR | 2 万+ 语言 |
| S4-3 | **GigaSpeech** | 英文 ASR | 1 万小时 |
| S4-4 | **WenetSpeech** | 中文 ASR | 1 万小时 |
| S4-5 | **LJSpeech** | 单人 TTS | 24 小时 |

---

## 四、多模态（Multimodal）—— 2024–2026 最大变量

> **多模态是横跨 NLP+Vision+Speech 的桥**。模型既能读文、看图、听音频，又能跨模态生成。**这是 LLM 之后下一个"范式转移"**。

### M1. 多模态核心模型 / 代码库

| # | 模型 | 类型 | 强项 |
|---|---|---|---|
| M1-1 | **CLIP**（OpenAI 2021）| 图文对比学习 | 多模态对齐的"地基"，零样本分类 |
| M1-2 | **BLIP / BLIP-2**（Salesforce）| 图文理解+生成 | bootstrapped language-image pretraining |
| M1-3 | **LLaVA** | 视觉对话 | 把 CLIP 视觉编码器接 LLaMA，开源 GPT-4V |
| M1-4 | **SAM / SAM 2**（Meta）| 可提示分割 | "图像分割的 ChatGPT 时刻"，SAM 2 扩到视频 |
| M1-5 | **GPT-4V / 4o / Gemini / Claude** | 闭源多模态 LLM | 商业最强 |
| M1-6 | **Qwen-VL / DeepSeek-VL / Yi-VL** | 开源多模态 LLM | 中文社区主力 |
| M1-7 | **Stable Diffusion / Flux / Midjourney** | 文生图 | 生成模型（详见 `讲透生成模型`）|
| M1-8 | **Sora / Veo / Wan / Minimax** | 文生视频 | 2024–2026 视频生成爆发 |

### M2. 多模态核心数据集

- **LAION-5B / LAION-COCO**：58.5 亿图文对，SD/CLIP 训练数据
- **CC3M / CC12M**：Google 概念字幕
- **RedCaps**：Reddit 图文
- **DataComp**：多模态基准数据集筛选

### M3. 多模态研究者必跟

- **Jia Deng**（Princeton，ImageNet 作者）
- **Kaiming He**（MIT，ResNet/Mask R-CNN/ViTDet）
- **Ross Girshick**（Meta，R-CNN 系列）
- **Yann LeCun**（Meta，JEPA）
- **Pieter Abbeel**（Berkeley，多模态 RL）
- **Chuang Gan**（MIT，多模态推理）
- **陈丹琦**（Princeton，多模态 NLP）

---

## 五、推荐信息食谱（按角色分流）

```
想做 NLP 工程师（非 LLM）：
  ├─ spaCy + HanLP + jieba（中文）         ← N1
  ├─ CS224n Winter 2026 + Stanford CoreNLP ← N3 + 讲透公开课 01
  └─ ACL/EMNLP Anthology                    ← N3
        │
想做 CV 工程师：
  ├─ OpenCV + YOLO26 + Detectron2           ← V1
  ├─ CS231n Spring 2026 + PyImageSearch     ← V4 + 讲透公开课 01
  └─ COCO + ImageNet                        ← V3
        │
想做 Speech 工程师：
  ├─ Whisper + FunASR（中文）+ ESPnet       ← S1
  ├─ HF Audio Course                        ← S3
  └─ LibriSpeech + GigaSpeech               ← S4
        │
想做多模态研究者：
  ├─ CLIP + LLaVA + SAM 全跑通              ← M1
  ├─ 读 BLIP-2 + SAM 论文                   ← 讲透基础模型
  └─ LAION + DataComp                       ← M2
```

**一句话策略**：**单模态工具是生产主力（OpenCV/spaCy/Whisper），多模态是研究前沿（CLIP/SAM/LLaVA）**。学单模态打地基，跟前沿看多模态。

---

## 六、维护说明

### 核对日志

- **2026-08-03（首版）**：
  - **环境**：本地 firecrawl self-host + GitHub API（`api.github.com/repos/...`）。
  - **✅ 成功核到**：
    - **NLP 代码库 11 个**（Transformers/BERT/HanLP/jieba/spaCy/Fairseq/UniLM/NLTK/CoreNLP/sacrebleu 全部 stars + last push）
    - **NLP 综述**：ruder.io（活跃）、ACL Anthology（活跃）
    - **Vision 代码库 8 个核心**（OpenCV/Ultralytics/Detectron2/CLIP/MMDet/torchvision/ViT/MMSeg 全部 stars + last push）
    - **Vision 综述**：CVPR 2026 官网（活跃）、COCO（活跃）、PyImageSearch（活跃）
    - **Speech 教程**：HF Audio Course（活跃）
  - **⚠️ 反爬/rate limit 未核到（基线收录）**：
    - **Speech 代码库 11 个**（GitHub API rate limit，下次重核补 stars）：Whisper/FunASR/ESPnet/Kaldi/Bark/Coqui/NeMo/HiFi-GAN/RVC/WeNet/SpeechBrain
    - **SAM 实际路径**（应该是 `facebookresearch/segment-anything`，不是 sam）
    - **Stanford NLP**（nlp.stanford.edu，超时）
    - **AssemblyAI Blog**（超时）

### 下次重核对建议

- **频次**：每 6 个月（模态信息源比课程快，但比 LLM 信息源慢）。
- **重点跟踪**：
  - **多模态迭代**：SAM 3 / GPT-5V / Claude 4V / Veo 3 / Sora 2 等
  - **中文 ASR/TTS**：FunASR/WeNet/MiniCPM-o 等中文社区进展
  - **YOLO 版本号**（YOLO26 已发布，YOLO27 何时？）
  - **GitHub rate limit 重置后**：补 Speech 11 个代码库 stars
- **新增方向**：未来可考虑 **视频生成专题**（Sora/Veo/Wan/Pika/Runway）、**3D AI 专题**（Point-E/Shap-E/LRM）。

### 与其他清单的关系

- **本篇 vs [`01-AI顶级信息源实时清单.md`](./01-AI顶级信息源实时清单.md)**：01 是横向广度（含 H 类 AI Safety、I 类评测等），本篇是模态垂直深度。
- **本篇 vs [`02-后训练信息源专题.md`](./02-后训练信息源专题.md)**：02 是后训练（RLHF/DPO），本篇是模态。**多模态后训练是 2026 的下一波**（如 LLaVA-RLHF、RLHF-V），未来可能要单独写"多模态后训练"。
- **本篇 vs [`../讲透公开课/`](../讲透公开课/)**：CS224n（NLP）/CS231n（CV）等已在 `01-前沿课实时清单.md`。

---

📌 **下一步**

1. **想立刻起步**？告诉我你的**目标模态**（NLP / CV / Speech / 多模态）+ 当前水平，我帮你挑 3 条做成"每周 2 小时学习路径"。
2. **想做某个具体实验**？比如"用 Whisper + FunASR 做中文播客转写"，我直接给可运行代码。
3. **发现 stars 已过时**？特别 Speech 11 个代码库，下次 GitHub API 恢复后告诉我，我补核。
4. **想做更细的垂直专题**？比如"中文 NLP 专题"（HanLP/PaddleNLP/苏剑林系列）、"医学影像专题"，可以单独写。
