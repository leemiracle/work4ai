# vid2vid Onboarding（NVIDIA 官方视频到视频翻译实现）

> 仓库：NVIDIA/vid2vid @ 2e6d137（2019-07-03）· 论文 *Video-to-Video Synthesis* (NeurIPS 2018)
> 图谱：283 节点 / 516 边 / 9 层 / 12 步 tour / fingerprints 114 文件
> 本文档所有行号锚均经源码逐条核实（2026-11-10）。

## 1. 一句话定位

vid2vid 是 NVIDIA 发表的「语义掩码/草图序列 → 真实感视频序列」的条件视频生成系统：以 pix2pixHD 的图像翻译为底座，加入光流引导的帧间复用（warp）、软掩码融合、跳帧多时间尺度判别器族三大时序机制，在 street（Cityscapes 语义标签）/ face（关键点边缘图）/ pose（DensePose+OpenPose）三域上实现高分辨率时序一致的视频翻译。

## 2. 整体架构与模块地图

四个顶层子系统构成清晰的单向依赖链 `options → data → models → 脚本入口`：

| 模块 | 角色 | 关键文件 |
|---|---|---|
| options | argparse 参数注册（Base/Train/Test 三级覆写） | `options/base_options.py:11`、`options/train_options.py:4` |
| data | 三域数据集 + 视频级参数采样 | `data/base_dataset.py:9`、`data/pose_dataset.py:11`、`data/face_dataset.py:13`、`data/temporal_dataset.py:11` |
| models | G/D/FlowNet 三模型 + 网络结构 | `models/models.py:61`、`models/vid2vid_model_G.py:15`、`models/vid2vid_model_D.py:13`、`models/networks.py:117`、`models/flownet.py:6` |
| scripts | 三域 × 分辨率 × g1 变体 × 训练/测试 的启动矩阵 | `scripts/street/`、`scripts/pose/`、`scripts/face/` |

models 的工厂入口 `create_model`（`models/models.py:61`）按 opt.model 延迟 import `Vid2VidModelG` 与 `Vid2VidModelD`（`models/models.py:64-67`），训练时再延迟构造 `FlowNet`（`models/models.py:73`）——函数体内 import 是本仓破循环依赖与按需装载的统一手法。data 层同构：`data/custom_dataset_data_loader.py:7-18` 按 dataset_mode 四路延迟 import temporal/face/pose/test 数据集，`data/data_loader.py:2` 的 `CreateDataLoader` 再延迟回调 `CustomDatasetDataLoader`，两层共同消解 data 包内循环。

`models/flownet2_pytorch/` 是整体 vendored 的上游 FlowNet2 子树（含自己的 datasets/main/convert 训练栈），主链只通过 `models/flownet.py` 的窄接口消费其 FlowNet2 网络与 checkpoint。

## 3. 核心模块深读

### 3.1 CompositeGenerator：掩码融合双分支（论文核心）

`models/networks.py:117` 的 CompositeGenerator 是 vid2vid 区别于逐帧 pix2pixHD 的关键。输入侧两条下采样支路共享拓扑：语义/关键点分支 `model_down_seg` 与「上帧生成结果」分支 `model_down_img`（`models/networks.py:153-163`，后者对前者的 resnet 段做 `copy.deepcopy`），特征逐元素相加（`models/networks.py:204`）。解码侧一分为三：

- **raw 分支**：`model_res_img → model_up_img → model_final_img` 直接生成当前帧（`models/networks.py:205-206`）；
- **flow 头**：`model_res_flow`（`models/networks.py:169-170`，deepcopy 自图像 res 段）输出 2 通道光流，乘以尺度 20（`models/networks.py:212`；Local 变体按尺度放大 `models/networks.py:297`）；
- **weight 头**：1 通道 Sigmoid 软掩码（`models/networks.py:183`）。

融合公式在 `models/networks.py:219-221`：先用 `BaseNetwork.resample`（`models/networks.py:108`，flow 归一化到 [-1,1] 网格坐标后 `grid_sample`）把上一帧 warp 到当前帧，再逐像素 `img_raw * weight + img_warp * (1-weight)`——网络自己学会「哪里信任光流复用、哪里必须重新生成」。`use_fg_model` 时另有前景独立生成支路 `indv_*`（`models/networks.py:128-149`），按前景掩码二次融合（`models/networks.py:224-230`）。

