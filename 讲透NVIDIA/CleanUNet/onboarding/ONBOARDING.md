# CleanUNet 项目 ONBOARDING（微仓精读版）

> 仓库：`/usr-data/data2/repos/agent-repos/NVIDIA/CleanUNet`（commit 9487a8db）
> 图谱基线：58 节点 / 125 边 / 8 层 / 14 步导览 / 0 issues / fingerprints 20 文件
> 本文所有行号锚均从源码逐一核实（2026-11-06 分析批次产物，批 1-4）

---

## 1. 项目定位

CleanUNet 是 NVIDIA 官方发布的**波形域因果语音去噪模型**——论文《Speech Denoising in the Waveform Domain with Self-Attention》（arXiv:2202.07790），发表于 **ICASSP 2022**（README.md:106-114 的 bibtex `kong2022speech` 钉版；注意它**不是**网上常被误传的 NeurIPS 论文）。作者 Kong/Ping/Dantrey/Catanzaro。

一句话概括模型：**编码器-解码器 U-Net 骨干 + 瓶颈处因果自注意力精炼块**，直接吃 16kHz 原始波形输出干净波形，不经过频谱域。训练损失同时定义在波形域（L1）与多分辨率频谱域（MRSTFT），这是论文的核心配方（README.md:3-10）。

仓库是典型"论文配套微仓"：8 个 Python 文件、2 份 JSON 配置、1 个 Dockerfile、5 份上游许可证、2 个 git-lfs 权重指针，共 20 个图谱文件节点。零测试、零 CI——所有验证靠 `__main__` 冒烟块与客观评测脚本。

## 2. 架构总览

三个层次看全仓：

**模型层**（network.py，384 行）
- Transformer 组件五件套：ScaledDotProductAttention（network.py:17-35）、MultiHeadAttention（network.py:38-88）、PositionwiseFeedForward（network.py:91-111）、EncoderLayer（network.py:147-159）、TransformerEncoder（network.py:162-202），外加 PositionalEncoding（network.py:122-144，实际未启用——CleanUNet 以 `n_position=0` 构造，位置编码退化为 `lambda x: x`，见 network.py:172-175 与 310）。
- 主模型 CleanUNet（network.py:226-355）：8 层 Conv1d 下采样（network.py:271-277，每层 Conv-K-S + ReLU + 1x1Conv + GLU，通道 H 从 64 翻倍至 max_H=768 封顶，network.py:297-298）→ 瓶颈处 1x1 卷积降到 d_model=512 → 因果自注意力 → 1x1 卷积升回 → ConvTranspose1d 上采样逐层加 skip（network.py:349-352）。全部卷积层用 weight_scaling_init 初始化（network.py:315-317，算法出处 util.py:164 的 arXiv:1911.13254）。

**训练/推理层**（train.py / denoise.py / distributed.py）
- train.py:56-197 的 `train()` 是唯一训练函数；distributed.py:150-176 的 `main()` 是多卡启动器（README.md:65 的标准训练入口 `python3 distributed.py -c configs/*.json`）。
- denoise.py:54-124 的 `denoise()` 负责加载权重逐条推理写 enhanced wav。

**支撑层**（util.py / dataset.py / stft_loss.py / python_eval.py / configs / Dockerfile）
- util.py 是工具箱：checkpoint 扫描、参数量打印、学习率调度、损失组合。stft_loss.py 是频域损失家族。dataset.py 管数据对加载。python_eval.py 管 PESQ/STOI 评测。

## 3. 目录地图

```
CleanUNet/
├── network.py          # 模型定义（Transformer 瓶颈 + UNet 编解码）384 行
├── train.py            # 训练入口（waveglow 改编）234 行
├── denoise.py          # 推理/去噪入口 157 行
├── distributed.py      # 多卡梯度同步 + GPU 启动器 189 行
├── dataset.py          # DNS 干净/带噪对数据集 119 行
├── stft_loss.py        # 多分辨率 STFT 损失（ParallelWaveGAN 改编）184 行
├── util.py             # 调度器/损失/工具（vq-vae-2 改编）224 行
├── python_eval.py      # PESQ/STOI 客观评测 60 行
├── configs/
│   ├── DNS-large-full.json   # 全频带损失变体（54 行）
│   └── DNS-large-high.json   # 高频带损失变体（唯一差异 band:"high"）
├── exp/
│   ├── DNS-large-full/checkpoint/pretrained.pkl   # git-lfs 指针，实体 184336765B≈176MB
│   └── DNS-large-high/checkpoint/pretrained.pkl   # 同上（oid 不同）
├── incl_licenses/      # 五份上游许可证（见第 7 节血统表）
├── Dockerfile          # NGC pytorch:20.12-py3 环境（9 行，无 COPY）
└── README.md           # 官方说明 114 行
```

