# DeepSeek-VL2 论文精读：MoE 视觉语言模型 + 动态切片视觉编码

> 仓：`/usr-data/data2/repos/deepseek-ai/DeepSeek-VL2`（论文 PDF `DeepSeek_VL2_paper.pdf` 28 页；代码 `deepseek_vl2/models/`）
> 精读日期：2026-11-03 · 锚说明：论文锚 = PDF 页码/节号（pdftotext -layout 对应），代码锚 = 本地仓 `文件:行号`（当前 HEAD 实测）

---

## 0. 一句话主张与发表信息

**一句话主张**：把 DeepSeek-VL 的"双固定分辨率混合编码器"换成**单一 SigLIP + 动态切片（dynamic tiling）**，再把语言底座换成 **DeepSeekMoE + MLA**，用 1.0B/2.8B/4.5B 激活参数在 OCR、grounding、图表理解上打平甚至超过 7B-8B 级稠密开源 VLM（论文 p.1 摘要、Figure 1）。

**发表信息**：arXiv 2412.10302，2024 年 12 月（v1 2024-12-13），DeepSeek-AI 技术报告，未走会议评审路线。前作 DeepSeek-VL（arXiv 2403.05525，ACL 2024）。姊妹篇关系网：语言底座 = DeepSeekMoE（arXiv 2401.06066）+ DeepSeek-V2 的 MLA（2405.04434）+ V3 的 auxiliary-loss-free 负载均衡（引 [20][53][86]，p.5 §2）。

三个变体（论文 Table 1，p.5）：

| 项 | Tiny | Small | VL2（大杯） |
|---|---|---|---|
| LLM 总参 / 激活 | 3B / 0.57B | 16B / 2.4B | 27B / 4.1B |
| 全模型激活参数 | **1.0B** | **2.8B** | **4.5B** |
| 注意力 | **MHA（非 MLA！）** | MLA rank=512 | MLA rank=512 |
| 层数 / 专家 | 12 层 / 64 路由+2 共享 | 27 层 / 64+2 | 30 层 / **72+2** |
| 路由打分 | softmax | softmax | **sigmoid + expert bias** |
| 单卡部署 | 10GB | 40GB | 80GB（p.20 §6） |

这张表里藏着第一个值得注意的细节：**Tiny 根本没用 MLA，也没用 sigmoid+bias 路由**——这两项 V2/V3 才有的技术在最小杯上被裁掉（12 层 MHA），大杯才上 sigmoid 路由 + 全局偏置修正（论文 Table 1 "Expert correction bias ✓" 一列）。这是"效率技术按规模分层启用"的实例，而不是论文摘要给人的"全家桶"印象。

---

## 1. 动机：要替换掉的旧方案是什么

### 1.1 视觉侧：DeepSeek-VL 的双固定分辨率混合编码器

DeepSeek-VL 的做法是 SigLIP（384×384 粗粒度）+ SAM-B（1024×1024 细粒度）双编码器拼接。论文 p.4 §2 明确列出其死穴：**1024×1024 是硬上限**，对超宽/超高长宽比（InfographicVQA 的信息图、密集 OCR、精细 grounding）无能为力；且双编码器带来两套视觉 token 体系的对齐负担。

动态切片的本质：**把"编码器适配图像"倒转为"图像适配编码器"**。任何分辨率、任何长宽比的图，都切回一组 384×384 的 tile 喂给同一个 SigLIP-SO400M——编码器永远工作在它预训练时的原生分辨率上，分辨率自由度被推到数据预处理层。这与 Qwen2-VL 的 NaViT 式原生动态分辨率（连续 resize）是两条路线：VL2 是离散 tile 化（借鉴 LLaVA-NeXT/InternVL2/NVLM，p.4 引 [16][21][55]），换来的是每个 tile 都落在 SigLIP 的分布内、以及 tile 数可精确控制的计算预算。

### 1.2 语言侧：稠密 LLM 的算力税