### 3.2 Vid2VidModelG：逐帧生成与首帧热启动

`models/vid2vid_model_G.py:15` 维护 n_scales 个金字塔生成器（`models/vid2vid_model_G.py:38-43`，粗尺度 netG0 + 细尺度 `netG+'Local'`），训练循环 `generate_frame_train` 外层逐帧、内层 coarse-to-fine（`models/vid2vid_model_G.py:151-157`）：每帧经 7 元组 forward 拿到 `img_final, flow, weight, img_raw, img_feat, flow_feat, img_fg_feat`（`models/vid2vid_model_G.py:176-178`），细尺度生成器把粗尺度特征注入解码器（`models/networks.py:298-299`）。截断 BPTT 由 `n_frames_bp = 1` 实现——只在帧边界 detach 历史（`models/vid2vid_model_G.py:58`、`models/vid2vid_model_G.py:167-168`）；`niter_fix_global` 阶段粗尺度整体 detach 冻结（`models/vid2vid_model_G.py:181-186`）。

首帧策略集中在 `generate_first_frame`（`models/vid2vid_model_G.py:231`）：训练直接用真实首帧（`models/vid2vid_model_G.py:235`）；推理 `--use_single_G` 时由 `load_single_G`（`models/vid2vid_model_G.py:261`）加载 pix2pixHD 单帧模型——'City' in dataroot 时按 loadSize 512/1024/2048 选 `label2city_single` 检查点（`models/vid2vid_model_G.py:264-274`），face 域加载 `edge2face_single` 并附带编码器 netE（`models/vid2vid_model_G.py:277-284`）。face 域还经 `get_face_features`（`models/vid2vid_model_G.py:290`）从 `features.npy` 特征库做最近邻聚类中心替换（`models/vid2vid_model_G.py:310`），注入实例风格特征。

### 3.3 Vid2VidModelD：单帧 D + 跳帧时序 D 族

`models/vid2vid_model_D.py:13` 构造四类判别器：单帧 `netD`（多尺度 patch，`models/vid2vid_model_D.py:35`）、face 局部 `netD_f`（`models/vid2vid_model_D.py:38-40`，在人脸区域 crop 上判别且 loss ×2，`models/vid2vid_model_D.py:149-158`）、以及 `n_scales_temporal` 个时序判别器 `netD_T{s}`（`models/vid2vid_model_D.py:44-46`）。时序 D 的输入是 tD 帧拼通道再加 2×(tD-1) 通道参考光流（`models/vid2vid_model_D.py:43`、`models/vid2vid_model_D.py:187-188`）——判别器同时看图像序列与其真实光流，逼生成器维持长时序一致。

跳帧采样在 `get_skipped_frames`（`models/vid2vid_model_D.py:275`）：第 s 个时间尺度的采样间隔 `tDs = tD ** s`（`models/vid2vid_model_D.py:279`），即默认 tD=3 时判别器分别看 1/3/9 帧间隔的三元组；`--sparse_D` 走流式稀疏版本 `get_skipped_frames_sparse`（`models/vid2vid_model_D.py:304`）。损失族九项 + 时序五项（`models/vid2vid_model_D.py:69-72`）：Flow/Warp 损失用 MaskedL1Loss 按置信度掩码（`models/vid2vid_model_D.py:119-130`），生成 warp 一致性损失锚定参考流（`models/vid2vid_model_D.py:139-140`）。

### 3.4 FlowNet 与 vendored FlowNet2

`models/flownet.py:6` 把 FlowNet2 包装成 eval-only 的参考流计算器：initialize 内延迟 import 上游子模块（`models/flownet.py:14-16`），用 `module_to_dict`（`models/flownet2_pytorch/utils/tools.py:18`）实例化 FlowNet2 并加载 checkpoint（`models/flownet.py:18-21`），forward 全程 `torch.no_grad()`（`models/flownet.py:26`）——光流权重固定不训练。输入尺寸对齐 64 倍数（`models/flownet.py:47`），置信度由 warp 重投影误差阈值化得出：`conf = (norm(im1 - resample(im2, flow)) < 0.02)`（`models/flownet.py:55`）。