图谱口径：file 级 20 节点 + 函数/类 38 子节点 = 58 节点。全部 8 个 py 文件都有 `__main__` 冒烟/入口块，是论文仓常见的"每个文件可独立跑通"风格。

## 4. 核心数据流

**训练前向流**（一条损失计算的完整路径）：

1. `dataset.py:67-68` torchaudio.load 读 clean/noisy wav 对 → `dataset.py:76-79` 训练分支随机裁剪 10 秒（configs/DNS-large-full.json 的 crop_length_sec）→ DataLoader（num_workers=4，dataset.py:93）。
2. `train.py:148-149` 批数据上 CUDA → `train.py:159` 调 `loss_fn(net, X, ...)`。
3. `util.py:206` loss_fn 内先前向 `net(noisy_audio)` 去噪 → `util.py:208-213` 算 L1 AE loss（ell_p=1）→ `util.py:217-221` 叠加 MultiResolutionSTFTLoss 的谱收敛+对数幅度损失。
4. `network.py:319-355` 模型内部：按批 std 归一化（network.py:327-328）→ padding 补齐到可整除长度（network.py:329，padding 函数在 network.py:208-223）→ 8 层下采样收集 skip（network.py:332-336）→ 因果下三角 mask（network.py:340）→ 512 维注意力（network.py:342-346）→ 上采样逐层 `x += skip`（network.py:349-352）→ 裁剪回原长乘 std 反归一化（network.py:354）。
5. `train.py:164-167` backward → clip_grad_norm(1e9)（train.py:165，1e9 等于几乎不裁）→ scheduler.step → optimizer.step。

**学习率流**：util.py:103-149 的 LinearWarmupCosineDecay 不是官方 `torch.optim.lr_scheduler` 子类——step() 直接改写 `param_groups` 的 lr（util.py:137-138），前 5% 迭代线性升到 lr_max（warmup_proportion=0.05，train.py:136），之后余弦衰减到 lr_min/1e4（util.py:126）。

## 5. 训练·推理·评测链

**训练**：`python3 distributed.py -c configs/DNS-large-full.json`（README.md:65）→ distributed.py:167-173 为每块 GPU spawn 一个 `python train.py --config=... --rank=i --group_name=group_<时间戳>` 子进程。8 GPU 全局 batch 64、250K 迭代（README.md:67；配置在 configs L22-26 的 n_iters=250000/lr=2e-4/batch_size_per_gpu=8）。断点续训靠 util.py:23-42 的 find_max_epoch 扫 checkpoint 目录取最大迭代号（train.py:100-101），恢复时连训练秒数一起还原（train.py:115）。

**推理**：`python denoise.py -c configs/DNS-large-high.json --ckpt_iter pretrained`（README.md:79）→ denoise.py:86-92 加载 pretrained.pkl（'max' 走 find_max_epoch，'pretrained' 保持字符串拼路径）→ net.eval() → 逐条 sampling 前向（denoise.py:114，util.py:173-178 的 no_grad 包装）→ scipy wavwrite 写 `enhanced_*.wav`（denoise.py:117-119）。

**评测**：`python python_eval.py -d dns -e <去噪目录> -t <测试集目录>`（README.md:87）→ python_eval.py:23 硬编码遍历 300 条（DNS no-reverb 测试集就是 300 条，README.md:55-56）→ 每条算 PESQ-WB/NB + STOI 按样本长度加权（python_eval.py:35-38）→ 主程序除以总长度打印均分（python_eval.py:58-60）。

链路注意：评测脚本与仓内代码零 import（只依赖 pesq/pystoi/scipy），接在 denoise.py 的输出目录之后使用，靠文件系统衔接。

## 6. 分布式与部署

**梯度同步**（distributed.py:95-147 apply_gradient_allreduce，waveglow 遗产）：先广播 state_dict 对齐参数（distributed.py:105-108）→ 每个可训练参数注册梯度 hook（distributed.py:136-140）→ 反向结束时把梯度按 dtype 分桶、摊平成 1D 缓冲 all_reduce 再写回（distributed.py:127-134，摊平/还原函数在 distributed.py:60-93）。这是 PyTorch DDP 普及前的手写数据并行。

