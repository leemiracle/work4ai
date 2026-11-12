# BigVGAN 讲透 · 新人上手指南（ONBOARDING）

> 仓库：`/usr-data/data2/repos/agent-repos/NVIDIA/BigVGAN` @ `7d2b454`（v2.4，2024-09 终版发布）
> 图谱：135 节点 / 305 边 / 10 层 / 15 步 tour / validator 0 issues / fingerprints 68 文件基线
> 本文行号锚全部从源码核实（2026-11-06），非凭记忆。字数约 4300。

---

## 1. 项目定位：双世代通用神经声码器

BigVGAN 是 NVIDIA 开源的**通用神经声码器（universal neural vocoder）**：输入 mel 频谱 `[B, num_mels, frames]`，输出音频波形 `[B, 1, time]`，是 TTS/音频生成管线的最后一公里。仓内代码承载两个世代：

- **v1**（论文 arXiv:2206.04658）：核心创新是**抗混叠周期性激活**——把 Snake 周期激活包在"上采样→激活→下采样"的低通结构里（AMPBlock），配 112M 参数大模型与 LibriTTS 大规模训练，主打语音；
- **v2**（2024-07 发布，README.md:23-27）：工程化续作——换用多尺度子带 CQT 判别器（arXiv:2311.14957）与多尺度 mel 损失（arXiv:2306.06546）、更大规模多类型音频数据（语音/环境声/乐器）、最高 44kHz/512x 上采样、以及**推理专用 fused CUDA kernel**（A100 上 1.5-3x 提速，demo/app.py:281）。

代码血统是"缝合的精品"：生成器骨架与 MPD 判别器来自 HiFi-GAN（bigvgan.py:4），Snake 激活来自 EdwardDixon/snake（activations.py:1），抗混叠树来自 junjun3518/alias-free-torch（Apache 2.0），CQT 判别器来自 Amphion（discriminators.py:406），多尺度 mel 损失来自 descript-audio-codec（loss.py:21）。八份第三方许可证全部收在 `incl_licenses/`（LICENSE_1~8：MIT×6 + Apache2 + BSD3），README.md:256-262 逐一致谢——这是合规引用型开源的范本。

## 2. 架构总览：一条生成器主干 + 对抗训练面

生成器（bigvgan.py:244 `class BigVGAN`）是纯卷积流水线：

`conv_pre(num_mels→1536)`（bigvgan.py:286-288）→ 6 级 `ConvTranspose1d` 上采样（通道逐级减半，bigvgan.py:301-317）→ 每级并联 3 个 AMPBlock1（kernel 3/7/11、dilation [1,3,5]）取平均（bigvgan.py:371-376）→ 尾部 SnakeBeta 激活（bigvgan.py:345）→ `conv_post(ch→1)`（bigvgan.py:349-351）→ tanh（v1）或 clamp（v2，bigvgan.py:382-385）。

AMPBlock1（bigvgan.py:31）是论文灵魂：每条膨胀卷积支路（convs1，bigvgan.py:56-70）后跟一条 dilation=1 的 convs2（bigvgan.py:73-87），**每个卷积前**都套 `Activation1d`（forward 里 zip 交错取激活，bigvgan.py:133-139），残差相加（bigvgan.py:139）。AMPBlock2（bigvgan.py:150）是去掉 convs2 的瘦身版，九个配置全用 `"resblock": "1"`。

对抗训练面：`train.py` 用 MPD（周期 2/3/5/7/11，discriminators.py:110）+ 一个可切换判别器——v1 走 UnivNet 式 MRD（三组 STFT 分辨率，discriminators.py:247），v2 配置置 `use_cqtd_instead_of_mrd=true`（train.py:85-89）改用 MS-SB-CQT（discriminators.py:568）。损失 = mel 重建（v1 单尺度 L1×45 / v2 多尺度×15）+ 特征匹配×2（loss.py:223）+ LSGAN 对抗项（loss.py:226-254）。

## 3. 目录地图（10 层图谱视角）