vendored 子树保留上游 Python2 时代原貌：`convert.py` shebang 即 `python2.7` 且 import caffe（`models/flownet2_pytorch/convert.py:1-3`）；`main.py:264` 的 `d.cuda(async=True)` 中 async 是 Python3.7+ 保留字，该文件无法被 Python3 解析——属上游训练入口，主链不消费。模型文件头硬编码权重规模注释 'Parameter count = 162,518,834'（`models/flownet2_pytorch/models.py:17`）。

### 3.5 数据层三域

- **temporal**（street 域也走此通道）：`_train_A/_train_B` 成对目录序列（`data/temporal_dataset.py:15-16`），标签图与真实图走不同插值/归一化 transform（`data/temporal_dataset.py:45`），inst 图 ×255 保留索引（`data/temporal_dataset.py:60`）。
- **pose**：DensePose（24 部位 UV）+ OpenPose（25+70+21+21 关键点，`data/keypoint2img.py:77-80`）双源输入按通道拼接（`data/pose_dataset.py:54`）；DensePose I 通道量化 0-24（`data/pose_dataset.py:44`）；训练随机丢部位/关键点增稳（`data/pose_dataset.py:80-84`、`data/pose_dataset.py:73-74`）；文件尾注释是 24 部位索引权威表（`data/pose_dataset.py:140-156`）。骨架拓扑硬编码于 `define_edge_lists`（`data/keypoint2img.py:151`）。
- **face**：68+15 点 csv 关键点画边缘图 + 每部件距离变换图 + 背景 canny（`data/face_dataset.py:130-136`、`data/face_dataset.py:81-83`），上半脸由对称性合成（`data/face_dataset.py:104-109`）；scale_ratio/scale_shift 是固定矩阵（随机代码被注释，`data/face_dataset.py:25-27`）。

所有域共享「视频级随机参数」机制：`get_img_params`（`data/base_dataset.py:85-128`）一次抽取 crop/flip 参数全序列复用（`data/base_dataset.py:127` 还显式排除 pose 域翻转）；`get_video_params`（`data/base_dataset.py:177-202`）随机 t_step 跳帧采样并按 pose/非 pose 区分起点策略（`data/base_dataset.py:191-194`）。

## 4. 数据流全链路（训练一轮）

1. `train.py:22-29` 建 DataLoader、`create_model`/`create_optimizer` 组装 G/D/FlowNet 与三组优化器。
2. `init_data_params`/`init_data` 按当前序列长度切装载窗口（`train.py:47-48`、`data/base_dataset.py:56-63`）。
3. 外层按 `n_frames_load` 分块喂序列（`train.py:50`），`prepare_data` 重塑 5D 张量（`data/base_dataset.py:74-80`）。
4. G 前向产出当前块 fake_B/flow/weight（`train.py:55`）。
5. FlowNet 对真实帧算参考流与置信度（`train.py:59-61`）。
6. 单帧 D 损失（scale_T=0，`train.py:64`）+ `get_all_skipped_frames` 抽各时间尺度跳帧组（`train.py:70-77`）逐尺度喂时序 D。
7. `get_losses` 汇总后 G/D/D_T 三路分别 backward（`train.py:86-93`），fp16 时经 apex amp 包装（`train.py:130-138`）。
8. epoch 末 `update_models` 触发学习率线性衰减、训练序列长度倍增（粗到细课程）与粗尺度解冻（`models/models.py:151-164`）；序列长度由数据侧 `update_training_batch` 同步倍增（`data/base_dataset.py:19-24`）。

推理链更短：`test.py:16-21` 强制单线程单样本、temporal 模式归一化为 test；`change_seq` 信号触发 `fake_B_prev` 重置换序列（`test.py:34-35`），模型 `inference` 内部维护逐帧滑窗状态（`models/vid2vid_model_G.py:228`）。

## 5. 配置与运行入口

