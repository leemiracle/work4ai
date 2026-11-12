# 讲透 diffusion-audio-restoration（NVIDIA A2SB）

A2SB: Audio-to-Audio Schrödinger Bridges（arXiv 2501.11311）官方实现——44.1kHz 音乐恢复：带宽扩展 + inpainting，无 vocoder 端到端、小时级长音频。

## 全链状态表

| 阶段 | 产物 | 状态 |
|------|------|------|
| 图谱 | 仓内 `.understand-anything/knowledge-graph.json`（112 节点/245 边/3 层/7 步，fingerprints 31@02ddff01） | ✅ |
| 甄别笔记 | 仓内 `.understand-anything/NOTES-DIGEST.md`（13 条） | ✅ |
| 上手指南 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（8 节，60+ 行号锚全源码核实） | ✅ |
| 精讲 | [explain/01-桥扩散数学-diffusion-MultiDiffusion.md](explain/01-桥扩散数学-diffusion-MultiDiffusion.md) · [02-音频骨干与相位-networks-audio_utils.md](explain/02-音频骨干与相位-networks-audio_utils.md) · [03-双轨与推理链-lightning-ensembled-子进程.md](explain/03-双轨与推理链-lightning-ensembled-子进程.md) | ✅ |

> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/diffusion-audio-restoration`（commit 02ddff01，2025-08-13，19 py/3491 行/5 YAML）。
> 字数口径：不计空格总字符。

## 十五分钟速览

- **数学核心** diffusion.py 169 行：对称二次 β 调度（t≤0.5 取 t²、t>0.5 取 (1−t)²，闭式积分）+ 高斯乘积系数（diffusion.py:90-98）+ 前向 q_sample（:137-151，论文 eq 11）+ MultiDiffusion 重叠窗口速度场均值融合（:27-64）。
- **表示层双轨**：实际管线 = 3 通道 [幅度, cos θ, sin θ]（audio_transforms/transforms.py:108-119）；论文级 SO(2) 旋转矩阵表示（audio_utils.py:15-25 等）**被 import 但全仓零调用**。
- **骨干** AttnUNetF（networks.py:188-322）：频带嵌入（:275-286）+ 第 3/4 级 RotaryAttentionPool2d（:394-452，pixel 频率 RoPE）——长音频平移外推的架构根基。
- **长音频**：T-finetune 切 t 区间分段精调（configs/t_finetune_2split_0.0_0.5.yaml:47-48）→ TimePartitioned 推理按 t 路由多 checkpoint（A2SB_lightning_module.py:81-86）→ MultiDiffusion 滑窗一致化。
- **推理工程**：inference/ 三脚本 = 配置生成器 + Popen(shell=True) 子进程两段式（README.md:67-74 命令）。

## 源码级勘误（钉版，全部 diff/grep 实证）

1. **SO(2) 因子化表示是死 import**。`phase_channels_to_R`/`stft_mag_R_to_wav`/`phase_R_to_channels` 在 A2SB_lightning_module.py:21 与 A2SB_lightning_module_api.py:21 导入后无任何调用点；实际波形重建走 transforms.py 的 `MagInstPhaseToComplex`+`InverseComplexSpectrogram`（audio_transforms/transforms.py:121-132, :163）。图谱节点摘要"stft_mag_R_to_wav 完成端到端无 vocoder 输出链路"措辞失准——无 vocoder 为真，但走的不是这个函数。
2. **双轨 = 文件级逐字复制，非参数化复用**。`A2SB_lightning_module(_api).py` 全量 diff 仅 4 处 hunk（参数名 :46 / 去 tqdm :122 / 单文件输出 :204-205 / 一行空行）；`ensembled_inference(_api).py` 整文件**只差 import 行**（ensembled_inference_api.py:9）。另有三份复制粘贴的同名 `InpaintingAudioSBLightningCLI`（main.py:14-30、ensembled_inference.py:14-30、ensembled_inference_api.py）。
3. **DockerFile 大写 F**。仓根文件名 `DockerFile`（非默认 `Dockerfile`），`docker build` 必须显式 `-f DockerFile`；且 README.md 通篇未提 docker（grep 零命中）——镜像构建完全靠读源码自悟。
4. **.DS_Store 垃圾进版本库**。datasets/.DS_Store 与 configs/.DS_Store（各 6148B，macOS Finder 元数据）被提交，图谱也被迫为其建了 2 个 file 节点（fanIn/fanOut=0 的孤立点）。
5. **入口行为不一致**。main.py:32 模块级实例化 cli、无 `__main__` 守卫（import 即解析参数）；ensembled_inference.py:31-32 却有守卫——同为入口脚本，可 import 性截然不同。
6. **STFTBridgeModel.predict_step 是占位符**：`breakpoint()` + `print("hello")`（A2SB_lightning_module.py:429-431）。训练模块的 predict 钩子从未实现，真预测走 TimePartitionedPretrainedSTFTBridgeModel.predict_step（:183-205）。
7. **验证可视化开关恒关**：`LogValidationInpaintingSTFTCallback` 中 `num_to_plot = 0`（A2SB_lightning_module.py:493），`for i in range(num_to_plot)` 永不执行——整个回调只剩空转。
8. **训练循环卫生问题**：每步 `print('\nloss: ...')`（:396）刷屏；`clip_grad_norm_` 写死在 training_step 内（:399）而非 Lightning 的 configure_gradient_clipping 钩子；NaN 时 print 后返回 None（:392-394）静默跳批。
9. **beta_max 默认值与配置不符**：Diffusion 类默认 0.3（diffusion.py:101），全部配置实测 1.0（configs/pretrain.yaml:78）——读默认值推断噪声强度会差 3 倍。
10. **inference 包装器硬编码**：manifest 根路径 `'PATH/TO/MANIFEST/FOLDER'`（A2SB_inpaint_dataset.py:187）必须改源码；shell 命令里 `cd ../`（A2SB_upsample_api.py:81）假定工作目录在 inference/ 下。
11. **read_standard_csv 三处独立复刻**：datasets/datasets.py:43-71、inference/A2SB_inpaint_dataset.py:32-51、inference/A2SB_upsample_dataset.py:31-50 各有一份语义相近的实现（签名与行为略异）——又一处复制替代复用。
12. **n_attn_heads 配置 8 vs 类默认 4**（configs/t_finetune_2split_0.0_0.5.yaml vs networks.py:190 默认）——以配置为准。

## 延伸

- 论文：A2SB (arXiv 2501.11311)；血统：I2SB（NVlabs，图像桥扩散，diffusion.py:9-15 版权头）→ A2SB 换域音频；网络骨架源自 OpenAI Improved Diffusion（README.md:97）。
- 许可：模型 NVIDIA OneWay NonCommercial（非商用），代码 NVIDIA Source Code License（README.md:94-95）——二次发布注意。
- 相关仓内邻居：BigVGAN/CleanUNet/DL4AGX 等 NVIDIA 音频恢复谱系见 work4ai 同级目录。
