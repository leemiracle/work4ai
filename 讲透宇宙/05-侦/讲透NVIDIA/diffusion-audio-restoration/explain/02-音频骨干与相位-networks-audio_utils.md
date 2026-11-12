# 02 · 音频骨干与相位表示：networks.py + audio_utils.py + transforms

## 角色定位

本篇覆盖"音频如何变成张量、张量如何被网络消化"两层。audio_transforms/transforms.py 与 audio_utils.py 负责表示层（波形↔谱图↔网络通道），networks.py 的 AttnUNetF 负责感知层。理解本篇的关键张力：**论文宣称的 SO(2) 旋转矩阵相位表示，与管线实际使用的 3 通道瞬时相位表示，是并存的两套系统，当前 HEAD 只有后者在跑**。

## 内部结构

**表示层（生效通路）**。四步链：`ComplexSpectrogram`（audio_transforms/transforms.py:83）做 STFT（torch.stft + Hann 窗）并 view_as_real 得 2×H×W；`ComplexToMagInstPhase`（transforms.py:108-119）输出 3×H×W——通道为 [幅度, cos θ, sin θ]，θ=atan2(虚部,实部)；`SpectrogramDropDCTerm`（transforms.py:214）摘掉 DC 频点让 H 成为 2 的幂（配合卷积下采样）；`PowerScaleSpectrogram`（transforms.py:187-207，配置 power=4）压缩幅度动态范围——音乐谱图高低频能量差可达数量级，四次幂后网络更好学。逆链 `MagInstPhaseToComplex`（transforms.py:121-132）→ `SpectrogramAddDCTerm`（:222）→ `InverseComplexSpectrogram`（:163）→ 波形，全程无 vocoder。幅度与相位解耦的意义：恢复任务里幅度好学、相位难学，解耦后网络对两路通道各自施加归纳偏置；且 cos/sin 双通道表示相位天然规避 ±π 回绕（标量相位在回绕点不连续，cos/sin 连续）。

**表示层（SO(2) 通路，未接线）**。audio_utils.py 实现论文 factorized representation 的"完全体"：`wav_to_stft`（audio_utils.py:28-46）输出幅度 + SO(2) 相位矩阵；`radian_to_SO2`（:15-25）把 θ 编码为 [cosθ,−sinθ;sinθ,cosθ] 2×2 旋转矩阵——数学上比 cos/sin 对更优雅，旋转群结构保证相位差=矩阵积，卷积看到的是群元素而非坐标；`phase_R_to_channels`（:48-58）摊平 ...×H×W×2×2 为 4 通道；`stft_mag_R_to_wav`（:70-86）从 4 通道重建复数谱逆 STFT。**源码核实：这三个函数仅被 A2SB_lightning_module.py:21 与 A2SB_lightning_module_api.py:21 import，全仓无任何调用点**；配置里 in/out_channels=3（configs/t_finetune_2split_0.0_0.5.yaml:52-54）也证实网络吃的是瞬时相位。transform 库里还有 SVD 相位修正（`SVDFixMagInstPhase`，transforms.py:135）与自实现 Griffin-Lim（`griffinlim`，transforms.py:273-374，支持随机初始化与 momentum 加速）——纯幅度输入时的相位重建后路，主链不用。

