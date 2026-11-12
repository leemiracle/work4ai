# diffusion-audio-restoration 新手上手指南（ONBOARDING）

> 基于知识图谱 112 节点/245 边/3 层/7 步（commit `02ddff01c4dbbe20839e13e09da1988db7dd4be9`，2025-08-13）。
> 所有行号锚从源码核实。仓路径：`/usr-data/data2/repos/agent-repos/NVIDIA/diffusion-audio-restoration`。

## 1. 一句话全景：这是什么仓库

NVIDIA（NVlabs）对论文 **A2SB: Audio-to-Audio Schrödinger Bridges**（arXiv 2501.11311，README.md:7）的官方 PyTorch 实现。一句话定位：**面向 44.1kHz 高保真音乐的一体化音频恢复模型**——不用 vocoder、直接输出波形，同时支持带宽扩展（补高频）与 inpainting（补缺失片段），并能恢复小时级长音频（README.md:19、modelcard.md）。

三个"它不是"：
- 不是通用语音增强工具箱——只吃 44.1kHz 单声道 WAV/MP3/FLAC（modelcard.md），用途限定带宽扩展（4kHz 以上）与短时 inpainting（<1 秒段落）；
- 不是从零写的扩散框架——训练代码继承自 NVlabs/I2SB 图像桥扩散（diffusion.py:9-15 原版权头），网络骨架改编自 OpenAI Improved Diffusion（README.md:97）；
- 不是服务化产品——`*_api.py` 文件只是"单文件输出版"研究副本（见第 6 节双轨）。

代码量极小：19 个 Python 文件约 3491 行，加 5 个 YAML 配置。图谱分三层：L01 核心模型与数据层（80 文件节点）、L02 配置层（6）、L03 推理与文档层（26）。

## 2. 桥扩散数学：diffusion.py（169 行讲完全部采样理论）

与 DDPM"从噪声到数据"不同，Schrödinger Bridge 学的是**从损坏后验 x₁ 到干净数据 x₀ 的直接转移核**。整个数学只有三块：

**(1) 对称二次 beta 调度**。`Diffusion.get_beta_t`（diffusion.py:107-112）：t≤0.5 时 β(t)=t²·β_max，t>0.5 时 β(t)=(1−t)²·β_max——峰值在 t=0.5，两端归零。这个对称形状让累积积分 `get_int_beta_0_t`（diffusion.py:114-123）有闭式解（β_max/3·t³ 与 full_integral=2β_max·0.5³/3），于是前向/反向标准差 `get_std_fwd/get_std_rev`（diffusion.py:125-129）全是解析量，无需预计算表。注意类默认 beta_max=0.3（diffusion.py:101），但全部配置文件都用 beta_max=1.0（configs/pretrain.yaml:78）。

**(2) 高斯乘积系数**。`compute_gaussian_product_coef`（diffusion.py:90-98）：两个高斯 N(x|x₀,σ₁²)·N(x|x₁,σ₂²) 的乘积仍是高斯，系数 coef₁=σ₂²/(σ₁²+σ₂²)、coef₂=σ₁²/(σ₁²+σ₂²)、var=σ₁²σ₂²/(σ₁²+σ₂²)。这是全仓唯一被三处共用的数学原语：q_sample（前向）、p_posterior（反向）、get_std_t。

**(3) 前向桥采样与反向步**。`q_sample`（diffusion.py:137-151，注释明言"eq 11"）在 x₀ 与 x₁ 之间插值采样 x_t = coef₁x₀ + coef₂x₁ + √var·ε；`ot_ode=True` 时去掉噪声项退化为确定性 ODE 路径。反向 `p_posterior`（diffusion.py:153-163）同样用高斯乘积把 (x₀ 预测, x_t) 合并回 x_{t_prev}。速度场反推 `get_pred_x0`（diffusion.py:165-168）：pred_x0 = x_t − σ_fwd(t)·net_out——训练目标因此是 (x_t−x₀)/σ_fwd(t)（A2SB_lightning_module.py:386），即网络学的是**归一化速度**，而非噪声或 x₀ 本身。

