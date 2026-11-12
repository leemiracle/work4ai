# 第 7 篇：LAM 隐动作模型双副本——external/lam_project 与 external/lam

## 一、角色定位

DreamDojo 里存在两份高度同源的 LAM（Latent Action Model，隐动作模型）：`external/lam_project/` 是**研究完整版**，自带训练入口、数据集、多种集群启动器与残差向量量化器；`external/lam/` 是**生产精简副本**，只保留推理所需最小网络子集，被 `cosmos_predict2/_src/predict2/models/text2world_model_rectified_flow.py:70` 以 `from external.lam.model import LAM` 消费——主模型 forward 时在线计算 latent action 注入动作条件。动作通道里显式动作嵌入之外那 32 维隐式表征，正是 LAM 从相邻帧对"看图猜动作"的产物。

两份副本对应工整：`lam_project/lam/modules/embeddings.py` 与 `lam/modules/embeddings.py` 逐字节相同（diff 零差异实证），旋转位置编码完全复用；`blocks.py` 前半段（patchify/位置编码/自注意力/Spatio·SpatioTemporal Transformer）结构一致，研究版 328 行、生产版 238 行，差额 90 行正是研究版尾部独有的 `VectorQuantizer`（`external/lam_project/lam/modules/blocks.py:243`）与 `ResidualVectorQuantizer`（`blocks.py:304`）。

## 二、内部结构

**研究完整版**。`main.py:5-9` 是一行式入口：`LightningCLI(LAM, LightningVideoDataset, seed_everything_default=32)`，模型与数据全由 yaml 声明。核心网络 `lam/modules/lam.py` 是"帧对 VAE"：可学习 `action_prompt` patch（`lam.py:32-33`）与 patchify 后的视频 token 拼接送入时空 Transformer 编码器，取每帧第 0 个 token 作为隐动作表征（`lam.py:66`），经 `fc` 输出均值方差做重参数化——训练采样、推理用均值（`lam.py:73-77`）；eval 下持续累积 `mu_record`（`lam.py:79-83`）。解码侧把上一帧 patch 与隐动作 patch 相加过 SpatioTransformer 重建下一帧（`lam.py:103-107`）。

LightningModule 外壳（`lam_project/lam/model.py`）：`shared_step` 算 MSE + β 加权 KL（`model.py:59-61`），piq 算 PSNR/SSIM（`model.py:66-67`），`log_images` 拼 GT/重建对比 PNG（`model.py:139-152`）；`validation_step` 整段被注释（`model.py:102-119`），只有 train/test。量化器是研究版独有武器：VQ 带 usage buffer（`blocks.py:250`）、死码随机重启（`blocks.py:259-266`）、`delta_psnr` 探针（`blocks.py:285-291`，换随机码量化测码本贡献）；RVQ 叠 inner_vq 吃残差（`blocks.py:318-319`），直通估计 `z_q = x + (z - x).detach()`（`blocks.py:300`）。但须甄别：**当前配置未启用量化器**——`config/lam_0.yaml` 模型段无任何量化参数，LAM 构造函数也不接收，RVQ 属于携带未上膛的实验资产。

`config/lam_0.yaml`：dim 1024/latent 32/patch 16/24+24 块/16 头，β=1e-6（比 `model.py:31` 默认 0.01 小四档，近乎纯 MSE），AdamW 2.5e-5，batch 20，num_frames=2，数据 `../../datasets/PhysicalAI-Robotics-GR00T-Teleop-GR1/GR1_robot`，1000 epoch、16-mixed、`ddp_find_unused_parameters_false`。数据侧 `lam/dataset.py` 三种数据集（VideoDataset/OriginalVideoDataset/MultiSourceSamplerDataset），`default_worker_init_fn`（`dataset.py:27-40`）按 worker 均分全局切片；import 时设 `OPENCV_FFMPEG_READ_ATTEMPTS=2**13`（`dataset.py:6-7`）抗拉流抖动。

**生产副本**。`external/lam/modules/lam.py` 只留编码路径：`assert T == 2`（`lam.py:57`）强制帧对；重参数化已删，`z_rep = z_mu` 直接返回（`lam.py:72`）；`forward` 只调 encode（`lam.py:80-84`），解码/重建/mu_record 全无。外壳 `external/lam/model.py` 反而**加**了 `ckpt_path` 与 `reload_ckpt`（`model.py:33`、`model.py:55-65`）：`torch.load(...)["state_dict"]` + `load_state_dict(assign=True)`，打印 missing/unexpected 键——生产版删了量化器，研究版 ckpt 的量化器权重会落 unexpected 被显式忽略，这正是键对账存在的原因。甄别二：生产版 `shared_step` 仍引用 `outputs["recon"]`（`model.py:72`）而网络 forward 不产出 recon——拷贝残留的死代码，生产副本只在 no_grad 下走 forward 拿 z_rep。