前作 VL 7B 是稠密 7B。MoE 化的直接收益：激活参数 4.1B 撑起 27B 总参的容量（论文 p.1 摘要"similar or fewer activated parameters"），MLA 再把 KV cache 压进 latent 向量提高吞吐（p.5 §2）。对 VLM 这是双重杠杆——视觉 token 动辄上千，长上下文推理的 KV cache 正是部署瓶颈。

---

## 2. 方法核心：公式主线

### 2.1 动态切片：候选分辨率选择

论文 p.4 §2 给出核心定义。候选分辨率集合：

$$CR = \{(m \cdot 384,\ n \cdot 384) \mid m,n \in \mathbb{N},\ 1 \le m,n,\ mn \le 9\}$$

对输入图像 $(H, W)$，先按长边对齐缩放再 padding（p.4 脚注 1），对每个候选分辨率计算 padding 面积，**选 padding 面积最小的** $(m_i \cdot 384, n_i \cdot 384)$。切出 $m_i \times n_i$ 个 384×384 局部 tile + 1 个全局缩略图，共 $1 + m_i n_i$ 个 tile 过 SigLIP。每个 tile 产出 $27 \times 27 = 729$ 个 1152 维 embedding（p.4）。

注意 $mn \le 9$ 这个约束是**计算预算阀门**：最多 9 个局部 tile + 1 全局 = 10 个 tile。评测 InfographicVQA 这类极限长宽比时放宽到 $mn \le 18$（p.11 脚注 2）——说明 9 的默认值是推理成本与能力的手动折中，而不是能力边界。

**直觉**：选 $(m,n)$ 就是在"格子数尽量少"和"每个格子浪费的 padding 尽量少"之间做帕累托选择。一张 800×2000 的长图会选 $m=1, n=5$（384×1920，padding 少）而不是硬塞 1024×1024。

### 2.2 token 压缩与序列格式

VL adaptor 用 2×2 pixel shuffle 把每 tile 的 27×27=729 token 压到 14×14=196（p.4-5 §2 "Vision-Language Adaptor"）。视觉 token 序列总长（p.5 公式化表述）：

$$\underbrace{14 \times 15 = 210}_{\text{全局缩略图（14 行各加 1 个换行符）}} + \underbrace{1}_{\langle\text{view\_separator}\rangle} + \underbrace{(m_i \cdot 14) \times (n_i \cdot 14 + 1)}_{\text{局部 tile 拼成的大网格 + 末列换行符}}$$

换行符 `<tile_newline>` 与 `<view_separator>` 是**可学习 embedding**（代码 `modeling_deepseek_vl_v2.py:314-318`），把 2D 网格结构显式编码进 1D token 流——LLM 靠这些分隔符恢复"下一行 tile"的边界感。随后两层 MLP（`downsample_mlp_gelu`）投影进语言空间（p.5）。

### 2.3 语言底座：MLA + MoE + 无辅助损失均衡

MLA 部分继承 DeepSeek-V2（p.5 §2 引 [53]）：KV cache 压缩为 latent 向量

$$c^{KV}_t = W^{DKV} h_t,\quad k_t = W^{UK} c^{KV}_t,\quad v_t = W^{UV} c^{KV}_t$$

推理时只缓存 $c^{KV}_t$（rank 512），键值按需上投影。MoE 部分继承 DeepSeekMoE：细粒度专家 + 共享专家隔离（Tiny/Small/大杯均为 top-6 路由 + 2 共享专家，Table 1）。负载均衡用 V3 的全局偏置项（p.5 §2 引 [86]）：

$$s_{i,t} = \sigma(\mathbf{w}_i^\top h_t),\quad \tilde{s}_{i,t} = s_{i,t} + b_i$$

**偏置 $b_i$ 只参与 top-k 专家选择（$\tilde{s}$ 排序），不进入最终权重（权重仍用原始 $s$ 归一化）**——这保证均衡干预不污染梯度信号。此细节在代码里看得比论文清楚（见 §4.3 `modeling_deepseek.py:469` vs `:491`）。

---

## 3. 实验关键数字（表格转述）

### 3.1 OCR/文档线（论文 Table 3，p.11）