## 3. 因子化音频表示：从波形到网络张量

论文卖点之一是 factorized audio representation（幅度与相位解耦）。实现分两套，**实际生效的是 3 通道瞬时相位那套**：

**主通路（生效）**：`ComplexSpectrogram`（audio_transforms/transforms.py:83）做 STFT 并 view_as_real 得 2 通道 → `ComplexToMagInstPhase`（transforms.py:108-119）输出 3×H×W：[幅度, cos θ, sin θ]——这就是网络 in/out_channels=3 的来源（configs/t_finetune_2split_0.0_0.5.yaml:52-54）。重建侧 `MagInstPhaseToComplex`（transforms.py:121-132）拼回复数谱，`InverseComplexSpectrogram`（transforms.py:163）逆 STFT 回波形——整条链**无 vocoder**。幅度动态范围由 `PowerScaleSpectrogram`（transforms.py:187-207，配置里 power=4）压缩，DC 项用 `SpectrogramDropDCTerm/AddDCTerm`（transforms.py:214-229）显式摘除/补回。

**SO(2) 通路（存在但未接线）**：audio_utils.py 提供了更讲究的相位表示——`radian_to_SO2`（audio_utils.py:15-25）把相位角编码为 2×2 旋转矩阵 [cos,−sin;sin,cos]，理论上规避 ±π 相位回绕的不连续；`phase_R_to_channels`（audio_utils.py:48-58）摊平为 4 通道供网络消费，`stft_mag_R_to_wav`（audio_utils.py:70-86）负责重建。**但源码核实：这三个函数在 A2SB_lightning_module.py:21 与 A2SB_lightning_module_api.py:21 被 import 后全仓零调用点**——当前 HEAD 的训练/推理管线完全走 3 通道瞬时相位。读论文再读码的人要小心这个"表示层声明与实现脱节"。

变换的组装机制是 `instantiate_from_ns`（transforms.py:26-52）：用 pydoc.locate 按 class_path 点路径动态实例化 jsonargparse Namespace——YAML 里写 `class_path: audio_transforms.transforms.PowerScaleSpectrogram` 就能变成运行时对象，"YAML 即对象图"。统一执行入口 `apply_audio_transforms`（transforms.py:55-80）顺序应用变换并**累积掩码**（stack→sum→clamp(0,1)），返回 (变换后音频, 联合掩码)——多种损坏叠加时掩码自动并集。

## 4. 网络骨干 AttnUNetF：频带嵌入 + 旋转位置编码注意力

`networks.py` 的 AttnUNetF（networks.py:188-322）是标准 UNet 变体，配置为 5 级下采样、通道 [128,256,512,768,1024,2048]、第 3/4 级加注意力（configs/pretrain.yaml:52-59）。四个值得看的组件：

- **频带嵌入**：`get_band_embeddings`（networks.py:275-286）为每个频率 bin 生成多频余弦/正弦嵌入，forward 时拼到条件向量上广播（networks.py:300-302）——让卷积网络显式知道"我在哪个频段"，对带宽扩展任务（高低频物理性质迥异）是关键先验。
- **RotaryAttentionPool2d**（networks.py:394-452）：用 rotary-embedding-torch 的 RotaryEmbedding（freqs_for='pixel'，networks.py:414-416）给 2D 谱图位置编码，Q/K 施转（networks.py:441-442）后 `F.scaled_dot_product_attention` 全局注意力（networks.py:447）。**这是长音频泛化的核心**：RoPE 的相对位置外推性让训练只见 256 帧窗口、推理能吃任意时长。前身 `AttentionPool2d`（networks.py:360-391，注释注明改编自 CLIP）用固定可学位置参数，无外推能力，仓库里两者并存。
- **时间条件**：`SinusoidalTemporalEmbedding`（networks.py:455-471）把扩散时间 t∈[0,1] 乘以 [0.5,16] 区间的多频带得 sin/cos 嵌入；`EmbeddingConditionalSequential`（networks.py:64-76）是能透传条件向量的 Sequential 变体。
- **残差块**：ResBlock（networks.py:79）带 scale-shift 条件注入（FiLM 式），GroupNorm32（networks.py:25）自实现的 GroupNorm 保 fp32 精度。