- 主入口 `train.py` / `test.py`；参数三层注册：`options/base_options.py:11`（60+ 项，含 `n_gpus_gen` 默认 -1 即全部 GPU 给 G，`options/base_options.py:28`）、`options/train_options.py:4` 追加训练项（`n_frames_D=3`、`n_scales_temporal=2` 默认在 `options/train_options.py:34-35`）。
- 脚本矩阵（实测计数）：`scripts/street/` 14 个（11 sh + 3 py，train/test × 512/1024/2048 × g1 短程变体）、`scripts/pose/` 12 个（全 sh，× 256p/512p/1024p）、`scripts/face/` 9 个（7 sh + 2 py，× 256/512）——域、分辨率、g1、训练/测试四轴组合，直接给出论文各配置的完整命令行。
- 预训练权重：`scripts/download_models_flownet2.py` 取 FlowNet2 checkpoint；三域各自 `download_models.py`。注意 `download_gdrive.py` 在 `scripts/`、`scripts/face/`、`scripts/street/` 各有一份 md5 完全相同的副本（8f23a129…），各域脚本 `from download_gdrive import *` 就近消费同目录副本。
- docker 链：`docker/Dockerfile:1` 基于 cuda:9.0-cudnn7-ubuntu16.04 单阶段构建、无 CMD；`docker/launch_docker.sh:5` 用 nvidia-docker 交互式进入。

## 6. 关键设计决策

1. **光流复用 + 软掩码**（`models/networks.py:219-221`）替代逐帧独立生成或纯光流 copy——warp 保时序、raw 保质量，weight 逐像素仲裁，这是论文「recycling by flow」的直接落地。
2. **判别器看光流**（`models/vid2vid_model_D.py:187-188`）：时序 D 的输入拼上参考光流通道，等价于要求生成帧之间的光流与真实光流一致。
3. **粗到细课程**：空间尺度先冻结粗层（`options/train_options.py:41` `niter_fix_global`），时间尺度由序列长度倍增推进（`models/models.py:158-160`）。
4. **显存分放**：`n_gpus_gen < len(gpu_ids)` 时 G 与 D/FlowNet 分别 DataParallel 到不同 GPU 子集（`models/models.py:16-23`），配 dummy batch 填充保证整除（`models/models.py:42-50`、`util/util.py:109`）。
5. **首帧热启动复用 pix2pixHD**（`models/vid2vid_model_G.py:261`）——图像→视频两阶段，避免视频模型从零学静态画质。
6. **参考流 eval-only**（`models/flownet.py:21-26`）：FlowNet2 当冻结的「真值探测器」用，不参与对抗。

## 7. 坑与勘误

- **README 默认值与代码不符**：README 称 `n_scales_temporal` 默认 3，代码实为 2（`options/train_options.py:35`）。
- **Python3 跑不了 vendored 子树**：`models/flownet2_pytorch/main.py:264` 的 `async=True` 是 Py3.7+ 保留字；convert.py 需要 python2.7+caffe。主链不受影响，但别试图 import 上游训练脚本。
- **上游数据层是死代码**：`models/flownet2_pytorch/datasets.py` 属上游独立训练栈，vid2vid 用自己的 data/ 包，不消费。
- **下载脚本版本分支已注释**：`scripts/download_flownet2.py:4-10` 的 torch 版本选择代码被 docstring 化，现行只剩跑 `install.sh`（`scripts/download_flownet2.py:18`）。
- **face 增强固定化**：`data/face_dataset.py:25-27` 的随机 scale 代码被注释成常量矩阵；`--random_scale_points` 只动关键点不重开随机。
- **torch 0.3 遗产**：`models/base_model.py:50-60` 手工补 `_rebuild_tensor_v2` 才能加载旧 checkpoint。
- **测试模式归一化**：README 命令行里的 `--dataset_mode temporal` 在 `test.py:20-21` 被静默改写为 `test`。

## 8. 新人上手路线

1. 读论文 §3 方法节，再按本页 §3.1 对照读 `models/networks.py:203-232` 的 forward（100 行内看懂双分支+融合）。
2. 用 `scripts/street/train_512.sh` 的命令行对照 `options/base_options.py` 逐项注解，理解四轴脚本矩阵。
3. 跟一遍 §4 数据流，重点盯 `train.py:50-93` 的分块循环与三路 backward。
4. 跑 `scripts/download_models.py` 下载预训练权重，用 `test.py` 在 Cityscapes val 上复现（注意 §7 的 temporal→test 改写）。
5. 进阶：读 `models/vid2vid_model_G.py:139-196` 的逐帧多 GPU 调度（split_gpus/replicate），理解 2018 年在 8 卡上训 2048p 视频的工程约束。

> 锚格式 `文件:行`，相对仓根 /usr-data/data2/repos/agent-repos/NVIDIA/vid2vid/。配合 deepwiki/ 17 页与 explain/ 4 篇精讲食用。