| 模型（激活参数） | DocVQA | InfoVQA | TextVQA | OCRBench |
|---|---|---|---|---|
| InternVL2-2B (2.2B) | 86.9 | 58.9 | 73.4 | 784 |
| Qwen2-VL-2B (2.2B) | 90.1 | 65.5 | 79.7 | 794 |
| **VL2-Tiny (1.0B)** | **88.9** | **66.1** | **80.7** | **809** |
| InternVL2-8B (8.0B) | 91.6 | 74.8 | 77.4 | 794 |
| Qwen2-VL-7B (8.3B) | 94.5 | 76.5 | 84.3 | 845 |
| **VL2-Small (2.8B)** | 92.3 | 75.8 | 83.4 | 834 |
| **VL2 大杯 (4.5B)** | 93.3 | **78.1** | 84.2 | 811 |

两个读数：① VL2-Tiny 以一半激活参数在 InfoVQA 上反超 Qwen2-VL-2B（66.1 vs 65.5）且 OCRBench 高 15 分——动态切片对**极端长宽比信息图**（InfoVQA 正是此类）的收益直接兑现；② 前作 DeepSeek-VL 7B 的 OCRBench 只有 456（Table 3 倒数第二行），到 VL2 大杯 811，**接近翻倍**——这是"固定 1024 上限 → 动态切片"单项升级的最干净证据。

### 3.2 通用 QA/数学线（论文 Table 4，p.12）

VL2 大杯（4.5B 激活）：MMStar 61.3 / MMMU(val) 51.1 / MathVista 62.8 / MMBench-en 83.1 / MME 2253。对比 InternVL2-8B（61.5/51.8/58.3/81.7/2210）与 Qwen2-VL-7B（60.7/54.1/58.2/83.0/2327）：**MathVista 大杯 62.8 明显领先两个 8B 级对手（+4.5/+4.6）**，但 MMMU 落后 Qwen2-VL-7B 3 分——MoE 省算力不等于全科免费午餐，学科知识密集型基准上总容量差距仍会显形（闭源 GPT-4o MMMU 69.1，差距仍约 17 分）。

### 3.3 Grounding 线（论文 Table 5，p.17-18）

| 模型 | RefCOCO val | RefCOCO testA | RefCOCO+ val | RefCOCOg val |
|---|---|---|---|---|
| Florence-2-L（任务专用微调） | 93.4 | 95.3 | 88.3 | 91.2 |
| Qwen2-VL-7B | 91.7 | 93.6 | 85.8 | 87.3 |
| **VL2-Small (2.8B)** | 93.9 | 95.3 | 89.4 | 92.6 |
| **VL2 大杯 (4.5B)** | **95.1** | **96.7** | **91.2** | **92.8** |

VL2 大杯 **RefCOCO 五项全部超过任务专用的 Florence-2-L**，RefCOCO val 95.1 也是该表全场最高。Grounding 是 VL2 新增能力（前作没有），靠的是预训练期的 `<|ref|>/<|det|>` 特殊 token 数据格式（p.7 §3.2：坐标归一化到 0-999、构造负样本）+ SFT 期的 in-context grounding 数据（p.8 §3.3）。定性部分（p.17-19）展示了向梗图/动漫/名人等训练分布外的泛化。

### 3.4 训练配置（论文 Table 2，p.10）

三阶段：对齐（1.2M ShareGPT4V，冻结 LLM，2.0B tokens）→ VL 预训练（~800B tokens，70% VL + 30% 纯文本，全参解冻）→ SFT（~19.5B tokens）。序列长 4096，三变体训 7/10/14 天、16/33/42 节点 × 8×A100。基础设施（p.10-11）：视觉编码器在流水线并行里做**细粒度按层切分**防 bubble；动态切片导致各 rank tile 数不均，需 **tile 级负载均衡**——动态切片给分布式训练带来的新工程税。

---

## 4. 代码对照：论文章节 ↔ 本地仓实现

仓内 `deepseek_vl2/models/` 六个文件 4876 行，覆盖推理全链路（训练代码未开源，仓内只有 `inference.py`/`web_demo.py`）。