**启动器陷阱**：distributed.py:158 先 append `--num_gpus=...`，随后每卡循环 distributed.py:168 用 `args_list[-2]='--rank=i'` **原位覆盖**它——`--num_gpus` 只是占位符，最终命令行不含该参数（train.py 的 argparse 也确实未定义它，train.py:201-208）。读代码时容易误判为 bug。

**进程组**：init_distributed（distributed.py:48-58）用 config 的 dist_config（nccl + tcp://localhost:54321，configs L46-49）初始化，并 set_device 绑卡。

**部署**：Dockerfile 仅 9 行——基于 `nvcr.io/nvidia/pytorch:20.12-py3`（L1），L4-L10 七条 pip 装固定版本依赖（torchaudio==0.8.0/pillow==6.2.0/inflect==4.1.0/scipy==1.5.0/tqdm/pesq/pystoi）。**无任何 COPY**——纯环境镜像，代码挂载进容器跑。torchaudio 0.8.0 对应 PyTorch 1.7，恰是 stft_loss.py:13 `is_pytorch_17plus` 版本探测分支针对的世代。

## 7. 上游血统（五份许可证精确对应）

README.md:99 的 References 节 + incl_licenses/ 五份文件，构成完整的血统链：

| 许可证 | 上游项目 | 继承部位 |
|---|---|---|
| LICENSE_1（BSD-3, NVIDIA 2018） | NVIDIA/waveglow | train.py/denoise.py/distributed.py 整体结构、分布式训练（train.py:1、denoise.py:1、distributed.py 版权头） |
| LICENSE_2（MIT, Hayashi 2020） | kan-bayashi/ParallelWaveGAN | stft_loss.py 全文件（stft_loss.py:1-4） |
| LICENSE_3（MIT, Victor Huang 2017） | jadore801120/attention-is-all-you-need-pytorch | network.py 的 Transformer 五件套（network.py:13-15） |
| LICENSE_4（MIT, OpenNMT） | OpenNMT-py | 注意力实现的间接上游（README.md:99 链式注明） |
| LICENSE_5（MIT, Kim Seonghyeon 2019） | rosinality/vq-vae-2-pytorch | util.py:68-71 的学习率调度器 |

本仓主许可证 MIT（根 LICENSE 文件）。这种"骨架借 waveglow、损失借 ParallelWaveGAN、注意力借 jadore、调度器借 vq-vae-2"的组合式构建，是 2020-2022 NVIDIA 语音仓的标准做法——读任何一块代码前先看头部注释，能少走很多弯路。

## 8. 新人上手

**最小复现路径**（有 V100/A100 环境）：
1. `docker run -it --gpus all nvcr.io/nvidia/pytorch:20.12-py3` + Dockerfile 的 pip 列表，或直接 `git lfs pull` 拉权重（README.md:69）。
2. `python denoise.py -c configs/DNS-large-full.json --ckpt_iter pretrained -subset testing`（denoise.py:127-156 主块）→ 得 enhanced wav。
3. `python python_eval.py -d dns -e exp/DNS-large-full/speech/pretrained -t <测试集路径>` 出 PESQ/STOI。
4. 想单独验证模型：`python network.py -c configs/DNS-large-full.json` 跑 network.py:358-384 的前向+反向冒烟。

**五个必知陷阱**（源码实证，详细展开见 explain/04 与 README 勘误清单）：
1. **subset 契约错位**：denoise.py:133-134 的 argparse choices 含 'validation'，但 dataset.py:33 断言只放行 training/testing——传 validation 必在数据集构造处 AssertionError。
2. **全局 config 注入**：train()（train.py:70/81/88）与 denoise()（denoise.py:67/71/81）直接读取 `__main__` 块注入的 global 变量（train.py:214-220、denoise.py:141-147）——单独 `from train import train` 调用会 NameError，这是 waveglow 时代的"Globals nicer in this case"风格（train.py:210 注释原话）。
3. **tsfm_n_layers 两套默认**：network.py:232 代码默认 3，configs 两个 JSON 都是 5（DNS-large-full.json L9）——复现论文规格以配置为准。
4. **裸 except 吞错**：train.py:118 的 checkpoint 恢复失败会静默从头训练；python_eval.py:30-31 文件缺失静默 continue。
5. **死代码**：dataset.py:7 的 scipy wavread 与 dataset.py:20 的 torchvision import 均未被使用；network.py:122-144 的 PositionalEncoding 整类未启用。

**图谱入口**：`.understand-anything/knowledge-graph.json`（58 节点/125 边），14 步导览从 README → 训练链 → 模型 → 推理评测逐层展开；explain/ 六篇对应六个子系统精讲。

（全文约 3600 字，行号锚 55 处）