## 5. 数据与损坏构造：三掩码组合

数据侧三层：`STFTAudioDataModule`（datasets/datamodule.py:34）按 manifest CSV 组装 train（随机片段）/val/test（多测试集，返回 DataLoader 列表 datamodule.py:186-198）/predict（整段长音频）四类 loader；`MixAudioDataset`（datasets/datasets.py:73-200）聚合多个数据集 manifest，对每个样本跑 gt（目标域）与 aug（损坏域）两条变换管线，输出桥模型所需的 x₀/x₁ 成对张量；`FullSequencePredictDataset`（datasets/datasets.py:203-245）不裁剪整段加载，供滑窗推理。

损坏构造在 corruption/corruptions.py，三个掩码生成器：`UpsampleMask`（corruptions.py:18-54，带宽扩展：随机截止频率以上全部置掩）、`ExtensionMask`（corruptions.py:57，频带边缘延伸）、`InpaintMask`（corruptions.py:85，时间段挖空）。训练时由 `MultinomialInpaintMaskTransform`（corruptions.py:120-146）按概率 p 多项式抽样其一（默认 0.5/0.5/0.0，corruptions.py:124），掩码区域用白噪填充模拟损坏输入（`mask_with_noise`，corruptions.py:14-15）。推理侧另有确定性的 `TimestampedSegmentInpaintMaskTransform`（corruptions.py:147+），configs/inference_files_inpainting.yaml:23-47 用四个固定时间戳（1.0-1.2s/3.7-4.0s/8.0-8.5s/11.2-12.0s）构造可复现测试掩码。

## 6. Lightning 双轨：训练模块与它的 API 影分身

训练入口 `python main.py fit --config configs/pretrain.yaml`（README.md:49）。main.py 的 `InpaintingAudioSBLightningCLI`（main.py:14-30）向 LightningCLI 注册 ModelCheckpoint 与验证 inpainting 回调；**cli 在模块顶层实例化、无 __main__ 守卫**（main.py:32）——import 即触发参数解析，纯入口脚本写法。

核心模块 `STFTBridgeModel`（A2SB_lightning_module.py:208-476）：`__init__` 用 `inspect.signature` 遍历参数并 `eval(item)` 批量 setattr 到 self（A2SB_lightning_module.py:218-219，研究代码典型偷懒模式）；`training_step`（:374-402）按 train_t_min/max 区间采 t（`sample_t_bounded`，:370-372）、q_sample 得 x_t、masked MSE 拟合速度目标（:386-388）；优化器 RAdam + decoupled weight decay（:239-242）。仓里还留着两个采样变体 `ddpm_sample_i2sb_way`（:280-316）与 `ddpm_sample_i2sb_change_order`（:318-355）——I2SB 原始采样顺序的对照实现，用于消融。

**双轨结构（README 勘误重点）**：`A2SB_lightning_module_api.py` 是原模块的文件级复制，`diff` 实证仅 4 处差异——构造参数 predict_output_dir 换成 output_audio_filename（原 :46）、去 tqdm 进度条（原 :122）、输出从目录批量改为单文件写（原 :204-205）、外加一行空行。`ensembled_inference.py` 与 `ensembled_inference_api.py` 的差异更极端：**整文件只有 import 行不同**（ensembled_inference_api.py:9）。加上三份复制粘贴的同名 CLI 类（main.py:14-30、ensembled_inference.py:14-30、ensembled_inference_api.py），共 4 组复制代码——这是研究仓"以复制换稳定"的典型样本，读码时切忌以为两轨会同步演进。

## 7. 长音频推理链：T-finetune → 时间分区 → 子进程包装

长音频能力来自三段式设计：