### 4.1 动态切片 preprocessing（论文 §2 "Dynamic Tiling Strategy" ↔ `processing_deepseek_vl_v2.py`）

| 论文表述 | 代码实现 | 锚 |
|---|---|---|
| "选 padding 面积最小的候选分辨率"（p.4） | `select_best_resolution()`：**先最大化 effective_resolution（缩放后落在候选框内的有效像素），平局再比 wasted_resolution（padding 浪费）**——与论文措辞语义等价但判据顺序更精确 | `processing_deepseek_vl_v2.py:34-52` |
| ">2 张图禁用动态切片"（p.4） | `cropping=len(pil_images) <= 2`，多图时直接退回 384×384 单 tile | `processing_deepseek_vl_v2.py:273,430,544-547` |
| 全局缩略图 | `ImageOps.pad(image, (384,384))` | `processing_deepseek_vl_v2.py:551-553` |
| 局部 tile 切割 | 先 pad 到 (best_w, best_h) 再按 384 步长 crop | `processing_deepseek_vl_v2.py:556-561` |
| token 数公式 210+1+(mh·14)(mw·14+1) | `h*(w+1) + 1 + (nh*h)*(nw*w+1)`，h=w=⌈(384/14)/2⌉=14 | `processing_deepseek_vl_v2.py:568-574` |
| grounding 特殊 token | tokenizer 注册 `<|ref|>` 等五个 | `processing_deepseek_vl_v2.py:180-188` |

### 4.2 Projector：论文说 pixel shuffle，代码是 unfold（论文 p.4-5 ↔ `modeling_deepseek_vl_v2.py`）

`MlpProjector` 的 `downsample_mlp_gelu` 分支（`modeling_deepseek_vl_v2.py:56-65`）首层 Linear 输入维度是 `input_dim * downsample_ratio²` = 1152×4 = 4608——4 个空间相邻 token 拼进通道。空间到深度的实际搬运用的是 **`F.unfold(kernel=2, stride=2)`**（`modeling_deepseek_vl_v2.py:93-109`），而非 `nn.PixelShuffle` 算子；同文件还实现了备选的 `token_pooling` 线性池化路径（`:70-91`，默认关闭）。另外 27→14 的"2×2"本该出奇数问题（27 不能被 2 整除），代码在 unfold 前 pad 到偶数（`:98-104`）——论文的"2×2 pixel shuffle 27×27→14×14"这七个字背后是 padding+unfold 两个工程细节。

### 4.3 tile 特征组装与 MoE/MLA（论文 §2 后半 ↔ `modeling_deepseek_vl_v2.py` + `modeling_deepseek.py`）

- **tile 序列拼装**（论文 Figure 3 ↔ `prepare_inputs_embeds`，`modeling_deepseek_vl_v2.py:336-477`）：按 `images_spatial_crop` 打包全部 tile → vision 前向（`:378`）→ projector（`:381`）→ 全局特征 reshape 成 (h, w+1) 加 newline（`:412-420`）→ 局部 tile 用 einops `rearrange("(th tw) (h w) d -> (th h) (tw w) d")` 拼成大网格再加 newline（`:424-446`）→ `global + view_separator + local` 按 `global_view_pos` 头/尾拼接（`:449-454`）→ `masked_scatter_` 写回 input_embeds 的 `<image>` token 位（`:475`）。论文 Figure 3 那张图的每一步箭头都能在这里对上。
- **MoE 路由与偏置**（论文 Table 1 sigmoid+bias ↔ `modeling_deepseek.py:393-522`）：`MoEGate.forward` 里 sigmoid 打分（`:433-434`）；`topk_method=="noaux_tc"` 分支中 `scores_for_choice = scores + e_score_correction_bias` 只用于 top-k 选择与组筛选（`:467-490`），**最终权重 `topk_weight = scores.gather(1, topk_idx)` 取的是无偏置原始分**（`:491`）——§2.3 的"偏置不进权重"论断的代码实证。注意 `assert not self.training`（`:468`）：推理期才走 noaux_tc 分支，训练期偏置直接参与路由（与 V3 报告的表述一致）。辅助损失计算在同函数 `:500-522`。
- **MLA**：`DeepseekV2Attention`（`modeling_deepseek.py:714` 起）完整搬自 DeepSeek-V2 实现；MoE 层 `DeepseekV2MoE` 在 `:552`。
- **SigLIP**：`siglip_vit.py:241` VisionTransformer，`forward` 在 `:552`；`forward_features`（`:524`）里 `num_recomputing_layers`（`:531`）对尾部层做 checkpoint 重算——视觉编码器训练省显存的细节，论文未提。

