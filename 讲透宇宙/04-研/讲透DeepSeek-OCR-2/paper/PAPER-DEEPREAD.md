# DeepSeek-OCR 2: Visual Causal Flow — 论文精读

> arXiv:2601.20552（2026-01-28 提交，v1）· Haoran Wei, Yaofeng Sun, Yukun Li · DeepSeek-AI
> 代码/权重：github.com/deepseek-ai/DeepSeek-OCR-2（本仓即本地对照对象）
> 本文是一手 arXiv HTML 全文精读 + 本地代码对照。前置阅读：DeepSeek-OCR 精读（同目录姊妹篇）。

---

## 1. 一句话定位

**把 DeepEncoder 里的 CLIP 换成一个 0.5B 的 LLM（Qwen2-0.5B），通过"视觉 token 双向注意力 + 可学习 query 因果注意力"的混合掩码，让 encoder 学会按语义因果顺序重排视觉 token**——提出"两个级联的 1D 因果推理结构（encoder 重排 + decoder 自回归）逼近真 2D 推理"的新范式，同时在 OmniDocBench v1.5 上以最少的视觉 token 上限（1120）拿到 91.09 的端到端最优成绩。同团队（Wei/Sun/Li）在 DeepSeek-OCR 发布 3 个月后的架构级升级，副标题 "Visual Causal Flow" 即核心机制名。

## 2. 动机与痛点

**认知科学动机**：人类视觉系统与 transformer encoder 相似（中央凹注视 ≈ visual tokens，局部锐利、全局感知），但有一个本质差异——现有 VLM 把 2D patch 按光栅扫描顺序（左上→右下）展平成 1D 序列并配固定位置编码（RoPE），而**人类扫视是语义驱动的因果流**：追踪一条螺旋线时，每次注视的位置因果地取决于之前的注视；读复杂版式的文档时视线按逻辑结构跳跃。空间坐标顺序是一种"不当归纳偏置"。

**架构动机**：LLM 天生是 1D 序列模型，图像是 2D 结构，直接展平引入语义无关的顺序偏置。文档 OCR 是理想试验台：复杂版式、公式、表格天然携带"因果视觉逻辑"。

**工程背景**（承自 V1）：DeepSeek-OCR 已证明 10× 光学压缩可行，但 encoder 里的 CLIP 只有双向注意力，无法做顺序决策。V2 的问题是：**能否让 encoder 自己决定"哪些视觉信息先被送进 LLM"**？

## 3. 核心方法

### 3.1 总体架构：DeepEncoder V2 = vision tokenizer + LM-style encoder

继承 V1 的"tokenizer 压缩 + 全局知识段"结构，关键替换：**CLIP-large → Qwen2-0.5B（decoder-only LLM）**。

- **Vision tokenizer**（保留自 V1）：SAM-base 80M（window attention）+ 2 层 conv（16× 下采样）。唯一改动：末层 conv 输出维度 1024→**896**，对齐 Qwen2 hidden size。论文论证这个压缩型 tokenizer 并非必需（可换成简单 patch embedding），保留它是为了用 80M 参数在窗口注意力内完成 16× token 压缩，参数量与 LLM 文本输入侧的 embedding（~100M）同量级。
- **LM-style encoder**：Qwen2-0.5B（500M，与 CLIP ViT 300M 计算量相当），**prefix-concatenation**：视觉 tokens 作为前缀拼接，causal flow queries 作为后缀追加。

### 3.2 Causal Flow Query（核心创新 #1）

可学习 query 数量 **等于** 视觉 token 数量（n=m，保持基数一致，为"重注视/冗余"留容量——padding、边框等冗余 token 为二次审视提供空间）：

$$n = \frac{W \times H}{16^2 \times 16}$$

（分子是 patch 数，分母 16²×16 是 patch 化再乘压缩器 16×。）

**多 crop 固定 query 配置**：global view 1024×1024 → 256 个共享 query embedding；local crops 768×768 → 144 个 query，crop 数 k∈[0,6]（两边 <768 则不切）。送入 LLM 的总 token 数 $= k \times 144 + 256 \in [256, 1120]$——上限 1120 低于 V1 Gundam 的 1156，且刻意对齐 **Gemini-3-Pro 的最大视觉 token 预算**（作者把模型放在与前沿闭源模型同预算可比的位置）。

### 3.3 混合注意力掩码（核心创新 #2，论文 Eq. 1）

$$M=\begin{bmatrix}\mathbf{1}_{m\times m} & \mathbf{0}_{m\times n}\\ \mathbf{1}_{n\times m} & \text{LowerTri}(n)\end{bmatrix},\quad \text{where } n=m$$