```
BigVGAN/
├── bigvgan.py            # L02 生成器核心：AMPBlock1/2 + BigVGAN + HF Hub 混入
├── activations.py        # L05 Snake/SnakeBeta 周期激活（论文公式在此）
├── alias_free_activation/
│   ├── torch/            # L05 纯 torch 抗混叠树：act/filter/resample
│   └── cuda/             # L06 JIT 编译 fused kernel：activation1d/load/.cpp/.cu
├── discriminators.py     # L03 九类判别器全集（P/R/B/CQT + 组合器）
├── loss.py               # L04 多尺度 mel 损失 + LSGAN/特征匹配
├── meldataset.py         # L04 mel 特征标准 + MelDataset 数据集
├── train.py              # L01 训练入口（610 行单函数 train()）
├── inference.py / inference_e2e.py  # L01 双推理路径（wav 入/mel 入）
├── demo/app.py           # L01 gradio 演示（预载全部 9 个模型）
├── env.py / utils.py     # L05/L07 AttrDict 配置容器 / 通用工具
├── configs/*.json        # L08 九配置三族
├── filelists/LibriTTS/   # L09 六清单（train-full.txt 354570 行=仓内最大文件）
├── tests/                # L07 三个 CUDA 一致性/速度测试
└── nv-modelcard++/       # L10 五份合规文档（nv-modelcard++/bias.md:2-4 行官方声明未缓解）
```

## 4. 核心数据流：LibriTTS → meldataset → GAN 训练 → 推理

**数据侧**：`filelists/LibriTTS/train-full.txt` 每行 `相对路径|归一化文本`，`get_dataset_filelist`（meldataset.py:146-179）拼出 wav 路径。`MelDataset.__getitem__`（meldataset.py:234）用 `librosa.load(sr=None)`（meldataset.py:243）零重采样读原始波形，随机裁剪 segment_size 片段、**只对裁出的块**做重采样（meldataset.py:249-283，省算力的关键设计），音量归一化 `*0.95`（meldataset.py:298），实时算 mel（meldataset.py:305-315），另算一份 `fmax_for_loss` 版 mel_loss（meldataset.py:365-375）。注意：**没有** .mel 磁盘缓存（那是 HiFi-GAN 旧版行为），只有 mel 基矩阵/窗函数的进程内缓存（meldataset.py:47-48、86-93）。加载失败会跳过换随机样本（meldataset.py:386-393）。

**mel 标准函数** `mel_spectrogram`（meldataset.py:51）：librosa slaney mel 滤波器组 + torch.stft + `sqrt(real²+imag²+1e-9)`（meldataset.py:115）+ log 压缩（meldataset.py:118）。训练与推理共用这一份，是全仓对齐的锚点——e2e 推理喂 .npy mel 时 STFT 超参必须与 config.json 一致（README.md:135）。

**训练循环**（train.py:456-665）：每批先更新 D（detach 生成波形，train.py:489/495，LSGAN 损失+clip_grad_norm，train.py:503 默认 1000、v2 配置 500），再更新 G（mel 损失 + 两路对抗 + 两路特征匹配，train.py:544-552）；`--freeze_step` 可先纯回归热身（train.py:506-520）。v2 的 ExponentialLR 从按 epoch 改为**按 step**衰减（train.py:658-660）。验证循环算 mel 误差/PESQ/MR-STFT 三指标（train.py:281-426，PESQ 需重采样到 16k，train.py:335-341，非语音集自动跳过，train.py:331）。

**推理**：checkpoint 目录里 `g_*` 只存生成器（train.py:577-585），`do_*` 存双判别器+优化器（train.py:586-597）。

## 5. alias-free 双实现树：torch 纯净版 vs CUDA JIT 版

`alias_free_activation/torch/act.py:8` 的 `Activation1d` 是三段式：`UpSample1d(2x)` → `act(x)` → `DownSample1d(2x)`（torch/act.py:25-28）。滤波核心是 `kaiser_sinc_filter1d`（torch/filter.py:30）：Kaiser 窗 + sinc 低通，按 Kaiser 公式估 β（torch/filter.py:38-44），归一化 sum=1 防直流泄漏（torch/filter.py:56-59），以 `register_buffer` 持久化（torch/filter.py:91）。上采样用 `conv_transpose1d` 补零插值再滤波（torch/resample.py:33-35），cutoff=0.5/ratio（torch/resample.py:23-25）。`sinc` 带版本条件定义：torch≥1.10 用内置 `torch.sinc`，否则手写数值稳定版（torch/filter.py:9-24）。

CUDA 版（alias_free_activation/cuda/activation1d.py:35）同构但多一个 `fused=True` 分支：把上滤波+snake+下滤波一次 kernel 完成（cuda/activation1d.py:74-76）。**两个关键约定**：kernel 内已烘焙 `exp()`，因此线性 scale 的 alpha/beta 传参前要取 log（cuda/activation1d.py:68-72）；Snake 没有 beta 参数，直接用 alpha 充当（cuda/activation1d.py:61-62）。docstring 自述硬编码假设：filter size 12 + replication padding + logscale 参数，**超参不同则结果错误**（cuda/activation1d.py:16-18）。`backward` 直接 `raise NotImplementedError`（cuda/activation1d.py:31）——只能推理。