**骨干层 AttnUNetF**（networks.py:188-322）。配置形态：5 级下采样、通道 [128,256,512,768,1024,2048]、第 3/4 级注意力、每级 2 个 ResBlock（configs/pretrain.yaml:52-61）。骨架是 Improved Diffusion 式 UNet：`EmbeddingConditionalSequential`（networks.py:64-76）顺序传递条件向量的 Sequential 变体；ResBlock（:79）用 scale-shift（FiLM）注入时间+频带联合条件；GroupNorm32（:25）强制 fp32 归一化保 bf16 训练稳定。两个任务定制组件：其一**频带嵌入** `get_band_embeddings`（:275-286）——为频率轴每个 bin 生成多频 cos/sin 嵌入（周期设计成超过 n_bands，:281 注释），forward 时拼进条件向量逐级广播（:300-302）——带宽扩展的本质是"从低频特征外推高频内容"，显式频率坐标是强先验；其二 **RotaryAttentionPool2d**（:394-452）——rotary-embedding-torch 的 pixel 频率 RoPE（:414-416），Q/K 过 apply_rotary_emb（:441-442）后做全谱图 scaled_dot_product_attention（:447），同名"Pool"是因为它由注意力池化组件演化来（前身 `AttentionPool2d`，:360-391，注释注明改编自 CLIP 的 attention pool，用固定可学位置参数）。RoPE 的相对位置特性使"训练只见 256 帧窗口、推理吃任意时长"成为可能——这是长音频泛化能力的架构根基。时间条件 `SinusoidalTemporalEmbedding`（:455-471）把 t∈[0,1] 展开成 [0.5,16] 频带的 sin/cos；频带轴与时间轴嵌入拼接（emb_channels=128+band_embedding_dim=16）。

## 外部连接

上游：transforms 管线由 `MixAudioDataset`（datasets/datasets.py:73-200）以 gt/aug 双管线消费，aug 管线尾部即损坏掩码注入点；组装机制 `instantiate_from_ns`（transforms.py:26-52）让 YAML class_path 直接变运行时对象。下游：AttnUNetF 作为 vf_model 被 Diffusion 采样循环调用，输入 (x_t 3 通道, t_emb)，输出同形速度场。可视化侧 `plot_spec_to_numpy`（plotting_utils.py:16-29）把幅度渲染成图。

## 数据流（一个训练样本的旅程）

44.1kHz 波形 → 随机裁 130560 样本段（configs/pretrain.yaml:91 segment_length）→ STFT(2048/512) → 3 通道表示 → gt 管线只做表示变换；aug 管线多走一步 MultinomialInpaintMask（掩区白噪填充）→ 双路进 collate（变长 pad 到 2 的幂，datasets/datamodule.py:17）→ training_step 里 q_sample 揉成 x_t → AttnUNetF(x_t, t_emb) 拟合归一化速度。

## 设计决策与批判

**(1) 双表示并存的解释**：SO(2) 版大概率是论文实验期的探索残留（或反之，3 通道是工程简化后的胜出者），import 保留说明作者未曾最终裁决——对复现者是陷阱：按论文措辞找 SO(2) 通路会以为管线错了。**(2) 4 通道 vs 3 通道**：SO(2) 的 2×2 矩阵四元有冗余（行列式约束只留 1 自由度），3 通道 cos/sin 是其最小信息等价物——工程上省通道，理论上丢群结构。**(3) 注意力只放深层**：第 3/4 级（空间已缩至 1/8、1/16）做全局注意力，浅层纯卷积——计算预算压在感受野最需要的地方，也和频带嵌入配合（深层 bin 少、嵌入密度高）。**(4) AttentionPool2d 留着的代价**：两个池化类并存，RotaryAttentionPool2d 硬编码 rotary_dim=32（networks.py:229）不可配，想调 RoPE 维度得改源码。**(5) power=4 的魔数**：PowerScaleSpectrogram 幂次是超参，配置间不一致风险存在——改配置时注意逆变换管线与前向 aug 管线必须同幂（configs/pretrain.yaml:63-70 与 :130-137 两处声明），否则 x₀/x₁ 量纲错位。

## 新人提示

先跑通表示链再读网络：用 transforms.py 里现成类写 10 行脚本，把任一 wav 转成 3×H×W 再转回去听一遍——幅度/相位解耦比任何文字描述都直观。读 AttnUNetF 从 forward（networks.py:288-322）入手，注意 emb_bcasts 列表在编码器逐级缓存、解码器 pop 复用——skip connection 不只传特征也传条件广播。调试相位问题时盯 cos/sin 通道的数值范围（应为 [−1,1]），出界多半是 PowerScaleSpectrogram 的 channels 参数配错（配置里 channels:[0] 只缩放幅度通道，configs/pretrain.yaml:63-67）。