- **左上块 $\mathbf{1}$**：视觉 token 之间双向注意力（ViT 式），保留 CLIP 式全局建模能力；
- **右上块 $\mathbf{0}$**：视觉 token 看不到 query（它们是被蒸馏的"原料"）；
- **左下块 $\mathbf{1}$**：每个 query 看得到**全部**视觉 token；
- **右下块 LowerTri**：query 之间因果注意力（decoder-only LLM 式）——**每个 query 只能基于"已看过的视觉信息 + 已排好的前序 query"决定自己要编码什么**，这就是 causal flow：重排是一个逐步的因果决策过程。

完整前向（论文 Eq. 2）：

$$\mathbf{O}=\mathcal{D}\left(\pi_{Q}\left(\mathcal{T}^{L}\left(\mathcal{E}(\mathbf{I})\oplus\mathbf{Q}_{0};\ M\right)\right)\right)$$

$\mathcal{E}$ 是 tokenizer（图 → m 个视觉 token），$\oplus$ 是序列拼接，$\mathcal{T}^L$ 是 L 层带掩码 Transformer，$\pi_Q$ 取**后 n 个 token**（只有 query 输出进 LLM），$\mathcal{D}$ 是 MoE decoder。

**重要负结果**：作者尝试过 mBART 式 encoder-decoder 的 cross-attention 方案（视觉 token 关在独立 encoder 里），**训练不收敛**。假设原因：视觉 token 与 query 的交互不足；prefix-concat 让视觉 token 在**所有层**保持活跃，才足以支撑信息交换。这个失败实验是架构选择的实证依据。

### 3.4 两级级联 1D 因果推理（论文的范式主张）

encoder（query 因果重排"阅读逻辑"）+ decoder（自回归"任务推理"）= 两个正交的 1D 因果推理子任务，可能是通向**真 2D 推理**的突破口——相对于"用位置编码硬编码 2D"的旧范式，因果排序的 query 自适应平滑的视觉语义，且天然对齐 LLM 的单向注意力。

### 3.5 训练管线（三阶段，160×A100-40G）

1. **Encoder 预训练**：tokenizer 从 V1 DeepEncoder 初始化，LM encoder 从 Qwen2-0.5B-base 初始化；接轻量 decoder 做 next-token prediction 联合训练；768/1024 双分辨率 dataloader；bs 640、40k iters、8K packing、lr 1e-4→1e-6（cosine），约 **100M 图文对**。
2. **Query enhancement**：接入 DeepSeek-3B-A500M 作最终 decoder；冻结 tokenizer，联合训练 LM encoder + LLM decoder；multi-crop 统一 dataloader；PP4 段（tokenizer PP0 / encoder PP1 / LLM 6+6 层 PP2-3）；GBS 1280、15k iters、5e-5→1e-6。
3. **Continue-training LLM**：冻结整个 DeepEncoder V2，只训 LLM——同 FLOPs 下数据吞吐翻倍，且让 LLM 适配"被重排过的"视觉 token 分布；20k iters、1e-6→5e-8。

数据与 V1 同源（OCR 80%），两处修改：OCR 1.0 按 text:formula:table = **3:1:1** 重平衡采样；layout 标签类别合并（如 figure caption/title 合一）。因此 V1 是干净的可比 baseline。

## 4. 实验与结果

### 4.1 主结果：OmniDocBench v1.5（1355 页、9 类、中英）

| 模型 | V-token^max | Overall↑ | TextED↓ | FormulaCDM↑ | TableTEDs↑ | R-orderED↓ |
|---|---|---|---|---|---|---|
| PaddleOCR-VL（pipeline 最强） | - | 92.86 | 0.035 | 91.22 | 90.89 | 0.043 |
| Qwen3-VL-235B | >6000 | 89.15 | 0.069 | 88.14 | 86.21 | 0.068 |
| DeepSeek-OCR（9-crops） | 1156 | 87.36 | 0.073 | 84.14 | 85.25 | 0.085 |
| **DeepSeek-OCR 2** | **1120** | **91.09** | **0.048** | **90.31** | **87.75** | **0.057** |

相对 V1：**+3.73 overall、FormulaCDM +6.17、阅读顺序 ED 0.085→0.057**——R-order 的显著改善直接验证了 causal flow 的设计目标（encoder 会按逻辑选排 token）。与闭源对标：同 1120 token 预算下 ED **0.100 vs Gemini-3 Pro 0.115**（Seed-1.8 用 5120 tokens 才到 0.106）——**压缩率最高且成绩最好**。

### 4.2 分文档类型（Table 3 的消融性观察）

9 类文档中 8 类全面提升（如 Note：text ED 0.145→0.068；彩色教材 0.130→0.053）；唯 **newspaper 的 text ED 0.139 反而略差于 V1 的 0.131**。两个归因：①token 上限 1120 对文字超密集的报纸不够（V1 Gundam-M 可到 1853）——未来加 local crops 数即可解；②报纸训练样本仅 250k，不足。**但 newspaper 的 R-order 仍优于 V1（0.176 vs 0.217）**——排序能力与识别容量是两个正交维度。