### 4.4 部署：单卡 10GB 的支撑（论文 p.20 §6 ↔ `modeling_deepseek_vl_v2.py:479-557`）

`incremental_prefilling()`：1024-token 分块 prefill + **每块 KV cache 在 CPU/GPU 间来回搬**（`_move_past_key_values_to_cpu` `:630-634` / 回 GPU `:636-640`）。Tiny 3B 装进 10GB 单卡的宣传背后，一半功劳是 MoE 激活 0.57B，另一半是这个 KV cache offload 工程——论文只在结论提了部署数字，机制全在代码里。

---

## 5. 批判性评估：论文没说的

1. **"每 tile 独立编码"丢失全局-局部交互**。所有 tile 过共享 SigLIP 时互相看不见（`siglip_vit.py` 前向按 batch 维独立），跨 tile 的长程依赖完全交给 LLM 在 token 序列上补——对"跨页表格追踪行"类任务这是结构性短板（对比 Qwen2-VL 的全程 2D-RoPE 连续注意力）。
2. **`mn ≤ 9` 的预算阀**。默认 10 tile ≈ 2730 个视觉 token（210+1+9×(14×15)=210+1+1890…按公式 (m·14)(n·14+1) 计），评测时才放宽到 18——说明视觉预算是拍出来的常数，且放宽后 token 数线性涨，上下文窗口压力直接转嫁给"每会话只能塞几张图"（p.20 limitation 自认）。
3. **Tiny 的中英混杂靠数据补丁修**（p.8 §3.3）——容量不足的症状治标。
4. **OCRBench 811 vs Small 的 834**：大杯 OCRBench 反而低于 Small（Table 3），MoE 放大OCR这种"记忆密集"任务的收益并不单调——选型时别默认"大杯全赢"。
5. **训练代码未开源**：三阶段 pipeline 与双流水线策略切换只有文字描述，复现者需自行补齐。

## 6. 局限与后续工作

论文自认三条（p.20 §6）：多图上下文窗口小、模糊图/未见物体鲁棒性弱、推理能力待加强。放在时间线上看后续：① 动态切片范式被社区广泛继承（token 公式与 LLaVA-NeXT AnyRes 同构），后来者普遍转向**原生动态分辨率 + 2D-RoPE** 路线（Qwen2.5-VL、InternVL2.5 系）；② MoE-VLM 路线被 Aria 等后续工作验证有效；③ grounding 特殊 token 协议（`<|ref|>...<|det|>[x1,y1,x2,y2]` + 0-999 归一化 + 负样本）成为开源 VLM 通用做法之一；④ VL2 无视觉生成、无视频输入——DeepSeek 后续多模态线转向 Janus 系（生成理解统一）而**没有出 VL3**，VL2 成为该系列在开源 VLM 竞争白热化前夜的绝唱。

对本系列读者的定位建议：**读 VL2 的最大价值不在 benchmark（已被超越），而在"论文七字表述 ↔ 代码真实实现"的缝隙**——select_best_resolution 的双判据、unfold 伪 pixel shuffle、noaux_tc 的训练/推理分叉、KV offload，这四处都是工程落地时才会撞上的暗礁，精读价值高于追分。

---

### 附：本仓姊妹精读

- `../../../../讲透宇宙/04-研/讲透DeepSeek-VL//paper/PAPER-DEEPREAD.md`：前作（混合编码器路线起点）
- `../../../../讲透宇宙/04-研/讲透DeepSeek-MoE//paper/PAPER-DEEPREAD.md`：语言底座细粒度专家分割源头（本篇 §2.3 的展开）