bigvgan.py 三处相同的 `h.get("use_cuda_kernel")` 懒加载开关（bigvgan.py:95/195/273，构造时从 CUDA 分支 import，否则回退 torch 版）保证不装 CUDA 工具链也能跑纯 torch 路径。

## 6. CUDA 加速链：import → JIT → kernel

`alias_free_activation/cuda/activation1d.py:11` 在**模块级**执行 `load.load()`——import 即触发 JIT 编译。load.py 是 apex 式套路：先清空 `TORCH_CUDA_ARCH_LIST` 防止架构列表乱序导致反复重编（cuda/load.py:11-14），探测 nvcc 版本（cuda/load.py:68-78），CUDA≥11 追加 sm_80（cuda/load.py:20-23），固定 build_directory 复用编译产物（cuda/load.py:26-28、31-48），开 `--use_fast_math`（cuda/load.py:43）与 half 宏解锁（cuda/load.py:50-55）。

kernel 侧（anti_alias_activation_cuda.cu）：入口 `anti_alias_activation_forward`（anti_alias_activation_cuda.cu:44），线程块内先把 alpha/beta 过 `expf`（anti_alias_activation_cuda.cu:85-89），snake 数学在 anti_alias_activation_cuda.cu:139（`1/(β+ε)·sin²(αx)`），类型分派走 `type_shim.h:20` 的 `DISPATCH_FLOAT_HALF_AND_BFLOAT` 宏（anti_alias_activation_cuda.cu:232）。正确性由 tests/test_activation.py:23-57 验证（fused vs 纯 torch 逐元素差 ≤1e-3），速度基准在 tests/test_cuda_vs_torch_model.py（A100 上 1672→3916 kHz，见 README.md:231-240 表）。

## 7. 配置矩阵三族（configs/ 九文件）

| 族 | 文件 | 通道/上采样 | 判别器 | mel 损失 | 关键差异 |
|---|---|---|---|---|---|
| v1 论文版 | bigvgan_{22,24}khz_*.json | 1536ch，[4,4,2,2,2,2]（256x） | MPD+MRD | 单尺度 L1×45 | batch 32/segment 8192 |
| v1 base | bigvgan_base_*.json | 512ch，[8,8,2,2]（256x） | 同上 | 同上 | 14M 参数轻量版（demo 表 Parameters 列，demo/app.py:399-409） |
| v2 | bigvgan_v2_*.json ×5 | 1536ch，256x 或 512x | MPD+CQTD | 多尺度×15 | batch 4/segment 65536/clip 500/`use_tanh_at_final=false` |

v2 五件差异在采样率（22.05k/24k/44.1k）、mel 数（80/100/128）、fmax（None 全带 / 8k 电话带）、hop（256 / 512=唯一 512x 变体）。两个易漏点：`use_mbd_instead_of_mrd` 分支（train.py:79-84）在九配置中**零消费**——MBD 判别器是可用但未启用的库存；v1 配置无 `use_tanh_at_final` 键，代码默认 True（bigvgan.py:359），v2 显式 False 改 clamp——同一份代码两个世代输出边界行为不同。

## 8. 新人上手路径（建议顺序）

1. **跑通推理**：`BigVGAN.from_pretrained("nvidia/bigvgan_v2_24khz_100band_256x")`（README.md:46-80；HF 混入实现在 bigvgan.py:414-493，加载失败自动去 weight_norm 重试，bigvgan.py:484-491）；本地 gradio：`python demo/app.py`（需补装 gradio+spaces，demo/requirements.txt 比根多两行）。
2. **读懂生成器**：bigvgan.py 从 `forward`（bigvgan.py:361-387）自顶向下，再进 AMPBlock1 与 activations.py:60/124 的两行 snake 公式。
3. **理解抗混叠**：alias_free_activation/torch 三文件各 30-60 行，小而完整。
4. **训练复现**：按 README.md:91-118 建 LibriTTS 软链后跑 train.py；**注意** argparse 默认清单路径是 `tests/LibriTTS/*.txt`（train.py:678/681），仓内实际在 `filelists/LibriTTS/`——必须显式传参，默认值跑不起来（见 README 勘误清单 #1）。
5. **核对配置**：改配置先看第 7 节矩阵；启用 CUDA kernel 只需 `use_cuda_kernel=True`（推理限定，训练不支持，bigvgan.py:452-461 有三行警告）。
6. **合规检查**：商用/部署前读 nv-modelcard++/ 五文档；bias.md 明言**未采取偏见缓解措施**（bias.md 全文 4 行），语音数据血统决定适用边界。

> 深入单文件精讲见 `../explain/` 六篇；跨文件勘误与坑见 `../README.md`。