## 三、外部连接

生产副本唯一消费者是 `text2world_model_rectified_flow.py`：以 1024/32/16/24/24/16 与 lam_0.yaml 完全一致的超参实例化（`text2world_model_rectified_flow.py:179-187`），`ckpt_path="checkpoints/DreamDojo/LAM_400k.ckpt"`（40 万步预训练产物）。研究版对外三脚本：单机 `train.sh`（torchrun 8 卡 fit lam_0.yaml）、多机 `launch.sh`（位置参数 `CONFIG_INDEX` 选 `config/lam_${INDEX}.yaml`）、`test.sh`（`checkpoints/lam/epoch=1.ckpt`）。外围另有 `osmo_launch.py`（Osmo 池 groot-h100-01/02，gear fast 模板 + 回车确认）与 `ray_launch.py`（Ray `_TrainingWorker` actor 各节点起 torchrun 子进程）。主训练侧 action_dim=384（`configs/2b_480_640_pretrain.yaml:23`）为 LAM 留出接口。

## 四、数据流

主训练 forward（`text2world_model_rectified_flow.py:863-869`）：`lam_video` 形如 `(b, p*2, h, w, c)`，rearrange 成 `(b*p, 2, h, w, c)` 独立帧对——每个 rollout 片段 p 对相邻帧；`{"videos": lam_video}` 在 `torch.no_grad()` 下过 `self.lam.lam(lam_input)`（双层 `.lam.lam`：LightningModule 属性包网络本体），z_rep squeeze 成 `(t*b, 32)` 再回 `(b, t, 32)` 对齐动作时间轴；关键融合在 `text2world_model_rectified_flow.py:869`——384 维动作 chunk 向量的**末 32 维与 LAM 隐动作逐元素相乘**：显式动作嵌入占前 352 维 + 隐动作乘性调制末 32 维，显隐两路在同一向量内融合而非拼接。研究版自身训练流：VideoDataset 随机取 2 帧 → recon/z_mu/z_var → MSE+KL 反传 → TensorBoard 与 exp_imgs PNG。

## 五、设计决策

**为什么双副本**：主训练管线 import 的是 `external.lam` 小包，`assert T==2`、无解码器的精简形态把"训练用完整 VAE"与"推理用纯编码器"物理隔离，主仓不必带 LightningCLI/piq/RVQ 依赖；代价是 embeddings.py 必须逐字节同步——目前零差异，但没有任何机制保证，改一份忘一份会静默不一致且无测试拦截。**为什么乘性融合**：GR00T 风格动作 chunk 嵌入是高维语义向量，末 32 维乘 LAM 隐动作等于给"机器人说要做的事"叠加"画面上实际发生的事"，对遥操作数据中动作标注与视觉结果不一致的噪声天然鲁棒。**为什么 β 压到 1e-6**：KL 项是正则，压到极小让后验几乎不受先验束缚，z_mu 更锐利——对下游乘性门控比对数似然更重要。**坑**：生产副本 shared_step 死代码、未启用的 RVQ、`test.sh` 的 epoch=1.ckpt 与 LAM_400k 命名体系不一致（疑早期残留）；三个 shell 脚本均硬编码 `source /mnt/amlfs-01/shared/shenyuang/DreamDojo/.venv/bin/activate`，AMLFS 路径外部用户必须改。

## 六、新人提示

入手顺序：先读 `external/lam/modules/lam.py`（85 行）建立"帧对→隐动作"最小心智模型，再对照研究版看 VAE 训练形态差异，最后读 `text2world_model_rectified_flow.py:850-870` 看融合点。两个练习：① 解释生产版为何可安全删重参数化（推理只取均值，训练期采样只在研究版发生）；② 亲跑 `diff external/lam_project/lam/modules/embeddings.py external/lam/modules/embeddings.py` 验证零差异，并思考上游改旋转位置编码时双副本会怎么坏（静默不一致）。改 LAM 超参务必同步 `text2world_model_rectified_flow.py:181-186` 硬编码与 `config/lam_0.yaml`——二者无共享配置源。

> 甄别说明：本文行号锚与字节级结论（embeddings.py 零差异、blocks.py 行数差、量化器归属）均已在源码逐处核实；"RVQ 未启用""生产版 shared_step 为死代码"为构造函数签名与 forward 返回键交叉验证的推断，已标注依据；Osmo/Ray 启动器基于源码结构概述，未在真实集群执行验证。
