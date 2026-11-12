# 06 · configs + Dockerfile + exp 权重 —— 配置变体 / 容器 / 资产层

> 锚均从源码核实（commit 9487a8db）。三组非代码资产构成 CleanUNet 的"运行参数面"，代码零改动即可切换论文两个变体。

## 角色定位

configs/DNS-large-*.json 是唯二的两份实验配置（全频带 vs 高频带变体）；Dockerfile 是 9 行纯环境镜像；exp/*/checkpoint/pretrained.pkl 是 NVIDIA 官方发布的两个 git-lfs 权重指针。三者一起回答"跑哪个模型、在哪跑、用什么起点跑"。

## 内部结构

**configs/DNS-large-full.json**（54 行）六节：
- network_config（L2-13）：channels_H=64、max_H=768、8 层 encoder、kernel 4/stride 2、**tsfm_n_layers=5**、8 头、d_model=512。
- train_config（L14-37）：exp_path 定 checkpoint 目录名；log 节（ckpt_iter='max'、iters_per_ckpt=10000、iters_per_valid=500）；optimization（n_iters=250000、lr=2e-4、batch_size_per_gpu=8）；loss_config（ell_p=1、双 lambda=1、stft_config 含 sc/mag_lambda=0.5、**band='full'**、三组分辨率）。
- trainset_config（L38-42）：root=./dns、crop_length_sec=10、sample_rate=16000。
- gen_config（L43-45）：输出 ./exp；dist_config（L46-49）：nccl + tcp://localhost:54321。

**DNS-large-high.json**：与 full **逐字段唯一差异**是 stft_config.band='high'（对应 stft_loss.py:117-120 的频带上半分支）——两份 54 行文件只差一个字符串，变体管理极简。

**Dockerfile**（9 行）：`FROM nvcr.io/nvidia/pytorch:20.12-py3`（L1）+ apt-get update（L2）+ 七条固定版本 pip（L4-L10：pillow==6.2.0、torchaudio==0.8.0、inflect==4.1.0、scipy==1.5.0、tqdm、pesq、pystoi）。

**exp 权重**：两个 pretrained.pkl 各 3 行 git-lfs 指针（L1 version / L2 oid / L3 **size 184336765** ≈176MB），.gitattributes:1 声明 `*.pkl filter=lfs diff=lfs merge=lfs`；denoise.py --ckpt_iter pretrained 按字面名加载（denoise.py:88-90）。

## 外部连接

配置被四处 `-c` 消费：train.py:211-220（注入四个 global）、denoise.py:138-147（三个 global）、network.py:364-371（__main__ 冒烟读 network_config）、dataset.py:106-109（__main__ 读 trainset_config）。Dockerfile 的 pesq/pystoi 专供 python_eval.py:15-16，torchaudio 0.8.0 专供 dataset.py:67——镜像与代码的依赖对应关系精确到文件。权重依赖链：.gitattributes（LFS 追踪）→ git lfs pull → pretrained.pkl 实体 → denoise.py:91 torch.load → CleanUNet state_dict。配置的 exp_path 与权重目录名互为镜像（DNS-large-full.json L15 ↔ exp/DNS-large-full/）。

## 数据流

配置流：JSON → train/denoise 的 `__main__` json.loads → **global 变量**分发函数体（train.py:214-220）——network_config 进 CleanUNet 构造、trainset_config 进数据加载、dist_config 进 init_distributed、loss_config 进损失。配置节与构造形参**逐名透传**（`**network_config`），多写一个 JSON 键就 TypeError。

资产流：git clone 得 3 行指针 → `git lfs pull`（README.md:69）拉回 176MB 实体 → torch.load(map_location='cpu')（denoise.py:91）→ load_state_dict。

## 设计决策

1. **一个字符串管理变体**：band full/high 承载论文两大实验分支，配置即论文表格的机器可读版。
2. **tsfm_n_layers=5 覆盖代码默认 3**（DNS-large-full.json L9 vs network.py:232）：复现论文规格看配置不看代码签名。
3. **无 COPY 的 Dockerfile**：代码挂载进容器，镜像只锁依赖版本——论文仓常见做法，代价是"镜像+代码"两件套才是完整环境。
4. **版本互锁**：pytorch:20.12-py3 镜像（torch 1.7 世代）+ torchaudio==0.8.0 + stft_loss.py:13 的 `LooseVersion(torch.__version__) >= LooseVersion("1.7")` 探测——三处共同钉死 PyTorch 1.7 兼容面，升级需同步改。
5. **权重走 LFS 而非 release 附件**：clone 即得（拉取后），但忘了 lfs pull 会把指针文本当 checkpoint 加载而崩溃。

## 新人提示

改配置改 JSON 别改代码；改完用 `python network.py -c 你的配置.json` 冒烟（network.py:358-384）最快发现键名错配。两个 pretrained 的 oid 不同（full: 145c101e…，high: 513d9e4f…）但 size 同为 184336765——架构相同仅权重不同，别被同尺寸迷惑。README.md:69 声明权重"未训练去除混响"，评测混响数据会翻车。8GB 显存跑不动 batch 8×10 秒 crop，微调时把 batch_size_per_gpu 与 crop_length_sec 一起降。dist_config 的 tcp 端口 54321 单机占死，多实验并行要改（configs L48）。

（不计空格约 2150 字符，锚 40+）