**(1) T-finetuning**：把桥的时间轴切开分段精调。README.md:51-55 指示：先把预训练 checkpoint 复制进实验目录作初始化，第一段跑 `configs/t_finetune_2split_0.0_0.5.yaml`（train_t_min/max=0.0/0.5，configs/t_finetune_2split_0.0_0.5.yaml:47-48；lr 降至 8e-5 :81），第二段复制配置改 t∈[0.5,1.0] 另训——两个模型分别只学桥的前/后半段。

**(2) 时间分区推理**：`TimePartitionedPretrainedSTFTBridgeModel`（A2SB_lightning_module.py:34-205）按 t_cutoffs 加载多 checkpoint（`load_t_bounded_checkpoints`，:64-78，从 state_dict 里剥出 vf_model.* 键），采样时按当前 t 路由到对应专家（`get_vf_model`，:81-86）。`ddpm_sample`（:103-146）先 `multidiffusion_pad_inputs`（diffusion.py:67-83）把长谱图 pad 成可滑窗分块，每个反向步调 `get_multidiffusion_vf`（diffusion.py:27-64）：**对同一输入的多个重叠窗口分别算速度场，按窗口计数取平均融合**（diffusion.py:54-64 的 counts 归一化）——这就是 MultiDiffusion 一致去噪。步内还做两次掩码混合：pred_x0 的掩区替换（:133-134）与 x_t 的已知区域回填（:139-144，SDE 模式下按 get_std_t 加噪保持一致边缘分布）。短洞快通道 `fast_inpaint_ddpm_sample`（:149-180）用 `find_middle_of_zero_segments`（utils.py:54）找每个洞的中点只跑局部窗口。

**(3) 子进程包装器**：inference/ 下三个脚本全是"配置生成器"模式——Python 动态改写 YAML 模板、`save_yaml` 带时间戳+随机数后缀防撞名（如 inference/A2SB_upsample_api.py:37-45）、`Popen(shell=True)` 调 ensembled_inference(_api).py predict（A2SB_upsample_api.py:81-87）。`A2SB_upsample_api.py` 是 README 主推易用入口（README.md:74）：`compute_rolloff_freq`（inference/A2SB_upsample_api.py:56-61）用 librosa 99% 能量滚降点自动检测截止频率，零参数跑任意长音频。数据集级 `A2SB_inpaint_dataset.py`/`A2SB_upsample_dataset.py` 读 manifest 循环逐文件推理，注意 manifest 根路径是**源码硬编码**（inference/A2SB_inpaint_dataset.py:187 的 `'PATH/TO/MANIFEST/FOLDER'`），用前必改。

## 8. 工程坑清单与新手上手顺序

已钉版的坑（详见同目录 ../README.md 勘误节）：DockerFile 大写 F 非 docker 默认名且 README 通篇未提 docker；datasets/.DS_Store 与 configs/.DS_Store 两个 macOS 垃圾文件进了版本库；`STFTBridgeModel.predict_step` 是 breakpoint() 占位（A2SB_lightning_module.py:429-431），真正预测走 TimePartitioned 模块；验证可视化回调 `num_to_plot = 0`（A2SB_lightning_module.py:493）等于开关关闭；training_step 每步 print loss（:396）且 clip_grad_norm_ 写在 loss 返回前（:399）。

建议上手顺序（对应图谱 7 步导览）：
1. 读 README.md + modelcard.md 建立任务观（带宽扩展 vs inpainting）；
2. 啃 diffusion.py 全文 169 行——桥数学的全部；
3. 跟 configs/pretrain.yaml 的 class_path 链路过一遍数据通路（STFT→3 通道表示→掩码）；
4. 读 networks.py:188-322 的 AttnUNetF forward 与 RotaryAttentionPool2d；
5. 对照 A2SB_lightning_module.py:374-402 看训练目标如何落到 masked MSE；
6. 跑通 `inference/A2SB_upsample_api.py -f 退化.wav -o 恢复.wav -n 50`（需先下载 checkpoint，见 README）；
7. 想改代码前先看 ../README.md 勘误清单，避开双轨复制与死 import 陷阱。
