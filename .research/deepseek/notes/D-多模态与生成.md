# D · 多模态与生成：DeepSeek-VL / VL2 / Janus(Pro/Flow) / DreamCraft3D / DeepSeek-OCR / DeepSeek-OCR-2

> 研究型代码考古笔记 · 六仓深读。基础目录：`C:\workspace\work4ai\.tools\deepseek-repos\`
> 纪律：所有数字均来自实际读到的仓库文件（源码 `文件:行号` 或仓内 PDF 论文）；论文级但仓库未含代码的结论单独标注。仓库文件未做任何修改。

---

## 1. DeepSeek-VL（2024-03）——混合视觉编码的开源起点

**定位一句话**：面向真实世界视觉语言理解（图表/网页/公式/文献/具身）的 dense VL 模型，首创 SAM(高分辨率感知) + SigLIP(低分辨率语义) 双塔混合编码。

### 核心机制（代码证据）

- **混合视觉塔** `deepseek_vl/models/clip_encoder.py:126` `HybridVisionTower`：
  - 高分辨率塔：SAM-B 变体 `sam_b_downsample`（`sam.py:529`，width 768 / 12 层 / 12 头 / patch 16 / window attention 窗口 14，全局注意力层索引 [2,5,8,11]），输入 1024×1024；neck 输出 256 通道，`F.interpolate` 到 96×96（`sam.py:181-183`），再过 2 个 stride-2 卷积（downsample_channels=(512,1024)，`sam.py:534`）→ 24×24×1024 = **576 token**。
  - `sam_hd` 分支（`sam.py:161-196`）：取第一个全局注意力块特征过 `neck_hd`（deepcopy）+ 同样插值下采样，以**零初始化可学习标量** `hd_alpha_downsamples` 门控加回主特征——保守的残差注入。
  - 低分辨率塔：`siglip_large_patch16_384`，384×384 → 24×24 = **576 token**，1024 维。
- **冻结策略**（`clip_encoder.py:146-161`）：两塔默认全冻结；即使 `freeze_high=False` 也**只放开 SAM 的 `downsamples` 和 `neck` 参数**（`clip_encoder.py:153`）——预训练 backbone 不动，只训"适配解剖结构"。
- **投影器** `projector.py:47` `low_high_hybrid_split_mlp_gelu`：高/低两路各 `nn.Linear(input_dim, n_embed//2)`，concat 后接 GELU+MLP（depth 2）——两塔信息在通道维拼接而非序列维。
- **图像 token 布局**：`processing_vlm.py:89` `num_image_tokens=576`；`add_image_token`（`processing_vlm.py:215-219`）把每个 `<image_placeholder>` 展开成 576 个 image token，由 `modeling_vlm.py:158-162` 用视觉 embedding 原位替换。
- **语言底座**：`modeling_vlm.py:123` 直接 `LlamaForCausalLM`（DeepSeek-LLM 1.3B/7B）；模型 4096 上下文（README 表格）。
- **训练时 tiling（论文级，arXiv 2403.05525，仓库推理代码不含）**：训练数据层面把图切成 384×384 tile，**约 85% tile 走 SAM 高分辨率路、全局缩略图 + 约 15% tile 走 SigLIP 低分辨率路**。仓库内推理只做"长边缩放到 image_size + expand2square 补边"（`image_processing_vlm.py:127-162`），tiling 属训练管线（未开源）。

### 训练细节
仓库为纯推理仓库（inference.py / cli_chat.py / Gradio serve），无训练脚本。模型族：1.3B/7B × base/chat，2024-03-11 发布。

### 工程亮点
- HF `trust_remote_code` 自定义 `MultiModalityCausalLM` + `AutoConfig.register`（`modeling_vlm.py:167-170`）；processor 继承 `ProcessorMixin`，对话模板走 `deepseek_vl/utils/conversation.py` 的 conv template 体系。
- Gradio demo（`deepseek_vl/serve/app_deepseek.py`）与 HF Space 同构；Makefile + pre-commit + flake8/pylint 全套。

### 演进关系
- → VL2：放弃"双塔各 576 token"（序列翻倍昂贵），改单 SigLIP + 动态 tiling；SAM 线在 OCR 系列复活（DeepEncoder 的感知前半）。
- → Janus：SigLIP-L-384 这颗理解编码器被原样复用为"理解路"。

### work4ai 输入
- **讲透多模态**：混合编码（感知 SAM vs 语义 SigLIP）是"视觉编码器分工"叙事第一幕；576 token、96×96→24×24 等具体数字可做直觉锚点。
- **讲透CV**：SAM ViTDet 结构（window attention + 4 个全局层 + 相对位置编码）的"改造为通用 backbone"案例。
- **用例库**：冻结策略只放 neck/downsamples——"预训练权重 + 新解剖层"模式卡。

---

## 2. DeepSeek-VL2（2024-12）——MoE + 动态 tiling

**定位一句话**：把 LLM 底座换成 DeepSeekMoE（MLA）的 VL 系列（Tiny/Small/大 = 1.0B/2.8B/4.5B 激活参数），用**单 SigLIP-SO400M-384 + 动态 tiling** 替代 VL1 双塔。

### 核心机制（代码证据）

- **动态 tiling**（`deepseek_vl2/models/processing_deepseek_vl_v2.py`）：
  - `select_best_resolution`（:34-52）：在候选分辨率中最大化有效分辨率、最小化浪费面积。候选集（论文 Table/正文）：`(m·384, n·384), 1≤m,n, mn≤9`。
  - `tokenize_with_images`（:523-597）：全局视图 pad 到 384×384；局部视图 pad 到 best 分辨率后按 384×384 切 tile；**当图片数 >2 时关闭裁剪**（:273、:430 `cropping=len(images)<=2`，控制序列长度）。
  - token 数（:568-574）：`h=w=ceil((384/16)/downsample_ratio)`，downsample_ratio=2（`modeling_deepseek_vl_v2.py:173`）→ 每 tile 12×12=144 有效 token；布局 = 全局 12×(12+1) + 1 个 view_separator + 局部 (th·12)×(tw·12+1)。论文口径：SigLIP-SO400M 每 tile 输出 27×27=729 个 1152 维 embedding，2×2 pixel-unfold 压到 14×14=196（全局 14×15=210 + 1 + m·14×(n·14+1)）。
- **投影器**（`modeling_deepseek_vl_v2.py:56-65` `downsample_mlp_gelu`）：2×2 unfold 拼接（input_dim×4）→ Linear 到 n_embed×mlp_ratio → … → n_embed；另有 `token_pooling` 变体（:70-91，unfold+Linear(4·input_dim→input_dim)）。
- **tile 结构化 token**（`modeling_deepseek_vl_v2.py:314-330`）：`tile_tag="2D"` 时学习 `image_newline`（行尾）与 `view_seperator`（全局/局部分隔）两个可学习向量；全局/局部特征按 2D 网格重排插行（:410-454）——**空间结构以"换行符"形式保留在 1D 序列里**。
- **视觉编码器**：仅 SigLIP（`modeling_deepseek_vl_v2.py:118-123`：siglip_large_patch16_384, width 1024, 24 层, 16 头, 无 class token）；论文确认为 **SigLIP-SO400M**。
- **语言底座**：`DeepseekV2ForCausalLM`（MLA + MoE，`modeling_deepseek_vl_v2.py:334`）。论文 Table 1：Tiny=3B(激活0.57B, 12层, embed 1280, **MHA 而非 MLA**, 64 路由+2 共享, top-6, softmax 路由)；Small=16B(激活2.4B, 27层, MLA rank 512, 64+2)；大=27B(激活4.1B, 30层, 72+2, **sigmoid 路由 + 专家偏置修正**)。

### 训练细节（仓内 PDF `DeepSeek_VL2_paper.pdf` §4，已抽文本核对）
- **三阶段**：① 对齐（训视觉编码器+adaptor，**LLM 冻结**，ShareGPT4V 1.2M caption/对话）；② VL 预训练（全解锁，**~800B token**，VL:文本≈70:30）；③ SFT（全解锁，~19.5-20B token，混入 DeepSeek-V2 纯文本对话数据）。
- 超参（Table 2）：LR Tiny 5.4e-?/…/3.0e-?（PDF 提取损坏，量级 1e-4/1e-5/1e-5 级），**视觉编码器 LR ×0.1**；batch 256/2304(大模型 3360)/64；序列 4096；AdamW β=(0.9,0.95)；aux loss 权重 0.001（大模型 1e-4 且开专家偏置修正）；阶段 2/3 开序列打包与流水线并行。
- 工程段落（§4.2）：视觉编码器在流水线第一段需**细粒度切层**做负载均衡；动态分辨率导致 tile 数不均，做 **tile 跨 DP rank 负载均衡**——多模态 MoE 训练的独有工程痛点。

### 工程亮点
- **incremental_prefilling**（`modeling_deepseek_vl_v2.py:480-557`）：prefill 按 chunk（如 512）切块，past_key_values 在 CPU/GPU 间换入换出（`_move_past_key_values_to_cpu/gpu`），40GB 卡跑 vl2-small——KV cache 异构内存管理的教学级实现。
- 视觉 grounding 专用 5 个特殊 token（`processing_deepseek_vl_v2.py:180`：`<|ref|> <|/ref|> <|det|> <|/det|> <|grounding|>`），bbox 直接以 `[[x1,y1,x2,y2]]` 文本输出（README 示例输出）。
- MoE 总参/激活参在 README 注释里成对出现：tiny 3.37B 总/1B 激活、small 16.1B/2.4B、大 27.5B/4.2B。

### 演进关系
- VL→VL2：**dense→MoE、双塔静态 1024²→单塔动态 tiling、序列拼接→pixel-unfold 4 合 1 压缩**；理解编码器统一到 SigLIP 一颗。
- VL2 是 Janus 理解路（SigLIP-L-384+MLP）与 OCR 数据配方的上游母体（OCR 论文明确"Following DeepSeek-VL2"造通用视觉数据）。

### work4ai 输入
- **讲透多模态**：动态 tiling + newline/view_separator 是"分辨率与序列经济的平衡术"核心案例；70:30 VL/文本配比、视觉 LR×0.1 是训练配方锚点。
- **讲透模型 / MoE 相关**：同系列三档 MoE 配置（softmax vs sigmoid 路由、专家偏置修正只在最大档开）是 MoE 课程设计的天然实验组。
- **讲透KV Cache**：incremental_prefilling 的 CPU offload 是 KV cache 章节的推理侧配对案例。
- **用例库**：HF 自定义类 + vLLM 迁移路径（见 OCR 仓复用 `DeepseekVLV2Config`）。

---

## 3. Janus / Janus-Pro / JanusFlow——理解与生成的"解耦双路"

**定位一句话**：单一自回归 transformer 统一多模态理解与生成，关键创新是**视觉编码解耦**——理解用 SigLIP 连续特征、生成用 VQ 离散 token，两路各自适配器进 LLM。

### 核心机制（代码证据）

- **五件套架构** `janus/models/modeling_vlm.py:190-219`：
  - `vision_model` = CLIPVisionTower(SigLIP-L-384)（理解路，576 token 连续特征）+ `aligner`（两层 MLP）
  - `gen_vision_model` = VQ tokenizer（生成路解码器）+ `gen_aligner`（两层 MLP，码本 embedding→LLM 空间）+ `gen_head`（`vision_head`，:36-51，Linear(n_embed→image_token_embed)→GELU→Linear(→image_token_size) 即码本 logits）+ `gen_embed`（:214，`nn.Embedding(16384, n_embed)` 码本查表）
- **VQ tokenizer** `janus/models/vq_model.py:31-44`（LlamaGen 系）：`codebook_size=16384`、`codebook_embed_dim=8`、l2_norm 码本、commit_loss β=0.25、encoder/decoder `ch_mult=[1,1,2,2,4]` → **下采样 16×**（4 次 stride-2）；z_channels=256，quant_conv 256→8。VectorQuantizer（:240-282）标准直通估计器 + 可选熵损失（`compute_entropy_loss` :450-463）。
- **生成流程**（README `generate()`，Janus-Pro 段）：384×384 图 → 576 个离散 token 逐个自回归采样；**CFG=5、temperature=1、parallel_size=16**（一批出 16 图，条件/无条件按 2N 交错，`logits = logit_uncond + cfg_weight*(logit_cond-logit_uncond)`）；生成 token 经 `gen_vision_model.decode_code(generated_tokens, shape=[N,8,24,24])` 解码。
- **理解流程**：与 VL 同构（SigLIP→576 token→aligner→LLM），对话模板 `<|User|>/<|Assistant|>`。

### Janus-Pro（仓内 `janus_pro_tech_report.pdf`，已抽文本核对）
- 架构不变，升级三点：训练策略 / 数据 / 规模（1B+7B；7B=embed 4096、32 头、30 层；LLM 底座 DeepSeek-LLM 1.5B/7B，词表 100K）。
- **训练策略修正**：旧版 stage II 按 PixArt 方式把 66.67% 文生图步数耗在 ImageNet 类别名生图上；Pro 改为 **stage I 拉长训练吃透 ImageNet（LLM 冻结即可学像素依赖），stage II 全部换成正常密集描述文生图数据**；SFT 数据配比从"多模态:纯文本:文生图=7:3:10"改为 **5:1:4**。
- **数据**：理解侧参照 VL2 加 ~90M 样本（YFCC、Docmatix 等）；生成侧加 **~72M 合成美学数据，真实:合成=1:1**——合成数据收敛更快、短 prompt 更稳。
- 超参（Table 2）：三阶段 LR 1e-?/1e-?/4e-?（常数调度，量级 1e-4/1e-4/1e-5 级），steps 20K/360K(早停在 270K)/80K(7B 40K)，batch 256/512/128；1.5B/7B 分别 16/32 节点 × 8×A100-40G 训 9/14 天；图像统一 384×384（理解 pad 短边 RGB(127,127,127)，生成裁长边）；序列打包训练。
- 成绩锚点：GenEval 0.80（Janus 0.61、DALL-E 3 0.67、SD3-M 0.74）；MMBench 79.2。

### JanusFlow（同仓 `janus/janusflow/`）
- 理解路同 SigLIP；生成路改为 **rectified flow**：SDXL-VAE（`stabilityai/sdxl-vae`）latent **4×48×48**，ODE 30 步，CFG 5.0；解码器为 UViT（`janus/janusflow/models/uvit.py`，ImageHead/Downsample2D/ConvNextBlock/Patchify 等组件）。第二分支证明"解耦哲学与生成头形态正交"（VQ 自回归 vs 连续流匹配都行）。

### 工程亮点
- 2024-10-20 修复 `tokenizer_config.json` bug——CFG 曾因配置失效导致生成质量虚低（README News，工程诚实度样本）。
- demo/ 目录四套 Gradio/FastAPI app（janus / janusflow / januspro 分开）。

### 演进关系
- 与 DreamCraft3D 构成"统一理解生成"的两条路线：**Janus 在 token 层解耦（一颗 LLM 双路输入）**，DreamCraft3D 在**流程层分层（几何→纹理，扩散先验自举）**。
- 理解路直接继承 VL；JanusFlow 是通往连续 latent 生成的过渡实验。

### work4ai 输入
- **讲透多模态**：「编码器解耦 vs 统一」辩论的核心正方证据；576/16384/16× 三个数字构成生成路完整骨架。
- **讲透生成模型**：VQ tokenizer（LlamaGen 式）+ AR 采样 + CFG 的最小完整实现；JanusFlow 提供同架构下 rectified flow 对照组。
- **讲透模型宇宙 / 模型**：`vision_head`/`gen_embed` 展示"LLM 词表旁挂一个 16384 码本表"的统一建模技巧。

---

## 4. DreamCraft3D（ICLR 2024）——分层 3D 生成与自举扩散先验

**定位一句话**：以单张参考图驱动"几何雕刻→纹理增强"两阶段的 3D 内容生成，核心是 **Bootstrapped Score Distillation（BSD）**——用当前 3D 场景的增广渲染微调场景专属 2D 扩散模型（DreamBooth），再用它蒸馏出视角一致的纹理指导，扩散先验与 3D 表征交替互促。

### 核心机制（代码证据）

- **三阶段训练流**（README Quickstart，四份 config 串联）：
  1. coarse：NeRF（`dreamcraft3d-coarse-nerf.yaml`，implicit-volume，Magic3D 式密度初始化 blob_magic3d，分辨率 128→384 @3000 步）→ NeuS 精修；
  2. geometry（`dreamcraft3d-geometry.yaml`）：转 tetrahedra-SDF 网格，**DeepFloyd/IF-I-XL-v1.0 做 2D guidance（guidance_scale 20）+ stable-zero123 做 3D guidance（guidance_scale 5.0）**，法线/RGB 交替渲染（`dreamcraft3d.py:359-360` `render_type = "rgb" if step % n_rgb == 0 else "normal"`），max_steps 5000，lambda_sd 0.1 / lambda_3d_sd 0.1；
  3. texture（`dreamcraft3d-texture.yaml`）：**冻结几何**（`fix_geometry: true`，:59），1024×1024 渲染，SD-2-1-base BSD guidance，max_steps 5000。
- **BSD = stable_diffusion_bsd_guidance.py 的三损失交替**：
  - `compute_grad_vsd`（:680-766）：`grad = w(t)·(ε_pretrainCFG − ε_lora)`——用**场景专属 LoRA 微调版**与预训练版两个扩散模型的噪声预测差作梯度（VSD 的个性化变体），w=(1−ᾱt)。
  - `train_lora`（:896-939）：对当前渲染 latent 加噪、以 10% 概率做 CFG dropout（:925-926），MSE 训练 `train_unet_lora` ——**在线 DreamBooth**：3D 场景每一步的渲染都在喂养自己的扩散先验。
  - `train_pretrain`（:941-1014）：用**固定 pipe 采样的参考图帧缓存**（cache_frames 最多 10 帧，:975-976）加噪重建，训 `train_unet`（基础模型分支，保持通用先验不漂移）。
  - 交替调度（`forward` :1079-1092 + `dreamcraft3d.py:344-357`）：`only_pretrain_step=1000` 内每 1000 步抽前 1/5 步专训 pretrain；`ref_or_guidance="alternate"`、`n_ref=2` ——每 2 步 1 步参考图监督（lambda_rgb 1000 / lambda_mask 100）、1 步扩散蒸馏（lambda_sd 0.01）；同时每步都带 `loss_lora`(λ0.1)。另有 `compute_grad_vsd_hifa`（:768-894，HiFA 式多步去噪目标）与 `compute_grad_du`（:593，可选感知损失）实验分支。
  - texture config 权重（:123-137）：lambda_sd 0.01、lambda_lora 0.1、lambda_pretrain 0.1、lambda_rgb 1000、lambda_mask 100；UNet lr 1e-5（:149-152）。
- **防"双面人"(Janus problem)**：README 提供可选路径——Zero123++ 生成多视图 → DeepFloyd-IF DreamBooth LoRA（`train_dreambooth_lora.py`，lr 5e-6、1200 步、resolution 64）替换 guidance。
- 预处理：`preprocess_image.py` 用 Omnidata 出深度/法线、去背景（--recenter）。

### 工程亮点
- 基于 threestudio 框架的 system/guidance/data 三层插件化（guidance 目录 11 种：sd/vsd/bsd/controlnet/zero123/deepfloyd…），配置驱动（OmegaConf），launch.py 统一入口——**SDS 变体动物园**，最适合做"损失函数实验平台"的教学仓库。
- 显存工程：xformers、gradient checkpointing、CPU offload、attention slicing 四开关齐备（:129-153）。

### 演进关系
- 与 Janus 是"统一"的两条路线：DreamCraft3D 不追求单模型统一，而是**管线解耦 + 先验自举**（2D↔3D 交替优化）；2024-10 官方升级 DreamCraft3D++（外部链接，仓库未含）。
- SDS 家族谱系在此仓可完整比对：SDS（stable_diffusion_guidance.py:209）→ SJC(:302) → VSD（vsd_guidance.py:622）→ **BSD**（本文）→ HiFA 变体。

### work4ai 输入
- **讲透生成模型**：SDS→VSD→BSD 的损失演化主叙事素材；`ε_pretrain − ε_lora` 差分梯度的直觉解释（"先验差 = 场景该补的细节"）。
- **讲透视频 / 三维**：score distillation 作为"用 2D 先验监督 3D/视频表征"的通用机制案例（NeRF/NeuS→SDF 网格的课程也是 3D 表示课程）。
- **用例库**：交替优化（alternate）调度、参考帧缓存（cache_frames≤10）等训练工程模式卡。

---

## 5. DeepSeek-OCR（2025-10）——Contexts Optical Compression

**定位一句话**：以"视觉-文本压缩比边界"为研究纲领的 OCR 专用 VLM：自研 **DeepEncoder**（SAM 感知 + 16× 压缩器 + CLIP 知识）串联，接 DeepSeek-3B-MoE(A570M) 解码器，探索"一张图压进几十~几百 vision token 还能解码出多少文字"。

### 核心机制（代码 + 仓内 PDF 双证据）

- **DeepEncoder**（论文 §3.2 + `DeepSeek-OCR-master/DeepSeek-OCR-vllm/deepseek_ocr.py:288-292`）：
  - 前半：SAM-base patch16（80M，window attention 为主，`sam_vary_sdpa.py`）；1024×1024 → 4096 patch token。
  - 中间：**2 层卷积 16× 压缩**（kernel 3/stride 2/pad 1，通道 256→1024，Vary 式）→ 256 token。
  - 后半：CLIP-large（300M，`clip_sdpa.py`：hidden 1024、patch 14、16 头，**去掉第一层 patch embedding**——输入已是 token）；项目器 `nn.Linear(2048→1280)`（`deepseek_ocr.py:291-292`）进 LLM。
  - 合计 ~380M 编码器；解码器 3B-MoE、64 路由 top-6 + 2 共享、激活 ~570M、12 层（PP2/PP3 各 6 层）。
- **五档分辨率模式**（README + 论文 Table 1）：Tiny 512²(64 token)/Small 640²(100)/Base 1024²(256)/Large 1280²(400)/**Gundam 动态 = n×640² 局部 + 1×1024² 全局 = n×100+256 token，n∈[2,9]**；Gundam-M(1024²局部+1280²全局)由训好的模型续训 6M 样本得到（超大分辨率与其它模式混训会拖慢整体，故分开）。
- **动态裁剪实现**（`process/image_process.py:28-83`）：`dynamic_preprocess` 按长宽比在 min 2~max 6（config.py:11-12，最大可 9）个 640² tile 里选最接近的比例裁切；token 布局（:424-432）：全局 16×17+1、局部 (10·W)×(10·H)。有效 token 公式（论文式 1）：`N_valid = N_actual × [1−(max(w,h)−min(w,h))/max(w,h)]`（padding 部分无效）。
- **压缩比边界**（论文 Table 2，Fox 英文文档 100 页实测）：**≤10× 压缩 → 解码精度 ~97%；~20× → ~60%**。100 token（Small）下 600-1300 token 文档压缩 6.7×~12.6×、精度 98.5%→87.1%。OmniDocBench：Gundam ~795 token 超 MinerU2.0（近 7000 token）；报纸类（文本 4-5K token）必须 Gundam-M。
- **防重复生成**：`ngram_norepeat.py` `NoRepeatNGramLogitsProcessor(ngram_size, window_size, whitelist={<td>,</td>})`——表格 token 白名单豁免（`run_dpsk_ocr_image.py:162`：ngram 30/window 90）。
- **诚实边界**：用户任务书提到的 `max_output_window` 与"背景/段落/行/词"裁剪粒度启发式，**在 GitHub 仓库代码中不存在**（全仓 grep 无 `output_window`）；它们位于 HuggingFace 模型仓的 `trust_remote_code` 远程 modeling 代码（`model.infer(..., test_compress=True)` 的实现在远端），本次未读到，不展开。
- **远期设想**（论文 §5 Discussion）：多轮对话超过 k 轮的历史**渲染成图**做光学压缩、旧图逐级降分辨率——模拟人类遗忘曲线（"近清晰远模糊"）的 token 经济学。

### 训练细节（论文 §3.4-3.5）
- 数据：30M PDF 页（~100 语言；中英 25M）粗标注 + 2M+2M 中英精细标注（PP-DocLayout/MinerU/GOT-OCR2.0 标注 + 小语种"模型飞轮"600K）；3M Word；场景 OCR 10M+10M（LAION/悟空 + PaddleOCR 标）；OCR2.0：图表 10M（pyecharts/matplotlib 渲染→HTML 表格）、化学式 5M（PubChem SMILES+RDKit）、平面几何 1M（Slow Perception，感知尺 4）；通用视觉 20%、纯文本 10%（8192 长）。配比 **OCR 70% : 通用视觉 20% : 文本 10%**。
- 两阶段：① 只训 DeepEncoder（配轻量解码器，LAION 采样 100M 通用，2 epoch，batch 1280，lr 5e-5 cosine，seq 4096）；② 全模型（PP=4：SAM+压缩器在 PP0 **冻结**，CLIP 在 PP1 **解冻**，LLM 6+6 层在 PP2/3；20 节点×8×A100-40G，DP=40，全局 batch 640，lr 3e-5 step 调度；吞吐：纯文本 90B token/天、多模态 70B/天）。

### 工程亮点
- vLLM 官方合入（2025-10-23，`vllm.model_executor.models.deepseek_ocr.NGramPerReqLogitsProcessor`）；本地 vllm-0.8.5 兼容层 + HF transformers 双路径；单 A100-40G PDF 并发 ~2500 token/s（README）。
- config.py 单文件切换五档模式；ngram 白名单 token id（128821/128822）硬编码进 README 示例。

### 演进关系
- 视觉血统：VL1 的 SAM 线（window attention 感知）+ VL2 的 token 布局（2D newline/separator、`DeepseekVLV2Config` 直接被 vLLM 侧复用，`deepseek_ocr.py:270`）+ Vary/GOT 的压缩卷积。
- → OCR-2：压缩范式（"把图压小"）转向因果范式（"把图读对"）。

### work4ai 输入
- **讲透多模态**：vision token 经济学的定量边界（10×/97%、20×/60%）是全部"token 压缩/Qwen2-VL 式动态分辨率"讨论的锚点数字。
- **讲透LLM / 长上下文**：光学压缩=另一种 context compression；遗忘曲线类比（时间→距离→分辨率三个衰减轴）可直接进"长上下文与记忆"章节。
- **讲透模型宇宙**：DeepSeek-3B-MoE（A570M）作为"领域专用 VLM 用小激活 MoE"的家族证据。

---

## 6. DeepSeek-OCR-2（2026-01/02）——Visual Causal Flow

**定位一句话**：把 OCR 的 CLIP 知识塔换成 **Qwen2-0.5B 改造的"LM 式视觉编码器"**——视觉 token 双向注意力 + 等量"因果流查询"token 三角注意力，让编码器**按语义重排视觉 token**（模拟人眼因果阅读流），仅查询输出进 LLM。

### 核心机制（代码 + 仓内 PDF 双证据）

- **DeepEncoder V2**（`deepencoderv2/qwen2_d2e.py` + 论文 §3.2）：
  - 前端不变：SAM-base(80M) + 2 卷积 16× 压缩；最后一卷积通道 **1024→896**（对齐 Qwen2 hidden，论文 §3.2.1）。
  - `Qwen2Decoder2Encoder`（:217-284）：`build_qwen2_decoder_as_encoder(decoder_layer=24, hidden=896, heads=14, kv_heads=2, intermediate=4864)`（:287-292）——**GQA 的 Qwen2 结构**；`query_768 = nn.Embedding(144, 896)`、`query_1024 = nn.Embedding(256, 896)`（:247-248）两套固定查询。
  - **双流注意力掩码**（`_create_custom_4d_mask` :135-172）：前段视觉 token `token_type_ids=0`（互看=ViT 式双向），后段查询 `=1`（看全部视觉 + 只看之前的查询=LLM 式因果三角）；拼接 `[visual_tokens; queries]`（:270-275），输出**只取后半查询** `y[:, n_query:, :]`（:281）。查询与视觉 token **等基数**（论文：留冗余给"再注视"re-fixation）。
  - 论文负面证据：mBART 式 cross-attention 编解码结构**不收敛**——prefix 拼接让视觉 token 全程参与每层，是与 Q-former 的本质差别。
- **模式**（README + `config.py:2-6`）：全局 1024²=256 查询 + k×768² 局部=144×k 查询，k∈[0,6] → **token ∈ [256, 1120]**（1120 对齐 Gemini-3-Pro 视觉 token 上限；低于 OCR-1 Gundam 的 1156）。max_crops=6。
- **两段级联因果**（论文 §3.2.2）：编码器做"阅读逻辑因果"（重排），LLM 解码器做"任务因果"（自回归）——**用两个 1D 因果结构级联逼近 2D 推理**的宣言。
- **成果**（论文 Table 1-4，OmniDocBench v1.5，1355 页 9 类中英文档）：Overall 91.09 vs OCR-1 87.36（+3.73%，同源数据）；阅读顺序 ED 0.085→**0.057**（因果重排的直接证据）；同 token 预算 1120 下 Overall ED 0.100 优于 Gemini-3 Pro 0.115；生产指标重复率：用户图 6.25%→4.17%、PDF 3.69%→2.88%。弱项：报纸（text ED 0.139，token 上限低 + 训练数据仅 250K 样本）。

### 训练细节（论文 §4.2，三阶段）
1. 编码器预训练：tokenizer 从 DeepEncoder 初始化、LM 编码器从 **Qwen2-0.5B-base** 初始化；配轻量解码器 LM 目标；双 dataloader 768²/1024²；lr 1e-4→1e-6 cosine，160×A100，batch 640，40K iter（8K 打包，~100M 图文对）。
2. 查询增强：接 DeepSeek-3B-A500M 组全管线；**冻结 SAM-conv tokenizer**，LM 编码器+LLM 联训；multi-crop 统一 dataloader；PP=4（tokenizer PP0 / LM 编码器 PP1 / LLM 6+6 层 PP2-3）；40 DP × 4 GPU，全局 batch 1280，lr 5e-5→1e-6，15K iter。
3. LLM 续训：**编码器全冻结只训 LLM**——同 batch 吞吐翻倍以上，lr 1e-6→5e-8，20K iter。
- 数据：同 OCR-1 源，OCR 占 80%；改动=OCR1.0 按 文本:公式:表格=3:1:1 重采样 + 版面类别合并（figure caption/title 合并）。

### 工程亮点
- 改造 HF Qwen2 只需子类化 `Qwen2Model` 重写 `_update_causal_mask`（:104-133）——**复用 LLM 全套基础设施（GQA/权重/优化器）做视觉编码**的示范；注意只支持 sdpa/eager，不支持 flash_attention_2（:36-37）。
- 推理栈与 OCR-1 完全同构（vllm-0.8.5 + HF 双路径），PDF 吞吐与 OCR-1 持平（README）。

### 演进关系
- OCR→OCR-2：从"压缩视角"（单位面积塞多少语义）到"因果视角"（token 顺序本身携带推理）；SAM 感知前端与 MoE 解码器冻结不动，**只换知识塔**——对照组干净的消融。
- 远期（论文 §6）：统一 omni 编码器（共享 Wk/Wv/FFN，模态专属查询 embedding）；更长的因果流 token 支持多跳重排。

### work4ai 输入
- **讲透多模态 / 讲透CV**："LM as Vision Encoder"是编码器架构叙事的最新一幕（CLIP→SigLIP→混合→LM 式）；双向+因果双流掩码是 attention mask 章节的进阶案例。
- **讲透Transformer**：`_create_custom_4d_mask` 是"掩码即架构"（mask-as-architecture）的教科书实现。
- **讲透生成模型 / 模型宇宙**：与 Janus 对照——"LLM 吃离散视觉 token"vs"LLM 结构当编码器"，DeepSeek 在两端的押注。
- **用例库**：HAI-LLM PP=4 的视觉-语言切分策略（tokenizer/编码器/解码器分段冻结分段解冻）工程卡。

---

## 7. 六仓纵向综合：DeepSeek 多模态的「编码器解耦/统一」设计哲学

**主线：视觉编码器从未定型，但它永远是第一创新位。**

1. **四个代际、四种编码器形态**：
   - VL(2024-03)：**并行双塔**（SAM 感知 + SigLIP 语义，576+576 token 并列）——功能解耦；
   - VL2(2024-12)：**单塔+动态 tiling**（SigLIP-SO400M，序列内 2D 结构 token）——效率统一；
   - Janus(2024-10/2025-01)：**任务解耦双路**（SigLIP 理解路 + VQ 码本生成路，共用一颗 LLM）——"解耦在编码器内部，统一在 transformer 主体"；
   - OCR→OCR2(2025-10→2026-01)：**串联再造**（SAM 感知 →16×压缩→ CLIP 知识 → Qwen2 因果重排）——把"知识压缩"从 CLIP 预训练继承转为 LLM 架构内生。
2. **解耦的三个正交轴**：功能轴（感知/语义，VL）、任务轴（理解/生成，Janus）、时序轴（双向/因果，OCR2）。DeepSeek 每代只动一个轴，控制变量式的家族演进——这本身就是"讲透"级方法论。
3. **token 经济学是贯穿性约束**：576(VL) → 144/tile+动态(VL2) → 64~400~1120 五档(OCR) → [256,1120] 固定查询(OCR2)；Janus 生成路 576 离散 token。所有设计都在回答同一个问题：**每张图该花多少 token、按什么顺序花**。OCR 的 10×/97%、20×/60% 给出了经验边界，OCR2 进一步证明"顺序（因果流）比数量更值钱"（同预算 ED 0.115→0.100）。
4. **冻结/解冻的家族直觉**：预训练 backbone 永远先冻着用（VL 只放 neck/downsamples；OCR 把 SAM+压缩器放 PP0 冻结、CLIP 解冻当"输入嵌入层"训；OCR2 三阶段逐级解冻再逐级回冻）；"新能力=新解剖层+旧权重"贯穿始终。VL2 的"视觉 LR×0.1"是同一哲学的软化版。
5. **MoE 复用是家族习惯**：VL2 三档 MoE（0.57B/2.4B/4.1B 激活）、OCR/OCR2 共用 DeepSeek-3B-MoE(A570M)——**领域 VLM 用小激活 MoE 换"3B 表达力 + 500M 推理成本"**，是 DeepSeekMoE 资产的多模态复利。
6. **两条"统一理解生成"路线的分岔**：Janus 相信**表征层统一**（一颗 AR transformer，输入端双编码）；DreamCraft3D 相信**过程层自举**（几何→纹理分层，2D 先验与 3D 表征交替进化，BSD=`ε_pretrain−ε_lora` 差分梯度）。前者是模型统一，后者是系统统一；JanusFlow（rectified flow in LLM）与 OCR2（LM as encoder）分别在两端继续外推。
7. **给 work4ai 的元洞察**：六仓合起来是一份"多模态架构搜索的实验日志"——每代都有明确的反面证据（VL1 双塔序列贵、Janus 旧版 ImageNet 配比低效、OCR 报纸 250K 数据不够、OCR2 cross-attention 不收敛）。**失败原因驱动下一代设计**，这条"负结果链"比成功指标更有教学价值。

---

## 附：本次未读到/不确定项（诚实清单）
- DeepSeek-VL "85% tile"：论文级结论（arXiv 2403.05525），训练管线代码未开源，仓库内无对应实现可核对精确比例。
- VL2 论文 PDF 部分 LR 数字上标在文本提取中损坏（仅量级可辨）。
- DeepSeek-OCR 的 `max_output_window` 与背景/段落/行/词裁剪粒度：位于 HuggingFace 模型仓远程代码，GitHub 仓无，未读。
- DreamCraft3D++ 仅有项目页链接，仓库未含代码。
- 各仓 HF config.json（如 VL2 candidate_resolutions 实际值、Janus image_token_size）未下载权重核对，以代码默认值+论文为准。