### 4.3 生产就绪度

无 GT 的生产环境用 repetition rate 度量：在线用户日志图像 6.25%→**4.17%**，PDF 预训练数据 3.69%→**2.88%**——逻辑性理解减少复读，且推理速度与 V1 持平（README：on-par speed）。

## 5. 局限与后续（论文自认 + 方向）

- **自认局限**：最难 IMO 级的复杂版式仍难（呼应 V1 newspaper 问题）；多 crop 上限是硬约束；泛化到通用视觉推理任务未验证。
- **Toward Genuine 2D Reasoning**（§6.1）：支持多次重审视（re-examination）与多跳重排（multi-hop reordering）可能需要**比原视觉 token 序列更长的 causal flow tokens**——即 query 数 >m 的过完备设计，这是下一步。
- **Toward Native Multimodality**（§6.2）：LM-style encoder 的更宏大愿景——**单一 encoder 共享 $W_k, W_v$、attention、FFN，仅靠模态专属 learnable queries 区分图像/音频/文本**，天然继承 LLM 社区的 MoE、高效注意力等基础设施优化。V1 的光学压缩 + V2 的 LM 式 encoder 被定位为通往 native multimodality 的两步。
- 相关脉络：Context Cascade Compression（2511.15244）在纯文本侧探索同类压缩极限；本架构与 Chameleon/Fuyu 的"LLM 直接多模态初始化"路线遥相呼应。

## 6. 与代码的对照（论文概念 → 本仓实现）

| 论文概念 | 本仓位置（DeepSeek-OCR2-master/） |
|---|---|
| 混合掩码 M（Eq. 1） | `DeepSeek-OCR2-vllm/deepencoderv2/qwen2_d2e.py`：`CustomQwen2Decoder`——`token_type_ids`（0=non-causal 视觉 / 1=causal query）+ `_create_custom_4d_mask`（`mask[image_positions[:,None], image_positions]=0.0` 双向、`mask[text_pos, text_positions[:i+1]]=0.0` 下三角），覆写 `_update_causal_mask` 注入 Qwen2Model |
| causal flow query（256/144） | 同文件 `Qwen2Decoder2Encoder`：`self.query_768 = nn.Embedding(144, hidden)`、`self.query_1024 = nn.Embedding(256, hidden)`——与论文 §3.2.3 数字逐字对应；另有注释掉的 `query_refixation`（重注视实验痕迹，对应 §6.1 的未来方向） |
| vision tokenizer（SAM+16× conv，896 维） | `deepencoderv2/sam_vary_sdpa.py`：与 V1 同源的 `ImageEncoderViT` + `net_2/net_3` conv 链 |
| π_Q（只取 query 输出）+ 整合 | `DeepSeek-OCR2-vllm/deepseek_ocr2.py`（582 行，vLLM 模型注册） |
| multi-crop [256,1120] | `process/image_process.py` + README "Support-Modes"：(0-6)×768²+1024² |
| 生产防重复 | `process/ngram_norepeat.py`（V1 NGram 机制的工程化） |
| 训练脚本入口 | `DeepSeek-OCR2-hf/run_dpsk_ocr2.py`（`model.infer(..., image_size=768, crop_mode=True)`） |

代码与论文的对应密度极高（query 维度、掩码语义、crop 预算三处硬编码数字可直接 grep 验证），是少见的"论文-代码零翻译损耗"仓。

## 7. 学习路径

1. **前置**：DeepSeek-OCR 精读（理解 16× 压缩与 token 预算体系）→ Qwen2 decoder-only 架构 → DETR object query / BLIP-2 Q-former（本文 related work 的"并行 query"两条线，注意它们是**双向** self-attention，本文的关键差异正是把 query 改成**因果**）。
2. **精读顺序**：§1 螺旋扫视例子 → Figure 1/5（掩码可视化）→ Eq. 1 掩码矩阵（全文数学核心，务必逐块理解四个子块的注意力语义）→ Table 1 主结果 → §6 两个 future work。
3. **复现建议**：3B-MoE 推理门槛与 V1 相同。最有信息量的实验是**对照掩码消融**：把 `qwen2_d2e.py` 的 `token_type_ids` 全置 0（退化成纯双向=Q-former 式）训/测对比，直接验证"因果性"本身的贡献；其次可改 `query_768` 的 144 为更大值，试探 §6.1 的过完备重排假说。
4. **延伸阅读**：Native multimodal encoder 路线（Chameleon、Fuyu、VALL-E）；DeepSeek-V3.2 的稀疏注意力（同代 DeepSeek 效率哲学）。

---

*写于 2026-09-05；一手来源 arXiv HTML v1 + 本仓代码实测 grep 验证。*
